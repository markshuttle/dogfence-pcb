# Dog Fence Indicator & Surge Protection System (v1.0)
**Project Knowledge Base & Agent Briefing**

---

## 1. Project Overview & Intent

This project implements a high-reliability, long-distance **4km (~2.5 miles) hidden perimeter dog containment fence** powered by the **DogWatch SmartFence** system.

The fence boundary is formed by a continuous outdoor **3-core 2.5mm² cable** installed in a closed loop. All three internal copper conductors (Wire A, Wire B, Wire C) run in parallel, providing an effective total cross-sectional area of **7.5mm² (~8 AWG)** and an ultra-low total loop resistance of **≈ 9.3 Ω**, well within the DogWatch transmitter driving threshold (<30 Ω).

To simplify long-term diagnostics, fault isolation, and lightning protection across 4 kilometres of rural terrain, **40 milestone junction boxes** are installed along the perimeter:
- **35 Standard Diagnostic Milestones** (every ≈ 100m): Provide visual green LED status indicators for Wires A and C.
- **5 Surge & Grounding Milestones** (at 0m, 1km, 2km, 3km, 4km): In addition to visual diagnostics, these stations connect to deep-driven copper earth ground rods to safely discharge lightning and static energy without affecting fence operation.

All 40 junction boxes use an identical, unified **"Dog Fence Indicator & Surge 1.0" PCB**.

---

## 2. Core Philosophy & Design Goals

1. **20+ Year Outdoor Lifespan**: Zero compromise on durability. Materials are rated for -40°C to +90°C+ temperature swings, moisture, UV, and ground humidity.
2. **Zero In-Field Soldering**: 100% turnkey factory assembly (PCBA) by JLCPCB/PCBWay. Field installation requires only a screwdriver.
3. **Dual-Mode Operation (RF RUN Mode vs. DC TEST Mode)**:
   - In **RUN Mode**, the board is electrically invisible to the DogWatch transmitter's 4–10 kHz RF signal (<1.5 pF capacitance load, zero antenna grounding).
   - In **TEST Mode**, an injected +36V DC supply illuminates milestone LEDs sequentially down the perimeter. If a core breaks, all downstream LEDs go dark, pin-pointing the exact 100m fault location immediately.
4. **Hermetic Enclosure & Potting**: Housed in IP66/IP67 **WISKA COMBI 308** junction boxes, backfilled with re-enterable two-part silicone potting gel (**WISKA MP0100**) for submersible **IP68 hermetic sealing**.

---

## 3. Electrical Architecture & Dual-Mode Circuitry

```
                  [ +36V DC in TEST Mode / RF Signal in RUN Mode ]
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   │                                           │
             [ Wire A (Core 1) ]                         [ Wire C (Core 3) ]
                   │                                           │
            ┌──────┴──────┐                             ┌──────┴──────┐
            │             │                             │             │
        [ 2.2kΩ 1W ]   [ GDT 1 ]                     [ 2.2kΩ 1W ]   [ GDT 3 ]
          (R1)       (470V 20kA)                       (R2)       (470V 20kA)
            │             │                             │             │
        [ 1N4007G ]       │                         [ 1N4007G ]       │
          (D1)            │                           (D2)            │
            │             │                             │             │
        [ LED A (+) ]     │                         [ LED C (+) ]     │
            │             │                             │             │
        [ LED A (-) ]     │                         [ LED C (-) ]     │
            │             │                             │             │
            └──────┬──────┘                             └──────┬──────┘
                   │                                           │
                   ├───────────────────[ Wire B (Core 2) ]─────┤
                   │                            │              │
                   │                        [ GDT 2 ]          │
                   │                       (470V 20kA)         │
                   │                            │              │
                   │                            ▼              │
                   │                   [ EARTH GROUND BUS ]    │
                   │                            │              │
                   │                     [ J_EARTH Pin ]       │
                   │                            │              │
                   │                  (To External Earth Rod   │
                   │                  at Surge Milestones only)│
                   ▼                                           ▼
         [ Return to 0V / DC Neg ]                   [ Return to 0V / DC Neg ]
```

### Modes of Operation

#### Mode 1: RUN Mode (SmartFence Transmitter Active)
* **Signal**: AC RF Carrier (4 kHz or 10.7 kHz), ≈ 10–20V RMS.
* **Resistor-Diode Rungs**: Total resistance per milestone rung ≈ 2.2 kΩ. Total parallel impedance of 40 milestones is ≈ 55 Ω, drawing negligible differential RF current because Wire A and B are driven at identical potentials.
* **GDT Capacitance**: <1.5 pF per GDT (<60 pF across entire 4km perimeter). Completely RF transparent.
* **Ground Isolation**: Earth ground is completely decoupled from the fence antenna loop by the GDTs' 470V air/gas spark gaps.

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
| **`GDT1`, `GDT2`, `GDT3`** | Gas Discharge Tube Arrester | **Ruilon 2R470TD-8** (LCSC: `C2836978`) | **20,000A (20kA)** impulse surge handling (8/20 µs), 470V breakdown, <1.5 pF, -40°C to +90°C. |
| **`R1`, `R2`** | 2.2kΩ Current Limiter | **1W Metal Film 1%** (LCSC: `C17533`) | 1W power rating (operates at 0.50W max), 350V working voltage, ±50ppm/°C temperature coefficient. |
| **`J_EARTH`, `J_LED_A`, `J_LED_C`** | 2-Pin 5.08mm Screw Terminals | **Cixi Kefa KF129S-5.08-2P** (LCSC: `C7435702`) | **24A / 630V Heavy Duty**, M3 steel clamping screws, -40°C to +105°C, accepts up to 2.5mm² / 4mm² wire. |
| **`J_IN`** | 3-Pin 5.08mm Screw Terminal | **Cixi Kefa KF128-5.08-3P** (LCSC: `C474953`) | **24A / 250V Heavy Duty**, matching rising cage clamp series, -40°C to +105°C. |

---

## 5. PCB Layout & Fabrication Rules

* **Board Dimensions**: 60.0 mm × 45.0 mm.
* **Mounting**: 4× M3 mounting holes (3.2mm drill) with 6.4mm courtyard clearance.
* **Substrate**: Shengyi **S1000H High-TG (TG155)** FR-4 laminate (low thermal expansion, anti-CAF, high moisture resistance).
* **Copper Weight**: **2 oz (70 µm)** on both top and bottom layers for high surge current absorption.
* **Plating**: **ENIG 2U" (Electroless Nickel Immersion Gold)** — real 24k gold over nickel prevents copper oxidation for 20+ years.
* **Plating Line**: **Horizontal Electroless Copper Plating** (ensures dense, void-free through-hole copper barrels).
* **Vias**: **Tented** with green solder mask.
* **Polarity Silkscreen**: Explicit `+` (Anode / Square pad) and `-` (Cathode / Round pad) on LED outputs; `A`, `B`, `C` on input; `EARTH / ROD` on earth terminal.

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
 │   │  (60 x 45mm) │         ┌───────────┐                    │
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

1. **Continuous Splice**: The main arriving and departing 3-core cable runs continuously through three **WAGO 221-413** 3-way lever connectors.
2. **PCB Tap**: A short 2.5mm² pigtail wire taps from each WAGO into `J_IN` (`A`, `B`, `C`).
3. **LED Indicators**: External panel-mount green LEDs (Marl IP67) have flying leads screwed into `J_LED_A` and `J_LED_C`.
4. **Surge Earth Ground (5 Stations Only)**: Heavy earth grounding cable from the copper ground rod is clamped into `J_EARTH`. (Standard boxes leave `J_EARTH` unpopulated/empty).
5. **Gel Encapsulation**: Once wired and tested, mix and pour **WISKA MP0100 re-enterable two-part silicone potting gel** to fill the box cavity.

---

## 7. Project File Directory

* `pcb/pcb.kicad_sch` — KiCad 9 Master Schematic.
* `pcb/pcb.kicad_pcb` — KiCad 9 Master PCB Layout (60mm × 45mm, 2 oz Cu, ENIG).
* `pcb/BOM.csv` — Standard JLCPCB/PCBWay Turnkey PCBA Bill of Materials.
* `pcb/CPL.csv` — Standard JLCPCB/PCBWay Pick-and-Place Centroid Coordinates.
* `ORDERING.md` — Complete Turnkey JLCPCB Ordering & Re-ordering Guide.
* `MATERIALS.md` — Complete Hardware Procurement & Materials Tracker.
* `INSTALL.md` — Complete Step-by-Step Field & Shed Installation Manual.
* `RISKS.md` — Electrical, polarity, miswiring, and environmental risk analysis.
* `LED.md` — Selected IP67 LED panel indicator part details.


