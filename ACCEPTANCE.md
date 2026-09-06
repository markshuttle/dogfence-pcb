# Dog Fence Indicator & Surge Protection System (v1.1.0)
**Prototype Acceptance & Bench Commissioning Protocol**

---

## 1. Scope & Objective

This document defines the rigorous bench verification, quality acceptance, and electrical commissioning protocol for the **5-board prototype batch** ordered from JLCPCB.

Executing this protocol validates:
1. **Manufacturing Quality**: Solder joint integrity, footprint alignments, and de-paneling accuracy.
2. **Component Polarities & Alignments**: Diode cathode bands, terminal block wire openings, and arrester vertical clearances.
3. **Cold DC Isolation & Continuity**: Galvanic isolation across GDT spark gaps and low-resistance through-rail bonding.
4. **Active DC TEST Mode & Reverse Polarity Protection**: Illumination, current draw, thermal stability, and reverse-bias cutoff under +36V DC.
5. **Mechanical Fit**: Compatibility with Essentra 9.5mm standoffs, WISKA COMBI 308 enclosures, and APEM IP67 LED panel mount indicators.

Passing all tests across all 5 prototype boards provides the formal **engineering sign-off** required to proceed with the final 40-board production run.

---

## 2. Required Bench Equipment & Tools

| Item | Specification / Purpose | Reference / Part # |
| :--- | :--- | :--- |
| **Digital Multimeter (DMM)** | DC Voltage, Resistance (0.01Ω to 100MΩ+), Diode check, DC Current (mA) | Standard 4.5-digit DMM |
| **DC Bench Power Supply** | Adjustable or fixed +36V DC (current limit set to 0.5A–1.0A) | Mean Well NDR-75-36 or bench PSU |
| **Test LEDs** | 2× APEM 10mm IP67 Green Panel Indicators (2V raw version) | [APEM `Q10F5SXXSG02E`](MATERIALS.md) |
| **Terminal Screwdriver** | 3.0mm–3.5mm flathead for M2.5 / M3 rising cage screws | Standard electrician's driver |
| **Jumper Wires** | Short lengths of 2.5mm² solid/stranded copper hookup wire | 2.5mm² single core |
| **Board Standoffs (4 pcs)** | Snap-lock nylon adhesive PCB supports (9.5mm height, 3.2mm hole) | [Essentra `LCBSBM-6-01A-RT`](MATERIALS.md) |
| **Sample Enclosure** | IP66/IP67 Outdoor Junction Box (85 × 85 × 51 mm) | [WISKA COMBI 308](MATERIALS.md) |

---

## 3. Phase 1: Visual & Mechanical Inspection (Unpowered)

Perform these visual checks on each of the 5 received prototype boards under good bench lighting:

```
                          [ TOP-DOWN INSPECTION MAP ]
   (101.5, 99.0)                                             (155.5, 99.0)
   [ M3 Hole H1 ] ────────────── 63.00 mm ────────────────── [ M3 Hole H2 ]
        │                                                         │
        │               [ R1 (2.2k) ]   [ D1 (1N4007G) ]          │
        │                                (Band -> Right)          │
        │                                                         │
        ▼                                                         ▼
   ┌──────────┐                                             ┌───────────┐
   │   J_IN   │ ◄── Wire A ───[ GDT_AB (SMD5050) ]          │  J_LED_A  │ (Opens UP)
   │  3-Pin   │ ◄── Wire B ───[ GDT_AC (Axial Arch) ]       │  2-Pin    │ [Pad 1: + (Left)]
   │  7.62mm  │ ◄── Wire C ───[ GDT_BC (SMD5050) ]          │  5.08mm   │ [Pad 2: - (Right)]
   │(Opens L) │                                             └───────────┘
   └──────────┘                                             ┌───────────┐
        ▲                                                   │  J_EARTH  │
        │               [ GDT_A_E, GDT_B_E, GDT_C_E ]       │  3-Pin    │
        │                (20kA Axial Line-to-Earth)         │  7.62mm   │
        │                                                   │(Opens R)  │
        │               [ R2 (2.2k) ]   [ D2 (1N4007G) ]    └───────────┘
        │                                (Band -> Right)    ┌───────────┐
        │                                                   │  J_LED_C  │ (Opens DOWN)
   [ M3 Hole H3 ] ───────────────────────────────────────── │  2-Pin    │ [Pad 1: + (Left)]
   (101.5, 146.0)                                           └───────────┘ [Pad 2: - (Right)]
                                                            (155.5, 146.0)
```

### 1.1 De-Paneling & Board Edge Quality
* [ ] Verify the temporary conveyor breakaway rails (mouse-bites or v-scores) have been cleanly removed by JLCPCB.
* [ ] Confirm overall PCB dimensions match **63.0 mm × 56.0 mm** (±0.2mm).
* [ ] Check that all 4 corner mounting holes ($H_1, H_2, H_3, H_4$) are clean, unplated 3.2mm holes with no copper intrusion into the 6.4mm keepout collar.

### 1.2 Connector Placement & Wire Opening Orientation
* [ ] **`J_IN` (3-pin 7.62mm pitch):** Wire entry openings face **LEFT** (toward the board outer edge). Clamping screws face upward.
* [ ] **`J_EARTH` (3-pin 7.62mm pitch):** Wire entry openings face **RIGHT** (toward the opposite board edge). Clamping screws face upward.
* [ ] **`J_LED_A` (2-pin 5.08mm pitch):** Wire entry opening faces **UP / NORTH** (toward the top board edge).
* [ ] **`J_LED_C` (2-pin 5.08mm pitch):** Wire entry opening faces **DOWN / SOUTH** (toward the bottom board edge).
* [ ] **LED Polarities:** For both `J_LED_A` and `J_LED_C`, verify **Pad 1 (Left, square pad)** is aligned with the silkscreen `+` marker (Anode), and **Pad 2 (Right, round pad)** is aligned with the silkscreen `-` marker (Cathode).

### 1.3 Discrete Diode & Arrester Alignments
* [ ] **`D1` and `D2` (1N4007G):** The **white cathode band points RIGHT** (toward Pad 1 / the `+` LED connector). The cathode lead must connect to the right-hand pad at X=137.58mm (`LED_POS` net).
* [ ] **`GDT_AC` (Axial 5kA Arrester):** Bridges over the insulated Wire B top copper track. Confirm that the axial body maintains a **≥ 2.0 mm vertical air gap standoff** above the board surface. The leads must not touch the copper track underneath.
* [ ] **`GDT_A_E`, `GDT_B_E`, `GDT_C_E` (Axial 20kA Arresters):** Verify that the large $\Phi 8.0\text{mm} \times 6\text{mm}$ ceramic bodies have a **1.0 mm physical air gap** between adjacent bodies with zero physical collision (9.00mm center-to-center pitch).
* [ ] **`GDT_AB` and `GDT_BC` (SMT 5050):** Confirm symmetrical, centered seating on SMD pads with uniform solder wetting on both metallized end caps.

### 1.4 Solder Joint Inspection (IPC-A-610 Class 2)
* [ ] Inspect through-hole component pins on the bottom (`B.Cu`) layer: verify 75%+ vertical solder barrel fill, smooth concave wetting fillets, and zero solder bridging or flux encrustation around dense via clusters.

---

## 4. Phase 2: Cold Electrical DMM Checks (Unpowered)

Set your Digital Multimeter (DMM) to resistance mode ($\Omega$) or continuity beeper.

```
+──────────────────────────────────────────────────────────────────────────+
│                      COLD DMM MEASUREMENT MATRIX                         │
+───────────────────┬───────────────────┬──────────────────┬───────────────+
│ Test Points       │ Target Reading    │ Acceptance Limit │ Status / Net  │
+───────────────────┼───────────────────┼──────────────────┼───────────────+
│ J_IN 1 to R1 In   │ < 0.10 Ω          │ ≤ 0.20 Ω         │ Wire A Rail   │
│ J_IN 2 to GDT_BC  │ < 0.10 Ω          │ ≤ 0.20 Ω         │ Wire B Rail   │
│ J_IN 3 to R2 In   │ < 0.10 Ω          │ ≤ 0.20 Ω         │ Wire C Rail   │
│ J_EARTH (Pins 1-3)│ < 0.05 Ω          │ ≤ 0.10 Ω         │ Earth Bus     │
│ Wire A to Wire B  │ Open (>100 MΩ)    │ > 50 MΩ          │ GDT Spark Gap │
│ Wire B to Wire C  │ Open (>100 MΩ)    │ > 50 MΩ          │ GDT Spark Gap │
│ Wire A to Wire C  │ Open (>100 MΩ)    │ > 50 MΩ          │ GDT Spark Gap │
│ Wire A to Earth   │ Open (>100 MΩ)    │ > 50 MΩ          │ GDT Spark Gap │
│ Wire B to Earth   │ Open (>100 MΩ)    │ > 50 MΩ          │ GDT Spark Gap │
│ Wire C to Earth   │ Open (>100 MΩ)    │ > 50 MΩ          │ GDT Spark Gap │
│ R1 Across Leads   │ 2.20 kΩ           │ 2.18–2.22 kΩ     │ 1% Metal Film │
│ R2 Across Leads   │ 2.20 kΩ           │ 2.18–2.22 kΩ     │ 1% Metal Film │
│ D1 Diode Check    │ ~0.60V–0.70V Drop │ 0.55V–0.75V      │ Forward Bias  │
│ D1 Reverse Diode  │ Open (OL)         │ Infinite         │ Reverse Bias  │
│ D2 Diode Check    │ ~0.60V–0.70V Drop │ 0.55V–0.75V      │ Forward Bias  │
│ D2 Reverse Diode  │ Open (OL)         │ Infinite         │ Reverse Bias  │
+───────────────────┴───────────────────┴──────────────────┴───────────────+
```

### 2.1 Through-Rail Continuity (2 oz Copper Rails)
1. Probe between **`J_IN` Pin 1 (Wire A)** and the top lead of `R1`. Reading must be **$< 0.10\ \Omega$**.
2. Probe between **`J_IN` Pin 2 (Wire B)** and the cathode pad (Pad 2) of `J_LED_A` and `J_LED_C`. Reading must be **$< 0.10\ \Omega$**.
3. Probe between **`J_IN` Pin 3 (Wire C)** and the top lead of `R2`. Reading must be **$< 0.10\ \Omega$**.
4. Probe between all three pins of **`J_EARTH`**. All pins must be solidly tied in parallel (**$< 0.05\ \Omega$** across the 4.5mm monolithic bus).

### 2.2 Arrester Spark Gap Galvanic Isolation
1. Measure resistance between **Wire A** and **Wire B**. Reading must show **OL / Open Circuit ($>100\text{ M}\Omega$)**.
2. Measure resistance between **Wire B** and **Wire C**. Reading must show **OL ($>100\text{ M}\Omega$)**.
3. Measure resistance between **Wire A** and **Wire C**. Reading must show **OL ($>100\text{ M}\Omega$)**.
4. Measure resistance between each wire (**A, B, C**) and **`J_EARTH`**. All readings must show **OL ($>100\text{ M}\Omega$)**.
*(Any measurable resistance under DC indicates a shorted trace, solder whisker, or damaged GDT).*

### 2.3 Resistor & Diode Passive Values
1. Measure resistance across `R1`: must read **$2.20\text{ k}\Omega \pm 1\%$** ($2.178\text{--}2.222\text{ k}\Omega$).
2. Measure resistance across `R2`: must read **$2.20\text{ k}\Omega \pm 1\%$**.
3. Switch DMM to **Diode Test Mode**:
   * Red probe on `D1` Anode (left lead / from R1), Black probe on `D1` Cathode (right lead / toward LED). Reading must show forward voltage drop of **$\approx 0.55\text{V to } 0.70\text{V}$**.
   * Reverse the probes: reading must show **OL (Infinite resistance)**.
   * Repeat the forward and reverse test on `D2`.

---

## 5. Phase 3: Active DC +36V Bench Commissioning

This test replicates the shed switchboard's **Diagnostic TEST Mode** to verify active LED drive, current consumption, and reverse-polarity protection.

```
                     [ BENCH DC TEST HOOKUP ]
   [ +36V DC Supply ] ────────┬───► J_IN Pin 1 (Wire A)
                              └───► J_IN Pin 3 (Wire C)
   [ 0V Return / Gnd ] ───────────► J_IN Pin 2 (Wire B)

   [ J_LED_A: Pad 1 (+) ] ────────► APEM LED A (Red Flying Lead)
   [ J_LED_A: Pad 2 (-) ] ────────► APEM LED A (Black Flying Lead)

   [ J_LED_C: Pad 1 (+) ] ────────► APEM LED C (Red Flying Lead)
   [ J_LED_C: Pad 2 (-) ] ────────► APEM LED C (Black Flying Lead)
```

### 3.1 Normal Forward Test (+36V DC Injected)
1. Connect two [APEM Q10F5SXXSG02E](MATERIALS.md) LEDs:
   * **LED A**: Red lead into `J_LED_A` Pad 1 (`+`), Black lead into Pad 2 (`-`).
   * **LED C**: Red lead into `J_LED_C` Pad 1 (`+`), Black lead into Pad 2 (`-`).
2. Insert jumper wires into `J_IN`:
   * Wire A (Pin 1) & Wire C (Pin 3) tied to **+36V DC**.
   * Wire B (Pin 2) tied to **0V DC Return**.
3. Energize the 36V power supply:
   * [ ] **Both Green LEDs (LED A and LED C) illuminate immediately with crisp, bright green output.**
4. Measure active circuit parameters with your DMM:
   * [ ] **Total Current Consumption:** Supply current should read **$\approx 30.0\text{ mA}$** ($\approx 15.0\text{ mA}$ per channel).
   * [ ] **LED Forward Voltage:** Measure across Pad 1 & Pad 2 of `J_LED_A`: reads **$\approx 2.0\text{V to } 2.2\text{V}$**.
   * [ ] **Diode Forward Drop:** Measure across `D1`: reads **$\approx 0.70\text{V}$**.
   * [ ] **Resistor Voltage Drop:** Measure across `R1`: reads **$\approx 33.1\text{V}$** ($I = 33.1\text{V} / 2.2\text{k}\Omega \approx 15.0\text{ mA}$, $P \approx 0.50\text{W}$).
5. **Thermal Soak Test (10 Minutes):**
   * Allow the board to run for 10 minutes. Touch `R1` and `R2`: the 1W metal film resistors should be gently warm to the touch ($< 45^\circ\text{C}$), operating safely at only 50% rated dissipation.

### 3.2 Reverse-Polarity Immunity Test (-36V Applied)
1. Power off the supply.
2. Swap the input supply leads at `J_IN`:
   * Connect **Wire B (Pin 2)** to **+36V DC**.
   * Connect **Wires A & C (Pins 1 & 3)** to **0V DC Return**.
3. Energize the 36V supply:
   * [ ] **Both LEDs MUST remain completely DARK.**
   * [ ] **Supply current MUST read $0.00\text{ mA}$ ($<1\ \mu\text{A}$ leakage).**
   * [ ] Touch `R1`, `R2`, `D1`, `D2`: all components remain completely cold ($P = 0\text{ W}$).
4. *Engineering Conclusion:* Proves the 1N4007G diodes (1,000V rated) provide absolute, fail-safe reverse-flow protection against shed switchboard miswiring or supply inversion.

### 3.3 Single-Wire Fault Simulation (Channel Independence)
1. Restore normal forward polarity (+36V on A and C; 0V on B).
2. **Sever Core A:** Disconnect the wire going into `J_IN` Pin 1:
   * [ ] **LED A turns OFF immediately.**
   * [ ] **LED C remains brightly illuminated.**
   * [ ] Supply current drops from $\approx 30\text{ mA}$ to $\approx 15\text{ mA}$.
3. Reconnect Pin 1 and **Sever Core C** (disconnect Pin 3):
   * [ ] **LED C turns OFF immediately.**
   * [ ] **LED A remains brightly illuminated.**
4. Disconnect **Wire B (Pin 2)**:
   * [ ] **Both LEDs turn OFF immediately.**
5. *Engineering Conclusion:* Confirms 100% channel isolation and validates that field fault-finding will pin-point the severed core down to the exact 100m span.

---

## 6. Phase 4: Enclosure & Standoff Mechanical Dry-Fit

Before potting with silicone gel, verify the physical interface inside a WISKA COMBI 308 enclosure.

```
       ┌───────────────────────────────────────────────────────────┐
       │             WISKA COMBI 308 ENCLOSURE FLOOR               │
       │                                                           │
       │     [H1: Standoff] ─────────────────── [H2: Standoff]     │
       │           │                                   │           │
       │           │       DOG FENCE PCB (v1.1.0)      │           │
       │           │             (63 x 56 mm)          │           │
       │           │                                   │           │
       │     [H3: Standoff] ─────────────────── [H4: Standoff]     │
       │                                                           │
       │  ═════════════════ 9.5mm Standoff Clearance ════════════  │
       └───────────────────────────────────────────────────────────┘
```

1. Snap four [Essentra LCBSBM-6-01A-RT](MATERIALS.md) 9.5mm nylon standoffs into the corner holes of the PCB.
2. Test-fit the board into the bottom of a **WISKA COMBI 308** box:
   * [ ] Confirm the board sits level with uniform **9.5mm clearance** above the floor (provides adequate volume for silicone gel potting underneath the PCB).
   * [ ] Verify the outer edge of the PCB maintains $\ge 4.5\text{mm}$ clearance to the inner box walls.
   * [ ] Confirm that a 3.0mm terminal screwdriver has direct, unimpeded vertical access to all screw clamping heads on `J_IN`, `J_EARTH`, `J_LED_A`, and `J_LED_C`.
3. Fit the lid with 2× APEM LEDs installed:
   * [ ] Verify the rear bodies of the LEDs and their flying leads do not collide with `GDT_AC` or the rising cage terminals when the lid is screwed fully closed.

---

## 7. Quality Acceptance Sign-Off Sheet

Record test results for each of the 5 prototype boards:

$$\begin{array}{|c|c|c|c|c|c|c|}
\hline
\textbf{Board \#} & \textbf{Visual / DFM} & \textbf{Cold Isolation} & \textbf{Forward 36V} & \textbf{Reverse Block} & \textbf{Single Break} & \textbf{Status} \\
\hline
\text{SN-001} & \text{[ ] PASS} & \text{[ ] PASS} & \text{[ ] PASS (}\approx 30\text{mA)} & \text{[ ] PASS (0mA)} & \text{[ ] PASS} & \text{[ ] ACCEPT} \\
\text{SN-002} & \text{[ ] PASS} & \text{[ ] PASS} & \text{[ ] PASS (}\approx 30\text{mA)} & \text{[ ] PASS (0mA)} & \text{[ ] PASS} & \text{[ ] ACCEPT} \\
\text{SN-003} & \text{[ ] PASS} & \text{[ ] PASS} & \text{[ ] PASS (}\approx 30\text{mA)} & \text{[ ] PASS (0mA)} & \text{[ ] PASS} & \text{[ ] ACCEPT} \\
\text{SN-004} & \text{[ ] PASS} & \text{[ ] PASS} & \text{[ ] PASS (}\approx 30\text{mA)} & \text{[ ] PASS (0mA)} & \text{[ ] PASS} & \text{[ ] ACCEPT} \\
\text{SN-005} & \text{[ ] PASS} & \text{[ ] PASS} & \text{[ ] PASS (}\approx 30\text{mA)} & \text{[ ] PASS (0mA)} & \text{[ ] PASS} & \text{[ ] ACCEPT} \\
\hline
\end{array}$$

### Gate Sign-Off for Full 40-Board Production
When all 5 prototype units achieve **100% PASS** across all verification phases:
1. Retain Board #1 as a reference bench golden sample.
2. Proceed to **[`ORDERING.md`](ORDERING.md) Section 5** to initiate the final 40-board production run.
