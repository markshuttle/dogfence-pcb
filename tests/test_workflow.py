import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import verify_workflow as w
from test_manufacturing import FakeKiCad, make_project


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def make_attempt(self, held, target="all"):
        root = self.root / (target + ("-held" if held else "-published"))
        root.mkdir()
        make_project(root)
        for name in w.m.ENGINEERING_NOTES:
            (root / "pcb" / name).write_bytes(f"Synthetic {name}; not engineering evidence.\r\n".encode("ascii"))
        if held:
            path = root / "pcb/verification.json"
            review = w.m.read_json(path)
            review.update(release_holds=[{"id": key, "reason": "Synthetic qualification hold"}
                                         for key in ("C4", "C5", "W3", "W1", "W4")], file_release_review=None)
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
            self.assertEqual(pipeline.execute("prototype" if target == "prototype" else "build"),
                             1 if held and target == "all" else 0, pipeline.errors)
        return pipeline

    def test_all_release_notes_match_staged_sources_and_compare_exact_bytes(self):
        for target in ("all", "prototype"):
            for held in (True, False):
                with self.subTest(target=target, held=held):
                    pipeline = self.make_attempt(held, target)
                    result = w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review,
                                                2 if held and target == "all" else 0, target)
                    self.assertEqual(result["mode"], "prototype" if target == "prototype" else "build")
                    for name in (*w.m.ENGINEERING_NOTES, "verification.json"):
                        self.assertEqual(result["artifact_comparison_hashes"][name],
                                         w.m.sha256(pipeline.project / name), name)

    def test_missing_or_changed_release_note_is_rejected_with_holds(self):
        for target, returncode in (("all", 2), ("prototype", 0)):
            pipeline = self.make_attempt(True, target)
            w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, returncode, target)
            release = pipeline.run / "release" if target == "all" else pipeline.build
            for name in (*w.m.ENGINEERING_NOTES, "verification.json"):
                path = release / name
                original = path.read_bytes()
                for missing in (True, False):
                    with self.subTest(target=target, note=name, missing=missing):
                        try:
                            if missing:
                                path.unlink()
                            else:
                                path.write_bytes(original + b"\n" if name == "verification.json"
                                                 else original.replace(b"\r\n", b"\n"))
                            error = FileNotFoundError if missing else w.m.VerificationError
                            with self.assertRaisesRegex(error, name):
                                w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, returncode, target)
                        finally:
                            path.write_bytes(original)

    def test_changed_assembly_terminal_datum_is_rejected(self):
        for target, returncode in (("all", 2), ("prototype", 0)):
            pipeline = self.make_attempt(True, target)
            release = pipeline.run / "release" if target == "all" else pipeline.build
            path = release / "Assembly.txt"
            text = path.read_text()
            changed = text.replace("8.500000 | -20.000000 | 1.000000", "8.500000 | 20.000000 | 1.000000", 1)
            self.assertNotEqual(changed, text)
            path.write_text(changed)
            with self.subTest(target=target), self.assertRaisesRegex(w.m.VerificationError, "Assembly datum reference differs"):
                w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, returncode, target)

    def test_publication_mode_status_scope_and_hashes_cannot_be_changed(self):
        for target in ("all", "prototype"):
            pipeline = self.make_attempt(target == "prototype", target)
            w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, 0, target)
            other = "prototype" if target == "all" else "all"
            with self.assertRaisesRegex(w.m.VerificationError, "Unexpected build outcome"):
                w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, 0, other)
            for name, changes in (
                    ("manifest.json", {"mode": "production", "status": "verified" if target == "prototype" else "prototype",
                                       "publication": "Field approved", "scope": {}, "source_hashes": {},
                                       "artifact_hashes": {}, "verification": {}}),
                    ("status.json", {"mode": "production", "status": "verified" if target == "prototype" else "prototype",
                                     "publication": "Field approved", "requires_matching_manifest_for_upload": False,
                                     "required_manifest_status": "verified" if target == "prototype" else "prototype"})):
                path = pipeline.build / name
                original = w.m.read_json(path)
                for key, value in changes.items():
                    with self.subTest(target=target, file=name, key=key):
                        try:
                            w.m.write_json(path, {**original, key: value})
                            with self.assertRaises(w.m.VerificationError):
                                w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, 0, target)
                        finally:
                            w.m.write_json(path, original)

    def test_prototype_scope_marker_is_required_in_both_archives_and_matches_ledger(self):
        pipeline = self.make_attempt(True, "prototype")
        for path in (pipeline.run / "exports/README.txt", pipeline.build / "README.txt"):
            original = path.read_bytes()
            try:
                path.write_bytes(original.replace(b"PROTOTYPE ONLY", b"PRODUCTION APPROVED"))
                with self.assertRaisesRegex(w.m.VerificationError, "Package scope README differs"):
                    w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, 0, "prototype")
            finally:
                path.write_bytes(original)
        for name in ("Gerbers.zip", "FlyTest.zip"):
            path = pipeline.build / name
            original = path.read_bytes()
            with zipfile.ZipFile(io.BytesIO(original)) as archive:
                members = {name: archive.read(name) for name in archive.namelist()}
            for change in ("missing", "altered", "extra"):
                with self.subTest(archive=name, change=change):
                    try:
                        payload = members.copy()
                        if change == "missing":
                            payload.pop("README.txt")
                        elif change == "altered":
                            payload["README.txt"] = b"Production approved; no holds.\n"
                        else:
                            payload["unexpected.txt"] = b"unreviewed"
                        with zipfile.ZipFile(path, "w") as archive:
                            for member, data in payload.items():
                                archive.writestr(member, data)
                        with self.assertRaisesRegex(w.m.VerificationError, "ZIP"):
                            w.validate_attempt(pipeline.root, pipeline.sources, pipeline.review, 0, "prototype")
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
        for target in ("all", "prototype"):
            with self.subTest(target=target), patch.object(w, "__file__", str(script)), \
                    patch.object(w.m, "source_inventory", return_value={}), \
                    patch.object(w.sys, "argv", [str(script), "--expect-holds", "WRONG", "--target", target]), \
                    patch.dict(w.os.environ, {"MAKEFLAGS": "", "MFLAGS": "", "MAKEFILES": ""}), \
                    patch.object(w.subprocess, "run") as execute, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(w.main(), 1)
                execute.assert_not_called()
        for path in (self.root / "tmp/workflow-validation").glob("run-*/report.json"):
            report = w.m.read_json(path)
            self.assertEqual(report["status"], "failed")
            self.assertIn("Unexpected release hold IDs", report["error"])
            self.assertEqual(report["commands"], [])

    def test_target_drives_serial_parallel_commands_and_publication_outcome(self):
        script = self.root / "scripts/verify_workflow.py"
        script.parent.mkdir()
        script.write_text("# Isolated runner-control fixture, not a release.\n", encoding="ascii")
        review = {"release_holds": [{"id": "C4", "reason": "Synthetic qualification hold"}]}
        for target in ("all", "prototype"):
            def invoke(command, **kwargs):
                return w.subprocess.CompletedProcess(command, 2 if command[-1] == "all" else 0)

            with self.subTest(target=target), patch.object(w, "__file__", str(script)), \
                    patch.object(w.sys, "argv", [str(script), "--expect-holds", "C4", "--target", target]), \
                    patch.dict(w.os.environ, {"MAKEFLAGS": "", "MFLAGS": "", "MAKEFILES": ""}), \
                    patch.object(w.m, "source_inventory", return_value={}), patch.object(w.m, "read_json", return_value=review), \
                    patch.object(w, "inventory", return_value={}), patch.object(w, "preserve", return_value={}), \
                    patch.object(w, "validate_attempt", return_value={}) as validate, \
                    patch.object(w.subprocess, "run", side_effect=invoke) as execute, contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(w.main(), 0)
                self.assertEqual([call.args[0] for call in execute.call_args_list],
                                 [["make", "clean"], ["make", target], ["make", "clean"], ["make", "-j4", target]])
                self.assertEqual([call.args[-1] for call in validate.call_args_list], [target, target])
        for path in (self.root / "tmp/workflow-validation").glob("run-*/report.json"):
            report = w.m.read_json(path)
            expected = "expected publication refusal" if report["target"] == "all" else w.m.PUBLICATION["prototype"]
            self.assertEqual(report["publication"], expected)
