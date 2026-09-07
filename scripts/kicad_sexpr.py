"""Small, strict S-expression reader for KiCad source and custom-rule files.

This is a syntax reader, not a complete KiCad schema validator. Consumers must
validate the fields they use and reject unsupported geometry. No token is
skipped on a lexical error, and single-document parsing rejects trailing roots.
"""

from __future__ import annotations

from dataclasses import dataclass


class SExprError(ValueError):
    def __init__(self, message: str, source: str = "<input>", line: int = 1,
                 column: int = 1):
        self.source, self.line, self.column = source, line, column
        super().__init__(f"{source}:{line}:{column}: {message}")


class Atom(str):
    """Retain quoting so test fixtures can be serialized without changing atoms."""

    def __new__(cls, value: str, quoted: bool = False):
        instance = super().__new__(cls, value)
        instance.quoted = quoted
        return instance


@dataclass
class Node:
    tag: str
    values: list[Atom | Node]
    line: int = 1
    column: int = 1
    source: str = "<input>"

    def children(self, tag: str | None = None) -> list[Node]:
        return [v for v in self.values if isinstance(v, Node)
                and (tag is None or v.tag == tag)]

    def one(self, tag: str, *, required: bool = True) -> Node | None:
        found = self.children(tag)
        if len(found) > 1 or (required and not found):
            self.fail(f"expected {'one' if required else 'at most one'} ({tag} ...), "
                      f"found {len(found)}")
        return found[0] if found else None

    def atoms(self, count: int | None = None) -> list[Atom]:
        if any(isinstance(v, Node) for v in self.values):
            self.fail(f"({self.tag} ...) requires scalar values")
        if count is not None and len(self.values) != count:
            self.fail(f"({self.tag} ...) requires {count} value(s)")
        return list(self.values)

    def fail(self, message: str):
        raise SExprError(message, self.source, self.line, self.column)


def parse_many(text: str, source: str = "<input>") -> list[Node]:
    """Read every expression, including # comments and quoted/escaped strings.

    KiCad rule files have multiple roots and permit either quote delimiter.
    Semicolon comments are also accepted, as in KiCad's format documentation.
    Limits bound accidental enormous input and deeply nested malformed files.
    """
    if len(text) > 16 * 1024 * 1024:
        raise SExprError("input exceeds 16 MiB reader limit", source)
    if text.startswith("\ufeff"):
        text = text[1:]
    stack: list[tuple[list, int, int]] = []
    roots: list[Node] = []
    i, line, column, tokens = 0, 1, 1, 0

    def fail(message):
        raise SExprError(message, source, line, column)

    def advance():
        nonlocal i, line, column
        if text[i] == "\n":
            line, column = line + 1, 1
        else:
            column += 1
        i += 1

    while i < len(text):
        char = text[i]
        if char in " \t\r\n":
            advance()
            continue
        if char in "#;":
            while i < len(text) and text[i] != "\n":
                advance()
            continue
        if ord(char) < 32:
            fail("unexpected control character")
        tokens += 1
        if tokens > 1_000_000:
            fail("input exceeds token limit")
        if char == "(":
            if len(stack) >= 128:
                fail("input exceeds nesting limit")
            stack.append(([], line, column))
            advance()
            continue
        if char == ")":
            if not stack:
                fail("unmatched closing parenthesis")
            values, start_line, start_column = stack.pop()
            if not values or not isinstance(values[0], Atom) or values[0].quoted:
                fail("KiCad expression must start with an unquoted atom")
            node = Node(str(values[0]), values[1:], start_line, start_column, source)
            (stack[-1][0] if stack else roots).append(node)
            advance()
            continue
        if not stack:
            fail("expected a parenthesized expression, not trailing/bare text")
        if char in "\"'":
            quote, start_line, start_column = char, line, column
            advance()
            value = []
            while i < len(text) and text[i] != quote:
                char = text[i]
                if char == "\\":
                    advance()
                    if i == len(text):
                        fail("unterminated escape")
                    escapes = {"n": "\n", "r": "\r", "t": "\t", "\\": "\\",
                               '"': '"', "'": "'"}
                    if text[i] not in escapes:
                        fail(f"unsupported escape \\{text[i]}")
                    value.append(escapes[text[i]])
                else:
                    if char in "\n\r":
                        fail("literal newline in quoted string; use \\n instead")
                    if ord(char) < 32 and char != "\t":
                        fail("unexpected control character in string")
                    value.append(char)
                advance()
            if i == len(text):
                raise SExprError("unterminated quoted string", source, start_line, start_column)
            advance()
            if i < len(text) and text[i] not in " \t\r\n()#;":
                fail("missing delimiter after quoted string")
            atom = Atom("".join(value), quoted=True)
        else:
            start = i
            while i < len(text) and text[i] not in " \t\r\n()#;":
                if text[i] in "\"\\" or ord(text[i]) < 32:
                    fail("unexpected quote, escape, or control character in bare atom")
                advance()
            atom = Atom(text[start:i])
        stack[-1][0].append(atom)
    if stack:
        _, start_line, start_column = stack[-1]
        raise SExprError("unclosed expression", source, start_line, start_column)
    if not roots:
        raise SExprError("empty input", source)
    return roots


def parse(text: str, source: str = "<input>", *, root: str | None = None) -> Node:
    nodes = parse_many(text, source)
    if len(nodes) != 1:
        nodes[1].fail("expected one root expression; trailing root found")
    result = nodes[0]
    if root is not None and result.tag != root:
        result.fail(f"expected ({root} ...), found ({result.tag} ...)")
    return result
