# Remediation Plan

Prepared: 2026-09-06. Reviewed hardware baseline: v1.1.0.

**Status: requirements and review completed; electrical, PCB, and build remediation NOT IMPLEMENTED. The current manufacturing package is on hold.**

This is the starting context and implementation checklist for subsequent sessions. It consolidates the review and the user's later decisions, including changes to the originally proposed TEST wiring. It is not manufacturing approval, a completed hardware test report, or a board-level lightning certification.

## Start Here

1. Read [AGENTS.md](AGENTS.md) for operating instructions and physical guardrails, then this file. Read the relevant source files before editing them.
2. Inspect `git status` and the existing diff. Preserve all work already present. At plan creation, `README.md`, `AGENTS.md`, and `ORDERING.md` contain preparation edits; an untracked `build-20260905/` archive also exists. Do not revert or clean these indiscriminately.
3. Treat the working `pcb/pcb.kicad_sch`, `pcb/pcb.kicad_pcb`, project settings, and reviewed sourcing data as the design sources. `build/*` contains Makefile-generated production outputs. Backups, archives, and `tmp/` copies are not authoritative designs.
4. Use the agreed requirements and TEST matrix below. Much of the older prose in `README.md`, `INSTALL.md`, `RISKS.md`, and other documents is still incorrect. `REVIEW.md` is an audit prompt/template, not the completed review or an approved order specification.
5. Start with **P1: Verification**, or the first unfinished work package requested by the user. Electrical analysis in P2 can proceed alongside P1. Do not freeze the final layout/BOM before the protection design is settled.
6. **Beware of the current Makefile:** `make clean` and successful packaging delete the entire project `tmp/` directory. Preserve any useful audit evidence before invoking them; P1 must restrict cleanup to build-owned staging.
7. Update checkboxes, issue status, evidence, and the session log as work is actually verified. Do not mark hardware qualification complete because documentation was corrected or DRC passed. Commit, order parts, upload designs, or place fabrication orders only when requested.

Preparation already completed:

- [x] Reviewed source PCB, schematic, documentation, BOM/CPL, and generated manufacturing data.
- [x] Recorded the user's clarified operating requirements at the start of `README.md`.
- [x] Added the [via and component-hole DFM policy](README.md#via-and-component-hole-dfm), corresponding agent instructions, and corrected the related via-ordering assumptions.
- [x] Modeled the revised TEST topology and representative cut faults in temporary scripts.
- [ ] Implement P1-P6 below. None of the preceding preparation closes the unresolved circuit, layout, or manufacturing defects.

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
- The existing 4PDT matrix leaves End A and End C joined at common Pin 8. An empty TEST throw does not separate them; the healthy core backfeeds the broken core.
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
| Overpass | GDT_AC north-south over B, with at least 2.0 mm physical standoff above the PCB, supported by a controlled forming/inspection drawing. |

Apply [README's DFM policy](README.md#via-and-component-hole-dfm) and AGENTS section 9. In particular: no ordinary via as a lead-insertion hole, no blanket filling of all 1 mm holes, and no assumption that 2 oz exterior copper means 70-micrometre barrels.

## Reviewed Components

The current board has 14 electrical components, all on top: two SMT and twelve THT, plus four mechanical hole footprints. Counts must be regenerated if protection parts are added.

| References | Baseline MPN / sourcing code |
| :--- | :--- |
| D1, D2 | onsemi 1N4007G / C232439. The CSV incorrectly says LGE. |
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

IDs retain the original review mapping. All implementation/qualification items are **OPEN** at plan creation; C3's replacement topology and W7's functional/site requirements are now decided.

| ID | Problem and evidence | Required closure |
| :--- | :--- | :--- |
| C1 | D1/D2 use 0.90 mm holes. JLCPCB's -0.08 mm tolerance permits 0.82 mm finished holes, smaller than onsemi's 0.86 mm maximum lead. BOM manufacturer is also wrong. | 1.10 mm finished holes with existing 2.20 mm pads; exact part identity/fit evidence; regenerated drills. P3/P4. |
| C2 | Hand-maintained CPL uses positive screen Y rather than native exported negative Y. J_LED_A/C are +103/+142 in the CPL versus -103/-142 in native output. Custom footprint axes/polarities also differ from standard-looking names. | Native generated coordinates, checked handedness/origin, and verified assembler rotations. P3/P4. |
| C3 | Legacy End A/C common Pin 8 creates diagnostic backfeed; the old B-return topology cannot locate a complete cut. | Implement the agreed same-end matrix and repair/retest truth table, not merely another empty throw. P2/P5/P6. |
| C4 | Series 1N4007 does not guarantee LED reverse voltage below 5 V. Reversing the LED leads is different from reversing the supply. Darkness is not proof of protection. | Design and verify actual protection for both reversal cases, normal operation, and relevant transients. P2/P3/P6. |
| C5 | The 2 A fuse does not clear every cable-limited fault promptly. GDT extinction/follow current with a powered 36 V source is unqualified. | Actual PSU/fuse/GDT fault analysis, any required protective circuit, and powered-recovery evidence. Documentation correction alone is not closure. P2/P5/P6. |
| W1 | Nine rail via holes intersect SMT GDT mask/paste apertures by 0.19 mm. All four SMT pads are involved. Normal reliable covering/filling limits are about 0.5 mm, not the protected 1.0 mm holes. | Correct land/mask/paste geometry and obtain compatible CAM/assembly treatment; preserve heavy vias. Policy already written, layout still unfixed. P3/P4/P6. |
| W2 | 470 V DC sparkover is not a 470 V transient clamp. Component 5/20 kA ratings, 2 oz copper, and paralleled terminals do not establish a board rating or guaranteed sharing. | Coordinated transient design, explicit qualified limits, corrected claims, and required complete-path tests. P2/P5/P6. |
| W3 | About 0.5 W per resistor is not proof of cool operation inside gel; the 1 W rating and long-life mode have different derating conditions. | Continuous-duty analysis and potted steady-state measurements at worst credible supply/solar conditions. P2/P5/P6. |
| W4 | Connector holes are 1.4/1.3 mm, versus 1.6 mm in linked supplier CAD; maximum-pin fit was not established. J_IN's courtyard ends at X=111.10 while its own body outline reaches 111.20; adjacent SMT courtyard starts at 111.15. | Exact maximum-pin/body drawings, honest courtyards, approved insertion allowances, and actual assembly clearance. Supplier CAD alone is not proof. P3/P6. |
| W5 | LED torque is stated as 1.5-2.0 Nm instead of APEM's published 0.20-0.25 Nm range, subject to exact model instructions. Full enclosure fit and formed GDT height are unproven. | Correct installation data, assembly drawing/acceptance, and actual COMBI dry-fit. P3/P5/P6. |
| W6 | Legend violates standard height/stroke rules; Makefile omits project settings and warning/parity checks. Libraries and metadata are inconsistent. | Effective rules, reproducible project libraries, full reports, corrected legend, and regression tests. P1/P3/P4. |
| W7 | Fault tables, RF assumptions, earthing, environmental/lifetime claims, and five-board sign-off are overstated. Cable and cattle-fence exposure add qualification requirements. | Synchronized truthful documents and separate workmanship, electrical, environmental, RF/site, and surge acceptance. P2/P5/P6. |

Also address the review suggestions: reconcile the nominal 1.60 mm board with the listed 1.67 mm stackup including masks; add useful underside references/revision identification; retain an unpotted reference prototype; and approve manufacturer-added rails/fiducials/tooling rather than treating their absence on the single PCB as an inherent defect.

## Implementation Sequence

**P1 and P2 can proceed in parallel. P3 needs P1's checking infrastructure and P2's approved protection-part decisions before final layout freeze. P4 follows the final layout. P5 accompanies every change, and P6 verifies the resulting release.**

Prefer small, coherent changes and reuse the existing Python/Make tooling. New helper, library, and test paths below are proposed deliverables, not files that already exist.

### P1: Verification

Files: `Makefile`, `pcb/pcb.kicad_pro`, new `pcb/pcb.kicad_dru`, `scripts/compare_nets.py`, focused checks under `scripts/` and `tests/`, `AGENTS.md`.

- [ ] Stage a consistent complete project: PCB, schematic, project/rule files, library tables, and project-local libraries. Keep KiCad staging in a non-hidden, project-local directory such as `tmp/manufacturing/`.
- [ ] Restrict cleanup to build-owned paths. Separate Gerber/drill scratch outputs and correct dependencies so `make -j4 all` cannot race, remove another target's files, or publish a partial package.
- [ ] Check the resolved CLI by invoking it, including `--version`; do not apply `command -v` to a multiword Flatpak command. Document the tested KiCad 9 baseline rather than claiming untested 7/8 compatibility.
- [ ] Make `make check` run project-aware DRC, ERC, and schematic parity. Retain readable and machine-readable reports on both success and failure. Report all design warnings; block electrical/DFM errors and unreviewed design warnings. Do not broadly suppress missing libraries, courtyard checks, or legend warnings.
- [ ] Gate every public manufacturing export/package target, including direct drill, IPC, BOM, and CPL invocations, through the appropriate verification. Keep raw exports needed by checks as private scratch steps so the dependency graph does not become circular.
- [ ] Set applicable two-layer/2 oz rules: e.g. at least 0.1651 mm track width, existing 0.20 mm general copper clearance, at least 0.254 mm nominal component PTH ring, appropriate hole clearances, and standard 1.0 mm / 0.15 mm legend height/stroke with pad clearance. Distinguish manufacturer minima from conservative project rules and via rules from component-pad rules.
- [ ] Add explicit earth separation and geometry assertions for protected rails/vias, mounting features, LED pad/net polarity, and relevant drill/mask/paste interactions. DRC alone does not verify part fit or via covering.
- [ ] Strengthen net comparison: reject empty/unrecognized input, compare full terminal membership, and check schematic/PCB/IPC-D-356 connectivity with documented net aliases, coordinate units, and rounding tolerances. Prefer native exports/APIs and structured data over fragile success-producing regexes.
- [ ] Add focused positive/negative fixtures showing that wrong nets, lost project rules, undersized holes, violated earth spacing, and exposed SMT via holes are detected. Provisional artifact checks may run after export to scratch; public release publication must wait for their success.

**Exit:** Known file-level defects are reproducibly detectable. An initial failure on the current design is expected, not a reason to weaken the gate.

### P2: Electrical Design

Files: `pcb/pcb.kicad_sch`, the PCB as required, `pcb/BOM.csv`, `scripts/analyze_limits.py`, electrical tests, `INSTALL.md`, `RISKS.md`, assembly/engineering notes.

- [ ] Replace the legacy hub connection matrix and diagrams with the six-end matrix above. Obtain the selected switch's contact diagram and DC/transfer approval before assigning physical terminal numbers. Keep the OEM transmitter protector and protective-earth requirements explicit.
- [ ] Make the default analysis use 41 stations and same-end return. Model A, B, and C separately for faults; a collapsed A/C model is suitable only for a justified healthy symmetry calculation. Parameterize actual cable resistance, voltage, LED characteristics, and temperature/tolerance inputs.
- [ ] Add regression cases for all seven cut combinations across the 40 spans, particularly the first and final spans, and representative repair/retest sequences. Include current/power-balance checks and negative controls reproducing the legacy A/C backfeed and both-B-return masking defects.
- [ ] Design LED protection that covers reversed supply and reversed flying leads while preserving normal light output. Prefer a PCB-side solution compatible with the purchased raw indicators and no field soldering. A single antiparallel diode across the PCB connector does not cover both faults.
- [ ] Select actual parts using maximum clamp voltage, leakage, temperature/tolerance, and pulse/current data, not just a nominal TVS/zener voltage. Check LED forward pulse current as well as reverse voltage. A voltage clamp alone is not automatically adequate forward-current protection. Recheck fault observability after any circuit change: preserve or explicitly model one-way rung behavior, rather than using the old forward-only model to validate a bidirectional replacement.
- [ ] Coordinate the primary GDTs, indicator branches, source interface, and any secondary protection. Reviewed impulse sparkover at 1 kV/us is up to 950 V for SMD5050-470NA and 1100 V for 2R470TD-8; B5G470L's 850 V figure is specified for 99% of measured values. Include lead overshoot and the cable's unverified impulse withstand.
- [ ] Analyze hard/resistive shorts and ignited/failed GDTs with the actual supply and cable topology. The tubes' roughly 10-15 V arc voltages matter after ignition. Do not infer extinction from 36 V being below DC sparkover, or infer holding current from a glow-to-arc transition figure. Implement a coordinated shutdown/protective arrangement if required; do not merely reduce the fuse value without discrimination analysis.
- [ ] Remove `BLOWS (>2A)` from the analysis logic. Use actual fuse/source behavior. The specified 2 A Littelfuse 217 has published DC interrupting ratings; the demonstrated problem is clearing coordination, not simply a 250 V marking. Recalculate legacy fault-current figures for the new wiring.
- [ ] Bound continuous resistor/LED/connector temperatures, including supply tolerance and accessible adjustment. Vishay MBE0414's 1 W power-mode rating is not its 0.65 W standard-mode long-life rating. Keep the present resistors only if the resulting limits support them; qualify any higher-wattage substitute rather than assuming a drop-in or reduced heat generation.
- [ ] Define the required electrical qualification scope and record unresolved supplier/test evidence. Do not add needless logic, a blanket earth plane, or a TEST-direction selector. Do not claim 5/20 kA assembled performance, 72 A terminal capability, or equal transient sharing without evidence.

**Exit:** The hub logic and protection architecture are specified, reviewed, and reflected in the schematic/BOM. Normal-operation safety is analyzed; remaining powered-surge qualification is explicitly open rather than declared solved by prose.

### P3: PCB DFM

Files: `pcb/pcb.kicad_pcb`, schematic footprint assignments, project-local libraries/tables, `pcb/pcb.kicad_pro`, `pcb/pcb.kicad_dru`, controlled assembly/fit notes under `pcb/`.

- [ ] Create project-local footprint/symbol definitions for intentional custom geometry. Use standard library objects where genuinely compatible. Preserve global pad positions/nets during migration and represent the intentional LED connector mappings accurately; do not silently replace modified footprints from the stock libraries.
- [ ] Change D1/D2 to **1.10 mm finished holes / 2.20 mm pads**. The nominal ring remains 0.55 mm. Correct the onsemi identity and other affected rating/geometry records.
- [ ] Obtain maximum finished lead dimensions for every selected THT part, including connector pin diagonals and forming tolerances. Record drawing revision and fit calculation. Treat 1.60 mm connector holes as a candidate to verify, not a guaranteed answer from supplier CAD.
- [ ] Apply `nominal finished hole - 0.08 mm >= maximum pin envelope + assembly allowance`; start with at least 0.10 mm diametral allowance after tolerance and account separately for pitch/hole-position/forming tolerances. Recheck annular rings, hole/copper spacing, and edges after resizing. Do not solve insertion by reaming plated finished boards.
- [ ] Rebuild body/fabrication outlines and courtyards from maximum dimensions plus appropriate assembly clearance. Resolve real interference by placement/geometry changes within the guardrails, not by shrinking courtyards. Check rework and screwdriver access.
- [ ] Correct SMT GDT land/mask/paste geometry while preserving the nine rail vias and full-width copper. The current via at Y=114.88 extends to 115.38 while its adjacent mask/paste opening starts at 115.19: a 0.19 mm overlap. Similar intersections occur on B/C. Inspect full drill circles, exposed annuli, and actual mask barriers, not just via-centre distance or a tenting flag.
- [ ] Follow the selected GDT land pattern and obtain solder-volume/thermal-process acceptance. If no compliant solution preserves the protected geometry, obtain explicit design/process approval rather than shrinking vias or assuming 1 mm resin filling is standard.
- [ ] Place/route the selected protection parts, then revalidate all nets, surge clearances, symmetry requirements, and component-fit evidence. Do not narrow surge connections with generic thermal-relief spokes simply to ease soldering; agree a suitable heavy-copper soldering process.
- [ ] Correct legend height/stroke and clipping. Prefer a suitable native stroke font if TrueType detail remains too fine. Preserve visible polarity, cathode, and A/B/C/EARTH labels; add useful underside references and a new revision identifier without creating new clearance problems.
- [ ] Reconcile the finished-thickness/stackup definition with the quote while keeping 70-micrometre copper on both sides. Check the Essentra support's actual hole and board-thickness acceptance, including fabrication tolerance.
- [ ] Add a controlled assembly drawing, including a side view defining the GDT_AC minimum gap, lead pitch/forming, orientation, and inspection method. Check full COMBI 308 fit with the actual WAGO 221-613s, cable bends/glands, earth wires, standoffs, lid LEDs, and screwdriver access. CAD/drawings do not replace physical dry-fit.

**Exit:** Layout and library checks pass with genuine geometry. Part-fit evidence and the chosen via/solder process are either accepted or explicitly held for CAM, never assumed from DRC.

### P4: Production Data

Files: `Makefile`, `pcb/BOM.csv`, `pcb/CPL.csv`, small export/validation helpers, generated `build/*`, assembly output sources.

- [ ] Keep `pcb/BOM.csv` as reviewed sourcing data and validate it against schematic/PCB references, values, MPNs, footprints, and population. Derive counts from the revised design rather than retaining the old 14-component total.
- [ ] Generate CPL from native KiCad positions in mm, retaining all required SMT and THT parts and excluding mechanical holes/DNP items. Do not use an SMD-only export for this mixed assembly. Make `pcb/CPL.csv` a generated reference mirror, not a second independent placement source.
- [ ] Prefer retaining the existing absolute Gerber/drill origin and native signed-Y placement convention. If another origin is chosen, explicitly apply/check the common transform across outputs. Never fix handedness with absolute coordinate values. Normalize rotations modulo 360; -90 and 270 degrees are equivalent, not a discrepancy.
- [ ] Verify every selected JLCPCB model's centroid and rotation. Native position output describes footprint placement origins, which must be checked against intended assembly centroids; document any anchor-to-centroid correction. Record only evidence-backed corrections, keyed clearly to the actual part/footprint. GDT_AC's internally vertical geometry and D1/D2's cathodes-right mapping must not be inferred from their old standard-looking footprint names. Do not move/rotate PCB pads to compensate for an import mistake.
- [ ] Export copper, mask, legend, top paste, outline, separate PTH/NPTH drills, and IPC-D-356 to fresh scratch outputs. Top paste already exists in the baseline package; preserve and inspect it. JLCPCB may prepare its own stencil data, so customer F.Paste is not proof of unchanged production apertures.
- [ ] Validate actual generated geometry, drill classification, BOM/CPL completeness, net connectivity, and archive contents before publication. Prevent stale files or a failed build from being presented as the current verified release. Preserve the documented upload filenames and mirrors unless a deliberate, documented change is approved.
- [ ] Export readable assembly documentation and a release manifest identifying the hardware revision, tool version, source/artifact hashes, and verification results. Do not hand-edit generated Gerbers, drills, or ZIPs.
- [ ] Obtain order-specific acceptance for 2 oz/ENIG mixed SMT/THT assembly, actual part allocation/attrition, heavy-copper soldering, and GDT lead forming. Current public guidance permits THT under both Economic and Standard in principle; verify the exact quote instead of asserting a universal service restriction.
- [ ] Approve manufacturer-added rails, fiducials, tooling, and depanelization without cuts/holes in protected functional copper. Standard PCBA's processing-size requirement may require panelization for this 63 x 56 mm board. Do not assume the old 73 x 76 mm panel or automatic rail removal, and distinguish five individual boards from five multi-up panels.
- [ ] Provide coordinate-based identification of the 14 stitching vias and their required dimensions/treatment. Resistor holes also use 1.0 mm drills: no blanket filling by diameter. Confirm processed CAM has not reduced protected vias. Agree any required minimum finished barrel copper separately; the published 18-micrometre average is not such a guarantee.

**Exit:** Verified production data is generated reproducibly and is unambiguous for assembly. Bare-board flying-probe continuity is not advertised as assembled functional or surge testing.

### P5: Documentation

Synchronize documents alongside the relevant implementation, then perform a final consistency pass. Keep user-confirmed purchases distinct from required quantities and proposed replacements.

- [ ] `README.md`: replace legacy counts, topology, power/brightness baselines, part identities, build descriptions, and unsupported 20-50-year/board-surge claims. Distinguish nominal design dimensions, tolerance calculations, and measured acceptance.
- [ ] `INSTALL.md`: replace every legacy hub diagram/pin table; preserve isolation and the agreed repair/retest workflow. Correct LED torque against the exact APEM instructions, cable/core identification, gland selection, mounting/dry-fit, potting procedure, and optional low-voltage DMM checks. Prohibit green/yellow as an active fence conductor. Replace "STORM ISOLATE" with accurate OFF labeling.
- [ ] `ORDERING.md`: use the actual prototype baseline and verified via/assembly process, separate PCB CAM approval from parts-placement approval, update sourcing/quote expectations, and remove blanket stock, lead-time, gold-sealing, and rail-removal guarantees. Optional upgrades require fresh qualification.
- [ ] `ACCEPTANCE.md`: separate workmanship, normal DC function, reversal protection, continuous thermal soak, 5 m daylight visibility, full-hub cut tests, RF/site behavior, and qualified surge/fault tests. Measure temperature rather than using touch; define instrument ranges/uncertainty. A dark LED or 0.00 mA reading does not prove safe reverse voltage or sub-microampere leakage. A DMM-open GDT is not proof of a functioning arrester.
- [ ] `RISKS.md`: correct the fuse and reverse-voltage analyses; include GDT follow current, failed-open/short devices, unequal firing, residual voltage, earthing/PE and touch/step potential, coastal/solar/cable limitations, and 0.5 m / 300 m cattle-fence coupling. Remove unconditional zero-risk, guaranteed-sharing, hermetic/IP68, and 72 A assertions.
- [ ] `MATERIALS.md`: reconcile 41-station requirements, 82 LEDs, quantities/spares, actual PSU/switch procurement, and any approved new protection parts. Preserve existing ORDERED/ON HAND history and identify shortfalls separately.
- [ ] `LED.md`: describe the selected no-resistor indicator correctly and record the 5 m acceptance target. Keep alternate-part suggestions clearly unqualified; a larger mounting bezel is not proof of better daylight contrast.
- [ ] `AGENTS.md`: synchronize the implemented build/rule/library workflow and genuine physical invariants. Retain the via/hole-fit policy, but correct unsupported rating assertions while preserving actual copper and terminal connections.
- [ ] `REVIEW.md`: update the reusable audit prompt to the agreed prototype specification, rather than automatically demanding high-Tg 170, 2-microinch gold, or filled vias. Keep it distinct from the actual issue/evidence record in this file.
- [ ] Assign a distinct hardware revision and synchronize visible board identification, schematic metadata, documentation, and release manifest. Remove pending-remediation warnings only to the extent their specific conditions are genuinely closed; retain field-qualification holds where necessary.

**Exit:** Documents agree with the actual remediated design and clearly separate file verification from hardware/site evidence.

### P6: Validation

- [ ] Run the focused automated tests, preferably using the existing lightweight Python environment, then `make check`. Reproduce the agreed 41-station and seven-cut-combination behavior using the final circuit assumptions.
- [ ] Run a clean `make all` and a clean `make -j4 all` after P1 fixes cleanup/races. Compare geometry/connectivity and population, allowing only documented metadata differences such as timestamps.
- [ ] Exercise failure fixtures: missing project/rules, a wrong net, insufficient earth clearance, an exposed SMT via hole, an incompatible part/hole, a missing BOM/CPL designator, reversed placement Y, and missing manufacturing layers. Confirm invalid current releases are blocked, not silently packaged.
- [ ] Inspect rendered source and generated copper/mask/paste/legend/drill/assembly data. Verify the actual JLCPCB processed files and placement before approving production, including hole treatment, pin fit, standoff instructions, and rail/tooling locations.
- [ ] Perform basic workmanship, value/polarity, and normal-function acceptance on all five prototypes. Allocate appropriate units to protected-reversal, full-hub cut, continuous potted thermal, enclosure-fit, and potentially destructive protection tests while retaining an unpotted reference. Inspect both source-end and reduced-voltage far-end conditions; seek approval for additional samples if the qualification program needs them.
- [ ] Test the actual indicators at 5 m in full daylight, at the final minimum expected current and real viewing angles. Confirm OFF is not confused with sunlit lens colour. Prefer optical improvements before increasing current; any alternative LED or resistor change needs renewed electrical/thermal/fit checks and procurement approval.
- [ ] Qualify RUN with the actual cable, fence construction/height, transmitter, and test receiver. Compare cattle-energizer off/on at the specified routing exposure; check unintended receiver responses, lost boundary field, misleading LED indications, repetitive protection stress, and recovery in both RUN and TEST.
- [ ] Complete the defined source-fault/surge recovery and discharge-path qualification with appropriate equipment and expertise. Do not use ordinary DMM/grounded-scope practices as an improvised high-voltage test method. Verify installation earthing with the qualified installer and applicable OEM/regional requirements.
- [ ] Retain one unpotted golden/reference sample, record per-board results and exact parts/process revision, and update issue closure with evidence. Passing basic bench tests alone does not authorize the full perimeter rollout.

## Release Gates

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

Plan-creation validation: `git diff --check` and `git diff --no-index --check /dev/null REMEDIATION.md` passed. These are documentation checks; the KiCad and model results above are prior review evidence, not newly performed hardware qualification.

Suggested instruction for a new implementation session:

```text
Read AGENTS.md and REMEDIATION.md, inspect the current worktree, and implement
the first unfinished work package (or the package I specify). Preserve existing
changes and physical guardrails. Use the settled 41-station, same-end-return,
continuous-safe TEST baseline; do not add a direction selector. Verify the work,
update the plan/session log with evidence and remaining blockers, and do not
place orders or commit changes unless requested.
```
