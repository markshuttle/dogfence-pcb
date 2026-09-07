#!/usr/bin/env python3
"""Extract reviewed embedded DogFence objects into deterministic local libraries.

This does not design footprints or approve fit. Edit the source objects first,
review their dimensions, then run --write. --check detects library drift without
changing files. --format-source only reformats the PCB/schematic and discards
obsolete native-font render caches; it never changes coordinates or nets.
--sync-metadata copies reviewed BOM identities to the existing electrical
instances only; it does not select parts, alter values, or change footprints.
"""

import argparse
import copy
import json
from pathlib import Path
import re
import sys
import uuid


def parse(text):
    tokens = re.compile(r'\s+|\(|\)|"(?:\\.|[^"\\])*"|[^\s()"]+')
    stack = []
    root = None
    end = 0
    for match in tokens.finditer(text):
        if match.start() != end:
            raise ValueError(f"Invalid S-expression at byte {end}")
        end = match.end()
        token = match.group()
        if token.isspace():
            continue
        if token == "(":
            node = []
            if stack:
                stack[-1].append(node)
            elif root is not None:
                raise ValueError("Multiple S-expression roots")
            else:
                root = node
            stack.append(node)
        elif token == ")":
            if not stack or not stack[-1]:
                raise ValueError("Unbalanced or empty S-expression")
            stack.pop()
        elif not stack:
            raise ValueError("Atom outside S-expression")
        else:
            stack[-1].append(token)
    if end != len(text) or stack or root is None:
        raise ValueError("Incomplete S-expression")
    return root


def children(node, name):
    return [item for item in node if isinstance(item, list) and item[0] == name]


def child(node, name):
    matches = children(node, name)
    if len(matches) != 1:
        raise ValueError(f"Expected one {name}, got {len(matches)}")
    return matches[0]


def strip(node, names):
    node[:] = [item for item in node
               if not isinstance(item, list) or item[0] not in names]
    for item in node:
        if isinstance(item, list):
            strip(item, names)


def format_node(node, depth=0):
    atoms = []
    lines = []
    for item in node:
        if isinstance(item, list):
            lines.append(format_node(item, depth + 1))
        elif lines:
            raise ValueError("Cannot format an atom following child nodes")
        else:
            atoms.append(item)
    prefix = "\t" * depth + "(" + " ".join(atoms)
    if not lines:
        return prefix + ")"
    return prefix + "\n" + "\n".join(lines) + "\n" + "\t" * depth + ")"


def footprint_definition(source):
    fp = copy.deepcopy(source)
    lib, name = json.loads(fp[1]).split(":", 1)
    if lib != "DogFence" or not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError(f"Not a local footprint: {fp[1]}")
    angle = float(child(fp, "at")[3]) if len(child(fp, "at")) > 3 else 0
    fp[1] = json.dumps(name)
    fp[:] = [item for item in fp if not isinstance(item, list)
             or item[0] not in {"at", "path", "sheetname", "sheetfile"}]
    strip(fp, {"uuid", "net", "pinfunction", "pintype", "render_cache"})
    fp.insert(2, ["version", "20241229"])
    fp.insert(3, ["generator", '"pcbnew"'])
    fp.insert(4, ["generator_version", '"9.0"'])
    for item in fp:
        if not isinstance(item, list):
            continue
        if item[0] in {"property", "fp_text", "pad"}:
            at = child(item, "at")
            absolute = float(at[3]) if len(at) > 3 else 0
            at[:] = at[:3] + [f"{(absolute - angle) % 360:g}"]
        if item[:2] == ["property", '"Reference"']:
            item[2] = '"REF**"'
    return name, fp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--format-source", action="store_true")
    mode.add_argument("--sync-metadata", action="store_true")
    args = parser.parse_args()
    project = Path(__file__).resolve().parent
    board_path = project / "pcb.kicad_pcb"
    schematic_path = project / "pcb.kicad_sch"
    board = parse(board_path.read_text())
    schematic = parse(schematic_path.read_text())
    if board[0] != "kicad_pcb" or schematic[0] != "kicad_sch":
        raise ValueError("Unexpected design root")
    if args.sync_metadata:
        if not __package__:
            sys.path.insert(0, str(project.parent))
        from scripts.manufacturing import read_bom

        bom = read_bom(project / "BOM.csv")
        for design, kind in ((board, "footprint"), (schematic, "symbol")):
            found = set()
            for instance in children(design, kind):
                props = {json.loads(p[1]): p for p in children(instance, "property")}
                if len(props) != len(children(instance, "property")):
                    raise ValueError("Duplicate instance property")
                ref = json.loads(props["Reference"][2])
                if ref not in bom:
                    continue
                row = bom[ref]
                name = json.loads(instance[1] if kind == "footprint" else props["Footprint"][2])
                if ref in found or name != row["Footprint"] or json.loads(props["Value"][2]) != row["Comment"]:
                    raise ValueError(f"BOM value/footprint/inventory mismatch: {ref}")
                found.add(ref)
                metadata = {"MPN": row["MPN"], "Manufacturer": row["Manufacturer"], "LCSC": row["LCSC Part #"],
                            "Sourcing": row.get("Sourcing", "LCSC"), "Sourcing Reference": row.get("Sourcing Reference", "")}
                if "LCSC Part #" in props:
                    metadata["LCSC Part #"] = row["LCSC Part #"]
                for key, content in metadata.items():
                    if key in props:
                        props[key][2] = json.dumps(content)
                        continue
                    at = child(instance, "at")
                    coords = ["0", "0", at[3] if len(at) > 3 else "0"] if kind == "footprint" else at[1:3] + ["0"]
                    prop = ["property", json.dumps(key), json.dumps(content), ["at", *coords]]
                    effects = ["effects", ["font", ["size", "1.27", "1.27"]]]
                    if kind == "footprint":
                        prop += [["layer", '"F.Fab"'], ["hide", "yes"],
                                 ["uuid", json.dumps(str(uuid.uuid5(uuid.NAMESPACE_URL, f"dogfence:{ref}:{key}")))]]
                        effects[1].append(["thickness", "0.15"])
                    else:
                        effects.append(["hide", "yes"])
                    prop.append(effects)
                    instance.insert(instance.index(props["Value"]) + 1, prop)
            if found != set(bom):
                raise ValueError(f"BOM references missing from {kind}: {sorted(set(bom) - found)}")
        board_path.write_text(format_node(board) + "\n")
        schematic_path.write_text(format_node(schematic) + "\n")
        print(f"Synchronized reviewed sourcing metadata for {len(bom)} PCB/schematic parts; run --write and make check")
        return
    if args.format_source:
        for path, design in ((board_path, board), (schematic_path, schematic)):
            # A native stroke font has no render cache. Do not strip live TTF data.
            def remove_native_caches(node):
                effects = children(node, "effects")
                if effects and not children(child(effects[0], "font"), "face"):
                    node[:] = [item for item in node if not isinstance(item, list)
                               or item[0] != "render_cache"]
                for item in node:
                    if isinstance(item, list):
                        remove_native_caches(item)
            remove_native_caches(design)
            path.write_text(format_node(design) + "\n")
        print("Formatted PCB/schematic; coordinates, nets and pin mappings unchanged")
        return

    definitions = {}
    for fp in children(board, "footprint"):
        name, definition = footprint_definition(fp)
        if name in definitions:
            # Ignore field placement, not sourcing identity or other field values.
            a, b = copy.deepcopy(definitions[name]), copy.deepcopy(definition)
            for candidate in (a, b):
                for prop in children(candidate, "property"):
                    prop[:] = prop[:3]
            if a != b:
                raise ValueError(f"Different geometry/metadata shares footprint name {name}")
        else:
            definitions[name] = definition
    if not definitions:
        raise ValueError("No footprints found")
    outputs = {project / "DogFence.pretty" / (name + ".kicad_mod"):
               format_node(definition) + "\n"
               for name, definition in sorted(definitions.items())}
    symbols = ["kicad_symbol_lib", ["version", "20241209"],
               ["generator", '"kicad_symbol_editor"'],
               ["generator_version", '"9.0"']]
    for source in children(child(schematic, "lib_symbols"), "symbol"):
        symbol = copy.deepcopy(source)
        lib, name = json.loads(symbol[1]).split(":", 1)
        if lib != "DogFence":
            raise ValueError(f"Not a local symbol: {symbol[1]}")
        symbol[1] = json.dumps(name)
        symbols.append(symbol)
    if len(symbols) == 4:
        raise ValueError("No symbols found")
    outputs[project / "DogFence.kicad_sym"] = format_node(symbols) + "\n"
    mismatches = []
    for path, content in outputs.items():
        if args.write:
            path.parent.mkdir(exist_ok=True)
            path.write_text(content)
        elif not path.is_file() or path.read_text() != content:
            mismatches.append(str(path.relative_to(project)))
    if mismatches:
        raise SystemExit("Library drift: " + ", ".join(mismatches))
    print(f"{'Wrote' if args.write else 'Verified'} {len(definitions)} local footprints "
          f"and {len(symbols) - 4} local symbols; no fit/process approval implied")


if __name__ == "__main__":
    main()
