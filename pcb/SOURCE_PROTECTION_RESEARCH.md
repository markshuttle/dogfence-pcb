# Source And GDT Protection Research

P2 continuation, 2026-09-07. Checkpoint `97e202d`, hardware **1.2.0-dev**.

**Research and proposed prototype architecture only. No design/BOM change,
hold closure, procurement authorization, or hardware approval.** This record
does not supersede `ELECTRICAL.md`, `ASSEMBLY.md`, or the release gates.
Only this research file is owned by this work. Switch research is delegated
to the environment workstream and is not a deliverable here.

**Historical integration after checkpoint ad282e3:** the PCB then had the simple
16-part PR02/BYG23T indicator hybrid, not any GDT/source replacement proposed
below. All six original GDTs remain. The user prohibits energized cattle fencing
near the whole boundary cable, stations and hub; the old parallel exposure is
withdrawn. This does not establish GDT recovery or remove nearby-lightning/RF/
switching and earthing questions. The 37 V / 1.6 A hub proposals below remain
**unimplemented historical targets**. Recalculate them before use: the then-current
PR02/40.39597 V normal-load screen could reach 1.561876 A, above the minimum
limit of the old proposed 8-kohm TPS26600 setting. See current ELECTRICAL and
DESIGN_BOUNDS, not the older hub circuit as a ready-to-populate design.

**2026-09-11 resistor correction:** the unchanged-topology 16-part hybrid uses
**TE Connectivity 35212K2FT / C4129105 2512 SMT** (in stock at JLCPCB) in the
prototype BOM only. The user confirms **Yageo SR2512FK-7W2K2L /
[C876850](https://jlcpcb.com/partdetail/C876850) ORDERED** with an advised 20-day
wait for future production, not receipt or allocation. The prior Uni-Royal PS12
order was cancelled/refunded due to stockout; [MATERIALS](../MATERIALS.md)
preserves its historical 110-part order. Whole-BOM `allocation_verified` remains
`false`; **C4/C5/W3/W1/W4 remain open**. TE prototype results do not qualify Yageo
thermal behavior. Separate production-part review and controlled BOM/CAD,
library, model and note updates, followed by reverification, are required before
production release under [ORDERING](../ORDERING.md).

PR02 figures above are historical. Current TE **9-1773463-5, Rev G, 02/2025**
evidence and conditional screens are in [ELECTRICAL](ELECTRICAL.md) and
[DESIGN_BOUNDS](DESIGN_BOUNDS.md): reference-board/P70 transfer is conditional,
and the retained 25 C reference / -30..125 C linear screen is an engineering
assumption, not verified TE TCR test conditions. Do not transfer PS12 overload
or pulse data. [ASSEMBLY](ASSEMBLY.md) controls the retained alternate project
lands and their supplier placement/stencil/solder hold, not a manufacturer-exact
fit claim. No source/GDT replacement below is selected or required to generate
Gate P files; all five holds are deferred for files, not closed.

## Decision

There is a credible bounded prototype path, but **no retrieved small bare-GDT
datasheet proves recovery on the complete powered fence merely because
36 V is below its 135 V holdover entry**. This is a specific network mismatch,
not a claim that these tubes certainly remain conducting at 36 V.

1. **Minimum-change evaluation circuit:** retain six separate shunt paths;
   evaluate Bourns `GDT25-47-S1-RP` for AB/BC, `2035-47-BLF` for the raised AC
   path, and `2027-47-BLF` for the three core/EARTH paths. Use the single-source
   controlled hub specified below, not a directly connected LRS/fuse pair.
   These are concrete prototype candidates with published network-qualified
   holdover, not a released replacement set. Earth-tube impulse-life ratings
   differ from the baseline and must not be described as an equivalent upgrade.
2. **Preferred alternative when a DC-power-rated primary is required without
   extrapolating telecom holdover:** evaluate TDK `B88069X1993B501`,
   `LN8-A1200DC-4`, with its three specified grading capacitors in **each**
   of the six shunt paths. Its 48 V +/-20%, 30 A DC-source specification is
   materially stronger evidence for this application. An engineered mounting/
   carrier and capacitive-loading review are necessary; it is not an axial or
   SMT drop-in. A hub-only replacement would leave the remote bare paths intact.
3. **Do not freeze an unattended-fault-safe field architecture yet.** Neither
   a holdover-qualified tube nor the proposed hub overcurrent latch disposes
   of every damaged, resistive GDT/cable fault. The missing disposition is
   local interruption/containment or demonstrated benign continuous failure,
   not an arbitrarily sensitive hub current threshold. Section 6 makes that
   distinction explicit.

A controlled prototype may be built to resolve powered recovery and thermal
behavior before field/surge qualification is complete. Such a prototype needs
an independently protected test fixture and accepted mechanical/process design;
it must not be represented as already meeting the unresolved fault requirement.
No field qualification is being demanded before an isolated component or hub
evaluation. The five assembled-board order still has the other project's
electrical, fit and process gates.

## 1. Fixed Inputs

- **Two MEAN WELL `LRS-75-36` units are ORDERED**, per the user in this session.
  The user subsequently allocated **one to TEST and one as a disconnected spare**.
  Delivered nameplates/settings remain to inspect. The circuit uses **one**
  source, never a parallel, series, opposite-end or second-channel connection.
- TEST remains same-end: Start A/C positive, Start B negative; End A/B/C each
  isolated. There is no normal TEST timer, direction selector or permanent
  End A/C strap. Reset does not restore RUN automatically.
- The current population specification fits all six GDTs on every station
  board, including the 36 standard boards with unwired external EARTH terminals.
  The 41-station requirement is therefore **246 tubes**, not 138; this is not
  a claim that 41 boards have already been manufactured or installed.
- Preserve WAGO through-splices and PCB taps, all protected copper/vias,
  63 x 56 mm board, 9.00 mm earth-tube centre pitch, and north-south AC overpass
  with 15.24 mm formed pitch and >=2.00 mm whole-span pre-gel clearance.
- No direct core/PE or DC-negative/PE bond is proposed. PE is never switched.
  External earth-potential rise and coupled mains/switching transients are not
  energy supplied by the 36 V source and need their own applicable envelope.
  Cattle-fence exposure is now excluded by the user-confirmed whole-boundary
  prohibition; inspect/maintain it rather than qualify the withdrawn setup.

## 2. What Holdover Actually Specifies

### Traceable Test Network

The primary ITU documents are available, so it is no longer necessary to leave
the entire standard network unspecified. ITU-T K.12 edition 9.0 (05/2010),
sections 6.5, 7.5, Table 3 and Figure 4, specifies the following two-electrode
tests [N1]. Edition 10.0 (08/2024), sections 7.5 and 8.5, retains these values
[N2]. Bourns GDT25 explicitly references edition 9.0, section 7 [G2].

| Test | DC source PS1 | DC-feed R3 | R2 | C1 | Turn-off requirement |
| :--- | ---: | ---: | ---: | ---: | :--- |
| 1 | 52 V | 200 ohm | Omitted | Omitted | <150 ms |
| 2 | 80 V | 330 ohm | 150 ohm | 100 nF | <150 ms |
| 3 | 135 V | 1300 ohm | 150 ohm | 100 nF | <150 ms |

The surge generator supplies a **100 A, 10/1000 us short-circuit waveform**,
with impulse and DC polarity the same. Turn-off is measured in both current
directions, with three impulses per direction at intervals no greater than
one minute. The RC portion is separate from the DC feed; **150 ohm is not
the test's sustained source resistance**.

For nominal sparkover >=230 V, the standard also calls for the Annex A ISDN
test. The retrieved text did not decode the Annex A drawing's circuit values.
Obtain the original readable figure and the vendor's actual test declaration
before claiming full equivalence. Likewise, a Bourns sheet saying only
"network applied" does not identify every optional standard test, temperature
or post-life condition. Littelfuse CG/CG2 and SH additionally name
**REA PE-80, 0.2 A** [G6, G7]; that condition is not interchangeable with
Table 3's 1300 ohm network.

K.12 defines holdover as clearing under **specified circuit conditions**, and
expressly excludes GDTs connected to electrical power systems from its scope.
Its electrical-requirements note also warns about circuit-dependent
oscillations involving impedance/inductance. Referencing K.12 terms alone is
not a declaration of every K.12 performance test.

### Conservative Comparison

For the standard's 135 V DC-feed branch, ignoring diode drop:

```text
I_test(v) = (135 - v) / 1300
I_test(0 V)  = 103.846 mA
I_test(10 V) =  96.154 mA
I_test(15 V) =  92.308 mA
```

The existing nominal 36 V calculation has **259.543 mA** in the far-end
10 V arc path, **2.602168 W** in that path, and only **0.979810 A total**.
That is about **2.70 times** the standard DC-feed current at 10 V, and also
exceeds 0.2 A. The voltage advantage does not produce a pointwise smaller
load line. A near-source, current-limited 1.6 A fault is still much farther
outside the telecom network.

As a useful sufficient-load-line screen, a 37 V source through a simple
series resistance would require:

```text
(37 - v) / R <= (135 - v) / 1300       for 0 <= v <= 37 V
R >= 1300 * 37 / 135 = 356.30 ohm      sufficient for that DC-feed comparison
```

This is **not** a proposed series rail resistor: it would destroy the healthy
load/brightness budget. Nor is DC load-line dominance alone a complete dynamic
GDT theorem. It identifies why a bare-tube substitution plus a 1.5-2 A hub
limit does not obtain a datasheet-only guarantee.

Do not infer extinction from typical glow voltage being above 36 V, or infer
holding current from a `<0.5 A` or `<1 A` **glow-to-arc** transition limit.
Those describe different operating states/directions. Conversely, failure
of this sufficient comparison is not proof of actual failure: a vendor
application limit or powered type test can establish a broader usable envelope.

## 3. Exact GDT Evidence

All current/impulse figures below are **component test ratings**, not a station
or assembled-board rating. Refer to the originals for complete conditions.

| Manufacturer / Exact Candidate | Retrieved revision and relevant specification | Disposition |
| :--- | :--- | :--- |
| Bourns `2027-47-BLF` | [G1], rev. E 01/26. 470 V +/-15% at 100 V/s; 135 V holdover, <150 ms, network applied. 1 kV/us sparkover 1000 V is a **typical distribution**, not a universal maximum. 25 kA 8/20 us one operation; 10 kA ten operations; 2 kA 10/350 us two operations. -55..+125 C. | Useful earth-path holdover evaluation candidate. Not a 5 mm overpass or SMT replacement. Its ten-shot 10 kA rating does **not** match Ruilon's ten-shot 20 kA entry. |
| Bourns `GDT25-47-S1-RP` | [G2], rev. D 06/23. Two electrodes; 470 V +/-20%; 135 V holdover, <150 ms, K.12 ed. 9 network. 860 V at 1 kV/us has a **99% measured-value probability** qualification. 7 kA 8/20 us ten operations; 10 kA one operation. <0.6 pF; -55..+125 C. | Preferred compact AB/BC evaluation candidate, subject to land-pattern acceptance. Not an unconditional 36 V power-network recovery guarantee. |
| Bourns `2035-47-BLF` | [G3], rev. 02/26. Two electrodes; 470 V +/-15%; 135 V holdover, <150 ms, network applied. 950 V at 1 kV/us is typical-distribution data. 5 kA 8/20 us >10 operations; 10 kA one operation. -55..+85 C. | Preferred small axial AC evaluation candidate. Control lot/date and PCN [G4] below. |
| Bourns `2057-47-BLF` | [G5], rev. B 09/19. Two electrodes; 470 V +/-20%; **150 V** holdover, <150 ms, network applied. 1100 V at 1 kV/us is typical-distribution data. 5 kA ten operations, 10 kA one operation; -40..+90 C. | Alternative axial part, not a better power-network guarantee merely because 150 >135. Body is slightly larger than the current Bencent maximum. |
| Littelfuse `CG2470L` | [G6], rev. 12/12/17, still linked by the active exact-part page. 400/470/540 V DC min/nom/max; 1200 V maximum impulse entry at 1 kV/us; 135 V holdover with REA PE-80 0.2 A / K.12 <150 ms note. 20 kA 8/20 us five operations; -40..+90 C. | Correct current ordering form of the historical `CG2-470L` suggestion. Live page says 150 V holdover, conflicting with its linked 135 V PDF: do not silently take the larger value. Failsafe: No on the part page. |
| Littelfuse `SH470` | [G7], rev. GD. 03/09/21. Two-electrode square SMT; 376/470/564 V; 1100 V maximum impulse entry at 1 kV/us; **135 V**, <150 ms, REA PE-80 0.2 A/K.12. 5 kA ten operations, 6 kA one operation; <0.7 pF; -40..+90 C. | Plausible same-size AB/BC alternative. The 2017 catalogue's 150 V entry is not the later datasheet's value. Existing large lands are not its recommended pattern. |
| Bourns `2038-47-SM-RPLF` | [G8], rev. P 01/26. **Three electrodes**, 135 V network-applied holdover <150 ms. Line/line breakdown tolerance is only typically <+30%; impulse entries are typical distributions. Current rating is total, divided between line/ground chambers. | Not a two-electrode `2035` substitute. A centre terminal cannot be ignored, bonded to PE, or assigned to B without redesigning/reviewing the complete network. No substitution proposed. |
| Littelfuse SL families | [G9], manufacturer GDT catalogue rev. 12/12/17. `SL1011A470`/`SL1411A470` rows have 135 V K.12 holdover <150 ms; two electrodes, 8 mm-class bodies. `SL1021A/B` is a **three-electrode** family. The inspected SL1021 table has 450/500 V rows, not a 470 V row. | Do not treat historical `SL1021A470R` prose as a validated two-pin earth-tube MPN. Exact current order/drawing would need confirmation. The family does not remove the network qualification. |
| TDK `B88069X6441S202` / `B88069X6441T502`, `A81-A470X` | [G10], version 03, 2026-04-01. Two electrodes; 470 V +/-20%; 1100 V at 1 kV/us for 99% of measurements; 20 kA ten operations, 25 kA one operation; arc ~10 V. | Current/size-class alternative, but **no DC holdover guarantee is stated** in the retrieved electrical table. Do not infer one from its K.12 terminology or power-supply application label. |
| TDK `B88069X7091S202` / `B88069X7091T502`, `EM470XS` | [G11], version 04, 2026-04-01. 400..588 V DC; 700 V at 1 kV/us for 99% of measurements; arc ~25 V; 2.5 kA ten operations, 5 kA one operation. | Lower front voltage is interesting, but ~25 V is not a guaranteed minimum arc/extinction voltage. No stated DC holdover; not an equivalent five-kA-ten-shot AC tube. |

The current Ruilon `2R470TD-8` manufacturer sheet is SP-GDT-017 A6,
2025-10-16 [G12]. It still gives **no holdover voltage/current/time network**.
It lists ~10 V arc, ~0.5 A glow/arc transition, 20 kA ten operations and 25 kA
one operation. Its general claim of returning to high resistance after an
overvoltage is not the missing powered-recovery specification. The currently
reviewed SMD5050/Bencent limitations remain as recorded in `ELECTRICAL.md`;
this session found no new application guarantee for those exact parts.

### Physical Screens

These are **pre-P3 checkpoint-97e202d comparisons**, not current source hole/land
dimensions, reviewed replacement footprints or actual forming/fit proof.
Subsequent P3 integration changed earth-GDT holes to 1.50, AC holes to 1.40 and
SMT lands to 5.50 x 1.20 at 4.00 centres; ASSEMBLY.md controls the current source.
The older-hole screens below are retained as research provenance and do not
approve any candidate automatically. Image-only details have not been invented.

| Candidate | Published envelope / check | Remaining mechanical evidence |
| :--- | :--- | :--- |
| `2027-47-BLF` | Body diameter 8.0 +/-0.4 mm, length 6.0 +/-0.3 mm; B wire 0.8 +/-0.04 mm. At 9.00 pitch, unplaced maximum-body gap is **0.60 mm**. Existing 1.20 hole can finish at 1.12: `1.12 - 0.84 = 0.28 mm` diametral allowance. | Subtract centre/forming errors from that 0.60, do not claim a 1 mm gap. Preserve earth separation, lead anchorage and enclosure access. C wire 1.0 +/-0.04 leaves only 0.08 mm and fails the current 0.10 mm allowance rule. |
| `2035-47-BLF` | Current drawing: body diameter <=5.30 mm, length <=4.50 mm; wire <=0.88 mm. `1.12 - 0.88 = 0.24 mm`. Body fits inside the baseline Bencent 5.70 x 6.20 envelope. | Still form north-south at 15.24 pitch, with >=2 mm under the entire raised span. Obtain bend/seal limits, height tolerance and PCN/lot applicability. |
| `2057-47-BLF` | Diameter <=5.80 mm, length <=6.30 mm; wire <=0.85 mm. `1.12 - 0.85 = 0.27 mm`. | Not inside the present 5.70 x 6.20 Bencent envelope; requires honest courtyard/access review. |
| `SH470` | Published body dimensions include 5.0 +/-0.2 mm and height 4.2 +/-0.3 mm. Recommended land figure gives 6.0, 3.7, 0.8 mm dimensions [G7]. | Same body class does not approve the existing 5.20 x 2.00 lands. Decode the original pattern and approve the alternative or redesign without disturbing protected rails/vias. |
| `GDT25-47-S1-RP` | Drawing includes electrode/body outside diameter 5.40 +/-0.20 mm and axial 4.19 +/-0.30 mm [G2]. | Use the actual IPC-7351 pattern, not a generic 5 x 5 label. Recheck both SMT bodies, AC body and mask/via separation together. |
| `CG2470L` | Axial drawing states 8.10 mm maximum body diameter and 6.07 +/-0.15 mm length; wire 0.81 mm is **typical** [G6]. | 0.90 mm nominal maximum-body gap at 9 mm pitch is promising. Maximum finished wire is not established by that typical value. Too wide for the current AC envelope. |
| `2038-47-SM-RPLF` | Three-terminal body 7.5 +/-0.26 mm long, 5.0 +/-0.3 mm diameter [G8]. | Wrong electrode count and land pattern; not a leaded AC bridge. |

**Same-MPN change:** Bourns PCN **GDT2615**, issued 2026-07-10, changes
`2035` manufacturing/design/materials starting **2027-01-04**, first code
**2701**, without changing the MPN [G4]. Listed changes include DC tolerance,
impulse limits, arc voltage, wire tolerance and packing. For `2035-47`, the
new impulse entries are 900/1100 V at 100/1000 V/us, replacing typical
750/950 V entries. New arc voltage is ~15 V rather than ~10 V. Obtain the
applicable delivered drawing and full holdover table; do not combine the most
favorable entries across generations. Old and new inventory may coexist.

## 4. DC-Power And MOV Alternatives

### Stacked GDT Circuit

TDK `LN8-A1200DC-4` / **`B88069X1993B501`**, version 05,
2019-07-25 [P1], explicitly specifies:

- 48 V +/-20% DC operating voltage, footnoted **DC current source 30 A**.
- 20 kA 8/20 us ten operations and 4 kA 10/350 us ten operations.
- With its three grading capacitors, front voltage <850 V initial and
  <1600 V after service life under the specified 6 kV, 1.2/50 us test.
- Without those capacitors: <2000 V initial, <3300 V after life. They are
  not optional if relying on the lower front-voltage figures.
- C1-C3 each 100-470 pF; recommended exact capacitor
  **TDK `C4520X7R3D471K130KA`**, connected exactly as its page 3 circuit,
  not an assumed generic grading topology.
- -40..+125 C. Manufacturer product index lists **8.4 x 13.8 x 8.9 mm**
  [P3]; original page 4 maximum tolerances/terminal association still need
  readable drawing review.

The concrete alternative netlist is six independent cells:

```text
AB: A -- [LN8-A1200DC-4 + its C1/C2/C3 network] -- B
BC: B -- [LN8-A1200DC-4 + its C1/C2/C3 network] -- C
AC: A -- [LN8-A1200DC-4 + its C1/C2/C3 network] -- C
AE: A -- [LN8-A1200DC-4 + its C1/C2/C3 network] -- EARTH
BE: B -- [LN8-A1200DC-4 + its C1/C2/C3 network] -- EARTH
CE: C -- [LN8-A1200DC-4 + its C1/C2/C3 network] -- EARTH
```

This has six stacks and eighteen capacitors per board. Remove each original
bare parallel path in this proposed circuit. No grading node goes to PE/B
unless that exact cell drawing calls for the cell's own terminal connection.
The bare stack's <1 pF entry must not be assigned to the populated capacitor
network; assess its complete RUN loading.

**A 37 V, <=1.6 A source is a credible conservative DC design basis against
57.6 V / 30 A, not a reason to reject the family pending field lightning tests.**
Recovery with cable L/C and damaged-device containment remain type-test/FMEA
work. The rating does not guarantee arbitrary stored energy or a failed stack.

Mechanical integration is the immediate design limitation. The part is SMD,
not a 15.24-pitch axial tube. An 8.4 mm dimension at 9 mm earth centres leaves
only 0.6 mm before tolerances, while the AB/BC centres are only 7.62 mm apart.
All six cannot simply occupy the existing footprints/orientations. A reviewed
carrier/formed-terminal arrangement, possibly using height, might preserve
the protected main-board copper and AC orientation, but **none is designed or
fit-proven here**. Do not authorize pad moves, rail/via changes or a silently
raised/reoriented assembly from this observation.

TDK **`B88069X2863T152` / `LN8A-A800DC-5`**, version 05,
2017-04-11 [P2], is another genuine power-DC candidate: 48 V nominal,
**60 V maximum at a 30 A DC source**, four grading capacitors, <900 V initial /
<1500 V after-life front voltage with them. Its listed envelope is
8.4 x 16.3 x 8.9 mm [P3], larger than the four-stack option. It is not a
470 V drop-in. Bourns' 04/25 exposed-DC application note likewise uses a
stacked `2033-80-G5-LF`, coordinating inductors and PTVS, not a claim that
ordinary 135 V telecom holdover solves a stiff DC power rail [P4].

### Series GDT/MOV Circuit

A non-latching MOV in **series** with every GDT is a valid alternative
mechanism. After the surge, the MOV must support the full permitted source
voltage at a bounded small current, even if the GDT is still conducting.
This avoids depending entirely on an unknown arc holding current.

**Bourns `GMOV-14D500K`** [M1], rev. 01/25, is a supported AC/DC hybrid:
65 VDC MCOV, <1 uA leakage at MCOV, 4 pF maximum, MOV 82 V +/-10% at 1 mA,
230 V nominal internal GDT. Front protection 800 V under its specified test;
150 V clamp entry is typical. It is **not thermally disconnected by an
explicit built-in TCO specification** in the retrieved datasheet.

Its maximum diameter/height are 16.5/20.0 mm, maximum combined thickness
8.0 mm and lead pitch 7.5 +/-1.0 mm. Those dimensions require an explicit
3-D placement/forming solution, not a blanket claim that 9 mm earth centres
either prove fit or make every possible upright arrangement impossible.
No acceptable six-path layout preserving the AC bridge is demonstrated here.

For a smaller discrete experiment, **`MOV-07D101K`** [M2], rev. 07/25,
has 85 VDC MCOV, 90 V minimum at 1 mA, 165 V maximum clamp at 10 A,
and a 9.0 mm maximum diameter / 3.6 mm maximum thickness. Under a monotone
25 C DC I/V interpretation, any applied voltage <=37 V is below its 1 mA
point. Even a conservative 1 mA branch would draw <=37 mW total from the
source. This is useful bounded reasoning, not a full-temperature/post-damage
leakage guarantee or a recovered-insulation claim.

That small part only has **1.2 kA one-shot 8/20 us capability and 6.5 J**.
`MOV-14D101K` [M3] increases this to 4.5 kA one-shot / 28 J, but again has a
16.5 mm maximum diameter. Neither is an equivalent 20 kA earth-path solution.
Do not reduce the surge design scope implicitly just to fit a small MOV.

For any series approach, handle these cases explicitly:

- GDT short, MOV healthy: MOV carries the DC stand-off duty continuously.
- MOV short, GDT healthy/ignited: the original bare-GDT recovery problem returns.
- Both damaged or MOV resistive: local heat may persist below hub overcurrent.
- MOV open or thermal disconnect open: the surge path is lost and needs a
  detectable service/replacement disposition.
- A MOV only in the external EARTH lead does **not** fix a local
  `A -> GDT_A_E -> floating EARTH -> GDT_B_E -> B` path. It bypasses that MOV.
- A new hybrid in parallel with an old bare tube does not solve follow current.

## 5. Proposed Single-Source Hub

This is an implementable **source-interface design proposal**, not a finished
hub schematic. It does not turn a remote resistive fault into an overcurrent.

```text
one LRS-75-36 -> existing 2 A fuse -> protected current-limiting interface
             -> normally-open two-pole DC isolation -> TEST source contacts
                                                      + -> Start A and C
                                                      - -> Start B

independent output-OV detector + armed interface FAULT + source/control loss
             -> master latched OFF -> semiconductor SHDN and isolation release
manual reset allowed only in stable TEST with a valid source and no fault
PE and the six mode-switch field-end isolation rules remain unchanged
```

The LRS-75 specification [H1], 2025-04-07, is 36 V / 2.1 A / 75.6 W;
32.4-39.6 V adjustment; 110-150% **rated power** overload, hiccup/recovery;
41.4-48.6 V OVP shutdown. There is no published output-capacitance or precise
hiccup-current/time guarantee here. Its OVP is not a 37 V limiter.

**Proposed normal envelope:** nominal 36 V at the TEST feed, **37.0 V maximum
in normal operation, including allowed ripple**, after the interface. Use a
tamper-controlled PSU adjustment and an independent cutoff. Source-fault/transient
overshoot needs a separate
voltage/time limit; an OV comparator is not an instantaneous voltage clamp.

Using the existing declared resistor corner, not a measured temperature:

```text
R_min = 2200 * 0.99 * (1 - 50e-6 * (125 - 20)) = 2166.5655 ohm
I_branch <= 37 / R_min                          = 17.0777 mA
P_R      <= 37^2 / R_min                        = 0.631876 W
I_82     <= 82 * 37 / R_min                     = 1.400373 A
P_82     <= 37 * I_82                           = 51.8138 W
```

This is below the resistor's 0.65 W standard-mode P70, but with little margin:
the standard derating equation permits only about **71.53 C local ambient**
at this power, subject to the specified heat-flow/film-temperature conditions.
It is not a potted-temperature pass. Normal TEST can be continuous only in
the accepted thermal envelope, not because a timer eventually turns it off.

### Candidate Source Parts And Behavior

- **TI `TPS26600PWPR`** [H2], SLVSDG2G, December 2019: back-to-back FET eFuse,
  4.2-60 V operation, **62 V absolute maximum**, reverse-current blocking,
  programmable current limit/OVP. `R_ILIM = 8.00 kohm` has a specified
  1.425/1.500/1.575 A min/typ/max limit at the table's conditions. A 0.1%
  resistor alone widens those to about 1.4236..1.5766 A; allow for TCR and
  the complete input/drop/temperature envelope before asserting **<=1.60 A**.
- Use active limiting with **402 kohm MODE-to-RTN** for thermal latch behavior,
  plus the external master latch. This MODE setting alone waits for internal
  thermal shutdown; it is **not a guaranteed short fault-duration cutoff**.
  `FLT` reports overload/UV/OV/reverse/thermal events, but is also asserted
  during startup. Use an explicit startup/armed state, not `FLT` directly
  wired into a reset-inhibiting deadlock or an indefinitely masked fault.
- `TPS26601PWPR` offers circuit-breaker latch mode with MODE open; that is a
  different fault response, not proof of the active-limit waveform above.
  `TPS26602`'s nominal 38 V clamp has a **36..40 V** specification and is not
  a 37 V enforcement solution.
- A concrete precision-OV starting point is **TI `REF5025ID`** (high grade,
  not `REF5025AID`) plus **`TLV1701AIDBVR`**, powered from a protected local
  low-voltage rail, with a 136.8 kohm / 10.0 kohm sense divider. Nominal trip
  is `2.5 * (1 + 136.8/10) = 36.70 V`. [H3, H4] provide high-grade reference
  initial +/-0.05%, 3 ppm/C full-range box drift, and comparator offset
  +/-5.5 mV / bias <=20 nA over -40..+125 C. With total divider-resistor
  errors bounded to +/-0.1% each, the first static screen is about
  **36.51..36.89 V**, before noise, aging, assembly shift and dynamic errors.
  This shows a feasible precision threshold budget, not a completed guarantee.
- **TI `TPS3762D02OVDDFR`** [H5], SNVSCM8A, December 2023, is an integrated
  65 V, adjustable 0.8 V, +/-0.9% OV detector with latch, but has a wider
  threshold budget. Its default no-cap detection entry is **100 us maximum
  at 20% overdrive**, not the family's headline <5 us option. Include sense
  leakage and the exact variant; do not use headline timing as a guaranteed
  cutoff at an infinitesimal overvoltage.

Power auxiliary circuitry upstream of the perimeter current limiter where
appropriate, but include it in the one PSU's power/thermal budget. The 8 kohm
choice leaves only about 23 mA above the extreme 1.4004 A branch bound at its
lower specified corner. Recalculate after the final C4 circuit; do not silently
raise the current limit or attach an auxiliary load exceeding this margin.
Shunt/divider current already flowing through the existing 2.2 kohm branch
resistance is inside the zero-forward-drop bound, not an extra current to add
twice. New bypass paths or changed branch resistance require a new bound.
Neither PSU hiccup recovery nor restoration of control power may self-arm the
master latch; a deliberate reset is required.

**Still to engineer before this hub is an accepted protective assembly:**
complete master latch/POR/startup/reset circuitry, DC-rated isolation hardware
and drive, current-limit behavior at actual voltage and all relevant FET drops,
guaranteed fault-duration/energy budget, transient clamp/coordinating network
at both eFuse ports, and independent semiconductor-short failure isolation.
TI timing entries such as 250 ns fast trip and 875 us flag deglitch are not a
complete maximum fence-disconnect time. No relay or external clamp MPN is
claimed approved by this note.

The eFuse's 62 V absolute limit is particularly important: a 470 V GDT upstream
does **not** protect it by itself. Do not connect the proposed electronics to
an exposed perimeter, or apply surge testing, before its front end is designed.
The existing fuse remains backup wiring protection subject to interruption
review, not the detector of a 0.98 A arc circuit.

## 6. Failure Coverage And Prototype Boundary

### Every Return Path

| Case | Required disposition |
| :--- | :--- |
| AB and BC direct paths | Each must recover at the maximum source/cable envelope or be locally interrupted/contained. Nominal equality does not let one channel stand in for asymmetric faults. |
| AC direct path | Healthy symmetric TEST has no driven AC voltage, but asymmetry, a cut, or other fired/shorted tubes can change this. A failed short can mask a clean cut. Keep the protection and diagnostic failure case. |
| One core/EARTH tube with no conductive return | No sustained current in the ideal floating DC model; not proof of zero common-mode voltage, no capacitive discharge, or real-site isolation. |
| Two core/EARTH tubes at one unwired standard board | The local floating EARTH bus still completes a differential path. Include AB, BC and AC combinations. |
| Tubes at different earth-connected stations | Include every source/return pair, both polarities, actual earth-path impedance and one tube already failed short. No DC-negative/PE bond is required for this loop. |
| Simultaneous differential/earth paths | Do not assume equal current or equal voltage division. A failed-short member may leave one surviving member exposed to the full source recovery voltage. |
| External earth rise / repetitive induced pulse | Separate external energy source, not bounded by `37 V * source current`. Requires site/surge qualification. |

### Benign Short Is Not Resistive Failure

With an **actually enforced** 1.60 A ceiling, a stable failed-short device and
its relevant connections totaling <=0.10 ohm dissipate at most **0.256 W**.
That is a realistic continuous thermal qualification case. It need not be
disconnected solely to obtain the words "every fault latches" if it is otherwise
electrically and thermally benign. The short resistance is an acceptance
criterion, **not a guaranteed failure mode of any candidate above**.

An intermediate-resistance failure is a different case. The original model's
100 ohm near-source fault dissipates **12.745 W** at only **1.197 A total**.
The new 37 V/R-min/zero-drop screen still has 100 ohm near-source dissipation
**13.448 W at 1.313 A total**, below the proposed limiter's lower threshold.
The far-end 2.6 W arc is likewise not an arbitrary infinitesimal fault.
**These must not be classified as benign or covered by the hub latch.**

For field release, choose and implement one of the following actual safeguards
for the identified potentially hazardous local failures: a qualified thermally released opening
path in each surge branch, a guaranteed low-resistance fail-short mechanism
with safe continuous current/temperature and diagnostic disposition, or
complete local fault sensing that releases the source. None of those mechanisms
is yet established for these six footprints. This is an irreducible design
item, not something an unpowered impulse-current rating closes.

Two investigated shortcuts do not supply it:

- **Bourns `SE77AAA`** [F1], rev. 09/25, is genuinely rated 48 VDC / 5 A
  and 54 V maximum, with 77 +/-5 C trip and <=5 milliohm closed resistance.
  However its self-holding PTC permits **200 mA maximum leakage** after opening,
  it has no specified kA surge endurance, and the manufacturer prohibits the
  cited wet/condensing/salt/direct-outdoor exposures without an appropriate
  protected application. It is not an isolating, surge-rated GDT thermal fuse.
- **Littelfuse `TMOV14RP115E`** [F2], rev. GD. 10/15/25, has an integrated
  thermal element for UL1449 abnormal-overvoltage limited-current conditions.
  It starts at 150 VDC MCOV in the retrieved family table, and its package is
  up to 17 mm diameter / 9 mm thickness. The data explicitly allows heating,
  arcing and venting before opening and requires enclosure containment. It
  does not prove safe interruption of this 36 V damaged-GDT circuit, or fit
  at the existing six positions.

A TCO in the PE conductor is forbidden. A TCO in a GDT **branch** is not PE
switching, but it must survive the entire specified surge, interrupt DC safely,
leave an adequate open gap, and be thermally coupled to the actual fault.
Do not specify it from normal 5 A/250 VAC data alone.

### Detection Limits

A source-only fixed threshold cannot distinguish overlapping healthy and fault
loads. A source-end AC short can even carry zero current when A and C are
equipotential. As fault conductance tends to zero, its terminal signature can
fall below load/tolerance/noise uncertainty. Universal identification of every
nonzero fault, with no false trips, is not a supportable hub-only requirement.

That limitation does **not** make useful safety engineering impossible. Define
which failures can overheat real materials, prove benign temperature below that
boundary, and detect/interrupt the rest. Do not invent a universal minimum
fault current or assume a healthy startup baseline in a cable being tested
precisely because it may be damaged. Nor does a remote GDT's thermal disconnect
protect an unrelated resistive fault in the cable insulation.

### What A Controlled Prototype Can Do Now

The compact candidate circuit is supportable as an **instrumented evaluation
design**, not as an unattended, powered-fault-qualified field installation.
For GDT/failed-part evaluation, the laboratory fixture must independently
monitor the actual tested branch voltage/current and local temperature, contain
the credible failure, and interrupt the source on the predeclared fault energy
or thermal limit. It must not rely on the DUT's hub total-current detector to
detect the fault under investigation.

For powered surge-recovery characterization, the known test trigger can arm
an independent energy-limited abort while observing whether the tube recovers
first. That is a **fault-test safeguard**, not a timer on healthy TEST. A failed
recovery remains a failed result, followed by latched source removal; no repeated
automatic attempts to make it pass. Define those fixture ratings and limits
before energizing, not after observing damage.

Isolated component/hub tests can precede assembled-board and field tests.
Ordering a bounded prototype does not require a completed lightning/site
qualification, but does require an honest safety scope, resolved known fit/
process defects, and the correct circuit populated. This note requests no order.

## 7. Cable And Source Energy Bounds

Missing cable C/L need not stop an initial bounded design. Declare conservative
fixture maxima and verify that the real system is inside them later. Do not
invent Oceanflex guarantees or equate a capacitance measurement at one port
with the full three-core/earth energy matrix.

For **source-only differential** initial conditions, an illustrative bound is:

```text
V_max             = 37 V
C_cable_equiv_max = 10 uF             # declared bound, not cable data
C_downstream_max  = 100 uF            # all hub/load C after the limiter
L_energy_equiv_max= 10 mH             # declared bound, not cable data
I_max             = 1.60 A

E_cable <= 0.5 * 10e-6  * 37^2       =  6.845 mJ
E_hub   <= 0.5 * 100e-6 * 37^2       = 68.450 mJ
E_L     <= 0.5 * 10e-3  * 1.60^2     = 12.800 mJ
E_0                                      88.095 mJ
```

This makes the normal stored-energy scale explicit. It is not an inherently
safe energy threshold or a proved substitute for the standard RC network.
For multiple conductors use `E_C = 0.5 * v^T C v` and `E_L = 0.5 * i^T L i`,
or a demonstrably conservative equivalent including coupling and initial state.
Common-mode energy must include the actual core/earth voltages, not assume
each is bounded by the source's 37 V differential output.

Capacitance upstream of an operating limiter is not all an instantaneous
unlimited downstream reservoir. Include the limiter's response overshoot and
`integral(v*i*dt)` during conduction. In its shorted-failure case, include that
upstream capacitance until the independent disconnect actually opens.

After a detected event, if source delivery really ends within time `t_off`:

```text
E_delivered <= E_0 + 37 * 1.60 * t_off + separately bounded response overshoot
```

At an illustrative 150 ms this is **8.968 J** before overshoot. This is a
total-network conservative bound, **not** an accepted GDT safe energy or a
guaranteed implementation delay. A nominal 10 V / 0.259543 A path lasting
150 ms would dissipate about **0.390 J** in the model. Choose the actual cutoff
from accepted part/assembly limits; the standard's 150 ms is not a universal
safe timeout.

Do not apply the 37 V capacitor estimate to a surge-charged cable: the same
10 uF at 1100 V stores **6.05 J**, at 1600 V **12.8 J**, and at 3300 V
**54.45 J**. Actual distributed charging, source impedance, waveform and
post-event state must be bounded. Source shutdown removes continued source
energy, not energy already induced into a floating island. A qualified fixture
must verify discharge before access or reset.

Thus conservative C/L bounds can support a controlled prototype and the
DC-rated stack comparison. They cannot establish safety of an **unbounded
duration** bare arc: a finite initial energy says nothing sufficient about
steady 2.6 W heating. Total dissipated energy grows with time, but temperature
depends on heat rejection; a separately demonstrated benign steady thermal
state is another valid disposition, not ruled out by energy arithmetic alone.

## 8. Quantities And Remaining Evidence

Quantities below are engineering population counts, not orders, allocations or
assembler attrition allowances. The 36 standard boards retain their earth
tubes. Alternatives are mutually exclusive, not additive.

| Item / Architecture | Per board | Five prototypes | 41 field boards | Unique prototype + field requirement |
| :--- | ---: | ---: | ---: | :--- |
| Compact: `GDT25-47-S1-RP` AB/BC | 2 | 10 | 82 | 84..92 |
| Compact: `2035-47-BLF` AC | 1 | 5 | 41 | 42..46 |
| Compact: `2027-47-BLF` core/EARTH | 3 | 15 | 123 | 126..138 |
| Stack alternative: `B88069X1993B501` | 6 | 30 | 246 | 252..276 |
| Stack alternative: `C4520X7R3D471K130KA` | 18 | 90 | 738 | 756..828 |
| One-source hub: `LRS-75-36` | Not per board | One TEST source | One TEST source | **2 ordered: one TEST, one disconnected spare** |
| Hub evaluation: `TPS26600PWPR`, `REF5025ID`, `TLV1701AIDBVR` | Not per board | 1 each per proposed hub | 1 each per proposed hub | Hub reuse/spares not allocated |

Unique-board range is **42..46**, assuming no extra process/spare samples:
one of the five prototypes is retained unpotted, so at most four can be reused
in the field after qualification. If none is reusable, all five are additional
to the 41 field units. Destructive tests and assembler minimums may require
more; there is no justified all-inclusive procurement maximum yet.

### Design Evidence Before Freeze

1. Choose compact powered-type-test route versus the power-rated stacked route;
   confirm actual MPN/lot specifications. For compact tubes, obtain application
   extinction bounds or establish them through controlled type tests over the
   declared source/cable envelope, including post-stress behavior. For the
   stack, inspect the exact test circuit and grading-node diagram and bound
   the application's additional stored energy.
2. Provide a real six-path fit/land/forming design that retains the guardrails.
   The nominal envelope screens are not authority to alter protected copper or
   substitute an unreviewed carrier. The stacked alternative has a concrete
   electrical basis but an unresolved packaging design.
3. Complete the source interface: component-level threshold and transient
   budget, current/energy cap, fault latch and loss-of-power behavior, DC
   isolation hardware, and semiconductor-short failure response.
4. Disposition **hazardous resistive failures**, not just ideal short circuits.
   Local protection must have actual MPN/process evidence or a qualified benign
   failure envelope. No universal minimum fault current is substituted for this.
5. Integrate the independent C4 LED/pulse solution and repeat the normal-load,
   one-way-rung observability, RF-loading and source-margin analysis. This
   record does not select or approve that separate circuit.

### Tests That May Follow A Bounded Prototype Order

- Actual forming/insertion/workmanship and enclosure dry fit after the design
  and supplier process have been accepted.
- Powered GDT recovery on the declared source/cable-equivalent networks,
  fault energy/disconnection, failed-short and intermediate-resistance thermal
  tests with independent fixture containment.
- Continuous normal/reversal/output-short potted thermal testing, with solar/
  internal-temperature bounds and the accepted resistor mode.
- Complete-path surge/RF/switching recovery, cable dielectric/impulse,
  environmental and site/earthing qualification before field reliance. Inspect
  and maintain the whole-boundary cattle-fence prohibition; reassess if violated
  or a future land-use change reintroduces that exposure.

These are not performed. Manufacturer component ratings and a few basic board
passes do not establish a 20 kA assembly, equal surge sharing or field approval.

## 9. Primary Source Register

Retrieved 2026-09-07 using native `webfetch`. Direct PDFs sometimes returned
binary; their manufacturer-hosted contents were read through
`https://r.jina.ai/https://...` using the same tool. This is a text-extraction
aid, not independent evidence, an archived original PDF, or proof of unreadable
figures. Revision dates below are document dates, not HTTP modification dates.
No manufacturer was contacted and no supplier acceptance was obtained.

- **N1:** [ITU-T K.12 edition 9.0, 05/2010](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-K.12-201005-S!!PDF-E&type=items), sections 3.5, 6.5, 7.5 and Annex A. Original standard, now superseded, explicitly referenced by GDT25.
- **N2:** [ITU-T K.12 edition 10.0, 08/2024](https://www.itu.int/rec/dologin_pub.asp?lang=e&id=T-REC-K.12-202408-I!!PDF-E&type=items), sections 3.2.5, 7.5 and 8.5. Same tabulated holdover network values.
- **G1:** [Bourns 2027](https://www.bourns.com/docs/product-datasheets/2027.pdf), rev. E 01/26, pp. 1-2.
- **G2:** [Bourns GDT25](https://www.bourns.com/docs/product-datasheets/GDT25.pdf), rev. D 06/23, pp. 1-3, especially electrical footnotes 2, 5, 8 and 9.
- **G3:** [Bourns 2035/2037](https://www.bourns.com/docs/product-datasheets/203537.pdf), rev. 02/26, pp. 1-3.
- **G4:** [Bourns PCN GDT2615](https://www.bourns.com/docs/technical-documents/product-change-notifications/Bourns_GDT2615_2035_PCN.pdf), issued 2026-07-10, all three pages; implementation code 2701.
- **G5:** [Bourns 2057](https://www.bourns.com/docs/product-datasheets/2057.pdf), rev. B 09/19, pp. 1-2.
- **G6:** [Littelfuse CG/CG2 datasheet](https://www.littelfuse.com/assetdocs/gas-discharge-tubes-cgcg2-sn-datasheet?assetguid=6852d716-4efb-4b8b-9661-3d8e474ee7a0), rev. 12/12/17, pp. 2-3 and 6; [active CG2470L page](https://www.littelfuse.com/products/overvoltage-protection/gas-discharge-tubes/medium-to-high-surge/cg-cg2/cg2470l) has the conflicting 150 V holdover field.
- **G7:** [Littelfuse SH](https://www.littelfuse.com/~/media/electronics/datasheets/gas_discharge_tubes/littelfuse_gdt_sh_datasheet.pdf.pdf), rev. GD. 03/09/21, pp. 2-4.
- **G8:** [Bourns 2038 SMT](https://www.bourns.com/docs/product-datasheets/2038-xx-SM.pdf), rev. P 01/26, pp. 1-3.
- **G9:** [Littelfuse GDT Product Catalog and Design Guide](https://www.littelfuse.com/assetdocs/gas-discharge-tubes-catalog?assetguid=c1597a5f-aedf-4ea0-8ca3-d2eadd0de6a5), rev. 12/12/17; SL1011/SL1411 and SL1021 sections and holdover definition. Use newer exact-part data where available.
- **G10:** [TDK A81-A470X](https://www.tdk-electronics.tdk.com/inf/100/ds/A81-A470X-X6441xxxx.pdf), version 03, 2026-04-01, pp. 2-3.
- **G11:** [TDK EM470XS](https://www.tdk-electronics.tdk.com/inf/100/ds/EM470XS-X7091xxxx.pdf), version 04, 2026-04-01, pp. 2-3. Served via public manufacturer product index; extraction includes template/internal-use markings. Confirm delivered specification before selection.
- **G12:** [Ruilon 2RD-8](https://www.ruilon.com.cn/Uploads/pdf/017-2rd-8%20series_a6.pdf), SP-GDT-017 A6, 2025-10-16, pp. 4 and 11. Do not merge it silently with the earlier allocated-part drawing.
- **P1:** [TDK LN8-A1200DC-4](https://www.tdk-electronics.tdk.com/inf/100/ds/LN8-A1200DC-4-X1993B501.pdf), version 05, 2019-07-25, pp. 2-5, especially the 30 A footnote and capacitor-dependent front voltage.
- **P2:** [TDK LN8A-A800DC-5](https://www.tdk-electronics.tdk.com/inf/100/ds/LN8A-A800DC-5-X2863T152.pdf), version 05, 2017-04-11, pp. 2-5.
- **P3:** [TDK surge-arrester product/datasheet index](https://www.tdk-electronics.tdk.com/en/529996/products/product-catalog/protection-devices/voltage-protection/surge-arresters); [Product Profile 2025](https://www.tdk-electronics.tdk.com/download/174146/2f5abeca101a09c264a07fd6ede44414/surge-arresters-pp.pdf), edition 01/25, pp. 9-12 and 63-64. Individual type drawings take precedence over the overview's generic dimensions.
- **P4:** [Bourns exposed DC power supply application note](https://www.bourns.com/docs/technical-documents/technical-library/gas-discharge-tubes/application-notes/bourns_surge_protection_for_exposed_dc_power_supplies_application_note.pdf), 04/25, e/K2525, pp. 2-3.
- **M1:** [Bourns GMOV](https://www.bourns.com/docs/product-datasheets/GMOV.pdf), rev. 01/25, pp. 1-3.
- **M2:** [Bourns MOV-07D](https://www.bourns.com/docs/product-datasheets/MOV07D.pdf), rev. 07/25, pp. 1-2.
- **M3:** [Bourns MOV-14D](https://www.bourns.com/docs/product-datasheets/MOV14D.pdf), rev. 07/25, pp. 1-2.
- **H1:** [MEAN WELL LRS-75](https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF), file revision 2025-04-07, pp. 2-3.
- **H2:** [TI TPS2660](https://www.ti.com/document-viewer/TPS2660/datasheet), SLVSDG2G, December 2019, sections 5, 7.5-7.6, 9.3.5.1.1, 9.3.5.3 and 11.1.
- **H3:** [TI REF50](https://www.ti.com/document-viewer/REF50/datasheet), SBOS410O, October 2025, section 6.5. High-grade `REF5025I` and standard-grade `REF5025AI` are different specifications.
- **H4:** [TI TLV1701/2/4](https://www.ti.com/lit/ds/symlink/tlv1701.pdf), SBOS589D, June 2015, sections 7.6-7.7. Delay values retrieved are typical, not a guaranteed complete shutdown delay.
- **H5:** [TI TPS3762](https://www.ti.com/lit/ds/symlink/tps3762.pdf), SNVSCM8A, December 2023, sections 6.5-6.7, 7.3.3.3 and 8.2-8.3.
- **F1:** [Bourns SE thermal cutoff](https://www.bourns.com/docs/product-datasheets/se.pdf), rev. 09/25, ratings, application/environment and design-caution sections.
- **F2:** [Littelfuse TMOV/iTMOV](https://www.littelfuse.com/~/media/electronics/datasheets/varistors/littelfuse_varistor_tmov_itmov_datasheet.pdf.pdf), rev. GD. 10/15/25, pp. 1-3 and dimensional table.

## 10. Work Performed

Read AGENTS, all of REMEDIATION including the handoff, ELECTRICAL, and the
relevant assembly/population records. Starting tracked worktree was clean at
`97e202d`. Other workstreams subsequently added `pcb/ENVIRONMENT_EVIDENCE.md`
and `pcb/DFM_EVIDENCE.md`; neither was edited by this work.

One read-only DC study was run against the unchanged persistent script:

```bash
python3 -B scripts/analyze_limits.py --voltage 37 --resistor-error -0.01 -0.01 --resistor-temp 125 --tcr-ppm -50 -50 --led-v 0 0 --diode-v 0 0
```

It exited 0, computed the 37 V bounds above, and passed all **280 clean-cut
cases** for those declared model inputs. Its separately labelled historical
maximum-adjustment scenario remains 40.39597 V / 0.753190 W; the CLI voltage
option does not replace that built-in scenario. Its fault results remain
prospective CV calculations, not actual LRS waveforms or GDT extinction tests.
Output was to the session only; no build/staging or design files were changed.

`git diff --no-index --check /dev/null pcb/SOURCE_PROTECTION_RESEARCH.md`
passed for the added note; this is a whitespace check, not electrical validation.

No KiCad/build/manufacturing command, hardware test, upload, order, commit,
approval-hash refresh or release-hold modification was performed. The optional
research note is the only intended repository edit from this work.
