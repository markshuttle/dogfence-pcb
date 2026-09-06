# JLCPCB Turnkey PCBA Ordering Guide
**Dog Fence Indicator & Surge 1.1.0 (63mm × 56mm)**

---

## 1. Scope & Ordering Strategy

This guide covers the turnkey manufacturing parameters, component matching, live stock tracking, and checkout procedures across two phases:
* **Phase 1 (Immediate Pilot): 5-Board Prototype Batch (100% Turnkey Assembled)** — For bench commissioning, mechanical dry-fit, and electrical verification before full rollout.
* **Phase 2 (Final Rollout): 40–50 Board Perimeter Production Run** — For permanent installation across the 40 perimeter milestone boxes (35 standard + 5 surge stations + 5–10 spares).

All 14 components on the board are assembled on the **Top Side** by JLCPCB, requiring **zero in-field or bench soldering**.

---

## 2. Automated 1-Command Production Build

Before uploading files to JLCPCB, generate fresh, verified production artifacts using the automated build script:

```bash
make all
```

This target runs KiCad's headless Design Rule Check (DRC) gate (`make check`) and exports all turnkey manufacturing artifacts into `build/`:
* **`build/Gerbers.zip`** — Master 2-layer Gerbers & Excellon drill files (Upload to PCB quote form).
* **`build/BOM.csv`** — Turnkey Pick-and-Place Bill of Materials (Upload to PCBA step).
* **`build/CPL.csv`** — Verified Pick-and-Place Centroid placement list (Upload to PCBA step).
* **`build/FlyTest.zip`** — Flying Probe Test package (contains `pcb.d356` netlist + Gerbers).
* **`build/pcb.d356`** — IPC-D-356 Electrical Test netlist (provide if CAM requests netlist testing).

---

## 3. JLCPCB PCB Fabrication Specifications

Go to **[jlcpcb.com/quote](https://jlcpcb.com/quote)** and upload **`build/Gerbers.zip`**.

Set the following options on the PCB specification form:

| Specification | Phase 1: Prototype (5 Boards) | Phase 2: Production (40–50 Boards) | Engineering Rationale & Longevity Benefit |
| :--- | :---: | :---: | :--- |
| **Base Material** | **FR-4** | **FR-4** | Standard fiberglass-reinforced epoxy laminate. |
| **Material / TG** | **FR-4 TG155 (Shengyi S1000H)** | **FR-4 High-TG 170 (S1000-2)** or **TG155 (S1000H)** | **Prototype:** S1000H (TG155) is standard stock at JLCPCB with no setup surcharge and excellent thermal/moisture stability.<br>**Production:** High-TG 170 minimizes Z-axis thermal expansion ($\le 2.5\%$) and maximizes anti-CAF resistance for 20–50 year outdoor buried ground humidity (-20°C to +50°C). |
| **Layers** | **2 Layers** | **2 Layers** | Top (Signal / Surge) & Bottom (Ground / Surge Return). |
| **Dimensions** | **63 mm × 56 mm** | **63 mm × 56 mm** | Auto-detected from Gerber files. |
| **PCB Quantity** | **5** | **40** (or 50) | **Prototype:** 5 is JLCPCB's minimum order quantity.<br>**Production:** 35 standard + 5 surge + 5–10 spares. |
| **Copper Weight** | **2 oz (70 µm)** | **2 oz (70 µm)** | **CRUCIAL INVARIANT:** 2× standard copper thickness. Essential for safely absorbing high lightning transients (20kA) and keeping 4km loop resistance ultra-low. |
| **Surface Finish** | **ENIG (Immersion Gold)** | **ENIG (Immersion Gold)** | **CRUCIAL:** 24k gold over nickel barrier prevents copper oxidation and terminal fretting permanently. |
| **Gold Thickness** | **1U"** (Standard) | **2U"** (2 micro-inches) | **Prototype:** 1U" is standard, cost-effective, and fully corrosion-resistant for test boards.<br>**Production:** 2U" provides a pore-free gold seal for multi-decade service life. |
| **Via Process / Covering** | **Solder Mask Plugged** (or Tented) | **Solder Mask Plugged** (or Tented) | **Freeze-Thaw Void Protection:** Solder mask plugging seals the via barrel hole, eliminating open air voids where moisture could collect.<br>*(See Engineering FAQ below on via conductivity).* |
| **Via Plating** | **Horizontal Electroless Copper** | **Horizontal Electroless Copper** | Automated conveyorized chemical deposition line ensuring dense, void-free copper barrels. |
| **Edge Rails / Panel** | **Added by JLCPCB (73×76mm)** | **Added by JLCPCB (73×76mm)** | **Required for Assembly:** Automated 5mm breakaway rails allow SMT conveyor clamping without contacting board edges. Breakaway tabs are cleanly removed post-assembly. |
| **Conformal Coating** | **No / Skip** | **No / Skip** | Redundant because boards are submerged in 100% solid silicone potting gel ([WISKA MP0100](MATERIALS.md)). |
| **Flying Probe Test** | **Fully Tested** | **Fully Tested** | 100% electrical continuity and isolation testing (free and automatic for 2-layer boards). |
| **Confirm Production File**| **Yes** | **Yes** | A CAM engineer manually verifies pick-and-place DFM alignment before manufacturing. |

> [!NOTE]
> **Engineering FAQ: Does "Plugged" provide more electrical conductivity than "Tented"?**
> **No.** Electrical conductivity through a via is determined **100% by the electroplated copper barrel wall thickness** (20–25 µm of copper deposited during plating), not the plugging material. Solder mask plugging uses **non-conductive dielectric ink** (epoxy/solder mask), which adds zero electrical conductivity. 
> 
> However, "Plugged" is strongly preferred over "Tented" for outdoor durability because it physically seals the hollow barrel cavity, preventing air/flux entrapment and eliminating freeze-thaw water expansion. Furthermore, because every board is fully submerged in **WISKA MP0100 silicone potting gel**, all vias are permanently encased in waterproof silicone elastomer regardless!

---

## 4. Turnkey PCB Assembly (PCBA) Settings & Matched Parts

1. On the JLCPCB quote page, enable the toggle for **"PCB Assembly"**.
2. **Assembly Side**: **Top Side** (all 14 components are on the top layer).
3. **PCBA Quantity**: **5** (Select 5 fully assembled boards for the prototype run; select 40 for production).
4. **Tooling Holes**: "Added by JLCPCB".
5. **Assembly Note**: In the JLCPCB PCBA special assembly notes, specify that axial component GDT_AC leads must be pre-formed to enforce a ≥ 2.0 mm vertical air gap standoff above the PCB surface.
5. Upload **`build/BOM.csv`** and **`build/CPL.csv`**.

> [!WARNING]
> ### ⚠️ URGENT LIVE STOCK ALERT: Ruilon SMD5050-470NA (`C39692533`)
> A real-time inventory audit at JLCPCB/LCSC indicates that **`C39692533` (SMD5050-470NA)** has **only 20 units remaining in stock**!
> * **For the 5-Board Prototype Order:** 5 boards require 10 pcs + tape feeder waste allowance (~12–15 pcs). **Your 5-board prototype order will succeed if placed promptly**, but stock will be virtually exhausted afterward.
> * **For the Future 40-Board Production Order:** 40 boards require 80 pcs. This part **must be pre-ordered** into your JLCPCB Private Library (or substituted with Littelfuse `SH470` via JLCPCB Global Sourcing) before placing the 40-board run. See [Section 7](#7-pre-ordering-for-the-future-40-board-production-run).

### Verified Component Match List:

| Designator | Component Name | JLCPCB Part # | Manufacturer & MPN | Live Stock | Specs & Technology |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **`D1`, `D2`** | 1000V 1A Diode | **`C232439`** | onsemi / LGE `1N4007G` | **27,330** (Abundant) | DO-41, 1kV 1A, Glass Passivated, -65°C to +175°C |
| **`GDT_AB`, `GDT_BC`** | Inter-Core SMT GDT | **`C39692533`** | Ruilon `SMD5050-470NA` | ⚠️ **20 (LOW)** | 470V, 5kA (8/20 µs), <1.5pF, 5.0×5.0mm SMT |
| **`GDT_AC`** | Inter-Core Axial GDT | **`C5337217`** | Bencent `B5G470L` | **180** (Healthy) | 470V, 5kA (8/20 µs), <1.5pF, $\Phi 5.5\text{mm} \times 6\text{mm}$ Axial THT |
| **`GDT_A_E`, `GDT_B_E`, `GDT_C_E`** | Line-to-Earth 20kA GDT | **`C2836978`** | Ruilon `2R470TD-8` | **6,052** (Abundant) | 470V, 20kA (8/20 µs), <1.5pF, $\Phi 8.0\text{mm} \times 6\text{mm}$ Axial THT |
| **`R1`, `R2`** | 2.2kΩ 1W Resistor | **`C1368610`** | Vishay `MBE04140C2201FC100` | **875** (Abundant) | 1W Metal Film 1% Axial Through-Hole (DIN 0414) |
| **`J_IN`, `J_EARTH`** | 3-Pin 7.62mm Terminal | **`C474957`** | Cixi Kefa `KF128-7.62-3P` | **3,505** (Abundant) | 24A 300V Heavy Duty, 7.62mm pitch rising cage |
| **`J_LED_A`, `J_LED_C`** | 2-Pin 5.08mm Terminal | **`C475092`** | Cixi Kefa `KF129-5.08-2P` | **20,515** (Abundant) | 24A 250V Heavy Duty, 5.08mm pitch rising cage |

### Estimated Prototype Cost Breakdown (5 Fully Assembled Boards)
* **5× Bare PCBs (2 oz Cu, ENIG, TG155):** ~$25 – $32
* **SMT & THT Assembly Base Fee:** ~$8.00
* **Extended Component Loading Fees (6–7 unique lines @ $3/line):** ~$18 – $21
* **Manual Through-Hole Soldering & Components:** ~$15 – $25
* **Estimated Total Turnkey PCBA Cost:** **~$70 – $90** for 5 fully assembled, ready-to-test boards.

---

## 5. 3D Preview Visual Verification

In the JLCPCB 3D placement review screen, verify the physical orientation of all 14 components:

```
                            [ 3D PLACEMENT CHECK ]
       Wire Openings Face OUTWARDS (Up)
               ▲
               │
          ┌─────────┐
          │ J_LED_A │  (Rotation 90°: opens North)
          │  [+ -]  │  [Pad 1: Left (+), Pad 2: Right (-)]
          └─────────┘
  ┌──────┐                                ┌─────────┐
  │ J_IN │ (Rotation 0°)                  │ J_EARTH │ (Rotation 180°)
  │(1,2,3│ Wire openings                  │ (1,2,3) │ Wire openings
  │face  │ face LEFT ◄──                 ──► face   │
  │LEFT) │                                │  RIGHT  │
  └──────┘                                └─────────┘
          ┌─────────┐
          │ J_LED_C │  (Rotation 270°: opens South)
          │  [+ -]  │  [Pad 1: Left (+), Pad 2: Right (-)]
          └─────────┘
               │
               ▼
       Wire Openings Face OUTWARDS (Down)
```

1. **`J_LED_A` & `J_LED_C` (2-Pin 5.08mm Terminals):**
   * Wire openings face **OUTWARDS** from the board (vertically mirrored geometry across $Y = 122.50\text{ mm}$).
   * **`J_LED_A` (top):** Rotation **`90°`** (wire opening faces **UP / North** toward the top edge).
   * **`J_LED_C` (bottom):** Rotation **`270°`** (wire opening faces **DOWN / South** toward the bottom edge).
   * **Polarity Consistency:** On both connectors, **Pad 1 (Anode `+`) is on the Left** ($X = 142.96\text{ mm}$) and **Pad 2 (Cathode `-`) is on the Right** ($X = 148.04\text{ mm}$).
2. **`J_IN` (3-Pin 7.62mm Input Terminal):**
   * Rotation **`0°`**. Wire openings face **LEFT** (toward the outer board edge). Pin 1 (Wire A) is at the top ($Y=114.88\text{ mm}$), Pin 2 (Wire B) is in the middle ($Y=122.50\text{ mm}$), Pin 3 (Wire C) is at the bottom ($Y=130.12\text{ mm}$).
3. **`J_EARTH` (3-Pin 7.62mm Ground Terminal):**
   * Rotation **`180°`**. Wire openings face **RIGHT** (toward the outer board edge).
4. **`D1` & `D2` (1N4007G Diodes):**
   * The **white cathode band points RIGHT** (toward the `+` pad / LED terminal).
5. **`GDT_AC` (Axial Arrester):**
   * Axial body bridges across Wire B with a visible vertical air gap ($\ge 2.0\text{ mm}$) above the board surface.
6. **`GDT_AB` & `GDT_BC` (SMT GDTs):**
   * Centered squarely on SMD pads at rotation `0°`.

*(If any 3D model appears misoriented, use the rotate/offset tool in the JLCPCB viewer to snap it into place; CAM engineers will also review orientation against silkscreen markers during pre-production DFM review).*

---

## 6. Prototype Acceptance & Bench Testing (Next Step)

Once your 5 prototype boards arrive, execute the formal bench acceptance and commissioning protocol detailed in:

👉 **[`ACCEPTANCE.md`](ACCEPTANCE.md)**

This protocol walks you through:
1. **Visual & Mechanical Acceptance** (de-paneling, solder fillets, standoff fit).
2. **Cold DMM Checks** (rail continuity, spark gap $>100\text{ M}\Omega$ isolation, diode checks).
3. **Powered +36V DC Commissioning** (15mA LED current, thermal stability, reverse-polarity cutoff).
4. **WISKA COMBI 308 Enclosure Dry-Fit** (Essentra 9.5mm standoffs and APEM LED wire clearance).

---

## 7. Pre-Ordering for the Future 40-Board Production Run

Because `GDT_AB / GDT_BC` (`C39692533`) will be depleted by prototype orders, use JLCPCB's Global Sourcing feature to pre-order components for the final 40-board run while your prototypes are in transit:

1. Log into your **[JLCPCB Account](https://jlcpcb.com)** and navigate to **User Center $\rightarrow$ Parts Manager $\rightarrow$ Global Sourcing** (or **Order Parts**).
2. Pre-order the required parts into your **"My Parts Lib"** (private Shenzhen inventory):
   * **Inter-Core SMT GDT:** Ruilon `SMD5050-470NA` (Qty: 100 pcs) or Littelfuse `SH470` (Qty: 100 pcs).
   * *(Optional Multi-Decade Upgrades):* Phoenix Contact Reakdyn terminals (`1731734`, `1715721`) or Vishay Superectifier diodes (`1N4007GP-E3/54`). See **[`README.md`](README.md) Section 5** for full MPN details.
3. Sourcing typically takes **5 to 10 business days**.
4. When your 5 prototype boards pass **[`ACCEPTANCE.md`](ACCEPTANCE.md)** and the pre-ordered parts arrive in your private library, proceed to Section 8.

---

## 8. How to Place the 40-Board Production Run in 1 Click

1. Go to **[JLCPCB Order History](https://jlcpcb.com)**.
2. Locate your prototype order (**Dog Fence Indicator & Surge 1.1**) and click **"Re-order"** (or create a new quote using `build/Gerbers.zip`).
3. Set **PCB Quantity to 40** (or 50) and **PCBA Quantity to 40**.
4. Select **FR-4 High-TG 170 (S1000-2)** or **TG155 (S1000H)**, **2 oz Cu**, and **ENIG 2U"**.
5. Upload `build/BOM.csv` and `build/CPL.csv`. The system will automatically allocate your private inventory parts alongside active warehouse stock.
6. Checkout and approve CAM production files!
