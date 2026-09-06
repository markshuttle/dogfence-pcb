# Dog Fence Indicator & Surge Protection System (v1.1.0)
**Project Knowledge Base & Agent Briefing**

---

## 1. Project Overview & Intent

This project implements a high-reliability, long-distance **4km (~2.5 miles) hidden perimeter dog containment fence** powered by the **DogWatch SmartFence** system.

The fence boundary is formed by a continuous outdoor **3-core 2.5mm² cable** installed in a closed loop. All three internal copper conductors (Wire A, Wire B, Wire C) run in parallel, providing an effective total cross-sectional area of **7.5mm² (~8 AWG)** and an ultra-low total loop resistance of **≈ 9.3 Ω**, well within the DogWatch transmitter driving threshold (<30 Ω).

To simplify long-term diagnostics, fault isolation, and lightning protection across 4 kilometres of rural terrain, **40 milestone junction boxes** are installed along the perimeter:
- **35 Standard Diagnostic Milestones** (every ≈ 100m): Provide visual green LED status indicators for Wires A and C, plus full inter-core differential surge protection across all conductors.
- **5 Surge & Grounding Milestones** (at 0m, 1km, 2km, 3km, 4km): In addition to visual diagnostics and inter-core surge protection, these stations connect via a mirrored 3-pin heavy-duty terminal block to deep-driven copper earth ground rods to safely discharge lightning and static energy to ground without affecting fence operation.

All 40 junction boxes use an identical, unified **"Dog Fence Indicator & Surge 1.1" PCB (v1.1.0)**.

---

## 2. Core Philosophy & Design Goals

1. **20+ Year Outdoor Lifespan**: Zero compromise on durability. Materials are rated for -40°C to +90°C+ temperature swings, moisture, UV, and ground humidity.
2. **Zero In-Field Soldering**: 100% turnkey factory assembly (PCBA) by JLCPCB/PCBWay. Field installation requires only a screwdriver.
3. **Dual-Mode Operation (RF RUN Mode vs. DC TEST Mode)**:
   - In **RUN Mode**, the board is electrically invisible to the DogWatch transmitter's 4–10 kHz RF signal (<1.5 pF capacitance load per GDT, zero antenna grounding).
   - In **TEST Mode**, an injected +36V DC supply illuminates milestone LEDs sequentially down the perimeter. If a core breaks, all downstream LEDs go dark, pin-pointing the exact 100m fault location immediately.
4. **Full 6-GDT Hybrid Surge Protection**:
   - **3× Core-to-Core Differential GDTs** (`GDT_AB`, `GDT_BC`, `GDT_AC` rated at 5kA) clamp lightning-induced potential differences between adjacent conductors.
   - **3× Line-to-Earth Common-Mode GDTs** (`GDT_A_E`, `GDT_B_E`, `GDT_C_E` rated at 20kA) divert catastrophic ground surges to external earth rods.
5. **Hermetic Enclosure & Potting**: Housed in IP66/IP67 **WISKA COMBI 308** junction boxes, backfilled with re-enterable two-part silicone potting gel (**WISKA MP0100**) for submersible **IP68 hermetic sealing**.

---

## 3. Electrical Architecture & Dual-Mode Circuitry

```
                 [ +36V DC in TEST Mode / RF Signal in RUN Mode ]
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           │                            │                            │
     [ Wire A (Core 1) ]          [ Wire B (Core 2) ]          [ Wire C (Core 3) ]
           │                            │                            │
    [ 3x Stitch Vias ]           [ 3x Stitch Vias ]           [ 3x Stitch Vias ]
     (Top <-> Bottom)             (Top <-> Bottom)             (Top <-> Bottom)
           │                            │                            │
           ├────────[ GDT_AB (5kA) ]────┤                            │
           │                            ├────────[ GDT_BC (5kA) ]────┤
           ├────────────────────────────┴────────[ GDT_AC (5kA) ]────┤
           │                    (Axial arches over Wire B)           │
           │                            │                            │
    ┌──────┴──────┐                     │                     ┌──────┴──────┐
    │             │                     │                     │             │
[ 2.2kΩ 1W ]  [ GDT_A_E ]               │                 [ 2.2kΩ 1W ]  [ GDT_C_E ]
   (R1)       (470V 20kA)               │                    (R2)       (470V 20kA)
    │             │                     │                     │             │
[ 1N4007G ]       │                     │                 [ 1N4007G ]       │
   (D1)           │                     │                    (D2)           │
    │             │                     │                     │             │
[ LED A (+) ]     │                     │                 [ LED C (+) ]     │
    │             │                     │                     │             │
[ LED A (-) ]     │                     │                 [ LED C (-) ]     │
    │             │                     │                     │             │
    └──────┬──────┘                     │                     └──────┬──────┘
           │                            │                            │
           └──────────────────[ Wire B (DC 0V Return) ]──────────────┘
                                        │
                                   [ GDT_B_E ]
                                   (470V 20kA)
                                        │
                                        ▼
                             [ 4.5mm EARTH BUS (2 oz Cu) ]
                                 [ 5x Stitch Vias ]
                                  (Top <-> Bottom)
                                        │
                            [ J_EARTH (3-Pin 7.62mm) ]
                             (Pins 1, 2, 3 in Parallel)
                                        │
                             (To External Earth Rod
                             at Surge Milestones only)
                                        │
                                        ▼
                                  [ Ground Rod ]
```

### Modes of Operation

#### Mode 1: RUN Mode (SmartFence Transmitter Active)
* **Signal**: AC RF Carrier (4 kHz or 10.7 kHz), ≈ 10–20V RMS.
* **Resistor-Diode Rungs**: Total resistance per milestone rung ≈ 2.2 kΩ. Total parallel impedance of 40 milestones is ≈ 55 Ω, drawing negligible differential RF current because Wire A and B are driven at identical potentials.
* **GDT Capacitance**: <1.5 pF per GDT (<9 pF per milestone, <360 pF total across entire 4km perimeter). Completely RF transparent.
* **Ground Isolation**: Earth ground is completely decoupled from the fence antenna loop by the GDTs' 470V gas discharge spark gaps.

#### Mode 2: TEST / Fault-Finding Mode (+36V DC Injected)
* **Switchboard State**: Disconnects DogWatch transmitter; injects +36V DC onto Wires A and C, with Wire B acting as the DC 0V ground return.
* **LED Current**: I = (36V - 2.1V - 0.7V) / 2.2kΩ ≈ 15.0 mA per LED.
* **Power Dissipation**: P = I²R ≈ 0.50W (The 1W-rated metal film resistors run cool at 50% capacity).
* **Fault Detection**: If Wire A breaks at 1.4km, LED A illuminates at boxes 0m–1.3km and stays OFF at 1.4km–4.0km.

---

## 4. Hardware Component Selection & Specifications

Every part on the board was specifically chosen for heavy-duty industrial endurance:

| Designator | Component Description | Selected Part | Key Durability Attributes |
|:---|:---|:---|:---|
| **`D1`, `D2`** | 1000V 1A Rectifier Diode | **1N4007G** (LCSC: `C232439`) | **Glass-passivated junction (`G` suffix)**, -65°C to +175°C, 30A forward surge (IFSM). |
| **`GDT_AB`, `GDT_BC`** | Core-to-Core SMT Arrester | **Ruilon SMD5050-470NA** (JLCPCB: `C39692533`) | **5,000A (5kA)** impulse surge (8/20 µs), 470V breakdown, <1.5 pF, 5.0×5.0mm SMT package. |
| **`GDT_AC`** | Core-to-Core Axial Arrester | **Ruilon 2RA470-L5.5** (JLCPCB: `C52741208`) | **5,000A (5kA)** impulse surge (8/20 µs), 470V breakdown, compact axial body ($\Phi 5.5\text{mm} \times 6\text{mm}$), bridges Wire B. |
| **`GDT_A_E`, `GDT_B_E`, `GDT_C_E`** | Line-to-Earth 20kA Arrester | **Ruilon 2R470TD-8** (JLCPCB: `C434855` / LCSC: `C2836978`) | **20,000A (20kA)** impulse surge (8/20 µs), 470V breakdown, heavy-duty axial body ($\Phi 8.0\text{mm} \times 6\text{mm}$). |
| **`R1`, `R2`** | 2.2kΩ Current Limiter | **1W Metal Film 1%** (MPN: `MFR01SF2201A10`) | 1W power rating (operates at ≈0.50W, 50% capacity), 350V working voltage, ±50ppm/°C temperature coefficient. |
| **`J_IN`, `J_EARTH`** | 3-Pin 7.62mm Pitch Screw Terminals | **Cixi Kefa KF128-7.62-3P** (JLCPCB: `ASSIGN_BY_JLCPCB`) | **24A / 300V Heavy Duty**, M3 steel clamping screws, 7.62mm pitch for high-voltage creepage & clearance. `J_EARTH` has all 3 pins tied in parallel (72A rating) for contact redundancy. |
| **`J_LED_A`, `J_LED_C`** | 2-Pin 5.08mm Screw Terminals | **Cixi Kefa KF129-5.08-2P** (JLCPCB: `C475092`) | **24A / 250V Heavy Duty**, M3 steel clamping screws, -40°C to +105°C. |

---

## 5. PCB Layout & Fabrication Rules

* **Board Dimensions**: 60.0 mm × 52.0 mm.
* **Mounting**: 4× M3 mounting holes (3.2mm drill) with 6.4mm courtyard clearance at (103.5, 100.0), (156.5, 100.0), (103.5, 145.0), (156.5, 145.0).
* **Substrate**: Shengyi **S1000H High-TG (TG155)** FR-4 laminate (low thermal expansion, anti-CAF, high moisture resistance).
* **Copper Weight**: **2 oz (70 µm)** on both top and bottom layers for high surge current absorption.
* **Plating**: **ENIG 2U" (Electroless Nickel Immersion Gold)** — real 24k gold over nickel prevents copper oxidation for 20+ years.
* **Plating Line**: **Horizontal Electroless Copper Plating** (ensures dense, void-free through-hole copper barrels).
* **Tri-Rail Symmetrical Copper Stitching**: Wires A, B, and C each retain 100% full 3.2mm width across both `F.Cu` and `B.Cu` layers (no waist relief). Each wire conductor features a dedicated cluster of **3× heavy plated stitching vias** (1.0mm drill, 1.8mm pad) directly at the SMT GDT junctions (at X=112.5, 114.0, 115.5mm). This guarantees that both front and back 2 oz copper layers are fully engaged with minimal transient inductance and maximum surge current absorption.
* **Earth Bus Symmetrical Copper Stitching**: The 4.5mm Earth bus connects all line-to-earth GDTs to the mirrored 3-pin `J_EARTH` terminal across both layers (2 oz top + 2 oz bottom = 4 oz / 140 µm total Cu). A dedicated column of **5× heavy plated stitching vias** (1.0mm drill, 1.8mm pad) at X=150.0mm stitches the top and bottom copper layers together every 3.81mm across the entire bus width, creating an 11-barrel monolithic ground network (3 GDT pins + 5 stitching vias + 3 terminal pins).
* **Wire B LED Return Westward Routing**: To eliminate any potential short circuits with the line-to-earth GDT inputs on Wire A and Wire C at X=131.00mm while maximizing surge clearance to the Earth network, the Wire B LED return traces on `B.Cu` run up a vertical spine at X=135.50mm with elevated horizontal rungs at Y=109.50mm (north) and Y=135.50mm (south), connecting directly into Pad 2 at (145.54, 103.00) and (145.54, 142.00). This achieves an expansive **8.44mm clearance (2.81× headroom over 3.0mm)** to the Earth GDT pins, with **>3.13mm clearance** from the return tracks to the Earth network.
* **GDT_AC Clearance**: `GDT_AC` axial leads are bent to maintain a 2.0mm+ vertical air gap standoff above the insulated Wire B top copper track. Through-hole pins bond top and bottom copper of Wire A and C directly at the SMT GDT junctions.
* **Vias**: **Tented** with green solder mask.
* **Polarity Silkscreen**: Explicit `+` (Anode / Square pad) and `-` (Cathode / Round pad) on LED outputs; `A`, `B`, `C` on input; `EARTH` on earth terminal.

---

## 6. Field Installation Guide

```
          [ WISKA COMBI 308 IP66/IP67 ENCLOSURE ]
 ┌─────────────────────────────────────────────────────────────┐
 │                                                             │
 │  INCOMING 3-CORE CABLE               OUTGOING 3-CORE CABLE  │
 │   (2.5mm² SWA / Exterior)           (2.5mm² SWA / Exterior) │
 │          │                                     │            │
 │          ▼                                     ▼            │
 │   [ WAGO 221-413 (Wire A) ] ─── Pigtail A ───┐              │
 │   [ WAGO 221-413 (Wire B) ] ─── Pigtail B ───┼──────────┐   │
 │   [ WAGO 221-413 (Wire C) ] ─── Pigtail C ───┼──────┐   │   │
 │                                              │      │   │   │
 │     ┌────────────────────────────────────────┘      │   │   │
 │     │    ┌──────────────────────────────────────────┘   │   │
 │     │    │    ┌─────────────────────────────────────────┘   │
 │     ▼    ▼    ▼                                             │
 │   ┌──────────────┐         ┌───────────┐                    │
 │   │ J_IN (A,B,C) │         │  J_LED_A  │ ──> Panel LED A    │
 │   │              │         │  (+, -)   │     (Green IP67)   │
 │   │  PCB BOARD   │         └───────────┘                    │
 │   │  (60 x 52mm) │         ┌───────────┐                    │
 │   │              │         │  J_LED_C  │ ──> Panel LED C    │
 │   │   J_EARTH    │         │  (+, -)   │     (Green IP67)   │
 │   └──────┬───────┘         └───────────┘                    │
 │          │                                                  │
 │          ▼ (Only at 5 Surge Boxes: 0m, 1km, 2km, 3km, 4km)  │
 │   [ Copper Ground Stake ]                                   │
 │                                                             │
 │   [ BACKFILLED WITH WISKA MP0100 SILICONE POTTING GEL ]     │
 └─────────────────────────────────────────────────────────────┘
```

1. **Continuous Splice**: The main arriving and departing 3-core cable runs continuously through three **WAGO 221-613** 3-way lever connectors.
2. **PCB Tap**: A short 2.5mm² pigtail wire taps from each WAGO into `J_IN` (`A`, `B`, `C`).
3. **LED Indicators**: External panel-mount green LEDs (Marl IP67) have flying leads screwed into `J_LED_A` and `J_LED_C`.
4. **Surge Earth Ground (5 Stations Only)**: Heavy earth grounding cable from the copper ground rod is clamped into `J_EARTH`. (Standard boxes leave `J_EARTH` unpopulated/empty).
5. **Gel Encapsulation**: Once wired and tested, mix and pour **WISKA MP0100 re-enterable two-part silicone potting gel** to fill the box cavity.

---

## 7. Project File Directory

* `pcb/pcb.kicad_sch` — KiCad 9 Master Schematic.
* `pcb/pcb.kicad_pcb` — KiCad 9 Master PCB Layout (60mm × 52mm, 2 oz Cu, ENIG).
* `pcb/BOM.csv` — Standard JLCPCB/PCBWay Turnkey PCBA Bill of Materials.
* `pcb/CPL.csv` — Standard JLCPCB/PCBWay Pick-and-Place Centroid Coordinates.
* `ORDERING.md` — Complete Turnkey JLCPCB Ordering & Re-ordering Guide.
* `MATERIALS.md` — Complete Hardware Procurement & Materials Tracker.
* `INSTALL.md` — Complete Step-by-Step Field & Shed Installation Manual.
* `RISKS.md` — Electrical, polarity, miswiring, and environmental risk analysis.
* `LED.md` — Selected IP67 LED panel indicator part details.


