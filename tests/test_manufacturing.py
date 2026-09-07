from concurrent.futures import ThreadPoolExecutor
import contextlib
import csv
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import manufacturing as m
from scripts import compare_nets as nets
from test_compare_nets import BOARD, ipc_text, xml_netlist


REPO = Path(__file__).resolve().parents[1]


def make_project(root):
    pcb = root / "pcb"
    pcb.mkdir()
    (root / "scripts").mkdir()
    (pcb / "pcb.kicad_pcb").write_text(BOARD, encoding="utf-8")
    (pcb / "pcb.kicad_sch").write_text(
        '(kicad_sch (version 20250114) (generator "eeschema") '
        '(uuid "00000000-0000-4000-8000-000000000001") (paper "A4") '
        '(title_block (title "Fixture") (rev "fixture-1")) (lib_symbols))\n', encoding="utf-8")
    settings = {"meta": {"filename": "pcb.kicad_pro", "version": 3},
                "board": {"design_settings": {"rules": m.MIN_RULES.copy(), "drc_exclusions": [],
                                             "rule_severities": {"clearance": "error", "text_height": "warning"}}},
                "erc": {"erc_exclusions": [], "rule_severities": {"pin_not_connected": "error"}}}
    m.write_json(pcb / "pcb.kicad_pro", settings)
    m.write_json(pcb / "verification.json", {
        "schema_version": 1, "hardware_revision": "fixture-1", "reviewed_single_global_labels": {},
        "release_holds": [], "file_release_review": "Synthetic pipeline fixture only; not hardware approval"})
    for name in ("ASSEMBLY.md", "ELECTRICAL.md"):
        (pcb / name).write_text("Synthetic test fixture, not engineering evidence.\n", encoding="utf-8")
    shutil.copy2(REPO / "pcb" / "pcb.kicad_dru", pcb)
    (pcb / "fp-lib-table").write_text(
        '(fp_lib_table (version 7) (lib (name "Local") (type "KiCad") '
        '(uri "${KIPRJMOD}/Local.pretty") (options "") (descr "Fixture")))\n', encoding="utf-8")
    (pcb / "sym-lib-table").write_text(
        '(sym_lib_table (version 7) (lib (name "Local") (type "KiCad") '
        '(uri "${KIPRJMOD}/Local.kicad_sym") (options "") (descr "Fixture")))\n', encoding="utf-8")
    (pcb / "Local.pretty").mkdir()
    for name in ("THT", "SMT", "Hole"):
        (pcb / "Local.pretty" / f"{name}.kicad_mod").write_text(
            f'(footprint "{name}" (version 20241229) (generator "pcbnew") (layer "F.Cu"))\n', encoding="utf-8")
    (pcb / "Local.kicad_sym").write_text(
        '(kicad_symbol_lib (version 20241209) (generator "kicad_symbol_editor") (symbol "THT"))\n', encoding="utf-8")
    for name in m.HELPERS:
        shutil.copy2(REPO / "scripts" / name, root / "scripts" / name)
    shutil.copy2(REPO / "Makefile", root / "Makefile")
    with (pcb / "BOM.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["Comment", "Designator", "Footprint", "LCSC Part #", "MPN", "Manufacturer"])
        writer.writerow(["1k", "R1", "Local:THT", "C123", "R1K", "Example"])
        for ref in ("J_LED_A", "J_LED_C"):
            writer.writerow(["SMT", ref, "Local:SMT", "C456", "SMT1", "Example"])
    (pcb / "CPL.csv").write_text("legacy source mirror; never a placement input\n", encoding="utf-8")


def native_positions(board):
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(m.POSITION_FIELDS)
    for ref, fp in sorted(board.footprints.items()):
        if fp.populated:
            writer.writerow([ref, fp.properties["Value"], fp.name.split(":")[1], fp.x, -fp.y,
                             -90 if fp.rotation == 270 else fp.rotation, fp.side])
    return stream.getvalue()


def fake_gerbers(directory, board):
    codes = {node[1]: node[2] for node in nets.children(board.tree, "net")}
    for layer, (filename, function) in m.LAYERS.items():
        lines = [f"%TF.FileFunction,{function}*%", "%TF.SameCoordinates,Original*%", "%MOMM*%", "%FSLAX46Y46*%",
                 f"%TF.FilePolarity,{'Negative' if layer.endswith('Mask') else 'Positive'}*%", "%LPD*%", "G01*"]
        aperture = 10
        roundrect_defined = False
        for pad in board.pads:
            if layer.endswith("Cu"):
                if pad.kind == "np_thru_hole" or not (layer in pad.layers or "*.Cu" in pad.layers):
                    continue
            elif layer.endswith(("Mask", "Paste")):
                if pad.kind == "via" or not (layer in pad.layers or "*." + layer.split(".")[1] in pad.layers):
                    continue
            else:
                continue
            w, h = (pad.width, pad.height) if pad.rotation % 180 == 0 else (pad.height, pad.width)
            shape = {"circle": "C", "rect": "R", "roundrect": "RoundRect"}[pad.shape]
            if shape == "RoundRect":
                if not roundrect_defined:
                    lines += ["%AMRoundRect*", "0 Rounded rectangle*", *m.ROUNDRECT_PRIMITIVES[:-1],
                              m.ROUNDRECT_PRIMITIVES[-1] + "%"]
                    roundrect_defined = True
                radius = min(w, h) * pad.roundrect_ratio
                hx, hy = max(w / 2 - radius, .00001), max(h / 2 - radius, .00001)
                params = "X".join(f"{v:.6f}" for v in (radius, -hx, -hy, hx, -hy, hx, hy, -hx, hy, 0))
            else:
                params = f"{w:.6f}" if shape == "C" else f"{w:.6f}X{h:.6f}"
            lines += [f"%ADD{aperture}{shape},{params}*%", f"D{aperture}*"]
            if layer.endswith("Cu"):
                if pad.kind != "via":
                    lines.append(f"%TO.P,{pad.ref},{pad.pin}*%")
                lines.append(f"%TO.N,{pad.net}*%")
            else:
                lines.append(f"%TO.C,{pad.ref}*%")
            lines += [f"X{round(pad.x * 1e6)}Y{round(-pad.y * 1e6)}D03*", "%TD*%"]
            aperture += 1
        for segment in nets.children(board.tree, "segment"):
            if nets.value(segment, "layer") != layer:
                continue
            lines += [f"%ADD{aperture}C,{nets.value(segment, 'width')}*%", f"D{aperture}*",
                      f"%TO.N,{codes[nets.value(segment, 'net')]}*%"]
            for key, code in (("start", "02"), ("end", "01")):
                x, y = nets.numbers(nets.child(segment, key)[1:])
                lines.append(f"X{round(x * 1e6)}Y{round(-y * 1e6)}D{code}*")
            lines.append("%TD*%")
            aperture += 1
        if layer == "Edge.Cuts":
            lines += ["%ADD10C,0.15*%", "D10*", "X0Y0D02*", "X60000000Y0D01*",
                      "X60000000Y-60000000D01*", "X0Y-60000000D01*", "X0Y0D01*"]
        (directory / filename).write_text("\n".join(lines + ["M02*", ""]), encoding="utf-8")


def fake_drills(directory, board):
    for plated, filename in ((True, "pcb-PTH.drl"), (False, "pcb-NPTH.drl")):
        function = "Plated,1,2,PTH" if plated else "NonPlated,1,2,NPTH"
        lines = ["M48", "; FORMAT={-:-/ absolute / metric / decimal}", f"; #@! TF.FileFunction,{function}", "FMAT,2", "METRIC"]
        pads = [pad for pad in board.pads if pad.drill and (pad.kind != "np_thru_hole") == plated]
        for i, pad in enumerate(pads, 1):
            role = "ViaDrill" if pad.kind == "via" else "ComponentDrill"
            lines += [f"; #@! TA.AperFunction,{role}", f"T{i}C{pad.drill:.3f}"]
        lines += ["%", "G90", "G05"]
        for i, pad in enumerate(pads, 1):
            lines += [f"T{i}", f"X{pad.x:.3f}Y{-pad.y:.3f}"]
        (directory / filename).write_text("\n".join(lines + ["M30", ""]), encoding="ascii")


class FakeKiCad:
    """Native-format producer for isolated pipeline failure/transaction tests."""
    def __init__(self, defect=None):
        self.defect = defect
        self.calls = []

    def __call__(self, command, **kwargs):
        self.calls.append(command)
        if "--version" in command:
            return subprocess.CompletedProcess(command, 0, "9.0.7\n", "")
        if command[0] == "git":
            return subprocess.CompletedProcess(command, 0, "fixture-revision\n" if command[1] == "rev-parse" else "", "")
        output = Path(command[command.index("--output") + 1])
        rc = 0
        if any(Path(arg).name == "check_geometry.py" for arg in command):
            inputs = {key: {"sha256": m.sha256(Path(command[command.index("--" + key) + 1]))}
                      for key in ("pcb", "project", "rules")}
            data = {"schema_version": 1, "check": "physical_geometry", "ok": True, "status": "pass",
                    "diagnostics": [], "inputs": inputs}
            if self.defect == "geometry":
                data.update(ok=False, status="fail", diagnostics=[{"severity": "error", "code": "EARTH_CLEARANCE"}])
                rc = 1
            elif self.defect == "geometry-malformed":
                data = {"pretend_success": True}
            m.write_json(output, data)
        elif "drc" in command or "erc" in command:
            kind = "drc" if "drc" in command else "erc"
            violation = [{"severity": "warning", "type": "fixture_warning", "description": "Unreviewed warning", "items": []}]
            warnings = violation if self.defect == "warning" and kind == "drc" else []
            rc = 5 if warnings else 0
            if command[command.index("--format") + 1] == "report":
                output.write_text(f"** {kind.upper()} report **\n{warnings}\n", encoding="utf-8")
            else:
                data = {"$schema": f"https://schemas.kicad.org/{kind}.v1.json", "source": command[-1],
                        "kicad_version": "9.0.7", "date": "2026-09-06T00:00:00Z", "coordinate_units": "mm"}
                if kind == "drc":
                    data.update(violations=warnings, unconnected_items=[], schematic_parity=[])
                else:
                    data["sheets"] = [{"path": "/", "uuid_path": "/fixture", "violations": []}]
                if self.defect == "report-malformed":
                    data = {"violations": []}
                m.write_json(output, data)
        else:
            board = nets.read_board(Path(kwargs["cwd"]) / "pcb.kicad_pcb")
            if "netlist" in command:
                output.write_text(xml_netlist(), encoding="utf-8")
            elif "ipcd356" in command:
                text = ipc_text(board)
                if self.defect == "ipc-net":
                    text = text.replace("POWER         ", "WRONG         ", 1)
                output.write_text(text, encoding="ascii")
            elif "pos" in command:
                if self.defect != "missing-cpl":
                    text = native_positions(board)
                    if self.defect == "flipped-y":
                        text = text.replace(",-", ",")
                    if self.defect == "missing-cpl-ref":
                        text = "\n".join(line for line in text.splitlines() if not line.startswith("R1,")) + "\n"
                    output.write_text(text, encoding="utf-8")
            elif "gerbers" in command:
                fake_gerbers(output, board)
                if self.defect == "missing-layer":
                    (output / "pcb-F_Paste.gbr").unlink()
            elif "drill" in command:
                fake_drills(output, board)
                if self.defect == "wrong-drill":
                    path = output / "pcb-PTH.drl"
                    path.write_text(path.read_text().replace("C1.000", "C0.900", 1))
            elif "pdf" in command:
                output.write_bytes(b"%PDF-1.7\nfixture-only\n%%EOF\n")
            else:
                raise AssertionError(command)
            if self.defect == "export-failure" and "drill" in command:
                rc = 1
        stdout, stderr = "fixture command\n", ""
        if "netlist" in command:
            if self.defect in ("annotation-warning", "annotation-plus-warning"):
                stdout = "Warning: schematic has annotation errors, please use the schematic editor to fix them\n"
                if self.defect == "annotation-plus-warning":
                    stdout += "Warning: another problem\n"
            elif self.defect == "export-warning":
                stdout = "Warning: unknown export problem\n"
            elif self.defect == "export-stderr":
                stderr = "Unexpected exporter diagnostic\n"
        if "ipcd356" in command and self.defect and self.defect.startswith("export-debug"):
            stderr = "00:35:19: Debug: Adding duplicate image handler for 'PNG file'\n"
            if self.defect == "export-debug-warning":
                stderr += "Warning: another problem\n"
            elif self.defect == "export-debug-unknown":
                stderr = stderr.replace("PNG", "UNKNOWN")
        return subprocess.CompletedProcess(command, rc, stdout, stderr)


class ManufacturingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        make_project(self.root)

    def execute(self, mode="build", defect=None):
        fake = FakeKiCad(defect)
        pipeline = m.Manufacturing(self.root, "fake-kicad")
        with patch.object(m.subprocess, "run", fake), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = pipeline.execute(mode)
        return rc, pipeline, fake

    def assert_failed(self, defect=None):
        previous_cpl = (self.root / "pcb" / "CPL.csv").read_bytes()
        rc, pipeline, fake = self.execute(defect=defect)
        self.assertNotEqual(rc, 0)
        self.assertFalse((self.root / "build" / "manifest.json").exists())
        self.assertFalse((self.root / "build" / "Gerbers.zip").exists())
        self.assertEqual((self.root / "pcb" / "CPL.csv").read_bytes(), previous_cpl)
        return pipeline, fake

    def test_success_publishes_complete_hashed_package_and_native_mirrors(self):
        rc, pipeline, fake = self.execute()
        self.assertEqual(rc, 0, pipeline.errors)
        build = self.root / "build"
        manifest = json.loads((build / "manifest.json").read_text())
        self.assertEqual(manifest["status"], "verified")
        self.assertEqual(manifest["hardware_revision"], "fixture-1")
        self.assertEqual(manifest["tool"]["version"], "9.0.7")
        self.assertEqual(manifest["verification"]["population"]["references"], ["J_LED_A", "J_LED_C", "R1"])
        for name, digest in manifest["artifact_hashes"].items():
            self.assertEqual(m.sha256(build / name), digest, name)
        self.assertEqual({p.relative_to(build).as_posix() for p in build.rglob("*") if p.is_file()},
                         set(manifest["artifact_hashes"]) | {"manifest.json"})
        for name in ("CPL.csv", "Gerbers.zip"):
            self.assertEqual((build / name).read_bytes(), (self.root / "pcb" / name).read_bytes())
        rows = m.read_csv(build / "CPL.csv", m.CPL_FIELDS)
        c = next(row for row in rows if row["Designator"] == "J_LED_C")
        self.assertEqual(float(c["Mid Y"]), -40)
        self.assertEqual(float(c["Rotation"]), 270)
        self.assertNotIn("H1", {row["Designator"] for row in rows})
        self.assertNotIn("R_DNP", {row["Designator"] for row in rows})
        self.assertIn("pcb/pcb.kicad_dru", manifest["source_hashes"])
        self.assertIn("pcb/Local.pretty/THT.kicad_mod", manifest["source_hashes"])
        self.assertNotIn("pcb/CPL.csv", manifest["source_hashes"])
        with zipfile.ZipFile(build / "Gerbers.zip") as archive:
            self.assertEqual(set(archive.namelist()), m.FAB_FILES)
        with zipfile.ZipFile(build / "FlyTest.zip") as archive:
            self.assertEqual(set(archive.namelist()), {"Gerbers.zip", "pcb.d356", "README.txt"})
        self.assertNotEqual(pipeline.run / "exports" / "drills", pipeline.run / "exports" / "gerbers")

    def test_check_runs_all_gates_and_refreshes_reference_without_publishing(self):
        rc, pipeline, fake = self.execute("check")
        self.assertEqual(rc, 0, pipeline.errors)
        self.assertFalse((self.root / "build" / "CPL.csv").exists())
        self.assertFalse((self.root / "build" / "manifest.json").exists())
        self.assertTrue((self.root / "pcb" / "CPL.csv").read_text().startswith("Designator,"))
        for kind in ("drc", "erc"):
            commands = [command for command in fake.calls if kind in command]
            self.assertEqual(len(commands), 2)
            self.assertTrue(all("--severity-all" in command for command in commands))
            if kind == "drc":
                self.assertTrue(all("--schematic-parity" in command for command in commands))
        self.assertTrue(any("ipcd356" in c for c in fake.calls))
        self.assertTrue(any(Path(arg).name == "check_geometry.py" for c in fake.calls for arg in c))

    def test_missing_rules_and_project_fail_before_exports(self):
        for filename in ("pcb.kicad_dru", "pcb.kicad_pro", "fp-lib-table", "sym-lib-table", "verification.json"):
            path = self.root / "pcb" / filename
            data = path.read_bytes()
            path.unlink()
            pipeline, fake = self.assert_failed()
            self.assertIn(filename, " ".join(pipeline.errors))
            self.assertEqual(fake.calls, [])
            path.write_bytes(data)

    def test_missing_helper_is_a_hard_gate(self):
        (self.root / "scripts" / "check_geometry.py").unlink()
        pipeline, fake = self.assert_failed()
        self.assertIn("check_geometry.py", " ".join(pipeline.errors))

    def test_weakened_project_minimum_and_ignored_warning_fail(self):
        path = self.root / "pcb" / "pcb.kicad_pro"
        original = json.loads(path.read_text())
        for edit in ("minimum", "ignore", "exclusion"):
            data = json.loads(json.dumps(original))
            design = data["board"]["design_settings"]
            if edit == "minimum":
                design["rules"]["min_track_width"] = 0
            elif edit == "ignore":
                design["rule_severities"]["text_height"] = "ignore"
            else:
                design["drc_exclusions"] = ["suppress-this"]
            m.write_json(path, data)
            with self.subTest(edit=edit):
                self.assert_failed()

    def test_custom_ignore_rule_cannot_suppress_a_gate(self):
        rules = self.root / "pcb" / "pcb.kicad_dru"
        rules.write_text(rules.read_text() + '\n(rule "hidden" (severity ignore) (constraint text_height (min 0mm)))\n')
        pipeline, fake = self.assert_failed()
        self.assertIn("severities are forbidden", " ".join(pipeline.errors))

    def test_duplicate_json_keys_and_nonfinite_values_rejected(self):
        path = self.root / "report.json"
        for text in ('{"violations":[1],"violations":[]}', '{"value":NaN}', '{"value":Infinity}', '[]'):
            path.write_text(text)
            with self.subTest(text=text), self.assertRaises(nets.VerificationError):
                m.read_json(path)

    def test_library_must_be_local_and_resolvable(self):
        table = self.root / "pcb" / "fp-lib-table"
        table.write_text(table.read_text().replace("${KIPRJMOD}/Local.pretty", "/usr/share/Local.pretty"))
        self.assert_failed()

    def test_failure_keeps_all_drc_erc_reports_and_command_logs(self):
        pipeline, fake = self.assert_failed("warning")
        for kind in ("drc", "erc"):
            for ext in ("txt", "json"):
                path = self.root / "build" / f"{kind}_report.{ext}"
                self.assertTrue(path.is_file())
                self.assertEqual(path.read_bytes(), (pipeline.reports / path.name).read_bytes())
        data = json.loads((pipeline.reports / "drc_report.json").read_text())
        self.assertEqual(data["violations"][0]["severity"], "warning")
        self.assertTrue((pipeline.reports / "commands.json").is_file())
        self.assertEqual(len([c for c in fake.calls if "erc" in c]), 2)

    def test_malformed_reports_cannot_pass_as_zero_violations(self):
        self.assert_failed("report-malformed")

    def test_engineering_holds_allow_checks_but_block_publication(self):
        path = self.root / "pcb" / "verification.json"
        review = m.read_json(path)
        review.update(release_holds=[{"id": "C4", "reason": "Protection not selected"}], file_release_review=None)
        m.write_json(path, review)
        for mode, expected in (("check", 0), ("build", 1)):
            rc, pipeline, fake = self.execute(mode)
            self.assertEqual(rc, expected, pipeline.errors)
            self.assertTrue((pipeline.run / "exports" / "CPL.csv").exists())
            self.assertFalse((self.root / "build" / "manifest.json").exists())
            self.assertFalse((self.root / "build" / "Gerbers.zip").exists())
            self.assertFalse((self.root / "pcb" / "Gerbers.zip").exists())
        review["release_holds"] = []
        m.write_json(path, review)
        rc, pipeline, fake = self.execute()
        self.assertNotEqual(rc, 0)
        self.assertIn("review is required", " ".join(pipeline.errors))

    def test_only_exact_reviewed_single_sheet_label_warnings_are_accepted(self):
        path = self.root / "erc.json"
        violation = {"severity": "warning", "type": "single_global_label",
                     "items": [{"uuid": "label-id", "description": "Global Label 'POWER'"}]}
        data = {"$schema": "https://schemas.kicad.org/erc.v1.json", "source": "pcb.kicad_sch",
                "date": "2026-09-06", "kicad_version": "9.0.7",
                "sheets": [{"path": "/", "uuid_path": "/fixture", "violations": [violation]}]}
        m.write_json(path, data)
        labels = {"label-id": "POWER"}
        self.assertEqual(m.validate_report(path, "erc", "9.0.7", labels)["reviewed_warnings"], 1)
        for mutate in (lambda: violation.update(severity="error"),
                       lambda: violation.update(type="pin_not_connected"),
                       lambda: violation["items"][0].update(description="Global Label 'WRONG'")):
            original = json.loads(json.dumps(violation))
            mutate()
            m.write_json(path, data)
            with self.assertRaises(nets.VerificationError):
                m.validate_report(path, "erc", "9.0.7", labels)
            violation.clear()
            violation.update(original)
        data["sheets"].append({"path": "/second", "uuid_path": "/second", "violations": []})
        m.write_json(path, data)
        with self.assertRaises(nets.VerificationError):
            m.validate_report(path, "erc", "9.0.7", labels)
        data["sheets"].pop()
        data["sheets"][0]["violations"] = []
        m.write_json(path, data)
        with self.assertRaisesRegex(nets.VerificationError, "Stale"):
            m.validate_report(path, "erc", "9.0.7", labels)

    def test_unreviewed_export_diagnostics_block_even_with_exit_zero(self):
        for defect in ("annotation-warning", "export-warning", "export-stderr"):
            with self.subTest(defect=defect):
                pipeline, fake = self.assert_failed(defect)
                self.assertIn("Unreviewed netlist export diagnostic", " ".join(pipeline.errors))

    def test_only_known_pcb_image_handler_debug_is_informational(self):
        rc, pipeline, fake = self.execute("check", "export-debug")
        self.assertEqual(rc, 0, pipeline.errors)
        self.assertEqual(pipeline.verification["export_diagnostics"]["informational_stderr"], {"ipc": 1})
        self.assertIn("Debug:", (pipeline.reports / "ipc.log").read_text())
        for defect in ("export-debug-warning", "export-debug-unknown"):
            with self.subTest(defect=defect):
                pipeline, fake = self.assert_failed(defect)
                self.assertIn("Unreviewed ipc export diagnostic", " ".join(pipeline.errors))

    def test_annotation_review_is_exact_command_version_and_input_hash_bound(self):
        path = self.root / "pcb" / "verification.json"
        review = m.read_json(path)
        hashes = m.source_inventory(self.root)
        review["reviewed_netlist_annotation"] = {
            "tool_version": "9.0.7", "reason": "Synthetic fixture diagnostic review only",
            "stdout": "Warning: schematic has annotation errors, please use the schematic editor to fix them\n",
            "source_hashes": {name: digest for name, digest in hashes.items() if name.startswith("pcb/")
                              and (Path(name).suffix in (".kicad_sch", ".kicad_pro", ".kicad_sym")
                                   or Path(name).name in ("fp-lib-table", "sym-lib-table"))}}
        m.write_json(path, review)
        rc, pipeline, fake = self.execute("check", "annotation-warning")
        self.assertEqual(rc, 0, pipeline.errors)
        self.assertTrue(pipeline.verification["export_diagnostics"]["diagnostics"][0]["reviewed"])
        for defect in ("annotation-plus-warning", "export-stderr", None):
            with self.subTest(defect=defect):
                rc, pipeline, fake = self.execute("check", defect)
                self.assertNotEqual(rc, 0)
        for source in review["reviewed_netlist_annotation"]["source_hashes"]:
            original = (self.root / source).read_bytes()
            (self.root / source).write_bytes(original + b"\n")
            rc, pipeline, fake = self.execute("check", "annotation-warning")
            self.assertNotEqual(rc, 0, source)
            (self.root / source).write_bytes(original)
        for change in ("version", "missing-hash"):
            changed = json.loads(json.dumps(review))
            if change == "version":
                changed["reviewed_netlist_annotation"]["tool_version"] = "9.0.8"
            else:
                changed["reviewed_netlist_annotation"]["source_hashes"].pop("pcb/pcb.kicad_sch")
            m.write_json(path, changed)
            rc, pipeline, fake = self.execute("check", "annotation-warning")
            self.assertNotEqual(rc, 0, change)

    def test_geometry_failure_or_malformed_success_blocks(self):
        for defect in ("geometry", "geometry-malformed"):
            with self.subTest(defect=defect):
                self.assert_failed(defect)

    def test_wrong_ipc_net_blocks_publication(self):
        self.assert_failed("ipc-net")

    def test_missing_bom_file_or_designator_blocks(self):
        path = self.root / "pcb" / "BOM.csv"
        data = path.read_text()
        path.unlink()
        self.assert_failed()
        path.write_text("\n".join(line for line in data.splitlines() if ",R1," not in line) + "\n")
        self.assert_failed()

    def test_bom_source_identity_mismatch_blocks(self):
        path = self.root / "pcb" / "BOM.csv"
        path.write_text(path.read_text().replace("R1K", "WRONG-MPN"))
        self.assert_failed()

    def test_existing_lcsc_source_field_alias_is_explicit_and_conflicts_fail(self):
        board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
        xml = self.root / "schematic.xml"
        xml.write_text(xml_netlist().replace('name="LCSC Part #"', 'name="LCSC"'))
        for fp in board.footprints.values():
            if fp.populated:
                fp.properties["LCSC"] = fp.properties.pop("LCSC Part #")
        bom = m.validate_bom(self.root / "pcb" / "BOM.csv", xml, board)
        self.assertEqual(len(bom), 3)
        board.footprints["R1"].properties["LCSC Part #"] = "C999"
        with self.assertRaisesRegex(nets.VerificationError, "LCSC Part #"):
            m.validate_bom(self.root / "pcb" / "BOM.csv", xml, board)

    def test_missing_exported_cpl_file_or_designator_blocks(self):
        for defect in ("missing-cpl", "missing-cpl-ref"):
            with self.subTest(defect=defect):
                self.assert_failed(defect)

    def test_missing_source_cpl_is_regenerated_not_a_second_input(self):
        (self.root / "pcb" / "CPL.csv").unlink()
        rc, pipeline, fake = self.execute()
        self.assertEqual(rc, 0, pipeline.errors)
        self.assertTrue((self.root / "pcb" / "CPL.csv").read_text().startswith("Designator,"))

    def test_y_flipped_cpl_blocks(self):
        self.assert_failed("flipped-y")

    def test_missing_paste_layer_blocks(self):
        self.assert_failed("missing-layer")

    def test_wrong_drill_and_nonzero_export_status_block(self):
        for defect in ("wrong-drill", "export-failure"):
            with self.subTest(defect=defect):
                self.assert_failed(defect)

    def test_stale_outputs_cannot_repair_a_failed_export(self):
        (self.root / "build").mkdir()
        (self.root / "build" / "Gerbers.zip").write_bytes(b"old-release")
        m.write_json(self.root / "build" / "manifest.json", {"status": "verified"})
        (self.root / "pcb" / "Gerbers.zip").write_bytes(b"old-mirror")
        pipeline, fake = self.assert_failed("missing-layer")
        self.assertEqual((pipeline.run / "previous-build" / "Gerbers.zip").read_bytes(), b"old-release")
        self.assertFalse((self.root / "pcb" / "Gerbers.zip").exists())

    def test_source_change_during_build_invalidates_snapshot(self):
        original = FakeKiCad()

        def change_source(command, **kwargs):
            result = original(command, **kwargs)
            if "pdf" in command:
                path = self.root / "pcb" / "BOM.csv"
                path.write_text(path.read_text() + "\n")
            return result

        pipeline = m.Manufacturing(self.root, "fake-kicad")
        with patch.object(m.subprocess, "run", change_source), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(pipeline.execute("build"), 0)
        self.assertIn("Sources changed", " ".join(pipeline.errors))
        self.assertFalse((self.root / "build" / "manifest.json").exists())

    def test_staged_source_change_invalidates_snapshot(self):
        original = FakeKiCad()

        def change_staged(command, **kwargs):
            result = original(command, **kwargs)
            if "pdf" in command:
                path = Path(kwargs["cwd"]) / "pcb.kicad_pro"
                path.write_text(path.read_text() + "\n")
            return result

        pipeline = m.Manufacturing(self.root, "fake-kicad")
        with patch.object(m.subprocess, "run", change_staged), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(pipeline.execute("build"), 0)
        self.assertIn("Staged source changed", " ".join(pipeline.errors))
        self.assertFalse((self.root / "build" / "manifest.json").exists())

    def test_clean_never_removes_other_tmp_evidence_or_generated_cpl(self):
        (self.root / "tmp" / "other-agent").mkdir(parents=True)
        evidence = self.root / "tmp" / "other-agent" / "evidence.txt"
        evidence.write_text("retain")
        self.execute()
        self.assertEqual(m.Manufacturing(self.root).execute("clean"), 0)
        self.assertEqual(evidence.read_text(), "retain")
        self.assertFalse((self.root / "build").exists())
        self.assertTrue((self.root / "tmp" / "manufacturing" / "lock").exists())
        self.assertTrue((self.root / "pcb" / "CPL.csv").exists())

    def test_multiword_cli_is_invoked_as_argv_not_command_v(self):
        fake = FakeKiCad()
        pipeline = m.Manufacturing(self.root, "flatpak run --command=kicad-cli org.kicad.KiCad")
        with patch.object(m.subprocess, "run", fake), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(pipeline.execute("check"), 0, pipeline.errors)
        self.assertEqual(fake.calls[0], ["flatpak", "run", "--command=kicad-cli", "org.kicad.KiCad", "--version"])

    def test_cli_invocation_failure_is_recorded_and_blocks(self):
        with patch.object(m.subprocess, "run", side_effect=FileNotFoundError("real invocation failure")), contextlib.redirect_stderr(io.StringIO()):
            pipeline = m.Manufacturing(self.root, "missing-cli")
            self.assertNotEqual(pipeline.execute("check"), 0)
        self.assertIn("real invocation failure", (pipeline.reports / "version-0.log").read_text())

    def test_make_j4_all_public_targets_share_one_transaction(self):
        result = subprocess.run(["make", "-n", "-j4", *m_target_names()], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("scripts/manufacturing.py build"), 1)
        self.assertNotIn("manufacturing.py check", result.stdout)

    def test_make_forwards_quoted_cli_paths_without_shell_reinterpretation(self):
        result = subprocess.run(["make", "all", 'KICAD_CLI="missing path/kicad-cli"'], cwd=self.root,
                                capture_output=True, text=True, timeout=120)
        self.assertNotEqual(result.returncode, 0)
        commands = json.loads((self.root / "build" / "reports" / "commands.json").read_text())
        self.assertEqual(commands[0]["command"], ["missing path/kicad-cli", "--version"])
        self.assertFalse((self.root / "build" / "manifest.json").exists())

    def test_parallel_transactions_serialize_without_partial_package(self):
        fake = FakeKiCad()
        with patch.object(m.subprocess, "run", fake), contextlib.redirect_stdout(io.StringIO()):
            with ThreadPoolExecutor(max_workers=2) as executor:
                results = list(executor.map(lambda _: m.Manufacturing(self.root, "fake-kicad").execute("build"), range(2)))
        self.assertEqual(results, [0, 0])
        manifest = json.loads((self.root / "build" / "manifest.json").read_text())
        for name, digest in manifest["artifact_hashes"].items():
            self.assertEqual(m.sha256(self.root / "build" / name), digest)

    def test_zip_membership_payload_and_deterministic_metadata(self):
        one, two = self.root / "one.zip", self.root / "two.zip"
        members = {"pcb.kicad_pcb": self.root / "pcb" / "pcb.kicad_pcb"}
        m.make_zip(one, members)
        m.make_zip(two, members)
        self.assertEqual(one.read_bytes(), two.read_bytes())
        with zipfile.ZipFile(one, "a") as archive:
            archive.writestr("unexpected.txt", "extra")
        with self.assertRaises(nets.VerificationError):
            m.validate_zip(one, members)

    def test_exported_mask_aperture_exposes_via_hole(self):
        board_path = self.root / "pcb" / "pcb.kicad_pcb"
        board_path.write_text(BOARD.replace('(via (at 30 20)', '(via (at 19 30)'))
        board = nets.read_board(board_path)
        directory = self.root / "gerbers"
        directory.mkdir()
        fake_gerbers(directory, board)
        with self.assertRaisesRegex(nets.VerificationError, "exposes via hole"):
            m.validate_gerbers(directory, board)

    def test_malformed_and_incomplete_manufacturing_data_rejected(self):
        path = self.root / "bad.gbr"
        path.write_text("garbage\nM02*\n")
        with self.assertRaises(nets.VerificationError):
            m.parse_gerber(path, "Copper,L1,Top")
        path = self.root / "bad.csv"
        path.write_text("Ref,Val\nR1,1k\n")
        with self.assertRaises(nets.VerificationError):
            m.read_csv(path, m.POSITION_FIELDS)

    def test_malformed_legend_body_is_not_accepted_from_its_header(self):
        board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
        directory = self.root / "gerbers"
        directory.mkdir()
        fake_gerbers(directory, board)
        path = directory / "pcb-F_Silkscreen.gbr"
        path.write_text(path.read_text().replace("M02*", "unrecognized drawing operation*\nM02*"))
        with self.assertRaisesRegex(nets.VerificationError, "Unsupported/malformed Gerber geometry"):
            m.validate_gerbers(directory, board)

    def test_commands_after_comments_and_attributes_cannot_hide_copper(self):
        board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
        directory = self.root / "gerbers"
        directory.mkdir()
        fake_gerbers(directory, board)
        m.validate_gerbers(directory, board)
        path = directory / "pcb-F_Cu.gbr"
        original = path.read_text()
        draw = ["D22*", "X131000000Y-122500000D02*", "X155000000Y-122500000D01*"]
        definition = "%ADD22C,3.2*%\n"
        visible = definition + "\n".join(draw) + "\nM02*"
        path.write_text(original.replace("M02*", visible))
        segments = m.parse_gerber(path, "Copper,L1,Top")[1]
        self.assertEqual(segments[-1][:5], (131, -122.5, 155, -122.5, 3.2))
        with self.assertRaisesRegex(nets.VerificationError, "Extra/wrong"):
            m.validate_gerbers(directory, board)
        for prefix in ("G04 repro*", "%TF.Review,repro*%", "%TA.AperFunction,Conductor*%",
                       "%TO.N,POWER*%", "%TO.P,R1,1*%", "%TO.C,R1*%"):
            injection = prefix + "".join(draw)
            path.write_text(original.replace("M02*", definition + injection + "\nM02*"))
            self.assertIn(injection, path.read_text())
            with self.subTest(prefix=prefix), self.assertRaisesRegex(nets.VerificationError, "one complete Gerber statement"):
                m.validate_gerbers(directory, board)
        for extra in ("%ADD010C,20*%", "G04 malformed\x00 comment*", "G04 incomplete comment"):
            path.write_text(original.replace("M02*", extra + "\nM02*"))
            with self.subTest(extra=extra), self.assertRaises(nets.VerificationError):
                m.validate_gerbers(directory, board)

    def roundrect_exports(self):
        source = BOARD.replace('(pad "1" smd rect (at 0 -1 90) (size 2 1)',
                               '(pad "1" smd roundrect (at 0 -1 90) (size 3.2 3.2) (roundrect_rratio 0.25)', 1)
        self.assertNotEqual(source, BOARD)
        path = self.root / "pcb" / "pcb.kicad_pcb"
        path.write_text(source)
        board = nets.read_board(path)
        directory = self.root / "gerbers"
        directory.mkdir()
        fake_gerbers(directory, board)
        m.validate_gerbers(directory, board)
        return board, directory

    def test_roundrect_shifted_crossed_and_repeated_corners_rejected(self):
        board, directory = self.roundrect_exports()
        mutants = (
            "0.8X10.8X0.8X9.2X0.8X9.2X-0.8X10.8X-0.8X0",
            "0.8X-0.8X-0.8X0.8X0.8X0.8X-0.8X-0.8X0.8X0",
            "0.8X-0.8X-0.8X0.8X-0.8X0.8X0.8X0.8X0.8X0",
        )
        for layer in ("F.Cu", "F.Mask", "F.Paste"):
            path = directory / m.LAYERS[layer][0]
            original = path.read_text()
            declaration = next(line for line in original.splitlines() if re.match(r"%ADD\d+RoundRect,", line))
            prefix = declaration.split(",")[0] + ","
            for params in mutants:
                path.write_text(original.replace(declaration, prefix + params + "*%"))
                with self.subTest(layer=layer, params=params), self.assertRaisesRegex(nets.VerificationError, "RoundRect corners"):
                    m.validate_gerbers(directory, board)
            path.write_text(original)

    def test_roundrect_radius_must_match_source_not_just_bounding_box(self):
        board, directory = self.roundrect_exports()
        for layer in ("F.Cu", "F.Mask", "F.Paste"):
            path = directory / m.LAYERS[layer][0]
            original = path.read_text()
            declaration = next(line for line in original.splitlines() if re.match(r"%ADD\d+RoundRect,", line))
            smaller_radius = declaration.split(",")[0] + ",0.4X-1.2X-1.2X1.2X-1.2X1.2X1.2X-1.2X1.2X0*%"
            path.write_text(original.replace(declaration, smaller_radius))
            flashes = m.parse_gerber(path, m.LAYERS[layer][1])[0]
            changed = next(f for f in flashes if f[4] == "RoundRect")
            self.assertEqual(changed[2:6], (3.2, 3.2, "RoundRect", .4))
            self.assertEqual(board.footprints["J_LED_A"].pads[0].roundrect_ratio, .25)
            with self.subTest(layer=layer), self.assertRaisesRegex(nets.VerificationError, "Extra/wrong"):
                m.validate_gerbers(directory, board)
            path.write_text(original)

    def test_roundrect_definition_and_macro_comments_are_validated_before_use(self):
        board, directory = self.roundrect_exports()
        path = directory / "pcb-F_Cu.gbr"
        original = path.read_text()
        start = original.index("%AMRoundRect*")
        end = original.index("*%", start) + 3
        definition = original[start:end]
        without = original.replace(definition, "", 1)
        for name, changed in (
                ("missing", without),
                ("late", without.replace("M02*", definition + "M02*")),
                ("redefined", original.replace(definition, definition + definition, 1)),
                ("macro comment", original.replace("0 Rounded rectangle*", "0 repro*21,1,4,4,10,0,0*")),
                ("macro header", original.replace("%AMRoundRect*", "%AMRoundRect*0 repro*")),
                ("wrong primitive", original.replace("1,1,$1+$1,$2,$3*", "1,1,$1+$1,$2+10,$3*"))):
            path.write_text(changed)
            self.assertNotEqual(changed, original)
            with self.subTest(name=name), self.assertRaises(nets.VerificationError):
                m.validate_gerbers(directory, board)

    def test_unmodelled_critical_source_graphics_cannot_be_omitted_from_exports(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        directory = self.root / "gerbers"
        directory.mkdir()
        for owner, tag, layer in (("board", "gr_rect", "B.Paste"), ("board", "gr_rect", "F.Paste"),
                                  ("board", "gr_line", "B.Cu"), ("board", "gr_rect", "F.Mask"),
                                  ("footprint", "fp_line", "Edge.Cuts"), ("footprint", "fp_rect", "B.Paste"),
                                  ("footprint", "fp_rect", "F.Mask"), ("footprint", "fp_line", "F.Cu")):
            graphic = f'({tag} (start 1 1) (end 2 2) (stroke (width 0.15) (type solid)) (layer "{layer}"))'
            if owner == "board":
                source = BOARD.rstrip()[:-1] + graphic + ")\n"
            else:
                source = BOARD.replace('(property "Reference" "R1")', graphic + '(property "Reference" "R1")', 1)
            path.write_text(source)
            board = nets.read_board(path)
            # This producer intentionally models only pads/tracks and the board
            # outline, reproducing a missing graphic rather than an extra export.
            fake_gerbers(directory, board)
            with self.subTest(owner=owner, layer=layer), self.assertRaisesRegex(nets.VerificationError, "Unsupported source geometry"):
                m.validate_gerbers(directory, board)

    def test_smt_paste_replaced_by_equivalent_graphic_is_not_silently_dropped(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        source = BOARD.replace('(layers "F.Cu" "F.Mask" "F.Paste")', '(layers "F.Cu" "F.Mask")', 1)
        graphic = '(gr_rect (start 18.5 29) (end 19.5 31) (stroke (width 0) (type solid)) (fill yes) (layer "F.Paste"))'
        path.write_text(source.rstrip()[:-1] + graphic + ")\n")
        board = nets.read_board(path)
        pad = board.footprints["J_LED_A"].pads[0]
        self.assertEqual((pad.x, pad.y, pad.width, pad.height, pad.rotation), (19, 30, 2, 1, 90))
        self.assertNotIn("F.Paste", pad.layers)
        directory = self.root / "gerbers"
        directory.mkdir()
        fake_gerbers(directory, board)
        self.assertEqual(len(m.parse_gerber(directory / "pcb-F_Paste.gbr", "Paste,Top")[0]), 3)
        with self.assertRaisesRegex(nets.VerificationError, "Unsupported source geometry.*gr_rect.*F.Paste"):
            m.validate_gerbers(directory, board)


def m_target_names():
    return ["all", "package", "gerbers", "drills", "ipc", "bom", "cpl", "zip-gerbers", "zip-flytest", "check"]


@unittest.skipUnless(os.environ.get("KICAD_TEST_CLI"), "Set KICAD_TEST_CLI for isolated native CLI fixture probes")
class NativeContractTests(unittest.TestCase):
    def test_native_roundrect_and_rect_margins(self):
        parent = REPO / "tmp" / "manufacturing"
        parent.mkdir(parents=True, exist_ok=True)
        cases = (
            ("roundrect", .25, .2, .1, .1, ((1, 2, .25), (1.4, 2.4, .35), (1.4, 2.6, .35))),
            ("roundrect", .25, -.1, -.1, -.1, ((1, 2, .25), (.8, 1.8, .2), (.6, 1.4, .15))),
            ("rect", .25, .2, .1, .1, ((1, 2, 0), (1.4, 2.4, .2), (1.4, 2.6, .3))),
            ("rect", .25, -.1, -.1, -.1, ((1, 2, 0), (.8, 1.8, 0), (.6, 1.4, 0))),
            ("roundrect", .5, 0, 0, 0, ((1.00002, 2, .5),) * 3),
            ("roundrect", 0, 0, 0, 0, ((1, 2, 0),) * 3),
        )
        with tempfile.TemporaryDirectory(prefix="native-corners-", dir=parent) as temporary:
            root = Path(temporary)
            make_project(root)
            project = root / "pcb"
            pcb = project / "pcb.kicad_pcb"
            for index, (shape, ratio, mask, paste, paste_ratio, expected) in enumerate(cases):
                with self.subTest(shape=shape, ratio=ratio, mask=mask, paste=paste, paste_ratio=paste_ratio):
                    replacement = (f'(pad "1" smd {shape} (at 0 -1 90) (size 2 1) (roundrect_rratio {ratio}) '
                                   f'(solder_mask_margin {mask}) (solder_paste_margin {paste}) '
                                   f'(solder_paste_margin_ratio {paste_ratio})')
                    source = BOARD.replace('(pad "1" smd rect (at 0 -1 90) (size 2 1)', replacement, 1)
                    self.assertNotEqual(source, BOARD)
                    pcb.write_text(source)
                    board = nets.read_board(pcb)
                    directory = root / f"gerbers-{index}"
                    directory.mkdir()
                    result = subprocess.run([os.environ["KICAD_TEST_CLI"], "pcb", "export", "gerbers",
                                             "--layers", ",".join(m.LAYERS), "--precision", "6", "--no-protel-ext",
                                             "--subtract-soldermask", "--output", str(directory) + "/", str(pcb)],
                                            cwd=project, capture_output=True, text=True, timeout=120)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    m.validate_gerbers(directory, board)
                    for layer, dimensions in zip(("F.Cu", "F.Mask", "F.Paste"), expected):
                        filename, function = m.LAYERS[layer]
                        flashes = m.parse_gerber(directory / filename, function)[0]
                        flash = next(f for f in flashes if f[:2] == (19, -30) and f[6] == "J_LED_A")
                        for actual, required in zip((flash[2], flash[3], flash[5]), dimensions):
                            self.assertAlmostEqual(actual, required, places=6, msg=(layer, flash))

    def test_native_annular_constraint_has_no_B_item(self):
        parent = REPO / "tmp" / "manufacturing"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="native-unary-rule-", dir=parent) as temporary:
            root = Path(temporary)
            make_project(root)
            project = root / "pcb"
            pcb = project / "pcb.kicad_pcb"
            pcb.write_text(BOARD.replace('(size 2.2 2.2)', '(size 1.4 1.4)', 1))
            for use_b in (False, True):
                condition = "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'"
                if use_b:
                    condition += " && B.Type == 'Pad'"
                (project / "pcb.kicad_dru").write_text(
                    f'(version 1)\n(rule "Unary probe" (condition "{condition}") '
                    '(constraint annular_width (min 0.254mm)))\n')
                output = root / f"annular-{use_b}.json"
                result = subprocess.run([os.environ["KICAD_TEST_CLI"], "pcb", "drc", "--format", "json",
                                         "--severity-all", "--exit-code-violations", "--output", str(output), str(pcb)],
                                        cwd=project, capture_output=True, text=True, timeout=120)
                self.assertEqual(result.returncode, 5, result.stdout + result.stderr)
                data = json.loads(output.read_text())
                annular = [v for v in data["violations"] if v["type"] == "annular_width"]
                # KiCad checks annular width with A only. Treating B=A in the
                # source checker would incorrectly approve the second condition.
                self.assertEqual(bool(annular), not use_b, data)
                if annular:
                    self.assertTrue(all("Unary probe" in v["description"] for v in annular))

    def test_native_export_formats_and_failure_reports(self):
        # This intentionally disconnected synthetic fixture never touches the shared
        # source PCB or build/. It probes KiCad contracts, not design acceptance.
        parent = REPO / "tmp" / "manufacturing"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="native-contract-", dir=parent) as temporary:
            root = Path(temporary)
            make_project(root)
            project = root / "pcb"
            pcb = project / "pcb.kicad_pcb"
            cli = os.environ["KICAD_TEST_CLI"]
            rounded = BOARD.replace('(pad "1" thru_hole circle', '(pad "1" thru_hole roundrect', 1)
            rounded = rounded.replace('(size 2.2 2.2) (drill 1.0)',
                                      '(size 2.2 2.2) (roundrect_rratio 0.25) (drill 1.0)', 1)
            rounded = rounded.rstrip()[:-1] + '''
              (gr_circle (center 40 10) (end 42 10) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))
              (gr_text "P1" (at 45 10) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15)))))
            '''
            pcb.write_text(rounded, encoding="utf-8")
            board = nets.read_board(pcb)
            gerbers, drills = root / "gerbers", root / "drills"
            gerbers.mkdir()
            drills.mkdir()
            jobs = [
                ["pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp", "--output", root / "native.csv", pcb],
                ["pcb", "export", "ipcd356", "--output", root / "pcb.d356", pcb],
                ["pcb", "export", "drill", "--format", "excellon", "--drill-origin", "absolute", "--excellon-units", "mm",
                 "--excellon-zeros-format", "decimal", "--excellon-separate-th", "--output", str(drills) + "/", pcb],
                ["pcb", "export", "gerbers", "--layers", ",".join(m.LAYERS), "--precision", "6", "--no-protel-ext", "--subtract-soldermask",
                 "--output", str(gerbers) + "/", pcb],
                ["pcb", "export", "pdf", "--layers", "F.Fab,F.SilkS,Edge.Cuts", "--mode-single", "--black-and-white",
                 "--output", root / "Assembly.pdf", pcb],
            ]
            for args in jobs:
                result = subprocess.run([cli, *map(str, args)], cwd=project, capture_output=True, text=True, timeout=120)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            m.generate_cpl(root / "native.csv", root / "CPL.csv", board)
            nets.compare_ipc(root / "pcb.d356", board)
            m.validate_gerbers(gerbers, board)
            m.validate_drill(drills / "pcb-PTH.drl", board, True)
            m.validate_drill(drills / "pcb-NPTH.drl", board, False)
            # These are legal syntax but deliberate violations of both custom
            # constraints, proving KiCad evaluates the rules rather than ignores them.
            pcb.write_text(rounded.replace('"POWER"', '"EARTH"').replace('(size 2.2 2.2)', '(size 1.4 1.4)', 1), encoding="utf-8")
            for kind, domain, source in (("drc", "pcb", pcb), ("erc", "sch", project / "pcb.kicad_sch")):
                for fmt, ext in (("report", "txt"), ("json", "json")):
                    output = root / f"{kind}.{ext}"
                    args = [domain, kind, "--format", fmt, "--severity-all", "--exit-code-violations", "--output", output]
                    if kind == "drc":
                        args.append("--schematic-parity")
                    result = subprocess.run([cli, *map(str, args), str(source)], cwd=project, capture_output=True, text=True, timeout=120)
                    self.assertIn(result.returncode, (0, 5), result.stdout + result.stderr)
                    self.assertTrue(output.is_file(), result.stderr)
                    if fmt == "json":
                        data = json.loads(output.read_text())
                        self.assertEqual(data["$schema"], f"https://schemas.kicad.org/{kind}.v1.json")
                        if kind == "drc":
                            self.assertNotEqual(result.returncode, 0, "Disconnected fixture must not pass DRC")
                            kinds = {violation["type"] for violation in data["violations"]}
                            self.assertIn("annular_width", kinds, data)
                            self.assertIn("clearance", kinds, data)
                            descriptions = " ".join(v["description"] for v in data["violations"])
                            self.assertIn("Earth isolation", descriptions)
                            self.assertIn("Component PTH annular ring", descriptions)
                            with self.assertRaises(nets.VerificationError):
                                m.validate_report(output, kind, "9.0.7")
                        elif result.returncode == 0:
                            m.validate_report(output, kind, "9.0.7")
            # Export a real nonempty native schematic in both structured formats.
            # Its two unconnected pin nets still have a complete terminal inventory.
            schematic = project / "pcb.kicad_sch"
            schematic.write_text('''(kicad_sch (version 20250114) (generator "eeschema")
              (uuid "00000000-0000-4000-8000-000000000001") (paper "A4")
              (lib_symbols (symbol "Local:R" (in_bom yes) (on_board yes)
                (property "Reference" "R" (at 0 0 0) (effects (font (size 1.27 1.27))))
                (property "Value" "R" (at 0 0 0) (effects (font (size 1.27 1.27))))
                (symbol "R_1_1"
                  (pin passive line (at -2.54 0 0) (length 2.54)
                    (name "1" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))
                  (pin passive line (at 2.54 0 180) (length 2.54)
                    (name "2" (effects (font (size 1.27 1.27))))
                    (number "2" (effects (font (size 1.27 1.27)))))
                )))
              (symbol (lib_id "Local:R") (at 50 50 0) (unit 1) (in_bom yes) (on_board yes) (dnp no)
                (uuid "00000000-0000-4000-8000-000000000002")
                (property "Reference" "R1" (at 50 45 0) (effects (font (size 1.27 1.27))))
                (property "Value" "1k" (at 50 47 0) (effects (font (size 1.27 1.27))))
                (property "Footprint" "Local:THT" (at 50 50 0) (effects (font (size 1.27 1.27)) (hide yes)))
                (instances (project "pcb" (path "/00000000-0000-4000-8000-000000000001" (reference "R1") (unit 1))))))
            ''', encoding="utf-8")
            self.assertEqual(len(nets.children(nets.read_tree(schematic), "symbol")), 1)
            parsed = []
            for fmt, suffix in (("kicadxml", "xml"), ("kicadsexpr", "net")):
                output = root / f"schematic.{suffix}"
                result = subprocess.run([cli, "sch", "export", "netlist", "--format", fmt,
                                         "--output", str(output), str(schematic)], cwd=project,
                                        capture_output=True, text=True, timeout=120)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                parsed.append(nets.parse_netlist(output))
            self.assertEqual(nets.differences(*parsed), [])
            self.assertEqual(set().union(*parsed[0].values()), {("R1", "1"), ("R1", "2")})


if __name__ == "__main__":
    unittest.main()
