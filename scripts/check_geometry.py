#!/usr/bin/env python3
"""P1/P6 nominal physical guardrails for the KiCad 9 Dog Fence source board.

Read-only, stdlib-only, and deliberately not a replacement for native DRC/ERC,
manufacturing-output inspection, maximum-pin fit evidence, or CAM acceptance.
Unsupported geometry is an error, never an omitted item in a passing report.
See LIMITATIONS and the JSON measurements for the conservative restrictions.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
import fnmatch
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import sys
import tempfile

if __package__:
    from .kicad_sexpr import Atom, Node, SExprError, parse, parse_many
else:
    from kicad_sexpr import Atom, Node, SExprError, parse, parse_many


EPS = 1e-6  # One nanometre in the source's millimetre coordinates, not a fit allowance.
CU = frozenset(("F.Cu", "B.Cu"))
MASK = frozenset(("F.Mask", "B.Mask"))
PASTE = frozenset(("F.Paste", "B.Paste"))
CRITICAL_LAYERS = CU | MASK | PASTE | {"Edge.Cuts"}
BOARD_BOUNDS = (97.0, 94.5, 160.0, 150.5)
RAILS = {"WIRE_A": 114.88, "WIRE_B": 122.5, "WIRE_C": 130.12}
PROTECTED_VIAS = {
    **{(x, y): net for net, y in RAILS.items() for x in (112.5, 114.0, 115.5)},
    **{(150.0, y): "EARTH" for y in (114.88, 118.69, 122.5, 126.31, 130.12)},
}
MOUNTS = {"H1": (101.5, 99.0), "H2": (155.5, 99.0),
          "H3": (101.5, 146.0), "H4": (155.5, 146.0)}
MIN_MASK_BARRIER = 0.10
PROJECT_MINIMA = {
    "min_track_width": 0.1651, "min_clearance": 0.20,
    "min_copper_edge_clearance": 0.50, "min_hole_clearance": 0.25,
    "min_hole_to_hole": 0.25, "min_via_annular_width": 0.10,
    "min_text_height": 1.0, "min_text_thickness": 0.15,
    "min_silk_clearance": 0.15,
}
REQUIRED_ERROR_RULES = (
    "annular_width", "clearance", "copper_edge_clearance", "hole_clearance",
    "track_width", "drill_out_of_range", "invalid_outline", "shorting_items",
    "unconnected_items", "courtyards_overlap", "malformed_courtyard", "solder_mask_bridge",
)
REQUIRED_VISIBLE_RULES = (
    "text_height", "text_thickness", "silk_over_copper", "hole_to_hole",
    "missing_courtyard", "lib_footprint_issues", "lib_footprint_mismatch",
)
LIMITATIONS = [
    "Nominal saved-source geometry only; native project-aware DRC/ERC/parity and regenerated "
    "Gerber, drill, stencil and assembler CAM inspection remain separate gates.",
    "Supported: straight tracks, round through vias, top-side footprints, circular/oval holes, "
    "circle/oval/rect/roundrect pads, straight/rect/filled-circle/convex-polygon graphics. "
    "Arcs, copper text, custom/chamfered pads, layer-specific padstacks and filled zones fail closed.",
    "Rail proofs require collinear full-width segments (splitting/reversing segments is allowed). "
    "Earth fill is proven with axis-aligned track strips and its original rounded outer boundary; "
    "an equivalent alternative construction may require extending the checker.",
    "Copper clearance uses outer copper envelopes, conservatively not subtracting drill voids. "
    "Mounting checks retain the 3.45 mm front/back courtyard radii and exclude copper; native "
    "courtyard DRC and physical enclosure/support fit are still required.",
    "The 0.10 mm hole-to-mask or open-via-mask-to-neighbour-mask barrier is a conservative nominal "
    "project check, not a CAM-approved covering/plugging process or the 0.35 mm ink-plugging rule. "
    "Nonzero mask minimum width is bounded by half-width aperture inflation before checking; "
    "rounded-pad apertures bound both flash and polygon-offset corner constructions.",
    "Tenting/filling flags cannot waive aperture collisions or prove reliable covering of 1.0 mm "
    "holes. Copper-only overlap can be mask-defined; exposed annuli and copper gaps are reported.",
    "Rule coverage models clearance and annular_width with string/NetCode comparisons, wildcards, "
    "parentheses and boolean operators; unsupported relevant conditions fail closed. "
    "Annular_width is unary (A only): B-dependent conditions are rejected, not evaluated with B=A. "
    "Clearance is binary. Other custom constraints require native KiCad validation.",
    "Diode drill >=1.10 mm and nominal component ring >=0.254 mm do not qualify other maximum "
    "pin dimensions, fabrication/registration tolerances, barrel plating, lead forming, "
    "GDT_AC's >=2.0 mm physical standoff, thermal/surge performance or assembly process.",
]


class Unsupported(ValueError):
    def __init__(self, message: str, node: Node):
        self.node = node
        super().__init__(message)


def numeric(value, node: Node | None = None) -> float:
    try:
        if isinstance(value, bool) or not isinstance(value, (str, int, float)):
            raise ValueError
        if isinstance(value, str) and (not value or any(c not in "0123456789+-.eE" for c in value)):
            raise ValueError
        result = float(value)
        if not math.isfinite(result):
            raise ValueError
        return result
    except (ValueError, OverflowError):
        if node is not None:
            node.fail(f"invalid finite number {value!r}")
        raise ValueError(f"invalid finite number {value!r}") from None


def scalar(node: Node, key: str, default=None):
    child = node.one(key, required=default is None)
    return child.atoms(1)[0] if child else default


def number(node: Node, key: str, default=None) -> float:
    value = numeric(scalar(node, key, default), node)
    if key != "version" and abs(value) > 2147.483647:
        node.fail(f"{key} exceeds KiCad's signed 32-bit nanometre dimensional range")
    return value


def point(node: Node, key: str) -> tuple[float, float]:
    child = node.one(key)
    result = tuple(numeric(v, child) for v in child.atoms(2))
    if any(abs(v) > 2147.483647 for v in result):
        child.fail("coordinate/dimension exceeds KiCad's signed 32-bit nanometre range")
    return result


def position(node: Node) -> tuple[tuple[float, float], float]:
    at = node.one("at")
    values = at.atoms()
    if len(values) not in (2, 3):
        at.fail("expected (at x y [angle])")
    coords = [numeric(v, at) for v in values]
    if any(abs(v) > 2147.483647 for v in coords[:2]):
        at.fail("position exceeds KiCad's signed 32-bit nanometre range")
    return tuple(coords[:2]), coords[2] % 360 if len(coords) == 3 else 0.0


def boolean(node: Node, key: str, default: bool = False) -> bool:
    child = node.one(key, required=False)
    if child is None:
        return default
    values = child.atoms()
    if not values:  # KiCad also writes bare flag clauses such as (locked).
        return True
    if values not in (["yes"], ["no"]):
        child.fail(f"invalid boolean ({key} ...)")
    return values == ["yes"]


def schema(node: Node, allowed: set[str], atom_count: int = 0, flags=()):
    atoms = [v for v in node.values if isinstance(v, Atom)]
    if len(atoms) < atom_count or any(not isinstance(v, Atom) for v in node.values[:atom_count]) \
            or any(v not in flags for v in atoms[atom_count:]):
        node.fail(f"unexpected scalar fields in ({node.tag} ...)")
    for child in node.children():
        if child.tag not in allowed:
            raise Unsupported(f"unsupported ({child.tag} ...) inside ({node.tag} ...)", child)


def move(p, origin=(0.0, 0.0), angle=0.0):
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    return origin[0] + c * p[0] + s * p[1], origin[1] - s * p[0] + c * p[1]


def cross(a, b, p):
    return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])


def edges(points):
    if len(points) == 1:
        return [(points[0], points[0])]
    if len(points) == 2:
        return [(points[0], points[1])]
    return list(zip(points, points[1:] + points[:1]))


def point_segment(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    norm = dx * dx + dy * dy
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / norm)) if norm else 0
    return math.dist(p, (a[0] + t * dx, a[1] + t * dy))


def inside(p, poly):
    if len(poly) < 3:
        return False
    signs = [cross(a, b, p) for a, b in edges(poly)]
    return min(signs) >= -1e-10 or max(signs) <= 1e-10


@dataclass(frozen=True)
class Shape:
    """Convex point/segment/polygon core Minkowski-summed with a round radius."""

    core: tuple[tuple[float, float], ...]
    radius: float = 0.0

    def signed_distance(self, p):
        distance = min(point_segment(p, a, b) for a, b in edges(self.core))
        return (-distance if inside(p, self.core) else distance) - self.radius

    def core_distance(self, other):
        if any(inside(p, other.core) for p in self.core) or any(inside(p, self.core) for p in other.core):
            return 0.0
        best = math.inf
        for a, b in edges(self.core):
            for c, d in edges(other.core):
                if cross(a, b, c) * cross(a, b, d) < 0 and cross(c, d, a) * cross(c, d, b) < 0:
                    return 0.0
                best = min(best, point_segment(a, c, d), point_segment(b, c, d),
                           point_segment(c, a, b), point_segment(d, a, b))
        return best

    def gap(self, other):
        return max(0.0, self.core_distance(other) - self.radius - other.radius)

    def overlaps(self, other):
        """Positive-area overlap, not a merely tangent solder-mask/paste opening."""
        if self.radius + other.radius > 0:
            return self.core_distance(other) < self.radius + other.radius - EPS
        if len(self.core) < 3 or len(other.core) < 3:
            return False
        for a, b in edges(self.core) + edges(other.core):
            normal = (a[1] - b[1], b[0] - a[0])
            left = [p[0] * normal[0] + p[1] * normal[1] for p in self.core]
            right = [p[0] * normal[0] + p[1] * normal[1] for p in other.core]
            if min(max(left), max(right)) - max(min(left), min(right)) <= EPS * math.hypot(*normal):
                return False
        return True

    def contains(self, other):
        return all(self.signed_distance(p) + other.radius <= EPS for p in other.core)

    def inflate(self, amount):
        return Shape(self.core, self.radius + amount)

    @property
    def bounds(self):
        xs, ys = zip(*self.core)
        return min(xs) - self.radius, min(ys) - self.radius, max(xs) + self.radius, max(ys) + self.radius


def pad_shape(kind, size, center, angle, ratio=0.25, rect_radius=0.0):
    x, y = size
    if min(size) <= 0:
        raise ValueError("nonpositive pad/aperture size")
    if kind == "circle":
        if abs(x - y) > EPS:
            raise ValueError("non-circular size for circle pad")
        return Shape((center,), x / 2)
    radius = min(size) / 2 if kind == "oval" else ratio * min(size) if kind == "roundrect" else rect_radius
    radius = min(radius, min(size) / 2)
    dx, dy = x / 2 - radius, y / 2 - radius
    points = [move(p, center, angle) for p in ((-dx, -dy), (dx, -dy), (dx, dy), (-dx, dy))]
    return Shape(tuple(dict.fromkeys(points)), radius)


@dataclass
class Item:
    node: Node
    label: str
    shape: Shape
    layers: frozenset[str]
    net: str = ""
    kind: str = ""
    reference: str = ""
    pad_number: str = ""
    center: tuple[float, float] = (0.0, 0.0)
    hole: Shape | None = None

    def properties(self, layer):
        net_field = self.node.one("net", required=False)
        return {"Type": "Pad" if self.kind in ("thru_hole", "np_thru_hole", "smd", "connect")
                else "Via" if self.kind == "via" else "Track" if self.kind == "segment" else "Graphic",
                "Pad_Type": {"thru_hole": "Through-hole", "np_thru_hole": "NPTH, mechanical",
                             "smd": "SMD", "connect": "Edge connector"}.get(self.kind, ""),
                "NetName": self.net, "NetCode": int(net_field.atoms()[0]) if net_field else 0,
                "Layer": layer, "Reference": self.reference,
                "Pad_Number": self.pad_number}


def condition(text: str, node: Node):
    """Parse a restricted KiCad rule expression, without eval or regex matching.

    KiCad's && and || have equal precedence and associate left-to-right.
    Return a tree so every branch is parsed, even when evaluation short-circuits.
    """
    tokens, i = [], 0
    while i < len(text):
        if len(tokens) > 256:
            raise Unsupported("relevant rule condition exceeds the 256-token complexity limit", node)
        if text[i].isspace():
            i += 1
        elif text[i] in "\"'":
            quote, i, value = text[i], i + 1, []
            while i < len(text) and text[i] != quote:
                if text[i] == "\\":
                    raise Unsupported("escapes inside rule condition literals are unsupported", node)
                value.append(text[i])
                i += 1
            if i == len(text):
                node.fail("unterminated rule condition literal")
            tokens.append(("literal", "".join(value)))
            i += 1
        elif text[i] in "0123456789+-.":
            start = i
            while i < len(text) and text[i] in "0123456789+-.eE":
                i += 1
            tokens.append(("number", numeric(text[start:i], node)))
        elif text[i:i + 2] in ("==", "!=", "&&", "||"):
            tokens.append(text[i:i + 2])
            i += 2
        elif text[i] in "()!":
            tokens.append(text[i])
            i += 1
        else:
            start = i
            while i < len(text) and (text[i].isalnum() or text[i] in "_."):
                i += 1
            name = text[start:i]
            if name not in {f"{obj}.{prop}" for obj in ("A", "B") for prop in
                            ("Type", "Pad_Type", "NetName", "NetCode", "Layer", "Reference", "Pad_Number")}:
                raise Unsupported(f"unsupported relevant rule expression at {text[start:]!r}", node)
            tokens.append(("property", name))
    at = 0

    def term():
        nonlocal at
        if at == len(tokens):
            node.fail("incomplete rule condition")
        token = tokens[at]
        at += 1
        if token == "!":
            return ("!", term())
        if token == "(":
            result = expression()
            if at == len(tokens) or tokens[at] != ")":
                node.fail("unbalanced rule condition")
            at += 1
            return result
        if not isinstance(token, tuple) or at + 1 >= len(tokens) or tokens[at] not in ("==", "!="):
            node.fail("expected equality/inequality comparison in rule condition")
        op, right = tokens[at:at + 2]
        if not isinstance(right, tuple):
            node.fail("expected rule comparison operand")
        numeric_operand = lambda operand: operand[0] == "number" or (
            operand[0] == "property" and operand[1].endswith(".NetCode"))
        if numeric_operand(token) != numeric_operand(right):
            raise Unsupported("mixed numeric/string rule comparison is unsupported", node)
        at += 2
        return (op, token, right)

    def expression():
        nonlocal at
        result = term()
        while at < len(tokens) and tokens[at] in ("&&", "||"):
            op = tokens[at]
            at += 1
            result = (op, result, term())
        return result

    result = expression()
    if at != len(tokens):
        node.fail("trailing rule condition tokens")
    return result


def matches(tree, a, b):
    if tree is None:
        return True
    op = tree[0]
    if op == "!":
        return not matches(tree[1], a, b)
    if op in ("&&", "||"):
        left, right = matches(tree[1], a, b), matches(tree[2], a, b)
        return left and right if op == "&&" else left or right

    def value(operand):
        kind, text = operand
        return (a if text[0] == "A" else b)[text[2:]] if kind == "property" else text

    left, right = value(tree[1]), value(tree[2])
    # KiCad string matching has * and ? wildcards, not fnmatch's [character] classes.
    if tree[2][0] == "literal":
        equal = fnmatch.fnmatchcase(left, right.replace("[", "[[]"))
    elif tree[1][0] == "literal":
        equal = fnmatch.fnmatchcase(right, left.replace("[", "[[]"))
    else:
        equal = left == right
    return equal if op == "==" else not equal


def rule_dimension(node):
    text = "".join(node.atoms())
    for suffix, scale in (("mm", 1.0), ("mil", 0.0254), ("th", 0.0254), ("in", 25.4)):
        if text.endswith(suffix):
            return numeric(numeric(text[:-len(suffix)], node) * scale, node)
    return numeric(text, node)


class GeometryCheck:
    def __init__(self, board: Node):
        self.board = board
        self.diagnostics = []
        self.measurements = {}
        self.copper: list[Item] = []
        self.pads: list[Item] = []
        self.vias: list[Item] = []
        self.apertures: list[Item] = []
        self.tracks: list[Item] = []
        self.footprints: dict[str, Node] = {}
        self.outline = []
        self.nets = {}
        self.layers = set()
        self.setup = board.one("setup")

    def error(self, code, message, node=None, **detail):
        node = node or self.board
        self.diagnostics.append({"code": code, "severity": "error", "message": message,
                                 "file": node.source, "line": node.line, **detail})

    def expect(self, valid, code, message, node=None, **detail):
        if not valid:
            self.error(code, message, node, **detail)

    def attempt(self, operation, *args):
        try:
            operation(*args)
        except Unsupported as exc:
            self.error("UNSUPPORTED_GEOMETRY", str(exc), exc.node)
        except SExprError as exc:
            self.diagnostics.append({"code": "INVALID_STRUCTURE", "severity": "error",
                                     "message": str(exc), "file": exc.source,
                                     "line": exc.line, "column": exc.column})

    def layer_set(self, node, key="layers"):
        values = node.one(key).atoms(1 if key == "layer" else None)
        if not values or len(values) != len(set(values)):
            node.fail("missing or duplicate layer names")
        result = set()
        for value in values:
            expanded = {"*.Cu": CU, "*.Mask": MASK, "*.Paste": PASTE,
                        "F&B.Cu": CU}.get(value, {str(value)})
            if not expanded <= self.layers:
                raise Unsupported(f"unknown or disabled layer(s): {sorted(expanded - self.layers)}", node)
            result.update(expanded)
        return frozenset(result)

    def net(self, node, required=True):
        field = node.one("net", required=required)
        if not field:
            return ""
        values = field.atoms()
        if len(values) not in (1, 2) or not values[0].isascii() or not values[0].isdigit():
            field.fail("expected (net integer [name])")
        code = int(values[0])
        if code not in self.nets or (len(values) == 2 and values[1] != self.nets[code]):
            field.fail("unknown net number or mismatched net name")
        return self.nets[code]

    def read_board(self):
        schema(self.board, {"version", "generator", "generator_version", "general", "paper",
                           "title_block", "layers", "setup", "net", "footprint", "segment", "via",
                           "arc", "zone", "gr_line", "gr_rect", "gr_circle", "gr_poly", "gr_arc",
                           "gr_curve", "gr_text", "gr_text_box", "dimension", "target", "image",
                           "group", "property", "embedded_fonts", "embedded_files"})
        if number(self.board, "version") != 20241229:
            raise Unsupported("only the KiCad 9 (20241229) source format is supported; "
                              "older versions have different zero-margin inheritance", self.board)
        layer_ids = set()
        layer_table = self.board.one("layers")
        if any(isinstance(v, Atom) for v in layer_table.values):
            layer_table.fail("layer table must contain layer entries only")
        for layer in layer_table.children():
            values = layer.atoms()
            if not layer.tag.isdigit() or len(values) not in (2, 3):
                layer.fail("invalid layer table entry")
            if layer.tag in layer_ids or values[0] in self.layers:
                layer.fail("duplicate layer ID or canonical name")
            layer_ids.add(layer.tag)
            self.layers.add(str(values[0]))
        self.expect({l for l in self.layers if l.endswith(".Cu")} == CU, "COPPER_LAYERS",
                    "exactly F.Cu and B.Cu copper layers are required")
        self.expect(CU | MASK | {"F.Paste", "Edge.Cuts"} <= self.layers, "REQUIRED_LAYERS",
                    "front/back copper and mask, top paste and Edge.Cuts must be enabled")
        schema(self.setup, {"stackup", "pad_to_mask_clearance", "solder_mask_min_width",
                            "pad_to_paste_clearance", "pad_to_paste_clearance_ratio",
                            "allow_soldermask_bridges_in_footprints", "tenting", "pcbplotparams",
                            "aux_axis_origin", "grid_origin", "user_trace_width", "user_via"})
        schema(self.board.one("general"), {"thickness", "legacy_teardrops"})
        self.expect(abs(number(self.board.one("general"), "thickness") - 1.6) <= EPS,
                    "BOARD_THICKNESS", "nominal board thickness must remain 1.60 mm")
        stack = self.setup.one("stackup")
        schema(stack, {"layer", "copper_finish", "dielectric_constraints", "edge_connector",
                       "castellated_pads", "edge_plating"})
        if boolean(stack, "edge_plating") or boolean(stack, "castellated_pads"):
            raise Unsupported("edge plating/castellations require additional physical geometry checks", stack)
        copper_stack = []
        for layer in stack.children("layer"):
            schema(layer, {"type", "color", "thickness", "material", "epsilon_r", "loss_tangent"}, 1)
            if scalar(layer, "type") == "copper":
                copper_stack.append(str(layer.values[0]))
        self.expect(len(copper_stack) == 2 and set(copper_stack) == CU, "COPPER_LAYERS",
                    "stackup must contain only F.Cu and B.Cu copper", stack)
        for name in CU:
            found = [n for n in stack.children("layer") if n.values and n.values[0] == name]
            self.expect(len(found) == 1, "COPPER_WEIGHT", f"one stackup entry is required for {name}")
            if len(found) == 1:
                self.expect(scalar(found[0], "type") == "copper"
                            and abs(number(found[0], "thickness") - 0.070) <= EPS,
                            "COPPER_WEIGHT", f"{name} must remain 0.070 mm copper", found[0])
        thicknesses = [number(n, "thickness", 0.0) for n in stack.children("layer")]
        self.measurements["stackup_total_mm"] = round(sum(thicknesses), 6)
        # This was an explicitly reviewed mismatch, not evidence of a different fabricated board.
        if abs(sum(thicknesses) - 1.6) > EPS:
            self.diagnostics.append({"code": "STACKUP_RECONCILIATION", "severity": "warning",
                                     "message": "saved stackup total differs from nominal 1.60 mm; "
                                     "reconcile the quote/finished-thickness definition",
                                     "file": stack.source, "line": stack.line,
                                     "measured_mm": round(sum(thicknesses), 6)})
        for field in self.board.children("net"):
            code, name = field.atoms(2)
            if not code.isascii() or not code.isdigit() or int(code) in self.nets or name in self.nets.values():
                field.fail("invalid or duplicate net table entry")
            self.nets[int(code)] = str(name)
        self.expect(self.nets.get(0) == "" and set(RAILS) | {"EARTH", "LED_A_POS", "LED_C_POS"}
                    <= set(self.nets.values()), "REQUIRED_NETS", "protected named nets or empty net 0 missing")
        for child in self.board.children():
            if child.tag == "footprint":
                self.attempt(self.read_footprint, child)
            elif child.tag == "segment":
                self.attempt(self.read_track, child)
            elif child.tag == "via":
                self.attempt(self.read_via, child)
            elif child.tag in ("arc", "zone"):
                self.error("UNSUPPORTED_GEOMETRY", f"({child.tag} ...) requires an explicit geometry implementation", child)
            elif child.tag.startswith("gr_") or child.tag in ("dimension", "target"):
                self.attempt(self.read_graphic, child)

    def read_footprint(self, fp):
        schema(fp, {"layer", "uuid", "tstamp", "at", "property", "path", "sheetname", "sheetfile",
                    "descr", "tags", "attr", "locked", "placed", "tedit", "version", "generator",
                    "generator_version", "autoplace_cost90", "autoplace_cost180", "solder_mask_margin",
                    "solder_paste_margin", "solder_paste_ratio", "clearance",
                    "zone_connect", "thermal_width", "thermal_gap", "pad", "fp_text", "fp_text_box",
                    "fp_line", "fp_rect", "fp_circle", "fp_poly", "fp_arc", "fp_curve", "model",
                    "embedded_fonts", "embedded_files", "private_layers", "net_tie_pad_groups"}, 1,
               flags=("locked", "placed"))
        refs = [p for p in fp.children("property") if p.values and p.values[0] == "Reference"]
        if len(refs) != 1 or len(refs[0].values) < 2 or not isinstance(refs[0].values[1], Atom):
            fp.fail("expected exactly one Reference property")
        ref = str(refs[0].values[1])
        if not ref or ref in self.footprints:
            fp.fail("empty or duplicate footprint reference")
        self.footprints[ref] = fp
        if scalar(fp, "layer") != "F.Cu":
            raise Unsupported(f"{ref}: back-side/flipped footprints are not supported", fp)
        origin, angle = position(fp)
        for prop in fp.children("property"):
            if prop.one("layer", required=False) and scalar(prop, "layer") in CRITICAL_LAYERS:
                raise Unsupported(f"{ref}: property text on a geometry-bearing layer", prop)
        for child in fp.children():
            if child.tag == "pad":
                self.attempt(self.read_pad, child, fp, ref, origin, angle)
            elif child.tag.startswith("fp_"):
                self.attempt(self.read_graphic, child, origin, angle, ref)

    def margin(self, pad, fp, key, setup_key):
        for owner in (pad, fp, self.setup):
            field = owner.one(setup_key if owner is self.setup else key, required=False)
            if field is not None:
                return numeric(field.atoms(1)[0], field)
        return 0.0

    def read_pad(self, pad, fp, ref, origin, angle):
        schema(pad, {"at", "size", "drill", "layers", "net", "uuid", "tstamp", "locked",
                     "remove_unused_layers", "keep_end_layers", "roundrect_rratio", "solder_mask_margin",
                     "solder_paste_margin", "solder_paste_margin_ratio", "clearance", "zone_connect",
                     "thermal_bridge_width", "thermal_gap", "thermal_bridge_angle", "pinfunction",
                     "pintype", "property", "die_length", "zone_layer_connections", "teardrops"}, 3,
               flags=("locked",))
        padnum, kind, shape_kind = pad.values[:3]
        if kind not in ("thru_hole", "np_thru_hole", "smd", "connect"):
            raise Unsupported(f"{ref}.{padnum}: unsupported pad type {kind}", pad)
        if shape_kind not in ("circle", "rect", "roundrect", "oval"):
            raise Unsupported(f"{ref}.{padnum}: unsupported pad shape {shape_kind}", pad)
        if boolean(pad, "remove_unused_layers") and not boolean(pad, "keep_end_layers"):
            raise Unsupported("connectivity-dependent removal of outer pad copper is unsupported", pad)
        local, pad_angle = position(pad)
        center = move(local, origin, angle)
        # KiCad serializes pad orientation in board axes, but pad position in footprint axes.
        size = point(pad, "size")
        ratio = number(pad, "roundrect_rratio", 0.25)
        if min(size) <= 0 or not 0 <= ratio <= 0.5:
            pad.fail("nonpositive pad dimensions or invalid roundrect ratio")
        layers = self.layer_set(pad)
        net = self.net(pad, required=False)
        offset = (0.0, 0.0)
        hole = None
        drill = pad.one("drill", required=False)
        if drill:
            schema(drill, {"offset"}, len([v for v in drill.values if isinstance(v, Atom)]))
            values = [v for v in drill.values if isinstance(v, Atom)]
            if len(values) == 1:
                d = numeric(values[0], drill)
                dims = (d, d)
            elif len(values) == 3 and values[0] == "oval":
                dims = tuple(numeric(v, drill) for v in values[1:])
            else:
                drill.fail("unsupported drill definition")
            if min(dims) <= 0 or max(dims) > 2147.483647:
                drill.fail("nonpositive or out-of-range hole diameter")
            hole = pad_shape("oval", dims, center, pad_angle)
            if drill.one("offset", required=False):
                offset = point(drill, "offset")
        if (kind in ("thru_hole", "np_thru_hole")) != bool(hole):
            pad.fail("pad type and drill presence disagree")
        copper_center = move(offset, center, pad_angle)
        try:
            shape = pad_shape(shape_kind, size, copper_center, pad_angle, ratio)
        except ValueError as exc:
            pad.fail(str(exc))
        item = Item(pad, f"{ref}.{padnum or '<aperture/hole>'}", shape, layers, net, kind,
                    ref, str(padnum), center, hole)
        self.pads.append(item)
        if kind == "thru_hole" and not CU <= layers:
            pad.fail("component PTH pad must retain both outer copper layers")
        if net and not layers & CU:
            pad.fail("a netted electrical pad cannot consist only of technical apertures")
        if kind == "np_thru_hole":
            if net or not hole or not (hole.contains(shape) and shape.contains(hole)):
                raise Unsupported("NPTH pads must be unnetted and have no extra copper annulus", pad)
        elif layers & CU:
            if kind in ("smd", "connect") and len(layers & CU) != 1:
                pad.fail("SMT copper pad must have exactly one copper layer")
            self.copper.append(item)
        for layer in layers & (MASK | PASTE):
            has_copper = bool(layers & CU)
            if layer in MASK:
                mx = my = self.margin(pad, fp, "solder_mask_margin", "pad_to_mask_clearance") if has_copper else 0
            else:
                margin = self.margin(pad, fp, "solder_paste_margin", "pad_to_paste_clearance") if has_copper else 0
                # Footprint syntax uses solder_paste_ratio; pad syntax uses ..._margin_ratio.
                ratio_field = pad.one("solder_paste_margin_ratio", required=False)
                if ratio_field is None:
                    ratio_field = fp.one("solder_paste_ratio", required=False)
                if ratio_field is None:
                    ratio_field = self.setup.one("pad_to_paste_clearance_ratio", required=False)
                paste_ratio = numeric(ratio_field.atoms(1)[0], ratio_field) if ratio_field and has_copper else 0
                mx, my = margin + size[0] * paste_ratio, margin + size[1] * paste_ratio
            aperture_size = (size[0] + 2 * mx, size[1] + 2 * my)
            if not all(math.isfinite(v) and abs(v) <= 2147.483647 for v in aperture_size):
                pad.fail("aperture size exceeds KiCad's dimensional range")
            if min(aperture_size) <= EPS:
                self.error("EMPTY_APERTURE", f"{item.label}: {layer} aperture vanishes", pad)
                continue
            try:
                aperture_ratio = ratio
                if shape_kind == "roundrect" and layer in MASK and number(self.setup, "solder_mask_min_width", 0.0):
                    # The mask-merging path offsets polygons instead of resizing flashes.
                    # The smaller corner radius encloses both possible constructions.
                    aperture_ratio = min(ratio, max(0.0, ratio * min(size) + mx) / min(aperture_size))
                aperture = pad_shape(shape_kind, aperture_size, copper_center, pad_angle, aperture_ratio,
                                     rect_radius=max(0.0, mx) if shape_kind == "rect" else 0)
            except ValueError as exc:
                raise Unsupported(f"{item.label}: {layer}: {exc}", pad) from exc
            self.apertures.append(Item(pad, item.label, aperture, frozenset((layer,)), net, kind,
                                       ref, str(padnum), center))

    def read_track(self, node):
        schema(node, {"start", "end", "width", "layer", "net", "uuid", "tstamp", "locked"},
               flags=("locked",))
        start, end, width = point(node, "start"), point(node, "end"), number(node, "width")
        layers = self.layer_set(node, "layer")
        if not layers <= CU or width <= 0:
            node.fail("track must have positive width on a copper layer")
        item = Item(node, f"track@{node.line}", Shape((start, end), width / 2), layers,
                    self.net(node), "segment")
        self.copper.append(item)
        self.tracks.append(item)
        self.expect(width >= PROJECT_MINIMA["min_track_width"] - EPS, "TRACK_WIDTH",
                    "track below two-layer/2 oz nominal minimum", node, measured_mm=width,
                    required_mm=PROJECT_MINIMA["min_track_width"])

    def tented(self, via, side):
        for owner in (via, self.setup):
            field = owner.one("tenting", required=False)
            if field is None:
                continue
            if field.children():
                schema(field, {"front", "back"})
                if field.one(side, required=False) is not None:
                    return boolean(field, side)
            else:
                values = field.atoms()
                if len(values) != len(set(values)) or any(v not in ("front", "back") for v in values):
                    field.fail("invalid tenting flags")
                return side in values
        raise Unsupported(f"cannot resolve {side} via tenting from source settings", via)

    def read_via(self, node):
        schema(node, {"at", "size", "drill", "layers", "net", "uuid", "tstamp", "locked", "free",
                      "remove_unused_layers", "keep_end_layers", "tenting", "solder_mask_margin",
                      "covering", "plugging", "filling", "capping", "teardrops"}, flags=("locked",))
        if boolean(node, "remove_unused_layers") and not boolean(node, "keep_end_layers"):
            raise Unsupported("connectivity-dependent removal of via copper is unsupported", node)
        center, angle = position(node)
        size, drill = number(node, "size"), number(node, "drill")
        layers = self.layer_set(node)
        if min(size, drill) <= 0 or layers != CU or angle:
            node.fail("only positive round F.Cu/B.Cu through vias are supported")
        item = Item(node, f"via@({center[0]:g},{center[1]:g})", Shape((center,), size / 2), layers,
                    self.net(node), "via", center=center, hole=Shape((center,), drill / 2))
        self.vias.append(item)
        self.copper.append(item)
        self.expect((size - drill) / 2 >= 0.1 - EPS, "VIA_RING", f"{item.label}: via nominal ring below 0.10 mm", node)
        for side, layer in (("front", "F.Mask"), ("back", "B.Mask")):
            if not self.tented(node, side):
                field = node.one("solder_mask_margin", required=False)
                margin = numeric(field.atoms(1)[0], field) if field else number(self.setup, "pad_to_mask_clearance", 0.0)
                if size / 2 + margin <= 0:
                    raise Unsupported("nonpositive untented via mask aperture", node)
                self.apertures.append(Item(node, item.label, Shape((center,), size / 2 + margin),
                                           frozenset((layer,)), item.net, "via", center=center))

    def read_graphic(self, node, origin=(0.0, 0.0), angle=0.0, ref=""):
        layers = self.layer_set(node, "layer")
        if not layers & CRITICAL_LAYERS:
            return
        kind = node.tag.removeprefix("fp_").removeprefix("gr_")
        if kind not in ("line", "rect", "circle", "poly"):
            raise Unsupported(f"{node.tag} on {sorted(layers)} is unsupported", node)
        schema(node, {"start", "end", "center", "pts", "stroke", "fill", "layer", "uuid", "tstamp",
                      "locked", "net", "status"}, flags=("locked",))
        stroke = node.one("stroke")
        schema(stroke, {"width", "type"})
        width = number(stroke, "width")
        if width < 0 or scalar(stroke, "type") != "solid":
            raise Unsupported("negative or non-solid geometry stroke", node)
        fill = scalar(node, "fill", "no")
        if fill not in ("no", "none", "solid", "yes"):
            raise Unsupported(f"unknown graphic fill {fill}", node)
        filled = fill in ("solid", "yes")
        if kind == "circle":
            center, end = point(node, "center"), point(node, "end")
            if not filled or "Edge.Cuts" in layers:
                raise Unsupported("unfilled circles on geometry-bearing layers are unsupported", node)
            shapes = [Shape((move(center, origin, angle),), math.dist(center, end) + width / 2)]
        else:
            if kind == "poly":
                pts = node.one("pts")
                schema(pts, {"xy"})
                coords = [tuple(numeric(v, n) for v in n.atoms(2)) for n in pts.children("xy")]
                if any(abs(v) > 2147.483647 for xy in coords for v in xy):
                    pts.fail("polygon exceeds KiCad's dimensional range")
                if len(coords) < 3:
                    pts.fail("polygon requires at least three points")
                if coords[0] == coords[-1]:
                    coords.pop()
            else:
                a, b = point(node, "start"), point(node, "end")
                coords = [a, b] if kind == "line" else [a, (b[0], a[1]), b, (a[0], b[1])]
            coords = tuple(move(p, origin, angle) for p in coords)
            if "Edge.Cuts" in layers:
                if kind not in ("line", "rect") or filled:
                    raise Unsupported("outline must use unfilled rectangles or straight lines", node)
                self.outline.extend(edges(coords))
                return
            if filled and kind != "line":
                area2 = sum(a[0] * b[1] - a[1] * b[0] for a, b in edges(coords))
                if len(set(coords)) != len(coords) or abs(area2) <= EPS * EPS \
                        or not all(inside(p, coords) for p in coords):
                    raise Unsupported("only simple convex filled polygons are supported", node)
                shapes = [Shape(coords, width / 2)]
            else:
                if width <= 0:
                    node.fail("unfilled geometry must have positive stroke width")
                shapes = [Shape((a, b), width / 2) for a, b in edges(coords)]
        for shape in shapes:
            item = Item(node, f"{ref + ':' if ref else ''}{node.tag}@{node.line}", shape, layers,
                        self.net(node, required=False), "graphic", ref)
            if layers & CU:
                self.copper.append(item)
            if layers & (MASK | PASTE):
                self.apertures.append(item)

    def required_pad(self, ref, number_):
        found = [p for p in self.pads if p.reference == ref and p.pad_number == number_]
        if len(found) != 1:
            self.error("REQUIRED_PAD", f"expected exactly one {ref}.{number_} pad, found {len(found)}")
            return None
        return found[0]

    def pad_at_net(self, ref, num, xy, net, code):
        pad = self.required_pad(ref, num)
        if pad:
            self.expect(math.dist(pad.center, xy) <= EPS and pad.net == net and pad.kind == "thru_hole",
                        code, f"{ref}.{num} must be PTH at {xy} on {net}", pad.node,
                        position_mm=list(pad.center), net=pad.net)
        return pad

    def run_covered(self, start, end, width, net, layer):
        axis = 0 if abs(start[1] - end[1]) <= EPS else 1
        other = 1 - axis
        low, high = sorted((start[axis], end[axis]))
        intervals = []
        for track in self.tracks:
            a, b = track.shape.core
            if track.net == net and layer in track.layers and track.shape.radius * 2 >= width - EPS \
                    and abs(a[other] - start[other]) <= EPS and abs(b[other] - start[other]) <= EPS:
                intervals.append(sorted((a[axis], b[axis])))
        for a, b in sorted(intervals):
            if a > low + EPS:
                break
            low = max(low, b)
        return low >= high - EPS

    def check_guardrails(self):
        x0, y0, x1, y1 = BOARD_BOUNDS
        wanted = [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)),
                  ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]
        # Outline subdivision is harmless; internal slots and extra contours are not.
        coverage = [[] for _ in wanted]
        for a, b in self.outline:
            assigned = False
            for index, (p, q) in enumerate(wanted):
                if point_segment(a, p, q) <= EPS and point_segment(b, p, q) <= EPS and math.dist(a, b) > EPS:
                    axis = 0 if p[1] == q[1] else 1
                    coverage[index].append(sorted((a[axis], b[axis])))
                    assigned = True
            self.expect(assigned, "BOARD_OUTLINE", "outline contains an extra/changed edge or internal cutout")
        for (p, q), intervals in zip(wanted, coverage):
            axis = 0 if p[1] == q[1] else 1
            low, high = sorted((p[axis], q[axis]))
            for a, b in sorted(intervals):
                if a > low + EPS:
                    break
                low = max(low, b)
            self.expect(low >= high - EPS, "BOARD_OUTLINE", "63 x 56 mm protected board outline is incomplete")

        protected = []
        for xy, net in PROTECTED_VIAS.items():
            found = [v for v in self.vias if math.dist(v.center, xy) <= EPS]
            good = len(found) == 1 and found[0].net == net and found[0].layers == CU \
                and abs(found[0].shape.radius - 0.9) <= EPS and abs(found[0].hole.radius - 0.5) <= EPS
            self.expect(good, "PROTECTED_VIA", f"require one {net} through via at {xy}, drill 1.0 / pad 1.8 mm",
                        found[0].node if found else None, position_mm=list(xy), net=net)
            protected.append({"position_mm": list(xy), "net": net, "ok": good})
        self.measurements["protected_vias"] = protected
        self.measurements["via_count"] = len(self.vias)

        for net, y in RAILS.items():
            for layer in CU:
                runs = [((106.0, y), (131.0, y))]
                if net != "WIRE_B":
                    runs.append(((131.0, y), (131.0, 113.5 if net == "WIRE_A" else 131.5)))
                for a, b in runs:
                    self.expect(self.run_covered(a, b, 3.2, net, layer), "RAIL_GEOMETRY",
                                f"{net} requires continuous >=3.2 mm rail {a} to {b} on {layer}")
        for y, end_y in ((107.2, 103.0), (137.8, 142.0)):
            for a, b in (((135.5, 122.5), (135.5, y)), ((135.5, y), (148.04, y)),
                         ((148.04, y), (148.04, end_y)), ((131.0, 122.5), (135.5, 122.5))):
                self.expect(self.run_covered(a, b, 1.6, "WIRE_B", "B.Cu"), "B_RETURN_GEOMETRY",
                            f"protected B-return >=1.6 mm run {a} to {b} on B.Cu is missing")

        bus = pad_shape("roundrect", (13.26, 22.5), (150.62, 122.5), 0, 2.25 / 13.26)
        for item in self.copper:
            if item.net == "EARTH":
                self.expect(bus.contains(item.shape), "EARTH_BOUNDS",
                            f"{item.label}: EARTH copper leaves the protected rounded bus envelope", item.node)
        for layer in CU:
            perimeter = [((146.24, 113.5), (155.0, 113.5)), ((146.24, 131.5), (155.0, 131.5)),
                         ((146.24, 113.5), (146.24, 131.5)), ((155.0, 113.5), (155.0, 131.5))]
            for a, b in perimeter:
                self.expect(self.run_covered(a, b, 4.5, "EARTH", layer), "EARTH_GEOMETRY",
                            f"{layer}: missing full-width earth perimeter run {a} to {b}")
            strips = []
            for item in self.tracks:
                if item.net != "EARTH" or layer not in item.layers:
                    continue
                a, b = item.shape.core
                r = item.shape.radius
                if abs(a[0] - b[0]) <= EPS:
                    strips.append((a[0] - r, min(a[1], b[1]), a[0] + r, max(a[1], b[1])))
                elif abs(a[1] - b[1]) <= EPS:
                    strips.append((min(a[0], b[0]), a[1] - r, max(a[0], b[0]), a[1] + r))
            xs = sorted({146.24, 155.0} | {max(146.24, min(155.0, r[i])) for r in strips for i in (0, 2)})
            solid = True
            for left, right in zip(xs, xs[1:]):
                if right - left <= EPS:
                    continue
                y = 113.5
                intervals = sorted((r[1], r[3]) for r in strips if r[0] <= left + EPS and r[2] >= right - EPS)
                for low, high in intervals:
                    if low > y + EPS:
                        break
                    y = max(y, high)
                solid &= y >= 131.5 - EPS
            self.expect(solid, "EARTH_CONTINUITY", f"{layer}: earth track strips do not prove a slit-free solid bus")

        for index, (net, y) in enumerate(RAILS.items(), 1):
            self.pad_at_net("J_IN", str(index), (106.0, y), net, "INPUT_TERMINAL")
        for index, y in enumerate((130.12, 122.5, 114.88), 1):
            self.pad_at_net("J_EARTH", str(index), (155.0, y), "EARTH", "EARTH_TERMINAL")
        for ref, y, angle, positive in (("J_LED_A", 103.0, 90, "LED_A_POS"),
                                         ("J_LED_C", 142.0, 270, "LED_C_POS")):
            fp = self.footprints.get(ref)
            if fp:
                xy, rotation = position(fp)
                self.expect(math.dist(xy, (145.5, y)) <= EPS and abs(rotation - angle) <= EPS,
                            "LED_ORIENTATION", f"{ref}: outward-facing origin/rotation must be preserved", fp)
            self.pad_at_net(ref, "1", (142.96, y), positive, "LED_POLARITY")
            self.pad_at_net(ref, "2", (148.04, y), "WIRE_B", "LED_POLARITY")
        for ref, y, net in (("GDT_A_E", 113.5, "WIRE_A"), ("GDT_B_E", 122.5, "WIRE_B"),
                            ("GDT_C_E", 131.5, "WIRE_C")):
            fp = self.footprints.get(ref)
            if fp:
                xy, _ = position(fp)
                self.expect(math.dist(xy, (138.62, y)) <= EPS, "EARTH_GDT_PITCH",
                            f"{ref}: preserve body centre and 9.00 mm pitch", fp)
            self.pad_at_net(ref, "1", (131.0, y), net, "EARTH_GDT_PITCH")
            self.pad_at_net(ref, "2", (146.24, y), "EARTH", "EARTH_GDT_PITCH")
        self.pad_at_net("GDT_AC", "1", (125.8, 114.88), "WIRE_A", "GDT_OVERPASS")
        self.pad_at_net("GDT_AC", "2", (125.8, 130.12), "WIRE_C", "GDT_OVERPASS")
        for ref, nets in (("GDT_AB", ("WIRE_A", "WIRE_B")), ("GDT_BC", ("WIRE_B", "WIRE_C"))):
            for num, net in enumerate(nets, 1):
                item = self.required_pad(ref, str(num))
                if item:
                    self.expect(item.kind == "smd" and item.net == net and item.layers & CU == {"F.Cu"},
                                "SMT_GDT_PAD", f"{ref}.{num}: top SMT pad on {net} required", item.node)
        for ref in ("D1", "D2"):
            for num in ("1", "2"):
                pad = self.required_pad(ref, num)
                if pad:
                    drill = 2 * pad.hole.radius if pad.hole else 0
                    self.expect(pad.kind == "thru_hole" and drill >= 1.1 - EPS, "C1_DIODE_DRILL",
                                f"{ref}.{num}: diode hole must be >=1.10 mm", pad.node,
                                issue="C1", measured_mm=round(drill, 6), required_mm=1.1)
        rings = []
        for item in self.pads:
            if item.kind == "thru_hole" and item.hole:
                ring = min(-item.shape.signed_distance(p) - item.hole.radius for p in item.hole.core)
                rings.append({"pad": item.label, "nominal_ring_mm": round(ring, 6)})
                self.expect(ring >= 0.254 - EPS, "COMPONENT_RING", f"{item.label}: nominal PTH ring below 0.254 mm",
                            item.node, measured_mm=round(ring, 6), required_mm=0.254)
        self.measurements["component_rings"] = rings
        self.attempt(self.check_mounts)

    def check_mounts(self):
        npth = [p for p in self.pads if p.kind == "np_thru_hole"]
        self.expect(len(npth) == 4, "MOUNTING_HOLES", "exactly four protected NPTH mounting holes required")
        for ref, xy in MOUNTS.items():
            holes = [p for p in npth if p.reference == ref]
            good = len(holes) == 1 and math.dist(holes[0].center, xy) <= EPS \
                and len(holes[0].hole.core) == 1 and abs(holes[0].hole.radius - 1.6) <= EPS
            self.expect(good, "MOUNTING_HOLES", f"{ref}: require 3.2 mm NPTH mounting hole at {xy}")
            fp = self.footprints.get(ref)
            if fp:
                origin, angle = position(fp)
                for layer in ("F.CrtYd", "B.CrtYd"):
                    circles = [n for n in fp.children("fp_circle") if scalar(n, "layer") == layer]
                    valid = any(math.dist(move(point(n, "center"), origin, angle), xy) <= EPS
                                and math.dist(point(n, "center"), point(n, "end")) >= 3.45 - EPS for n in circles)
                    self.expect(valid, "MOUNTING_COURTYARD", f"{ref}: preserve >=3.45 mm circular {layer} keepout", fp)
            keepout = Shape((xy,), 3.45)
            for item in self.copper:
                if keepout.gap(item.shape) <= EPS:
                    self.error("MOUNTING_CLEARANCE", f"{item.label}: copper enters {ref} mechanical keepout", item.node)

    def check_clearances(self):
        earth = [c for c in self.copper if c.net == "EARTH"]
        fence = [c for c in self.copper if c.net != "EARTH"]
        minimum = math.inf
        for a, b in itertools.product(earth, fence):
            if not a.layers & b.layers & CU:
                continue
            gap = a.shape.gap(b.shape)
            minimum = min(minimum, gap)
            self.expect(gap >= 3.0 - EPS, "EARTH_CLEARANCE", f"{a.label} to {b.label}: fence-to-earth copper below 3.0 mm",
                        b.node, measured_mm=round(gap, 6), required_mm=3.0,
                        items=[a.label, b.label], layers=sorted(a.layers & b.layers & CU))
        self.measurements["minimum_fence_earth_clearance_mm"] = round(minimum, 6) if math.isfinite(minimum) else None
        x0, y0, x1, y1 = BOARD_BOUNDS
        for item in self.copper:
            a, b, c, d = item.shape.bounds
            gap = min(a - x0, b - y0, x1 - c, y1 - d)
            self.expect(gap >= 0.5 - EPS, "COPPER_EDGE", f"{item.label}: copper-to-outline below 0.50 mm", item.node,
                        measured_mm=round(gap, 6), required_mm=0.5)
        holes = [p for p in self.pads + self.vias if p.hole]
        for a, b in itertools.combinations(holes, 2):
            gap = a.hole.gap(b.hole)
            self.expect(gap >= 0.25 - EPS, "HOLE_CLEARANCE", f"{a.label} to {b.label}: hole-to-hole below 0.25 mm",
                        a.node, measured_mm=round(gap, 6), required_mm=0.25)

    def check_apertures(self):
        merge = number(self.setup, "solder_mask_min_width", 0.0)
        if merge < 0:
            self.setup.fail("negative solder_mask_min_width")
        self.measurements["mask_barrier_minimum_mm"] = MIN_MASK_BARRIER
        self.measurements["mask_merge_envelope_inflation_mm"] = merge / 2
        records = []
        for via in self.vias:
            for opening in self.apertures:
                if opening.node is via.node:
                    continue
                for layer in opening.layers & (MASK | PASTE):
                    aperture = opening.shape.inflate(merge / 2) if layer in MASK else opening.shape
                    hole_gap = aperture.signed_distance(via.center) - via.hole.radius
                    annulus_gap = aperture.signed_distance(via.center) - via.shape.radius
                    related = [p for p in self.pads if p.node is opening.node and p.layers & CU]
                    copper_gap = min((p.shape.signed_distance(via.center) - via.hole.radius for p in related), default=None)
                    own = next((p for p in self.apertures if p.node is via.node and layer in p.layers), None)
                    barrier = hole_gap
                    if layer in MASK and own:
                        barrier = min(hole_gap, own.shape.inflate(merge / 2).gap(aperture))
                    if hole_gap < 2.0:
                        records.append({"via": via.label, "position_mm": list(via.center), "aperture": opening.label,
                                        "layer": layer, "hole_gap_mm": round(hole_gap, 6),
                                        "copper_hole_gap_mm": round(copper_gap, 6) if copper_gap is not None else None,
                                        "annulus_gap_mm": round(annulus_gap, 6), "annulus_exposed": annulus_gap < -EPS,
                                        "mask_barrier_mm": round(barrier, 6) if layer in MASK else None,
                                        "own_via_mask_opening": bool(own)})
                    if layer in MASK:
                        self.expect(hole_gap >= -EPS, "W1_VIA_MASK", f"{via.label}: drill circle intersects {opening.label} {layer}",
                                    opening.node, issue="W1", position_mm=list(via.center), measured_mm=round(hole_gap, 6),
                                    aperture=opening.label, layer=layer)
                        if hole_gap >= -EPS:
                            self.expect(barrier >= MIN_MASK_BARRIER - EPS, "W1_MASK_BARRIER",
                                        f"{via.label}: mask barrier to {opening.label} {layer} below {MIN_MASK_BARRIER:.2f} mm",
                                        opening.node, issue="W1", measured_mm=round(barrier, 6),
                                        required_mm=MIN_MASK_BARRIER, position_mm=list(via.center), layer=layer)
                    else:
                        self.expect(hole_gap >= -EPS, "W1_VIA_PASTE", f"{via.label}: drill circle intersects {opening.label} {layer}",
                                    opening.node, issue="W1", measured_mm=round(hole_gap, 6),
                                    position_mm=list(via.center), aperture=opening.label, layer=layer)
        self.measurements["via_apertures"] = records
        # Separate mask/paste-only pads or graphics are permitted, but deleting every
        # aperture must not turn a non-solderable SMT pad into a successful W1 check.
        for pad in self.pads:
            if pad.kind != "smd" or not pad.layers & CU:
                continue
            side = "F" if "F.Cu" in pad.layers else "B"
            for layer in (f"{side}.Mask", f"{side}.Paste"):
                found = any(layer in a.layers and a.kind != "via" and a.shape.overlaps(pad.shape)
                            for a in self.apertures)
                self.expect(found, "MISSING_SMT_APERTURE", f"{pad.label}: no intersecting {layer} aperture", pad.node)

    def check_project(self, project, source):
        settings = project.get("board", {}).get("design_settings", {})
        rules = settings.get("rules", {})
        for key, minimum in PROJECT_MINIMA.items():
            value = rules.get(key)
            try:
                good = isinstance(value, (int, float)) and not isinstance(value, bool) \
                    and numeric(value) >= minimum - EPS
            except ValueError:
                good = False
            if not good:
                self.diagnostics.append({"code": "PROJECT_RULE", "severity": "error", "file": source,
                                         "message": f"project {key} must be >= {minimum:g} mm",
                                         "setting": key, "required_mm": minimum, "actual": value})
        severities = settings.get("rule_severities", {})
        for key in REQUIRED_ERROR_RULES + REQUIRED_VISIBLE_RULES:
            accepted = ("error",) if key in REQUIRED_ERROR_RULES else ("error", "warning")
            if severities.get(key) not in accepted:
                self.diagnostics.append({"code": "PROJECT_SEVERITY", "severity": "error", "file": source,
                                         "message": f"project check {key} must remain {'/'.join(accepted)}",
                                         "setting": key, "actual": severities.get(key)})
        if settings.get("drc_exclusions", []) != []:
            self.diagnostics.append({"code": "PROJECT_EXCLUSIONS", "severity": "error", "file": source,
                                     "message": "DRC exclusions are not accepted by this focused guardrail checker"})

    def check_rules(self, nodes):
        if nodes[0].tag != "version" or nodes[0].atoms() != ["1"]:
            nodes[0].fail("custom rules must start with (version 1)")
        relevant = {"clearance": [], "annular_width": []}
        for rule in nodes[1:]:
            if rule.tag != "rule":
                rule.fail("unexpected custom-rule root")
            schema(rule, {"condition", "constraint", "layer", "severity"}, 1)
            if not rule.children("constraint"):
                rule.fail("rule has no constraints")
            seen = set()
            for constraint in rule.children("constraint"):
                if not constraint.values or not isinstance(constraint.values[0], Atom):
                    constraint.fail("missing constraint type")
                kind = str(constraint.values[0])
                if kind in seen:
                    constraint.fail("duplicate constraint type within a rule")
                seen.add(kind)
                if kind not in relevant:
                    continue  # Native KiCad compiles and enforces the other constraints.
                schema(constraint, {"min", "opt", "max"}, 1)
                condition_node = rule.one("condition", required=False)
                tree = condition(condition_node.atoms(1)[0], condition_node) if condition_node else None
                if kind == "annular_width" and tree is not None:
                    # Native unary checks bind A=item, B=null; inspect even inactive branches.
                    pending = [tree]
                    while pending:
                        part = pending.pop()
                        if part[0] == "property" and part[1].startswith("B."):
                            raise Unsupported("annular_width is unary (A=item, B=null); "
                                              "B-dependent conditions are unsupported", condition_node)
                        pending.extend(child for child in part[1:] if isinstance(child, tuple))
                value = constraint.one("min", required=False)
                minimum = rule_dimension(value) if value else 0.0
                layer = str(scalar(rule, "layer", "*"))
                if layer not in ("*", "outer", "inner") and layer not in self.layers:
                    raise Unsupported(f"unsupported rule layer {layer}", rule)
                severity = str(scalar(rule, "severity", "error"))
                if severity not in ("error", "warning", "ignore", "exclusion"):
                    rule.fail("unknown rule severity")
                relevant[kind].append((rule, tree, minimum, layer, severity))

        def covered(kind, a, b, layer, required):
            ap = a.properties(layer)
            bp = b.properties(layer) if b is not None else None
            for rule, tree, minimum, rule_layer, severity in reversed(relevant[kind]):
                if rule_layer not in ("*", "outer", layer):
                    continue
                if matches(tree, ap, bp) or (b is not None and matches(tree, bp, ap)):
                    return minimum >= required - EPS and severity in ("error", "warning")
            return False

        for kind in relevant:
            self.expect(bool(relevant[kind]), "MISSING_CUSTOM_RULE", f"required {kind} custom rule is missing", nodes[0])
        for pad in self.pads:
            if pad.kind == "thru_hole":
                for layer in CU:
                    self.expect(covered("annular_width", pad, None, layer, 0.254), "CUSTOM_RULE_COVERAGE",
                                f"{pad.label} on {layer}: effective component ring rule must be >=0.254 mm", nodes[0])
        failures = set()
        for a, b in itertools.product((c for c in self.copper if c.net == "EARTH"),
                                      (c for c in self.copper if c.net != "EARTH")):
            for layer in a.layers & b.layers & CU:
                if not covered("clearance", a, b, layer, 3.0):
                    failures.add((layer, a.net, a.kind, b.net, b.kind))
        for layer, anet, akind, bnet, bkind in sorted(failures):
            self.error("CUSTOM_RULE_COVERAGE", f"effective earth separation rule missing/weakened for "
                       f"{anet} {akind} to {bnet or '<unnetted>'} {bkind} on {layer}", nodes[0], required_mm=3.0)


def strict_json(text):
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ValueError(f"duplicate JSON key {key!r}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"non-finite JSON value {value}")

    result = json.loads(text, object_pairs_hook=pairs, parse_constant=constant, parse_float=numeric)
    if not isinstance(result, dict):
        raise ValueError("project must be a JSON object")
    for route in (("board",), ("board", "design_settings"), ("board", "design_settings", "rules"),
                  ("board", "design_settings", "rule_severities")):
        obj = result
        for key in route:
            obj = obj.get(key) if isinstance(obj, dict) else None
        if not isinstance(obj, dict) or not obj:
            raise ValueError(f"project is missing nonempty {'.'.join(route)}")
    return result


def check_sources(pcb_text, project_text, rules_text, paths=None):
    """Check supplied source snapshots; tests use controlled copies of the real PCB."""
    paths = paths or {"pcb": "<pcb>", "project": "<project>", "rules": "<rules>"}
    report = {"schema_version": 1, "check": "physical_geometry", "ok": False, "status": "fail",
              "diagnostics": [], "measurements": {}, "limitations": LIMITATIONS,
              "qualification": {"physical_fit": "not_verified", "via_covering_cam": "not_verified",
                                "assembly_standoff": "not_verified", "surge_rating": "not_verified"}}
    parsed = {}
    for name, text in (("pcb", pcb_text), ("project", project_text), ("rules", rules_text)):
        try:
            if text is None:
                raise ValueError("required source file is missing or unreadable")
            parsed[name] = strict_json(text) if name == "project" else parse_many(text, paths[name]) \
                if name == "rules" else parse(text, paths[name], root="kicad_pcb")
        except (SExprError, ValueError) as exc:
            report["diagnostics"].append({"code": "INPUT_" + name.upper(), "severity": "error",
                                           "file": paths[name], "message": str(exc)})
    if "pcb" in parsed:
        try:
            checker = GeometryCheck(parsed["pcb"])
        except SExprError as exc:
            report["diagnostics"].append({"code": "INVALID_STRUCTURE", "severity": "error",
                                           "file": paths["pcb"], "message": str(exc)})
        else:
            checker.attempt(checker.read_board)
            for operation in (checker.check_guardrails, checker.check_clearances, checker.check_apertures):
                checker.attempt(operation)
            if "project" in parsed:
                checker.attempt(checker.check_project, parsed["project"], paths["project"])
            if "rules" in parsed:
                checker.attempt(checker.check_rules, parsed["rules"])
            report["diagnostics"].extend(checker.diagnostics)
            report["measurements"] = checker.measurements
    report["ok"] = not any(d["severity"] == "error" for d in report["diagnostics"])
    report["status"] = "pass" if report["ok"] else "fail"
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("pcb", "project", "rules", "output"):
        parser.add_argument("--" + name, type=Path, required=True)
    args = parser.parse_args(argv)
    paths = {name: getattr(args, name) for name in ("pcb", "project", "rules")}
    output = args.output
    if output.suffix.lower() != ".json":
        print("Geometry ERROR: --output must name a .json report, not a design file", file=sys.stderr)
        return 2
    if output.resolve() in {path.resolve() for path in paths.values()}:
        print("Geometry ERROR: --output must not overwrite an input", file=sys.stderr)
        return 2
    texts, inputs, errors = {}, {}, []
    for name, path in paths.items():
        try:
            data = path.read_bytes()
            texts[name] = data.decode("utf-8-sig")
            inputs[name] = {"path": str(path), "sha256": hashlib.sha256(data).hexdigest()}
        except (OSError, UnicodeError) as exc:
            texts[name] = None
            inputs[name] = {"path": str(path), "sha256": None}
            errors.append({"code": "INPUT_IO", "severity": "error", "file": str(path), "message": str(exc)})
    report = check_sources(texts["pcb"], texts["project"], texts["rules"],
                           {name: str(path) for name, path in paths.items()})
    report["inputs"] = inputs
    report["diagnostics"].extend(errors)
    suffixes = {"pcb": ".kicad_pcb", "project": ".kicad_pro", "rules": ".kicad_dru"}
    if any(path.parent.resolve() != args.pcb.parent.resolve() or path.stem != args.pcb.stem
           or path.suffix != suffixes[name] for name, path in paths.items()):
        report["diagnostics"].append({"code": "PROJECT_ASSOCIATION", "severity": "error",
                                       "message": "PCB/project/rules must share a directory and basename "
                                       "and use KiCad extensions so KiCad loads the checked settings"})
    report["ok"] = not any(d["severity"] == "error" for d in report["diagnostics"])
    report["status"] = "pass" if report["ok"] else "fail"
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
        # Publish a complete report on success AND failure, never a partial JSON file.
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=output.parent,
                                         prefix=output.name + ".", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            try:
                json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
                stream.write("\n")
                stream.flush()
                os.replace(temporary, output)
            finally:
                temporary.unlink(missing_ok=True)
    except (OSError, ValueError) as exc:
        print(f"Geometry ERROR: cannot publish JSON report: {exc}", file=sys.stderr)
        return 2
    defects = [d for d in report["diagnostics"] if d["severity"] == "error"]
    counts = Counter(d["code"] for d in defects)
    print(f"Geometry {report['status'].upper()}: {len(defects)} defect(s); report: {output}")
    for code, count in sorted(counts.items()):
        first = next(d for d in defects if d["code"] == code)
        print(f"  {code} ({count}): {first['message']}")
    print("Nominal source checks only; physical fit, via covering and CAM acceptance are not verified.")
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
