#!/usr/bin/env python3
"""Fail-closed KiCad 9 terminal comparison.

Inputs are native KiCad XML/S-expression netlists or a native .kicad_pcb.
Names and complete (reference, pin) membership are compared, not net counts.
IPC-D-356 requires --pcb: KiCad truncates references to 6 and pins to 4
characters, so coordinates must disambiguate them (notably J_LED_A/J_LED_C).
KiCad 9 IPC aliases replace non-graphic ASCII with '?', uppercase, and keep
the last 14 characters. Alias collisions require review; they are NOT guessed.
CUST 0 coordinates are 0.0001 inch = 0.00254 mm, with <= 0.001271 mm rounding
error per axis. Native board Y is negated, never made absolute. An auxiliary
origin other than (0, 0) is rejected to keep IPC, Gerbers, drills and CPL aligned.
This verifies file connectivity, not physical continuity or surge performance.
"""

import argparse
from dataclasses import dataclass, field
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def children(node, name):
    return [item for item in node[1:] if isinstance(item, list) and item and item[0] == name]


def child(node, name, required=True):
    found = children(node, name)
    require(len(found) <= 1, f"Duplicate {name} in {node[0]}")
    require(found or not required, f"Missing {name} in {node[0]}")
    return found[0] if found else None


def value(node, name, default=None):
    item = child(node, name, required=default is None)
    if item is None:
        return default
    require(len(item) == 2 and isinstance(item[1], str), f"Malformed {name}")
    return item[1]


def read_tree(path):
    # Shared with the geometry checker; never fall back to regex parsing.
    if __package__:
        from .kicad_sexpr import Node, parse
    else:
        from kicad_sexpr import Node, parse

    def as_list(node):
        return [node.tag, *(as_list(item) if isinstance(item, Node) else str(item) for item in node.values)]

    try:
        tree = as_list(parse(Path(path).read_text(encoding="utf-8"), source=str(path)))
    except (ValueError, OSError) as exc:
        raise VerificationError(f"{path}: {exc}") from exc
    require(isinstance(tree, list) and tree, f"Empty S-expression: {path}")
    return tree


def numbers(items):
    try:
        result = tuple(float(item) for item in items)
    except (ValueError, TypeError) as exc:
        raise VerificationError(f"Invalid numeric data: {items}") from exc
    require(all(math.isfinite(item) for item in result), "Non-finite numeric data")
    return result


@dataclass
class Pad:
    ref: str
    pin: str
    net: str
    x: float
    y: float
    kind: str
    drill: float
    width: float
    height: float
    rotation: float
    layers: tuple
    shape: str = "circle"
    mask_margin: float = 0.0
    paste_margin: float = 0.0
    paste_ratio: float = 0.0
    roundrect_ratio: float = 0.25


@dataclass
class Footprint:
    name: str
    properties: dict
    x: float
    y: float
    rotation: float
    side: str
    attributes: set
    pads: list = field(default_factory=list)

    @property
    def mechanical(self):
        return not any(pad.kind != "np_thru_hole" for pad in self.pads)

    @property
    def populated(self):
        return not self.mechanical and "dnp" not in self.attributes


@dataclass
class Board:
    tree: list
    nets: dict
    footprints: dict
    pads: list


def read_board(path):
    tree = read_tree(path)
    require(tree[0] == "kicad_pcb", f"Not a native KiCad PCB: {path}")
    setup = child(tree, "setup")
    origin = child(setup, "aux_axis_origin", False)
    require(origin is None or numbers(origin[1:]) == (0.0, 0.0), "Nonzero IPC auxiliary origin")
    net_codes = {}
    for net in children(tree, "net"):
        require(len(net) == 3 and str(net[1]).isdigit(), "Malformed PCB net declaration")
        require(net[1] not in net_codes and net[2] not in net_codes.values(), "Duplicate PCB net")
        net_codes[net[1]] = net[2]
    require(net_codes.get("0") == "" and len(net_codes) > 1, "Empty/malformed PCB net table")
    nets = {name: set() for name in net_codes.values() if name}
    footprints, pads = {}, []
    for fp in children(tree, "footprint"):
        require(len(fp) > 1 and isinstance(fp[1], str) and fp[1], "Missing footprint identifier")
        props = {}
        for prop in children(fp, "property"):
            require(len(prop) >= 3 and prop[1] not in props, "Malformed/duplicate footprint property")
            props[prop[1]] = prop[2]
        ref = props.get("Reference", "")
        require(ref and ref not in footprints and props.get("Value"), "Missing/duplicate reference or value")
        at = numbers(child(fp, "at")[1:])
        require(len(at) in (2, 3), f"Malformed position for {ref}")
        x, y = at[:2]
        rotation = at[2] % 360 if len(at) == 3 else 0.0
        layer = value(fp, "layer")
        require(layer in ("F.Cu", "B.Cu"), f"Unsupported footprint layer: {layer}")
        attrs = child(fp, "attr", False)
        attributes = set(attrs[1:]) if attrs else set()
        if value(fp, "dnp", "no") == "yes":
            attributes.add("dnp")
        footprint = Footprint(fp[1], props, x, y, rotation,
                              "top" if layer == "F.Cu" else "bottom", attributes)
        footprints[ref] = footprint
        for pad in children(fp, "pad"):
            require(len(pad) >= 4 and pad[2] in ("thru_hole", "np_thru_hole", "smd", "connect"),
                    f"Unsupported/malformed pad on {ref}")
            pin, kind = pad[1:3]
            layers = tuple(child(pad, "layers")[1:])
            require(any(layer in ("*.Cu", "F.Cu", "B.Cu") for layer in layers),
                    f"Unsupported non-copper pad on {ref}")
            local = numbers(child(pad, "at")[1:])
            require(len(local) in (2, 3), f"Malformed pad position: {ref}.{pin}")
            angle = math.radians(rotation)
            px = x + local[0] * math.cos(angle) + local[1] * math.sin(angle)
            py = y - local[0] * math.sin(angle) + local[1] * math.cos(angle)
            size = numbers(child(pad, "size")[1:])
            require(len(size) == 2 and min(size) > 0, f"Malformed pad size: {ref}.{pin}")
            drill_node = child(pad, "drill", False)
            drill = 0.0
            if drill_node:
                require(len(drill_node) == 2, "Slotted/offset drills need an explicit validator")
                drill = numbers(drill_node[1:])[0]
                require(drill > 0, "Invalid drill diameter")
            require((drill > 0) == (kind in ("thru_hole", "np_thru_hole")),
                    f"Pad/drill classification mismatch: {ref}.{pin}")
            net_node = child(pad, "net", False)
            net_name = ""
            if net_node:
                require(len(net_node) == 3 and net_codes.get(net_node[1]) == net_node[2],
                        f"Bad PCB pad net: {ref}.{pin}")
                net_name = net_node[2]
            if kind != "np_thru_hole":
                require(pin and net_name, f"Unnumbered/unassigned electrical pad: {ref}.{pin}")
                nets[net_name].add((ref, pin))
            else:
                require(not net_name, f"NPTH assigned to electrical net: {ref}.{pin}")
            mask = value(pad, "solder_mask_margin", value(fp, "solder_mask_margin", value(setup, "pad_to_mask_clearance", "0")))
            paste = value(pad, "solder_paste_margin", value(fp, "solder_paste_margin", value(setup, "pad_to_paste_clearance", "0")))
            ratio = value(pad, "solder_paste_margin_ratio", value(fp, "solder_paste_ratio", value(setup, "pad_to_paste_clearance_ratio", "0")))
            roundrect_ratio = numbers([value(pad, "roundrect_rratio", "0.25")])[0]
            require(0 <= roundrect_ratio <= 0.5, f"Invalid roundrect ratio: {ref}.{pin}")
            terminal = Pad(ref, pin, net_name, px, py, kind, drill, *size,
                           local[2] % 360 if len(local) == 3 else rotation, layers, pad[3],
                           *numbers((mask, paste, ratio)), roundrect_ratio)
            footprint.pads.append(terminal)
            pads.append(terminal)
    for via in children(tree, "via"):
        at = numbers(child(via, "at")[1:])
        require(len(at) == 2, "Malformed via coordinates")
        name = net_codes.get(value(via, "net"))
        require(name, "Unassigned/unknown via net")
        size = numbers([value(via, "size")])[0]
        drill = numbers([value(via, "drill")])[0]
        layers = tuple(child(via, "layers")[1:])
        require(set(layers) == {"F.Cu", "B.Cu"} and 0 < drill < size, "Unsupported via geometry")
        pads.append(Pad("VIA", "", name, *at, "via", drill, size, size, 0.0, layers))
    require(footprints and nets and all(nets.values()), "Empty PCB or net without terminals")
    validate_membership(nets)
    return Board(tree, nets, footprints, pads)


def validate_membership(nets):
    require(nets and all(name and nodes for name, nodes in nets.items()), "Empty net or netlist")
    seen = set()
    for name, nodes in nets.items():
        for terminal in nodes:
            require(len(terminal) == 2 and all(terminal), f"Malformed terminal in {name}")
            require(terminal not in seen, f"Terminal assigned more than once: {terminal}")
            seen.add(terminal)


def read_xml(path):
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise VerificationError(f"{path}: {exc}") from exc
    require(root.tag == "export" and root.get("version") == "E", "Unrecognized KiCad 9 XML")
    return root


def parse_netlist(filename):
    path = Path(filename)
    if path.suffix == ".kicad_pcb":
        return read_board(path).nets
    text = path.read_text(encoding="utf-8").lstrip()
    require(text, f"Empty netlist: {path}")
    entries, refs, inventory = [], set(), set()
    if text.startswith("<"):
        root = read_xml(path)
        blocks = root.findall("nets")
        require(len(blocks) == 1 and len(root.findall("components")) == 1
                and len(root.findall("libparts")) == 1, "Missing/duplicate XML sections")
        libparts = {}
        for part in root.findall("libparts/libpart"):
            key = (part.get("lib"), part.get("part"))
            require(all(key) and key not in libparts, "Malformed/duplicate library part")
            pins = [pin.get("num") for pin in part.findall("pins/pin")]
            require(all(pins) and len(pins) == len(set(pins)), "Malformed/duplicate library pins")
            libparts[key] = pins
        for comp in root.findall("components/comp"):
            ref = comp.get("ref")
            require(ref and ref not in refs, "Missing/duplicate component reference")
            refs.add(ref)
            source = comp.find("libsource")
            require(source is not None, "Missing component library source")
            key = (source.get("lib"), source.get("part"))
            require(key in libparts, "Missing component library pin inventory")
            inventory.update((ref, pin) for pin in libparts[key])
        for net in blocks[0]:
            require(net.tag == "net" and all(node.tag == "node" for node in net), "Unrecognized net data")
            entries.append((net.get("code"), net.get("name"),
                            [(node.get("ref"), node.get("pin")) for node in net]))
    elif text.startswith("("):
        root = read_tree(path)
        require(root[0] == "export", "Unrecognized S-expression netlist")
        require(value(root, "version") == "E", "Unrecognized KiCad 9 netlist version")
        libparts = {}
        for part in children(child(root, "libparts"), "libpart"):
            key = (value(part, "lib"), value(part, "part"))
            require(key not in libparts, "Duplicate library part")
            block = child(part, "pins", False)
            pins = [value(pin, "num") for pin in children(block, "pin")] if block else []
            require(all(pins) and len(pins) == len(set(pins)), "Malformed/duplicate library pins")
            libparts[key] = pins
        comps = child(root, "components")
        for comp in children(comps, "comp"):
            ref = value(comp, "ref")
            require(ref and ref not in refs, "Missing/duplicate component reference")
            refs.add(ref)
            source = child(comp, "libsource")
            key = (value(source, "lib"), value(source, "part"))
            require(key in libparts, "Missing component library pin inventory")
            inventory.update((ref, pin) for pin in libparts[key])
        block = child(root, "nets")
        require(all(isinstance(net, list) and net[0] == "net" for net in block[1:]), "Malformed nets block")
        for net in children(block, "net"):
            entries.append((value(net, "code"), value(net, "name"),
                            [(value(node, "ref"), value(node, "pin")) for node in children(net, "node")]))
    else:
        raise VerificationError(f"Unrecognized netlist format: {path}")
    require(refs, "Netlist has no component inventory")
    nets, codes = {}, set()
    for code, name, nodes in entries:
        require(code and code.isdigit() and int(code) > 0 and code not in codes, "Malformed/duplicate net code")
        require(name and name not in nets and nodes, "Missing/duplicate/empty net")
        require(all(ref in refs and pin for ref, pin in nodes), f"Unknown/incomplete terminal in {name}")
        require(len(nodes) == len(set(nodes)), f"Duplicate terminal in {name}")
        nets[name] = set(nodes)
        codes.add(code)
    validate_membership(nets)
    terminals = set().union(*nets.values())
    require(terminals == inventory, f"Incomplete/extra terminal inventory: {sorted(terminals ^ inventory)}")
    return nets


def differences(left, right):
    validate_membership(left)
    validate_membership(right)
    return [f"{name}: left={sorted(left.get(name, set()))}, right={sorted(right.get(name, set()))}"
            for name in sorted(left.keys() | right.keys()) if left.get(name) != right.get(name)]


def ipc_alias(name):
    return "".join(c if 33 <= ord(c) <= 126 else "?" for c in name).upper()[-14:]


IPC_RECORD = re.compile(
    r"(317|327|367)(.{14})   (.{6})([- ])(.{4})([ M])"
    r"(D\d{4}[PU]| {6})A(\d{2})X([+-]\d{6})Y([+-]\d{6})X(\d{4})Y(\d{4})R(\d{3})S([0-3])"
)


def compare_ipc(path, board):
    lines = Path(path).read_text(encoding="ascii").splitlines()
    require(lines[:3] == ["P  CODE 00", "P  UNITS CUST 0", "P  arrayDim   N"]
            and lines[-1:] == ["999"], "Unrecognized/incomplete KiCad 9 IPC-D-356 header or terminator")
    aliases = {name: ipc_alias(name) for name in board.nets}
    require(len(set(aliases.values())) == len(aliases) and "N/C" not in aliases.values(),
            "IPC alias collision: explicit reviewed mapping required")
    remaining = list(board.pads)
    require(remaining and len(lines) > 4, "Empty IPC data")
    for number, line in enumerate(lines[3:-1], 4):
        match = IPC_RECORD.fullmatch(line)
        require(match is not None, f"Malformed/unsupported IPC record at line {number}")
        kind, net, ref, sep, pin, midpoint, hole, access, x, y, width, height, rotation, mask = match.groups()
        x, y = int(x) * 0.00254, int(y) * 0.00254
        candidates = [p for p in remaining if p.ref[:6] == ref.strip() and p.pin[:4] == pin.strip()
                      and abs(p.x - x) <= 0.001271 and abs(-p.y - y) <= 0.001271]
        require(len(candidates) == 1, f"IPC terminal missing/extra/ambiguous at line {number}: {ref.strip()}.{pin.strip()}")
        pad = candidates[0]
        require(net.strip() == (aliases[pad.net] if pad.net else "N/C"),
                f"Wrong IPC net on {pad.ref}.{pad.pin}: {net.strip()} != {pad.net}")
        expected_kind = "367" if pad.kind == "np_thru_hole" else "327" if pad.kind in ("smd", "connect") else "317"
        require(kind == expected_kind and midpoint == ("M" if pad.kind == "via" else " ")
                and sep == ("-" if pad.pin else " "), f"Wrong IPC classification on {pad.ref}.{pad.pin}")
        if pad.drill:
            require(hole.startswith("D") and hole[-1] == ("U" if pad.kind == "np_thru_hole" else "P")
                    and abs(int(hole[1:5]) * 0.00254 - pad.drill) <= 0.001271,
                    f"Wrong IPC drill on {pad.ref}.{pad.pin}")
        else:
            require(hole == " " * 6, f"Unexpected IPC drill on {pad.ref}.{pad.pin}")
        expected_access = 0 if pad.kind not in ("smd", "connect") else 1 if "F.Cu" in pad.layers else 2
        require(int(access) == expected_access, f"Wrong IPC access layer on {pad.ref}.{pad.pin}")
        expected_height = 0 if pad.shape == "circle" else pad.height
        require(abs(int(width) * 0.00254 - pad.width) <= 0.001271
                and abs(int(height) * 0.00254 - expected_height) <= 0.001271,
                f"Wrong IPC pad size on {pad.ref}.{pad.pin}")
        require(abs((int(rotation) + pad.rotation + 180) % 360 - 180) <= 0.500001,
                f"Wrong IPC pad rotation on {pad.ref}.{pad.pin}")
        remaining.remove(pad)
    require(not remaining, f"IPC missing {len(remaining)} physical pads/vias")
    return {"records": len(board.pads), "aliases": aliases, "units": "0.0001 inch", "tolerance_mm": 0.001271}


def compare(f1, f2):
    try:
        diffs = differences(parse_netlist(f1), parse_netlist(f2))
        require(not diffs, "\n".join(diffs))
    except (VerificationError, OSError, ImportError, UnicodeError) as exc:
        print(f"Net verification FAILED: {exc}", file=sys.stderr)
        return 1
    print("Complete net terminal membership matches.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("left", type=Path, help="Native schematic XML/netlist or PCB")
    parser.add_argument("right", type=Path, help="Native netlist or PCB")
    parser.add_argument("--ipc", type=Path)
    parser.add_argument("--pcb", type=Path, help="Native PCB required to resolve IPC truncation")
    parser.add_argument("--output", type=Path, help="JSON verification report (also written on failure)")
    args = parser.parse_args()
    result = {"verified": False}
    try:
        left, right = parse_netlist(args.left), parse_netlist(args.right)
        require(not differences(left, right), "\n".join(differences(left, right)))
        result["nets"] = len(left)
        result["terminals"] = sum(map(len, left.values()))
        if args.ipc:
            require(args.pcb, "--ipc requires --pcb")
            board = read_board(args.pcb)
            require(not differences(left, board.nets), "PCB terminal membership differs")
            result["ipc"] = compare_ipc(args.ipc, board)
        result["verified"] = True
    except (VerificationError, OSError, ImportError, UnicodeError) as exc:
        result["error"] = str(exc)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verified"] else 1


if __name__ == "__main__":
    sys.exit(main())
