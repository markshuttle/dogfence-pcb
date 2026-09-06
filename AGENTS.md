# Dog Fence Indicator & Surge Protection System (v1.1.0)
**Agent & Developer Operating Briefing & Environment Guide**

---

## 1. Document Scope & Target Audience

This document serves as the operational guide and environment manual for **AI coding agents** (e.g., Antigravity, Cursor, Claude Code, GitHub Copilot) and **human developers** working on this repository.

* For the **master engineering specification**, circuit theory, dual-mode operational analysis, complete hardware bill of materials, PCB fabrication rules, and field installation architecture, see **[`README.md`](README.md)**.
* For step-by-step physical installation instructions, see **[`INSTALL.md`](INSTALL.md)**.
* For turnkey JLCPCB / PCBWay manufacturing instructions, see **[`ORDERING.md`](ORDERING.md)**.
* For procurement and hardware tracking, see **[`MATERIALS.md`](MATERIALS.md)**.
* For failure modes, reverse-flow, and lightning surge risk analysis, see **[`RISKS.md`](RISKS.md)**.

---

## 2. Operating System & Desktop Environment Conventions

* **Host OS**: Ubuntu Linux (tested and verified on Ubuntu Desktop 24.04 / 26.04 LTS).
* **Execution Context**: Agents and automation scripts operate within the standard desktop user space (`$HOME = /home/<username>`) with non-root privileges.
* **Shell & Core Utilities**:
  * Default shell: `bash`.
  * Build system: GNU Make (`make`).
  * Packaging utilities: `zip`, `git`, standard POSIX utilities (`cp`, `rm`, `mkdir`, `sed`, `grep`).
* **Headless Execution Invariant**:
  * All automated agent tasks **must run headlessly** via CLI commands.
  * **Do not** attempt to invoke interactive graphical desktop applications (e.g., launching the interactive `kicad` GUI editor, `pcbnew`, or `eeschema`).
  * All design rule checks (DRC), netlist exports, Gerber generation, and drill outputs must be executed using headless CLI tooling (`kicad-cli` via `make`).

---

## 3. KiCad Snap Architecture & Confinement Constraints

The system relies on KiCad 9 (or KiCad 8) installed as an **Ubuntu Snap package** (`snap install kicad`).

### Strict Snap Confinement Restrictions
Ubuntu Snaps execute inside an AppArmor-enforced security sandbox with `strict` confinement:
1. **No Access to System `/tmp` or Root Paths**:
   * The KiCad Snap **cannot access** `/tmp`, `/var/tmp`, `/run`, or arbitrary directories outside `$HOME`.
   * Passing paths such as `/tmp/drc_report.txt` or `/tmp/gerbers/` to `kicad-cli` will fail immediately with permission-denied or file-not-found errors.
2. **No Access to Hidden Dot-Directories**:
   * The KiCad Snap is restricted from accessing hidden directories within `$HOME` (e.g., `~/.gemini/`, `~/.tmp/`, `~/.local/`, or `.workshop/`).
3. **Allowed Paths**:
   * The Snap can **only** read and write files located within standard, unhidden user directories inside `$HOME` (e.g., `$(HOME)/dogfence_kicad_tmp` or the workspace `/home/<username>/projects/...`).

### Staging Protocol & Temporary Files
* **Never invoke `kicad-cli` directly targeting `/tmp` or hidden directories.**
* The repository's **[`Makefile`](Makefile)** automatically implements the required Snap staging protocol:
  * Creates an unhidden temporary directory: `$(HOME)/dogfence_kicad_tmp`
  * Copies the required `.kicad_pcb` or `.kicad_sch` files into the staging directory.
  * Executes `kicad-cli` within the staging directory.
  * Copies generated outputs back into `build/`.
  * Tears down `$(HOME)/dogfence_kicad_tmp` upon completion.
* When executing custom KiCad automation, always use `make` targets or replicate this staging protocol.

### CLI Binary Resolution Priority
The `Makefile` resolves the `kicad-cli` binary across environments in this prioritized sequence:
```makefile
KICAD_CLI ?= $(shell \
	if command -v kicad-cli >/dev/null 2>&1; then echo kicad-cli; \
	elif command -v kicad.kicad-cli >/dev/null 2>&1; then echo kicad.kicad-cli; \
	elif [ -x /snap/bin/kicad.kicad-cli ]; then echo /snap/bin/kicad.kicad-cli; \
	elif [ -x /snap/kicad/current/usr/bin/kicad-cli ]; then echo /snap/kicad/current/usr/bin/kicad-cli; \
	elif command -v flatpak >/dev/null 2>&1 && flatpak info org.kicad.KiCad >/dev/null 2>&1; then echo "flatpak run --command=kicad-cli org.kicad.KiCad"; \
	else echo kicad-cli; fi)
```

---

## 4. Build, DRC, and Verification Workflow

### Mandatory Inline DRC Gate (`make check`)
Whenever any modification is made to the PCB layout (`pcb/pcb.kicad_pcb`) or schematic (`pcb/pcb.kicad_sch`), the changes **must be validated** by running:
```bash
make check
```
* The DRC gate runs `kicad-cli pcb drc --format report --severity-error --exit-code-violations`.
* **Zero violations rule**: If any DRC error or courtyard violation is detected, the command exits with non-zero status and halts the export.
* The resulting report is written to `build/drc_report.txt`.

### Turnkey Manufacturing Package (`make all` / `make package`)
To build the complete turnkey package ready for JLCPCB or PCBWay upload:
```bash
make all
```
This target:
1. Runs `make check` (blocks on any DRC violation).
2. Exports all 2-layer Gerber files into `build/gerbers/`.
3. Exports PTH and NPTH Excellon drill files into `build/gerbers/`.
4. Exports IPC-D-356 electrical test netlist into `build/pcb.d356`.
5. Packages `pcb/BOM.csv` into `build/BOM.csv`.
6. Exports pick-and-place centroid coordinates into `build/CPL.csv`.
7. Compresses Gerbers and drills into `build/Gerbers.zip` (and mirrors to `pcb/Gerbers.zip`).
8. Packages `build/FlyTest.zip` for JLCPCB electrical probe testing.

To clean generated artifacts:
```bash
make clean
```

---

## 5. Critical Electrical & Physical Invariants (Guardrails)

When modifying schematics or PCB layouts, agents must strictly uphold the following hard design constraints:

1. **Copper Weight**:
   * Must remain **2 oz (70 µm)** on both top (`F.Cu`) and bottom (`B.Cu`) layers.
2. **Tri-Rail Symmetrical Copper Stitching**:
   * Conductors Wire A, Wire B, and Wire C must maintain **100% full 3.2mm width** across both copper layers.
   * Dedicated clusters of **3× heavy plated stitching vias** (1.0mm drill, 1.8mm pad) at X=112.5, 114.0, 115.5mm on each rail must never be deleted or shrunk.
3. **Earth Bus Stitching**:
   * The 4.5mm Earth bus must maintain its column of **5× heavy plated stitching vias** (1.0mm drill, 1.8mm pad) at X=150.0mm, stitching the top and bottom layers into a monolithic ground network.
4. **Line-to-Earth 20kA GDT Pitch (9.0mm)**:
   * `GDT_A_E` and `GDT_C_E` must remain spaced at Y=113.50mm and Y=131.50mm (**9.00mm center-to-center pitch**).
   * **Do not compress this pitch**: 9.00mm is required to provide a 1.00mm physical air gap and 0.50mm courtyard clearance between the heavy-duty $\Phi 8.0\text{mm} \times 6\text{mm}$ ceramic bodies of the Ruilon 2R470TD-8 arresters.
5. **Surge Clearance Invariant (≥3.0mm)**:
   * The Wire B LED return traces on `B.Cu` run westward at X=135.50mm to provide **4.31mm copper clearance** to the Earth GDT pins and **3.70mm clearance** to the Earth bus.
   * Clearance between fence conductors and the Earth ground bus must never drop below 3.0mm.
6. **Axial Arrester GDT_AC Standoff**:
   * `GDT_AC` bridges over the top copper trace of Wire B. Axial leads must be formed to maintain a **≥2.0mm vertical air gap standoff** above the board surface.
7. **Component Matches & Ratings**:
   * Rectifier Diodes (`D1`, `D2`): **1N4007G** (1000V / 1A glass-passivated DO-41).
   * Resistors (`R1`, `R2`): **2.2kΩ 1W Metal Film 1%** (derated to 50% power).
   * Differential GDTs (`GDT_AB`, `GDT_BC`): **Ruilon SMD5050-470NA** (5kA / 470V SMT).
   * Differential GDT (`GDT_AC`): **Ruilon 2RA470-L5.5** (5kA / 470V axial $\Phi 5.5\text{mm} \times 6\text{mm}$).
   * Common-Mode GDTs (`GDT_A_E`, `GDT_B_E`, `GDT_C_E`): **Ruilon 2R470TD-8** (20kA / 470V axial $\Phi 8.0\text{mm} \times 6\text{mm}$).
   * Input Terminal (`J_IN`): **KF128-7.62-3P** (3-pin 7.62mm pitch, 24A / 300V).
   * Earth Terminal (`J_EARTH`): **KF128-7.62-3P** (all 3 pins tied in parallel for 72A rating).
   * LED Terminals (`J_LED_A`, `J_LED_C`): **KF129-5.08-2P** (2-pin 5.08mm pitch, 24A / 250V).

---

## 6. Documentation & Synchronization Protocol

Whenever schematic components, footprint geometry, or layout routing are modified:
1. Update `pcb/BOM.csv` and `pcb/CPL.csv` to match component designations and centroid coordinates.
2. Synchronize technical parameters in **[`README.md`](README.md)**.
3. Update part tracking in **[`MATERIALS.md`](MATERIALS.md)** and fabrication notes in **[`ORDERING.md`](ORDERING.md)**.
4. If electrical modes or risk profiles change, update **[`RISKS.md`](RISKS.md)**.
5. If operating environment, tooling, or build scripts change, update this file (**[`AGENTS.md`](AGENTS.md)**).
