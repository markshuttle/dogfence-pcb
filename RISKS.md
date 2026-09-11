# Electrical and Environmental Risks

**Draft revision: 1.2.0-dev. Production/field-release hold; prototype-file authorization is not hardware approval.**

This is a risk register and qualification boundary, not a safety certificate or measured reliability prediction. [Agreed requirements](REMEDIATION.md#agreed-requirements), the [issue register](REMEDIATION.md#issue-register) and [release gates](REMEDIATION.md#release-gates) control decisions. The [implemented circuit](pcb/ELECTRICAL.md#1-implemented-model) and [reviewed population](pcb/ASSEMBLY.md#reviewed-components) define the design under assessment, not qualified hardware. **C4, C5, W3, W1 and W4 remain open.**

**Gate P permits file-verified prototype artifacts with all five holds deferred, not closed.** Unresolved external sourcing still blocks publication; files do not authorize upload or order. Supplier CAM/placement/allocated parts and board-specific process/fit acceptance remain order tasks. Environmental/switch qualification and enclosure dry-fit after prototype receipt remain separate from file generation and the original A/B/C production/field gates.

Use [INSTALL.md](INSTALL.md) for safe installation/operation and [ACCEPTANCE.md](ACCEPTANCE.md) for separate workmanship, normal, selected negative-voltage protection, thermal, visibility, hub, material, RF/site and powered fault/surge qualification. No numerical failure probability, guaranteed service life, board surge-current rating or direct-strike protection is established here. Missing evidence is not proof of inevitable failure, but it prevents an unsupported safety claim.

Manufacturer sources and unresolved discrepancies are in [ENVIRONMENT_EVIDENCE](pcb/ENVIRONMENT_EVIDENCE.md). [MATERIALS](MATERIALS.md) owns purchases, reel labels and allocation, including [resistor procurement/history](MATERIALS.md#resistor-procurement-and-history).

## System Boundary

The design has **41 stations at 0, 100, ..., 4000 m and 82 external LEDs**, including distinct 0 m and 4000 m stations at the shed. Retaining the five earth-connected locations at 0, 1000, 2000, 3000 and 4000 m leaves **36 standard stations**. The five-prototype order is for controlled evaluation, not five-board proof of a full perimeter installation.

WAGO 221-613 through-splices maintain each core's perimeter path and tap the local PCB. Normal perimeter current does not traverse every PCB rail in series. Surge discharge current through a station's tap, PCB, terminals and earth path is a separate load case. A standard station without an external earth connection has no assured local common-mode discharge path.

Apply [INSTALL's six-independent-end functional matrix](INSTALL.md#functional-matrix), not an assumed switch terminal-number table. **TEST feeds Start A/C positive and returns at Start B DC negative; End A/B/C stay separately isolated.** OFF leaves all six ends independently accessible/isolated at the hub.

T1/T2 retain the actual transmitter's required **OEM protector arrangement**. RUN and TEST ties belong on the corresponding **source-side contacts**, not permanent boundary-side straps. No **End A/C common, opposite-end B return or dual-B negative return** is permitted in TEST; these can destroy the required cut indications.

### Containment and Switching

- **TEST and OFF disable RF containment.** Secure animals independently before either mode or any maintenance; do not use animals to test the boundary. Clear hub mode indication and the operator's deliberate restoration and verification of **RUN** are required. Typical TEST use is one to two hours, but continuous-safe normal TEST is required for accidental extended use; a timer or automatic RUN restoration is not the baseline safeguard.
- OFF is ordinary disconnection, not demonstrated lightning isolation, removal of all induced voltage, or safe maintenance isolation. Cable transients can flash over unsuitable contacts or couple into disconnected equipment. Do not handle the outdoor circuit or earthing during storms.
- The provisional **CA10.A364/WAA364** has eight poles, with **two extra poles unassigned**; follow [INSTALL's switch acceptance controls](INSTALL.md#switch-and-supply). Its 20 A thermal rating does not establish actual DC load breaking, contact development, insulation for this exposure, or **global break-before-make**. Manufacturer confirmation for the exact offered program must show all old-source paths open before any new-source path makes across the whole used program, in both directions. Physical terminal numbers remain unapproved; individual pole timing and static continuity alone are insufficient. Until confirmed, overlap or miswiring could inject TEST DC into the transmitter or defeat fault detection.
- RUN combines the cores only through the approved source contacts. In an ideal isolated AC loop, interchanging transmitter outputs may simply change phase; that is not a zero-risk conclusion for a real nonstandard loop, its protection, receiver response or coupled sources. Record the actual RF configuration and qualify it. No direction selector is required or approved.

## Diagnostic Limits

Use [INSTALL's clean-cut indications](INSTALL.md#clean-cut-indications) only for one clean cut site, healthy boards/GDTs and no extra inter-core short. The **first applicable state transition** locates the adjacent 100 m span, including **3900-4000 m**; it does not uniquely classify the broken cores. For multiple sites, follow [repair and retest](INSTALL.md#repair-and-retest): isolate sources and all six ends, repair the first located span and repeat TEST across all 41 stations. Qualification must exercise **all seven combinations over all 40 spans** using the real hub/final branch behavior, not merely disconnect one input from a single board.

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

Both LEDs on only demonstrate the expected local indication under the tested conditions, not freedom from all shorts, hidden arrester damage or RF problems. [Optional DMM checks](INSTALL.md#optional-dmm-checks) require the transmitter/PSU/backups disconnected and **all six boundary ends isolated**. Measure Start-to-End on each individual core, using verified cable data and commissioning baselines rather than zero or parallel-core resistance. Account for connected branch paths, and never megger through electronics.

## LED Reversal

The purchased baseline **APEM Q10F5SXXSG02E** is the **no-internal-resistor** indicator. Published family limits are **20 mA maximum forward current and 5 V maximum reverse voltage**, subject to exact-model temperature/pulse conditions. `02` does not make it a regulated 2 V device.

| Condition | Implemented behavior / remaining limitation |
| :--- | :--- |
| Reversed TEST supply / negative connector voltage | D3/D4 now provide forward-conducting negative shunts at LED_POS-to-B, after the series diodes. Unlike the retired series-only circuit, a local shunt path exists; its dynamic voltage and the physical LED harness remain unqualified. This is not proof of <=5 V reverse stress. |
| Reversed LED flying leads with correct supply | The series rectifier can be forward-biased while the LED is reverse-biased through the resistor. Limiting current does not establish a safe reverse voltage or prevent damage. |
| Swapped core taps / mixed polarity errors | Branches may see unexpected polarity, current paths or local voltage. They cannot be called harmless because the indicators remain dark. |
| Transient or RF stress | A DC clamp's nominal voltage and a rectifier's rating alone do not establish peak LED reverse voltage or forward pulse current. Switching, parasitic coupling and protection tolerances must be included. |

**User-accepted risk, 2026-09-07:** indicator damage from accidental low-voltage installation polarity errors is accepted, with spare LEDs for replacement. Reversed flying-lead survival is no longer a required feature; D3/D4 are also reverse-biased in that condition and do not protect it. Accepting replacement is not evidence of immunity or permission to continue powering suspect wiring. [Installation spares](MATERIALS.md#1-station-inventory) remain unallocated and must be additional to field and test requirements.

**C4 remains open for the implemented protection's ordinary-transient response.** D3/D4 BYG23T shunts have cathodes to LED positive and anodes to B; they are not extra series parts or positive-voltage/current regulators. The **75 ns reverse-recovery rating is not forward-clamp speed**; the [typical forward-recovery evidence](pcb/DESIGN_BOUNDS.md#fault-screen) does not establish a <=5 V LED transient bound. Assess actual RUN/TEST, switching and nearby-lightning response without imposing the historical 40-part circuit. The one-way cut model is not a reverse-leakage or transient solver.

Measure voltage at the **physical LED**, current and temperature with suitable isolated/differential methods and stated uncertainty, accounting for probe loading. Darkness, a **0.00 mA** display or a working LED after rewiring is not proof of safe reverse stress or negligible leakage. Correct suspect wiring only while isolated; do not continue energizing a miswired indicator to diagnose it visually.

## Source and Heating

### Fuse Coordination

The specified fuse is **Littelfuse 0217002.MXP, 2 A, 217 series**, in **Phoenix Contact UK 5-HESILED 60 / 3004139**. Published 217 data includes **DC interrupting ratings** applicable to the relevant variant/conditions. It is not correct to reject it solely because of a 250 V marking, nor to assume every overcurrent opens it immediately. Interrupting capacity concerns safely breaking an established fault; **time-current clearing coordination is the unresolved design issue** here.

Cable resistance can hold fault current below or near the fuse rating for a sustained period. A current-limited/hiccup PSU may supply short pulses and retries without enough heating to clear a fuse promptly. Use the exact fuse's time-current/I^2t and ambient data with the **actual source waveform**, prospective current and fault location. A calculated current above 2 A is not an automatic fuse-opening result. Include holder indication/leakage paths where relevant; its lamp is not proof of isolation or protection health.

The authorized [source configuration](INSTALL.md#switch-and-supply) uses **one MEAN WELL LRS-75-36 for TEST and the second as a disconnected spare**. No parallel, series, separate-channel or opposite-end feeding is authorized. Verify received nameplates and output settings. Adjustable output and hiccup overload behavior are not a coordination fix; a larger supply can change fault energy as well as normal margin. Do not substitute the legacy fault calculations, change a fuse value, or assume an ideal current source without a new analysis of the agreed same-end topology.

### Follow Current

Nominal **470 V DC sparkover** describes ignition under specified conditions, not the voltage needed to keep a GDT conducting. After ignition, these tubes have arc voltages roughly **10-15 V**. A powered 36 V source may therefore supply follow current, depending on the actual path, cable resistance, device extinction behavior and source dynamics. A glow-to-arc transition current is not a demonstrated holding-current limit.

Analyze/test hard and resistive faults, ignited and failed-short GDTs, near/middle/far locations, floating or bonded earth return paths, and source hiccup/restart sequences. Some resistive faults cause sustained heating without high enough current for prompt fuse operation. A tube may fail open and silently lose protection, or fail short and continue loading the circuit. Determine and verify a coordinated safe shutdown/extinction/recovery arrangement where needed. **C5 cannot be closed by documentation, a PSU upgrade, a fuse calculation alone, or an unpowered surge test.**

The [current fault screens](pcb/DESIGN_BOUNDS.md#fault-screen) illustrate limits on overcurrent-only protection: cable-limited ignited-GDT paths and resistive faults can dissipate sustained heat at source currents below the fuse rating. These are selected prospective load lines, not maximum fault bounds or observed latched failures. They do not establish physical extinction or non-extinction; actual holdover/source-recovery evidence remains necessary. D3/D4 do not alter the upstream GDT follow-current paths.

### Normal Duty

Same-end TEST has distributed loading and a source-to-far-end current gradient. Use the [TE-prototype / BYG23T load cases](pcb/ELECTRICAL.md#2-calculated-results) and [declared source/cable envelope](pcb/DESIGN_BOUNDS.md#evidence-and-inputs), not enforced source limits or guaranteed combined ratings. The historical restricted-voltage window was only a proposal; include actual adjustment, hub/interface losses, ripple and startup rather than treating PSU OVP as a precision operating limiter. Qualifying the real normal source range is an alternative to imposing an active cutoff. Include credible negligible-cable staging, not just five boards.

Use [DESIGN_BOUNDS's nonuniform current cases](pcb/DESIGN_BOUNDS.md#normal-current) and loose comparison floor, not retired PS12/PR02 evidence or unreviewed Yageo extrapolations. The high-drop/Rmax branch, zero-drop/Rmin neighbours and conditional clamp diversion are screening assumptions, not an exhaustive joint-tolerance minimum, measurement or guaranteed optical floor. Uniform loads can overstate the weakest LED's current. Clamp leakage diverts branch current rather than adding it again to source demand. Series-diode reverse leakage and OFF-state glow are not solved by the ideal one-way cut model.

The [thermal screens](pcb/DESIGN_BOUNDS.md#thermal-screens) depend on engineering resistance-reference and temperature assumptions, not verified TE test conditions. Resistor temperature is an input, not a self-heating result or qualified operating point. [TE's four-layer reference mounting](pcb/DFM_EVIDENCE.md#te-rating-and-mounting-basis) differs from this two-layer PCB. Applying catalogue power/derating requires evidence and measured chip/termination/pad/PCB and material-interface temperatures. The difference does not prove two-layer failure, but the catalogue curve alone cannot close W3; its zero-power ambient endpoint is not an acceptable powered-chip or gel temperature.

SMT terminations, solder lands and PCB copper may help heat rejection, but do not lower electrical loss or prove a cooler result. PR02's hot-spot, mounted thermal-resistance and axial standoff/forming data do not apply. No closed/gel-filled thermal test has been performed; the rating does not establish cool operation, material compatibility or long life.

Qualify **continuous-safe normal TEST**, separately from fault safety, using instrumented closed/potted source-end and far-end assemblies at the worst credible source/solar conditions. Check LEDs, resistors, new protection parts, terminals, cable, gel, seals and adhesive. Measure temperature, not touch. Also demonstrate **5 m daylight ON/OFF distinction at the final minimum field current and real angles**; increasing current to improve brightness requires renewed electrical/thermal/fit approval.

**TE prototype results do not qualify Yageo production.** Apply the [independent population/substitution review](pcb/ASSEMBLY.md#reviewed-components): manufacturer rating, land-pattern, thermal, pulse and process evidence, controlled BOM/CAD/library/model/note updates, reverification and applicable qualification. Matching resistance/wattage or procurement status does not establish interchangeable qualification or an implemented production BOM.

## Surges and Insulation

The user accepts potentially wholesale rebuilding after a **direct strike**.
No numerical probability follows from that decision. A damaging surge need
not be a direct hit: nearby lightning can induce voltage in the long cable or
raise local earth potential relative to remote cable/earth. The close A/B/C
cores can share much of the induced voltage (common mode), but imbalance,
connections and unequal protection firing can convert some to differential
voltage across an indicator branch. No station waveform has been measured.

More ordinary candidates are switching/interruption of cable current, contact
bounce or loose/arcing connections, and source startup/disturbances. These are
mechanisms to assess, not a claim that normal operation currently produces
destructive pulses. **Energized cattle fencing is now prohibited near the whole
boundary cable, stations and hub**; close-parallel cattle-wire coupling is a
withdrawn exposure scenario, not part of the accepted installation. Reintroducing
it requires reassessment before use, not an assumed safe clearance or automatic
acceptance of repeated failures. Ordinary switching/RUN and nearby-lightning
damage have not been waived wholesale.

There is no universal voltage threshold for "severe": peak voltage/current,
duration, source impedance, deposited energy, repetition and path determine
damage. The historical 950/1200 V screens are not measured field conditions.
[Bourns' exposed-DC note, 04/25](https://www.bourns.com/docs/technical-documents/technical-library/gas-discharge-tubes/application-notes/bourns_surge_protection_for_exposed_dc_power_supplies_application_note.pdf)
provides manufacturer context for direct/indirect lightning and powered GDT
follow current; its telecom test levels are **not adopted as DogFence requirements**.

Use the [reviewed arrester population](pcb/ASSEMBLY.md#reviewed-components) and [component evidence](pcb/ELECTRICAL.md#7-evidence-register). Keep component data distinct from complete-system performance:

| Mechanism | Risk / evidence needed |
| :--- | :--- |
| Impulse sparkover and residual voltage | A nominal 470 V GDT is not a 470 V transient clamp. Reviewed data at 1 kV/us gives up to **950 V** for SMD5050-470NA and **1100 V** for 2R470TD-8; B5G470L's **850 V** figure covers **99% of measured values**, not a universal maximum. Include lead/trace inductive overshoot and the final protected-load voltage. |
| Unequal firing and current paths | Different tubes, wire lengths, contact resistances and inductances prevent assuming simultaneous firing or equal sharing. One path may carry most of a transient, and common-mode firing can create differential stress. Measure the complete intended path and vulnerable residual voltages. |
| Component versus board ratings | Component 5/20 kA figures apply to their specified waveforms and test conditions. They do not rate the board, WAGO tap, terminal, solder joint, via barrel, cable or electrode path. The three `J_EARTH` positions share a net; individual terminal ampere ratings cannot simply be added. No assembled surge-current rating is established. |
| Pulse coordination | A rectifier's repetitive reverse rating or single forward-surge rating and a resistor's steady wattage do not establish arbitrary pulse survival or protect a 5 V-reverse LED. [TE's family ceilings and power-limited working-voltage calculation](pcb/DESIGN_BOUNDS.md#thermal-screens) are conditional catalogue data, not a system or pulse rating. The cited TE sheet does not establish the historical PS12 overload test or one-pulse curves. Do not transfer those data to TE or use TE results to qualify Yageo. Verify exact-part voltage, current, pulse energy, timing, repetition and powered recovery for the actual network. |
| Insulation | Cable working voltage, switch/terminal nominal voltage, PCB spacing and gel dielectric data are not a coordinated impulse-withstand specification. The possible residual voltage must be compatible with the actual cable, hub, indicators and wet/coastal assembly, or an approved protection/insulation change is needed. |
| Physical construction | Breaching the [physical guardrails](pcb/ASSEMBLY.md#physical-guardrails) or collapsing the raised overpass can weaken a discharge path or short crossing conductors. Preserve full-width dual-layer rails, all protected vias and earth copper/isolation. **GDT_AC's whole raised span remains >=2.00 mm above the highest finished PCB top before gel**; apply the complete [forming/height controls](pcb/ASSEMBLY.md#gdt_ac-forming-drawing). Drawing/inspection limits are not forming approval or surge proof. Actual controlled body/pose limits and contamination still matter. |
| Manufacturing defects | Selected [via treatment](pcb/ASSEMBLY.md#stitching-via-identification) is **UNTENTED both sides, no via paste and no fill/plug/cap**. Adjacent same-net rail-via mask overlap is intentional; SMT mask/paste apertures must not overlap via holes or annuli. Exposed ENIG is wettable, not sealed: solder ingress/drain-through, loose beads, poor component barrel fill, damaged plating or placement can weaken a path. Inspect processed CAM/stencil/assembly data and samples; no protected-drill reduction is authorized. 2 oz surface copper does not specify barrel plating. |

[Assembly controls](pcb/ASSEMBLY.md#physical-guardrails) and [DFM evidence](pcb/DFM_EVIDENCE.md) distinguish body boxes, SMT lands and retained holes from actual fit. TE body containment does not approve its [alternate project lands](pcb/ASSEMBLY.md#2512-smt-resistors); supplier placement/stencil/solder acceptance remains required. No resistor/diode insertion holes or axial resistor forming/standoff remain. Retained Kefa/GDT [E limits](pcb/ASSEMBLY.md#hole-fit-evidence) are procurement envelopes, not guaranteed or measured lots; **W4 actual pin/pattern/body fit and solder/GDT-forming acceptance remain open**. **W1 retains the Ruilon metric/inch contradiction and actual solder/stencil/CAM acceptance**, alongside TE/BYG23T process review. File choices do not authorize altered guardrails, folded routing or extra vias, or close production/field holds.

Do not assume solder mask, a sleeve/tape or gel constitutes independently qualified reinforced insulation over the GDT_AC crossing. Do not weaken its clearance/formed standoff or protected copper/vias to make assembly easier. Supplier manufacturing-process acceptance remains an order task; full COMBI dry-fit follows prototype receipt before enclosure/field acceptance, not before Gate P file generation.

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
| Cable identity | User-confirmed **AMC Oceanflex CM03/05.100** reel labels and **red, black and PLAIN green** cores are recorded in MATERIALS. [AMC 2026 Update V.3](pcb/ENVIRONMENT_EVIDENCE.md#amc-oceanflex-cable) gives **60 V max DC, -30 to +70 degrees C** complete-cable service. The [standard-resistance ceiling](pcb/DESIGN_BOUNDS.md#evidence-and-inputs) is conditional, not a reel measurement; reconcile the labelled-strand/standard construction discrepancy and supplied-revision applicability, not product identity or colours. |
| Cable suitability | The older listing's 105-degree core reference is not a complete-cable rating. Long-term exposed-weather/UV, wet-conduit and impulse suitability need evidence; do not assume arctic or mains ratings. A 60 V working rating does not establish surge withstand or inevitable failure at every short overvoltage. **GREEN/YELLOW IS NOT AN ACTIVE FENCE CONDUCTOR**, even if re-sleeved; the confirmed core is plain green. |
| Route and mechanics | Cable is mostly 0.3-1.0 m above ground on timber fencing with horizontal metal wire strands and no electrical connection to them. Driveway/gate conduit may be wet. Prevent abrasion, strain, animal/strimmer damage, water tracking and unsuitable bends. Raised COMBI installations are not intended for continuous submersion. |
| Enclosure / entry seals | COMBI 308 is **polypropylene (PP) with a TPE gasket, not polycarbonate**. Its original IP66 membrane/IP67 specified-gland arrangements do not automatically rate drilled indicator holes, different glands, plugs or a gel-filled assembly. Select glands for actual jacket diameter and validate the complete seal/strain-relief arrangement. No hermetic or automatic IP68 claim is supported. |
| OneGel | Confirmed **WISKA OneGel, not MP0100: single-component cartridge, no mixing**. [Manufacturer cure/temperature conflicts](pcb/ENVIRONMENT_EVIDENCE.md#wiska-onegel) require supplied-lot clarification, not an assumed curing step or self-levelling pour. **No thermal conductivity is published in the reviewed sources.** Validate material compatibility, dispensing/coverage/voids and re-entry, including actual WAGO 221-613 contacts/housings; unrelated Gelbox system evidence is not approval. Gel can alter heat flow or retain contamination and does not guarantee sealing or lifetime. |
| Supports and fit | Essentra **LCBSBM-6-01A-RT** nominal hole/panel/spacing data must be checked against finished board tolerances, COMBI 308's PP substrate, adhesive instructions and retention. Use the [controlled J_EARTH overhang/body/pose and courtyard envelopes](pcb/ASSEMBLY.md#body-and-courtyard-evidence); a bare-board rectangle is not enclosure-fit approval. Complete dry-fit includes WAGOs, glands, cable bends, earth wires, complete GDT height, lid LEDs and screwdriver access. Do not assume gel permanently carries the PCB after adhesive failure. |
| LED seals and visibility | Use exact **Q10F5SXXSG02E** mounting instructions; published Q10 torque guidance is **0.20-0.25 Nm**, subject to model confirmation. Excess torque can damage the lid/seal. Confirm 5 m full-daylight visibility at minimum current and actual angles; sunlight can make an OFF lens appear coloured. |
| Surface finish / ageing | ENIG is an assembly finish, not a pore-free lifetime seal over all conductors. Tinned cores, connector plating and gel do not eliminate salt ingress, capillary wicking, loosened joints, solder fatigue, polymer ageing or maintenance needs. Verify actual material compatibility and use bounded evidence, not multi-decade guarantees. |

### Cattle-Fence Prohibition

The supporting fence is **not energized**. Apply [INSTALL's prohibition](INSTALL.md#cattle-fence-prohibition) on energized cattle fencing near the **entire 4 km boundary cable, every station and the hub**, not only the shed. Inspect and maintain this restriction instead of testing the withdrawn close-parallel exposure. If land use changes or the hazard returns, stop work/use, arrange safe isolation and reassess before use.

No numerical safe separation follows from the prohibition, and plastic conduit is not electromagnetic shielding. It removes the previously declared close-cattle-wire exposure from the installation scope, not every induced voltage, nearby-lightning event or earth-potential difference. RF/site qualification still uses the actual cable, station loading, fence construction/height, transmitter/receiver and regional earthing arrangement. A short five-board bench exercise does not establish site behavior or endurance.

## Residual Holds

**Gate P is the authorized file-verified prototype-artifact scope, separate from the original A/B/C production/field gates.** It retains all strict file/sourcing checks and records all five engineering holds as deferred, not closed. Original Gate A remains held by unresolved electrical and part/land-pattern acceptance; B by the required order/fit/process/CAM evidence; C by hardware/site qualification. Neither P nor a generated ZIP authorizes upload, purchase or use. Refer to [REMEDIATION.md](REMEDIATION.md), not this draft as a live completion checklist.

In particular, **C4 LED transient qualification**, **C5 source/GDT coordination**, **W3 actual continuous thermal behavior** and **W1/W4 process/fit acceptance** remain open. Unresolved external rows still block both publication modes. Neither stock nor an order establishes PCBA-job allocation; whole-BOM `allocation_verified` remains `false`. Latest file/publication results belong to [REMEDIATION](REMEDIATION.md#release-gates), not this risk register. Keep outstanding switch, source, cable, OneGel, enclosure, thermal/visibility/RF/site and earthing qualification explicit without restarting that research for prototype files. Retain an unpotted reference and obtain approval for additional samples when the existing qualification scope requires them.

After suspected surge damage, ingress, mechanical impact, repeated source trips or anomalous indications, independently contain animals, isolate safely, inspect and repair, then repeat the relevant checks and the TEST repair/retest workflow before the operator restores RUN. Agree inspection/replacement intervals for the actual coastal site and OEM/material requirements. Visible normal operation alone cannot certify a hidden arrester or insulation path as healthy, and no zero-risk or fixed multi-decade service promise is made.
