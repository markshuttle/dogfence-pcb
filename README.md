# Dog Fence Indicator & Surge Protection System (v1.1.0)
**4km High-Reliability Perimeter Containment & Lightning Protection**

## Pending Remediation Requirements

Implementation checklist and new-session context: **[REMEDIATION.md](REMEDIATION.md)**.

User clarifications recorded on 2026-09-06 for the next design revision:

- The prototype order remains **5 assembled boards**, using readily available FR-4, 2 oz outer copper, and ENIG.
- Stations at 0 m, 100 m, ..., 4000 m mean **41 installed station boards and 82 LEDs**, including separate 0 km and 4 km stations at the shed. Legacy 40-station quantities below and in associated documents await synchronization during remediation.
- The purchased PSU is believed to be a **Mean Well LRS-35-36**; nameplate confirmation is pending. Its [manufacturer specification](https://www.meanwell.com/Upload/PDF/LRS-35/LRS-35-SPEC.PDF) is 36 V, 1 A, 36 W. The user is willing to upgrade to an **LRS-75-36**, [specified at 36 V, 2.1 A, 75.6 W](https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF), for additional capacity. The upgrade is a candidate, not a confirmed purchase. Keep the nominal TEST voltage at 36 V; both models offer 32.4-39.6 V adjustment and hiccup-mode overload protection. Source/GDT/fuse coordination remains unresolved and is not fixed merely by increasing PSU wattage.
- The **Kraus & Naimer CA10.A362** six-pole centre-off switch is a sourcing candidate. Its 20 A thermal rating exceeds the expected normal current, but the exact changeover function's DC breaking capability and transfer sequencing still require confirmation. It is not an approved lightning-isolation device.
- Normal TEST sessions may last **one to two hours**, and the user prefers **continuous-safe TEST** rather than relying on a timeout. Design for accidental extended normal TEST operation using continuous-duty thermal limits; assess abnormal faults and surges separately. TEST still disables RF containment, so the hub must identify the fence-inactive state clearly and restoration to RUN remains an operator action.
- The site is on the **Isle of Man, less than 1 km from the coast**, with frequent rain. Observed outdoor ambient temperatures are approximately **-10 to +30 degrees C**. Raised junction boxes may be in direct sun or shade; continuous submersion is not an intended service condition. Qualification must allow for weather margin, solar heating, salt contamination, and condensation rather than treating +30 degrees C as the maximum internal component temperature.
- The likely cable is **Oceanflex 3-core tinned thin-wall 3 x 2.5 mm^2**, as listed by [12 Volt Planet](https://www.12voltplanet.co.uk/CAB3CTNTW2.5PNT.html), product code **P01018**, listed part **CM03/05.100**. Actual purchased cable identity is still to be confirmed. The listing specifies **60 V maximum**, **-15 to +70 degrees C** complete-cable working temperature, **7.3 mm maximum overall diameter**, and **35 strands of 0.30 mm per core**. Its reference to ISO 6722 Class B / 105 degrees C concerns the cores, not a 105-degree rating for the complete cable. Do not retain the earlier unverified arctic-temperature assumption. The page does not establish maximum conductor resistance, permanent UV/weather exposure, wet-conduit suitability, or impulse withstand; its colour table also lists only black/red for three cores. Obtain the applicable manufacturer data or verify the actual cable before assigning core colours or qualification limits. A 60 V operating rating alone neither qualifies nor disproves survival of a short surge above 60 V.
- The cable will mostly run **0.3-1.0 m above ground** on a **timber fence with horizontal metal wire strands**, and through plastic conduit below driveways and gates. The supporting fence is not energized, but an energized cattle wire may run in parallel for **up to 300 m**, with **at least 0.5 m separation**. Use 0.5 m / 300 m as the planned repetitive-pulse qualification case, not a demonstrated interference-safe clearance. Compare energizer-off and energizer-on operation in both RUN and TEST: verify the intended RF boundary field, absence of unintended receiver responses outside it, correct LED indications, and no damaging or sustained protection conduction. Record the actual energizer/pulse characteristics and routing used for qualification. Maintain the minimum actual separation, allow for wire movement, and increase separation where practical. Do not electrically connect the boundary cable to supporting or energized fence wires; plastic conduit is mechanical protection, not electromagnetic shielding.
- The diagnostic requirement is to locate **one damage site affecting any one, two, or all three cores within a 100 m span**. For multiple sites, **repair the first fault and repeat TEST** is acceptable. Identifying the particular broken core(s) is not required; optional low-voltage multimeter checks at the isolated shed ends can assist troubleshooting. An additional TEST-direction selector is not required for this baseline.
- The LED visibility target is **4-5 m in full daylight**. Verify that ON and OFF are distinguishable at 5 m in the intended mounting/viewing direction, including glare, at the lowest expected far-station current. The current nominal same-end DC model predicts approximately 8 mA per far-end LED; this is not a guaranteed cable/temperature worst case or proof of visibility. Finalize the current budget from verified cable data and test the actual purchased indicators before claiming compliance. Retain safe near-station current and continuous resistor dissipation if the optical or electrical design changes.
- The proposed shed arrangement shares an earth connection between the **DogWatch SmartFence protection and both shed-end milestone stations**. Confirm its relationship to the actual building protective-earth system against the regional DogWatch installation requirements and a qualified installer's site-specific earthing/bonding design; do not substitute arbitrary separate, unbonded rods. Do not equate this proposal with directly bonding a fence core or PSU DC negative to earth.

**TEST topology for remediation:** Use the same-end feed/return: Start A/C to +36 V, Start B to DC negative, and End A, End B, and End C each separately open, with the transmitter isolated. This produces an LED-state boundary for all seven one-location open-circuit cut-core combinations in the DC model, assuming healthy boards and no additional inter-core shorts. Connecting both B ends to DC negative is not the normal TEST arrangement because it masks a B-only break. Use the agreed repair-and-retest workflow for multiple sites; no reverse-feed selector is needed. RUN retains the three parallel cores at each transmitter end. This replaces the legacy opposite-end B-return design in the remediation plan, but is **not yet implemented in the hub wiring documents or qualified on hardware**.

The circuit, hub wiring, production files, and remaining legacy claims have not yet been remediated. These requirements and the DFM policy below are **not manufacturing or field-release approval**.

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
* **LED Current**: $I = (36\text{V} - 2.1\text{V} - 0.7\text{V}) / 2.2\text{k}\Omega \approx 15.0\text{ mA}$ per LED.
* **Power Dissipation**: $P = I^2 R \approx 0.50\text{W}$ (The 1W-rated metal film resistors run cool at 50% capacity).
* **Fault Detection**: If Wire A breaks at 1.4km, LED A illuminates at boxes 0m–1.3km and stays OFF at 1.4km–4.0km.

---

## 4. Hardware Component Selection & Specifications (Current In-Stock Baseline)

Every part on the board was specifically chosen for heavy-duty industrial endurance using parts actively stocked in the JLCPCB/LCSC Shenzhen warehouse for instant, friction-free assembly:

| Designator | Component Description | Selected Part | Key Durability Attributes |
|:---|:---|:---|:---|
| **`D1`, `D2`** | 1000V 1A Rectifier Diode | **1N4007G** (LCSC: `C232439`) | **Glass-passivated junction (`G` suffix)**, -65°C to +175°C, 30A forward surge (IFSM). Operates under <2% electrical stress. |
| **`GDT_AB`, `GDT_BC`** | Core-to-Core SMT Arrester | **Ruilon SMD5050-470NA** (JLCPCB: `C39692533`) | **5,000A (5kA)** impulse surge (8/20 µs), 470V breakdown, <1.5 pF, 5.0×5.0mm SMT package. |
| **`GDT_AC`** | Core-to-Core Axial Arrester | **Bencent B5G470L** (JLCPCB: `C5337217`) | **5,000A (5kA)** impulse surge (8/20 µs), 470V breakdown, compact axial body ($\Phi 5.5\text{mm} \times 6\text{mm}$), bridges Wire B. |
| **`GDT_A_E`, `GDT_B_E`, `GDT_C_E`** | Line-to-Earth 20kA Arrester | **Ruilon 2R470TD-8** (JLCPCB: `C2836978`) | **20,000A (20kA)** impulse surge (8/20 µs), 470V breakdown, heavy-duty axial body ($\Phi 8.0\text{mm} \times 6\text{mm}$). |
| **`R1`, `R2`** | 2.2kΩ Current Limiter | **1W Metal Film 1%** (Vishay `MBE04140C2201FC100`, JLCPCB: `C1368610`) | 1W power rating (operates at ≈0.50W, 50% capacity), 500V working voltage, DIN 0414 axial package. |
| **`J_IN`, `J_EARTH`** | 3-Pin 7.62mm Pitch Screw Terminals | **Cixi Kefa KF128-7.62-3P** (JLCPCB: `C474957`) | **24A / 300V Heavy Duty**, M3 steel clamping screws, 7.62mm pitch for high-voltage creepage & clearance. `J_EARTH` has all 3 pins tied in parallel (72A rating) for contact redundancy. |
| **`J_LED_A`, `J_LED_C`** | 2-Pin 5.08mm Screw Terminals | **Cixi Kefa KF129-5.08-2P** (JLCPCB: `C475092`) | **24A / 250V Heavy Duty**, M3 steel clamping screws, -40°C to +105°C. |

---

## 5. Multi-Decade (20–50 Year) Ultra-Durable Component Upgrades (Pre-Order Option)

For initial prototyping, testing, and pilot deployments, the design is 100% turnkey manufacturable using **JLCPCB in-house inventory** (Section 4). All 14 components are active, stocked on reels in Shenzhen, and build in 3–5 days without sourcing delays.

For a **final permanent perimeter deployment** targeting an uncompromising **20 to 50 year outdoor service life**, the following Tier-1 Western industrial components can be pre-ordered into your **JLCPCB Private Library (via JLCPCB Global Sourcing)** from authorized distributors (Mouser, DigiKey, Farnell) prior to production assembly.

Every proposed upgrade component has been pre-verified for **100% native courtyard, pad geometry, and physical layout compatibility** with zero changes required to the PCB routing or KiCad copper layers:

| Designator | In-Stock Baseline | 20–50 Year Pre-Order Upgrade | Manufacturer & MPN | Multi-Decade Durability Justification | Courtyard & Physical Compatibility |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`D1`, `D2`** | 1N4007G (DO-41, `C232439`) | **1N4007GP-E3/54 (Superectifier®)** | **Vishay Intertech** `1N4007GP-E3/54` | **Cavity-Free Hermetic Glass Bead:** The silicon die is brazed at >600°C and completely encapsulated in a solid glass sleeve before outer flame-retardant molding. Permanently prevents moisture tracking along the lead wires to the junction over 50 years. 1000V / 1A, -65°C to +175°C. | **100% Drop-in Match:** Standard JEDEC DO-41 (DO-204AL), 10.16mm pitch. Courtyard: $5.00 \times 2.60\text{ mm}$. Pad drill: 1.1mm. |
| **`R1`, `R2`** | MBE0414 1W (DIN 0414, `C1368610`) | **PR02 Series (2.2kΩ 2W Power Metal Film)** | **Vishay Intertech** `PR02000202201JA100` | **4× Derating Headroom (25% Load):** Operates at only 0.50W (25% of 2W rating) during 36V TEST mode, keeping local potting temperature rise minimal during extended fault-finding. Pure silicone flameproof lacquer withstands up to 155°C without aging or outgassing. | **100% Drop-in Match:** Body is $10.0 \times 3.9\text{ mm}$, which is slightly *more compact* than DIN 0414 ($11.9 \times 4.5\text{ mm}$). Fits inside existing $12.00 \times 4.50\text{ mm}$ courtyard on 15.24mm pitch. |
| **`GDT_AB`, `GDT_BC`** | SMD5050-470NA (5kA SMT, `C39692533`) | **SH470 / SH Series (5kA 470V SMT)** | **Littelfuse** `SH470` | **Global Tier-1 Vacuum Brazing:** Ultra-low capacitance (<0.7 pF), planar metal end electrodes for high thermal-fatigue endurance, ceramic-to-metal vacuum brazed envelope ensures multi-decade noble gas containment without air leakage. | **100% Drop-in Match:** Standard $5.0 \times 5.0\text{ mm}$ squared SMT footprint. Fits existing $5.20 \times 5.20\text{ mm}$ courtyard and $5.2 \times 2.0\text{ mm}$ pads. |
| **`GDT_AC`** | B5G470L (5kA axial, `C5337217`) | **2027-47-BLF or CG2-470L (10kA 470V axial)** | **Bourns / Littelfuse** `2027-47-BLF` | **2× Surge Energy Absorption (10kA):** Upgrades differential inter-core A-C protection from 5kA to 10kA (8/20 µs). Rugged ceramic envelope with 15.24mm axial lead forming. | **100% Drop-in Match:** $\Phi 6.0 \times 6.0\text{ mm}$ body on 15.24mm pitch. Fits existing $5.60 \times 6.00\text{ mm}$ courtyard. Leads maintain $\ge 2.0\text{ mm}$ vertical standoff over Wire B. |
| **`GDT_A_E`, `GDT_B_E`, `GDT_C_E`** | 2R470TD-8 (20kA axial, `C2836978`) | **SL1021A470R (20kA 470V axial)** | **Littelfuse** `SL1021A470R` *(or retain Ruilon 2R470TD-8)* | **Heavy-Duty 20,000A Telecom Grade:** Exact Tier-1 equivalent with ultra-low fail rate, exceptional AC discharge withstand, and multi-decade noble gas seal integrity. | **100% Drop-in Match:** $\Phi 8.0 \times 6.0\text{ mm}$ body, 15.24mm pitch. Courtyard: $6.00 \times 8.00\text{ mm}$. Sits on 9.00mm pitch layout with verified 1.00mm physical air gap between bodies. |
| **`J_IN`, `J_EARTH`** | KF128-7.62-3P (3-Pin, `C474957`) | **GMKDS 3/ 3-7,62 (3-Pin 7.62mm)** | **Phoenix Contact** `1731734` | **Patented Reakdyn Anti-Loosening Screw Clamping:** Integrated resilient screw collar prevents screw backout under decades of diurnal thermal cycling (-20°C to +50°C). High-conductivity copper alloy with galvanic nickel/tin plating prevents contact relaxation and fretting corrosion. 24A, 630V rating. | **100% Native Drop-in Match:** The KiCad footprint was originally designed for Phoenix Contact MKDS/GMKDS! Pad drill: 1.3mm. Courtyard: $10.50 \times 22.86\text{ mm}$. |
| **`J_LED_A`, `J_LED_C`** | KF129-5.08-2P (2-Pin, `C475092`) | **MKDS 1,5/ 2-5,08 (2-Pin 5.08mm)** | **Phoenix Contact** `1715721` | **Patented Reakdyn Rising Cage:** Captive M3 screw with integrated anti-loosening spring sleeve. Solid copper alloy contact pins with nickel barrier layer. 17.5A, 400V rating. | **100% Native Drop-in Match:** KiCad footprint is `TerminalBlock_Phoenix_MKDS-1,5-2-5.08`. Pad drill: 1.3mm. Courtyard: $10.60 \times 11.26\text{ mm}$. Rotations 90° and 270° fully preserved. |

### How to Order Pre-Order Components via JLCPCB Global Sourcing (Final Run)
1. Sign in to **[jlcpcb.com](https://jlcpcb.com)** and navigate to **User Center $\rightarrow$ Parts Manager $\rightarrow$ Global Sourcing** (or **Order Parts**).
2. Enter the MPNs listed above (e.g. Phoenix Contact `1731734`, `1715721`, Vishay `1N4007GP-E3/54`, etc.).
3. Pre-purchase the required quantities for your order into your **"My Parts Lib"** (private inventory).
4. Sourcing lead time is typically **5 to 10 business days** for parts to arrive in Shenzhen.
5. Once marked "In Stock in My Parts Lib", upload `build/Gerbers.zip`, `build/BOM.csv`, and `build/CPL.csv` to place the turnkey PCBA order. The system will automatically allocate your private inventory to the board.

---

## 6. PCB Layout & Fabrication Rules

* **Board Dimensions**: 63.0 mm × 56.0 mm.
* **Mounting**: 4× M3 mounting holes (3.2mm drill) with 6.4mm keepout collar / 6.9mm courtyard clearance at (101.5, 99.0), (155.5, 99.0), (101.5, 146.0), (155.5, 146.0), positioned with uniform 4.5mm edge inset and 1.05mm courtyard clearance to all board edges.
* **Substrate**: Shengyi **S1000-2 High-TG (TG170)** or **S1000H (TG155)** FR-4 laminate (low Z-axis thermal expansion $\le 2.5\%$, high anti-CAF resistance, high moisture resistance for multi-decade ground humidity).
* **Copper Weight**: **2 oz (70 µm)** on both top and bottom layers for high surge current absorption.
* **Plating**: **ENIG 2U" (Electroless Nickel Immersion Gold)** — real 24k gold over nickel prevents copper oxidation for 20+ years.
* **Hole Plating**: Specify any required minimum finished barrel-copper thickness separately with the fabricator. A 2 oz outer-copper selection or a plating-line description does not establish via-barrel thickness or guarantee void-free plating.
* **Via Process**: **Requires explicit CAM agreement for the protected 1.0 mm stitching holes.** Normal tenting, soldermask plugging, and filled-and-capped processes cannot be assumed to seal these holes. See the [via and component hole DFM policy](#via-and-component-hole-dfm); do not shrink the stitching vias to obtain a covering option.
* **Tri-Rail Symmetrical Copper Stitching**: Wires A, B, and C each retain 100% full 3.2mm width across both `F.Cu` and `B.Cu` layers (no waist relief). Each wire conductor features a dedicated cluster of **3× heavy plated stitching vias** (1.0mm drill, 1.8mm pad) directly at the SMT GDT junctions (at X=112.5, 114.0, 115.5mm). This guarantees that both front and back 2 oz copper layers are fully engaged with minimal transient inductance and maximum surge current absorption.
* **Earth Bus Symmetrical Copper Stitching & Monolithic Plane**: The 4.5mm-grid Earth bus connects all line-to-earth GDTs to the mirrored 3-pin `J_EARTH` terminal across both layers (2 oz top + 2 oz bottom = 4 oz / 140 µm total Cu). Both front and back layers feature an identical solid monolithic copper plane ($13.26\text{ mm} \times 22.50\text{ mm}$, zero voids, zero slit gaps). A dedicated column of **5× heavy plated stitching vias** (1.0mm drill, 1.8mm pad) at X=150.0mm stitches the top and bottom copper layers together across the entire bus width, creating an 11-barrel monolithic ground network (3 GDT pins + 5 stitching vias + 3 terminal pins).
* **Line-to-Earth 20kA GDT Respacing (9.0mm Pitch)**: To accommodate the heavy-duty $\Phi 8.0\text{mm} \times 6\text{mm}$ ceramic bodies of the Ruilon 2R470TD-8 arresters without physical collision (which occurred on legacy 7.62mm pitch), `GDT_A_E` and `GDT_C_E` are spaced to Y=113.50mm and Y=131.50mm (9.00mm center-to-center pitch). This provides a verified 1.00mm physical air gap between arrester bodies and 0.50mm courtyard clearance.
* **Indicator Rung Courtyard Optimization & LED Terminal Vertical Symmetry**: `D1` and `D2` (DO-41) are positioned at X=132.50mm, eliminating the legacy 0.0mm pad clearance and 0.55mm courtyard overlap with `R1`/`R2`, achieving 1.50mm pad-to-pad copper gap and 0.95mm courtyard clearance. `J_LED_A` and `J_LED_C` (KF129-5.08-2P) are centered symmetrically at **(145.50, 103.00)** and **(145.50, 142.00)** across the horizontal centerline ($Y = 122.50\text{ mm}$), maintaining identical $8.50\text{ mm}$ board-edge margins and $10.50\text{ mm}$ Earth-bus clearances. Crucially, the terminal blocks are **vertically flipped so their wire openings face outward from the board** (opening UP at rotation `90°` for `J_LED_A` and opening DOWN at rotation `270°` for `J_LED_C`), while Pad 1 (Anode `+`) is consistently on the Left ($X = 142.96\text{ mm}$) and Pad 2 (Cathode `-`) on the Right ($X = 148.04\text{ mm}$) on both channels.
* **Wire B LED Return Westward Routing**: To eliminate any potential short circuits with the line-to-earth GDT inputs on Wire A and Wire C at X=131.00mm while maximizing surge clearance to the Earth network, the Wire B LED return traces on `B.Cu` run up a vertical spine at X=135.50mm with elevated horizontal rungs at Y=107.20mm (north) and Y=137.80mm (south), connecting directly into Pad 2 at (148.04, 103.00) and (148.04, 142.00). This achieves a copper clearance of **8.44mm** to the Earth GDT pins, with **3.25mm clearance** from the horizontal return tracks to the solid Earth bus plane ($\ge 3.0\text{mm}$ surge invariant satisfied).
* **Full Courtyard Compliance**: 100% of footprints define explicit, standard `F.CrtYd` (and `B.CrtYd` for mounting holes) bounding geometries according to IPC-7351B / IPC-7251 and manufacturer datasheets, with zero courtyard overlaps across all 18 board footprints.
* **GDT_AC Clearance**: `GDT_AC` axial leads are bent to maintain a 2.0mm+ vertical air gap standoff above the insulated Wire B top copper track. Through-hole pins bond top and bottom copper of Wire A and C directly at the SMT GDT junctions.
* **Polarity Silkscreen**: Explicit `+` (Anode / Square pad) and `-` (Cathode / Round pad) on LED outputs; `A`, `B`, `C` on input; `EARTH` on earth terminal.
* **Typography & Silkscreen**: Unified **Ubuntu Bold** font family across all board elements using a clean, high-contrast hierarchy (Large = 1.30mm, Medium = 1.00mm, Small = 0.85mm):
  - **Large Bold** (1.30mm × 1.30mm, 0.18mm stroke): Board title `"Dog Fence Indicator & Surge v1.1.0"`, and explicit polarity markings (`+` Anode / Square pad, `-` Cathode / Round pad) symmetrically aligned with LED terminals `J_LED_A` and `J_LED_C`.
  - **Small Bold** (0.85mm × 0.85mm, 0.15mm stroke): Input channel indicators (`A`, `B`, `C` on `J_IN`) and ground terminal indicator (`EARTH` on `J_EARTH` on `F.SilkS` at (155.00, 108.00) for installer visibility).
  - **Medium Bold** (1.00mm height, 0.15mm stroke): All discrete and arrester component references (`D1`, `D2`, `R1`, `R2`, `GDT_AB`, `GDT_BC`, `GDT_AC` at 1.00mm × 1.00mm, and `GDT_A_E`, `GDT_B_E`, `GDT_C_E` at 1.00mm × 0.80mm), strictly conforming to JLCPCB $\ge 0.15\text{mm}$ silkscreen line width rules with zero pad solder mask clipping.

---

### Via and Component Hole DFM

**Policy reviewed 2026-09-06.** Recheck the selected fabricator's capabilities for each order and whenever a part, footprint, copper weight, or via process changes. The controlling references are [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [via covering](https://jlcpcb.com/help/article/pcb-via-covering), and [via versus component-hole tolerances](https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes). Order-specific written acceptance takes precedence over assumptions based on checkout options.

**Via process selection:** The diameter limits below concern the **hole**, not its copper pad.

| Process | Published guidance | Consequence for this board's 1.0 mm stitching holes |
| :--- | :--- | :--- |
| Untented | No additional covering-process requirement. Copper remains exposed and solderable. | Ordinary hole fabrication is possible, but there is no seal; evaluate solder wicking and environmental protection. |
| Tented | Ideally at most 0.4 mm; normal coverage guidance is at most 0.5 mm. Larger holes are not guaranteed fully covered. | Do not treat the KiCad tenting setting as a guaranteed closure. |
| Soldermask plugged | At most 0.5 mm, no mask openings on either side, and at least 0.35 mm process clearance from other mask openings/pads. | Outside the normal process limit. Ink plugging is not equivalent to filled-and-capped via-in-pad processing. |
| Filled and capped | The detailed guide recommends at most 0.5 mm; the capability table lists 0.15-0.55 mm. Resolve the applicable limit with CAM. | 1.0 mm exceeds both published ranges. Any exception requires written process acceptance. |

- Preserve the nine rail-stitching and five earth-stitching vias and their electrical geometry. Revise surrounding soldering geometry or obtain an approved manufacturing solution rather than silently deleting or reducing these vias.
- Inspect the actual drill circles against `F.Mask`, `B.Mask`, and `F.Paste`, including the assembler's processed mask/stencil data. A nearby SMT mask opening can expose part of a nominally tented hole. Keep holes out of SMT wettable areas and retain a process-approved mask barrier; otherwise explicitly qualify the via-in-pad process and solder volume.
- JLCPCB does not control ordinary via-hole diameter like a component insertion hole and may adjust it in CAM. Obtain agreement not to reduce the protected hole sizes if the electrical design depends on them.
- Identify vias by coordinates and hole function when specifying treatment. The present resistor insertion holes and stitching vias both use 1.0 mm drills: **do not request blanket filling of every 1.0 mm hole**.
- Outer copper weight does not specify barrel plating. The capability page lists **18 micrometres average hole plating**, not a guaranteed minimum for every barrel. Use an agreed finished minimum if a current/surge calculation depends on it. Soldermask or ordinary nonconductive epoxy fill adds no conductive copper cross-section.
- Tenting, opacity, or potting is not evidence of hermetic sealing, freeze-thaw immunity, or an assembled IP rating.

**Component insertion holes:** Use plated through-hole **pads**, not vias, for component leads. For every exact manufacturer/MPN, record the drawing revision, maximum finished lead dimensions, lead spacing, proposed finished hole, and assembly allowance. Nominal package names and supplier CAD footprints are not sufficient fit evidence.

For a round insertion hole, check:

```text
Round lead envelope     = maximum finished lead diameter
Rectangular envelope    = sqrt(maximum_width^2 + maximum_thickness^2)
Minimum finished hole   = nominal finished hole - negative hole tolerance
Minimum finished hole  >= maximum lead envelope + diametral assembly allowance
```

JLCPCB publishes **+0.13/-0.08 mm** for ordinary component PTH holes. Use at least **0.10 mm diametral assembly allowance after the negative tolerance** as a conservative project starting point, unless the component/assembly requirements call for more. This project allowance is distinct from JLCPCB's general recommendation to make the nominal hole 0.10 mm larger than the maximum pin. Also account for pin-pitch, hole-position, and lead-forming tolerances, especially for rigid multi-pin connectors. Do not assume tighter press-fit tolerances are available for this two-layer order.

For example, the [onsemi 1N4007G drawing](https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf) allows a 0.86 mm lead. The current 0.90 mm hole can finish at 0.82 mm and fail insertion. A 1.10 mm hole can finish at 1.02 mm, providing 0.16 mm diametral clearance at the maximum lead size. **The 1.10 mm hole is a remediation proposal, not a change already applied to the PCB.**

After increasing a drill, separately recheck pad size, annular ring, hole/copper spacing, and the component envelope. JLCPCB's two-layer, 2 oz **component PTH annular-ring design requirement is at least 0.254 mm**; do not substitute its smaller generic via-ring rule. For finished-ring requirements, include hole-size and registration tolerances. Resolve fit in CAD and regenerate production files rather than relying on forced insertion or post-fabrication reaming of plated holes.

A normal electrical DRC pass does not verify these part-tolerance or via-covering requirements. Complete this review in addition to `make check` and inspect the final processed production files before approval.

---

## 7. Field Installation Guide

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
 │   │  (63 x 56mm) │         ┌───────────┐                    │
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

## 8. Automated Production Build

You can generate and package the complete JLCPCB manufacturing package with a single terminal command:

```bash
make all
```

This runs the automated KiCad DRC check and exports:
* **`build/Gerbers.zip`** — Master 2-layer Gerbers & Excellon drill files.
* **`build/BOM.csv`** — Verified PCBA Bill of Materials.
* **`build/CPL.csv`** — Verified Pick-and-Place Centroid component positions.
* **`build/FlyTest.zip`** — Flying Probe Electrical Test package (contains `pcb.d356` netlist + Gerbers).
* **`build/pcb.d356`** — IPC-D-356 Netlist for probe verification.

To run only the DRC gate verification:
```bash
make check
```

---

## 9. Documentation & Project Structure

* [`README.md`](README.md) — Master project overview, architecture, and specifications (this file).
* [`AGENTS.md`](AGENTS.md) — Operating environment guide for AI agents and developers (Ubuntu conventions, KiCad Snap confinement, build workflows).
* [`INSTALL.md`](INSTALL.md) — Complete Step-by-Step Field & Shed Installation Manual.
* [`ORDERING.md`](ORDERING.md) — Turnkey JLCPCB Ordering & Re-ordering Guide.
* [`ACCEPTANCE.md`](ACCEPTANCE.md) — Prototype Acceptance & Bench Commissioning Protocol.
* [`MATERIALS.md`](MATERIALS.md) — Hardware Procurement & Materials Tracker.
* [`RISKS.md`](RISKS.md) — Electrical, polarity, miswiring, and environmental risk analysis.
* [`LED.md`](LED.md) — Selected IP67 LED panel indicator part details.
* [`Makefile`](Makefile) — Automated manufacturing package build script.
* `pcb/pcb.kicad_sch` — KiCad 9 Master Schematic.
* `pcb/pcb.kicad_pcb` — KiCad 9 Master PCB Layout (63mm × 56mm, 2 oz Cu, ENIG).
* `pcb/BOM.csv` — Standard JLCPCB/PCBWay Turnkey PCBA Bill of Materials.
* `pcb/CPL.csv` — Standard JLCPCB/PCBWay Pick-and-Place Centroid Coordinates.
