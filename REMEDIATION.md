# Remediation Plan

Prepared: 2026-09-06. Reviewed hardware baseline: v1.1.0.
Implementation handoff: **2026-09-07, hardware 1.2.0-dev**.

**Status: verification/build tooling, DC analysis, bounded PCB corrections and documentation are implemented and file-checked. Protection design, remaining part/process acceptance, and physical qualification are NOT complete. Manufacturing and field release remain on hold.**

This is the starting context and implementation checklist for subsequent sessions. It consolidates the review and the user's later decisions, including changes to the originally proposed TEST wiring. It is not manufacturing approval, a completed hardware test report, or a board-level lightning certification.

## Start Here

1. Read [AGENTS.md](AGENTS.md) for operating instructions and physical guardrails, then this file. Read the relevant source files before editing them.
2. Inspect `git status` and the existing diff. Preserve all work already present. The implementation session started from a clean tracked worktree; its changes are not committed. Historical preparation edits/archives and unrelated `tmp/` evidence must not be reverted or cleaned indiscriminately. See the current handoff for preserved build evidence.
3. Treat the working `pcb/pcb.kicad_sch`, `pcb/pcb.kicad_pcb`, project settings, and reviewed sourcing data as the design sources. `build/*` contains Makefile-generated production outputs. Backups, archives, and `tmp/` copies are not authoritative designs.
4. Use the agreed requirements and TEST matrix below. Documents are synchronized to the current development source; `pcb/ELECTRICAL.md` and `pcb/ASSEMBLY.md` record the remaining design/evidence limitations. `REVIEW.md` remains an audit template, not completed approval.
5. P1's checking infrastructure is implemented. The next bounded tasks are **P2 protection/continuous-duty decisions** and **P3 maximum-pin/land-pattern evidence**, which can proceed independently. Do not freeze the final layout/BOM before the protection architecture is settled.
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
| P2 | Six-end functional matrix; separate A/B/C DC model; 280 clean cuts, 615 inter-core fault cases, repair/retest and legacy negative controls; source/fuse/thermal screens and candidate research. | C4/C5 protection architecture and parts are **not selected or implemented**. W3's enforceable source/thermal envelope, switch approval and actual device/site evidence remain open. |
| P3 | Diode holes/identity, local libraries/metadata, SMT-via separation by relocation, honest nominal courtyard correction, legend/F.Fab/underside references, stackup arithmetic and controlled assembly drawing. | Maximum finished pins/bodies for several THT parts, exact SMT land pattern or approved alternative, forming/solder process, enclosure fit and final protection placement. |
| P4 | Reproducible, validated private draft exports; native signed-Y mixed-assembly CPL; population/net/drill/archive checks; manifest implementation and release holds. | No current published release. Exact assembler centroids/rotations, CAM/stencil, quote/allocation, panel and process approvals remain open. |
| P5 | All nine main guides updated for the actual 1.2.0-dev draft, truthful claims, preserved purchases and separate acceptance categories. | Resynchronize after any future circuit/part/process decision; documents are not approval. |
| P6 | 130 automated tests including native probes; `make check`; preserved clean serial/parallel comparison; source/assembly render review. | Actual processed CAM review, five-prototype acceptance, reversal/fault/thermal/visibility/RF/site/surge tests and installer earthing approval are **not performed**. |

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
| PSU | User believes the purchased unit is **Mean Well LRS-35-36**, 36 V / 1 A / 36 W; confirm the nameplate. User is willing to upgrade to **LRS-75-36**, 36 V / 2.1 A / 75.6 W. The latter is the preferred capacity-margin candidate, not a confirmed purchase or a solution to fuse/GDT coordination. Both have adjustable output and hiccup overload protection. |
| Switch | **Kraus & Naimer CA10.A362**, six-pole centre-off, is a sourcing candidate. Its 20 A thermal rating is ample for expected normal current. Exact DC load-breaking capability, contact program, and transfer sequencing remain to be confirmed. Do not equate AC/thermal or insulation ratings with DC switching or lightning isolation. |
| Enclosures | WISKA **COMBI 308**, using the documented Essentra supports and WISKA MP0100 gel. Raised installation, not intended for continuous submersion. Validate the actual assembled fit and material/process compatibility. |
| Site | Isle of Man, less than 1 km from the coast; frequent rain, salt exposure, and possible condensation. Observed outdoor ambient is approximately **-10 to +30 degrees C**. Some boxes are in direct sun. These observations are not guaranteed lifetime extremes or maximum internal temperatures. |
| Cable | Likely **Oceanflex CM03/05.100**, supplier code **P01018**, linked in the source list. Listed as three tinned-copper 2.5 mm^2 cores, 35/0.30 mm strands per core, 7.3 mm maximum outside diameter, **60 V maximum**, and **-15 to +70 degrees C** complete-cable working temperature. Actual purchased identity remains unconfirmed. |
| Cable limitations | The supplier's 105-degree ISO 6722 reference concerns cores, not the complete cable. Do not assume -40-degree arctic performance, mains-voltage suitability, permanent UV exposure, wet-conduit suitability, or impulse withstand. Maximum conductor resistance and actual three-core colours need evidence; the listing's black/red colour table is incomplete. |
| Routing | Mostly 0.3-1.0 m above ground on timber fencing with horizontal metal wire strands. Plastic conduit beneath driveways/gates; consider that conduit can become wet. No electrical connection to the supporting fence wires. |
| Cattle fencing | The supporting fence is not energized. A separate energized cattle wire may run **at least 0.5 m away for up to 300 m in parallel**. Use that as a repetitive-pulse qualification case, not an interference-safe clearance claim. Allow for movement; increase separation where practical. Plastic conduit is not electromagnetic shielding. |
| LEDs | Purchased baseline **APEM Q10F5SXXSG02E**, no internal resistor, 20 mA maximum per published family data and 5 V maximum reverse voltage. `02` does not mean regulated 2 V operation. Target **4-5 m visibility in full daylight**, with ON/OFF distinguishable at 5 m at the minimum field current and real viewing angles. |
| Earthing | User proposes sharing local earth between DogWatch protection and both shed-end boards. Confirm the connection to actual building PE/electrodes against regional OEM instructions and a qualified installer's site-specific earthing design. Do not add arbitrary unbonded rods, directly earth a fence core, or assume DC negative must be bonded to earth. Five earth-connected stations do not automatically require five independent electrodes. |

The functional choices above are settled. Do not repeatedly ask the user to choose TEST direction, automatic identification, or a timeout. Remaining manufacturer, CAM, and physical-test evidence is tracked separately below.

## TEST Topology

Implement this **functional** contact matrix, then map it to the confirmed switch's actual terminal numbering. It is not a terminal-number wiring instruction for an unverified switch.

| Boundary-cable end | RUN | OFF | TEST |
| :--- | :--- | :--- | :--- |
| Start A | Transmitter T1 | Isolated | +36 V |
| Start B | Transmitter T1 | Isolated | DC negative |
| Start C | Transmitter T1 | Isolated | +36 V |
| End A | Transmitter T2 | Isolated | Isolated |
| End B | Transmitter T2 | Isolated | Isolated |
| End C | Transmitter T2 | Isolated | Isolated |

- Use six independent boundary-end connections so OFF leaves all six ends individually accessible/isolated. Required RUN ties and TEST positive ties belong on the appropriate source-side contacts, not as permanent field-end straps.
- The removed legacy 4PDT matrix left End A and End C joined at common Pin 8. An empty TEST throw does not separate them; the healthy core backfeeds the broken core. The negative regression reproduces this defect; do not restore that wiring.
- **Do not retain the earlier opposite-end B-return proposal.** It leaves both sides dark after a complete cable cut. **Do not connect both B ends to negative in normal TEST.** That masks a B-only break.
- Keep the transmitter and TEST supply isolated in the required modes, including the actual transfer sequence. OFF is ordinary disconnection, not demonstrated storm/lightning isolation.
- Preserve the WAGO through-splice/PCB-tap architecture. Normal perimeter current does not pass through every PCB's rails; each board draws its local indicator current. Surge current through a board is a separate design case.

Expected steady-state indications for one clean cut location, with healthy boards/GDTs and no additional inter-core shorts:

| Cut cores | Before the cut | After the cut |
| :--- | :--- | :--- |
| A | Both on | A off, C on |
| B | Both on | Both off |
| C | Both on | A on, C off |
| A + B | Both on | Both off |
| A + C | Both on | Both off |
| B + C | Both on | Both off |
| A + B + C | Both on | Both off |

Use the first applicable LED-state transition to identify the adjacent span, including 3900-4000 m. Repair and retest for further faults. The ambiguity between B-only and several multi-core cuts is acceptable to the user. Local indicator failures and shorts require separate troubleshooting, not a guarantee that every dark LED means a cable cut.

Optional DMM checks belong in the revised installation/acceptance documentation: with all power/backup sources disconnected and all six ends isolated, measure Start A to End A, and likewise B and C. Both physical ends are at the shed. An ideal 4 km / 2.5 mm^2 copper core is about 28 ohms at 20 degrees C, not zero or the three-core parallel-loop resistance. Use verified cable data and recorded commissioning baselines for actual limits. Do not use resistance mode on powered wiring or a high-voltage insulation tester through connected boards/transmitter. These measurements aid diagnosis; they do not replace LED span localization.

## Physical Guardrails

Preserve these unless the user explicitly approves a reasoned design change. Correcting unsupported rating claims is not permission to weaken the physical construction.

| Feature | Preserve |
| :--- | :--- |
| Board | 63 x 56 mm, outline from (97.0, 94.5) to (160.0, 150.5) mm. Four 3.2 mm mounting holes at (101.5, 99.0), (155.5, 99.0), (101.5, 146.0), (155.5, 146.0), with their mechanical clearances. |
| Copper | 0.070 mm on F.Cu and B.Cu; 3.2 mm nominal full-width A/B/C rails on both layers. |
| Rail vias | Three per rail, X = 112.5, 114.0, 115.5 mm; Y = 114.88, 122.50, 130.12 mm respectively. Each 1.0 mm drill / 1.8 mm pad. Do not delete or shrink. |
| Earth copper | Matching solid dual-layer earth bus, bounding X = 143.99-157.25 mm and Y = 111.25-133.75 mm. Five 1.0/1.8 mm drill/pad vias at X = 150 mm and Y = 114.88, 118.69, 122.50, 126.31, 130.12 mm; preserve continuity and geometry. |
| Isolation | At least 3.0 mm fence-to-earth copper clearance. Preserve the B-return routing at X = 135.50 mm and Y = 107.20 / 137.80 mm unless an approved alternative maintains the constraints. |
| Earth GDTs | Centres at Y = 113.50, 122.50, 131.50 mm: retain 9.00 mm pitch. Check actual maximum body dimensions; nominal spacing does not prove a tolerance-free 1 mm air gap. |
| LED terminals | J_LED_A at (145.50, 103.00), 90 degrees, opens north; J_LED_C at (145.50, 142.00), 270 degrees, opens south. Pad 1 positive at X = 142.96 and pad 2 B return at X = 148.04 on both. Preserve the intentional pad mapping. |
| Overpass | GDT_AC north-south over B, now at X=125.80, with 15.24 mm formed pitch and at least 2.0 mm physical gap under the complete raised span. See the controlled forming/inspection drawing in `pcb/ASSEMBLY.md`. |

Apply [README's DFM policy](README.md#via-and-component-hole-dfm) and AGENTS section 9. In particular: no ordinary via as a lead-insertion hole, no blanket filling of all 1 mm holes, and no assumption that 2 oz exterior copper means 70-micrometre barrels.

## Reviewed Components

The current board has 14 electrical components, all on top: two SMT and twelve THT, plus four mechanical hole footprints. Counts must be regenerated if protection parts are added.

| References | Baseline MPN / sourcing code |
| :--- | :--- |
| D1, D2 | onsemi 1N4007G / C232439. The former LGE attribution is corrected in the BOM and source metadata. |
| R1, R2 | Vishay MBE04140C2201FC100, 2.2 kohm / C1368610. |
| GDT_AB, GDT_BC | Ruilon SMD5050-470NA / C39692533. |
| GDT_AC | Bencent B5G470L / C5337217. |
| GDT_A_E, GDT_B_E, GDT_C_E | Ruilon 2R470TD-8 / C2836978. |
| J_IN, J_EARTH | Cixi Kefa KF128-7.62-3P / C474957. |
| J_LED_A, J_LED_C | Cixi Kefa KF129-5.08-2P / C475092. |

The external baseline includes APEM Q10F5SXXSG02E indicators, Essentra LCBSBM-6-01A-RT supports, WAGO 221-613 splices, and WISKA MP0100 gel. The existing hub fuse is specified as Littelfuse 0217002.MXP in Phoenix Contact UK 5-HESILED 60 / 3004139. Verify exact supplied items and ratings before design freeze. Historic inventory counts are not allocations for the new order.

Do not select the optional upgrades in README, or the Q14 indicator suggestion in `LED.md`, as pre-approved drop-ins. Preserve the user's procurement records and qualify any substitution separately.

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
| C1 | Former D1/D2 0.90 mm holes could finish at 0.82, below the onsemi maximum lead; manufacturer attribution was wrong. | **File defect corrected:** source/library and native drills are 1.10 / 2.20 mm. Controlling 0.034-inch = 0.8636 mm lead gives 0.1564 mm worst-hole diametral clearance and 0.55 mm nominal ring. BOM/source identity is onsemi. Actual forming/insertion/workmanship remains P6 acceptance. |
| C2 | Former hand-maintained CPL had positive screen Y; custom footprint axes/polarities differ from stock-looking names. | **Coordinate-generation defect corrected:** all 14 parts now come from native positions, with -103/-142 LED Y, absolute origin and rotations modulo 360. **OPEN:** assembler model centroid/rotation approval. |
| C3 | Legacy End A/C common Pin 8 backfed breaks; earlier B-return proposals masked required cuts. | **Functional/software correction implemented:** six-end matrix, all 280 clean-cut cases, repair/retest and both legacy negative controls pass. **OPEN:** actual switch DC/global-transfer approval and full-hub physical tests. |
| C4 | A series 1N4007 does not guarantee LED reverse voltage below 5 V or limit every forward transient safely. Supply and flying-lead reversal differ. | **OPEN DESIGN HOLD.** Candidate clamp/active-stage evidence is in `pcb/ELECTRICAL.md`; none is approved or populated. Complete simultaneous voltage, leakage/brightness and forward-pulse bounds, implement the circuit and qualify it. |
| C5 | The 2 A fuse need not clear cable-limited faults; powered GDT holdover/extinction is unqualified. | **OPEN DESIGN HOLD.** New-topology fault screens and actual published PSU/fuse limits replace the old fuse-blow claim. A modeled far-end 10 V arc draws 0.259543 A / 2.602168 W in its path with only 0.979810 A total. Select a supported protection/shutdown architecture and obtain actual powered-recovery evidence. |
| W1 | Former nine rail-via holes overlapped all four SMT GDT apertures by 0.19 mm; normal covering limits do not fit the protected 1.00 mm holes. | **Collision corrected, PROCESS/DESIGN HOLD remains.** GDT_AB/BC at X=119.50 give minimum nominal hole/aperture gap 0.933911 mm and full-annulus gap 0.533911 mm; all vias/rails remain. Retained 5.20 x 2.00 lands differ from the retrieved Ruilon recommended-pattern table. Resolve the actual drawing or approve the alternative, solder volume and via/CAM treatment. |
| W2 | DC sparkover, component impulse ratings, heavy copper and parallel pins do not establish transient clamp limits, sharing or a board rating. | **Claims corrected; qualification OPEN.** No assembled surge/current/lifetime rating is assigned. Coordinate the actual protection/cable/earth paths and complete defined transient and recovery tests. |
| W3 | Nominal 0.50 W/resistor does not prove cool operation or long life in gel; rating modes differ. | **OPEN DESIGN/THERMAL HOLD.** Declared 40.39597 V/R-min screening gives 0.753190 W/resistor, above 0.65 W standard-mode P70. Establish an enforceable supply envelope and accepted resistor/thermal design; perform potted/solar steady-state measurements. |
| W4 | Connector holes remain 1.4/1.3 mm without maximum-pin proof; old J_IN courtyard cut through its nominal body. | **Courtyard defect corrected; FIT HOLD remains.** J_IN east courtyard is now X=111.45 and adjacent SMT starts at 116.65. Maximum pins/bodies for several THT parts are still unverified; no guessed 1.60 mm resize. Provisional J_EARTH body overhang is 0.30 mm, requiring panel/enclosure approval. See `pcb/ASSEMBLY.md`. |
| W5 | Former LED torque was too high; complete enclosure fit and raised GDT geometry were unproven. | **Instructions/drawing corrected:** 0.20-0.25 Nm subject to exact APEM model; controlled whole-span >=2.00 mm overpass drawing and inspection method. **OPEN:** accepted forming tolerances, Essentra thickness fit, COMBI dry-fit and material/process tests. |
| W6 | Legacy legend, incomplete checks and inconsistent libraries/metadata undermined verification. | **File-level correction verified:** native 1.00/0.15 legend, strict effective rules, ten local footprints/six symbols, matched BOM metadata, DRC/parity/geometry and regression checks. Reviewed warnings remain visible and narrowly bound; no project severity ignores or exclusions. |
| W7 | Legacy fault, RF, earthing, environmental/lifetime and five-board sign-off claims were overstated. | **Documentation corrected.** 41-station/same-end requirements and separate acceptance categories are synchronized. **OPEN:** actual switch/cable/PSU identity, RF/cattle-fence, coastal/solar/material, earthing and hardware/site qualification. |

The source stackup now totals 1.600 mm (1.440 core + two 0.070 copper + two
0.010 mask layers), and underside references/revision identification are added.
Supplier thickness convention/tolerances, retaining an actual unpotted reference,
and manufacturer-added panel rails/fiducials/tooling still require acceptance.

## Implementation Sequence

**P1 and P2 can proceed in parallel. P3 needs P1's checking infrastructure and P2's approved protection-part decisions before final layout freeze. P4 follows the final layout. P5 accompanies every change, and P6 verifies the resulting release.**

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
- [ ] Obtain the exact selected switch contact diagram and DC/global-transfer approval, then assign and verify physical terminal numbers.
- [x] Make the default analysis use 41 stations and same-end return. Model A, B and C separately, including floating islands and one-way branches; parameterize cable resistance, voltage, LED/diode drops and temperature/tolerance inputs.
- [x] Add all seven cut combinations across all 40 spans, first/final spans and repair/retest sequences, with current/power balance and both legacy backfeed/masking negative controls.
- [ ] Design LED protection that covers reversed supply and reversed flying leads while preserving normal light output. Prefer a PCB-side solution compatible with the purchased raw indicators and no field soldering. A single antiparallel diode across the PCB connector does not cover both faults.
- [ ] Select actual parts using maximum clamp voltage, leakage, temperature/tolerance, and pulse/current data, not just a nominal TVS/zener voltage. Check LED forward pulse current as well as reverse voltage. A voltage clamp alone is not automatically adequate forward-current protection. Recheck fault observability after any circuit change: preserve or explicitly model one-way rung behavior, rather than using the old forward-only model to validate a bidirectional replacement.
- [ ] Coordinate the primary GDTs, indicator branches, source interface, and any secondary protection. Reviewed impulse sparkover at 1 kV/us is up to 950 V for SMD5050-470NA and 1100 V for 2R470TD-8; B5G470L's 850 V figure is specified for 99% of measured values. Include lead overshoot and the cable's unverified impulse withstand.
- [x] Implement hard/resistive-short and conditional 10/15 V ignited-GDT load-line screens in the new topology, including separate earth paths and every station for inter-core faults. Explicitly distinguish CV demand from actual PSU overload/hiccup current and GDT holdover.
- [ ] Complete the actual PSU/cable/GDT dynamic and failed-device analysis, and implement a coordinated protective/shutdown arrangement. Do not infer extinction from sparkover, holding current from glow-to-arc figures, or discrimination from a reduced fuse value alone.
- [x] Remove `BLOWS (>2A)` from analysis logic. Use published Littelfuse 217 DC interruption/opening conditions and Mean Well current/power/overload envelopes; leave unmeasured hiccup and clearing times unknown. Recalculate faults for the new wiring.
- [ ] Bound continuous resistor/LED/connector temperatures, including supply tolerance and accessible adjustment. Vishay MBE0414's 1 W power-mode rating is not its 0.65 W standard-mode long-life rating. Keep the present resistors only if the resulting limits support them; qualify any higher-wattage substitute rather than assuming a drop-in or reduced heat generation.
- [x] Define the electrical qualification scope and unresolved supplier/test evidence in `pcb/ELECTRICAL.md` and `ACCEPTANCE.md`. No needless logic, blanket earth plane, direction selector or unsupported assembled ratings were added.

**Exit:** The hub logic and protection architecture are specified, reviewed, and reflected in the schematic/BOM. Normal-operation safety is analyzed; remaining powered-surge qualification is explicitly open rather than declared solved by prose.

**Current exit: NOT met.** The model/research is implemented, but no final
protection MPN/circuit is approved. BZX85C3V9-TR and TL431BQDBZR investigations
still need simultaneous clamp, leakage/brightness and pulse-current bounds;
TL431LIBQDBZR was rejected for direct shunt use because of its lower current
ceiling. Bare-GDT holdover, the 2027-47-BLF alternative and a series GDT/MOV
architecture need actual-network evidence, not a nominal voltage comparison.
The resistor/source screen is not a potted temperature qualification.

### P3: PCB DFM

Files: `pcb/pcb.kicad_pcb`, schematic footprint assignments, project-local libraries/tables, `pcb/pcb.kicad_pro`, `pcb/pcb.kicad_dru`, controlled assembly/fit notes under `pcb/`.

- [x] Create project-local definitions for intentional geometry: ten footprints and six symbols. Preserve global pad/net mappings through migration, including distinct LED connectors and the cathode-right diode. Deliberate DFM relocations are recorded separately in `pcb/ASSEMBLY.md`.
- [x] Change D1/D2 to **1.10 mm finished holes / 2.20 mm pads**, nominal ring 0.55 mm. Correct onsemi identity and affected sourcing/geometry records; native-generated drills match.
- [ ] Obtain maximum finished lead dimensions for every selected THT part, including connector pin diagonals and forming tolerances. Record drawing revision and fit calculation. Treat 1.60 mm connector holes as a candidate to verify, not a guaranteed answer from supplier CAD.
- [ ] Apply `nominal finished hole - 0.08 mm >= maximum pin envelope + assembly allowance`; start with at least 0.10 mm diametral allowance after tolerance and account separately for pitch/hole-position/forming tolerances. Recheck annular rings, hole/copper spacing, and edges after resizing. Do not solve insertion by reaming plated finished boards.
- [ ] Rebuild body/fabrication outlines and courtyards from maximum dimensions plus appropriate assembly clearance. Resolve real interference by placement/geometry changes within the guardrails, not by shrinking courtyards. Check rework and screwdriver access.
- [x] Remove the demonstrated 0.19 mm SMT/via-aperture collision by moving GDT_AB/BC to X=119.50 and GDT_AC to X=125.80. Retain all nine rail vias, full-width copper and original SMT pads; full drill-circle/annulus/mask/paste separation is checked. This does not approve the retained land pattern or process below.
- [ ] Follow the selected GDT land pattern and obtain solder-volume/thermal-process acceptance. If no compliant solution preserves the protected geometry, obtain explicit design/process approval rather than shrinking vias or assuming 1 mm resin filling is standard.
- [ ] Place/route the selected protection parts, then revalidate all nets, surge clearances, symmetry requirements, and component-fit evidence. Do not narrow surge connections with generic thermal-relief spokes simply to ease soldering; agree a suitable heavy-copper soldering process.
- [x] Correct legend height/stroke/clipping using native 1.00 / 0.15 mm text. Retain polarity, cathode and A/B/C/EARTH labels; add underside references, F.Fab aids and 1.2.0-dev identification. Native DRC and rendered drawings checked.
- [x] Reconcile the source stackup sum to 1.600 mm while retaining 0.070 mm copper on both sides.
- [ ] Agree finished-thickness convention/tolerance in the actual quote and verify Essentra hole/panel-thickness engagement, including fabrication tolerance.
- [x] Add the controlled assembly drawing/notes, including GDT_AC's whole-span >=2.00 mm gap, 15.24 mm pitch, orientation and uncertainty-aware inspection method.
- [ ] Approve detailed forming tolerances/process and perform full COMBI 308 dry-fit with actual WAGOs, cable bends/glands, earth wires, supports, lid LEDs and screwdriver access. CAD/drawings do not replace physical fit.

**Exit:** Layout and library checks pass with genuine geometry. Part-fit evidence and the chosen via/solder process are either accepted or explicitly held for CAM, never assumed from DRC.

**Current exit: partial.** Checks pass for the actual corrected source, but final
protection placement depends on P2. Maximum-body F.Fab outlines are supported
for the diode, resistor and Bencent tube; the corrected KF128 courtyard still
uses a provisional body, and other maximum pins/bodies remain unknown. W1/W4
are explicit release holds; no supplier, solder, via or enclosure approval is
invented to close them.

### P4: Production Data

Files: `Makefile`, `pcb/BOM.csv`, `pcb/CPL.csv`, small export/validation helpers, generated `build/*`, assembly output sources.

- [x] Keep `pcb/BOM.csv` as reviewed sourcing data and validate exact schematic/PCB references, values, MPNs, manufacturers, LCSC codes, footprints and population. The derived current count remains 14; no protection additions are approved.
- [x] Generate CPL from native KiCad mm positions for all SMT/THT parts, excluding mechanical/DNP items. `pcb/CPL.csv` is a generated reference, refreshed only after complete file checks, never a second placement input.
- [x] Retain absolute Gerber/drill origin and native signed-Y placement; validate common coordinates and rotations modulo 360 without taking absolute Y.
- [ ] Verify every selected JLCPCB model's centroid and rotation. Native position output describes footprint placement origins, which must be checked against intended assembly centroids; document any anchor-to-centroid correction. Record only evidence-backed corrections, keyed clearly to the actual part/footprint. GDT_AC's internally vertical geometry and D1/D2's cathodes-right mapping must not be inferred from their old standard-looking footprint names. Do not move/rotate PCB pads to compensate for an import mistake.
- [x] Export copper, mask, legend, top paste, outline, separate PTH/NPTH drills and IPC-D-356 to fresh private scratch outputs. Customer F.Paste does not approve the assembler's processed stencil.
- [x] Validate actual exported geometry, drills, BOM/CPL, connectivity and ZIP payloads before publication. Quarantine stale outputs, preserve documented filenames, and block publication for any failure or open engineering hold.
- [x] Export native assembly PDF, placement text, coordinate-based via CSV and controlled engineering notes. Implement and test release-manifest revision/tool/source/artifact hashes and results; no generated files are hand-edited.
- [ ] Publish the real revision's manifest/package only after evidence-backed engineering holds are closed. Current private draft exports are not a published release; manifest publication was verified with isolated fixtures, not an approved hardware package.
- [ ] Obtain order-specific acceptance for 2 oz/ENIG mixed SMT/THT assembly, actual part allocation/attrition, heavy-copper soldering, and GDT lead forming. Current public guidance permits THT under both Economic and Standard in principle; verify the exact quote instead of asserting a universal service restriction.
- [ ] Approve manufacturer-added rails, fiducials, tooling, and depanelization without cuts/holes in protected functional copper. Standard PCBA's processing-size requirement may require panelization for this 63 x 56 mm board. Do not assume the old 73 x 76 mm panel or automatic rail removal, and distinguish five individual boards from five multi-up panels.
- [x] Provide exact coordinate-based identification of all 14 stitching vias in `pcb/ASSEMBLY.md` and generated `ViaTreatment.csv`, including required 1.00 / 1.80 mm geometry and no fill-by-diameter instruction.
- [ ] Obtain actual via-treatment/CAM acceptance, confirm protected drill sizes were not reduced, and agree any required minimum finished barrel copper separately. The published average is not a minimum guarantee; resistor insertion holes remain open.

**Exit:** Verified production data is generated reproducibly and is unambiguous for assembly. Bare-board flying-probe continuity is not advertised as assembled functional or surge testing.

**Current exit: tooling and checked drafts complete; final release held.**
Serial/parallel native geometry, population and connectivity match. Supplier
placement, CAM, panel, allocation and process approvals remain unchecked.

### P5: Documentation

Synchronize documents alongside the relevant implementation, then perform a final consistency pass. Keep user-confirmed purchases distinct from required quantities and proposed replacements.

- [x] `README.md`: correct counts, topology, model baselines, identities, actual DFM/build status and unsupported lifetime/surge claims; distinguish nominal, calculated and measured evidence.
- [x] `INSTALL.md`: replace legacy hub matrices with six independent ends, repair/retest, accurate OFF/fence-inactive labeling and safe DMM checks; correct LED torque, cable/core identification, gland/dry-fit/potting requirements and prohibit active green/yellow conductors.
- [x] `ORDERING.md`: use the five-assembled-board baseline, actual geometry and explicit remaining via/land/process holds, separate PCB CAM and placement approvals, quote-specific sourcing/panels and no unsupported stock/lead-time/sealing promises.
- [x] `ACCEPTANCE.md`: separate workmanship, normal DC, protected reversal, measured continuous thermal, 5 m daylight, full-hub cuts, enclosure/material, RF/site and qualified fault/surge tests; define instrumentation/uncertainty and retain an unpotted reference allocation.
- [x] `RISKS.md`: correct fuse/reversal analyses and include follow current, failed devices, unequal firing/residual voltage, PE/touch/step potential, coastal/solar/cable and 0.5 m / 300 m cattle-fence exposure, without unsupported ratings or guarantees.
- [x] `MATERIALS.md`: reconcile 41 stations / 82 LEDs / 164 supports / 123 splices, pending boxes/entries, prototypes/spares and PSU/switch candidates. Preserve orders of 80 LEDs / 160 supports / 120 splices; field-only shortfalls are 2 / 4 / 3 before extra samples or spares.
- [x] `LED.md`: explain the purchased no-resistor indicator, 20 mA / 5 V reverse limits and 5 m target; keep alternatives unqualified.
- [x] `AGENTS.md`: synchronize actual headless CLI, strict transactional build/rules/libraries, tested environment, cleanup/evidence ownership and physical/DFM invariants without unsupported ratings.
- [x] `REVIEW.md`: update the reusable audit template for the agreed prototype specification, distinct from this actual issue/evidence record.
- [x] Assign **1.2.0-dev** consistently to PCB/schematic, visible board identification, documents and revision-bound verification/manifest generation. Keep unresolved design/manufacturing/field holds explicit.

**Exit:** Documents agree with the actual remediated design and clearly separate file verification from hardware/site evidence.

**Current exit: met for the present development draft**, not an approved final
protection design. Repeat synchronization after any circuit/part/process change.

### P6: Validation

- [x] Run the stdlib tests and `make check` on the present circuit assumptions: **130 tests pass including native probes**, with 41 stations and all 280 clean-cut cases. Repeat after final protection integration; these results are not its unimplemented circuit's qualification.
- [x] Run separate clean `make all` and clean `make -j4 all`, preserve evidence, and compare validated geometry/connectivity/population with only documented metadata normalization. Both real builds correctly return nonzero solely for the five open holds; the comparison passes, not publication.
- [x] Exercise missing rules/project, wrong net, inadequate earth spacing, undersized diode hole, exposed via aperture, missing BOM/CPL part, reversed Y and missing layer fixtures, plus parser/export/race/staleness/diagnostic regressions. Invalid releases are blocked. Other THT maximum-pin fit remains an external evidence hold, not a claimed automatic fit check.
- [x] Inspect rendered PCB/schematic/assembly data and validate native-generated copper/mask/paste/legend/drill geometry and archives. Retain supported-geometry and rendering limitations with the reports.
- [ ] Review actual JLCPCB processed PCB/stencil and placement, including hole treatment, maximum-pin fit, forming/standoff and panel/tooling locations, before production approval.
- [ ] Perform basic workmanship, value/polarity, and normal-function acceptance on all five prototypes. Allocate appropriate units to protected-reversal, full-hub cut, continuous potted thermal, enclosure-fit, and potentially destructive protection tests while retaining an unpotted reference. Inspect both source-end and reduced-voltage far-end conditions; seek approval for additional samples if the qualification program needs them.
- [ ] Test the actual indicators at 5 m in full daylight, at the final minimum expected current and real viewing angles. Confirm OFF is not confused with sunlit lens colour. Prefer optical improvements before increasing current; any alternative LED or resistor change needs renewed electrical/thermal/fit checks and procurement approval.
- [ ] Qualify RUN with the actual cable, fence construction/height, transmitter, and test receiver. Compare cattle-energizer off/on at the specified routing exposure; check unintended receiver responses, lost boundary field, misleading LED indications, repetitive protection stress, and recovery in both RUN and TEST.
- [ ] Complete the defined source-fault/surge recovery and discharge-path qualification with appropriate equipment and expertise. Do not use ordinary DMM/grounded-scope practices as an improvised high-voltage test method. Verify installation earthing with the qualified installer and applicable OEM/regional requirements.
- [ ] Retain one unpotted golden/reference sample, record per-board results and exact parts/process revision, and update issue closure with evidence. Passing basic bench tests alone does not authorize the full perimeter rollout.

## Release Gates

**Current disposition: A, B and C remain HELD.** Passing `make check` is a
file-level result, not Gate A closure: the circuit/protection/part decisions
are unfinished. `pcb/verification.json` blocks every public export/package
alias for **C4, C5, W3, W1 and W4**, with no override. C2/W5 and the broader
supplier/hardware/site evidence remain tracked even though they are not separate
machine hold IDs. No current `build/manifest.json` or public order ZIP is issued.

| Gate | Required evidence | What it does not mean |
| :--- | :--- | :--- |
| **A: File ready** | Source/library/rule consistency, correct hub/circuit design, passing automated checks, regenerated and reviewed BOM/CPL/fabrication data, synchronized documentation, explicit open qualification items. | Not CAM acceptance, physical fit proof, or field qualification. |
| **B: Prototype order** | Gate A plus required part/fit/process/placement/CAM acceptance and a defined, controlled prototype test scope. Known diode-hole/CPL/wicking defects must not be silently accepted as "the prototype will test it." | Not permission to rely on the prototypes for lightning protection or containment before qualification. |
| **C: Field release** | Required normal/fault/reversal/thermal/visibility/RF/site/protection evidence, accepted earthing, verified installation materials, and documented performance limits for the intended use. | Not an untested 20 kA board rating, direct-strike protection, or multi-decade warranty. |

Prototype hardware is needed for some qualification, so Gate B may precede those physical tests when their scope and restrictions are explicit. Never close C4/C5 or surge/environmental performance solely by changing wording. Conversely, do not call every missing qualification a demonstrated certain hardware failure.

The build's success message should mean **"manufacturing data verified for this revision"**, not **"20 kA lightning protection verified."**

## External Evidence

These are evidence-gathering tasks, not reasons to reopen settled feature decisions:

- [ ] Confirm actual PSU nameplate, selected upgrade if any, and the installed output setting/limits.
- [ ] Obtain the exact switch contact development, DC breaking suitability, global transfer sequence, mounting details, and applicable insulation conditions. General CA10 data qualifies DC switching capacity by function; the A362 changeover must be checked specifically.
- [ ] Obtain exact component drawings/tolerances, verify connector pin fit and body envelopes, and record the accepted forming/solder process.
- [ ] Confirm the actual Oceanflex cable/reel identity, colours, maximum resistance, long-term exposed-weather/UV and wet-conduit suitability, and insulation/impulse data. Its 60 V operating rating is not by itself a surge-withstand rating or proof of failure at every brief higher voltage.
- [ ] Confirm the actual MP0100 formulation, mixing/cure process, compatibility/cleanliness requirements, and the assembled environmental acceptance scope. Do not conflate a related product/formulation with the ordered material.
- [ ] Obtain JLCPCB's exact quote, part allocation/attrition, panel/rail plan, via treatment, relevant barrel-copper minimum, and processed PCB/stencil/assembly acceptance.
- [ ] Record actual cattle-energizer pulse characteristics and routing used for qualification. The user has already supplied 0.5 m minimum separation and up to 300 m parallel exposure; do not ask for those again unless the routing changes.
- [ ] Obtain the site-specific earthing/bonding review and required physical qualification results. Do not copy US outlet-faceplate grounding instructions directly into an Isle of Man installation.

## Source Links

Specifications were researched on 2026-09-06; recheck revisions and order-specific capabilities. Public stock is not a purchase allocation. Prefer primary manufacturer/fabricator sources and retain accepted evidence with the release.

- [JLCPCB fabrication capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [via covering](https://jlcpcb.com/help/article/pcb-via-covering), and [via versus pad-hole tolerance](https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes).
- [JLCPCB PCBA capabilities](https://jlcpcb.com/capabilities/pcb-assembly-capabilities), [placement-file requirements](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly), [stencil-data preparation](https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders), and [assembly terms](https://jlcpcb.com/help/article/Terms-and-Conditions-of-JLCPCB-Assembly-Service).
- [onsemi 1N4007 family datasheet](https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf) and [C232439 identity](https://www.lcsc.com/product-detail/C232439.html). Reviewed drawing maximum lead: 0.86 mm. Reconcile other ratings with the actual revision, including temperature limits and the meaning of ordering suffixes.
- [Vishay MBE0414 family datasheet](https://www.vishay.com/docs/28766/mbxsma.pdf), including derating, mounting dimensions, and pulse curves.
- [Ruilon SMD5050-470NA](https://www.lcsc.com/datasheet/C39692533.pdf), [Ruilon 2R470TD-8](https://www.lcsc.com/datasheet/C2836978.pdf), and [Bencent B5G470L](https://www.lcsc.com/datasheet/C5337217.pdf) manufacturer documents distributed through LCSC.
- [KF128-7.62-3P](https://www.lcsc.com/datasheet/C474957.pdf) and [KF129-5.08-2P](https://www.lcsc.com/datasheet/C475092.pdf) drawings; verify maximum finished pin dimensions, not only linked CAD land patterns.
- [APEM Q10F5SXXSG02E](https://www.apem.com/led-indicators/professional-grade-panel-mount-led-indicators/q10/q10f5sxxsg02e): no-resistor option, 5 V reverse limit, 20 mA family maximum, model-dependent viewing/torque data, and -40 to +85 degrees C temperature range.
- [WISKA COMBI 308 LG](https://www.wiska.co.uk/en/30/pde/10060400/combi-308-lg.html): external 85 x 85 x 51 mm, -30 to +100 degrees C, IP66 via membrane and IP67 with the specified gland arrangement. These are not automatic ratings for the modified/potted assembly.
- [Essentra support listing](https://www.digikey.com/en/products/detail/essentra-components/LCBSBM-6-01A-RT/392198): nominal 3.18 mm support hole, 1.57 mm panel, 9.53 mm spacing. Obtain the applicable dimensional/tolerance drawing for final acceptance.
- [LRS-35 datasheet](https://www.meanwell.com/Upload/PDF/LRS-35/LRS-35-SPEC.PDF) and [LRS-75 datasheet](https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF).
- [Kraus & Naimer catalogue, centre-off functions](https://flippingbook.krausnaimer.com/KN100GB/11/), [CA10 data](https://www.krausnaimer.com/fileadmin/user_upload/Kraus_u_Naimer/PDFs/ElecData/Switches/Dynamic/english/CA10_EN.pdf), and [custom configuration service](https://www.krausnaimer.com/gb_en/products/customized-switches).
- [Littelfuse 217 fuse data](https://www.littelfuse.com/assetdocs/littelfuse-fuse-217-datasheet?assetguid=af55be94-c42e-41b1-ad43-e070e09443fe).
- [Oceanflex cable supplied by 12 Volt Planet](https://www.12voltplanet.co.uk/CAB3CTNTW2.5PNT.html) and [AMC manufacturer](https://www.automarinecables.com/). Manufacturer web navigation did not provide the missing product-specific data during the review; absence from the retrieved listing is not proof that the manufacturer cannot supply it.
- [DogWatch SmartFence owner's guide](https://www.dogwatch.com/wp-content/uploads/2026/06/SmartFence_OwnersGuide_Rev.E.1-06.26.pdf), especially installation/protector/grounding information. Obtain applicable regional instructions and approval for the actual nonstandard boundary configuration.

## Session Handoff

At the end of each implementation session, record the work-package IDs touched, changed files, exact verification commands/results, unresolved evidence, and the next bounded task. Preserve the distinction between implemented, file-verified, CAM-accepted, and physically qualified. Do not silently lower a requirement to obtain a PASS.

| Date | Session result | Next task |
| :--- | :--- | :--- |
| 2026-09-06 | Review, requirements clarification, DFM policy, and this handoff plan prepared. No PCB/schematic/build remediation implemented; P1-P6 remain unchecked. | Start P1: complete-project staging, report/gate reliability, and regression-check foundations. P2 protection analysis may proceed independently. |
| 2026-09-06 to 2026-09-07 | Implemented P1, bounded P2/P3, P4 tooling/drafts, P5 and automated P6 with focused parallel ownership. Retried interrupted electrical/layout agents, integrated their work, and corrected independent audit findings with negative/native fixtures. Final native suite: 130 PASS; `make check` PASS with exact reviewed warnings and five visible release holds. Clean serial/parallel builds both refuse publication and their checked data matches. No hardware/CAM qualification, commits, uploads or orders. | Obtain bounded P2 LED/clamp/pulse and GDT holdover/source evidence before circuit selection. In parallel obtain P3 maximum-pin/body and SMT-pattern/process acceptance. Then integrate approved protection and rerun every affected gate. |

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

### Next Bounded Work

1. **P2, C4/W3:** obtain exact purchased APEM SG I/V/temperature/pulse bounds and
   clamp leakage/voltage envelopes, decide a pulse-safe one-way branch design,
   and establish the enforceable source setting/thermal envelope. Candidate
   circuitry in ELECTRICAL.md is not authorization to populate it.
2. **P2, C5/W2:** obtain actual PSU nameplate/output-C/hiccup data and GDT
   holdover test networks; choose a proved extinction/fault-containment or
   shutdown architecture. The sub-rated fault cases rule out assuming a simple
   2 A fuse or PSU upgrade solves every case.
3. **P3, W1/W4/W5, parallel with P2 evidence:** obtain maximum finished THT pin
   envelopes and body/forming tolerances; resolve the Ruilon land drawing or
   written alternative acceptance, KF128 overhang, via and heavy-copper process,
   supports and COMBI dry-fit. Do not infer these from stock CAD or DRC.
4. After a reviewed circuit/part/process decision, update actual source/BOM/
   libraries/notes, regenerate/check CPL and fabrication data, repeat the
   relevant automated/native checks and controlled supplier/hardware tests,
   and close only evidence-backed issues/gates. No order/upload/commit is
   authorized by this handoff.

Suggested instruction for a new implementation session:

```text
Read AGENTS.md and REMEDIATION.md, inspect the current worktree, and implement
the first unfinished work package (or the package I specify). Preserve existing
changes and physical guardrails. Use the settled 41-station, same-end-return,
continuous-safe TEST baseline; do not add a direction selector. Verify the work,
update the plan/session log with evidence and remaining blockers, and do not
place orders or commit changes unless requested.
```
