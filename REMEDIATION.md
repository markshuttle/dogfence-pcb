# Remediation Plan

Prepared: 2026-09-06. Reviewed hardware baseline: v1.1.0.
Implementation handoff: **2026-09-11, hardware 1.2.0-dev**.

**Documentation deduplication is complete and file-verified, with no CAD,
population, model, rule or approval changes.** See
[Documentation Cleanup](#documentation-cleanup) for the fresh prototype package
and verification; earlier results apply only to their recorded snapshots. The
next board priority remains the five-prototype **P3/P4 supplier queue**, not renewed
switch/environmental research. [Reviewed Components](pcb/ASSEMBLY.md#reviewed-components)
owns the implemented population and assembly limits;
[MATERIALS](MATERIALS.md#resistor-procurement-and-history) owns purchasing history.
All engineering and supplier/physical acceptance holds remain open.

This is the starting context and implementation checklist for subsequent sessions. It consolidates the review and the user's later decisions, including changes to the originally proposed TEST wiring. It is not manufacturing approval, a completed hardware test report, or a board-level lightning certification.

## Start Here

1. Read [AGENTS.md](AGENTS.md) for operating instructions and physical guardrails, then this file. Read the relevant source files before editing them.
2. Inspect `git status` and the existing diff. This documentation session began on **d60c83e**, with clean tracked/staged diffs and the user-approved untracked `DeduplicationPlan.md`. Preserve work by other contributors and all unrelated evidence; earlier worktree descriptions belong to their historical sessions. No commit, push, upload or order is authorized. See the latest handoff for preserved build evidence.
3. Treat the working `pcb/pcb.kicad_sch`, `pcb/pcb.kicad_pcb`, project settings, and reviewed sourcing data as the design sources. `build/*` contains generated reports and, only after successful publication, prototype or production outputs identified by their matching manifest. Backups, archives, and `tmp/` copies are not authoritative designs.
4. Use the agreed requirements and TEST matrix below. Documents are synchronized to the current development source; `pcb/ELECTRICAL.md` and `pcb/ASSEMBLY.md` record the remaining design/evidence limitations. `REVIEW.md` remains an audit template, not completed approval.
5. P1's checking infrastructure and the selected hybrid placement are implemented. For the current **board-only request**, work **P3 assembly/fit finalization, then P4 five-board supplier review**, following [ORDERING's focused queue](ORDERING.md#board-finalization-queue). Do not choose the first unchecked P2 switch or environmental item instead. Preserve those holds without restarting research; any later approved circuit change requires renewed layout/BOM checks.
6. The unsafe whole-`tmp/` cleanup is replaced. `make clean` removes only `build/`, owned manufacturing runs and the generated Gerber mirror; it retains unrelated evidence and the last generated CPL reference. Preserve wanted run reports first, or use the evidence-preserving P6 workflow below. Run clean separately, never parallel with a build.
7. Update checkboxes, issue status, evidence, and the session log as work is actually verified. Do not mark hardware qualification complete because documentation was corrected or DRC passed. Commit, order parts, upload designs, or place fabrication orders only when requested.

Preparation already completed:

- [x] Reviewed source PCB, schematic, documentation, BOM/CPL, and generated manufacturing data.
- [x] Recorded the user's clarified operating requirements at the start of `README.md`.
- [x] Added the [via and component-hole DFM policy](README.md#via-and-component-hole-dfm), corresponding agent instructions, and corrected the related via-ordering assumptions.
- [x] Modeled the revised TEST topology and representative cut faults in temporary scripts.
- [ ] Complete all P1-P6 exits below. Implemented/file-checked portions are marked individually; open design decisions and hardware qualification are not closed by those checks.

### Current Package Status

| Package | Implemented and verified | Still open |
| :--- | :--- | :--- |
| P1 | Complete-project staging, strict native checks, fail-closed geometry/net/artifact validation, warning reviews, locked transactions and negative fixtures. | Maintain the checks for future supported geometry/tool changes; no broad warning suppression. |
| P2 | [Implemented prototype circuit](pcb/ELECTRICAL.md#1-implemented-model), preserving one-way rungs, six-end TEST and original GDTs. [DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md) distinguishes engineering assumptions, manufacturer data and unknowns. Production substitutions are not qualified by prototype results. | Actual clamp/RF/transient performance, powered recovery/fault containment, continuous thermal/source limits and exact switch approval remain separate production/field holds, not Gate P prerequisites. No new circuit or hub numbering is selected. |
| P3 | All parts placed/routed; geometry unchanged. [ASSEMBLY](pcb/ASSEMBLY.md#physical-guardrails) now owns complete human guardrails, alternate-land requirements and fit/forming inventories. | Actual allocated-lot/variant/pattern, GDT forming, placement/stencil/solder, overhang and support acceptance remain in the [board queue](ORDERING.md#board-finalization-queue). Enclosure dry-fit follows receipt, not Gate P files. |
| P4 | **Fresh Gate P package published and verified** with consolidated controlled notes and matching hashes/mode/hold notices; see [Documentation Cleanup](#documentation-cleanup). | Public stock is not receipt/inspection or job allocation; `allocation_verified` remains false. Actual supplier centroids, allocation, panel, process and CAM acceptance remain order tasks. |
| P5 | Canonical owners and linked consumer guidance consolidated under [the approved plan](DeduplicationPlan.md); independent semantic/link review preserves historical evidence and local work controls. | Future engineering changes remain impact-based; documentation review is not hardware approval. |
| P6 | **208 tests PASS including native probes; native checks and real production-refusal/prototype-publication comparisons PASS.** [Documentation Cleanup](#documentation-cleanup) records this snapshot's commands, evidence and isolated-package audit. | Actual processed CAM, allocated parts and physical qualification are **not performed**. File-verified prototype artifacts do not close production or field qualification. |

## Agreed Requirements

| Area | Agreed baseline / status |
| :--- | :--- |
| Prototype order | **Five fully assembled JLCPCB boards**, with no field soldering. Use readily available FR-4, **2 oz on both exterior copper layers**, and ENIG. Nominal 1.6 mm thickness follows the current board; green mask is a recommended quote default. Do not impose the legacy high-Tg/filled-via options without a demonstrated need and supplier acceptance. |
| Deployment | **41 stations** at 0, 100, ..., 4000 m, including separate 0 km and 4 km stations at the shed. **82 external LEDs**. Retaining the existing five earth-connected station locations leaves **36 standard stations**, not 35. |
| Quantity accounting | One board and two LEDs per station; four supports and three WAGO 221-613 splices per station imply 164 supports and 123 splices. Reconcile enclosure/gland quantities and prototype/spare allocation. Do not change records of 80 LEDs or other items already purchased into fictional purchases of the larger required quantity. |
| Fault detection | Locate one damage site affecting **any one, two, or all three cores within a 100 m span**. For multiple damage sites, locating/repairing the first fault and repeating TEST is acceptable. Exact broken-core identification is not required. |
| TEST operation | Nominal **36 V DC**, same-end feed and return as defined below. Typical use is one to two hours. **Continuous-safe normal TEST** is required for accidental extended use; a timer is not the baseline safeguard. Fault and surge safety must be evaluated separately. |
| Deliberate exclusions | No reverse-feed/direction selector, automatic core-classification system, or automatic return to RUN is required. Mixed open/short faults are not promised the same visual localization as clean open-circuit cuts. |
| Containment | TEST and OFF disable the RF fence. Provide clear hub labeling/indication and independent animal containment while testing. Restoring RUN remains an operator action. |
| PSU | **MEAN WELL LRS-75-36: one for TEST, one disconnected spare**. No parallel, series, opposite-end or separate-channel connection. Verify receipt/nameplates, installed setting/limits and fault behavior under [INSTALL](INSTALL.md#switch-and-supply); [MATERIALS](MATERIALS.md#3-shed-hub-inventory) owns the two-unit order and superseded LRS-35 belief. A larger source is not a C5 solution. |
| Switch | **Kraus & Naimer CA10.A364** provisionally replaces A362. Manufacturer 10/2025 pocketbook: **WAA364, formerly A364, eight-pole 1-0-2 centre-off, 60 degrees**. Six independent ends remain required; extra poles are unassigned. Exact supplied program/factory links, DC application and global transfer approval remain open. CA10's DC table is explicitly for ON/OFF functions, not automatic changeover approval. |
| Enclosures | WISKA **COMBI 308 (PP enclosure, TPE gasket)**, Essentra supports and **WISKA OneGel**, not MP0100. OneGel 10108963 is a 300 ml, one-component silicone cartridge with no mixing. Conflicting manufacturer cure/temperature fields and actual material/thermal compatibility remain to resolve. Raised installation, not continuous submersion. |
| Site | Isle of Man, less than 1 km from the coast; frequent rain, salt exposure, and possible condensation. Observed outdoor ambient is approximately **-10 to +30 degrees C**. Some boxes are in direct sun. These observations are not guaranteed lifetime extremes or maximum internal temperatures. |
| Cable | User confirms reels marked **CM03/05.100**, **"3 CORE (3 x 35/0.30) TINNED BLACK 100 MTR"**, and **red/black/plain-green cores**. AMC **2026 Update V.3** identifies CM03/05 as **3 x 2.5 mm^2 Class 5 tinned copper, PVC sheath, 7.4 mm maximum OD, 60 V max DC, -30 to +70 C**. Confirm that revision's applicability to the supplied lot, not the already settled product identity/colours. |
| Cable limitations | V.3 contains no numerical resistance despite its footnote. A conditional standard-based resistance envelope is analyzed in `pcb/DESIGN_BOUNDS.md`; it is not a reel measurement. The 105 C core reference is not a complete-cable rating. Permanent UV exposure, wet conduit, installation bend/temperature and impulse data remain open; no mains or -40 C claim. Plain green is an identified active core, never PE; green/yellow remains forbidden for active cores. |
| Routing | Mostly 0.3-1.0 m above ground on timber fencing with horizontal metal wire strands. Plastic conduit beneath driveways/gates; consider that conduit can become wet. No electrical connection to the supporting fence wires. |
| Cattle fencing | **Energized cattle fencing is prohibited near the ENTIRE 4 km boundary cable, station boxes and hub**, explicitly confirmed by the user. The former 0.5 m / 300 m parallel scenario is withdrawn. Inspect and maintain the prohibition, reassessing if land use changes; do not invent a numerical safe separation or require an energizer-on test of the prohibited setup. Ordinary RF/switching and nearby-lightning exposure remain relevant. |
| LEDs | Purchased baseline **APEM Q10F5SXXSG02E**, no internal resistor, 20 mA maximum per published family data and 5 V maximum reverse voltage. `02` does not mean regulated 2 V operation. Target **4-5 m visibility in full daylight**, with ON/OFF distinguishable at 5 m at the minimum field current and real viewing angles. |
| Installation polarity risk | **User accepts LED damage from accidental low-voltage polarity reversal during installation**, with replacement LEDs available. Survival of reversed LED flying leads is no longer a required feature. Check polarity before power and correct mistakes while isolated; spare quantity remains to allocate, not a new purchase. This does not waive continuous TEST safety, source/earthing safety or normal-operation transient assessment. |
| Direct lightning | User accepts potentially wholesale rebuilding after a direct strike; continued operation/direct-strike survival is not required. No numerical strike probability is established. This is **not** blanket acceptance of repeated damage from normal switching, RF, cattle-fence coupling or all nearby-lightning events. |
| Simplified design direction | User authorized the **16-part SMT/BYG23T hybrid** and the [prototype/production part-selection split](MATERIALS.md#resistor-procurement-and-history). The implemented [prototype BOM and assembly requirements](pcb/ASSEMBLY.md#reviewed-components) are not a second production BOM. Preserve existing takeoffs, rails/vias, EARTH, B returns, LED mappings and straight cathode links under the physical guardrails; **no fold or new vias**. Any production substitution needs its own evidence/model/process/thermal review and deliberate source updates; prototype results do not qualify it. |
| Earthing | User proposes sharing local earth between DogWatch protection and both shed-end boards. Confirm the connection to actual building PE/electrodes against regional OEM instructions and a qualified installer's site-specific earthing design. Do not add arbitrary unbonded rods, directly earth a fence core, or assume DC negative must be bonded to earth. Five earth-connected stations do not automatically require five independent electrodes. |

The functional choices above are settled. Do not repeatedly ask the user to choose TEST direction, automatic identification, or a timeout. Remaining manufacturer, CAM, and physical-test evidence is tracked separately below.

## TEST Topology

The settled requirement is **same-end TEST: Start A/C positive, Start B negative,
End A/B/C individually isolated**. [INSTALL's functional matrix](INSTALL.md#functional-matrix)
owns the full RUN/OFF/TEST table. Map it to actual terminal numbers only after
the exact supplied switch and its DC/global-transfer application are approved.

- Use six independent boundary-end connections so OFF leaves all six ends individually accessible/isolated. Required RUN ties and TEST positive ties belong on the appropriate source-side contacts, not as permanent field-end straps.
- The removed legacy 4PDT matrix left End A and End C joined at common Pin 8. An empty TEST throw does not separate them; the healthy core backfeeds the broken core. The negative regression reproduces this defect; do not restore that wiring.
- **Do not retain the earlier opposite-end B-return proposal.** It leaves both sides dark after a complete cable cut. **Do not connect both B ends to negative in normal TEST.** That masks a B-only break.
- Keep the transmitter and TEST supply isolated in the required modes, including the actual transfer sequence. OFF is ordinary disconnection, not demonstrated storm/lightning isolation.
- Preserve the WAGO through-splice/PCB-tap architecture. Normal perimeter current does not pass through every PCB's rails; each board draws its local indicator current. Surge current through a board is a separate design case.

Use [INSTALL's clean-cut indications](INSTALL.md#clean-cut-indications) for one
clean site, healthy boards/GDTs and no additional inter-core shorts. The first
applicable LED-state transition identifies the adjacent span, including
3900-4000 m; [repair and retest](INSTALL.md#repair-and-retest) for further faults.
Ambiguity between B-only and several multi-core cuts is accepted. Local indicator
failures and shorts need separate troubleshooting, not automatic cut diagnoses.

[Optional DMM checks](INSTALL.md#optional-dmm-checks) require all power/backup
sources disconnected, absence of voltage verified and all six ends isolated.
They aid diagnosis, not LED span localization. Do not use resistance mode on
powered wiring or a high-voltage insulation tester through connected electronics.

## Physical Guardrails

The complete human inventory is now
[ASSEMBLY's Physical Guardrails](pcb/ASSEMBLY.md#physical-guardrails), including
its linked placement, land, hole-fit, forming, via and process schedules. Read it
before any physical/source/process edit. Preserve these requirements unless the
user explicitly approves a reasoned design change; correcting a rating claim is
not permission to weaken construction. Independent executable guards remain.

Apply [README's master DFM policy](README.md#via-and-component-hole-dfm).
No ordinary via may serve as a lead-insertion hole, no filling by diameter is
authorized, and exterior copper thickness is not guaranteed barrel plating.

## Reviewed Components

[BOM.csv](pcb/BOM.csv) and synchronized CAD/libraries control the exact PCB
population and sourcing. [ASSEMBLY's component index](pcb/ASSEMBLY.md#reviewed-components)
owns human assembly applicability and expected file inventories; native evidence,
not a table of design counts, controls verification. [MATERIALS](MATERIALS.md)
owns external inventory and purchases, not a second implemented BOM.

Verify supplied items under [INSTALL](INSTALL.md#materials-and-site) and the
[manufacturer evidence](pcb/ENVIRONMENT_EVIDENCE.md). Historic stock is not new
job allocation. README's alternatives and LED.md's Q14 suggestion remain
unapproved, not drop-ins; substitutions need separate engineering/source review.

## Review Evidence

Historical checks below were performed with KiCad **9.0.7** on 2026-09-06. Recheck the source revision before relying on them. The reviewed PCB SHA-256 was:

```text
9ee7d906f1489954692362d4675ffe994d6a1076fe3551a4ad009a7fad1c8c92
```

| Check | Historical result |
| :--- | :--- |
| Existing `make check` | Zero reported errors/unconnected items, but only error-level DRC on a PCB-only staging copy. |
| Project-aware DRC/parity | 18 library warnings and five value-metadata warnings involving H1-H4 and J_EARTH; no unconnected pads. |
| ERC | Zero errors, 26 library/symbol/link warnings. |
| Stricter legend constraints | 12 additional warnings: four undersized labels and eight insufficient TrueType stroke-weight findings. |
| Pin connectivity | All eight schematic and PCB nets matched in the independent comparison. |
| Production data | Fresh exports matched all ten current Gerber/drill files after ignoring timestamps. ZIP members and copied BOM/CPL matched their sources. This did not make the CPL coordinate convention correct. |
| Copper geometry | Minimum track width 1.60 mm, different-net clearance 0.80 mm, earth separation 3.25 mm, component nominal annular ring 0.65 mm, via ring 0.40 mm, copper-to-outline 2.75 mm, NPTH-to-copper about 5.46 mm. |

No ICs, oscillators, or high-speed digital interfaces exist in the baseline milestone circuit. Do not add a blanket ground plane or decoupling network merely to satisfy a generic checklist. Any new protection circuitry must be checked for normal RF loading and isolation.

The revised DC model used 41 stations, a 36 V ideal source, 27.6 ohms per 4 km core, 2.2 kohm per indicator, and 2.8 V total LED/rectifier drop:

| Configuration | Calculated result, not measurement |
| :--- | :--- |
| Same-end TEST, healthy 4 km cable | 0.8477 A / 30.52 W; approximately 15.09 mA per source-end LED and 8.04 mA per far-end LED. |
| Five boards, negligible cable drop | 0.1509 A / 5.43 W. |
| All 41 boards, negligible cable drop | 1.2375 A / 44.55 W; beyond LRS-35-36 capacity. |
| Illustrative higher-resistance case | At 40 ohms per core and 4.0 V total forward drop, far-end LED current is about 6.21 mA. These are sensitivity inputs, not Oceanflex guaranteed limits. |
| Cut combinations | 42 cases checked all seven combinations at first/middle/final spans in both directions. Reverse-feed capability was subsequently excluded from the required implementation. |

Do not reuse the earlier legacy opposite-end-return fault-current calculations as the budget for the new topology. Recalculate shorts, follow current, tolerances, and new clamp loading in P2. The forward-only DC model is not a reverse-bias, RF, surge, thermal, or visibility qualification.

Optional local evidence may still exist in `tmp/dfm-review/`, `tmp/dfm_audit.py`, `tmp/independent_electrical_review_calcs.py`, `tmp/check_41_station_load.py`, and `tmp/test_return_topologies.py`. These are ignored scratch files and may disappear. The staged project in `tmp/dfm-review/` has review-only rule changes. Do not copy it over the authoritative project. Promote or reimplement useful checks under `scripts/` and `tests/`; do not make the finished workflow depend on scratch files.

## Issue Register

IDs retain the original review mapping. The original defects and closure criteria
are preserved below with their **current scope-specific disposition**. File-level
correction, supplier acceptance and physical qualification are distinct.

| ID | Problem and evidence | Required closure |
| :--- | :--- | :--- |
| C1 | Former onsemi D1/D2 0.90 mm holes were too small and manufacturer attribution was wrong. | **Historical defect corrected, then retired by reviewed SMT conversion.** Checkpoint ad282e3 retains the 1.10/2.20 correction and controlling-inch proof. Current D1-D4 are SMA, with no insertion holes; exact land/polarity/process checks now apply. |
| C2 | Former hand-maintained CPL had positive screen Y; custom axes/polarities differ from stock-looking names. | **Coordinate-generation correction retained for all 16 parts:** native signed Y, absolute origin and rotations modulo 360. D1/D2 cathodes east; D3/D4 cathodes west. **OPEN:** actual assembler centroid/model rotation approval. |
| C3 | Legacy End A/C common Pin 8 backfed breaks; earlier B-return proposals masked required cuts. | **Functional/software correction implemented:** six-end matrix, all 280 clean-cut cases, repair/retest and both legacy negative controls pass. Standard WAA364 catalogue contact/link schedule is now transcribed from the original graphic, not assigned to field ends. **OPEN:** exact supplied-switch configuration, DC/global-transfer approval and full-hub physical tests. |
| C4 | Series isolation alone did not guarantee LED reverse voltage; a shunt still does not regulate forward pulse current. | **SIMPLE CIRCUIT IMPLEMENTED; performance hold remains.** D3/D4 BYG23T negative shunts are fitted in the design after D1/D2. Installation-polarity LED damage is accepted. 75 ns reverse recovery is not forward-clamp speed; typical 9 V forward recovery under the datasheet's high-current test is not <=5 V LED proof. Qualify actual RF/ordinary-switching/nearby transient scope; do not require the prohibited cattle-fence configuration or the historical 40-part circuit. |
| C5 | The 2 A fuse need not clear cable-limited faults; powered GDT holdover/extinction is unqualified. | **OPEN DESIGN HOLD.** New-topology fault screens and actual published PSU/fuse limits replace the old fuse-blow claim. A modeled far-end 10 V arc draws 0.259543 A / 2.602168 W in its path with only 0.979810 A total. Select a supported protection/shutdown architecture and obtain actual powered-recovery evidence. |
| W1 | Former nine rail-via holes overlapped all four SMT GDT apertures by 0.19 mm; 1.00 mm reliable covering was unsupported. | **FILE CORRECTION IMPLEMENTED; order/process hold remains.** Selected metric 5.50 x 1.20 lands at +/-2.00 and X=119.50 give **1.239713 hole / 0.839713 annulus gaps**. All fourteen vias are now standard untented, no fill/plug/cap. Original X1 leader is resolved; printed 4.00 mm versus 0.165-inch contradiction, processed stencil/profile and retained drill acceptance remain specific supplier facts. |
| W2 | DC sparkover, component impulse ratings, heavy copper and parallel pins do not establish transient clamp limits, sharing or a board rating. | **Claims corrected; qualification OPEN.** No assembled surge/current/lifetime rating is assigned. Coordinate the actual protection/cable/earth paths and complete defined transient and recovery tests. |
| W3 | Nominal 0.50 W/resistor and a wattage label do not prove closed-OneGel temperature or continuous safety. | **TE 2512 SMT IMPLEMENTED; thermal hold remains, deferred for Gate P.** The TE prototype screen gives **0.756803 W/resistor at 40.39597 V** using an assumed 25 C reference and temperature inputs, not TE-confirmed test endpoints or measured chip/pad/PCB temperatures. TE's reference PCB is four-layer, 2 oz outer / 4 oz inner; rating transfer to this two-layer board is unverified, not demonstrated failure. Yageo production needs separate review and qualification. Require accepted source limits and instrumented duty evidence; no PR02 thermal/standoff transfer. See DESIGN_BOUNDS. |
| W4 | Original connector/earth-GDT holes lacked tolerance margin; part/process and sourcing acceptance remain incomplete. | **BOUNDED FILE DESIGN IMPLEMENTED; lot/fit/process hold remains, deferred for Gate P.** Retained hole/land geometry and minimum ring 0.40 remain. Accept the project-alternate resistor lands, actual placement/stencil/heavy-copper solder process, GDT forming and E/pattern lots. J_EARTH needs **1.00 nominal / 1.30 budgeted overhang**. Use the [reviewed prototype population](pcb/ASSEMBLY.md#reviewed-components) and [separate procurement ledger](MATERIALS.md#resistor-procurement-and-history); stock or an order is not job allocation or W4 closure. |
| W5 | Former LED torque was too high; complete enclosure fit and raised GDT geometry were unproven. | **Instructions/drawing corrected:** 0.20-0.25 Nm subject to exact APEM model; controlled whole-span >=2.00 mm overpass drawing and inspection method. **OPEN:** accepted forming tolerances, Essentra thickness fit, COMBI dry-fit and material/process tests. |
| W6 | Legacy legend, incomplete checks and inconsistent libraries/metadata undermined verification. | **File-level correction verified:** native 1.00/0.15 legend, strict effective rules, ten local footprints/six symbols, matched BOM metadata, DRC/parity/geometry and regression checks. Reviewed warnings remain visible and narrowly bound; no project severity ignores or exclusions. |
| W7 | Legacy fault, RF, earthing, environmental/lifetime and five-board sign-off claims were overstated. | **Scope/documentation corrected.** PSU allocation, cable identity/colours, OneGel identity and A364 program family resolved. Entire-boundary energized-cattle fencing is prohibited; verify/maintain that restriction rather than qualify the withdrawn parallel run. **OPEN:** actual source/switch approval, cable/environmental applicability, OneGel/thermal conflicts, RF, earthing and physical qualification. |

The source stackup now totals 1.600 mm (1.440 core + two 0.070 copper + two
0.010 mask layers), and underside references/revision identification are added.
Supplier thickness convention/tolerances, retaining an actual unpotted reference,
and manufacturer-added panel rails/fiducials/tooling still require acceptance.

## Implementation Sequence

**P1 and the selected 16-part placement are implemented. Current scope is P3/P4 board finalization for five prototypes; P5 accompanies those changes and P6 verifies them. P2 hub/performance and environmental work remain independently held, not this session's research queue. A future supported circuit/part change would reopen the affected layout/BOM checks, not justify speculative redesign now.**

Prefer small, coherent changes and reuse the implemented Python/Make tooling.
Helpers, libraries and tests described below now exist; unchecked items denote
remaining work, not permission to substitute a weaker requirement.

### P1: Verification

Files: `Makefile`, `pcb/pcb.kicad_pro`, new `pcb/pcb.kicad_dru`, `scripts/compare_nets.py`, focused checks under `scripts/` and `tests/`, `AGENTS.md`.

- [x] Stage a consistent complete project: PCB, schematic, project/rule files, library tables, and project-local libraries. Keep KiCad staging in a non-hidden, project-local directory such as `tmp/manufacturing/`.
- [x] Restrict cleanup to build-owned paths. Separate Gerber/drill scratch outputs and correct dependencies so `make -j4 all` cannot race, remove another target's files, or publish a partial package.
- [x] Check the resolved CLI by invoking it, including `--version`; do not apply `command -v` to a multiword Flatpak command. Document the tested KiCad 9 baseline rather than claiming untested 7/8 compatibility.
- [x] Make `make check` run project-aware DRC, ERC, and schematic parity. Retain readable and machine-readable reports on both success and failure. Report all design warnings; block electrical/DFM errors and unreviewed design warnings. Do not broadly suppress missing libraries, courtyard checks, or legend warnings.
- [x] Gate every public manufacturing export/package target, including direct drill, IPC, BOM, and CPL invocations, through the appropriate verification. Keep raw exports needed by checks as private scratch steps so the dependency graph does not become circular.
- [x] Set applicable two-layer/2 oz rules: at least 0.1651 mm track width, 0.20 mm general copper clearance, 0.254 mm nominal component PTH ring, 0.25 mm hole clearances, 0.50 mm copper-edge clearance, and 1.0 mm / 0.15 mm legend height/stroke with 0.15 mm pad clearance. Distinguish conservative project rules from manufacturer minima and via rings from component-pad rings.
- [x] Add explicit earth separation and geometry assertions for protected rails/vias, mounting features, LED pad/net polarity, and relevant drill/mask/paste interactions. DRC alone does not verify part fit or via covering.
- [x] Strengthen net comparison: reject empty/unrecognized input, compare full terminal membership, and check schematic/PCB/IPC-D-356 connectivity with documented net aliases, coordinate units, and rounding tolerances. Use native exports and structured source parsing.
- [x] Add positive/negative fixtures for wrong nets, lost rules, undersized holes, earth spacing and exposed SMT holes. Also reject hidden Gerber commands, displaced/malformed rounded apertures, omitted unsupported artwork and B-dependent unary annular rules; validate before any publication.

**Exit:** Known file-level defects are reproducibly detectable. An initial failure on the current design is expected, not a reason to weaken the gate.

**Current exit: met for the documented supported geometry/tool scope.** Initial
integrated failure retained the eight newly visible global-label warnings;
their narrow review did not disable any ERC category. See the diagnostic review
and negative-probe evidence in the handoff.

### P2: Electrical Design

Files: `pcb/pcb.kicad_sch`, the PCB as required, `pcb/BOM.csv`, `scripts/analyze_limits.py`, electrical tests, `INSTALL.md`, `RISKS.md`, assembly/engineering notes.

- [x] Replace legacy hub connection matrices/diagrams with the six-end functional matrix, preserving OEM protector/PE requirements. No unverified physical terminal numbers are assigned.
- [x] Recover and visually verify the standard WAA364 catalogue contact/link schedule: eight independent changeover poles, 16 switched contact pairs, 32 terminals and eight fixed common links. Record the source graphic and distinguish catalogue positions from unassigned DogFence wiring/detent roles in `pcb/ENVIRONMENT_EVIDENCE.md`.
- [ ] Match the exact offered/supplied switch article, mounting and factory-link/contact diagram to the reviewed programme; obtain application-specific DC/global-transfer approval, then assign and verify physical terminal numbers. The catalogue transcription does not close this item.
- [x] Make the default analysis use 41 stations and same-end return. Model A, B and C separately, including floating islands and one-way branches; parameterize cable resistance, voltage, LED/diode drops and temperature/tolerance inputs.
- [x] Add all seven cut combinations across all 40 spans, first/final spans and repair/retest sequences, with current/power balance and both legacy backfeed/masking negative controls.
- [x] Record the user's acceptance of LED damage from accidental installation polarity errors. Reversed flying-lead survival is no longer a required feature; correct polarity, spare allocation and safe replacement remain installation controls.
- [x] Implement the simple 16-part circuit with TE 35212K2FT / C4129105 prototype resistors and BYG23T series/negative-shunt diodes. Preserve one-way topology and no field soldering. Yageo SR2512FK-7W2K2L / C876850 is the production pre-order, not populated by this BOM; actual pulse/clamp response and light output remain qualification, not forward-current regulation or reversed-lead immunity.
- [ ] Select actual parts using maximum clamp voltage, leakage, temperature/tolerance, and pulse/current data, not just a nominal TVS/zener voltage. Check LED forward pulse current as well as reverse voltage. A voltage clamp alone is not automatically adequate forward-current protection. Recheck fault observability after any circuit change: preserve or explicitly model one-way rung behavior, rather than using the old forward-only model to validate a bidirectional replacement.
- [ ] Coordinate the primary GDTs, indicator branches, source interface, and any secondary protection. Reviewed impulse sparkover at 1 kV/us is up to 950 V for SMD5050-470NA and 1100 V for 2R470TD-8; B5G470L's 850 V figure is specified for 99% of measured values. Include lead overshoot and the cable's unverified impulse withstand.
- [x] Implement hard/resistive-short and conditional 10/15 V ignited-GDT load-line screens in the new topology, including separate earth paths and every station for inter-core faults. Explicitly distinguish CV demand from actual PSU overload/hiccup current and GDT holdover.
- [ ] Complete the actual PSU/cable/GDT dynamic and failed-device analysis, and implement a coordinated protective/shutdown arrangement. Do not infer extinction from sparkover, holding current from glow-to-arc figures, or discrimination from a reduced fuse value alone.
- [x] Remove `BLOWS (>2A)` from analysis logic. Use published Littelfuse 217 DC interruption/opening conditions and Mean Well current/power/overload envelopes; leave unmeasured hiccup and clearing times unknown. Recalculate faults for the new wiring.
- [ ] Qualify continuous resistor/LED/connector temperatures for the intended population over the actual supply range for production/field release, not Gate P. DESIGN_BOUNDS models TE 35212K2FT prototypes with declared temperature/reference assumptions and conditional catalogue-rating transfer. Yageo SR2512FK-7W2K2L production requires its own manufacturer/model/process evidence and controlled source/BOM update; TE results do not qualify it. Verify chip/pad/PCB and material interfaces; no catalogue P70 margin or retired-part mounting data qualifies closed-OneGel duty.
- [x] Define the electrical qualification scope and unresolved supplier/test evidence in `pcb/ELECTRICAL.md` and `ACCEPTANCE.md`. No needless logic, blanket earth plane, direction selector or unsupported assembled ratings were added.

**Exit:** The hub logic and protection architecture are specified, reviewed, and reflected in the schematic/BOM. Normal-operation safety is analyzed; remaining powered-surge qualification is explicitly open rather than declared solved by prose.

**Current exit: partial.** The simple 16-part hybrid is implemented, not
mandatory L1/L2 active circuitry. Installation-polarity LED damage is accepted;
the entire-boundary cattle-fence prohibition is confirmed. Ordinary transient
and actual continuous thermal behavior remain unmeasured. K.12's
135 V/1300 ohm feed still does not establish actual powered-GDT recovery;
hazardous resistive faults and the source interface remain to resolve.
See ELECTRICAL section 9 for the current direction, keeping section 8's
calculations/rejections as evidence. W3 remains a hard requirement; the proposed
35-37 V window is not hardware-enforced or the only possible passive design basis.
The standard WAA364 contact/link schedule is now known, but the exact supplied
configuration and loaded DC/global-transfer acceptance still block hub numbering.

### P3: PCB DFM

Files: `pcb/pcb.kicad_pcb`, schematic footprint assignments, project-local libraries/tables, `pcb/pcb.kicad_pro`, `pcb/pcb.kicad_dru`, controlled assembly/fit notes under `pcb/`.

- [x] Create project-local definitions for intentional geometry: ten footprints and six symbols. Preserve global pad/net mappings through migration, including distinct LED connectors and the cathode-right diode. Deliberate DFM relocations are recorded separately in `pcb/ASSEMBLY.md`.
- [x] Historically correct the onsemi hole/identity defect, then replace D1/D2 with reviewed SMA BYG23T in the hybrid. No current diode PTH remains; current source/native gates check the exact SMA pad/net/polarity geometry.
- [ ] Accept actual allocated finished leads, body datums and pin patterns against the adopted drawing/E limits, including plating/burrs and forming uncertainty. KF128/KF129 now use 2.00 mm holes, not an unselected 1.60 mm CAD suggestion. Missing manufacturer maxima are not closed by an unperformed lot inspection.
- [x] Read the original pin/body/SMT figures; resolve the earth-GDT 1.05 maximum and real KF129 drawing conflict. Define explicit conservative E/pattern procurement envelopes for missing maxima, separately from actual lot acceptance.
- [x] Implement bounded component-hole sizes, independent position budgets and body/courtyard envelopes, preserving retained THT pad centres, mapping, rails and vias. Minimum nominal ring is 0.40 mm. R1/R2 and D1-D4 now have SMT lands, not PTH forming; retained GDT forming/standoff still needs supplier acceptance.
- [x] Apply selected hole/position budgets, >=0.10 mm residual diametral allowance and >=0.254 nominal rings; recheck exported holes/copper/edges. Actual part-pattern, GDT forming and selected resistor/SMA land/polarity/stencil/solder acceptance remain separate. Never repair insertion by reaming PTHs.
- [x] Rebuild body/F.Fab and courtyard envelopes with pose/assembly clearance, including the diode courtyard correction found in review. No protected placement changes or courtyard trimming.
- [ ] Accept actual rework/screwdriver access and the inspected body/forming projections; drawing clearance is not physical access proof.
- [x] Retain the collision-removing GDT_AB/BC X=119.50 and GDT_AC X=125.80 relocation, all nine rail vias and full-width copper. The continuation replaces the former lands with **5.50 x 1.20 mm, 4.00 mm centres**; full drill-circle/annulus/mask/paste separation is checked.
- [ ] Follow the selected GDT land pattern and obtain solder-volume/thermal-process acceptance. If no compliant solution preserves the protected geometry, obtain explicit design/process approval rather than shrinking vias or assuming 1 mm resin filling is standard.
- [x] Implement the visually resolved metric SMD5050 pattern (5.50 x 1.20, 4.00 centres) and standard untented 1.80 mask openings on both sides. Keep the inch discrepancy and actual solder/CAM acceptance open; no fill exception or guardrail change is needed.
- [x] Place/route the selected **16-part hybrid**, followed by the authorized HP12 SMT conversion and straight cathode links in 02661d8. Correct its resistor lands/body/courtyards to the manufacturer drawing and retain strict geometry regressions. No additional protection placement, thermal-relief narrowing, fold, new via or direction selector is introduced. Native verification for this correction is recorded in the latest handoff; supplier and performance approvals remain separate.
- [x] Preserve the historical PS12 body/land review, **SMD-SP-007 V.7, 08-Jan-2026**, as evidence for the retained geometry, not a current part/process approval. Independently review TE **9-1773463-5 Rev G, 02/2025**: body containment is supported, recommended lands differ, and the four-layer reference PCB limits rating-transfer claims. Retain the alternative geometry without a reroute; actual TE placement/stencil/process acceptance remains W4 and thermal qualification W3.
- [x] Correct legend height/stroke/clipping using native 1.00 / 0.15 mm text. Retain polarity, cathode and A/B/C/EARTH labels; add underside references, F.Fab aids and 1.2.0-dev identification. Native DRC and rendered drawings checked.
- [x] Reconcile the source stackup sum to 1.600 mm while retaining 0.070 mm copper on both sides.
- [ ] Agree finished-thickness convention/tolerance in the actual quote and verify Essentra hole/panel-thickness engagement, including fabrication tolerance.
- [x] Add the controlled assembly drawing/notes, including GDT_AC's whole-span >=2.00 mm gap, 15.24 mm pitch, orientation and uncertainty-aware inspection method.
- [x] Bound retained GDT forming room and J_EARTH panel envelope against source geometry, with regressions. Former PR02 forming-room calculations remain history only; SMT removes that order task. Required GDT supplier drawing fields remain explicit.
- [ ] Approve retained GDT forming tolerances/process for assembly. After receipt, perform full COMBI 308 dry-fit with actual WAGOs, cable bends/glands, earth wires, supports, lid LEDs and screwdriver access. CAD does not replace physical fit; received-board dry-fit does not gate prototype files.

**Exit:** Layout and library checks pass with genuine geometry. Part-fit evidence and the chosen via/solder process are either accepted or explicitly held for CAM, never assumed from DRC.

**Current exit: bounded file design implemented, supplier acceptance partial.**
Original figures are resolved, metric lands and standard untented processing
are selected, and source/library hole/body envelopes are explicit. Unknown
guaranteed maxima are controlled by declared E/pattern lot limits, not guessed
to be manufacturer specifications. Actual lot acceptance, forming/solder fill,
metric/inch clarification, processed CAM and COMBI/support fit remain W1/W4/W5
evidence. The selected hybrid placement is already implemented and file-checked;
only a later approved circuit/part change would require another placement step.

### P4: Prototype And Production Data

Files: `Makefile`, `pcb/BOM.csv`, `pcb/CPL.csv`, small export/validation helpers, generated `build/*`, assembly output sources.

- [x] Keep `pcb/BOM.csv` as reviewed sourcing data for the **16-part** population. Prototype BOM uses verified **C4129105**, `Sourcing=LCSC` and empty sourcing reference in both CAD sources. This resolves the prototype resistor procurement blocker. Yageo SR2512FK-7W2K2L is ordered for production; prior Uni-Royal PS12 order was cancelled/refunded. In-stock JLCPCB status is not PCBA-job allocation.
- [x] Generate CPL from native KiCad mm positions for all SMT/THT parts, excluding mechanical/DNP items. `pcb/CPL.csv` is a generated reference, refreshed only after complete file checks, never a second placement input.
- [x] Retain absolute Gerber/drill origin and native signed-Y placement; validate common coordinates and rotations modulo 360 without taking absolute Y.
- [x] Generate exact-part/footprint anchors and all 34 electrical terminal datums in both PCB and signed-Y fabrication coordinates, with native pad outlines/courtyards for review. Do not infer a centroid from a body/courtyard midpoint; actual supplier transforms remain the separate next item.
- [ ] Verify every selected JLCPCB model's centroid and rotation. Native position output describes footprint placement origins, which must be checked against intended assembly centroids; document any anchor-to-centroid correction. Record only evidence-backed corrections, keyed clearly to the actual part/footprint. GDT_AC's internally vertical geometry and D1/D2's cathodes-right mapping must not be inferred from their old standard-looking footprint names. Do not move/rotate PCB pads to compensate for an import mistake.
- [x] Export copper, mask, legend, top paste, outline, separate PTH/NPTH drills and IPC-D-356 to fresh private scratch outputs. Customer F.Paste does not approve the assembler's processed stencil.
- [x] Validate actual exported geometry, drills, BOM/CPL, connectivity and ZIP payloads before either publication mode. Quarantine stale outputs and preserve filenames. Production still blocks on all engineering holds; prototype exports retain those holds as explicitly deferred and still block on every file/sourcing failure.
- [x] Export native assembly PDF, placement text, coordinate-based via CSV and controlled engineering notes. Implement and test release-manifest revision/tool/source/artifact hashes and results; no generated files are hand-edited.
- [x] Implement separate `gerbers`/`prototype` and production modes, production precedence for mixed goals, explicit mode/status manifests and generated scope/hold README text inside both transferable ZIPs. No diagnostic, geometry or sourcing gate is waived.
- [x] Resolve the selected prototype resistor identity with user-approved **TE Connectivity 35212K2FT / C4129105** (in stock at JLCPCB); record Yageo SR2512FK-7W2K2L production pre-order and Uni-Royal PS12 cancellation.
- [x] Republish the corrected TE 35212K2FT **Gate P prototype** snapshot after native/file checks and real serial/parallel prototype comparison. C4/C5/W3/W1/W4 remain deferred, not closed; **TE Review Corrections** controls current results, not the earlier TE or PS12 snapshots.
- [ ] Publish a **production** manifest/package only after an evidence-backed file-release review closes the production holds. Gate P authorization does not satisfy this item.
- [ ] Obtain order-specific acceptance for 2 oz/ENIG mixed SMT/THT assembly, actual part allocation/attrition, heavy-copper soldering, and GDT lead forming. Current public guidance permits THT under both Economic and Standard in principle; verify the exact quote instead of asserting a universal service restriction.
- [ ] Approve manufacturer-added rails, fiducials, tooling, and depanelization without cuts/holes in protected functional copper. Standard PCBA's processing-size requirement may require panelization for this 63 x 56 mm board. Do not assume the old 73 x 76 mm panel or automatic rail removal, and distinguish five individual boards from five multi-up panels.
- [x] Provide exact coordinate-based identification of all 14 stitching vias in `pcb/ASSEMBLY.md` and generated `ViaTreatment.csv`, including required 1.00 / 1.80 mm geometry and no fill-by-diameter instruction.
- [ ] Obtain actual via-treatment/CAM acceptance, confirm protected drill sizes were not reduced, and agree any required minimum finished barrel copper separately. The published average is not a minimum guarantee; retained connector/GDT holes remain open and resistor holes are removed.

**Exit:** Verified production data is generated reproducibly and is unambiguous for assembly. Bare-board flying-probe continuity is not advertised as assembled functional or surge testing.

**Current exit: corrected TE Gate P files published and verified, including real serial/parallel comparison.** Earlier publication results are historical. Production remains held. Supplier placement, CAM, panel, allocated parts and process approvals remain order tasks; they are not replaced by artifact verification or physical environmental/switch tests.

### P5: Documentation

Synchronize documents alongside the relevant implementation, then perform a final consistency pass. Keep user-confirmed purchases distinct from required quantities and proposed replacements.

- [x] `README.md`: correct counts, topology, model baselines, identities, actual DFM/build status and unsupported lifetime/surge claims; distinguish nominal, calculated and measured evidence.
- [x] `INSTALL.md`: replace legacy hub matrices with six independent ends, repair/retest, accurate OFF/fence-inactive labeling and safe DMM checks; correct LED torque, cable/core identification, gland/dry-fit/potting requirements and prohibit active green/yellow conductors.
- [x] `ORDERING.md`: use the five-assembled-board baseline, actual geometry and explicit remaining via/land/process holds, separate PCB CAM and placement approvals, quote-specific sourcing/panels and no unsupported stock/lead-time/sealing promises.
- [x] `ACCEPTANCE.md`: separate workmanship, normal DC, protected reversal, measured continuous thermal, 5 m daylight, full-hub cuts, enclosure/material, RF/site and qualified fault/surge tests; define instrumentation/uncertainty and retain an unpotted reference allocation.
- [x] `RISKS.md`: correct fuse/reversal analyses and include follow current, failed devices, unequal firing/residual voltage, PE/touch/step potential and coastal/solar/cable limitations. Replace the withdrawn cattle-fence exposure with the confirmed whole-boundary prohibition and reassessment if it changes; no unsupported ratings or guarantees.
- [x] `MATERIALS.md`: reconcile 41 stations / 82 LEDs / 164 supports / 123 splices, pending boxes/entries, prototypes/spares and PSU/switch candidates. Preserve orders of 80 LEDs / 160 supports / 120 splices; field-only shortfalls are 2 / 4 / 3 before extra samples or spares.
- [x] `LED.md`: explain the purchased no-resistor indicator, 20 mA / 5 V reverse limits and 5 m target; keep alternatives unqualified.
- [x] `AGENTS.md`: synchronize actual headless CLI, strict transactional build/rules/libraries, tested environment, cleanup/evidence ownership and physical/DFM invariants without unsupported ratings.
- [x] `REVIEW.md`: update the reusable audit template for the agreed prototype specification, distinct from this actual issue/evidence record.
- [x] Assign **1.2.0-dev** consistently to PCB/schematic, visible board identification, documents and revision-bound verification/manifest generation. Keep unresolved design/manufacturing/field holds explicit.

**Exit:** Documents agree with the actual remediated design and clearly separate file verification from hardware/site evidence.

**Current exit: met for the present development draft**, not an approved final
protection design. Repeat synchronization after any circuit/part/process change.

### P6: Validation

- [x] Run full stdlib/native tests and `make check` for the corrected TE model/evidence snapshot: **208 PASS, no skips**, including **23 electrical +14 design-bound tests** and six native probes. Earlier 207-test results are historical. Repeat after supported source/process changes; these are file/model tests, not hardware qualification.
- [x] Repeat separate clean `make all` and clean `make -j4 all`, preserving evidence and comparing validated geometry/connectivity/population. Both return exit 2 solely for the same five open holds; comparison passes, not production publication.
- [x] Repeat real TE serial/parallel **prototype publication** with `--target prototype`: clean, serial `make prototype`, clean and `make -j4 prototype` all exit 0, with matching geometry, population, corrected notes and manifest/mode/hold notices.
- [x] Exercise missing rules/project, wrong net, inadequate earth spacing, undersized diode hole, exposed via aperture, missing BOM/CPL part, reversed Y and missing layer fixtures, plus parser/export/race/staleness/diagnostic regressions. Invalid releases are blocked. Other THT maximum-pin fit remains an external evidence hold, not a claimed automatic fit check.
- [x] Inspect rendered PCB/schematic/assembly data and validate native-generated copper/mask/paste/legend/drill geometry and archives. Retain supported-geometry and rendering limitations with the reports.
- [ ] Review actual JLCPCB processed PCB/stencil and placement, including hole treatment, maximum-pin fit, forming/standoff and panel/tooling locations, before production approval.
- [ ] Perform basic workmanship, value/polarity, and normal-function acceptance on all five prototypes. Allocate appropriate units to protected-reversal, full-hub cut, continuous potted thermal, enclosure-fit, and potentially destructive protection tests while retaining an unpotted reference. Inspect both source-end and reduced-voltage far-end conditions; seek approval for additional samples if the qualification program needs them.
- [ ] Test the actual indicators at 5 m in full daylight, at the final minimum expected current and real viewing angles. Confirm OFF is not confused with sunlit lens colour. Prefer optical improvements before increasing current; any alternative LED or resistor change needs renewed electrical/thermal/fit checks and procurement approval.
- [ ] Qualify RUN with the actual cable, fence construction/height, transmitter and receiver; check unintended responses, lost field, misleading indications and normal switching/recovery. Verify and maintain **no energized cattle fence near the entire boundary/stations/hub**. Do not require the withdrawn energizer-on comparison unless a future approved land-use/design change reintroduces that exposure.
- [ ] Complete the defined source-fault/surge recovery and discharge-path qualification with appropriate equipment and expertise. Do not use ordinary DMM/grounded-scope practices as an improvised high-voltage test method. Verify installation earthing with the qualified installer and applicable OEM/regional requirements.
- [ ] Retain one unpotted golden/reference sample, record per-board results and exact parts/process revision, and update issue closure with evidence. Passing basic bench tests alone does not authorize the full perimeter rollout.

## Release Gates

**Current disposition: original A, B and C remain HELD; Gate P is MET for the
fresh documentation-cleanup snapshot under
[Documentation Cleanup](#documentation-cleanup).**
The user explicitly permits prototype files without environmental, switching or
completed hardware qualification. This does not close or rename any of the five
ledger holds. `make gerbers` and `make prototype` retain **C4, C5, W3, W1 and W4 as deferred**,
while every source/library/DRC/ERC/net/geometry/artifact and sourcing check still
blocks. The [reviewed BOM](pcb/BOM.csv) resolves prototype identity without a
gate override. Public stock is not whole-BOM job allocation or a substitute for
current native/file verification.

Production targets `all`, `package`, `release`, `production`, `drills`, `ipc`,
`bom`, `cpl`, `zip-gerbers` and `zip-flytest` retain all holds and sourcing gates.
**Production wins mixed goals in either order.** `make check` never publishes.
C2/W5 and broader supplier/hardware/site evidence remain tracked even though
they are not separate machine hold IDs.

| Gate | Required evidence | What it does not mean |
| :--- | :--- | :--- |
| **P: Prototype files** | Complete strict file/artifact checks, resolved exact sourcing metadata, reviewed current geometry and synchronized notes. All five production ledger holds may remain explicitly deferred. Manifest must have `status=prototype`, `mode=prototype` and matching revision/source/artifact hashes; ZIP README notices travel with the files. | Not upload/order authorization, accepted supplier CAM/placement/allocated parts, received-board dry-fit or electrical/environmental/switch qualification. |
| **A: File ready** | Source/library/rule consistency, correct hub/circuit design, passing automated checks, regenerated and reviewed BOM/CPL/fabrication data, synchronized documentation, explicit open qualification items. | Not CAM acceptance, physical fit proof, or field qualification. |
| **B: Prototype order** | Gate A plus required part/fit/process/placement/CAM acceptance and a defined, controlled prototype test scope. Known diode-hole/CPL/wicking defects must not be silently accepted as "the prototype will test it." | Not permission to rely on the prototypes for lightning protection or containment before qualification. |
| **C: Field release** | Required normal/fault/reversal/thermal/visibility/RF/site/protection evidence, accepted earthing, verified installation materials, and documented performance limits for the intended use. | Not an untested 20 kA board rating, direct-strike protection, or multi-decade warranty. |

The original A/B/C requirements above remain the production/field baseline;
they are **not prerequisites for Gate P**. Before a separately authorized actual
prototype order, accept the P3/P4 supplier part/fit/forming, processed CAM/stencil,
placement, panel and process evidence and define its controlled test scope.
Enclosure dry-fit and prototype-dependent electrical/thermal/switch/site tests
follow receipt. Never turn deferred C4/C5/W3 or W1/W4 into fictitious passes, or
call every missing qualification a demonstrated certain hardware failure.

Both modes use `build/Gerbers.zip` (mirror `pcb/Gerbers.zip`), BOM/CPL, FlyTest,
assembly outputs and notes. Only the matching manifest identifies the current
package: **prototype `status=prototype`, `mode=prototype`** versus **production
`status=verified`, `mode=build`**. A filename, status alone, stale ZIP or private
draft is insufficient. Use **[Documentation Cleanup](#documentation-cleanup)**
for this session's publication results. PS12 Selection and both TE handoffs
retain the evidence for their earlier snapshots, not changed-note verification.

The build's success message should mean **"manufacturing data verified for this revision"**, not **"20 kA lightning protection verified."**

## External Evidence

These are evidence-gathering tasks, not reasons to reopen settled feature decisions:

- [x] Confirm user procurement/allocation: two LRS-75-36 ordered, one TEST and one disconnected spare. No dual-source connection.
- [ ] Inspect received PSU nameplates and establish the installed output setting/limits and dynamic fault behavior.
- [ ] Obtain the exact CA10.A364/current WAA364 order-specific contact development, DC breaking suitability, global transfer sequence, mounting details and insulation conditions. Eight-pole identification and the standard catalogue contact/link schedule are resolved; correspondence to the supplied article, DogFence terminal assignment and application approval are not.
- [ ] Obtain exact component drawings/tolerances, verify connector pin fit and body envelopes, and record the accepted forming/solder process.
- [x] Confirm reel product identity CM03/05.100 and red/black/plain-green colours from the user's actual markings; use the specified AMC 2026 Update V.3.
- [ ] Confirm V.3/standard resistance applicability to the supplied cable lot, long-term exposed-weather/UV and wet-conduit suitability, installation bend limits and insulation/impulse data. Its 60 V working rating is not surge-withstand evidence.
- [ ] Obtain the supplied **OneGel** lot's dated process/safety clarification: one component/no mixing is resolved, but WISKA lists conflicting cure and temperature fields. No readable OneGel-specific thermal conductivity or exact material-combination approval was found. Resolve those facts and the actual PP/TPE/PVC/adhesive/WAGO compatibility, not a generic MP0100 process.
- [ ] Obtain JLCPCB's exact quote, part allocation/attrition, panel/rail plan, via treatment, relevant barrel-copper minimum, and processed PCB/stencil/assembly acceptance.
- [x] Confirm the user's energized-cattle-fence prohibition covers the full 4 km cable, station boxes and hub, not only the transmitter.
- [ ] Verify/maintain the prohibition in the installed site survey and reassess if land use changes. The earlier 0.5 m / 300 m parallel exposure is withdrawn, not a mandatory test or a safe-distance claim.
- [ ] Obtain the site-specific earthing/bonding review and required physical qualification results. Do not copy US outlet-faceplate grounding instructions directly into an Isle of Man installation.

## Source Links

Specifications were researched on 2026-09-06; recheck revisions and order-specific capabilities. Public stock is not a purchase allocation. Prefer primary manufacturer/fabricator sources and retain accepted evidence with the release.

- [JLCPCB fabrication capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [via covering](https://jlcpcb.com/help/article/pcb-via-covering), and [via versus pad-hole tolerance](https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes).
- [JLCPCB PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), [placement-file requirements](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly), [stencil-data preparation](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders), and [assembly terms](https://jlcpcb.com/help/article/Terms-and-Conditions-of-JLCPCB-Assembly-Service).
- [onsemi 1N4007 family datasheet](https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf) and [C232439 identity](https://www.lcsc.com/product-detail/C232439.html). Reviewed drawing maximum lead: 0.86 mm. Reconcile other ratings with the actual revision, including temperature limits and the meaning of ordering suffixes.
- [Vishay MBE0414 family datasheet](https://www.vishay.com/docs/28766/mbxsma.pdf), including derating, mounting dimensions, and pulse curves.
- Resistors: [TE Connectivity 3521 Series, Data Sheet 9-1773463-5 Rev G, 02/2025](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7F9-1773463-5%7FG1%7Fpdf%7FEnglish%7FENG_DS_9-1773463-5_G1.pdf), [JLCPCB C4129105](https://jlcpcb.com/partdetail/C4129105); user-confirmed and independently verified [Yageo SR2512FK-7W2K2L / JLCPCB C876850](https://jlcpcb.com/partdetail/C876850) production-order identity, not manufacturer/model/process/thermal acceptance; historical [Uni-Royal PS Series, SMD-SP-007 V.7, 08-Jan-2026](https://www.uni-royal.cn/en/images/userfile/file/1784854235b7c79f8d8a205c5d.pdf), [JLCPCB C2793873](https://jlcpcb.com/partdetail/C2793873) and HP12 / PR02. DFM_EVIDENCE records the corrected TE revision and unretained March 2023 citation.
- [Ruilon SMD5050-470NA](https://www.lcsc.com/datasheet/C39692533.pdf), [Ruilon 2R470TD-8](https://www.lcsc.com/datasheet/C2836978.pdf), and [Bencent B5G470L](https://www.lcsc.com/datasheet/C5337217.pdf) manufacturer documents distributed through LCSC.
- [KF128-7.62-3P](https://www.lcsc.com/datasheet/C474957.pdf) and [KF129-5.08-2P](https://www.lcsc.com/datasheet/C475092.pdf) drawings; verify maximum finished pin dimensions, not only linked CAD land patterns.
- [APEM Q10F5SXXSG02E](https://www.apem.com/led-indicators/professional-grade-panel-mount-led-indicators/q10/q10f5sxxsg02e): no-resistor option, 5 V reverse limit, 20 mA family maximum, model-dependent viewing/torque data, and -40 to +85 degrees C temperature range.
- [WISKA COMBI 308 LG](https://www.wiska.co.uk/en/30/pde/10060400/combi-308-lg.html): external 85 x 85 x 51 mm, -30 to +100 degrees C, IP66 via membrane and IP67 with the specified gland arrangement. These are not automatic ratings for the modified/potted assembly.
- [Essentra support listing](https://www.digikey.com/en/products/detail/essentra-components/LCBSBM-6-01A-RT/392198): nominal 3.18 mm support hole, 1.57 mm panel, 9.53 mm spacing. Obtain the applicable dimensional/tolerance drawing for final acceptance.
- [LRS-35 datasheet](https://www.meanwell.com/Upload/PDF/LRS-35/LRS-35-SPEC.PDF) and [LRS-75 datasheet](https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF).
- [Kraus & Naimer catalogue, centre-off functions](https://flippingbook.krausnaimer.com/KN100GB/11/), [CA10 data](https://www.krausnaimer.com/fileadmin/user_upload/Kraus_u_Naimer/PDFs/ElecData/Switches/Dynamic/english/CA10_EN.pdf), and [custom configuration service](https://www.krausnaimer.com/gb_en/products/customized-switches).
- [Littelfuse 217 fuse data](https://www.littelfuse.com/assetdocs/littelfuse-fuse-217-datasheet?assetguid=af55be94-c42e-41b1-ad43-e070e09443fe).
- [Oceanflex cable supplied by 12 Volt Planet](https://www.12voltplanet.co.uk/CAB3CTNTW2.5PNT.html) and [AMC manufacturer](https://www.automarinecables.com/). Manufacturer web navigation did not provide the missing product-specific data during the review; absence from the retrieved listing is not proof that the manufacturer cannot supply it.
- Current controlling cable source: [AMC 2026 Update V.3](https://cdn.prod.website-files.com/62deaee72baf3ef3b83165ff/69fc985a23120ee62491a529_14%20-%20AMC%20Datasheet%20%20-%20Oceanflex%20Tinned%20Copper%203%20Core%20Cable%20(2026%20Update)%20V.3.pdf). [Environment/hub evidence](pcb/ENVIRONMENT_EVIDENCE.md) records visual/table review, OneGel's conflicting manufacturer data and A364/WAA364 identification; it supersedes the older distributor-only assumptions above.
- [DogWatch SmartFence owner's guide](https://www.dogwatch.com/wp-content/uploads/2026/06/SmartFence_OwnersGuide_Rev.E.1-06.26.pdf), especially installation/protector/grounding information. Obtain applicable regional instructions and approval for the actual nonstandard boundary configuration.

## Session Handoff

At the end of each implementation session, record the work-package IDs touched, changed files, exact verification commands/results, unresolved evidence, and the next bounded task. Preserve the distinction between implemented, file-verified, CAM-accepted, and physically qualified. Do not silently lower a requirement to obtain a PASS.

Entries and evidence subsections through **TE Review Corrections**, including
**PS12 Selection**, are historical records for their named snapshots.
**[Documentation Cleanup](#documentation-cleanup)** and the current
requirements/queue control this session. Earlier tests do not verify changed notes
or assumptions, and an old package's use of the same revision/filenames does
not make it current.

| Date | Session result | Next task |
| :--- | :--- | :--- |
| 2026-09-06 | Review, requirements clarification, DFM policy, and this handoff plan prepared. No PCB/schematic/build remediation implemented; P1-P6 remain unchecked. | Start P1: complete-project staging, report/gate reliability, and regression-check foundations. P2 protection analysis may proceed independently. |
| 2026-09-06 to 2026-09-07 | Implemented P1, bounded P2/P3, P4 tooling/drafts, P5 and automated P6 with focused parallel ownership. Retried interrupted electrical/layout agents, integrated their work, and corrected independent audit findings with negative/native fixtures. Final native suite: 130 PASS; `make check` PASS with exact reviewed warnings and five visible release holds. Clean serial/parallel builds both refuse publication and their checked data matches. No hardware/CAM qualification, commits, uploads or orders. | Obtain bounded P2 LED/clamp/pulse and GDT holdover/source evidence before circuit selection. In parallel obtain P3 maximum-pin/body and SMT-pattern/process acceptance. Then integrate approved protection and rerun every affected gate. |
| 2026-09-07, continuation from 97e202d | Confirmed one TEST PSU plus one disconnected spare and actual reel markings/colours; corrected OneGel and A364/WAA364 evidence. Implemented bounded P3 holes/body/courtyards, metric SMT lands and standard untented vias, preserving guardrails. Added conditional nonuniform cable/thermal analysis and precise negative protection findings. **159 tests PASS including native; final `make check` PASS; clean serial/parallel comparison PASS with publication correctly refused.** No protection circuit/BOM substitution, approval-hash refresh, supplier/hardware approval, commit, upload or order. | **P2 remains incomplete.** Resolve the specific current/clamp ordinary-duty and pulse gaps, powered fault containment, completed source interface and thermal evidence in the next bounded work below. P3's remaining work is actual lot/process/fit acceptance, not rereading supposedly inaccessible figures. |
| 2026-09-07, user simplification decision | User accepts installation-polarity LED damage and direct-strike rebuilding, but reaffirms continuous-safe normal TEST and has not waived ordinary/nearby transient damage. Narrowed C4 records and removed mandatory reversed-flying-lead immunity. Read-only agents assessed 16-part placement/folded routing and real 2 W axial/SMT resistor options; the blocked resistor agent resumed after the user resolved credits. **No PCB/schematic/BOM/library change in this step.** `TMPDIR=/tmp/opencode make test`: 159 discovered, 153 pass/six native skips; `make check` PASS with the same five holds; whitespace checks PASS. | Develop the simple candidate in ELECTRICAL section 9, not the historical 40-part circuit. Exact clamps/resistor and thermal/pulse scope remain to select. Existing geometry remains file-checked, not a fitted 16-part or thermally qualified design. |
| 2026-09-07, authorized hybrid implementation | **Committed checkpoint ad282e3 first**, covering all 36 relevant prior files, then implemented the PR02/BYG23T 16-part hybrid with focused ownership. User confirmed energized-cattle fencing is prohibited near the entire cable/stations/hub. **198 tests PASS including native, `make check` PASS, clean serial/parallel refusal/comparison PASS**. Reviewed fresh numbering/invalid-reference probes and deliberately updated only the changed schematic approval hash/rationale; no automatic refresh or hardware approval. All five holds and unresolved PR02 external allocation remain. Hybrid changes are **uncommitted**; no push/upload/order. | Qualify the implemented simple circuit and actual continuous thermal/recovery behavior, resolve PR02 allocation and order-specific fit/process/CAM. Do not restart P1, reintroduce the withdrawn cattle-fence test or require the historical 40-part circuit. |
| 2026-09-07, P2 switch evidence continuation | Worked the first unfinished package's switch item. Visually verified the full standard WAA364 contact/link graphic and recorded catalogue-only connectivity; synchronized INSTALL/ACCEPTANCE without assigning field terminals. During read-only research the prior hybrid was committed externally as **6ba2a07**; this continuation made no commit. **192 tests PASS/six native skips, library check PASS, `make check` PASS** with all existing holds. No CAD/BOM, approval-hash or hardware change. | Obtain the complete offered/supplied switch code and manufacturer drawing, plus actual-application DC/global-transfer approval before physical terminal assignment. C4/C5/W3 physical evidence, source design and existing part/process holds remain open; do not repeat the now-resolved catalogue transcription. |
| 2026-09-07, board-only finalization from aca11eb | Worked **P3 assembly/fit handoff and P4 placement evidence**, not switch/environmental research. Reconciled the stale unchecked hybrid-placement item; added conditional axial-forming/panel bounds, native pad/courtyard overlay and exact sixteen-anchor/34-terminal datums. **202 tests PASS including native, final `make check` PASS, serial/parallel refusal/comparison PASS**. Final CAD/BOM/CPL/libraries and all release/approval fields are unchanged. No commit, upload or order. | Obtain **PR02 exact sourcing and accepted 15.24-pitch forming**, then allocated-part/process and actual supplier-model/panel/CAM acceptance for five individual assembled boards. Follow the board queue below; independent hub/qualification holds remain outside this scope. |
| 2026-09-07, SMT/prototype review from 02661d8 | Corrected the wrong 4.7-kohm resistor code to explicit pending HP12 sourcing, adopted manufacturer SMT lands/body/courtyards, restored missed geometry coverage and hardened prototype/production mode handling. Synchronized current notes/model and added Gate P without closing A/B/C or the five holds. **207 tests PASS including native, `make check` PASS, real production serial/parallel refusal/comparison PASS.** `make gerbers` and real prototype workflow stop only on R1/R2 sourcing; no public package, upload, order or commit. | Resolve exact **HP122WF2201T4E** supplier mapping, then repeat real prototype publication and P3/P4 supplier model/process/panel/CAM review. No PR02 forming, switch or environmental research is needed for the prototype-file queue. |
| 2026-09-08, PS12 selection from 5d405b0 | User selected **PS122WF2201T4E / C2793873 for prototype AND production** and reports **110 ORDERED** into JLCPCB library. Verified identity and independent PS body/lands; synchronized BOM/CAD/library/model/notes with **no layout change**. **207 tests PASS including native; `make check`, `make gerbers`, real serial/parallel prototype publication/comparison PASS; production refusal/comparison PASS.** Gate P files are current; all five production holds remain. No commit, upload or agent order. | Use current prototype manifest/package for separately authorized P3/P4 supplier review: job allocation/attrition, GDT/Kefa fit/forming, models, processed stencil/CAM and panel/process acceptance. Preserve independent qualification holds without reopening their research for files. |
| 2026-09-11, initial TE 35212K2FT prototype selection | Selected **TE Connectivity 35212K2FT / C4129105** for prototypes, retaining the Yageo production pre-order after PS12 cancellation. BOM/CAD/library metadata changed with **no layout change**. **207 tests and the recorded native/publication workflows passed for that snapshot**; all five holds remained. The claimed exact TE land match and inherited TCR/overload-test conditions were subsequently found unsupported and are corrected below. No commit, upload or agent order. | Superseded by **TE Review Corrections**; preserve this snapshot's actual verification evidence, not its rejected manufacturer-equivalence claims. |
| 2026-09-11, TE review corrections | User confirmed production **Yageo SR2512FK-7W2K2L / C876850**, independently identity-checked. Corrected TE alternate-land/mounting evidence, TCR assumption provenance, unknown overload test, live guides and current-release pointers. No additional CAD/BOM/library/geometry or diagnostic-approval change. **208 tests PASS including native, `make check`/`make gerbers` PASS, real serial/parallel prototype publication and production-refusal comparisons PASS.** | Current corrected Gate P files are ready for separately authorized supplier review. Accept actual alternate-land/process, parts/allocation, GDT forming, models/panel/CAM; qualify the intended population separately. No hold closure, upload, order or commit. |
| 2026-09-11, documentation cleanup from d60c83e | Implemented the approved plan across all 17 guides/notes: canonical owners, linked summaries and preserved historical/local controls. Independent semantic/link review, **208 native-enabled tests**, `make check`/`make gerbers`, production-refusal and real serial/parallel prototype comparison **PASS**. Source/artifact/mirror hashes and isolated-package context checked; no CAD/BOM/model/rule/approval change. | Current Gate P files contain the consolidated notes. Resume the separately authorized P3/P4 supplier queue; all engineering, job-allocation and physical acceptance holds remain. No upload, order or commit. |

Plan-creation validation: `git diff --check` and `git diff --no-index --check /dev/null REMEDIATION.md` passed. These are documentation checks; the KiCad and model results above are prior review evidence, not newly performed hardware qualification.

### Implementation Evidence

Files changed in this implementation:

- P1/P4/P6: `Makefile`, `.gitignore`, `scripts/manufacturing.py`,
  `scripts/compare_nets.py`, `scripts/check_geometry.py`, `scripts/kicad_sexpr.py`,
  `scripts/verify_workflow.py`, `pcb/pcb.kicad_pro`, `pcb/pcb.kicad_dru`,
  `pcb/verification.json`, and focused tests under `tests/`.
- P2: `scripts/analyze_limits.py`, `tests/test_electrical.py`,
  `pcb/ELECTRICAL.md`; **no approved new protection circuit or BOM delta**.
- P3: PCB/schematic, reviewed BOM, native-generated CPL, local symbol/footprint
  libraries/tables, `pcb/sync_libraries.py`, and `pcb/ASSEMBLY.md`.
- P5: README, INSTALL, ORDERING, ACCEPTANCE, RISKS, MATERIALS, LED, REVIEW,
  AGENTS and this handoff. An unrelated `pcb/pcb.kicad_prl` layer-visibility
  setting changed during the session; it was left untouched.

Final reproducible commands and actual results:

| Command / review | Result and scope |
| :--- | :--- |
| `TMPDIR=/tmp/opencode make test` | PASS: 130 tests discovered, 127 run/pass and three opt-in native probes skipped. |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | PASS: **all 130**, including native DRC rule activation, unary-annular behavior, export formats and rounded-pad/margin geometry. Python 3.14.4, KiCad 9.0.7. |
| `python3 -B pcb/sync_libraries.py --check` | PASS: ten local footprints and six symbols; shared geometry and sourcing metadata match. The deliberate `--sync-metadata`, `--write` sequence was run before final checks. |
| `make check` | PASS: DRC 0, unconnected 0, parity 0; ERC 0 errors and eight exact reviewed label warnings; geometry 0 defects; eight nets / 30 terminals / 48 IPC records; 14 populated parts; 40 PTH drill hits (26 component + 14 via), four NPTH and all eight Gerber layers/ZIP payloads validated. All five engineering holds remain open. |
| `python3 -B scripts/analyze_limits.py` | PASS of declared DC study: nominal 0.847705 A / 30.5174 W, 8.0448..15.0909 mA; all 280 cuts; explicit prospective-fault/source and conditional thermal screens. Not measurement or reversal/surge qualification. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | PASS of workflow/refusal test. Executes `make clean` (0), `make all` (2), `make clean` (0), `make -j4 all` (2), separately and sequentially. Both builds complete file checks, refuse publication solely for the expected holds, and match in validated fabrication/connectivity/population. |
| Source/assembly render review | Front and underside assembly PDFs and schematic inspected under `tmp/layout-review/current/`; native fabrication geometry additionally validated. Actual processed CAM/stencil, placement and physical samples were not available. |
| Whitespace checks | `git diff --check` passed during integration; final documentation consistency is checked separately from hardware acceptance. |

Latest preserved serial/parallel evidence is
**`tmp/workflow-validation/run-w745r3h7/report.json`**, with commands, hashes,
preserved before/serial/parallel trees and exact comparison scope. Gerber/drill
comparison normalizes only bounded native creation timestamps; BOM/CPL/IPC/
positions and controlled notes compare exactly. Geometry-report path fields
and complete via-row ordering are normalized without removing measurements or
duplicates. Assembly PDFs are archived/hashed but not automatically render-diffed.
The initial workflow row-order comparison failure was corrected and its evidence
was retained, not erased or converted into a claimed PASS.

Original pre-clean build/manufacturing-run evidence remains under
`tmp/workflow-validation/run-vrr6147i/before/`; subsequent validation runs preserve
their own prior state. `tmp/dfm-review/`, `tmp/layout-review/` and other unrelated
evidence survived cleanup checks. A final `make check` refreshes `build/` reports
and the draft CPL; `build/status.json` identifies that latest attempt, not an order
release. No source Gerber mirror or public verified manifest is left current.

### Diagnostic Review

- The exact eight `single_global_label` UUID/name pairs are reviewed for this
  deliberately single-sheet circuit, which retains unprefixed net names.
  They label already wired networks, not missing inter-sheet connections.
  UUID/name/revision/sheet checks, complete terminal comparison and native
  parity remain mandatory; errors, new warnings and stale reviews still fail.
- The XML exporter returns 0 while printing
  `Warning: schematic has annotation errors, please use the schematic editor to fix them`.
  KiCad 9.0.7 `SCH_REFERENCE::Split()` treats references ending in letters as
  unannotated. The ten intentional J_/GDT_ references cause this warning, not
  their underscores. Twenty-two isolated exports and twelve ERC probes under
  `tmp/annotation-review/probe-hzgnve0_/` established the cause; both numbered
  controls remove it while preserving all 18 component contents and 30 terminal
  memberships after inverse renaming.
- Duplicate/unassigned and property/instance-mismatch probes show that the same
  aggregate warning can hide genuine annotation defects and native ERC alone
  did not detect them. Therefore **warning text alone is not an approval**.
  The one exact stdout line, empty stderr, command, exit 0 and KiCad 9.0.7 are
  reviewed only with the exact schematic/project/symbol-library/table hashes
  in `pcb/verification.json`. Any changed input requires a fresh review; hashes
  are never refreshed automatically. Unknown export diagnostics block too.
- The exact known wxWidgets duplicate-image-handler `Debug` lines from PCB
  exports are informational, retained and counted, not design warnings. Other
  stderr is not discarded. Raw native warnings and all command results remain
  available in the build/attempt logs.
- Independent review found four verifier gaps: trailing Gerber commands hidden
  in comments/attributes, shifted or malformed RoundRect apertures, unsupported
  source artwork omitted from the export model, and binary treatment of unary
  annular rules. All four were corrected and have focused negative fixtures;
  native probes establish actual rounded-aperture and unary-rule behavior.

### Continuation Evidence

The 2026-09-07 continuation started on `main` at **97e202d** with clean tracked
and staged diffs. The earlier implementation was already committed; this
continuation is **uncommitted**. Focused agents owned separate research records,
analysis/tests, or named guide files. Parent integrated the source and controlled
checks; no concurrent process owned the real workflow staging during validation.
The initial agent quota interruption was retried after the user resolved it.

Implemented scope:

- **Requirements/P5:** two ordered LRS-75-36, one TEST/one disconnected spare;
  confirmed `CM03/05.100` and `3 CORE (3 x 35/0.30) TINNED BLACK 100 MTR` labels;
  red/black/plain-green cores; exact AMC 2026 V.3; OneGel/no mixing and genuine
  manufacturer cure/temperature conflicts; provisional eight-pole A364/WAA364,
  with physical numbering and DC/global-transfer approval still open.
- **P2 analysis, not circuit completion:** `scripts/design_bounds.py`,
  `tests/test_design_bounds.py` and `pcb/DESIGN_BOUNDS.md` add the conditional
  8.21 ohm/km standard ceiling, explicit contacts/temperature, nonuniform loads,
  unenforced 35-37 V source proposal and thermal interfaces. LED/source research
  records preserve actual candidate netlists, pulse-curve rejections and the
  K.12 135 V/1300 ohm network comparison. No C4/C5 part is selected or populated.
- **P3 source:** PCB and nine of the ten existing local footprint definitions
  changed. KF128/KF129 holes are 2.00; R/AC 1.40; earth GDT 1.50 mm. D1/D2 remain
  1.10/2.20, with courtyard Y enlarged to +/-1.70 for the declared pose margin.
  All THT pad centres, protected copper/vias/mounts, connector mappings and
  footprint origins remain. SMT pads intentionally change to 5.50 x 1.20 at
  +/-2.00; stubs retain their former full-width endpoints. Standard untented
  1.80 mask openings replace unreliable tenting assumptions. The J_EARTH silk
  rear edge alone was omitted where it crossed those openings; F.Fab/courtyard
  geometry and the 1.30 tolerance-budgeted overhang remain explicit.
- **P1 maintenance/P4/P6:** existing transaction extended, not restarted.
  Source-selected component holes, actual native flat tenting behavior and
  source-matched open-via aperture inventories have negative/native regressions.
  Intentional same-net via-mask overlap never excuses component paste over a
  hole. All seven engineering notes and analysis helpers are now snapshotted;
  note release copies must match staged-source hashes and compare byte-exactly.
  The unchanged 14-part BOM/schematic identities and generated CPL still match.

| Exact command / review | Actual continuation result |
| :--- | :--- |
| `TMPDIR=/tmp/opencode make test` | PASS: **159 discovered, 153 pass, six opt-in native probes skipped**. Fixture cleanup messages concern isolated test roots, not the authoritative build. |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | PASS: **all 159**, including six native contracts. KiCad **9.0.7**; tests include the reused 280-cut sweep at an asymmetric corner, source fit/mask regressions and missing/changed controlled-note copies. |
| `python3 -B pcb/sync_libraries.py --write` then `python3 -B pcb/sync_libraries.py --check` | PASS: ten local footprints and six symbols; deliberate reviewed geometry propagated. Symbol-library content and annotation-review inputs stayed unchanged. No synchronization was used to approve a substitution. |
| `make check` | Final PASS: **0 DRC violations, 0 unconnected pads, 0 footprint/parity errors; ERC 0 errors/eight exact reviewed warnings**; geometry clean; eight nets/30 terminals/48 IPC records; 14 populated parts; **40 PTH hits (26 component +14 via), four NPTH**, all eight Gerber layers and archives validated. F.Mask/B.Mask contain 48/44 flashes respectively, including fourteen 1.80 via openings per side; F.Paste has four component apertures. Five engineering holds stay visible. |
| `python3 -B scripts/analyze_limits.py` | PASS: original nominal 0.847705 A / 30.5174 W and all 280 cuts reproduced. Fault currents remain prospective CV/conditional-arc calculations, not measured PSU behavior. |
| `python3 -B scripts/design_bounds.py` | PASS: declared hot cable/contact 40.29306 ohm/core; nonuniform A40 4.6681 mA corner at 35 V; zero-drop 37 V upper 1.400373 A and 0.631876 W/resistor. Loose comparison floor and rating-only thermal limits remain explicitly conditional, not visibility or continuous-duty approval. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | PASS: separate `make clean` (0), `make all` (2), `make clean` (0), `make -j4 all` (2). Both real builds pass file checks and refuse publication **solely for expected holds**. Validated geometry/connectivity/population and all seven note copies match; unrelated evidence preserved. This is not a successful `make all` or an order release. |
| Independent review and assembly inspection | Review found an undersized diode courtyard pose allowance and omitted new-note copies in workflow comparison; both corrected with regressions. First native integration also caught J_EARTH silk clipping after untenting; fixed geometrically, no warning suppression. Final native front assembly PDF inspected; no processed CAM/stencil or physical assembly was available. |
| Whitespace / source review | `git diff --check` and separate `git diff --no-index --check /dev/null <file>` for each of the seven new files PASS. Schematic, project/rule settings, BOM, library tables, symbol library and hash-bound annotation approval are unchanged. `verification.json` changes only W1/W4 hold reasons, not IDs or approvals. |

Preserved real workflow evidence:
**`tmp/workflow-validation/run-l2q678y3/report.json`**. Its `before/` tree retains
the initial failed silk check and subsequent successful integration runs; its
`serial/` and `parallel/` trees retain the complete compared source/export/note
snapshots. Isolated native probes remain under `tmp/native-manufacturing-tests/`.

Final report refresh: **`tmp/manufacturing/runs/attempt-p08lf2yg`**, identified by
`build/status.json` as **checked**, not published. Its `exports/Assembly.pdf`
was inspected, and its `release/ViaTreatment.csv` lists all fourteen vias with
front/back requested tenting **no/no** and standard untented/no-fill wording.
Native-generated CPL was refreshed and remained byte-identical because component
origins, rotations, values and footprint names did not change. No public
`build/manifest.json`, order ZIP or Gerber mirror is current.

**Exit remains partial:** P3 has explicit, verified file geometry, but actual
lot, forming, solder/process, stencil/CAM and enclosure acceptance are not
performed. **Gate A remains held by unfinished P2 circuit/source/thermal design;
Gate B additionally needs the real order/fit/process approvals; Gate C needs
physical and site qualification.** None of C4/C5/W3/W1/W4 is closed. No field
hardware, sustained reversal, powered-GDT recovery, potted thermal, daylight,
RF/cattle-fence or site/earthing test was performed. Do not turn the conditional
model or researched parts into an implicit approved protection BOM.

### Simplification Handoff

The latest user decision changes **required installation fault tolerance**, not
the LED's ratings or a physical test result. Main requirements, LED/installation/
risk/acceptance/audit/procurement guides, AGENTS and the C4 hold reason are
synchronized. ELECTRICAL section 9 records the actual netlist concept, read-only
placement screen, PR02/PWC2512/CRCW-HP candidate data and source URLs. The old
active investigations remain historical evidence, not mandatory prerequisites.

The proposed additional diodes are **parallel shunts at the LED outputs**, with
cathodes to LED positive and anodes to B, after the existing series diodes.
Locations near (135,99)/(135,146) appear possible within provisional envelopes;
the user's farther-right tee/fold is an alternative, not necessary for two small
shunts. Neither is laid out or checked as a new circuit. A 2 W label gives no
automatic cool-body result; actual heat-flow and closed-box duty evidence remain
mandatory. Direct/indirect lightning and ordinary/cattle/switching mechanisms
are distinguished in RISKS; no unmeasured pulse level is promoted to a requirement.

Latest report refresh is **`tmp/manufacturing/runs/attempt-599vlrbj`**, with
`build/status.json=checked`, no publication. `make check` passed the unchanged
14-part source and updated controlled-note snapshot with zero DRC/unconnected/
parity errors and eight existing reviewed ERC warnings. The prior full native
159-test and serial/parallel evidence remains historical; the six opt-in probes
and real serial/parallel workflow were **not rerun for this documentation-only
step**. No hardware/thermal/surge test, approval-hash refresh, hold closure,
commit, upload or order occurred. Preserve all earlier worktree/evidence changes.

### Hybrid Implementation

The requested checkpoint is **ad282e3**, `Checkpoint DFM remediation and
simplified protection scope`, committed before new requirements or CAD changes.
It records the previously checked 14-part geometry and the accepted installation
polarity risk. The worktree was clean immediately after that commit; subsequent
hybrid changes remain unstaged/uncommitted for review. No push was performed.

Current hardware **1.2.0-dev**:

- **R1/R2:** PR02000202201FA100, 2.2k, copper-lead 2 W/1%/250 ppm/K, at the
  same centres and 15.24 pitch. Drills/pads remain 1.40/2.40; conservative body
  box is 12.00 x 4.20, and assembly requires >=1.00 body standoff. Actual source
  properties/BOM use explicit external sourcing and no guessed LCSC code.
- **D1/D2:** BYG23T-M3/TR / C145454 SMA series replacements, unchanged centres
  (132.50,104.50)/(132.50,140.50), rotation 0, cathodes east.
- **D3/D4:** same SMA part, negative shunts at (135,99)/(135,146), rotation 180,
  cathodes west to the corresponding LED positive and anodes to B. Lands are
  2.50 x 2.00 at local +/-2.10; original manufacturer figure was visually read.
  These are not positive-voltage/current regulators or reversed-lead immunity.
- **Retained:** all six GDTs, WAGO-tap topology, board/mounts, full-width rails,
  fourteen untented 1.00/1.80 vias, solid EARTH, protected B returns and LED
  terminal mappings. No moved takeoffs, folded routing or new vias. Schematic
  has eight nets/34 terminals and 20 symbols including four mounts. BOM is
  **16 electrical parts: six SMT, ten THT**; native-generated CPL agrees.
- **Scope:** the cattle-fence prohibition covers the full 4 km cable, every
  station and the hub, not merely the transmitter. Inspection/maintenance of
  that restriction replaces qualification of the withdrawn 0.5 m / 300 m run.
  Installation-polarity LED damage/direct-strike rebuilding remain accepted;
  ordinary RF/switching/nearby-lightning and continuous-safe TEST are not waived.

Changed files include PCB/schematic/BOM/CPL, the new SMA and PR02 local
footprints, sourced-property synchronization, geometry and manufacturing
validators/tests, the two analysis helpers/tests and all affected guides/notes.
Retired onsemi/MBE footprint definitions were removed; the six generic local
symbols and library-table/project/rule files are unchanged. Other retained
footprints gained sourcing metadata only, not geometry changes. New
`scripts/review_annotation.py` and its tests collect private evidence and never
modify approvals. External sourcing validation is a bounded extension for this
actual part, not an export bypass: missing/mismatched identity/reference fails,
and unresolved external allocation blocks publication even with holds closed.

| Command / review | Actual result |
| :--- | :--- |
| `TMPDIR=/tmp/opencode make test` | PASS: **198 discovered, 192 run/pass, six opt-in native probes skipped**. |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | PASS: **all 198**, Python 3.14.4 / KiCad 9.0.7. Includes exact SMA polarity/type/land/aperture and retired-THT regressions, PR02/TCR/leakage/current cases, external-sourcing/parity/publication controls and annotation helpers. |
| `python3 -B pcb/sync_libraries.py --sync-metadata`, `--write`, `--check` | PASS: reviewed metadata propagated, ten local footprints/six symbols verified. Deliberate source geometry changes preceded generation; no approval hashes were synchronized. |
| `python3 -B scripts/analyze_limits.py` and `python3 -B scripts/design_bounds.py` | PASS of declared studies: 280 nominal cuts with conditional shunt-diversion margin, 615 fault cases in the suite and the reused asymmetric cut sweep. Nominal comparison remains 0.847705 A / 0.501018 W per resistor. PR02 upper screen is **1.561876 A / 63.0935 W total and 0.769433 W/resistor**; after-diversion nonuniform A40 corner is **4.090396 mA**, not measured or guaranteed daylight current. |
| `python3 -B scripts/review_annotation.py --cli /snap/bin/kicad.kicad-cli` | PASS of evidence collection, **not automatic approval**: baseline 20 components/16 populated/four mounts/eight nets/34 terminals; numbering only the ten J_/GDT_ refs removes the warning with complete inverse-renamed component/net equivalence. Duplicate, unassigned and property/instance mismatch probes are structurally rejected despite the same native warning. Sources unchanged during collection. |
| Manual annotation review | Inspected **`tmp/annotation-review/hybrid-10dti06b/report.json`**, command logs and baseline/numbered comparisons. Accepted only the same exact KiCad 9.0.7 XML warning/exit/stdout/stderr contract. Deliberately changed **only the schematic hash** in that review, to `63f5e08d4fe6cc145d442fbf6364d7c79a9f455a8f93c960322c8b1c4a9ebfdb`, and its rationale. Other four approval hashes and the eight-label review remain unchanged; engineering holds are not approvals. |
| `make check` | Final PASS: **DRC 0, unconnected 0, footprint/parity 0; ERC 0 errors/eight exact reviewed warnings**. Eight nets/34 terminals/**52 IPC records**, 16-part BOM/CPL, **36 PTH hits (22 component +14 via), four NPTH**, all eight Gerber layers and archive payloads validated. F.Mask/B.Mask flashes **52/40**, top paste **12**, no via paste. External R1/R2 are explicitly reported pending, not allocated. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | PASS of preservation/comparison/refusal: separate clean (0), serial `make all` (2), clean (0), parallel `make -j4 all` (2). Both builds passed file checks and refused publication solely for the expected holds; validated geometry, population, connectivity and all seven controlled-note copies match. No successful package build or order is claimed. |
| Independent review / rendering / whitespace | Independent code/electrical/geometry review found no additional actionable defects. A separate documentation pass corrected remaining retired-part/cattle-exposure clauses. Native first integration caught D4 silk overlap and stale annotation approval; D4's reference moved to Y=149, without rule suppression. Schematic and final front assembly PDFs inspected. Tracked diff and all four new-file whitespace checks PASS. |

Preserved workflow evidence is
**`tmp/workflow-validation/run-bdauix0k/report.json`**, including the `before/`
tree with the initial hybrid failure and earlier checked reports. Earlier
annotation probes remain alongside the reviewed run; none were cleaned away.
Latest report refresh is **`tmp/manufacturing/runs/attempt-j4_8iteb`**,
`build/status.json=checked`, with its inspected `exports/Assembly.pdf`.
The schematic render is **`tmp/layout-review/hybrid-schematic.pdf`**.
No current public manifest, Gerber mirror or order ZIP is published.

**Still held:** C4 actual clamp/RF/transient performance; C5 powered-GDT recovery
and source/fault containment; W3 measured closed-OneGel continuous duty and real
source envelope; W1/W4 actual part/process/stencil/CAM/forming/fit acceptance.
PR02 external allocation is independently unresolved. No assembled prototype,
thermal/recovery/surge/visibility/site test or supplier acceptance was performed.
The 2 W part improves catalogue margin, not proof of cool operation. This
implements the requested starting point, not a field or prototype-order release.

### P2 Switch Evidence

The 2026-09-07 continuation began with the prior hybrid changes present and
unstaged. While read-only research proceeded, **6ba2a07** appeared and the
worktree became clean. That commit was made outside this continuation's actions;
the four documentation edits below are relative to it. Historical uncommitted
descriptions above refer to their original sessions, not the current checkpoint.

**P2 is still partial.** Its first unchecked switch item was advanced with new
source evidence, not a guessed physical pinout or an unrelated verification
rewrite. `pcb/ENVIRONMENT_EVIDENCE.md` now transcribes all eight fixed common
links and both sets of switched contacts from the original **2025 catalogue,
page 23** graphic. Parent and independent reviewer visually checked every row.
All 16 contacts are open at catalogue `0`, but the eight separate common links
remain; they must not be mistaken for a shared bus. The source's `1`/`2` detents
and pole rows have **no assigned DogFence roles**.

The CA10 **v4.2 / 2026-08-15** sheet still limits its DC-capacity statement to
ON/OFF functions; neither that table nor the static cam graphic supplies loaded
global-transfer approval. The newly recorded **0.60 Nm** screw datum and
factory-link instructions are manufacturer evidence, not a passed assembly
inspection. K&N's custom-function form likewise distinguishes a customer request
from the manufacturer's effective cam drawing. No manufacturer was contacted
and no order-specific response or physical measurement was available.

Changed files: **`pcb/ENVIRONMENT_EVIDENCE.md`, `INSTALL.md`, `ACCEPTANCE.md` and
`REMEDIATION.md` only**. The 41-station/same-end/continuous-safe TEST requirement,
16-part circuit, physical guardrails, procurement history and release holds are
unchanged. No new analysis code or speculative measurement tool was needed to
record the recovered diagram.

| Command / review | Actual continuation result |
| :--- | :--- |
| `TMPDIR=/tmp/opencode make test` | PASS: **198 discovered, 192 pass, six opt-in native probes skipped**. Includes the existing nominal/asymmetric 280-cut regressions, repair/retest and legacy negative controls; no physical hub test. The cleanup message concerns isolated fixtures, not the authoritative build or unrelated evidence. |
| `python3 -B pcb/sync_libraries.py --check` | PASS: ten footprints and six symbols; no source/library edits or fit approval. |
| `make check` | Final PASS, **KiCad 9.0.7**: zero DRC violations; ERC has only the eight existing reviewed warnings; geometry, eight nets/34 terminals/52 IPC records, 16-part population, 36 PTH/four NPTH hits, eight Gerber layers and archives verified. C4/C5/W3/W1/W4 and external PR02 allocation remain held; no publication. Rerun after the documentation-review correction so the controlled-note snapshot is current. |
| Independent source/document review | All eight schedule rows, source restrictions, links and preserved scope verified. Corrected a truncated detent clarification; no substantive wiring/scope finding. No supplied-switch or dynamic DC evidence inferred. |
| Diff/status review and `git diff --check` | PASS: only the four intended documents changed; PCB/schematic/project/rules/BOM/CPL/libraries, scripts/tests and `pcb/verification.json` unchanged. Generated CPL remains byte-identical. |

Final evidence is **`tmp/manufacturing/runs/attempt-byopgqv8`**, with
`build/status.json=checked` and `build/reports/verification.json`. Its
`previous-build/` retains the preceding check's reports; earlier workflow and
annotation evidence was not cleaned. The final controlled environment note has
SHA-256 **`416b123866aa98b911fcbf7045d253e4445f09551cce21fdf54d80f64cb288c2`**
in the verification record. No current public manifest, order ZIP or Gerber
mirror is published. The full opt-in native suite, clean serial/parallel
workflow and annotation probes were **not rerun for this documentation-only
change**; their earlier results remain historical.

**Blocking inputs:** the complete offered/supplied switch article and link/cam
drawing, application-specific DC/global-transfer acceptance over the real
source/fault envelope, then physical wiring and full-hub tests. The separate
C4/C5/W3 hardware captures and accepted source/thermal limits are also absent;
no numerical model or public catalogue can substitute for them. C3 and all
engineering/release holds remain open. No order, upload, commit, approval-hash
refresh or physical qualification occurred in this continuation.

### Board Finalization

Started with clean tracked/staged diffs on **aca11eb**. The first unfinished
board-focused package was P3's actual assembly/fit handoff, followed by P4's
placement review. A bounded source audit found no demonstrated layout defect
requiring another circuit, relocated part or changed guardrail. The stale
"place/route selected protection" checkbox now acknowledges the already
implemented and rechecked 16-part hybrid, not new placement work.

Changed files: `pcb/ASSEMBLY.md`, `ORDERING.md`, `AGENTS.md`, this plan,
`scripts/manufacturing.py`, `scripts/verify_workflow.py`,
`tests/test_geometry.py`, `tests/test_manufacturing.py`, `tests/test_workflow.py`.

- PR02/GDT drawing-space ceilings and J_EARTH's full panel-coordinate envelope
  are explicit and checked against the source. **1.62 nominal / 1.47 budgeted
  PR02 room per end** does not approve a bend; supplier radius/setback, upper
  height and protrusion are still needed. Vishay 28729 p2/p3 wire/packaging
  tables were visually rechecked, not the outline pages or an allocated lot.
- Native Assembly.pdf adds **pad outlines and courtyards**. The CLI's help
  claimed pad numbers, but the actual PDF did not render them even in a
  saved-plot-toggle trial. Those ineffective source toggles were removed.
  Generated Assembly.txt instead states **all sixteen exact-part/footprint
  anchors and 34 pin-number/net datums**, in both coordinate conventions.
- The source-derived datum text is reconstructed during workflow validation;
  changed terminal Y is a negative fixture. Actual unusual LED/diode/overpass
  mappings and geometry budgets have regression checks. No supplier centroid
  correction, lot acceptance or new publication path was introduced.
- Independent review corrected a duplicated board task under the out-of-scope
  list and aligned the existing native PDF probe with the production arguments.
  No arithmetic/coordinate defect was found. Final render inspection confirms
  pad/courtyard outlines and the exposed east overhang, not supplier approval.

| Command / evidence | Actual result |
| :--- | :--- |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | **202 PASS, no skips**, including the six native contracts and existing settled-topology regressions. |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -p test_manufacturing.py -k native_export_formats_and_failure_reports -v` | **1 PASS**, rerun after aligning the native PDF probe with the new pad/courtyard arguments. |
| `python3 -B pcb/sync_libraries.py --check` | **PASS**, ten footprints/six symbols, unchanged. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | **PASS**. Separate clean (0), serial `make all` (2), clean (0), parallel `make -j4 all` (2); checked geometry, population, connectivity, assembly datums and notes match. Both builds correctly refuse publication; unrelated evidence preserved. |
| Final `make check` | **PASS, KiCad 9.0.7**: DRC/unconnected/parity 0; ERC 0 errors/eight existing reviewed warnings; geometry clean; eight nets/34 terminals/52 IPC records; 16 populated parts; 36 PTH (22 component +14 via), four NPTH; eight Gerber layers, twelve paste apertures and archives checked. |
| Final source/artifact review | CAD, schematic, rules, BOM, regenerated CPL, libraries and `pcb/verification.json` have **no diff**. Existing approval hashes and all five holds remain unchanged. Final native Assembly.pdf and terminal/polarity datums inspected; `git diff --check` PASS. |

Preserved workflow evidence: **`tmp/workflow-validation/run-xrxhsuyd/report.json`**.
Its `before/` tree retains the initial checks and ineffective plot-toggle trial;
serial/parallel source and artifact snapshots are preserved separately.
Final current check: **`tmp/manufacturing/runs/attempt-r40jqkoe`**,
`build/status.json=checked`, with the reviewed `exports/Assembly.pdf` and
`release/Assembly.txt`. The final assembly-note SHA-256 in the verification
record is **`87e5c11c994d643a84c5d633004ec87ed11529099f005140444fa005e2263f9c`**.

**Exit: board-side handoff improved and file-verified; P3/P4 supplier acceptance
still partial.** PR02 sourcing/forming is the first concrete response needed.
Allocated-lot fit, GDT/Kefa variants/forming, SMT/THT process, placement-model,
panel and CAM acceptance are still absent. C4/C5/W3/W1/W4 remain held; no public
manifest/package, order, upload, commit or hardware qualification is claimed.
No switch/environmental research or additional protection circuit was undertaken.

### SMT Prototype Review

Reviewed **02661d8** from a clean worktree for the user's authorized SMT and
prototype-file scope. Changes remain uncommitted. The straight cathode links,
one-way circuit, full rails, fourteen vias, EARTH, mounts and distinct LED
terminal mappings are retained; no demonstrated placement conflict required
moving them or adding a circuit.

Findings and corrections:

- **Wrong resistor identity:** C2791283 actually selects HP122WJ0472T4E,
  4.7 kohm/5%, not HP122WF2201T4E, 2.2 kohm/1%. Removed it from BOM, schematic,
  PCB and generated local definition. Exact NAC Semi listing supports the
  intended identity, but its retrieved MOQ is 3,600 and no JLCPCB code/allocation
  was established. External/pending is truthful, not a sourcing solution.
- **Manufacturer lands/envelopes:** original HP12 V.7 figures support
  1.35 x 3.70 rectangles at +/-3.125, maximum-body 6.45 x 3.40 and courtyard
  8.10 x 4.20. Corrected the unreviewed generic roundrect pattern and shortened
  only the four resistor connection endpoints to the new pad centres. Removed
  the retired PR02 library definition; the ten used footprints remain local.
- **Regression coverage:** require HP12 orientation, exact undrilled copper and
  effective mask/paste shapes, full body/courtyard envelopes and straight
  1.80-mm cathode links. R1/R2 are explicitly included in the courtyard test;
  removal from the THT hole list had made the committed resistor branch unreachable.
- **Prototype scope:** production aliases now win mixed goals; external sourcing
  blocks both publishing modes. Generated README notices travel inside Gerber
  and FlyTest ZIPs. Manifests require the exact mode/status pair, and the real
  workflow checker supports an explicit prototype-publication path. No ledger
  hold or diagnostic check is approved away.
- **Documentation/model:** synchronized current assembly/order/operating notes
  and procurement history. HP12 uses 100 ppm/C at 25 C, without PR02 thermal or
  axial mounting assumptions. Nominal loss remains 0.501018 W/resistor; the
  updated conditional upper screen is 0.756803 W, not measured cooling. No
  switch/environment research or new protection circuit was undertaken.

Verification already performed during integration:

| Command / review | Actual result and scope |
| :--- | :--- |
| `TMPDIR=/tmp/opencode make test` | **207 discovered, 201 PASS, six opt-in native skips.** Includes prototype publication/hold/sourcing/manifest/ZIP/quarantine fixtures and mixed-goal tests. A preliminary new drill-mutation assertion expected the wrong diagnostic; the parser already rejected it, and the assertion was corrected to require `INVALID_STRUCTURE`. |
| `python3 -B pcb/sync_libraries.py --sync-metadata`, then `--write` and `--check` | **PASS**: reviewed pending sourcing propagated; ten local footprints and six symbols agree. No values/nets or approval hashes were synchronized. |
| `python3 -B scripts/review_annotation.py --cli /snap/bin/kicad.kicad-cli` | **PASS, evidence only**, under `tmp/annotation-review/hybrid-64xarlnh/`. Baseline 20 components/16 populated/four mounts/eight nets/34 terminals; numbering the ten J_/GDT_ refs removes the exact warning. Duplicate/unassigned/property-instance mismatch probes remain rejected. |
| Manual diagnostic review | Inspected report/command logs and byte-compared baseline/inverse-numbered `comparison.json` files with `git diff --no-index` (no differences). Deliberately accepted only the changed schematic hash **`e03c0c8df5e148db9ce868eb5da40800a557c386d29bfc9803020ae97c7f83fd`** and rationale. Other four hash approvals and the eight-label review are unchanged; all five engineering holds remain. |
| Independent integration review | **No additional actionable finding.** Rechecked source/library/metadata, land/net/link guards, mode/hold/freshness behavior and operative assembly/order instructions. Exact HP12 sourcing remains the independent package blocker. |

| Integrated command / review | Actual result and scope |
| :--- | :--- |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | **207 PASS, no skips**, Python 3.14.4 / KiCad 9.0.7. Six isolated native contracts include current-source fabrication inventory. Both 280-cut sweeps and 615 prospective inter-core cases remain model checks, not field tests. |
| `make check` | **PASS**: DRC 0, unconnected 0, footprint/parity 0; ERC 0 errors/eight existing reviewed warnings. Eight nets/34 terminals/52 IPC records, 16 populated parts, **32 PTH (18 component +14 via), four NPTH**, all eight Gerber layers and exact archives verified; F.Mask/B.Mask/F.Paste **52/36/16**. Sourcing remains pending and five engineering holds remain visible. |
| `python3 -B scripts/analyze_limits.py` and `python3 -B scripts/design_bounds.py` | Both **exit 0**. Nominal comparison remains 0.847705 A and 0.501018 W/resistor; selected HP12 upper screen 18.734624 mA / 0.756803 W per resistor and 1.536239 A total. Nonuniform A40 after-diversion example 4.227619 mA. Conditional calculations, not source/temperature/visibility approval. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | **PASS of production refusal/comparison**, not publication. Separate clean (0), `make all` (2), clean (0), `make -j4 all` (2). Both pass file checks and retain the same five holds; normalized fabrication geometry, connectivity, population, assembly datums and all controlled notes match; unrelated evidence is unchanged. |
| `make gerbers` | **Exit 2: prototype sourcing refusal**, after complete native/file checks. `mode=prototype`, `status=failed`; sole error is unresolved External R1/R2. C4/C5/W3/W1/W4 are deferred, not the cause of this refusal. No public manifest/ZIP is issued. |
| `python3 -B scripts/verify_workflow.py --target prototype --expect-holds C4 C5 W3 W1 W4` | **Exit 1 / workflow FAILED**, correctly refusing to treat failed publication as a PASS. Clean exits 0, serial `make prototype` exits 2 solely for R1/R2 sourcing; validation reports unexpected publication outcome and stops before the parallel phase. Repeat after sourcing is resolved. |
| Native assembly / source review | Corrected front Assembly.pdf inspected with HP12 lands, body/courtyard outlines, diode polarity and J_EARTH overhang. Assembly.txt confirms **16 anchors/34 pin/net datums** and no resistor holes; ViaTreatment.csv retains all fourteen 1.00/1.80 untented/no-fill vias. Native-generated `pcb/CPL.csv` is byte-identical to 02661d8 because footprint origins/angles did not change in this correction. |

Preserved production evidence:
**`tmp/workflow-validation/run-kcl5ptwm/report.json`**. Its `before/` tree retains
the first integrated `attempt-qn_3qqsm` check and inspected assembly PDF, including
the older publication quarantined at the start of this review. Source hashes
are **PCB `44e7fd57979a0baa8286ce3df1353a0ed78ab7d0268892681bd7b3413c0cc885`**
and schematic **`e03c0c8df5e148db9ce868eb5da40800a557c386d29bfc9803020ae97c7f83fd`**.

Preserved prototype attempt:
**`tmp/workflow-validation/run-dasnaiw5/report.json`**. Its `before/` tree
retains `make gerbers` attempt **`attempt-v99_3t57`** and its private
mode-marked README/ZIPs. The serial `make prototype` sourcing refusal is saved
separately as **`attempt-tdb514qz`**. These private files are not a current public
package or upload authorization. No physical qualification, supplier acceptance,
order or commit is claimed; sourcing remains the next bounded board task.

Final report refresh: `make check` **PASS** at
**`tmp/manufacturing/runs/attempt-_7xhejig`**, with `build/status.json` reporting
**`status=checked`, `mode=check`**. `build/` contains only current reports/status;
no public manifest, order ZIP or Gerber mirror remains. Final library and
`git diff --check` checks pass; all changes are uncommitted.

### PS12 Selection

**Historical snapshot, superseded by TE prototype selection and the corrected
TE/Yageo split below.** Its publication results and 110-piece order record are
preserved; the later cancellation/refund means those parts are not inventory.

The **2026-09-08** update started clean on **5d405b0**, which contains the prior
HP12 review. The user selects **Uni-Royal PS122WF2201T4E / C2793873** for both
R1/R2 in **prototype and production under one BOM**, and reports **110 ORDERED
into their JLCPCB parts library**. MATERIALS records that order separately from
receipt, inspection and actual PCBA-job allocation; whole-BOM
`allocation_verified` remains false. HP122WF2201T4E's old External sourcing is
superseded, not ordered; C2791283 remains rejected 4.7-kohm/5% history.

- JLCPCB and LCSC independently identify the selected **2.2 kohm / 2 W / 1% /
  +/-100 ppm/C / 2512** part. BOM and CAD now use manufacturer **Uni-Royal**,
  MPN **PS122WF2201T4E**, **C2793873**, **Sourcing=LCSC** and an empty sourcing
  reference. Exact identity resolves the previous External blocker; no Makefile,
  manufacturing or workflow gate relaxation is needed.
- The original **PS SMD-SP-007 V.7, 08-Jan-2026** outline and land leaders were
  independently visually read. **1.35 x 3.70 rectangular lands at +/-3.125**,
  maximum body **6.45 x 3.40 x 0.65 high** and **8.10 x 4.20 courtyard** match
  the existing source. All placements, routing, pads, apertures, drills and
  protected geometry remain unchanged; CAD/library edits are metadata only.
- The selected-part model keeps **100 ppm/C at 25 C**, TCR endpoints -55/+125 C
  and **2 W at 70 C ambient**, derating to zero at 155 C. Normal numerical
  screens remain **0.501018 W nominal / 0.756803 W upper per resistor**.
  PS's **500 V working / 1000 V overload family ceilings** still yield only
  **66.33 V rated working / 165.83 V for the specified 5 s overload** at 2.2k/2W.
  PS page 6 supplies one-pulse power and voltage curves, not repetitive-pulse
  or board/lightning qualification. HP's missing-curve and 75/100 ppm discrepancy
  findings remain historical, not PS facts.
- Synchronized assembly, electrical/model, procurement, operation, ordering and
  agent guidance. Older protection/environment research is explicitly labelled
  as superseded resistor context, without restarting it. All five production
  holds and original A/B/C remain open; physical fit/CAM/process/job-allocation
  tasks remain separate from Gate P files.

| Verification / review | Actual result |
| :--- | :--- |
| `python3 -B pcb/sync_libraries.py --sync-metadata`, then `--write` and `--check` | **PASS**: reviewed identity propagated; ten footprints and six symbols agree. Only R1/R2 metadata changes; no values, geometry or approval hashes synchronized. |
| `python3 -B scripts/review_annotation.py --cli /snap/bin/kicad.kicad-cli` | **PASS of evidence collection**, `tmp/annotation-review/hybrid-j8a0a85i/`. Baseline and inverse-numbered comparisons are byte-identical; ten J_/GDT_ renames remove the exact warning, while duplicate/unassigned/property-instance mismatch probes remain rejected. |
| Manual diagnostic review | Read report and complete command logs, byte-compared both `comparison.json` files, and checked current source hashes. Deliberately accepted only changed schematic hash **`632e440e8ec321428eaf0521bed7bd2e04f64335e29f9a864a636e872a880cef`** plus rationale; other four hash approvals and eight-label review unchanged. No production hold or allocation approval follows. |

| Integrated verification | Actual result |
| :--- | :--- |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | **207 PASS, no skips**, Python 3.14.4 / KiCad 9.0.7. Includes six isolated native contracts, selected PS identity/ratings, exact BOM/CAD/CPL population and geometry/aperture negatives, production/prototype gating and both 280-cut model sweeps. |
| `make check` | **PASS**, `attempt-zlkzjgnb`: DRC 0, unconnected 0, footprint/parity 0; ERC 0 errors/eight exact reviewed warnings. Eight nets/34 terminals/52 IPC records; 16 parts, **32 PTH (18 component +14 via), four NPTH**; F.Mask/B.Mask/F.Paste **52/36/16**; native artifacts and exact archives validated. `pending_external={}`, `allocation_verified=false`; no publication from this target. |
| `make gerbers` | **Exit 0, real prototype publication**, `attempt-nwsg7k7m`. Complete file/sourcing checks pass without a gate change; mode/status both `prototype`, all five holds recorded as deferred. Source BOM and published BOM identify PS122WF2201T4E / C2793873 for both resistors. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | **PASS of production refusal/comparison**. Clean (0), serial `make all` (2), clean (0), `make -j4 all` (2): both pass file checks and refuse publication for the same five holds; validated fabrication, connectivity, population and controlled notes agree. No successful production build is claimed. |
| `python3 -B scripts/verify_workflow.py --target prototype --expect-holds C4 C5 W3 W1 W4` | **PASS of real serial/parallel prototype publication/comparison**. Both clean commands and both builds exit 0; actual mode/status, source/artifact hashes, ZIP members/payloads/notices, BOM/CPL, assembly datums and controlled notes validate. Unrelated evidence preserved. This is new PS12 publication evidence, not the historical HP12 refusal. |
| Model and independent review | Focused electrical/design-bound suites (**23 +13 PASS**) and both plain/JSON analysis CLIs pass with unchanged normal numerical screens. Independent source/model/document review found **no actionable issue**; CAD/library changes are metadata-only. Existing topology, rules and all five holds remain. |
| Artifact/render review | Current native Assembly.pdf inspected; Assembly.txt has all 16 anchors and 34 pin/net datums, with PS12 identities and unchanged coordinates. Gerber/CPL mirrors match their published hashes. `pcb/CPL.csv` remains byte-identical to 5d405b0; no generated file was hand-edited. |

Preserved production workflow:
**`tmp/workflow-validation/run-00vsaeo9/report.json`**. Its `before/` tree retains
the initial PS12 check and successful direct `make gerbers` publication, including
the prior HP12 evidence quarantined by the normal transaction.
Preserved prototype workflow:
**`tmp/workflow-validation/run-_tcteri8/report.json`**, including separate
serial/parallel source, report and published-package snapshots.

**Then-published package (historical):** `build/manifest.json` and `build/status.json` identified
**`status=prototype`, `mode=prototype`**, attempt **`attempt-eotyxtlu`**, hardware
**1.2.0-dev**, base commit **5d405b0**, with `worktree_dirty=true`. That snapshot's source
hashes are PCB **`71831aa537a8c14d5f91907ad923e15bf79c722bf9a34d6879c389107704b3ed`**
and schematic **`632e440e8ec321428eaf0521bed7bd2e04f64335e29f9a864a636e872a880cef`**.
Gerber ZIP/mirror SHA-256 is
**`65e79e2c753290cd8a84868ddcca305d52c5fea14f4d87fda47b683909b43921`**;
manifest SHA-256 is
**`e2766237a9f60c8c25ddf250eba8752b0873adcf999d52ff6b13117fc2be61e4`**.

`build/Gerbers.zip` (mirror `pcb/Gerbers.zip`), `build/BOM.csv`, `build/CPL.csv`,
`build/pcb.d356`, `build/FlyTest.zip`, assembly outputs, README notices, all seven
controlled notes and reports are present. Keep the matching manifest with this
**FILE-VERIFIED PROTOTYPE ONLY** package. Gate P is met; A/B/C, the five ledger
holds and order-specific supplier/lot/job-allocation/physical acceptance remain
open. No file, diagnostic or sourcing gate was weakened. This update makes no
commit, push, upload or additional order.

### TE Connectivity 35212K2FT Prototype Selection

**Initial TE snapshot, now superseded by [TE Review Corrections](#te-review-corrections).**
The native/package evidence below remains valid for its recorded source hashes,
not for subsequently corrected manufacturer claims or changed controlled notes.

The initial **2026-09-11** update handled JLCPCB's cancellation/refund of the prior Uni-Royal PS122WF2201T4E / C2793873 order. The user retained the **Yageo SR2512FK-7W2K2L** production pre-order (20-day wait, now confirmed as **C876850**) and selected **TE Connectivity 35212K2FT / C4129105** for prototype fabrication under Gate P.

- The initial manufacturer-exact drop-in claim was rejected during review. TE's
  maximum body **6.45 x 3.40 x 0.65 mm** fits the retained envelope, but its
  recommended lands differ from the unchanged HP/PS-derived alternative. The
  single terminal-band and guaranteed-fillet descriptions were also corrected;
  use current ASSEMBLY/DFM_EVIDENCE, not this initial assessment, for dimensions.
- The initial TE overload-test and TCR-reference attribution was unsupported.
  **66.33 V catalogue working** and **250/500 V family ceilings** remain valid
  component arithmetic/data. The **0.501018 W nominal / 0.756803 W upper** normal
  screens remain conditional calculations; the later correction distinguishes
  engineering temperature assumptions and unknown TE test conditions.
- Updated BOM, CAD metadata (`pcb.kicad_pcb`, `pcb.kicad_sch`, local footprint `R_2512_6332Metric.kicad_mod`), scripts, tests, and documentation across the entire repository.
- Reviewed netlist annotation diagnostics via `review_annotation.py`; verified byte-identical comparisons and updated `pcb/verification.json` with new schematic hash `01329ea3bf88981f3df2f7ba202226f94947c2a3b8ff6c80a75d3c1ecd87e77a`.

| Verification / review | Actual result |
| :--- | :--- |
| `python3 -B pcb/sync_libraries.py --check` | **PASS**: ten local footprints and six symbols agree; no drift. |
| `python3 -B scripts/review_annotation.py --cli /snap/bin/kicad.kicad-cli` | **PASS of evidence collection**, `tmp/annotation-review/hybrid-zr6pvihg/report.json`. |
| Manual diagnostic review | Accepted schematic hash `01329ea3bf88981f3df2f7ba202226f94947c2a3b8ff6c80a75d3c1ecd87e77a`; all four other input hashes and eight-label review unchanged. |

| Integrated verification | Actual result |
| :--- | :--- |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | **207 PASS, no skips**, Python 3.14.4 / KiCad 9.0.7. |
| `python3 -B scripts/analyze_limits.py && python3 -B scripts/design_bounds.py` | **PASS**: 0.501018 W nominal / 0.756803 W upper per resistor screens confirmed. |
| `make check` | **PASS**, `attempt-i2kehgcu`: DRC 0, unconnected 0, footprint/parity 0; ERC 0 errors / 8 reviewed warnings. Eight nets, 34 terminals, 52 IPC records, 16 parts, 32 PTH (18 component + 14 via), 4 NPTH, F.Mask/B.Mask/F.Paste 52/36/16. `allocation_verified=false`; no publication. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | **PASS of expected publication refusal**, `tmp/workflow-validation/run-iolhmkqe/report.json`. Clean, serial `make all` (exit 2), clean, parallel `make -j4 all` (exit 2); all 5 holds refuse publication. |
| `python3 -B scripts/verify_workflow.py --target prototype --expect-holds C4 C5 W3 W1 W4` | **PASS of serial/parallel prototype publication**, `tmp/workflow-validation/run-ounph_j6/report.json`. Both clean and both prototype builds exit 0 with matching validated geometry, connectivity, population and manifests. |
| `make prototype` | **Exit 0, real prototype publication**, `attempt-qg3u34m7`. Mode/status both `prototype`, all five holds deferred. |

Preserved prototype workflow: **`tmp/workflow-validation/run-ounph_j6/report.json`**.
Preserved production refusal workflow: **`tmp/workflow-validation/run-iolhmkqe/report.json`**.

**Then-published package (historical):** `build/manifest.json` and `build/status.json` identified **`status=prototype`, `mode=prototype`**, attempt **`attempt-qg3u34m7`**, hardware **1.2.0-dev**, base commit **399c588**, with `worktree_dirty=true`. That snapshot's source hashes were PCB **`da897569fe74102178f1bf5c51d4b7c27f283395c6c3026fd016a22f3eb2c1ff`** and schematic **`01329ea3bf88981f3df2f7ba202226f94947c2a3b8ff6c80a75d3c1ecd87e77a`**.
Gerber ZIP/mirror SHA-256 is **`28422059378843896e07faf594ac297b1c610fac3b736dd469839806cc47ddc9`**; manifest SHA-256 is **`38ba2f0d5afe1698519a9aba17e4aa06bd6ac5870a2d0c0a10de754baa0c9c65`**.

That publication contained the prototype ZIPs, BOM/CPL, IPC, assembly outputs,
notices, controlled notes and reports. Its Gate P result applied only to that
snapshot. It is not the current corrected package; A/B/C and all five holds
remained open. No file/diagnostic/sourcing gate was weakened and no commit,
push, upload or additional order was made.

### TE Review Corrections

**Historical corrected-TE snapshot.** Its evidence and source hashes remain
preserved below; changed-note verification belongs to
[Documentation Cleanup](#documentation-cleanup).

The **2026-09-11** review correction implements the user's requested findings
without changing the prototype BOM, CAD, libraries, placement, routing or circuit.
It preserves all pre-existing uncommitted work on **399c588**; no commit, push,
upload or order is authorized or performed.

- **Production identity:** the user confirms **Yageo SR2512FK-7W2K2L / C876850**
  is ordered with a 20-day wait. Direct [JLCPCB identity verification](https://jlcpcb.com/partdetail/C876850)
  agrees on manufacturer, MPN, code, 2.2 kohm / 2 W / 1% / 100 ppm/C / 2512.
  The earlier unverified code is corrected history in MATERIALS, not an ordered
  alternate. Identity/order status is not receipt, inspection or job allocation.
- **Mounting evidence:** TE **9-1773463-5 Rev G, 02/2025**, pages 1-5, supersedes
  the unretained March 2023 citation. Its body envelope fits, but **1.50 x 3.00
  recommended lands, 5.00 inner gap / 6.50 pitch** are not the retained
  **1.35 x 3.70, 4.90 gap / 6.25 pitch** project alternative. Actual alternative
  placement/stencil/solder approval remains W4. Distinct terminal bands and
  conditional toe/heel/side extensions are corrected in DFM_EVIDENCE.
- **Model provenance:** +/-100 ppm/C at 2.2 kohm is TE data; **25 C reference,
  -30..125 C study and -55..125 C supported inputs** are engineering assumptions,
  not verified TE TCR test endpoints. Numeric manufacturer TCR test conditions
  and the unsupported PS12-derived overload voltage/duration are now `null` in
  the report. The normal **0.501018 / 0.756803 W per resistor** screens are unchanged.
  One new regression prevents promoting the unknown test conditions to facts.
- **Rating transfer:** TE's page 3 reference PCB has **four layers, 2 oz outer /
  4 oz inner copper**, unlike this two-layer board. Catalogue rating/derating
  transfer is explicitly unverified, not a demonstrated two-layer failure.
  TE **250/500/500 V** family ceilings and **66.33 V catalogue working** do not
  establish a five-second pulse rating or a board operating limit.
- **Live records:** electrical/risk/qualification/ordering/agent instructions
  now distinguish TE prototypes from ordered Yageo production and retired PS12.
  Yageo needs separate part/model/process/thermal review and a deliberate
  source/BOM/library update before production; TE tests do not qualify it.
  Current release pointers lead here; historical package evidence is preserved.
- **Release ledger:** C4/C5/W3/W1/W4 remain open; W3/W4 reasons describe the
  actual mounting/evidence limitations. No diagnostic approval or its five
  input hashes was refreshed; those reviewed CAD/library inputs are unchanged.

Changed scope: the two analysis helpers, two focused test files, geometry-checker
diagnostic wording, seven controlled engineering notes, nine main guides, this
handoff and W3/W4 ledger reasons. Independent integration review found the
remaining live PS12 geometry diagnostics; their wording is corrected without
changing validation behavior or dimensions. No other actionable issue was found.
The existing TE BOM/CAD/library changes remain intact; no generated artifact is
hand-edited. All integrated checks below completed on the corrected snapshot.

| Exact command / review | Actual result |
| :--- | :--- |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | **208 PASS, no skips**, Python 3.14.4 / KiCad 9.0.7. Includes six isolated native probes, the new TE-provenance regression, both 280-cut sweeps and existing file/negative fixtures. |
| `python3 -B scripts/analyze_limits.py` and `python3 -B scripts/design_bounds.py` | Both **exit 0**; **0.501018 W nominal / 0.756803 W upper per resistor** unchanged. JSON now identifies prototype-only scope, engineering temperature assumptions, unknown manufacturer test conditions and unverified catalogue-rating transfer. These are conditional calculations, not measurements. |
| `python3 -B pcb/sync_libraries.py --check` | **PASS**, ten footprints/six symbols. PCB, schematic, BOM, resistor footprint and all five diagnostic-review inputs match the reviewed pre-correction hashes; no synchronization or approval refresh was needed. |
| `make check` | **PASS**, `attempt-l85xrk62`: DRC 0, unconnected 0, footprint/parity 0; ERC 0 errors/eight exact reviewed warnings. Eight nets/34 terminals/52 IPC records, 16 parts, **32 PTH (18 component +14 via), four NPTH**, F.Mask/B.Mask/F.Paste **52/36/16** and all archives checked. No publication from this target. |
| `make gerbers` | **Exit 0, prototype publication**, `attempt-vcvn00fw`, with corrected notes and W3/W4 reasons. Native Assembly.pdf inspected; Assembly.txt confirms **16 anchors/34 terminal datums**, TE identities and unchanged signed-Y coordinates. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | **PASS of production refusal/comparison**, `tmp/workflow-validation/run-b4pz11o5/report.json`: clean (0), serial `make all` (2), clean (0), parallel `make -j4 all` (2). Both pass file checks and refuse solely for all five holds; validated geometry/connectivity/population/notes agree. |
| `python3 -B scripts/verify_workflow.py --target prototype --expect-holds C4 C5 W3 W1 W4` | **PASS of actual prototype publication/comparison**, `tmp/workflow-validation/run-t_v3ku83/report.json`: both clean commands and serial/parallel prototype builds exit 0. Validated geometry/connectivity/population, controlled notes, manifests, mirrors and ZIP mode/hold notices agree. |
| Final source/artifact review | `git diff --check` PASS. All unchanged physical/CAD/BOM/CPL hashes remain consistent. Current package source/artifact hashes and both mirrors validate; no generated artifact was hand-edited. Supplier CAM/placement/process/allocation and hardware tests remain unperformed. |

**Current package:** `build/status.json` and `build/manifest.json` identify
**status=prototype, mode=prototype**, attempt **`attempt-m6qoxdcv`**, hardware
**1.2.0-dev**, base **399c588**, `worktree_dirty=true`. This is the final parallel
prototype publication, preserved in the workflow above. PCB and schematic hashes
remain **`da897569fe74102178f1bf5c51d4b7c27f283395c6c3026fd016a22f3eb2c1ff`** and
**`01329ea3bf88981f3df2f7ba202226f94947c2a3b8ff6c80a75d3c1ecd87e77a`**.
Gerber ZIP/mirror SHA-256:
**`b8816e9a4d422c916b345c5ce63fe0b7b97df98ed8c7b91eb8623e383475801b`**.
Manifest SHA-256:
**`2df63812c0ea3971fbd7e4e8a368e96c857eb639e71f105ee03e192482998d05`**.

The package contains Gerbers/FlyTest, TE BOM, generated CPL, IPC, assembly outputs,
via treatment, scope notices, all seven corrected controlled notes and reports.
The production workflow's `before/` preserves the initial check/direct prototype
exports and earlier quarantined evidence; both workflows preserve their own
serial/parallel snapshots and verify unrelated `tmp/` evidence unchanged.
**Gate P is met, not upload/order or field approval.** A/B/C and C4/C5/W3/W1/W4
remain held; `allocation_verified=false`. No switch/environment research,
physical qualification, commit, upload or order was performed in this correction.

### Documentation Cleanup

The user approved implementation of [DeduplicationPlan.md](DeduplicationPlan.md)
on **2026-09-11**, beginning at **d60c83e** with clean tracked/staged diffs and
only that plan untracked. This is **P5 documentation maintenance plus P6 file
verification**, not new electrical, mechanical, supplier or physical qualification.

ASSEMBLY now owns complete human guardrails and the reviewed-component index;
INSTALL owns the functional/cut tables and directly linked whole-boundary safety
policy; MATERIALS owns live procurement history and quantity allocation. Other
guides link these owners while retaining their local inspect/stop/record duties.
Named current screens remain in DESIGN_BOUNDS, model/historical comparisons in
ELECTRICAL, and manufacturer evidence and dated research corrections in their
controlled notes. AGENTS now defines impact-based documentation maintenance.

The [plan's implementation record](DeduplicationPlan.md#8-implementation-record)
tracks deleted sections, destinations and retained controls. The baseline audit
under **`tmp/deduplication-review/baseline-final/`** preserves the original 17
documents, the approved plan and previous package manifest/status. Its SHA256
comparison found **36/36 authoritative machine/analysis/test files unchanged**
from d60c83e, with generated CPL also unchanged. That baseline comparison and
the earlier prototype package are not renewed native or publication evidence.

Three independent read-only reviews covered physical/DFM guardrails,
operation/acceptance/procurement, and electrical/model/research evidence against
the originals. **No actionable semantic loss was found.** Every old section
heading remains; complete owners were established before consumer tables were
removed. Code, model expectations and native diagnostic approvals are unchanged.

| Exact command / review | Actual result and scope |
| :--- | :--- |
| `/snap/bin/kicad.kicad-cli --version` | **9.0.7**, executed headlessly; no sandbox-bypass parameter used. |
| `python3 -B pcb/sync_libraries.py --check` | **PASS**, ten local footprints/six symbols. No synchronization/write or part/process approval. |
| `TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v` | **208 PASS, no skips**, Python 3.14.4 / KiCad 9.0.7, including all six native probes. Runtime 56.410 s. Fixtures are isolated, not a cleanup of authoritative artifacts. |
| `python3 -B scripts/analyze_limits.py` and `python3 -B scripts/design_bounds.py` | Both **exit 0**, unchanged declared results and assumptions, including the 280-cut sweep and 0.501018 W nominal / 0.756803 W upper resistor screens. Models are not measurements or qualification. |
| `make check` | **PASS**, `attempt-_7bqspsx`: DRC/unconnected/footprint-parity 0; ERC has the same eight exact reviewed warnings. Hash-bound annotation diagnostic and known export debug lines retained. Eight nets/34 terminals/52 IPC records, 16 parts, 32 PTH/four NPTH, F.Mask/B.Mask/F.Paste 52/36/16 and archives verified. No publication from this target. |
| `make gerbers` | **Exit 0**, direct prototype publication `attempt-3dhahcaa` with the consolidated notes, all five holds deferred and unchanged sourcing gates. |
| `python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4` | **PASS of production refusal/comparison**, `tmp/workflow-validation/run-phk67p0_/report.json`: separate clean (0), serial `make all` (2), clean (0), `make -j4 all` (2). Both pass file checks and refuse solely for the same five holds; validated data/notes match and unrelated temporary evidence is preserved. |
| `python3 -B scripts/verify_workflow.py --target prototype --expect-holds C4 C5 W3 W1 W4` | **PASS of actual serial/parallel prototype publication/comparison**, `tmp/workflow-validation/run-6mo3gme4/report.json`: both clean commands and builds exit 0. Prototype ran last; normalized fabrication, connectivity, population, assembly datums, notes and mode/hold notices match. PDFs are archived/hashed, not render-diffed or physically inspected. |
| `python3 -B tmp/deduplication-review/audit.py --isolate-build --manifest-hashes --name published-release` | **Source/artifact/mirror hashes and manifest identity match** for a complete external copy under `/tmp/opencode/dogfence-dedup-release-8x13k3gs/release`. All 115 shipped-note link occurrences resolve; the 15 labelled supplementary repository-only references are reported separately and manually reviewed, not silently treated as shipped links. |
| Checkout links, semantic review and whitespace | The pre-handoff audit checked **511 guide/note links plus 72 plan links**, with no missing paths/fragments or parser warnings in its supported scope. Independent deletion review and `git diff --check`, `git diff --cached --check`, and the untracked-plan whitespace check passed. No external-URL, full Markdown-renderer or hardware qualification is claimed. |

**Current package:** `build/status.json` and `build/manifest.json` identify
**status=prototype, mode=prototype**, attempt **`attempt-8fj6a2h2`**, hardware
**1.2.0-dev**, base **d60c83e**, `worktree_dirty=true`. Manifest SHA256 is
**`0cd67bc1309e719fc89d08f0a2516e0d61d8ea66b26f28835ee6dceb5b7f8db7`**;
Gerber ZIP/mirror SHA256 is
**`8240e0d05d3baf446d245c96868c3a8290c80fcde2f86f9f1a30536194f19a2a`**.
The source PCB/schematic hashes are unchanged from the TE correction record.
Generated CPL, assembly datum text and via-treatment data also retain their
previous bytes; artifact creation timestamps are not design changes.

The production workflow's `before/` preserves this session's initial check,
direct prototype publication and their quarantined prior package. Both workflow
runs preserve separate serial/parallel trees and report unrelated `tmp/` evidence
unchanged. Session-only audit tooling, original/current note copies and reports
remain under `tmp/deduplication-review/`; it is not a new manufacturing gate or
shipped dependency. Its nineteen synthetic parser/hash/isolation checks passed.

`tmp/deduplication-review/context-review.md` records the manual disposition of
all fifteen repository-only link occurrences. Root guides are still deliberately
not shipped: recipients need the checkout for these supplemental references;
essential assembly/model/qualification limits remain local or in shipped siblings.
This is a documented packaging limitation, not a claim that every root link works
outside the repository. The generated ZIP notices remain self-contained.

Before this final handoff entry, `reviewed-docs/report.json` measured the original
17 documents at **7,664 -> 7,593 lines**, **811,154 -> 758,380 bytes**, and
**112,368 -> 101,989 whitespace-delimited Markdown tokens**. Tokens include tables,
code and links, not only rendered prose. Line rewrapping and completing missing
owner inventories explain the modest line reduction; historical records were not
deleted to meet a quota. Final handoff bookkeeping is additional text.

**Gate P is met for these files only.** A/B/C and C4/C5/W3/W1/W4 remain held;
`allocation_verified=false`. No annotation re-review was needed because its
five approval-bound inputs did not change. No approval hashes, source rules or
population were changed; no supplier acceptance, hardware test, upload, order or
commit occurred. Subsequent work follows the existing P3/P4 supplier queue below.

### Next Bounded Work

**Current scope: board design/finalization only, for five fully assembled
JLCPCB prototypes.** The following queue supersedes the old instruction to start
with the first unchecked P2 item. Preserve the independent holds below without
spending this board package on their research.

1. **P3/P4, job allocation:** follow [ORDERING's board queue](ORDERING.md#board-finalization-queue)
   for the [reviewed prototype population](pcb/ASSEMBLY.md#reviewed-components),
   including fitted quantities and supplier-specified attrition. [MATERIALS](MATERIALS.md#resistor-procurement-and-history)
   owns the separate production order and cancelled/rejected history. These are
   supplier order tasks, not new Gate P file blockers. Do not reopen retired
   sourcing or axial-resistor forming; a production substitution still requires
   its own evidence/model/process review and deliberate source updates.
2. **P3, W1/W4/W5:** accept actual Kefa/GDT lot/body/pin patterns, KF129 variant,
   GDT forming, Ruilon metric/inch clarification and heavy-copper SMT/THT solder
   process against the already implemented holes/lands, including the **retained
   resistor-land alternative to TE's recommendation**. Board-side geometry is
   explicit; supplier and physical acceptance remain unperformed.
3. **P4, C2/W1/W4:** review actual supplier models against the generated sixteen
   anchors / 34 pin datums, then the panel, processed PCB/stencil and protected
   drills. Use J_EARTH's **X=161.35 courtyard** and **1.30 budgeted body
   overhang**; do not default to five panels or insert tooling into functional
   geometry. Obtain the exact five-individual-board quote, including attrition.
4. After any further source change, rerun `make check`, `make gerbers` and
   `python3 -B scripts/verify_workflow.py --target prototype --expect-holds C4 C5 W3 W1 W4`.
   Verify actual serial/parallel publication, matching manifests and scope notices;
   a sourcing refusal is not a prototype workflow PASS. Production must continue
   to refuse with its five holds. Record supplier responses separately and leave
   prototype-dependent tests deferred. No upload/order/commit is authorized.

### Independent Held Work

These tasks remain valid for their respective release scopes, **outside the
current board-only package**. They are not a reason to restart switch or
environmental research while waiting for a PCB supplier response.

1. **P2/C3 switch:** obtain the complete offered/supplied article and K&N
   link/contact development, then application-specific DC and global-transfer
   acceptance for the real source/cable/fault envelope. The standard WAA364
   catalogue schedule is now resolved; do not repeat its transcription or use
   it as approved field wiring. Assign physical terminals and RUN/TEST detents
   only after that evidence is accepted, then perform the full-hub checks.
2. **C4/P6:** qualify the **implemented two-shunt hybrid** at actual LED terminals
   for normal RUN/TEST/switching and an explicitly defined nearby-transient
   scope. Record forward/reverse peaks, recovery/ringing and usable 5 m light
   at the accepted minimum current. Do not confuse reverse recovery with forward
   clamp response or require the historical 40-part circuit by default. No
   reversed-flying-lead survival or prohibited cattle-fence test is required.
3. **P2, C5/W2:** use the now-resolved K.12 **135 V / 1300 ohm** network rather
   than re-researching its headline voltage. Obtain application/type-test
   recovery evidence for the actual compact tubes, or develop the genuinely
   DC-power-rated TDK stack's mechanical/RF solution. Any necessary guardrail
   change requires user approval. Complete hazardous resistive-fault containment
   and the real hub current/OV/latch/isolation/transient circuit; a larger PSU,
   2 A fuse or 62 V eFuse alone is not that circuit.
4. **W3/P6:** verify actual source setting/range and closed-OneGel temperatures
   for the intended TE prototype or separately reviewed Yageo production population,
   including chip/pad/PCB/material interfaces and rating transfer from the
   manufacturer's mounting basis,
   upper-source, hot/solar and output-short cases. The **0.756803 W** current
   screen is not a temperature measurement; PR02/MBE and 37 V figures remain
   historical. No axial resistor standoff applies. A passive
   design covering the normal source range is an alternative to a new cutoff.
   Resolve OneGel process/temperature conflicts; healthy TEST cannot use a timer
   as its baseline safeguard. A364's exact DC/global-transfer approval stays open.
5. **Cable/environment applicability:** cable lot/standard, UV/wet-conduit and
   bend/impulse applicability remain independent evidence, not a guessed
   resistor-model change. Do not repeat questions about confirmed reel colours.
   P3/P4 sourcing, forming, placement and CAM tasks belong to the active board
   queue above, not this independent research list.
6. After a reviewed circuit/part/process decision, update actual source/BOM/
   libraries/notes, regenerate/check CPL and fabrication data, repeat the
   relevant automated/native checks and controlled supplier/hardware tests,
   and close only evidence-backed issues/gates. No order/upload/commit is
   authorized by this handoff.

Suggested instruction for the next board-finalization session:

```text
Focus ONLY on PCB finalization for five fully assembled JLCPCB prototypes.
Read AGENTS.md and REMEDIATION.md, inspect the current worktree, and work the
next P3/P4 board item in Next Bounded Work (or the package I specify). Do not
restart switch or environmental research; preserve their holds. Preserve existing
changes and physical guardrails. Use the settled 41-station, same-end-return,
continuous-safe TEST baseline; do not add a direction selector. Verify the work,
update the plan/session log with evidence and remaining blockers, and do not
place orders or commit changes unless requested.
```
