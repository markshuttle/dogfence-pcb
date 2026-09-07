# Installation and Operation

**Draft revision: 1.2.0-dev. Engineering and release hold.**

This manual describes the agreed installation and operating requirements, not an approved or qualified hardware release. [REMEDIATION.md](REMEDIATION.md) controls settled requirements, the live checklist, and [release gates A/B/C](REMEDIATION.md#release-gates). [pcb/ELECTRICAL.md](pcb/ELECTRICAL.md) records the implemented DC model and unresolved design decisions; **no new LED reversal/pulse protection or powered-GDT shutdown circuit is selected or fitted**. File checks and documentation do not close C4 (LED reversal), C5 (fault/follow-current coordination), continuous thermal safety, or site qualification. Keep the engineering publication holds and do not install this draft as qualified hardware.

Use [ACCEPTANCE.md](ACCEPTANCE.md) for controlled prototype qualification and commissioning records, and [RISKS.md](RISKS.md) for limitations. Do not roll out an unqualified design or rely on it for containment or lightning protection.

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
- Before wiring or resistance checks, isolate the transmitter, TEST PSU, their mains feeds and every battery/backup source using the accepted safe-isolation procedure. Prevent reconnection, allow stored energy to discharge, and verify absence of voltage before touching terminals, using a suitable instrument and a check-before/check-after procedure. Then disconnect all six boundary ends from the hub and keep them individually separated for the work/checks. Coordinate isolation of nearby energizers that could couple into the circuit before handling field conductors. A switch label or fuse-holder lamp is not an isolation test.
- A qualified installer must design and install the mains enclosure, protective earth (PE), supply protection, bonding, electrode arrangements, and transmitter protectors to applicable Isle of Man/regional and OEM requirements. Do not copy US outlet-faceplate grounding instructions into this installation.
- Retain the actual DogWatch transmitter's required protector(s) and obtain regional OEM approval for this nonstandard boundary configuration. The station boards are not replacements for the OEM protection. A nominal 36 V supply is not permission to touch wet or surge-exposed wiring.

## Materials and Site

| Item | Installation requirement / unresolved evidence |
| :--- | :--- |
| Indicators | Purchased baseline **APEM Q10F5SXXSG02E**, the **no-internal-resistor** option. Published family limits are **20 mA maximum forward current and 5 V maximum reverse voltage**, subject to applicable temperature/pulse conditions. `02` does not mean regulated 2 V operation. Use the qualified board drive, not a direct 36 V connection. |
| Boundary cable | Likely Oceanflex **CM03/05.100**, supplier code **P01018**, but confirm the actual reel/markings. The listing describes three tinned-copper 2.5 mm^2 cores, 35/0.30 mm strands per core, 7.3 mm maximum outside diameter, **60 V maximum**, and **-15 to +70 degrees C** complete-cable working temperature. Obtain maximum conductor resistance and actual core colours. |
| Core identification | Identify every core end-to-end and label it A, B, or C at every termination. Do not infer colours from an incomplete supplier colour table. **GREEN/YELLOW MUST NOT BE USED AS AN ACTIVE A, B, OR C CONDUCTOR**, including by re-sleeving it. If the purchased cable cannot provide three permissible active cores, stop for an approved cable solution. |
| Cable exposure | The 105-degree ISO 6722 reference is for the cores, not the complete cable. Obtain evidence for exposed-weather/UV service, wet conduit, and the required insulation/impulse performance. The 60 V operating rating neither establishes surge withstand nor proves failure at every brief higher voltage. Do not assume armoured, arctic, or mains cable properties. |
| Enclosure | WISKA **COMBI 308**, external dimensions 85 x 85 x 51 mm. Internal usable space must be measured with the actual assembly. Its published IP66 membrane/IP67 specified-gland arrangements are not automatic ratings for a drilled, wired, gel-filled assembly. No continuous submersion is intended. |
| Supports and gel | Essentra **LCBSBM-6-01A-RT** supports and WISKA **MP0100** gel. Obtain the exact support tolerance/retention drawing and the supplied gel's technical/process and safety documents. Do not substitute a related gel formulation's instructions. |
| Environment | Isle of Man, less than 1 km from the coast, with frequent rain, salt and possible condensation. Observed outdoor ambient is approximately **-10 to +30 degrees C**; some boxes receive direct sun. These observations are not lifetime extremes or maximum internal temperatures. Gel, cable, seals, adhesives and electronics need a qualified solar/thermal envelope. |

Route the cable mostly 0.3-1.0 m above ground on timber fencing, with abrasion protection, suitable supports, slack for movement, and no electrical connection to the horizontal supporting metal wires. The supporting fence is not energized. Plastic conduit under driveways/gates can become wet and is not electromagnetic shielding; verify cable suitability, mechanical protection, drainage arrangements, and utility locations before ground work.

A separate energized cattle wire may run **at least 0.5 m away for up to 300 m in parallel**. Maintain clearance with allowance for wind, sag and animal movement, and increase separation where practical. This is the agreed repetitive-pulse qualification exposure, **not proof of interference-safe clearance**. Record the actual energizer and routing for RUN and TEST qualification.

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

1. Confirm the actual switch and obtain its manufacturer's contact development, DC load-breaking suitability for the actual circuit, global transfer sequence, mounting details, and applicable insulation conditions. **Kraus & Naimer CA10.A362** is a six-pole centre-off sourcing candidate, not an approved pinout. Its 20 A thermal rating does not prove DC breaking or lightning isolation. Previously purchased switch inventory is not evidence of compliance. Do not assign terminal numbers or energize the hub until the exact program is accepted.
2. Confirm the PSU nameplate. The user believes the purchased unit is **Mean Well LRS-35-36 (36 V / 1 A / 36 W)**. **LRS-75-36 (36 V / 2.1 A / 75.6 W)** is the preferred capacity-margin candidate, not a confirmed purchase. Both have adjustable output and hiccup overload protection. Set and record only the voltage range authorized by the final electrical/thermal analysis; do not raise it to compensate for poor visibility.
3. Install the PSU using its actual mounting and ventilation instructions inside a dry, guarded mains enclosure. Do not assume an LRS chassis supply snaps onto DIN rail. A 35 mm rail may carry the compatible fuse holder and other approved rail-mounted parts. Keep mains terminals finger-safe and mains wiring segregated from the field/test wiring as the installer specifies.
4. Verify the specified **Littelfuse 0217002.MXP, 2 A 217-series fuse**, and **Phoenix Contact UK 5-HESILED 60 / 3004139** holder against supplied items and the final source design. The fuse has published DC interrupting data; its unresolved issue here is clearing coordination with cable-limited faults and PSU hiccup behavior. Do not assume every short clears it, or change its value without analysis. The PSU upgrade does not resolve C5.
5. With sources and field disconnected, verify the accepted wiring against every cell of the functional matrix. Check that no source, protector connection, test lead, jumper or label creates an unintended field-end tie. Static continuity checks supplement, but do not prove, rated DC breaking or transfer timing. Record the accepted terminal drawing separately once the exact hardware is confirmed.

Label the actual detents only after their function is verified; do not assume a particular UP/DOWN orientation:

| Label | Operator meaning |
| :--- | :--- |
| **RUN - RF FENCE SELECTED** | Confirm transmitter and receiver operation before relying on containment. |
| **OFF - SIX ENDS ISOLATED - NO CONTAINMENT** | Neither source connected to the boundary at the hub; not lightning-safe isolation. |
| **TEST - 36 V CABLE TEST - NO CONTAINMENT** | Independent animal containment required. **RESTORE RUN AFTER TEST.** |

## Workshop Assembly

First dry-fit a complete prototype. Do not drill or prepare all lids until that fit and the process have been accepted.

1. Match each received board to the reviewed revision, BOM and assembly drawing. Inspect workmanship and run the all-five basic checks in [ACCEPTANCE.md](ACCEPTANCE.md). Board outline is nominally 63 x 56 mm with four 3.2 mm mounting holes; actual thickness and hole tolerances must suit the supports. No forcing leads into undersized holes, reaming finished plated holes, or field PCB soldering is allowed.
2. Check the **Essentra LCBSBM-6-01A-RT** drawing against actual holes and finished board thickness, including fabrication tolerance. The listing's nominal 3.18 mm support hole, 1.57 mm panel and 9.53 mm spacing are not a universal fit guarantee. Verify all four locks engage without board damage or flex. Qualify adhesive retention, surface preparation and cure/dwell conditions on the actual enclosure plastic. Use IPA only if accepted by the material/adhesive instructions, and allow the surface to dry fully. Do not assume cured gel becomes a permanent structural support.
3. Lay out both lid indicators to suit real viewing angles and internal clearances. The earlier approximately 35-40 mm centre spacing is only a dry-fit starting point. Use the exact APEM cutout tolerance and lid-thickness instructions; the nominal cutout is 10 mm. Deburr without damaging the sealing surface. Install the specified seal, washer and nut in the model's documented order. Published Q10 tightening guidance is **0.20-0.25 Nm, subject to the exact Q10F5SXXSG02E instructions**; use a suitable low-range torque tool and record the instruction revision. Do not over-compress the seal or crack the lid.
4. Position the board with `J_IN` toward the incoming tap wiring and `J_EARTH` toward the earth wiring. In the controlled board view, `J_IN` opens left, `J_EARTH` right, `J_LED_A` north and `J_LED_C` south. The two LED connectors are intentionally oppositely oriented; verify both `+` and `-` markings against the actual assembly drawing rather than assuming matching rotations.
5. Trial-fit **all** contents: three WAGO 221-613s, actual incoming/outgoing cable and glands, three pigtails, earth conductors where applicable, supports, both LED bodies, lid seals, plugs, and a suitable terminal screwdriver. Allow cable bend radii, wire strain relief and lid service slack. Close the lid fully and verify no wire or LED body pushes the axial `GDT_AC` bridge down. Preserve its **at least 2.0 mm physical standoff above the PCB** and the earth GDTs' 9.00 mm centre pitch; actual body tolerances still require clearance inspection. Do not rely on solder mask, tape or gel to excuse contact or bad forming.
6. Prepare labelled A/B/C pigtails, nominally 2.5 mm^2, with lengths determined by the dry-fit; approximately 120-150 mm is a starting allowance, not a prescribed bend geometry. Use a separately identified permissible active conductor for each core. Follow the terminal manufacturers' conductor range, strip length, ferrule policy and screw torque. Do not solder-tin stranded wire ends, put multiple wires in an unapproved clamp, or leave stray/exposed strands.
7. Connect each pigtail between its own WAGO and the matching `J_IN` **A, B or C** marking. Connect each actual APEM anode to its channel's `+` and cathode to `-`; verify the supplied lead identification rather than relying solely on assumed red/black colours. **The existing series diode does not guarantee safety if an LED or the supply is reversed.** Correct suspect wiring while isolated, not by leaving it powered to see whether it stays dark.
8. Seat one conductor per WAGO port, close each lever and perform a gentle retention check. The WAGO 221-613 strip marking is the authority (nominally 13 mm); use the PCB terminal's own specification for its end of a pigtail. Record torques, component identities, clearances and photographs before gel makes inspection harder.

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

In a healthy qualified TEST installation, both indicators should be on at all **41 stations**, including the separate shed-end stations. Same-end feeding creates a brightness/current gradient; the final minimum current must still pass 5 m daylight visibility at real angles. In RUN, verify the actual transmitter, boundary field and receiver behavior with the required protectors fitted. Indicators should not give misleading light in RUN; their darkness is **not** proof that a series diode blocks RF or that the added circuit is transparent. Test the specified cattle-energizer off/on exposure in both modes.

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

1. Secure independent animal containment and notify the responsible operator. Use only the accepted hub switching procedure to select TEST, with the transmitter isolated and the supply at its qualified setting. Typical TEST use is one to two hours; **continuous-safe normal TEST is required** for accidental extended use, but this remains a qualification requirement, not a claim about the legacy board. A timeout or automatic return to RUN is not the baseline safeguard.
2. Check the **0 m station first**, then follow increasing distance and record both LED states at every station. If the source-end indicators are wrong, investigate the hub, PSU/fuse/protective shutdown, polarity and local assembly before assigning a cable fault. Do not repeatedly reset protection or replace fuses without finding the cause.
3. Use the **first applicable LED-state transition** to identify the span between adjacent stations. Include the final **3900-4000 m** span and inspect the 4000 m station separately from the 0 m station at the shed. LEDs show a steady network state, not a timed sequence.
4. Isolate all sources and six ends before opening wiring. Inspect/repair the identified span and its terminations using an approved cable joint or replacement section with suitable mechanical and environmental protection. Replace defective PCB assemblies rather than improvising field soldering. Investigate shorts, earth faults and local indicator failures separately when the pattern does not fit the clean-cut assumptions.
5. Restore the accepted TEST configuration and check **all 41 stations again**. Multiple damage sites may only become apparent after the first repair; repeat location, isolation, repair and retest until the required normal indications and electrical checks are restored.
6. Close and reseal repaired boxes using the qualified material process. **The operator must restore RUN**, verify the transmitter has returned to normal, and check boundary/receiver operation before removing independent animal containment. TEST/OFF do not automatically restore the RF fence.

## Gel and Service

**Hold pouring until the exact MP0100 process is accepted.** Obtain and retain the supplied product's formulation/variant, batch and shelf-life information, technical and safety document revisions, mixing method/ratio if applicable, preparation requirements, working time, temperature limits, fill/vent method, cure conditions and re-entry instructions. Confirm compatibility with COMBI plastic and seals, Essentra supports/adhesive, cable insulation, WAGO connectors, LED rear seals/leads, components and residual assembly materials. This manual intentionally supplies no invented mix ratio, fixed mixing time, cure time or fill volume.

1. Complete the documented pre-potting inspections and electrical checks on a clean, dry, unpowered assembly. Photograph the wiring and record the board/parts revision and measured fit. Leave the designated reference prototype unpotted.
2. Prepare the assembly and material exactly as accepted, including compatible cleaning, full drying and any adhesive dwell requirements. Protect the enclosure gasket and gland sealing surfaces. Do not assume gel cures correctly over water, salt or incompatible flux residue.
3. Use the accepted fill level, orientation and venting process to obtain the specified coverage, including beneath the PCB and around the actual wiring. A closed fill/vent method may be used only if the manufacturer-compatible process has been validated on the real assembly. A vent overflowing does not demonstrate a void-free interior; do not force an arbitrary full-to-the-roof fill or add unapproved ports. Record actual material consumption and any void/coverage inspection.
4. Observe the specified cure/environmental conditions and refit the accepted plugs, glands and lid seals at their specified torques. Perform the post-process normal electrical, fit, sealing and instrumented thermal checks in [ACCEPTANCE.md](ACCEPTANCE.md). No hermetic seal, automatic IP68 rating or multi-decade lifetime follows from adding gel.

For service, isolate the installation first and follow the exact material's accepted re-entry, PPE, cleaning and repair instructions. Do not assume gel always peels off cleanly by hand or that arbitrary fresh gel can be poured over contaminated cured material. Replace damaged seals, supports, glands or assemblies as needed; re-inspect and retest after disturbance. Agree inspection intervals with the installer for this coastal site and inspect after suspected surge damage, water ingress or mechanical impact. Keep installation, repair, source-setting and qualification records with the live release checklist in [REMEDIATION.md](REMEDIATION.md).
