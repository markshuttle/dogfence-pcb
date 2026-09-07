# Prototype and Field Acceptance

**Draft revision: 1.2.0-dev. Test requirements, not test results or release approval.**

This protocol separates basic acceptance of **five fully assembled prototypes** from qualification of the **41-station, 0-4000 m installation with 82 APEM indicators**. There are 40 spans, five earth-connected stations and 36 standard stations. Five basic bench passes do not authorize a perimeter production order, prove a board surge rating, or release the fence for animal containment.

[REMEDIATION.md](REMEDIATION.md) contains the authoritative requirements, live evidence checklist and [release gates](REMEDIATION.md#release-gates). **The current source has no selected new LED reversal/pulse protection or coordinated source/GDT shutdown circuit.** [pcb/ELECTRICAL.md](pcb/ELECTRICAL.md) records analysis and candidates, not a released design. The series diode does not guarantee LED reversal safety. Documentation does not close C4 or C5, and passing file checks or the forward-current model does not close hardware/site qualification.

Use [INSTALL.md](INSTALL.md) for isolation, wiring and operation, and [RISKS.md](RISKS.md) for fault and environmental limitations. All steps below require recorded evidence; an unperformed or inconclusive test is **NOT RUN / HELD**, not PASS.

## Release Boundaries

| Gate | Evidence needed before release | Status in this draft |
| :--- | :--- | :--- |
| **A: File ready** | Correct hub/circuit design; consistent source, libraries, rules and revision; passing automated checks; regenerated/reviewed manufacturing and assembly data; synchronized documentation and explicit qualification limits. | **Held by unresolved protection, continuous-duty and part/land-pattern decisions**, even when automated file checks pass. See `pcb/verification.json`. |
| **B: Prototype order** | Gate A plus exact part/fit, placement, forming, solder/via process and CAM acceptance, and an approved, safely bounded prototype test programme. Known manufacturing defects cannot be deferred silently to the prototypes. | **Held wherever supplier/process evidence or controlled scope is missing.** B can precede defined physical qualification, but does not authorize field reliance. |
| **C: Field release** | Required normal, reversal, duty/thermal, visibility, full-hub, RF/site, fault/surge and material evidence; accepted earthing; documented performance limits. | **Held pending genuine qualification.** C4/C5 and environmental/protection claims cannot be closed by wording changes. |

The live checklist, not this table, records subsequent evidence-backed closures. `1.2.0-dev` identifies a draft target; record the actual board marking and source/artifact hashes rather than relabelling older hardware as a tested revision.

## Preconditions

1. Freeze the intended test configuration and record board serial numbers, source revision, schematic/BOM, as-built deviations, native placement/assembly drawing, fabrication manifest and report hashes. The population comes from the final BOM, not the legacy component count. Approve substitutions and rework explicitly; no field soldering is part of the installation plan.
2. Have the electrical reviewer supply **numerical acceptance bands before testing**: source minimum/nominal/maximum including accessible adjustment, tolerance and overshoot; verified cable resistance/temperature range; per-channel current and branch loading; LED forward/reverse limits; power/temperature derating and stop limits; protection trip/recovery behavior; and the intended surge/insulation test envelope. Missing bounds hold the corresponding test. Do not choose limits after seeing the result.
3. Confirm the actual PSU nameplate and setting. LRS-35-36 is the user's believed purchase; LRS-75-36 is a capacity-margin candidate, not a confirmed purchase. Qualify the actual supply's hiccup/retry behavior with the actual **Littelfuse 0217002.MXP (2 A, 217 series)** and **Phoenix Contact UK 5-HESILED 60 / 3004139** holder and any revised source protection. Published DC interrupting capability is not clearing coordination.
4. Confirm the exact six-end switch program and source-side wiring. **CA10.A362** is only a candidate until the manufacturer confirms the contact development, DC breaking suitability and **global break-before-make** sequence across all six ends, in both directions. A 20 A thermal rating or a static continuity test cannot supply this evidence. Assign physical terminal numbers only in the subsequently accepted hardware drawing.
5. Establish an authorized test area, independent animal containment, emergency shutdown, personnel responsibility and safe source isolation. OFF/TEST disable the RF fence. Follow [INSTALL.md](INSTALL.md#safety-first): isolate transmitter/PSU/backups, discharge and verify de-energization before handling terminals, then disconnect all six field ends. Coordinate nearby energizer isolation before field wiring work; energizer-on measurements belong to the controlled site test. Do not work during storms. Mains/PE and any surge testing require the relevant qualified personnel.
6. Obtain the exact APEM, COMBI, Essentra, cable and MP0100 documents and define the material/fit process. Do not pot the reference sample. Do not deliberately reverse or surge-test an unprotected legacy assembly as an ordinary bench check; hold such work for the approved protection design and controlled test plan.

## Sample Allocation

All five units receive the workmanship, cold-circuit and normal-function checks below. The allocation is **proposed scope, not accomplished coverage**; record changes and sample history before each qualification test.

| Unit | Proposed additional use | Restriction |
| :--- | :--- | :--- |
| Board 1 | **Unpotted reference** with approved parts, measurements and photographs. | Retain unpotted; no intentional fault, reversal-stress, environmental or destructive surge programme. |
| Board 2 | Instrumented protected-reversal tests and unpotted electrical characterization; support nondestructive hub testing. | Use only after the protection architecture and test limits are approved. Record any stress/degradation before reuse. |
| Board 3 | Complete enclosure dry-fit/process qualification, then potted **0 m/source-end** continuous-duty thermal testing. | Fit actual WAGOs, cables, glands, earth conductors and lid indicators; instrument before filling. |
| Board 4 | Complete enclosure dry-fit/process qualification, then potted **4000 m/far-end** duty, visibility and environmental/site work. | Include reduced-voltage conditions and real viewing angles; reuse only if prior tests leave the unit suitable. |
| Board 5 | Full-hub/RF work and controlled source-fault/protection development; potentially destructive tests only when approved. | One unit cannot establish every surge, fault and environmental corner. Record stress order and preserve evidence. |

Five boards are not a 41-station fixture and do not provide independent replicates for every test. Review the required fault/surge polarities, levels, repetitions and destructive sample count with the test laboratory. **Request approval for more boards, indicators and fixture materials when the scope needs them**, rather than sacrificing the reference or inventing five-board coverage. Required deployment quantities and historic purchases remain distinct in [MATERIALS.md](MATERIALS.md).

## Instruments and Evidence

Use calibrated instruments suited to the circuit, location and energy involved. The following are acquisition requirements for the low-voltage programme, not claims about an available meter. Tighten them where the final design's margin requires it; record instrument model/serial, calibration, range, resolution, accuracy specification, offsets and probe loading.

| Measurement | Required capability / method |
| :--- | :--- |
| Steady DC voltage | At least a **0-60 V DC** measurement range covering the verified supply maximum, with appropriate overload/transient and common-mode ratings. Target expanded uncertainty no worse than **0.5% of reading + 0.05 V** for source/rail readings. Resolve the actual LED terminal voltage with **0.05 V or better uncertainty**, or tighter if needed for the 5 V limit. |
| Normal current | Suitable ranges for roughly **0-50 mA per indicator** and **0-3 A source current**, enlarged if the approved source can exceed these ranges. Target uncertainty **1% of reading or better** at each operating point, including offsets and shunt tolerance. Use calibrated low-burden shunts or properly fused current inputs; connect in series while unpowered, never place a current input across a supply. Fault/pulse ranges need separate sizing. |
| Resistance | Low-ohm/Kelvin measurement for PCB bonds, typically **0-1 ohm with at most 0.02 ohm uncertainty**; **0-100 ohms with at most 0.2 ohm uncertainty** for a core baseline; and a suitable resistor range with **0.25% or better uncertainty** for a 1% resistor. Lead/contact compensation is required. A beeper is a connectivity screen, not a precision bond measurement. |
| Leakage / high resistance | Record the meter's actual range, test voltage, input impedance and detection limit. Use a suitably sensitive guarded measurement if a sub-microampere bound is required. **A 0.00 mA display is not proof of zero or sub-microampere leakage**, and `OL` means beyond that instrument's range under those conditions, not infinity. |
| Temperature | Calibrated attached thermocouples/RTDs and an electrically suitable logger, covering at least **-20 to +125 degrees C**, with **2 degrees C or better uncertainty** including attachment effects; tighten for small margins. Measure ambient, internal gel/air and critical parts. Use appropriately isolated sensors. Do not infer part temperature by touching it; uncorrected IR readings on shiny parts are not sufficient. |
| Waveforms / timing | Appropriately rated **differential or isolated** voltage and current acquisition. Select probe bandwidth and sampling to resolve the fastest relevant edge, with at least ten samples across it and a justified probe rise-time/loading budget. Capture peaks, switching transitions, RF, start-up and full PSU hiccup/retry cycles, not just a DMM average. Record trigger, bandwidth, sample rate, time span, clipping checks and raw data. |
| Mechanical / optical | Calipers/gauges adequate for drawing tolerances, a calibrated low-range torque tool for the LED nut, and a measured **5 m** viewing distance. Record actual daylight illuminance, weather, background, sun direction, lens orientation and observer angles; use a light meter with documented range/accuracy suitable for full sun. Photographs alone do not establish ON/OFF visibility. |

These low-voltage ranges **do not authorize high-voltage field or surge measurements**. The qualified lab must select probes, isolation, differential/common-mode voltage, impulse energy and measurement-category ratings for the actual test. Never lift a scope's protective earth or improvise with a grounded scope clip on a floating field core. A mains isolation transformer is not a substitute for rated differential measurement. Keep required source chassis PE intact. Probe resistance/capacitance can alter LED reverse-voltage sharing; include that loading in the method and uncertainty.

Document an expanded uncertainty `U` with its confidence/coverage factor and the complete measurement chain. Apply guard bands: for an upper limit require `measured maximum + U <= limit`; for a lower limit require `measured minimum - U >= limit`. Include component/environmental corner allowances from the analysis separately. Resolution is not accuracy. If uncertainty or uncaptured transients could conceal a violation, mark **HELD**, not PASS.

## All-Five Workmanship

Perform and record these checks on **each** unpowered prototype before stress testing:

1. Match markings, references, MPNs, values, population and orientation to the accepted BOM/drawing. Confirm onsemi identity for baseline 1N4007G parts, and all protection additions actually specified by P2. No assumed approval of alternative indicators or optional upgrades.
2. Verify the **63 x 56 mm** outline and agreed fabrication tolerances, clean depanelized edges, and four **3.2 mm NPTH** mounting holes at nominal board coordinates (101.5, 99.0), (155.5, 99.0), (101.5, 146.0), (155.5, 146.0) mm. Inspect their mechanical clearances. Rails/tooling removal follows the accepted manufacturer's plan; do not assume automatic removal or impose an unquoted outline tolerance.
3. Verify the required two exterior **2 oz / 0.070 mm** copper layers and protected geometry through manufacturing evidence and inspection: full-width 3.2 mm rails, nine rail and five earth stitching vias at **1.0 mm drill / 1.8 mm pad**, intact earth copper and required **at least 3.0 mm fence-to-earth copper separation**. The surface-copper weight is not the barrel-plating thickness. Check accepted processed drill/mask/paste data and solder-wicking controls; a tenting flag or gel is not proof of sealed 1.0 mm vias.
4. Check exact maximum-pin/body drawing and insertion-fit evidence against the actual finished holes, annular rings and courtyards. The baseline diode-hole correction is **1.10 mm finished hole / 2.20 mm pad**; connector-hole selection still needs exact-part tolerance evidence. Do not ream a plated hole, force a component or shrink a courtyard to hide interference. Resolve defects through the assembler/design owner.
5. In the controlled board view, verify `J_IN` opens left, `J_EARTH` right, `J_LED_A` north and `J_LED_C` south. Verify the intentionally mirrored LED connectors both place the anode `+` left and cathode `-` right, consistent with the actual nets/drawing. Verify diode cathode orientation from the final assembly drawing, not just an old footprint name or a remembered pin number.
6. Inspect the controlled forming of **GDT_AC**, including lead geometry and **at least 2.0 mm standoff above the PCB** over Wire B. Check the earth GDTs at **9.00 mm centre pitch** against actual maximum bodies and required assembly clearance; nominal dimensions do not prove a tolerance-free 1 mm body gap. Neither gel nor solder mask excuses contact with the crossing conductor.
7. Inspect SMT seating/wetting, THT joints, shorts, contamination, damaged parts and excessive lead protrusion to the **agreed workmanship class and edition** (for example IPC-A-610 Class 2 when specified in the order). Obtain appropriate assembler evidence for internal barrel fill or hidden defects; an exterior fillet alone does not establish internal fill. Record any inspection requiring additional samples rather than sectioning the reference.

## All-Five Cold Checks

Disconnect external LEDs/loads as the **final circuit's** cold-test procedure requires; unplug all sources. Added clamps and semiconductor branches can change inter-net readings. Do not reuse a blanket requirement that every A/B/C pair must read above 50 or 100 megohms.

- Check intended same-net continuity from each `J_IN` core to its branch/rail test points, and between the three `J_EARTH` positions. Use the final netlist and a documented low-ohm limit with the uncertainty above; investigate unexpected resistance or intermittency. A shared earth net is not an aggregate terminal-current rating.
- Screen unintended shorts and earth leakage in both meter polarities, recording test voltage, range, connected loads and expected semiconductor paths. Compare against the final schematic's predicted behavior. **A DMM-open GDT is not proof of sparkover, discharge capacity or recovery.** Do not use a megger through electronics.
- Check resistor values and diode orientation/forward behavior at the meter's actual test current and temperature. For an unchanged **2.2 kohm, 1%** resistor, the component band is **2178-2222 ohms**, with measurement guard bands applied; account for parallel paths before accepting an in-circuit reading. A diode's forward reading is test-current dependent, and reverse `OL` is not a rated-voltage test.
- For an optional installed-cable baseline, follow [INSTALL.md](INSTALL.md#optional-dmm-checks): disconnect all six ends from hub/PSU/transmitter/backups and measure each **Start-to-End core separately**. Ideal 4 km / 2.5 mm^2 copper is approximately **28 ohms at 20 degrees C**, not zero or the parallel-core resistance. Record actual cable data, temperature and meter uncertainty; separate electronics if they affect the diagnosis.

## All-Five Normal Function

Use two actual **APEM Q10F5SXXSG02E no-resistor indicators** per board. Verify lead polarity before power. The published family maximum is **20 mA forward and 5 V reverse**, subject to the exact part's temperature and pulse conditions. A raw indicator is not a regulated 2 V load.

1. On a guarded, isolated low-voltage bench fixture, connect labelled A and C to the approved TEST positive source and B to **DC negative, not an assumed earth ground**. Connect each LED anode/cathode to its channel's verified `+`/`-` terminals. Set current limiting from the approved per-board normal envelope and fault-stop plan, not an arbitrary 0.5-1 A limit for one board.
2. Energize under the approved procedure and capture start-up as well as steady values. Test at the approved minimum, nominal **36 V**, and maximum supply/local-voltage conditions, including **0 m/source-end and 4000 m/far-end** loading. Record each LED's current and voltage, resistor voltage/power, board input and source current. Derive LED current from resistor drop only if the final branch current balance permits it; protection/bleed current may make them different.
3. Compare results with the final tolerance-aware analysis. Historical nominal forward-only calculations in REMEDIATION are context, not acceptance bands for a modified circuit. Verify the source can supply the actual 41-station network, including any credible negligible-cable commissioning load, without overload cycling. An upgrade's normal capacity margin does not prove fault coordination.
4. Check both channels illuminate as specified. Capture peak LED current/reverse voltage as well as steady readings; apply uncertainty and the exact part's limits. A visual glow is not a current measurement. Normal operation must remain within limits throughout the approved temperature and source range.
5. With power removed between changes, disconnect local tap A, then C, then B independently and verify the final design's expected local responses: A off/C on, A on/C off, and both off respectively. Restore and retest normal function. These are **local branch checks**, not a substitute for the full-hub cut tests below.
6. Record initial measured temperatures and abnormal behavior, but do not call a short bench run a continuous-duty qualification. Quarantine a failing unit and record correction/retest before any later qualification use.

## Protected Reversal

This is a separate engineered test, not a claim of immunity and not an instruction to energize reversed legacy LEDs. **C4 remains held until the actual P2 protection is implemented, reviewed and qualified.** A series 1N4007 does not control all reverse-voltage division; reversing LED flying leads is also different from reversing the supply. A single antiparallel diode at a PCB connector does not by itself cover both errors.

On the allocated instrumented unit, use the approved current-limited fixture, test limits and emergency shutdown. Verify the complete supply/lead-polarity matrix: normal and reversed supply, each with neither LED reversed, A reversed, C reversed, and both reversed. Change wiring only while isolated. Cover the approved minimum/maximum local voltages, temperature/tolerance corners and start-up/turn-off/transient cases. Record indicator behavior according to the actual protection architecture; do not prescribe darkness as evidence of safety.

Measure **directly across the physical LED**, accounting for probe loading, and capture reverse-voltage peaks, forward current, any permitted pulse envelope, protection current/power and temperature. Require the **5 V reverse and 20 mA forward maxima** with applicable derating and guard bands, or any stricter approved limits. A dark LED, a 0.00 mA source display, or subsequent illumination does not establish that it was never overstressed. Stop at the pre-approved safety thresholds, inspect/retest normal operation, and record failures rather than hiding them with corrected wiring. Any topology change must also pass the full-hub observability tests.

## Full-Hub Cuts

Use the **actual approved hub**, including sources/protectors and independently accessible boundary ends. Its functional matrix is:

| Boundary-cable end | RUN | OFF | TEST |
| :--- | :--- | :--- | :--- |
| Start A | Transmitter T1 | Isolated | +36 V |
| Start B | Transmitter T1 | Isolated | DC negative |
| Start C | Transmitter T1 | Isolated | +36 V |
| End A | Transmitter T2 | Isolated | Isolated |
| End B | Transmitter T2 | Isolated | Isolated |
| End C | Transmitter T2 | Isolated | Isolated |

T1/T2 retain the required OEM protector connections. RUN and TEST ties are made only on the appropriate **source-side contacts**; no permanent boundary-side straps. End A/B/C remain **separate and isolated in TEST**. Verify static states with the hub disconnected from the field, and retain manufacturer/dynamic evidence of global break-before-make, source isolation and DC load breaking. Do not infer physical terminal numbering here.

Build a reviewed **41-station** fixture with A, B and C modeled separately over all 40 spans, using actual assemblies or validated electrically equivalent indicator/protection modules. A plain resistor load that loses the final branch's directionality or protection leakage is not automatically equivalent. Validate cable resistance/tolerances and actual nonlinear branch behavior; request additional hardware if needed. A five-board chain or software-only test is not a full-hub hardware pass.

Run and record **all seven clean-cut combinations at each of the 40 spans: 7 x 40 = 280 cases**, including **0-100 m and 3900-4000 m**. Record the automated model/regression results and the full-fixture results separately. In every case, with one clean cut site and otherwise healthy branches/GDTs:

| Cut cores | Before the cut | After the cut |
| :--- | :--- | :--- |
| A | Both on | A off, C on |
| B | Both on | Both off |
| C | Both on | A on, C off |
| A + B | Both on | Both off |
| A + C | Both on | Both off |
| B + C | Both on | Both off |
| A + B + C | Both on | Both off |

Record station states and representative actual currents/voltages, not just a count of lit LEDs. The first applicable transition must identify the adjacent 100 m span. Exact broken-core classification is not required. Exercise representative multiple-site **repair/retest** sequences: isolate, repair the first located span, restore TEST, and locate remaining faults, including the final span. The separate 0 m and 4000 m stations at the shed must not be joined accidentally in the fixture.

Include negative controls for an unintended field-side A/C tie and an extra End B negative connection, demonstrating that the procedure/model detects their masking effects; do not install these as operating options. Separately record local failed indicators/taps, inter-core shorts and mixed open/short cases. They are diagnostic limitations, not cases required to satisfy the clean-cut table. Perform live fault stress only under the later qualified fault plan. Finish by restoring the approved wiring and verifying **operator restoration of RUN** and receiver function; TEST/OFF require independent containment throughout.

## Enclosure and Materials

Dry-fit the actual **COMBI 308** with board, four **Essentra LCBSBM-6-01A-RT** supports, three **WAGO 221-613s**, actual cables/glands, both lid LEDs, plugs/seals, earth conductors where applicable, and service tools. Test both standard and earth-connected configurations. Check each board's support interfaces; use the allocated full assemblies for documented enclosure/process qualification.

- Verify support hole and board-thickness tolerances against the exact Essentra drawing (listing nominally 3.18 mm hole, 1.57 mm panel and 9.53 mm spacing), retention without damage, accepted adhesive preparation/dwell and long-term mechanical support. Gel is not assumed to replace failed adhesive or support locks.
- Measure the actual internal clearances, wire bends, screwdriver access and lid service slack. External box dimensions do not establish a universal wall-clearance margin. Close the lid fully without displacing GDT_AC, straining LED leads or trapping the gasket. Inspect forming clearance again after closure/re-entry.
- Verify the exact APEM cutout, panel thickness, seal stack and tightening instructions. Published Q10 guidance is **0.20-0.25 Nm**, subject to **Q10F5SXXSG02E** confirmation; record the actual torque/instruction revision. Verify cable glands against measured jacket diameter and the accepted WISKA entry/sealing arrangement. Do not use green/yellow as an active core.
- Obtain the actual cable identity/colours, resistance, **60 V / -15 to +70 degrees C** complete-cable limits if the proposed Oceanflex is confirmed, and separate weather/UV, wet-conduit and impulse evidence. The core-only 105-degree reference is not a complete-cable rating.
- Retain the **exact WISKA MP0100** technical/process and safety evidence: variant/formulation, batch/shelf life, preparation, mixing instructions if applicable, work/cure conditions, coverage/fill/vent method, compatibility and re-entry limits. Do not invent a ratio, cure time or volume, or borrow another product's process. Verify compatibility with enclosure, supports/adhesive, LED seals/leads, WAGOs, cable, components and assembly residues.
- Record pre-/post-potting photographs, measured consumption, coverage/void inspection and normal electrical results. Define and perform the intended raised-installation rain/condensation/salt, thermal-cycle, cable-entry strain and service/resealing tests on the completed assembly. IP claims must be limited to an applicable tested configuration; constituent ratings and gel do not establish hermetic or IP68 performance. No continuous submersion or multi-decade life is qualified here.

## Continuous Duty

**Continuous-safe normal TEST** is required even though normal use is one to two hours. A timer is not the baseline safeguard. Qualify the potted, closed assembly under an approved worst-credible ambient and solar envelope, not just the observed outdoor **-10 to +30 degrees C** or a ten-minute unpotted bench test.

| Case | Required coverage |
| :--- | :--- |
| **0 m / source end** | Highest accessible PSU adjustment plus tolerance/ripple/overshoot, low cable drop, resistor/LED tolerances that maximize dissipation, and the hottest credible solar-loaded enclosure. Include the real load on the source, not only an ideal bench PSU. |
| **4000 m / far end** | Final distributed-cable/load behavior at both the minimum-current/visibility corner and the maximum credible local heating corner, with the actual potted enclosure and solar exposure. Do not assume far-end and source-end boards have identical currents or temperatures. |
| Normal source capacity | Actual 41-station load and any credible negligible-cable staging configuration, maximum setting and temperature derating. Record source regulation, overload/hiccup absence in normal operation, and power balance against the final analysis. |

Attach calibrated sensors before potting to R1/R2 and any new dissipative protection parts, relevant terminals/cable, gel/interior and enclosure/ambient locations. Record supply and branch current/voltage alongside temperatures. Ensure sensors do not compromise insulation, sealing or heat flow without accounting for it. Use a controlled radiant/thermal setup or a justified measured outdoor solar case; brief cloud-cooled results do not bound direct-sun operation.

Run through at least the two-hour typical duty and continue to demonstrated steady state. As a protocol criterion, under stable imposed conditions require critical temperatures to change by less than **1 degree C over an hour**, then log another hour; justify logger stability and any alternative criterion before testing. If stability or the environmental envelope is not established, extend the test or hold it. This demonstrates a bounded steady-state condition, not indefinite lifetime.

Compare measured temperatures/powers plus uncertainty and corner allowances with **each actual component's applicable derating/mounting conditions**. For unchanged Vishay MBE0414 resistors, distinguish the **1 W power-mode** rating from the **0.65 W standard-mode** rating; roughly 0.5 W dissipation does not prove a cool or long-lived part in gel. Check the cable, LED, gel, support adhesive and seals as well as the resistor. Define automatic/manual stop thresholds before starting and stop for instability, smell, damage, abnormal source cycling or a limit violation. Abnormal fault/surge heating is a separate qualification, not covered by passing this normal-duty soak.

## Daylight Visibility

Test the actual **Q10F5SXXSG02E** units in the final lid/gel/installation geometry at **5 m in full daylight**. Drive at the **final minimum expected field LED current**, including supply minimum, cable resistance/temperature, LED/protection tolerances and actual branch loading. A nominal source-end current or a larger bezel is not a visibility qualification.

Use real patrol heights/angles, sun directions and backgrounds, including sunlight directly colouring the OFF lens. Record measured current, illuminance, lens condition and geometry. Require the intended operator to distinguish ON/OFF correctly in repeated blinded state changes at every required viewing angle, including the A-off/C-on and A-on/C-off patterns; retain observations and failures. Qualify any shade, orientation or other optical improvement before raising current. LED/resistor substitutions require renewed electrical, thermal, fit and procurement approval.

## RF and Site

1. Use the actual transmitter, required OEM protectors, accepted regional PE/bonding and cable, intended station population, fence construction/height and test receiver. Obtain OEM acceptance of the nonstandard boundary configuration. Record the real carrier/output settings and safe measurements; do not assume a universal RF amplitude or perfect inter-core equality.
2. Compare an accepted reference configuration with the added circuit in **RUN**. Verify boundary detection, absence of unintended receiver activation, transmitter loop/alarm behavior, and absence of misleading indicator light. Check inter-core/common-mode behavior and any rectified/protection current with suitable isolated methods. Darkness is not proof of RF transparency.
3. Exercise the actual separate cattle energizer **off and on**, in both **RUN and TEST**, at the stated routing case: **at least 0.5 m separation, up to 300 m parallel**, allowing for movement. Record energizer pulse characteristics, repetition and routing used. Look for lost or false receiver responses, misleading indicators, repetitive protection firing/heating and recovery. Plastic conduit is not shielding, and the stated separation is not proof of safe clearance.
4. Qualify enough repetitions and operating/environmental corners to support the declared scope; define the duration/count beforehand with the reviewer. Record any incomplete population or untested exposure and retain the corresponding release hold. A short pilot with five boards cannot silently stand in for the final RF network or an endurance claim.
5. Verify earthing/bonding and any required site measurements through the qualified installer. The proposed common local earth for the OEM protection and both shed-end boards must match actual building PE/electrodes. Do not introduce independent unbonded rods, direct core-earth connections, or an assumed DC-negative earth bond. Keep animals independently contained until the operator restores and verifies RUN.

## Qualified Fault Tests

**C5 remains held** until the final powered fault and surge behavior is demonstrated. A suitably equipped, qualified reviewer/laboratory must approve the procedure, sample count, applied energy, instrumentation, barriers, shutdown and discharge arrangements. Do not create high-voltage impulses or ignite GDTs with ordinary bench/DMM/grounded-scope improvisations.

- Test the actual source, fuse/holder, switch/interface and final circuit at relevant minimum/maximum output, ambient and cable conditions. Include near/middle/far **A-B, B-C and A-C shorts**, resistive faults that can produce sustained heating below a fuse threshold, and earth faults with the actual floating/bonded return paths. Include appropriate failed-short/failed-open GDT and protection-device cases, and representative additional faults needed by the analysis.
- For the **2 A Littelfuse 217**, use the applicable published **DC interrupting** conditions and actual time-current/I^2t data. Verify clearing or controlled shutdown under the real source waveform; do not assign a pass because a calculated current is merely above 2 A. Cable resistance and PSU hiccup pulses can prevent prompt clearing. Include fuse-holder indication/leakage paths where relevant. An intact fuse is not proof of safety.
- Include GDT ignition followed by a **powered nominal 36 V source**. Approximately **10-15 V arc voltage** can allow DC follow current after sparkover; 36 V below the nominal 470 V firing level does not prove extinction. Capture ignition, arc/follow current, extinction or safe shutdown, and all source retry cycles. Do not substitute a glow-to-arc transition number for holding-current evidence.
- Define the line-to-line and line-to-earth surge waveforms, polarities, source impedances, levels and repetitions before testing the **complete intended discharge path**. Measure residual/overshoot voltage at the vulnerable LED branch, cable, board and hub/OEM interface, and current/temperature in the real GDT/terminal/copper/earth paths. Account for unequal firing, not guaranteed sharing. Component impulse-current figures do not establish an assembled board rating.
- Include actual cable/insulation and enclosure/material configurations in the applicable dielectric/transient tests. The cable's 60 V operating rating is not impulse qualification; neither is a GDT's nominal DC sparkover or a switch's insulation/thermal rating. Any destructive insulation testing must isolate unrelated electronics and use an approved laboratory method.
- Require the predeclared limits for touch/step hazards, temperature, current, residual voltage, insulation and physical damage to be met, with no uncontrolled arcing or persistent/repeating follow-current heating. After each exposure, verify the specified **powered recovery or safe shutdown**, inspect for latent open/short damage, and repeat normal/reversal/diagnostic checks as appropriate. A DMM-open GDT must not be called a functioning arrester without the relevant post-stress characterization.

Record any required manual reset/replacement and safe inspection procedure. Recovery of the TEST source is not automatic return to RUN; containment restoration remains the operator's action. Qualifying a declared exposure does not establish direct-strike survival or an untested assembled surge-current/lifetime rating.

## Acceptance Record

For each unit, retain serial/revision, part and process identities, test configuration and source settings, measured values with uncertainty, raw captures, photographs, test date/operator, defects, rework, repeat tests and disposition. Retain the unpotted reference and its baseline data. Use the table as an empty record, not a pre-issued certificate:

| Unit | Workmanship | Cold checks | Normal min/nominal/max | Allocated qualification evidence | Disposition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Board 1 | NOT RUN | NOT RUN | NOT RUN | Unpotted reference record pending | HELD |
| Board 2 | NOT RUN | NOT RUN | NOT RUN | Protected-reversal/characterization pending | HELD |
| Board 3 | NOT RUN | NOT RUN | NOT RUN | Source-end potted duty/process pending | HELD |
| Board 4 | NOT RUN | NOT RUN | NOT RUN | Far-end duty/visibility/material/site pending | HELD |
| Board 5 | NOT RUN | NOT RUN | NOT RUN | Hub/fault/protection scope and evidence pending | HELD |

Maintain separate evidence reports for the **280 full-hub cut cases**, protected reversal, thermal corners, visibility, enclosure/material process, RF/site and qualified powered fault/surge recovery. Identify sample reuse and gaps explicitly. The engineering reviewer records evidence-backed gate or issue closure in [REMEDIATION.md](REMEDIATION.md); these documents neither authorize an order nor close C4/C5. Resolve remaining sample, supplier, installer or laboratory requirements before requesting the applicable release.
