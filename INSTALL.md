# Installation and Operation

**Draft revision: 1.2.0-dev. Production/field release remains held; prototype-file authorization is not installation approval.**

This manual describes the agreed installation and operating requirements, not an approved or qualified hardware release. [REMEDIATION.md](REMEDIATION.md) controls settled requirements, the live checklist, and [release gates](REMEDIATION.md#release-gates). The authorized **16-part HP12/BYG23T hybrid** uses intended **Uni-Royal HP122WF2201T4E, 2.2 kohm / 2 W / 1% SMT resistors** for R1/R2; exact sourcing remains pending in [MATERIALS](MATERIALS.md). D1/D2 are series diodes and D3/D4 are negative-voltage shunts across the LED outputs, not additional series parts. [pcb/ELECTRICAL.md](pcb/ELECTRICAL.md) records the remaining limits. Negative clamp paths are not qualified pulse protection; powered-GDT recovery is unresolved and actual OneGel thermal testing is unperformed. **C4, C5, W3, W1 and W4 remain open**. Do not install this draft as qualified hardware.

**Gate P permits file-verified prototype artifacts only**, with those holds deferred, not closed; unresolved external sourcing still blocks publication. It does not authorize uploading or ordering. Supplier CAM/placement/allocated-part acceptance remains an order task. Switch/environmental qualification and full enclosure dry-fit are separate hardware activities, not prerequisites to generating prototype files; the original A/B/C production/field holds remain.

Use [ACCEPTANCE.md](ACCEPTANCE.md) for controlled prototype qualification and commissioning records, and [RISKS.md](RISKS.md) for limitations. Do not roll out an unqualified design or rely on it for containment or lightning protection.

Manufacturer sources and detailed unresolved discrepancies are in [pcb/ENVIRONMENT_EVIDENCE.md](pcb/ENVIRONMENT_EVIDENCE.md); [MATERIALS.md](MATERIALS.md) records the latest confirmed inventory, reel labels and PSU allocation.

## System Layout

- Install **41 stations at 0, 100, ..., 4000 m**, with one board and two external LEDs per station: **82 LEDs and 40 diagnostic spans**. The 0 m and 4000 m stations are separate stations even though both cable ends reach the shed.
- Retain the five earth-connected station locations at 0, 1000, 2000, 3000, and 4000 m, subject to the accepted earthing design. This leaves **36 standard stations**. Five earth-connected stations do not imply five independent earth electrodes.
- Preserve the WAGO through-splice/PCB-tap arrangement. Use three WAGO 221-613 splices and four supports per station, giving 123 splices and 164 supports before prototype/spare allowances. Required quantities are not evidence of purchases; reconcile the recorded 80-LED purchase and other inventory in [MATERIALS.md](MATERIALS.md).
- The first order is five fully assembled prototypes, with no field PCB soldering. Retain an unpotted reference and qualify the assembly before preparing the perimeter batch; passing basic tests on five boards is not field-release approval.

Each core has its own through-splice. Do not join different cores at a station:

```text
Incoming A ---- WAGO A ---- Outgoing A
                  |
                J_IN A

Incoming B ---- WAGO B ---- Outgoing B
                  |
                J_IN B

Incoming C ---- WAGO C ---- Outgoing C
                  |
                J_IN C
```

At the two shed-end stations, the corresponding hub lead occupies the end connection. Normal perimeter current follows the cable and WAGO splices, not a series path through every PCB. Each PCB takes its local indicator current; surge current through a board is a separate qualification case.

## Safety First

- **TEST and OFF disable the RF fence.** Secure animals using independent containment before selecting either mode, opening a box, or testing the transmitter. Do not use an animal as a test receiver. Provide clear hub mode indication and an operator reminder to restore RUN.
- OFF is ordinary hub disconnection, **not demonstrated lightning isolation or safe maintenance isolation**. Long outdoor conductors can acquire dangerous induced voltage even with local supplies off. Do not handle the fence, earth connections, or test equipment during electrical storms.
- Before wiring or resistance checks, isolate the transmitter, TEST PSU, their mains feeds and every battery/backup source using the accepted safe-isolation procedure. Prevent reconnection, allow stored energy to discharge, and verify absence of voltage before touching terminals, using a suitable instrument and a check-before/check-after procedure. Then disconnect all six boundary ends from the hub and keep them individually separated for the work/checks. Energized cattle fencing is prohibited near the entire boundary, stations and hub; if discovered, stop work/use and arrange safe isolation and reassessment before handling conductors or resuming use. A switch label or fuse-holder lamp is not an isolation test.
- A qualified installer must design and install the mains enclosure, protective earth (PE), supply protection, bonding, electrode arrangements, and transmitter protectors to applicable Isle of Man/regional and OEM requirements. Do not copy US outlet-faceplate grounding instructions into this installation.
- Retain the actual DogWatch transmitter's required protector(s) and obtain regional OEM approval for this nonstandard boundary configuration. The station boards are not replacements for the OEM protection. A nominal 36 V supply is not permission to touch wet or surge-exposed wiring.

## Materials and Site

| Item | Installation requirement / unresolved evidence |
| :--- | :--- |
| Indicators | Purchased baseline **APEM Q10F5SXXSG02E**, the **no-internal-resistor** option. Published family limits are **20 mA maximum forward current and 5 V maximum reverse voltage**, subject to applicable temperature/pulse conditions. `02` does not mean regulated 2 V operation. Use the qualified board drive, not a direct 36 V connection. |
| Boundary cable | User-confirmed **AMC Oceanflex CM03/05.100** reels labelled `3 CORE (3 x 35/0.30) TINNED BLACK 100 MTR`. AMC **2026 Update V.3** lists **3 x 2.5 mm^2, Class 5 tinned copper, 7.4 mm maximum OD, 60 V max DC, -30 to +70 degrees C** complete-cable service. Product identity is settled; distinguish supplied manufacturing-revision/lot applicability. The standard-based **8.21 ohm/km at 20 degrees C** ceiling is conditional, not a reel measurement: reconcile **0.30 mm labelled strands versus Table 3's 0.26 mm maximum** in [DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md). |
| Core identification | Confirmed colours are **red, black and PLAIN green**, not green/yellow. Identify every core end-to-end and record/label its A/B/C assignment at every termination; no colour-to-net mapping is assigned here. **GREEN/YELLOW MUST NOT BE USED AS AN ACTIVE A, B, OR C CONDUCTOR**, including by re-sleeving it. |
| Cable exposure | The older listing's 105-degree core reference is not a complete-cable rating. Obtain evidence for exposed-weather/UV service, wet conduit, and the required insulation/impulse performance. The 60 V operating rating neither establishes surge withstand nor proves failure at every brief higher voltage. Do not assume armoured, arctic, or mains cable properties. |
| Enclosure | WISKA **COMBI 308**, **polypropylene (PP) with TPE gasket, not polycarbonate**, external dimensions 85 x 85 x 51 mm. Internal usable space must be measured with the actual assembly. Its published IP66 membrane/IP67 specified-gland arrangements are not automatic ratings for a drilled, wired, gel-filled assembly. No continuous submersion is intended. |
| Supports and gel | Essentra **LCBSBM-6-01A-RT** supports and confirmed WISKA **OneGel**, correcting the mistaken MP0100 identity: **single-component 300 ml cartridge, order no. 10108963; no mixing**. Obtain the exact support tolerance/retention drawing and supplied-lot gel process/safety clarification before filling. Do not substitute a related gel formulation's instructions. |
| Environment | Isle of Man, less than 1 km from the coast, with frequent rain, salt and possible condensation. Observed outdoor ambient is approximately **-10 to +30 degrees C**; some boxes receive direct sun. These observations are not lifetime extremes or maximum internal temperatures. Gel, cable, seals, adhesives and electronics need a qualified solar/thermal envelope. |

Route the cable mostly 0.3-1.0 m above ground on timber fencing, with abrasion protection, suitable supports, slack for movement, and no electrical connection to the horizontal supporting metal wires. The supporting fence is not energized. Plastic conduit under driveways/gates can become wet and is not electromagnetic shielding; verify cable suitability, mechanical protection, drainage arrangements, and utility locations before ground work.

**No energized cattle fencing is permitted near the whole 4 km boundary cable, any station or the hub**, as explicitly confirmed by the user. The former **0.5 m / up to 300 m parallel scenario is withdrawn and historical**, not an accepted installation or current energizer-on/off test requirement. Inspect the whole route and maintain the prohibition. If land use changes or the hazard is reintroduced, reassess before use; no numerical safe separation, zero induction or zero lightning exposure is established.

## Hub Wiring

### Functional Matrix

The following is a **functional contact matrix, not a physical terminal-number diagram**. T1 and T2 mean the transmitter's two boundary connections through the required OEM protector arrangement. They do not authorize bypassing those protectors.

| Boundary-cable end | RUN | OFF | TEST |
| :--- | :--- | :--- | :--- |
| Start A | Transmitter T1 | Isolated | +36 V |
| Start B | Transmitter T1 | Isolated | DC negative |
| Start C | Transmitter T1 | Isolated | +36 V |
| End A | Transmitter T2 | Isolated | Isolated |
| End B | Transmitter T2 | Isolated | Isolated |
| End C | Transmitter T2 | Isolated | Isolated |

Use **six independent boundary-end connections**, individually accessible and isolated at the hub in OFF. All three End connections remain **separately isolated in TEST**. Required RUN ties and the TEST positive tie belong on the appropriate **source-side contacts**, never as permanent boundary-side straps. TEST feeds and returns at Start; no additional End return connection is permitted.

The transmitter must be isolated from the TEST source in TEST, and the TEST source isolated from the boundary/transmitter in RUN. Transfer must also preserve isolation: **all old-source connections must break before any new-source connection can make across the entire six-end contact program**, in either direction. Per-pole timing or a centre-off label alone does not establish this global break-before-make requirement.

### Switch and Supply

1. Confirm the actual switch and obtain its manufacturer's contact development, DC load-breaking suitability for the actual circuit, global transfer sequence, mounting details, and applicable insulation conditions. **Kraus & Naimer CA10.A364** is provisional; the current **WAA364 (formerly A364) is eight-pole, 1-0-2 centre-off, 60-degree switching, not six-pole**. The six-end matrix is unchanged and the **two extra poles remain unassigned**. Its 20 A thermal rating does not prove DC breaking or lightning isolation. Previously purchased switch inventory is not evidence of compliance. Do not assign terminal numbers or energize the hub until the exact offered program is accepted.
2. The user confirms **two MEAN WELL LRS-75-36 supplies ORDERED**, each **36 V / 2.1 A / 75.6 W**: **one for TEST and the second a disconnected spare**. No parallel, series, separate-channel or opposite-end feeding is authorized. Verify receipt/nameplates and the intended unit's output setting; ORDERED is not inspected hardware. The earlier LRS-35-36 belief is procurement history, not a third confirmed PSU. LRS-75-36 has adjustable output and hiccup overload protection. Set and record only the voltage range authorized by the final electrical/thermal analysis; do not raise it to compensate for poor visibility.
3. Install the PSU using its actual mounting and ventilation instructions inside a dry, guarded mains enclosure. Do not assume an LRS chassis supply snaps onto DIN rail. A 35 mm rail may carry the compatible fuse holder and other approved rail-mounted parts. Keep mains terminals finger-safe and mains wiring segregated from the field/test wiring as the installer specifies.
4. Verify the specified **Littelfuse 0217002.MXP, 2 A 217-series fuse**, and **Phoenix Contact UK 5-HESILED 60 / 3004139** holder against supplied items and the final source design. The fuse has published DC interrupting data; its unresolved issue here is clearing coordination with cable-limited faults and PSU hiccup behavior. Do not assume every short clears it, or change its value without analysis. The ordered LRS-75-36 does not resolve C5.
5. With sources and field disconnected, verify the accepted wiring against every cell of the functional matrix. Check that no source, protector connection, test lead, jumper or label creates an unintended field-end tie. Static continuity checks supplement, but do not prove, rated DC breaking or transfer timing. Record the accepted terminal drawing separately once the exact hardware is confirmed.

The [WAA364 catalogue contact/link schedule](pcb/ENVIRONMENT_EVIDENCE.md#catalogue-contact-schedule)
is now recorded as design-review evidence, **not the supplied-switch pinout**.
Its eight separate fixed common links remain connected in `0`; do not mistake
them for a common bus or assign two field ends to one link. No catalogue pole
or `1`/`2` detent has been assigned a DogFence wiring or RUN/TEST role.

The [current electrical analysis](pcb/ELECTRICAL.md) and [conditional design bounds](pcb/DESIGN_BOUNDS.md) use **nominal 36 V, a declared 35 V feed floor and a 40.39597 V upper screening value**. These are not hardware-enforced or approved installed limits; the floor must include hub/interface losses, and actual adjustment, tolerance, ripple and startup still need evidence. The earlier **35-37 V proposal was never enforced**, and PSU OVP is not a 37 V limiter. Qualifying the real normal source range is an alternative to imposing a new precision cutoff; it does not settle source-malfunction or GDT recovery safety.

Label the actual detents only after their function is verified; do not assume a particular UP/DOWN orientation:

| Label | Operator meaning |
| :--- | :--- |
| **RUN - RF FENCE SELECTED** | Confirm transmitter and receiver operation before relying on containment. |
| **OFF - SIX ENDS ISOLATED - NO CONTAINMENT** | Neither source connected to the boundary at the hub; not lightning-safe isolation. |
| **TEST - 36 V CABLE TEST - NO CONTAINMENT** | Independent animal containment required. **RESTORE RUN AFTER TEST.** |

## Workshop Assembly

After receiving the prototypes, first dry-fit a complete assembly. Do not drill or prepare all lids until that fit and the process have been accepted. [pcb/ASSEMBLY.md](pcb/ASSEMBLY.md) controls SMT lands, retained holes, pin-pattern, body and GDT forming limits; [pcb/DFM_EVIDENCE.md](pcb/DFM_EVIDENCE.md) preserves supporting evidence and historical parts. The authorized design specifies **16 electrical parts, eight SMT and eight THT**, plus four mounting footprints. R1/R2 are intended **Uni-Royal HP122WF2201T4E**, HP12 / 2512 SMT, 2.2 kohm / 2 W / 1% / +/-100 ppm/C at 25 C reference, with **no resistor holes, axial standoff or lead forming**. D1-D4 remain **Vishay General Semiconductor BYG23T-M3/TR**, SMA. The old 1N4007G/MBE/PR02 selections are retired. Controlled envelopes and design counts are not native-check results, accepted lots or assembled hardware.

1. Match each received board to the reviewed revision, BOM and assembly drawing. Inspect workmanship and run the all-five basic checks in [ACCEPTANCE.md](ACCEPTANCE.md). Board outline is nominally 63 x 56 mm with four 3.2 mm mounting holes; actual thickness and hole tolerances must suit the supports. No forcing leads into undersized holes, reaming finished plated holes, or field PCB soldering is allowed.
2. Check the **Essentra LCBSBM-6-01A-RT** drawing against actual holes and finished board thickness, including fabrication tolerance. The listing's nominal 3.18 mm support hole, 1.57 mm panel and 9.53 mm spacing are not a universal fit guarantee. Verify all four locks engage without board damage or flex. Qualify adhesive retention, surface preparation and the adhesive's cure/dwell conditions on COMBI 308's PP substrate. Use IPA only if accepted by the material/adhesive instructions, and allow the surface to dry fully. Gel is not a permanent structural support.
3. Lay out both lid indicators to suit real viewing angles and internal clearances. The earlier approximately 35-40 mm centre spacing is only a dry-fit starting point. Use the exact APEM cutout tolerance and lid-thickness instructions; the nominal cutout is 10 mm. Deburr without damaging the sealing surface. Install the specified seal, washer and nut in the model's documented order. Published Q10 tightening guidance is **0.20-0.25 Nm, subject to the exact Q10F5SXXSG02E instructions**; use a suitable low-range torque tool and record the instruction revision. Do not over-compress the seal or crack the lid.
4. Position the board with `J_IN` toward the incoming tap wiring and `J_EARTH` toward the earth wiring. In the controlled board view, `J_IN` opens left, `J_EARTH` right, `J_LED_A` north and `J_LED_C` south. The two LED connectors are intentionally oppositely oriented; verify both `+` and `-` markings against the actual assembly drawing rather than assuming matching rotations. D1/D2 cathodes face right; D3/D4 cathodes face left to LED positive, with their anodes right to B. Do not infer all four orientations from the local cathode-right footprint name.
5. Trial-fit **all** contents: three WAGO 221-613s, actual incoming/outgoing cable and glands, three pigtails, earth conductors where applicable, supports, both LED bodies, lid seals, plugs, and a suitable terminal screwdriver. Allow cable bend radii, wire strain relief and lid service slack. Close the lid fully and verify no wire or LED body pushes `GDT_AC` down. Preserve **at least 2.00 mm gap under the whole raised body/electrode/lead span above the highest finished PCB top surface** before gel. Its development target is **body underside 2.50 +/-0.25 mm, complete assembled height <=8.50 mm**, not actual forming-process approval. HP12 resistors are surface-mounted; do not apply retired PR02 standoff/forming instructions. Inspect earth GDTs at the unchanged **9.00 mm centre pitch** against the controlled maximum-body/pose envelopes, not an assumed 1 mm air gap. Do not rely on solder mask, tape or gel to excuse contact or bad forming.
6. Prepare labelled A/B/C pigtails, nominally 2.5 mm^2, with lengths determined by the dry-fit; approximately 120-150 mm is a starting allowance, not a prescribed bend geometry. Use a separately identified permissible active conductor for each core. Follow the terminal manufacturers' conductor range, strip length, ferrule policy and screw torque. Do not solder-tin stranded wire ends, put multiple wires in an unapproved clamp, or leave stray/exposed strands.
7. Connect each pigtail between its own WAGO and the matching `J_IN` **A, B or C** marking. Connect each actual APEM anode to its channel's `+` and cathode to `-`; verify the supplied lead identification rather than relying solely on assumed red/black colours. **The implemented negative shunts do not protect reversed LED flying leads or establish pulse-safe reversal survival.** The user accepts indicator damage from accidental low-voltage installation polarity errors and requires installation spares, with quantity still to allocate. The recorded 80 LEDs are already two short of the 82 field requirement before test use or spares. Check before power; correct suspect wiring and replace damaged indicators while isolated, not by leaving a dark/miswired branch powered. This does not waive safe wiring or continuous TEST thermal requirements.
8. Seat one conductor per WAGO port, close each lever and perform a gentle retention check. The WAGO 221-613 strip marking is the authority (nominally 13 mm); use the PCB terminal's own specification for its end of a pigtail. Record torques, component identities, clearances and photographs before gel makes inspection harder.

Allow for J_EARTH's **1.00 mm nominal body-envelope overhang, 1.30 mm including pose/routed-edge tolerance**, and courtyard east edge **X=161.35 mm** in the dry-fit. The body boxes are now controlled; actual lot, support/enclosure fit and wire/tool access remain to accept.

All fourteen stitching vias retain their **1.00 mm nominal drill / 1.80 mm copper and positions**, but are intentionally **UNTENTED on both sides, with nominal 1.80 mm mask openings, no via paste and no fill/plug/cap**. Adjacent same-net rail-via mask openings intentionally overlap; this is distinct from an SMT mask/paste aperture over a via hole or annulus, which is not permitted. Inspect the actual solder/cleanliness process and processed data per ORDERING/ACCEPTANCE. Neither exposed ENIG nor OneGel seals a via.

## Field Mounting

1. Label stations by distance, **0 m through 4000 m**, with A/C lens identification and the direction from Start toward End. Orient the lid toward the patrol track at the angles used for the 5 m visibility acceptance test.
2. Mount boxes raised, typically **0.8-1.2 m above ground** where safe and accessible, away from strimmers, standing water and predictable animal/mechanical damage. Use the enclosure's approved mounting bracket or mounting points. On timber, choose suitable corrosion-resistant fasteners for the post and bracket; on other supports, use an accepted UV/corrosion-resistant mounting method without crushing the enclosure or electrically joining fence conductors to metalwork. Do not make unapproved penetrations through the sealing envelope.
3. Prefer downward cable entries. Form drip loops below the entries, approximately 50 mm where compatible with the cable's minimum bend radius, so runoff does not lead into the gland. Select each gland by the **measured jacket diameter**, clamping/sealing range, enclosure thread/seal system and exposure, not just by the label M20. Do not assume one ordinary gland seals two cables, or that a conduit fitting seals the cable. Fit approved plugs/seals to unused entries.
4. Remove only enough jacket for the accepted layout, keeping the jacket under the gland's sealing/strain-relief area. Maintain A-to-A, B-to-B and C-to-C continuity in the three independent WAGO splices. Support the cable externally so the splices, PCB taps and lid leads carry no cable tension. Check every termination before closing the box.
5. Install earth connections **only to the accepted site drawing**. At the five earth-connected stations, use `J_EARTH`, never an A/B/C terminal. Standard stations leave the external `J_EARTH` connection empty; they have no assured local common-mode discharge path. The three earth terminal positions share a PCB net, but their ratings cannot simply be added and equal surge-current sharing is not established.

The user's proposal to share local earth between the DogWatch protection and the two shed-end boards must be reviewed against the **actual building PE/electrodes**, regional OEM instructions, and touch/step-potential and bonding requirements. Do not install arbitrary unbonded rods, directly earth a fence core, or assume DC negative should be earth-bonded. Recorded rod/clamp hardware, including 5/8 inch clamp inventory and paired 2.5 mm^2 green/yellow leads, is not approval of electrode placement, conductor sizing or multiwire clamping. The installer must specify compatible clamps, conductor routing and mechanical protection, inspectable connections, and any electrodes/bonds. Check buried services before any electrode or conduit work. Never remove protective earth casually as part of fault diagnosis.

## Commissioning and Diagnosis

### Optional DMM Checks

These are low-voltage diagnostic checks, not insulation or arrester qualification:

1. Secure animals and isolate **all six boundary ends from the hub, transmitter, PSU and every backup source** as described in Safety First. Both physical cable ends are at the shed. Verify de-energization before selecting resistance mode. Do not use resistance mode on RUN or TEST wiring.
2. Measure **Start A to End A**, then **Start B to End B**, then **Start C to End C**, leaving the other ends separately isolated. Record lead resistance/compensation, instrument range and uncertainty, cable temperature and the commissioning baseline for each core. An ideal **individual 4 km / 2.5 mm^2 copper core is about 28 ohms at 20 degrees C**, not zero and not a three-core parallel-loop reading. Use verified cable resistance/tolerance data and installed connection losses to set actual limits, not an arbitrary tolerance around 28 ohms.
3. Unexpected or changing readings require sectional investigation. Connected indicator/protection branches can affect measurements; follow the final circuit's measurement procedure and disconnect electronics for cable-only measurements where necessary. These checks aid diagnosis but do not replace LED span localization or rule out every short.
4. **Never apply a high-voltage insulation tester/megger through connected boards, LEDs, transmitter, protectors or PSU.** Any cable-only insulation test requires all electronics removed from the test circuit and an installer-approved test voltage/procedure appropriate to the actual cable. A DMM-open GDT only shows no detected conduction at that meter's test conditions; it does not prove that the arrester will fire or survive a surge.

### Normal Commissioning

Complete the controlled [acceptance programme](ACCEPTANCE.md) on the approved prototype configuration before field release. Initial workmanship, dry-fit and normal electrical checks precede potting the selected qualification units; potted thermal/material tests are still required before rollout. Record the final source setting and per-station currents/voltages instead of copying old aggregate-current or uniform-brightness assumptions.

Use the [HP12/BYG23T model](pcb/DESIGN_BOUNDS.md) for the selected resistance envelope, nonuniform far-end current and upper current/power screens, not retired PR02 numbers. These are conditional calculations, not measured source limits, exhaustive minimum current or guaranteed brightness. The selected 2 W resistors still generate about **0.50 W each** at the nominal comparison point. Their rating derates from 2 W at 70 C ambient to zero at 155 C; SMT heat flow does not lower the loss or prove cooler operation. Actual thermal interfaces and 5 m daylight results remain unqualified, and no OneGel thermal test has been performed.

In a healthy qualified TEST installation, both indicators should be on at all **41 stations**, including the separate shed-end stations. Same-end feeding creates a brightness/current gradient; the final minimum current must still pass 5 m daylight visibility at real angles. In RUN, verify the actual transmitter, boundary field and receiver behavior with the required protectors fitted. Indicators should not give misleading light in RUN; their darkness is **not** proof that a series diode blocks RF or that the added circuit is transparent. Confirm that the whole-boundary cattle-fence prohibition remains satisfied; energizer-on/off testing is not part of the accepted installation. Series-diode leakage and possible OFF-state glow still need actual observation, not an ideal-model blackout assumption.

### Clean-Cut Indications

For **one clean damage site** in a span, healthy boards/LEDs/GDTs, and no other inter-core shorts, the required steady-state truth table is:

| Cut cores | Before the cut | After the cut |
| :--- | :--- | :--- |
| A | Both on | A off, C on |
| B | Both on | Both off |
| C | Both on | A on, C off |
| A + B | Both on | Both off |
| A + C | Both on | Both off |
| B + C | Both on | Both off |
| A + B + C | Both on | Both off |

The aim is the damaged **100 m span**, not exact broken-core classification. B-only and several multi-core cuts have the same indication. All-on indications do not certify freedom from shorts; an A-C short, for example, can create backfeed and mask an open. A failed local LED, loose tap, damaged branch or failed GDT can also mislead the display. An isolated dark station with healthy stations beyond it calls for local inspection, not an automatic conclusion that the preceding cable span is cut.

### Repair and Retest

1. Secure independent animal containment and notify the responsible operator. Use only the accepted hub switching procedure to select TEST, with the transmitter isolated and the supply at its qualified setting. Typical TEST use is one to two hours; **continuous-safe normal TEST is required** for accidental extended use, but this remains a qualification requirement, not a demonstrated property of the current draft. A timeout or automatic return to RUN is not the baseline safeguard.
2. Check the **0 m station first**, then follow increasing distance and record both LED states at every station. If the source-end indicators are wrong, investigate the hub, PSU/fuse/protective shutdown, polarity and local assembly before assigning a cable fault. Do not repeatedly reset protection or replace fuses without finding the cause.
3. Use the **first applicable LED-state transition** to identify the span between adjacent stations. Include the final **3900-4000 m** span and inspect the 4000 m station separately from the 0 m station at the shed. LEDs show a steady network state, not a timed sequence.
4. Isolate all sources and six ends before opening wiring. Inspect/repair the identified span and its terminations using an approved cable joint or replacement section with suitable mechanical and environmental protection. Replace defective PCB assemblies rather than improvising field soldering. Investigate shorts, earth faults and local indicator failures separately when the pattern does not fit the clean-cut assumptions.
5. Restore the accepted TEST configuration and check **all 41 stations again**. Multiple damage sites may only become apparent after the first repair; repeat location, isolation, repair and retest until the required normal indications and electrical checks are restored.
6. Close and reseal repaired boxes using the qualified material process. **The operator must restore RUN**, verify the transmitter has returned to normal, and check boundary/receiver operation before removing independent animal containment. TEST/OFF do not automatically restore the RF fence.

## Gel and Service

**Hold OneGel application until the supplied-lot process and compatibility are accepted.** Use the single-component cartridge without mixing; do not add a catalyst, prescribe a heat cure or assume self-levelling pour behaviour. WISKA's published **20 min versus no curing time**, and **-20 to +90 versus -60 to +200 degrees C** temperature entries require a dated OneGel-specific clarification, including separate application/service limits. Do not prescribe a curing interval or select the wider range as the assembly envelope. **No thermal conductivity is published in the reviewed sources.** See [the manufacturer evidence and conflicts](pcb/ENVIRONMENT_EVIDENCE.md#wiska-onegel).

Retain the supplied cartridge/lot and storage record, technical/safety document revisions, preparation and application conditions, accepted coverage/fill/vent method and re-entry instructions. Confirm compatibility with COMBI 308 PP/TPE, the exact Essentra supports/adhesive, cable sheath/core insulation, WAGO 221-613 contacts/housings, LED rear seals/leads, components and residual assembly materials. No fixed fill volume or usable cartridge yield is established by the historical quantity estimate in MATERIALS.

1. Complete the documented pre-potting inspections and electrical checks on a clean, dry, unpowered assembly. Photograph the wiring and record the board/parts revision and measured fit. Leave the designated reference prototype unpotted.
2. Prepare the assembly and material exactly as accepted, including compatible cleaning, full drying and any adhesive dwell requirements. Protect the enclosure gasket and gland sealing surfaces. Do not apply OneGel over water, salt or incompatible flux residue.
3. Dispense from the cartridge using the accepted fill level, orientation and venting process to obtain the specified coverage, including beneath the PCB and around the actual wiring. A closed fill/vent method may be used only if the manufacturer-compatible process has been validated on the real assembly. A vent overflowing does not demonstrate a void-free interior; do not force an arbitrary full-to-the-roof fill or add unapproved ports. Record actual material consumption and any void/coverage inspection.
4. Follow the clarified application/post-application conditions and refit the accepted plugs, glands and lid seals at their specified torques. Perform the post-process normal electrical, fit, sealing and instrumented thermal checks in [ACCEPTANCE.md](ACCEPTANCE.md). No hermetic seal, automatic IP68 rating or multi-decade lifetime follows from adding gel.

For service, isolate the installation first and follow the exact material's accepted re-entry, PPE, cleaning and repair instructions. Do not assume OneGel always peels off cleanly by hand or that fresh material may be dispensed over contaminated or removed gel without approval. Replace damaged seals, supports, glands or assemblies as needed; re-inspect and retest after disturbance. Agree inspection intervals with the installer for this coastal site and inspect after suspected surge damage, water ingress or mechanical impact. Keep installation, repair, source-setting and qualification records with the live release checklist in [REMEDIATION.md](REMEDIATION.md).
