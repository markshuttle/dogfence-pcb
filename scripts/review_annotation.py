#!/usr/bin/env python3
"""Collect hash-bound annotation evidence, NEVER update a warning approval.

Run with python3 -B scripts/review_annotation.py [--cli 'CLI invocation'].
Each run retains complete private projects, raw native output and comparisons in
tmp/annotation-review/hybrid-*/. Only KiCad 9.0.7 kicadxml exports are exercised;
no ERC, DRC, manufacturing transaction, GUI, publication or source write occurs.
The numbered and deliberately invalid schematics are probes, not CAD candidates.
PASS means the evidence checks passed, not that a person approved the warning.
"""

import argparse
import copy
import csv
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pcb import sync_libraries as sync
from scripts import compare_nets as nets
from scripts import manufacturing as m


VERSION = "9.0.7"
WARNING = "Warning: schematic has annotation errors, please use the schematic editor to fix them\n"
NUMBERED = {
    "J_IN": "J1", "J_EARTH": "J2", "J_LED_A": "J3", "J_LED_C": "J4",
    "GDT_AB": "GDT1", "GDT_BC": "GDT2", "GDT_AC": "GDT3",
    "GDT_A_E": "GDT4", "GDT_B_E": "GDT5", "GDT_C_E": "GDT6",
}
REVIEW_INPUTS = {
    "pcb/pcb.kicad_sch", "pcb/pcb.kicad_pro", "pcb/DogFence.kicad_sym",
    "pcb/fp-lib-table", "pcb/sym-lib-table",
}
EXTRA_INPUTS = ("scripts/review_annotation.py", "pcb/sync_libraries.py")
EXPECTED_COUNTS = {"components": 20, "nets": 8, "terminals": 34, "populated": 16, "mechanical": 4}


def source_hashes(root):
    result = m.source_inventory(root)
    for name in EXTRA_INPUTS:
        path = root / name
        m.require(path.is_file() and not path.is_symlink() and path.stat().st_size,
                  f"Missing/empty/linked review helper: {name}")
        result[name] = m.sha256(path)
    return result


def tree_hashes(directory):
    m.require(directory.is_dir() and not directory.is_symlink(), f"Missing/linked evidence tree: {directory}")
    result = {}
    for path in sorted(directory.rglob("*")):
        m.require(not path.is_symlink() and (path.is_dir() or path.is_file()), f"Non-regular evidence: {path}")
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = m.sha256(path)
    return result


def validate_references(path):
    """Fail closed on anything outside one sheet, one project and unit 1.

    Native annotation diagnostics are aggregate and cannot replace this check.
    Inspect source properties AND instance references before trusting XML refs.
    """
    tree = nets.read_tree(path)
    m.require(tree[0] == "kicad_sch" and not nets.children(tree, "sheet")
              and not nets.children(tree, "symbol_instances"), "Only the current single-sheet schema is supported")
    root_uuid = nets.value(tree, "uuid")
    sheet_instances = nets.child(tree, "sheet_instances")
    m.require(sheet_instances == ["sheet_instances", ["path", "/", ["page", "1"]]],
              "Unexpected sheet instance inventory")
    references, identifiers = {}, set()
    for symbol in nets.children(tree, "symbol"):
        props = {}
        for prop in nets.children(symbol, "property"):
            m.require(len(prop) >= 3 and all(isinstance(v, str) for v in prop[1:3])
                      and prop[1] not in props, "Malformed/duplicate source property")
            props[prop[1]] = prop[2]
        ref = props.get("Reference", "")
        instances = nets.child(symbol, "instances")
        project = nets.child(instances, "project")
        m.require(len(instances) == 2 and len(project) == 3 and project[1] == "pcb",
                  f"Unexpected source project instances: {ref}")
        instance = nets.child(project, "path")
        m.require(len(instance) == 4 and instance[1] == "/" + root_uuid,
                  f"Unexpected source instance path: {ref}")
        instance_ref = nets.value(instance, "reference")
        m.require(ref == instance_ref, f"Property/instance reference mismatch: {ref!r} != {instance_ref!r}")
        m.require(ref in NUMBERED or re.fullmatch(r"[A-Z]+[1-9][0-9]*", ref),
                  f"Unassigned or unexpected source reference: {ref!r}")
        m.require(ref not in references, f"Duplicate source reference: {ref}")
        unit = nets.value(symbol, "unit")
        m.require(unit == nets.value(instance, "unit") == "1", f"Unexpected source unit: {ref}")
        identifier = nets.value(symbol, "uuid")
        m.require(identifier and identifier not in identifiers, f"Missing/duplicate source symbol UUID: {ref}")
        identifiers.add(identifier)
        references[ref] = {"property_reference": ref, "instance_reference": instance_ref,
                           "uuid": identifier, "instance_path": instance[1], "unit": unit,
                           "lib_id": nets.value(symbol, "lib_id"), "properties": props}
    m.require(references, "Empty source reference inventory")
    return references


def numbering_map(references):
    nonnumeric = {ref for ref in references if not re.fullmatch(r"[A-Z]+[1-9][0-9]*", ref)}
    m.require(nonnumeric == set(NUMBERED), "The exact ten intentional nonnumeric references have changed")
    m.require(not set(NUMBERED.values()).intersection(references), "Numbered-reference control would collide")
    return NUMBERED.copy()


def rename_references(tree, mapping, locations=("property", "instance")):
    """Edit only named reference atoms in the existing lossless-token list tree."""
    m.require(locations and set(locations) <= {"property", "instance"}, "Unknown reference location")
    result, found = copy.deepcopy(tree), set()
    for symbol in sync.children(result, "symbol"):
        props = [p for p in sync.children(symbol, "property") if json.loads(p[1]) == "Reference"]
        m.require(len(props) == 1, "Expected one source Reference property")
        prop = props[0]
        old = json.loads(prop[2])
        if old not in mapping:
            continue
        m.require(old not in found, f"Ambiguous reference mutation: {old}")
        found.add(old)
        instance = sync.child(sync.child(sync.child(symbol, "instances"), "project"), "path")
        ref = sync.child(instance, "reference")
        m.require(json.loads(ref[1]) == old, f"Cannot mutate mismatched reference: {old}")
        if "property" in locations:
            prop[2] = json.dumps(mapping[old])
        if "instance" in locations:
            ref[1] = json.dumps(mapping[old])
    m.require(found == set(mapping), f"Missing mutation references: {sorted(set(mapping) - found)}")
    return result


def export_proof(xml_path, references, board, bom_path, baseline=None, inverse=None):
    """Validate native XML; inverse renaming is in-memory, never an XML rewrite."""
    inverse = inverse or {}
    parsed = nets.parse_netlist(xml_path)
    components = nets.read_xml(xml_path).findall("components/comp")
    m.require({comp.get("ref") for comp in components} == set(references),
              "Source/XML reference inventory differs")
    contents = {}
    for comp in components:
        ref = inverse.get(comp.get("ref"), comp.get("ref"))
        m.require(ref not in contents, "Inverse reference mapping collides")
        comp.set("ref", ref)
        comp.tail = None  # Inter-component XML indentation is not component content.
        contents[ref] = ET.tostring(comp, encoding="unicode")
    normalized = {name: {(inverse.get(ref, ref), pin) for ref, pin in nodes} for name, nodes in parsed.items()}
    diffs = nets.differences(normalized, board.nets)
    m.require(not diffs, "Schematic/PCB terminal membership differs: " + "\n".join(diffs))
    bom = m.validate_bom(bom_path, xml_path, board) if baseline is None else m.read_bom(bom_path)
    proof = {
        "counts": {"components": len(components), "nets": len(parsed), "terminals": sum(map(len, parsed.values())),
                   "populated": len(bom), "mechanical": sum(fp.mechanical for fp in board.footprints.values())},
        "terminal_membership": {name: sorted(nodes) for name, nodes in normalized.items()},
        "component_contents": contents, "bom": bom,
    }
    m.require(baseline is None or proof == baseline, "Numbered export differs after inverse renaming")
    return proof


def require_output(result, stdout):
    m.require(not result.get("execution_error") and result["returncode"] == 0
              and result["stdout"] == stdout and result["stderr"] == "",
              "Unexpected native exit/stdout/stderr; inspect retained command and raw output")


class NativeCommands:
    # Reuse argv-safe resolution only, never the manufacturing transaction.
    resolve_cli = m.Manufacturing.resolve_cli

    def __init__(self, run, project, cli):
        self.run, self.project, self.cli_setting = run, project, cli
        self.commands, self.cli, self.version = [], [], None
        (run / "logs").mkdir()
        (run / "native-tmp").mkdir()
        self.environment = {"LC_ALL": "C.UTF-8", "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1",
                            "TMPDIR": str(run / "native-tmp")}

    def invoke(self, command, label, gate=False):
        command = list(map(str, command))
        record = {"command": command, "shell_command": shlex.join(command), "cwd": str(self.project),
                  "environment_overrides": self.environment, "started_utc": datetime.now(timezone.utc).isoformat(),
                  "returncode": None, "stdout_file": f"logs/{label}.stdout", "stderr_file": f"logs/{label}.stderr"}
        self.commands.append(record)
        m.write_json(self.run / "commands.json", self.commands)
        stdout = stderr = b""
        try:
            process = subprocess.run(command, cwd=self.project, stdin=subprocess.DEVNULL, capture_output=True,
                                     timeout=120, env={**os.environ, **self.environment})
            record["returncode"] = process.returncode
            stdout, stderr = process.stdout, process.stderr
        except (OSError, subprocess.TimeoutExpired) as exc:
            record.update(returncode=-1, execution_error=f"{type(exc).__name__}: {exc}")
            if isinstance(exc, subprocess.TimeoutExpired):
                stdout, stderr = exc.stdout or b"", exc.stderr or b""
        for stream, raw in (("stdout", stdout), ("stderr", stderr)):
            path = self.run / record[stream + "_file"]
            path.write_bytes(raw)
            record[stream] = raw.decode("utf-8", errors="surrogateescape")
            record[stream + "_sha256"] = m.sha256(path)
        record["finished_utc"] = datetime.now(timezone.utc).isoformat()
        m.write_json(self.run / "commands.json", self.commands)
        return record


def review(root, cli=""):
    root = root.resolve()
    for name in ("pcb", "tmp", "tmp/annotation-review"):
        m.require(not (root / name).is_symlink(), f"Refusing linked review path: {name}")
    area = root / "tmp/annotation-review"
    area.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="hybrid-", dir=area))
    print(f"Annotation evidence: {run}", flush=True)
    report = {"schema_version": 1, "status": "running", "errors": [], "cases": {},
              "scope": "Evidence only. Manual warning review required; no approval, source update, or release.",
              "process_argv": sys.orig_argv, "process_cwd": str(Path.cwd()), "python_version": sys.version,
              "started_utc": datetime.now(timezone.utc).isoformat(), "commands_file": "commands.json"}
    m.write_json(run / "report.json", report)
    m.write_json(run / "commands.json", [])
    before, snapshot_before, completed = {}, {}, False
    snapshot = run / "snapshot"
    try:
        before = source_hashes(root)
        report["source_hashes_before"] = before
        dependencies = {name: digest for name, digest in before.items() if name.startswith("pcb/")
                        and (Path(name).suffix in (".kicad_sch", ".kicad_pro", ".kicad_sym")
                             or Path(name).name in ("fp-lib-table", "sym-lib-table"))}
        report["review_input_hashes_before"] = dependencies
        m.require(set(dependencies) == REVIEW_INPUTS, "Annotation review dependency inventory changed; extend the review explicitly")
        for name, digest in before.items():
            target = snapshot / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / name, target)
            m.require(m.sha256(target) == digest, f"Source changed during copying: {name}")
        snapshot_before = tree_hashes(snapshot)
        m.require(snapshot_before == before == source_hashes(root), "Sources changed during snapshot")
        board, report["hardware_revision"] = m.validate_project(snapshot / "pcb")
        old = m.read_json(snapshot / "pcb/verification.json").get("reviewed_netlist_annotation", {}).get("source_hashes", {})
        report["previous_review"] = {"source_hashes": old, "matches_current_inputs": old == dependencies,
                                     "different_inputs": sorted(name for name in old.keys() | dependencies.keys()
                                                                if old.get(name) != dependencies.get(name))}
        native = NativeCommands(run, snapshot / "pcb", cli)
        native.resolve_cli()
        report["tool"] = {"command": native.cli, "version": native.version}
        m.require(native.version == VERSION, f"This review requires KiCad {VERSION}, found {native.version}")
        require_output(native.commands[-1], VERSION + "\n")
        original = sync.parse((snapshot / "pcb/pcb.kicad_sch").read_text(encoding="utf-8"))
        project_hashes = {name[4:]: digest for name, digest in before.items() if name.startswith("pcb/")}
        baseline = None
        cases = [
            ("baseline", {}, ("property", "instance"), None),
            ("numbered", NUMBERED, ("property", "instance"), None),
            ("duplicate", {"D2": "D1"}, ("property", "instance"), "Duplicate source reference"),
            ("unassigned", {"R2": "R?"}, ("property", "instance"), "Unassigned or unexpected source reference"),
            ("property-instance-mismatch", {"R2": "R9"}, ("property",), "Property/instance reference mismatch"),
        ]
        for label, mapping, locations, expected_error in cases:
            case_dir = run / label
            project = case_dir / "project"
            case = report["cases"][label] = {"expected_source_rejection": expected_error, "renames": mapping,
                                             "locations": locations, "verified": False}
            shutil.copytree(snapshot / "pcb", project)
            sch = project / "pcb.kicad_sch"
            if mapping:
                changed = rename_references(original, mapping, locations)
                sch.write_text(sync.format_node(changed) + "\n", encoding="utf-8")
                m.require(sync.parse(sch.read_text(encoding="utf-8")) == changed, "Reference edit did not round-trip")
                if label == "numbered":
                    inverse = {new: old for old, new in mapping.items()}
                    m.require(rename_references(changed, inverse) == original, "Control changed non-reference source content")
                    case.update(inverse_mapping=inverse, inverse_source_tree_matches=True)
            case["source_hashes_before"] = tree_hashes(project)
            m.require(set(case["source_hashes_before"]) == set(project_hashes) and all(
                digest == project_hashes[name] for name, digest in case["source_hashes_before"].items()
                if name != "pcb.kicad_sch" or not mapping), "Non-schematic input changed in a probe copy")
            references, reference_error = {}, None
            try:
                references = validate_references(sch)
            except nets.VerificationError as exc:
                reference_error = str(exc)
            case["source_reference_validation"] = {"valid": reference_error is None, "error": reference_error,
                                                    "references": references}
            m.write_json(run / "report.json", report)
            native.project = project
            xml = case_dir / "schematic.xml"
            result = native.invoke(native.cli + ["sch", "export", "netlist", "--format", "kicadxml",
                                                 "--output", xml, sch], label)
            case["command_index"] = len(native.commands) - 1
            case["source_hashes_after"] = tree_hashes(project)
            case["native_inputs_unchanged"] = case["source_hashes_before"] == case["source_hashes_after"]
            case["native_matches_baseline_diagnostic"] = (not result.get("execution_error") and result["returncode"] == 0
                                                         and result["stdout"] == WARNING and result["stderr"] == "")
            case["native_xml"] = {"path": xml.relative_to(run).as_posix()}
            try:
                case["native_xml"]["sha256"] = m.sha256(xml)
                exported = nets.read_xml(xml)
                case["native_xml"]["observed_counts_not_validation"] = {
                    "components": len(exported.findall("components/comp")), "nets": len(exported.findall("nets/net")),
                    "terminals": len(exported.findall("nets/net/node")),
                }
                case["native_xml"]["references"] = [comp.get("ref") for comp in exported.findall("components/comp")]
            except (OSError, ValueError) as exc:
                case["native_xml"]["error"] = str(exc)
            m.require(case["native_inputs_unchanged"], f"Native command changed {label} project inputs")
            m.require(not result.get("execution_error") and result["returncode"] >= 0,
                      f"Native {label} probe did not complete")
            if expected_error:
                m.require(reference_error is not None and expected_error in reference_error,
                          f"{label} did not fail the intended source-reference validation")
            else:
                m.require(reference_error is None, f"Invalid {label} source references: {reference_error}")
                require_output(result, WARNING if label == "baseline" else "")
                proof = export_proof(xml, references, board, project / "BOM.csv", baseline, case.get("inverse_mapping"))
                m.require(proof["counts"] == EXPECTED_COUNTS, f"Hybrid population/connectivity counts changed: {proof['counts']}")
                if label == "baseline":
                    numbering_map(references)
                    baseline = proof
                case.update(counts=proof["counts"], pcb_bom_equivalence=True,
                            baseline_equivalent_after_inverse_rename=label == "numbered",
                            comparison_file=f"{label}/comparison.json")
                m.write_json(case_dir / "comparison.json", proof)
            case["verified"] = True
            m.write_json(run / "report.json", report)
            print(f"{label}: exit={result['returncode']}, stdout={result['stdout']!r}, stderr={result['stderr']!r}; "
                  f"source references {'rejected as intended' if expected_error else 'valid'}", flush=True)
        completed = True
    except (OSError, ValueError, KeyError, TypeError, csv.Error) as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
    finally:
        try:
            after = {name: m.sha256(root / name) if (root / name).is_file() and not (root / name).is_symlink() else None
                     for name in before}
            report["source_hashes_after"] = after
            report["review_input_hashes_after"] = {name: after.get(name) for name in sorted(REVIEW_INPUTS)}
            report["sources_unchanged"] = bool(before) and after == before
            m.require(not before or after == before, "Authoritative source bytes changed during review; rerun")
            m.require(not before or source_hashes(root) == before, "Authoritative source inventory changed during review; rerun")
            if snapshot_before:
                report["snapshot_hashes_after"] = tree_hashes(snapshot)
                m.require(report["snapshot_hashes_after"] == snapshot_before, "Preserved source snapshot changed")
        except (OSError, ValueError) as exc:
            report["errors"].append(f"{type(exc).__name__}: {exc}")
        report["status"] = "pass" if completed and not report["errors"] else "failed"
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        report["evidence_hashes"] = {name: digest for name, digest in tree_hashes(run).items() if name != "report.json"}
        m.write_json(run / "report.json", report)
    for error in report["errors"]:
        print(f"Annotation evidence FAILED: {error}", file=sys.stderr)
    print(f"Annotation evidence {report['status'].upper()}: {run / 'report.json'}; manual review required")
    return run, report


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cli", default=os.environ.get("KICAD_CLI", ""),
                        help="Native/Snap/Flatpak invocation; shell quoting is split to argv, never evaluated")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        _, report = review(args.root, args.cli)
        return 0 if report["status"] == "pass" else 1
    except (OSError, ValueError) as exc:
        print(f"Annotation evidence FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
