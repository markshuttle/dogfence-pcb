# Dog Fence Indicator & Surge Protection System

**Draft hardware revision: 1.2.0-dev. Reviewed baseline: 1.1.0. File-verified prototype artifacts are authorized; production and field release remain on hold. No upload or order is authorized.**

This repository documents a 4 km DogWatch SmartFence boundary with local DC fault
indicators and GDT surge paths. The implemented 16-part hybrid includes series
indicator branches and negative-voltage output shunts; it is not a qualified
lightning-protection design or completed hardware test report.

[REMEDIATION](REMEDIATION.md) owns the agreed requirements, issue decisions and
revision-specific results. [BOM.csv](pcb/BOM.csv) and the synchronized CAD/local
libraries own PCB population; [ASSEMBLY](pcb/ASSEMBLY.md#reviewed-components)
explains assembly applicability. [MATERIALS](MATERIALS.md#resistor-procurement-and-history)
preserves purchases, cancellations and allocations. A production pre-order is
not an implemented substitution, and prototype results do not qualify another part.

Use the working schematic, PCB, settings/rules and libraries under `pcb/`, not
generated `build/`, backups or `tmp/` copies, as design sources. File verification
does not close the [engineering holds and release gates](REMEDIATION.md#release-gates).

## 1. Deployment Baseline

| Item | Agreed requirement |
| :--- | :--- |
| Stations | **41**, at 0, 100, ..., 4000 m, covering 40 diagnostic spans. The 0 km and 4 km stations are separate boards at the shed. |
| Station types | **36 standard + 5 earth-connected**, retaining earth-connected locations at 0, 1000, 2000, 3000, and 4000 m. Five locations do not imply five independent electrodes. |
| Field equipment | One identical, fully populated board and two external LEDs per station. [MATERIALS](MATERIALS.md#1-station-inventory) owns total requirements, purchases and shortfalls. |
| Initial order | **Five fully assembled JLCPCB boards**, all required SMT and THT parts fitted. No field soldering. Prototype allocation and later production/spares are separate decisions. |
| Fabrication | Readily available **FR-4, two layers, 2 oz / 70 micrometres copper on both F.Cu and B.Cu, ENIG, nominal 1.6 mm finished thickness**. Green soldermask is the quote default, not a new performance qualification. No imposed high-Tg laminate, gold thickness upgrade, or filled-via process. |
| Enclosure | WISKA COMBI 308 with Essentra LCBSBM-6-01A-RT supports and WISKA **OneGel**, subject to assembled fit and process acceptance. Raised installation, not continuous submersion. |
| TEST duty | Nominal 36 V DC, usually one to two hours. **Continuous-safe normal TEST** is required for accidental extended operation; a timer is not the baseline safeguard. Fault/surge safety needs separate evidence. |
| Visibility | ON/OFF distinguishable at **5 m in full daylight**, at the final minimum field current and actual viewing angles. |

[MATERIALS](MATERIALS.md#assembly-and-quantity-allocation) separates field needs
from prototype consumption, the retained reference and spares. A five-board
prototype order is not five proven field spares.

## 2. Operation And Fault Localization

### Hub Contact Matrix

Both physical cable ends return to the shed. The full
[functional matrix](INSTALL.md#functional-matrix) uses **six independent ends**:
TEST feeds Start A/C positive and Start B negative, leaving End A/B/C individually
isolated. Required ties belong on source-side contacts only. No permanent End A/C
strap, opposite-end B return or dual-B negative return is permitted; those
connections defeat the agreed indication. OFF isolates all six ends at the hub,
but is not demonstrated lightning or maintenance isolation.

Follow [INSTALL's switch/source controls](INSTALL.md#switch-and-supply). Exact
switch configuration, DC suitability and global transfer require approval before
physical terminal assignment; extra poles remain unassigned. No direction
selector, automatic core classification or automatic return to RUN is required.

**TEST and OFF disable RF containment.** Provide clear RUN/OFF/TEST and fence-inactive labeling/indication, independent animal containment during testing, and an explicit operator return to RUN. See [INSTALL.md](INSTALL.md) for the controlled operating instructions and [RISKS.md](RISKS.md) for fault/earthing limitations.

### Indication For A Clean Cut

Use [INSTALL's clean-cut truth table](INSTALL.md#clean-cut-indications) for one
cut site with healthy indicators/GDTs and no additional inter-core shorts. The
first applicable state transition identifies the adjacent 100 m span, including
3900-4000 m; exact broken-core classification is not required. For multiple sites,
[repair and repeat TEST](INSTALL.md#repair-and-retest). Mixed open/short faults or
failed indicators/GDTs need separate troubleshooting; not every dark LED proves a cut.

### Station Connections

Three **WAGO 221-613** three-way splices maintain A/B/C cable continuity and provide short 2.5 mm^2 taps to `J_IN`. Normal perimeter current does **not** pass through every PCB's rails; each PCB draws its local indicator current. Surge current through a board is a different design case.

The [implemented circuit](pcb/ELECTRICAL.md#1-implemented-model) has separate
A-to-B and C-to-B one-way indicator branches. D3/D4 are output shunts after
D1/D2, not additional series parts. GDT paths join the core pairs and the separate
EARTH bus. Standard boards retain all parts but leave external `J_EARTH` unwired;
earth-connected stations follow the accepted site design.

RUN parallels the three cores at each transmitter end. The electrical record
preserves the historical parallel-resistance comparison, not RF compatibility
proof. Actual imbalance, faults, capacitance and earth coupling require checks
with the transmitter and receiver; the boards are not demonstrated RF-invisible.

## 3. Electrical Limits And Open Protection Work

Use [ELECTRICAL's named historical comparisons](pcb/ELECTRICAL.md#2-calculated-results)
and [DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md) for the current population's
cable/tolerance, leakage, power and fault screens. They are conditional models,
not measurements, enforced source limits, an exhaustive brightness minimum or
thermal qualification. The source/test commands and assumptions travel with those
records; do not copy retired-part values into current operating limits.

- Use **one TEST supply and one disconnected spare**, never interconnected
  supplies. Verify the actual unit and qualified settings under
  [INSTALL](INSTALL.md#switch-and-supply); a larger PSU does not coordinate faults.
- Negative shunts are not forward pulse-current regulators or reversed-lead
  immunity. Reverse recovery is not forward-clamp response. Ordinary RF,
  switching and nearby-lightning behavior remain unqualified.
- Cable-limited faults may not clear the fuse promptly. Powered-GDT recovery is
  unresolved, not an observed latched failure; conditional load lines do not
  predict extinction. Indicator resistors/shunts do not protect upstream GDT paths.
- Resistor wattage and SMT construction do not prove cool OneGel operation.
  Manufacturer mounting/rating transfer and actual chip/pad/PCB/material-interface
  temperatures require separate qualification; retired-part pulse/thermal data do
  not transfer. Continuous-safe normal TEST remains mandatory, without a timer.
- DC sparkover is not transient clamp voltage. Component impulse ratings,
  paralleled pins and heavy copper do not establish assembled surge/current,
  equal-sharing, direct-strike or lifetime ratings.

The [accepted risk boundaries](REMEDIATION.md#agreed-requirements) allow LED
damage from accidental installation polarity errors and rebuilding after a direct
strike, not all ordinary/nearby transient damage. Maintain the
[whole-boundary cattle-fence prohibition](INSTALL.md#cattle-fence-prohibition);
the withdrawn exposure is not qualified safe. [ACCEPTANCE](ACCEPTANCE.md) defines
the unperformed hardware tests; [RISKS](RISKS.md) explains their consequences.

## 4. Hardware Component Selection & Specifications

Use [BOM.csv](pcb/BOM.csv) and [Reviewed Components](pcb/ASSEMBLY.md#reviewed-components)
for the exact population, sourcing identities and assembly requirements. Detailed
component electrical ratings remain in [ELECTRICAL](pcb/ELECTRICAL.md#1-implemented-model);
reviewed drawings, maximum dimensions and rating conditions remain in the
controlled assembly/evidence notes. A C-code is not footprint or stock allocation
approval. The external indicator's limits, polarity, mounting and visibility
requirements are in [LED.md](LED.md).

[MATERIALS](MATERIALS.md#resistor-procurement-and-history) owns cancelled,
superseded and rejected selections. They are not substitutions or a second active
BOM. Sourcing parity does not establish job allocation; unresolved External rows
still block both publication modes under [AGENTS' sourcing rules](AGENTS.md#3-verification-and-publication).

## 5. Unapproved Alternatives

Retain these earlier sourcing suggestions for investigation, **not as approved upgrades or drop-ins**. No purchase, footprint fit, higher assembled surge capability, or lifetime benefit is established by this list. Differences in electrode configuration, body, lead diameter, pin mapping, RF loading, and thermal/pulse behavior may require redesign and new qualification.

| Intended references | Previously suggested alternatives |
| :--- | :--- |
| D1, D2 | Vishay 1N4007GP-E3/54 |
| R1, R2 | Vishay PR02000202201JA100, historical PR02 suggestion; both it and the former 1% FA100 selection are **retired, not the selected 2512 SMT part** |
| GDT_AB, GDT_BC | Littelfuse SH470 |
| GDT_AC | Bourns 2027-47-BLF or Littelfuse CG2-470L |
| Earth GDTs | Littelfuse SL1021A470R |
| J_IN, J_EARTH | Phoenix Contact 1731734, GMKDS 3/ 3-7,62 |
| LED terminals | Phoenix Contact 1715721, MKDS 1,5/ 2-5,08 |
| External LED | APEM Q14P5BXXHG02E, discussed in LED.md |

A higher resistor wattage does not reduce heat at the same resistance/current. A larger LED bezel does not prove better daylight contrast. Global sourcing/private inventory is an option only after engineering approval and a supplier quote; it is not a guaranteed route to stock or a fixed lead time.

## 6. PCB And Assembly Constraints

**Read [ASSEMBLY's Physical Guardrails](pcb/ASSEMBLY.md#physical-guardrails)
before changing geometry or process.** It owns the complete outline/mount,
copper/via, isolation, polarity, placement, land, forming and tolerance inventories.
Preserve protected geometry and distinct local LED mappings; do not narrow copper,
fold branches, add vias or trim courtyards to conceal an assembly problem.

The [retained resistor lands](pcb/ASSEMBLY.md#2512-smt-resistors) are an
alternative to the manufacturer's recommendation, not an exact-fit approval.
Actual parts, stencil/solder process, GDT forming, overhang and enclosure/support
fit remain separate acceptance tasks. Source stackup arithmetic is not a finished
thickness guarantee; ENIG is not a hermetic seal. Use the controlled notes and
[ORDERING](ORDERING.md#3-hole-via-and-solder-process) for the actual handoff.

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
- Inspect full drill circles and exposed annuli against actual `F.Mask`, `B.Mask`, and `F.Paste`, then the processed mask/stencil. [ASSEMBLY's SMT/via inventory](pcb/ASSEMBLY.md#smt-via-relocation) records the corrected aperture gaps and selected metric lands; the drawing discrepancy and actual solder-volume/profile acceptance remain held. Adjacent same-net rail-via mask circles intentionally overlap, but no component paste/mask aperture is excused over a via hole.
- Identify treatment by **coordinates and hole function**, never diameter alone. Legacy resistor holes are removed by the SMT conversion. All retained connector/GDT insertion holes remain open. Ordinary via diameters may be adjusted in CAM; check that no protected nominal drill was reduced. No fill is requested.
- **70 micrometres of exterior copper is not 70 micrometres of barrel plating.** JLCPCB's published 18 micrometres average hole plating is not a guaranteed minimum in every barrel. Agree any finished minimum used in current/surge calculations separately. Nonconductive fill adds no conductive cross-section.
- Tenting, plugging, opacity, or gel encapsulation does not prove hermetic sealing, freeze-thaw immunity, or an assembled ingress rating.

Use **component PTH pads**, never ordinary vias, for lead insertion. Record the exact manufacturer/MPN, drawing revision, maximum finished lead dimensions, pitch, proposed hole, and assembly allowance. For round holes:

```text
Round pin envelope       = maximum finished lead diameter
Rectangular pin envelope = sqrt(maximum_width^2 + maximum_thickness^2)
nominal finished hole - 0.08 mm >= maximum pin envelope + 0.10 mm
```

The last line uses JLCPCB's ordinary component-hole **+0.13/-0.08 mm** tolerance and the project's starting **0.10 mm diametral allowance after tolerance**. Increase the allowance when required; also account for pin-pitch, hole-position, and forming tolerances, particularly rigid connectors. This is stricter than simply adding 0.10 mm to a nominal pin. Do not assume press-fit tolerances for this order.

The exact [SMA lands/polarity](pcb/ASSEMBLY.md#indicator-sma-and-resistor-assembly),
[resistor lands](pcb/ASSEMBLY.md#2512-smt-resistors) and
[component hole/pad/pin schedule](pcb/ASSEMBLY.md#hole-fit-evidence) are controlled
in ASSEMBLY. Diodes and resistors are SMT, not insertion or axial-forming parts.
Allocated THT parts must pass free-insertion, GDT forming/standoff and solder
inspection with separate position/pattern allowances. Supplier CAD or nominal
pitch is not actual lot acceptance.

After drill changes, recheck pad sizes, hole/copper spacing, edge clearances and **at least 0.254 mm nominal component PTH annular ring for two-layer 2 oz fabrication**. Generic via-ring rules do not establish component-pad compliance. Finished-ring acceptance also requires hole and registration tolerances. Resolve fit in CAD, not by forced insertion or reaming plated boards.

DRC alone cannot close hole-fit, solder-wicking, body/forming, or process approval. Record the accepted evidence in the controlled assembly notes, regenerate the production outputs, and inspect the final processed files.

## 7. Enclosure, Cable And Site

Follow [INSTALL's materials/site requirements](INSTALL.md#materials-and-site),
[workshop dry-fit](INSTALL.md#workshop-assembly) and
[gel/service procedure](INSTALL.md#gel-and-service). The coastal, wet and partly
sunlit route requires assembled thermal/environmental qualification, not reliance
on component IP or temperature labels. OneGel is single-component/no mixing;
its conflicting published process/temperature fields and missing thermal data
remain unresolved in [ENVIRONMENT_EVIDENCE](pcb/ENVIRONMENT_EVIDENCE.md).

Cable identity and red/black/plain-green colours are settled; supplied-lot,
UV/wet-conduit and impulse applicability still need evidence. Label A/B/C
end-to-end: plain green is not PE, and **green/yellow is never an active core**.
Keep the boundary electrically separate from supporting fence wires and inspect
and maintain the [whole-boundary cattle-fence prohibition](INSTALL.md#cattle-fence-prohibition).

A qualified installer must approve the site-specific PE/electrode/OEM protection
arrangement, including the proposed shared shed earth. Do not directly earth a
core, switch PE or invent unbonded rods or a DC-negative earth bond. Inventory is
not an approved discharge-path design. Apply [INSTALL's safety controls](INSTALL.md#safety-first).

## 8. Verification And Release

Use the headless environment and full
[verification/publication workflow](AGENTS.md#3-verification-and-publication).
Native DRC/ERC, parity, geometry, population and exported artifacts are checked
against a complete snapshot. All errors and unreviewed diagnostics block; narrow
reviewed warnings remain visible. Tested KiCad is **9.0.7**, not an unverified
7/8 compatibility claim.

```bash
make check
make prototype
```

`make check` verifies without publication and refreshes the draft CPL only after
all file/artifact checks pass. `make prototype` / `make gerbers` may publish
**FILE-VERIFIED PROTOTYPE ONLY** with all five ledger holds deferred, not closed.
Production targets retain their holds and win mixed goals; unresolved External
sourcing blocks both modes. See the [latest handoff](REMEDIATION.md#session-handoff)
for actual results, not a reused PASS from an earlier note snapshot.

Require matching `build/status.json` and `build/manifest.json` with validated
revision/source/artifact hashes and **status=prototype, mode=prototype**, or
production **status=verified, mode=build**. Shared filenames alone prove nothing.
New attempts quarantine old outputs; run cleanup separately and preserve evidence.

[ORDERING's artifact guide](ORDERING.md#1-before-upload) describes Gerbers,
BOM/CPL, bare-board FlyTest and assembly aids. Generated mode/hold notices travel
inside both ZIPs; the seven controlled notes accompany the full release directory,
not the ZIPs alone. Never hand-edit artifacts or correct signed Y with `abs(Y)`.
Obtain separate processed CAM/stencil and parts-placement/assembly approvals.

The [release-gate definitions](REMEDIATION.md#release-gates) keep Gate P separate
from original A/B/C production/field holds. Supplier part/fit/forming, allocation,
panel/process and CAM/placement remain order tasks. Enclosure dry-fit and
prototype-dependent tests follow receipt, not as prerequisites to prototype files.
Neither file generation nor basic five-board tests authorize upload, an order,
containment/protection use or full rollout.

## 9. Documentation Map

| Document | Role |
| :--- | :--- |
| [REMEDIATION.md](REMEDIATION.md) | Agreed requirements, issue/evidence register, gates and session handoff. |
| [AGENTS.md](AGENTS.md) | Headless tooling, staging, mandatory guardrail reads and documentation maintenance. |
| [INSTALL.md](INSTALL.md), [RISKS.md](RISKS.md), [ACCEPTANCE.md](ACCEPTANCE.md) | Operating, risk and qualification procedures, synchronized by their owners with the final circuit. |
| [ORDERING.md](ORDERING.md), [MATERIALS.md](MATERIALS.md), [LED.md](LED.md) | Quote/approval workflow, procurement ledger, indicator limits and visibility target. |
| [REVIEW.md](REVIEW.md) | Reusable read-only audit brief, not a completed review or sign-off. |
| [ELECTRICAL](pcb/ELECTRICAL.md), [ASSEMBLY](pcb/ASSEMBLY.md), [DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md) | Circuit/model interpretation, physical/component controls and current parametric screens. |
| [DFM evidence](pcb/DFM_EVIDENCE.md), [environment evidence](pcb/ENVIRONMENT_EVIDENCE.md), [LED research](pcb/LED_PROTECTION_RESEARCH.md), [source research](pcb/SOURCE_PROTECTION_RESEARCH.md) | Manufacturer evidence, named historical investigations and later applicability corrections; not selected circuits or approvals. |
| [Makefile](Makefile), `pcb/pcb.kicad_sch`, `pcb/pcb.kicad_pcb`, `pcb/pcb.kicad_pro` | Build implementation and authoritative design/project sources, together with applicable rules and local libraries. |
