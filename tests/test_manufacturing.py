from concurrent.futures import ThreadPoolExecutor
import contextlib
import copy
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
import xml.etree.ElementTree as ET
import zipfile

from pcb import sync_libraries as sync
from scripts import manufacturing as m
from scripts import compare_nets as nets
from test_compare_nets import BOARD, ipc_text, xml_netlist


REPO = Path(__file__).resolve().parents[1]
# Superseded HP12 selection retained only as a synthetic pending-sourcing fixture.
EXTERNAL_METADATA = {
    "MPN": "HP122WF2201T4E", "Manufacturer": "Uni-Royal", "LCSC": "",
    "Sourcing": "External",
    "Sourcing Reference": "https://store.nacsemi.com/products/detail?stock=XSJMZ0000010410",
}


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
    for name in m.ENGINEERING_NOTES:
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
    setup = nets.child(board.tree, "setup")
    global_tenting = nets.child(setup, "tenting", False)
    via_flags = {}
    for node in nets.children(board.tree, "via"):
        field = nets.child(node, "tenting", False)
        if field is None:
            field = global_tenting
        via_flags[nets.numbers(nets.child(node, "at")[1:])] = field[1:] if field is not None else ["front", "back"]
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
                if pad.kind == "via":
                    side = "front" if layer == "F.Mask" else "back"
                    if not layer.endswith("Mask") or side in via_flags[(pad.x, pad.y)]:
                        continue
                elif not (layer in pad.layers or "*." + layer.split(".")[1] in pad.layers):
                    continue
            else:
                continue
            w, h = pad.width, pad.height
            shape = {"circle": "C", "rect": "R", "roundrect": "RoundRect"}[pad.shape]
            radius = 0
            if layer.endswith(("Mask", "Paste")):
                margin = (float(nets.value(setup, "pad_to_mask_clearance", "0")) if pad.kind == "via"
                          else pad.mask_margin if layer.endswith("Mask") else pad.paste_margin)
                ratio = pad.paste_ratio if layer.endswith("Paste") else 0
                mx, my = margin + w * ratio, margin + h * ratio
                w, h = w + 2 * mx, h + 2 * my
                if pad.shape == "rect" and mx > 0:
                    shape, radius = "RoundRect", min(mx, w / 2, h / 2)
            if pad.shape == "roundrect":
                radius = min(w, h) * pad.roundrect_ratio
            if pad.rotation % 180:
                w, h = h, w
            if shape == "RoundRect":
                if not roundrect_defined:
                    lines += ["%AMRoundRect*", "0 Rounded rectangle*", *m.ROUNDRECT_PRIMITIVES[:-1],
                              m.ROUNDRECT_PRIMITIVES[-1] + "%"]
                    roundrect_defined = True
                hx, hy = max(w / 2 - radius, .00001), max(h / 2 - radius, .00001)
                params = "X".join(f"{v:.6f}" for v in (radius, -hx, -hy, hx, -hy, hx, hy, -hx, hy, 0))
            else:
                params = f"{w:.6f}" if shape == "C" else f"{w:.6f}X{h:.6f}"
            lines += [f"%ADD{aperture}{shape},{params}*%", f"D{aperture}*"]
            if layer.endswith("Cu"):
                if pad.kind != "via":
                    lines.append(f"%TO.P,{pad.ref},{pad.pin}*%")
                lines.append(f"%TO.N,{pad.net}*%")
            elif pad.kind != "via":
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
    def __init__(self, defect=None, netlist=None):
        self.defect = defect
        self.netlist = xml_netlist() if netlist is None else netlist
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
                output.write_text(self.netlist, encoding="utf-8")
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

    def execute(self, mode="build", defect=None, netlist=None):
        fake = FakeKiCad(defect, netlist)
        pipeline = m.Manufacturing(self.root, "fake-kicad")
        with patch.object(m.subprocess, "run", fake), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = pipeline.execute(mode)
        return rc, pipeline, fake

    def write_bom(self, rows):
        with (self.root / "pcb" / "BOM.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    def external_project(self):
        metadata = " ".join(f'(property {json.dumps(key)} {json.dumps(content)})'
                            for key, content in EXTERNAL_METADATA.items())
        source = BOARD.replace(
            '(property "MPN" "R1K") (property "Manufacturer" "Example") (property "LCSC Part #" "C123")', metadata)
        source = source.replace('(property "Reference" "R_DNP")', '(property "Reference" "R2") ' + metadata)
        source = source.replace('(attr through_hole dnp)', '(attr through_hole)')
        source = source.replace('(property "Value" "1k")', '(property "Value" "2k2")')
        (self.root / "pcb" / "pcb.kicad_pcb").write_text(source, encoding="utf-8")
        rows = m.read_csv(self.root / "pcb" / "BOM.csv", ("Designator",))
        for row in rows:
            row.update(Sourcing="LCSC", **{"Sourcing Reference": ""})
            if row["Designator"] == "R1":
                row.update(Comment="2k2", Designator="R1,R2", **{
                    "LCSC Part #": "", **{key: val for key, val in EXTERNAL_METADATA.items() if key != "LCSC"}})
        self.write_bom(rows)
        tree = ET.fromstring(xml_netlist())
        for comp in tree.findall("components/comp"):
            if comp.get("ref") == "R_DNP":
                comp.set("ref", "R2")
                comp.remove(comp.find("property"))
            if comp.get("ref") in ("R1", "R2"):
                comp.find("value").text = "2k2"
                fields = comp.find("fields")
                fields.clear()
                for key, content in EXTERNAL_METADATA.items():
                    if key != "LCSC":  # Native XML may omit this deliberately empty field.
                        ET.SubElement(fields, "field", name=key).text = content
        for node in tree.findall("nets/net/node"):
            if node.get("ref") == "R_DNP":
                node.set("ref", "R2")
        xml = self.root / "schematic.xml"
        ET.ElementTree(tree).write(xml, encoding="utf-8", xml_declaration=True)
        return xml

    def assert_failed(self, defect=None, mode="build"):
        previous_cpl = (self.root / "pcb" / "CPL.csv").read_bytes()
        rc, pipeline, fake = self.execute(mode, defect=defect)
        self.assertNotEqual(rc, 0)
        self.assertFalse((self.root / "build" / "manifest.json").exists())
        self.assertFalse((self.root / "build" / "Gerbers.zip").exists())
        self.assertEqual((self.root / "pcb" / "CPL.csv").read_bytes(), previous_cpl)
        return pipeline, fake

    def test_success_publishes_complete_hashed_package_and_native_mirrors(self):
        for mode, state in (("build", "verified"), ("prototype", "prototype")):
            with self.subTest(mode=mode):
                rc, pipeline, fake = self.execute(mode)
                self.assertEqual(rc, 0, pipeline.errors)
                build = self.root / "build"
                manifest = m.read_json(build / "manifest.json")
                status = m.read_json(build / "status.json")
                report = m.read_json(build / "reports/verification.json")
                for record in (manifest, status, report):
                    self.assertEqual((record["status"], record["mode"], record["publication"]),
                                     (state, mode, m.PUBLICATION[state]))
                self.assertTrue(status["requires_matching_manifest_for_upload"])
                self.assertEqual(status["required_manifest_status"], state)
                self.assertEqual(manifest["hardware_revision"], "fixture-1")
                self.assertEqual(manifest["tool"]["version"], "9.0.7")
                self.assertEqual(manifest["verification"]["population"]["references"], ["J_LED_A", "J_LED_C", "R1"])
                self.assertEqual(manifest["source_hashes"], m.source_inventory(self.root))
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
                for name in (*m.ENGINEERING_NOTES, "verification.json"):
                    self.assertEqual((build / name).read_bytes(), (self.root / "pcb" / name).read_bytes())
                    self.assertEqual(m.sha256(build / name), manifest["source_hashes"][f"pcb/{name}"])
                for name in ("analyze_limits.py", "design_bounds.py"):
                    self.assertIn(f"scripts/{name}", manifest["source_hashes"])
                readme = (build / "README.txt").read_bytes()
                self.assertEqual(readme, m.package_readme("fixture-1", mode, []).encode("utf-8"))
                self.assertEqual(b"PROTOTYPE ONLY" in readme, mode == "prototype")
                for name, members in (("Gerbers.zip", m.FAB_FILES | {"README.txt"}),
                                      ("FlyTest.zip", {"Gerbers.zip", "pcb.d356", "README.txt"})):
                    with zipfile.ZipFile(build / name) as archive:
                        self.assertEqual(set(archive.namelist()), members)
                        self.assertEqual(archive.read("README.txt"), readme)
                self.assertNotEqual(pipeline.run / "exports" / "drills", pipeline.run / "exports" / "gerbers")

    def test_check_runs_all_gates_and_refreshes_reference_without_publishing(self):
        rc, pipeline, fake = self.execute("check")
        self.assertEqual(rc, 0, pipeline.errors)
        self.assertFalse((self.root / "build" / "CPL.csv").exists())
        self.assertFalse((self.root / "build" / "manifest.json").exists())
        status = m.read_json(self.root / "build/status.json")
        self.assertEqual(status["mode"], "check")
        self.assertEqual(status["publication"], "Not published.")
        self.assertIsNone(status["required_manifest_status"])
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
        for filename in ("pcb.kicad_dru", "pcb.kicad_pro", "fp-lib-table", "sym-lib-table", "verification.json",
                         *m.ENGINEERING_NOTES):
            path = self.root / "pcb" / filename
            data = path.read_bytes()
            path.unlink()
            for mode in ("build", "prototype"):
                with self.subTest(filename=filename, mode=mode):
                    pipeline, fake = self.assert_failed(mode=mode)
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

    def test_engineering_holds_defer_for_prototype_but_failed_production_quarantines_it(self):
        path = self.root / "pcb" / "verification.json"
        review = m.read_json(path)
        review.update(release_holds=[{"id": key, "reason": "Synthetic qualification hold"}
                                     for key in ("C4", "C5", "W3", "W1", "W4")], file_release_review=None)
        m.write_json(path, review)
        review_hash = m.sha256(path)
        for mode, expected in (("check", 0), ("prototype", 0), ("build", 1)):
            rc, pipeline, fake = self.execute(mode)
            self.assertEqual(rc, expected, pipeline.errors)
            self.assertTrue((pipeline.run / "exports" / "CPL.csv").exists())
            self.assertEqual(pipeline.verification["engineering_release"],
                             {"verified": False, "holds": review["release_holds"], "review": None})
            self.assertEqual(m.sha256(path), review_hash)
            for name in ("build/manifest.json", "build/Gerbers.zip", "pcb/Gerbers.zip"):
                self.assertEqual((self.root / name).exists(), mode == "prototype", name)
            if mode == "prototype":
                self.assertEqual(m.read_json(self.root / "build/manifest.json")["status"], "prototype")
                readme = (self.root / "build/README.txt").read_text()
                self.assertIn("PROTOTYPE ONLY", readme)
                for hold in review["release_holds"]:
                    self.assertIn(f"- {hold['id']}: {hold['reason']}", readme)
                prototype_zip = m.sha256(self.root / "pcb/Gerbers.zip")
            elif mode == "build":
                self.assertEqual(m.read_json(pipeline.run / "previous-build/manifest.json")["status"], "prototype")
                self.assertEqual(m.sha256(pipeline.run / "previous-pcb-Gerbers.zip"), prototype_zip)
                self.assertEqual(m.read_json(self.root / "build/status.json")["status"], "failed")
        for defect in ("warning", "report-malformed", "geometry", "ipc-net", "missing-cpl", "flipped-y",
                       "missing-layer", "wrong-drill", "export-warning", "export-failure"):
            with self.subTest(prototype_defect=defect):
                self.assert_failed(defect, mode="prototype")
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
        for mode in ("build", "prototype"):
            with self.subTest(mode=mode):
                self.assert_failed(mode=mode)

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

    def test_lcsc_sourcing_defaults_require_codes_and_explicit_sources_match(self):
        path = self.root / "pcb" / "BOM.csv"
        rows = m.read_csv(path, ("Designator",))
        board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
        xml = self.root / "schematic.xml"
        xml.write_text(xml_netlist(), encoding="utf-8")
        for explicit in (False, True):
            with self.subTest(explicit=explicit):
                if explicit:
                    for row in rows:
                        row.update(Sourcing="LCSC", **{"Sourcing Reference": ""})
                self.write_bom(rows)
                self.assertEqual(len(m.validate_bom(path, xml, board)), 3)
                rows[0]["LCSC Part #"] = ""
                self.write_bom(rows)
                with self.assertRaisesRegex(nets.VerificationError, "invalid LCSC"):
                    m.validate_bom(path, xml, board)
                rows[0]["LCSC Part #"] = "C123"
        self.write_bom(rows)
        for key, content in (("Sourcing", ""), ("Sourcing", "Unknown"), ("Sourcing", "External"),
                             ("Sourcing Reference", EXTERNAL_METADATA["Sourcing Reference"])):
            for owner in ("PCB", "XML"):
                with self.subTest(owner=owner, key=key, content=content):
                    fields = {"Sourcing": "LCSC", "Sourcing Reference": "", key: content}
                    board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
                    tree = ET.fromstring(xml_netlist())
                    if owner == "PCB":
                        board.footprints["R1"].properties.update(fields)
                    else:
                        for name, val in fields.items():
                            ET.SubElement(tree.find("components/comp/fields"), "field", name=name).text = val
                    ET.ElementTree(tree).write(xml, encoding="utf-8")
                    with self.assertRaisesRegex(nets.VerificationError, "BOM Sourcing"):
                        m.validate_bom(path, xml, board)

    def test_external_bom_requires_explicit_source_empty_code_and_https_record(self):
        self.external_project()
        path = self.root / "pcb" / "BOM.csv"
        original = m.read_csv(path, ("Designator",))
        for key, contents in (
                ("Sourcing", (None, "", " ", "Unknown", "external", "LCSC")),
                ("LCSC Part #", (None, "C123", "TBD", " ")),
                ("Sourcing Reference", (None, "", " ", "TBD", "http://www.vishay.com/part", "https://",
                                       "https:///part", "https://[invalid", "https://vishay.com:invalid/part",
                                       "https://user@vishay.com/part", "https://vishay.com/part\n",
                                       "https://vishay.com/part name", "https://vishay.com\\part")),
                ("LCSC", ("C123",))):
            for content in contents:
                with self.subTest(key=key, content=content):
                    rows = copy.deepcopy(original)
                    if content is None:
                        for row in rows:
                            row.pop(key, None)
                    else:
                        for row in rows:
                            row.setdefault(key, "")
                        rows[0][key] = content
                    self.write_bom(rows)
                    with self.assertRaises(nets.VerificationError):
                        m.read_bom(path)
        for key in ("Comment", "Designator", "Footprint", "MPN", "Manufacturer"):
            rows = copy.deepcopy(original)
            rows[0][key] = " "
            self.write_bom(rows)
            with self.subTest(key=key), self.assertRaisesRegex(nets.VerificationError, "empty sourcing"):
                m.read_bom(path)
        rows = copy.deepcopy(original)
        rows[1]["Sourcing Reference"] = EXTERNAL_METADATA["Sourcing Reference"]
        self.write_bom(rows)
        with self.assertRaisesRegex(nets.VerificationError, "LCSC BOM Sourcing Reference must be empty"):
            m.read_bom(path)

    def test_external_source_identity_and_reference_parity_are_not_optional(self):
        xml = self.external_project()
        original = xml.read_text()
        path = self.root / "pcb" / "BOM.csv"
        for owner in ("PCB", "XML"):
            for key, contents in (
                    ("MPN", (None, "", "WRONG-MPN")), ("Manufacturer", (None, "", "WRONG-MANUFACTURER")),
                    ("Sourcing", (None, "", "LCSC", "Unknown")),
                    ("Sourcing Reference", (None, "", EXTERNAL_METADATA["Sourcing Reference"] + "0"))):
                for content in contents:
                    with self.subTest(owner=owner, key=key, content=content):
                        board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
                        tree = ET.fromstring(original)
                        if owner == "PCB":
                            fields = board.footprints["R1"].properties
                            if content is None:
                                fields.pop(key)
                            else:
                                fields[key] = content
                        else:
                            fields = tree.find("components/comp/fields")
                            field = fields.find(f"field[@name='{key}']")
                            if content is None:
                                fields.remove(field)
                            else:
                                field.text = content
                        ET.ElementTree(tree).write(xml, encoding="utf-8")
                        with self.assertRaisesRegex(nets.VerificationError, "BOM " + key):
                            m.validate_bom(path, xml, board)

    def test_external_lcsc_aliases_and_xml_empty_field_omission_are_narrow(self):
        xml = self.external_project()
        original = xml.read_text()
        path = self.root / "pcb" / "BOM.csv"
        for owner in ("PCB", "XML"):
            for aliases in ({}, {"LCSC": ""}, {"LCSC Part #": ""}, {"LCSC": "", "LCSC Part #": ""},
                            {"LCSC": "C123"}, {"LCSC Part #": "C123"},
                            {"LCSC": "", "LCSC Part #": "C123"}, {"LCSC": "C123", "LCSC Part #": ""}):
                with self.subTest(owner=owner, aliases=aliases):
                    board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
                    tree = ET.fromstring(original)
                    if owner == "PCB":
                        board.footprints["R1"].properties.pop("LCSC")
                        board.footprints["R1"].properties.update(aliases)
                    else:
                        for key, content in aliases.items():
                            ET.SubElement(tree.find("components/comp/fields"), "field", name=key).text = content
                    ET.ElementTree(tree).write(xml, encoding="utf-8")
                    if any(aliases.values()) or (owner == "PCB" and not aliases):
                        with self.assertRaisesRegex(nets.VerificationError, "LCSC Part #"):
                            m.validate_bom(path, xml, board)
                    else:
                        self.assertEqual(len(m.validate_bom(path, xml, board)), 4)
        for key in ("MPN", "Manufacturer", "Sourcing", "Sourcing Reference", "LCSC"):
            tree = ET.fromstring(original)
            fields = tree.find("components/comp/fields")
            if key == "LCSC":
                ET.SubElement(fields, "field", name=key).text = "C123"
            ET.SubElement(fields, "field", name=key).text = EXTERNAL_METADATA[key]
            ET.ElementTree(tree).write(xml, encoding="utf-8")
            with self.subTest(key=key), self.assertRaisesRegex(nets.VerificationError, "duplicate XML component field"):
                m.validate_bom(path, xml, nets.read_board(self.root / "pcb" / "pcb.kicad_pcb"))
        # Ordinary XML must still contain its code, even when the BOM has one.
        tree = ET.fromstring(original)
        fields = tree.find("components/comp[@ref='J_LED_A']/fields")
        fields.remove(fields.find("field[@name='LCSC Part #']"))
        ET.ElementTree(tree).write(xml, encoding="utf-8")
        with self.assertRaisesRegex(nets.VerificationError, "LCSC Part #"):
            m.validate_bom(path, xml, nets.read_board(self.root / "pcb" / "pcb.kicad_pcb"))

    def test_external_parts_still_require_exact_bom_identity_and_population(self):
        xml = self.external_project()
        path = self.root / "pcb" / "BOM.csv"
        original = m.read_csv(path, ("Designator",))
        board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
        for key, content in (("MPN", "WRONG-MPN"), ("Manufacturer", "WRONG-MANUFACTURER"), ("Comment", "1k"),
                             ("Footprint", "Local:SMT"), ("Designator", "R1"), ("Designator", "R1,R1"),
                             ("Designator", "R1,UNKNOWN"), ("Designator", "R1,R2,H1"), ("Quantity", "1")):
            rows = copy.deepcopy(original)
            if key == "Quantity":
                for row in rows:
                    row[key] = str(len(row["Designator"].split(",")))
            rows[0][key] = content
            self.write_bom(rows)
            with self.subTest(key=key, content=content), self.assertRaises(nets.VerificationError):
                m.validate_bom(path, xml, board)
        self.write_bom(original)
        original_xml = xml.read_text()
        for attribute in ("dnp", "exclude_from_bom", "exclude_from_pos_files"):
            for schematic_matches in (False, True):
                with self.subTest(attribute=attribute, schematic_matches=schematic_matches):
                    board = nets.read_board(self.root / "pcb" / "pcb.kicad_pcb")
                    board.footprints["R1"].attributes.add(attribute)
                    tree = ET.fromstring(original_xml)
                    if schematic_matches:
                        ET.SubElement(tree.find("components/comp"), "property", name=attribute)
                    ET.ElementTree(tree).write(xml, encoding="utf-8")
                    with self.assertRaises(nets.VerificationError):
                        m.validate_bom(path, xml, board)

    def test_external_check_reports_file_parity_not_allocation_and_keeps_bom_exact(self):
        xml = self.external_project()
        with patch("builtins.print") as output:
            rc, pipeline, fake = self.execute("check", netlist=xml.read_text())
        self.assertEqual(rc, 0, pipeline.errors)
        sourcing = pipeline.verification["sourcing"]
        self.assertEqual(sourcing, {
            "file_metadata_verified": True, "allocation_verified": False,
            "pending_external": {ref: {key: EXTERNAL_METADATA[key] for key in
                                      ("MPN", "Manufacturer", "Sourcing Reference")} for ref in ("R1", "R2")}})
        printed = "\n".join(call.args[0] for call in output.call_args_list)
        self.assertIn("pending allocation (not verified)", printed)
        for ref in ("R1", "R2"):
            self.assertIn(f"{ref}: {EXTERNAL_METADATA['MPN']} ({EXTERNAL_METADATA['Sourcing Reference']})", printed)
        report = m.read_json(self.root / "build" / "reports" / "verification.json")
        self.assertEqual(report["status"], "checked")
        self.assertEqual(report["checks"]["sourcing"], sourcing)
        for key in ("population", "nets", "archives", "export_diagnostics"):
            self.assertTrue(report["checks"][key]["verified"])
        self.assertEqual(report["checks"]["population"]["references"], ["J_LED_A", "J_LED_C", "R1", "R2"])
        self.assertEqual((pipeline.run / "release" / "BOM.csv").read_bytes(),
                         (self.root / "pcb" / "BOM.csv").read_bytes())
        self.assertTrue((self.root / "pcb" / "CPL.csv").read_text().startswith("Designator,"))
        self.assertEqual({p.name for p in (self.root / "build").iterdir()},
                         {"reports", "status.json", "drc_report.txt", "drc_report.json", "erc_report.txt", "erc_report.json"})
        self.assertFalse((self.root / "pcb" / "Gerbers.zip").exists())

    def test_external_allocation_blocks_publication_even_with_closed_engineering_holds(self):
        rc, pipeline, fake = self.execute()
        self.assertEqual(rc, 0, pipeline.errors)
        self.assertFalse(pipeline.verification["sourcing"]["allocation_verified"])
        self.assertEqual(pipeline.verification["sourcing"]["pending_external"], {})
        xml = self.external_project()
        rc, pipeline, fake = self.execute(netlist=xml.read_text())
        self.assertEqual(rc, 1)
        self.assertEqual(pipeline.errors, [
            "Unresolved external sourcing allocation; verified draft exports retained privately: R1, R2"])
        self.assertTrue(pipeline.verification["engineering_release"]["verified"])
        self.assertTrue(pipeline.verification["archives"]["verified"])
        self.assertEqual(set(pipeline.verification["sourcing"]["pending_external"]), {"R1", "R2"})
        self.assertTrue((pipeline.run / "previous-build" / "manifest.json").exists())
        self.assertTrue((pipeline.run / "previous-pcb-Gerbers.zip").exists())
        self.assertFalse(any(c[0] == "git" for c in fake.calls))
        self.assertEqual({p.name for p in (self.root / "build").iterdir()},
                         {"reports", "status.json", "drc_report.txt", "drc_report.json", "erc_report.txt", "erc_report.json"})
        self.assertFalse((self.root / "pcb" / "Gerbers.zip").exists())
        self.assertEqual(m.read_json(self.root / "build" / "status.json")["status"], "failed")

    def test_external_allocation_does_not_replace_or_add_to_engineering_hold_error(self):
        xml = self.external_project()
        path = self.root / "pcb" / "verification.json"
        review = m.read_json(path)
        review.update(release_holds=[{"id": key, "reason": "Synthetic open hold"} for key in ("C4", "C5", "W3", "W1", "W4")],
                      file_release_review=None)
        m.write_json(path, review)
        for mode, expected in (("check", 0), ("build", 1), ("prototype", 1)):
            with self.subTest(mode=mode):
                rc, pipeline, fake = self.execute(mode, netlist=xml.read_text())
                self.assertEqual(rc, expected)
                error = {"build": "Open engineering release holds; verified draft exports retained privately",
                         "prototype": "Unresolved external sourcing allocation; verified draft exports retained privately: R1, R2"}
                self.assertEqual(pipeline.errors, [error[mode]] if mode in error else [])
                self.assertEqual(pipeline.verification["engineering_release"]["holds"], review["release_holds"])
                self.assertEqual(set(pipeline.verification["sourcing"]["pending_external"]), {"R1", "R2"})
                self.assertEqual({p.name for p in (self.root / "build").iterdir()},
                                 {"reports", "status.json", "drc_report.txt", "drc_report.json", "erc_report.txt", "erc_report.json"})
                self.assertFalse((self.root / "pcb" / "Gerbers.zip").exists())

    def test_sync_metadata_validates_external_rows_and_changes_only_reviewed_metadata(self):
        xml = self.external_project()
        project = self.root / "pcb"
        paths = (project / "pcb.kicad_pcb", project / "pcb.kicad_sch")
        board, schematic = (sync.parse(path.read_text()) for path in paths)
        bom = m.read_bom(project / "BOM.csv")
        metadata_keys = {*EXTERNAL_METADATA, "LCSC Part #"}
        for fp in sync.children(board, "footprint"):
            props = {json.loads(p[1]): p for p in sync.children(fp, "property")}
            ref = json.loads(props["Reference"][2])
            if ref not in bom:
                continue
            if ref == "R2":
                fp[:] = [item for item in fp if not (isinstance(item, list) and item[0] == "property"
                                                    and json.loads(item[1]) in metadata_keys)]
            else:
                stale = {"Sourcing": "LCSC" if ref == "R1" else "External",
                         "Sourcing Reference": "https://example.com/stale-record"}
                if ref == "R1":
                    stale.update(MPN="OLD-MPN", Manufacturer="OLD-MANUFACTURER", LCSC="C999", **{"LCSC Part #": "C888"})
                for key, content in stale.items():
                    if key in props:
                        props[key][2] = json.dumps(content)
                    else:
                        fp.append(["property", json.dumps(key), json.dumps(content)])
            schematic.append(["symbol", ["lib_id", '"Local:THT"'], ["at", "50", "50", "0"],
                              ["in_bom", "yes"], ["on_board", "yes"], ["dnp", "no"],
                              *copy.deepcopy(sync.children(fp, "property")), ["property", '"Footprint"', fp[1]]])
        for path, tree in zip(paths, (board, schematic)):
            path.write_text(sync.format_node(tree) + "\n", encoding="utf-8")
        before = [path.read_bytes() for path in paths]
        rows = m.read_csv(project / "BOM.csv", ("Designator",))
        with patch.object(sync, "__file__", str(project / "sync_libraries.py")), \
                patch.object(sync.sys, "argv", ["sync_libraries.py", "--sync-metadata"]), \
                contextlib.redirect_stdout(io.StringIO()):
            for key, content in (("Sourcing", ""), ("Sourcing", "Unknown"), ("Sourcing Reference", ""),
                                 ("Sourcing Reference", "http://example.com/part"), ("LCSC Part #", "C123"),
                                 ("MPN", ""), ("Manufacturer", ""), ("Comment", "WRONG"),
                                 ("Footprint", "Local:SMT"), ("Designator", "R1,R2,UNKNOWN"),
                                 ("Designator", "R1,R1")):
                changed = copy.deepcopy(rows)
                changed[0][key] = content
                self.write_bom(changed)
                with self.subTest(key=key, content=content), self.assertRaises(ValueError):
                    sync.main()
                self.assertEqual([path.read_bytes() for path in paths], before)
            self.write_bom(rows)
            sync.main()
            after = [path.read_bytes() for path in paths]
            sync.main()
            self.assertEqual([path.read_bytes() for path in paths], after)
        for old, new, kind in zip(before, after, ("footprint", "symbol")):
            original, updated = sync.parse(old.decode()), sync.parse(new.decode())
            for instance in sync.children(updated, kind):
                props = {json.loads(p[1]): json.loads(p[2]) for p in sync.children(instance, "property")}
                ref = props["Reference"]
                if ref in bom:
                    row = bom[ref]
                    expected = {"MPN": row["MPN"], "Manufacturer": row["Manufacturer"], "LCSC": row["LCSC Part #"],
                                "Sourcing": row["Sourcing"], "Sourcing Reference": row["Sourcing Reference"]}
                    self.assertEqual({key: props[key] for key in expected}, expected)
                    if "LCSC Part #" in props:
                        self.assertEqual(props["LCSC Part #"], row["LCSC Part #"])
            for tree in (original, updated):
                for instance in sync.children(tree, kind):
                    instance[:] = [item for item in instance if not (
                        isinstance(item, list) and item[0] == "property" and json.loads(item[1]) in metadata_keys)]
            self.assertEqual(original, updated, "Geometry, values, footprints and non-sourcing fields must not change")
        self.assertEqual(set(m.validate_bom(project / "BOM.csv", xml, nets.read_board(paths[0]))), set(bom))
        # The standalone script must resolve the same shared validator from its fixture root.
        script = project / "sync_libraries.py"
        shutil.copy2(REPO / "pcb" / "sync_libraries.py", script)
        result = subprocess.run([sync.sys.executable, "-B", "-W", "error", str(script), "--sync-metadata"],
                                cwd=self.root, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([path.read_bytes() for path in paths], after)

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

        for mode in ("build", "prototype"):
            with self.subTest(mode=mode):
                pipeline = m.Manufacturing(self.root, "fake-kicad")
                with patch.object(m.subprocess, "run", change_source), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertNotEqual(pipeline.execute(mode), 0)
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

        for mode in ("build", "prototype"):
            with self.subTest(mode=mode):
                pipeline = m.Manufacturing(self.root, "fake-kicad")
                with patch.object(m.subprocess, "run", change_staged), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    self.assertNotEqual(pipeline.execute(mode), 0)
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
        cases = [([], "build"), (["check"], "check"), (m_target_names(), "build"),
                 (["gerbers", "prototype", "check"], "prototype")]
        for prototype in ("gerbers", "prototype"):
            cases += [([prototype], "prototype"), (["check", prototype], "prototype"), ([prototype, "check"], "prototype")]
            for production in set(m_target_names()) - {"gerbers", "prototype", "check"}:
                cases += [([production], "build"), ([production, prototype], "build"), ([prototype, production], "build")]
        for goals, mode in cases:
            with self.subTest(goals=goals):
                result = subprocess.run(["make", "-n", "-j4", *goals], cwd=self.root, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                commands = [line.split() for line in result.stdout.splitlines() if "scripts/manufacturing.py" in line]
                self.assertEqual(len(commands), 1, result.stdout)
                self.assertEqual(commands[0][-1], mode)

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
            for modes in (("build", "build"), ("prototype", "build"), ("build", "prototype")):
                with self.subTest(modes=modes), ThreadPoolExecutor(max_workers=2) as executor:
                    results = list(executor.map(lambda mode: m.Manufacturing(self.root, "fake-kicad").execute(mode), modes))
                self.assertEqual(results, [0, 0])
                manifest = m.read_json(self.root / "build/manifest.json")
                self.assertIn((manifest["mode"], manifest["status"]), (("build", "verified"), ("prototype", "prototype")))
                for name, digest in manifest["artifact_hashes"].items():
                    self.assertEqual(m.sha256(self.root / "build" / name), digest)
                self.assertEqual((self.root / "build/README.txt").read_text(),
                                 m.package_readme("fixture-1", manifest["mode"], []))

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

    def test_via_mask_settings_inheritance_and_explicit_both_side_overrides(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        cases = (("", (True, True)), ("(tenting)", (False, False)), ("(tenting none)", (False, False)),
                 ("(tenting front)", (True, False)), ("(tenting back)", (False, True)),
                 ("(tenting front back)", (True, True)))
        for global_flags, default in cases:
            for local_flags, override in cases:
                for margin in (0, .2, -.1):
                    with self.subTest(global_flags=global_flags, local_flags=local_flags, margin=margin):
                        source = BOARD.replace('(pad_to_mask_clearance 0) (tenting front back)',
                                               f'(pad_to_mask_clearance {margin}) {global_flags}')
                        path.write_text(source.replace('(via (at 30 20)', f'(via {local_flags} (at 30 20)'))
                        settings = m.via_mask_settings(nets.read_board(path))
                        self.assertEqual(set(settings), {(30, 20)})
                        self.assertEqual(settings[(30, 20)][:2], override if local_flags else default)
                        self.assertAlmostEqual(settings[(30, 20)][2], .9 + margin)

    def test_via_mask_settings_reject_unsupported_or_ambiguous_source(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        sources = [BOARD.replace('(tenting front back)', flags) for flags in
                   ('(tenting front front)', '(tenting none front)', '(tenting yes)',
                    '(tenting (front no))', '(tenting) (tenting front)')]
        sources += [BOARD.replace('(via (at 30 20)', f'(via {field} (at 30 20)') for field in
                    ('(tenting (front no) (back yes))', '(tenting front front)', '(tenting unknown)',
                     '(tenting) (tenting back)', '(solder_mask_margin 0.2)', '(padstack)', '(filling yes)')]
        sources += [BOARD.replace('(tenting front back)', '(tenting)').replace(
                        '(pad_to_mask_clearance 0)', f'(pad_to_mask_clearance {margin})')
                    for margin in ('-0.9', '-1', 'nan', 'inf')]
        sources += [BOARD.replace('(setup ', '(setup (pcbplotparams (viasonmask true)) '),
                    BOARD.replace('(via (at 30 20)',
                                  '(via (at 30 20) (size 1.8) (drill 1) (layers "F.Cu" "B.Cu") (net 1)) '
                                  '(via (at 30 20)')]
        for source in sources:
            path.write_text(source)
            with self.subTest(source=source), self.assertRaises(nets.VerificationError):
                m.via_mask_settings(nets.read_board(path))

    def test_open_via_mask_inventory_rejects_missing_extra_shifted_size_shape_and_attributes(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        path.write_text(BOARD.replace('(tenting front back)', '(tenting)'))
        board = nets.read_board(path)
        directory = self.root / "gerbers"
        directory.mkdir()
        fake_gerbers(directory, board)
        m.validate_gerbers(directory, board)
        flash = "X30000000Y-20000000D03*"
        for layer in ("F.Mask", "B.Mask"):
            path = directory / m.LAYERS[layer][0]
            original = path.read_text()
            for name, changed in (
                    ("missing", original.replace(flash + "\n", "")),
                    ("duplicate", original.replace(flash, flash + "\n" + flash)),
                    ("extra", original.replace(flash, flash + "\nX50000000Y-10000000D03*")),
                    ("shifted", original.replace(flash, "X30010000Y-20000000D03*")),
                    ("radius", original.replace("C,1.800000", "C,2.000000")),
                    ("shape", original.replace("C,1.800000", "R,1.800000X1.800000")),
                    ("reference", original.replace(flash, "%TO.C,VIA*%\n" + flash)),
                    ("pin", original.replace(flash, "%TO.P,R1,1*%\n" + flash)),
                    ("net", original.replace(flash, "%TO.N,POWER*%\n" + flash))):
                self.assertNotEqual(changed, original, name)
                path.write_text(changed)
                with self.subTest(layer=layer, defect=name), self.assertRaisesRegex(nets.VerificationError, "aperture inventory"):
                    m.validate_gerbers(directory, board)
            path.write_text(original)
        # No unreferenced mask/paste flash is exempt, even at a real but tented via.
        path = self.root / "pcb" / "pcb.kicad_pcb"
        path.write_text(BOARD)
        board = nets.read_board(path)
        fake_gerbers(directory, board)
        for layer in ("F.Mask", "B.Mask", "F.Paste"):
            path = directory / m.LAYERS[layer][0]
            original = path.read_text()
            path.write_text(original.replace("M02*", "%TD*%\n%ADD99C,1.800000*%\nD99*\n" + flash + "\nM02*"))
            with self.subTest(layer=layer), self.assertRaisesRegex(nets.VerificationError, "Extra/wrong"):
                m.validate_gerbers(directory, board)
            path.write_text(original)

    def test_via_mask_group_exception_is_source_net_and_layer_bound(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        directory = self.root / "gerbers"
        directory.mkdir()
        cases = ((31.5, 1, "", .2, None), (31.5, 2, "", .2, "F.Mask"),
                 (31.5, 1, "(tenting front)", .2, "F.Mask"), (31.5, 1, "(tenting back)", .2, "B.Mask"),
                 (32, 1, "", .7, "F.Mask"))
        for x, net, flags, margin, failure in cases:
            with self.subTest(x=x, net=net, flags=flags, margin=margin):
                source = BOARD.replace('(pad_to_mask_clearance 0) (tenting front back)',
                                       f'(pad_to_mask_clearance {margin}) (tenting)')
                extra = f'(via (at {x} 20) (size 1.8) (drill 1) (layers "F.Cu" "B.Cu") (net {net}) {flags})'
                path.write_text(source.rstrip()[:-1] + extra + ")\n")
                board = nets.read_board(path)
                fake_gerbers(directory, board)
                if failure:
                    with self.assertRaisesRegex(nets.VerificationError, failure + ".*exposes via hole"):
                        m.validate_gerbers(directory, board)
                else:
                    m.validate_gerbers(directory, board)

    def test_untented_vias_still_reject_component_mask_and_paste_collisions(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        directory = self.root / "gerbers"
        directory.mkdir()
        for flags in ("(tenting)", "(tenting front)", "(tenting back)", "(tenting front back)"):
            for layer in ("F.Mask", "B.Mask", "F.Paste"):
                with self.subTest(flags=flags, layer=layer):
                    source = BOARD.replace('(tenting front back)', flags)
                    if layer == "B.Mask":
                        source = source.replace('(via (at 30 20)', '(via (at 8.5 20)')
                        source = source.replace('(layers "*.Cu" "*.Mask")', '(layers "*.Cu" "B.Mask")', 1)
                    else:
                        source = source.replace('(via (at 30 20)', '(via (at 19 30)')
                        if layer == "F.Paste":
                            source = source.replace('(layers "F.Cu" "F.Mask" "F.Paste")', '(layers "F.Cu" "F.Paste")', 1)
                    path.write_text(source)
                    board = nets.read_board(path)
                    fake_gerbers(directory, board)
                    with self.assertRaisesRegex(nets.VerificationError, layer + ".*exposes via hole"):
                        m.validate_gerbers(directory, board)

    def test_nonzero_mask_minimum_width_remains_unsupported_for_open_vias(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        path.write_text(BOARD.replace('(tenting front back)', '(tenting) (solder_mask_min_width 0.1)'))
        board = nets.read_board(path)
        directory = self.root / "gerbers"
        directory.mkdir()
        fake_gerbers(directory, board)
        with self.assertRaisesRegex(nets.VerificationError, "Merged/polygonal solder mask"):
            m.validate_gerbers(directory, board)

    def test_assembly_reference_excludes_nonpopulated_parts_and_requests_native_pad_overlay(self):
        rc, pipeline, fake = self.execute("check")
        self.assertEqual(rc, 0, pipeline.errors)
        text = (pipeline.run / "release" / "Assembly.txt").read_text()
        self.assertIn("DRAFT: not an accepted JLCPCB placement model or production approval.", text)
        self.assertIn("Population: 3 components; 2 SMT / 1 THT.", text)
        self.assertNotIn("PR02", text)
        self.assertIn("R1 | R1K | Local:THT | 10.000000 | 20.000000 | 10.000000 | -20.000000 | 0.000000 | top", text)
        self.assertIn("R1 | 1 | POWER | thru_hole | 8.500000 | 20.000000 | 8.500000 | -20.000000 | 1.000000", text)
        for ref in ("H1", "R_DNP", "VIA"):
            self.assertNotRegex(text, rf"(?m)^{ref} \|")
        command = next(command for command in fake.calls if "pdf" in command)
        self.assertEqual(command[command.index("--layers") + 1], "F.Fab,F.SilkS,F.CrtYd,Edge.Cuts")
        self.assertIn("--sketch-pads-on-fab-layers", command)

    def test_real_assembly_datums_preserve_all_hybrid_terminals_and_unusual_axes(self):
        board = nets.read_board(REPO / "pcb" / "pcb.kicad_pcb")
        path = self.root / "native-pos.csv"
        path.write_text(native_positions(board))
        positions = m.check_placement(m.read_csv(path, m.POSITION_FIELDS), board, native=True)
        bom = m.read_bom(REPO / "pcb" / "BOM.csv")
        for ref in ("R1", "R2"):
            for key, expected in {"MPN": "PS122WF2201T4E", "Manufacturer": "Uni-Royal",
                                  "LCSC Part #": "C2793873", "Sourcing": "LCSC", "Sourcing Reference": ""}.items():
                self.assertEqual(bom[ref][key], expected)
        text = m.assembly_reference(board, bom, positions, "1.2.0-dev")
        anchors, terminals = text.split("TERMINAL DATUMS\n")
        self.assertIn("Population: 16 components; 8 SMT / 8 THT.", anchors)
        self.assertEqual(sum(line.startswith(tuple(ref + " | " for ref in bom)) for line in anchors.splitlines()), 16)
        rows = [line.split(" | ") for line in terminals.splitlines() if " | " in line][1:]
        self.assertEqual(len(rows), 34)
        self.assertEqual({(row[0], row[1], row[2]) for row in rows},
                         {(ref, pin, net) for net, pins in board.nets.items() for ref, pin in pins})
        expected = {
            ("J_LED_A", "1"): ("LED_A_POS", 142.96, 103.0, 2.0),
            ("J_LED_C", "1"): ("LED_C_POS", 142.96, 142.0, 2.0),
            ("J_LED_A", "2"): ("WIRE_B", 148.04, 103.0, 2.0),
            ("J_LED_C", "2"): ("WIRE_B", 148.04, 142.0, 2.0),
            ("D1", "1"): ("LED_A_POS", 132.9, 104.5, 0),
            ("D2", "1"): ("LED_C_POS", 132.9, 140.5, 0),
            ("D3", "1"): ("LED_A_POS", 132.9, 99.0, 0),
            ("D4", "1"): ("LED_C_POS", 132.9, 146.0, 0),
            ("GDT_AC", "1"): ("WIRE_A", 125.8, 114.88, 1.4),
            ("GDT_AC", "2"): ("WIRE_C", 125.8, 130.12, 1.4),
        }
        expected.update({(ref, pad.pin): (pad.net, pad.x, pad.y, pad.drill)
                         for ref in ("R1", "R2") for pad in board.footprints[ref].pads})
        for row in rows:
            key = (row[0], row[1])
            if key in expected:
                with self.subTest(terminal=key):
                    net, x, y, drill = expected[key]
                    self.assertEqual(row[2], net)
                    self.assertEqual(tuple(map(float, row[4:])), (x, y, x, -y, drill))
        self.assertIn("PS122WF2201T4E", anchors)
        self.assertIn("Footprint anchors and terminal centres are NOT measured package centroids.", text)

    def test_via_treatment_csv_reports_source_requested_front_and_back(self):
        path = self.root / "pcb" / "pcb.kicad_pcb"
        for global_flags, local_flags, expected in (
                ("(tenting front back)", "", ("yes", "yes")), ("(tenting)", "", ("no", "no")),
                ("(tenting front)", "", ("yes", "no")), ("(tenting back)", "", ("no", "yes")),
                ("(tenting front back)", "(tenting)", ("no", "no")),
                ("(tenting front back)", "(tenting back)", ("no", "yes")),
                ("(tenting)", "(tenting front)", ("yes", "no"))):
            with self.subTest(global_flags=global_flags, local_flags=local_flags):
                source = BOARD.replace('(tenting front back)', global_flags)
                path.write_text(source.replace('(via (at 30 20)', f'(via {local_flags} (at 30 20)'))
                rc, pipeline, _ = self.execute("check")
                self.assertEqual(rc, 0, pipeline.errors)
                rows = m.read_csv(pipeline.run / "release" / "ViaTreatment.csv",
                                  ("Requested front tented", "Requested back tented", "Treatment"))
                self.assertEqual(len(rows), 1)
                row = rows[0]
                self.assertEqual((row["Requested front tented"], row["Requested back tented"]), expected)
                self.assertEqual((row["Function"], row["Net"]), ("Stitching via", "POWER"))
                self.assertEqual(tuple(float(row[key]) for key in ("PCB X mm", "PCB Y mm", "Drill mm", "Pad mm")),
                                 (30, 20, 1, 1.8))
                self.assertEqual(row["Treatment"].startswith("Standard untented"), expected == ("no", "no"))
                self.assertIn("no fill; preserve diameters; CAM acceptance not established", row["Treatment"])

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
    return ["all", "package", "release", "production", "gerbers", "prototype", "drills", "ipc", "bom", "cpl",
            "zip-gerbers", "zip-flytest", "check"]


@unittest.skipUnless(os.environ.get("KICAD_TEST_CLI"), "Set KICAD_TEST_CLI for isolated native CLI fixture probes")
class NativeContractTests(unittest.TestCase):
    def test_native_current_source_fabrication_inventory(self):
        parent = REPO / "tmp" / "native-manufacturing-tests"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="native-current-source-", dir=parent, delete=False) as temporary:
            root = Path(temporary)
            project = root / "pcb"
            project.mkdir()
            hashes = {}
            for name in ("pcb.kicad_pcb", "pcb.kicad_pro", "pcb.kicad_dru"):
                source = REPO / "pcb" / name
                hashes[name] = m.sha256(source)
                shutil.copy2(source, project / name)
                self.assertEqual(m.sha256(project / name), hashes[name])
            pcb = project / "pcb.kicad_pcb"
            board = nets.read_board(pcb)
            gerbers, drills = root / "gerbers", root / "drills"
            gerbers.mkdir()
            drills.mkdir()
            jobs = [
                ["pcb", "export", "gerbers", "--layers", ",".join(m.LAYERS), "--precision", "6", "--no-protel-ext",
                 "--subtract-soldermask", "--output", str(gerbers) + "/", str(pcb)],
                ["pcb", "export", "drill", "--format", "excellon", "--drill-origin", "absolute", "--excellon-units", "mm",
                 "--excellon-zeros-format", "decimal", "--excellon-separate-th", "--output", str(drills) + "/", str(pcb)],
            ]
            for args in jobs:
                command = [os.environ["KICAD_TEST_CLI"], *args]
                result = subprocess.run(command, cwd=project, capture_output=True, text=True, timeout=120)
                m.write_json(root / f"{args[2]}-command.json", {"command": command, "returncode": result.returncode,
                                                              "stdout": result.stdout, "stderr": result.stderr})
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(re.sub(m.WX_IMAGE_DEBUG, "", result.stderr), "")
                self.assertIsNone(re.search(r"(?im)^\s*(?:warning|error)\b", result.stdout))
            checked = {"source_hashes": hashes, "gerbers": m.validate_gerbers(gerbers, board),
                       "drills": {name: m.validate_drill(drills / name, board, name == "pcb-PTH.drl")
                                  for name in sorted(m.DRILLS)}}
            for name, digest in hashes.items():
                self.assertEqual(m.sha256(project / name), digest)
            vias = m.via_mask_settings(board)
            self.assertEqual(len(vias), 14)
            self.assertTrue(all(settings == (False, False, .9) for settings in vias.values()))
            checked["via_mask_openings"] = {}
            for layer in ("F.Mask", "B.Mask"):
                flashes = m.parse_gerber(gerbers / m.LAYERS[layer][0], m.LAYERS[layer][1])[0]
                checked["via_mask_openings"][layer] = [f for f in flashes if not f[6]]
                self.assertEqual(len(checked["via_mask_openings"][layer]), 14)
            m.write_json(root / "validated.json", checked)

    def test_native_via_mask_flags_inheritance_margins_and_overlapping_flashes(self):
        parent = REPO / "tmp" / "native-manufacturing-tests"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="native-via-mask-", dir=parent, delete=False) as temporary:
            root = Path(temporary)
            cases = (("", 0, True, True), ("(tenting)", 0, False, False),
                     ("(tenting front)", 0, True, False), ("(tenting back)", 0, False, True),
                     ("(tenting front back)", 0, True, True), ("(tenting none)", 0, False, False),
                     ("(tenting)", .2, False, False), ("(tenting)", -.1, False, False))
            for index, (flags, margin, front, back) in enumerate(cases):
                with self.subTest(flags=flags, margin=margin):
                    case = root / str(index)
                    case.mkdir()
                    make_project(case)
                    project = case / "pcb"
                    pcb = project / "pcb.kicad_pcb"
                    # Three 1.8 mm annuli on 1.5 mm pitch deliberately overlap.
                    # A local flat flag list overrides BOTH sides, not only named sides.
                    vias = ((30, "", front, back), (31.5, "", front, back), (33, "", front, back),
                            (36, "(tenting)", False, False), (39, "(tenting front)", True, False),
                            (42, "(tenting back)", False, True), (45, "(tenting front back)", True, True),
                            (48, "(tenting none)", False, False))
                    source = BOARD.replace('(pad_to_mask_clearance 0) (tenting front back)',
                                           f'(pad_to_mask_clearance {margin}) (solder_mask_min_width 0) {flags}')
                    source = source.replace(
                        '(via (at 30 20) (size 1.8) (drill 1.0) (layers "F.Cu" "B.Cu") (net 1))',
                        "\n".join(f'(via (at {x} 20) (size 1.8) (drill 1.0) '
                                  f'(layers "F.Cu" "B.Cu") (net 1) {override})'
                                  for x, override, _, _ in vias))
                    pcb.write_text(source, encoding="utf-8")
                    directory = case / "gerbers"
                    directory.mkdir()
                    command = [os.environ["KICAD_TEST_CLI"], "pcb", "export", "gerbers",
                               "--layers", ",".join(m.LAYERS), "--precision", "6", "--no-protel-ext",
                               "--subtract-soldermask", "--output", str(directory) + "/", str(pcb)]
                    result = subprocess.run(command, cwd=project, capture_output=True, text=True, timeout=120)
                    m.write_json(case / "native-command.json", {"command": command, "returncode": result.returncode,
                                                               "stdout": result.stdout, "stderr": result.stderr})
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertEqual(re.sub(m.WX_IMAGE_DEBUG, "", result.stderr), "")
                    self.assertIsNone(re.search(r"(?im)^\s*(?:warning|error)\b", result.stdout))
                    for side, layer in enumerate(("F.Mask", "B.Mask"), 2):
                        filename, function = m.LAYERS[layer]
                        flashes, segments = m.parse_gerber(directory / filename, function)
                        actual = [f for f in flashes if not f[6]]
                        expected = [(v[0], -20, 1.8 + 2 * margin, 1.8 + 2 * margin, "C", 0, "", "", "")
                                    for v in vias if not v[side]]
                        self.assertEqual(segments, [])
                        m.match_geometry(actual, expected, .000002, layer + " native via mask contract")
                    m.validate_gerbers(directory, nets.read_board(pcb))

    def test_native_via_mask_rejects_non_native_overrides(self):
        parent = REPO / "tmp" / "native-manufacturing-tests"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="native-via-syntax-", dir=parent, delete=False) as temporary:
            root = Path(temporary)
            cases = (("", 0), ("(tenting (front no) (back yes))", 3), ("(solder_mask_margin 0.2)", 3))
            for index, (override, status) in enumerate(cases):
                with self.subTest(override=override):
                    case = root / str(index)
                    case.mkdir()
                    make_project(case)
                    project = case / "pcb"
                    pcb = project / "pcb.kicad_pcb"
                    pcb.write_text(BOARD.replace('(via (at 30 20)', f'(via {override} (at 30 20)'), encoding="utf-8")
                    command = [os.environ["KICAD_TEST_CLI"], "pcb", "export", "gerbers", "--layers", "F.Mask,B.Mask",
                               "--output", str(case / "gerbers") + "/", str(pcb)]
                    result = subprocess.run(command, cwd=project, capture_output=True, text=True, timeout=120)
                    m.write_json(case / "native-command.json", {"command": command, "returncode": result.returncode,
                                                               "stdout": result.stdout, "stderr": result.stderr})
                    self.assertEqual(result.returncode, status, result.stdout + result.stderr)

    def test_native_roundrect_and_rect_margins(self):
        parent = REPO / "tmp" / "native-manufacturing-tests"
        parent.mkdir(parents=True, exist_ok=True)
        cases = (
            ("roundrect", .25, .2, .1, .1, ((1, 2, .25), (1.4, 2.4, .35), (1.4, 2.6, .35))),
            ("roundrect", .25, -.1, -.1, -.1, ((1, 2, .25), (.8, 1.8, .2), (.6, 1.4, .15))),
            ("rect", .25, .2, .1, .1, ((1, 2, 0), (1.4, 2.4, .2), (1.4, 2.6, .3))),
            ("rect", .25, -.1, -.1, -.1, ((1, 2, 0), (.8, 1.8, 0), (.6, 1.4, 0))),
            ("roundrect", .5, 0, 0, 0, ((1.00002, 2, .5),) * 3),
            ("roundrect", 0, 0, 0, 0, ((1, 2, 0),) * 3),
        )
        with tempfile.TemporaryDirectory(prefix="native-corners-", dir=parent, delete=False) as temporary:
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
        parent = REPO / "tmp" / "native-manufacturing-tests"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="native-unary-rule-", dir=parent, delete=False) as temporary:
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
        parent = REPO / "tmp" / "native-manufacturing-tests"
        parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="native-contract-", dir=parent, delete=False) as temporary:
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
                ["pcb", "export", "pdf", "--layers", "F.Fab,F.SilkS,F.CrtYd,Edge.Cuts", "--mode-single", "--black-and-white",
                 "--sketch-pads-on-fab-layers",
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
