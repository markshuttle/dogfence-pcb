"""Controlled mutations of the authoritative PCB, never tmp/ or backup fixtures.

Full-board positives use the current 16-part CAD. Historical W1 geometry is
restored explicitly; aperture-only fixtures exercise the parser/distance model,
not an exemption from the current untented-via or SMA design guards.
Run: python3 -B -m unittest discover -s tests -p test_geometry.py -v
"""

from copy import deepcopy
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.check_geometry import (  # noqa: E402
    COMPONENT_HOLE_MINIMA, CU, GeometryCheck, MIN_MASK_BARRIER, PROJECT_MINIMA, PROTECTED_VIAS,
    REQUIRED_ERROR_RULES, REQUIRED_VISIBLE_RULES, Shape, check_sources,
    condition, matches, move, pad_shape,
)
from scripts.kicad_sexpr import Atom, Node, SExprError, parse, parse_many  # noqa: E402


RULES = """(version 1)
# Names do not constitute proof of rule coverage.
(rule "component PTH ring"
  (condition "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'")
  (constraint annular_width (min 0.254mm)))
(rule "earth separation"
  (condition "(A.NetName == 'EARTH' && B.NetCode != 0 && B.NetName != 'EARTH') || (B.NetName == 'EARTH' && A.NetCode != 0 && A.NetName != 'EARTH')")
  (constraint clearance (min 3.0mm)))
"""


def dump(node):
    if isinstance(node, Node):
        return "(" + node.tag + " " + " ".join(dump(v) for v in node.values) + ")"
    if isinstance(node, Atom) and not node.quoted:
        return str(node)
    # KiCad uses literal UTF-8 strings, not JSON's \uXXXX escapes.
    return json.dumps(str(node), ensure_ascii=False)


def replace(node, text):
    new = parse(text)
    node.values = [v for v in node.values if not isinstance(v, Node) or v.tag != new.tag]
    node.values.append(new)
    return new


def remove(node, tag):
    node.values = [v for v in node.values if not isinstance(v, Node) or v.tag != tag]


def footprint(board, ref):
    return next(fp for fp in board.children("footprint") if any(
        p.values[:2] == ["Reference", ref] for p in fp.children("property")))


def pad(board, ref, num):
    return next(p for p in footprint(board, ref).children("pad") if p.values[0] == num)


def set_net(board, node, name):
    code = next(n.values[0] for n in board.children("net") if n.values[1] == name)
    replace(node, f'(net {code} "{name}")')


def historical_smt(board, *, land_height=2):
    setup = board.one("setup")
    replace(setup, "(tenting front back)")
    for key in ("pad_to_mask_clearance", "pad_to_paste_clearance", "pad_to_paste_clearance_ratio"):
        replace(setup, f"({key} 0)")
    replace(setup, "(solder_mask_min_width 0)")
    for ref, y in (("GDT_AB", 118.69), ("GDT_BC", 126.31)):
        fp = footprint(board, ref)
        replace(fp, f"(at 114 {y})")
        for key in ("solder_mask_margin", "solder_paste_margin", "solder_paste_ratio", "solder_paste_margin_ratio"):
            remove(fp, key)
        for number, y in (("1", -2.5), ("2", 2.5)):
            p = pad(board, ref, number)
            p.values[2] = Atom("rect")
            replace(p, f"(at 0 {y})")
            replace(p, f"(size 5.2 {land_height})")
            replace(p, '(layers "F.Cu" "F.Mask" "F.Paste")')
            for key in ("solder_mask_margin", "solder_paste_margin", "solder_paste_margin_ratio"):
                remove(p, key)


class ParserTests(unittest.TestCase):
    def test_strings_comments_and_locations(self):
        node = parse('# comment (ignored)\n(root "a(\\\"b\\n)c" (field "C:\\\\parts"))')
        self.assertEqual(node.line, 2)
        self.assertEqual(node.values[0], 'a("b\n)c')
        self.assertEqual(node.one("field").atoms(), ["C:\\parts"])
        self.assertEqual(parse(dump(node)).values[0], node.values[0])
        self.assertEqual(parse_many("(version 1) # x\n(rule 'quoted name' (constraint clearance (min 3mm)))")[1].values[0],
                         "quoted name")

    def test_malformed_is_not_partially_accepted(self):
        for text in ("", "# only a comment", "(root", "(root))", "root", "(root) garbage", "()",
                     '(root "unterminated)', '(root "bad\\q")', '(root "value"trailing)',
                     "(root) (root)", "((root))", "(root \x00)", '("root" x)', '(root "raw\nnewline")'):
            with self.subTest(text=text), self.assertRaises(SExprError):
                parse(text)

    def test_duplicate_required_fields_and_depth(self):
        with self.assertRaises(SExprError):
            parse("(root (size 1 1) (size 2 2))").one("size")
        with self.assertRaises(SExprError):
            parse("(x " * 130 + ")" * 130)

    def test_rule_precedence_and_numeric_netcode(self):
        node = parse("(condition x)")
        a = {"NetName": "EARTH", "Type": "Pad", "NetCode": 4}
        b = {"NetName": "WIRE_B", "Type": "Track", "NetCode": 2}
        tree = condition("A.NetName == 'EARTH' && B.NetCode != 0", node)
        self.assertTrue(matches(tree, a, b))
        self.assertFalse(matches(tree, a, dict(b, NetCode=0)))
        tree = condition("A.Type == 'Pad' || B.Type == 'Via' && A.NetName != 'EARTH'", node)
        self.assertFalse(matches(tree, a, b))  # (true || false) && false, as in KiCad.
        self.assertTrue(matches(condition("!(A.NetName != 'EARTH') && B.NetName == 'WIRE_*'", node), a, b))
        bracket = condition("B.NetName == 'WIRE_[ABC]'", node)
        self.assertFalse(matches(bracket, a, b))
        self.assertTrue(matches(bracket, a, dict(b, NetName="WIRE_[ABC]")))


class GeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authoritative = parse((ROOT / "pcb/pcb.kicad_pcb").read_text(), root="kicad_pcb")
        cls.positive = deepcopy(cls.authoritative)
        cls.project = json.loads((ROOT / "pcb/pcb.kicad_pro").read_text())
        settings = cls.project["board"]["design_settings"]
        settings["rules"].update(PROJECT_MINIMA)
        settings["rule_severities"].update({key: "error" for key in REQUIRED_ERROR_RULES})
        settings["rule_severities"].update({key: "warning" for key in REQUIRED_VISIBLE_RULES})
        settings["drc_exclusions"] = []

    def setUp(self):
        self.board = deepcopy(self.positive)
        self.settings = deepcopy(self.project)
        self.rules = RULES

    def report(self, board=None, project=None, rules=None):
        return check_sources(dump(board if board is not None else self.board),
                             json.dumps(project if project is not None else self.settings),
                             rules if rules is not None else self.rules)

    def aperture_report(self, board=None):
        checker = GeometryCheck(board if board is not None else self.board)
        checker.attempt(checker.read_board)
        checker.attempt(checker.check_apertures)
        ok = not any(d["severity"] == "error" for d in checker.diagnostics)
        return {"ok": ok, "status": "pass" if ok else "fail", "diagnostics": checker.diagnostics,
                "measurements": checker.measurements}

    def assert_pass(self, report=None):
        report = report if report is not None else self.report()
        self.assertTrue(report["ok"], json.dumps(report["diagnostics"], indent=2))
        self.assertEqual(report["status"], "pass")
        return report

    def assert_defect(self, code, report=None):
        report = report if report is not None else self.report()
        self.assertFalse(report["ok"])
        found = [d for d in report["diagnostics"] if d["code"] == code]
        self.assertTrue(found, json.dumps(report["diagnostics"], indent=2))
        return found

    def test_nominal_positive_real_board_fixture(self):
        report = self.assert_pass()
        self.assertEqual(len(report["measurements"]["protected_vias"]), 14)
        self.assertTrue(all(v["ok"] for v in report["measurements"]["protected_vias"]))
        self.assertAlmostEqual(report["measurements"]["minimum_fence_earth_clearance_mm"], 3.25)
        self.assertEqual(report["qualification"]["physical_fit"], "not_verified")
        self.assertEqual(report["qualification"]["via_covering_cam"], "not_verified")

    def test_adopted_dfm_holes_lands_and_untented_vias(self):
        report = self.assert_pass(self.report(self.authoritative))
        self.assertEqual(len(report["measurements"]["component_hole_design"]), 18)
        self.assertEqual(len(report["measurements"]["component_rings"]), 18)
        self.assertAlmostEqual(min(row["nominal_ring_mm"] for row in report["measurements"]["component_rings"]), 0.4)
        self.assertEqual(report["measurements"]["via_count"], 14)
        checker = GeometryCheck(self.authoritative)
        checker.read_board()
        parts = [fp for fp in checker.footprints.values() if fp.one("attr").atoms() in (["smd"], ["through_hole"])]
        self.assertEqual(len(parts), 16)
        self.assertEqual(sum(fp.one("attr").atoms() == ["smd"] for fp in parts), 8)
        self.assertEqual(sum(p.kind == "thru_hole" for p in checker.pads), 18)
        self.assertEqual(sum(p.kind == "np_thru_hole" for p in checker.pads), 4)
        self.assertEqual(sum(p.kind == "smd" for p in checker.pads), 16)
        for layer, count in (("F.Mask", 52), ("B.Mask", 36), ("F.Paste", 16)):
            self.assertEqual(sum(layer in a.layers for a in checker.apertures), count)
        for via in checker.vias:
            self.assertFalse(checker.tented(via.node, "front"))
            self.assertFalse(checker.tented(via.node, "back"))
        for ref in ("GDT_AB", "GDT_BC"):
            for num, y in (("1", -2.0), ("2", 2.0)):
                item = pad(self.authoritative, ref, num)
                self.assertEqual(list(map(float, item.one("size").atoms())), [5.5, 1.2])
                self.assertEqual(list(map(float, item.one("at").atoms())), [0.0, y])
        smt = [row for row in report["measurements"]["via_apertures"]
               if row["aperture"].startswith(("GDT_AB.", "GDT_BC."))]
        self.assertAlmostEqual(min(row["hole_gap_mm"] for row in smt), 1.239713)
        self.assertAlmostEqual(min(row["annulus_gap_mm"] for row in smt), 0.839713)

    def test_sma_series_and_shunt_lands_match_selected_geometry(self):
        report = self.assert_pass()
        rows = {row["reference"]: row for row in report["measurements"]["sma_diodes"]}
        expected = {
            "D1": (130.8, 104.5, 0, 132.9, 128.7, "LED_A_POS", "Net-(D1-A)"),
            "D2": (130.8, 140.5, 0, 132.9, 128.7, "LED_C_POS", "Net-(D2-A)"),
            "D3": (135.0, 99.0, 180, 132.9, 137.1, "LED_A_POS", "WIRE_B"),
            "D4": (135.0, 146.0, 180, 132.9, 137.1, "LED_C_POS", "WIRE_B"),
        }
        self.assertEqual(rows.keys(), expected.keys())
        checker = GeometryCheck(self.authoritative)
        checker.read_board()
        for ref, (x, y, angle, kx, ax, cathode, anode) in expected.items():
            with self.subTest(ref=ref):
                row = rows[ref]
                self.assertNotIn(ref, COMPONENT_HOLE_MINIMA)
                self.assertEqual(row["position_mm"], [x, y])
                self.assertEqual(row["rotation_deg"], angle)
                self.assertAlmostEqual(row["inner_gap_mm"], 1.7)
                self.assertEqual(row["pads"], [
                    {"pad": f"{ref}.1", "position_mm": [kx, y], "net": cathode, "size_mm": [2.5, 2.0]},
                    {"pad": f"{ref}.2", "position_mm": [ax, y], "net": anode, "size_mm": [2.5, 2.0]},
                ])
                for num, px in (("1", kx), ("2", ax)):
                    openings = [a for a in checker.apertures if a.reference == ref and a.pad_number == num]
                    self.assertEqual(len(openings), 2)
                    for opening in openings:
                        for actual, bound in zip(opening.shape.bounds, (px - 1.25, y - 1, px + 1.25, y + 1)):
                            self.assertAlmostEqual(actual, bound)

    def test_sma_footprints_require_reference_library_and_population(self):
        for ref in ("D1", "D2", "D3", "D4"):
            for change in ("missing", "renamed", "library", "type", "dnp", "bottom"):
                with self.subTest(ref=ref, change=change):
                    board = deepcopy(self.positive)
                    fp = footprint(board, ref)
                    if change == "missing":
                        board.values.remove(fp)
                    elif change == "renamed":
                        reference = next(p for p in fp.children("property") if p.values[0] == "Reference")
                        reference.values[1] = Atom("D9", quoted=True)
                    elif change == "library":
                        fp.values[0] = Atom("Diode_SMD:D_SMA", quoted=True)
                    else:
                        replace(fp, {"type": "(attr through_hole)", "dnp": "(attr smd dnp)",
                                     "bottom": '(layer "B.Cu")'}[change])
                    self.assert_defect("SMA_DIODE_FOOTPRINT", self.report(board))

    def test_sma_missing_duplicate_and_renumbered_pads_fail(self):
        for ref in ("D1", "D2", "D3", "D4"):
            for num in ("1", "2"):
                for change in ("missing", "duplicate", "renumbered"):
                    with self.subTest(ref=ref, num=num, change=change):
                        board = deepcopy(self.positive)
                        fp, p = footprint(board, ref), pad(board, ref, num)
                        if change == "missing":
                            fp.values.remove(p)
                        elif change == "duplicate":
                            fp.values.append(deepcopy(p))
                        else:
                            p.values[0] = Atom("3", quoted=True)
                        self.assert_defect("SMA_DIODE_PAD", self.report(board))

    def test_sma_pad_type_and_drill_presence_fail_with_sma_diagnostics(self):
        for ref in ("D1", "D2", "D3", "D4"):
            for num in ("1", "2"):
                for kind, drilled in (("smd", True), ("thru_hole", True),
                                      ("thru_hole", False), ("connect", False)):
                    with self.subTest(ref=ref, num=num, kind=kind, drilled=drilled):
                        board = deepcopy(self.positive)
                        p = pad(board, ref, num)
                        p.values[1] = Atom(kind)
                        if kind == "thru_hole":
                            replace(p, '(layers "*.Cu" "*.Mask")')
                        if drilled:
                            replace(p, "(drill 1.1)")
                        report = self.report(board)
                        self.assert_defect("SMA_DIODE_PAD", report)
                        if (kind == "thru_hole") != drilled:
                            self.assert_defect("INVALID_STRUCTURE", report)
                        self.assertNotIn("C1_DIODE_DRILL", {d["code"] for d in report["diagnostics"]})

    def test_retired_c1_tht_diode_is_not_a_supported_sma_substitution(self):
        # The former 1.10 mm C1 fix was valid for the retired part, not for an SMA.
        for ref in ("D1", "D2"):
            for drill in (0.9, 1.1):
                with self.subTest(ref=ref, drill=drill):
                    board = deepcopy(self.positive)
                    fp = footprint(board, ref)
                    fp.values[0] = Atom("DogFence:1N4007G_P10.16mm_K_Right", quoted=True)
                    replace(fp, "(attr through_hole)")
                    for num, x in (("1", 5.08), ("2", -5.08)):
                        p = pad(board, ref, num)
                        p.values[1:3] = [Atom("thru_hole"), Atom("circle")]
                        replace(p, f"(at {x} 0)")
                        replace(p, "(size 2.2 2.2)")
                        replace(p, f"(drill {drill})")
                        replace(p, '(layers "*.Cu" "*.Mask")')
                    report = self.report(board)
                    self.assert_defect("SMA_DIODE_FOOTPRINT", report)
                    self.assert_defect("SMA_DIODE_PAD", report)

    def test_sma_placement_and_pad_geometry_cannot_drift(self):
        for ref in ("D1", "D2", "D3", "D4"):
            for change in ("origin", "rotation"):
                with self.subTest(ref=ref, change=change):
                    board = deepcopy(self.positive)
                    fp = footprint(board, ref)
                    x, y, *angle = map(float, fp.one("at").atoms())
                    replace(fp, f"(at {x + (0.1 if change == 'origin' else 0)} {y} "
                            f"{(angle[0] if angle else 0) + (180 if change == 'rotation' else 0)})")
                    self.assert_defect("SMA_DIODE_PLACEMENT", self.report(board))
            for num in ("1", "2"):
                for change in ("(at 2 0)", "(at 2.1 0 90)", "(size 2.4 2)", "(size 2.5 1.9)", "oval"):
                    with self.subTest(ref=ref, num=num, change=change):
                        board = deepcopy(self.positive)
                        p = pad(board, ref, num)
                        if change == "oval":
                            p.values[2] = Atom(change)
                        else:
                            replace(p, change)
                        self.assert_defect("SMA_DIODE_PAD", self.report(board))

    def test_sma_series_and_shunt_polarity_and_wrong_nets(self):
        for ref in ("D1", "D2", "D3", "D4"):
            with self.subTest(ref=ref, change="reversed"):
                board = deepcopy(self.positive)
                k, a = pad(board, ref, "1"), pad(board, ref, "2")
                cathode, anode = k.one("net").atoms()[1], a.one("net").atoms()[1]
                set_net(board, k, anode)
                set_net(board, a, cathode)
                self.assertEqual(len(self.assert_defect("SMA_DIODE_POLARITY", self.report(board))), 2)
            for num in ("1", "2"):
                for net in ("WIRE_A", ""):
                    with self.subTest(ref=ref, num=num, net=net):
                        board = deepcopy(self.positive)
                        set_net(board, pad(board, ref, num), net)
                        self.assert_defect("SMA_DIODE_POLARITY", self.report(board))

    def test_sma_mask_paste_layers_and_effective_margins_are_strict(self):
        for ref in ("D1", "D2", "D3", "D4"):
            for num in ("1", "2"):
                for change in ('(layers "F.Cu" "F.Mask")', '(layers "F.Cu" "F.Paste")',
                               '(layers "B.Cu" "B.Mask" "B.Paste")', "(solder_mask_margin 0.1)",
                               "(solder_paste_margin -0.1)", "(solder_paste_margin_ratio -0.05)"):
                    with self.subTest(ref=ref, num=num, change=change):
                        board = deepcopy(self.positive)
                        replace(pad(board, ref, num), change)
                        self.assert_defect("SMA_DIODE_APERTURE", self.report(board))
            for field in ("solder_mask_margin", "solder_paste_margin", "solder_paste_ratio"):
                with self.subTest(ref=ref, inherited=field):
                    board = deepcopy(self.positive)
                    replace(footprint(board, ref), f"({field} 0.1)")
                    self.assert_defect("SMA_DIODE_APERTURE", self.report(board))

    def test_sma_explicit_zero_overrides_and_modulo_rotations_remain_valid(self):
        for ref in ("D1", "D2", "D3", "D4"):
            fp = footprint(self.board, ref)
            x, y, *angle = map(float, fp.one("at").atoms())
            rotation = (angle[0] if angle else 0) - 360
            replace(fp, f"(at {x} {y} {rotation})")
            for field in ("solder_mask_margin", "solder_paste_margin", "solder_paste_ratio"):
                replace(fp, f"({field} 0.2)")
            for p in fp.children("pad"):
                px, py = p.one("at").atoms()[:2]
                replace(p, f"(at {px} {py} {rotation})")
                for field in ("solder_mask_margin", "solder_paste_margin", "solder_paste_margin_ratio"):
                    replace(p, f"({field} 0)")
        self.assert_pass()

    def test_sma_separate_or_extra_apertures_cannot_replace_pad_owned_openings(self):
        for ref in ("D1", "D2", "D3", "D4"):
            for change in ("replacement", "extra", "F.Mask", "F.Paste"):
                with self.subTest(ref=ref, change=change):
                    board = deepcopy(self.positive)
                    fp, p = footprint(board, ref), pad(board, ref, "1")
                    if change == "replacement":
                        opening = deepcopy(p)
                        opening.values[0] = Atom("", quoted=True)
                        remove(opening, "net")
                        replace(opening, '(layers "F.Mask" "F.Paste")')
                        replace(p, '(layers "F.Cu")')
                        fp.values.append(opening)
                    elif change == "extra":
                        fp.values.append(parse('''(fp_rect (start -1 -1) (end 1 1)
                            (stroke (width 0) (type solid)) (fill solid) (layer "F.Paste"))'''))
                    else:
                        x, y = map(float, fp.one("at").atoms()[:2])
                        # Unowned artwork in the inner gap leaves all eight pads unchanged.
                        board.values.append(parse(f'''(gr_rect (start {x - 0.5} {y - 0.5})
                            (end {x + 0.5} {y + 0.5}) (stroke (width 0) (type solid))
                            (fill solid) (layer "{change}"))'''))
                    self.assert_defect("SMA_DIODE_APERTURE", self.report(board))

    def test_resistor_footprint_and_pads_are_required(self):
        for ref, y in (("R1", 104.5), ("R2", 140.5)):
            for num, x in (("1", -3.125), ("2", 3.125)):
                p = pad(self.authoritative, ref, num)
                self.assertEqual(list(map(float, p.one("at").atoms()[:2])), [x, 0.0])
                self.assertEqual(list(map(float, p.one("size").atoms())), [1.35, 3.7])
                self.assertEqual(p.values[1:3], ["smd", "rect"])
                self.assertIsNone(p.one("drill", required=False))
            for change in ("library", "missing", "bottom", "dnp", "type", "origin", "pitch", "pad",
                           "net", "rotation", "shape", "drill", "extra-pad"):
                with self.subTest(ref=ref, change=change):
                    board = deepcopy(self.positive)
                    fp, p = footprint(board, ref), pad(board, ref, "2")
                    if change == "library":
                        fp.values[0] = Atom("DogFence:MBE0414_P15.24mm", quoted=True)
                    elif change == "missing":
                        board.values.remove(fp)
                    elif change in ("bottom", "dnp", "type"):
                        replace(fp, {"bottom": '(layer "B.Cu")', "dnp": "(attr smd dnp)",
                                     "type": "(attr through_hole)"}[change])
                    elif change == "origin":
                        replace(fp, f"(at 120.1 {y})")
                    elif change == "pitch":
                        replace(p, "(at 2.5 0)")
                    elif change == "pad":
                        replace(p, "(size 2.5 2.5)")
                    elif change == "net":
                        set_net(board, p, "WIRE_B")
                    elif change == "rotation":
                        replace(p, "(at 3.125 0 90)")
                    elif change == "shape":
                        p.values[2] = Atom("roundrect")
                        replace(p, "(roundrect_rratio 0.25)")
                    elif change == "drill":
                        replace(p, "(drill 1.4)")
                    else:
                        fp.values.append(deepcopy(p))
                    code = "RESISTOR_FOOTPRINT" if change in ("library", "missing", "bottom", "dnp", "type") \
                        else "RESISTOR_GEOMETRY"
                    if change == "drill":
                        code = "INVALID_STRUCTURE"
                    self.assert_defect(code, self.report(board))

    def test_resistor_mask_paste_and_extra_apertures_cannot_drift(self):
        for ref in ("R1", "R2"):
            for num in ("1", "2"):
                for change in ('(layers "F.Cu" "F.Mask")', '(layers "F.Cu" "F.Paste")',
                               '(layers "B.Cu" "B.Mask" "B.Paste")', "(solder_mask_margin -0.1)",
                               "(solder_paste_margin -0.1)", "(solder_paste_margin_ratio -0.05)"):
                    with self.subTest(ref=ref, num=num, change=change):
                        board = deepcopy(self.positive)
                        replace(pad(board, ref, num), change)
                        self.assert_defect("RESISTOR_APERTURE", self.report(board))
            for field in ("solder_mask_margin", "solder_paste_margin", "solder_paste_ratio"):
                with self.subTest(ref=ref, inherited=field):
                    board = deepcopy(self.positive)
                    fp = footprint(board, ref)
                    replace(fp, f"({field} -0.1)")
                    self.assert_defect("RESISTOR_APERTURE", self.report(board))
                    pad_field = "solder_paste_margin_ratio" if field == "solder_paste_ratio" else field
                    for p in fp.children("pad"):
                        replace(p, f"({pad_field} 0)")
                    self.assert_pass(self.report(board))
            for layer in ("F.Mask", "F.Paste"):
                with self.subTest(ref=ref, extra=layer):
                    board = deepcopy(self.positive)
                    fp = footprint(board, ref)
                    fp.values.append(parse(f'''(fp_rect (start -1 -1) (end 1 1)
                        (stroke (width 0) (type solid)) (fill solid) (layer "{layer}"))'''))
                    self.assert_defect("RESISTOR_APERTURE", self.report(board))

    def test_straight_shunt_cathode_links_keep_full_width(self):
        for start, end in (((132.9, 99), (132.9, 104.5)), ((132.9, 140.5), (132.9, 146))):
            for change in ("width", "missing"):
                with self.subTest(start=start, change=change):
                    board = deepcopy(self.positive)
                    track = next(n for n in board.children("segment")
                                 if tuple(map(float, n.one("start").atoms())) == start
                                 and tuple(map(float, n.one("end").atoms())) == end)
                    self.assertEqual(track.one("width").atoms(), ["1.8"])
                    if change == "width":
                        replace(track, "(width 0.8)")
                    else:
                        board.values.remove(track)
                    self.assert_defect("SHUNT_LINK_GEOMETRY", self.report(board))

    def test_selected_fit_holes_cannot_revert_to_unsupported_sizes(self):
        for ref, minimum in COMPONENT_HOLE_MINIMA.items():
            with self.subTest(ref=ref):
                board = deepcopy(self.positive)
                replace(pad(board, ref, "1"), f"(drill {minimum - 0.1:.2f})")
                self.assert_defect("COMPONENT_FIT_DRILL", self.report(board))

    def test_body_courtyards_include_declared_pose_and_assembly_margin(self):
        for ref in (*COMPONENT_HOLE_MINIMA, "GDT_AB", "GDT_BC", "D1", "D2", "D3", "D4", "R1", "R2"):
            with self.subTest(ref=ref):
                fp = footprint(self.authoritative, ref)
                boxes = {rect.one("layer").atoms()[0]: rect for rect in fp.children("fp_rect")}
                body, courtyard = boxes["F.Fab"], boxes["F.CrtYd"]
                if ref in ("R1", "R2", "D1", "D2", "D3", "D4"):
                    half_body, half_courtyard = ((3.225, 1.7), (4.05, 2.1)) if ref.startswith("R") \
                        else ((2.25, 1.4), (3.6, 1.8))
                    for rect, half in ((body, half_body), (courtyard, half_courtyard)):
                        self.assertEqual(tuple(map(float, rect.one("start").atoms())), tuple(-v for v in half))
                        self.assertEqual(tuple(map(float, rect.one("end").atoms())), half)
                for edge, direction in (("start", -1), ("end", 1)):
                    for b, c in zip(body.one(edge).atoms(), courtyard.one(edge).atoms()):
                        self.assertGreaterEqual(direction * (float(c) - float(b)) + 1e-9, 0.10 + 0.25)
                if ref.startswith("R"):
                    for layer in ("F.Fab", "F.CrtYd"):
                        board = deepcopy(self.positive)
                        box = next(n for n in footprint(board, ref).children("fp_rect")
                                   if n.one("layer").atoms() == [layer])
                        replace(box, "(start -3.15 -1.6)")
                        self.assert_defect("RESISTOR_ENVELOPE", self.report(board))

        earth = footprint(self.authoritative, "J_EARTH")
        x, y, angle = map(float, earth.one("at").atoms())
        for layer, bounds in (("F.Fab", (149.6, 110.0, 161.0, 135.0)),
                              ("F.CrtYd", (149.25, 109.65, 161.35, 135.35))):
            rect = next(item for item in earth.children("fp_rect") if item.one("layer").atoms() == [layer])
            points = [move(tuple(map(float, rect.one(edge).atoms())), (x, y), angle) for edge in ("start", "end")]
            actual = (*map(min, zip(*points)), *map(max, zip(*points)))
            for coordinate, expected in zip(actual, bounds):
                self.assertAlmostEqual(coordinate, expected)

    def test_axial_forming_room_is_a_geometric_ceiling_not_bend_approval(self):
        for ref, axis, wire, room in (("GDT_AC", 1, .90, 4.37), ("GDT_A_E", 0, 1.05, 4.32),
                                     ("GDT_B_E", 0, 1.05, 4.32), ("GDT_C_E", 0, 1.05, 4.32)):
            with self.subTest(ref=ref):
                fp = footprint(self.authoritative, ref)
                body = next(rect for rect in fp.children("fp_rect") if rect.one("layer").atoms() == ["F.Fab"])
                low, high = (float(body.one(edge).atoms()[axis]) for edge in ("start", "end"))
                pins = sorted(float(p.one("at").atoms()[axis]) for p in fp.children("pad"))
                self.assertAlmostEqual(pins[1] - pins[0], 15.24)
                available = min(low - pins[0], pins[1] - high) - .05 - .10
                self.assertAlmostEqual(available, room)
                self.assertAlmostEqual(available - wire / 2,
                                       3.92 if ref == "GDT_AC" else 3.795)

    def test_adopted_pin_envelopes_include_independent_pattern_allowance(self):
        position_budget = 2 * (math.hypot(0.05, 0.05) + 0.05)
        envelopes = {"J_IN": math.hypot(1.1, 1.0), "J_LED_A": math.hypot(1.15, 1.0),
                     "GDT_AC": 0.9, "GDT_A_E": 1.05}
        for ref, maximum in envelopes.items():
            with self.subTest(ref=ref):
                hole = float(pad(self.authoritative, ref, "1").one("drill").atoms()[0])
                self.assertGreaterEqual(hole - 0.08 - maximum - position_budget, 0.1)

    def test_historical_w1_collision_remains_reproducible_after_layout_fixes(self):
        historical_smt(self.board)
        report = self.report()
        mask = self.assert_defect("W1_VIA_MASK", report)
        paste = self.assert_defect("W1_VIA_PASTE", report)
        self.assertEqual(len(mask), 12)  # B's three vias meet both SMT GDTs.
        self.assertEqual(len(paste), 12)
        self.assertEqual(len({tuple(d["position_mm"]) for d in mask}), 9)
        self.assertEqual(len({d["aperture"] for d in mask}), 4)
        self.assertTrue(all(abs(d["measured_mm"] + 0.19) < 1e-6 for d in mask + paste))

    def test_component_fit_drill_and_ring_are_independent(self):
        replace(pad(self.board, "GDT_AC", "2"), "(drill 1.3)")
        report = self.report()
        self.assert_defect("COMPONENT_FIT_DRILL", report)
        self.assertNotIn("COMPONENT_RING", {d["code"] for d in report["diagnostics"]})
        replace(pad(self.board, "GDT_AC", "2"), "(drill 1.4)")
        replace(pad(self.board, "GDT_AC", "2"), "(size 1.8 1.8)")
        report = self.report()
        self.assert_defect("COMPONENT_RING", report)
        self.assertNotIn("COMPONENT_FIT_DRILL", {d["code"] for d in report["diagnostics"]})

    def test_offset_hole_uses_true_ring_not_min_size_only(self):
        replace(pad(self.board, "GDT_AC", "1"), "(size 2.4 2.4)")
        replace(pad(self.board, "GDT_AC", "1"), "(drill 1.4 (offset 0.35 0))")
        self.assertAlmostEqual(self.assert_defect("COMPONENT_RING")[0]["measured_mm"], 0.15)

    def test_slot_ring_and_arbitrary_pad_rotation(self):
        extra = parse('''(footprint "slot fixture" (layer "F.Cu") (at 116 99)
            (property "Reference" "X_PTH")
            (pad "1" thru_hole oval (at 0 0 37) (size 2.8 2.4) (drill oval 1.6 1.4)
                (layers "*.Cu" "*.Mask") (net 1 "WIRE_A")))''')
        self.board.values.append(extra)
        p = extra.children("pad")[0]
        self.assert_pass()
        replace(p, "(drill oval 2.4 1.4)")
        self.assert_defect("COMPONENT_RING")

    def test_earth_encroachment_on_both_copper_layers(self):
        for layer in CU:
            with self.subTest(layer=layer):
                board = deepcopy(self.positive)
                board.values.append(parse(f'''(segment (start 139 116) (end 142 116)
                    (width 1) (layer "{layer}") (net 2))'''))
                self.assert_defect("EARTH_CLEARANCE", self.report(board))

    def test_rotated_pad_not_axis_aligned_bbox_and_global_pad_coordinates(self):
        extra = parse('''(footprint "fixture" (layer "F.Cu") (at 139 117 90)
            (property "Reference" "X1")
            (pad "1" smd rect (at 1 0 90) (size 5 1)
              (layers "F.Cu" "F.Mask" "F.Paste") (net 2 "WIRE_B")))''')
        self.board.values.append(extra)
        check = GeometryCheck(self.board)
        check.read_board()
        p = next(p for p in check.pads if p.reference == "X1")
        self.assertAlmostEqual(p.center[0], 139)
        self.assertAlmostEqual(p.center[1], 116)
        self.assertAlmostEqual(p.shape.bounds[0], 138.5)  # Absolute pad angle, not 90+90.
        self.assert_pass()
        replace(extra.children("pad")[0], "(at 1 0 0)")
        self.assert_defect("EARTH_CLEARANCE")

    def test_roundrect_and_oval_corner_distance_not_bounding_box(self):
        rounded = pad_shape("roundrect", (4, 2), (0, 0), 31, 0.25)
        point_ = move((1.9, 0.9), angle=31)
        self.assertAlmostEqual(rounded.signed_distance(point_), math.hypot(0.4, 0.4) - 0.5)
        self.assertLess(pad_shape("rect", (4, 2), (0, 0), 31).signed_distance(point_), 0)
        oval = pad_shape("oval", (4, 2), (0, 0), 90)
        self.assertAlmostEqual(oval.signed_distance((1, -2)), math.sqrt(2) - 1)
        crossing = Shape(((-1, -1), (1, 1)), 0.1)
        self.assertEqual(crossing.gap(Shape(((-1, 1), (1, -1)), 0.1)), 0)

    def test_inherited_mask_paste_and_explicit_zero_override(self):
        historical_smt(self.board)
        for ref in ("GDT_AB", "GDT_BC"):
            fp = footprint(self.board, ref)
            replace(fp, "(solder_mask_margin -0.35)")
            replace(fp, "(solder_paste_margin -0.05)")
            replace(fp, "(solder_paste_ratio -0.15)")
        report = self.assert_pass(self.aperture_report())
        records = report["measurements"]["via_apertures"]
        self.assertTrue(any(r["annulus_exposed"] and r["mask_barrier_mm"] >= MIN_MASK_BARRIER
                            and r["copper_hole_gap_mm"] < 0 for r in records if r["layer"] == "F.Mask"))
        replace(pad(self.board, "GDT_AB", "1"), "(solder_mask_margin 0)")
        self.assert_defect("W1_VIA_MASK", self.aperture_report())  # KiCad 9 zero overrides inheritance.

    def test_board_margin_inheritance_and_pad_priority(self):
        historical_smt(self.board)
        replace(self.board.one("setup"), "(pad_to_mask_clearance -0.4)")
        replace(self.board.one("setup"), "(pad_to_paste_clearance -0.4)")
        self.assert_pass(self.aperture_report())
        fp = footprint(self.board, "GDT_AB")
        replace(fp, "(solder_mask_margin 0.2)")
        for p in fp.children("pad"):
            replace(p, "(solder_mask_margin -0.4)")
        self.assert_pass(self.aperture_report())  # Not the sum of board, footprint and pad overrides.
        remove(fp.children("pad")[0], "solder_mask_margin")
        self.assert_defect("W1_VIA_MASK", self.aperture_report())

    def test_mask_and_paste_are_independent(self):
        for field, code in (("solder_mask_margin", "W1_VIA_MASK"),
                            ("solder_paste_margin", "W1_VIA_PASTE")):
            with self.subTest(field=field):
                board = deepcopy(self.positive)
                historical_smt(board, land_height=0.8)
                replace(pad(board, "GDT_AB", "1"), f"({field} 0.6)")
                self.assert_defect(code, self.aperture_report(board))

    def test_mask_barrier_and_untented_annulus(self):
        historical_smt(self.board, land_height=0.8)
        p = pad(self.board, "GDT_AB", "1")
        replace(p, "(solder_mask_margin 0.36)")  # 0.41 - 0.36 = 0.05 mm, no drill overlap.
        self.assert_defect("W1_MASK_BARRIER", self.aperture_report())
        remove(p, "solder_mask_margin")
        via = next(v for v in self.board.children("via") if v.one("at").atoms() == ["114", "114.88"])
        replace(via, "(tenting back)")
        self.assert_defect("W1_MASK_BARRIER", self.aperture_report())  # Only 0.01 mm between open annulus and land.

    def test_same_net_open_vias_do_not_waive_component_or_other_net_collisions(self):
        board = deepcopy(self.authoritative)
        replace(pad(board, "GDT_AB", "1"), "(solder_mask_margin 1.3)")
        self.assert_defect("W1_VIA_MASK", self.report(board))
        board = deepcopy(self.authoritative)
        set_net(board, board.children("via")[0], "WIRE_B")
        self.assert_defect("W1_MASK_BARRIER", self.report(board))

    def test_native_unsupported_via_tenting_and_margin_fail_closed(self):
        for text in ("(tenting (front no) (back yes))", "(solder_mask_margin 0.1)"):
            with self.subTest(text=text):
                board = deepcopy(self.authoritative)
                replace(board.children("via")[0], text)
                self.assert_defect("UNSUPPORTED_GEOMETRY", self.report(board))

    def test_mask_minimum_width_cannot_silently_merge_a_barrier(self):
        historical_smt(self.board, land_height=0.8)
        replace(self.board.one("setup"), "(solder_mask_min_width 0.7)")
        self.assert_defect("W1_MASK_BARRIER", self.aperture_report())

    def test_mask_graphic_and_separate_apertures_are_checked(self):
        self.board.values.append(parse('''(gr_rect (start 113.9 114.8) (end 114.1 115.1)
            (stroke (width 0) (type solid)) (fill solid) (layer "F.Mask"))'''))
        self.assert_defect("W1_VIA_MASK")

    def test_separate_aperture_pad_and_tangent_opening(self):
        fp = footprint(self.board, "GDT_AB")
        p = pad(self.board, "GDT_AB", "1")
        opening = deepcopy(p)
        opening.values[0] = Atom("", quoted=True)
        remove(opening, "net")
        replace(opening, '(layers "F.Mask" "F.Paste")')
        # Technical-only aperture pads ignore even inherited extreme margins.
        replace(opening, "(solder_mask_margin -100)")
        replace(opening, "(solder_paste_margin 100)")
        replace(p, '(layers "F.Cu")')
        fp.values.append(opening)
        self.assert_pass()
        replace(opening, "(at 0 -3.2)")  # Touches the copper only along one edge.
        self.assert_defect("MISSING_SMT_APERTURE")

    def test_smd_roundrect_corner_and_rotation_at_via(self):
        # The drill misses the rounded corner but intersects the rotated square.
        delta = move((1.8, 1.8), angle=31)
        origin = (112.5 - delta[0], 114.88 - delta[1])
        extra = parse(f'''(footprint "corner fixture" (layer "F.Cu") (at {origin[0]} {origin[1]})
            (property "Reference" "X2")
            (pad "" smd roundrect (at 0 0 31) (size 3 3) (roundrect_rratio 0.5)
                (layers "F.Mask")))''')
        self.board.values.append(extra)
        self.assert_pass()  # Open-annulus mask gap: 1.8*sqrt(2) - 1.5 - 0.9 > 0.1 mm.
        extra.children("pad")[0].values[2] = Atom("rect")
        self.assert_defect("W1_VIA_MASK")

    def test_missing_or_collapsed_smt_aperture_does_not_pass(self):
        p = pad(self.board, "GDT_AB", "1")
        replace(p, '(layers "F.Cu")')
        self.assert_defect("MISSING_SMT_APERTURE")
        replace(p, '(layers "F.Cu" "F.Mask" "F.Paste")')
        replace(p, "(solder_mask_margin -10)")
        self.assert_defect("EMPTY_APERTURE")

    def test_every_protected_via_is_required_at_its_coordinate(self):
        for xy, net in PROTECTED_VIAS.items():
            with self.subTest(xy=xy, net=net):
                board = deepcopy(self.positive)
                via = next(v for v in board.children("via") if tuple(map(float, v.one("at").atoms())) == xy)
                board.values.remove(via)
                self.assert_defect("PROTECTED_VIA", self.report(board))

    def test_via_size_drill_net_and_duplicate(self):
        via = self.board.children("via")[0]
        for change in ("(size 1.7)", "(drill 0.9)", "(at 115.51 114.88)", "(net 4)"):
            with self.subTest(change=change):
                board = deepcopy(self.positive)
                replace(board.children("via")[0], change)
                self.assert_defect("PROTECTED_VIA", self.report(board))
        self.board.values.append(deepcopy(via))
        self.assert_defect("PROTECTED_VIA")

    def test_no_added_vias_even_with_all_protected_vias_intact(self):
        extra = deepcopy(self.board.children("via")[0])
        replace(extra, "(at 117 114.88)")
        set_net(self.board, extra, "WIRE_A")
        self.board.values.append(extra)
        report = self.report()
        self.assert_defect("VIA_COUNT", report)
        self.assertEqual(report["measurements"]["via_count"], 15)
        self.assertTrue(all(v["ok"] for v in report["measurements"]["protected_vias"]))

    def test_untented_via_mask_policy_cannot_be_changed(self):
        for owner in ("setup", "via"):
            for flags in ("front", "back", "front back"):
                with self.subTest(owner=owner, flags=flags):
                    board = deepcopy(self.positive)
                    node = board.one("setup") if owner == "setup" else board.children("via")[0]
                    replace(node, f"(tenting {flags})")
                    self.assert_defect("VIA_TREATMENT", self.report(board))
        for margin in (-0.05, 0.05):
            with self.subTest(margin=margin):
                board = deepcopy(self.positive)
                replace(board.one("setup"), f"(pad_to_mask_clearance {margin})")
                self.assert_defect("VIA_TREATMENT", self.report(board))

    def test_rail_width_loss_and_harmless_split(self):
        rail = next(t for t in self.board.children("segment") if t.one("start").atoms() == ["106", "114.88"])
        replace(rail, "(width 3.1)")
        self.assert_defect("RAIL_GEOMETRY")
        replace(rail, "(width 3.2)")
        other = deepcopy(rail)
        replace(rail, "(end 118 114.88)")
        replace(other, "(start 131 114.88)")
        replace(other, "(end 118 114.88)")
        self.board.values.append(other)
        self.assert_pass()

    def test_lost_b_return_and_compressed_earth_gdt_pitch(self):
        return_track = next(t for t in self.board.children("segment")
                            if t.one("start").atoms() == ["135.5", "107.2"])
        self.board.values.remove(return_track)
        self.assert_defect("B_RETURN_GEOMETRY")
        replace(footprint(self.board, "GDT_A_E"), "(at 138.62 114)")
        self.assert_defect("EARTH_GDT_PITCH")

    def test_earth_bus_interior_slit_and_boundary(self):
        board = deepcopy(self.positive)
        for t in list(board.children("segment")):
            if t.one("net").atoms() == ["4"] and t.one("layer").atoms() == ["F.Cu"] \
                    and t.one("start").atoms()[0] in ("148.12", "150", "152.5"):
                board.values.remove(t)
        self.assert_defect("EARTH_CONTINUITY", self.report(board))
        earth = next(t for t in self.board.children("segment") if t.one("net").atoms() == ["4"])
        replace(earth, "(width 4.6)")
        self.assert_defect("EARTH_BOUNDS")

    def test_led_global_polarity_and_modulo_rotation(self):
        set_net(self.board, pad(self.board, "J_LED_C", "1"), "WIRE_B")
        self.assert_defect("LED_POLARITY")
        set_net(self.board, pad(self.board, "J_LED_C", "1"), "LED_C_POS")
        replace(footprint(self.board, "J_LED_C"), "(at 145.5 142 270)")
        self.assert_pass()
        replace(footprint(self.board, "J_LED_C"), "(at 145.5 142 90)")
        self.assert_defect("LED_ORIENTATION")
        self.assert_defect("LED_POLARITY")

    def test_copper_layers_weight_outline_and_mounting(self):
        mutations = (
            (lambda b: replace(b.one("general"), "(thickness 1.2)"), "BOARD_THICKNESS"),
            (lambda b: replace(next(l for l in b.one("setup").one("stackup").children("layer")
                                    if l.values[0] == "F.Cu"), "(thickness 0.035)"), "COPPER_WEIGHT"),
            (lambda b: b.one("layers").values.append(parse('(4 "In1.Cu" signal)')), "COPPER_LAYERS"),
            (lambda b: replace(next(n for n in b.children("gr_rect") if n.one("layer").atoms() == ["Edge.Cuts"]),
                                "(end 161 150.5)"), "BOARD_OUTLINE"),
            (lambda b: replace(footprint(b, "H1"), "(at 101.6 99)"), "MOUNTING_HOLES"),
            (lambda b: replace(footprint(b, "H1").children("pad")[0], "(drill 3.1)"), "UNSUPPORTED_GEOMETRY"),
        )
        for mutate, code in mutations:
            with self.subTest(code=code):
                board = deepcopy(self.positive)
                mutate(board)
                self.assert_defect(code, self.report(board))

    def test_mounting_courtyard_and_copper_keepout(self):
        fp = footprint(self.board, "H1")
        for circle in fp.children("fp_circle"):
            if circle.one("layer").atoms() == ["B.CrtYd"]:
                replace(circle, "(end 3.2 0)")
        self.assert_defect("MOUNTING_COURTYARD")
        self.board.values.append(parse('''(segment (start 103 99) (end 104 99)
            (width 0.2) (layer "B.Cu") (net 2))'''))
        self.assert_defect("MOUNTING_CLEARANCE")

    def test_lost_project_minima_and_severities(self):
        for key in PROJECT_MINIMA:
            with self.subTest(key=key):
                settings = deepcopy(self.project)
                del settings["board"]["design_settings"]["rules"][key]
                self.assert_defect("PROJECT_RULE", self.report(project=settings))
        self.settings["board"]["design_settings"]["rule_severities"]["clearance"] = "ignore"
        self.assert_defect("PROJECT_SEVERITY")

    def test_lost_rules_and_later_weakened_overrides(self):
        self.assert_defect("MISSING_CUSTOM_RULE", self.report(rules="(version 1)"))
        for change in (
            '(rule "override" (constraint clearance (min 0.2mm)))',
            '(rule "ignored" (severity ignore) (constraint clearance (min 3mm)))',
            '(rule "ring override" (constraint annular_width (min 0.1mm)))',
        ):
            with self.subTest(change=change):
                self.assert_defect("CUSTOM_RULE_COVERAGE", self.report(rules=RULES + change))
        self.assert_defect("CUSTOM_RULE_COVERAGE", self.report(rules=RULES.replace("'EARTH'", "'MISSING_EARTH'")))
        self.assert_defect("CUSTOM_RULE_COVERAGE", self.report(rules=RULES.replace("(min 3.0mm)", "(min 2.9mm)")))

    def test_annular_rules_reject_b_dependent_conditions(self):
        for expression in (
            "B.Type == 'Pad' && B.Pad_Type == 'Through-hole'",
            "A.Type == 'Pad' && B.Pad_Type == 'Through-hole'",
            "!(B.Type != 'Pad') && A.Pad_Type == 'Through-hole'",
            "A.Type == 'Pad' || (B.Type == 'Pad' && B.Pad_Type == 'Through-hole')",
            "A.Type != 'Pad' && B.Pad_Type == 'Through-hole'",
            "!(A.Type != 'Pad' || (B.Pad_Type != 'Through-hole'))",
            "'Through-hole' == B.Pad_Type",
            "A.Pad_Type == B.Pad_Type",
            "B.NetCode != 0",
        ):
            with self.subTest(expression=expression):
                nodes = parse_many(RULES)
                replace(nodes[1], f'(condition "{expression}")')
                report = self.report(rules="\n".join(dump(n) for n in nodes))
                defects = self.assert_defect("UNSUPPORTED_GEOMETRY", report)
                self.assertTrue(any("annular_width" in d["message"] and "B=null" in d["message"]
                                    for d in defects))

    def test_annular_b_dependent_overrides_fail_closed(self):
        for expression, minimum in (
            ("B.Type == 'Pad' && B.Pad_Type == 'Through-hole'", 0.254),
            ("B.Type != 'Pad'", 0.1),
            ("!(B.Pad_Type == 'Through-hole')", 0.1),
        ):
            for later in (True, False):
                with self.subTest(expression=expression, later=later):
                    nodes = parse_many(RULES)
                    override = parse(f'''(rule "B-dependent ring override"
                        (condition "{expression}")
                        (constraint annular_width (min {minimum}mm)))''')
                    nodes.insert(len(nodes) if later else 1, override)
                    self.assert_defect("UNSUPPORTED_GEOMETRY", self.report(
                        rules="\n".join(dump(n) for n in nodes)))
        # A shared binary condition cannot be reused for a unary constraint.
        nodes = parse_many(RULES)
        nodes[2].values.append(parse("(constraint annular_width (min 0.254mm))"))
        self.assert_defect("UNSUPPORTED_GEOMETRY", self.report(rules="\n".join(dump(n) for n in nodes)))

    def test_annular_a_only_and_binary_earth_rules_remain_supported(self):
        for ring in (
            "A.Type == 'Pad' && A.Pad_Type == 'Through-hole'",
            "!(A.Type != 'Pad') && 'Through-hole' == A.Pad_Type",
            "A.Type == 'Pad' && A.Reference != 'B.Type'",  # A literal is not a B reference.
            None,
        ):
            for earth in (
                "A.NetName == 'EARTH' && B.NetName != 'EARTH'",
                "B.NetName == 'EARTH' && A.NetName != 'EARTH'",
            ):
                with self.subTest(ring=ring, earth=earth):
                    nodes = parse_many(RULES)
                    if ring is None:
                        remove(nodes[1], "condition")
                    else:
                        replace(nodes[1], f'(condition "{ring}")')
                    replace(nodes[2], f'(condition "{earth}")')
                    report = self.assert_pass(self.report(rules="\n".join(dump(n) for n in nodes)))
                    self.assertEqual(report["diagnostics"], [])

    def test_harmless_rules_metadata_and_layer_selection(self):
        rules = RULES.replace('"component PTH ring"', "'any other name'").replace(
            '(constraint annular_width', '(layer outer) (constraint annular_width')
        rules += '\n(rule "legend" (constraint text_height (min 1mm)))\n'
        self.board.values.append(parse('(group "fixture group" (uuid "unused") (members "unused"))'))
        self.board.values.append(parse('(image (at 100 100) (scale 1) (data "reference image"))'))
        table = self.board.one("layers")
        table.values = [n for n in table.values if n.values[0] != "B.Paste"]  # Unused back paste is not a guardrail.
        replace(footprint(self.board, "D1"), "(locked yes)")
        self.assert_pass(self.report(rules=rules))

    def test_unknown_geometry_is_explicitly_rejected(self):
        additions = (
            '(arc (start 138 112) (mid 141 114) (end 138 116) (width 1) (layer "F.Cu") (net 2))',
            '(zone (net 4) (net_name "EARTH") (layer "F.Cu"))',
            '(gr_text "copper" (at 140 113) (layer "F.Cu"))',
            '(future_geometry (layer "F.Cu"))',
        )
        for text in additions:
            with self.subTest(text=text):
                board = deepcopy(self.positive)
                board.values.append(parse(text))
                self.assert_defect("UNSUPPORTED_GEOMETRY", self.report(board))
        for change in ("(padstack (mode custom))", "(future_copper 1)"):
            board = deepcopy(self.positive)
            pad(board, "R1", "1").values.append(parse(change))
            self.assert_defect("UNSUPPORTED_GEOMETRY", self.report(board))
        pad(self.board, "R1", "1").values[2] = Atom("custom")
        self.assert_defect("UNSUPPORTED_GEOMETRY")

    def test_malformed_numeric_and_duplicate_geometry_fail_closed(self):
        for change in ("(size nan 2.2)", "(size 1_0 2.2)", "(size 2.2)", "(size 1e308 1e308)",
                       "(drill 1e308)", "(at 0 1e308)", "(solder_mask_margin 1e308)"):
            with self.subTest(change=change):
                board = deepcopy(self.positive)
                replace(pad(board, "R1", "1"), change)
                self.assert_defect("INVALID_STRUCTURE", self.report(board))
        pad(self.board, "R1", "1").values.append(parse("(size 2.2 2.2)"))
        self.assert_defect("INVALID_STRUCTURE")

    def test_project_numeric_strings_overflow_and_unknown_rule_conditions(self):
        self.settings["board"]["design_settings"]["rules"]["min_clearance"] = "0.2"
        self.assert_defect("PROJECT_RULE")
        report = check_sources(dump(self.board), json.dumps(self.project).replace('"min_clearance": 0.2',
                               '"min_clearance": 1e999'), RULES)
        self.assert_defect("INPUT_PROJECT", report)
        self.assert_defect("UNSUPPORTED_GEOMETRY", self.report(rules=RULES.replace(
            "A.Type == 'Pad'", "A.unknownGeometryFunction()")))

    def test_empty_malformed_and_missing_inputs(self):
        for name, values in (("pcb", ("", "(not_a_board)", None)),
                             ("project", ("{}", "[]", '{"board":{}, "board":{}}', None)),
                             ("rules", ("", "(version 1", None))):
            for value in values:
                with self.subTest(name=name, value=value):
                    inputs = {"pcb": dump(self.board), "project": json.dumps(self.settings), "rules": RULES}
                    inputs[name] = value
                    report = check_sources(inputs["pcb"], inputs["project"], inputs["rules"])
                    self.assert_defect("INPUT_" + name.upper(), report)

    def test_cli_json_exit_status_and_missing_project_rules(self):
        with tempfile.TemporaryDirectory(prefix="geometry-test-") as directory:
            base = Path(directory)
            pcb, project, rules = (base / f"pcb.kicad_{ext}" for ext in ("pcb", "pro", "dru"))
            output = base / "reports" / "geometry.json"
            pcb.write_text(dump(self.board))
            project.write_text(json.dumps(self.settings))
            rules.write_text(RULES)
            command = [sys.executable, "-B", str(ROOT / "scripts/check_geometry.py"), "--pcb", str(pcb),
                       "--project", str(project), "--rules", str(rules), "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            report = json.loads(output.read_text())
            self.assertTrue(report["ok"])
            self.assertEqual(len(report["measurements"]["component_hole_design"]), 18)
            self.assertEqual(len(report["measurements"]["sma_diodes"]), 4)
            nodes = parse_many(RULES)
            replace(nodes[1], '(condition "B.Type == \'Pad\' && B.Pad_Type == \'Through-hole\'")')
            rules.write_text("\n".join(dump(n) for n in nodes))
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assert_defect("UNSUPPORTED_GEOMETRY", json.loads(output.read_text()))
            rules.write_text(RULES)
            for source in (project, rules):
                contents = source.read_text()
                source.unlink()
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                report = json.loads(output.read_text())
                self.assertFalse(report["ok"])
                self.assertTrue(any(d["code"] == "INPUT_IO" for d in report["diagnostics"]))
                source.write_text(contents)
            bad = command[:-1] + [str(pcb)]
            original = pcb.read_bytes()
            self.assertEqual(subprocess.run(bad, capture_output=True).returncode, 2)
            self.assertEqual(pcb.read_bytes(), original)
            alias = base / "source-alias.json"
            alias.symlink_to(pcb)
            self.assertEqual(subprocess.run(command[:-1] + [str(alias)], capture_output=True).returncode, 2)
            self.assertEqual(pcb.read_bytes(), original)
            unrelated = base / "other.kicad_pro"
            unrelated.write_text(project.read_text())
            mismatched = [str(unrelated) if part == str(project) else part for part in command]
            result = subprocess.run(mismatched, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assert_defect("PROJECT_ASSOCIATION", json.loads(output.read_text()))


if __name__ == "__main__":
    unittest.main()
