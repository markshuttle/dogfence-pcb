# Dog Fence Indicator & Surge Protection System

**Draft hardware revision: 1.2.0-dev. Reviewed baseline: 1.1.0. Manufacturing and field release remain on hold.**

This is the specification for a 4 km DogWatch SmartFence boundary with local DC fault indicators and GDT surge paths. It is not a board-level surge rating, a completed qualification report, or permission to upload the existing manufacturing files.

[REMEDIATION.md](REMEDIATION.md) records the agreed requirements, issue evidence, and release gates. The design sources are the working schematic, PCB, project settings/rules, and libraries under `pcb/`, with reviewed sourcing in `pcb/BOM.csv`. Generated `build/` files, backup archives, and `tmp/` copies are not design authorities. [Electrical analysis](pcb/ELECTRICAL.md) and [controlled assembly notes](pcb/ASSEMBLY.md) distinguish implemented changes from unresolved protection, fit and process decisions. `pcb/verification.json` enforces the engineering publication holds. Revision labels and documentation changes alone do not establish hardware qualification.

## 1. Deployment Baseline

| Item | Agreed requirement |
| :--- | :--- |
| Stations | **41**, at 0, 100, ..., 4000 m, covering 40 diagnostic spans. The 0 km and 4 km stations are separate boards at the shed. |
| Station types | **36 standard + 5 earth-connected**, retaining earth-connected locations at 0, 1000, 2000, 3000, and 4000 m. Five locations do not imply five independent electrodes. |
| Field equipment | One identical, fully populated board and two external LEDs per station: **41 boards, 82 LEDs, 164 supports, and 123 WAGO 221-613 splices**. |
| Initial order | **Five fully assembled JLCPCB boards**, all required SMT and THT parts fitted. No field soldering. Prototype allocation and later production/spares are separate decisions. |
| Fabrication | Readily available **FR-4, two layers, 2 oz / 70 micrometres copper on both F.Cu and B.Cu, ENIG, nominal 1.6 mm finished thickness**. Green soldermask is the quote default, not a new performance qualification. No imposed high-Tg laminate, gold thickness upgrade, or filled-via process. |
| Enclosure | WISKA COMBI 308 with Essentra LCBSBM-6-01A-RT supports and WISKA **OneGel**, subject to assembled fit and process acceptance. Raised installation, not continuous submersion. |
| TEST duty | Nominal 36 V DC, usually one to two hours. **Continuous-safe normal TEST** is required for accidental extended operation; a timer is not the baseline safeguard. Fault/surge safety needs separate evidence. |
| Visibility | ON/OFF distinguishable at **5 m in full daylight**, at the final minimum field current and actual viewing angles. |

[MATERIALS.md](MATERIALS.md) separates purchases from requirements. In particular, the **80 purchased LEDs remain recorded as 80**, leaving a field shortfall of **2** before prototype losses or spares. Enclosure/gland quantities and retained test units must also be allocated; a five-board prototype order is not five proven field spares.

## 2. Operation And Fault Localization

### Hub Contact Matrix

Both physical ends of the boundary cable return to the shed. Use **six independent cable-end connections** and this functional matrix; map it to physical terminals only after the exact switch contact program is approved.

| Boundary-cable end | RUN | OFF | TEST |
| :--- | :--- | :--- | :--- |
| Start A | Transmitter T1 | Isolated | +36 V |
| Start B | Transmitter T1 | Isolated | DC negative |
| Start C | Transmitter T1 | Isolated | +36 V |
| End A | Transmitter T2 | Isolated | Isolated |
| End B | Transmitter T2 | Isolated | Isolated |
| End C | Transmitter T2 | Isolated | Isolated |

Required RUN ties and TEST positive ties belong on the source-side contacts, not on permanent field-end straps. End A/B/C remain individually open in TEST; all six ends are individually isolated in OFF. Do not use an opposite-end B return, connect both B ends to negative, or retain an End A/C common connection: these defeat the agreed cut indication. No reverse-feed selector, automatic core classifier, or automatic return to RUN is required.

The provisional switch is **Kraus & Naimer CA10.A364**, replacing A362. The 10/2025 manufacturer pocketbook calls the current program **WAA364, formerly A364: eight poles, 1-0-2 centre-off, 60-degree switching**. Six independent cable ends remain required; the extra poles have no assigned function. Its 20 A thermal rating and ON/OFF-only DC table do not approve this changeover. Obtain the exact supplied contact development, factory links, DC application approval and **global transfer sequence**, ensuring the transmitter and DC supply cannot connect during transfer. No physical terminal numbers are assigned. OFF is not demonstrated lightning isolation. Sources: [environment/hub evidence](pcb/ENVIRONMENT_EVIDENCE.md#ca10a364-switch).

**TEST and OFF disable RF containment.** Provide clear RUN/OFF/TEST and fence-inactive labeling/indication, independent animal containment during testing, and an explicit operator return to RUN. See [INSTALL.md](INSTALL.md) for the controlled operating instructions and [RISKS.md](RISKS.md) for fault/earthing limitations.

### Indication For A Clean Cut

With healthy indicators/GDTs, no additional inter-core shorts, and one cut site:

| Cut cores | Stations before cut | Stations after cut |
| :--- | :--- | :--- |
| A | Both on | A off, C on |
| B | Both on | Both off |
| C | Both on | A on, C off |
| A + B | Both on | Both off |
| A + C | Both on | Both off |
| B + C | Both on | Both off |
| A + B + C | Both on | Both off |

Use the first applicable state transition to identify the adjacent 100 m span, including 3900-4000 m. Exact broken-core identification is not required. For multiple sites, repair the first fault and repeat TEST. Mixed open/short faults, failed local indicators, and failed GDTs need separate troubleshooting; not every dark LED proves a cable cut.

### Station Connections

Three **WAGO 221-613** three-way splices maintain A/B/C cable continuity and provide short 2.5 mm^2 taps to `J_IN`. Normal perimeter current does **not** pass through every PCB's rails; each PCB draws its local indicator current. Surge current through a board is a different design case.

| Baseline circuit path | Connection |
| :--- | :--- |
| A indicator | WIRE_A -> R1 (2.2 kohm) -> D1 -> external LED A -> WIRE_B |
| C indicator | WIRE_C -> R2 (2.2 kohm) -> D2 -> external LED C -> WIRE_B |
| Differential GDTs | GDT_AB between A/B, GDT_BC between B/C, GDT_AC between A/C |
| Earth GDTs | GDT_A_E, GDT_B_E, GDT_C_E each connect their respective core to the separate EARTH bus |
| Earth terminal | All three `J_EARTH` pins connect to EARTH copper. The terminal and GDTs remain fitted on standard boards; their external earth terminal is left unwired. |

In RUN, all three cores are paralleled at each transmitter end. Their nominal combined copper area is 7.5 mm^2; the illustrative 27.6 ohm/core model gives 9.2 ohms for three healthy parallel cores. This is not proof of transmitter compatibility. Healthy symmetry reduces differential indicator loading, but real cable imbalance, faults, protection capacitance, and earth coupling must be checked with the actual transmitter and receiver. Do not describe the boards as RF-invisible or add a blanket earth plane across the isolated fence nets.

## 3. Electrical Limits And Open Protection Work

The **forward-only calculated baseline**, not a measurement, uses 41 stations, an ideal 36 V source, 27.6 ohms per 4 km core, 2.2 kohm per LED branch, and 2.8 V combined LED/rectifier forward drop:

| Configuration | Calculated source load | LED current |
| :--- | :--- | :--- |
| Healthy 4 km, same-end TEST | **0.8477 A / 30.52 W** | **15.09 mA near source -> 8.04 mA at far end** |
| Five boards with negligible cable drop | **0.1509 A / 5.43 W** | About 15.09 mA each |
| All 41 boards with negligible cable drop | **1.2375 A / 44.55 W** | About 15.09 mA each |
| Illustrative sensitivity: 40 ohms/core and 4.0 V combined forward drop | Not a guaranteed cable/temperature limit | About **6.21 mA** at the far end |

Recalculate tolerances, shorts, and observability for the final protection circuit. The forward-only model does not establish safe reverse bias, RF behavior, surge survival, thermal limits, or daylight visibility. Neither the 8.04 mA result nor the illustrative 6.21 mA result is an accepted worst-case current until the cable and component bounds are known.

**Two MEAN WELL LRS-75-36 supplies (each 36 V, 2.1 A, 75.6 W) are ORDERED. The user has allocated one to TEST and one as a disconnected spare.** There is no parallel, series, opposite-end or second-channel supply connection. Verify receipt/nameplates and the working unit's setting, 32.4-39.6 V adjustment, tolerances, derating and hiccup behavior. The earlier LRS-35-36 belief is procurement history, not a third confirmed PSU. The capacity increase does not solve source/fuse/GDT coordination.

At nominal source-end current, each 2.2 kohm resistor dissipates about **0.50 W**, approximately **1 W per board in the two resistors alone**. Vishay MBE0414's **1 W power-mode** rating differs from its **0.65 W standard-mode** rating and associated derating conditions. A nominal 50% power-mode load is not evidence of cool operation or long life inside gel. Continuous potted thermal measurements must cover credible supply/solar conditions and component limits.

The implemented stdlib analysis is reproducible with `python3 -B scripts/analyze_limits.py`. It independently models all three cores, checks all **280 clean-cut cases**, and screens shorts and conditional ignited-GDT paths. Its conservative selected adjustment/tolerance envelope is **40.39597 V**, giving **18.6452 mA and 0.753190 W per minimum-resistance branch** with zero forward drops. That exceeds standard-mode resistor power and is not an accepted combined PSU maximum or measured temperature. A representative far-end 10 V GDT arc draws **0.259543 A / 2.602168 W in the modeled path**, while total source demand remains **0.979810 A**. The PSU/fuse therefore cannot be assumed to disconnect it.

The continuation adds `python3 -B scripts/design_bounds.py`: conditional standard-based **8.21 ohm/km**, 70 C cable plus an explicit contact budget, and a **proposed, unenforced 35-37 V feed window**. Nonuniform LED/loading corners give **4.6681 mA** at a high-drop far-end LED, below the uniform-case 5.8796 mA; neither is a guaranteed optical minimum. At 37 V the resistor upper screen is **0.631876 W**, leaving only 18.124 mW below standard P70 and a **71.534 C rating-only local ambient ceiling**. These are actionable design/thermal requirements, not normal-duty approval. [Electrical continuation](pcb/ELECTRICAL.md#8-continuation-decision-2026-09-07) records why the researched LED and compact-GDT substitutions were not populated. **P2 remains unfinished.**

**Protection holds remain open:**

- **C4, simplified LED protection:** The user accepts LED damage from accidental low-voltage installation polarity errors, with spares; reversed flying-lead survival is no longer required. Assess the **16-part, two-antiparallel-diode candidate** for negative connector voltage, retaining the one-way series path. It is not implemented and does not regulate forward pulse current. Ordinary RUN/TEST/switching/cattle-fence exposure remains to assess; the prior 40-part investigation is not a prerequisite. See [the revised scope and resistor/layout options](pcb/ELECTRICAL.md#9-simplified-indicator-direction).
- **C5, powered faults:** The ordered 2 A Littelfuse 0217002.MXP fuse has published DC interrupting data, but cable-limited faults and PSU hiccup behavior may prevent prompt clearing. GDT follow current/extinction with a powered 36 V source remains unqualified. Roughly 10-15 V GDT arc voltage matters after ignition; being below DC sparkover does not prove extinction.
- **Transient coordination:** A 470 V DC sparkover value is not a 470 V transient clamp. Reviewed impulse sparkover at 1 kV/us reaches 950 V for SMD5050-470NA and 1100 V for 2R470TD-8; B5G470L's 850 V figure covers 99% of measured values. Account for lead overshoot and unverified cable impulse withstand.
- **System ratings:** Component 5/20 kA impulse ratings, paralleled terminal pins, and heavy copper do not establish an assembled 20 kA rating, 72 A terminal capability, equal current sharing, direct-strike protection, or a multi-decade service life. Complete-path qualification and documented limits are required.

The user accepts potentially wholesale rebuilding after a **direct lightning
strike**, not blanket damage acceptance for all nearby lightning or ordinary
repetitive pulses. Continuous-safe normal TEST remains mandatory. A 2 W resistor
or SMT conversion is a candidate way to gain thermal margin, not a reduction
of the roughly 1 W nominal heat generated by the two resistors. The current
14-part BOM is unchanged; no 2 W replacement or added diode is already fitted.

## 4. Hardware Component Selection & Specifications

The reviewed 1.1.0 baseline has **14 electrical parts, all top-side: two SMT and twelve THT**, plus four mechanical hole footprints. This is a baseline count, not a frozen 1.2.0-dev protection BOM. Recount from the approved schematic/PCB if parts are added. Codes identify sourcing candidates, not reserved stock or verified footprint compatibility.

| References | Manufacturer / MPN | Sourcing code | Component data and design role |
| :--- | :--- | :--- | :--- |
| D1, D2 | **onsemi 1N4007G** | C232439 | 1000 V / 1 A rectifier, DO-41. BOM and schematic/PCB identities are corrected, and 1.10 mm holes are implemented. Do not infer junction technology from an ordering suffix alone. |
| R1, R2 | Vishay MBE04140C2201FC100 | C1368610 | 2.2 kohm, 1%, DIN 0414 axial, 15.24 mm formed pitch in the baseline; use the actual power-mode/standard-mode, voltage and pulse limits. |
| GDT_AB, GDT_BC | Ruilon SMD5050-470NA | C39692533 | 470 V DC sparkover, component 5 kA impulse rating (8/20 us), nominal 5 x 5 mm SMT body. |
| GDT_AC | Bencent B5G470L | C5337217 | 470 V DC sparkover, component 5 kA (8/20 us), nominal 5.5 mm diameter x 6 mm axial body, bridging over B. |
| GDT_A_E, GDT_B_E, GDT_C_E | Ruilon 2R470TD-8 | C2836978 | 470 V DC sparkover, component 20 kA (8/20 us), nominal 8 mm diameter x 6 mm axial body. |
| J_IN, J_EARTH | Cixi Kefa KF128-7.62-3P | C474957 | Three-pin 7.62 mm pitch, listed component 24 A / 300 V. All J_EARTH pins share the earth net; do not multiply the rating by three. |
| J_LED_A, J_LED_C | Cixi Kefa KF129-5.08-2P | C475092 | Two-pin 5.08 mm pitch, listed component 24 A / 250 V. Outward orientation and intentional pad polarity must be preserved. |

Use the exact manufacturers' drawings and rating conditions, including maximum body/lead dimensions, capacitance, pulse endurance, and soldering limits. [REMEDIATION source links](REMEDIATION.md#source-links) include the reviewed datasheets. The purchased external indicator is **APEM Q10F5SXXSG02E**, a **no-internal-resistor** device with a **20 mA family maximum and 5 V reverse maximum**, not a regulated 2 V lamp; see [LED.md](LED.md).

## 5. Unapproved Alternatives

Retain these earlier sourcing suggestions for investigation, **not as approved upgrades or drop-ins**. No purchase, footprint fit, higher assembled surge capability, or lifetime benefit is established by this list. Differences in electrode configuration, body, lead diameter, pin mapping, RF loading, and thermal/pulse behavior may require redesign and new qualification.

| Intended references | Previously suggested alternatives |
| :--- | :--- |
| D1, D2 | Vishay 1N4007GP-E3/54 |
| R1, R2 | Vishay PR02000202201JA100 (PR02 series) |
| GDT_AB, GDT_BC | Littelfuse SH470 |
| GDT_AC | Bourns 2027-47-BLF or Littelfuse CG2-470L |
| Earth GDTs | Littelfuse SL1021A470R |
| J_IN, J_EARTH | Phoenix Contact 1731734, GMKDS 3/ 3-7,62 |
| LED terminals | Phoenix Contact 1715721, MKDS 1,5/ 2-5,08 |
| External LED | APEM Q14P5BXXHG02E, discussed in LED.md |

A higher resistor wattage does not reduce heat at the same resistance/current. A larger LED bezel does not prove better daylight contrast. Global sourcing/private inventory is an option only after engineering approval and a supplier quote; it is not a guaranteed route to stock or a fixed lead time.

## 6. PCB And Assembly Constraints

These are protected nominal design features, not tolerance-free measured acceptance. See [AGENTS.md](AGENTS.md), [REMEDIATION.md](REMEDIATION.md#physical-guardrails), and the controlled assembly evidence under `pcb/` before changing them.

| Feature | Required geometry / verification |
| :--- | :--- |
| Board | 63 x 56 mm; outline (97.0, 94.5) to (160.0, 150.5) mm. |
| Mounting | Four 3.2 mm holes at (101.5, 99.0), (155.5, 99.0), (101.5, 146.0), (155.5, 146.0); preserve 6.4 mm keepout collars and 6.9 mm mechanical courtyards. Nominal centres are 4.5 mm from edges. |
| Fence rails | Full 3.2 mm nominal width on **both** copper layers; no waist relief or unapproved narrowing. |
| Rail stitching | Nine vias: X = 112.5, 114.0, 115.5 mm on each rail at Y = 114.88, 122.50, 130.12 mm. Each **1.0 mm drill / 1.8 mm pad**. |
| Earth bus | Matching solid copper on both layers, X = 143.99-157.25 mm, Y = 111.25-133.75 mm; preserve continuity and the 4.5 mm-grid construction. |
| Earth stitching | Five **1.0/1.8 mm drill/pad** vias at X = 150.0 mm, Y = 114.88, 118.69, 122.50, 126.31, 130.12 mm. Together with the rail vias, **14 protected vias**. |
| Fence/earth isolation | At least **3.0 mm copper clearance**. Preserve B-return routing at X = 135.50 mm, Y = 107.20 / 137.80 mm unless an approved equivalent maintains the constraints. Historical geometry gave 3.25 mm to the earth plane and 8.44 mm to earth-GDT input pins; remeasure revised outputs. |
| Earth GDT spacing | Centres Y = 113.50, 122.50, 131.50 mm, retaining **9.00 mm pitch**. Nominal 8 mm bodies suggest a 1 mm gap, but actual maximum bodies, formed leads, and honest courtyards must establish fit. |
| GDT_AC overpass | Now at X=125.80 mm, north-south over Wire B, 15.24 mm formed pitch. **At least 2.0 mm physical standoff under the entire raised span**, per the controlled side-view/forming drawing and inspection method. |
| LED terminals | J_LED_A origin (145.50, 103.00), 90 degrees, opens north; J_LED_C (145.50, 142.00), 270 degrees, opens south. On both, pad 1 positive is at X = 142.96 and pad 2 B return at X = 148.04 mm. Do not replace intentional custom pad mappings with stock-library geometry. |
| Other orientation | J_IN opens left (0 degrees), J_EARTH right (180 degrees); J_IN A/B/C run north to south. D1/D2 cathodes face right toward the LED positive terminals in the baseline. Footprint origins/rotations are not automatically assembler centroids/model rotations. |
| Legend | Native 1.0 mm height / 0.15 mm stroke lettering, underside references and 1.2.0-dev identification are implemented. A/B/C/EARTH, polarity and cathode identification remain; processed printing still needs inspection. |

The source stackup now sums to **1.600 mm**: 1.440 mm core, two 0.070 mm copper layers and two 0.010 mm mask layers. Confirm the actual supplier thickness convention, tolerance and support fit; this arithmetic is not a stock-laminate guarantee. ENIG is the selected solderable surface finish, **not a hermetic seal or a guarantee against terminal corrosion**. Do not narrow protected copper with generic thermal spokes to ease soldering; agree a suitable heavy-copper assembly process.

Intentional geometry is captured in **ten project-local footprints and six symbols**. GDT_AB/GDT_BC remain at X=119.50 with **5.50 x 1.20 mm metric lands, 4.00 mm centre spacing** and unchanged full-width track stubs; GDT_AC remains at X=125.80. Body drawings are now resolved, with explicit conservative procurement envelopes where maximum metal-pin/body datums are not guaranteed. J_EARTH's accepted envelope needs **1.00 mm nominal / 1.30 mm tolerance-budgeted overhang**, not the old nominal 0.30 claim. [ASSEMBLY.md](pcb/ASSEMBLY.md) controls holes, courtyards, forming, lot inspection and supplier holds.

### Via and Component Hole DFM

**Policy updated 2026-09-07. Selected standard process: UNTENTED both sides, no fill/plug/cap, ENIG.** Source openings are nominal 1.80 mm with no via paste; no special 1.00 mm filling or reliable tenting is assumed. Recheck each actual order's processed data and assembly process. References: [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [via covering](https://jlcpcb.com/help/article/pcb-via-covering), and [via versus component-hole tolerances](https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes).

The following limits concern the **hole**, not its copper pad:

| Process | Published guidance | Consequence for the protected 1.0 mm holes |
| :--- | :--- | :--- |
| **Untented, selected** | Standard process; exposed copper receives ENIG. | No seal. Inspect solder ingress/beads and environmental protection. |
| Tented | Ideally at most 0.4 mm; normal coverage guidance at most 0.5 mm. | Larger holes are not guaranteed covered. A KiCad tenting flag is not proof. |
| Soldermask plugged | At most 0.5 mm, no mask openings on either side, at least 0.35 mm process clearance from other mask openings/pads. | Outside the normal limit. Ink plugging is not filled-and-capped via-in-pad processing. |
| Filled and capped | Detailed guide recommends at most 0.5 mm; capability table lists 0.15-0.55 mm. Resolve the applicable limit with CAM. | 1.0 mm exceeds both ranges; any exception needs written process acceptance. |

- Preserve **all 14 stitching vias at 1.0 mm drill / 1.8 mm pad** and the protected copper. Fix surrounding soldering geometry or seek an approved process/layout solution; do not delete or shrink vias to fit a covering option.
- Inspect full drill circles and exposed annuli against actual `F.Mask`, `B.Mask`, and `F.Paste`, then the processed mask/stencil. The historical **0.19 mm SMT/via intersections** are gone; new metric lands give **1.239713 mm hole-to-SMT-aperture and 0.839713 mm full-annulus-to-aperture** gaps. The 4.00 mm metric centre spacing is an explicit design choice; the drawing's contradictory 0.165-inch entry and actual solder-volume/profile acceptance remain W1 holds. Adjacent same-net rail-via mask circles intentionally overlap, but no component paste/mask aperture is excused over a via hole.
- Identify treatment by **coordinates and hole function**, never diameter alone. Resistor holes formerly shared the 1.0 mm via diameter and now use 1.40 mm. All insertion holes remain open. Ordinary via diameters may be adjusted in CAM; check that no protected nominal drill was reduced. No fill is requested.
- **70 micrometres of exterior copper is not 70 micrometres of barrel plating.** JLCPCB's published 18 micrometres average hole plating is not a guaranteed minimum in every barrel. Agree any finished minimum used in current/surge calculations separately. Nonconductive fill adds no conductive cross-section.
- Tenting, plugging, opacity, or gel encapsulation does not prove hermetic sealing, freeze-thaw immunity, or an assembled ingress rating.

Use **component PTH pads**, never ordinary vias, for lead insertion. Record the exact manufacturer/MPN, drawing revision, maximum finished lead dimensions, pitch, proposed hole, and assembly allowance. For round holes:

```text
Round pin envelope       = maximum finished lead diameter
Rectangular pin envelope = sqrt(maximum_width^2 + maximum_thickness^2)
nominal finished hole - 0.08 mm >= maximum pin envelope + 0.10 mm
```

The last line uses JLCPCB's ordinary component-hole **+0.13/-0.08 mm** tolerance and the project's starting **0.10 mm diametral allowance after tolerance**. Increase the allowance when required; also account for pin-pitch, hole-position, and forming tolerances, particularly rigid connectors. This is stricter than simply adding 0.10 mm to a nominal pin. Do not assume press-fit tolerances for this order.

For **onsemi 1N4007G / C232439**, the old 0.90 mm hole could finish at 0.82 mm and fail insertion. **D1/D2 now have 1.10 mm finished holes with 2.20 mm pads** in the source/local library. Minimum hole 1.02 mm gives **0.1564 mm** clearance over the controlling 0.034-inch / 0.8636 mm maximum lead, and a 0.55 mm nominal ring. Native drill validation checks the exported diameters; actual finished holes, lead forming and insertion still require acceptance.

The selected hole/pad schedule is **KF128 2.00/3.20, KF129 2.00/2.80, MBE0414 1.40/2.40, B5G470L 1.40/2.80, earth GDTs 1.50/3.00 mm**. Minimum nominal ring is 0.40 mm. These use the exact 1.05 mm earth-GDT lead maximum and explicit conservative procurement limits for the other pins, plus a separate hole-position/formed-pattern budget. Drawings are no longer simply "unreadable"; actual allocated parts still must pass the specified envelope and free-insertion/solder-process inspection. See [fit evidence](pcb/ASSEMBLY.md#hole-fit-evidence), including the separate as-built diode-forming requirement. Supplier CAD or nominal pitch is not that acceptance.

After drill changes, recheck pad sizes, hole/copper spacing, edge clearances and **at least 0.254 mm nominal component PTH annular ring for two-layer 2 oz fabrication**. Generic via-ring rules do not establish component-pad compliance. Finished-ring acceptance also requires hole and registration tolerances. Resolve fit in CAD, not by forced insertion or reaming plated boards.

DRC alone cannot close hole-fit, solder-wicking, body/forming, or process approval. Record the accepted evidence in the controlled assembly notes, regenerate the production outputs, and inspect the final processed files.

## 7. Enclosure, Cable And Site

WISKA COMBI 308 external dimensions are **85 x 85 x 51 mm**. Published box ratings include IP66 via membranes and IP67 with the specified gland arrangement, and -30 to +100 degrees C; they do not transfer automatically to drilled, wired, gel-filled assemblies. Essentra LCBSBM-6-01A-RT data lists nominal **3.18 mm support hole, 1.57 mm panel thickness, and 9.53 mm spacing**. Confirm tolerance compatibility with the PCB and dry-fit the actual WAGOs, cable bends/glands, earth wires, formed GDTs, lid LEDs, and screwdriver access.

The baseline APEM LEDs use nominal 10 mm panel mounting; use the exact cutout/seal instructions and **0.20-0.25 Nm mounting torque**, subject to the supplied model instructions. The gel is **WISKA OneGel**, not the previously misidentified MP0100: manufacturer order 10108963 is a 300 ml, single-component silicone cartridge requiring **no mixing**. WISKA's own sources conflict on cure time (none versus 20 minutes) and temperature (-60..+200 C versus -20..+90 C); neither provides OneGel thermal conductivity. Do not choose the more permissive claim or invent a cure process. Check the supplied lot's process and compatibility with the **PP/TPE COMBI 308**, supports/adhesive, PVC and WAGO 221-613. The old 180-190 ml/box estimate is not measured yield. Gel does not establish IP68, hermeticity, heat dissipation or lifetime; retain an unpotted reference. See [OneGel evidence](pcb/ENVIRONMENT_EVIDENCE.md#wiska-onegel).

The site is on the **Isle of Man, less than 1 km from the coast**, with rain, salt exposure and possible condensation. Observed outdoor ambient is about **-10 to +30 degrees C**; these are not guaranteed lifetime extremes or maximum internal temperatures. Some boxes receive direct sun. Qualification must include credible solar and weather margins.

The user confirms reel markings **CM03/05.100** and **"3 CORE (3 x 35/0.30) TINNED BLACK 100 MTR"**. AMC's [2026 Update V.3 datasheet](https://cdn.prod.website-files.com/62deaee72baf3ef3b83165ff/69fc985a23120ee62491a529_14%20-%20AMC%20Datasheet%20%20-%20Oceanflex%20Tinned%20Copper%203%20Core%20Cable%20(2026%20Update)%20V.3.pdf) identifies CM03/05 as **3 x 2.5 mm^2 tinned copper, Class 5, PVC sheath, maximum 7.4 mm OD, 60 V max DC, -30 to +70 C**. These replace the older distributor's 7.3 mm/-15 C assumptions for the current specified product; confirm V.3 applicability to the supplied manufacturing lot. The core-only 105 C reference is not a complete-cable rating. No mains, armoured or -40 C cable claim follows.

The actual core colours are **red, black and plain green**, confirmed by the user and consistent with V.3. Identify and label A/B/C end-to-end; plain green is not PE, and **green/yellow must never be an active fence core**. V.3 omits numerical conductor resistance despite its footnote; [the bounded DC study](pcb/DESIGN_BOUNDS.md) uses the cited conductor standard conditionally, not a measured reel guarantee. Confirm permanent UV/weather exposure, wet-conduit suitability, installation bend limits and impulse data. A 60 V working rating is not surge qualification. [Cable evidence](pcb/ENVIRONMENT_EVIDENCE.md#amc-oceanflex-cable) distinguishes resolved identity/colours from these remaining limits.

Routing is mostly **0.3-1.0 m above ground** on timber fencing with horizontal metal wires, with plastic conduit under driveways/gates. Conduit can become wet and is not electromagnetic shielding. Do not connect the boundary cable electrically to supporting fence wires. A separate energized cattle wire may run **at least 0.5 m away for up to 300 m in parallel**: maintain separation allowing for movement, increase it where practical, and use that exposure for repetitive-pulse qualification in RUN and TEST. Compare energizer off/on, receiver behavior, LED indications, protection stress and recovery; it is not an established interference-safe clearance.

The proposed shed earth is shared by the DogWatch protector and both shed-end boards. A qualified installer must confirm building PE/electrode relationships against applicable regional OEM instructions and the site design. Do not add arbitrary unbonded rods, directly earth a fence core, or assume DC negative needs an earth bond. Ordered rods and parallel earth wires are inventory, not an approved discharge-path design.

## 8. Verification And Release

The implemented [Makefile](Makefile) uses one locked transaction in `scripts/manufacturing.py`. It stages a **complete project** including schematic, PCB, settings/rules and local libraries, runs strict **DRC, ERC, schematic/PCB parity, protected-geometry and artifact checks**, and retains readable/machine-readable reports. All errors and unreviewed warnings block; the exact eight intentional single-sheet global-label warnings are explicitly reviewed by UUID/name in `pcb/verification.json`, not broadly suppressed. Every public export alias, including BOM/CPL/drill/netlist, uses the complete gated transaction.

The native XML netlist export also warns about the ten intentional nonnumeric J_/GDT_ references. Isolated numbering controls confirmed the cause; duplicate/unassigned-reference probes showed why the generic warning alone is not safe to accept. Its separate review is locked to the exact KiCad 9.0.7 diagnostic and schematic/project/library/table hashes. Other export diagnostics and changed inputs block; neither exception hides a native warning or constitutes circuit approval.

Use headless KiCad 9 (tested baseline **9.0.7**). The CLI is verified by invocation and the complete snapshot lives in `tmp/manufacturing/runs/attempt-*/project`. Cleanup affects only build-owned runs/outputs, not other `tmp/` evidence. New attempts quarantine previous public outputs, and source/artifact verification precedes publication. Do not rely on PCB-only error-level DRC or assume KiCad 7/8 compatibility.

```bash
make check
make all
```

`make check` performs file verification and refreshes the generated CPL reference without publishing an upload package. **`make all` remains blocked by the engineering holds in `pcb/verification.json`**, even when file checks pass. Reports are in `build/reports/` and `build/drc_report.*` / `build/erc_report.*`; `build/status.json` identifies the attempt. Only a published `build/manifest.json` with `status=verified` and matching source/artifact hashes identifies a current file-verified package. It still does not approve a prototype order or field use. Run `make clean` separately from builds and preserve desired run evidence first.

| Intended output | Purpose, only after verification |
| :--- | :--- |
| `build/Gerbers.zip` | Copper, mask, legend, top paste, outline and separate PTH/NPTH drills for fabrication; generated mirror at `pcb/Gerbers.zip`. |
| `build/BOM.csv` | Reviewed source population and exact sourcing identities matched to the schematic/PCB. |
| `build/CPL.csv` | Native-generated placement including all required SMT/THT parts, excluding mechanical/DNP items; `pcb/CPL.csv` is the generated draft reference. Native signed Y is retained and rotations normalized modulo 360. |
| `build/pcb.d356`, `build/FlyTest.zip` | IPC-D-356 and fabrication data for bare-board electrical testing, not assembled functional or surge testing. |
| `build/Assembly.pdf`, `build/Assembly.txt`, `build/ViaTreatment.csv` | Native assembly drawing/placements and coordinate-based via identification, accompanied by all seven controlled engineering notes. Notes and analysis helpers are snapshotted/hashed; release-note copies compare exactly. Not supplier placement/process approval. |

Fresh exports must agree in origin, handedness, drills, geometry, population, net connectivity and archive contents. Never hand-edit generated fabrication data or correct placement handedness using absolute Y values. Obtain separate **processed PCB/stencil CAM approval** and **parts-placement/assembly approval**, including any evidence-backed centroid/model rotation corrections. See [ORDERING.md](ORDERING.md).

| Release gate | Evidence required |
| :--- | :--- |
| A: File ready | Correct source/circuit/library/rule data, passing automated checks, reviewed regenerated artifacts and synchronized documentation with open qualifications identified. |
| B: Prototype order | Gate A plus required part-fit, via/solder/forming process, CAM and placement acceptance, and a controlled prototype test scope. Known manufacturing defects must not be deferred to chance assembly. |
| C: Field release | Required reversal/fault, continuous thermal, 5 m daylight, full-hub cut, RF/site, environmental and protection evidence, accepted earthing and documented performance limits. |

Gate B can precede defined physical qualification tests, but neither documentation nor five basic bench passes closes **C4/C5** or authorizes full rollout. A successful build means manufacturing data verified for that revision, not lightning protection verified.

## 9. Documentation Map

| Document | Role |
| :--- | :--- |
| [REMEDIATION.md](REMEDIATION.md) | Agreed requirements, issue/evidence register, gates and session handoff. |
| [AGENTS.md](AGENTS.md) | Headless tooling, staging and physical guardrails. |
| [INSTALL.md](INSTALL.md), [RISKS.md](RISKS.md), [ACCEPTANCE.md](ACCEPTANCE.md) | Operating, risk and qualification procedures, synchronized by their owners with the final circuit. |
| [ORDERING.md](ORDERING.md), [MATERIALS.md](MATERIALS.md), [LED.md](LED.md) | Quote/approval workflow, procurement ledger, indicator limits and visibility target. |
| [REVIEW.md](REVIEW.md) | Reusable read-only audit brief, not a completed review or sign-off. |
| `pcb/ELECTRICAL.md`, `pcb/ASSEMBLY.md` | Electrical analysis and controlled assembly/fit notes for this draft; require their actual revision and evidence before release. |
| [Makefile](Makefile), `pcb/pcb.kicad_sch`, `pcb/pcb.kicad_pcb`, `pcb/pcb.kicad_pro` | Build implementation and authoritative design/project sources, together with applicable rules and local libraries. |
