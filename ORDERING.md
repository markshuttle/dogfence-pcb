# JLCPCB Prototype Ordering Guide

**Draft hardware revision 1.2.0-dev; reviewed baseline 1.1.0. File-verified prototype artifacts are authorized; uploads and orders are not. Production/field holds remain in force.**

The agreed first order is **five individual, fully assembled boards**, with no field soldering. This guide describes the required quote and approval process; it does not certify the current files as ready for upload. **Gate P is the authorized file-verified prototype-artifact scope**, separate from the original [A/B/C production/field gates](REMEDIATION.md#release-gates). Supplier CAM, placement, allocated parts and separate user authorization remain necessary before an actual order.

The field requirement is **41 stations, 36 standard + 5 earth-connected, and 82 LEDs**, including both shed-end boards. Future production quantity depends on qualified prototype reuse, retained/destructive test units, and explicitly approved spares. Do not turn a five-board prototype order into five multi-up panels or automatically reorder the old production quantity. [MATERIALS](MATERIALS.md#assembly-and-quantity-allocation) controls quantity allocation.

## Board Finalization Queue

For **board/prototype-file** work, follow P3/P4 while preserving the
[physical guardrails](pcb/ASSEMBLY.md#physical-guardrails) and
[prototype population](#4-parts-and-allocation). Keep the supplier-response queue
below for a later, separately authorized five-board order. Do not restart switch,
cable or environmental research; those independent holds do not themselves
select a different circuit.

| Next board decision | Exact response/evidence needed |
| :--- | :--- |
| **2512 resistor job allocation** | Accept **ten fitted TE prototype resistors plus supplier-specified attrition** for five boards; record packaging and exact job allocation under [Parts And Allocation](#4-parts-and-allocation). No resistor lead forming or insertion-hole approval is needed. |
| **Remaining part/fit acceptance** | Exact KF129 variant and allocated Kefa/GDT pin/body/pattern limits; accepted GDT forming drawings. The selected hole/body envelopes are already implemented, not still awaiting a CAD resize. |
| **SMT and THT process** | Accept the retained **alternate project resistor lands for TE**, not a claimed manufacturer-exact pattern, and the selected metric Ruilon/SMA lands. Resolve Ruilon's 4.00 mm/0.165-inch conflict and approve actual placement, processed stencil and heavy-copper solder/inspection process. |
| **Panel and drill preservation** | Drawing for five finished individual boards, retaining all fourteen 1.00/1.80 untented vias, four mounts, outline and protected copper; account for J_EARTH's courtyard through X=161.35 and 1.30 budgeted body overhang. |
| **Placement approval** | Compare all sixteen anchors and 34 terminal datums in generated Assembly.txt with exact supplier models, using the pad-outline/courtyard Assembly.pdf. Pin numbers/nets are explicit in the text; native PDF pad numbering is not assumed. Record any supported model transform; do not hand-edit CPL or PCB pads to fix import conventions. |

This is a **supplier-response checklist, not an order authorization or a claim
that responses have been received**. [Gate P](REMEDIATION.md#release-gates) may
publish checked prototype files with **C4/C5/W3/W1/W4 deferred, not closed**;
every file/sourcing check still applies. Supplier responses above are order
tasks. Enclosure dry-fit and prototype-dependent physical tests follow receipt
under [ACCEPTANCE](ACCEPTANCE.md), not as prerequisites for prototype files.
Original A/B/C holds remain; no upload is authorized.

External material/switch evidence and unresolved discrepancies remain in [ENVIRONMENT_EVIDENCE](pcb/ENVIRONMENT_EVIDENCE.md), not this board-response queue.

## 1. Before Upload

Use the working design/project sources under `pcb/`, not backups, archived ZIPs or scratch copies. `pcb/BOM.csv` is reviewed sourcing data; `pcb/CPL.csv` is a **native-generated draft reference**, not an independently edited coordinate list or upload approval. [Electrical analysis](pcb/ELECTRICAL.md) and [controlled assembly notes](pcb/ASSEMBLY.md) record the current corrections and remaining decisions.

For Gate P file verification and the later, separately authorized supplier review, verify the actual implementation and reports for:

- The authorized **16-part SMT/THT hybrid** and [six-end functional matrix](INSTALL.md#functional-matrix). D3/D4 are output shunts after D1/D2, not extra series parts or qualified forward pulse-current regulators. The [electrical record](pcb/ELECTRICAL.md#9-simplified-indicator-direction) controls protection limitations; historical active candidates are not required purchases.
- Exact parts and local footprints against the [BOM](pcb/BOM.csv) and [reviewed component index](pcb/ASSEMBLY.md#reviewed-components), not retired selections or stock-library substitutes. D1-D4 and R1/R2 are SMT, with no insertion holes or axial-resistor standoff/forming. The retained resistor lands are an alternative to TE's recommendation requiring supplier acceptance under section 3.
- The adopted [hole/pin/pattern limits](pcb/ASSEMBLY.md#hole-fit-evidence), [body envelopes](pcb/ASSEMBLY.md#body-and-courtyard-evidence), real courtyards, reproducible local libraries, legend and GDT forming drawing. Actual allocated-lot fit and solder/process acceptance are supplier order tasks, not file-check results. A standard-looking footprint name or matching C-code is not a mechanical match.
- Corrected SMT GDT mask/paste geometry around the protected vias, native signed-Y placement, and complete population/net parity.

Use the [current normal-current cases](pcb/DESIGN_BOUNDS.md#normal-current) and [thermal screens](pcb/DESIGN_BOUNDS.md#thermal-screens) to define separate qualification work, not procurement acceptance bands, enforced source limits or a guaranteed field-current minimum. Preserve INSTALL's [one TEST source/disconnected spare configuration](INSTALL.md#switch-and-supply) and [whole-boundary cattle-fence prohibition](INSTALL.md#cattle-fence-prohibition); neither is changed by a PCB order.

Apply [AGENTS' verification/publication workflow](AGENTS.md#3-verification-and-publication) for complete-project DRC, ERC, parity, geometry, population and artifact checks. Errors, unreviewed warnings/export diagnostics and stale review inputs block; narrowly reviewed diagnostics remain visible. Do not weaken gates or refresh approval hashes to obtain a package.

`make check` verifies without publication; `make prototype` / `make gerbers` may publish **FILE-VERIFIED PROTOTYPE ONLY** after all file/sourcing checks. Unresolved external sourcing blocks both modes; file parity or public stock is not job allocation. Production targets retain all engineering holds and win mixed goals. Detailed native commands, diagnostic reviews, locking and evidence-preserving cleanup belong to AGENTS.

Use the latest revision-specific [session handoff](REMEDIATION.md#session-handoff) and matching manifest, not a part-selection statement or an old PASS. **Changed controlled-note hashes require fresh artifact evidence**, even with unchanged CAD and revision labels; this guide does not reverify an earlier Gate P package.

| Intended file | Use after verification |
| :--- | :--- |
| `build/Gerbers.zip` | PCB quote/fabrication: F.Cu, B.Cu, F.Mask, B.Mask, F.SilkS, B.SilkS, F.Paste, Edge.Cuts and separate PTH/NPTH drills. Generated mirror: `pcb/Gerbers.zip`. |
| `build/BOM.csv` | Assembly references, population and reviewed sourcing identities. |
| `build/CPL.csv` | Native-generated placement for **all required SMT and THT** parts, excluding mechanical holes/DNP items. |
| `build/pcb.d356` | IPC-D-356 connectivity for bare-board test/CAM comparison. |
| `build/FlyTest.zip` | Netlist and fabrication package for bare-board electrical testing, not an assembled functional/surge test. |
| `build/README.txt` | Generated mode and open-hold notice, included inside both ZIPs so prototype restrictions travel with the files. |

Inspect fresh exported geometry, layer/drill classification, schematic/PCB/IPC connectivity, BOM/CPL completeness, and archive members. Check `build/status.json`, `build/reports/verification.json`, readable/JSON DRC/ERC reports, and the published `build/manifest.json` revision/source/artifact hashes. Require **`status=prototype`, `mode=prototype`** for prototype files, or **`status=verified`, `mode=build`** for production files. **No matching manifest means no current file-verified package; neither pair authorizes upload or order.** Both modes use the same filenames and Gerber mirror. Assembly outputs include native pad outlines and courtyards in `Assembly.pdf`, exact footprint/terminal datums with pin numbers/nets in both coordinate conventions in `Assembly.txt`, `ViaTreatment.csv` and all seven controlled engineering notes. These are supplier-review aids, not accepted centroid corrections. Never hand-edit generated Gerbers, drills or ZIPs to bypass a failed check.

Compare the reports with [ASSEMBLY's expected file inventory](pcb/ASSEMBLY.md#reviewed-components). Design counts alone are not evidence that the current native exports passed.

## 2. Quote Specification

After Gate P file verification and **separate authorization to share the files**, request the actual quote at [JLCPCB](https://jlcpcb.com/quote). Capture the accepted options and any exceptions in the release record. The current authorization is file generation only, not this upload/quote/order step.

JLCPCB offers **standard two-layer FR-4 with 2 oz copper on both sides and ENIG**. Use the standard quote options for this combination, not an assumed special-stackup exception. No special CAM approval is implied or recorded; availability does not accept this design's hole/via, land-pattern, soldering or assembly details. The design-specific reviews below remain required.

| Item | Five-board prototype baseline / supplier confirmation |
| :--- | :--- |
| Quantity | **Five individual usable boards, all five fully assembled**. State panel-to-individual-board conversion explicitly. |
| Material | Readily available standard **FR-4**. Do not impose High-Tg 170, a particular Shengyi grade, or a claimed lifetime requirement without an approved engineering need. |
| Layers / size | **Two layers, 63 x 56 mm** per individual board. Both layers carry isolated fence and earth copper; B.Cu is not a blanket ground plane. |
| Thickness | **Nominal 1.6 mm finished board**. Confirm supplier measurement convention, including over-mask thickness, tolerance and support fit against the [controlled stackup/acceptance requirements](pcb/ASSEMBLY.md#thickness-and-process), not just the nominal arithmetic. |
| Copper | **2 oz / 70 micrometres on both F.Cu and B.Cu**. This does not specify finished barrel plating or an assembled surge rating. |
| Finish / mask | **ENIG, green soldermask default**. Record actual finish specification; do not mandate 2-microinch gold or claim a pore-free environmental seal. |
| Hole/via process | Selected standard **UNTENTED on both sides, no fill/plug/cap** for all **14 protected 1.00 mm nominal drill / 1.80 mm copper vias**, with nominal **1.80 mm F.Mask/B.Mask openings and no via paste**. Preserve positions/drills and inspect the processed data; this is not a sealed-hole process. See section 3. |
| Assembly | All **eight SMT and eight THT parts per board**, top-side, fitted and soldered, with 2512 SMT resistors and controlled axial GDT lead forming. Confirm against the accepted design before quote acceptance. |
| Service | Current public guidance permits THT under **both Economic and Standard PCBA in principle**. Confirm the exact mixed SMT/THT, 2 oz/ENIG job, part sourcing, manual operations and test scope in the actual quote. |
| Panel / tooling | Supplier-proposed rails, fiducials and tooling, with an approved drawing and depanelization method. Standard PCBA processing-size requirements may require panelization for this small board. |
| Solder process | Explicit acceptance of heavy-copper soldering, 2512 SMT / Ruilon / BYG23T SMT paste volume, THT fillets/barrel wetting and GDT forming/standoff inspection. No axial resistor forming, field soldering or forced insertion/reaming to repair fit. |
| Additional coating | Not part of the agreed baseline. Do not assume **OneGel** makes coating universally redundant or that adding coating is automatically compatible. Its process/material acceptance remains open under the [OneGel evidence](pcb/ENVIRONMENT_EVIDENCE.md#wiska-onegel) and [installation controls](INSTALL.md#gel-and-service). |
| Testing | Agree bare-board continuity/isolation test coverage and any assembled testing separately. Do not label flying probe as LED, reversal, thermal, RF or surge qualification. |
| Price / schedule | Obtain a dated itemized quote: PCB finish/copper, parts, loading/extended fees, attrition, SMT/THT labor, forming, tooling, tests, shipping and applicable taxes/import costs. No fixed stock, cost or lead-time promise is established here. |

The supplier must propose the actual panel/rail dimensions. The old **73 x 76 mm** assumption is not an approved panel plan, and rail removal is not automatic. Confirm five finished boards will be delivered in the agreed condition, with no cuts/tooling holes in protected functional copper and no damage to board edges or mounting features. Absence of fiducials on the single PCB is not itself a defect if approved panel fiducials/tooling satisfy assembly needs.

## 3. Hole, Via And Solder Process

Apply the complete [via and component hole DFM policy](README.md#via-and-component-hole-dfm). [ASSEMBLY's physical guardrails](pcb/ASSEMBLY.md#physical-guardrails) control preservation; [DFM evidence](pcb/DFM_EVIDENCE.md) supplies drawing provenance, calculations and remaining supplier facts, not replacement policy. Keep the coordinate-based via drawing and exact lot/envelope requirements with the quote/assembly package.

- Preserve all **nine rail and five earth vias**, **1.00 mm drill / 1.80 mm copper**, at the exact [function/coordinate schedule](pcb/ASSEMBLY.md#stitching-via-identification). Compare that drawing and generated `ViaTreatment.csv` with processed CAM; **never request filling by diameter**.
- Select standard **UNTENTED, both sides, no fill/plug/cap**. Each via has nominal **1.80 mm circular F.Mask/B.Mask openings**, with no via paste. Adjacent **same-net rail-via mask openings intentionally overlap** at 1.50 mm pitch; this does not permit an SMT mask/paste aperture over a via hole or annulus. No reliable 1.00 mm tenting or special filling exception is needed. Exposed ENIG is wettable: qualify solder ingress, drain-through, beads and cleanliness.
- All retained component holes remain open for insertion and no via is an insertion pad; SMT resistors and diodes have **no component holes**. Obtain written CAM agreement not to reduce protected via drills; ordinary via guidance does not guarantee a finished 1.00 mm diameter/tolerance. Any required finished-via minimum is a separate unresolved supplier fact, not assumed special processing.
- Use the [selected metric Ruilon lands](pcb/ASSEMBLY.md#smt-via-relocation). The printed **4.00 mm centre spacing is selected**, not an inner-gap dimension; the conflicting **0.165-inch** entry is not an approved erratum. **W1 remains open for that contradiction and actual placement/processed-stencil/solder-profile acceptance.**
- Compare complete drill circles, exposed annuli and actual mask/paste, not just pad centres. [Nominal aperture gaps](pcb/ASSEMBLY.md#smt-via-relocation) are not registration/solder-spread allowances. Recheck all Ruilon, 2512 and BYG23T apertures in fresh native and processed data; none may overlap a protected via hole or annulus. Preserve the **2.80 mm land/mask/paste gap** and separate **1.80 mm connected-copper gap** beneath each GDT; do not extend the full-width stubs blindly to the pad centres. Customer F.Paste does not approve the assembler's processed stencil.
- For D1-D4, use the [reviewed SMA lands and cathode mapping](pcb/ASSEMBLY.md#indicator-sma-and-resistor-assembly), not a generic SMA model. Obtain actual stencil/reflow and placement acceptance for **all eight diode apertures**, including the opposite D1/D2 and D3/D4 orientations in section 5.
- R1/R2 use the [retained alternate project lands](pcb/ASSEMBLY.md#2512-smt-resistors), **not TE's recommended pattern**. Body containment does not approve placement or solder joints. Obtain explicit supplier placement, processed-stencil and solder/reflow acceptance for this alternative under **W4**. No layout change, generic-footprint substitution or resistor holes/standoff/forming is authorized.
- For the retained Kefa and GDT holes, require `nominal finished hole - 0.08 - maximum pin envelope - 0.241421 >= 0.10 mm`. The separate **0.241421 mm diametral position budget** includes **+/-0.05 mm hole position on each axis** and an independently inspected **0.050 mm radial per-pin part-pattern limit after common rigid alignment**, through the insertion length. It is additional to the 0.10 mm diametral assembly allowance, not a replacement for it. Use rectangular-pin diagonals, not nominal widths.
- Preserve at least **0.254 mm nominal component PTH annular ring** under the applicable two-layer/2 oz rules. The adopted component rings are all at least 0.40 mm; do not substitute the generic via-ring rule or infer finished registration from nominal rings. Recheck copper/hole/edge clearances and finished-ring tolerance requirements.
- Agree any required finished barrel-copper **minimum** separately. A 2 oz outer layer and the published **18 micrometres average hole plating** do not prove a particular minimum barrel thickness. Untented ENIG does not establish that minimum either.
- Agree reflow and THT soldering processes for the heavy copper without unauthorized thermal-relief narrowing. Obtain dimensioned [GDT forming approvals](pcb/ASSEMBLY.md#axial-forming-approval), including seal support, bend radius and springback. The [GDT_AC drawing](pcb/ASSEMBLY.md#gdt_ac-forming-drawing) requires **at least 2.00 mm gap under the whole raised body/electrode/lead span**, measured above the highest finished PCB top surface before gel. Its development target is **body underside 2.50 +/-0.25 mm and complete assembled height <=8.50 mm**. These limits are not actual forming/solder-process approval; gel is not proof of equivalent air-gap insulation.

Quote/lot acceptance schedule from [ASSEMBLY's hole-fit controls](pcb/ASSEMBLY.md#hole-fit-evidence), all dimensions in mm. **E denotes an incoming procurement envelope, not a manufacturer-guaranteed finished-pin maximum.** Full calculations and body boxes remain in ASSEMBLY/DFM_EVIDENCE.

| References / family | Nominal finished hole / pad | Finished-pin limit basis |
| :--- | :--- | :--- |
| J_IN, J_EARTH / KF128 | **2.00 / 3.20** | Rectangular **E <=1.10 x 1.00**. |
| J_LED_A, J_LED_C / KF129 | **2.00 / 2.80** | Rectangular **E <=1.15 x 1.00**; supplied drawing variant still to confirm. |
| GDT_AC / Bencent B5G470L | **1.40 / 2.80** | Round **E <=0.90**; published 0.80 has no tolerance. |
| Earth GDTs / Ruilon 2R470TD-8 | **1.50 / 3.00** | Drawing maximum **1.05**, from 1.00 +/-0.05; retain after forming. |

Independently inspect every allocated controlled-envelope part for the five prototypes, including attrition, with measurement uncertainty and pin-pattern/body checks. Larger retained holes do not establish free insertion, lot yield or adequate solder fill. **W4 remains open for actual lot/pattern/body fit and process acceptance.**

Neither controlled maximum-body boxes, CAM acceptance nor a good 3D render replaces physical [COMBI 308 dry-fit](pcb/ASSEMBLY.md#combi-dry-fit-hold), support-thickness fit or solder/forming inspection. Full enclosure dry-fit follows prototype receipt; it is not a Gate P artifact prerequisite.

The KF128 J_EARTH **E body envelope reaches X=161.00 mm**, **1.00 mm beyond the nominal east edge**. With pose and a routed edge as far inward as X=159.80, budget **1.30 mm overhang**; the courtyard reaches **X=161.35 mm**. Include the [controlled envelope](pcb/ASSEMBLY.md#body-and-courtyard-evidence) in panel, depanelization, enclosure and screwdriver/wire-access acceptance; do not trim the body/courtyard or move protected earth copper to hide it.

## 4. Parts And Allocation

The [reviewed BOM](pcb/BOM.csv) controls exact manufacturer/MPN/code identities; [ASSEMBLY](pcb/ASSEMBLY.md#reviewed-components) owns component specifications and assembly applicability. **R1/R2 are TE Connectivity 35212K2FT / C4129105 in the prototype BOM only.** The production pre-order **Yageo SR2512FK-7W2K2L / C876850 is not integrated or qualified** by that BOM or TE results; apply [section 7's change review](#7-prototype-acceptance-and-later-orders) before production. [MATERIALS](MATERIALS.md#resistor-procurement-and-history) owns purchasing, cancellation and rejected-code history, not a second population list.

The BOM-derived fitted population is **16 electrical parts per board: eight SMT + eight THT, all on top**, excluding four mechanical hole footprints. Five boards require **40 SMT + 40 THT parts before attrition**. These are quote population counts, not native-check results, purchase quantities or stock reservations.

| References | Assembly | Per board | Five-board population |
| :--- | :--- | ---: | ---: |
| D1-D4 | SMT | 4 | 20 |
| R1, R2 | SMT | 2 | 10 |
| GDT_AB, GDT_BC | SMT | 2 | 10 |
| GDT_AC | THT | 1 | 5 |
| GDT_A_E, GDT_B_E, GDT_C_E | THT | 3 | 15 |
| J_IN, J_EARTH | THT | 2 | 10 |
| J_LED_A, J_LED_C | THT | 2 | 10 |
| **Total** | All top-side | **16** | **80** |

Confirm actual job-specific stock/allocation, Basic/Extended classification, packaging, minimum order/loading quantities and **order-specific attrition for every BOM line**, including the SMT GDTs. Public JLCPCB/LCSC stock does not reserve inventory or guarantee that five boards can be built. Do not use a generic 12-15-piece feeder estimate as supplier acceptance.

Whole-BOM **`allocation_verified` remains `false`**. Obtain accepted allocation of all **80 fitted parts plus line-specific attrition**, including ten TE resistors, before ordering boards. Record allocated quantities, leftovers and test/spare use in [MATERIALS](MATERIALS.md#assembly-and-quantity-allocation); purchases and this population table do not establish receipt, inspection or allocation.

If an accepted JLCPCB private-library/Global Sourcing route is offered, record ownership, leftover stock and confirmed allocation; no such route or lead time is promised in advance. Substitutions, including the [unapproved alternatives](README.md#5-unapproved-alternatives), require fresh electrical, hole/body, footprint, thermal/pulse, placement and procurement approval. A C-code, nominal pitch or larger rating is insufficient; reverse-recovery data is not forward-clamp proof. Use the [electrical qualification boundaries](pcb/ELECTRICAL.md#9-simplified-indicator-direction), not a component rating alone.

Intentional custom footprints must be supplied as reproducible project-local definitions and matched to the BOM. A standard-looking name does not prove a pin/body match. Keep schematic, layout, library tables and assembly drawings synchronized rather than compensating in a hand-maintained CPL.

## 5. Placement Approval

Native KiCad output describes **footprint placement origins**, which need checking against actual assembly centroids. Prefer the retained absolute Gerber/drill origin and **native signed-Y** convention in mm. For example, the baseline LED origins at board Y = +103 / +142 mm export as **-103 / -142 mm**, not positive screen coordinates. Never repair handedness with `abs(Y)` or by rotating/moving PCB pads.

Include every required SMT/THT part, exclude mechanical/DNP items, and normalize rotations **modulo 360**: -90 and 270 degrees are equivalent. Any origin-to-centroid or supplier-model rotation correction must be evidence-backed, keyed to the exact part/footprint, consistently transformed and recorded with the approved placement.

Compare every supplier model with [ASSEMBLY's exact origins, rotations and terminal nets](pcb/ASSEMBLY.md#placement-and-polarity) and the generated sixteen-anchor/34-terminal drawings. The following are order-review cautions, not an unverified upload-angle table:

| Part | Physical orientation to confirm |
| :--- | :--- |
| J_LED_A | North/top connector opens outward north; footprint rotation 90 degrees. Pad 1 positive is left; pad 2 B return right in the top view. |
| J_LED_C | South/bottom connector opens outward south; footprint rotation 270 degrees. Same left-positive/right-return global pad mapping. |
| J_IN | Opens left, baseline rotation 0 degrees; A/B/C pins north-to-south. |
| J_EARTH | Opens right, baseline rotation 180 degrees; all three pins on EARTH, not a multiplied current rating. |
| D1, D2 | 0 degrees, **cathode bands right toward LED positive; anodes left to resistor outputs**. Check actual pad/net mapping and the BYG23T model. |
| D3, D4 | 180 degrees, **cathodes left to LED positive; anodes right to B**. They use the local cathode-right footprint rotated, not matching global diode orientations. |
| R1, R2 | 0 degrees, nonpolar SMT on the retained alternate project lands, pending supplier placement/stencil/solder acceptance; no insertion holes, axial standoff or lead forming. |
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

For later production, separately review **Yageo SR2512FK-7W2K2L / C876850** against its own manufacturer/rating, land-pattern, thermal, pulse and process evidence. Update the controlled BOM/CAD, libraries, models and notes for the accepted production part and reverify before production release; an order does not create an approved substitution or an automatic BOM variant. **TE prototype test results do not qualify Yageo thermal behavior.** Close the applicable production/field gates for the intended configuration and settle [prototype/spare allocation](MATERIALS.md#assembly-and-quantity-allocation). Requote the **actual remaining 41-station requirement**, approved hardware revision, parts, attrition, panelization and process. Reusing order history does not authorize old Gerbers, quantities, substitutes, gold thickness or via treatment. Revalidate files and both manufacturer approvals before any reorder.

## Sources

Capability references and the 2026-09-07 continuation's visual/process evidence are recorded in [pcb/DFM_EVIDENCE.md](pcb/DFM_EVIDENCE.md); recheck for the actual quote:

- [JLCPCB PCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [via covering](https://jlcpcb.com/help/article/pcb-via-covering), [via/pad-hole tolerances](https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes).
- [PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), [assembly terms](https://jlcpcb.com/help/article/Terms-and-Conditions-of-JLCPCB-Assembly-Service), [placement-file requirements](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly), [stencil-data preparation](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders).
- [Reviewed component/manufacturer sources](pcb/ASSEMBLY.md#evidence-links) and the [master DFM policy](README.md#via-and-component-hole-dfm).
- [TE land/mounting evidence](pcb/DFM_EVIDENCE.md#te-3521-prototype-selection) and [conditional thermal screens](pcb/DESIGN_BOUNDS.md#thermal-screens). Catalogue-rating transfer is unverified, not a demonstrated two-layer failure or a new four-layer quote requirement. Other resistor families' pulse/thermal data do not qualify the prototype or production population.
- [Resistor procurement and production-order identity](MATERIALS.md#resistor-procurement-and-history); that ledger is not receipt, job allocation or engineering approval.
