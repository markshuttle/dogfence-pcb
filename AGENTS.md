# Dog Fence Agent And Developer Guide

Hardware development revision: **1.2.0-dev**. Tested native CLI: **KiCad 9.0.7**.
File-verified prototype artifacts are authorized, not uploads or orders.
Production/field release remains held; file checks are not hardware approval.

## 1. Start Here

1. Read [REMEDIATION.md](REMEDIATION.md), including the agreed requirements,
   issue register, current session handoff and release gates, before editing.
2. Inspect `git status` and the existing diff. Preserve changes by the user and
   other agents. Do not commit, upload, order or clean unrelated evidence unless
   requested. Use headless tools only, never interactive KiCad applications.
3. Authoritative inputs are `pcb/pcb.kicad_pcb`, `pcb/pcb.kicad_sch`, project/rule
   files, local libraries/tables, reviewed `pcb/BOM.csv`, and the controlled
   engineering records. Backups, generated `build/`, and `tmp/` are not designs.
4. [README.md](README.md) describes the system; [INSTALL.md](INSTALL.md) controls
   operation; [ORDERING.md](ORDERING.md) controls quote/CAM/placement review;
   [MATERIALS.md](MATERIALS.md) preserves procurement history;
   [ACCEPTANCE.md](ACCEPTANCE.md) separates qualification activities;
   [RISKS.md](RISKS.md) records limitations. `REVIEW.md` is an audit template,
   not completed approval.
5. [pcb/ELECTRICAL.md](pcb/ELECTRICAL.md) records the implemented DC model and
   unresolved protection architecture. [pcb/ASSEMBLY.md](pcb/ASSEMBLY.md) controls
   placement, lead forming, dimensional/lot acceptance and process holds.
   Do not populate a candidate protection part just because it is listed there.
   `pcb/DFM_EVIDENCE.md`, `pcb/ENVIRONMENT_EVIDENCE.md`, `pcb/DESIGN_BOUNDS.md`
   and the two `*_PROTECTION_RESEARCH.md` notes preserve source evidence and
   rejected/unselected circuits; they do not override the release holds.
6. For a **board/prototype-only request**, work the P3/P4 board-finalization
   queue in ORDERING/REMEDIATION, not the first unchecked switch or environmental
   item. Preserve those independent holds without restarting their research.
   The authorized 16-part hybrid selects 2512 SMT (TE Connectivity 35212K2FT
   for prototype; Yageo SR2512FK-7W2K2L / C876850 for production pre-order) preserving
   the existing lands, placement, routing and circuit topology;
   do not add a new circuit or move sound geometry just to produce a PCB diff.
   **Gate P is file-verified prototype artifacts**, separate from original A/B/C
   production/field holds. Supplier CAM/placement/allocated parts, GDT fit/forming
   and panel/process acceptance remain order tasks; enclosure dry-fit on received
   boards and switch/environmental physical qualification do not gate P files.

## 2. Headless Environment

- Linux, Bash, GNU Make, git and Python standard library. Python 3.14.4 and
  KiCad 9.0.7 were exercised in this session; no KiCad 7/8 compatibility is claimed.
- The host Snap CLI is `/snap/bin/kicad.kicad-cli`. Bare `kicad-cli` need not exist.
  Do not launch `kicad`, `pcbnew`, `eeschema` or a desktop editor.
- `scripts/manufacturing.py` resolves native, Snap and Flatpak invocations by
  actually executing `--version`. `KICAD_CLI` can contain a quoted executable or
  a multiword Flatpak command; it is split into argv, never evaluated by a shell.
- If the agent runner requires a KiCad-only host/sandbox bypass and provides
  that option, use it for native KiCad tasks. Do not apply it to ordinary file,
  git or Python work. This tool interface has no `BypassSandbox` parameter;
  normal CLI execution reached the host Snap successfully. Do not invent tool
  arguments or report a bypass that was not used.
- Snap confinement is separate from the agent runner. KiCad inputs/outputs must
  stay under a non-hidden user-workspace directory, not system `/tmp`, `/run`,
  `/var/tmp` or hidden home directories. Project-local `tmp/` is git-ignored.

## 3. Verification And Publication

After any PCB/schematic/layout change, run:

```bash
make check
```

The complete snapshot is staged under `tmp/manufacturing/runs/attempt-*/project`:
PCB, schematic, settings/rules, local libraries/tables, BOM, `verification.json`
and all seven controlled engineering notes (assembly/electrical, DFM,
environment, design bounds and both protection research records). Build and
analysis helpers are also snapshotted
and inputs are hashed before and after verification. Changed/missing inputs fail.

`make check` performs project-aware native DRC, ERC, schematic parity, geometric
guardrails, and private native netlist/IPC/position/Gerber/drill/assembly exports.
It checks complete terminal membership, BOM identities/population, signed-Y CPL,
fabrication geometry, drill classification and archive contents. Unsupported
geometry fails closed; extend and test the validator rather than ignore it.

- Readable and JSON DRC/ERC reports are retained at `build/drc_report.*` and
  `build/erc_report.*` on success and failure. Additional logs, geometry and
  verification results are in `build/reports/`; `build/status.json` identifies
  the attempt. Failed native execution is not an empty successful report.
- All electrical/DFM errors and unreviewed warnings block. Project severity
  ignores and DRC/ERC exclusions are forbidden. The **only current reviewed
  DRC/ERC warning exception** is the exact eight single-global-label UUID/name pairs
  recorded with rationale in `pcb/verification.json`, bound to this revision
  and a single sheet. Native warnings remain visible in both reports; changed
  labels, extra sheets, stale reviews and every other warning require review.
- Native export diagnostics are gated too. The one annotation-warning line
  from KiCad 9.0.7 XML netlist export is separately reviewed for the ten
  intentional nonnumeric J_/GDT_ designators, with exact schematic/project/
  symbol-library/table hashes in `pcb/verification.json`. Numbered-reference
  controls and duplicate/unassigned-reference probes established its cause.
  Any changed input, different warning, extra diagnostic or different tool
  version invalidates that review. Never automatically refresh approval hashes.
  The exact known KiCad 9.0.7 wxWidgets duplicate-image-handler `Debug` lines
  from PCB exports are informational, retained and counted in reports; unknown
  stderr is not silently discarded.
- `pcb/verification.json` also records engineering release holds. `make check`
  may pass file checks with those holds explicitly reported, but does not close
  Gate A or publish an order package. It refreshes `pcb/CPL.csv` only after all
  file/artifact checks pass. That CSV is a generated draft reference, not an
  independent source or upload approval; on failure it may remain from an older
  checked revision.
- For the prototype order, the user selected **TE Connectivity 35212K2FT / C4129105**,
  CGS 3521 / 2512 SMT, 2.2 kohm / 2 W / 1%, AEC-Q200, for **both R1/R2 in the prototype
  BOM** (verified in stock at JLCPCB). Use manufacturer `TE Connectivity`, `Sourcing=LCSC`
  and empty `Sourcing Reference` in BOM/CAD. [JLCPCB C4129105](https://jlcpcb.com/partdetail/C4129105)
  verifies identity and resolves the prototype resistor procurement blocker.
  The user confirms the production order is **Yageo SR2512FK-7W2K2L / C876850**
  (20-day wait); [JLCPCB C876850](https://jlcpcb.com/partdetail/C876850) independently
  confirms its identity. The prior **Uni-Royal PS122WF2201T4E / C2793873** order was
  cancelled and refunded by JLCPCB due to distributor stockout. In-stock JLCPCB status is not
  PCBA job allocation; whole-BOM **`allocation_verified` remains `false`**. MATERIALS records
  quantities and separate allocation tasks. No agent upload or order is authorized.
  Yageo is not populated by the current TE prototype BOM. Before production,
  review its own manufacturer/model, footprint/process and thermal evidence,
  deliberately update BOM/CAD/libraries/model/notes and repeat the affected checks.
  TE prototype results do not qualify Yageo or automatically switch the BOM.
  Prior **HP122WF2201T4E pending External sourcing is superseded, not ordered**.
  **C2791283 is HP122WJ0472T4E, 4.7 kohm / 5%**; its wrong pairing with
  HP122WF2201T4E in `02661d8` remains rejected history, not a 2512 identity.
  The generic BOM `Sourcing=External` rule still requires an empty code and exact HTTPS
  `Sourcing Reference` matched to PCB/schematic metadata. This is explicit
  pending procurement, not a guessed C-code or allocation approval. Unresolved
  external rows block **both prototype and production publication**. Ordinary
  LCSC rows still require valid reviewed C-codes; those do not reserve stock.
  Use REMEDIATION's latest revision-specific results, not prior checks,
  for native verification and publication status. Part selection is not a new PASS.
- `make gerbers` / `make prototype` run the complete file/artifact checks and
  may publish **FILE-VERIFIED PROTOTYPE ONLY** packages with **all five
  C4/C5/W3/W1/W4 ledger holds recorded as deferred, not closed**. No file,
  sourcing or diagnostic check is bypassed. `make check` never publishes.
- Production targets `all`, `package`, `release`, `production`, `drills`, `ipc`,
  `bom`, `cpl`, `zip-gerbers`, `zip-flytest` retain all engineering holds and
  sourcing gates. **Production wins mixed goals**, regardless of order.
  Clearing production holds requires an evidence-backed file-release review;
  prototype authorization is not that review or an upload/order authorization.
- One shared Make prerequisite and a filesystem lock serialize both modes.
  Gerber and drill scratch directories are separate. `make -j4 all` cannot
  remove another target's outputs or publish a half-built package.
- Each new attempt quarantines prior `build/` and the Gerber mirror within its
  owned run directory. A failure must not present yesterday's package as current.
  Only a matching `build/manifest.json` with validated revision/source/artifact
  hashes and the correct pair identifies current file-verified artifacts:
  **`status=prototype`, `mode=prototype`** or production **`status=verified`,
  `mode=build`**. Status alone is insufficient. Neither means CAM, order, field
  or lightning approval.

When the selected publication mode's gates pass, filenames remain `build/Gerbers.zip`
(mirror `pcb/Gerbers.zip`), `build/BOM.csv`, `build/CPL.csv` (generated source
mirror), `build/pcb.d356` and `build/FlyTest.zip`. The release also contains
`Assembly.pdf`, `Assembly.txt`, `ViaTreatment.csv`, the controlled notes, reports
and manifest. Generated `README.txt` accompanies the release and travels inside
both Gerbers/FlyTest ZIPs, identifying the mode and open holds. Both modes share
these filenames and mirrors; require the matching manifest, not a filename.
The native assembly PDF includes pad outlines and courtyards;
the text gives exact footprint anchors and all electrical terminal datums with
pin numbers/nets in PCB and signed-Y fabrication coordinates. These aid supplier-model
review, not approved centroid corrections. Flying-probe inputs describe
**bare-board continuity**, not an assembled functional or surge test. Never
hand-edit generated artifacts.

```bash
make test
TMPDIR=/tmp/opencode KICAD_TEST_CLI=/snap/bin/kicad.kicad-cli python3 -B -W error -m unittest discover -s tests -v
python3 -B scripts/analyze_limits.py
python3 -B scripts/design_bounds.py
python3 -B scripts/review_annotation.py --cli /snap/bin/kicad.kicad-cli
python3 -B scripts/verify_workflow.py --expect-holds C4 C5 W3 W1 W4
python3 -B scripts/verify_workflow.py --target prototype --expect-holds C4 C5 W3 W1 W4
```

The first command runs stdlib tests; native contract probes need
`KICAD_TEST_CLI`. Those probes use their own Snap-accessible project-local staging,
not the authoritative PCB or shared release. Non-KiCad temporary fixtures may
use the runner's approved temporary directory. Tests cover negative inputs and
the 41-station, seven-cut-combination model, not physical qualification.

`review_annotation.py` collects fresh XML numbering and malformed-reference
probe evidence in complete private projects under `tmp/annotation-review/`.
It verifies reference/property/instance consistency, inverse-renamed component
contents and terminal membership. Its PASS is evidence for **manual review**;
the helper never updates approval hashes or qualifies the circuit. Rerun after
any changed netlist-review input, inspect the result, then deliberately update
only the justified review fields if accepted. No automatic hash refresh.

`verify_workflow.py` requires exclusive runtime ownership of `build/` and
`tmp/manufacturing/`. It preserves old runs/reports under `tmp/workflow-validation/`,
then executes clean/serial and clean/parallel builds separately and compares
validated fabrication geometry, connectivity and population. `--expect-holds`
is an assertion, not an override. Default `--target all` with open holds must
verify production refusal, not claim `make all` succeeded. `--target prototype`
instead verifies **real serial/parallel prototype publication**, including the
mode/hold notices and matching manifests. That PASS requires resolved sourcing;
prototype refusal for an unresolved external part is not successful publication.

`make clean` removes **only `build/`, owned manufacturing runs and the generated
Gerber mirror**. It preserves unrelated `tmp/` evidence, the lock and the last
generated CPL reference. Run clean separately, never `make -j clean all`.
Preserve useful run reports before deliberate cleanup. If native KiCad is
unavailable, record the actual failed version probe; do not claim DRC passed.

## 4. Libraries And Design Rules

All intentional custom geometry is under `pcb/DogFence.pretty/` with symbols
in `pcb/DogFence.kicad_sym`. `fp-lib-table` / `sym-lib-table` use `${KIPRJMOD}`.
Do not replace modified Kefa terminals, project-selected 2512 SMT lands, the cathode-right
SMA diode, or the axial GDT overpass with similarly named stock-library objects.
Preserve global pad nets, positions and the two distinct local LED-terminal mappings.

```bash
python3 -B pcb/sync_libraries.py --check
```

This detects drift between reviewed embedded objects and local definitions.
After deliberately editing/reviewing the source objects, `--write` regenerates
the definitions. `--sync-metadata` propagates **reviewed BOM** MPN/manufacturer/
LCSC fields without changing values or footprints; run `--write`, `--check` and
`make check` afterward. Never use synchronization to conceal an accidental
geometry or part substitution. Reference/value text placement can differ per
instance; shared geometry and sourcing metadata must agree.

The project enforces two-layer/2 oz track width >=0.1651 mm, conservative
general clearance 0.20 mm, hole clearance 0.25 mm, copper-edge clearance 0.50 mm,
and legend height/stroke >=1.00/0.15 mm with 0.15 mm pad clearance. These values
are not all fabricator minima. Component-PTH annular ring >=0.254 mm and EARTH
separation >=3.0 mm are explicit `.kicad_dru` constraints. Via-ring rules are not
component-ring or pin-fit evidence. Do not weaken settings to obtain a PASS.

## 5. Physical Guardrails

Preserve these unless the user approves a reasoned physical design change:

| Feature | Protected geometry |
| :--- | :--- |
| Board | 63 x 56 mm, (97.00,94.50) to (160.00,150.50). Nominal finished thickness 1.60 mm; the source now totals 1.440 core + 0.070 copper per side + 0.010 mask per side. Supplier thickness convention/tolerances and support fit remain to agree. |
| Mounting | Four 3.20 mm NPTH at (101.50,99.00), (155.50,99.00), (101.50,146.00), (155.50,146.00), with protected 3.45 mm-radius front/back courtyards and copper keepouts. |
| Exterior copper | 0.070 mm on both F.Cu and B.Cu. A/B/C rails stay full 3.20 mm width on both layers, not narrowed thermal-relief spokes. |
| Rail vias | Three per rail at X=112.50,114.00,115.50; Y=114.88 (A),122.50 (B),130.12 (C). All 1.00 mm drill / 1.80 mm copper. Do not delete, shrink or move. |
| Earth copper/vias | Matching solid 4.50 mm-grid copper on both sides, bounding X=143.99..157.25 and Y=111.25..133.75. Five 1.00/1.80 mm vias at X=150.00, Y=114.88,118.69,122.50,126.31,130.12. Preserve slit-free continuity and geometry. |
| Earth isolation | >=3.00 mm fence-to-earth copper separation; present minimum 3.25 mm. Preserve B returns at X=135.50, Y=107.20/137.80 unless an approved equivalent maintains constraints. |
| Earth GDTs | Centres Y=113.50,122.50,131.50; 9.00 mm pitch. Actual maximum bodies/forming must establish the gap, not a nominal 8 mm diameter claim. |
| Overpass | GDT_AC runs north-south over B, now at X=125.80, with 15.24 mm pitch and >=2.00 mm pre-encapsulation physical gap under the complete raised span. Follow ASSEMBLY.md; gel is not automatically equivalent to an air gap. |
| LED terminals | J_LED_A=(145.50,103.00),90 degrees, opens north; J_LED_C=(145.50,142.00),270 degrees, opens south. Both pad1 positive X=142.96 and pad2 B return X=148.04. |

The LED local pad coordinates intentionally differ: A pad1 `(0,-2.54,90)` and
pad2 `(0,2.54,90)`; C pad1 `(0,2.54,270)` and pad2 `(0,-2.54,270)`. Do not match
their rotations or replace them with one generic footprint.

The authorized **16-part BOM (eight SMT, eight THT)** uses Vishay **BYG23T-M3/TR /
C145454** for D1-D4 and selected **TE Connectivity 35212K2FT / C4129105**,
CGS 3521 / 2512 SMT, 2.2 kohm / 2 W / 1%, AEC-Q200, for both R1/R2 in the prototype
order (in stock at JLCPCB; with Yageo SR2512FK-7W2K2L / C876850 ordered with 20-day wait for
production builds; prior Uni-Royal PS12 cancelled/refunded), plus the retained
GDTs and Kefa terminals. This evidence correction makes no layout modification.
R1/R2 origins are **(120.00,104.50)/(120.00,140.50), rotation 0**, pads at
**X=116.875/123.125**. Retained project-alternate lands are **1.35 x 3.70 mm rectangles at
local X=+/-3.125**, maximum body **6.45 x 3.40 mm**, maximum height **0.65 mm**;
the **8.10 x 4.20 mm courtyard** and project-selected zero additional mask/paste
margins remain unchanged. No resistor holes, standoff or forming.
TE's recommendation is **1.50 x 3.00 mm, 5.00 mm inner gap / 6.50 mm pitch**,
not these HP/PS-derived lands. Body containment does not establish an exact
land-pattern match; accept the retained alternative's placement/stencil/solder
process under W4. Preserve geometry unless a reviewed change is authorized.
D1/D2 origins are **(130.80,104.50)/(130.80,140.50), rotation 0**, cathodes east
at **X=132.90**, anodes at **X=128.70**. D3/D4 remain at
**(135.00,99.00)/(135.00,146.00), rotation 180**, cathodes west to LED positive
at **X=132.90**, anodes east to B at **X=137.10**. Straight cathode links at
**X=132.90 are 1.80 mm wide and 5.50 mm long**. SMA pads remain 2.50 x 2.00 at
local X=+/-2.10, zero additional mask/paste margins; no diode holes.
Initial takeoffs and protected rails/vias/earth/mounts/LED mappings remain;
no fold or new vias. Expected inventory is **34 terminals, 32 PTH hits
(18 component +14 via), four NPTH, 52 IPC records; F.Mask 52, B.Mask 36,
F.Paste 16**. These are design expectations, not a native-check result.
Datasheet 5/20 kA impulse or terminal current ratings are
**component** ratings, not assembled-board performance. Three paralleled EARTH
pins remain connected, but are not a 72 A assembly rating. The 2 W resistor
still dissipates about 0.50 W nominal; a wattage label is not cool-body or
continuous potted qualification. TE 3521's [Data Sheet 9-1773463-5 Rev G, 02/2025](https://www.te.com/commerce/DocumentDelivery/DDEController?Action=showdoc&DocId=Data+Sheet%7F9-1773463-5%7FG1%7Fpdf%7FEnglish%7FENG_DS_9-1773463-5_G1.pdf)
specifies **+/-100 ppm/C** at 2.2 kohm, -55 to +155 C operation and catalogue
2 W at 70 C ambient derating to zero at 155 C. Its TCR method names room and
minimum/maximum operating temperatures, not numeric reference/test endpoints.
The model's **25 C reference, -30..125 C study and -55..125 C supported inputs
are engineering assumptions**, not TE test conditions. The conditional screens
remain **0.501018 W nominal / 0.756803 W upper per resistor**.
TE's page 3 reference PCB has **four layers, 2 oz outer / 4 oz inner copper**;
catalogue rating/derating transfer to this two-layer board is unverified, not a
demonstrated failure. The family **250 V working / 500 V overload** ceilings
do not override power/resistance limits: **66.33 V catalogue working** at
2 W / 2.2 kohm is not a system rating. The cited TE sheet does not establish
PS12's `2.5*RCWV` / five-second overload test; model test voltage/duration remain
unknown. Do not transfer PS pulse curves or PR02 hot-spot/K/W/standoff data.
Use DESIGN_BOUNDS for current screens; actual chip/pad/PCB and gel/cable interface
temperatures require separate qualification for the intended population.

Selected hole/pad sizes are KF128 2.00/3.20, KF129 2.00/2.80,
B5G470L 1.40/2.80 and earth GDT 1.50/3.00 mm. These depend on the
controlled pin/body/pattern envelopes in ASSEMBLY, including actual lot and
forming acceptance. Minimum ring is 0.40. Do not restore smaller legacy holes
or equate these file checks with insertion/solder approval. J_EARTH has 1.00 mm
nominal / 1.30 mm tolerance-budgeted body overhang; no courtyard trimming.
GDT forming/overpass standoff remains required. Old onsemi/MBE/PR02 footprints
and axial resistor instructions are retired, not substitutes or order tasks;
preserve their procurement history.

## 6. Functional And Documentation Rules

- Keep 41 stations / 82 LEDs and the **same-end** six-independent-end TEST
  matrix from REMEDIATION: Start A/C positive, Start B negative, End A/B/C each
  isolated. No direction selector, permanent End A/C strap or dual-B return.
- User now accepts LED damage from accidental low-voltage installation polarity
  errors, with spare indicators; reversed flying-lead survival is not required.
  Direct-strike rebuilding is accepted, not all ordinary/nearby transient damage.
  Continuous-safe normal TEST stays mandatory. The simple 16-part hybrid is now
  implemented in the source, not thermally/surge qualified. Do not reinstate the
  40-part investigation as a prerequisite or confuse reverse recovery with
  forward-clamp response. See ELECTRICAL section 9 and ASSEMBLY.
- Energized cattle fencing is **prohibited near the entire 4 km boundary,
  stations and hub**, as explicitly confirmed by the user. The earlier 0.5 m /
  300 m parallel scenario is withdrawn; do not require testing a prohibited
  configuration or invent a safe separation distance. Verify and maintain the
  restriction, reassessing if land use changes. Ordinary RF/switching and
  nearby-lightning exposure, source recovery and site earthing remain relevant.
- User-confirmed source allocation is **two ordered LRS-75-36: one TEST, one
  disconnected spare**, not interconnected supplies. CA10.A364/current WAA364
  is provisionally **eight-pole**, with extra poles unassigned and exact DC/
  global transfer approval open. Reel markings CM03/05.100 and red/black/plain
  green are confirmed; use the AMC 2026 V.3 evidence, not the older listing.
- Gel is **WISKA OneGel**, one-component/no mixing, not MP0100. Resolve its
  conflicting manufacturer cure/temperature fields; do not invent conductivity,
  compatible materials or completed thermal qualification. The 35-37 V source
  window is an unimplemented historical proposal. `design_bounds.py` now uses
  a declared 35 V floor / 40.39597 V upper screen, not a guaranteed or enforced
  window. The TE prototype +/-100 ppm/C screen assumes a 25 C reference; it is
  not a verified TE TCR test condition or a Yageo qualification. Use
  `pcb/DESIGN_BOUNDS.md` rather than duplicating stale derived values.
- Preserve WAGO through-splice/PCB-tap wiring. Normal perimeter current does
  not pass through every PCB. Surge current is a separate design case.
- Normal TEST must be continuous-safe; do not substitute a timer. TEST/OFF
  disable containment, and restoring RUN is an operator action. OFF is not
  demonstrated storm isolation. Do not directly earth a core, switch PE or
  invent an unbonded-rod/DC-negative bonding design.
- Synchronize source, local libraries, BOM, native-generated CPL, assembly and
  electrical notes, README, ORDERING, MATERIALS and affected INSTALL/RISKS/
  ACCEPTANCE whenever parts/routing/geometry or operation change. Update this
  guide when tooling changes, and update REMEDIATION with actual evidence.
- Preserve ORDERED/ON HAND history separately from increased requirements and
  unapproved candidates. Revision identifiers must agree across PCB, schematic,
  documents, release review and manifest. Only verified conditions close issues.

## 7. Research And Tool Use

Use native Read/Glob/Grep for file inspection and apply_patch for manual edits.
Use persistent project scripts for nontrivial analysis, not inline Python file
search/edit commands. Use native web fetching for public manufacturer/CAM
evidence; no terminal `curl`, `wget` or ad-hoc network scraping. A PDF text
extraction or distributor CAD model is not proof of unreadable drawing details.
Record manufacturer, exact MPN, drawing revision, limitations and accepted
supplier response. Public stock is not order allocation. Do not claim a check
was run, a part approved, or a physical test passed without the corresponding
result.

## 8. Parallel Ownership

Give each agent bounded context, named file ownership and exact verification
expectations. P1 infrastructure and P2 analysis may proceed in parallel. Known
P3 corrections may proceed without freezing the design; final protection
placement/BOM needs a supported P2 decision. P4 production follows verified
geometry. Coordinate shared source/staging changes and run integrated gates
after edits settle. Independent read-only review and isolated tests are safe
parallel tasks. Never revert another agent's or the user's work.

## 9. JLCPCB Via And Component Hole DFM

Apply the [master DFM policy](README.md#via-and-component-hole-dfm). Published
guidance was reviewed through 2026-09-07; confirm the actual order. These checks
supplement, not replace, electrical DRC.

- Preserve all fourteen 1.00/1.80 mm stitching vias and protected copper.
  An incompatible process needs an approved layout/process solution, not
  smaller vias or an unreviewed exception.
- Selected ordinary process: **untented both sides, no fill/plug/cap, ENIG**,
  with nominal 1.80 mm circular mask openings and no via paste. Same-net
  stitching annuli may intentionally overlap; this never excuses a component
  mask/paste aperture over a hole. KiCad 9.0.7 uses flat `(tenting ...)` flags;
  nested side booleans and per-via mask-margin clauses fail native parsing.
- Normal reliable tenting/ink plugging guidance is <=0.5 mm. Filled-and-capped
  guides/table give 0.5/0.55 mm upper limits; neither establishes reliable
  filling of 1.00 mm holes. Obtain written CAM acceptance for exceptions.
  Tenting flags, a filling checkbox, opaque mask or gel do not prove a seal.
- Compare full drill circles, annuli, copper and actual mask/paste apertures.
  A neighbouring SMT pad can expose a nominally tented via. Inspect processed
  Gerbers/stencil data too. The current relocation removes the historical
  intersection; retained GDT land-pattern/process approval remains open.
- Identify hole treatment by **function and coordinates**. Ordinary vias are
  not lead-insertion holes. Legacy resistor holes are removed by SMT conversion;
  retained connector/GDT holes stay open. Never request filling by diameter.
  Confirm protected drills survive CAM.
- Use maximum finished lead dimensions, including rectangular-pin diagonals.
  Require `nominal hole - 0.08 mm >= maximum pin envelope + 0.10 mm` as the
  starting diametral allowance after tolerance, with separate pin-pitch,
  hole-position and forming allowances. Nominal diameter/pitch or C-code is
  insufficient. Do not ream plated finished boards to repair insertion fit.
- Recheck >=0.254 mm nominal component-PTH ring for two-layer/2 oz fabrication,
  hole/copper/edge spacing and finished registration after resizing. Generic
  via rules are not component rules. 70 micrometre surface copper is not barrel
  copper; agree a required finished barrel minimum separately.
- Record exact MPN/drawing revisions, tolerance calculations and accepted
  process in assembly evidence; regenerate/inspect artifacts and run `make
  check` for design changes. Documentation or DRC alone does not close physical
  fit, manufacturing, enclosure or electrical qualification.
