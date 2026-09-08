# JLCPCB Prototype Ordering Guide

**Draft hardware revision 1.2.0-dev; reviewed baseline 1.1.0. File-verified prototype artifacts are authorized; uploads and orders are not. Production/field holds remain in force.**

The agreed first order is **five individual, fully assembled boards**, with no field soldering. This guide describes the required quote and approval process; it does not certify the current files as ready for upload. **Gate P is the authorized file-verified prototype-artifact scope**, separate from the original [A/B/C production/field gates](REMEDIATION.md#release-gates). Supplier CAM, placement, allocated parts and separate user authorization remain necessary before an actual order.

The field requirement is **41 stations, 36 standard + 5 earth-connected, and 82 LEDs**, including both shed-end boards. Future production quantity depends on qualified prototype reuse, retained/destructive test units, and explicitly approved spares. Do not turn a five-board prototype order into five multi-up panels or automatically reorder the old production quantity. [MATERIALS.md](MATERIALS.md) controls purchase history and allocation.

## Board Finalization Queue

For the current **board/prototype-file** work, finish P3's source/assembly handoff
and P4's file-verified artifacts. Keep the supplier-response queue below for a
later, separately authorized five-board order. Do not restart switch, cable or
environmental research. The authorized circuit/layout is the 16-part PS12/BYG23T
hybrid; unresolved performance holds remain recorded, not silently closed or
evidence that a different circuit is already required.

| Next board decision | Exact response/evidence needed |
| :--- | :--- |
| **PS12 job allocation** | The user selected **Uni-Royal PS122WF2201T4E / C2793873, 2.2 kohm / 2 W / 1%**, for both prototype and production and reports **110 ORDERED into their JLCPCB parts library**. Identity mapping is resolved, not receipt/inspection or PCBA-job allocation. Accept ten fitted parts plus supplier-specified attrition for the five prototypes before order. No resistor lead forming or insertion-hole approval is needed. |
| **Remaining part/fit acceptance** | Exact KF129 variant and allocated Kefa/GDT pin/body/pattern limits; accepted GDT forming drawings. The selected hole/body envelopes are already implemented, not still awaiting a CAD resize. |
| **SMT and THT process** | Accept the manufacturer PS12 lands and selected metric Ruilon/SMA lands, resolve Ruilon's 4.00 mm/0.165-inch conflict, and approve the processed stencil and heavy-copper solder/inspection process. |
| **Panel and drill preservation** | Drawing for five finished individual boards, retaining all fourteen 1.00/1.80 untented vias, four mounts, outline and protected copper; account for J_EARTH's courtyard through X=161.35 and 1.30 budgeted body overhang. |
| **Placement approval** | Compare all sixteen anchors and 34 terminal datums in generated Assembly.txt with exact supplier models, using the pad-outline/courtyard Assembly.pdf. Pin numbers/nets are explicit in the text; native PDF pad numbering is not assumed. Record any supported model transform; do not hand-edit CPL or PCB pads to fix import conventions. |

This is a **supplier-response checklist, not an order authorization or a claim
that responses have been received**. Gate P may publish checked prototype files
with **C4/C5/W3/W1/W4 deferred, not closed**; unresolved external sourcing still
blocks publication, but the former resistor External blocker is resolved by
PS122WF2201T4E/C2793873. Supplier responses above are order tasks, not a demand for
switch/environmental qualification or enclosure dry-fit before prototype files
can exist. Dry-fit and prototype-dependent physical tests follow receipt under
their controlled scopes. Original A/B/C holds remain; no upload is authorized.

External cable, OneGel, enclosure and switch manufacturer sources and unresolved discrepancies are recorded in [pcb/ENVIRONMENT_EVIDENCE.md](pcb/ENVIRONMENT_EVIDENCE.md); use MATERIALS for the latest confirmed reel labels and TEST-PSU/disconnected-spare allocation.

## 1. Before Upload

Use the working design/project sources under `pcb/`, not backups, archived ZIPs or scratch copies. `pcb/BOM.csv` is reviewed sourcing data; `pcb/CPL.csv` is a **native-generated draft reference**, not an independently edited coordinate list or upload approval. [Electrical analysis](pcb/ELECTRICAL.md) and [controlled assembly notes](pcb/ASSEMBLY.md) record the current corrections and remaining decisions.

For Gate P file verification and the later, separately authorized supplier review, verify the actual implementation and reports for:

- The authorized **16-part PS12/BYG23T hybrid and six-end hub matrix**, with **C4 negative-voltage/transient qualification, C5 PSU/fuse/GDT recovery, W3 actual continuous thermal behavior and W1/W4 process/fit acceptance still open**. Installation-polarity LED damage is user-accepted, not a required immunity feature. D3/D4 are output shunts after D1/D2, not extra series parts or qualified forward pulse-current regulators. Historical active candidates are not required purchases.
- Exact **Vishay General Semiconductor BYG23T-M3/TR / C145454** for D1-D4 and selected **Uni-Royal PS122WF2201T4E / C2793873** for both R1/R2 in the shared prototype/production BOM. The old 1N4007G/MBE0414/PR02 are retired; prior HP122WF2201T4E pending External sourcing is superseded, not ordered. D1-D4 and R1/R2 use unchanged SMT lands, with no resistor/diode insertion holes or axial resistor standoff/forming. The reported PS12 order does not establish JLCPCB-job allocation; C2791283 remains rejected history.
- The adopted component-hole, finished-pin/pattern and body-envelope limits, real courtyards, reproducible local libraries, legend and GDT forming drawing. Actual allocated-lot fit and solder/process acceptance are supplier order tasks, not file-check results. Full enclosure dry-fit remains a later prototype activity. A standard-looking footprint name or matching C-code is not a mechanical match.
- Corrected SMT GDT mask/paste geometry around the protected vias, native signed-Y placement, and complete population/net parity.

The [current electrical record](pcb/ELECTRICAL.md) and [conditional design bounds](pcb/DESIGN_BOUNDS.md) describe implementation, not protection or continuous-duty approval. The declared **35 V floor / 40.39597 V upper screen** are not enforced hardware limits; the earlier **35-37 V proposal was never implemented**. Updated PS12/BYG23T current/thermal calculations are not procurement acceptance bands or a guaranteed field-current minimum. One ordered LRS-75-36 serves TEST; its disconnected spare adds no capacity. The user's prohibition on energized cattle fencing covers the **whole 4 km boundary cable, every station and the hub**; the old 0.5 m / 300 m parallel case is withdrawn, not a current energizer-on/off qualification requirement. Maintain the restriction and reassess before use if the hazard returns; no numerical safe separation or zero induction/lightning claim follows.

The implemented build stages the **complete project**, runs **DRC, ERC, schematic/PCB parity, protected-geometry and artifact checks**, blocks errors and unreviewed warnings, and retains readable/JSON reports. The eight intentional single-sheet global-label warnings are narrowly reviewed in `pcb/verification.json` and remain visible, not suppressed. Every public export alias uses the same locked complete-package transaction. See [AGENTS.md](AGENTS.md) for the implemented workflow.

The separate netlist-export annotation warning is reviewed only for the exact tested input hashes, ten intentional nonnumeric references and KiCad 9.0.7 diagnostic. It remains in the logs; other export diagnostics or changed review inputs block. Do not treat this as a general annotation-error exemption.

```bash
make check
make prototype
```

Use headless KiCad 9 (tested baseline 9.0.7). `make check` retains evidence and refreshes the CPL reference only after all file/artifact checks pass, **without publication**. Current R1/R2 use **C2793873, `Sourcing=LCSC`, empty `Sourcing Reference`**; file parity does not verify allocation. The generic `External` route still requires empty LCSC metadata and a matching HTTPS reference, and unresolved external sourcing blocks both modes. **`make gerbers` / `make prototype` may publish FILE-VERIFIED PROTOTYPE ONLY packages after all file/sourcing checks, with all five holds deferred, not closed.** No gate change is needed for PS12. Use the latest [REMEDIATION](REMEDIATION.md) results and matching manifest; this selection alone is not a new native PASS or publication.

Production targets **`all`, `package`, `release`, `production`, `drills`, `ipc`, `bom`, `cpl`, `zip-gerbers`, `zip-flytest`** retain all engineering holds and sourcing gates. The stricter production mode wins mixed goals, regardless of order. Private drafts remain under `tmp/manufacturing/runs/attempt-*`; serial/parallel transactions use a lock and quarantine stale public outputs. `make clean` removes owned runs/outputs only; preserve useful evidence first and run clean separately.

| Intended file | Use after verification |
| :--- | :--- |
| `build/Gerbers.zip` | PCB quote/fabrication: F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, F.Paste, Edge.Cuts and separate PTH/NPTH drills. Generated mirror: `pcb/Gerbers.zip`. |
| `build/BOM.csv` | Assembly references, population and reviewed sourcing identities. |
| `build/CPL.csv` | Native-generated placement for **all required SMT and THT** parts, excluding mechanical holes/DNP items. |
| `build/pcb.d356` | IPC-D-356 connectivity for bare-board test/CAM comparison. |
| `build/FlyTest.zip` | Netlist and fabrication package for bare-board electrical testing, not an assembled functional/surge test. |
| `build/README.txt` | Generated mode and open-hold notice, included inside both ZIPs so prototype restrictions travel with the files. |

Inspect fresh exported geometry, layer/drill classification, schematic/PCB/IPC connectivity, BOM/CPL completeness, and archive members. Check `build/status.json`, `build/reports/verification.json`, readable/JSON DRC/ERC reports, and the published `build/manifest.json` revision/source/artifact hashes. Require **`status=prototype`, `mode=prototype`** for prototype files, or **`status=verified`, `mode=build`** for production files. **No matching manifest means no current file-verified package; neither pair authorizes upload or order.** Both modes use the same filenames and Gerber mirror. Assembly outputs include native pad outlines and courtyards in `Assembly.pdf`, exact footprint/terminal datums with pin numbers/nets in both coordinate conventions in `Assembly.txt`, `ViaTreatment.csv` and all seven controlled engineering notes. These are supplier-review aids, not accepted centroid corrections. Never hand-edit generated Gerbers, drills or ZIPs to bypass a failed check.

The **design inventory expected during integrated native verification** is **eight nets, 34 terminals, 32 PTH hits (18 component + 14 via), four NPTH and 52 IPC records**, with **16 electrical parts / eight SMT / eight THT** plus four mounting footprints. Expected aperture counts are **F.Mask 52, B.Mask 36 and F.Paste 16**: four PS12, four Ruilon and eight BYG23T paste apertures. These counts and all layout geometry are unchanged by the resistor selection, **not a claim that the current native exports have passed**; use revision-specific reports.

## 2. Quote Specification

After Gate P file verification and **separate authorization to share the files**, request the actual quote at [JLCPCB](https://jlcpcb.com/quote). Capture the accepted options and any exceptions in the release record. The current authorization is file generation only, not this upload/quote/order step.

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
| Assembly | All **eight SMT and eight THT parts per board**, top-side, fitted and soldered, with PS12 SMT resistors and controlled axial GDT lead forming. Confirm against the accepted design before quote acceptance. |
| Service | Current public guidance permits THT under **both Economic and Standard PCBA in principle**. Confirm the exact mixed SMT/THT, 2 oz/ENIG job, part sourcing, manual operations and test scope in the actual quote. |
| Panel / tooling | Supplier-proposed rails, fiducials and tooling, with an approved drawing and depanelization method. Standard PCBA processing-size requirements may require panelization for this small board. |
| Solder process | Explicit acceptance of heavy-copper soldering, PS12/Ruilon/BYG23T SMT paste volume, THT fillets/barrel wetting and GDT forming/standoff inspection. No axial resistor forming, field soldering or forced insertion/reaming to repair fit. |
| Additional coating | Not part of the agreed baseline. Do not assume **OneGel** makes coating universally redundant or that adding coating is automatically compatible. OneGel is a **single-component 300 ml cartridge, 10108963; no mixing**, not MP0100. Its process/material acceptance remains open; see the environment evidence and INSTALL. |
| Testing | Agree bare-board continuity/isolation test coverage and any assembled testing separately. Do not label flying probe as LED, reversal, thermal, RF or surge qualification. |
| Price / schedule | Obtain a dated itemized quote: PCB finish/copper, parts, loading/extended fees, attrition, SMT/THT labor, forming, tooling, tests, shipping and applicable taxes/import costs. No fixed stock, cost or lead-time promise is established here. |

The supplier must propose the actual panel/rail dimensions. The old **73 x 76 mm** assumption is not an approved panel plan, and rail removal is not automatic. Confirm five finished boards will be delivered in the agreed condition, with no cuts/tooling holes in protected functional copper and no damage to board edges or mounting features. Absence of fiducials on the single PCB is not itself a defect if approved panel fiducials/tooling satisfy assembly needs.

## 3. Hole, Via And Solder Process

Apply the complete [via and component hole DFM policy](README.md#via-and-component-hole-dfm). [Controlled assembly notes](pcb/ASSEMBLY.md) specify the adopted P3 limits; [DFM evidence](pcb/DFM_EVIDENCE.md) records the visually read figures, calculations and remaining supplier facts. Keep the coordinate-based via drawing and the exact lot/envelope requirements with the quote/assembly package.

- Preserve nine rail vias at X = 112.5, 114.0, 115.5 mm on each Y = 114.88, 122.50, 130.12 mm rail, plus five earth vias at X = 150.0 mm and Y = 114.88, 118.69, 122.50, 126.31, 130.12 mm. All remain **1.0 mm drill / 1.8 mm pad**.
- Select standard **UNTENTED, both sides, no fill/plug/cap**. Each via has nominal **1.80 mm circular F.Mask/B.Mask openings**, with no via paste. Adjacent **same-net rail-via mask openings intentionally overlap** at 1.50 mm pitch; this does not permit an SMT mask/paste aperture over a via hole or annulus. No reliable 1.00 mm tenting or special filling exception is needed. Exposed ENIG is wettable: qualify solder ingress, drain-through, beads and cleanliness.
- Identify holes by **function and coordinates**, never a blanket fill-by-diameter instruction. R1/R2 are now SMT with **no component holes**; the former axial hole sizes are historical. All retained component holes remain open for insertion and no via is an insertion pad. Obtain written CAM agreement not to reduce protected via drills; ordinary via guidance does not guarantee a finished 1.00 mm diameter/tolerance. Any required finished-via minimum is a separate unresolved supplier fact, not assumed special processing.
- The adopted Ruilon SMT lands are **5.50 X x 1.20 Y mm at local Y=+/-2.00**, at **X=119.50 mm**, Y=118.69/126.31, for copper, mask and paste with zero additional mask/paste margins. The printed **metric 4.00 mm centre spacing is explicitly selected**; it is not an inner-gap dimension. The manufacturer's conflicting **0.165-inch** entry is not an approved erratum. **W1 remains open for that contradiction and actual processed stencil/solder/profile acceptance.**
- Compare complete drill circles, exposed annuli and actual mask/paste, not just pad centres. The retained nominal distances to the **four Ruilon SMT apertures** are **1.239713 mm from a via drill circle** and **0.839713 mm from its full annulus/mask opening**, before actual registration/solder-spread allowances. Recheck all apertures, including PS12 and BYG23T lands, in fresh native and processed data; none may overlap a protected via hole or annulus. Preserve the **2.80 mm land/mask/paste gap** and separate **1.80 mm connected-copper gap** beneath each GDT; do not extend the full-width stubs blindly to the pad centres. Customer F.Paste does not approve the assembler's processed stencil.
- D1-D4 use `DogFence:BYG23T_SMA_K_Right`, each with **2.50 x 2.00 mm rectangular copper/mask/paste lands at local X=+/-2.10 mm**, a **1.70 mm inner gap**, and zero additional mask/paste margins. Local pad 1/cathode is +X, but D3/D4 are rotated 180 degrees. Obtain actual stencil/reflow and placement acceptance for all eight diode apertures; no diode PTHs or extra vias are added.
- R1/R2 use the manufacturer **PS12 lands: 1.35 x 3.70 mm rectangles at local X=+/-3.125 mm**, matching the existing layout, with **6.45 x 3.40 mm maximum body and 0.65 mm maximum height**. The **8.10 x 4.20 mm courtyard** and project-selected zero additional mask/paste margins remain unchanged. Review all four resistor apertures and the actual stencil/reflow process; do not substitute a generic 2512 land pattern or restore resistor holes/standoff/forming.
- For the retained Kefa and GDT holes, require `nominal finished hole - 0.08 - maximum pin envelope - 0.241421 >= 0.10 mm`. The separate **0.241421 mm diametral position budget** includes **+/-0.05 mm hole position on each axis** and an independently inspected **0.050 mm radial per-pin part-pattern limit after common rigid alignment**, through the insertion length. It is additional to the 0.10 mm diametral assembly allowance, not a replacement for it. Use rectangular-pin diagonals, not nominal widths.
- Preserve at least **0.254 mm nominal component PTH annular ring** under the applicable two-layer/2 oz rules. The adopted component rings are all at least 0.40 mm; do not substitute the generic via-ring rule or infer finished registration from nominal rings. Recheck copper/hole/edge clearances and finished-ring tolerance requirements.
- Agree any required finished barrel-copper **minimum** separately. A 2 oz outer layer and the published **18 micrometres average hole plating** do not prove a particular minimum barrel thickness. Untented ENIG does not establish that minimum either.
- Agree reflow and THT soldering processes for the heavy copper without unauthorized thermal-relief narrowing. The GDT_AC drawing retains **at least 2.00 mm gap under the whole raised body/electrode/lead span**, measured above the highest finished PCB top surface before gel. Its development target is **body underside 2.50 +/-0.25 mm and complete assembled height <=8.50 mm**. These limits do not approve actual seal support, bend radius, springback or GDT forming/solder process; the retired PR02 process is not a current order task.

Adopted component-hole schedule, all dimensions in mm. **E denotes an incoming procurement envelope, not a manufacturer-guaranteed finished-pin maximum.** The full calculations and body boxes remain in ASSEMBLY/DFM_EVIDENCE rather than being repeated here.

| References / family | Nominal finished hole / pad | Finished-pin limit basis |
| :--- | :--- | :--- |
| J_IN, J_EARTH / KF128 | **2.00 / 3.20** | Rectangular **E <=1.10 x 1.00**. |
| J_LED_A, J_LED_C / KF129 | **2.00 / 2.80** | Rectangular **E <=1.15 x 1.00**; supplied drawing variant still to confirm. |
| GDT_AC / Bencent B5G470L | **1.40 / 2.80** | Round **E <=0.90**; published 0.80 has no tolerance. |
| Earth GDTs / Ruilon 2R470TD-8 | **1.50 / 3.00** | Drawing maximum **1.05**, from 1.00 +/-0.05; retain after forming. |

Independently inspect every allocated controlled-envelope part for the five prototypes, including attrition, with measurement uncertainty and pin-pattern/body checks. The old PR02/MBE resistor holes and 1N4007G diode holes/forming are historical; current resistors and diodes are SMT. Larger retained holes do not establish free insertion, lot yield or adequate solder fill. **W4 remains open for actual lot/pattern/body fit and process acceptance.**

All maximum-body boxes are controlled from manufacturer figures or explicit E limits. Neither those boxes, CAM acceptance nor a good 3D render replaces physical COMBI 308 **PP/TPE (not polycarbonate)** dry-fit, support-thickness fit or solder/forming inspection. Full enclosure dry-fit follows prototype receipt; it is not a Gate P artifact prerequisite.

The KF128 J_EARTH **E body envelope reaches X=161.00 mm**, **1.00 mm beyond the nominal east edge**. With pose and a routed edge as far inward as X=159.80, budget **1.30 mm overhang**; the courtyard reaches **X=161.35 mm**. The old 0.30 mm body / 0.55 mm courtyard-overhang descriptions are historical only. Include the controlled envelope in panel, depanelization, enclosure and screwdriver/wire-access acceptance; do not trim the body/courtyard or move protected earth copper to hide it.

## 4. Parts And Allocation

The authorized circuit/BOM has **16 electrical parts per board: eight SMT + eight THT, all on top**, excluding four mechanical hole footprints. D1/D2 replace the old through-hole rectifiers, D3/D4 add negative-voltage shunts, and PS12 supersedes the prior HP12 selection without a layout change; axial PR02/MBE selections remain retired. **One BOM selects the same PS122WF2201T4E/C2793873 for R1/R2 in both prototype and production.** Protected rails, vias, earth geometry and LED terminals remain unchanged; no folded takeoff or additional via is implemented. The quantities below are **design population only**, not native-check results, purchase quantities or stock reservations.

| References | Exact reviewed manufacturer / MPN | Code | Per board | Five-board population |
| :--- | :--- | :--- | ---: | ---: |
| D1-D4 | **Vishay General Semiconductor BYG23T-M3/TR** | C145454 | 4 | 20 |
| R1, R2 | **Uni-Royal PS122WF2201T4E** | **[C2793873](https://jlcpcb.com/partdetail/C2793873)** | 2 | 10 |
| GDT_AB, GDT_BC | Ruilon SMD5050-470NA | C39692533 | 2 | 10 |
| GDT_AC | Bencent B5G470L | C5337217 | 1 | 5 |
| GDT_A_E, GDT_B_E, GDT_C_E | Ruilon 2R470TD-8 | C2836978 | 3 | 15 |
| J_IN, J_EARTH | Cixi Kefa KF128-7.62-3P | C474957 | 2 | 10 |
| J_LED_A, J_LED_C | Cixi Kefa KF129-5.08-2P | C475092 | 2 | 10 |
| **Total** | Implemented design population | | **16** | **80** |

Confirm actual stock/allocation, Basic/Extended classification, packaging, minimum order/loading quantities and **order-specific attrition** for every line. Public JLCPCB/LCSC stock and historical low-stock warnings do not reserve inventory or guarantee that five boards can be built. In particular, recheck C39692533 rather than relying on the earlier urgency claim. Do not use a generic 12-15-piece feeder estimate as supplier acceptance.

PS12 is **2512 SMT, 2.2 kohm / 2 W / 1% / +/-100 ppm/C referenced to 25 C**. Current BOM/CAD metadata is **manufacturer `Uni-Royal`, MPN `PS122WF2201T4E`, C2793873, `Sourcing=LCSC`, empty `Sourcing Reference`**. The JLCPCB identity mapping resolves the former resistor External blocker in both modes, not the whole-BOM allocation review: **`allocation_verified` remains `false`**. The user reports **110 ORDERED into their JLCPCB parts library**, not received, inspected or allocated to this PCBA job. Obtain packaging, order-specific attrition and accepted allocation of ten fitted resistors for the five prototypes before ordering boards. [MATERIALS](MATERIALS.md) preserves the purchase and quantity arithmetic; no agent upload or order is authorized.

**Superseded, not ordered:** HP122WF2201T4E's former External sourcing and
[NAC Semi reference](https://store.nacsemi.com/products/detail?stock=XSJMZ0000010410)
(retrieved MOQ **3,600**) remain historical leads, not current procurement tasks.
**C2791283 maps to HP122WJ0472T4E, 4.7 kohm / 5%, not HP122WF2201T4E**; that
rejected mapping is unchanged. PR02's earlier Mouser lead and the old onsemi/MBE
selections remain history in MATERIALS, not current procurement/forming tasks or
default substitutes. Preserve any separately confirmed legacy purchases.

If an accepted JLCPCB private-library/Global Sourcing route is offered, record ownership, leftover stock and confirmed allocation; no such route or lead time is promised in advance. Substitutions, including the [unapproved alternatives](README.md#5-unapproved-alternatives), require fresh electrical, hole/body, footprint, thermal/pulse, placement and procurement approval. A C-code, nominal pitch or larger rating is insufficient. BYG23T's **1300 V / 75 ns reverse-recovery** data does not establish forward clamp speed: typical **9 V / 620 ns forward overshoot at 1.5 A, 12 A/us, 25 C** is not <=5 V LED transient proof.

Intentional custom footprints must be supplied as reproducible project-local definitions and matched to the BOM. Legacy Phoenix- or resistor-style footprint names do not prove that Kefa terminals or axial GDTs match those libraries. Keep schematic, layout, library tables and assembly drawings synchronized rather than compensating in a hand-maintained CPL.

## 5. Placement Approval

Native KiCad output describes **footprint placement origins**, which need checking against actual assembly centroids. Prefer the retained absolute Gerber/drill origin and **native signed-Y** convention in mm. For example, the baseline LED origins at board Y = +103 / +142 mm export as **-103 / -142 mm**, not positive screen coordinates. Never repair handedness with `abs(Y)` or by rotating/moving PCB pads.

Include every required SMT/THT part, exclude mechanical/DNP items, and normalize rotations **modulo 360**: -90 and 270 degrees are equivalent. Any origin-to-centroid or supplier-model rotation correction must be evidence-backed, keyed to the exact part/footprint, consistently transformed and recorded with the approved placement.

Use this implemented-design orientation table against the source and supplier models, not as an unverified upload-angle table:

| Part | Physical orientation to confirm |
| :--- | :--- |
| J_LED_A | North/top connector opens outward north; footprint rotation 90 degrees. Pad 1 positive is left at X = 142.96 mm; pad 2 B return right at X = 148.04 mm. |
| J_LED_C | South/bottom connector opens outward south; footprint rotation 270 degrees. Same left-positive/right-return global pad mapping. |
| J_IN | Opens left, baseline rotation 0 degrees; A/B/C pins north-to-south at Y = 114.88 / 122.50 / 130.12 mm. |
| J_EARTH | Opens right, baseline rotation 180 degrees; all three pins on EARTH, not a multiplied current rating. |
| D1, D2 | Origins **(130.80,104.50)/(130.80,140.50) mm**, 0 degrees, cathode bands right toward LED positive: **K X=132.90, A X=128.70**. Check actual pad/net mapping and the BYG23T model, not retired through-hole geometry. |
| D3, D4 | Origins **(135.00,99.00)/(135.00,146.00) mm**, 180 degrees, **cathodes left to LED positive at X=132.90; anodes right to B at X=137.10**. Straight cathode links at X=132.90 are **1.80 mm wide / 5.50 mm long**. They use the local cathode-right footprint rotated, not matching global diode orientations. |
| R1, R2 | Origins **(120.00,104.50)/(120.00,140.50) mm**, 0 degrees; pads at **X=116.875/123.125**. Nonpolar PS12 SMT, using the unchanged manufacturer lands above; no insertion holes, axial standoff or lead forming. |
| GDT_AC | Body runs north-south over B despite the baseline footprint's 0-degree placement angle; controlled lead forming and >=2.0 mm gap are separate from a top-view render. |
| GDT_AB, GDT_BC | Centred on the revised SMT land pattern with correct electrode orientation and processed paste volume. |
| Earth GDTs | Retain 9.00 mm centre pitch and the controlled 8.21 mm body-diameter envelope with 0.10 mm per-side projected pose allowance. The resulting 0.59 mm budgeted body gap is not a 1.00 mm air-gap or impulse-insulation guarantee. Inspect the actual formed bodies and lid clearance. |

A viewer offset/rotation is not evidence of a correct machine placement file. Resolve discrepancies with the assembler and retain the corrected approved placement data; do not rely on silkscreen or a CAM engineer to silently fix all orientation errors.

## 6. Separate Approvals

Before authorizing fabrication/assembly, retain **both** approvals:

1. **Processed PCB/stencil CAM:** actual copper, mask, paste/stencil, PTH/NPTH drill function/diameters, protected vias, annular rings, outline and panel/rail/tooling plan. Confirm no unauthorized copper or hole changes, and agree depanelization/delivery condition.
2. **Parts placement and assembly:** allocated exact MPNs, approved local footprint/centroid/model rotations, all SMT/THT population, polarity, lead forming, solder process and inspection/test scope.

A checkout option called "Confirm Production File" is not proof that both reviews occurred. Record the source/artifact revision and manufacturer responses with the release. Gate P file generation does not supply these approvals or order authorization; the original Gate B remains held. Any later prototype-order decision needs the supplier evidence and controlled test scope, with prototype-dependent qualifications explicitly deferred, not fictitiously passed.

## 7. Prototype Acceptance And Later Orders

Perform the controlled [ACCEPTANCE.md](ACCEPTANCE.md) procedure on the actual five boards, beginning with workmanship, values/polarity, soldering, dimensions/forming and normal DC function. Keep an **unpotted reference**. Allocate other units explicitly for enclosure fit, selected negative-voltage protection, full-hub cut behavior, potted continuous thermal, minimum-current daylight visibility, RF/site and potentially destructive fault/surge tests. Installation-polarity LED damage is accepted with spares, not an immunity-test requirement. Obtain approval for additional samples if five cannot cover the existing scope.

Bare-board flying probe, an open-circuit GDT reading, dark LEDs under reversal, or basic nominal-current bench operation do not close protection or field qualification. Component 5/20 kA ratings, heavy copper and parallel terminals are not assembled ratings. Do not release for containment/protection based on basic five-board acceptance alone.

For later production, first close gate C for the intended use and settle prototype/spare allocation in MATERIALS. Requote the **actual remaining 41-station requirement**, current approved hardware revision, parts, attrition, panelization and process. Reusing an order-history entry does not authorize old Gerbers, quantities, substitutes, gold thickness, or via treatment. Revalidate files and both manufacturer approvals before any reorder.

## Sources

Capability references and the 2026-09-07 continuation's visual/process evidence are recorded in [pcb/DFM_EVIDENCE.md](pcb/DFM_EVIDENCE.md); recheck for the actual quote:

- [JLCPCB PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [via covering](https://jlcpcb.com/help/article/pcb-via-covering), [via/pad-hole tolerances](https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes).
- [PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), [assembly terms](https://jlcpcb.com/help/article/Terms-and-Conditions-of-JLCPCB-Assembly-Service), [placement-file requirements](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly), [stencil-data preparation](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders).
- [Reviewed component/manufacturer sources](REMEDIATION.md#source-links) and the [master DFM policy](README.md#via-and-component-hole-dfm).
- Selected parts: [Uni-Royal PS Series, SMD-SP-007 V.7, 08-Jan-2026](https://www.uni-royal.cn/en/images/userfile/file/1784854235b7c79f8d8a205c5d.pdf), via the [manufacturer PS page](https://www.uni-royal.cn/en/article.php?id=10109), and [JLCPCB C2793873 identity](https://jlcpcb.com/partdetail/C2793873); [BYG23T-M3, 89429, 25-Feb-2020](https://www.vishay.com/docs/89429/byg23t.pdf). PS manufacturer review covers pp. 1/2/4/5/6/7/8; controlled drawing evidence and limits are in [DFM_EVIDENCE](pcb/DFM_EVIDENCE.md) and [DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md). PS12's 2 W rating at 70 C ambient derates to zero at 155 C; page 6 one-pulse power/voltage curves do not establish repetitive-pulse or board qualification. SMT heat flow does not remove the loss or prove cooler continuous operation. Historical HP12/PR02 sources remain in those records and MATERIALS, not current part selections.
