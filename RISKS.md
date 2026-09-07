# Electrical and Environmental Risks

**Draft revision: 1.2.0-dev. Engineering and field-release hold.**

This is a risk register and qualification boundary, not a safety certificate or measured reliability prediction. [REMEDIATION.md](REMEDIATION.md) controls settled requirements, the live issue checklist and [release gates A/B/C](REMEDIATION.md#release-gates). [pcb/ELECTRICAL.md](pcb/ELECTRICAL.md) records the three-core DC analysis and candidate-part research. **No new LED reversal/pulse protection or coordinated source/GDT shutdown circuit is selected or fitted. C4 and C5 require real implementation and test evidence, not corrected prose.**

Use [INSTALL.md](INSTALL.md) for safe installation/operation and [ACCEPTANCE.md](ACCEPTANCE.md) for separate workmanship, normal, reversal, thermal, visibility, hub, material, RF/site and powered fault/surge qualification. No numerical failure probability, guaranteed service life, board surge-current rating or direct-strike protection is established here. Missing evidence is not proof of inevitable failure, but it prevents an unsupported safety claim.

## System Boundary

The design has **41 stations at 0, 100, ..., 4000 m and 82 external LEDs**, including distinct 0 m and 4000 m stations at the shed. Retaining the five earth-connected locations at 0, 1000, 2000, 3000 and 4000 m leaves **36 standard stations**. The five-prototype order is for controlled evaluation, not five-board proof of a full perimeter installation.

WAGO 221-613 through-splices maintain each core's perimeter path and tap the local PCB. Normal perimeter current does not traverse every PCB rail in series. Surge discharge current through a station's tap, PCB, terminals and earth path is a separate load case. A standard station without an external earth connection has no assured local common-mode discharge path.

The agreed six-independent-end functional matrix is:

| Boundary-cable end | RUN | OFF | TEST |
| :--- | :--- | :--- | :--- |
| Start A | Transmitter T1 | Isolated | +36 V |
| Start B | Transmitter T1 | Isolated | DC negative |
| Start C | Transmitter T1 | Isolated | +36 V |
| End A | Transmitter T2 | Isolated | Isolated |
| End B | Transmitter T2 | Isolated | Isolated |
| End C | Transmitter T2 | Isolated | Isolated |

T1/T2 retain the actual transmitter's required **OEM protector arrangement**. This is not a switch terminal-number table. RUN and TEST ties belong on the corresponding **source-side contacts**, not permanent boundary-side straps. OFF leaves all six ends independently accessible/isolated at the hub; TEST leaves End A/B/C **separately isolated** and returns only at Start B.

### Containment and Switching

- **TEST and OFF disable RF containment.** Secure animals independently before either mode or any maintenance; do not use animals to test the boundary. Clear hub mode indication and the operator's deliberate restoration and verification of **RUN** are required. Typical TEST use is one to two hours, but continuous-safe normal TEST is required for accidental extended use; a timer or automatic RUN restoration is not the baseline safeguard.
- OFF is ordinary disconnection, not demonstrated lightning isolation, removal of all induced voltage, or safe maintenance isolation. Cable transients can flash over unsuitable contacts or couple into disconnected equipment. Do not handle the outdoor circuit or earthing during storms.
- **CA10.A362** is a six-pole centre-off sourcing candidate. Its 20 A thermal rating does not establish actual DC load breaking, contact development, insulation for this exposure, or **global break-before-make**. Manufacturer confirmation must show all old-source paths open before any new-source path makes across the whole six-end program, in both directions. Individual pole timing and static continuity alone are insufficient. Until confirmed, overlap or miswiring could inject TEST DC into the transmitter or defeat fault detection.
- RUN combines the cores only through the approved source contacts. In an ideal isolated AC loop, interchanging transmitter outputs may simply change phase; that is not a zero-risk conclusion for a real nonstandard loop, its protection, receiver response or coupled sources. Record the actual RF configuration and qualify it. No direction selector is required or approved.

## Diagnostic Limits

For one clean cut site, healthy boards/GDTs and no extra inter-core short, the required steady-state behavior is:

| Cut cores | Before the cut | After the cut |
| :--- | :--- | :--- |
| A | Both on | A off, C on |
| B | Both on | Both off |
| C | Both on | A on, C off |
| A + B | Both on | Both off |
| A + C | Both on | Both off |
| B + C | Both on | Both off |
| A + B + C | Both on | Both off |

The **first applicable state transition** locates the adjacent 100 m span, including **3900-4000 m**. It does not uniquely classify the broken cores. Multiple damage sites may be found by isolating sources, repairing the first located span and repeating TEST across all 41 stations. Qualification must exercise **all seven combinations over all 40 spans** using the real hub/final branch behavior, not merely disconnect one input from a single board.

| Failure / error | Consequence and diagnostic limitation | Required response |
| :--- | :--- | :--- |
| Failed-open LED, resistor, tap or terminal | A dark local indicator can resemble a cable fault. Healthy stations beyond a dark station suggest local trouble, but do not establish the cause alone. | Isolate and inspect the station and neighboring span; repair and retest. Do not label every dark LED a cable cut. |
| LED short or failed branch protection | May lose indication, change current/power or expose the LED to damage. A series resistor limits some current, not every fault stress. | Analyze final single-fault behavior and measure it; replace defective assemblies rather than improvise field soldering. |
| A-B or B-C cable short | Can collapse TEST voltage, trigger PSU hiccup or sustain a cable-limited current; RUN behavior may also change. | Do not assume the fuse clears. Isolate, locate and repair using the approved fault procedure. |
| A-C short or unintended field-side tie | Equal-potential conductors can look normal in healthy TEST yet backfeed across a later open and mask it. | Test shorts separately; the clean-cut truth table does not promise mixed open/short localization. No permanent field-side straps. |
| Additional End B negative connection | Provides another return and can mask a B-only cut. | Keep all three End connections separately isolated in TEST; verify the actual hub, not just an empty switch throw. |
| Failed-short or persistently conducting GDT | Can join cores or connect a core to earth, alter RF/TEST behavior and carry sustained source current. | Qualify shutdown/extinction and inspect/retest after a suspected event. No assumption that the fuse or low nominal voltage makes it safe. |
| Failed-open/degraded GDT | Normal LEDs and a DMM-open reading may persist while surge protection is lost or firing voltage has changed. | Use appropriate arrester/post-stress qualification and replacement criteria, not a continuity-only health claim. |
| Open fuse, source shutdown, wrong mode/polarity or poor hub connection | May make all indicators dark without a boundary cut. | Check the 0 m station, actual source status, voltage and accepted hub wiring first. Do not repeatedly reset or replace fuses without identifying the fault. |

Both LEDs on only demonstrate the expected local indication under the tested conditions, not freedom from all shorts, hidden arrester damage or RF problems. Optional DMM checks require the transmitter/PSU/backups disconnected and **all six boundary ends isolated**. Measure Start-to-End on each individual core: ideal 4 km / 2.5 mm^2 copper is about **28 ohms at 20 degrees C**, not zero or the parallel-core resistance. Use verified cable data and commissioning baselines, account for connected branch paths, and never megger through electronics.

## LED Reversal

The purchased baseline **APEM Q10F5SXXSG02E** is the **no-internal-resistor** indicator. Published family limits are **20 mA maximum forward current and 5 V maximum reverse voltage**, subject to exact-model temperature/pulse conditions. `02` does not make it a regulated 2 V device.

| Condition | Why the legacy safety claim is invalid |
| :--- | :--- |
| Reversed TEST supply | The series 1N4007 and LED can both be reverse-biased. Their voltage division depends on leakage, temperature, tolerances, capacitance and transients; the diode's high reverse rating does not force the LED below 5 V. |
| Reversed LED flying leads with correct supply | The series rectifier can be forward-biased while the LED is reverse-biased through the resistor. Limiting current does not establish a safe reverse voltage or prevent damage. |
| Swapped core taps / mixed polarity errors | Branches may see unexpected polarity, current paths or local voltage. They cannot be called harmless because the indicators remain dark. |
| Transient or RF stress | A DC clamp's nominal voltage and a rectifier's rating alone do not establish peak LED reverse voltage or forward pulse current. Switching, parasitic coupling and protection tolerances must be included. |

**C4 remains open until the actual protection design is verified and qualified.** A single antiparallel diode across the PCB connector does not by itself cover both supply reversal and reversed flying leads. This document does not promise that a selected P2 solution is already fitted or solves the problem. Reconcile `pcb/ELECTRICAL.md` with actual circuitry/parts and test both reversal mechanisms and their combinations at the approved voltage/temperature corners, with relevant transients. Recheck clean-cut observability after any change to branch directionality or loading.

Measure voltage at the **physical LED**, current and temperature with suitable isolated/differential methods and stated uncertainty, accounting for probe loading. Darkness, a **0.00 mA** display or a working LED after rewiring is not proof of safe reverse stress or negligible leakage. Correct suspect wiring only while isolated; do not continue energizing a miswired indicator to diagnose it visually.

## Source and Heating

### Fuse Coordination

The specified fuse is **Littelfuse 0217002.MXP, 2 A, 217 series**, in **Phoenix Contact UK 5-HESILED 60 / 3004139**. Published 217 data includes **DC interrupting ratings** applicable to the relevant variant/conditions. It is not correct to reject it solely because of a 250 V marking, nor to assume every overcurrent opens it immediately. Interrupting capacity concerns safely breaking an established fault; **time-current clearing coordination is the unresolved design issue** here.

Cable resistance can hold fault current below or near the fuse rating for a sustained period. A current-limited/hiccup PSU may supply short pulses and retries without enough heating to clear a fuse promptly. Use the exact fuse's time-current/I^2t and ambient data with the **actual source waveform**, prospective current and fault location. A calculated current above 2 A is not an automatic fuse-opening result. Include holder indication/leakage paths where relevant; its lamp is not proof of isolation or protection health.

The user believes the purchased source is **LRS-35-36, 36 V / 1 A / 36 W**; verify the nameplate. **LRS-75-36, 36 V / 2.1 A / 75.6 W** is the preferred normal capacity-margin candidate, not a confirmed purchase or a coordination fix. Both have adjustable output and hiccup overload behavior. A larger supply can change fault energy as well as normal margin. Do not substitute the legacy fault calculations, change a fuse value, or assume an ideal current source without a new analysis of the agreed same-end topology.

### Follow Current

Nominal **470 V DC sparkover** describes ignition under specified conditions, not the voltage needed to keep a GDT conducting. After ignition, these tubes have arc voltages roughly **10-15 V**. A powered 36 V source may therefore supply follow current, depending on the actual path, cable resistance, device extinction behavior and source dynamics. A glow-to-arc transition current is not a demonstrated holding-current limit.

Analyze/test hard and resistive faults, ignited and failed-short GDTs, near/middle/far locations, floating or bonded earth return paths, and source hiccup/restart sequences. Some resistive faults cause sustained heating without high enough current for prompt fuse operation. A tube may fail open and silently lose protection, or fail short and continue loading the circuit. Determine and verify a coordinated safe shutdown/extinction/recovery arrangement where needed. **C5 cannot be closed by documentation, a PSU upgrade, a fuse calculation alone, or an unpowered surge test.**

The implemented model provides a concrete counterexample to overcurrent-only protection: a conditional far-end 10 V AB arc carries **0.259543 A / 2.602168 W** in its modeled path while total source demand is only **0.979810 A**. This is a declared load-line sensitivity, not proof the real tube sustains an arc. It shows why neither nominal PSU overload nor the 2 A fuse can be assumed to intervene; actual holdover/source-recovery evidence remains necessary.

### Normal Duty

Same-end TEST has distributed loading and a source-to-far-end current gradient. Recalculate the **41-station** network using verified cable resistance/temperature, source minimum/maximum, actual LED drops and P2 branch loading. Include any credible negligible-cable staging load; do not assume a five-board bench current represents the complete installation.

With the baseline 2.2 kohm resistors, an illustrative roughly 0.5 W dissipation does not establish a cool component or a long life inside gel. The Vishay MBE0414 **1 W power-mode rating differs from its 0.65 W standard-mode rating** and both need their specified derating/mounting conditions. Accessible PSU adjustment, tolerances, internal heating and direct sun can reduce margin. A higher-wattage resistor dissipating the same power does not automatically reduce enclosure heat or fit the footprint.

Qualify **continuous-safe normal TEST**, separately from fault safety, using instrumented closed/potted source-end and far-end assemblies at the worst credible source/solar conditions. Check LEDs, resistors, new protection parts, terminals, cable, gel, seals and adhesive. Measure temperature, not touch. Also demonstrate **5 m daylight ON/OFF distinction at the final minimum field current and real angles**; increasing current to improve brightness requires renewed electrical/thermal/fit approval.

## Surges and Insulation

The baseline arrester identities are **Ruilon SMD5050-470NA** for A-B/B-C, **Bencent B5G470L** for A-C, and **Ruilon 2R470TD-8** for the three line-to-earth positions. Keep component data distinct from complete-system performance:

| Mechanism | Risk / evidence needed |
| :--- | :--- |
| Impulse sparkover and residual voltage | A nominal 470 V GDT is not a 470 V transient clamp. Reviewed data at 1 kV/us gives up to **950 V** for SMD5050-470NA and **1100 V** for 2R470TD-8; B5G470L's **850 V** figure covers **99% of measured values**, not a universal maximum. Include lead/trace inductive overshoot and the final protected-load voltage. |
| Unequal firing and current paths | Different tubes, wire lengths, contact resistances and inductances prevent assuming simultaneous firing or equal sharing. One path may carry most of a transient, and common-mode firing can create differential stress. Measure the complete intended path and vulnerable residual voltages. |
| Component versus board ratings | Component 5/20 kA figures apply to their specified waveforms and test conditions. They do not rate the board, WAGO tap, terminal, solder joint, via barrel, cable or electrode path. The three `J_EARTH` positions share a net; individual terminal ampere ratings cannot simply be added. No assembled surge-current rating is established. |
| Pulse coordination | A rectifier's repetitive reverse rating or single forward-surge rating and a resistor's steady wattage do not establish survival of an arbitrary lightning waveform, nor protect a 5 V-reverse LED. Verify voltage, current, pulse energy, timing and powered recovery for the actual network. |
| Insulation | Cable working voltage, switch/terminal nominal voltage, PCB spacing and gel dielectric data are not a coordinated impulse-withstand specification. The possible residual voltage must be compatible with the actual cable, hub, indicators and wet/coastal assembly, or an approved protection/insulation change is needed. |
| Physical construction | Preserve 2 oz copper on both sides, full-width 3.2 mm rails, protected 1.0/1.8 mm stitching vias and earth copper, at least 3.0 mm fence-to-earth copper clearance, earth GDT 9.00 mm pitch and **GDT_AC at least 2.0 mm standoff**. These are guardrails, not proof of surge survival. Actual body tolerances, forming and contamination matter. |
| Manufacturing defects | Undersized component holes, solder wicking into via apertures, poor barrel fill, damaged plating or bad placement can weaken a path despite a clean netlist. Inspect accepted processed CAM/stencil/assembly data and physical samples. A 1.0 mm via is not reliably filled merely by a generic covering option; 2 oz surface copper does not specify barrel plating. |

Do not assume solder mask, a sleeve/tape or gel constitutes independently qualified reinforced insulation over the GDT_AC crossing. Do not weaken its clearance/formed standoff or the protected copper/vias to make assembly easier. The full COMBI dry-fit and manufacturing-process acceptance must confirm the design can actually be built.

Qualified fault/surge work must cover the actual source, fuse/interface, boards, cable samples, enclosure/material system, OEM protectors and earthing as relevant to the declared exposure. Use rated differential/isolated instruments and competent laboratory methods; ordinary DMM or grounded-scope practices are not safe substitutes. Capture powered recovery and post-stress hidden damage. No direct-strike survival or untested rating follows from a passing bare-board continuity test or an individual arrester datasheet.

## Earthing and Touch

- A qualified installer must review the **actual building PE/electrodes**, regional DogWatch protection instructions and the site's bonding/lightning arrangements. The user proposes sharing local earth between the DogWatch protection and both shed-end boards; this is a site-design proposal to confirm, not permission to join arbitrary grounds.
- Five earth-connected station locations do not automatically require five separate rods. Do not install unbonded electrodes by default, directly earth an A/B/C core, or assume DC negative must be bonded to earth. Purchased rods, clamps and paired 2.5 mm^2 conductors do not establish acceptable sizing, placement, multiwire clamping or impulse performance.
- Retain the OEM transmitter protector(s) and applicable PE connection. Station GDTs do not replace the OEM network. Any LRS mains/chassis PE, overcurrent protection and enclosure segregation must follow the exact supply instructions and regional installation requirements; do not omit protective earth to float a measurement.
- Earth-potential rise, inductive voltage on earth leads and different remote electrode potentials can transfer a surge into the shed or nearby metalwork. **Touch and step potential** can endanger people and animals near conductors, electrodes and supporting fences. Specify conductor routes, bonding, accessible-metal treatment and electrode locations through the installer, including buried-service checks before ground work.
- Loose/corroded earth connections and unequal contact paths can increase residual voltage or redirect discharge. Multiple terminal positions are not guaranteed redundant protection or equal sharing. Provide compatible clamps, mechanical protection and inspectable connections; record the required site verification and maintenance.
- OFF or a removed source fuse does not make a long outdoor line lightning-safe. Isolate mains/PSU/transmitter/backups and all six ends before ordinary wiring checks, verify de-energization, and avoid storms. Do not disconnect protective earth casually during troubleshooting. Use the separate laboratory procedure for abnormal-voltage testing.

## Site and Materials

| Exposure / material | Known facts and remaining controls |
| :--- | :--- |
| Coastal climate / sun | Site is on the Isle of Man, less than 1 km from the coast, with frequent rain, salt and condensation. Observed ambient is about **-10 to +30 degrees C**, with some boxes in direct sun. This is not a lifetime weather envelope; internal gel/component temperature can exceed ambient. Establish solar/thermal, moisture and corrosion limits for the actual assembly. |
| Cable identity | Likely **Oceanflex CM03/05.100 / supplier P01018**, but actual purchase identity remains unconfirmed. Listed three tinned-copper 2.5 mm^2 cores, 35/0.30 mm strands, 7.3 mm maximum outside diameter, **60 V maximum**, and **-15 to +70 degrees C** complete-cable working temperature. Confirm the reel, maximum resistance and actual core colours. |
| Cable suitability | The supplier's 105-degree reference is for cores, not the complete cable. Long-term exposed-weather/UV, wet-conduit and impulse suitability need evidence; do not assume arctic or mains ratings. A 60 V working rating does not establish surge withstand or inevitable failure at every short overvoltage. **GREEN/YELLOW IS NOT AN ACTIVE FENCE CONDUCTOR**, even if re-sleeved. |
| Route and mechanics | Cable is mostly 0.3-1.0 m above ground on timber fencing with horizontal metal wire strands and no electrical connection to them. Driveway/gate conduit may be wet. Prevent abrasion, strain, animal/strimmer damage, water tracking and unsuitable bends. Raised COMBI installations are not intended for continuous submersion. |
| Enclosure / entry seals | COMBI 308's original IP66 membrane/IP67 specified-gland arrangements do not automatically rate drilled indicator holes, different glands, plugs or a gel-filled assembly. Select glands for actual jacket diameter and validate the complete seal/strain-relief arrangement. No hermetic or automatic IP68 claim is supported. |
| MP0100 gel | Exact formulation/process and compatibility evidence remain necessary. Obtain the supplied product's technical/safety instructions, preparation, mixing/cure method, fill/vent conditions and re-entry limits. Do not invent ratios, cure times or a void-free fill from an overflowing vent. Gel can alter heat flow, retain contamination or leave voids; it does not guarantee sealing or lifetime. |
| Supports and fit | Essentra **LCBSBM-6-01A-RT** nominal hole/panel/spacing data must be checked against finished board tolerances, actual COMBI plastic, adhesive instructions and retention. Complete dry-fit includes WAGOs, glands, cable bends, earth wires, GDT height, lid LEDs and screwdriver access. Do not assume gel permanently carries the PCB after adhesive failure. |
| LED seals and visibility | Use exact **Q10F5SXXSG02E** mounting instructions; published Q10 torque guidance is **0.20-0.25 Nm**, subject to model confirmation. Excess torque can damage the lid/seal. Confirm 5 m full-daylight visibility at minimum current and actual angles; sunlight can make an OFF lens appear coloured. |
| Surface finish / ageing | ENIG is an assembly finish, not a pore-free lifetime seal over all conductors. Tinned cores, connector plating and gel do not eliminate salt ingress, capillary wicking, loosened joints, solder fatigue, polymer ageing or maintenance needs. Verify actual material compatibility and use bounded evidence, not multi-decade guarantees. |

### Cattle-Fence Coupling

The supporting fence is **not energized**. A separate energized cattle wire may run **at least 0.5 m away for up to 300 m in parallel**. This user-supplied geometry is the qualification case, not an interference-safe clearance proof. Movement can reduce separation; increase it where practical. Plastic conduit does not shield electromagnetic coupling.

Capacitive/inductive coupling and shared earth paths can impose repetitive common-mode/differential pulses, create false or lost receiver responses, mislead the TEST indicators, or repeatedly stress protection without an obvious immediate failure. Record the actual energizer pulse characteristics and routing and compare energizer **off/on in both RUN and TEST**, including recovery and repetitive heating. Qualification must use the actual cable, station loading, fence construction/height, transmitter/receiver and regional earthing arrangement. A short five-board bench exercise does not establish site behavior or long-term pulse endurance.

## Residual Holds

**Gate A remains held by the unresolved electrical and part/land-pattern decisions, despite passing automated file checks. Gate B remains held wherever exact fit/process/CAM acceptance or a safely defined prototype scope is absent. Gate C remains held until the required hardware/site evidence and performance limits exist.** Refer to [REMEDIATION.md](REMEDIATION.md), rather than treating this draft as the live completion checklist.

In particular, neither **C4 LED reversal** nor **C5 source/GDT coordination** is resolved by removing unsafe claims. Keep outstanding switch DC/contact/transfer evidence, PSU/cable identity, insulation, MP0100/Essentra acceptance, enclosure fit, thermal/visibility/RF/site tests and installer earthing review explicit. Retain one unpotted reference among the five prototypes and obtain approval for additional samples when the destructive/qualification scope requires them.

After suspected surge damage, ingress, mechanical impact, repeated source trips or anomalous indications, independently contain animals, isolate safely, inspect and repair, then repeat the relevant checks and the TEST repair/retest workflow before the operator restores RUN. Agree inspection/replacement intervals for the actual coastal site and OEM/material requirements. Visible normal operation alone cannot certify a hidden arrester or insulation path as healthy, and no zero-risk or fixed multi-decade service promise is made.
