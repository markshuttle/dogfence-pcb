"""Focused conditional-bound regressions; no network, KiCad or shared staging."""

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest

from scripts import analyze_limits as dc
from scripts.design_bounds import (
    CONTACT_OHM_PER_SPAN, R20_MAX_OHM_PER_KM, analyze, cable_corner,
    effective_rtheta_limit, main, normal_cases, resistor_bounds, thermal_envelope,
)


class DesignBoundsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = analyze()

    def test_standard_metal_coated_value_and_separate_contact_temperature(self):
        self.assertEqual(R20_MAX_OHM_PER_KM, 8.21)
        self.assertAlmostEqual(cable_corner(20, (0, 0, 0)).r20_ohm_per_km[0] * 4, 32.84)
        self.assertAlmostEqual(cable_corner(70, (0, 0, 0)).r20_ohm_per_km[0] * 4, 39.29306)
        hot = cable_corner(70, (0.01, 0.02, 0.03)).span_resistances(0.1)
        cold = cable_corner(-30, (0.01, 0.02, 0.03)).span_resistances(0.1)
        for actual, contact in zip(hot, (0.01, 0.02, 0.03)):
            self.assertAlmostEqual(actual, 8.21 * 1.1965 * 0.1 + contact)
        self.assertAlmostEqual(hot[2] - hot[0], 0.02)
        self.assertAlmostEqual(cold[2] - cold[0], 0.02)
        self.assertEqual(CONTACT_OHM_PER_SPAN, (0.025,) * 3)
        self.assertAlmostEqual(self.report["cable"]["effective_4km_core_ohm_ABC"][0], 40.29306)

    def test_resistor_tolerance_tcr_cold_hot_and_zero_spread(self):
        low, high = resistor_bounds()
        self.assertAlmostEqual(low, 2156.22)
        self.assertAlmostEqual(high, 2244.22)
        for temperature in (-55, -30, 20, 25, 125):
            for tolerance in (-0.01, 0.01):
                for tcr in (-100, 100):
                    selected = dc.Channel(resistor_error=tolerance, resistor_tcr_ppm=tcr,
                                          resistor_temperature_c=temperature).values()[0]
                    self.assertLessEqual(low, selected)
                    self.assertGreaterEqual(high, selected)
        self.assertEqual(resistor_bounds(tolerance_fraction=0, tcr_ppm=0), (2200, 2200))
        self.assertEqual(resistor_bounds(minimum_c=25, maximum_c=25), (2178, 2222))
        self.assertAlmostEqual(resistor_bounds(minimum_c=-55, maximum_c=-30)[0],
                               2200 * 0.99 * (1 - 100e-6 * 80))
        resistor = self.report["resistor"]
        self.assertEqual(resistor["mpn"], "PS122WF2201T4E")
        self.assertEqual(resistor["manufacturer"], "Uni-Royal")
        self.assertEqual(resistor["package"], "2512 SMT")
        self.assertNotIn("lead_material", resistor)
        self.assertEqual(resistor["screen_temperature_range_c"], [-30, 125])
        self.assertEqual(resistor["reference_temperature_c"], 25)
        self.assertEqual(resistor["tcr_test_temperatures_c"], [-55, 125])
        self.assertEqual(resistor["tcr_abs_ppm_per_c"], 100)
        self.assertEqual(resistor["p70_w"], 2)
        self.assertEqual(resistor["zero_power_ambient_c"], 155)
        self.assertNotIn("pr02_", json.dumps(self.report))
        self.assertEqual(resistor["family_max_working_voltage_v"], 500)
        self.assertAlmostEqual(resistor["rated_working_voltage_at_p70_v"], math.sqrt(2 * 2200))
        self.assertEqual(resistor["family_max_overload_voltage_v"], 1000)
        self.assertEqual(resistor["dielectric_withstanding_voltage_v"], 500)
        self.assertAlmostEqual(resistor["short_time_overload_test_v"], 165.83123951777)
        self.assertEqual(resistor["short_time_overload_test_s"], 5)
        self.assertIn("one-pulse power and voltage curves", " ".join(self.report["limitations"]))
        self.assertIn("neither establishes repetitive surge or board-lightning qualification",
                      " ".join(self.report["limitations"]))

    def test_nominal_comparison_and_nonuniform_vf_is_worse_than_uniform(self):
        rows = self.report["normal_cases"]
        old = rows["historical_36V_2.8V_6.9_nominal"]
        self.assertAlmostEqual(old["source_a"], 0.847705, places=6)
        self.assertAlmostEqual(old["led_min_ma"], 8.0448, places=4)
        self.assertGreater(old["A40_ma"], rows["standard_max_20C_nominal_load"]["A40_ma"])
        self.assertGreater(rows["standard_max_20C_nominal_load"]["A40_ma"],
                           rows["declared_cable_nominal_load"]["A40_ma"])
        self.assertGreater(rows["uniform_high_vf_rmax"]["A40_ma"], rows["nonuniform_vf_only_A40"]["A40_ma"])
        self.assertGreater(rows["nonuniform_vf_only_A40"]["A40_ma"], rows["nonuniform_A40"]["A40_ma"])
        self.assertLess(rows["nonuniform_A40"]["A40_ma"], rows["nonuniform_A40"]["C40_ma"])
        self.assertLess(rows["nonuniform_A40_other_rail_zero"]["A40_ma"], rows["nonuniform_A40"]["A40_ma"])
        self.assertAlmostEqual(rows["nonuniform_A40"]["A40_ma"], rows["nonuniform_C40"]["C40_ma"])
        self.assertAlmostEqual(rows["uniform_high_vf_rmax"]["A40_ma"], 5.7170665239, places=9)
        self.assertAlmostEqual(rows["nonuniform_A40"]["A40_ma"], 4.2776194086, places=9)
        self.assertAlmostEqual(rows["nonuniform_A40_other_rail_zero"]["A40_ma"], 3.7936689719, places=9)
        for row in rows.values():
            self.assertLess(row["kcl_error_a"], 1.1e-10)
            self.assertLess(abs(row["power_balance_w"]), 1e-7)

    def test_independent_comparison_floor_and_zero_cable_closed_form_upper(self):
        bounds = self.report["current_bounds"]
        minimum = bounds["conditional_all_station_led_min_ma"]
        maximum = bounds["conditional_all_station_led_max_ma"]
        self.assertAlmostEqual(bounds["conditional_all_station_branch_min_ma"], 0.389146872551, places=9)
        self.assertAlmostEqual(minimum, 0.339146872551, places=9)
        self.assertAlmostEqual(maximum, 1000 * dc.ADJUSTMENT_SCREEN_V / 2156.22)
        self.assertAlmostEqual(bounds["conditional_total_current_upper_a"], 82 * maximum / 1000)
        self.assertAlmostEqual(bounds["local_B_tap_current_upper_a"], 2 * maximum / 1000)
        for name, row in self.report["normal_cases"].items():
            if name != "historical_36V_2.8V_6.9_nominal":
                self.assertGreaterEqual(row["led_min_after_clamp_leakage_ma"] + 1e-8, minimum)
                self.assertLessEqual(row["led_max_ma"], maximum + 1e-8)
        low, high = resistor_bounds()
        overrides = {(core, station): dc.Channel(
            resistor_ohm=low if station % 2 else high,
            led_v=3.3 if station % 3 else 0, diode_v=1.9 if core == "A" else 0)
            for station in range(41) for core in "AC"}
        for voltage in (35, dc.ADJUSTMENT_SCREEN_V):
            result = dc.simulate(source=dc.Source(voltage), cable=dc.Cable((2, 9, 6)),
                                 channel_overrides=overrides)
            self.assertGreaterEqual((min(result.led_currents_a.values()) - dc.CLAMP_LEAKAGE_SCREEN_A)
                                    * 1000, minimum)
            self.assertLessEqual(max(result.led_currents_a.values()) * 1000, maximum)
            self.assertLessEqual(max(result.voltages["B", s] for s in range(41)),
                                 bounds["comparison_B_rail_upper_v"])
        # Deliberately unequal service contact ceilings and junction drops.
        varied = analyze(contact_ohm_per_span=(0.0, 0.1, 0.05), high_drop_v=5.0)
        self.assertNotAlmostEqual(varied["normal_cases"]["nonuniform_A40"]["A40_ma"],
                                  varied["normal_cases"]["nonuniform_C40"]["C40_ma"])
        self.assertLessEqual(varied["current_bounds"]["conditional_all_station_led_min_ma"],
                             varied["normal_cases"]["nonuniform_A40"]["A40_ma"])
        self.assertEqual(analyze(source_min_v=0)["current_bounds"]["conditional_all_station_led_min_ma"], 0)
        self.assertEqual(analyze(high_drop_v=60)["current_bounds"]["conditional_all_station_led_min_ma"], 0)

    def test_historical_pr02_mbe_screens_are_not_selected_limits(self):
        # Historical 20 C reference is explicit, not a compatibility mode in PS12 helpers.
        pr02_min = 2200 * 0.99 * (1 - 250e-6 * (125 - 20))
        self.assertAlmostEqual(pr02_min, 2120.8275)
        self.assertAlmostEqual(dc.branch_budget(dc.ADJUSTMENT_SCREEN_V, dc.Channel(
            resistor_ohm=pr02_min, led_v=0, diode_v=0))["resistor_w"], 0.7694328710095, places=12)
        r_min = 2200 * 0.99 * (1 - 50e-6 * (125 - 20))
        r_max = 2200 * 1.01 * (1 + 50e-6 * (125 - 20))
        low = dc.Channel(resistor_ohm=r_min, led_v=0, diode_v=0)
        high = dc.Channel(resistor_ohm=r_max, led_v=4.4, diode_v=0)
        self.assertAlmostEqual(r_min, 2166.5655)
        self.assertAlmostEqual(r_max, 2233.6655)
        self.assertAlmostEqual(dc.branch_budget(dc.ADJUSTMENT_SCREEN_V, low)["resistor_w"],
                               0.753190, places=6)
        old = dc.branch_budget(37, low)
        self.assertAlmostEqual(old["branch_a"] * 82, 1.400373, places=6)
        self.assertAlmostEqual(old["resistor_w"], 0.631876, places=6)
        cable = cable_corner()
        options = dict(source=dc.Source(35), channel_a=low, channel_c=low)
        nonuniform = dc.simulate(**options, cable=cable, channel_overrides={("A", 40): high})
        self.assertAlmostEqual(nonuniform.led_currents_a["A", 40] * 1000, 4.6681, places=4)
        rail_r = cable.r20_ohm_per_km[0]
        positive = dc.simulate(**options, cable=dc.Cable((rail_r, 0, 0)))
        returned = dc.simulate(**(options | {"source": dc.Source(37)}), cable=dc.Cable((0, rail_r, 0)))
        old_floor_ma = 1000 * (positive.voltages["A", 40] - returned.voltages["B", 40] - 4.4) / r_max
        self.assertAlmostEqual(old_floor_ma, 1.4945906084, places=9)
        self.assertGreater(old_floor_ma, self.report["current_bounds"]["conditional_all_station_led_min_ma"])

    def test_clamp_diversion_has_no_extra_psu_path_or_positive_regulation(self):
        diode = self.report["diodes"]
        self.assertEqual(diode["D1_D2_D3_D4_mpn"], "BYG23T-M3/TR")
        self.assertEqual(diode["D3_D4_cathodes"], "LED_A_POS / LED_C_POS after D1/D2")
        self.assertEqual(diode["D3_D4_anodes"], "WIRE_B")
        self.assertFalse(diode["positive_voltage_regulation"])
        self.assertFalse(diode["extra_input_shunt_load"])
        self.assertEqual(diode["reverse_leakage_max_at_1300V_25C_a"], 5e-6)
        self.assertEqual(diode["reverse_leakage_max_at_1300V_125C_a"], 50e-6)
        self.assertAlmostEqual(self.report["current_bounds"]["high_total_vf_screen_v"], 3.3 + 1.9)
        for row in self.report["normal_cases"].values():
            for key in ("led_min", "A40", "C40"):
                self.assertAlmostEqual(row[key + "_after_clamp_leakage_ma"],
                                       max(0, row[key + "_ma"] - 0.05))
        # Leakage partitions a rung, not 82 new feed loads. Zero-drop upper includes all branch energy.
        upper = self.report["normal_cases"]["zero_cable_upper"]
        self.assertAlmostEqual(upper["source_a"], 82 * dc.ADJUSTMENT_SCREEN_V / 2156.22)
        self.assertAlmostEqual(upper["source_w"], 62.057869866597, places=9)
        floor = self.report["current_bounds"]["conditional_all_station_led_min_ma"]
        self.assertGreater(floor, 0.001)  # Numerical ON margin only, NOT daylight or dark-state acceptance.
        lower_case = normal_cases()["nonuniform_A40"]
        result = dc.simulate(**lower_case)
        local = result.voltages["A", 40] - result.voltages["B", 40]
        budget = dc.branch_budget(local, lower_case["channel_overrides"]["A", 40], shunt_a=50e-6)
        self.assertAlmostEqual(budget["led_a"] * 1000,
                               self.report["normal_cases"]["nonuniform_A40"]["A40_after_clamp_leakage_ma"])

    def test_all_cuts_reuse_existing_sweep_at_nonuniform_corner(self):
        inputs = normal_cases()["nonuniform_A40_other_rail_zero"]
        sweep = dc.cut_sweep(**inputs, shunt_max_a=dc.CLAMP_LEAKAGE_SCREEN_A)
        self.assertEqual(sweep["cases"], 280)
        self.assertLess(sweep["max_kcl_a"], 1.1e-10)
        self.assertLess(sweep["max_power_error_w"], 1e-7)
        self.assertEqual(sweep["shunt_diversion_bound_a"], 50e-6)

    def test_branch_power_table_and_no_below_70C_rating_extrapolation(self):
        nominal, at36, at37, upper, adjustment = self.report["source_end_branches"]
        self.assertAlmostEqual(nominal["resistor_w"], 0.501018181818)
        self.assertAlmostEqual(nominal["two_resistors_and_rectifiers_w"], 1.023163636364)
        self.assertAlmostEqual(nominal["two_resistors_rectifiers_clamps_upper_w"], 1.023373636364)
        self.assertAlmostEqual(at36["resistor_w"], 36 * 36 / 2156.22)
        self.assertAlmostEqual(at37["resistor_w"], 37 ** 2 / 2156.22, places=12)
        self.assertAlmostEqual(at37["resistor_w"], 0.634907, places=6)
        self.assertAlmostEqual(at37["rating_only_local_ambient_ceiling_c"], 128.0164, places=4)
        self.assertAlmostEqual(adjustment["voltage_v"], 40.39597)
        self.assertAlmostEqual(adjustment["resistor_w"], 0.7568032910561, places=12)
        self.assertAlmostEqual(adjustment["rating_only_local_ambient_ceiling_c"], 122.8359, places=4)
        self.assertAlmostEqual(adjustment["p70_margin_w"], 1.2431967089439, places=12)
        self.assertEqual(upper["resistor_w"], adjustment["resistor_w"])
        self.assertFalse(self.report["source"]["enforced"])
        self.assertEqual(self.report["source"]["legacy_unenforced_proposal_v"], [35, 37])
        self.assertAlmostEqual(self.report["source"]["analysis_upper_v"], 40.39597)
        self.assertAlmostEqual(self.report["source"]["minimum_capacity_fraction"], 0.8208712945317, places=12)

    def test_thermal_feasible_resistance_current_voltage_and_zero_allowance(self):
        low, high = resistor_bounds()
        for temperature in (30, 60, 70, 75, 85, 100, 125, 155):
            row = thermal_envelope(dc.ADJUSTMENT_SCREEN_V, temperature)
            allowance = dc.resistor_allowance(temperature)
            self.assertAlmostEqual(row["fixed_current_ceiling_a_rmax"] ** 2 * high, allowance)
            self.assertAlmostEqual(row["source_ceiling_v_zero_drop"] ** 2 / low, allowance)
            if allowance:
                required = row["required_nominal_r_min_ohm_zero_drop"]
                self.assertAlmostEqual(dc.ADJUSTMENT_SCREEN_V ** 2 / (required * low / 2200), allowance)
            else:
                self.assertIsNone(row["required_nominal_r_min_ohm_zero_drop"])
        self.assertTrue(thermal_envelope(dc.ADJUSTMENT_SCREEN_V, 70)["within_power_allowance_only"])
        self.assertTrue(thermal_envelope(dc.ADJUSTMENT_SCREEN_V, 75)["within_power_allowance_only"])
        self.assertFalse(thermal_envelope(dc.ADJUSTMENT_SCREEN_V, 125)["within_power_allowance_only"])
        self.assertEqual(thermal_envelope(37, -55)["allowed_resistor_w"], 2)
        self.assertTrue(thermal_envelope(0, 155)["within_power_allowance_only"])

    def test_thermal_interface_is_requirement_not_onegel_property(self):
        self.assertEqual(effective_rtheta_limit(2, 30, 60), 15)
        self.assertEqual(effective_rtheta_limit(2, 60, 60), 0)
        self.assertIsNone(effective_rtheta_limit(0, 30, 60))
        interface = self.report["thermal_interfaces"]
        self.assertFalse(interface["onegel_thermal_property_assumed"])
        self.assertAlmostEqual(interface["two_branch_heat_upper_w"], 2 * dc.ADJUSTMENT_SCREEN_V ** 2 / 2156.22)
        self.assertAlmostEqual(interface["bulk_to_outside_effective_rtheta_max_k_per_w"]
                               * interface["two_branch_heat_upper_w"], 30)
        self.assertEqual(interface["cable_temperature_margin_k"], 10)
        self.assertEqual(interface["film_target_c"], 110)
        self.assertEqual(interface["bulk_and_local_ambient_target_c"], 60)
        self.assertIn("proposals", interface["targets_status"])
        self.assertAlmostEqual(interface["bulk_to_outside_effective_rtheta_max_k_per_w"], 19.8202097920)
        self.assertAlmostEqual(interface["film_to_local_effective_rtheta_max_k_per_w"], 66.0673659733)
        self.assertIn("SMT changes heat flow", " ".join(self.report["limitations"]))

    def test_faults_do_not_promote_cv_to_hiccup_or_k12_extinction(self):
        faults = self.report["faults_cv_demand_only"]
        nominal_arc = next(f for f in faults if f["profile"] == "historical_36V_2.8V_6.9_nominal"
                           and f["path"] == "AB@40")
        self.assertAlmostEqual(nominal_arc["path_a"], 0.259543, places=6)
        self.assertAlmostEqual(nominal_arc["path_w"], 2.602168, places=6)
        self.assertGreater(nominal_arc["k12_current_ratio"], 2.69)
        selected_arc = next(f for f in faults if f["profile"] == "analysis_upper_selected_R_zero_drop_rmin"
                            and f["path"] == "AB@40")
        self.assertAlmostEqual(selected_arc["path_a"], 0.130838026726, places=9)
        self.assertAlmostEqual(selected_arc["path_w"], 1.310092126188, places=9)
        for fault in faults:
            self.assertIsNone(fault["psu"]["actual_overload_current_a"])
            self.assertIsNone(fault["psu"]["fuse_clearing_s"])
            if fault["path_ohm"] == 100:
                self.assertGreater(fault["path_w"], 10)
                self.assertLess(fault["source_a"], 1.4)
            elif fault["path_ohm"] == 0:
                self.assertEqual(fault["psu"]["status"], "hiccup-expected-CV-invalid")
        screen = self.report["fault_comparison"]
        self.assertAlmostEqual(screen["sufficient_dc_dominance_series_ohm"], 388.9982296296)
        self.assertAlmostEqual(screen["conditional_0.1ohm_failed_short_heat_upper_w"], 0.256)
        resistance = screen["sufficient_dc_dominance_series_ohm"]
        for voltage in (0, 10, 15, dc.ADJUSTMENT_SCREEN_V):
            self.assertLessEqual((dc.ADJUSTMENT_SCREEN_V - voltage) / resistance, (135 - voltage) / 1300 + 1e-12)

    def test_finite_and_physical_validation_including_derived_overflow(self):
        for value in (math.nan, math.inf, -math.inf, True):
            for function, args in ((resistor_bounds, (value,)), (cable_corner, (value,)),
                                   (thermal_envelope, (value, 70)),
                                   (effective_rtheta_limit, (value, 30, 60))):
                with self.subTest(function=function, value=value), self.assertRaises(ValueError):
                    function(*args)
        bad_calls = (
            (resistor_bounds, {"nominal_ohm": 0}), (resistor_bounds, {"tolerance_fraction": 1}),
            (resistor_bounds, {"tcr_ppm": -50}), (resistor_bounds, {"tcr_ppm": 10000}),
            (resistor_bounds, {"minimum_c": -55.01}), (resistor_bounds, {"maximum_c": 125.01}),
            (resistor_bounds, {"maximum_c": 155}),
            (resistor_bounds, {"minimum_c": 100, "maximum_c": 70}),
            (resistor_bounds, {"nominal_ohm": 1.79e308}),
            (cable_corner, {"temperature_c": 70.01}), (cable_corner, {"temperature_c": -30.01}),
            (cable_corner, {"contact_ohm_per_span": (0, 0)}),
            (cable_corner, {"contact_ohm_per_span": (-0.1, 0, 0)}),
            (cable_corner, {"contact_ohm_per_span": (0, math.nan, 0)}),
            (cable_corner, {"contact_ohm_per_span": (1e308,) * 3}),
            (normal_cases, {"source_min_v": -1}), (normal_cases, {"source_min_v": 37}),
            (normal_cases, {"source_max_v": 35}), (normal_cases, {"source_max_v": 1e308}),
            (normal_cases, {"high_drop_v": -1}),
            (thermal_envelope, {"voltage_v": 1e308, "local_ambient_c": 70}),
            (thermal_envelope, {"voltage_v": 1e-300, "local_ambient_c": 125}),
            (thermal_envelope, {"voltage_v": -1, "local_ambient_c": 70}),
            (thermal_envelope, {"voltage_v": 36, "local_ambient_c": 155.01}),
            (thermal_envelope, {"voltage_v": 36, "local_ambient_c": -55.01}),
            (effective_rtheta_limit, {"power_w": -1, "ambient_c": 30, "target_c": 60}),
            (effective_rtheta_limit, {"power_w": 1, "ambient_c": 60, "target_c": 30}),
        )
        for function, kwargs in bad_calls:
            with self.subTest(function=function, kwargs=kwargs), self.assertRaises(ValueError):
                function(**kwargs)

    def test_cli_json_human_direct_execution_and_fail_closed(self):
        output = StringIO()
        with redirect_stdout(output):
            main(["--json"])
        self.assertEqual(json.loads(output.getvalue()), json.loads(json.dumps(self.report, allow_nan=False)))
        output = StringIO()
        with redirect_stdout(output):
            main([])
        self.assertIn("CONDITIONAL BOUNDS", output.getvalue())
        self.assertIn("0.756803", output.getvalue())
        self.assertIn("after diversion", output.getvalue())
        self.assertIn("K/W", output.getvalue())
        root = Path(__file__).resolve().parents[1]
        run = subprocess.run([sys.executable, "-B", str(root / "scripts/design_bounds.py"), "--json"],
                             cwd=root, text=True, capture_output=True, check=True)
        self.assertEqual(run.stderr, "")
        self.assertTrue(json.loads(run.stdout)["conditional_only"])
        for args in (["--source-max-v", "nan"], ["--contact-ohm-per-span", "0", "-1", "0"],
                     ["--cable-temperature-c", "71"], ["--high-drop-v", "inf"]):
            with self.subTest(args=args), redirect_stderr(StringIO()), self.assertRaises(SystemExit) as failure:
                main(args)
            self.assertEqual(failure.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
