# Remediation Plan

Prepared: 2026-09-06. Reviewed hardware baseline: v1.1.0.
Implementation handoff: **2026-09-07, hardware 1.2.0-dev**.

**Status: the minimal-change 16-part PR02/BYG23T hybrid is implemented after checkpoint ad282e3; integrated verification results are recorded in the current handoff. Powered-GDT/source protection, actual thermal/transient performance and part/process acceptance are NOT complete. Manufacturing and field release remain on hold.**

This is the starting context and implementation checklist for subsequent sessions. It consolidates the review and the user's later decisions, including changes to the originally proposed TEST wiring. It is not manufacturing approval, a completed hardware test report, or a board-level lightning certification.

## Start Here

1. Read [AGENTS.md](AGENTS.md) for operating instructions and physical guardrails, then this file. Read the relevant source files before editing them.
2. Inspect `git status` and the existing diff. Preserve all work already present. At the user's request the prior remediation/scope state was committed as **ad282e3**, before hybrid implementation. The current hybrid changes are not committed. Historical preparation edits/archives and unrelated `tmp/` evidence must not be reverted or cleaned indiscriminately. See the current handoff for preserved build evidence.
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
| P2 | **16-part PR02/BYG23T circuit implemented**, preserving one-way rungs, six-end TEST and the original GDTs. Selected-part TCR, diode/drop/leakage screens and explicit procurement data are in the source/model. Cattle fencing is prohibited near the whole boundary. | Actual negative-clamp/RF/ordinary-transient response, C5 powered recovery/fault containment, the accepted source/thermal envelope and A364 DC/global-transfer approval remain open. The 40-part active candidate is not a prerequisite. |
| P3 | Original part figures read; metric SMT lands, untented vias, resized PTHs and honest body/courtyard envelopes implemented; minimum-pin and native open-via checks added without disturbing guardrails. | Allocated-lot E/pattern acceptance, KF129 variant, SMT metric/inch clarification and actual forming/solder/stencil approval, 1.30 mm tolerance-budgeted earth-terminal overhang, enclosure/support fit and final P2 placement. |
| P4 | Reproducible, validated private draft exports; native signed-Y mixed-assembly CPL; population/net/drill/archive checks; manifest implementation and release holds. | No current published release. Exact assembler centroids/rotations, CAM/stencil, quote/allocation, panel and process approvals remain open. |
| P5 | All nine main guides updated for the actual 1.2.0-dev draft, truthful claims, preserved purchases and separate acceptance categories. | Resynchronize after any future circuit/part/process decision; documents are not approval. |
| P6 | **198 tests PASS including native probes**, hybrid `make check` PASS, manually reviewed fresh annotation evidence, clean serial/parallel comparison and schematic/assembly render inspection. See Hybrid Implementation below; earlier 130/159-test results are historical. | Actual processed CAM, allocated parts, assembled-prototype acceptance, selected protection/recovery, thermal/visibility/RF/site tests and earthing approval are **not performed**. |

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
| PSU | **Two MEAN WELL LRS-75-36 are ORDERED**, each 36 V / 2.1 A / 75.6 W. User allocation: **one for TEST, one disconnected spare**. No parallel, series, opposite-end or separate-channel connection. Receipt/nameplates, installed setting/limits and fault behavior still need verification. Preserve the earlier LRS-35 belief as history, not a third confirmed supply or a C5 solution. |
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
| Simplified design direction | User authorized the **16-part hybrid**, now implemented with 2 W axial PR02 and four SMA BYG23T diodes (two series replacements, two negative shunts). Existing takeoffs, resistor/series-diode centres, rails/vias, B returns and LED terminals stay; **no fold or new vias**. Hardware/transient/thermal approval is not implied. |
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

The current board has **16 electrical components, all on top: six SMT and ten THT**, plus four mechanical hole footprints. Eight nets contain 34 component terminals; expected drills are 22 component PTH +14 vias and four NPTH. Native evidence, not these design counts alone, controls file verification.

| References | Baseline MPN / sourcing code |
| :--- | :--- |
| D1-D4 | **Vishay General Semiconductor BYG23T-M3/TR / C145454**. 1300 V SMA; series D1/D2 and negative shunts D3/D4. The old onsemi THT diodes are retired. |
| R1, R2 | **Vishay BCcomponents PR02000202201FA100**, 2.2 kohm, 2 W copper-lead, 1%, +/-250 ppm/K. **External sourcing, no verified LCSC code**; BOM/source reference is the exact manufacturer inventory URL. C1368610 belongs to the retired MBE and must not be reused. |
| GDT_AB, GDT_BC | Ruilon SMD5050-470NA / C39692533. |
| GDT_AC | Bencent B5G470L / C5337217. |
| GDT_A_E, GDT_B_E, GDT_C_E | Ruilon 2R470TD-8 / C2836978. |
| J_IN, J_EARTH | Cixi Kefa KF128-7.62-3P / C474957. |
| J_LED_A, J_LED_C | Cixi Kefa KF129-5.08-2P / C475092. |

The external baseline includes APEM Q10F5SXXSG02E indicators, Essentra LCBSBM-6-01A-RT supports, WAGO 221-613 splices, and **WISKA OneGel**. The existing hub fuse is specified as Littelfuse 0217002.MXP in Phoenix Contact UK 5-HESILED 60 / 3004139. Verify exact supplied items and ratings before design freeze. Historic inventory counts are not allocations for the new order. [Environment/hub evidence](pcb/ENVIRONMENT_EVIDENCE.md) records the corrected product documents and their actual conflicts.

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
| C1 | Former onsemi D1/D2 0.90 mm holes were too small and manufacturer attribution was wrong. | **Historical defect corrected, then retired by reviewed SMT conversion.** Checkpoint ad282e3 retains the 1.10/2.20 correction and controlling-inch proof. Current D1-D4 are SMA, with no insertion holes; exact land/polarity/process checks now apply. |
| C2 | Former hand-maintained CPL had positive screen Y; custom axes/polarities differ from stock-looking names. | **Coordinate-generation correction retained for all 16 parts:** native signed Y, absolute origin and rotations modulo 360. D1/D2 cathodes east; D3/D4 cathodes west. **OPEN:** actual assembler centroid/model rotation approval. |
| C3 | Legacy End A/C common Pin 8 backfed breaks; earlier B-return proposals masked required cuts. | **Functional/software correction implemented:** six-end matrix, all 280 clean-cut cases, repair/retest and both legacy negative controls pass. **OPEN:** actual switch DC/global-transfer approval and full-hub physical tests. |
| C4 | Series isolation alone did not guarantee LED reverse voltage; a shunt still does not regulate forward pulse current. | **SIMPLE CIRCUIT IMPLEMENTED; performance hold remains.** D3/D4 BYG23T negative shunts are fitted in the design after D1/D2. Installation-polarity LED damage is accepted. 75 ns reverse recovery is not forward-clamp speed; typical 9 V forward recovery under the datasheet's high-current test is not <=5 V LED proof. Qualify actual RF/ordinary-switching/nearby transient scope; do not require the prohibited cattle-fence configuration or the historical 40-part circuit. |
| C5 | The 2 A fuse need not clear cable-limited faults; powered GDT holdover/extinction is unqualified. | **OPEN DESIGN HOLD.** New-topology fault screens and actual published PSU/fuse limits replace the old fuse-blow claim. A modeled far-end 10 V arc draws 0.259543 A / 2.602168 W in its path with only 0.979810 A total. Select a supported protection/shutdown architecture and obtain actual powered-recovery evidence. |
| W1 | Former nine rail-via holes overlapped all four SMT GDT apertures by 0.19 mm; 1.00 mm reliable covering was unsupported. | **FILE CORRECTION IMPLEMENTED; order/process hold remains.** Selected metric 5.50 x 1.20 lands at +/-2.00 and X=119.50 give **1.239713 hole / 0.839713 annulus gaps**. All fourteen vias are now standard untented, no fill/plug/cap. Original X1 leader is resolved; printed 4.00 mm versus 0.165-inch contradiction, processed stencil/profile and retained drill acceptance remain specific supplier facts. |
| W2 | DC sparkover, component impulse ratings, heavy copper and parallel pins do not establish transient clamp limits, sharing or a board rating. | **Claims corrected; qualification OPEN.** No assembled surge/current/lifetime rating is assigned. Coordinate the actual protection/cable/earth paths and complete defined transient and recovery tests. |
| W3 | Nominal 0.50 W/resistor and a wattage label do not prove closed-OneGel temperature or continuous safety. | **2 W PR02 IMPLEMENTED; thermal hold remains.** Its actual 250 ppm/K / 1% / 125 C resistance screen gives **0.769433 W/resistor at 40.39597 V**, below 2 W P70 but not a measured temperature. Require >=1.00 body standoff, an accepted real source envelope and instrumented closed/solar duty evidence. PR02 ambient derating and 220 C hot-spot limit are not allowable gel/cable temperatures. |
| W4 | Original connector/earth-GDT holes lacked tolerance margin; part/process and sourcing acceptance remain incomplete. | **BOUNDED FILE DESIGN IMPLEMENTED; lot/fit/procurement hold remains.** KF128/KF129 2.00; PR02/B5G 1.40; earth GDT 1.50 mm, retained THT pad centres and minimum ring 0.40. PR02's actual maximum lead is 0.83; forming/standoff, E/pattern lot inspection and solder fill remain to accept. J_EARTH needs **1.00 nominal / 1.30 budgeted overhang**. PR02 has explicit external sourcing, not assigned LCSC inventory or JLCPCB allocation. |
| W5 | Former LED torque was too high; complete enclosure fit and raised GDT geometry were unproven. | **Instructions/drawing corrected:** 0.20-0.25 Nm subject to exact APEM model; controlled whole-span >=2.00 mm overpass drawing and inspection method. **OPEN:** accepted forming tolerances, Essentra thickness fit, COMBI dry-fit and material/process tests. |
| W6 | Legacy legend, incomplete checks and inconsistent libraries/metadata undermined verification. | **File-level correction verified:** native 1.00/0.15 legend, strict effective rules, ten local footprints/six symbols, matched BOM metadata, DRC/parity/geometry and regression checks. Reviewed warnings remain visible and narrowly bound; no project severity ignores or exclusions. |
| W7 | Legacy fault, RF, earthing, environmental/lifetime and five-board sign-off claims were overstated. | **Scope/documentation corrected.** PSU allocation, cable identity/colours, OneGel identity and A364 program family resolved. Entire-boundary energized-cattle fencing is prohibited; verify/maintain that restriction rather than qualify the withdrawn parallel run. **OPEN:** actual source/switch approval, cable/environmental applicability, OneGel/thermal conflicts, RF, earthing and physical qualification. |

The source stackup now totals 1.600 mm (1.440 core + two 0.070 copper + two
0.010 mask layers), and underside references/revision identification are added.
Supplier thickness convention/tolerances, retaining an actual unpotted reference,
and manufacturer-added panel rails/fiducials/tooling still require acceptance.

## Implementation Sequence

**P1 is implemented; maintain it only for actual geometry/tool changes. Remaining P2/P3 evidence can proceed in parallel. P3 final placement/BOM needs a supported P2 decision. P4 follows the final layout, P5 accompanies changes, and P6 verifies the resulting release.**

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
- [x] Record the user's acceptance of LED damage from accidental installation polarity errors. Reversed flying-lead survival is no longer a required feature; correct polarity, spare allocation and safe replacement remain installation controls.
- [x] Implement the simple 16-part circuit: PR02 resistors and BYG23T series/negative-shunt diodes. Preserve the one-way branch topology and no field soldering; actual pulse/clamp response and light output remain qualification, not implied forward-current regulation or reversed-lead immunity.
- [ ] Select actual parts using maximum clamp voltage, leakage, temperature/tolerance, and pulse/current data, not just a nominal TVS/zener voltage. Check LED forward pulse current as well as reverse voltage. A voltage clamp alone is not automatically adequate forward-current protection. Recheck fault observability after any circuit change: preserve or explicitly model one-way rung behavior, rather than using the old forward-only model to validate a bidirectional replacement.
- [ ] Coordinate the primary GDTs, indicator branches, source interface, and any secondary protection. Reviewed impulse sparkover at 1 kV/us is up to 950 V for SMD5050-470NA and 1100 V for 2R470TD-8; B5G470L's 850 V figure is specified for 99% of measured values. Include lead overshoot and the cable's unverified impulse withstand.
- [x] Implement hard/resistive-short and conditional 10/15 V ignited-GDT load-line screens in the new topology, including separate earth paths and every station for inter-core faults. Explicitly distinguish CV demand from actual PSU overload/hiccup current and GDT holdover.
- [ ] Complete the actual PSU/cable/GDT dynamic and failed-device analysis, and implement a coordinated protective/shutdown arrangement. Do not infer extinction from sparkover, holding current from glow-to-arc figures, or discrimination from a reduced fuse value alone.
- [x] Remove `BLOWS (>2A)` from analysis logic. Use published Littelfuse 217 DC interruption/opening conditions and Mean Well current/power/overload envelopes; leave unmeasured hiccup and clearing times unknown. Recalculate faults for the new wiring.
- [ ] Qualify continuous resistor/LED/connector temperatures over the actual supply range. Selected PR02000202201FA100 is copper-lead 2 W, 1%, +/-250 ppm/K; the 40.39597 V / 125 C resistance screen is **0.769432871 W/resistor**, not a measured temperature. Verify mounting/standoff, body/lead and material interfaces; neither P70 rating margin nor the retired MBE modes qualify current closed-OneGel duty.
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

### P3: PCB DFM

Files: `pcb/pcb.kicad_pcb`, schematic footprint assignments, project-local libraries/tables, `pcb/pcb.kicad_pro`, `pcb/pcb.kicad_dru`, controlled assembly/fit notes under `pcb/`.

- [x] Create project-local definitions for intentional geometry: ten footprints and six symbols. Preserve global pad/net mappings through migration, including distinct LED connectors and the cathode-right diode. Deliberate DFM relocations are recorded separately in `pcb/ASSEMBLY.md`.
- [x] Historically correct the onsemi hole/identity defect, then replace D1/D2 with reviewed SMA BYG23T in the hybrid. No current diode PTH remains; current source/native gates check the exact SMA pad/net/polarity geometry.
- [ ] Accept actual allocated finished leads, body datums and pin patterns against the adopted drawing/E limits, including plating/burrs and forming uncertainty. KF128/KF129 now use 2.00 mm holes, not an unselected 1.60 mm CAD suggestion. Missing manufacturer maxima are not closed by an unperformed lot inspection.
- [x] Read the original pin/body/SMT figures; resolve the earth-GDT 1.05 maximum and real KF129 drawing conflict. Define explicit conservative E/pattern procurement envelopes for missing maxima, separately from actual lot acceptance.
- [x] Implement bounded component-hole sizes, independent position budgets and body/courtyard envelopes, preserving THT pad centres, mapping, rails and vias. Minimum nominal ring is 0.40 mm. D1-D4 now have SMA lands, not PTH forming; PR02/GDT forming and standoff still require acceptance.
- [x] Apply selected hole/position budgets, >=0.10 mm residual diametral allowance and >=0.254 nominal rings; recheck exported holes/copper/edges. Actual part-pattern, resistor/GDT forming and SMA land/polarity/stencil/solder acceptance remain separate. Never repair insertion by reaming PTHs.
- [x] Rebuild body/F.Fab and courtyard envelopes with pose/assembly clearance, including the diode courtyard correction found in review. No protected placement changes or courtyard trimming.
- [ ] Accept actual rework/screwdriver access and the inspected body/forming projections; drawing clearance is not physical access proof.
- [x] Retain the collision-removing GDT_AB/BC X=119.50 and GDT_AC X=125.80 relocation, all nine rail vias and full-width copper. The continuation replaces the former lands with **5.50 x 1.20 mm, 4.00 mm centres**; full drill-circle/annulus/mask/paste separation is checked.
- [ ] Follow the selected GDT land pattern and obtain solder-volume/thermal-process acceptance. If no compliant solution preserves the protected geometry, obtain explicit design/process approval rather than shrinking vias or assuming 1 mm resin filling is standard.
- [x] Implement the visually resolved metric SMD5050 pattern (5.50 x 1.20, 4.00 centres) and standard untented 1.80 mask openings on both sides. Keep the inch discrepancy and actual solder/CAM acceptance open; no fill exception or guardrail change is needed.
- [ ] Place/route the selected protection parts, then revalidate all nets, surge clearances, symmetry requirements, and component-fit evidence. Do not narrow surge connections with generic thermal-relief spokes simply to ease soldering; agree a suitable heavy-copper soldering process.
- [x] Correct legend height/stroke/clipping using native 1.00 / 0.15 mm text. Retain polarity, cathode and A/B/C/EARTH labels; add underside references, F.Fab aids and 1.2.0-dev identification. Native DRC and rendered drawings checked.
- [x] Reconcile the source stackup sum to 1.600 mm while retaining 0.070 mm copper on both sides.
- [ ] Agree finished-thickness convention/tolerance in the actual quote and verify Essentra hole/panel-thickness engagement, including fabrication tolerance.
- [x] Add the controlled assembly drawing/notes, including GDT_AC's whole-span >=2.00 mm gap, 15.24 mm pitch, orientation and uncertainty-aware inspection method.
- [ ] Approve detailed forming tolerances/process and perform full COMBI 308 dry-fit with actual WAGOs, cable bends/glands, earth wires, supports, lid LEDs and screwdriver access. CAD/drawings do not replace physical fit.

**Exit:** Layout and library checks pass with genuine geometry. Part-fit evidence and the chosen via/solder process are either accepted or explicitly held for CAM, never assumed from DRC.

**Current exit: bounded file design implemented, supplier acceptance partial.**
Original figures are resolved, metric lands and standard untented processing
are selected, and source/library hole/body envelopes are explicit. Unknown
guaranteed maxima are controlled by declared E/pattern lot limits, not guessed
to be manufacturer specifications. Actual lot acceptance, forming/solder fill,
metric/inch clarification, processed CAM and COMBI/support fit remain W1/W4/W5
evidence. Final protection placement still depends on P2.

### P4: Production Data

Files: `Makefile`, `pcb/BOM.csv`, `pcb/CPL.csv`, small export/validation helpers, generated `build/*`, assembly output sources.

- [x] Keep `pcb/BOM.csv` as reviewed sourcing data and validate the **16-part** population and exact identities. PR02 uses explicit `Sourcing=External`, empty C-code and source-matched HTTPS reference. File metadata checks do not verify allocation; unresolved external rows independently block publication even if engineering holds are closed.
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

- [x] Run stdlib/native tests and `make check` on the implemented circuit assumptions: **130 tests passed at checkpoint 97e202d**; the continuation adds fit/via/analysis and controlled-note regressions, with exact results in its handoff below. Repeat after final protection integration; none qualifies an unimplemented circuit.
- [x] Run separate clean `make all` and clean `make -j4 all`, preserve evidence, and compare validated geometry/connectivity/population with only documented metadata normalization. Both real builds correctly return nonzero solely for the five open holds; the comparison passes, not publication.
- [x] Exercise missing rules/project, wrong net, inadequate earth spacing, undersized diode hole, exposed via aperture, missing BOM/CPL part, reversed Y and missing layer fixtures, plus parser/export/race/staleness/diagnostic regressions. Invalid releases are blocked. Other THT maximum-pin fit remains an external evidence hold, not a claimed automatic fit check.
- [x] Inspect rendered PCB/schematic/assembly data and validate native-generated copper/mask/paste/legend/drill geometry and archives. Retain supported-geometry and rendering limitations with the reports.
- [ ] Review actual JLCPCB processed PCB/stencil and placement, including hole treatment, maximum-pin fit, forming/standoff and panel/tooling locations, before production approval.
- [ ] Perform basic workmanship, value/polarity, and normal-function acceptance on all five prototypes. Allocate appropriate units to protected-reversal, full-hub cut, continuous potted thermal, enclosure-fit, and potentially destructive protection tests while retaining an unpotted reference. Inspect both source-end and reduced-voltage far-end conditions; seek approval for additional samples if the qualification program needs them.
- [ ] Test the actual indicators at 5 m in full daylight, at the final minimum expected current and real viewing angles. Confirm OFF is not confused with sunlit lens colour. Prefer optical improvements before increasing current; any alternative LED or resistor change needs renewed electrical/thermal/fit checks and procurement approval.
- [ ] Qualify RUN with the actual cable, fence construction/height, transmitter and receiver; check unintended responses, lost field, misleading indications and normal switching/recovery. Verify and maintain **no energized cattle fence near the entire boundary/stations/hub**. Do not require the withdrawn energizer-on comparison unless a future approved land-use/design change reintroduces that exposure.
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

- [x] Confirm user procurement/allocation: two LRS-75-36 ordered, one TEST and one disconnected spare. No dual-source connection.
- [ ] Inspect received PSU nameplates and establish the installed output setting/limits and dynamic fault behavior.
- [ ] Obtain the exact CA10.A364/current WAA364 order-specific contact development, DC breaking suitability, global transfer sequence, mounting details and insulation conditions. Eight-pole static catalogue identification is resolved; physical numbering and application approval are not.
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

| Date | Session result | Next task |
| :--- | :--- | :--- |
| 2026-09-06 | Review, requirements clarification, DFM policy, and this handoff plan prepared. No PCB/schematic/build remediation implemented; P1-P6 remain unchecked. | Start P1: complete-project staging, report/gate reliability, and regression-check foundations. P2 protection analysis may proceed independently. |
| 2026-09-06 to 2026-09-07 | Implemented P1, bounded P2/P3, P4 tooling/drafts, P5 and automated P6 with focused parallel ownership. Retried interrupted electrical/layout agents, integrated their work, and corrected independent audit findings with negative/native fixtures. Final native suite: 130 PASS; `make check` PASS with exact reviewed warnings and five visible release holds. Clean serial/parallel builds both refuse publication and their checked data matches. No hardware/CAM qualification, commits, uploads or orders. | Obtain bounded P2 LED/clamp/pulse and GDT holdover/source evidence before circuit selection. In parallel obtain P3 maximum-pin/body and SMT-pattern/process acceptance. Then integrate approved protection and rerun every affected gate. |
| 2026-09-07, continuation from 97e202d | Confirmed one TEST PSU plus one disconnected spare and actual reel markings/colours; corrected OneGel and A364/WAA364 evidence. Implemented bounded P3 holes/body/courtyards, metric SMT lands and standard untented vias, preserving guardrails. Added conditional nonuniform cable/thermal analysis and precise negative protection findings. **159 tests PASS including native; final `make check` PASS; clean serial/parallel comparison PASS with publication correctly refused.** No protection circuit/BOM substitution, approval-hash refresh, supplier/hardware approval, commit, upload or order. | **P2 remains incomplete.** Resolve the specific current/clamp ordinary-duty and pulse gaps, powered fault containment, completed source interface and thermal evidence in the next bounded work below. P3's remaining work is actual lot/process/fit acceptance, not rereading supposedly inaccessible figures. |
| 2026-09-07, user simplification decision | User accepts installation-polarity LED damage and direct-strike rebuilding, but reaffirms continuous-safe normal TEST and has not waived ordinary/nearby transient damage. Narrowed C4 records and removed mandatory reversed-flying-lead immunity. Read-only agents assessed 16-part placement/folded routing and real 2 W axial/SMT resistor options; the blocked resistor agent resumed after the user resolved credits. **No PCB/schematic/BOM/library change in this step.** `TMPDIR=/tmp/opencode make test`: 159 discovered, 153 pass/six native skips; `make check` PASS with the same five holds; whitespace checks PASS. | Develop the simple candidate in ELECTRICAL section 9, not the historical 40-part circuit. Exact clamps/resistor and thermal/pulse scope remain to select. Existing geometry remains file-checked, not a fitted 16-part or thermally qualified design. |
| 2026-09-07, authorized hybrid implementation | **Committed checkpoint ad282e3 first**, covering all 36 relevant prior files, then implemented the PR02/BYG23T 16-part hybrid with focused ownership. User confirmed energized-cattle fencing is prohibited near the entire cable/stations/hub. **198 tests PASS including native, `make check` PASS, clean serial/parallel refusal/comparison PASS**. Reviewed fresh numbering/invalid-reference probes and deliberately updated only the changed schematic approval hash/rationale; no automatic refresh or hardware approval. All five holds and unresolved PR02 external allocation remain. Hybrid changes are **uncommitted**; no push/upload/order. | Qualify the implemented simple circuit and actual continuous thermal/recovery behavior, resolve PR02 allocation and order-specific fit/process/CAM. Do not restart P1, reintroduce the withdrawn cattle-fence test or require the historical 40-part circuit. |

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

### Next Bounded Work

1. **C4/P6:** qualify the **implemented two-shunt hybrid** at actual LED terminals
   for normal RUN/TEST/switching and an explicitly defined nearby-transient
   scope. Record forward/reverse peaks, recovery/ringing and usable 5 m light
   at the accepted minimum current. Do not confuse reverse recovery with forward
   clamp response or require the historical 40-part circuit by default. No
   reversed-flying-lead survival or prohibited cattle-fence test is required.
2. **P2, C5/W2:** use the now-resolved K.12 **135 V / 1300 ohm** network rather
   than re-researching its headline voltage. Obtain application/type-test
   recovery evidence for the actual compact tubes, or develop the genuinely
   DC-power-rated TDK stack's mechanical/RF solution. Any necessary guardrail
   change requires user approval. Complete hazardous resistive-fault containment
   and the real hub current/OV/latch/isolation/transient circuit; a larger PSU,
   2 A fuse or 62 V eFuse alone is not that circuit.
3. **W3/P6:** verify actual source setting/range and closed-OneGel temperatures
   with the selected PR02 mounted >=1.00 above the PCB, including upper-source,
   hot/solar and output-short cases. The **0.769433 W** current screen is not a
   temperature measurement; the old 37 V/MBE figures are historical. A passive
   design covering the normal source range is an alternative to a new cutoff.
   Resolve OneGel process/temperature conflicts; healthy TEST cannot use a timer
   as its baseline safeguard. A364's exact DC/global-transfer approval stays open.
4. **P3/P4, W1/W4/W5:** resolve **PR02000202201FA100 external sourcing/private
   inventory**, without guessed C-codes. Retain adopted SMA/metric GDT lands,
   untented process and hole/body envelopes. Obtain allocated-lot E/pattern and
   KF129-variant acceptance, Ruilon's metric/inch clarification, actual stencil/
   solder/PR02-and-GDT forming/CAM evidence and COMBI/support/access fit for
   **1.00 nominal / 1.30 budgeted earth-terminal overhang**.
   No special 1.00 mm filling or repeat question about confirmed reel colours
   is needed. Cable lot/standard, UV/wet-conduit and bend/impulse applicability
   remain independent evidence, not a guessed resistor-model change.
5. After a reviewed circuit/part/process decision, update actual source/BOM/
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
