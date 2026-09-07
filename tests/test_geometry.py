"""Controlled mutations of the authoritative PCB, never tmp/ or backup fixtures.

The positive fixture corrects only known nominal C1/W1/rule defects in memory.
These artificial land changes are test data, not proposed manufacturing artwork.
Historical defects are restored explicitly so the tests survive their real fixes.
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


def historical_smt(board):
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
            replace(p, "(size 5.2 2)")
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
        historical_smt(cls.positive)
        for ref in ("D1", "D2"):
            for num in ("1", "2"):
                replace(pad(cls.positive, ref, num), "(drill 1.1)")
        for ref in ("GDT_AB", "GDT_BC"):
            for num in ("1", "2"):
                # A simple nominal fixture with positive hole and annulus separation.
                replace(pad(cls.positive, ref, num), "(size 5.2 0.8)")
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
        self.assertEqual(len(report["measurements"]["component_hole_design"]), 26)
        checker = GeometryCheck(self.authoritative)
        checker.read_board()
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

    def test_selected_fit_holes_cannot_revert_to_unsupported_sizes(self):
        for ref, minimum in COMPONENT_HOLE_MINIMA.items():
            with self.subTest(ref=ref):
                board = deepcopy(self.positive)
                replace(pad(board, ref, "1"), f"(drill {minimum - 0.1:.2f})")
                self.assert_defect("C1_DIODE_DRILL" if ref in ("D1", "D2") else "COMPONENT_FIT_DRILL",
                                   self.report(board))

    def test_body_courtyards_include_declared_pose_and_assembly_margin(self):
        for ref in (*COMPONENT_HOLE_MINIMA, "GDT_AB", "GDT_BC"):
            with self.subTest(ref=ref):
                fp = footprint(self.authoritative, ref)
                boxes = {rect.one("layer").atoms()[0]: rect for rect in fp.children("fp_rect")}
                body, courtyard = boxes["F.Fab"], boxes["F.CrtYd"]
                for edge, direction in (("start", -1), ("end", 1)):
                    for b, c in zip(body.one(edge).atoms(), courtyard.one(edge).atoms()):
                        self.assertGreaterEqual(direction * (float(c) - float(b)) + 1e-9, 0.10 + 0.25)

    def test_adopted_pin_envelopes_include_independent_pattern_allowance(self):
        position_budget = 2 * (math.hypot(0.05, 0.05) + 0.05)
        envelopes = {"J_IN": math.hypot(1.1, 1.0), "J_LED_A": math.hypot(1.15, 1.0),
                     "R1": 0.9, "GDT_AC": 0.9, "GDT_A_E": 1.05}
        for ref, maximum in envelopes.items():
            with self.subTest(ref=ref):
                hole = float(pad(self.authoritative, ref, "1").one("drill").atoms()[0])
                self.assertGreaterEqual(hole - 0.08 - maximum - position_budget, 0.1)

    def test_reviewed_c1_w1_defects_remain_reproducible_after_layout_fixes(self):
        historical_smt(self.board)
        for ref in ("D1", "D2"):
            for num in ("1", "2"):
                replace(pad(self.board, ref, num), "(drill 0.9)")
        report = self.report()
        self.assertEqual(len(self.assert_defect("C1_DIODE_DRILL", report)), 4)
        mask = self.assert_defect("W1_VIA_MASK", report)
        paste = self.assert_defect("W1_VIA_PASTE", report)
        self.assertEqual(len(mask), 12)  # B's three vias meet both SMT GDTs.
        self.assertEqual(len(paste), 12)
        self.assertEqual(len({tuple(d["position_mm"]) for d in mask}), 9)
        self.assertEqual(len({d["aperture"] for d in mask}), 4)
        self.assertTrue(all(abs(d["measured_mm"] + 0.19) < 1e-6 for d in mask + paste))

    def test_diode_drill_and_component_ring_are_independent(self):
        replace(pad(self.board, "D1", "2"), "(drill 1.0)")
        self.assert_defect("C1_DIODE_DRILL")
        replace(pad(self.board, "D1", "2"), "(drill 1.1)")
        replace(pad(self.board, "D1", "2"), "(size 1.6 1.6)")
        self.assert_defect("COMPONENT_RING")

    def test_offset_hole_uses_true_ring_not_min_size_only(self):
        replace(pad(self.board, "D1", "1"), "(drill 1.1 (offset 0.4 0))")
        self.assertAlmostEqual(self.assert_defect("COMPONENT_RING")[0]["measured_mm"], 0.15)

    def test_slot_ring_and_arbitrary_pad_rotation(self):
        p = pad(self.board, "R1", "2")
        p.values[2] = Atom("oval")
        replace(p, "(size 2.8 2.4)")
        replace(p, "(drill oval 1.6 1.4)")
        replace(p, "(at 7.62 0 37)")
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
        report = self.assert_pass()
        records = report["measurements"]["via_apertures"]
        self.assertTrue(any(r["annulus_exposed"] and r["mask_barrier_mm"] >= MIN_MASK_BARRIER
                            and r["copper_hole_gap_mm"] < 0 for r in records if r["layer"] == "F.Mask"))
        replace(pad(self.board, "GDT_AB", "1"), "(solder_mask_margin 0)")
        self.assert_defect("W1_VIA_MASK")  # KiCad 9 zero is an override, not inheritance.

    def test_board_margin_inheritance_and_pad_priority(self):
        historical_smt(self.board)
        replace(self.board.one("setup"), "(pad_to_mask_clearance -0.4)")
        replace(self.board.one("setup"), "(pad_to_paste_clearance -0.4)")
        self.assert_pass()
        fp = footprint(self.board, "GDT_AB")
        replace(fp, "(solder_mask_margin 0.2)")
        for p in fp.children("pad"):
            replace(p, "(solder_mask_margin -0.4)")
        self.assert_pass()  # Not the sum of board, footprint and pad overrides.
        remove(fp.children("pad")[0], "solder_mask_margin")
        self.assert_defect("W1_VIA_MASK")

    def test_mask_and_paste_are_independent(self):
        for field, code in (("solder_mask_margin", "W1_VIA_MASK"),
                            ("solder_paste_margin", "W1_VIA_PASTE")):
            with self.subTest(field=field):
                board = deepcopy(self.positive)
                replace(pad(board, "GDT_AB", "1"), f"({field} 0.6)")
                self.assert_defect(code, self.report(board))

    def test_mask_barrier_and_untented_annulus(self):
        p = pad(self.board, "GDT_AB", "1")
        replace(p, "(solder_mask_margin 0.36)")  # 0.41 - 0.36 = 0.05 mm, no drill overlap.
        self.assert_defect("W1_MASK_BARRIER")
        remove(p, "solder_mask_margin")
        via = next(v for v in self.board.children("via") if v.one("at").atoms() == ["114", "114.88"])
        replace(via, "(tenting back)")
        self.assert_defect("W1_MASK_BARRIER")  # Only 0.01 mm between open annulus and land.

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
        replace(self.board.one("setup"), "(solder_mask_min_width 0.7)")
        self.assert_defect("W1_MASK_BARRIER")

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
        replace(opening, "(at 0 -3.3)")  # Touches the copper only along one edge.
        self.assert_defect("MISSING_SMT_APERTURE")

    def test_smd_roundrect_corner_and_rotation_at_via(self):
        # The drill misses the rounded corner but intersects the rotated square.
        delta = move((1.5, 1.5), angle=31)
        origin = (112.5 - delta[0], 114.88 - delta[1])
        extra = parse(f'''(footprint "corner fixture" (layer "F.Cu") (at {origin[0]} {origin[1]})
            (property "Reference" "X2")
            (pad "" smd roundrect (at 0 0 31) (size 2.4 2.4) (roundrect_rratio 0.5)
                (layers "F.Mask")))''')
        self.board.values.append(extra)
        self.assert_pass()  # 1.5*sqrt(2) - 1.2 - 0.5 > 0.1 mm.
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
            pad(board, "D1", "1").values.append(parse(change))
            self.assert_defect("UNSUPPORTED_GEOMETRY", self.report(board))
        pad(self.board, "D1", "1").values[2] = Atom("custom")
        self.assert_defect("UNSUPPORTED_GEOMETRY")

    def test_malformed_numeric_and_duplicate_geometry_fail_closed(self):
        for change in ("(size nan 2.2)", "(size 1_0 2.2)", "(size 2.2)", "(size 1e308 1e308)",
                       "(drill 1e308)", "(at 0 1e308)", "(solder_mask_margin 1e308)"):
            with self.subTest(change=change):
                board = deepcopy(self.positive)
                replace(pad(board, "D1", "1"), change)
                self.assert_defect("INVALID_STRUCTURE", self.report(board))
        pad(self.board, "D1", "1").values.append(parse("(size 2.2 2.2)"))
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
            self.assertTrue(json.loads(output.read_text())["ok"])
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
