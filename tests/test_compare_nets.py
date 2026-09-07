import contextlib
import io
from pathlib import Path
import tempfile
import unittest

from scripts import compare_nets as nets


BOARD = '''(kicad_pcb (version 20241229) (generator "pcbnew")
  (general (thickness 1.6)) (paper "A4")
  (title_block (title "Fixture") (rev "fixture-1"))
  (layers (0 "F.Cu" signal) (2 "B.Cu" signal)
    (13 "F.Paste" user) (15 "B.Paste" user)
    (5 "F.SilkS" user) (7 "B.SilkS" user)
    (1 "F.Mask" user) (3 "B.Mask" user)
    (25 "Edge.Cuts" user) (35 "F.Fab" user))
  (setup (pad_to_mask_clearance 0) (tenting front back))
  (net 0 "") (net 1 "POWER") (net 2 "Net-(D1-A)")
  (footprint "Local:THT" (layer "F.Cu") (at 10 20)
    (property "Reference" "R1") (property "Value" "1k")
    (property "MPN" "R1K") (property "Manufacturer" "Example") (property "LCSC Part #" "C123")
    (attr through_hole)
    (pad "1" thru_hole circle (at -1.5 0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "POWER"))
    (pad "2" thru_hole circle (at 1.5 0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 2 "Net-(D1-A)")))
  (footprint "Local:SMT" (layer "F.Cu") (at 20 30 90)
    (property "Reference" "J_LED_A") (property "Value" "SMT")
    (property "MPN" "SMT1") (property "Manufacturer" "Example") (property "LCSC Part #" "C456")
    (attr smd)
    (pad "1" smd rect (at 0 -1 90) (size 2 1) (layers "F.Cu" "F.Mask" "F.Paste") (net 1 "POWER"))
    (pad "2" smd rect (at 0 1 90) (size 2 1) (layers "F.Cu" "F.Mask" "F.Paste") (net 2 "Net-(D1-A)")))
  (footprint "Local:SMT" (layer "F.Cu") (at 20 40 270)
    (property "Reference" "J_LED_C") (property "Value" "SMT")
    (property "MPN" "SMT1") (property "Manufacturer" "Example") (property "LCSC Part #" "C456")
    (attr smd)
    (pad "1" smd rect (at 0 1 270) (size 2 1) (layers "F.Cu" "F.Mask" "F.Paste") (net 1 "POWER"))
    (pad "2" smd rect (at 0 -1 270) (size 2 1) (layers "F.Cu" "F.Mask" "F.Paste") (net 2 "Net-(D1-A)")))
  (footprint "Local:THT" (layer "F.Cu") (at 30 50)
    (property "Reference" "R_DNP") (property "Value" "1k")
    (attr through_hole dnp)
    (pad "1" thru_hole circle (at -1.5 0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 1 "POWER"))
    (pad "2" thru_hole circle (at 1.5 0) (size 2.2 2.2) (drill 1.0) (layers "*.Cu" "*.Mask") (net 2 "Net-(D1-A)")))
  (footprint "Local:Hole" (layer "F.Cu") (at 3 3)
    (property "Reference" "H1") (property "Value" "Hole")
    (attr exclude_from_bom exclude_from_pos_files)
    (pad "" np_thru_hole circle (at 0 0) (size 3.2 3.2) (drill 3.2) (layers "*.Cu" "*.Mask")))
  (via (at 30 20) (size 1.8) (drill 1.0) (layers "F.Cu" "B.Cu") (net 1))
  (segment (start 8.5 20) (end 30 20) (width 1) (layer "F.Cu") (net 1))
  (segment (start 8.5 20) (end 30 20) (width 1) (layer "B.Cu") (net 1))
  (gr_rect (start 0 0) (end 60 60) (stroke (width 0.15) (type solid)) (fill none) (layer "Edge.Cuts")))
'''


def xml_netlist():
    parts = [("R1", "THT", "1k"), ("J_LED_A", "SMT", "SMT"), ("J_LED_C", "SMT", "SMT"),
             ("R_DNP", "THT", "1k"), ("H1", "Hole", "Hole")]
    result = ['<?xml version="1.0"?><export version="E"><components>']
    for ref, part, val in parts:
        mpn, code = ("R1K", "C123") if part == "THT" else ("SMT1", "C456")
        result.append(f'<comp ref="{ref}"><value>{val}</value><footprint>Local:{part}</footprint>'
                      f'<libsource lib="Local" part="{part}"/><fields>'
                      f'<field name="MPN">{mpn}</field><field name="Manufacturer">Example</field>'
                      f'<field name="LCSC Part #">{code}</field></fields>'
                      + ('<property name="dnp"/>' if ref == "R_DNP" else "") + '</comp>')
    result.append('</components><libparts>')
    for part in ("THT", "SMT", "Hole"):
        pins = '<pins><pin num="1"/><pin num="2"/></pins>' if part != "Hole" else ""
        result.append(f'<libpart lib="Local" part="{part}">{pins}</libpart>')
    result.append('</libparts><nets>')
    for code, name, pin in ((1, "POWER", 1), (2, "Net-(D1-A)", 2)):
        result.append(f'<net code="{code}" name="{name}">')
        for ref, part, val in parts:
            if part != "Hole":
                result.append(f'<node ref="{ref}" pin="{pin}"/>')
        result.append('</net>')
    result.append('</nets></export>')
    return "\n".join(result)


def ipc_text(board):
    lines = ["P  CODE 00", "P  UNITS CUST 0", "P  arrayDim   N"]
    for p in board.pads:
        kind = "367" if p.kind == "np_thru_hole" else "327" if p.kind == "smd" else "317"
        net = nets.ipc_alias(p.net) if p.net else "N/C"
        hole = f"D{round(p.drill / .00254):04d}{'U' if p.kind == 'np_thru_hole' else 'P'}" if p.drill else " " * 6
        access = 1 if p.kind == "smd" else 0
        height = 0 if p.shape == "circle" else round(p.height / .00254)
        lines.append(f"{kind}{net:<14}   {p.ref[:6]:<6}{'-' if p.pin else ' '}{p.pin[:4]:<4}"
                     f"{'M' if p.kind == 'via' else ' '}{hole}A{access:02d}"
                     f"X{round(p.x / .00254):+07d}Y{round(-p.y / .00254):+07d}"
                     f"X{round(p.width / .00254):04d}Y{height:04d}R{round(-p.rotation % 360):03d}S0")
    return "\n".join(lines + ["999", ""])


class NetComparisonTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.xml = self.write("schematic.xml", xml_netlist())

    def write(self, name, data):
        path = self.root / name
        path.write_text(data, encoding="utf-8")
        return path

    def board(self):
        return nets.read_board(self.write("pcb.kicad_pcb", BOARD))

    def test_xml_positive_complete_membership(self):
        parsed = nets.parse_netlist(self.xml)
        self.assertEqual(set(parsed), {"POWER", "Net-(D1-A)"})
        self.assertEqual(sum(map(len, parsed.values())), 8)
        self.assertEqual(nets.differences(parsed, parsed), [])

    def test_empty_unrecognized_and_malformed_inputs_fail(self):
        for content in ("", " ", "hello", "<export>", '<export version="E"><nets/></export>',
                        '(export (nets))', '(export (nets', '<export version="E"/>'):
            with self.subTest(content=content), self.assertRaises((nets.VerificationError, ValueError)):
                nets.parse_netlist(self.write("bad.net", content))

    def test_missing_terminal_cannot_pass_even_against_itself(self):
        bad = xml_netlist().replace('<node ref="R1" pin="1"/>', '')
        with self.assertRaisesRegex(nets.VerificationError, "terminal inventory"):
            nets.parse_netlist(self.write("missing.xml", bad))

    def test_duplicate_and_unknown_terminals_rejected(self):
        for replacement in ('<node ref="R1" pin="1"/><node ref="R1" pin="1"/>',
                            '<node ref="UNKNOWN" pin="1"/>', '<node ref="R1"/>'):
            bad = xml_netlist().replace('<node ref="R1" pin="1"/>', replacement)
            with self.subTest(replacement=replacement), self.assertRaises(nets.VerificationError):
                nets.parse_netlist(self.write("bad.xml", bad))

    def test_duplicate_net_names_and_codes_rejected(self):
        for old, new in (('code="2"', 'code="1"'), ('name="Net-(D1-A)"', 'name="POWER"')):
            with self.subTest(old=old), self.assertRaises(nets.VerificationError):
                nets.parse_netlist(self.write("bad.xml", xml_netlist().replace(old, new)))

    def test_wrong_net_detected_not_just_terminal_count(self):
        parsed = nets.parse_netlist(self.xml)
        swapped = {name: set(nodes) for name, nodes in parsed.items()}
        swapped["POWER"].remove(("R1", "1"))
        swapped["POWER"].add(("R1", "2"))
        swapped["Net-(D1-A)"].remove(("R1", "2"))
        swapped["Net-(D1-A)"].add(("R1", "1"))
        self.assertEqual(len(nets.differences(parsed, swapped)), 2)

    def test_no_success_on_parse_failure(self):
        invalid = self.write("bad.xml", "garbage")
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            self.assertNotEqual(nets.compare(invalid, invalid), 0)
        self.assertNotIn("matches", out.getvalue())

    def test_native_pcb_membership_and_mirrored_pads(self):
        board = self.board()
        self.assertEqual(nets.differences(nets.parse_netlist(self.xml), board.nets), [])
        for ref, y in (("J_LED_A", 30), ("J_LED_C", 40)):
            self.assertAlmostEqual(board.footprints[ref].pads[0].x, 19)
            self.assertAlmostEqual(board.footprints[ref].pads[0].y, y)
        self.assertEqual(len(board.pads), 10)

    def test_native_pcb_unknown_pad_net_fails(self):
        bad = BOARD.replace('(layers "*.Cu" "*.Mask") (net 1 "POWER")',
                            '(layers "*.Cu" "*.Mask") (net 1 "WRONG")', 1)
        self.assertNotEqual(bad, BOARD)
        with self.assertRaises(nets.VerificationError):
            nets.read_board(self.write("bad.kicad_pcb", bad))

    def test_nonzero_origin_rejected(self):
        bad = BOARD.replace('(setup ', '(setup (aux_axis_origin 1 2) ')
        with self.assertRaisesRegex(nets.VerificationError, "origin"):
            nets.read_board(self.write("bad.kicad_pcb", bad))

    def test_roundrect_ratio_is_retained_and_validated(self):
        source = BOARD.replace('(pad "1" smd rect', '(pad "1" smd roundrect', 1)
        for ratio in (0, .2, .25, .5):
            text = source.replace('(size 2 1)', f'(size 2 1) (roundrect_rratio {ratio})', 1)
            board = nets.read_board(self.write("round.kicad_pcb", text))
            self.assertEqual(board.footprints["J_LED_A"].pads[0].roundrect_ratio, ratio)
        board = nets.read_board(self.write("default.kicad_pcb", source))
        self.assertEqual(board.footprints["J_LED_A"].pads[0].roundrect_ratio, .25)
        for ratio in ("-0.1", "0.51", "nan", "inf", "invalid"):
            text = source.replace('(size 2 1)', f'(size 2 1) (roundrect_rratio {ratio})', 1)
            with self.subTest(ratio=ratio), self.assertRaises(nets.VerificationError):
                nets.read_board(self.write("bad.kicad_pcb", text))

    def test_ipc_resolves_truncated_led_references_and_case_aliases(self):
        board = self.board()
        result = nets.compare_ipc(self.write("pcb.d356", ipc_text(board)), board)
        self.assertEqual(result["records"], 10)
        self.assertEqual(result["aliases"]["Net-(D1-A)"], "NET-(D1-A)")

    def test_ipc_wrong_net_missing_record_and_flipped_y_fail(self):
        board = self.board()
        text = ipc_text(board)
        for bad in (text.replace("POWER         ", "WRONG         ", 1),
                    "\n".join(text.splitlines()[:3] + text.splitlines()[4:]) + "\n",
                    text.replace("Y-", "Y+"), text.replace("999\n", ""), text.replace("CUST 0", "CUST 1"),
                    text.replace("D0394P", "D0354P", 1)):
            with self.subTest(bad=bad[:100]), self.assertRaises(nets.VerificationError):
                nets.compare_ipc(self.write("bad.d356", bad), board)

    def test_ipc_alias_collision_fails_instead_of_guessing(self):
        board = self.board()
        board.nets["power"] = {("X", "1")}
        with self.assertRaisesRegex(nets.VerificationError, "alias collision"):
            nets.compare_ipc(self.write("pcb.d356", ipc_text(board)), board)

    def test_sexpr_netlist_positive_and_truncation(self):
        content = '''(export (version "E")
          (components (comp (ref "R1") (libsource (lib "L") (part "R"))))
          (libparts (libpart (lib "L") (part "R") (pins (pin (num "1")))))
          (nets (net (code "1") (name "N") (node (ref "R1") (pin "1")))))'''
        self.assertEqual(nets.parse_netlist(self.write("native.net", content)), {"N": {("R1", "1")}})
        with self.assertRaises((nets.VerificationError, ValueError)):
            nets.parse_netlist(self.write("truncated.net", content[:-1]))


if __name__ == "__main__":
    unittest.main()
