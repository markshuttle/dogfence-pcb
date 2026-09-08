# Conditional Design Bounds

Hardware **1.2.0-dev**, analysis/evidence 2026-09-07, updated for the authorized
**16-part HP12 / BYG23T SMT conversion**. This bounded update covers
`scripts/analyze_limits.py`, `scripts/design_bounds.py`, their two focused test
files, this note and `ELECTRICAL.md`. The nodal solver, topology, cable, source,
PSU, OneGel and site assumptions are retained. Layout/BOM/sourcing, assembly,
ordering and production-gate integration belong to the parent/other owners.
These are calculations, not hardware qualification or closure of C4/C5/W3;
they add no physical-test prerequisite to prototype exports.

## Selected Circuit

```text
WIRE_A -> R1 HP122WF2201T4E -> D1 BYG23T-M3/TR -> LED_A_POS -> external LED -> WIRE_B
WIRE_C -> R2 HP122WF2201T4E -> D2 BYG23T-M3/TR -> LED_C_POS -> external LED -> WIRE_B
D3 BYG23T-M3/TR: cathode LED_A_POS, anode WIRE_B
D4 BYG23T-M3/TR: cathode LED_C_POS, anode WIRE_B
```

D3/D4 are **negative clamps after the series diodes**, not input shunts or
positive-voltage regulators. Negative connector voltage forward-biases the
corresponding clamp. The forward-only core-to-B model remains applicable to
healthy normal TEST; there is no new forward B-to-A/C path. Actual series-diode
reverse leakage, junction capacitance, recovery and harness ringing are not
solved. The electrical regression is not a source-connectivity guard or proof
that physical dark branches have zero leakage.

The user accepts installation lead-reversal LED damage and direct-strike
rebuilding. **Energized cattle fencing is prohibited near the ENTIRE boundary,
including the 4 km cable, every station and the hub**, not just the shed. This
supersedes the earlier 0.5 m / 300 m exposure assumption; no numerical safe
separation is established here. RF, ordinary switching, nearby lightning,
powered recovery and continuous thermal behavior remain unqualified. Normal
TEST must still be continuous-safe; no timer or active current-stage prerequisite
is added. README/REMEDIATION synchronization belongs to the parent.

## Evidence And Inputs

- **User-confirmed reels:** `CM03/05.100`, labelled
  `3 CORE (3 x 35/0.30) TINNED BLACK 100 MTR`. Identity is settled, not measured
  conductor resistance. The user also confirmed **one LRS-75-36 for TEST and
  the second as a spare**, not interconnected supplies.
- **Resistance source:** IEC 60228:2004, edition 3, section 6.2 and Table 3,
  printed page 11, gives **8.21 ohm/km maximum at 20 C** for Class 5,
  metal-coated 2.5 mm^2 copper [1]. The plain-copper column is 7.98, not the
  tinned value. Section 2.1 explicitly includes tin in "metal-coated".
  Nexans reproduces the same values in its February 2021 table, page 3 [2].
- AMC's exact **2026 Update V.3** specifies Class 5 tinned conductors,
  **BS EN 60228:2005**, CM03/05 = 3 x 2.5 mm^2, and -30..70 C [3]. This
  supports using the standard maximum **conditionally**, without demanding an
  absent AMC numerical resistance column. BSI identifies the British edition
  as identical to EN 60228:2005 [4]; no claim is made that it is the latest edition.
- **Separate construction discrepancy:** Table 3 limits wires to **0.26 mm**;
  AMC's representative construction/reel label says **0.30 mm**. AMC permits
  representative strand configurations to differ. Do not call the label proof
  of complete Class 5 compliance or of measured resistance. Retain the 8.21
  conditional design ceiling while the construction declaration is reconciled.
- **Declared model envelope:** 41 stations at 100 m spacing; same-end A/C
  positive and B return; six independent ends and one-way branches. Source
  nominal 36 V; **35 V floor / 40.39597 V upper are current analysis inputs,
  not an enforced operating window or a guaranteed combined MCOV**. The floor
  must include hub/interface/contact losses at the feeds. The legacy **35..37 V
  proposal was never implemented**; selecting `--source-max-v 37` only changes
  a calculation. LRS adjustment up to 39.6 V and 41.4..48.6 V OVP do not enforce
  37 V [5]. The deliberately stacked adjustment/tolerance screen remains:

  `39.6 * 1.01 * (1 + 0.0003 * (50 - 25)) + 0.1 = 40.39597 V`.

  The 1% includes line/load regulation, not three additive tolerances. The
  0.03%/C figure applies over 0..50 C, and 0.1 V is a selected ripple peak,
  conservatively treated as continuous here. Accessible setting, tolerance
  interaction, startup/overshoot, malfunction and actual maximum still need
  evidence. A passive design qualified over the real normal source range is
  possible; the model does not demand an active 37 V cutoff to pass W3.
- **Cable/contact corner:** 70 C with the existing copper approximation
  `alpha = 0.00393/K`. Each core in **each 100 m span** is allowed 0.025 ohm of
  additional contacts/splices at service temperature: 1.00 ohm per 4 km core.
  This is a declared budget, not a WAGO specification or a measured result.
  It must bound the individual spans, not merely the whole-core sum. The script
  accepts separate A/B/C budgets and does not apply copper TCR to contacts.
- **R1/R2:** Uni-Royal **HP122WF2201T4E**, HP12 / 2512 SMT, 2200 ohm,
  +/-1%, **+/-100 ppm/C referenced to 25 C**, **2 W P70** [9]. Use the PDF's
  100 ppm/C, not the website's tighter 75 ppm/C claim. The unchanged selected
  -30..125 C resistance-temperature screen gives **2156.22..2244.22 ohm**:
  `Rmin = 2200 * 0.99 * (1 - 100e-6 * (125 - 25))`. The PDF's TCR method
  specifies a +25 C (or specified room-temperature) reference and -55/+125 C
  test temperatures. The helper uses a conditional linear envelope within
  those endpoints; **it does not extend TCR to the separate 155 C operating
  endpoint**. Temperature is an input, not a self-heating result. Aging,
  assembly/solder drift and unbudgeted tap/harness losses are excluded.
- **Identity/sourcing:** the supplied **C2791283 is a rejected 4.7k/5% identity**,
  not the selected 2.2k/1% resistor. This model assigns no replacement C-code;
  corrected sourcing is controlled by the parent and reviewed BOM. No allocation
  or land-pattern approval follows from the selected electrical model.
- **D1-D4:** Vishay **BYG23T-M3/TR**, 1300 V repetitive reverse, SMA [8].
  Preserve **36 V / 2.1 V LED + 0.7 V diode** as a named zero-leak historical
  comparison, not measured BYG23T Vf at roughly 15 mA. Its **1.9 V maximum at
  1 A / 25 C** is a 300 us, 1%-duty pulse test, not a minimum or typical value
  at indicator current. The **5.2 V = 3.3 LED + 1.9 diode** high-drop screen
  replaces 4.4 V for headroom/brightness studies. Neither the APEM family 3.3 V
  figure nor the BYG23T test point supplies a full-temperature low-current I/V
  bound. Zero junction drops still screen maximum branch current and heat.
- **Clamp leakage:** the only cited maxima are **5 uA at 25 C / 50 uA at
  125 C**, both at **1300 V reverse**, pulse width <=40 ms [8]. There is no
  guaranteed 5 uA limit at LED voltage across all temperatures. A deliberately
  conservative **50 uA per branch** screen assumes monotone leakage versus
  reverse voltage and temperature for normal positive LED voltage within
  rating and device temperature <=125 C. It is conditional, not a new vendor
  specification. It does not extend to the 150 C junction maximum, avalanche,
  transients or damaged parts.

Sources [1]-[8] preserve earlier evidence; [6]/[7] concern retired resistors.
For this SMT conversion, the supplied research review visually confirmed [9],
pages 1, 2, 4, 5, 6 and 8. This bounded model update reread its TCR reference/test
temperatures and rating text: direct PDF webfetch returned binary, then text
was obtained through `https://r.jina.ai/` prefixed to the same manufacturer URL.
That extraction is not a new visual land-pattern review, archived original or
vendor reply. No broad protection research or supplier acceptance is claimed.

1. [IEC 60228:2004 public standard preview, including Table 3](https://cdn.standards.iteh.ai/samples/12024/921fee9a88c24612b68340a7330c2262/IEC-60228-2004.pdf), with [IEC edition metadata](https://webstore.iec.ch/en/publication/1065).
2. [Nexans IEC 60228 classification, February 2021](https://www.nexans.be/en/dam/jcr:efe5d9a2-f346-4047-87b4-99d1e319d768/IEC60228_ENG.pdf).
3. [AMC Tinned Copper 3 Core Cables, 2026 Update V.3](https://cdn.prod.website-files.com/62deaee72baf3ef3b83165ff/69fc985a23120ee62491a529_14%20-%20AMC%20Datasheet%20%20-%20Oceanflex%20Tinned%20Copper%203%20Core%20Cable%20(2026%20Update)%20V.3.pdf).
4. [BSI BS EN 60228:2005 metadata](https://knowledge.bsigroup.com/products/conductors-of-insulated-cables).
5. [Mean Well LRS-75 specification, 2025-04-07](https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF).
6. [Vishay 28766, MBE/SMA 0414, 11-Jul-2018](https://www.vishay.com/docs/28766/mbxsma.pdf), pp. 2-4/8/11: **historical** MBE rating modes and TCR, not the selected resistor.
7. [Vishay PR01/PR02/PR03, 28729, 08-Jul-2025](https://www.vishay.com/docs/28729/pr010203.pdf): **historical, retired PR02 only**. Cu/FeCu ratings, TCR, mounting/hot-spot examples and PR02-specific 220 C limit do not apply to HP12.
8. [Vishay BYG23T-M3, 89429, 25-Feb-2020](https://www.vishay.com/docs/89429/byg23t.pdf): pp. 1-2 ratings, exact `/TR` ordering, leakage/Vf test conditions and typical forward recovery. Original pulse/thermal curves are not a system qualification.
9. [Uni-Royal HP Series, SMD-SP-003, V.7, 08-Jan-2026](https://www.uni-royal.cn/en/images/userfile/file/1784806233a2e6d381ea80b5d9.pdf): p. 2 ordering; p. 4 HP12 2512 / 2 W and family voltage/operating range; p. 5 ambient derating and working/overload-voltage formula; p. 6 100 ppm/C for 2.2k, 25 C reference, -55/125 C TCR tests and five-second overload. No HP12 220 C hot-spot or 75 K/W mounted thermal parameter is established by these data; p. 8 soldering guidance is not continuous-duty qualification.

## Normal Current

At 20 C the conditional conductor maximum is **32.84 ohm/core**, versus the
old nominal **27.60 ohm/core**. At 70 C it is **39.29306 ohm/core**, or
**40.29306 ohm/core** including the declared contact budgets.

The solver's existing `led_currents_a`, `led_min_ma`, `A40_ma` and related
fields are **branch currents before clamp diversion**, equivalent to LED
current at zero leakage. They are retained for the historical comparisons.
The new `*_after_clamp_leakage_ma` fields subtract at most 0.05 mA locally:

```text
I_branch = max(0, (V_core - V_B - V_LED - V_D) / R)
I_LED_lower = max(0, I_branch - 50e-6)
I_branch = I_LED + I_clamp
P_R = I_branch^2 * R
P_D = I_branch * V_D
P_LED + P_clamp = I_branch * V_LED
```

This is a supported-parameter subtraction screen, not a constant leakage sink
on an unpowered/floating branch or a new nonlinear solver. At fixed conducting
LED Vf, clamp leakage **does not add to PSU/cable/R/series-diode current**. If
leakage consumes the branch current, the fixed-Vf partition needs actual I/V
data; `branch_budget()` rejects an overdrawn partition. The named normal
corners below retain conducting LEDs after diversion; clipped zero bounds in
other input studies are not physical OFF-current predictions.

| Case | Feed V | A40 branch mA | A40 LED lower mA after diversion | Source A |
| :--- | ---: | ---: | ---: | ---: |
| Historical 6.9 ohm/km, 20 C, 2.8 V Vf / 2200 ohm | 36 | 8.044804 | 7.994804 | 0.847705 |
| Standard maximum, 20 C, no contacts, same nominal loads | 36 | 7.300320 | 7.250320 | 0.804701 |
| Declared 70 C cable/contact corner, same nominal loads | 36 | 6.410705 | 6.360705 | 0.752464 |
| Uniform 5.2 V high Vf / HP12 Rmax at every branch | 35 | 5.717067 | 5.667067 | 0.666615 |
| Only A40 high Vf; all other Vf zero; Rmax everywhere | 35 | 4.452016 | 4.402016 | 0.781940 |
| Only A40 high Vf / Rmax; all other Vf zero / Rmin | 35 | 4.277619 | 4.227619 | 0.802694 |
| Previous case with the other positive rail C at zero ohms | 35 | 3.793669 | 3.743669 | 0.860225 |
| Zero cable/contact R, zero Vf / HP12 Rmin everywhere | 40.39597 | 18.734624 | 18.684624 | 1.536239 |

The last row is a zero-drop upper stress screen, not a physical LED operating
point. A real clamp need not draw the full 50 uA, especially at zero bias;
maximum possible LED current uses **zero** diversion, not forced subtraction.

Uniform Vf overstates A40 current by **1.265050 mA** even before the additional
**0.174397 mA** reduction from asymmetric resistor tolerance. Lower resistance
in C can increase shared B loading and further reduce A current. Mirrored
C40 cases are also calculated; they agree only for symmetric cable inputs.
The named corners are **not** an exhaustive joint-tolerance minimum.

For a conservative all-station floor without assuming equal source contacts
or uniform loads, two independent comparisons reuse the existing solver:
ground B and load the positive rail with Rmin/zero Vf at the **35 V floor**;
then hold A/C ideal at the **40.39597 V upper screen** and load B with both
Rmin/zero-Vf channels. Actual positive potentials cannot be lower than the first comparison,
and actual B cannot exceed the second, within the stated healthy passive
envelope. Their worst differences occur at the far end. Subtract the declared
maximum Vf and divide by Rmax, clipped at zero, then subtract the conditional
leakage bound. The positive-rail lower value is **24.8554792613 V**, B upper is
**18.7821480669 V**, and this intentionally loose all-station floor becomes
**0.3891468726 mA branch / 0.3391468726 mA LED after diversion**. It is much
lower than the coupled-corner currents, not predicted installed brightness.

The old **1.4945906084 mA** floor belonged to **MBE 50 ppm/K, 35..37 V and
4.4 V high Vf with zero clamp leakage**. It is reproduced by an explicitly
named historical regression, not silently reused for HP12/BYG23T. Even merely
subtracting 50 uA would make that old comparison 1.4445906084 mA; that does not
account for the changed source/R/Vf inputs and is not the current floor.
Neither number is an optical dark threshold. The existing **1 uA** cut-state
classifier tests the ideal one-way model only; reverse leakage through series
D1/D2 can exceed that classifier and is not solved. Verify actual ON/OFF
distinguishability, including leakage-induced glow, sunlit lenses and the
minimum accepted current at **5 m in full daylight**. No brightness or physical
blackout guarantee follows from the cuts passing or the floor being positive.

The independent upper bound is **18.7346235542 mA/branch**,
**1.5362391314 A / 62.0578698666 W** for 82 branches, and
**37.4692471084 mA at the local PCB B tap**. WAGO through-splices
carry distributed perimeter current, not just that tap current. One LRS-75-36
needs at least **82.0871%** of its rated current/power capacity available for this
upper load, before auxiliary/interface losses. Actual input/thermal derating
still applies; its spare contributes no capacity.

## Thermal Screens

HP12 is **2 W from -55 to 70 C ambient**, derating linearly to
**zero at 155 C ambient** [9]:

`P_allow(T_local) = 2 * clamp((155 - T_local)/(155 - 70), 0, 1)`.

**155 C is the zero-power ambient/operating endpoint, not a demonstrated
powered-chip or material-interface temperature.** No separate HP12 hot-spot
ceiling or mounted K/W parameter is established in this model. SMT sends heat
through chip terminations, solder lands and the PCB differently from the retired
axial parts; it does not remove the dissipated watts or prove a cooler result.
PR02 body standoff, lead forming and its thermal examples do not apply to the
selected no-hole SMT resistor. Ambient derating alone is not W3 closure.

The family **300 V maximum working voltage** is also limited by
`min(300, sqrt(P * R_nominal))`: **66.3324958071 V at 2 W / 2200 ohm**.
The **five-second short-time overload test** uses
`min(2.5 * rated_working_voltage, 500)` = **165.8312395178 V** at that rating.
This is a resistance-change test, **not an impulse curve or repetitive surge
rating**, and neither voltage is permission to expose this system to it.

| Source-end condition | Branch mA | One resistor W | Two resistors W | Rating-only local ambient ceiling C |
| :--- | ---: | ---: | ---: | ---: |
| 36 V, nominal R / 2.8 V Vf comparison | 15.090909 | 0.501018 | 1.002036 | 133.707 |
| 36 V, HP12 Rmin / zero Vf | 16.695884 | 0.601052 | 1.202104 | 129.455 |
| Legacy 37 V proposal, now HP12 Rmin / zero Vf | 17.159659 | 0.634907 | 1.269815 | 128.016 |
| Current 40.39597 V screen, HP12 Rmin / zero Vf | 18.734624 | 0.756803 | 1.513607 | 122.836 |

At the current upper screen, **0.7568032911 W/resistor** leaves
**1.2431967089 W below HP12 P70**. The rating-only local ambient ceiling is
**122.8358601301 C**. At 125 C ambient, allowance is only **0.7058823529 W**,
so this screen exceeds it by **0.0509209381 W**. Do not extrapolate below
70 C to permit more than 2 W, or treat the arithmetic ambient ceilings as
simultaneous safe operating points: the resistance model separately assumes
-30..125 C resistor temperature, while powered hot spots exceed ambient.
The lower calculated upper power than the retired PR02 case comes solely from
the changed TCR/reference resistance envelope, not a modeled SMT cooling benefit.

The helper still distinguishes fixed-current ceilings using **Rmax** from
voltage-fed power using **Rmin**. Its thermal-only 70 C source ceiling of
**65.669171 V** is **not** an allowed source voltage: it exceeds the cable's
60 V working rating and the LED-current screen. It neither sizes a substitute
resistor nor supplies a positive-voltage clamp. Under just the selected initial
R/TCR screen, 20 mA with zero drops corresponds to **43.1244 V**, not a hardware
OV limit, startup/aging margin or full-temperature APEM current qualification.

The nominal heat remains **1.0020363636 W in the two resistors**, plus
**0.0211272727 W** in D1/D2 at the illustrative 0.7 V each. At 2.1 V LED voltage,
two 50 uA clamp diversions move at most **0.000210 W** from the external LEDs
to D3/D4, giving **1.0233736364 W** in these PCB parts at the comparison point.
That heat is not removed by SMT mounting or the 2 W resistor rating, and clamp
leakage is not added again to the PSU current or whole-branch input budget.

**Bulk/local interfaces:** **60 C interface** and **110 C film** remain
conservative **proposed development targets**, not user hard future/all-temperature
requirements or measured temperatures. The 60 C example leaves 10 K to the
complete cable's actual 70 C limit; the old 15 K MBE film margin no longer applies.
Film, body, adjacent gel and cable-entry hot spots are different temperatures.
Measure or otherwise establish each with uncertainty; a cool bulk reading
does not establish safe cable or gel contact temperature near a hot resistor.
OneGel's conflicting service fields and missing thermal data remain as recorded
in ENVIRONMENT_EVIDENCE.md; adhesive, connector and LED limits also apply.

For the **two selected branches only**, assigning all their electrical input to
heat bounds it by **1.5136065821 W** at 40.39597 V. This already includes any
partition between resistor, series diode, LED and clamp; adding a separate
clamp-input load would double-count energy. At an illustrative 30 C outside / 60 C
bulk target, allowable **effective** bulk-to-outside resistance is at most
**19.8202097920 K/W**. At 60 C local ambient / 110 C film, the paired-load effective
film-to-local allowance is **66.0673659733 K/W per resistor**. These are required
heat-rejection capabilities, **not OneGel properties or self-heating claims**.
Add through-contact/auxiliary heat, mutual heating and solar exposure before
using the budget for a real enclosure. 30 C observed outdoor ambient is not a
guaranteed design maximum. No normal TEST timer substitutes for this envelope.

Actual HP12 chip/pad/PCB and adjacent-material temperatures are not calculated
from an assumed package K/W. Instrumented steady-state evidence with both
branches, solar exposure and output-short conditions remains a separate physical
qualification activity, not a new prerequisite imposed on prototype exports.

**Historical only:** the retired PR02 calculation used +/-250 ppm/K and a 20 C
reference, giving **2120.8275..2280.3275 ohm** and **0.7694328710 W** at the upper
source screen. Its **220 C hot-spot limit, typical 75 K/W mounted example and
>=1 mm body standoff** [7] belong to that axial part, not HP12. The old example's
**57.7074653257 K rise** is not retained as an SMT or OneGel prediction.
The named historical regression also retains the former MBE **2166.5655 ohm**
minimum, **0.631876 W at 37 V** and **0.753190 W at 40.39597 V**, rather than
calling them HP12 limits. Neither retired resistor's analysis was physical qualification;
their 20 C arithmetic is explicit in the historical test, not a compatibility
mode in the selected-part helpers.

## Fault Screen

The existing solver supplies only selected AB/CB prospective CV examples,
with explicitly illustrative **0.25 ohm source series R** and **0.1 ohm arc
slope**. At 40.39597 V / declared cable / zero-Vf HP12 Rmin loads, a near-source
100 ohm fault dissipates **16.0526650917 W** at **0.4006577728 A in the fault**
with just **1.3207708739 A total**, below even the healthy upper envelope.
A hub overcurrent threshold is not complete coverage.
The near-source ideal short's **161.58388 A** is invalid CV demand, not LRS current.

The same far-end 10 V arc case with the selected load gives
**0.1308380267 A / 1.3100921262 W** in the path and **0.9769095285 A total**.
Neither it nor the higher old nominal arc value below is a maximum over
cable/load/fault conditions or evidence of
improved physical recovery. D3/D4 do not alter the upstream GDT paths.

K.12's known 135 V / 1300 ohm DC-feed comparison is retained from
SOURCE_PROTECTION_RESEARCH.md, sections 2/9 [N1,N2]. Ignoring the test diode
drop gives **103.846 / 96.154 / 92.308 mA** at **0 / 10 / 15 V**. The old
nominal far 10 V arc remains **0.259543 A / 2.602168 W**. Ratios in the new CLI
use the actual modeled terminal voltage, including arc slope, not just its
10 V knee. A simple 40.39597 V source would need at least **388.9982296296 ohm**
for this sufficient pointwise DC-feed dominance, not an acceptable rail-resistor design.
This does not prove dynamic extinction or non-extinction; K.12 also has surge/
RC conditions and does not qualify this powered fence by voltage comparison.
The **0.256 W** bound for a <=0.1 ohm failed-short path requires an **actually
enforced 1.6 A** ceiling and does not cover resistive damage or external energy.
That is an unimplemented historical source proposal, not a newly required
active stage or a safety limit imposed by this update.

**C4 mechanism, not transient approval:** D3/D4 provide an ordinary forward
conduction path for negative LED-connector voltage. BYG23T's datasheet forward
recovery is **typical 9 V peak / 620 ns at 1.5 A and 12 A/us, 25 C** [8],
**not proof of <=5 V at the LED**. The 75 ns reverse-recovery maximum is a
different test and does not fix this gap. No positive regulation or forward
pulse-current limit is introduced, and neither the 1300 V diode rating nor
the 2 W resistor label qualifies ordinary switching/RF/nearby-lightning stress.
The installation-lead reversal exclusion does not waive normal-operation safety.

## Reproduction

```bash
TMPDIR=/tmp/opencode python3 -B scripts/design_bounds.py --json
TMPDIR=/tmp/opencode python3 -B scripts/analyze_limits.py --json
TMPDIR=/tmp/opencode python3 -B -W error -m unittest discover -s tests -p test_design_bounds.py -v
TMPDIR=/tmp/opencode python3 -B -W error -m unittest discover -s tests -p test_electrical.py -v
```

CLI output is deterministic and offline, with explicit units and no file writes.
Focused tests reuse `analyze_limits.cut_sweep` for all **280 cuts** at the updated
asymmetric corner with 50 uA ON-current diversion margin. Raw OFF currents must
still be zero; leakage subtraction cannot conceal a forward backfeed. The
original **280 nominal cuts and 615 prospective inter-core fault cases** are
retained, along with repair/retest, floating-island and legacy-topology controls.
No second network solver, full transient solver or shared-source guard is added.

On **Python 3.14.4**, the SMT-focused runs passed **23 electrical tests and
13 design-bound tests**. Both normal `--json` CLIs exited 0; human/JSON/error
paths were also exercised by the isolated suites. These results concern only
the bounded analysis, not the concurrent PCB/production integration.

The suites cover selected HP12 rating/TCR/25 C reference and test endpoints,
working-voltage/five-second-overload arithmetic, historical named values, BYG23T
headroom, clamp diversion/blackout margin, unchanged resistor/PSU power and
nonzero clamp body heat, finite/invalid inputs, thermal arithmetic and CLI JSON.
These checks verify declared calculations, not actual LED polarity survival,
source limits, optical darkness, recovery or physical temperatures. No
`make check`, manufacturing/staging operation, approval refresh, commit, order
or physical test is part of this bounded work. Parent owns integrated gates
and README/REMEDIATION updates after source edits settle.
