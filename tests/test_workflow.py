import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import verify_workflow as w
from test_manufacturing import FakeKiCad, make_project


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_attempt(self, held):
        root = self.root / ("held" if held else "published")
        root.mkdir()
        make_project(root)
        for name in w.m.ENGINEERING_NOTES:
            (root / "pcb" / name).write_bytes(f"Synthetic {name}; not engineering evidence.\r\n".encode("ascii"))
        if held:
            path = root / "pcb/verification.json"
            review = w.m.read_json(path)
            review.update(release_holds=[{"id": "TEST", "reason": "Synthetic hold"}], file_release_review=None)
            w.m.write_json(path, review)
        fake = FakeKiCad()

        def invoke(command, **kwargs):
            result = fake(command, **kwargs)
            if "--output" not in command:
                return result
            output = Path(command[command.index("--output") + 1])
            # Supply workflow metadata absent from the simpler exporter fixture.
            if any(Path(arg).name == "check_geometry.py" for arg in command):
                data = w.m.read_json(output)
                for key in ("pcb", "project", "rules"):
                    data["inputs"][key]["path"] = command[command.index("--" + key) + 1]
                data["measurements"] = {"via_apertures": []}
                w.m.write_json(output, data)
            elif "gerbers" in command:
                for path in output.glob("*.gbr"):
                    path.write_text("%TF.CreationDate,2026-09-07T01:02:03+01:00*%\n"
                                    "G04 Created by KiCad (PCBNEW 9.0.7) date 2026-09-07 01:02:03*\n"
                                    + path.read_text(encoding="utf-8"), encoding="utf-8")
            elif "drill" in command:
                for path in output.glob("*.drl"):
                    path.write_text(path.read_text(encoding="ascii").replace(
                        "M48\n", "M48\n; DRILL file {KiCad 9.0.7} date 2026-09-07T01:02:03+0100\n"
                        "; #@! TF.CreationDate,2026-09-07T01:02:03+01:00\n", 1), encoding="ascii")
            return result

        pipeline = w.m.Manufacturing(root, "fake-kicad")
        with patch.object(w.m.subprocess, "run", invoke), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(pipeline.execute("build"), 1 if held else 0, pipeline.errors)
        return pipeline

    def test_all_release_notes_match_staged_sources_and_compare_exact_bytes(self):
        for held in (True, False):
            with self.subTest(held=held):
                pipeline = self.make_attempt(held)
                result = w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, 2 if held else 0)
                for name in w.m.ENGINEERING_NOTES:
                    self.assertEqual(result["artifact_comparison_hashes"][name],
                                     w.m.sha256(pipeline.project / name), name)

    def test_missing_or_changed_release_note_is_rejected_with_holds(self):
        pipeline = self.make_attempt(True)
        w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, 2)
        for name in w.m.ENGINEERING_NOTES:
            path = pipeline.run / "release" / name
            original = path.read_bytes()
            for missing in (True, False):
                with self.subTest(note=name, missing=missing):
                    try:
                        if missing:
                            path.unlink()
                        else:
                            path.write_bytes(original.replace(b"\r\n", b"\n"))
                        error = FileNotFoundError if missing else w.m.VerificationError
                        with self.assertRaisesRegex(error, name):
                            w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, 2)
                    finally:
                        path.write_bytes(original)

    def test_only_recognized_timestamps_are_normalized(self):
        fixtures = {
            "test.gbr": "%TF.CreationDate,2026-09-07T01:02:03+01:00*%\n"
                        "G04 Created by KiCad (PCBNEW 9.0.7) date 2026-09-07 01:02:03*\nX1Y2D03*\n",
            "test.drl": "; DRILL file {KiCad 9.0.7} date 2026-09-07T01:02:03+0100\n"
                        "; #@! TF.CreationDate,2026-09-07T01:02:03+01:00\nX1Y2\n",
        }
        for name, text in fixtures.items():
            path = self.root / name
            path.write_text(text, encoding="ascii")
            original = w.comparison_hash(path)
            path.write_text(text.replace("01:02:03", "04:05:06"), encoding="ascii")
            self.assertEqual(w.comparison_hash(path), original)
            for old, new in (("X1Y2", "X1Y3"), ("9.0.7", "9.0.8")):
                path.write_text(text.replace(old, new), encoding="ascii")
                self.assertNotEqual(w.comparison_hash(path), original)
            path.write_text(text + text, encoding="ascii")
            with self.assertRaisesRegex(w.m.VerificationError, "one recognized"):
                w.comparison_hash(path)

    def test_other_artifacts_are_byte_exact(self):
        path = self.root / "CPL.csv"
        path.write_bytes(b"J_LED_A,145.5,-103\n")
        self.assertEqual(w.comparison_hash(path), w.m.sha256(path))
        original = w.comparison_hash(path)
        path.write_bytes(b"J_LED_A,145.5,103\n")
        self.assertNotEqual(w.comparison_hash(path), original)

    def test_geometry_row_order_is_not_measurement_but_every_value_and_duplicate_is(self):
        data = {"inputs": {key: {"path": "/old/" + key, "sha256": key} for key in ("pcb", "project", "rules")},
                "measurements": {"via_apertures": [{"layer": "F.Mask", "hole_gap_mm": 0.9},
                                                  {"layer": "F.Paste", "hole_gap_mm": 0.9}]}}
        expected = w.geometry_comparison(copy.deepcopy(data))
        reversed_rows = copy.deepcopy(data)
        reversed_rows["measurements"]["via_apertures"].reverse()
        reversed_rows["inputs"]["pcb"]["path"] = "/new/pcb"
        self.assertEqual(w.geometry_comparison(reversed_rows), expected)
        for change in ("value", "duplicate", "hash"):
            changed = copy.deepcopy(data)
            rows = changed["measurements"]["via_apertures"]
            if change == "value":
                rows[0]["hole_gap_mm"] = 0.8
            elif change == "duplicate":
                rows.append(rows[0].copy())
            else:
                changed["inputs"]["pcb"]["sha256"] = "different"
            self.assertNotEqual(w.geometry_comparison(changed), expected)

    def test_preserves_every_owned_tree_and_link_without_following_it(self):
        for name in ("build/reports/result.json", "pcb/Gerbers.zip", "pcb/CPL.csv",
                     "tmp/manufacturing/runs/old/project/pcb.kicad_pcb"):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(name, encoding="ascii")
        (self.root / "build/empty").mkdir()
        (self.root / "build/dangling").symlink_to("absent")
        destination = self.root / "saved"
        before = w.preserve(self.root, destination)
        for name in w.OWNED:
            self.assertEqual(before[name], w.inventory(self.root / name))
            self.assertEqual(before[name], w.inventory(destination / name))
        self.assertTrue((destination / "build/dangling").is_symlink())
        self.assertTrue((destination / "build/empty").is_dir())

    def test_preservation_error_prevents_success(self):
        source = self.root / "pcb/CPL.csv"
        source.parent.mkdir()
        source.write_text("original", encoding="ascii")
        original_copy = w.shutil.copy2

        def corrupt(source, target, **kwargs):
            original_copy(source, target, **kwargs)
            target.write_text("corrupt", encoding="ascii")

        with patch.object(w.shutil, "copy2", corrupt), self.assertRaisesRegex(w.m.VerificationError, "Preservation mismatch"):
            w.preserve(self.root, self.root / "saved")
        self.assertEqual(source.read_text(encoding="ascii"), "original")

    def test_unrelated_inventory_excludes_only_exact_owned_subtree(self):
        owned, unrelated = self.root / "runs", self.root / "layout-review"
        owned.mkdir()
        unrelated.mkdir()
        evidence = unrelated / "evidence.txt"
        evidence.write_text("retain", encoding="ascii")
        before = w.inventory(self.root, (owned,))
        (owned / "new").write_text("ignored", encoding="ascii")
        self.assertEqual(before, w.inventory(self.root, (owned,)))
        evidence.write_text("changed", encoding="ascii")
        self.assertNotEqual(before, w.inventory(self.root, (owned,)))

    def test_unexpected_holds_return_failure_without_running_clean(self):
        script = self.root / "scripts/verify_workflow.py"
        script.parent.mkdir()
        script.write_text("# Isolated runner-control fixture, not a release.\n", encoding="ascii")
        (self.root / "pcb").mkdir()
        w.m.write_json(self.root / "pcb/verification.json", {"release_holds": [{"id": "C4", "reason": "Open"}]})
        with patch.object(w, "__file__", str(script)), patch.object(w.m, "source_inventory", return_value={}), \
                patch.object(w.sys, "argv", [str(script), "--expect-holds", "WRONG"]), \
                patch.dict(w.os.environ, {"MAKEFLAGS": "", "MFLAGS": "", "MAKEFILES": ""}), \
                patch.object(w.subprocess, "run") as execute, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(w.main(), 1)
            execute.assert_not_called()
        report = w.m.read_json(next((self.root / "tmp/workflow-validation").glob("run-*/report.json")))
        self.assertEqual(report["status"], "failed")
        self.assertIn("Unexpected release hold IDs", report["error"])
        self.assertEqual(report["commands"], [])
