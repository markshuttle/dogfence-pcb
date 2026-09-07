"""Electrical regression tests; no KiCad, numpy, scratch files, or hardware required."""

from dataclasses import replace
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import math
import unittest

from scripts.analyze_limits import (
    Cable, Channel, CUT_SETS, Fault, IdealSourceShort, Source,
    assess_psu, branch_budget, main, resistor_allowance, simulate,
)


class ElectricalTests(unittest.TestCase):
    def assert_balanced(self, result):
        self.assertLess(result.kcl_error_a, 1.1e-10)
        self.assertLess(abs(result.power_balance_w), 1e-7)
        self.assertAlmostEqual(result.supply_current_a, result.return_current_a, places=8)
        self.assertTrue(all(math.isfinite(i) and i >= 0 for i in result.led_currents_a.values()))
        self.assertTrue(all(p >= 0 and math.isfinite(p) for p in result.element_power_w.values()))

    def test_healthy_41_station_baseline(self):
        result = simulate()
        self.assert_balanced(result)
        self.assertEqual(len(result.led_currents_a), 82)
        self.assertAlmostEqual(result.supply_current_a, 0.8477, places=4)
        self.assertAlmostEqual(result.led_currents_a["A", 0], 33.2 / 2200, places=12)
        self.assertAlmostEqual(result.led_currents_a["A", 40] * 1000, 8.04, places=2)
        self.assertAlmostEqual(result.supply_current_a, sum(result.led_currents_a.values()), places=9)
        for s in range(41):
            self.assertEqual(result.state(s), (True, True))
            self.assertAlmostEqual(result.led_currents_a["A", s], result.led_currents_a["C", s], places=10)
        self.assertGreater(result.voltages["B", 40], 0)
        self.assertAlmostEqual(result.voltages["B", 0], 0)

    def test_all_seven_cut_sets_in_all_40_spans(self):
        self.assertEqual(set(CUT_SETS), {"A", "B", "C", "AB", "AC", "BC", "ABC"})
        for span in range(40):
            for cores in CUT_SETS:
                with self.subTest(span=span, cores=cores):
                    result = simulate(cuts=tuple((c, span) for c in cores))
                    self.assert_balanced(result)
                    for s in range(41):
                        expected = ((True, True) if s <= span else
                                    ("A" not in cores and "B" not in cores,
                                     "C" not in cores and "B" not in cores))
                        self.assertEqual(result.state(s), expected)
                    self.assertAlmostEqual(result.supply_current_a, sum(result.led_currents_a.values()), places=8)

    def test_disconnected_islands_have_no_numerical_ground(self):
        result = simulate(cuts=tuple((c, span) for c in "ABC" for span in (4, 20)))
        self.assert_balanced(result)
        for c in "ABC":
            for s in range(5, 41):
                self.assertIsNone(result.voltages[c, s])
        for s in range(5, 41):
            for c in "AC":
                self.assertLess(result.led_currents_a[c, s], 1e-10)
        for core in ("A", "B", "C"):
            cut = simulate(cuts=((core, 12),))
            self.assertIsNone(cut.voltages[core, 40])
            self.assert_balanced(cut)

    def test_repair_and_retest_reveals_next_site(self):
        faults = {(c, s) for c in "ABC" for s in (0, 19, 39)}
        for first in (0, 19, 39):
            result = simulate(cuts=faults)
            transitions = [s for s in range(40) if result.state(s) != result.state(s + 1)]
            self.assertEqual(transitions, [first])
            faults.difference_update((c, first) for c in "ABC")
        result = simulate(cuts=faults)
        self.assertEqual([result.state(s) for s in range(41)], [(True, True)] * 41)
        for cuts in ((("A", 13), ("B", 26)), (("C", 13), ("A", 26))):
            before = simulate(cuts=cuts)
            repaired = simulate(cuts=cuts[1:])
            self.assertNotEqual(before.state(13), before.state(14))
            self.assertEqual(repaired.state(13), repaired.state(14))
            self.assertNotEqual(repaired.state(26), repaired.state(27))

    def test_legacy_ac_strap_backfeeds_an_open_core(self):
        for core in "AC":
            for span in (0, 19, 39):
                with self.subTest(core=core, span=span):
                    correct = simulate(cuts=((core, span),))
                    legacy = simulate(cuts=((core, span),), legacy_end_ac_strap=True)
                    self.assertLess(correct.led_currents_a[core, span + 1], 1e-10)
                    self.assertGreater(legacy.led_currents_a[core, span + 1], 1e-3)
                    self.assertTrue(all(legacy.state(s) == (True, True) for s in range(41)))
                    self.assert_balanced(legacy)

    def test_both_b_returns_mask_b_cut(self):
        for span in (0, 19, 39):
            correct = simulate(cuts=(("B", span),))
            bad = simulate(cuts=(("B", span),), both_b_returns=True)
            self.assertEqual(correct.state(span + 1), (False, False))
            self.assertTrue(all(bad.state(s) == (True, True) for s in range(41)))
            self.assert_balanced(bad)

    def test_asymmetric_rails_drops_and_station_override(self):
        options = dict(cable=Cable((5, 9, 12)), channel_a=Channel(led_v=1.8, diode_v=0.6),
                       channel_c=Channel(led_v=3.3, diode_v=1.1),
                       channel_overrides={("A", 25): Channel(resistor_ohm=2700)})
        result = simulate(**options)
        self.assert_balanced(result)
        self.assertNotAlmostEqual(result.led_currents_a["A", 40], result.led_currents_a["C", 40])
        self.assertLess(result.led_currents_a["A", 25], result.led_currents_a["A", 26])
        for cores in CUT_SETS:
            cut = simulate(**options, cuts=tuple((c, 22) for c in cores))
            self.assert_balanced(cut)
            self.assertEqual(cut.state(23), ("A" not in cores and "B" not in cores,
                                            "C" not in cores and "B" not in cores))

    def test_zero_cable_resistance_and_single_station_closed_forms(self):
        for n in (1, 5, 41):
            result = simulate(stations=n, cable=Cable((0, 0, 0)))
            self.assert_balanced(result)
            self.assertAlmostEqual(result.supply_current_a, n * 2 * 33.2 / 2200, places=10)
            self.assertAlmostEqual(result.resistor_power_w["A", 0], 33.2 ** 2 / 2200, places=12)
        cut = simulate(cable=Cable((0, 0, 0)), cuts=(("A", 2),))
        self.assertEqual(cut.state(3), (False, True))
        self.assert_balanced(cut)

    def test_nonzero_source_resistance_closed_form(self):
        n, rs = 5, 3.5
        expected = n * 2 * 33.2 / (2200 + n * 2 * rs)
        result = simulate(stations=n, cable=Cable((0, 0, 0)), source=Source(series_ohm=rs))
        self.assert_balanced(result)
        self.assertAlmostEqual(result.supply_current_a, expected, places=10)
        self.assertAlmostEqual(result.element_power_w["source:lead"], expected ** 2 * rs, places=10)

    def test_temperature_and_tolerance_inputs(self):
        cable = Cable((6.9, 7, 8), (0.01, -0.01, 0.05), 70)
        self.assertAlmostEqual(cable.span_resistances(0.1)[0], 6.9 * 1.01 * 1.1965 * 0.1)
        channel = Channel(resistor_error=-0.01, resistor_tcr_ppm=-50,
                          resistor_temperature_c=125, junction_temperature_c=70,
                          led_tempco_v_per_c=-0.002, diode_tempco_v_per_c=-0.001)
        r, led, diode = channel.values()
        self.assertAlmostEqual(r, 2200 * 0.99 * (1 - 50e-6 * 105))
        self.assertAlmostEqual(led, 2.0)
        self.assertAlmostEqual(diode, 0.65)
        source = Source(39.6, error_fraction=0.01, temperature_c=50,
                        tempco_per_c=0.0003, ripple_peak_v=0.1)
        self.assertAlmostEqual(source.voltage(), 40.39597)
        self.assert_balanced(simulate(cable=cable, source=source, channel_a=channel))
        self.assertLess(simulate(cable=Cable(temperature_c=70)).led_currents_a["A", 40],
                        simulate().led_currents_a["A", 40])

    def test_reverse_supply_has_no_forward_current_not_a_reverse_voltage_proof(self):
        for voltage in (-40.4, -36, 0, 2):
            result = simulate(source=Source(voltage))
            self.assert_balanced(result)
            self.assertAlmostEqual(result.supply_current_a, 0, places=9)
            self.assertTrue(all(i < 1e-10 for i in result.led_currents_a.values()))
            self.assertAlmostEqual(result.voltages["A", 40], voltage, places=8)

    def test_exact_hard_short_and_ideal_source_conflict(self):
        fault = Fault("hard", ("A", 0), ("B", 0))
        with self.assertRaises(IdealSourceShort):
            simulate(faults=(fault,))
        result = simulate(source=Source(series_ohm=0.25), faults=(fault,))
        self.assert_balanced(result)
        self.assertAlmostEqual(result.supply_current_a, 144, places=8)
        self.assertAlmostEqual(result.element_currents_a["hard"], 144, places=8)
        self.assertEqual(result.element_power_w["hard"], 0)

    def test_hard_resistive_and_ignited_faults_at_every_station(self):
        for s in range(41):
            for pair in ("AB", "CB", "AC"):
                for r, arc in ((0, 0), (10, 0), (100, 0), (0.1, 10), (0.1, 15)):
                    with self.subTest(station=s, pair=pair, ohm=r, arc=arc):
                        f = Fault("fault", (pair[0], s), (pair[1], s), r, arc)
                        result = simulate(source=Source(series_ohm=0.25), faults=(f,))
                        self.assert_balanced(result)
                        if pair == "AC":
                            i = result.element_currents_a["fault"]
                            if i is not None:
                                self.assertAlmostEqual(i, 0, places=8)
                        else:
                            self.assertGreater(result.element_currents_a["fault"], 0)

    def test_arc_follow_current_and_location_not_legacy_loop_resistance(self):
        source = Source(series_ohm=0.25)
        near = simulate(source=source, faults=(Fault("tube", ("A", 0), ("B", 0), 0.1, 10),))
        far = simulate(source=source, faults=(Fault("tube", ("A", 40), ("B", 40), 0.1, 10),))
        self.assertGreater(near.element_currents_a["tube"], 50)
        self.assertGreater(far.element_currents_a["tube"], 0.01)
        self.assertLess(far.supply_current_a, 2)
        isolated = simulate(source=source, cuts=tuple((c, 20) for c in "ABC"),
                            faults=(Fault("tube", ("A", 40), ("B", 40), 0.1, 10),))
        self.assertLess(abs(isolated.element_currents_a["tube"]), 1e-9)
        self.assert_balanced(isolated)

    def test_common_earth_two_tube_path_needs_no_negative_pe_bond(self):
        for arc in (10, 15):
            faults = (Fault("A_E", ("A", 40), ("E", 40), 0.1, arc),
                      Fault("B_E", ("E", 0), ("B", 0), 0.1, arc),
                      Fault("bonded_path", ("E", 40), ("E", 0), 1))
            result = simulate(faults=faults)
            self.assert_balanced(result)
            self.assertGreater(result.element_currents_a["A_E"], 0)
            self.assertAlmostEqual(result.element_currents_a["A_E"],
                                   result.element_currents_a["B_E"], places=9)
        # A missing DC return is a limiting model case, not an earthing proposal.
        single = simulate(faults=(Fault("A_E", ("A", 40), ("E", 40), 0.1, 10),))
        self.assertAlmostEqual(single.element_currents_a["A_E"], 0, places=9)
        self.assertIsNone(single.voltages["E", 40])

    def test_three_common_mode_tubes_at_five_earth_station_locations(self):
        for s in (0, 10, 20, 30, 40):
            for arc in (10, 15):
                faults = (Fault("A_E", ("A", s), ("E", s), 0.1, arc),
                          Fault("C_E", ("C", s), ("E", s), 0.1, arc),
                          Fault("E_B", ("E", s), ("B", s), 0.1, arc))
                with self.subTest(station=s, arc=arc):
                    result = simulate(source=Source(series_ohm=0.25), faults=faults)
                    self.assert_balanced(result)
                    a, c, b = (result.element_currents_a[n] for n in ("A_E", "C_E", "E_B"))
                    self.assertAlmostEqual(a, c, places=8)
                    self.assertAlmostEqual(a + c, b, places=8)

    def test_ac_short_can_mask_cut_but_ac_arc_is_not_always_energized(self):
        correct = simulate(cuts=(("A", 19),))
        masked = simulate(cuts=(("A", 19),), faults=(Fault("AC", ("A", 40), ("C", 40)),))
        self.assertEqual(correct.state(40), (False, True))
        self.assertEqual(masked.state(40), (True, True))
        self.assertLess(masked.element_currents_a["AC"], 0)
        self.assert_balanced(masked)

    def test_psu_continuous_capacity_and_hiccup_are_not_fuse_clearing(self):
        healthy = simulate()
        low_r = simulate(cable=Cable((0, 0, 0)))
        near = simulate(source=Source(series_ohm=0.25),
                        faults=(Fault("hard", ("A", 0), ("B", 0)),))
        small = lambda r: assess_psu(r, rated_a=1, rated_w=36)
        large = lambda r: assess_psu(r, rated_a=2.1, rated_w=75.6)
        self.assertEqual(small(healthy)["status"], "within-rated-envelope")
        self.assertEqual(small(low_r)["status"], "overload-threshold-band-CV-unqualified")
        self.assertEqual(large(low_r)["status"], "within-rated-envelope")
        self.assertEqual(large(near)["status"], "hiccup-expected-CV-invalid")
        self.assertEqual(assess_psu(low_r, rated_a=2.1, rated_w=75.6, derating=0.5)["status"],
                         "outside-rated-envelope-CV-unqualified")
        for r in (healthy, low_r, near):
            self.assertIsNone(small(r)["actual_overload_current_a"])
            self.assertIsNone(small(r)["fuse_clearing_s"])
        # At adjusted voltage, power as well as current must fit the rating.
        adjusted = replace(healthy, voltage_v=40.4, supply_current_a=0.95)
        self.assertEqual(small(adjusted)["status"], "outside-rated-envelope-CV-unqualified")

    def test_continuous_power_and_clamp_budget_do_not_claim_surge_safety(self):
        b = branch_budget(36)
        self.assertAlmostEqual(b["resistor_w"], 0.501018181818, places=10)
        leaky = branch_budget(36, shunt_a=0.001)
        self.assertAlmostEqual(leaky["led_a"], b["led_a"] - 0.001)
        self.assertAlmostEqual(leaky["resistor_w"], b["resistor_w"])
        clamped = branch_budget(40.39597, connector_v=4.3)
        self.assertGreater(clamped["branch_a"], 0.015)
        self.assertIsNone(clamped["led_a"])
        surge = branch_budget(950)
        self.assertGreater(surge["led_a"], 0.4)
        self.assertGreater(surge["resistor_w"], 400)
        minimum_r = Channel(led_v=0, diode_v=0, resistor_error=-0.01,
                            resistor_tcr_ppm=-50, resistor_temperature_c=125)
        upper = branch_budget(40.39597, minimum_r)
        self.assertLess(upper["led_a"], 0.020)
        self.assertGreater(upper["resistor_w"], resistor_allowance(70))
        self.assertEqual(resistor_allowance(70), 0.65)
        self.assertEqual(resistor_allowance(125), 0)
        self.assertEqual(resistor_allowance(155, standard_mode=False), 0)
        self.assertAlmostEqual(resistor_allowance(100), 0.65 * 25 / 55)
        with self.assertRaises(ValueError):
            branch_budget(36, shunt_a=0.1)

    def test_fail_closed_on_bad_inputs_or_nonconvergence(self):
        for options in ({"stations": 0}, {"stations": 1.5}, {"spacing_km": 0},
                        {"source": Source(float("nan"))}, {"source": Source(series_ohm=-1)},
                        {"source": Source(1e308, error_fraction=1e308)},
                        {"channel_a": Channel(resistor_ohm=0)},
                        {"cable": Cable((-1, 1, 1))}, {"cable": Cable((1, 2))},
                        {"cuts": (("B", 40),)}, {"cuts": (("D", 2),)},
                        {"cuts": (("AB", 2),)}, {"cuts": (("", 2),)},
                        {"cuts": (("B", True),)}, {"max_iterations": 1.5},
                        {"channel_overrides": {("AC", 2): Channel()}},
                        {"faults": (Fault("bad", ("A", 0), ("B", 41)),)},
                        {"faults": (Fault("bad", ("AB", 0), ("B", 1)),)},
                        {"faults": (Fault("bad", ("A", 0), ("B", 1), 0, 10),)},
                        {"faults": (Fault("rung:A:0", ("A", 0), ("B", 0), 1),)}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                simulate(**options)
        with self.assertRaises(ArithmeticError):
            simulate(max_iterations=1)

    def test_cli_json_parameters_and_failure_status(self):
        output = StringIO()
        with redirect_stdout(output):
            main(["--json", "--stations", "5", "--r-core", "7", "8", "9",
                  "--led-v", "2.8", "3.3", "--source-error", "0.01"])
        report = json.loads(output.getvalue())
        self.assertTrue(report["provisional"])
        self.assertEqual(report["cut_sweep"]["cases"], 28)
        self.assertEqual(report["inputs"]["cable"]["r20_ohm_per_km"], [7, 8, 9])
        self.assertAlmostEqual(report["loads"][0]["voltage_v"], 36.36)
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as failure:
            main(["--stations", "0"])
        self.assertEqual(failure.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
