# LED Protection Research

**2026-09-07; hardware 1.2.0-dev; starting checkpoint 97e202d. Research, not circuit selection or release approval.**

Only this evidence record is owned by this investigation. No schematic, PCB,
library, BOM, approval hash, main guide, `build/`, or `tmp/manufacturing/` was
changed by this investigation. C4/C5/W3 and the existing release gates remain
open. Latest user facts: **two LRS-75-36 supplies ORDERED; one allocated to TEST,
the other a disconnected spare**. The **CM03/05 reel identity is confirmed**;
the separate cable investigation owns its Class 5 resistance envelope. No
series, parallel, or opposite-end source connection is assumed. Older
procurement statements in the shared guides were deliberately not edited.

**Current handoff: see section 11's negative findings before selecting parts.**
The original pulse curve rejects L1's proposed PWC resistor string. L2 removes
the separate regulator-current overshoot problem, but its TVS2700 operates
outside the recommended input range during normal TEST and can exceed its DC
absolute limit after a post-resistor fault. **Neither circuit is selected for
population.** The records preserve calculations and failures, not a completed
design awaiting field qualification alone.

**Later implementation after checkpoint ad282e3:** installation-polarity LED
damage and direct-strike rebuilding are accepted, but not all routine/nearby
transient damage. Energized cattle fencing is prohibited near the entire
boundary, stations and hub; the old close-parallel exposure is withdrawn.
ELECTRICAL/ASSEMBLY now control the **implemented 16-part PR02/BYG23T hybrid**:
two 2 W axial resistors, two SMA series diodes and two SMA negative shunts,
not L1/L2's active/current-regulating circuits. Their research below remains
history, not a prerequisite or the current BOM. The new shunts are not a
guaranteed forward-pulse limiter or an instantaneous <=5 V clamp.

## 1. Initial L1 Investigation

The initial active development circuit investigated was:
**pulse impedance and a protected input, a floating LT3092 current source, then
ballasted precision shunts and a separate negative clamp at the LED connector**.
The current setting is about **16.18 mA**, not 20 mA nominal. The output shunt
can accommodate **20 mA total without exceeding either reference's 15 mA
operating ceiling**. Its calculated steady positive limit is **4.3584 V**.

This removes LED minimum forward voltage from the current-safety calculation.
It also establishes a useful output-voltage passband without first demanding
the entire SG LED I/V distribution. It does **not** establish an instantaneous
20 mA ceiling merely by quoting the current source's DC accuracy.

**No complete, datasheet-only, pulse-safe selection is supported yet.** The
specific remaining design gaps are current-source recovery/overshoot, shunt
turn-on overshoot, interpretation of below-knee reference loading, the selected
pulse resistor's applicable curves, and the actual excitation of the 200 mm
LED harness. A concrete test envelope and quantitative closure conditions are
below. Unknown LED minimum Vf is not the reason for this disposition.

## 2. Candidate Netlist

Candidate **L1**, repeated independently for X=A and X=C. `B` means `WIRE_B`,
not earth or a new ground plane. Intermediate nodes are private to that rung.
References below are research names, not assignments in the existing schematic.

```text
WIRE_X -- RPx1 -- RPx2 -- RPx3 -- RPx4 -- DPx(A->K) -- Px
Px -- UCLx.IN
UCLx.OUT -- RIx -- LED_X_POS -- J_LED_X.1 -- external LED anode
UCLx.SET -- RSx -- LED_X_POS
external LED cathode -- J_LED_X.2 -- WIRE_B

Px -- TVPx.IN;             TVPx.GND -- B
Px -- CPx -- B

LED_X_POS -- RBx1 -- Kx1 -- UZx1.cathode
LED_X_POS -- RBx2 -- Kx2 -- UZx2.cathode
UZx1.anode = UZx1.pin3 = B
UZx2.anode = UZx2.pin3 = B

LED_X_POS -- TVNx.IN;      TVNx.GND -- B
```

| Per-Rung Reference | Quantity | Exact Candidate MPN | Connection / Purpose |
| :--- | ---: | :--- | :--- |
| RPx1..4 | 4 | TT Electronics `PWC2512-390RFI` | Four 390 ohm, 1%, 100 ppm/K pulse-withstanding resistors in series: 1560 ohm nominal. Pulse-envelope approval remains outstanding. |
| DPx | 1 | Diotec `BYG23T` | Anode toward resistor string, cathode to Px; 1300 V repetitive blocking. Not a claim that the original 1N4007G has sufficient repetitive margin. |
| TVPx | 1 | TI `TVS1800DRVR` | IN pins 4/5/6 to Px; GND pins 1/2/3 and exposed pad to B. Primary low-voltage input protection, not an LED-voltage clamp. |
| CPx | 1 | KEMET `C1210C106K5RACTU` | 10 uF, 50 V, X7R, 10%, nonpolar, Px-to-B. Effective capacitance at bias/temperature is a design gap; nominal 10 uF is not its minimum. |
| UCLx | 1 | ADI `LT3092IST#PBF` | SOT-223: IN pin 3 to Px, SET pin 1 to RSx, OUT pin 2 and tab to RIx. Use I grade for the specified industrial junction range. |
| RSx | 1 | Vishay `TNPW080551K1BEEA` | 51.1 kohm, 0.1%, 25 ppm/K, SET-to-LED_X_POS. |
| RIx | 1 | Vishay `TNPW080531R6BEEA` | 31.6 ohm, 0.1%, 25 ppm/K, OUT-to-LED_X_POS. |
| UZx1, UZx2 | 2 | TI `LM4050BEM3-4.1/NOPB` | Each: cathode pin 1 to its own Kx node, anode pin 2 to B, pin 3 tied to B as recommended for high EMI. B-grade extended-temperature 4.096 V reference. |
| RBx1, RBx2 | 2 | Vishay `TNPW080522R0BEEA` | Separate 22.0 ohm, 0.1%, 25 ppm/K ballast resistors. Do not parallel the references without them. |
| TVNx | 1 | TI `TVS0500DRVR` | IN pins 4/5/6 to LED_X_POS; GND pins 1/2/3 and pad to B. Used for its specified forward/negative clamp, **not** its approximately 9 V positive surge clamp. |

This version has 15 components per rung, replacing the existing two. If all ten
other electrical parts were retained, the board would have 40 electrical parts,
not the current 14. No allocation, JLCPCB code, footprint fit, or placement is
approved. The resistor and capacitor codes follow their manufacturers' ordering
tables; supplier allocation and exact product specification sheets still need
confirmation. The `LM4050BEM3` orderable is listed in TI's addendum; do not invent
an A-grade extended-temperature 4.1 V order code from a family description.

All shunts and the input capacitor are **after DPx**. Moving TVPx ahead of DPx
creates a B-to-A/C forward-diode path through RP and can defeat clean-cut
isolation. There is no A-to-C auxiliary supply or shared reference node. Keep
the existing connector polarity and two distinct local LED terminal mappings.

## 3. Current Source Bounds

ADI LT3092 revision D, 08/20, pp. 4, 9-16 [R1]:

- ISET = 9.8..10.2 uA over the specified full-temperature, 2..40 V,
  1..200 mA conditions; initial 25 C accuracy is 1%.
- OUT-to-SET offset is +/-4 mV over temperature at the listed 2 V/1 mA
  condition. Load-related offset change is specified up to 2 mV; line-related
  offset change is 0.010 mV/V at the specified condition. Not every row carries
  the full-temperature marker.
- Dropout maxima are 1.45 V at 10 mA and 1.65 V at 200 mA. The external RI
  drop is additional. At 6.2 mA, nominal RI contributes 0.196 V, not 0.511 V.
- All quiescent/drive current goes to OUT; there is no separate B-referenced
  milliamp bias load. SET contributes an additional approximately 10 uA.
- IN withstands +/-40 V relative to SET/OUT. Reverse current is less than
  1 mA in the protection description; this is not sufficiently small to replace
  the one-way input rectifier for cut isolation.
- No input/output capacitors are generally required, but ADI explicitly
  requires in-situ stability checking with complex loads and long wires.

The correct two-terminal programming equation includes SET current:

```text
Iterminal = (ISET * RS + VOS) / RI + ISET
Inominal = 10 uA * 51100 / 31.6 + 10 uA = 16.180886 mA
```

A transparent **engineering screen**, allowing each programming resistor a
total +/-1% envelope and |VOS,total| <=6.4 mV, gives:

```text
Ilow  = (9.8 uA * 51100 * 0.99 - 6.4 mV) / (31.6 * 1.01) + 9.8 uA
      = 15.342931 mA
Ihigh = (10.2 uA * 51100 * 1.01 + 6.4 mV) / (31.6 * 0.99) + 10.2 uA
      = 17.042299 mA
```

The 6.4 mV screen rounds 4 mV offset + 2 mV load change + 0.38 mV line change
upward. **It is not a newly guaranteed all-corner 17.043 mA rating.** Confirm
the combined line/load/temperature envelope and dropout transition, rather
than silently extending the 25 C rows. The +/-1% resistor allowance includes
design margin for TCR/process/drift, not a lifetime qualification. TNPW's
general-operation rating, low dissipation, cleanliness and process limits
remain applicable [R6].

ADI also calls out leakage at the 10 uA SET node: 10 nA already creates a 0.1%
reference error. Keep the SET circuit clean and compact; the suggested guard
potential is OUT, on both PCB sides, not B or EARTH. Potting is not proof of
acceptable surface leakage or a reason to omit this check.

Use **18 mA as the development stage ceiling**, leaving 2 mA to the user's
20 mA limit. Obtain a supported dynamic bound or qualification sufficient for
the declared envelope before calling that ceiling enforced. LT3092's internal
200 mA-class fault current limit is **not** the programmed 16 mA protection.
Its typical line-transient and turn-on plots are not maximum overshoot data.

No LED minimum Vf occurs in these equations. A shorted LED is included in the
intended current limit. A simple pass transistor/0.65 V VBE limiter or a
20 mA-nominal CCR does not offer an equivalent maximum-current bound.

## 4. Precision Shunt Bounds

TI LM4050-N, SNOS455H, March 2025, section 5.7 [R2], for the chosen BEM3 part:

| Parameter | Specified Limit / Condition |
| :--- | :--- |
| Reference voltage | 4.096 V; +/-29 mV at 100 uA over -40..125 C |
| Current-related voltage change | <=1.2 mV from IRMIN to 1 mA; <=10 mV from 1 to 15 mA, over temperature |
| Minimum operating current | <=78 uA over the extended temperature range |
| Maximum operating current | 15 mA; 20 mA is absolute maximum, not a usable shunt rating |
| Stability | Internally compensated; no output capacitor needed; tolerates capacitive loads |

Adding the magnitudes of both current-change limits conservatively:

```text
Vz_lo = 4.096 - 0.029 - 0.0012 - 0.010 = 4.0558 V
Vz_hi = 4.096 + 0.029 + 0.0012 + 0.010 = 4.1362 V
RB_lo = 22 * 0.99 = 21.78 ohm
RB_hi = 22 * 1.01 = 22.22 ohm

Vconnector_hi <= Vz_hi + Itotal * RB_hi / 2
              = 4.33618 V at 18 mA
              = 4.35840 V at 20 mA

Ione_hi <= (Itotal * RB_hi + Vz_hi - Vz_lo) / (RB_lo + RB_hi)
         = 11.927273 mA at 20 mA total < 15 mA
```

These are steady-state bounds with functioning references and the stated
resistor/temperature envelope. They do not assume equal current sharing.
At small total currents only one reference may regulate; that cannot increase
the positive voltage above the high-current bound. Self-heating must keep each
junction in range; the current-change tests are pulsed. Approximately 50 mW in
the more heavily loaded reference would produce about 14 C rise using TI's
287 C/W test-board metric, not a measured potted-board thermal resistance.

**Low-loading argument, with its exact limitation:** a fixed reference must
already be near 4.096 V at 100 uA. For its normal monotone, non-latching shunt
characteristic, a terminal voltage <=4.0 V therefore implies less than 100 uA
per reference. The pair's conservative DC diversion budget is **0.20 mA**,
about 3.3% of 6 mA. This uses a specified operating point, not a typical zener
leakage curve and not the TL431 `REF=0` off-current specification. However,
TI does not explicitly tabulate maximum current throughout the below-knee
0..4.0 V region. Treat monotonic/no-latch operation there as a stated circuit
assumption; obtain vendor confirmation of **I <=100 uA for 0..4.0 V over
-40..125 C**, or qualify/review that assumption before claiming it guaranteed.
Do not relabel IRMIN as a literal datasheet leakage specification.

Thus the design offers a **0..4.0 V normal LED-voltage passband**. Exact SG Vf
is needed only to establish where the purchased LEDs lie within that passband
and their brightness/headroom, not to bound forward current or the positive
reversed-lead voltage. The existing 3.3 V family screen has substantial voltage
separation from the reference knee.

For negative connector voltage, TVS0500 section 7.6 [R3] specifies **VF <=0.65 V
at 1 mA over operating free-air temperature**, unlike the retrieved ordinary
diodes' 25 C-only forward maxima. BYG23T's <=50 uA reverse leakage at 125 C and
rated voltage is below that current in steady supply reversal. Use the usual
monotone forward-diode characteristic for lower current. TVS0500 leakage at
5 V is <=220 nA at 85 C and <=755 nA at 105 C. These are specified temperature
points, not an invented 125 C maximum. Its 155 pF capacitance is typical.

TVS0500 alone is **not** sufficient: its positive breakdown is 7.5..8.4 V at
1 mA and its positive surge clamp can reach 9.5 V. The two precision references
are what protect a reversed external LED under positive supply.

## 5. Normal Current And Cuts

Use 3.3 V as an explicit LED **brightness/headroom screen**, not as an inferred
full-temperature APEM guarantee. With RP allowed +/-4%, RI allowed +/-1%,
BYG23T screened at 1.9 V, and a conservative 1.65 V current-source dropout:

The RP +/-4% is an allowed design/measurement envelope for these screens, not
a manufacturer guarantee combining every tolerance, aging and pulse-history
extreme. Extend the envelope and recalculate if the accepted process requires it.

```text
RP = 1497.6..1622.4 ohm
RI_max = 31.916 ohm
Vlocal_needed_for_6mA_LED
  >= 3.3 + 1.9 + 1.65 + (0.006 + 0.00020022) * (1622.4 + 31.916)
  ~= 17.1071 V, before upstream capacitor/TVP leakage and wiring allowances.
```

Use **17.2 V local X-to-B** as a preliminary useful-light interface target under
those assumptions, not as a guaranteed field voltage. The 1.65 V dropout use
at lower current assumes monotone dropout behavior; the guaranteed table
points and the diode's 25 C forward-voltage condition must remain visible.
At 35.5..36 V near the source there is enough series headroom for the current
setting; allowing 0..0.20022 mA diversion gives about **15.14..17.04 mA**.

Read-only calculations with the existing persistent model used RP+RI =1591.6
ohm and a combined constant semiconductor drop of 6.85 V. They deliberately
omit current clipping, new shunt loading, input-capacitor dynamics and leakage:

| Uniform 41-Station Screen | Total Source Current | Far-End Branch Current | Unclipped Source-End Branch Current |
| :--- | ---: | ---: | ---: |
| 27.6 ohm per 4 km core | 0.930308 A | 8.069182 mA | 18.314903 mA |
| 40 ohm per 4 km core | 0.813526 A | 6.132720 mA | 18.314903 mA |

Subtracting 0.20022 mA for the reference pair and negative-clamp allowance
from the latter gives **5.9325 mA**,
not a proven 6 mA minimum. Current clipping changes cable drops, and independent
LED/resistor corners must be modeled; uniform high Vf is not the worst possible
loading of a single high-Vf far-end LED. The smaller resistance is a credible
headroom recovery, **not** a completed full-network guarantee. A lower verified
low-current rectifier drop, lower cable resistance, or revised resistor/current
settings can close this small uniform-case deficit. Do not lower RP blindly:
more upstream load and inrush can counteract the apparent benefit.

With DPx blocking every new core-to-B path, the ideal one-way clean-cut topology
is preserved: A-only leaves C on after the cut, C-only leaves A on, and B/any
two/all-three cuts leave both off after the cut. No End A/C strap or second B
return is added. Real reverse leakage and stored energy require an OFF-state
and settling check, not the old solver's 1 uA classifier as an optical limit.
The new input capacitors must discharge after a cut; a brief decay is different
from a permanent backfeed. Aggregate hot leakage must not create a misleading
visible indication on a floating island.

## 6. Conducted Pulse Envelope

Proposed **development envelope**, to be accepted by the electrical/GDT owners
and the laboratory, not claimed to describe every lightning or cattle pulse:

- Absolute differential voltage at the rung's WIRE_X/B pads <=1200 V, including
  DC bias and local overshoot; both polarities; powered and unpowered.
- Exercise 1.2/50 us voltage pulses with declared generator impedance, initially
  42 ohm, and a faster front up to 1 kV/us. Independently exercise the fast
  collapse/reversal caused by GDT firing, not only the generator's rising edge.
- For the high-voltage portion, screen energy conservatively as no more than
  1200 V for 100 us: integral(V^2 dt) <=144 V^2 s. Specify the subsequent tail
  separately; an arbitrarily long 40 V tail is not inside that energy budget.
- Initial component-development repetition: five pulses per polarity per
  selected corner, at least 60 s apart. This is neither lifetime nor repetitive
  cattle-fence qualification. Add the actual repetitive envelope separately.
- The circuit-level test excludes direct injection into the LED harness until
  its separate coupling test is defined. Excluding it is not field approval.

For RP_min =1497.6 ohm, conservatively ignoring all diode/clamp drops:

```text
Ipre_peak <= 1200 / 1497.6 = 0.801282 A
E_RP_total <= 1200^2 * 100 us / 1497.6 = 0.096154 J
P_RP_each_peak <= (0.801282)^2 * (390 * 1.04) < 261 W
E_RP_each <= 0.0261 J
V_RP_each <= 0.801282 * (390 * 1.04) < 326 V
```

The individual figures intentionally combine adverse independent corners.
PWC2512 has a 500 V limiting-element voltage, but **that does not approve a
261 W pulse**. TT publishes separate 1.2/50, 10/700, single-pulse and repetitive
curves [R7]. They were not visually read in the initial investigation. **Section
11 now resolves them and rejects this L1 resistor string for the stated 100 us
rectangular screen.** For any other use, confirm the
390 ohm curve, initial hot temperature, repetition and allowed drift against
the numbers above before selecting these parts. The original MBE0414's 1 W
rating is not such evidence. Four parts reduce voltage and heat concentration;
they do not magically multiply an unverified pulse rating.

TVS1800 [R4] specifies 24.7 V maximum for the stated 35 A 8/20 us test with
18 V prebias at 125 C; 23/23.4 V maxima at 24/40 A and 27 C; VBR=19.5..23.8 V
at 1 mA. Its 10/1000 us absolute current rating is 6 A. The candidate's <0.81 A
screen is much smaller, but waveform equivalence and startup at this lower
current are still to be established. Set a **30 V measured input-node ceiling**
including layout overshoot; the LT3092 then has margin to its 40 V limit even
with a slightly negative LED output. No 24.7 V universal clamp is inferred
for every pulse shape or duration from one test entry.

With Px <=30 V and raw negative input >=-1200 V, DP reverse stress is <=1230 V,
below its 1300 V repetitive rating. The original 1000 V 1N4007G is not adequate
for this declared envelope; its 1200 V nonrepetitive entry is not a substitute.
BYG23T's 5 mJ avalanche figure is not used as permission to exceed 1300 V [R5].

Require CP **effective capacitance >=4.7 uF at the actual bias, temperature and
age** if relying on the following first-order filter screen:

```text
dVP/dt <= 0.801282 A / 4.7 uF = 0.1705 V/us
RP_min * CP_min = 7.0387 ms
```

This is a lumped charging bound, not a parasitic feedthrough or current-loop
overshoot guarantee. KEMET [R8] provides nominal tolerance, +/-15% X7R
temperature behavior, insulation and process tests, but not that particular
biased/aged 4.7 uF minimum in the retrieved family table. Obtain the part-specific
bound. The 50 V rating does not establish retained capacitance.

Bulk capacitance stays **before the current source**. No capacitor is put
across the limiter, and no deliberate output reservoir is connected directly
across the external LED. Both arrangements can bypass the programmed current
limit. Even small unavoidable shunt/connector capacitances and the harness
still need transient evaluation. Wiring remains power-off/discharged; hot
reconnection of a charged output is not included in a nominal DC limit.

## 7. Source, Thermal And RF Consequences

The purchased supplies are individually 36 V / 2.1 A /75.6 W, with adjustable
output, hiccup overload and higher OVP thresholds [R9]. Two ordered units are
not a 4.2 A fence source. For one active source, a provisional 18 mA per rung
ceiling gives <=1.476 A and <=59.63 W at 40.4 V, before other loads.

Input-capacitor startup is different: an ideal voltage step into all 82 empty
capacitors through RP_min gives **1.971 A at 36 V**, or **2.212 A /89.37 W at
40.4 V**. The latter exceeds one LRS-75's ratings. The published typical
30 ms PSU rise time is not an enforced slew limit. A controlled source window
and/or supported startup behavior are necessary; another ordered PSU is not
an assumed remedy. No timer is proposed for normal TEST.

Normal source-end heat is still roughly a watt per board. At 18 mA, RP_max
would dissipate 0.526 W per rung (about 0.132 W per resistor). Lower RP moves
some heat into LT3092 rather than removing it. Its tab is OUT, **not B or
EARTH**. At 40.4 V, RP_min and zero LED/rectifier drop, the simple
`I*(40.4-I*RP_min)` screen is 0.2673 W at the low current-setting corner;
its maximum over all currents is 0.2725 W. This upper screen includes RI/SET
network dissipation, so does not undercount LT3092's share. Thermal layout must
support it and keep junctions <=125 C in normal operation. Neither ADI's
four-layer thermal examples nor a resistor's catalog P70 establish gel/solar
temperatures on this board.

TVS1800's DC breakdown-current absolute maximum is only 18 mA. It is not a
continuous-power substitute for a failed-open current source: calculate and
qualify that fault separately. With normal current-source/shunt operation,
the 40.4 V screen places Px below about 18 V, but low-end setting/resistor
corners and leakage need checking. The input-capacitor short and current-source
open/short faults must be included in the eventual fault/thermal analysis.

RF loading is not zero just because a current source is used. CP bypasses its
high AC impedance through the input rectifier. In an ideal symmetric RUN
connection, A/B/C have equal local potentials; real imbalance does not.
The additional input path is approximately
`RP + Z(DP) + Z(CP || TVP)`, in parallel with the downstream branch. If DP
conducts, a crude lumped worst-case conductance for 82 branches is
`82/1497.6 = 54.75 mS`; if DP is off, junction capacitance dominates. This is
not a transmission-line prediction or a sum of 82 directly connected 10 uF
capacitors. TVS0500 and LM4050 also add connector capacitance. The Flat-Clamp
parts can draw transient current below standoff on fast edges; TI cautions
about repetitive edges above approximately 0.7 V/us at high temperature.
Measure the actual carrier, differential/common-mode amplitudes, impedance,
receiver field and unintended LED light with the final station population.

A guaranteed GDT holdover candidate would help powered recovery, **not** prove
LED pulse safety or bound the pre-spark front. Its impulse maximum, test slope,
extinction network and failure behavior must be supplied by the other owner.
If its guaranteed impulse level exceeds this envelope, revise the rectifier,
RP, TVP and spacing before integration. Added branch clamps/energy storage can
change the network used to assess holdover; give their load model to that owner.

## 8. Alternatives Investigated

| Candidate / Topology | Useful Evidence | Disposition |
| :--- | :--- | :--- |
| Diodes `AL5809-15P1-7` | DS36625 rev. 5-2, Dec 2016: 14.25..15.75 mA at 3.5 V over -40..125 C; 2.5..60 V operation; line regulation only typical; 500 us minimum PWM on/off widths. | Smaller alternative to LT3092, but greater dropout and no guaranteed peak-current/line envelope. At 2.2k, the extra 2.5 V costs far-end light. The 20 mA version allows 21 mA even at its accuracy test and is rejected. |
| Diodes `AL5809-15QP1-7` | Retrieved DS38233 rev. 2-2, Aug 2017 is marked advanced information; full-temperature row is 12.8..17.3 mA, not simply +/-5%. | Do not transfer the commercial accuracy claim or approve from the automotive label. Obtain current production data if pursued. |
| Diodes `AL5802-7` | DS35516 rev. 10-2, Jan 2021: discrete VBE-derived current sink, 4.5 V minimum bias, 0.8 V output range, broad transistor data. | No sufficiently tight all-temperature 15..18 mA bound from the nominal 0.65 V reference alone. Bias current and separate supply path complicate far-end operation. |
| Nexperia `NCR420U` / `NCR421U` | Rev. 1, 10-Dec-2018: 9..11 mA at specified conditions; nominal 1.4 V overhead; external-current, temperature and voltage coefficients are largely typical. | Attractive simple sinks, not a guaranteed externally adjusted <=18 mA limit over this envelope. Additional bias and reverse paths need a new topology. |
| Infineon `BCR431U` | Rev. 1.0, 03-Mar-2020: <=200 mV saturation at 32.8 mA, but 6 V minimum supply and up to 2 mA supply current; external settings predominantly typical, LED pin only 15 V absolute. | Low output dropout does not mean a low-headroom, low-loading two-terminal rung. Bias loading alone is large compared with a 6 mA LED. Not preferred. |
| ST `STCS05DR` | DocID13969 rev. 5, Jan 2022: 90..110 mV sense reference, 1..500 mA setting, <=0.16 V dropout at 100 mA, <=750 uA quiescent, 4.5 V supply minimum. | Stronger low-drop sink alternative, but bias loading, low-side return redesign and required capacitor/stability behavior are disadvantages here. No published all-event 20 mA peak bound. |
| TI `TPS92611QDGNRQ1` | SLDS238B, Jan 2020: low-drop high-side driver, 93.5..102.5 mV sense at stated 4.5..18 V conditions, <=250 uA quiescent. | Separate minimum SUPPLY voltage matters in dropout. Section 7.3.5.2 explicitly warns of a large recovery current pulse; do not call DC accuracy a pulse limit. Diagnostics/retry and reverse pin limits add complexity. |
| TI `TLA431AQDBZR` | SNVSCR4D, June 2026: 0.2..100 mA operating range, stable with all output capacitors, Q reference deviation <=20 mV. | Best single-IC adjustable shunt fallback to investigate. Use e.g. 6.04k/10.0k for about 4.00 V; divider, IREF, voltage/current errors must be stacked. Its 0.5 uA off-current is still tested at REF=0, not the intended divider voltage. All-capacitor stability is not a turn-on overshoot bound. |
| TI `TLVH431BQDBZR` | SLVS555N, June 2024: 0.1..70 mA operating range, Q VREF=1.221..1.265 V at 10 mA. | Sufficient shunt current and lower bias, but capacitive stability and below-threshold loading need support; do not assume the 25 C Imin/Ioff rows are full-temperature leakage bounds. |
| TI `ATL431BQDBZR` | SLVSCV5E, Dec 2024: 35 uA minimum operating-current maximum and 100 mA range. | The updated application section recommends cathode slew <0.0125 V/us; poor unqualified fast-clamp choice. `ATL431LI` improves bandwidth but returns to a 15 mA operating /18 mA absolute ceiling. |
| ADI `LT1634AIS8-4.096#PBF` | Rev. F, Oct 2014: full-temperature reference maximum 4.10317 V; add <=3 mV and <=20 mV current changes up to 20 mA: 4.12617 V DC. | Excellent single-reference DC candidate, but footnote 4 **requires 0.1 uF above 1 mA**. This creates an output stored-energy path; its hot reconnection and harness response cannot be ignored. Not the no-reservoir candidate L1. |
| TI `LM285BXZ/NOPB` | SNVS741F, Apr 2013: adjustable 1.24..5.3 V, operating up to 20 mA, -40..85 C, low bias. | Credible lower-cost DC shunt fallback. Larger package, older test-table qualification, below-knee loading and fast response still need analysis; not an unconditional pulse-clamp substitution. |
| BZX85C3V9 / BZT52H-B3V9 alone | Prior ELECTRICAL evidence: voltage at particular test currents; leakage measured well below green Vf. | Neither regulates forward LED current. Keep rejected as a complete C4 solution; a nominal zener number is insufficient. |
| TVS3300 + resistor after it + 4 V output shunt | SLVSDO2C, Feb 2018: 40 V maximum clamp at the stated 27 C 8/20 tests. A >=2.0k post-resistor could then bound current even with LED Vf=0. | Important alternative, **not ruled out** by the old single-5-V-clamp feasibility calculation. However 33 V standoff, 34..39 V VBR, only 10 mA DC breakdown absolute limit, temperature/pulse conditions and pre-resistor drop constrain 36 V continuous use. A 100 ohm pre-resistor also takes roughly ampere-to-tens-of-ampere surges, not L1's <0.81 A. Not a complete selection. |
| TVS2700 + post-resistor | SLVSED6A, Mar 2018: 35 V maximum in the stated hot 8/20 test; VBR=29.3..33.9 V; 12 mA DC breakdown absolute limit. | A >=1.75k post-resistor can bound ideal current at that clamp maximum without Vf_min. At the low clamp corner, source-end high-Vf light and sustained shunt dissipation become limiting. Do not treat an absolute DC current limit as normal-duty approval. |
| Vishay `SMBJ18A-E3/52` input clamp | 88392, 09-Jan-2024: 18 V standoff; 20.0..22.1 V VBR; 29.2 V maximum clamp at 20.5 A/10-1000 us and 25 C. | Robust passive TVP alternative. Its maximum VBR temperature coefficient does not by itself guarantee the entire hot dynamic clamping curve. Do not substitute 29.2 V as a universal maximum. |
| Ohmite `OX182KE-TR` / `OY182KE-TR` pulse resistor | OW/OX/OY EC#11705: high energy, but +/-10% and -1300 +/-300 ppm/C, plus much larger bodies. | Useful pulse-development alternatives, not precision 1.8k replacements. Cold/hot resistance shifts change brightness/inrush materially. The 14/20 kV figures expressly use a circuit where the full voltage is **not** applied directly to the resistor. |
| Input bridge or shunt before blocking diode | Corrects polarity for an isolated lamp. | Reject for this rung unless the entire six-end cut behavior is redesigned and proved; it can provide B-to-A/C return paths. |

## 9. Exact Closure Work

**Facts/decisions needed before a complete protection claim:**

1. Accept the conducted pulse amplitude, slopes, duration/energy, repetition and
   post-GDT tail at the branch pads. Sparkover maxima alone do not supply this.
2. Obtain LT3092's supported combined DC and transient envelope for L1, including
   rising power, dropout recovery, supply reversal, LED open/reversal, and the
   specified input filter. Required stage maximum: 18 mA, not just a typical trace.
3. Confirm fixed-reference below-knee loading and obtain/establish maximum
   turn-on overshoot with this limited current and parasitic load. The static
   4.3584 V bound leaves only 0.6416 V to the LED's 5 V reverse ceiling.
4. Resolve PWC pulse curves and CP effective capacitance/ESR/ESL for the declared
   envelope. These are concrete component requirements, not an open-ended
   request to replace every part.
5. Establish the actual cable/local-voltage envelope and source startup/maximum
   voltage. A 6 mA far-end guarantee cannot come from the old illustrative
   40 ohm/uniform-drop model or from assuming two supplies are connected.
6. Bound harness-induced differential voltage/current or accept a qualification
   envelope for it. No PCB clamp can guarantee an arbitrary externally induced
   voltage at the far end of 200 mm wires. Keep pair area small and route away
   from GDT/earth discharge paths; no field-soldered LED diode is proposed.

**Prototype qualification after a supported circuit decision:** instrument
the actual LED terminals and LED current, not only Px or the PCB connector.
Include cold/hot, low-current far-end, source-end, open/reversed LEDs, both
supply polarities, dropout/restart, final harness geometry and both GDT pulse
polarities. Reject measured peaks plus uncertainty above 20 mA forward or 5 V
reverse. Check stability across reference turn-on and regulator dropout, stored
charge, source-startup demand, every required clean-cut state, aggregate OFF
leakage, 5 m daylight visibility, RF loading and potted/solar steady temperatures.
A few successful samples do not create a missing manufacturer maximum.

The initial handoff proposed further L1 schematic/test-article development,
not production population. **That recommendation is superseded by the parent's
passive-circuit investigation in section 11.** No order, C4 closure, approval
refresh or protection qualification follows from either research route.

## 10. Sources And Execution

In the initial investigation, primary manufacturer documents were fetched with
native `webfetch`. For PDFs returned as binary, `https://r.jina.ai/https://...`
was used only to extract the same manufacturer-hosted document. Tabular pin
descriptions and text were used, without claiming visual verification then.
Section 11 records the subsequent actual page-image inspection. No network
command-line tool, physical test, vendor acceptance or stock allocation was
used. Search results were navigation only, not specification evidence.

| ID | Direct Primary Source | Revision / Main Use |
| :--- | :--- | :--- |
| R0 | [APEM Q10F5SXXSG02E](https://www.apem.com/led-indicators/professional-grade-panel-mount-led-indicators/q10/q10f5sxxsg02e) | Live page retrieved 2026-09-07: no resistor, family 1.8..3.3 V/20 mA max, 5 V reverse, 200 mm wires. |
| R1 | [ADI LT3092](https://www.analog.com/media/en/technical-documentation/data-sheets/lt3092.pdf) | Rev. D, 08/20; current programming, industrial grade, headroom, reverse paths, stability and typical-only transient plots. |
| R2 | [TI LM4050-N](https://www.ti.com/lit/ds/symlink/lm4050-n.pdf) | SNOS455H, March 2025, sections 5.1/5.3/5.7/7/8; orderable addendum 14-Oct-2025. |
| R3 | [TI TVS0500](https://www.ti.com/lit/ds/symlink/tvs0500.pdf) | SLVSED2C, Nov 2019, sections 6/7/8; negative diode, leakage and positive-clamp limitation. |
| R4 | [TI TVS1800](https://www.ti.com/lit/ds/symlink/tvs1800.pdf) | SLVSED4A, March 2018, sections 6/7/8; hot surge maximum, DC limit, dynamic loading. |
| R5 | [Diotec BYG23T](https://diotec.com/request/datasheet/byg23t.pdf) | Version 2026-08-11; 1300 V repetitive rating, current/recovery/leakage limits. |
| R6 | [Vishay TNPW e3](https://www.vishay.com/docs/28758/tnpw_e3.pdf) | 28758, 10-Apr-2026; coding, tolerance/TCR, thermal modes and drift/process limits. |
| R7 | [TT PWC](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Resistors/Datasheets/PWC.pdf) | 07.26; pulse-specific tests/curves, 500 V element limit, ordering and 110 C solder-joint condition. |
| R8 | [KEMET X7R MLCC](https://content.kemet.com/datasheets/KEM_C1002_X7R_SMD.pdf) | C1002_X7R, 2026-08-18; 1210/10 uF/50 V family and ordering, capacitance/process limitations. |
| R9 | [Mean Well LRS-75](https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF) | File revision 2025-04-07; capacity, adjustment, overload/OVP and typical rise time. |
| R10 | [Diodes AL5809](https://www.diodes.com/assets/Datasheets/AL5809.pdf), [AL5809Q](https://www.diodes.com/assets/Datasheets/AL5809Q.pdf), [AL5802](https://www.diodes.com/assets/Datasheets/AL5802.pdf) | DS36625 rev. 5-2; DS38233 rev. 2-2 advanced information; DS35516 rev. 10-2. |
| R11 | [Nexperia NCR420U/421U](https://assets.nexperia.com/documents/data-sheet/NCR420U_NCR421U.pdf), [BAS116](https://assets.nexperia.com/documents/data-sheet/BAS116.pdf) | 10-Dec-2018; 05-Aug-2020. BAS116,115 is a smaller negative-diode candidate: 80 nA maximum at 150 C/75 V, but retrieved VF maxima are at 25 C only. |
| R12 | [Infineon BCR431U](https://www.infineon.com/assets/row/public/documents/24/49/infineon-bcr431u-datasheet-en.pdf) | Rev. 1.0, 2020-03-03. |
| R13 | [ST STCS05](https://www.st.com/resource/en/datasheet/stcs05.pdf), [STTH112](https://www.st.com/resource/en/datasheet/stth112.pdf) | DocID13969 rev. 5, Jan 2022; Doc ID9343 rev. 5, Oct 2009. STTH112 is 1200 V, insufficient for the declared 1200 V plus stored-input reverse stress. |
| R14 | [TI TPS92611-Q1](https://www.ti.com/lit/ds/symlink/tps92611-q1.pdf) | SLDS238B, Jan 2020; especially dropout-recovery pulse warning. |
| R15 | [TI TLA431](https://www.ti.com/lit/ds/symlink/tla431.pdf), [TLVH431](https://www.ti.com/lit/ds/symlink/tlvh431.pdf) | SNVSCR4D, June 2026; SLVS555N, June 2024. |
| R16 | [TI ATL431](https://www.ti.com/lit/ds/symlink/atl431.pdf), [ATL431LI](https://www.ti.com/lit/ds/symlink/atl431li.pdf) | SLVSCV5E, Dec 2024; SLVSDU6D, Nov 2019. |
| R17 | [ADI LT1634](https://www.analog.com/media/en/technical-documentation/data-sheets/1634ff.pdf), [TI LM385/285-ADJ](https://www.ti.com/lit/ds/symlink/lm385-adj.pdf) | Rev. F, Oct 2014; SNVS741F, Apr 2013. |
| R18 | [TI TVS3300](https://www.ti.com/lit/ds/symlink/tvs3300.pdf), [TVS2700](https://www.ti.com/lit/ds/symlink/tvs2700.pdf) | SLVSDO2C, Feb 2018; SLVSED6A, March 2018. |
| R19 | [Vishay SMBJ](https://www.vishay.com/docs/88392/smbj.pdf), [MBE0414](https://www.vishay.com/docs/28766/mbxsma.pdf), [PR01/02/03](https://www.vishay.com/docs/28729/pr010203.pdf) | 88392, 09-Jan-2024; 28766, 11-Jul-2018; 28729, 08-Jul-2025. General ratings are not pulse approval. |
| R20 | [Ohmite OW/OX/OY](https://www.ohmite.com/assets/files/Datasheets/ow-ox-oy-series.pdf) | EC#11705; no printed revision date identified. Exact high-voltage test-circuit limitation retained. |

Commands actually run were read-only git inspection, `scripts/analyze_limits.py`
with declared screening parameters, calls to its existing `simulate()` function,
and arithmetic checks printed to stdout. The 1800 ohm /40 ohm-core /6.2 V-drop
CLI screen also ran its existing 280 ideal one-way cut cases successfully; it
was **not** a test of L1. No native KiCad/build/workflow commands were run.

The two rows in section 5 are reproducible with the existing model:

```bash
python3 -B -c 'from scripts.analyze_limits import simulate, Cable, Channel; print(simulate(cable=Cable(r20_ohm_per_km=(6.9,)*3), channel_a=Channel(resistor_ohm=1591.6, led_v=3.3, diode_v=3.55), channel_c=Channel(resistor_ohm=1591.6, led_v=3.3, diode_v=3.55)).summary())'
python3 -B -c 'from scripts.analyze_limits import simulate, Cable, Channel; print(simulate(cable=Cable(r20_ohm_per_km=(10.0,)*3), channel_a=Channel(resistor_ohm=1591.6, led_v=3.3, diode_v=3.55), channel_c=Channel(resistor_ohm=1591.6, led_v=3.3, diode_v=3.55)).summary())'
```

## 11. Passive Follow-Up

**2026-09-07, subsequent parent request. Comparison for a controlled prototype,
not an approved BOM or evidence that every requirement has passed.**

### Recommendation

Use the **400 ohm upstream /1800 ohm downstream topology** as the preferred
passive prototype comparison, with **two WHS2 200 ohm pulse resistors**, not
four PWC2512 100 ohm parts. It preserves 2200 ohm nominal total resistance and
requires no LT3092, programming network or bulk input capacitor. With the
previous output protection retained it has **10 parts per rung**, rather than
L1's 15. It trades a regulator-current transient claim for directly testable
node-voltage and resistor-current limits.

A **nine-part** version using a single WHS2 330 ohm and 1870 ohm post-resistor
also preserves 2200 ohm nominal total. Its pulse data support investigation,
but it raises the adverse-corner TVS DC current to about **11.3 mA against a
12 mA absolute limit**, and the zero-cable 82-rung source screen to **74.2 W**.
It is the lowest-count candidate found, **not the preferred margin choice**.
Do not save one resistor by concealing those consequences.

Neither variant is single-component-fault safe: in particular, **an open
post-resistor can overrun the input TVS's DC-current limit**. A controlled
prototype can investigate the circuit with explicit restrictions and protective
test equipment; this known gap must not be relabelled field qualification.

**Final audit: continuous TVP operation is a separate hold even with healthy
parts.** TI specifies a recommended 0..27 V input range [R26]. L2 can remain
above 27 V during normal TEST; being below a 12 mA absolute maximum does not
authorize that use. The comparison needs supported continuous-clamp evidence
or a revised input stage before normal-duty circuit selection, not merely a
successful pulse trace.

### L2 Netlist

Repeat for X=A and C; all named intermediate nodes are private to one rung.
The input diode is before **every** B-connected shunt. No earth connection is
added. The ordering of DP and the unshunted resistor string does not change
the DC proof, but the following explicit order avoids ambiguity:

```text
WIRE_X -- DPx(A->K) -- RUx1 200R -- RUx2 200R -- Px
Px -- RPOSTx 1k8 -- LED_X_POS -- J_LED_X.1
J_LED_X.2 = WIRE_B

TVPx: IN = Px; GND = B
LED_X_POS -- RBx1 22R -- UZx1.K; UZx1.A = B
LED_X_POS -- RBx2 22R -- UZx2.K; UZx2.A = B
TVNx: IN = LED_X_POS; GND = B

No current-regulator IC. No intentional reservoir capacitor.
External LED anode -> J.1; cathode -> J.2.
```

| Function | Exact L2 Candidate | Per Rung | Evidence / Limit |
| :--- | :--- | ---: | :--- |
| DP | Diotec `BYG23T` | 1 | Same 1300 V blocking candidate [R5]; do not substitute the 1000 V baseline diode for the 1200 V development envelope. |
| RU | TT `WHS2-200RFA25` | 2 | 200 ohm, 1%, +/-200 ppm/C. Body <=9.0 x 3.6 mm, lead <=0.81 mm, listed mounting centres 12.5 mm, minimum bend radius 1.2 mm [R21]. |
| TVP | TI `TVS2700DRVR` | 1 | IN pins 4/5/6 to P; GND pins 1/2/3 and exposed pad to B. 35 V hot 8/20 us clamp entry; **12 mA DC absolute limit at TA=27 C**, not a continuous-duty operating rating [R24]. Recommended input 0..27 V [R26]. |
| RPOST | Vishay `MBE04140D1801DC100` | 1 | 1800 ohm, **0.5%, 25 ppm/K** candidate, using [R19]'s order-code table. Same 0414 geometry/rating modes, not the existing purchased 2200 ohm part. |
| Positive clamp | TI `LM4050BEM3-4.1/NOPB` | 2 | Same pinning and shunt-current proof as section 4. |
| Ballast | Vishay `TNPW080522R0BEEA` | 2 | 22 ohm per reference; retain separate resistors. |
| Negative clamp | TI `TVS0500DRVR` | 1 | Same pinning as L1. Used for negative clamping, not its too-high positive clamp. |

This is a comparison BOM, not newly purchased inventory. The listed MBE variant
and WHS ordering options still need actual quote/allocation confirmation.
No source footprint or location was changed. A single WHS2 **390/400 ohm** is
not an available value inferred from its graph: the actual specified family
range stops at **330 ohm**. Two 200 ohm parts avoid that unsupported order code.

### Current And Reversal

The parent's proposed 1.8k/1% calculation is correct **at that resistance
corner**, but initial tolerance alone is insufficient for a temperature-aware
ceiling:

```text
35 / (1800 * 0.99) = 19.640853 mA
```

For the tighter MBE candidate at -40..125 C element temperature, using the
20 C TCR reference and the larger 105 C excursion:

```text
RPOST_initial_min = 1800 * 0.995 * (1 - 25e-6 * 105) = 1786.298625 ohm
RPOST_initial_max = 1800 * 1.005 * (1 + 25e-6 * 105) = 1813.748625 ohm
```

Use these explicit **prototype acceptance envelopes**, including measurement
uncertainty, temperature, assembly and changes after the pulse sequence:

```text
RU_each = 190..210 ohm
RU_total = 380..420 ohm
RPOST = 1770..1830 ohm
RB_each = 21.78..22.22 ohm
Vsource_DC <=37.0 V including ripple; nominal setting 36 V
```

They are controlled test-article requirements, not manufacturer-guaranteed
combined lifetime corners. Accept each RU separately: the total alone does not
bound pulse-voltage or energy sharing. Recheck resistance after stress. Source
startup and other transients remain separate waveform acceptance cases, not
permission to exceed the normal ceiling periodically. Do not use a generic
250 ppm/C 1.8k power resistor without recalculating its minimum.

For **VP(t) <=35 V**, a forward-conducting LED with Vf >=0 and no bypassing
current gives:

```text
I_RPOST <=35 /1770 = 19.774011 mA <20 mA
```

No LED Vf_min, current-regulator startup time, or LED pulse-overdrive rating is
needed for that inequality. But it is **not a claim that VP(t) is always <=35 V**,
nor a proof against lead-induced current or parasitic-capacitance discharge.
Acceptance must independently verify **actual LED peak current + uncertainty
<=20 mA**, not just average current or voltage at P.

The functioning positive shunts retain section 4's **4.3584 V steady maximum
at 20 mA total**, with <=11.9273 mA in either reference. Thus LED-lead reversal
is bounded in steady operation. Negative source reversal has the specified
<=0.65 V/1 mA negative-clamp point, with input-diode DC leakage much smaller.
Neither static result proves the LED-terminal peak during initial energization,
polarity changes, GDT collapse, or a harness-induced event. The spare PSU remains
disconnected and all six field-end mode contacts remain independent.

### Continuous Clamp Current

Define V as the local positive X-to-B source voltage, VO as connector voltage,
IU as upstream current, IP as post-resistor current, and IT as input-TVS current:

```text
IU = (V - VDP - VP) / RU
IP = (VP - VO) / RPOST
IT = IU - IP
```

TI specifies **VBR >=29.3 V at 1 mA over operating free-air temperature**.
For the normal monotone clamp characteristic, split the proof into two cases:
IT <=1 mA is already small; if IT >1 mA, VP >=29.3 V. Therefore, for functioning
output shunts and VO <=4.3584 V:

```text
IT_max <= max(1 mA, (V - 29.3)/380 - (29.3 - 4.3584)/1830)
       = 4.002289 mA at V=36 V
       = 6.633868 mA at V=37 V
```

VDP_min=0 is deliberately conservative. This covers an external LED open or
reversed, **not** an open post-resistor. It does not pretend the 29.3 V/1 mA
point is a constant clamp voltage at all currents.

At nominal 400/1800 ohm, a 0.7 V diode and the illustrative low-clamp VP=29.3 V,
an open/reversed LED near 4.27 V gives approximately **1.09 mA at 36 V** and
**3.59 mA at 37 V** in TVP. The adverse maximum is higher; a high-breakdown
TVP may not conduct appreciably at all. Thus "2-4 mA" is a possible operating
case, not a guaranteed clamp-current range.

The resulting adverse-corner steady bounds are:

| Quantity, Functioning Protection And External LED Open/Reversed/Short | Bound |
| :--- | ---: |
| Post current with V <=37 V, even LED Vf=0 | <=37/(380+1770) = **17.2093 mA** |
| P without any positive input-TVS conduction, V <=37 V | <=(37*1830+4.3584*380)/(380+1830) = **31.3874 V** |
| Input current per rung at 36 /37 V | <=**17.6316 /20.2632 mA** |
| TVP dissipation at 37 V | <=**0.1944 W** |
| Combined RU dissipation at 37 V | <=**0.1561 W** |
| RPOST dissipation at 37 V | <=**0.5243 W** |
| All 82 rungs, negligible cable resistance, 37 V | <=**1.6616 A /61.48 W**, before hub/other loads and PSU derating |

The current bound includes the IT <=1 mA case too. For example, that case's
upstream maximum at 37 V is `(37 +1770*0.001)/(380+1770) =18.03 mA`, smaller
than the 20.2632 mA high-clamp case. The power maxima are separate adverse
corners; do not add them as though simultaneously attained.

TVP's 70.4 C/W JEDEC metric gives about **13.7 C** rise at 0.1944 W. This is a
thermal screen, not the gel-board thermal resistance. The 12 mA number is an
absolute maximum under the table's **TA=27 C** condition, not an all-temperature
continuous operating rating. More fundamentally, TI's recommended input range
is **0..27 V**, and section 10 explicitly cautions against violating it [R26].
Even the nominal 36 V /2.1 V LED /0.7 V diode, TVP-inactive example places P at
**29.2636 V**. This is sustained operation outside that recommendation, not
just a fault or surge excursion. Obtain TI-supported continuous operation
above 27 V for the calculated voltage/current/power and accepted temperature/
lifetime envelope, or revise the input stage. Neither the JEDEC heat estimate
nor a successful short pulse establishes that evidence.

At 70 C local ambient the MBE standard-mode rating is 0.65 W, above the 0.5243 W
steady screen; its film must still stay <=125 C. At 85 C its standard-mode
derated allowance is only about 0.473 W, so the worst shorted-LED screen would
not fit. **An unqualified hot box is not covered.**

With the normal 36 V/2.1 V LED/0.7 V diode assumptions and TVP inactive, total
current remains **15.0909 mA**, RU dissipates **0.0911 W**, and RPOST **0.4099 W**.
Two rungs have essentially the baseline's approximately 1 W resistor heat,
redistributed between parts, before any extra input-shunt dissipation.

The 40.4 V accessible-adjustment screen is **outside this prototype window**:
the loaded TVP-current bound becomes **15.58 mA**, already beyond 12 mA.
Neither Mean Well's much higher OVP threshold nor an unused spare enforces
37 V. Independently limit/monitor the actual prototype supply; the parent owns
the final source-interface enforcement.

### Steady Fault Disposition

| Fault | Electrical Result / Hold |
| :--- | :--- |
| External LED open or leads reversed, output shunts healthy | Output remains shunt-loaded; the <=6.634 mA TVP bound at 37 V applies. These are calculated steady load cases, not approval of sustained TVP operation above its recommended 27 V input or a thermal pass. |
| External LED /connector short | Post current <=17.2093 mA steady; RPOST <=0.5243 W. This is not a hot-box thermal pass. |
| Supply reversed; either external LED orientation | DP blocks the new B-to-core path. Negative clamps carry leakage in steady operation; check transient recovery separately. |
| **RPOST open, or connection to the entire downstream network lost** | **TVP may take <=17.63 mA at 36 V or <=20.26 mA at 37 V, exceeding 12 mA. NOT benign.** A favorable temperature estimate cannot override the current absolute maximum. |
| One LM4050 /its ballast opens | The other reference is not guaranteed to share. It can exceed 15 mA in an adverse steady corner and during a pulse. No redundancy claim. |
| Both output shunts lost | Reversed LED is no longer protected to 5 V. TVP is not a 5 V clamp. |
| Output shunt shorts | LED is dark; the intact post-resistor limits steady current as for an output short. |
| RPOST shorts | LED/output shunts can receive tens of mA through RU alone; the 20 mA proof is lost. |
| TVP shorts | <=97.4 mA and <=3.60 W in RU at 37 V; investigate hot fault containment. Two catalog 2 W resistors do not establish gel/solar safety or a clearing time. |
| TVP opens | Normal DC post-current limiting remains; conducted-surge limiting to 20 mA does not. |
| DP opens | Local indicators go dark; the WAGO through-splices remain unchanged. |
| DP shorts | Positive DC may appear normal, but reverse/core-isolation behavior is lost; required clean-cut behavior can be compromised. |
| One RU shorts | Higher TVP DC and surge current; recalculate/fault-test, not a protected substitution. |

If a lost downstream load must keep TVP below 12 mA solely through RU at 37 V,
the necessary bound is **RU_min >=(37-29.3)/0.012 =641.67 ohm**, before design
margin. That is incompatible with retaining 400+1800=2200 ohm unchanged.
Options are a larger upstream resistance with rechecked brightness, a clamp
with supported higher continuous capability, or a genuinely detecting cutoff.
An ordinary common 2 A fuse does not detect this roughly 20 mA local fault.
Do not silently omit it from the prototype risk statement or field-release work.

### Original Pulse Curves Resolved

Used the DFM evidence method: native `webfetch` of Google's public `gview` for
the **original TT-hosted PDFs**, followed by `viewerng/img?id=...&page=N-1&w=2400`.
The returned image attachments were actually inspected. Permanent sources are
the manufacturer links below, not expiring viewer IDs. No PDF/image file was
written into the workspace. Figure-reading precision is stated conservatively;
these are not digitally tabulated exact limits.

| Source / Figures Actually Read | Relevant Result | Decision For This Envelope |
| :--- | :--- | :--- |
| PWC, **07.26**, PDF pp. 1-3: dimensions, 1.2/50, 10/700 and rectangular-pulse plots | PWC2512 single-pulse curve is about **200 W at 100 us**, or 0.020 J; 50 rectangular pulses at 1-minute intervals, <1% resistance shift. Continuous-pulse limit there is lower, about 100 W. | **Reject four 100 ohm PWC2512 parts for 1200 V/100 us rectangular exposure.** Each nominal part would take 900 W/0.090 J, before tolerances. The much shorter lightning-waveform curves are different tests and cannot rescue this rectangle by a voltage-only comparison. |
| WHS, **06.26**, PDF pp. 1-3: family range, body/pin maxima, short-pulse energy and 1.2/50 plots | Around 200 ohm, WHS2's plotted energy is approximately **1.2 J**, conservatively above 1 J; its 1.2/50 voltage limit is above 2 kV. The voltage plot explicitly describes **net voltage across the resistor**, 10 pulses/30 s intervals, <5% drift. | Two 200 ohm parts have useful room-temperature/low-repetition screening margin over <=0.210 J and <=664 V per part below. Hot repetitive performance and actual assembly still require qualification. |
| WP-S, **06.26**, PDF pp. 1-2: dimensions, ratings, energy curves | WP1S is 6.2 x 2.8 mm and about 0.2 J near 390 ohm: too small energetically. WP2S is 9 x 3.6 mm, with only roughly 0.5 J near 390 ohm; energy plot expressly applies below 100 ms, low mean power, at 25 C. WP-S also lists limiting-element voltages, unlike WHS's explicit no-LEV statement. | Single WP2S 390 ohm is a compact lead, not selected: modest energy margin and unresolved applicability of its voltage limit to a 1200 V pulse. A larger WP3S improves energy but is 14.5 x 5.2 mm; do not claim high-voltage suitability from joules alone. |
| SPP, **04.22**, PDF pp. 1-3 | Original sheets prominently carry **OBSOLETE** in red, not apparent in the earlier text extraction. | Reject for a new sourcing baseline. Do not add its attractive nominal dimensions to candidate inventory as though current production were confirmed. |

The newly visible PWC 200 W/100 us limit also rejects L1's earlier four
390 ohm string against L1's own <=261 W-per-part rectangular screen. This is
a resolved negative finding, not an indefinitely unreadable curve.

For L2's accepted RU_total >=380 ohm, conservatively ignoring clamp/diode drops
and generator resistance:

```text
I_RU_screen <=1200/380 =3.157895 A
E_RU_total_screen <=1200^2 *100 us/380 =0.378947 J
R_each <=210 ohm
E_each_screen <=3.157895^2 *210*100 us =0.209419 J
V_each_screen <=3.157895*210 =663.16 V
```

These are lumped resistor-domain screens, not a guarantee of a complete RLC
waveform. Do not infer hot pulse capability by scaling the DC derating graph.
Use the defined initial temperature, five pulses per polarity/60 s interval
development sequence, and check resistance/body condition afterward. Validate
the complete tail and any pre-existing stored energy separately.

BYG23T lists 3 A repetitive peak at its stated frequency/temperature and
15/18 A single half-sine surge conditions. The 3.158 A zero-source-impedance
screen is not itself a repeated-pulse diode qualification. With a **1200 V
Thevenin generator and >=42 ohm series source impedance**, the corresponding
resistive screen falls below 2.85 A. State which voltage is being specified;
1200 V measured at the board pads is not the same test. Check the actual diode
current and reverse recovery. With P <=35 V, the simple negative-input reverse
screen is <=1235 V, but wirewound/trace ringing must be included in the actual
1300 V diode-voltage limit.

### Smaller And 33 V Alternatives

| Variant | Advantages | Actual Limitations |
| :--- | :--- | :--- |
| **Single `WHS2-330RFA25` + `MBE04140D1871DC100`**, same TVP/output clamps | Nine parts/rung; nominal 330+1870=2200 ohm. WHS2 330 ohm is actually within its specified range. Its short-pulse curve is around 1 J and 1.2/50 limit above 2 kV; body 9 x 3.6 mm. | At initial tolerance/TCR corners, loaded TVP current can reach **10.84 mA at 37 V**. With a declared wider RU=315..345 and RPOST=1840..1900 envelope, it reaches **11.32 mA**, about 0.332 W. An all-near-source 82-rung screen is **74.16 W**, before auxiliaries/PSU derating. RPOST-open remains unsafe. More low-clamp source-end dimming than the 400/1800 version. |
| **TVS3300 +200 ohm upstream +2000 ohm post**, same output clamps | Nominal total 2200 ohm; potentially less normal input-shunt loading. | **40/(2000*0.99)=20.202 mA**, so a 2k/1% post-resistor fails the zero-Vf peak screen even at the cited 27 C maximum clamp. Need >=2k minimum including all errors, practically a higher nominal value. The 40 V maximum is not a tabulated all-temperature arbitrary-waveform bound. |
| TVS3300 normal/reversed-load corners | 33 V standoff, VBR=34..39 V at 1 mA. | With nominal 200/2000 and VO=4.3584, VDP=0, the unloaded-by-TVP P is **33.1235 V at 36 V** and **34.0326 V at 37 V**. Thus even normal LED-open/reversed operation cannot simply use the 33 V leakage specification. RPOST-open at 37 V can draw **15.15 mA through 198 ohm**, versus TVS3300's **10 mA DC absolute** limit. Raising RU or lowering the enforced source window changes the light-output budget. |

For the nine-part option, the accepted RPOST minimum 1840 ohm would give
35/1840=19.022 mA resistor current. Its low-count advantage is real, but it
does not justify operating a 12 mA-absolute device with unspecified current
or source-temperature margin. It also inherits TVS2700's above-27 V
continuous-use hold. Prefer the 400/1800 comparison unless the parent explicitly
accepts and verifies the narrower envelope.

### Light, RF And Prototype Exit

Keeping nominal total R=2200 preserves the baseline **only when TVP is inactive**.
At the low-breakdown corner it adds input load and can trim source-end light.
For example, at VP=29.3 V and LED Vf=3.3 V, the nominal 1.8k post current is
14.444 mA, before the <=0.20022 mA output-shunt allowance. That allowance retains
section 4's below-knee assumption and TVN's **85 C** leakage point; it is not a
125 C leakage guarantee. The resulting LED current is in the 15 mA class, not
a guaranteed 15 mA minimum. At an actual 6 mA far-end LED, P is far below TVP's
knee; no regulator dropout has been added. Under the deliberate 3.3 V LED
/1.9 V diode and accepted resistor maxima, local X-to-B
voltage of about **19.2 V plus wiring/leakage allowance** is needed to guarantee
6 mA. Actual diode drop is likely much lower but was not assigned a new maximum.

The separate [conditional cable study](DESIGN_BOUNDS.md) now supplies an
**8.21 ohm/km at 20 C** metal-coated Class 5 ceiling. Its 70 C copper screen plus
the declared 0.025 ohm/core/span contact budget gives **40.29306 ohm per 4 km
core**, conditional on the stated compliance and contact assumptions; the
0.30 mm strand/Class 5 construction discrepancy remains open. Its baseline
nonuniform-load cases already give less than 6 mA at a 35 V feed. Those results
are **not L2 predictions**: they use the existing resistor/diode branch without
TVP or output-shunt loading. The new 35 V feed floor is also a requirement,
not enforced hardware. Use those cable/source conditions in a proper L2 network
model; do not claim a field-wide 6 mA minimum solely because nominal total R
matches. Test the purchased LEDs at the final minimum current and at source-end
current for 5 m daylight contrast. No direction selector, timeout or field
soldering is introduced.

Removing the 10 uF input capacitors removes L1's deliberate reservoir/inrush
and strong input AC-bypass problem. RF loading still includes the input diode,
wirewound parasitics and TVS2700's **100 pF typical** input capacitance, plus
the RPOST-isolated output clamps. No maximum RF admittance or RF transparency
is proved. The actual transmitter, unequal-core and cattle-fence conditions
remain qualification cases; no B-to-EARTH plane or bond is added.

For the controlled test article, **VP_peak + uncertainty <=35 V must cover the
complete trace**, including first turn-on, prebias, the leading edge, GDT snap-down,
reversal and ringing. The 35 V hot 8/20 us entry does not guarantee it for a
1200 V/100 us rectangle or an arbitrary front. Independently require LED forward
peak + uncertainty <=20 mA and LED reverse peak + uncertainty <=5 V at the LED,
not just at the PCB. Output shunt startup/low-knee behavior and parasitic paths
still matter. Establish those waveforms first with suitable surrogate loads;
do not sacrifice purchased LEDs to an assumed clamp response.

No capacitor is specified by this comparison. If measurement establishes that
P-node filtering is necessary, a capacitor **before RPOST** does not bypass
that resistor, unlike a capacitor across it or across the LED. Its value,
stored energy, RF loading and pulse response would need a new bounded decision,
not automatic population of another speculative part.

The immediate P3 handoff is the circuit and component envelopes above, **not
placement approval**. Two WHS2 bodies, the additional post-resistor, the SMA diode
and the shunts need real placement/routing and high-voltage-to-protected-node
spacing review. WHS2's stated 0.81 mm lead maximum is useful fit evidence; its
forming, two-part layout and solder process are not approved by the family
dimensions. Preserve every protected rail, via, mount and LED terminal mapping.

The normal/LED-open/LED-reversed/LED-short current and heat calculations are
conditional on the stated <=37 V envelope and functioning parts. They do not
establish supported continuous TVP operation above its recommended input range.
That issue, the dynamic tests, hot pulse endurance, real minimum light/RF
behavior and known single-component fault gaps remain explicit. **No
production-parts approval or field release is claimed.**

Additional direct sources, all fetched in this follow-up:

- **R21:** [TT WHS](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Resistors/Datasheets/WHS.pdf), 06.26, PDF pp. 1-3 visually inspected; ordering text identifies F/1% and A25 packaging.
- **R22:** [TT WP-S](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Resistors/Datasheets/WP-S.pdf), 06.26, PDF pp. 1-2 visually inspected.
- **R23:** [TT SPP](https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Resistors/Datasheets/SPP.pdf), 04.22, PDF pp. 1-3 visually inspected, marked OBSOLETE.
- **R24:** [TI TVS2700 electrical limits](https://www.ti.com/document-viewer/TVS2700/datasheet/electrical-characteristics-a-tvs-vvcm-template-electchar), [absolute ratings](https://www.ti.com/document-viewer/TVS2700/datasheet/absolute-maximum-ratings-a-tvs-vvcm-template-absmax), [thermal information](https://www.ti.com/document-viewer/TVS2700/datasheet/thermal-information-a-tvs-vvcm-template-thermal), SLVSED6A, March 2018, re-read directly in manufacturer HTML.
- **R25:** [TI TVS3300 electrical limits](https://www.ti.com/document-viewer/TVS3300/datasheet/electrical-characteristics-a-tvs-vvcm-template-electchar), SLVSDO2C, February 2018, re-read directly in manufacturer HTML.
- **R26:** [TI TVS2700 recommended operating conditions](https://www.ti.com/document-viewer/TVS2700/datasheet/recommended-operating-conditions-a-1426275860-roc) and [power-supply recommendations](https://www.ti.com/document-viewer/TVS2700/datasheet/power-supply-recommendations-slvsed27749), SLVSED6A, March 2018, sections 7.4/10 re-read in the final audit. Recommended input 0..27 V; section 10 expressly cautions against exceeding this range for proper function. The 12 mA absolute-maximum comparison is not continuous-use authorization.

The numerical follow-up screens, including the final audit, were checked by
calculation-only `python3 -B -c` commands printing to stdout. No file/network
I/O was performed by those commands. The final audit also reran the unchanged
`python3 -B scripts/design_bounds.py` (exit 0), reproducing the baseline cable
and nonuniform-current results cited above; it does not model L2.
`git diff --no-index --check /dev/null pcb/LED_PROTECTION_RESEARCH.md` passed.
No L2 full-network/transient model, KiCad check or physical test was run in this
follow-up, and no shared design/build file was edited.
