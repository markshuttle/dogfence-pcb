# JLCPCB Turnkey PCBA Ordering Guide
**Dog Fence Indicator & Surge 1.0.2 (60mm × 45mm)**

This guide captures all exact fabrication parameters, high-reliability materials, component matches, and repeat-order steps for turnkey manufacturing.

---

## 1. Automated 1-Command Production Build

You can generate and package the complete JLCPCB manufacturing package with a single terminal command:

```bash
make
```

This automatically generates the `build/` directory with all verified files ready for upload:
* **`build/Gerbers.zip`** — Master 2-layer Gerbers & Excellon drill files.
* **`build/BOM.csv`** — Verified PCBA Bill of Materials.
* **`build/CPL.csv`** — Verified Pick-and-Place Centroid component positions.
* **`build/FlyTest.zip`** — Flying Probe Test package (contains `pcb.d356` netlist + Gerbers).
* **`build/pcb.d356`** — IPC-D-356 Electrical Test netlist.

---

### Manual GUI Export Steps (Alternative):
1. **Gerbers:** In KiCad PCB Editor, **File → Fabrication Outputs → Gerbers (.gbr)...** (Layers: `F.Cu`, `B.Cu`, `F.SilkS`, `B.SilkS`, `F.Mask`, `B.Mask`, `Edge.Cuts`).
2. **Drills:** In the same dialog, click **Generate Drill Files...** (Excellon, Millimeters, Separate PTH/NPTH).
3. **IPC-D-356:** **File → Fabrication Outputs → IPC-D-356 Netlist File (.d356)...**
4. **CPL Position:** **File → Fabrication Outputs → Component Placement (.pos)...** (Format: CSV, Units: mm).

---

## 2. JLCPCB PCB Fabrication Options

Go to **[jlcpcb.com/quote](https://jlcpcb.com/quote)** and upload **`Gerbers.zip`**.

Set the following options on the PCB specification form:

| Option | Selected Value | Engineering Rationale / Longevity Benefit |
|:---|:---|:---|
| **Base Material** | **FR-4** | Standard fiberglass reinforced epoxy. |
| **Material / TG** | **S1000H TG155** (Shengyi) | **Crucial:** High glass transition temp (155°C) with low Z-axis thermal expansion and high moisture/anti-CAF resistance for extreme outdoor climate swings (-20°C to +50°C). |
| **Layers** | **2 Layers** | Top (Signal/Surge) & Bottom (Ground/Surge Return). |
| **Dimensions** | **60 mm × 45 mm** | Auto-detected from Gerber files. |
| **PCB Quantity** | **40** (or 50) | 35 standard milestones + 5 surge milestones + interchangeable spares. |
| **Copper Weight** | **2 oz (70 µm)** | **Crucial:** 2× standard copper thickness. Essential for safely absorbing high lightning surge transients and minimizing resistance across the 4km run. |
| **Surface Finish** | **ENIG (Electroless Nickel Immersion Gold)** | **Crucial:** 24k gold over nickel prevents copper oxidation and contact corrosion permanently. |
| **Gold Thickness** | **2U" (2 micro-inches)** | Pore-free gold seal providing maximum long-term environmental protection. |
| **Via Covering** | **Tented** | Solder mask covers all via annular rings to prevent moisture ingress. |
| **Via Plating** | **Horizontal Electroless Copper Plating** | Automated conveyorized chemical deposition line ensuring uniform, void-free copper barrels. |
| **Edge Rails / Fiducials** | **Added by JLCPCB (70×71mm temporary panel)** | Automated breakaway rails for assembly machines; final board remains 60×45mm. |
| **Conformal Coating** | **No / Skip** | Redundant because boards are submerged in 100% solid silicone potting gel in the WISKA boxes. |
| **Flying Probe Test** | **Fully Tested** | 100% electrical continuity and isolation testing. |
| **Confirm Production File** | **Yes** | A CAM engineer manually verifies pick-and-place alignment before manufacturing. |

---

## 3. PCB Assembly (PCBA) Settings & Matched Parts

1. On the quote page, enable the toggle for **"PCB Assembly"**.
2. **Assembly Side**: **Top Side** (all 11 components are on top).
3. **PCBA Quantity**: **40**.
4. Upload **`pcb/BOM.csv`** and **`pcb/CPL.csv`**.

### Verified Component Match List:

| Designator | Component Name | JLCPCB Part # | Manufacturer & Model | Specs |
|:---|:---|:---|:---|:---|
| **`D1`, `D2`** | 1000V 1A Diode | **`C232439`** | 1N4007G (Glass Passivated) | DO-41, 1kV 1A, -65°C to +175°C |
| **`GDT1`, `GDT2`, `GDT3`** | Surge Arrestor | **`C2836978`** | Ruilon 2R470TD-8 | 470V, 20kA (8/20 µs), <1.5pF |
| **`R1`, `R2`** | 2.2kΩ 1W Resistor | **`ASSIGN_BY_JLCPCB`** | Uni-Royal / Yageo (MFR01SF2201A10) | 1W Metal Film 1% Axial Through-Hole |
| **`J_EARTH`, `J_LED_A`, `J_LED_C`** | 2-Pin Screw Terminal | **`C475092`** | Cixi Kefa KF129-5.08-2P | 24A 250V Heavy Duty, M3 Screws |
| **`J_IN`** | 3-Pin Screw Terminal | **`C474953`** | Cixi Kefa KF128-5.08-3P | 24A 250V Heavy Duty |

> [!TIP]
> **Resistor Matching on JLCPCB:** In the JLCPCB SMT/Assembly parts assignment screen, JLCPCB dynamically matches $R_1, R_2$ to their active in-stock 2.2kΩ 1W through-hole axial metal film resistor (search keyword `2.2k 1W` if prompted, or let the CAM engineer assign it during DFM file review).

---

## 4. 3D Preview Visual Verification

In the JLCPCB 3D placement screen:
1. **`J_LED_A` & `J_LED_C`**: Wire openings face **outwards** from the board — mirrored pair geometry. **CPL rotation `270°` for `J_LED_A` (opens toward the top edge) and `90°` for `J_LED_C` (opens toward the bottom edge)**. The silkscreen `+`/`-` markers remain the authoritative polarity guide for both.
2. **`J_IN`**: Wire openings face **Left** (toward board edge).
3. **`J_EARTH`**: Wire openings face **Down** (toward bottom edge).
4. **`D1` & `D2`**: White cathode band points **Right** (toward the `+` square pad).
*(If any 3D model appears rotated, use the 90° rotate tool in the top bar to snap it into position; the CAM engineer will also verify this during pre-production DFM review).*

---

## 5. How to Place a 1-Click Repeat Order in Future

1. Log into your **[JLCPCB Account](https://jlcpcb.com)**.
2. Go to **Order History / Order List**.
3. Locate this order (**Dog Fence Indicator & Surge 1.0**) and click **"Re-order"** (or "Order Again").
4. The system automatically loads the saved production package, Gerber stackup, S1000H TG155 material, 2 oz copper, 2U" ENIG gold, BOM, and CPL alignment.
5. Select your new quantity (e.g. 20 or 50) and checkout in 1 click!
