#!/usr/bin/env python3
"""KiCad 9 manufacturing transaction, not hardware/protection certification.

build: verify a complete snapshot, export privately, validate, then publish.
check: the same checks/exports, retaining evidence and refreshing the generated
       CPL reference, but publishing no upload package.
clean: remove build-owned outputs/runs only; NEVER delete the project's tmp/.

All public Make targets use this one locked transaction. Each attempt invalidates
the previous public release and retains it under tmp/manufacturing/runs/ until
explicit clean. Only build/manifest.json with status=verified describes a release.
pcb/CPL.csv is a generated reference mirror, not an input or independent source.
pcb/verification.json records narrowly reviewed warnings and design-release
holds. Holds cannot be bypassed by a successful DRC or an export target.

Placement uses mm, absolute origin, native signed Y, native footprint anchors and
rotations modulo 360. No unreviewed JLCPCB centroid/rotation corrections are made.
The supported fabrication subset is KiCad 9 two-layer, circular drills, ordinary
pad flashes and straight copper/outline segments. Unsupported geometry fails
closed and needs a tested validator extension, not an ignore switch. Supplier
processed CAM/stencil geometry and exact assembly-model orientation need review.
Native timestamps remain intact; ZIP metadata is deterministic, native files are
not hand-edited to manufacture byte-for-byte reproducibility.
"""

import argparse
import csv
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import zipfile

if __package__:
    from .compare_nets import (VerificationError, child, children, compare_ipc, differences,
                              numbers, parse_netlist, read_board, read_tree, read_xml, require, value)
else:
    from compare_nets import (VerificationError, child, children, compare_ipc, differences,
                             numbers, parse_netlist, read_board, read_tree, read_xml, require, value)


LAYERS = {
    "F.Cu": ("pcb-F_Cu.gbr", "Copper,L1,Top"),
    "B.Cu": ("pcb-B_Cu.gbr", "Copper,L2,Bot"),
    "F.Mask": ("pcb-F_Mask.gbr", "Soldermask,Top"),
    "B.Mask": ("pcb-B_Mask.gbr", "Soldermask,Bot"),
    "F.Paste": ("pcb-F_Paste.gbr", "Paste,Top"),
    "F.SilkS": ("pcb-F_Silkscreen.gbr", "Legend,Top"),
    "B.SilkS": ("pcb-B_Silkscreen.gbr", "Legend,Bot"),
    "Edge.Cuts": ("pcb-Edge_Cuts.gbr", "Profile,NP"),
}
DRILLS = {"pcb-PTH.drl", "pcb-NPTH.drl"}
FAB_FILES = {item[0] for item in LAYERS.values()} | DRILLS
# 0.1651 mm is the two-layer/2 oz track minimum; 0.20/0.25/0.50 mm are
# conservative project clearances. Component PTH rings have a separate .dru rule.
MIN_RULES = {
    "min_clearance": 0.2, "min_track_width": 0.1651,
    "min_hole_clearance": 0.25, "min_hole_to_hole": 0.25,
    "min_copper_edge_clearance": 0.5, "min_via_annular_width": 0.1,
    "min_silk_clearance": 0.15, "min_text_height": 1.0, "min_text_thickness": 0.15,
}
ENGINEERING_NOTES = ("ASSEMBLY.md", "ELECTRICAL.md", "DFM_EVIDENCE.md", "ENVIRONMENT_EVIDENCE.md",
                     "DESIGN_BOUNDS.md", "LED_PROTECTION_RESEARCH.md", "SOURCE_PROTECTION_RESEARCH.md")
REQUIRED = ("pcb.kicad_pcb", "pcb.kicad_sch", "pcb.kicad_pro", "pcb.kicad_dru",
            "fp-lib-table", "sym-lib-table", "BOM.csv", "verification.json", *ENGINEERING_NOTES)
HELPERS = ("manufacturing.py", "compare_nets.py", "check_geometry.py", "kicad_sexpr.py",
           "analyze_limits.py", "design_bounds.py")
SOURCE_SUFFIXES = {".kicad_pcb", ".kicad_sch", ".kicad_pro", ".kicad_dru", ".kicad_mod",
                   ".kicad_sym", ".kicad_wks", ".step", ".stp", ".wrl"}
CPL_FIELDS = ["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"]
POSITION_FIELDS = ["Ref", "Val", "Package", "PosX", "PosY", "Rot", "Side"]
WX_IMAGE_DEBUG = (r"(?m)^\d{2}:\d{2}:\d{2}: Debug: Adding duplicate image handler for '"
                  r"(?:PNG|JPEG|TIFF|GIF|PNM|PCX|IFF|Windows icon|Windows cursor|Windows animated cursor|TGA|XPM) file'\r?\n")
ROUNDRECT_PRIMITIVES = [
    "4,1,4,$2,$3,$4,$5,$6,$7,$8,$9,$2,$3,0*",
    "1,1,$1+$1,$2,$3*", "1,1,$1+$1,$4,$5*", "1,1,$1+$1,$6,$7*", "1,1,$1+$1,$8,$9*",
    "20,1,$1+$1,$2,$3,$4,$5,0*", "20,1,$1+$1,$4,$5,$6,$7,0*",
    "20,1,$1+$1,$6,$7,$8,$9,0*", "20,1,$1+$1,$8,$9,$2,$3,0*",
]
SCOPE = {
    "claim": "Manufacturing file verification only; not surge certification or order approval.",
    "placement": "mm; absolute (0,0); X=PCB X, Y=-PCB Y; angles modulo 360; no centroid corrections",
    "placement_tolerance_mm": 0.00001,
    "rotation_tolerance_degrees": 0.00001,
    "bom_fields": "Exact MPN and Manufacturer in schematic/PCB; CSV 'LCSC Part #' accepts source 'LCSC' (existing project field) or 'LCSC Part #'; conflicting aliases fail",
    "gerber_tolerance_mm": 0.000002,
    "gerber_coverage": "Copper pads/vias/straight tracks, board outline, mask/paste aperture inventory, sizes and corner radii; unsupported critical-layer source graphics rejected; legend syntax (not rendered glyph equivalence)",
    "via_masks": "KiCad 9 flat global/per-via tenting flags; absent local flags inherit; absent global flags tent both sides. Via openings use board mask expansion and individual circular flashes at zero minimum mask width. Only source-matched openings of untented, overlapping same-net vias may expose their group holes; component mask/paste exposure is forbidden.",
    "via_treatment": "ViaTreatment.csv reports resolved source-requested front/back tenting, not physical covering. Both open: standard untented, no fill. No seal, CAM acceptance, finish thickness or barrel-copper limit is inferred.",
    "drill_tolerance_mm": 0.000501,
    "open_acceptance": ["JLCPCB exact-part centroid/rotation and polarity",
                        "processed CAM/stencil and via treatment; pin fit and forming",
                        "mixed SMT/THT heavy-copper assembly quote and panel plan",
                        "circuit protection, powered fault/surge, thermal and site qualification"],
    "reproducibility": "Fresh source snapshot and exports; deterministic ZIP metadata; native timestamps retained",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def read_json(path):
    def unique_keys(pairs):
        result = {}
        for key, item in pairs:
            require(key not in result, f"Duplicate JSON key {key} in {path.name}")
            result[key] = item
        return result

    def reject_constant(item):
        raise VerificationError(f"Non-finite JSON value {item} in {path.name}")

    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_keys, parse_constant=reject_constant)
    require(isinstance(data, dict), f"Expected JSON object in {path.name}")
    return data


def source_inventory(root):
    required = [root / "pcb" / name for name in REQUIRED]
    required += [root / "scripts" / name for name in HELPERS] + [root / "Makefile"]
    for path in required:
        require(path.is_file() and not path.is_symlink() and path.stat().st_size,
                f"Missing/empty/linked required source: {path.relative_to(root)}")
    paths = set(required)
    for path in (root / "pcb").rglob("*"):
        if path.suffix in SOURCE_SUFFIXES or path.name in ("fp-lib-table", "sym-lib-table"):
            require(path.is_file() and not path.is_symlink(), f"Non-regular source: {path}")
            paths.add(path)
    for path in paths:
        require(path.resolve().is_relative_to(root.resolve()), f"External source dependency: {path}")
    return {path.relative_to(root).as_posix(): sha256(path) for path in sorted(paths)}


def validate_project(project):
    if __package__:
        from .kicad_sexpr import parse_many
    else:
        from kicad_sexpr import parse_many
    settings = read_json(project / "pcb.kicad_pro")
    design = settings["board"]["design_settings"]
    for name, minimum in MIN_RULES.items():
        actual = design["rules"].get(name)
        require(isinstance(actual, (float, int)) and actual >= minimum,
                f"Project rule {name} must be >= {minimum} mm")
    require(not design.get("drc_exclusions") and not settings["erc"].get("erc_exclusions"),
            "Unreviewed DRC/ERC exclusions are forbidden")
    for section in (design, settings["erc"]):
        severities = section["rule_severities"]
        require(severities and all(s in ("error", "warning") for s in severities.values()),
                "Ignored/unrecognized rule severities are forbidden")
    rules_path = project / "pcb.kicad_dru"
    rules = parse_many(rules_path.read_text(encoding="utf-8"), source=str(rules_path))
    require(rules[0].tag == "version" and rules[0].atoms() == ["1"] and len(rules) > 1,
            "Empty/unrecognized custom rules")
    for rule in rules[1:]:
        require(rule.tag == "rule", "Unexpected custom-rule root")
        severity = rule.one("severity", required=False)
        require(severity is None or severity.atoms() in (["error"], ["warning"]),
                "Custom-rule ignore/exclusion severities are forbidden")
    # Effective clearance/ring coverage is independently checked by check_geometry.py.
    libraries = {}
    for table, tag, library_type in (("fp-lib-table", "fp_lib_table", "KiCad"),
                                     ("sym-lib-table", "sym_lib_table", "KiCad")):
        tree = read_tree(project / table)
        require(tree[0] == tag and children(tree, "lib"), f"Empty/invalid {table}")
        entries = {}
        for lib in children(tree, "lib"):
            name, uri = value(lib, "name"), value(lib, "uri")
            require(name and name not in entries and value(lib, "type") == library_type,
                    f"Malformed/duplicate library in {table}")
            require(uri.startswith("${KIPRJMOD}/"), f"Library must be project-local: {uri}")
            target = project / uri.removeprefix("${KIPRJMOD}/")
            require(target.resolve().is_relative_to(project.resolve()) and target.exists(),
                    f"Missing/external project library: {uri}")
            if table == "fp-lib-table":
                require(target.is_dir() and list(target.glob("*.kicad_mod")), f"Empty footprint library: {uri}")
                entries[name] = {p.stem for p in target.glob("*.kicad_mod")}
            else:
                lib_tree = read_tree(target)
                require(lib_tree[0] == "kicad_symbol_lib", f"Invalid symbol library: {uri}")
                entries[name] = {item[1] for item in children(lib_tree, "symbol")}
                require(entries[name], f"Empty symbol library: {uri}")
        libraries[table] = entries
    board = read_board(project / "pcb.kicad_pcb")
    identifiers = [(fp.name, "fp-lib-table") for fp in board.footprints.values()]
    for path in project.rglob("*.kicad_sch"):
        sch = read_tree(path)
        require(sch[0] == "kicad_sch", f"Invalid schematic: {path}")
        identifiers += [(value(symbol, "lib_id"), "sym-lib-table") for symbol in children(sch, "symbol")]
        for sheet in children(sch, "sheet"):
            files = [p[2] for p in children(sheet, "property") if p[1] == "Sheetfile"]
            require(len(files) == 1 and (path.parent / files[0]).resolve().is_relative_to(project.resolve())
                    and (path.parent / files[0]).is_file(), "Missing/external hierarchical sheet")
    for identifier, table in identifiers:
        parts = identifier.split(":", 1)
        require(len(parts) == 2 and parts[1] in libraries[table].get(parts[0], set()),
                f"Unresolved project-local library item: {identifier}")
    sch = read_tree(project / "pcb.kicad_sch")
    revision = value(child(sch, "title_block"), "rev")
    require(revision and value(child(board.tree, "title_block"), "rev") == revision,
            "PCB/schematic hardware revisions must be explicit and identical")
    return board, revision


def validate_report(path, kind, version, reviewed_labels=None):
    data = read_json(path)
    require(isinstance(data, dict) and data.get("$schema") == f"https://schemas.kicad.org/{kind}.v1.json"
            and data.get("source") and data.get("date") and data.get("kicad_version") == version,
            f"Unrecognized/incomplete {kind.upper()} JSON report")
    require(not data.get("ignored_checks"), f"{kind.upper()} has ignored checks")
    if "included_severities" in data:
        require(set(data["included_severities"]) == {"error", "warning", "exclusion"},
                f"{kind.upper()} report omitted severities")
    if kind == "drc":
        require(data.get("coordinate_units") == "mm", "DRC coordinate units are not mm")
        groups = [data.get(name) for name in ("violations", "unconnected_items", "schematic_parity")]
    else:
        sheets = data.get("sheets")
        require(isinstance(sheets, list) and sheets, "ERC contains no sheet inventory")
        require(all(isinstance(s, dict) and s.get("path") and s.get("uuid_path") for s in sheets),
                "Malformed ERC sheet inventory")
        groups = [sheet.get("violations") for sheet in sheets]
    require(all(isinstance(group, list) for group in groups), f"Missing {kind.upper()} result sections")
    violations = [violation for group in groups for violation in group]
    accepted = {}
    reviewed_labels = reviewed_labels or {}
    for violation in violations:
        items = violation.get("items", [])
        reviewed = (kind == "erc" and len(sheets) == 1 and sheets[0]["path"] == "/"
                    and violation.get("severity") == "warning"
                    and violation.get("type") == "single_global_label"
                    and len(items) == 1 and items[0].get("uuid") in reviewed_labels)
        if reviewed:
            identifier = items[0]["uuid"]
            reviewed = (identifier not in accepted and items[0].get("description") ==
                        f"Global Label '{reviewed_labels[identifier]}'")
        require(reviewed, f"{kind.upper()}: unreviewed {violation.get('type', 'malformed violation')}; review retained report")
        accepted[identifier] = reviewed_labels[identifier]
    require(accepted == reviewed_labels, f"Stale {kind.upper()} warning review; review this source again")
    return {"verified": True, "violations": len(violations), "reviewed_warnings": len(accepted)}


def read_csv(path, required_fields):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream, strict=True)
        require(reader.fieldnames and len(reader.fieldnames) == len(set(reader.fieldnames))
                and set(required_fields).issubset(reader.fieldnames), f"Malformed CSV header: {path.name}")
        rows = list(reader)
    require(rows and all(None not in row and all(v is not None for v in row.values()) for row in rows),
            f"Empty/malformed CSV rows: {path.name}")
    return rows


def validate_bom(path, xml_path, board):
    components = {}
    for comp in read_xml(xml_path).findall("components/comp"):
        ref = comp.get("ref")
        require(ref and ref not in components, "Duplicate/empty XML component")
        fields = {item.get("name"): item.text or "" for item in comp.findall("fields/field")}
        flags = {item.get("name") for item in comp.findall("property")}
        if "exclude_from_board" not in flags:
            components[ref] = (comp.findtext("value"), comp.findtext("footprint"), fields, flags)
    require(set(components) == set(board.footprints), "Schematic/PCB component inventory differs")
    for ref, fp in board.footprints.items():
        val, name, fields, flags = components[ref]
        require(val == fp.properties["Value"] and name == fp.name, f"Schematic/PCB value/footprint differs: {ref}")
        require(("dnp" in flags) == ("dnp" in fp.attributes), f"DNP mismatch: {ref}")
        if fp.populated:
            require("exclude_from_bom" not in flags and not fp.attributes.intersection(
                {"exclude_from_bom", "exclude_from_pos_files"}), f"Populated part excluded from assembly: {ref}")
    expected = {ref for ref, fp in board.footprints.items() if fp.populated}
    require(expected, "No populated electrical components")
    bom = {}
    for row in read_csv(path, ("Comment", "Designator", "Footprint", "LCSC Part #", "MPN", "Manufacturer")):
        require(all(row[key].strip() for key in ("Comment", "Designator", "Footprint", "MPN", "Manufacturer")),
                "BOM has empty sourcing data")
        require(re.fullmatch(r"C[1-9]\d*", row["LCSC Part #"]), "BOM has invalid LCSC part number")
        refs = [ref.strip() for ref in row["Designator"].split(",")]
        if "Quantity" in row:
            require(row["Quantity"].isdigit() and int(row["Quantity"]) == len(refs), "BOM quantity mismatch")
        for ref in refs:
            require(ref in expected and ref not in bom, f"Extra/duplicate/non-populated BOM designator: {ref}")
            fp = board.footprints[ref]
            require(row["Comment"] == fp.properties["Value"] and row["Footprint"] == fp.name,
                    f"BOM value/qualified footprint mismatch: {ref}")
            for name in ("MPN", "Manufacturer", "LCSC Part #"):
                aliases = ("LCSC Part #", "LCSC") if name == "LCSC Part #" else (name,)
                for fields in (components[ref][2], fp.properties):
                    present = [fields[key] for key in aliases if key in fields]
                    require(present and all(item == row[name] for item in present),
                            f"BOM {name} missing/different in schematic or PCB: {ref}")
            bom[ref] = row
    require(set(bom) == expected, f"Missing BOM designators: {sorted(expected - bom.keys())}")
    return bom


def check_placement(rows, board, native=False):
    fields = POSITION_FIELDS if native else CPL_FIELDS
    ref_col, val_col, package_col, x_col, y_col, rot_col, side_col = fields
    found, seen = {}, set()
    for row in rows:
        ref = row[ref_col]
        require(ref in board.footprints and ref not in seen, f"Extra/duplicate CPL reference: {ref}")
        seen.add(ref)
        fp = board.footprints[ref]
        if native and fp.mechanical:
            continue  # KiCad may include unflagged holes; they are never assembly parts.
        require(fp.populated, f"Non-populated part in CPL: {ref}")
        x, y, rot = numbers((row[x_col], row[y_col], row[rot_col]))
        require(abs(x - fp.x) <= 0.00001 and abs(y + fp.y) <= 0.00001,
                f"CPL origin/handedness/position differs: {ref}")
        require(abs((rot - fp.rotation + 180) % 360 - 180) <= 0.00001, f"CPL rotation differs: {ref}")
        require(row[side_col] == fp.side and row[val_col] == fp.properties["Value"], f"CPL side/value differs: {ref}")
        package = fp.name.split(":", 1)[-1] if native else fp.name
        require(row[package_col] == package, f"CPL footprint differs: {ref}")
        found[ref] = [ref, row[val_col], fp.name, f"{x:.6f}", f"{y:.6f}", f"{rot % 360:.6f}", fp.side]
    expected = {ref for ref, fp in board.footprints.items() if fp.populated}
    require(set(found) == expected, f"Missing CPL designators: {sorted(expected - found.keys())}")
    return found


def generate_cpl(native, output, board):
    positions = check_placement(read_csv(native, POSITION_FIELDS), board, native=True)
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(CPL_FIELDS)
        writer.writerows(positions[ref] for ref in sorted(positions))
    check_placement(read_csv(output, CPL_FIELDS), board)
    return positions


def match_geometry(actual, expected, tolerance, label):
    """Return the one-to-one matched source records in exported order."""
    remaining, matched = list(expected), []
    for record in actual:
        matches = [i for i, candidate in enumerate(remaining) if len(record) == len(candidate)
                   and all(abs(a - b) <= tolerance if isinstance(a, (int, float)) else a == b
                           for a, b in zip(record, candidate))]
        require(matches, f"Extra/wrong {label}: {record}")
        matched.append(remaining.pop(matches[0]))
    require(not remaining, f"Missing {label}: {remaining[:3]} ({len(remaining)} total)")
    return matched


def via_mask_settings(board):
    """Resolve (front tented, back tented, opening radius) by source PCB coordinate."""
    setup = child(board.tree, "setup")
    plot = child(setup, "pcbplotparams", False)
    require(plot is None or child(plot, "viasonmask", False) is None,
            "Legacy viasonmask needs a tested tenting resolver")
    margin = numbers([value(setup, "pad_to_mask_clearance", "0")])[0]
    inherited, result = (True, True), {}
    for owner in [setup, *children(board.tree, "via")]:
        field = child(owner, "tenting", False)
        tented = inherited
        if field is not None:
            flags = field[1:]
            require(all(isinstance(flag, str) and flag in ("front", "back", "none") for flag in flags)
                    and len(flags) == len(set(flags)) and ("none" not in flags or len(flags) == 1),
                    "Unsupported/malformed KiCad 9 tenting flags")
            # A present flat list overrides both sides; an omitted side is open.
            tented = tuple(side in flags for side in ("front", "back"))
        if owner is setup:
            inherited = tented
            continue
        require(not any(child(owner, key, False) is not None for key in
                        ("solder_mask_margin", "padstack", "covering", "plugging", "filling", "capping")),
                "Unsupported via mask/treatment override; KiCad 9 vias use board mask expansion")
        point = numbers(child(owner, "at")[1:])
        require(len(point) == 2 and point not in result, "Malformed/duplicate via mask coordinates")
        radius = numbers([value(owner, "size")])[0] / 2 + margin
        require(math.isfinite(radius) and (all(tented) or radius > 0), "Nonpositive/nonfinite via mask aperture")
        result[point] = (*tented, radius)
    return result


def validate_drill(path, board, plated):
    lines = path.read_text(encoding="ascii").splitlines()
    function = "Plated,1,2,PTH" if plated else "NonPlated,1,2,NPTH"
    require(lines and lines[0] == "M48" and lines[-1] == "M30" and "METRIC" in lines
            and "G90" in lines and f"; #@! TF.FileFunction,{function}" in lines
            and "; FORMAT={-:-/ absolute / metric / decimal}" in lines, f"Invalid drill header/units: {path.name}")
    tools, records, role, selected = {}, [], None, None
    header = True
    for line in lines[1:-1]:
        if line.startswith("; #@! TA.AperFunction,"):
            role = line.rsplit(",", 1)[-1]
            require(role in ("ComponentDrill", "ViaDrill"), f"Unsupported drill role: {role}")
        elif line.startswith(";") or line in ("FMAT,2", "METRIC", "G90", "G05"):
            continue
        elif line == "%":
            require(header, "Duplicate Excellon header terminator")
            header = False
        elif match := re.fullmatch(r"T(\d+)C(\d+\.\d+)", line):
            require(header and role and match[1] not in tools, "Malformed/duplicate Excellon tool")
            tools[match[1]] = (float(match[2]), role)
        elif match := re.fullmatch(r"T(\d+)", line):
            require(not header and match[1] in tools, "Unknown Excellon tool")
            selected = tools[match[1]]
        elif match := re.fullmatch(r"X([+-]?\d+\.\d*)Y([+-]?\d+\.\d*)", line):
            require(not header and selected, "Drill hit without tool")
            records.append((*numbers(match.groups()), *selected))
        else:
            raise VerificationError(f"Unsupported/malformed Excellon record: {line}")
    expected = [(p.x, -p.y, p.drill, "ViaDrill" if p.kind == "via" else "ComponentDrill")
                for p in board.pads if p.drill and (p.kind != "np_thru_hole") == plated]
    require(records and not header, f"Empty drill file: {path.name}")
    match_geometry(records, expected, 0.000501, path.name)
    return len(records)


def parse_gerber(path, function):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    require([line for line in lines if line.startswith("%TF.FileFunction,")] == [f"%TF.FileFunction,{function}*%"]
            and lines.count("%MOMM*%") == 1
            and "%FSLAX46Y46*%" in lines and "%TF.SameCoordinates,Original*%" in lines
            and lines[-1:] == ["M02*"] and lines.count("M02*") == 1,
            f"Missing/invalid Gerber layer, origin, units or terminator: {path.name}")
    require(not re.search(r"%(?:MI|OF|SF|AS|IR|IP|SR)|G91", text), f"Unsupported Gerber transform: {path.name}")
    legend = function.startswith("Legend")
    require(legend or "%LPC" not in text, f"Unsupported subtractive geometry: {path.name}")
    polarity = "Negative" if function.startswith("Soldermask") else "Positive"
    require(function == "Profile,NP" or f"%TF.FilePolarity,{polarity}*%" in lines, "Invalid Gerber polarity")
    apertures, flashes, segments = {}, [], []
    aperture, point, net, ref, pin, macro = None, None, "", "", "", None
    interpolation, multi_quadrant, region = "G01", False, None
    roundrect_defined = False
    for line in lines:
        # Gerber is '*' delimited, not line delimited. Our native-output subset
        # permits exactly one statement per line, including comments and attributes.
        require(all(32 <= ord(char) <= 126 for char in line)
                and line.count("*") == 1 and line.endswith(("*", "*%")),
                f"Expected one complete Gerber statement per line in {path.name}: {line}")
        if line == "%AMRoundRect*":
            require(macro is None and not roundrect_defined, "Nested/redefined Gerber macro")
            macro = []
            continue
        if macro is not None:
            if not re.fullmatch(r"0 [^*%\r\n]*\*%?", line):
                macro.append(line.removesuffix("%"))
            if line.endswith("*%"):
                require(macro == ROUNDRECT_PRIMITIVES, "Unrecognized/modified RoundRect macro body")
                macro = None
                roundrect_defined = True
            continue
        if match := re.fullmatch(r"%ADD([1-9]\d+)(C|R|O|RoundRect),([+-]?\d+(?:\.\d+)?(?:X[+-]?\d+(?:\.\d+)?)*)\*%", line):
            params = numbers(match[3].split("X"))
            corner_radius = 0.0
            if match[2] == "C":
                require(len(params) == 1, "Unsupported holed aperture")
                size = (params[0], params[0])
            elif match[2] in ("R", "O"):
                require(len(params) == 2, "Unsupported aperture")
                size = params
            else:
                require(roundrect_defined, "RoundRect used before a validated macro definition")
                require(len(params) == 10 and params[-1] == 0 and params[0] >= 0, "Unsupported RoundRect macro")
                corner_radius = params[0]
                xs, ys = params[1:9:2], params[2:9:2]
                hx, hy = max(xs), max(ys)
                corners = list(zip(xs, ys))
                require(hx > 0 and hy > 0 and set(corners) == {(-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy)}
                        and all((a[0] == b[0]) != (a[1] == b[1]) for a, b in zip(corners, corners[1:] + corners[:1])),
                        "RoundRect corners must describe a centered, axis-aligned rectangle in perimeter order")
                size = (2 * (hx + corner_radius), 2 * (hy + corner_radius))
            require(match[1] not in apertures and min(size) > 0, "Invalid/duplicate aperture")
            apertures[match[1]] = (*size, match[2], corner_radius)
        elif match := re.fullmatch(r"D([1-9]\d+)\*", line):
            require(match[1] in apertures, "Unknown Gerber aperture")
            aperture = apertures[match[1]]
        elif match := re.fullmatch(r"%TO.N,([^*%\r\n]*)\*%", line):
            net = match[1]
        elif match := re.fullmatch(r"%TO.P,([^,*%\r\n]+),([^,*%\r\n]+)(?:,[^*%\r\n]*)?\*%", line):
            ref, pin = match[1], match[2]
        elif match := re.fullmatch(r"%TO.C,([^*%\r\n]+)\*%", line):
            ref, pin = match[1], ""
        elif line == "%TD*%":
            net, ref, pin = "", "", ""
        elif line in ("G01*", "G02*", "G03*"):
            require(legend or line == "G01*", f"Unsupported arc geometry: {path.name}")
            interpolation = line[:-1]
        elif line == "G75*":
            require(legend, f"Unsupported arc geometry: {path.name}")
            multi_quadrant = True
        elif line == "G36*":
            require(legend and region is None, "Unsupported/nested Gerber region")
            region = []
        elif line == "G37*":
            require(region is not None and len(region) >= 4 and region[0] == region[-1],
                    "Incomplete/unclosed Gerber region")
            region = None
        elif match := re.fullmatch(r"X([+-]?\d+)Y([+-]?\d+)I([+-]?\d+)J([+-]?\d+)D01\*", line):
            require(legend and point and aperture and aperture[2] == "C" and multi_quadrant
                    and interpolation in ("G02", "G03") and region is None, "Invalid/unsupported Gerber arc")
            new_point = (int(match[1]) / 1e6, int(match[2]) / 1e6)
            center = (point[0] + int(match[3]) / 1e6, point[1] + int(match[4]) / 1e6)
            radius = math.dist(point, center)
            require(radius > 0 and abs(radius - math.dist(new_point, center)) <= 0.000002, "Malformed Gerber arc radius")
            segments.append((*point, *new_point, aperture[0], net))
            point = new_point
        elif match := re.fullmatch(r"X([+-]?\d+)Y([+-]?\d+)D0([123])\*", line):
            require(aperture or region is not None, "Gerber draw without aperture")
            new_point = (int(match[1]) / 1e6, int(match[2]) / 1e6)
            if region is not None:
                require(interpolation == "G01" and match[3] in ("1", "2"), "Unsupported region operation")
                if match[3] == "2" and region:
                    require(len(region) >= 4 and region[0] == region[-1], "Unclosed Gerber region contour")
                    region = []
                require(region or match[3] == "2", "Region has no start point")
                region.append(new_point)
            elif match[3] == "3":
                flashes.append((*new_point, *aperture, ref, pin, net))
            elif match[3] == "1":
                require(point and aperture[2] == "C" and interpolation == "G01", "Unsupported Gerber stroke")
                ends = sorted((point, new_point))
                segments.append((*ends[0], *ends[1], aperture[0], net))
            point = new_point
        elif re.fullmatch(r"G04 [^*%\r\n]*\*|%T[FA]\.[A-Za-z][A-Za-z0-9_.]*(?:,[^*%\r\n]*)?\*%", line) or line in (
                "%MOMM*%", "%FSLAX46Y46*%", "%LPD*%", "M02*") or (legend and line == "%LPC*%"):
            continue
        else:
            raise VerificationError(f"Unsupported/malformed Gerber geometry in {path.name}: {line}")
    require(macro is None and region is None, "Unterminated Gerber macro/region")
    return flashes, segments


def validate_gerbers(directory, board):
    require({p.name for p in directory.glob("*.gbr")} == {item[0] for item in LAYERS.values()},
            "Missing/extra Gerber layers")
    require(not children(board.tree, "zone") and not children(board.tree, "arc"),
            "Copper zones/arcs need a tested export geometry validator")
    require(not any("B.Paste" in p.layers or "*.Paste" in p.layers for p in board.pads),
            "Bottom paste requires a B.Paste export and assembly-validation extension")
    pending = [(board.tree, None)]
    while pending:
        item, parent = pending.pop()
        pending.extend((node, item) for node in item[1:] if isinstance(node, list))
        if item[0] in ("kicad_pcb", "stackup", "layers"):
            continue
        layers = {layer for field in children(item, "layer") + children(item, "layers")
                  for layer in field[1:] if isinstance(layer, str)
                  and (layer == "Edge.Cuts" or layer.endswith((".Cu", ".Mask", ".Paste")))}
        if not layers:
            continue
        supported = (parent is board.tree and item[0] in ("footprint", "segment", "via") and layers <= {"F.Cu", "B.Cu"}
                     or parent is not None and parent[0] == "footprint" and item[0] == "pad"
                     and layers <= {"F.Cu", "B.Cu", "*.Cu", "F.Mask", "B.Mask", "*.Mask", "F.Paste"}
                     or parent is board.tree and item[0] in ("gr_rect", "gr_line") and layers == {"Edge.Cuts"}
                     and value(item, "fill", "none") in ("none", "no"))
        require(supported, f"Unsupported source geometry on critical manufacturing layers: {item[0]} {sorted(layers)}")
    require(numbers([value(child(board.tree, "setup"), "solder_mask_min_width", "0")])[0] == 0,
            "Merged/polygonal solder mask needs an export geometry validator")
    via_masks = via_mask_settings(board)
    vias = {(pad.x, pad.y): pad for pad in board.pads if pad.kind == "via"}

    def pad_aperture(pad, layer):
        require(pad.rotation % 90 == 0 or pad.shape == "circle", "Non-orthogonal pad needs geometry support")
        shape = {"circle": "C", "rect": "R", "oval": "O", "roundrect": "RoundRect"}.get(pad.shape)
        require(shape, f"Unsupported pad shape: {pad.shape}")
        size, radius = (pad.width, pad.height), 0.0
        if layer.endswith(("Mask", "Paste")):
            margin = pad.mask_margin if layer.endswith("Mask") else pad.paste_margin
            ratio = 0 if layer.endswith("Mask") else pad.paste_ratio
            mx, my = margin + pad.width * ratio, margin + pad.height * ratio
            size = (pad.width + 2 * mx, pad.height + 2 * my)
            if pad.shape == "rect" and mx > 0:
                shape, radius = "RoundRect", min(mx, min(size) / 2)
        require(min(size) > 0, "Unsupported paste/mask aperture geometry")
        # KiCad 9 PlotStandardLayer retains the roundrect ratio after resizing,
        # but rounds an expanded rectangular pad using its local X margin.
        if pad.shape == "roundrect":
            radius = min(size) * pad.roundrect_ratio
        if shape == "RoundRect":
            # GERBER_PLOTTER enforces a 10 nm minimum half-core even at ratio .5.
            size = tuple(2 * (max(d / 2 - radius, 0.00001) + radius) for d in size)
        if pad.rotation % 180:
            size = size[::-1]
        return (*size, shape, radius)

    result = {}
    codes = {node[1]: node[2] for node in children(board.tree, "net")}
    for layer, (filename, function) in LAYERS.items():
        flashes, segments = parse_gerber(directory / filename, function)
        result[layer] = {"flashes": len(flashes), "segments": len(segments)}
        if layer in ("F.Cu", "B.Cu"):
            expected = []
            for pad in board.pads:
                if pad.kind == "np_thru_hole" or not (layer in pad.layers or "*.Cu" in pad.layers):
                    continue
                expected.append((pad.x, -pad.y, *pad_aperture(pad, layer),
                                 "" if pad.kind == "via" else pad.ref, pad.pin, pad.net))
            match_geometry(flashes, expected, 0.000002, layer + " pad/via flashes")
            expected = []
            for item in children(board.tree, "segment"):
                if value(item, "layer") != layer:
                    continue
                start, end = numbers(child(item, "start")[1:]), numbers(child(item, "end")[1:])
                ends = sorted(((start[0], -start[1]), (end[0], -end[1])))
                expected.append((*ends[0], *ends[1], float(value(item, "width")), codes[value(item, "net")]))
            match_geometry(segments, expected, 0.000002, layer + " copper segments")
        elif layer == "Edge.Cuts":
            expected = []
            for item in board.tree[1:]:
                if not isinstance(item, list) or not item[0].startswith("gr_"):
                    continue
                if value(item, "layer", "") != layer:
                    continue
                require(item[0] in ("gr_rect", "gr_line"), "Unsupported outline geometry")
                start, end = numbers(child(item, "start")[1:]), numbers(child(item, "end")[1:])
                points = [(start[0], -start[1]), (end[0], -end[1])]
                if item[0] == "gr_rect":
                    points = [points[0], (end[0], -start[1]), points[1], (start[0], -end[1]), points[0]]
                for a, b in zip(points, points[1:]):
                    ends = sorted((a, b))
                    expected.append((*ends[0], *ends[1]))
            require(expected and not flashes, "Empty/invalid outline")
            match_geometry([s[:4] for s in segments], expected, 0.000002, "outline segments")
        elif layer.endswith(("Mask", "Paste")):
            require(not segments, "Non-flashed mask/paste apertures need geometry support")
            expected = []
            side = 0 if layer == "F.Mask" else 1
            for pad in board.pads:
                if pad.kind == "via":
                    front, back, radius = via_masks[(pad.x, pad.y)]
                    if layer.endswith("Mask") and not (front, back)[side]:
                        expected.append((pad.x, -pad.y, 2 * radius, 2 * radius, "C", 0, "", "", ""))
                    continue
                if not (layer in pad.layers or "*." + layer.split(".")[1] in pad.layers):
                    continue
                expected.append((pad.x, -pad.y, *pad_aperture(pad, layer), pad.ref, "", ""))
            matched = match_geometry(flashes, expected, 0.000002, layer + " aperture inventory/size/corners")
            # Conservative bounding rectangles cover ordinary circle/oval/roundrect
            # component flashes. Via exceptions require a matched source owner,
            # both openings requested on this side, and overlapping same-net copper.
            for via in vias.values():
                for flash, source in zip(flashes, matched):
                    x, y, width, height, shape, radius, ref, pin, net = flash
                    opening = vias.get((source[0], -source[1])) if layer.endswith("Mask") and not ref else None
                    if (opening is not None and not via_masks[(via.x, via.y)][side] and opening.net == via.net
                            and math.dist((opening.x, opening.y), (via.x, via.y)) <= (opening.width + via.width) / 2):
                        continue
                    dx, dy = max(abs(via.x - x) - width / 2, 0), max(abs(-via.y - y) - height / 2, 0)
                    require(math.hypot(dx, dy) > via.drill / 2 + 0.000002,
                            f"Exported {layer} aperture {ref} exposes via hole at ({via.x}, {via.y})")
    return result


def make_zip(path, members):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, source in sorted(members.items()):
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())
    validate_zip(path, members)


def validate_zip(path, members):
    with zipfile.ZipFile(path) as archive:
        require(len(archive.namelist()) == len(members) and set(archive.namelist()) == set(members)
                and archive.testzip() is None, f"Wrong/corrupt ZIP membership: {path.name}")
        require(all(archive.read(name) == source.read_bytes() for name, source in members.items()),
                f"ZIP payload differs from verified artifacts: {path.name}")


class Manufacturing:
    def __init__(self, root, cli=""):
        self.root = root.resolve()
        self.staging = self.root / "tmp" / "manufacturing"
        self.build = self.root / "build"
        self.cli_setting = cli
        self.commands, self.errors, self.verification = [], [], {}
        self.version, self.sources, self.revision = None, {}, None
        self.review = {}

    def invoke(self, command, label, gate=True):
        command = list(map(str, command))
        try:
            process = subprocess.run(command, cwd=self.project, text=True, capture_output=True,
                                     timeout=600, env={**os.environ, "LC_ALL": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1"})
            result = {"command": command, "returncode": process.returncode,
                      "stdout": process.stdout, "stderr": process.stderr}
        except (OSError, subprocess.TimeoutExpired) as exc:
            result = {"command": command, "returncode": -1, "stdout": "", "stderr": str(exc)}
        self.commands.append(result)
        (self.reports / f"{label}.log").write_text(
            shlex.join(command) + "\n" + result["stdout"] + result["stderr"] +
            f"\nexit={result['returncode']}\n", encoding="utf-8")
        if gate and result["returncode"]:
            self.errors.append(f"{label} failed (exit {result['returncode']}); see retained log")
        return result

    def resolve_cli(self):
        candidates = [shlex.split(self.cli_setting)] if self.cli_setting else [
            ["kicad-cli"], ["kicad.kicad-cli"], ["/snap/bin/kicad.kicad-cli"],
            ["flatpak", "run", "--command=kicad-cli", "org.kicad.KiCad"]]
        for index, command in enumerate(candidates):
            require(command, "Empty KiCad invocation")
            result = self.invoke(command + ["--version"], f"version-{index}", gate=False)
            version = result["stdout"].strip()
            if result["returncode"] == 0 and re.fullmatch(r"9\.\d+\.\d+", version):
                self.cli, self.version = command, version
                return
        raise VerificationError("Could not invoke a KiCad 9 CLI successfully; see actual --version logs")

    def retain_reports(self, state):
        for kind in ("drc", "erc"):
            for extension in ("txt", "json"):
                path = self.reports / f"{kind}_report.{extension}"
                if not path.exists():
                    message = "Not completed; see verification.json and command logs"
                    if extension == "json":
                        write_json(path, {"verified": False, "status": "not_completed", "error": message})
                    else:
                        path.write_text(message + "\n", encoding="utf-8")
        write_json(self.reports / "commands.json", self.commands)
        write_json(self.reports / "verification.json", {
            "status": state, "errors": self.errors, "checks": self.verification,
            "source_hashes": self.sources, "hardware_revision": self.revision,
            "tool_version": self.version, "scope": SCOPE,
        })
        self.build.mkdir(exist_ok=True)
        shutil.copytree(self.reports, self.build / "reports", dirs_exist_ok=True)
        for kind in ("drc", "erc"):
            for extension in ("txt", "json"):
                shutil.copy2(self.reports / f"{kind}_report.{extension}", self.build)
        write_json(self.build / "status.json", {"status": state, "attempt": str(self.run.relative_to(self.root)),
                                               "requires_verified_manifest_for_upload": True})

    def run_checks(self):
        pcb, sch = self.project / "pcb.kicad_pcb", self.project / "pcb.kicad_sch"
        for kind, domain, source in (("drc", "pcb", pcb), ("erc", "sch", sch)):
            results = []
            for fmt, extension in (("report", "txt"), ("json", "json")):
                args = [domain, kind, "--format", fmt, "--units", "mm", "--severity-all", "--exit-code-violations"]
                if kind == "drc":
                    args += ["--schematic-parity", "--all-track-errors"]
                report = self.reports / f"{kind}_report.{extension}"
                results.append(self.invoke(self.cli + args + ["--output", report, source], f"{kind}-{fmt}", gate=False))
            try:
                require(all(result["returncode"] in (0, 5) for result in results),
                        f"{kind.upper()} command failed; see retained logs")
                text = (self.reports / f"{kind}_report.txt").read_text(encoding="utf-8")
                require(text.strip() and "report" in text.lower(), f"Missing/malformed {kind.upper()} text report")
                labels = self.review["reviewed_single_global_labels"] if kind == "erc" else {}
                checked = validate_report(self.reports / f"{kind}_report.json", kind, self.version, labels)
                require(all(result["returncode"] == (5 if checked["violations"] else 0) for result in results),
                        f"{kind.upper()} report/exit status differs")
                self.verification[kind] = checked
                if checked["reviewed_warnings"]:
                    print(f"{kind.upper()}: {checked['reviewed_warnings']} explicitly reviewed label warnings; full reports retained.")
            except (VerificationError, OSError, ValueError, TypeError) as exc:
                self.errors.append(str(exc))
        geometry = self.reports / "geometry.json"
        result = self.invoke([sys.executable, "-B", self.run / "scripts" / "check_geometry.py", "--pcb", pcb,
                              "--project", self.project / "pcb.kicad_pro", "--rules", self.project / "pcb.kicad_dru",
                              "--output", geometry], "geometry")
        try:
            data = read_json(geometry)
            require(isinstance(data, dict) and data.get("schema_version") == 1
                    and data.get("check") == "physical_geometry", "Empty/unrecognized geometry report")
            require(result["returncode"] == 0 and data.get("ok") is True and data.get("status") == "pass"
                    and data.get("diagnostics") == [], "Geometry checker rejected design")
            for name, source in (("pcb", pcb), ("project", self.project / "pcb.kicad_pro"),
                                 ("rules", self.project / "pcb.kicad_dru")):
                require(data.get("inputs", {}).get(name, {}).get("sha256") == sha256(source),
                        "Geometry report does not describe this source snapshot")
            self.verification["geometry"] = {"verified": True, "report_sha256": sha256(geometry)}
        except (VerificationError, OSError, ValueError, TypeError) as exc:
            self.errors.append(str(exc))

    def export_and_validate(self, board):
        pcb, sch = self.project / "pcb.kicad_pcb", self.project / "pcb.kicad_sch"
        scratch = self.run / "exports"
        gerbers, drills = scratch / "gerbers", scratch / "drills"
        gerbers.mkdir(parents=True)
        drills.mkdir()
        xml, ipc, native_pos = scratch / "schematic.xml", scratch / "pcb.d356", scratch / "native-pos.csv"
        jobs = [
            (["sch", "export", "netlist", "--format", "kicadxml", "--output", xml, sch], "netlist"),
            (["pcb", "export", "ipcd356", "--output", ipc, pcb], "ipc"),
            (["pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp",
              "--output", native_pos, pcb], "positions"),
            (["pcb", "export", "gerbers", "--layers", ",".join(LAYERS), "--precision", "6", "--no-protel-ext",
              "--subtract-soldermask", "--output", str(gerbers) + "/", pcb], "gerbers"),
            (["pcb", "export", "drill", "--format", "excellon", "--drill-origin", "absolute", "--excellon-units", "mm",
              "--excellon-zeros-format", "decimal", "--excellon-separate-th", "--output", str(drills) + "/", pcb], "drills"),
            (["pcb", "export", "pdf", "--layers", "F.Fab,F.SilkS,Edge.Cuts", "--mode-single", "--black-and-white",
              "--output", scratch / "Assembly.pdf", pcb], "assembly"),
        ]
        annotation = self.review.get("reviewed_netlist_annotation")
        annotation_seen = False
        export_diagnostics = []
        informational_stderr = {}
        for arguments, label in jobs:
            result = self.invoke(self.cli + arguments, label)
            stderr = result["stderr"]
            if arguments[0] == "pcb" and self.version == "9.0.7":
                # wxWidgets startup debug output, not a design/export warning.
                stderr, count = re.subn(WX_IMAGE_DEBUG, "", stderr)
                if count:
                    informational_stderr[label] = count
            diagnostic = stderr.strip() or re.search(r"(?im)^\s*(?:warning|error)\b", result["stdout"])
            if not diagnostic:
                continue
            dependencies = {name: digest for name, digest in self.sources.items() if name.startswith("pcb/")
                            and (Path(name).suffix in (".kicad_sch", ".kicad_pro", ".kicad_sym")
                                 or Path(name).name in ("fp-lib-table", "sym-lib-table"))}
            reviewed = (label == "netlist" and isinstance(annotation, dict) and annotation.get("reason")
                        and self.version == annotation.get("tool_version") == "9.0.7"
                        and result["returncode"] == 0 and result["stderr"] == ""
                        and result["stdout"] == annotation.get("stdout") ==
                        "Warning: schematic has annotation errors, please use the schematic editor to fix them\n"
                        and dependencies == annotation.get("source_hashes"))
            export_diagnostics.append({"command": label, "stdout": result["stdout"], "stderr": result["stderr"],
                                       "reviewed": bool(reviewed)})
            if reviewed:
                annotation_seen = True
                print("Netlist: exact hash-bound annotation warning reviewed; full diagnostic retained.")
            else:
                self.errors.append(f"Unreviewed {label} export diagnostic; see retained log")
        if annotation and not annotation_seen:
            self.errors.append("Stale netlist annotation review; recheck source and native diagnostics")
        self.verification["export_diagnostics"] = {"verified": not self.errors, "diagnostics": export_diagnostics,
                                                   "informational_stderr": informational_stderr}
        require(not self.errors, "Native checks/exports failed; nothing will be published")
        nets = parse_netlist(xml)
        require(not differences(nets, board.nets), "Schematic/PCB nets differ: " + "\n".join(differences(nets, board.nets)))
        self.verification["nets"] = {"verified": True, "nets": len(nets), "terminals": sum(map(len, nets.values())),
                                     "ipc": compare_ipc(ipc, board)}
        bom = validate_bom(self.project / "BOM.csv", xml, board)
        positions = generate_cpl(native_pos, scratch / "CPL.csv", board)
        require(set(positions) == set(bom), "BOM/CPL population differs")
        self.verification["population"] = {"verified": True, "count": len(bom), "references": sorted(bom)}
        self.verification["gerbers"] = validate_gerbers(gerbers, board)
        require({p.name for p in drills.iterdir()} == DRILLS, "Missing/extra drill files")
        self.verification["drills"] = {name: validate_drill(drills / name, board, name == "pcb-PTH.drl")
                                       for name in sorted(DRILLS)}
        pdf = (scratch / "Assembly.pdf").read_bytes()
        require(pdf.startswith(b"%PDF-") and b"%%EOF" in pdf[-1024:], "Missing/incomplete assembly PDF")
        release = self.run / "release"
        release.mkdir()
        (release / "gerbers").mkdir()
        for name in FAB_FILES:
            shutil.copy2((drills if name in DRILLS else gerbers) / name, release / "gerbers" / name)
        for name in ("pcb.d356", "CPL.csv", "Assembly.pdf"):
            shutil.copy2(scratch / name, release / name)
        shutil.copy2(self.project / "BOM.csv", release / "BOM.csv")
        for name in (*ENGINEERING_NOTES, "verification.json"):
            shutil.copy2(self.project / name, release / name)
        assembly = [f"Dog Fence {self.revision} - native assembly placement reference", SCOPE["placement"],
                    "Not an accepted JLCPCB placement model. Confirm all centroids, rotations and polarity.",
                    "GDT_AC forming/standoff and exact pin fit require controlled assembly acceptance.", "",
                    "Reference | MPN | X mm | Y mm | Rotation deg | Side"]
        for ref in sorted(positions):
            row = positions[ref]
            assembly.append(" | ".join([ref, bom[ref]["MPN"], *row[3:]]))
        (release / "Assembly.txt").write_text("\n".join(assembly) + "\n", encoding="utf-8")
        with (release / "ViaTreatment.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream, lineterminator="\n")
            writer.writerow(["Function", "Net", "PCB X mm", "PCB Y mm", "Drill mm", "Pad mm",
                             "Requested front tented", "Requested back tented", "Treatment"])
            via_masks = via_mask_settings(board)
            for p in sorted((p for p in board.pads if p.kind == "via"), key=lambda p: (p.x, p.y)):
                front, back, _ = via_masks[(p.x, p.y)]
                treatment = "Standard untented" if not front and not back else "Source-requested tenting (not a seal)"
                writer.writerow(["Stitching via", p.net, p.x, p.y, p.drill, p.width,
                                 "yes" if front else "no", "yes" if back else "no",
                                 treatment + "; no fill; preserve diameters; CAM acceptance not established"])
        members = {name: release / "gerbers" / name for name in FAB_FILES}
        make_zip(release / "Gerbers.zip", members)
        readme = scratch / "README.txt"
        readme.write_text(f"Dog Fence {self.revision} - bare-board flying-probe input\n"
                          "Contains pcb.d356 and Gerbers.zip. Not assembled functional or surge testing.\n", encoding="utf-8")
        make_zip(release / "FlyTest.zip", {"pcb.d356": release / "pcb.d356",
                                          "Gerbers.zip": release / "Gerbers.zip", "README.txt": readme})
        self.verification["archives"] = {"verified": True, "Gerbers.zip": sorted(members),
                                         "FlyTest.zip": ["Gerbers.zip", "README.txt", "pcb.d356"]}
        return release

    def execute(self, mode):
        require(mode in ("build", "check", "clean"), "Unknown manufacturing mode")
        require(not (self.root / "tmp").is_symlink() and not self.staging.is_symlink()
                and not self.build.is_symlink(), "Refusing symlinked build/staging paths")
        self.staging.mkdir(parents=True, exist_ok=True)
        with (self.staging / "lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            if mode == "clean":
                if self.build.exists():
                    shutil.rmtree(self.build)
                runs = self.staging / "runs"
                if runs.exists():
                    shutil.rmtree(runs)
                (self.root / "pcb" / "Gerbers.zip").unlink(missing_ok=True)
                print("Removed build outputs and tmp/manufacturing/runs only. Other tmp/ evidence and CPL mirror retained.")
                return 0
            runs = self.staging / "runs"
            runs.mkdir(exist_ok=True)
            self.run = Path(tempfile.mkdtemp(prefix="attempt-", dir=runs))
            self.project, self.reports = self.run / "project", self.run / "reports"
            self.project.mkdir()
            self.reports.mkdir()
            if self.build.exists():
                self.build.rename(self.run / "previous-build")
            self.build.mkdir()
            mirror = self.root / "pcb" / "Gerbers.zip"
            if mirror.exists():
                mirror.rename(self.run / "previous-pcb-Gerbers.zip")
            self.retain_reports("running")
            state = "failed"
            try:
                self.sources = source_inventory(self.root)
                for name in self.sources:
                    target = self.project / name[4:] if name.startswith("pcb/") else self.run / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(self.root / name, target)
                    require(sha256(target) == self.sources[name], f"Source changed during staging: {name}")
                require(source_inventory(self.root) == self.sources, "Sources changed while staging")
                self.resolve_cli()
                board, self.revision = validate_project(self.project)
                self.review = read_json(self.project / "verification.json")
                require(self.review.get("schema_version") == 1 and self.review.get("hardware_revision") == self.revision,
                        "Missing/mismatched revision-bound verification review")
                labels = self.review.get("reviewed_single_global_labels")
                require(isinstance(labels, dict) and all(isinstance(k, str) and isinstance(v, str) and k and v
                                                        for k, v in labels.items()), "Malformed label warning review")
                schematic = read_tree(self.project / "pcb.kicad_sch")
                actual_labels = {value(item, "uuid"): item[1] for item in children(schematic, "global_label")}
                require(not labels or (not children(schematic, "sheet") and labels == actual_labels
                                       and self.review.get("single_global_label_review")),
                        "Single-sheet label review no longer describes this schematic")
                holds = self.review.get("release_holds")
                require(isinstance(holds, list) and all(isinstance(h, dict) and h.get("id") and h.get("reason")
                                                       for h in holds), "Missing/malformed release hold inventory")
                require(holds or self.review.get("file_release_review"), "File-release review is required before clearing holds")
                self.verification["engineering_release"] = {"verified": not holds, "holds": holds,
                                                            "review": self.review.get("file_release_review")}
                self.verification["project"] = {"verified": True, "complete_local_libraries": True}
                self.run_checks()
                # Provisional exports also run after rule violations, providing native
                # diagnostic evidence; no release is built if ANY command/check failed.
                release = self.export_and_validate(board)
                for name, digest in self.sources.items():
                    staged = self.project / name[4:] if name.startswith("pcb/") else self.run / name
                    require(sha256(staged) == digest, f"Staged source changed during verification: {name}")
                require(source_inventory(self.root) == self.sources, "Sources changed during verification; rerun")
                # This is a draft placement reference, not publication of an order package.
                pending_cpl = self.run / "mirror-CPL.csv"
                shutil.copy2(release / "CPL.csv", pending_cpl)
                os.replace(pending_cpl, self.root / "pcb" / "CPL.csv")
                if holds:
                    print("Manufacturing release held: " + "; ".join(f"{h['id']}: {h['reason']}" for h in holds))
                require(mode != "build" or not holds, "Open engineering release holds; verified draft exports retained privately")
                state = "checked" if mode == "check" else "verified"
                if mode == "build":
                    revision = self.invoke(["git", "rev-parse", "HEAD"], "git-revision", gate=False)
                    dirty = self.invoke(["git", "status", "--porcelain"], "git-status", gate=False)
                    self.retain_reports(state)
                    shutil.copytree(self.build, release, dirs_exist_ok=True)
                    artifacts = {p.relative_to(release).as_posix(): sha256(p) for p in sorted(release.rglob("*")) if p.is_file()}
                    manifest = {"status": "verified", "hardware_revision": self.revision,
                                "created_utc": datetime.now(timezone.utc).isoformat(),
                                "git_revision": revision["stdout"].strip() if revision["returncode"] == 0 else None,
                                "worktree_dirty": bool(dirty["stdout"].strip()) if dirty["returncode"] == 0 else None,
                                "tool": {"command": self.cli, "version": self.version, "baseline_major": 9},
                                "python_version": sys.version.split()[0],
                                "source_hashes": self.sources, "artifact_hashes": artifacts,
                                "verification": self.verification, "scope": SCOPE}
                    require(source_inventory(self.root) == self.sources, "Sources changed before publication")
                    # Publish complete payload, then mirrors, then the verification marker.
                    # A failed/interrupted publication has no verified manifest.
                    self.build.rename(self.run / "current-reports")
                    release.rename(self.build)
                    for name in ("CPL.csv", "Gerbers.zip"):
                        pending = self.run / ("mirror-" + name)
                        shutil.copy2(self.build / name, pending)
                        os.replace(pending, self.root / "pcb" / name)
                    write_json(self.build / "manifest.json", manifest)
                print(f"Manufacturing data {'verified' if mode == 'build' else 'checked (not published)'} for revision {self.revision}.")
                print("File checks only, not CAM acceptance, order approval or surge certification.")
                return 0
            except (VerificationError, OSError, ValueError, KeyError, TypeError, ImportError, csv.Error,
                    zipfile.BadZipFile) as exc:
                self.errors.append(str(exc))
                state = "failed"
                (self.build / "manifest.json").unlink(missing_ok=True)
                print(f"Manufacturing verification FAILED: {exc}", file=sys.stderr)
                return 1
            finally:
                if state != "verified":
                    self.retain_reports(state if not self.errors else "failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("build", "check", "clean"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--kicad-cli", default=os.environ.get("KICAD_CLI", ""), help="CLI invocation, shell quoting allowed; no shell is executed")
    args = parser.parse_args()
    try:
        return Manufacturing(args.root, args.kicad_cli).execute(args.mode)
    except (VerificationError, OSError) as exc:
        print(f"Manufacturing verification FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
