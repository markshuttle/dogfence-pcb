# Electrical Engineering Record

**Revision: 1.2.0-dev. P2 analysis record, 2026-09-06. Electrical release HOLD.**

This record accompanies `scripts/analyze_limits.py` and `tests/test_electrical.py`. It does not approve a manufacturing BOM or qualify hardware. The model implements the agreed same-end TEST topology; **LED reversal/pulse protection and coordinated source/fault protection are not implemented in the circuit**. C4 and C5 remain design holds, not merely tests awaiting an otherwise approved design. W3 remains a continuous-duty design/thermal qualification hold. Do not remove the controlled `pcb/verification.json` engineering holds because these tests or KiCad file checks pass.

No PCB, schematic, BOM, production output, switch terminal assignment, or main document was changed by this P2 work. Other agents' geometry/library and documentation work is independent. All new component suggestions below are **candidates, not authorized substitutions, stock allocations, or drop-ins**.

## 1. Implemented Model

The inspected indicator circuit is:

```text
WIRE_A -> R1 2.2k -> D1 anode(2), cathode(1) -> LED_A_POS -> J_LED_A.1
WIRE_C -> R2 2.2k -> D2 anode(2), cathode(1) -> LED_C_POS -> J_LED_C.1
J_LED_A.2 = J_LED_C.2 = WIRE_B
External LED anode goes to terminal 1, cathode to terminal 2.
```

GDT_AB, GDT_BC and GDT_AC connect the named core pairs **before** the indicator resistors. GDT_A_E, GDT_B_E and GDT_C_E connect the respective cores to the separate EARTH bus. Thus R1/R2 do not limit a GDT's source follow current. D1/D2 are onsemi `1N4007G`; the current integration BOM has corrected the earlier LGE attribution.

The functional hub connections used in the calculation are:

| End | RUN | OFF | TEST |
| :--- | :--- | :--- | :--- |
| Start A | T1 | Individually isolated | Positive |
| Start B | T1 | Individually isolated | Negative |
| Start C | T1 | Individually isolated | Positive |
| End A | T2 | Individually isolated | Individually isolated |
| End B | T2 | Individually isolated | Individually isolated |
| End C | T2 | Individually isolated | Individually isolated |

Ties belong on the source-side contacts. There is no permanent End A/C strap, opposite-end return, both-B return, direction selector, or normal-operation timeout. TEST/OFF disable RF containment. The actual six-pole switch's DC interruption and global transfer sequence still require approval; this table is not its physical terminal numbering.

### Parameters And Equations

Defaults are **41 stations**, numbered 0 through 40 at 0.1 km spacing, including both shed-end boards; 82 indicator branches; 36 V; and 6.9 ohm/km per core at 20 C, or 27.6 ohm per 4 km core. The default LED drop of 2.1 V and rectifier drop of 0.7 V reproduce the earlier 2.8 V illustrative calculation. **They are not an APEM SG-characterization result.**

For core `c`, station `s`, and span length `dx`:

```text
r_span[c] = r20[c] * dx * (1 + cable_error[c]) * (1 + alpha * (T_cable - 20))
R[c,s]    = R_nom[c,s] * (1 + R_error[c,s]) * (1 + TCR_ppm[c,s]*1e-6*(T_R - 20))
V_LED     = V_LED_20 + LED_tempco * (T_junction - 20)
V_D       = V_D_20   + D_tempco   * (T_junction - 20)
V_source  = V_setting * (1 + source_error) * (1 + source_tempco*(T_source - 25))
            + selected_ripple_peak
I[c,s]    = max(0, (V[c,s] - V[B,s] - V_LED[c,s] - V_D[c,s]) / R[c,s])
P_R       = I^2 * R
P_LED     = I * V_LED
P_D       = I * V_D
```

The copper temperature coefficient defaults to 0.00393/C as an engineering approximation. Tolerances and temperature coefficients are **signed selected corners**, not random distributions or automatically combined manufacturer maxima. Per-core cable resistance/errors and per-channel R/LED/diode parameters are independent. `channel_overrides` permits station-specific branches. Temperature correction is an input, not a self-heating iteration; reject negative/nonfinite effective parameters. Contact/splice aging, actual cable maximum resistance, and LED I/V distributions still need data.

- Nodes A/B/C are separate everywhere except the explicit source-side A/C connection. Healthy symmetry is an output/check, not a fault-model simplification.
- A cut `("A", 0)` removes the A conductor between stations 0 and 1. Span 39 is 3900-4000 m. Cut core names must be single valid core names; `"AB"` is not accepted as one core.
- Ideal wires and zero cable resistance are contracted exactly. An ideal short across an ideal nonzero source raises `IdealSourceShort`; it cannot produce a finite fuse verdict.
- Piecewise-linear passive branches are solved using damped Newton steps with sparse symmetric elimination. Convergence is checked against KCL, not just small voltage changes. Default residual tolerance is 1e-10 A; nonconvergence is an error.
- Floating components use a numerical voltage reference **without a conductance to earth/negative**. Their undetermined absolute node voltages are returned as `None`. Blocked one-way branches cannot backfeed those islands. These voltages are not inferred to be zero or safe to touch.
- Ideal-link currents are recovered by KCL where the ideal connection graph is a tree. Ideal cycles have indeterminate sharing, reported as `None`, with zero ideal-link dissipation. No equal-sharing assumption is made.
- Source and return current, every finite path's current/power, individual resistor/LED/diode power, KCL residual, and total power residual are available. Source power equals cable, branch, source-series, and fault-path dissipation within numerical tolerance. Only without cross-core/earth faults does source current equal the sum of indicator currents.
- `Fault(name, a, b, ohm, arc_v)` adds an explicit node-to-node path. Zero arc voltage is an ohmic fault; a positive arc voltage uses `I = sign(dV)*max(abs(dV)-V_arc,0)/R_arc`. It is a **conditional ignited-state load line**, not a sparkover, holding-current, hysteresis, or extinction model. The 10/15 V study values are sensitivities around published typical arc voltages, not guaranteed limits.
- `E` nodes and earth-path impedances must be explicitly supplied. This permits two fired line/earth tubes at different stations to complete a loop even with no DC-negative/PE bond. It makes **no proposal for unbonded electrodes**. A single tube with no modeled DC return has zero modeled steady current, not demonstrated safety in the real site's capacitive/leakage/PE network.

The solver does not model the external LED's internal reverse voltage, semiconductor recovery/capacitance, ignition, cable inductance/propagation, RF, lightning, cattle-fence pulses, PSU control dynamics, optics, or actual temperature. A zero forward current under reversed supply is expressly **not** a C4 protection pass.

### Reproduction

From the repository root, using Python's standard library only:

```bash
python3 -B -m unittest discover -s tests -p test_electrical.py -v
python3 -B scripts/analyze_limits.py
python3 -B scripts/analyze_limits.py --json
python3 -B scripts/analyze_limits.py --help
```

`--json` writes the declared inputs, summaries, cut regression, and prospective fault study to stdout; no scratch evidence or third-party numeric packages are needed. CLI two-value channel arguments are A then C; three-value cable arguments are A, B, C. `--r-core` units are ohm/km at 20 C, not resistance of the whole perimeter. The CLI clean-cut sweep is a functional test and fails if selected inputs cannot produce the expected electrically ON states; use `simulate()` directly for undervoltage/reversed-source investigations.

Verified on Python **3.14.4**: **21 focused tests PASS**, including all **280 clean-cut cases** (7 combinations x 40 spans), **615 inter-core fault cases** (3 pairs x 5 states x 41 stations), all five earth-connected station locations (0/10/20/30/40), repair/retest, asymmetric parameters, disconnected islands, exact zero-R cases, analytic single-station/parallel-load solutions, source impedance, parameter validation, and CLI JSON/error status.

Clean-cut sweep maximum KCL residual: **4.34e-14 A**. Maximum source/power-balance residual: **7.71e-12 W**. These are numerical errors, not measurement uncertainty or model accuracy.

## 2. Calculated Results

All values in this section are calculations, not measurements. First four rows use the default ideal 36 V source and nominal R; last row is the explicitly constructed upper screening case in section 3.

| Case | Source A | Source W | LED current min/max, mA | Largest resistor W |
| :--- | ---: | ---: | ---: | ---: |
| 41 boards, 27.6 ohm/core, 2.8 V total branch drop | 0.847705 | 30.5174 | 8.0448 / 15.0909 | 0.501018 |
| Five boards, zero cable R | 0.150909 | 5.4327 | 15.0909 / 15.0909 | 0.501018 |
| All 41 boards, zero cable R | 1.237455 | 44.5484 | 15.0909 / 15.0909 | 0.501018 |
| 41 boards, 40 ohm/core, 3.3 V LED + 0.7 V diode | 0.727083 | 26.1750 | 6.2096 / 14.5455 | 0.465455 |
| 40.39597 V, zero drops, minimum R, all 41 boards, zero cable R | 1.528903 | 61.7615 | 18.6452 / 18.6452 | 0.753190 |

The low-R entire-load case is essential: a five-board demonstration does not establish LRS-35-36 capacity for 41 boards. LRS-75-36 has capacity margin for these declared cases before applicable thermal/input derating and added protection/auxiliary load. Neither supply's nameplate is yet confirmed, and neither is a coordinated fence-fault protective device.

### Open-Circuit Observability

The expected states pass at **every** span, including both terminal spans:

| Cut | Before | After |
| :--- | :--- | :--- |
| A | Both on | A off, C on |
| B | Both on | Both off |
| C | Both on | A on, C off |
| AB, AC, BC, ABC | Both on | Both off |

Tests remove complete cuts at spans 0, 19, and 39 in turn and verify that repair reveals the next site; representative successive single-core faults are also tested. The 1 microamp ON discriminator is only a numerical state classifier. No daylight brightness is established at that threshold.

Negative controls deliberately reproduce both defects: a permanent End A/C strap illuminates the broken channel after an A-only or C-only cut; connecting both B ends to negative leaves both channels lit after a B-only cut. A failed-short AC arrester can similarly mask an A cut. No clean-cut localization promise applies to mixed shorts/cuts or failed indicators/protection parts.

## 3. Continuous Operation: W3 Open

The current Mean Well specifications [S4] give 32.4-39.6 V adjustment, +/-1% voltage tolerance **including setup, line and load regulation**, 200 mV peak-to-peak ripple/noise under the stated measurement arrangement, and +/-0.03%/C temperature coefficient over **0-50 C**. Do not add the separate line/load figures a second time to the 1%. Do not extrapolate that temperature coefficient to the whole -30 to +70 C operation range.

The study deliberately stacks the upper adjustment setting, +1% tolerance, +0.75% temperature contribution at 50 C, and a +0.1 V ripple peak:

```text
V_screen = 39.6 * 1.01 * (1 + 0.0003 * (50 - 25)) + 0.1 = 40.39597 V
R_min    = 2200 * 0.99 * (1 - 50e-6 * (125 - 20))        = 2166.5655 ohm
I_upper  = V_screen / R_min                            = 18.6452 mA
P_upper  = V_screen^2 / R_min                           = 0.753190 W
```

This is a **conservative chosen screening envelope, not Mean Well's guaranteed combined maximum**, a measured accessible-adjustment limit, or a claim that a resistor will operate at 125 C. Adjustment-range/tolerance interaction must be confirmed. Treating a ripple peak as continuous overestimates its steady heating but gives a simple upper screen. Zero LED and diode drops avoid claiming unprovided minimum Vf; they also screen an output short. Supply startup, overshoot, malfunction, external surges, aging, and any voltage above this declared window are not covered. The PSU's 41.4-48.6 V overvoltage shutdown range is **not** enforcement of this 40.39597 V screen.

Vishay [S3] specifies MBE0414 **0.65 W at 70 C in standard mode, 125 C maximum film**, versus **1 W at 70 C in power mode, 155 C maximum film**. Above 70 C, the published derating slopes reach zero at the corresponding film limit. The helper implements:

```text
P_standard(T_local) = 0.65 * clamp((125 - T_local)/(125 - 70), 0, 1)
P_power(T_local)    = 1.00 * clamp((155 - T_local)/(155 - 70), 0, 1)
```

The data explicitly makes the rating conditional on actual film temperature and heat-flow support. Gel, lead forming, copper, lid LEDs, sun and enclosure temperature change that support. The 0.753190 W screen already exceeds standard-mode P70; being below 1 W is not a continuous-safe potted result. At nominal source-end current, two resistors dissipate **1.0020 W/board**; the two rectifiers add approximately **0.0211 W** at the assumed 0.7 V. The zero-drop upper screen puts **1.5064 W/board in the resistors**. A higher-wattage replacement at the same resistance does not reduce those watts.

**Disposition:** do not approve retaining R1/R2 for unrestricted adjustment/solar exposure yet. Prefer a controlled 36 V setting with an enforceable maximum and verify its continuous thermal envelope; alternatively qualify a pulse/thermally suitable resistor or split network while retaining the required effective resistance/current. No substitute MPN is approved here. Measure steady-state potted resistor body/lead and estimated film temperatures, LED junction margin, connectors, gel and enclosure at credible solar/internal temperatures. Use sensors and uncertainty margins, not touch. Include LED open/reversal/clamp-conducting and output-short cases. Normal TEST must be continuous-safe without a timer.

The calculated normal J_IN currents are local branch currents: one branch on A and C, their sum on B, up to **37.2904 mA** for the two zero-drop branches in the declared upper screen. The WAGO through-splices, source wiring and hub carry the distributed perimeter current instead. Connector heating needs actual `I^2 * R_contact` and temperature-rise evidence; a listed contact rating alone is not a temperature result. Surge current takes different PCB paths. There is no 72 A terminal or board current rating in this analysis.

## 4. Powered Faults: C5 Open

### Source And Fuse Interpretation

`assess_psu()` checks **both** rated current and rated output power, with a configurable continuous derating factor. Mean Well [S4] specifies overload at **110-150% of rated output power**, hiccup mode, automatic recovery after fault removal. The model distinguishes within-rated, outside-rated, overload-threshold-band, and above-the-band CV demand. It does **not** replace the supply by a constant-current source or claim a hiccup duration/duty cycle. Actual overload current and fuse-clearing time are returned as `None`.

Littelfuse 217 data [S5], for the specified `0217002.MXP` 2 A fuse, includes **70 A interruption at 60/75 VDC**, not just a 250 VAC label. Relevant standardized continuous-current tests are:

| Applied current | Published opening condition |
| :--- | :--- |
| 3.0 A, 150% | 60 minutes minimum |
| 4.2 A, 210% | 30 minutes maximum |
| 5.5 A, 275% | 0.05 to 2 seconds |
| 8.0 A, 400% | 0.01 to 0.3 seconds |

These are specified test conditions, not a prediction under source hiccup, outdoor temperatures or pulse repetition. The nominal melting I-squared-t of 5.73 A2s is not a complete low-current clearing or cyclic cooling model. The former instantaneous 2 A fuse-blow verdict is removed. Do not fix coordination by simply choosing a smaller fuse without healthy-load, cable, fault, temperature and inrush discrimination.

### Actual Topology Locations

The fault study explicitly uses **0.25 ohm lumped source-path resistance**, with **0.1 ohm arc slope** for ignited-state cases. These are transparent example inputs, not measured PSU/lead/GDT specifications. `--source-ohm` changes that input; the study uses the 0.25 ohm example when the nominal source is ideal. Hard faults are exact zero ohms. Each location includes both channels' distributed load and the separate A/B/C conductors. Selected results:

| Path/state | Station / distance | Source A | Fault-path A | Fault-path W | Interpretation |
| :--- | :--- | ---: | ---: | ---: | :--- |
| AB hard short | 0 / 0 km | 144.000000 | 144.000000 | 0 ideal | CV invalid for either PSU; **not actual fault current** |
| AB 100 ohm | 0 / 0 km | 1.197071 | 0.357007 | 12.745423 | Within LRS-75 rating; resistor-like fault heating can persist |
| AB hard short | 20 / 2 km | 1.600490 | 1.160727 | 0 ideal | Within LRS-75 rating; 2 A fuse not a prompt disconnect |
| AB 100 ohm | 20 / 2 km | 0.969602 | 0.199537 | 3.981497 | Within either nominal PSU envelope |
| AB hard short | 40 / 4 km | 1.112913 | 0.507648 | 0 ideal | LRS-35 overload band; within LRS-75 rating |
| AB 100 ohm | 40 / 4 km | 0.919507 | 0.145702 | 2.122913 | Within either nominal PSU envelope |
| AB ignited 10 V | 40 / 4 km | **0.979810** | **0.259543** | **2.602168** | Follow-current load line below 1 A total |
| AB ignited 15 V | 40 / 4 km | 0.913626 | 0.134598 | 2.020787 | Also below either source's rating |
| A_E@40 and B_E@0, each 10 V, shared-earth path 1 ohm | Both shed ends | 1.192841 | 0.417771 per tube | 4.195167 per modeled tube path | No negative/PE bond needed for this two-tube circuit |
| Same two paths, each 15 V | Both shed ends | 0.863876 | 0.025684 per tube | 0.385321 per modeled tube path | Positive load-line current is not proof the physical arc holds |

CB results equal AB only for the symmetric default inputs; both are separately solved. AC has no driven steady follow current in the healthy symmetric case, not a generic guarantee under asymmetry, cuts or an external transient. A short AC tube creates a diagnostic backfeed path. All three common-mode tubes are additionally tested at the actual five earth-connected station indices. The earth-path values 0/1/10 ohm are sensitivities, not an earthing design or electrode measurements.

An ideal short's zero modeled dissipation excludes real contact/arcing resistance; cable and source-path power still dissipate energy. A large CV demand is useful for showing loss of regulation, but **cannot** be used as sustained GDT heating or as evidence that the fuse will open. Conversely, the sub-rated far-end cases demonstrate that the PSU overload function need not intervene. GDT glow-to-arc transition current is not holding current, and 36 V below 470 V DC sparkover says nothing sufficient about post-ignition extinction.

### Architecture Decision And Interface Requirements

**Bare GDTs plus the existing fuse/hiccup PSU are not an approved protection architecture.** The following are bounded engineering paths, not completed selections:

1. **Retain bare tubes only with explicit DC holdover and fault containment evidence.** Obtain Ruilon/Bencent extinction specifications for the actual source/cable RLC network, temperature, life, pulse polarity and restarting PSU. Bourns `2027-47-BLF` is a concrete alternative to investigate: [S11] specifies 135 V DC holdover with extinction under 150 ms, but expressly says **"network applied"**. Its test network must be obtained and compared with this system; a voltage number alone is insufficient. The current drawing is **8.0 +/-0.4 mm body diameter**, not the previously suggested 6 mm drop-in. It cannot silently replace the overpass or SMT tubes. Its 1 kV/us sparkover figure is a **typical distribution**, not a guaranteed better residual-voltage limit. No substitution is approved.
2. **Use a coordinated series GDT/MOV path instead of an unqualified bare tube where self-extinction cannot be established.** Bourns `GMOV-14D500K` is an actual manufacturer-supported AC/DC hybrid candidate [S12]: 65 VDC MCOV, <1 microamp leakage and 4 pF capacitance at the stated 25 C conditions, MOV 82 V +/-10% at 1 mA, and a 230 V nominal GDT. This gives a concrete non-arc voltage-limiting element in series with the tube, rather than trying to infer extinction from 470 V sparkover. However its front protection level is still up to 800 V under the stated test; its 150 V clamp entry is **typical**, not a 5 V LED clamp. Body maximum 16.5 mm diameter/20 mm height and 7.5 +/-1 mm lead pitch are not existing footprints. DC recovery, post-damage failure, thermal disconnect/containment, RF/cable coordination, protected geometry and enclosure fit remain to qualify. Do not parallel it with the original bare GDT and assume follow current is then solved; the bare path would remain.
3. **A source disconnect can supplement either path, not replace missing remote-fault coverage.** A simple fixed overcurrent threshold cannot distinguish the 0.86-0.98 A follow-current cases from the provisional normal-load range, which extends beyond 1.2 A at low cable R. A larger supply worsens available follow energy. If retaining tubes without guaranteed self-extinction, event/local-temperature sensing or another proven means of detecting every sustaining path must drive a latched disconnect. No such complete detector/shutdown design is implemented. Do not call a hub relay alone a C5 fix.

Required TEST interface behavior for the next circuit decision:

- Maintain nominal 36 V and an **enforced** allowed maximum appropriate to the accepted resistor/LED design; detect overvoltage independently of the PSU's higher OVP threshold. Include supply adjustment, tolerance, startup, failed regulation and source-interface drop.
- Carry the entire healthy low-R load continuously, including tolerances and auxiliary/clamp currents; the present screening demand is 1.528903 A/61.7615 W. Apply actual source/interface derating and margin rather than selecting from the nominal healthy 0.847705 A alone.
- Coordinate fast current limiting, short-circuit interruption, and **latched** source isolation following detected surge/follow-current, persistent overload or repeated PSU dropout. No automatic retry into a known fault. Operator reset must not automatically restore RUN.
- Isolate TEST positive before the A/C source split and TEST negative from Start B using appropriately rated, independently reviewed interruption/isolation means. Keep all six mode contacts independent, prevent transmitter/PSU connection during global transfer, and retain protective-earth continuity. Never open PE to extinguish a GDT.
- Specify the actual maximum fault energy and interruption time from component/path limits, not an arbitrary safe timeout. Measure source output capacitance and current waveforms: `E_cap = C*V^2/2`, `E_GDT = integral(V_GDT(t)*I_GDT(t) dt)`. Include cable stored energy, turn-off overshoot and repeated hiccup pulses. Require sufficient off time and a verified recovery test before re-energization.
- Prove detection or benign continuous fault behavior for **sub-rated resistive shorts** as well as GDT follow current. Overcurrent protection alone cannot promise this; normal/fault current ranges overlap. Local thermal interruption in a GDT path does not protect an unrelated cable resistive short.

No time limit on healthy TEST is proposed. A fault-triggered latch is a different safety function. The preferred immediate evidence request is a quantified holdover/recovery comparison for the actual tubes and the `2027-47` candidate; if that fails, evaluate the series GDT/MOV architecture before freezing the PCB. None of these routes establishes a board-level lightning rating.

## 5. LED Protection: C4 Open

### Necessary Topology

With only the series rectifier, reversed supply puts two dissimilar reverse-biased junctions in series. Their leakage/capacitance determines voltage sharing; it does not guarantee LED VR <=5 V. With normal supply but reversed flying leads, the rectifier conducts and the external LED takes reverse voltage. An ordinary PCB antiparallel diode, anode at B and cathode at LED_POS, is then **also reverse biased** and does not solve that second fault.

The smallest credible **DC-reversal candidate** is a true low-voltage avalanche/shunt clamp from LED_POS to B, downstream of the existing R and rectifier. It must conduct in avalanche for positive connector voltage and in the forward direction for negative connector voltage. The existing R/D must remain in series with **every** core-to-connector path, so a clamp cannot introduce B-to-A/C backfeed. A bridge or a clamp directly across the core pair cannot be validated by the existing one-way-rung model.

Required evidence is simultaneous, not interchangeable:

```text
V_clamp_positive_max(I, T, tolerance, ringing) <= 5 V     # LED leads reversed
abs(V_clamp_negative_min(I, T, ringing))       <= 5 V     # source reversed
I_LED_normal_min = I_branch_min - I_shunt_max(V_LED_max,T) # retain daylight current
I_LED_peak and pulse energy <= accepted APEM pulse limits # correct orientation too
```

The accessible APEM product page [S1] confirms no resistor, family 1.8-3.3 V, 20 mA maximum and 5 V reverse maximum. It does not provide the **exact SG LED's maximum Vf over current/temperature**, reverse-leakage distribution or a forward-pulse safe operating envelope. The family voltage range is not a guaranteed min/max junction I/V specification at all temperatures. Pending better data, do not design above 20 mA on the assumption that short pulses are harmless, or trade away existing useful current without a daylight test.

### Researched Candidates

| Candidate | Accessible primary data | Decision / missing evidence |
| :--- | :--- | :--- |
| **Vishay BZX85C3V9-TR**, two proposed PCB clamps | [S6], rev. 2.9: VZ **3.7-4.1 V at 60 mA**, 5 ms pulse, 25 C; dynamic R <15 ohm at that point; coefficient -0.07 to -0.02 %/C **at 60 mA**; leakage <10 microamp **at 1 V**. DO-41; 0.86 mm maximum lead. | Best minimal passive candidate to characterize, **not approved**. Available DC branch current is <18.65 mA in the declared screen, below its 60 mA VZ test point. A monotone quasi-static I/V assumption therefore makes the 4.1 V point useful, unlike a 5 mA-tested small zener. But no guaranteed leakage at the green LED's actual Vf/temperature, no full-current/full-temperature clamp envelope, and no forward transient LED-current protection are established. Its forward-voltage graph is typical, not a guaranteed negative-polarity clamp bound. |
| **Vishay BZX85C4V3-TR** | [S6]: **4.0-4.6 V at 50 mA**, coefficient -0.05 to +0.01 %/C there, leakage <3 microamp at 1 V. | More separation from green Vf, less reverse-voltage margin. Still no guaranteed leakage at 3.3 V or actual maximum green Vf. Not approved. |
| **Nexperia BZT52H-B3V9** | [S7], rev. 7: **3.82-3.98 V at 5 mA**, differential R up to 95 ohm at 5 mA and 500 ohm at 1 mA; coefficient -3.5 to 0 mV/K at 5 mA; leakage <=3 microamp at 1 V; VF <=0.9 V at 10 mA under pulse test. | Not enough evidence for a 16-19 mA reversed-lead DC load. The 5 mA VZ maximum is not its clamp maximum at that higher current; a small-signal differential resistance at one point is not a global slope bound. The headline 830 mW requires 1 cm2 cathode copper; standard-footprint P25 is 375 mW. No implementation approval or packaging suffix allocation. |
| **TI TL431BQDBZR**, adjustable shunt fallback | [S8], SLVS543S: 1-100 mA recommended cathode range; B-grade Vref **2.483-2.507 V at 10 mA**; 34 mV maximum full Q-temperature deviation; Iref <=4 microamp, deviation <=2.5 microamp; dynamic impedance <=0.5 ohm at the specified low-frequency conditions. | A sharper, calculable DC threshold is possible, at the cost of two divider resistors per channel and reverse-polarity design. Not an automatically qualified fast clamp. Off-current <=0.5 microamp is tested at **REF=0**, not at the near-threshold REF voltage during normal LED operation. Need actual off-region loading, startup/overshoot, capacitive stability, negative-polarity behavior, thermal/pulse data and LED Vf. No complete circuit/BOM selected. |
| **TI TL431LIBQDBZR** | [S9]: 1-15 mA recommended cathode range, 18 mA absolute positive limit. | **Reject as a direct replacement shunt for this unrestricted branch.** Reversed/open-LED branch current can exceed 15 mA. The similar name does not confer the standard TL431's 100 mA capability. |

For example, extrapolating the BZX85C3V9 test-point coefficient from 25 to -40 C gives `4.1*(1 + 0.0007*65) = 4.28655 V` at that test point. This is a useful **screening calculation**, not proof of a guaranteed 4.28655 V transient/full-temperature clamp at this application's current. Hot low-current leakage and the cold LED's higher Vf can both matter to brightness. Obtain those bounds rather than silently using the nominal zener number or a typical curve.

### Forward-Pulse Obstacle

Even a perfectly bounded 4 V clamp across an LED does not enforce 20 mA: a correctly oriented LED may take excessive current **before** its terminal voltage reaches the clamp threshold. The existing R limits but does not establish pulse safety. At an illustrative 950 V input and the nominal 2.8 V branch drop, `branch_budget(950)` gives **430.5 mA and 407.8 W instantaneous resistor demand**. This is an electrical stress screen, not the actual transient waveform or absorbed energy. Neither a 1 W DC resistor rating nor a zener's pulse-power rating qualifies the LED.

Simply splitting the present 2.2 kohm into a pre-clamp resistor and a post-clamp resistor also needs a feasibility check. With only the broad family screening values Vf_min=1.8 V, Vf_max=3.3 V, an ideal clamp `Vc <=5 V`, a desired high-Vf source-end current of `(36-3.3-0.7)/2200 = 14.545 mA`, and a 20 mA peak ceiling:

```text
R_post >= (Vc - 1.8)/0.020        # bound current for the low-Vf LED
R_post <= (Vc - 3.3)/0.014545...  # do not clip normal high-Vf LED current
```

Even with **zero clamp tolerance**, both require Vc >=7.3 V, incompatible with a 5 V reversed-lead limit. This does not prove the actual SG LED has that broad Vf spread; it proves that **those family numbers are insufficient to approve the simple split-resistor solution**. Narrower exact LED data, an accepted optical-current tradeoff, or a separately qualified active current limiter is needed. Do not choose a 20 mA nominal current-regulator part whose maximum exceeds the LED's 20 mA limit.

A supportable next architecture must therefore retain the one-way series path and provide **both local output-polarity voltage limiting and a demonstrated forward-current/pulse bound**. A pulse-rated upstream impedance plus a protected low-voltage current-limiting stage and output clamp is a credible larger alternative if the passive feasibility window does not close. Its compliance voltage, quiescent current and branch R must be recomputed to preserve the 6-15 mA-class useful field currents; no such active stage is selected or represented as validated by this DC model. Source shutdown alone cannot stop a transient induced locally in a kilometre-scale cable.

Measure the voltage at the **actual LED terminals**, not only the PCB connector: the nominal 200 mm flying leads add inductance and coupling, so clamp-loop placement and ringing can consume the reverse-voltage margin. Changing their polarity must not disconnect the protection from the LED being protected.

Rectifier coordination is also open. onsemi [S2] gives **1000 V repetitive reverse**, 1200 V **nonrepetitive** under the stated half-wave condition, junction range **-65 to +150 C**, and reverse leakage maxima 10 microamp at 25 C / 50 microamp at 100 C at rated DC voltage. The G suffix identifies the Pb-free order option; do not infer a 175 C limit from legacy prose. No specified fast-recovery/ringing bound is supplied here. The reviewed GDT data [S10] gives up to 950 V impulse sparkover for SMD5050-470NA and 1100 V for 2R470TD-8 at 1 kV/us; B5G470L's 850 V covers **99% of measured values**. Account for actual differential/common-mode paths, unequal ignition and lead inductance; do not treat 1200 V nonrepetitive rectifier data as blanket repetitive margin or 470 V as a transient clamp. Cable impulse withstand is unverified.

## 6. P3 Integration Handoff

**Released protection MPNs: none. Approved new circuit/BOM delta: none.** Keep C4/C5/W3 open and do not populate a speculative protection footprint merely to make the revision appear complete. Normal/DC model and test implementation is complete for its stated scope; P2's full electrical-design exit is not met.

The exact **C4-A candidate netlist delta**, solely for evaluation if its evidence closes, is:

| Proposed reference | Candidate MPN | Required connections | Quantity |
| :--- | :--- | :--- | ---: |
| ZD1 | Vishay BZX85C3V9-TR | Cathode / KiCad pin 1 to `LED_A_POS` = D1.1 = J_LED_A.1; anode / pin 2 to `WIRE_B` = J_LED_A.2 | 1 |
| ZD2 | Vishay BZX85C3V9-TR | Cathode / pin 1 to `LED_C_POS` = D2.1 = J_LED_C.1; anode / pin 2 to `WIRE_B` = J_LED_C.2 | 1 |

R1/R2, D1/D2, terminal polarity and the one-way series order stay unchanged in that candidate. Do **not** connect these clamps to EARTH, the resistor input, or across D1/D2. Candidate DO-41 maximum body is 4.1 x 2.6 mm, lead maximum 0.86 mm; a 1.10 mm nominal finished PTH permits 1.02 mm at -0.08 tolerance, or 0.16 mm diametral lead clearance. Pad/annular ring, spacing, forming, pulse loop and actual placement still require P3/assembler acceptance. No coordinates, footprint fit, availability/C-code, or current sharing are assumed. If eventually selected alone it adds two THT parts, but **alone it does not close the forward-pulse requirement**; final counts depend on the complete design.

For the **C4-B active-clamp investigation**, an explicit DC starting circuit is TL431BQDBZR cathode pin 1 to the same LED_POS, anode pin 3 to B, reference pin 2 to a divider with 4.42 kohm LED_POS-to-REF and 10.0 kohm REF-to-B. Its ideal threshold is about 3.598 V; calculate reference, divider tolerance/TCR, Iref, cathode-current dependence, and transient errors before assigning a bound. Divider nominal loading alone is approximately 0.23 mA at 3.3 V. Divider MPNs and reverse protection are **not selected**; this is not a complete alternative BOM or pulse-safe circuit.

The next bounded decisions/evidence are:

1. **APEM:** obtain SG02E max/min Vf vs current and junction temperature, continuous-current derating, permitted forward pulse current/energy/repetition, reverse limit conditions and harness capacitance. Measure representative purchased parts and daylight ON/OFF at 5 m, but do not replace manufacturer worst-case bounds with a few samples.
2. **Clamp vendor/design:** for BZX85C3V9/C4V3, request maximum I at the actual LED maximum Vf over temperature and maximum positive/negative clamp voltage over the available branch current and defined pulse envelope. A provisional brightness budget is <=0.3 mA shunt diversion at the minimum useful current (about 5% of the 6.21 mA sensitivity), subject to actual 5 m acceptance; it is a target, not a part specification. If unavailable or incompatible, use the active-stage route and qualify its current limit rather than adding a guessed zener.
3. **Source/GDT:** confirm PSU nameplate, setting/adjustment behavior, thermal derating, output C, overload/hiccup I(t), and shutdown/restart response. Obtain actual tube holdover test networks/conditions and a quantified quenching/failure-containment decision for every discharge path. Require the same review for `2027-47-BLF` or `GMOV-14D500K` before any geometry/BOM substitution.
4. **Thermal and transients:** settle the enforceable supply window and R choice, then test continuous normal/reversal/fault conditions in the potted/sun-heated assembly. Define the surge and nearby-cattle-fence pulse source impedance, polarities, repetitions and energy before approving rectifiers, resistors, clamps or shutdown timing. Keep an unpotted reference; use appropriate isolated/high-voltage instruments and qualified test facilities.
5. **Integration:** only after an approved electrical decision, parent/layout owners update actual schematic/PCB/BOM/CPL, retain protected copper/vias/earth clearance and LED terminal mappings, regenerate/check production data, and rerun these regressions with the real branch behavior. Add nonlinear/reverse/transient evidence; a one-way approximation must not validate a replacement that is actually bidirectional.

No claim of 5/20 kA assembled performance, 72 A terminal capacity, equal transient sharing, direct-strike protection, weather lifetime, or cable impulse withstand follows from this work. A source-side or local protection redesign must retain the agreed earthing/bonding review and RF/site acceptance; there is no assumed unbonded-earth solution.

## 7. Evidence Register

Sources were retrieved during this P2 session on 2026-09-06 using **webfetch only**. APEM and TI HTML were readable directly. Where direct PDF fetching produced raw binary or a 403, text was obtained through `https://r.jina.ai/https://...` targeting the manufacturer document (or manufacturer-authored LCSC-hosted GDT document). That is an extraction aid, not a second manufacturer guarantee or proof the served revision is the latest. Recheck originals, graphs, test conditions and ordering data for approval; no original PDF archive or vendor acceptance has been created here.

| ID | Primary document / provenance | Relevant evidence |
| :--- | :--- | :--- |
| S1 | [APEM Q10F5SXXSG02E live product page](https://www.apem.com/led-indicators/professional-grade-panel-mount-led-indicators/q10/q10f5sxxsg02e) | No-resistor option, 1.8-3.3 V family listing, 20 mA max, 5 V reverse, -40 to +85 C, 20-25 cNm = 0.20-0.25 Nm. Exact SG I/V/pulse bounds absent from retrieved page. |
| S2 | [onsemi 1N4001/D](https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf), June 2024 rev. 18; [text extraction](https://r.jina.ai/https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf) | Pages 2/5/6: blocking/leakage/temperature, ordering suffixes, 0.86 mm lead maximum. |
| S3 | [Vishay 28766, MBx/SMA](https://www.vishay.com/docs/28766/mbxsma.pdf), 11-Jul-2018; [text extraction](https://r.jina.ai/https://www.vishay.com/docs/28766/mbxsma.pdf) | Pages 1-4/8-10: rating modes, film limits, TCR/tolerance, derating and separate pulse constraints. Pulse graphs still require original-graph review for the chosen waveform. |
| S4 | [Mean Well LRS-35](https://www.meanwell.com/Upload/PDF/LRS-35/LRS-35-SPEC.PDF), [LRS-75](https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF), file revision 2025-04-07; [35 text](https://r.jina.ai/https://www.meanwell.com/Upload/PDF/LRS-35/LRS-35-SPEC.PDF), [75 text](https://r.jina.ai/https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF) | 36 V / 1 A / 36 W and 36 V / 2.1 A / 75.6 W; adjustment/tolerance/ripple/tempco conditions; 110-150% output-power hiccup; higher OVP threshold. |
| S5 | [Littelfuse 217 datasheet](https://www.littelfuse.com/assetdocs/littelfuse-fuse-217-datasheet?assetguid=af55be94-c42e-41b1-ad43-e070e09443fe), revised 07/17/25; [text extraction](https://r.jina.ai/https://www.littelfuse.com/assetdocs/littelfuse-fuse-217-datasheet?assetguid=af55be94-c42e-41b1-ad43-e070e09443fe) | Pages 1-2: opening-time test conditions, 2 A row DC interruption and nominal I2t. |
| S6 | [Vishay BZX85, 85607](https://www.vishay.com/docs/85607/bzx85.pdf), rev. 2.9, 17-Sep-2025; [text extraction](https://r.jina.ai/https://www.vishay.com/docs/85607/bzx85.pdf) | Pages 1-3: exact zener test currents, leakage test voltages, coefficients, pulse conditions, conditional 1.3 W thermal rating, DO-41 dimensions and -TR ordering. |
| S7 | [Nexperia BZT52H series](https://assets.nexperia.com/documents/data-sheet/BZT52H_SER.pdf), rev. 7, 1-Jan-2023; [text extraction](https://r.jina.ai/https://assets.nexperia.com/documents/data-sheet/BZT52H_SER.pdf) | Pages 4-6: 5 mA VZ test, current-dependent differential R, 1 V leakage test, pulse and copper-dependent power ratings. |
| S8 | [TI TL431/TL432 SLVS543S](https://www.ti.com/document-viewer/TL431/datasheet), May 2024, sections 5, 6.4, 6.13, 9.2.2.2.3 | [BQ electrical limits](https://www.ti.com/document-viewer/TL431/datasheet/GUID-XXXXXXXX-SF0T-XXXX-XXXX-000000299837), [operating conditions](https://www.ti.com/document-viewer/TL431/datasheet/GUID-XXXXXXXX-SF0T-XXXX-XXXX-000000290477), [stability](https://www.ti.com/document-viewer/TL431/datasheet/GUID-AB8AA1BF-5A8E-4134-8DDE-4B67E83A4679), [pin mapping](https://www.ti.com/document-viewer/TL431/datasheet/GUID-55DC935C-B584-4F42-9176-D1944A98396D). |
| S9 | [TI TL431LI/TL432LI SLVSDQ6A](https://www.ti.com/lit/ds/symlink/tl431li.pdf), Nov 2018; [text extraction](https://r.jina.ai/https://www.ti.com/lit/ds/symlink/tl431li.pdf) | Pages 4-5: 15 mA recommended vs 18 mA absolute cathode current, not the standard TL431 rating. |
| S10 | Manufacturer-authored [Ruilon SMD5050 SP-GDT-006 A3/2024-08-19](https://www.lcsc.com/datasheet/C39692533.pdf), [2RD-8 SP-GDT-017 A3/2023-11-02](https://www.lcsc.com/datasheet/C2836978.pdf), [Bencent B5G470L A2/2018-01-03](https://www.lcsc.com/datasheet/C5337217.pdf), distributed by LCSC | Newly retrieved text via [SMD5050 extraction](https://r.jina.ai/https://www.lcsc.com/datasheet/C39692533.pdf), [2RD-8 extraction](https://r.jina.ai/https://www.lcsc.com/datasheet/C2836978.pdf), [B5G extraction](https://r.jina.ai/https://www.lcsc.com/datasheet/C5337217.pdf): 950/1100 V impulse limits and B5G's 99% figure; typical 15/10/15 V arcs at stated 1 A conditions. No system-specific holdover guarantee. |
| S11 | [Bourns 2027](https://www.bourns.com/docs/product-datasheets/2027.pdf), rev. E 01/26; [text extraction](https://r.jina.ai/https://www.bourns.com/docs/product-datasheets/2027.pdf) | Network-qualified DC holdover, typical-distribution impulse sparkover and actual 8 mm body/lead variants. |
| S12 | [Bourns GMOV](https://www.bourns.com/docs/product-datasheets/GMOV.pdf), rev. 01/25; [text extraction](https://r.jina.ai/https://www.bourns.com/docs/product-datasheets/GMOV.pdf) | Series GDT/MOV hybrid for AC/DC, explicit 14D500K data, large physical envelope and still-high transient front voltage. |
