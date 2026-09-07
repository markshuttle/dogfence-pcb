import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from pcb import sync_libraries as sync
from scripts import compare_nets as nets
from scripts import manufacturing as m
from scripts import review_annotation as review
from test_compare_nets import xml_netlist
from test_manufacturing import make_project


REPO = Path(__file__).resolve().parents[1]


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "pcb.kicad_sch"
        self.original = sync.parse((REPO / "pcb/pcb.kicad_sch").read_text(encoding="utf-8"))

    def validate(self, tree):
        self.path.write_text(sync.format_node(tree) + "\n", encoding="utf-8")
        return review.validate_references(self.path)

    def test_current_hybrid_reference_and_board_inventory(self):
        refs = self.validate(self.original)
        board = nets.read_board(REPO / "pcb/pcb.kicad_pcb")
        self.assertEqual(len(refs), 20)
        self.assertEqual(set(refs), set(board.footprints))
        self.assertEqual((len(board.nets), sum(map(len, board.nets.values()))), (8, 34))
        self.assertEqual(sum(fp.populated for fp in board.footprints.values()), 16)
        self.assertEqual(set(review.numbering_map(refs)), set(review.NUMBERED))

    def test_numbered_control_is_reversible_and_does_not_replace_other_text(self):
        symbol = sync.children(self.original, "symbol")[0]
        note = next(p for p in sync.children(symbol, "property") if json.loads(p[1]) == "Description")
        note[2] = json.dumps('J_IN J_LED_C GDT_AB "quoted" \\ escaped\ntext')
        original = copy.deepcopy(self.original)
        changed = review.rename_references(original, review.NUMBERED)
        refs = self.validate(changed)
        self.assertEqual(self.original, original)
        self.assertEqual(sync.parse(self.path.read_text(encoding="utf-8")), changed)
        self.assertTrue(set(review.NUMBERED.values()) <= set(refs))
        changed_note = next(p for p in sync.children(sync.children(changed, "symbol")[0], "property")
                            if json.loads(p[1]) == "Description")
        self.assertEqual(changed_note, note)
        for old, new in zip(sync.children(original, "symbol"), sync.children(changed, "symbol")):
            old_props = [p for p in sync.children(old, "property") if json.loads(p[1]) != "Reference"]
            new_props = [p for p in sync.children(new, "property") if json.loads(p[1]) != "Reference"]
            self.assertEqual(old_props, new_props)
        inverse = {new: old for old, new in review.NUMBERED.items()}
        self.assertEqual(review.rename_references(changed, inverse), original)

    def test_duplicate_unassigned_and_both_mismatch_directions_fail(self):
        cases = [({"D2": "D1"}, ("property", "instance"), "Duplicate source reference"),
                 ({"R2": "R?"}, ("property", "instance"), "Unassigned"),
                 ({"R2": ""}, ("property", "instance"), "Unassigned"),
                 ({"R2": "R_BAD"}, ("property", "instance"), "unexpected source reference"),
                 ({"R2": "R9"}, ("property",), "Property/instance"),
                 ({"R2": "R9"}, ("instance",), "Property/instance")]
        for mapping, locations, error in cases:
            with self.subTest(mapping=mapping, locations=locations), self.assertRaisesRegex(nets.VerificationError, error):
                self.validate(review.rename_references(self.original, mapping, locations))

    def test_missing_duplicate_or_wrong_reference_context_fails_closed(self):
        for defect in ("missing-property", "duplicate-property", "missing-instance", "duplicate-project",
                       "wrong-project", "wrong-path", "wrong-unit", "duplicate-uuid", "extra-sheet"):
            tree = copy.deepcopy(self.original)
            symbols = sync.children(tree, "symbol")
            symbol = symbols[0]
            prop = next(p for p in sync.children(symbol, "property") if json.loads(p[1]) == "Reference")
            instances = sync.child(symbol, "instances")
            project = sync.child(instances, "project")
            instance = sync.child(project, "path")
            if defect == "missing-property":
                symbol.remove(prop)
            elif defect == "duplicate-property":
                symbol.append(copy.deepcopy(prop))
            elif defect == "missing-instance":
                symbol.remove(instances)
            elif defect == "duplicate-project":
                instances.append(copy.deepcopy(project))
            elif defect == "wrong-project":
                project[1] = '"other"'
            elif defect == "wrong-path":
                instance[1] = '"/wrong"'
            elif defect == "wrong-unit":
                sync.child(instance, "unit")[1] = "2"
            elif defect == "duplicate-uuid":
                sync.child(symbol, "uuid")[1] = sync.child(symbols[1], "uuid")[1]
            else:
                tree.append(["sheet", ["uuid", '"extra"']])
            with self.subTest(defect=defect), self.assertRaises(nets.VerificationError):
                self.validate(tree)

    def test_control_refuses_changed_reference_set_collisions_and_missing_edits(self):
        refs = self.validate(self.original)
        for bad in (set(refs) - {"J_IN"}, set(refs) | {"R_BAD"}, set(refs) | {"J1"}):
            with self.subTest(refs=bad), self.assertRaises(nets.VerificationError):
                review.numbering_map(bad)
        with self.assertRaisesRegex(nets.VerificationError, "Missing mutation"):
            review.rename_references(self.original, {"MISSING": "X1"})


class ExportProofTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        make_project(self.root)
        self.xml = self.root / "schematic.xml"
        self.xml.write_text(xml_netlist(), encoding="utf-8")
        self.board = nets.read_board(self.root / "pcb/pcb.kicad_pcb")
        self.refs = set(self.board.footprints)
        self.bom = self.root / "pcb/BOM.csv"

    def test_numbering_preserves_full_component_contents_and_terminals(self):
        baseline = review.export_proof(self.xml, self.refs, self.board, self.bom)
        tree = nets.read_xml(self.xml)
        mapping = {"J_LED_A": "J1", "J_LED_C": "J2"}
        for node in [*tree.findall("components/comp"), *tree.findall("nets/net/node")]:
            node.set("ref", mapping.get(node.get("ref"), node.get("ref")))
        ET.ElementTree(tree).write(self.xml, encoding="utf-8")
        refs = {mapping.get(ref, ref) for ref in self.refs}
        proof = review.export_proof(self.xml, refs, self.board, self.bom, baseline,
                                    {new: old for old, new in mapping.items()})
        self.assertEqual(proof, baseline)
        self.assertEqual(proof["counts"]["terminals"], 8)
        with self.assertRaises(nets.VerificationError):
            review.export_proof(self.xml, refs, self.board, self.bom, baseline)

    def test_same_counts_wrong_membership_or_identity_do_not_pass(self):
        baseline = review.export_proof(self.xml, self.refs, self.board, self.bom)
        for defect in ("swap-pins", "missing-pin", "mpn", "footprint", "dnp", "source-ref", "full-content"):
            tree = ET.fromstring(xml_netlist())
            first = tree.find("components/comp")
            refs = self.refs
            if defect == "swap-pins":
                for node in tree.findall("nets/net/node"):
                    if node.get("ref") == "R1":
                        node.set("pin", "2" if node.get("pin") == "1" else "1")
            elif defect == "missing-pin":
                net = tree.find("nets/net")
                net.remove(net[0])
            elif defect == "mpn":
                first.find("fields/field[@name='MPN']").text = "WRONG"
            elif defect == "footprint":
                first.find("footprint").text = "Local:WRONG"
            elif defect == "dnp":
                ET.SubElement(first, "property", name="dnp")
            elif defect == "source-ref":
                refs = self.refs - {"H1"}
            else:
                ET.SubElement(first, "datasheet").text = "changed component content"
            ET.ElementTree(tree).write(self.xml, encoding="utf-8")
            with self.subTest(defect=defect), self.assertRaises(nets.VerificationError):
                review.export_proof(self.xml, refs, self.board, self.bom,
                                    baseline if defect == "full-content" else None)


class CommandTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.project.mkdir()

    def test_exact_diagnostic_contract_has_no_warning_or_stderr_suppression(self):
        good = {"returncode": 0, "stdout": review.WARNING, "stderr": ""}
        review.require_output(good, review.WARNING)
        review.require_output({**good, "stdout": ""}, "")
        for change in ({"returncode": 1}, {"stdout": ""}, {"stdout": review.WARNING + "\n"},
                       {"stdout": review.WARNING + "Warning: another issue\n"}, {"stderr": "\n"},
                       {"stderr": "Debug: unexpected\n"}, {"execution_error": "timeout"}):
            with self.subTest(change=change), self.assertRaises(nets.VerificationError):
                review.require_output({**good, **change}, review.WARNING)

    def test_cli_quoting_is_argv_safe(self):
        runner = review.NativeCommands(self.root, self.project, "'/path with spaces/kicad-cli' '$(not-a-shell)' ")

        def fake(command, **kwargs):
            self.assertEqual(command, ["/path with spaces/kicad-cli", "$(not-a-shell)", "--version"])
            self.assertFalse(kwargs.get("shell", False))
            self.assertTrue(kwargs["capture_output"])
            return subprocess.CompletedProcess(command, 0, b"9.0.7\n", b"")

        with patch.object(review.subprocess, "run", fake):
            runner.resolve_cli()
        self.assertEqual(runner.version, "9.0.7")
        review.require_output(runner.commands[0], "9.0.7\n")

    def test_default_resolution_retains_failed_probes_then_uses_snap(self):
        runner = review.NativeCommands(self.root, self.project, "")

        def fake(command, **kwargs):
            if command[0] != "/snap/bin/kicad.kicad-cli":
                raise FileNotFoundError(command[0])
            return subprocess.CompletedProcess(command, 0, b"9.0.7\n", b"")

        with patch.object(review.subprocess, "run", fake):
            runner.resolve_cli()
        self.assertEqual(runner.cli, ["/snap/bin/kicad.kicad-cli"])
        self.assertEqual(len(runner.commands), 3)
        for record in runner.commands[:2]:
            self.assertEqual((record["returncode"], record["stdout"], record["stderr"]), (-1, "", ""))
            self.assertIn("FileNotFoundError", record["execution_error"])

    def test_timeout_preserves_raw_partial_streams_and_separate_runner_error(self):
        runner = review.NativeCommands(self.root, self.project, "fake")

        def timeout(command, **kwargs):
            raise subprocess.TimeoutExpired(command, 120, output=b"actual partial\r\n", stderr=b"actual error\xff")

        with patch.object(review.subprocess, "run", timeout):
            result = runner.invoke(["fake", "--version"], "timeout")
        self.assertEqual((self.root / result["stdout_file"]).read_bytes(), b"actual partial\r\n")
        self.assertEqual((self.root / result["stderr_file"]).read_bytes(), b"actual error\xff")
        self.assertEqual(result["stdout"], "actual partial\r\n")
        self.assertIn("TimeoutExpired", result["execution_error"])
        self.assertEqual(json.loads((self.root / "commands.json").read_text()), [result])


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in review.source_hashes(REPO):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / name, target)

    def test_failed_native_review_is_private_unique_hash_bound_and_never_approves(self):
        before = review.source_hashes(self.root)
        runs = []
        with patch.object(review.subprocess, "run", side_effect=FileNotFoundError("missing CLI")), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            for _ in range(2):
                run, report = review.review(self.root, "missing-cli")
                runs.append(run)
                self.assertEqual(report["status"], "failed")
                self.assertEqual(report["source_hashes_before"], before)
                self.assertEqual(report["source_hashes_after"], before)
                self.assertEqual(set(report["review_input_hashes_before"]), review.REVIEW_INPUTS)
                self.assertEqual(report["review_input_hashes_after"], report["review_input_hashes_before"])
                self.assertEqual(review.tree_hashes(run / "snapshot"), before)
                self.assertEqual(json.loads((run / "report.json").read_text()), report)
                commands = json.loads((run / "commands.json").read_text())
                self.assertEqual(commands[0]["command"], ["missing-cli", "--version"])
                self.assertIn("FileNotFoundError", commands[0]["execution_error"])
                self.assertEqual(run.parent, self.root / "tmp/annotation-review")
                self.assertTrue(run.name.startswith("hybrid-"))
        self.assertNotEqual(*runs)
        self.assertEqual(review.source_hashes(self.root), before)
        self.assertFalse((self.root / "build").exists())
        self.assertFalse((self.root / "tmp/manufacturing").exists())

    def test_source_change_during_command_is_reported_even_when_native_fails(self):
        path = self.root / "pcb/pcb.kicad_sch"
        before = m.sha256(path)

        def mutate(command, **kwargs):
            path.write_bytes(path.read_bytes() + b"\n")
            raise FileNotFoundError("synthetic failure after source edit")

        with patch.object(review.subprocess, "run", mutate), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            _, report = review.review(self.root, "missing-cli")
        self.assertEqual(report["status"], "failed")
        self.assertFalse(report["sources_unchanged"])
        self.assertEqual(report["review_input_hashes_before"]["pcb/pcb.kicad_sch"], before)
        self.assertEqual(report["review_input_hashes_after"]["pcb/pcb.kicad_sch"], m.sha256(path))
        self.assertTrue(any("source bytes changed" in error for error in report["errors"]))


if __name__ == "__main__":
    unittest.main()
