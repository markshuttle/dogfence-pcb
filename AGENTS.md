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
   Use the [reviewed prototype population](pcb/ASSEMBLY.md#reviewed-components),
   preserving the existing lands, placement, routing and circuit topology;
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
- Use [BOM.csv](pcb/BOM.csv) and the synchronized CAD/library metadata for exact
  prototype identities. [MATERIALS](MATERIALS.md#resistor-procurement-and-history)
  owns purchasing, cancelled/rejected selections and allocation evidence. A
  production pre-order is not a second implemented BOM; prototype results do not
  qualify a substitution. Review its own evidence and deliberately update affected
  sources/models/notes before repeating the checks. Whole-BOM
  **`allocation_verified` remains `false`**; public stock is not PCBA-job allocation.
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

Before editing rules, read the [project guardrails](pcb/ASSEMBLY.md#physical-guardrails)
and [master DFM policy](README.md#via-and-component-hole-dfm). Project settings,
`.kicad_dru` and independent executable guards enforce the adopted requirements,
not merely fabricator minima. Via-ring rules are not component-ring or pin-fit
evidence. Do not weaken settings to obtain a PASS.

## 5. Physical Guardrails

**Before any PCB, footprint, placement, routing or process edit, read
[ASSEMBLY's Physical Guardrails](pcb/ASSEMBLY.md#physical-guardrails) and its linked
placement, land, forming, hole-fit and via inventories.** These constraints are
binding unless the user approves a reasoned physical design change. Preserve
protected copper, mounts, all stitching vias, takeoffs, B returns, EARTH separation
and the distinct LED mappings; do not fold branches, add vias or trim courtyards
to conceal a fit problem. Keep independent executable geometry checks.

[Reviewed Components](pcb/ASSEMBLY.md#reviewed-components) and
[DFM evidence](pcb/DFM_EVIDENCE.md) distinguish implemented geometry from
manufacturer recommendations and actual lot/process acceptance. Body containment
is not exact land-pattern approval; component ratings are not assembly ratings.
Use [DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md) for named current/thermal screens and
their assumptions. Never transfer retired-part mounting/pulse data to the current
population or claim measured temperatures from a wattage label or file check.

## 6. Functional And Documentation Rules

- Keep 41 stations / 82 LEDs and the **same-end** six-independent-end TEST
  [matrix in INSTALL](INSTALL.md#functional-matrix): Start A/C positive, Start B negative, End A/B/C each
  isolated. No direction selector, permanent End A/C strap or dual-B return.
- User now accepts LED damage from accidental low-voltage installation polarity
  errors, with spare indicators; reversed flying-lead survival is not required.
  Direct-strike rebuilding is accepted, not all ordinary/nearby transient damage.
  Continuous-safe normal TEST stays mandatory. The simple 16-part hybrid is now
  implemented in the source, not thermally/surge qualified. Do not reinstate the
  40-part investigation as a prerequisite or confuse reverse recovery with
  forward-clamp response. See ELECTRICAL section 9 and ASSEMBLY.
- Energized cattle fencing is **prohibited near the entire 4 km boundary,
  stations and hub** under [INSTALL's policy](INSTALL.md#cattle-fence-prohibition).
  The earlier close-parallel scenario is withdrawn; do not require testing a prohibited
  configuration or invent a safe separation distance. Verify and maintain the
  restriction, reassessing if land use changes. Ordinary RF/switching and
  nearby-lightning exposure, source recovery and site earthing remain relevant.
- Use **one TEST source and one disconnected spare**, not interconnected supplies.
  Follow [INSTALL's switch/source controls](INSTALL.md#switch-and-supply): exact
  DC/global-transfer approval remains open and extra switch poles are unassigned.
  Cable identity and red/black/plain-green colours are settled; use the current
  [manufacturer evidence](pcb/ENVIRONMENT_EVIDENCE.md), not older listings.
- Gel is **WISKA OneGel**, one-component/no mixing, not MP0100. Resolve its
  conflicting manufacturer cure/temperature fields; do not invent conductivity,
  compatible materials or completed thermal qualification. Source/temperature
  screens in [DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md) are declared assumptions, not
  enforced operating limits or manufacturer test conditions. Do not revive a
  historical source-window proposal or transfer prototype results to production.
- Preserve WAGO through-splice/PCB-tap wiring. Normal perimeter current does
  not pass through every PCB. Surge current is a separate design case.
- Normal TEST must be continuous-safe; do not substitute a timer. TEST/OFF
  disable containment, and restoring RUN is an operator action. OFF is not
  demonstrated storm isolation. Do not directly earth a core, switch PE or
  invent an unbonded-rod/DC-negative bonding design.
- Follow [Documentation Maintenance](#10-documentation-maintenance) for
  impact-based synchronization, and update REMEDIATION with actual evidence.
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

- Read the [hole-fit](pcb/ASSEMBLY.md#hole-fit-evidence) and
  [coordinate-based via controls](pcb/ASSEMBLY.md#stitching-via-identification)
  before changes. Preserve protected drills/copper; no fill-by-diameter request,
  via as a lead-insertion hole, forced insertion or reaming of finished PTHs.
- The selected process is **untented both sides, no fill/plug/cap, ENIG**, with
  no via paste. KiCad 9.0.7 uses flat `(tenting ...)` flags;
  nested side booleans and per-via mask-margin clauses fail native parsing.
- Compare full drill circles, annuli, copper and actual mask/paste apertures.
  Same-net via-aperture overlap never excuses component mask/paste over a hole.
  Inspect processed Gerbers/stencil too; native flags, opaque mask or gel do not
  prove a seal. Surface copper is not a guaranteed barrel-copper minimum.
- Preserve dimensional/tolerance evidence and supplier process holds in
  ASSEMBLY/DFM_EVIDENCE. Regenerate/inspect artifacts and run `make check` after
  design changes; documentation or DRC does not close physical acceptance.

## 10. Documentation Maintenance

Use the document responsibilities in **Start Here**. Maintain one authority per
kind of claim, not one occurrence per fact:

- REMEDIATION owns agreed requirements, issue/gate decisions and dated results;
  `pcb/verification.json` enforces machine release/diagnostic reviews. A template,
  model, stock listing or rewritten guide cannot close a hold.
- MATERIALS owns purchases, cancellations, quantities, receipts and allocation
  evidence. Do not propagate a purchase-status update into universal preambles.
  Preserve existing ORDERED/ON HAND history and distinguish current population
  from unimplemented production orders or candidates.
- BOM/CAD/libraries own PCB population; ASSEMBLY owns human guardrails and
  assembly requirements. Link their tables instead of maintaining overview copies.
  INSTALL owns full operating/diagnostic tables; ACCEPTANCE still specifies every
  test action, precondition, numerical acceptance criterion and required record.
- ELECTRICAL owns circuit/model explanations and named historical comparisons;
  DESIGN_BOUNDS owns current parametric screens; DFM/ENVIRONMENT notes own source
  evidence. Preserve case inputs, provenance and unknowns, not just the number.
- Keep concise local safety instructions, scope limitations, model assumptions,
  risk consequences and inspect/stop/record duties where the work is performed.
  They are intentional summaries, not permission to repeat purchasing narratives.
- Preserve historical research and session evidence, including later dated errata.
  Do not rewrite candidate calculations to match new purchases, freeze out real
  corrections, or revive rejected circuits as prototype prerequisites.
- Complete the destination before deleting a copy; check links and anchors and
  review semantic preservation against the original. All seven controlled notes
  ship flat, but root guides do not. Use shipped sibling links for essential
  release context; mark supplementary root-guide links as repository-only.
- Engineering changes still require all affected BOM/PCB/schematic/library,
  datasheet/description metadata, model/test, assembly and operating/qualification
  updates plus regenerated artifacts. This is impact-based, not a file-count cap.
  `--sync-metadata` does not update Datasheet/Description or approval hashes.
- Update this guide for tooling changes and REMEDIATION for actual verification.
  Changed controlled notes need a new matching artifact snapshot; no automatic
  annotation reapproval follows from Markdown edits. Run whole-workflow checks
  exclusively, with prototype last if leaving a current prototype package.
