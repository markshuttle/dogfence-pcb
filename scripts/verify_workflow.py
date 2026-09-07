#!/usr/bin/env python3
"""P6: preserve evidence, then run clean/all and clean/-j4 all, sequentially.

Requires exclusive ownership of build/ and tmp/manufacturing/ for the whole run.
--expect-holds asserts ledger IDs; it never changes or bypasses the ledger. Pass
the option with no IDs only for a genuinely reviewed, holds-closed source.
Evidence stays in tmp/workflow-validation/run-*/{before,serial,parallel}/.
PASS can mean correctly REFUSED publication, not successful make all or approval.
Assembly PDF rendering, processed CAM and hardware qualification remain separate.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

if __package__:
    from . import manufacturing as m
else:
    import manufacturing as m


OWNED = ("build", "pcb/Gerbers.zip", "pcb/CPL.csv", "tmp/manufacturing/runs")
HOLD_ERROR = "Open engineering release holds; verified draft exports retained privately"
DATE = rb"\d{4}-\d{2}-\d{2}"
TIME = rb"\d{2}:\d{2}:\d{2}"
TIMESTAMPS = {
    ".gbr": (
        rb"(?m)^(%TF.CreationDate,)" + DATE + b"T" + TIME + rb"[+-]\d{2}:\d{2}(\*%)$",
        rb"(?m)^(G04 Created by KiCad \(PCBNEW 9\.\d+\.\d+\) date )" + DATE + b" " + TIME + rb"(\*)$",
    ),
    ".drl": (
        rb"(?m)^(; DRILL file \{KiCad 9\.\d+\.\d+\} date )" + DATE + b"T" + TIME + rb"[+-]\d{4}()$",
        rb"(?m)^(; #@! TF.CreationDate,)" + DATE + b"T" + TIME + rb"[+-]\d{2}:\d{2}()$",
    ),
}


def inventory(path, excluded=()):
    """Content hashes, directory inventory and link targets; never follow links."""
    result, pending = {}, [path] if path.exists() or path.is_symlink() else []
    while pending:
        item = pending.pop()
        if item in excluded:
            continue
        name = item.relative_to(path).as_posix()
        if item.is_symlink():
            result[name] = {"symlink": str(item.readlink())}
        elif item.is_dir():
            result[name] = "directory"
            pending.extend(item.iterdir())
        else:
            m.require(item.is_file(), f"Non-regular evidence: {item}")
            result[name] = m.sha256(item)
    return result


def preserve(root, destination):
    destination.mkdir()
    hashes = {}
    for name in OWNED:
        source, target = root / name, destination / name
        hashes[name] = inventory(source)
        if not hashes[name]:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir() and not source.is_symlink():
            shutil.copytree(source, target, symlinks=True)
        else:
            shutil.copy2(source, target, follow_symlinks=False)
        m.require(hashes[name] == inventory(target) == inventory(source), f"Preservation mismatch: {name}")
    m.write_json(destination / "hashes.json", hashes)
    return hashes


def comparison_hash(path):
    data = path.read_bytes()
    for pattern in TIMESTAMPS.get(path.suffix, ()):
        data, count = re.subn(pattern, rb"\1<TIMESTAMP>\2", data)
        m.require(count == 1, f"Expected one recognized native timestamp header: {path.name}")
    return hashlib.sha256(data).hexdigest()


def geometry_comparison(data):
    for key in ("pcb", "project", "rules"):
        data["inputs"][key].pop("path")
    # check_geometry iterates layer sets; row order is not a physical measurement.
    data["measurements"]["via_apertures"].sort(key=lambda row: json.dumps(row, sort_keys=True))
    return data


def validate_attempt(saved, sources, review, returncode):
    status = m.read_json(saved / "build/status.json")
    relative = Path(status["attempt"])
    m.require(relative.parent == Path("tmp/manufacturing/runs") and relative.name.startswith("attempt-"),
              "Status points outside owned attempts")
    m.require({p.name for p in (saved / relative.parent).iterdir()} == {relative.name},
              "Clean build did not produce exactly one transaction")
    attempt = saved / relative
    project, exports, reports = attempt / "project", attempt / "exports", attempt / "reports"
    verification = m.read_json(reports / "verification.json")
    checks, holds = verification["checks"], review["release_holds"]
    m.require(inventory(reports) == inventory(saved / "build/reports"), "Public/private reports differ")
    m.require(verification["source_hashes"] == sources and all(
        m.sha256(project / name[4:] if name.startswith("pcb/") else attempt / name) == digest
        for name, digest in sources.items()), "Attempt source hashes differ")
    board, revision = m.validate_project(project)
    m.require(revision == verification["hardware_revision"] == review["hardware_revision"], "Revision differs")
    m.require(all(checks[name]["verified"] is True for name in
                  ("project", "drc", "erc", "geometry", "nets", "population", "archives", "export_diagnostics")),
              "Incomplete file checks")
    m.require(checks["engineering_release"] == {
        "verified": not holds, "holds": holds, "review": review.get("file_release_review")}, "Release ledger differs")
    m.require(returncode == (2 if holds else 0) and verification["errors"] == ([HOLD_ERROR] if holds else [])
              and status["status"] == verification["status"] == ("failed" if holds else "verified")
              and status["requires_verified_manifest_for_upload"] is True, "Unexpected build outcome")
    commands = json.loads((reports / "commands.json").read_text(encoding="utf-8"))
    tools = [c["command"][:-1] for c in commands if c["command"][-1:] == ["--version"]
             and c["returncode"] == 0 and c["stdout"].strip() == verification["tool_version"]]
    m.require(len(tools) == 1, "Missing/ambiguous successful native version probe")
    result = {"sources": sources, "revision": revision, "tool": tools[0], "version": verification["tool_version"]}
    result["export_diagnostics"] = checks["export_diagnostics"]
    for command in commands:
        args = command["command"]
        if args[-1:] != ["--version"]:
            violations = any(kind in args and checks[kind]["violations"] for kind in ("drc", "erc"))
            m.require(command["returncode"] == (5 if violations else 0), "Unexpected native command failure")
    for kind in ("drc", "erc"):
        labels = review["reviewed_single_global_labels"] if kind == "erc" else {}
        path = reports / f"{kind}_report.json"
        m.require(m.validate_report(path, kind, result["version"], labels) == checks[kind], f"Invalid {kind} report")
        result[kind] = m.read_json(path)
        result[kind].pop("date")
    geometry = m.read_json(reports / "geometry.json")
    m.require(geometry["ok"] is True and geometry["status"] == "pass" and not geometry["diagnostics"]
              and m.sha256(reports / "geometry.json") == checks["geometry"]["report_sha256"], "Invalid geometry report")
    for key, name in (("pcb", "pcb.kicad_pcb"), ("project", "pcb.kicad_pro"), ("rules", "pcb.kicad_dru")):
        m.require(geometry["inputs"][key]["sha256"] == m.sha256(project / name), "Geometry source differs")
    result["geometry"] = geometry_comparison(geometry)
    nets = m.parse_netlist(exports / "schematic.xml")
    m.require(not m.differences(nets, board.nets), "Schematic/PCB terminal membership differs")
    m.require(m.compare_ipc(exports / "pcb.d356", board) == checks["nets"]["ipc"], "IPC differs")
    result["nets"] = {name: sorted(nodes) for name, nodes in nets.items()}
    release = attempt / "release" if holds else saved / "build"
    result["bom"] = m.validate_bom(release / "BOM.csv", exports / "schematic.xml", board)
    positions = m.check_placement(m.read_csv(exports / "native-pos.csv", m.POSITION_FIELDS), board, native=True)
    for path in (exports / "CPL.csv", release / "CPL.csv", saved / "pcb/CPL.csv"):
        m.require(m.check_placement(m.read_csv(path, m.CPL_FIELDS), board) == positions
                  and m.sha256(path) == m.sha256(exports / "CPL.csv"), "Generated signed-Y CPL differs")
    m.require(set(positions) == set(result["bom"]) == set(checks["population"]["references"]), "Population differs")
    m.require(m.validate_gerbers(exports / "gerbers", board) == checks["gerbers"], "Gerber validation differs")
    m.require({p.name for p in (exports / "drills").iterdir()} == m.DRILLS, "Drill inventory differs")
    for name in m.DRILLS:
        m.require(m.validate_drill(exports / "drills" / name, board, name == "pcb-PTH.drl")
                  == checks["drills"][name], "Drill validation differs")
    files = {"gerbers/" + name: exports / ("drills" if name in m.DRILLS else "gerbers") / name for name in m.FAB_FILES}
    m.require({p.name for p in (release / "gerbers").iterdir()} == m.FAB_FILES, "Release layer inventory differs")
    m.require(all(m.sha256(release / name) == m.sha256(path) for name, path in files.items()), "Release geometry differs")
    m.validate_zip(release / "Gerbers.zip", {Path(name).name: path for name, path in files.items()})
    m.validate_zip(release / "FlyTest.zip", {"Gerbers.zip": release / "Gerbers.zip",
                   "pcb.d356": exports / "pcb.d356", "README.txt": exports / "README.txt"})
    for name in ("pcb.d356", "Assembly.pdf"):
        m.require(m.sha256(release / name) == m.sha256(exports / name), f"Release copy differs: {name}")
    m.require(m.sha256(release / "BOM.csv") == m.sha256(project / "BOM.csv"), "Release BOM differs")
    files.update({name: release / name for name in ("BOM.csv", "CPL.csv", "pcb.d356", "Assembly.txt", "ViaTreatment.csv",
                                                   "ASSEMBLY.md", "ELECTRICAL.md", "verification.json")})
    files.update({name: exports / name for name in ("native-pos.csv", "README.txt")})
    result["artifact_comparison_hashes"] = {name: comparison_hash(path) for name, path in files.items()}
    if holds:
        m.require({p.name for p in (saved / "build").iterdir()} == {
            "status.json", "reports", "drc_report.json", "drc_report.txt", "erc_report.json", "erc_report.txt"}
            and not inventory(saved / "pcb/Gerbers.zip"), "Held build leaked public artifacts")
    else:
        manifest = m.read_json(release / "manifest.json")
        artifacts = {name: digest for name, digest in inventory(release).items()
                     if digest != "directory" and name != "manifest.json"}
        m.require(review.get("file_release_review") and manifest["status"] == "verified"
                  and manifest["source_hashes"] == sources and manifest["artifact_hashes"] == artifacts
                  and manifest["hardware_revision"] == revision and manifest["verification"] == checks
                  and manifest["tool"]["command"] == tools[0] and manifest["tool"]["version"] == result["version"]
                  and m.sha256(saved / "pcb/Gerbers.zip") == m.sha256(release / "Gerbers.zip"), "Invalid publication")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--expect-holds", nargs="*", required=True, help="Exact expected ledger IDs (no bypass)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    parent, runs = root / "tmp/workflow-validation", root / "tmp/manufacturing/runs"
    for name in ("tmp", "tmp/workflow-validation", "tmp/manufacturing", "pcb", *OWNED):
        m.require(not (root / name).is_symlink(), f"Refusing linked workflow path: {name}")
    parent.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="run-", dir=parent))
    print(f"Workflow evidence: {run}", flush=True)
    sentinel = run / "clean-boundary-sentinel.txt"
    sentinel.write_text(f"Preserve {run.name} across both clean commands.\n", encoding="ascii")
    shutil.copy2(Path(__file__), run / "verify_workflow.py")
    report = {"status": "failed", "commands": [], "snapshots": {}, "python_version": sys.version,
              "runner_sha256": m.sha256(Path(__file__)), "sentinel_sha256": m.sha256(sentinel),
              "scope": {"file_validation": m.SCOPE,
                        "comparison": "Validated Gerbers/drills: strict bytes except the timestamp regexes below. BOM/CPL/IPC/native positions/assembly text/controlled notes: exact bytes. XML: complete terminals and BOM identities. DRC/ERC JSON: only date removed. Geometry JSON: only input path fields removed and via_apertures rows sorted by complete content (layer-set iteration order); every field and duplicate retained. All hashes and measurements compared.",
                        "timestamp_patterns": {suffix: [p.decode("ascii") for p in patterns] for suffix, patterns in TIMESTAMPS.items()},
                        "not_geometry_proof": "Assembly.pdf archived and hashed, not render-compared. ZIPs validated against exact member payloads; native timestamp changes propagate to ZIP hashes. XML generation date/staging paths, command logs, status paths and report timestamps are retained but not byte-compared. No CAM, order or hardware approval.",
                        "clean_boundary": "All pre-existing tmp entries outside owned runs and this validation run: file bytes, directories and symlink targets, not mtimes."}}
    try:
        m.require(not any(os.environ.get(key) for key in ("MAKEFLAGS", "MFLAGS", "MAKEFILES")), "Inherited Make overrides are unsafe")
        sources = m.source_inventory(root)
        review = m.read_json(root / "pcb/verification.json")
        ids = [hold["id"] for hold in review["release_holds"]]
        m.require(sorted(ids) == sorted(args.expect_holds) and len(ids) == len(set(ids)), "Unexpected release hold IDs")
        report.update(source_hashes=sources, expected_holds=review["release_holds"])
        report["unrelated_tmp_before"] = inventory(root / "tmp", (runs, run))
        report["snapshots"]["before"] = preserve(root, run / "before")
        results = report["comparison"] = {}
        for label, build_command in (("serial", ["make", "all"]), ("parallel", ["make", "-j4", "all"])):
            for command in (["make", "clean"], build_command):
                clean = command[-1] == "clean"
                name = label + ("-clean" if clean else "-build")
                cpl_before = inventory(root / "pcb/CPL.csv")
                record = {"command": command, "cwd": str(root), "log": name + ".log",
                          "started_utc": datetime.now(timezone.utc).isoformat(), "source_hashes_before": m.source_inventory(root)}
                report["commands"].append(record)
                m.write_json(run / "report.json", report)
                m.require(record["source_hashes_before"] == sources, "Sources changed before command")
                with (run / record["log"]).open("w", encoding="utf-8") as log:
                    process = subprocess.run(command, cwd=root, stdout=log, stderr=subprocess.STDOUT)
                record.update(returncode=process.returncode, finished_utc=datetime.now(timezone.utc).isoformat())
                print(f"{' '.join(command)}: exit {process.returncode}; {run / record['log']}", flush=True)
                if not clean:
                    report["snapshots"][label] = preserve(root, run / label)
                record["source_hashes_after"] = m.source_inventory(root)
                m.require(record["source_hashes_before"] == sources == record["source_hashes_after"], "Sources changed")
                m.require(m.sha256(sentinel) == report["sentinel_sha256"] and
                          inventory(root / "tmp", (runs, run)) == report["unrelated_tmp_before"], "Unrelated evidence changed")
                for snapshot, inventories in report["snapshots"].items():
                    m.require(all(inventory(run / snapshot / path) == hashes for path, hashes in inventories.items()),
                              f"Saved evidence changed: {snapshot}")
                if clean:
                    m.require(process.returncode == 0 and not any(inventory(root / p) for p in OWNED if p != "pcb/CPL.csv")
                              and inventory(root / "pcb/CPL.csv") == cpl_before, "Clean boundary violated")
                else:
                    results[label] = validate_attempt(run / label, sources, review, process.returncode)
                    record.update(outcome="expected publication refusal" if ids else "verified file publication",
                                  status=m.read_json(root / "build/status.json"), artifact_hashes=report["snapshots"][label])
                record["verified"] = True
                m.write_json(run / "report.json", report)
        changed = [key for key in results["serial"] if results["serial"][key] != results["parallel"].get(key)]
        m.require(results["serial"] == results["parallel"], f"Serial/parallel comparison differs: {changed}")
        report.update(status="pass", comparison_verified=True, unrelated_tmp_unchanged=True,
                      publication="refused as required" if ids else "file-verified, not order approval")
    except Exception as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        m.write_json(run / "report.json", report)
    print(f"Workflow {report['status'].upper()}: {report.get('error', report.get('publication'))}; {run / 'report.json'}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
