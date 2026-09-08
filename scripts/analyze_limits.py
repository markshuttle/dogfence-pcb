#!/usr/bin/env python3
"""Provisional 1.2.0-dev TEST DC analysis, using only the standard library.

Run this file for a reproducible study or use simulate() for individual cases.
Stations and cut spans are zero based: cut ("A", 0) opens A between stations
0 and 1. Rungs conduct only A -> B and C -> B. The selected PS12 / BYG23T
branches retain series isolation: D3/D4 have cathodes at LED_POS and anodes
at B, AFTER D1/D2. They neither regulate positive voltage nor shunt the inputs.
Six boundary ends remain independent except for source-side TEST connections.
See pcb/ELECTRICAL.md section 9 and pcb/DESIGN_BOUNDS.md.

Default 36 V / 2.8 V drop / zero leakage preserves the historical comparison,
not measured BYG23T Vf at 15 mA. Normal clamp leakage diverts existing branch
current; it is not an extra PSU path. Series reverse leakage is not solved.

This is NOT an LED reverse-bias, transient, GDT ignition/extinction, thermal,
visibility, or dynamic PSU model. Fault results are prospective constant-
voltage demand; assess_psu() explicitly refuses to predict overload current.
"""

import argparse
from dataclasses import asdict, dataclass, replace
from itertools import combinations
import json
import math


REVISION = "1.2.0-dev"
CORES = "ABC"
CHANNELS = "AC"
CUT_SETS = tuple("".join(c) for n in (1, 2, 3) for c in combinations(CORES, n))
RESISTOR_MPN = "PS122WF2201T4E"
RESISTOR_TCR_PPM = 100.0
RESISTOR_REFERENCE_C = 25.0
RESISTOR_P70_W = 2.0
RESISTOR_ZERO_POWER_AMBIENT_C = 155.0
DIODE_MPN = "BYG23T-M3/TR"
# Conditional monotone reverse-leakage screen at normal positive LED voltage,
# within 1300 V / <=125 C. Not a guaranteed 2 V or all-temperature leakage spec.
CLAMP_LEAKAGE_SCREEN_A = 50e-6


def _finite(name, *values):
    if not all(math.isfinite(value) for value in values):
        raise ValueError(f"{name} must be finite")


@dataclass(frozen=True)
class Source:
    voltage_v: float = 36.0
    series_ohm: float = 0.0
    error_fraction: float = 0.0
    temperature_c: float = 25.0
    tempco_per_c: float = 0.0
    ripple_peak_v: float = 0.0

    def voltage(self):
        _finite("source", *asdict(self).values())
        if self.series_ohm < 0 or self.error_fraction <= -1:
            raise ValueError("source resistance must be >= 0 and error > -1")
        factor = 1 + self.tempco_per_c * (self.temperature_c - 25)
        if factor <= 0 or self.temperature_c < -273.15:
            raise ValueError("invalid source temperature/coefficient")
        voltage = self.voltage_v * (1 + self.error_fraction) * factor + self.ripple_peak_v
        _finite("calculated source voltage", voltage)
        return voltage


# Deliberately stacked screen, not a guaranteed combined maximum or hardware OV limit.
ADJUSTMENT_SCREEN_V = Source(39.6, error_fraction=0.01, temperature_c=50,
                             tempco_per_c=0.0003, ripple_peak_v=0.1).voltage()


@dataclass(frozen=True)
class Cable:
    r20_ohm_per_km: tuple = (6.9, 6.9, 6.9)
    error_fraction: tuple = (0.0, 0.0, 0.0)
    temperature_c: float = 20.0
    alpha_per_c: float = 0.00393

    def span_resistances(self, spacing_km):
        if len(self.r20_ohm_per_km) != 3 or len(self.error_fraction) != 3:
            raise ValueError("cable requires separate A, B, C resistance/error inputs")
        _finite("cable", *self.r20_ohm_per_km, *self.error_fraction,
                self.temperature_c, self.alpha_per_c, spacing_km)
        factor = 1 + self.alpha_per_c * (self.temperature_c - 20)
        if (min(self.r20_ohm_per_km) < 0 or min(self.error_fraction) <= -1
                or factor <= 0 or self.temperature_c < -273.15 or spacing_km <= 0):
            raise ValueError("invalid cable resistance, temperature, or spacing")
        resistances = tuple(r * (1 + e) * factor * spacing_km
                            for r, e in zip(self.r20_ohm_per_km, self.error_fraction))
        _finite("calculated span resistance", *resistances)
        return resistances


@dataclass(frozen=True)
class Channel:
    resistor_ohm: float = 2200.0
    led_v: float = 2.1
    diode_v: float = 0.7
    resistor_error: float = 0.0
    resistor_tcr_ppm: float = 0.0
    resistor_temperature_c: float = RESISTOR_REFERENCE_C
    junction_temperature_c: float = 20.0
    led_tempco_v_per_c: float = 0.0
    diode_tempco_v_per_c: float = 0.0

    def values(self):
        """Selected corner; R references 25 C, junction drops retain 20 C."""
        _finite("channel", *asdict(self).values())
        r = self.resistor_ohm * (1 + self.resistor_error) * (
            1 + self.resistor_tcr_ppm * 1e-6 * (self.resistor_temperature_c - RESISTOR_REFERENCE_C))
        led = self.led_v + self.led_tempco_v_per_c * (self.junction_temperature_c - 20)
        diode = self.diode_v + self.diode_tempco_v_per_c * (self.junction_temperature_c - 20)
        _finite("calculated channel values", r, led, diode)
        if (self.resistor_ohm <= 0 or self.resistor_error <= -1 or r <= 0
                or min(led, diode) < 0
                or min(self.resistor_temperature_c, self.junction_temperature_c) < -273.15):
            raise ValueError("invalid channel resistance, forward drop, or temperature")
        return r, led, diode


@dataclass(frozen=True)
class Fault:
    """An explicit path at node tuples (core, station), including optional E nodes.

    arc_v=0 is an ohmic short/path. arc_v>0 is a *conditional ignited* GDT
    represented by sign(V) * max(abs(V)-arc_v, 0) / ohm. Positive ohm is
    required for an arc. It is not a holding-current or extinction criterion.
    Earth nodes have no implicit connection to B, PE, or each other.
    """
    name: str
    a: tuple
    b: tuple
    ohm: float = 0.0
    arc_v: float = 0.0


@dataclass(frozen=True)
class _Element:
    name: str
    a: tuple
    b: tuple
    ohm: float
    knee_v: float = 0.0
    one_way: bool = False

    def overdrive(self, voltage):
        if self.one_way:
            return max(0.0, voltage - self.knee_v)
        return math.copysign(max(0.0, abs(voltage) - self.knee_v), voltage)


class IdealSourceShort(ValueError):
    """Conflicting ideal voltage constraints; no finite CV demand exists."""


@dataclass
class Result:
    """Zero-leakage one-way solution; LED fields precede clamp-current diversion."""

    voltage_v: float
    supply_current_a: float
    return_current_a: float
    voltages: dict
    led_currents_a: dict
    resistor_power_w: dict
    diode_power_w: dict
    led_power_w: dict
    element_currents_a: dict
    element_power_w: dict
    kcl_error_a: float
    power_balance_w: float
    iterations: int

    def state(self, station, threshold_a=1e-6):
        """Electrical ON only; threshold is NOT a daylight visibility limit."""
        return tuple(self.led_currents_a[c, station] > threshold_a for c in CHANNELS)

    def summary(self):
        return {
            "voltage_v": self.voltage_v,
            "source_a": self.supply_current_a,
            "source_w": self.voltage_v * self.supply_current_a,
            "led_min_ma": 1000 * min(self.led_currents_a.values()),
            "led_max_ma": 1000 * max(self.led_currents_a.values()),
            "resistor_max_w": max(self.resistor_power_w.values()),
            "cable_loss_w": sum(p for name, p in self.element_power_w.items()
                                if name.startswith("cable:")),
            "floating_node_count": sum(v is None for v in self.voltages.values()),
            "kcl_error_a": self.kcl_error_a,
            "power_balance_w": self.power_balance_w,
        }


def _components(nodes, pairs):
    neighbors = {n: set() for n in nodes}
    for a, b in pairs:
        neighbors[a].add(b)
        neighbors[b].add(a)
    unseen = set(nodes)
    while unseen:
        todo = [min(unseen)]
        group = set(todo)
        unseen.difference_update(group)
        while todo:
            new = neighbors[todo.pop()] & unseen
            todo.extend(new)
            group.update(new)
            unseen.difference_update(new)
        yield group


def _linear_step(nodes, active, fixed, previous):
    """Sparse symmetric elimination; gauge floating components without shunts."""
    anchors = dict(fixed)
    for group in _components(nodes, ((a, b) for a, b, _, _ in active)):
        if not group.intersection(anchors):
            node = min(group)
            anchors[node] = previous[node]
    unknown = [n for n in nodes if n not in anchors]
    index = {n: i for i, n in enumerate(unknown)}
    rows = [{} for _ in unknown]
    rhs = [0.0] * len(unknown)
    for a, b, g, drop in active:
        if a == b:
            continue
        for node, other, offset in ((a, b, drop), (b, a, -drop)):
            if node not in index:
                continue
            i = index[node]
            rows[i][i] = rows[i].get(i, 0.0) + g
            rhs[i] += g * offset
            if other in anchors:
                rhs[i] += g * anchors[other]
            elif index[other] > i:
                j = index[other]
                rows[i][j] = rows[i].get(j, 0.0) - g
    for i, row in enumerate(rows):
        pivot = row.get(i, 0.0)
        if not math.isfinite(pivot) or pivot <= 0:
            raise ArithmeticError("singular/ill-conditioned network")
        rest = sorted((j, a) for j, a in row.items() if j > i and a)
        for k, (j, a) in enumerate(rest):
            ratio = a / pivot
            rhs[j] -= ratio * rhs[i]
            for col, value in rest[k:]:
                rows[j][col] = rows[j].get(col, 0.0) - ratio * value
    values = [0.0] * len(unknown)
    for i in reversed(range(len(unknown))):
        values[i] = (rhs[i] - sum(a * values[j] for j, a in rows[i].items()
                                if j > i)) / rows[i][i]
    return anchors | dict(zip(unknown, values))


def simulate(*, stations=41, spacing_km=0.1, source=Source(), cable=Cable(),
             channel_a=Channel(), channel_c=Channel(), cuts=(), faults=(),
             channel_overrides=None, legacy_end_ac_strap=False, both_b_returns=False,
             tolerance_a=1e-10, max_iterations=100):
    """Solve all three rails independently, including station 0 and the last.

    Ideal wires/zero-resistance spans are contracted exactly. Piecewise-linear
    passive branches minimize a convex nodal energy by damped Newton steps.
    A floating island is never grounded through a numerical leakage resistor.
    Its absolute potentials are returned as None, even if an internal gauge
    was necessary to solve its currents. Reversal darkness proves no VR limit.
    """
    if not isinstance(stations, int) or isinstance(stations, bool) or stations < 1:
        raise ValueError("stations must be a positive integer")
    _finite("solver tolerance", tolerance_a)
    if tolerance_a <= 0 or type(max_iterations) is not int or max_iterations < 1:
        raise ValueError("positive solver tolerance and iteration count required")
    voltage = source.voltage()
    span_r = cable.span_resistances(spacing_km)
    cut_set = set(cuts)
    for core, span in cut_set:
        if core not in tuple(CORES) or type(span) is not int or not 0 <= span < stations - 1:
            raise ValueError("cut must name A/B/C and a zero-based existing span")
    channels = {"A": channel_a, "C": channel_c}
    overrides = channel_overrides or {}
    for core, station in overrides:
        if core not in tuple(CHANNELS) or type(station) is not int or not 0 <= station < stations:
            raise ValueError("invalid channel override node")
    values = {(c, s): overrides.get((c, s), channels[c]).values()
              for s in range(stations) for c in CHANNELS}
    nodes = [(c, s) for s in range(stations) for c in CORES] + [("+", 0)]
    elements = [
        _Element("source:lead", ("+", 0), ("A", 0), source.series_ohm),
        _Element("source:AC", ("A", 0), ("C", 0), 0.0),
    ]
    for s in range(stations - 1):
        for c, r in zip(CORES, span_r):
            if (c, s) not in cut_set:
                elements.append(_Element(f"cable:{c}:{s}", (c, s), (c, s + 1), r))
    for (c, s), (r, led, diode) in values.items():
        elements.append(_Element(f"rung:{c}:{s}", (c, s), ("B", s), r,
                                 led + diode, True))
    if legacy_end_ac_strap:
        elements.append(_Element("legacy:AC", ("A", stations - 1), ("C", stations - 1), 0.0))
    if both_b_returns:
        elements.append(_Element("legacy:B", ("B", stations - 1), ("B", 0), 0.0))
    names = {e.name for e in elements}
    for f in faults:
        _finite("fault", f.ohm, f.arc_v)
        if f.ohm < 0 or f.arc_v < 0 or (f.arc_v and not f.ohm):
            raise ValueError("fault R and arc voltage must be >= 0; arcs need positive R")
        if not f.name or f.name in names:
            raise ValueError("fault names must be nonempty and unique")
        names.add(f.name)
        for c, s in (f.a, f.b):
            if c not in ("A", "B", "C", "E") or type(s) is not int or not 0 <= s < stations:
                raise ValueError("fault endpoint must be an existing station A/B/C/E")
            if (c, s) not in nodes:
                nodes.append((c, s))
        elements.append(_Element(f.name, f.a, f.b, f.ohm, f.arc_v))

    parent = {n: n for n in nodes}

    def root(n):
        while parent[n] != n:
            parent[n] = parent[parent[n]]
            n = parent[n]
        return n

    for e in elements:
        if e.ohm == 0:
            parent[root(e.b)] = root(e.a)
    fixed = {root(("+", 0)): voltage}
    negative = root(("B", 0))
    if negative in fixed and voltage != 0:
        raise IdealSourceShort("ideal short across ideal source; specify source impedance, not a fuse verdict")
    fixed[negative] = 0.0
    reduced_nodes = list(dict.fromkeys(root(n) for n in nodes))
    branches = [(e, root(e.a), root(e.b)) for e in elements if e.ohm > 0]
    v = {n: fixed.get(n, 0.0) for n in reduced_nodes}
    free = [n for n in reduced_nodes if n not in fixed]

    def evaluate(potentials):
        gradient = {n: 0.0 for n in reduced_nodes}
        energy = 0.0
        for e, a, b in branches:
            over = e.overdrive(potentials[a] - potentials[b])
            current = over / e.ohm
            gradient[a] += current
            gradient[b] -= current
            energy += 0.5 * over * current
        return gradient, energy

    for iteration in range(1, max_iterations + 1):
        gradient, energy = evaluate(v)
        if max((abs(gradient[n]) for n in free), default=0.0) <= tolerance_a:
            break
        active = []
        for e, a, b in branches:
            diff = v[a] - v[b]
            if (not e.one_way and e.knee_v == 0) or e.overdrive(diff):
                drop = e.knee_v if e.one_way else math.copysign(e.knee_v, diff)
                active.append((a, b, 1 / e.ohm, drop))
        target = _linear_step(reduced_nodes, active, fixed, v)
        direction = {n: target[n] - v[n] for n in reduced_nodes}
        slope = sum(gradient[n] * direction[n] for n in free)
        step = 1.0
        for _ in range(50):
            trial = {n: v[n] + step * direction[n] for n in reduced_nodes}
            _, trial_energy = evaluate(trial)
            if trial_energy <= energy + 1e-4 * step * slope + 1e-13 * max(1.0, energy):
                v = trial
                break
            step *= 0.5
        else:
            raise ArithmeticError("network line search did not converge")
    else:
        raise ArithmeticError("network KCL did not converge; no result published")

    gradient, _ = evaluate(v)
    supply_i = gradient[root(("+", 0))]
    return_i = -gradient[negative]
    currents = {e.name: e.overdrive(v[a] - v[b]) / e.ohm for e, a, b in branches}
    powers = {e.name: currents[e.name] ** 2 * e.ohm + abs(currents[e.name]) * e.knee_v
              for e, _, _ in branches}

    # Recover ideal-wire currents when the ideal connection graph is a tree.
    # Currents in an ideal zero-ohm cycle are indeterminate, not silently zero.
    ideal = [e for e in elements if e.ohm == 0]
    balances = {n: 0.0 for n in nodes}
    for e, _, _ in branches:
        balances[e.a] += currents[e.name]
        balances[e.b] -= currents[e.name]
    balances["+", 0] -= supply_i
    balances["B", 0] += return_i
    for e in ideal:
        currents[e.name] = None
        powers[e.name] = 0.0
    for group in _components(nodes, ((e.a, e.b) for e in ideal)):
        links = [e for e in ideal if e.a in group]
        if len(links) != len(group) - 1:
            continue
        neighbors = {n: [] for n in group}
        for e in links:
            neighbors[e.a].append((e.b, e))
            neighbors[e.b].append((e.a, e))
        order = [(min(group), None, None)]
        for n, preceding, _ in order:
            order.extend((other, n, e) for other, e in neighbors[n] if other != preceding)
        for n, preceding, e in reversed(order[1:]):
            currents[e.name] = -balances[n] if e.a == n else balances[n]
            balances[preceding] += balances[n]

    floating = set()
    conducting = [(a, b) for e, a, b in branches
                  if (not e.one_way and e.knee_v == 0) or abs(currents[e.name]) > tolerance_a]
    for group in _components(reduced_nodes, conducting):
        if not group.intersection(fixed):
            floating.update(group)
    led_i = {n: currents[f"rung:{n[0]}:{n[1]}"] for n in values}
    power_error = voltage * supply_i - sum(powers.values())
    if not math.isfinite(power_error) or abs(power_error) > 1e-6 * max(1.0, abs(voltage * supply_i)):
        raise ArithmeticError("network power balance failed")
    return Result(
        voltage, supply_i, return_i,
        {n: None if root(n) in floating else v[root(n)] for n in nodes}, led_i,
        {n: led_i[n] ** 2 * r for n, (r, _, _) in values.items()},
        {n: led_i[n] * diode for n, (_, _, diode) in values.items()},
        {n: led_i[n] * led for n, (_, led, _) in values.items()},
        currents, powers, max((abs(gradient[n]) for n in free), default=0.0),
        power_error, iteration,
    )


def assess_psu(result, *, rated_a, rated_w, derating=1.0,
               overload_min=1.1, overload_max=1.5):
    """LRS continuous envelope/overload screening, NOT a constant-current supply.

    Manufacturer overload thresholds are percentages of rated OUTPUT POWER.
    Neither thresholds, rated current, nor I^2*t specify hiccup pulse shape.
    Derating affects the allowable load, not an invented protection threshold.
    """
    _finite("PSU limits", rated_a, rated_w, derating, overload_min, overload_max)
    if min(rated_a, rated_w) <= 0 or not 0 < derating <= 1 or not 1 <= overload_min <= overload_max:
        raise ValueError("invalid PSU envelope")
    current = abs(result.supply_current_a)
    power = result.voltage_v * result.supply_current_a
    if current <= rated_a * derating and power <= rated_w * derating:
        status = "within-rated-envelope"
    elif power >= rated_w * overload_max:
        status = "hiccup-expected-CV-invalid"
    elif power >= rated_w * overload_min:
        status = "overload-threshold-band-CV-unqualified"
    else:
        status = "outside-rated-envelope-CV-unqualified"
    return {"status": status, "current_fraction": current / (rated_a * derating),
            "power_fraction": power / (rated_w * derating),
            "actual_overload_current_a": None, "fuse_clearing_s": None}


def branch_budget(voltage_v, channel=Channel(), *, connector_v=None, shunt_a=0.0):
    """Static local branch budget; a supplied clamp voltage is NOT a part rating.

    At a conducting LED's fixed Vf, shunt leakage subtracts from LED current,
    not from the R/rectifier current. If it takes all the current an I/V curve
    is necessary. With an explicit connector voltage the load may be a clamp,
    reversed LED, or open circuit, so LED current is unknown (None).
    Reverse supply cannot be qualified by this forward model.
    """
    r, led, diode = channel.values()
    terminal = led if connector_v is None else connector_v
    _finite("branch budget", voltage_v, terminal, shunt_a)
    if min(terminal, shunt_a) < 0 or voltage_v < 0:
        raise ValueError("budget requires nonnegative forward voltage and leakage")
    current = max(0.0, (voltage_v - diode - terminal) / r)
    if shunt_a > current:
        raise ValueError("shunt takes all available current; solve the actual clamp I/V curve")
    return {"branch_a": current, "led_a": current - shunt_a if connector_v is None else None,
            "shunt_a": shunt_a, "shunt_w": terminal * shunt_a,
            "led_w": terminal * (current - shunt_a) if connector_v is None else None,
            "resistor_w": current ** 2 * r, "diode_w": current * diode,
            "terminal_w": terminal * current}


def resistor_allowance(local_ambient_c):
    """PS12 ambient derating only, NOT a chip/gel temperature prediction.

    Uni-Royal SMD-SP-007 V.7, 08-Jan-2026: 2 W P70, zero at 155 C ambient.
    No PS12 hot-spot limit or mounted K/W is supplied by this model; adequate
    heat flow and assembly/material limits still apply. No below-70 C uprating.
    """
    _finite("resistor ambient", local_ambient_c)
    if local_ambient_c < -55:
        raise ValueError("PS12 ambient below -55 C operating range")
    return RESISTOR_P70_W * max(0.0, min(
        1.0, (RESISTOR_ZERO_POWER_AMBIENT_C - local_ambient_c) / (RESISTOR_ZERO_POWER_AMBIENT_C - 70)))


def cut_sweep(*, shunt_max_a=0.0, **options):
    """Ideal one-way cuts plus ON-current diversion margin, not optical darkness.

    Raw OFF branch currents must still be zero; subtraction cannot hide backfeed.
    A maximum leakage is not a constant current sink on a disconnected branch.
    """
    _finite("shunt diversion bound", shunt_max_a)
    if shunt_max_a < 0:
        raise ValueError("shunt diversion bound must be nonnegative")
    stations = options.get("stations", 41)
    count, kcl, power = 0, 0.0, 0.0
    for span in range(stations - 1):
        for cores in CUT_SETS:
            result = simulate(**options, cuts=tuple((c, span) for c in cores))
            after = tuple("B" not in cores and c not in cores for c in CHANNELS)
            for station in range(stations):
                expected = (True, True) if station <= span else after
                if result.state(station) != expected:
                    raise ArithmeticError(f"cut truth table failed: {cores}, span {span}, station {station}")
                for core, on in zip(CHANNELS, expected):
                    if on and result.led_currents_a[core, station] - shunt_max_a <= 1e-6:
                        raise ArithmeticError(f"ON margin lost to shunt diversion: {core}, station {station}")
            kcl = max(kcl, result.kcl_error_a)
            power = max(power, abs(result.power_balance_w))
            count += 1
    return {"cases": count, "max_kcl_a": kcl, "max_power_error_w": power,
            "shunt_diversion_bound_a": shunt_max_a}


def study(options):
    """The named sensitivity cases are declared inputs, not field guarantees."""
    nominal = simulate(**options)
    psus = {"LRS-35-36": (1.0, 36.0), "LRS-75-36": (2.1, 75.6)}

    def row(name, result):
        return {"case": name, **result.summary(),
                "psu": {name: assess_psu(result, rated_a=a, rated_w=w)
                        for name, (a, w) in psus.items()}}

    loads = [row("selected inputs (defaults: historical 36 V / 2.8 V, zero leakage)", nominal)]
    zero_cable = Cable(r20_ohm_per_km=(0.0, 0.0, 0.0))
    for n in (5, options["stations"]):
        loads.append(row(f"{n} boards / zero cable R", simulate(
            **(options | {"stations": n, "cable": zero_cable}))))
    loads.append(row("historical 10 ohm/km/core, LED 3.3 V + diode 0.7 V sensitivity", simulate(
        **(options | {"cable": Cable(r20_ohm_per_km=(10.0,) * 3),
                      "channel_a": Channel(led_v=3.3), "channel_c": Channel(led_v=3.3)}))))
    loads.append(row("BYG23T high-drop screen: LED 3.3 V + diode 1.9 V, 10 ohm/km/core", simulate(
        **(options | {"cable": Cable(r20_ohm_per_km=(10.0,) * 3),
                      "channel_a": Channel(led_v=3.3, diode_v=1.9),
                      "channel_c": Channel(led_v=3.3, diode_v=1.9)}))))
    minimum_r = Channel(led_v=0, diode_v=0, resistor_error=-0.01,
                        resistor_tcr_ppm=-RESISTOR_TCR_PPM, resistor_temperature_c=125)
    loads.append(row("PS12 max-adjustment screen, zero drops, R-min at 125 C (25 C reference), zero cable R", simulate(
        **(options | {"source": Source(ADJUSTMENT_SCREEN_V), "cable": zero_cable,
                      "channel_a": minimum_r, "channel_c": minimum_r}))))

    # Series impedance is explicit and illustrative, NOT an LRS output model.
    fault_source = replace(options["source"], series_ohm=options["source"].series_ohm or 0.25)
    fault_options = options | {"source": fault_source}
    fault_rows = []
    locations = sorted({0, min(1, options["stations"] - 1),
                        options["stations"] // 2, options["stations"] - 1})
    for pair in ("AB", "CB", "AC"):
        for station in locations:
            for name, r, arc in (("hard", 0, 0), ("10ohm", 10, 0), ("100ohm", 100, 0),
                                 ("arc10", 0.1, 10), ("arc15", 0.1, 15)):
                fault = Fault("fault", (pair[0], station), (pair[1], station), r, arc)
                result = simulate(**fault_options, faults=(fault,))
                fault_rows.append({**row(f"{pair}@{station}:{name}", result),
                                   "fault_a": result.element_currents_a["fault"],
                                   "fault_w": result.element_power_w["fault"]})
    earth_rows = []
    end = options["stations"] - 1
    for arc in (10.0, 15.0):
        for earth_r in (0.0, 1.0, 10.0):
            faults = (Fault("GDT_A_E", ("A", end), ("E", end), 0.1, arc),
                      Fault("GDT_B_E", ("E", 0), ("B", 0), 0.1, arc),
                      Fault("earth_path", ("E", end), ("E", 0), earth_r))
            result = simulate(**fault_options, faults=faults)
            earth_rows.append({**row(f"A_E@{end}, B_E@0, arc={arc:g}, earth_R={earth_r:g}", result),
                               "tube_a": result.element_currents_a["GDT_A_E"],
                               "tube_w": result.element_power_w["GDT_A_E"]})
    return {"revision": REVISION, "provisional": True,
            "selected_parts": {"R1_R2": RESISTOR_MPN, "D1_D2_D3_D4": DIODE_MPN},
            "inputs": {k: asdict(v) if hasattr(v, "__dataclass_fields__") else v
                       for k, v in options.items()},
            "loads": loads, "cut_sweep": cut_sweep(**options, shunt_max_a=CLAMP_LEAKAGE_SCREEN_A),
            "fault_source_series_ohm": fault_source.series_ohm,
            "faults_cv_demand_only": fault_rows, "earth_paths_cv_demand_only": earth_rows,
            "maximum_adjustment_branch": branch_budget(ADJUSTMENT_SCREEN_V, minimum_r),
            "negative_clamp_screen": {
                "normal_positive_diversion_bound_a": CLAMP_LEAKAGE_SCREEN_A,
                "nominal_36V_2.8V_budget": branch_budget(36, shunt_a=CLAMP_LEAKAGE_SCREEN_A),
                "scope": "Monotone leakage assumption within 1300 V and <=125 C; datasheet maxima "
                         "5 uA at 25 C / 50 uA at 125 C, both at 1300 V, not 5 uA at LED voltage. "
                         "No input shunt or positive regulation. Forward-only cuts omit series reverse "
                         "leakage; 1 uA classification is not physical darkness or daylight visibility."},
            "limitations": [
                "PS122WF2201T4E uses +/-100 ppm/C referenced to 25 C from SMD-SP-007 V.7. "
                "The selected 125 C R input is not a thermal prediction. "
                "SMT changes heat flow, not nominal power loss or a proven cooler result; PR02 "
                "hot-spot/standoff/K/W data do not apply.",
                "0.7 V diode default preserves comparison, not BYG23T data at 15 mA. Its 1.9 V "
                "maximum is at 1 A / 25 C, not a minimum or full-temperature low-current bound.",
                "40.39597 V is an accessible-adjustment screen, not enforced MCOV. The legacy 35..37 V "
                "proposal is not hardware and does not make TEST automatically safe.",
                "Negative connector voltage forward-biases D3/D4, but recovery/ringing are not solved. "
                "Typical 9 V / 620 ns forward recovery at 1.5 A, 12 A/us is NOT <=5 V LED proof.",
                "Installation lead-reversal LED damage and direct-strike rebuilding are accepted. "
                "Energized cattle fencing is prohibited near the ENTIRE boundary: 4 km cable, stations, hub.",
                "RF, ordinary switching, nearby lightning, powered recovery and potted continuous thermal "
                "behavior remain unqualified. C4/C5/W3 stay open; no timer or active-stage prerequisite.",
            ]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stations", type=int, default=41)
    parser.add_argument("--spacing-km", type=float, default=0.1)
    parser.add_argument("--voltage", type=float, default=36.0)
    parser.add_argument("--source-ohm", type=float, default=0.0)
    parser.add_argument("--source-error", type=float, default=0.0, help="signed fractional error")
    parser.add_argument("--source-temp", type=float, default=25.0)
    parser.add_argument("--source-tempco", type=float, default=0.0, help="signed fraction/degree C")
    parser.add_argument("--source-ripple", type=float, default=0.0, help="selected signed peak V")
    parser.add_argument("--r-core", type=float, nargs=3, default=(6.9,) * 3, metavar=("A", "B", "C"))
    parser.add_argument("--cable-error", type=float, nargs=3, default=(0.0,) * 3)
    parser.add_argument("--cable-temp", type=float, default=20.0)
    parser.add_argument("--copper-alpha", type=float, default=0.00393)
    parser.add_argument("--resistor-ohm", type=float, nargs=2, default=(2200.0,) * 2)
    parser.add_argument("--resistor-error", type=float, nargs=2, default=(0.0,) * 2)
    parser.add_argument("--resistor-temp", type=float, default=RESISTOR_REFERENCE_C,
                        help="selected resistor temperature in C; resistance references 25 C")
    parser.add_argument("--tcr-ppm", type=float, nargs=2, default=(0.0,) * 2,
                        help="signed ppm/C relative to 25 C; zero preserves nominal comparison")
    parser.add_argument("--led-v", type=float, nargs=2, default=(2.1,) * 2)
    parser.add_argument("--diode-v", type=float, nargs=2, default=(0.7,) * 2)
    parser.add_argument("--junction-temp", type=float, default=20.0)
    parser.add_argument("--led-tempco", type=float, nargs=2, default=(0.0,) * 2)
    parser.add_argument("--diode-tempco", type=float, nargs=2, default=(0.0,) * 2)
    parser.add_argument("--json", action="store_true", help="machine-readable study on stdout")
    args = parser.parse_args(argv)
    source = Source(args.voltage, args.source_ohm, args.source_error, args.source_temp,
                    args.source_tempco, args.source_ripple)
    cable = Cable(tuple(args.r_core), tuple(args.cable_error), args.cable_temp, args.copper_alpha)
    channels = [Channel(args.resistor_ohm[i], args.led_v[i], args.diode_v[i],
                        args.resistor_error[i], args.tcr_ppm[i], args.resistor_temp,
                        args.junction_temp, args.led_tempco[i], args.diode_tempco[i]) for i in (0, 1)]
    try:
        report = study(dict(stations=args.stations, spacing_km=args.spacing_km, source=source,
                            cable=cable, channel_a=channels[0], channel_c=channels[1]))
    except (ValueError, ArithmeticError) as exc:
        parser.exit(2, f"Analysis failed: {exc}\n")
    if args.json:
        print(json.dumps(report, indent=2, allow_nan=False))
        return
    print(f"Dog Fence {REVISION}: PROVISIONAL DC model, not a protection qualification")
    print(f"{args.stations} stations; same-end A/C positive, B negative; all end terminals separate")
    print("Inputs: " + json.dumps(report["inputs"], sort_keys=True))
    print("Selected parts: " + json.dumps(report["selected_parts"]))
    print("\nLoad cases: source A / W; branch (= zero-leak LED) min..max mA; max resistor W; LRS-35 / LRS-75")
    for r in report["loads"]:
        states = " / ".join(p["status"] for p in r["psu"].values())
        print(f"{r['case']}: {r['source_a']:.6f} A / {r['source_w']:.4f} W; "
              f"{r['led_min_ma']:.4f}..{r['led_max_ma']:.4f} mA; {r['resistor_max_w']:.6f} W; {states}")
    print("\nClean-cut regression: " + json.dumps(report["cut_sweep"]))
    print("\nNegative-clamp diversion (no extra PSU load): " + json.dumps(report["negative_clamp_screen"]))
    print(f"\nFaults: CV DEMAND ONLY, illustrative source series R={report['fault_source_series_ohm']:g} ohm")
    print("case | source A | path A | path W | LRS-35 / LRS-75")
    for r in report["faults_cv_demand_only"] + report["earth_paths_cv_demand_only"]:
        current = r.get("fault_a", r.get("tube_a"))
        current_text = "indeterminate" if current is None else f"{current:.6f}"
        power = r.get("fault_w", r.get("tube_w"))
        states = " / ".join(p["status"] for p in r["psu"].values())
        print(f"{r['case']} | {r['source_a']:.6f} | {current_text} | {power:.6f} | {states}")
    print("\nNo fuse clearing time or GDT extinction follows from these DC solutions.")
    print("217 2 A data: 3 A for >=60 min; 4.2 A <=30 min; 5.5 A 0.05..2 s, under test conditions.")
    print("Hiccup timing/capacitor discharge, LED/clamp I-V, cable bounds and potted temperatures remain unqualified.")
    for limitation in report["limitations"]:
        print("NOTE: " + limitation)


if __name__ == "__main__":
    main()
