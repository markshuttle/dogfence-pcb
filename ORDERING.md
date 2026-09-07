# JLCPCB Prototype Ordering Guide

**Draft hardware revision 1.2.0-dev; reviewed baseline 1.1.0. Order hold remains in force.**

The agreed first order is **five individual, fully assembled boards**, with no field soldering. This guide describes the required quote and approval process; it does not certify the current files as ready for upload. See [REMEDIATION.md](REMEDIATION.md#release-gates) for gates A (file ready), B (prototype order), and C (field release).

The field requirement is **41 stations, 36 standard + 5 earth-connected, and 82 LEDs**, including both shed-end boards. Future production quantity depends on qualified prototype reuse, retained/destructive test units, and explicitly approved spares. Do not turn a five-board prototype order into five multi-up panels or automatically reorder the old production quantity. [MATERIALS.md](MATERIALS.md) controls purchase history and allocation.

External cable, OneGel, enclosure and switch manufacturer sources and unresolved discrepancies are recorded in [pcb/ENVIRONMENT_EVIDENCE.md](pcb/ENVIRONMENT_EVIDENCE.md); use MATERIALS for the latest confirmed reel labels and TEST-PSU/disconnected-spare allocation.

## 1. Before Upload

Use the working design/project sources under `pcb/`, not backups, archived ZIPs or scratch copies. `pcb/BOM.csv` is reviewed sourcing data; `pcb/CPL.csv` is a **native-generated draft reference**, not an independently edited coordinate list or upload approval. [Electrical analysis](pcb/ELECTRICAL.md) and [controlled assembly notes](pcb/ASSEMBLY.md) record the current corrections and remaining decisions.

Before gate A, verify the actual implementation and reports for:

- The approved circuit/protection architecture and hub matrix, with **C4 simplified negative-voltage/transient protection and C5 PSU/fuse/GDT coordination still open**. Installation-polarity LED damage is now user-accepted, not a required immunity feature. The **16-part candidate and 2 W/SMT options in ELECTRICAL section 9 are not implemented**: the circuit/BOM remains 14 parts. Do not order the historical active candidate parts or a resistor substitution from a headline wattage; recount after a reviewed circuit change.
- The onsemi **1N4007G / C232439** identity and implemented **1.10 mm finished diode holes / 2.20 mm pads**. Native checks verify exported drill geometry; forming and actual manufactured-hole fit still need acceptance.
- The adopted component-hole, finished-pin/pattern and body-envelope limits, real courtyards, reproducible local libraries, legend, GDT forming and full enclosure fit evidence. Original mechanical figures have been read; the remaining fit task is independent allocated-lot acceptance against the controlled limits, not an unresolved drawing-reader task. A standard-looking footprint name or matching C-code is not a mechanical match.
- Corrected SMT GDT mask/paste geometry around the protected vias, native signed-Y placement, and complete population/net parity.

The [P2 continuation decision](pcb/ELECTRICAL.md#8-continuation-decision-2026-09-07) and [conditional design bounds](pcb/DESIGN_BOUNDS.md) do not release a protection circuit or continuous-duty design. Their proposed **35-37 V TEST-feed window is not hardware-enforced**; the new current/thermal calculations are not procurement acceptance bands or evidence of a guaranteed 6 mA field minimum. One ordered LRS-75-36 serves TEST; its disconnected spare adds no capacity.

The implemented build stages the **complete project**, runs **DRC, ERC, schematic/PCB parity, protected-geometry and artifact checks**, blocks errors and unreviewed warnings, and retains readable/JSON reports. The eight intentional single-sheet global-label warnings are narrowly reviewed in `pcb/verification.json` and remain visible, not suppressed. Every public export alias uses the same locked complete-package transaction. See [AGENTS.md](AGENTS.md) for the implemented workflow.

The separate netlist-export annotation warning is reviewed only for the exact tested input hashes, ten intentional nonnumeric references and KiCad 9.0.7 diagnostic. It remains in the logs; other export diagnostics or changed review inputs block. Do not treat this as a general annotation-error exemption.

```bash
make check
make all
```

Use headless KiCad 9 (tested baseline 9.0.7). `make check` retains evidence and refreshes the CPL reference, **not an upload package**. `make all` and the direct export aliases remain blocked by the engineering holds in `pcb/verification.json`; do not clear those holds to obtain ZIPs. Private draft exports are retained under `tmp/manufacturing/runs/attempt-*`. Serial/parallel builds use a lock and quarantine stale public outputs. `make clean` removes owned runs/outputs only; preserve useful run evidence first and run clean separately.

| Intended file | Use after verification |
| :--- | :--- |
| `build/Gerbers.zip` | PCB quote/fabrication: F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, F.Paste, Edge.Cuts and separate PTH/NPTH drills. Generated mirror: `pcb/Gerbers.zip`. |
| `build/BOM.csv` | Assembly references, population and reviewed sourcing identities. |
| `build/CPL.csv` | Native-generated placement for **all required SMT and THT** parts, excluding mechanical holes/DNP items. |
| `build/pcb.d356` | IPC-D-356 connectivity for bare-board test/CAM comparison. |
| `build/FlyTest.zip` | Netlist and fabrication package for bare-board electrical testing, not an assembled functional/surge test. |

Inspect fresh exported geometry, layer/drill classification, schematic/PCB/IPC connectivity, BOM/CPL completeness, and archive members. Check `build/status.json`, `build/reports/verification.json`, readable/JSON DRC/ERC reports, and the published `build/manifest.json` source/artifact hashes. **No verified manifest means no current upload package.** Assembly outputs include `Assembly.pdf`, `Assembly.txt`, `ViaTreatment.csv` and all seven controlled engineering notes. Never hand-edit generated Gerbers, drills or ZIPs to bypass a failed check.

## 2. Quote Specification

After gate A and authorization to proceed, request the actual quote at [JLCPCB](https://jlcpcb.com/quote). Capture the accepted options and any exceptions in the release record.

JLCPCB offers **standard two-layer FR-4 with 2 oz copper on both sides and ENIG**. Use the standard quote options for this combination, not an assumed special-stackup exception. No special CAM approval is implied or recorded; availability does not accept this design's hole/via, land-pattern, soldering or assembly details. The design-specific reviews below remain required.

| Item | Five-board prototype baseline / supplier confirmation |
| :--- | :--- |
| Quantity | **Five individual usable boards, all five fully assembled**. State panel-to-individual-board conversion explicitly. |
| Material | Readily available standard **FR-4**. Do not impose High-Tg 170, a particular Shengyi grade, or a claimed lifetime requirement without an approved engineering need. |
| Layers / size | **Two layers, 63 x 56 mm** per individual board. Both layers carry isolated fence and earth copper; B.Cu is not a blanket ground plane. |
| Thickness | **Nominal 1.6 mm finished board**. The source now totals 1.600 mm including two 0.070 mm copper and two 0.010 mm mask layers; confirm supplier thickness convention/tolerance and support fit, not just the arithmetic. |
| Copper | **2 oz / 70 micrometres on both F.Cu and B.Cu**. This does not specify finished barrel plating or an assembled surge rating. |
| Finish / mask | **ENIG, green soldermask default**. Record actual finish specification; do not mandate 2-microinch gold or claim a pore-free environmental seal. |
| Hole/via process | Selected standard **UNTENTED on both sides, no fill/plug/cap** for all **14 protected 1.00 mm nominal drill / 1.80 mm copper vias**, with nominal **1.80 mm F.Mask/B.Mask openings and no via paste**. Preserve positions/drills and inspect the processed data; this is not a sealed-hole process. See section 3. |
| Assembly | All required top-side SMT and THT parts fitted and soldered, with controlled axial GDT lead forming. Recount from the approved design before quote acceptance. |
| Service | Current public guidance permits THT under **both Economic and Standard PCBA in principle**. Confirm the exact mixed SMT/THT, 2 oz/ENIG job, part sourcing, manual operations and test scope in the actual quote. |
| Panel / tooling | Supplier-proposed rails, fiducials and tooling, with an approved drawing and depanelization method. Standard PCBA processing-size requirements may require panelization for this small board. |
| Solder process | Explicit acceptance of heavy-copper soldering, SMT paste volume, THT fillets/barrel wetting, and the GDT forming/standoff inspection. No field soldering or forced insertion/reaming to repair fit. |
| Additional coating | Not part of the agreed baseline. Do not assume **OneGel** makes coating universally redundant or that adding coating is automatically compatible. OneGel is a **single-component 300 ml cartridge, 10108963; no mixing**, not MP0100. Its process/material acceptance remains open; see the environment evidence and INSTALL. |
| Testing | Agree bare-board continuity/isolation test coverage and any assembled testing separately. Do not label flying probe as LED, reversal, thermal, RF or surge qualification. |
| Price / schedule | Obtain a dated itemized quote: PCB finish/copper, parts, loading/extended fees, attrition, SMT/THT labor, forming, tooling, tests, shipping and applicable taxes/import costs. No fixed stock, cost or lead-time promise is established here. |

The supplier must propose the actual panel/rail dimensions. The old **73 x 76 mm** assumption is not an approved panel plan, and rail removal is not automatic. Confirm five finished boards will be delivered in the agreed condition, with no cuts/tooling holes in protected functional copper and no damage to board edges or mounting features. Absence of fiducials on the single PCB is not itself a defect if approved panel fiducials/tooling satisfy assembly needs.

## 3. Hole, Via And Solder Process

Apply the complete [via and component hole DFM policy](README.md#via-and-component-hole-dfm). [Controlled assembly notes](pcb/ASSEMBLY.md) specify the adopted P3 limits; [DFM evidence](pcb/DFM_EVIDENCE.md) records the visually read figures, calculations and remaining supplier facts. Keep the coordinate-based via drawing and the exact lot/envelope requirements with the quote/assembly package.

- Preserve nine rail vias at X = 112.5, 114.0, 115.5 mm on each Y = 114.88, 122.50, 130.12 mm rail, plus five earth vias at X = 150.0 mm and Y = 114.88, 118.69, 122.50, 126.31, 130.12 mm. All remain **1.0 mm drill / 1.8 mm pad**.
- Select standard **UNTENTED, both sides, no fill/plug/cap**. Each via has nominal **1.80 mm circular F.Mask/B.Mask openings**, with no via paste. Adjacent **same-net rail-via mask openings intentionally overlap** at 1.50 mm pitch; this does not permit an SMT mask/paste aperture over a via hole or annulus. No reliable 1.00 mm tenting or special filling exception is needed. Exposed ENIG is wettable: qualify solder ingress, drain-through, beads and cleanliness.
- Identify holes by **function and coordinates**, never a blanket fill-by-diameter instruction. R1/R2 now use **1.40 mm component holes**; their former shared 1.00 mm diameter is historical. All component holes remain open for insertion and no via is an insertion pad. Obtain written CAM agreement not to reduce protected via drills; ordinary via guidance does not guarantee a finished 1.00 mm diameter/tolerance. Any required finished-via minimum is a separate unresolved supplier fact, not assumed special processing.
- The adopted Ruilon SMT lands are **5.50 X x 1.20 Y mm at local Y=+/-2.00**, at **X=119.50 mm**, Y=118.69/126.31, for copper, mask and paste with zero additional mask/paste margins. The printed **metric 4.00 mm centre spacing is explicitly selected**; it is not an inner-gap dimension. The manufacturer's conflicting **0.165-inch** entry is not an approved erratum. **W1 remains open for that contradiction and actual processed stencil/solder/profile acceptance.**
- Compare complete drill circles, exposed annuli and actual mask/paste, not just pad centres. Current nominal minimum distances to all four SMT mask/paste apertures are **1.239713 mm from a via drill circle** and **0.839713 mm from its full annulus/mask opening**. No SMT aperture overlaps a protected via hole or annulus. These replace the former geometry's distances, not actual registration/solder-spread allowances. Preserve the **2.80 mm land/mask/paste gap** and separate **1.80 mm connected-copper gap** beneath each tube; do not extend the full-width stubs blindly to the new pad centres. Customer F.Paste does not approve the assembler's processed stencil.
- For the enlarged Kefa, resistor and GDT holes, require `nominal finished hole - 0.08 - maximum pin envelope - 0.241421 >= 0.10 mm`. The separate **0.241421 mm diametral position budget** includes **+/-0.05 mm hole position on each axis** and an independently inspected **0.050 mm radial per-pin part-pattern limit after common rigid alignment**, through the insertion length. It is additional to the 0.10 mm diametral assembly allowance, not a replacement for it. Use rectangular-pin diagonals, not nominal widths. The diode-specific forming treatment is below.
- Preserve at least **0.254 mm nominal component PTH annular ring** under the applicable two-layer/2 oz rules. The adopted component rings are all at least 0.40 mm; do not substitute the generic via-ring rule or infer finished registration from nominal rings. Recheck copper/hole/edge clearances and finished-ring tolerance requirements.
- Agree any required finished barrel-copper **minimum** separately. A 2 oz outer layer and the published **18 micrometres average hole plating** do not prove a particular minimum barrel thickness. Untented ENIG does not establish that minimum either.
- Agree reflow and THT soldering processes for the heavy copper without unauthorized thermal-relief narrowing. The GDT_AC drawing retains **at least 2.00 mm gap under the whole raised body/electrode/lead span**, measured above the highest finished PCB top surface before gel. Its development target is **body underside 2.50 +/-0.25 mm and complete assembled height <=8.50 mm**. These drawing/inspection limits do not approve actual seal support, bend radius, springback or forming/solder process.

Adopted component-hole schedule, all dimensions in mm. **E denotes an incoming procurement envelope, not a manufacturer-guaranteed finished-pin maximum.** The full calculations and body boxes remain in ASSEMBLY/DFM_EVIDENCE rather than being repeated here.

| References / family | Nominal finished hole / pad | Finished-pin limit basis |
| :--- | :--- | :--- |
| J_IN, J_EARTH / KF128 | **2.00 / 3.20** | Rectangular **E <=1.10 x 1.00**. |
| J_LED_A, J_LED_C / KF129 | **2.00 / 2.80** | Rectangular **E <=1.15 x 1.00**; supplied drawing variant still to confirm. |
| R1, R2 / Vishay MBE0414 | **1.40 / 2.40** | Round **E <=0.90**; published 0.80 is nominal. |
| GDT_AC / Bencent B5G470L | **1.40 / 2.80** | Round **E <=0.90**; published 0.80 has no tolerance. |
| Earth GDTs / Ruilon 2R470TD-8 | **1.50 / 3.00** | Drawing maximum **1.05**, from 1.00 +/-0.05; retain after forming. |
| D1, D2 / onsemi 1N4007G | **1.10 / 2.20**, unchanged | Controlling 0.034-inch = **0.8636** maximum; separate forming/alignment acceptance. |

Independently inspect every allocated controlled-envelope part for the five prototypes, including attrition, with measurement uncertainty and pin-pattern/body checks. The **diode holes retain their reviewed diameter-only fit**; the fixed 0.241421 position budget is not claimed for D1/D2. Their flexible leads must be formed/aligned to the actual board pattern under an accepted seal-safe process. Larger holes do not establish free insertion, lot yield or adequate solder fill. **W4 remains open for actual lot/pattern/body fit and process acceptance.**

All maximum-body boxes are now controlled from visually read figures or explicit E limits; they are not unresolved image-only dimensions. Neither those boxes, CAM acceptance nor a good 3D render replaces physical COMBI 308 **PP/TPE (not polycarbonate)** dry-fit, support-thickness fit or solder/forming inspection.

The KF128 J_EARTH **E body envelope reaches X=161.00 mm**, **1.00 mm beyond the nominal east edge**. With pose and a routed edge as far inward as X=159.80, budget **1.30 mm overhang**; the courtyard reaches **X=161.35 mm**. The old 0.30 mm body / 0.55 mm courtyard-overhang descriptions are historical only. Include the controlled envelope in panel, depanelization, enclosure and screwdriver/wire-access acceptance; do not trim the body/courtyard or move protected earth copper to hide it.

## 4. Parts And Allocation

The current circuit/BOM remains **14 electrical parts per board: two SMT + twelve THT, all on top**, excluding four mechanical hole footprints. P3 changes holes, body boxes, lands and via process, not component identities or population; no new C4/C5 parts are selected. Recount if protection is subsequently approved. The quantities below are **population only**, not purchase quantities or stock reservations.

| References | Exact reviewed manufacturer / MPN | Code | Per board | Five-board population |
| :--- | :--- | :--- | ---: | ---: |
| D1, D2 | **onsemi 1N4007G** | C232439 | 2 | 10 |
| R1, R2 | Vishay MBE04140C2201FC100 | C1368610 | 2 | 10 |
| GDT_AB, GDT_BC | Ruilon SMD5050-470NA | C39692533 | 2 | 10 |
| GDT_AC | Bencent B5G470L | C5337217 | 1 | 5 |
| GDT_A_E, GDT_B_E, GDT_C_E | Ruilon 2R470TD-8 | C2836978 | 3 | 15 |
| J_IN, J_EARTH | Cixi Kefa KF128-7.62-3P | C474957 | 2 | 10 |
| J_LED_A, J_LED_C | Cixi Kefa KF129-5.08-2P | C475092 | 2 | 10 |
| **Total** | Baseline only | | **14** | **70** |

Confirm actual stock/allocation, Basic/Extended classification, packaging, minimum order/loading quantities and **order-specific attrition** for every line. Public JLCPCB/LCSC stock and historical low-stock warnings do not reserve inventory or guarantee that five boards can be built. In particular, recheck C39692533 rather than relying on the earlier urgency claim. Do not use a generic 12-15-piece feeder estimate as supplier acceptance.

If sourcing is needed, obtain a quote for the exact approved MPN into JLCPCB's private parts library/Global Sourcing, record ownership and leftover stock, and wait for confirmed allocation. No pre-purchase has been recorded here. Substitutions, including the [unapproved alternatives](README.md#5-unapproved-alternatives), require fresh electrical, hole/body, footprint, thermal/pulse, placement and procurement approval. A C-code, nominal pitch or larger rating is insufficient.

Intentional custom footprints must be supplied as reproducible project-local definitions and matched to the BOM. Legacy Phoenix- or resistor-style footprint names do not prove that Kefa terminals or axial GDTs match those libraries. Keep schematic, layout, library tables and assembly drawings synchronized rather than compensating in a hand-maintained CPL.

## 5. Placement Approval

Native KiCad output describes **footprint placement origins**, which need checking against actual assembly centroids. Prefer the retained absolute Gerber/drill origin and **native signed-Y** convention in mm. For example, the baseline LED origins at board Y = +103 / +142 mm export as **-103 / -142 mm**, not positive screen coordinates. Never repair handedness with `abs(Y)` or by rotating/moving PCB pads.

Include every required SMT/THT part, exclude mechanical/DNP items, and normalize rotations **modulo 360**: -90 and 270 degrees are equivalent. Any origin-to-centroid or supplier-model rotation correction must be evidence-backed, keyed to the exact part/footprint, consistently transformed and recorded with the approved placement.

Use this baseline physical checklist against the revised source and supplier models, not as an unverified upload-angle table:

| Part | Physical orientation to confirm |
| :--- | :--- |
| J_LED_A | North/top connector opens outward north; footprint rotation 90 degrees. Pad 1 positive is left at X = 142.96 mm; pad 2 B return right at X = 148.04 mm. |
| J_LED_C | South/bottom connector opens outward south; footprint rotation 270 degrees. Same left-positive/right-return global pad mapping. |
| J_IN | Opens left, baseline rotation 0 degrees; A/B/C pins north-to-south at Y = 114.88 / 122.50 / 130.12 mm. |
| J_EARTH | Opens right, baseline rotation 180 degrees; all three pins on EARTH, not a multiplied current rating. |
| D1, D2 | Cathode bands face right toward the LED positive terminals. Check actual pad/net mapping and selected model, not the legacy library convention. |
| GDT_AC | Body runs north-south over B despite the baseline footprint's 0-degree placement angle; controlled lead forming and >=2.0 mm gap are separate from a top-view render. |
| GDT_AB, GDT_BC | Centred on the revised SMT land pattern with correct electrode orientation and processed paste volume. |
| Earth GDTs | Retain 9.00 mm centre pitch and the controlled 8.21 mm body-diameter envelope with 0.10 mm per-side projected pose allowance. The resulting 0.59 mm budgeted body gap is not a 1.00 mm air-gap or impulse-insulation guarantee. Inspect the actual formed bodies and lid clearance. |

A viewer offset/rotation is not evidence of a correct machine placement file. Resolve discrepancies with the assembler and retain the corrected approved placement data; do not rely on silkscreen or a CAM engineer to silently fix all orientation errors.

## 6. Separate Approvals

Before authorizing fabrication/assembly, retain **both** approvals:

1. **Processed PCB/stencil CAM:** actual copper, mask, paste/stencil, PTH/NPTH drill function/diameters, protected vias, annular rings, outline and panel/rail/tooling plan. Confirm no unauthorized copper or hole changes, and agree depanelization/delivery condition.
2. **Parts placement and assembly:** allocated exact MPNs, approved local footprint/centroid/model rotations, all SMT/THT population, polarity, lead forming, solder process and inspection/test scope.

A checkout option called "Confirm Production File" is not proof that both reviews occurred. Record the source/artifact revision and manufacturer responses with the release. Gate B requires this evidence and a controlled qualification scope, not simply payment or an apparently correct preview.

## 7. Prototype Acceptance And Later Orders

Perform the controlled [ACCEPTANCE.md](ACCEPTANCE.md) procedure on the actual five boards, beginning with workmanship, values/polarity, soldering, dimensions/forming and normal DC function. Keep an **unpotted reference**. Allocate other units explicitly for enclosure fit, protection/reversal, full-hub cut behavior, potted continuous thermal, minimum-current daylight visibility, RF/site and potentially destructive fault/surge tests. Obtain approval for additional samples if five cannot cover the required scope.

Bare-board flying probe, an open-circuit GDT reading, dark LEDs under reversal, or basic nominal-current bench operation do not close protection or field qualification. Component 5/20 kA ratings, heavy copper and parallel terminals are not assembled ratings. Do not release for containment/protection based on basic five-board acceptance alone.

For later production, first close gate C for the intended use and settle prototype/spare allocation in MATERIALS. Requote the **actual remaining 41-station requirement**, current approved hardware revision, parts, attrition, panelization and process. Reusing an order-history entry does not authorize old Gerbers, quantities, substitutes, gold thickness, or via treatment. Revalidate files and both manufacturer approvals before any reorder.

## Sources

Capability references and the 2026-09-07 continuation's visual/process evidence are recorded in [pcb/DFM_EVIDENCE.md](pcb/DFM_EVIDENCE.md); recheck for the actual quote:

- [JLCPCB PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [via covering](https://jlcpcb.com/help/article/pcb-via-covering), [via/pad-hole tolerances](https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes).
- [PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), [assembly terms](https://jlcpcb.com/help/article/Terms-and-Conditions-of-JLCPCB-Assembly-Service), [placement-file requirements](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly), [stencil-data preparation](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders).
- [Reviewed component/manufacturer sources](REMEDIATION.md#source-links) and the [master DFM policy](README.md#via-and-component-hole-dfm).
