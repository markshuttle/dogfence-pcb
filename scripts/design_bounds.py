#!/usr/bin/env python3
"""Conditional P2 DC/thermal bounds for the selected 16-part station circuit.

Offline, stdlib only; reuses analyze_limits, without changing its defaults.
All numbers are calculations, not measurements or release approval. The 35 V
floor / 40.39597 V upper screen are current analysis inputs, NOT an enforced
source window. The legacy 35..37 V proposal was never implemented as a limit.
See pcb/DESIGN_BOUNDS.md for sources, assumptions and thermal-interface scope.
"""

import argparse
from dataclasses import replace
import json
import math

if __package__:
    from . import analyze_limits as dc
else:
    import analyze_limits as dc


# IEC 60228:2004, ed. 3, 6.2 / Table 3, printed p. 11, metal-coated column.
RESISTANCE_SOURCE = (
    "https://cdn.standards.iteh.ai/samples/12024/"
    "921fee9a88c24612b68340a7330c2262/IEC-60228-2004.pdf"
)
R20_MAX_OHM_PER_KM = 8.21
STATIONS, SPACING_KM = 41, 0.1
CONTACT_OHM_PER_SPAN = (0.025, 0.025, 0.025)


def _finite(name, *values):
    try:
        valid = all(not isinstance(v, bool) and math.isfinite(v) for v in values)
    except (TypeError, OverflowError):
        valid = False
    if not valid:
        raise ValueError(f"{name} must contain finite numbers")


def resistor_bounds(nominal_ohm=2200.0, tolerance_fraction=0.01, tcr_ppm=dc.RESISTOR_TCR_PPM,
                    minimum_c=-30.0, maximum_c=125.0):
    """PS12 initial tolerance / linear TCR screen about 25 C, not aging.

    SMD-SP-007 V.7 tests TCR at -55/125 C; do not extend the screen to the
    separate 155 C operating/zero-power endpoint.
    """
    _finite("resistor inputs", nominal_ohm, tolerance_fraction, tcr_ppm,
            minimum_c, maximum_c)
    if (nominal_ohm <= 0 or not 0 <= tolerance_fraction < 1 or tcr_ppm < 0
            or not -55 <= minimum_c <= maximum_c <= 125):
        raise ValueError("invalid resistance/tolerance or PS12 -55..125 C TCR test envelope")
    drift = tcr_ppm * 1e-6 * max(abs(minimum_c - dc.RESISTOR_REFERENCE_C),
                              abs(maximum_c - dc.RESISTOR_REFERENCE_C))
    if drift >= 1:
        raise ValueError("TCR envelope permits nonpositive resistance")
    bounds = (nominal_ohm * (1 - tolerance_fraction) * (1 - drift),
              nominal_ohm * (1 + tolerance_fraction) * (1 + drift))
    _finite("calculated resistor bounds", *bounds)
    if bounds[0] <= 0:
        raise ValueError("resistance underflow")
    return bounds


def cable_corner(temperature_c=70.0, contact_ohm_per_span=CONTACT_OHM_PER_SPAN):
    """Each 100 m span has its own A/B/C contact ceiling, not just a total budget.

    Return an equivalent Cable with temperature correction already applied.
    Its r20 field is an effective series value, NOT the physical cable's R20.
    Contacts are bounded at service temperature; do not apply copper TCR to them.
    """
    if not isinstance(contact_ohm_per_span, (tuple, list)) or len(contact_ohm_per_span) != 3:
        raise ValueError("three per-span contact budgets required, in A/B/C order")
    _finite("cable inputs", temperature_c, *contact_ohm_per_span)
    if not -30 <= temperature_c <= 70 or min(contact_ohm_per_span) < 0:
        raise ValueError("cable must be within -30..70 C; contact budgets must be nonnegative")
    wire = dc.Cable((R20_MAX_OHM_PER_KM,) * 3, temperature_c=temperature_c)
    effective = tuple((r + contact) / SPACING_KM for r, contact in
                      zip(wire.span_resistances(SPACING_KM), contact_ohm_per_span))
    _finite("calculated cable corner", *effective)
    return dc.Cable(effective, alpha_per_c=0.0)


def normal_cases(*, source_min_v=35.0, source_max_v=dc.ADJUSTMENT_SCREEN_V, cable_temperature_c=70.0,
                 contact_ohm_per_span=CONTACT_OHM_PER_SPAN, high_drop_v=5.2):
    """Named corners, not an exhaustive joint tolerance optimization.

    high_drop_v is a declared total LED/rectifier Vf screen (3.3 + 1.9 V),
    NOT a guaranteed full-temperature SG/BYG23T limit at indicator current.
    BYG23T's 1.9 V maximum is tested at 1 A / 25 C. Other drops may be zero.
    The combined knee uses led_v; individual junction heat is not inferred.
    """
    _finite("source and forward drop", source_min_v, source_max_v, high_drop_v)
    if not 0 <= source_min_v <= 36 <= source_max_v <= 60 or not 0 <= high_drop_v <= 60:
        raise ValueError("require 0 <= source floor <= 36 <= ceiling <= 60 V; Vf in 0..60 V")
    r_min, r_max = resistor_bounds()
    cable = cable_corner(cable_temperature_c, contact_ohm_per_span)
    low = dc.Channel(resistor_ohm=r_min, led_v=0, diode_v=0)
    high = dc.Channel(resistor_ohm=r_max, led_v=high_drop_v, diode_v=0)
    base = dict(stations=STATIONS, spacing_km=SPACING_KM, source=dc.Source(36),
                cable=dc.Cable(), channel_a=dc.Channel(), channel_c=dc.Channel())
    uniform = base | dict(source=dc.Source(source_min_v), cable=cable,
                          channel_a=high, channel_c=high)
    mixed = uniform | dict(channel_a=low, channel_c=low)
    cases = {
        "historical_36V_2.8V_6.9_nominal": base,
        "standard_max_20C_nominal_load": base | {"cable": dc.Cable((R20_MAX_OHM_PER_KM,) * 3)},
        "declared_cable_nominal_load": base | {"cable": cable},
        "uniform_high_vf_rmax": uniform,
        "nonuniform_vf_only_A40": uniform | dict(
            channel_a=replace(high, led_v=0), channel_c=replace(high, led_v=0),
            channel_overrides={("A", 40): high}),
    }
    for core, other in (("A", "C"), ("C", "A")):
        options = mixed | {"channel_overrides": {(core, 40): high}}
        cases[f"nonuniform_{core}40"] = options
        rails = list(cable.r20_ohm_per_km)
        rails[dc.CORES.index(other)] = 0.0
        cases[f"nonuniform_{core}40_other_rail_zero"] = options | {
            "cable": dc.Cable(tuple(rails), alpha_per_c=0.0)}
    cases["zero_cable_upper"] = mixed | dict(
        source=dc.Source(source_max_v), cable=dc.Cable((0.0,) * 3))
    return cases


def thermal_envelope(voltage_v, local_ambient_c):
    """PS12 ambient derating arithmetic, conditional on adequate heat flow.

    Fixed-current ceiling uses Rmax; a voltage-fed power bound uses Rmin.
    R uses the separate -30..125 C screen, not an electrothermal equilibrium.
    Ambient derating to zero at 155 C is not a film or OneGel temperature limit.
    The required nominal R is arithmetic, not a replacement MPN or LED-current limit.
    """
    _finite("thermal inputs", voltage_v, local_ambient_c)
    if voltage_v < 0 or not -55 <= local_ambient_c <= 155:
        raise ValueError("nonnegative voltage and -55..155 C local ambient required")
    r_min, r_max = resistor_bounds()
    allowance = dc.resistor_allowance(local_ambient_c)
    upper_w = voltage_v * voltage_v / r_min
    required_r = (voltage_v * voltage_v / allowance / (r_min / 2200)
                  if allowance else (0.0 if voltage_v == 0 else None))
    _finite("calculated thermal power", upper_w)
    if voltage_v > 0 and upper_w == 0:
        raise ValueError("thermal power underflow")
    if required_r is not None:
        _finite("calculated required resistance", required_r)
    return {
        "local_ambient_c": local_ambient_c, "allowed_resistor_w": allowance,
        "zero_drop_resistor_upper_w": upper_w, "power_margin_w": allowance - upper_w,
        "fixed_current_ceiling_a_rmax": math.sqrt(allowance / r_max),
        "source_ceiling_v_zero_drop": math.sqrt(allowance * r_min),
        "required_nominal_r_min_ohm_zero_drop": required_r,
        "within_power_allowance_only": upper_w <= allowance,
    }


def effective_rtheta_limit(power_w, ambient_c, target_c):
    """Allowable effective K/W, not a material property or predicted temperature.

    None means no heating constraint at zero power, not infinite measured Rtheta.
    """
    _finite("thermal interface", power_w, ambient_c, target_c)
    if power_w < 0 or not -273.15 <= ambient_c <= target_c:
        raise ValueError("require nonnegative heat and physical ambient <= target")
    if power_w == 0:
        return None
    limit = (target_c - ambient_c) / power_w
    _finite("calculated effective Rtheta", limit)
    return limit


def analyze(**options):
    cases = normal_cases(**options)
    results = {name: dc.simulate(**inputs) for name, inputs in cases.items()}
    corner = cases["nonuniform_A40"]
    floor_v = corner["source"].voltage()
    ceiling_v = cases["zero_cable_upper"]["source"].voltage()
    high_drop = corner["channel_overrides"]["A", 40].values()[1]
    r_min, r_max = resistor_bounds()
    effective_rails = corner["cable"].r20_ohm_per_km
    low = corner["channel_a"]

    # Independent comparison bounds: ground B for the lowest positive rail;
    # ideal A/C feeds at the ceiling maximize B. Zero-Vf/Rmin over-loads both
    # comparisons, without assuming identical voltages at the two feed contacts.
    comparison = dict(source=dc.Source(floor_v), channel_a=low, channel_c=low,
                      stations=STATIONS, spacing_km=SPACING_KM)
    b_upper = dc.simulate(**(comparison | {"source": dc.Source(ceiling_v)}),
                          cable=dc.Cable((0, effective_rails[1], 0)))
    positive_lower = {}
    for core in dc.CHANNELS:
        rails = tuple(r if c == core else 0 for c, r in zip(dc.CORES, effective_rails))
        result = dc.simulate(**comparison, cable=dc.Cable(rails))
        positive_lower[core] = result.voltages[core, 40]
    differential_lower = min(positive_lower.values()) - b_upper.voltages["B", 40]
    branch_lower = max(0.0, differential_lower - high_drop) / r_max
    led_lower = max(0.0, branch_lower - dc.CLAMP_LEAKAGE_SCREEN_A)

    rows = {}
    for name, result in results.items():
        row = result.summary()
        row["cable_and_contact_loss_w"] = row.pop("cable_loss_w")
        row.update({f"{c}40_ma": 1000 * result.led_currents_a[c, 40] for c in dc.CHANNELS})
        for key in ("led_min_ma", "A40_ma", "C40_ma"):
            row[key.removesuffix("_ma") + "_after_clamp_leakage_ma"] = max(
                0.0, row[key] - 1000 * dc.CLAMP_LEAKAGE_SCREEN_A)
        rows[name] = row
    branch_rows = []
    for name, voltage, channel in (
            ("36V_2.8V_nominal_comparison", 36.0, dc.Channel()), ("36V_zero_drop_rmin", 36.0, low),
            ("legacy_37V_proposal_selected_R_zero_drop_rmin", 37.0, low),
            ("analysis_upper_zero_drop_rmin", ceiling_v, low),
            ("accessible_adjustment_screen", dc.ADJUSTMENT_SCREEN_V, low)):
        budget = dc.branch_budget(voltage, channel)
        watts = budget["resistor_w"]
        # Clamp leakage heat is diverted from external LED heat, not extra input power.
        clamp_w = channel.values()[1] * dc.CLAMP_LEAKAGE_SCREEN_A
        branch_rows.append({
            "case": name, "voltage_v": voltage, "branch_a": budget["branch_a"],
            "resistor_w": watts, "two_resistors_w": 2 * watts,
            "two_resistors_and_rectifiers_w": 2 * (watts + budget["diode_w"]),
            "two_resistors_rectifiers_clamps_upper_w": 2 * (watts + budget["diode_w"] + clamp_w),
            "two_branch_electrical_input_w": 2 * voltage * budget["branch_a"],
            "p70_margin_w": dc.RESISTOR_P70_W - watts,
            "rating_only_local_ambient_ceiling_c": (
                dc.RESISTOR_ZERO_POWER_AMBIENT_C
                - (dc.RESISTOR_ZERO_POWER_AMBIENT_C - 70) * watts / dc.RESISTOR_P70_W
                if watts <= dc.RESISTOR_P70_W else None),
        })

    upper = rows["zero_cable_upper"]
    watts = upper["resistor_max_w"]
    board_heat = 2 * watts
    faults = []
    for profile, case, voltage in (("historical_36V_2.8V_6.9_nominal", "historical_36V_2.8V_6.9_nominal", 36.0),
                                   ("analysis_upper_selected_R_zero_drop_rmin", "nonuniform_A40", ceiling_v)):
        inputs = cases[case] | {"source": dc.Source(voltage, series_ohm=0.25)}
        inputs = {k: v for k, v in inputs.items() if k != "channel_overrides"}
        for core in dc.CHANNELS:
            for station, resistance, arc in ((0, 0.0, 0.0), (0, 100.0, 0.0), (40, 0.1, 10.0)):
                result = dc.simulate(**inputs, faults=(
                    dc.Fault("fault", (core, station), ("B", station), resistance, arc),))
                current = result.element_currents_a["fault"]
                path_v = abs(result.voltages[core, station] - result.voltages["B", station])
                k12_a = max(0.0, (135 - path_v) / 1300)
                faults.append({
                    "profile": profile, "path": f"{core}B@{station}",
                    "path_ohm": resistance, "conditional_arc_v": arc,
                    "source_a": result.supply_current_a, "path_a": current,
                    "path_v": path_v, "path_w": result.element_power_w["fault"],
                    "psu": dc.assess_psu(result, rated_a=2.1, rated_w=75.6),
                    "k12_dc_feed_a_at_same_path_v": k12_a if arc else None,
                    "k12_current_ratio": abs(current) / k12_a if arc else None,
                })

    rated_voltage_v = min(500.0, math.sqrt(dc.RESISTOR_P70_W * 2200))
    return {
        "revision": dc.REVISION, "conditional_only": True,
        "stations": STATIONS, "spacing_km": SPACING_KM,
        "source": {"model": "one LRS-75-36 for TEST; second is spare (user confirmed)",
                   "nominal_v": 36.0, "analysis_floor_v": floor_v,
                   "analysis_upper_v": ceiling_v, "enforced": False,
                   "accessible_adjustment_screen_v": dc.ADJUSTMENT_SCREEN_V,
                   "legacy_unenforced_proposal_v": [35.0, 37.0],
                   "minimum_capacity_fraction": max(upper["source_a"] / 2.1,
                                                    upper["source_w"] / 75.6),
                   "unallocated_capacity_a": 2.1 - upper["source_a"],
                   "unallocated_capacity_w": 75.6 - upper["source_w"]},
        "cable": {"reel": "CM03/05.100: 3 CORE (3 x 35/0.30) TINNED BLACK 100 MTR",
                  "r20_max_ohm_per_km_conditional": R20_MAX_OHM_PER_KM,
                  "resistance_source": RESISTANCE_SOURCE,
                  "temperature_c": options.get("cable_temperature_c", 70.0),
                  "copper_alpha_per_c": 0.00393,
                  "contact_ohm_per_span_ABC": options.get("contact_ohm_per_span", CONTACT_OHM_PER_SPAN),
                  "effective_4km_core_ohm_ABC": [r * 4 for r in effective_rails]},
        "resistor": {"mpn": dc.RESISTOR_MPN, "manufacturer": "Uni-Royal", "package": "2512 SMT",
                     "nominal_ohm": 2200.0,
                     "r_min_ohm": r_min, "r_max_ohm": r_max,
                     "screen_temperature_range_c": [-30, 125], "tolerance_fraction": 0.01,
                     "tcr_abs_ppm_per_c": dc.RESISTOR_TCR_PPM, "aging_included": False,
                     "reference_temperature_c": dc.RESISTOR_REFERENCE_C,
                     "tcr_test_temperatures_c": [-55, 125],
                     "p70_w": dc.RESISTOR_P70_W,
                     "zero_power_ambient_c": dc.RESISTOR_ZERO_POWER_AMBIENT_C,
                     "family_max_working_voltage_v": 500.0,
                     "rated_working_voltage_at_p70_v": rated_voltage_v,
                     "family_max_overload_voltage_v": 1000.0,
                     "dielectric_withstanding_voltage_v": 500.0,
                     "short_time_overload_test_v": min(2.5 * rated_voltage_v, 1000.0),
                     "short_time_overload_test_s": 5.0},
        "diodes": {"D1_D2_D3_D4_mpn": dc.DIODE_MPN, "vrrm_v": 1300,
                   "D3_D4_cathodes": "LED_A_POS / LED_C_POS after D1/D2",
                   "D3_D4_anodes": "WIRE_B", "positive_voltage_regulation": False,
                   "extra_input_shunt_load": False,
                   "forward_v_max_at_1A_25C": 1.9, "nominal_comparison_v_not_characterized": 0.7,
                   "reverse_leakage_max_at_1300V_25C_a": 5e-6,
                   "reverse_leakage_max_at_1300V_125C_a": 50e-6,
                   "normal_positive_clamp_diversion_screen_a": dc.CLAMP_LEAKAGE_SCREEN_A,
                   "leakage_scope": "Conditional monotone bound vs reverse voltage/temperature up to "
                                    "1300 V / 125 C, not a guaranteed 5 uA at LED voltage or at all temperatures"},
        "current_bounds": {"scope": "healthy uncut network, not fault states or visibility",
                           "high_total_vf_screen_v": high_drop, "low_total_vf_bound_v": 0.0,
                           "comparison_positive_rail_lower_v": positive_lower,
                           "comparison_B_rail_upper_v": b_upper.voltages["B", 40],
                           "conditional_all_station_branch_min_ma": 1000 * branch_lower,
                           "conditional_all_station_led_min_ma": 1000 * led_lower,
                           "conditional_all_station_led_max_ma": upper["led_max_ma"],
                           "conditional_total_current_upper_a": upper["source_a"],
                           "local_B_tap_current_upper_a": 2 * ceiling_v / r_min,
                           "uniform_vf_optimism_A40_ma": rows["uniform_high_vf_rmax"]["A40_ma"]
                           - rows["nonuniform_vf_only_A40"]["A40_ma"],
                           "additional_R_spread_reduction_A40_ma": rows["nonuniform_vf_only_A40"]["A40_ma"]
                           - rows["nonuniform_A40"]["A40_ma"]},
        "normal_cases": rows, "source_end_branches": branch_rows,
        "thermal_envelope": [thermal_envelope(ceiling_v, t) for t in (30, 60, 70, 75, 85, 100, 125, 155)],
        "thermal_interfaces": {
            "two_branch_heat_upper_w": board_heat, "outside_example_c": 30.0,
            "bulk_and_local_ambient_target_c": 60.0, "film_target_c": 110.0,
            "targets_status": "Conservative proposals, not user hard future all-temperature limits",
            "cable_temperature_margin_k": 10.0,
            "bulk_to_outside_effective_rtheta_max_k_per_w": effective_rtheta_limit(board_heat, 30, 60),
            "film_to_local_effective_rtheta_max_k_per_w": effective_rtheta_limit(watts, 60, 110),
            "onegel_thermal_property_assumed": False,
        },
        "faults_cv_demand_only": faults,
        "fault_comparison": {"illustrative_source_series_ohm": 0.25,
                             "k12_test_source_v": 135, "k12_dc_feed_ohm": 1300,
                             "sufficient_dc_dominance_series_ohm": 1300 * ceiling_v / 135,
                             "historical_not_enforced_current_ceiling_a": 1.6,
                             "conditional_0.1ohm_failed_short_heat_upper_w": 1.6 * 1.6 * 0.1},
        "limitations": [
            "Reel identity is confirmed, not measured R. Class 5 Table 3 permits 0.26 mm wires; "
            "AMC's representative/reel 0.30 mm construction needs reconciliation, not an invented R column.",
            "Each 100 m span must meet its own service-temperature contact budget. A 4 km total alone "
            "does not bound concentrated bad joints. Start A/C-to-B source floor includes hub losses.",
            "Current floor needs the declared Vf/R/cable/contact envelope, negligible unbudgeted tap "
            "losses, and <=50 uA clamp diversion under the monotone <=125 C leakage assumption. "
            "5.2 V is a headroom screen, not an SG/BYG23T full-temperature I/V guarantee or daylight test.",
            "Comparison floor is deliberately loose; named nonuniform cases are not an exhaustive "
            "tolerance optimization. Cuts use existing cut_sweep with diversion margin, not this CLI. "
            "1 uA state classification is not an optical dark threshold; series reverse leakage is not solved.",
            "The two-branch input-power heat bound already includes resistor, diode, LED and clamp energy. "
            "Do not add clamp leakage as another PSU load. Contact/auxiliary heat and solar input are excluded.",
            "PS12 2 W does not remove the nominal 1.002 W resistor heat per board. SMT changes heat flow, "
            "not power loss or a proven cooler result. Ambient derating reaches zero at 155 C; no PS12 "
            "hot-spot or mounted K/W is established. PR02 thermal/standoff data do not apply.",
            "PS12 TCR uses +/-100 ppm/C referenced to 25 C from SMD-SP-007 V.7. The linear "
            "-30..125 C screen stays within the PDF's -55/125 C TCR test endpoints, not 155 C. "
            "Aging and assembly/solder drift are excluded.",
            "PS12 family 500 V is limited by sqrt(P*R): 66.3325 V at 2 W / nominal 2.2k. "
            "The 165.8312 V five-second overload test (1000 V family cap) is separate from the "
            "PS one-pulse power and voltage curves (SMD-SP-007 V.7 p. 6), not digitized here; "
            "neither establishes repetitive surge or board-lightning qualification.",
            "60 C interface / 110 C film are proposed conservative targets, not universal user limits. "
            "Meet actual cable <=70 C and all gel/adhesive/LED/connector limits with uncertainty.",
            "Resistance uses selected -30..125 C inputs, not self-heating. Rating-only ambient/current/voltage "
            "ceilings are not simultaneous electrothermal, LED-current or system operating approvals.",
            "PSU capacity needs actual input/temperature derating and auxiliary/interface-loss budget. "
            "35 V floor / 40.39597 V upper are default analysis inputs, not an enforced window or guaranteed "
            "combined MCOV. Legacy 35..37 V and 1.6 A proposals are not implemented; PSU OVP is not a 37 V limit.",
            "Faults are prospective CV demands, not actual LRS current or GDT holding/extinction. "
            "K.12 DC dominance alone does not establish dynamic recovery or a safe fault duration.",
            "D3/D4 forward-bias for negative connector voltage, but their typical 9 V / 620 ns forward "
            "recovery at 1.5 A, 12 A/us is NOT a <=5 V reverse-LED proof. No positive regulation, "
            "forward-pulse current control or reversed-flying-lead survival is claimed.",
            "User accepts installation lead-reversal LED damage and direct-strike rebuilding; energized "
            "cattle fencing is prohibited near the ENTIRE boundary, including 4 km cable, stations and hub.",
            "RF, ordinary switching, nearby lightning, recovery, aging/lifetime and potted thermal behavior "
            "remain unqualified. C4/C5/W3 performance review is separate from prototype export. "
            "Continuous-safe normal TEST stays mandatory; no timer or active current-stage prerequisite is added.",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-min-v", type=float, default=35.0, help="analysis feed floor, not enforced")
    parser.add_argument("--source-max-v", type=float, default=dc.ADJUSTMENT_SCREEN_V,
                        help="analysis upper screen INCLUDING ripple, not enforced MCOV")
    parser.add_argument("--cable-temperature-c", type=float, default=70.0)
    parser.add_argument("--contact-ohm-per-span", nargs=3, type=float, default=CONTACT_OHM_PER_SPAN,
                        metavar=("A", "B", "C"), help="maximum per core per 100 m span at service temperature")
    parser.add_argument("--high-drop-v", type=float, default=5.2,
                        help="LED 3.3 + BYG23T 1.9 V headroom screen, not full-temperature I/V data")
    parser.add_argument("--json", action="store_true")
    args = vars(parser.parse_args(argv))
    json_output = args.pop("json")
    try:
        report = analyze(**args)
        serialized = json.dumps(report, indent=2, allow_nan=False)
    except (ValueError, ArithmeticError) as exc:
        parser.exit(2, f"Analysis failed: {exc}\n")
    if json_output:
        print(serialized)
        return
    print(f"Dog Fence {dc.REVISION}: CONDITIONAL BOUNDS, not measurements or approval")
    print("41 stations / 82 LEDs; one LRS-75-36 TEST source, second spare; same-end feed/return")
    print("Source: " + json.dumps(report["source"]))
    print("Cable: " + json.dumps(report["cable"]))
    print("Resistor: " + json.dumps(report["resistor"]))
    print("Diodes: " + json.dumps(report["diodes"]))
    print("\nNormal cases | source A | branch min..max mA | A40 / C40 LED lower mA after diversion | max resistor W")
    for name, row in report["normal_cases"].items():
        print(f"{name} | {row['source_a']:.6f} | {row['led_min_ma']:.4f}..{row['led_max_ma']:.4f}"
              f" | {row['A40_after_clamp_leakage_ma']:.4f} / {row['C40_after_clamp_leakage_ma']:.4f}"
              f" | {row['resistor_max_w']:.6f}")
    print("\nConditional current bounds: " + json.dumps(report["current_bounds"]))
    print("\nSource-end case | branch mA | resistor W | two resistors W | rating local ceiling C")
    for row in report["source_end_branches"]:
        local = row["rating_only_local_ambient_ceiling_c"]
        text = f"{local:.3f}" if local is not None else "NONE (above PS12 P70)"
        print(f"{row['case']} | {1000 * row['branch_a']:.4f} | {row['resistor_w']:.6f}"
              f" | {row['two_resistors_w']:.6f} | {text}")
    print("\nLocal C | allowed W | margin W | fixed-current ceiling mA | zero-drop source ceiling V | nominal R min ohm")
    for row in report["thermal_envelope"]:
        required = row["required_nominal_r_min_ohm_zero_drop"]
        text = f"{required:.2f}" if required is not None else "no finite R"
        print(f"{row['local_ambient_c']:g} | {row['allowed_resistor_w']:.6f} | {row['power_margin_w']:.6f}"
              f" | {1000 * row['fixed_current_ceiling_a_rmax']:.4f}"
              f" | {row['source_ceiling_v_zero_drop']:.4f} | {text}")
    print("\nProposed thermal interface targets (K/W), not predictions: " + json.dumps(report["thermal_interfaces"]))
    print("\nFault CV DEMAND ONLY | source A | path A | path W | LRS-75 envelope | K.12 ratio (arc only)")
    for row in report["faults_cv_demand_only"]:
        ratio = row["k12_current_ratio"]
        text = f"{ratio:.3f}" if ratio is not None else "-"
        print(f"{row['profile']} {row['path']} R={row['path_ohm']:g} arc={row['conditional_arc_v']:g}"
              f" | {row['source_a']:.6f} | {row['path_a']:.6f} | {row['path_w']:.6f}"
              f" | {row['psu']['status']} | {text}")
    print("\nK.12 / failed-short conditional comparison: " + json.dumps(report["fault_comparison"]))
    for limitation in report["limitations"]:
        print("NOTE: " + limitation)


if __name__ == "__main__":
    main()
