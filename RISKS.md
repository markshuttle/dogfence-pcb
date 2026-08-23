# Electrical & Environmental Risk Analysis
**Dog Fence Indicator & Surge Protection System (v1.0.2)**

---

## 1. Overview & Purpose

This document provides a comprehensive risk and failure-mode analysis for the 4km perimeter containment fence system. It covers reverse flow, wiring errors, electrical faults, transient surges, and environmental hazards across both **SmartFence (RUN Mode)** and **Diagnostic (TEST Mode)**.

---

## 2. Reverse Flow & Polarity Reversal Analysis

### A. SmartFence RUN Mode (Transmitter Flow Reversal)
* **Condition:** Reversing the DogWatch SmartFence transmitter output leads ($T_1 \leftrightarrow T_2$), or swapping the perimeter loop start/end feed.
* **Component Impact:** **Zero risk.**
* **Engineering Rationale:**
  * The SmartFence transmitter generates an AC RF carrier ($4\text{ kHz}$ or $10.7\text{ kHz}$, $\approx 10\text{--}20\text{ V RMS}$).
  * An AC signal alternates polarity thousands of times per second; there is no static positive or negative pole. Swapping $T_1$ and $T_2$ is electrically identical to a $180^\circ$ phase shift in an isolated closed loop.
  * In RUN mode, Wires A, B, and C are strapped in parallel at both ends, forming a single continuous $7.5\text{ mm}^2$ loop. Inter-core voltage difference across milestone boards is negligible ($<0.1\text{ V}$).
  * The [1N4007G](file:///home/mark/projects/dogfence-1.0/AGENTS.md) diodes have a **1,000V Peak Repetitive Reverse Voltage ($\text{V}_{\text{RRM}}$)** rating, easily blocking any instantaneous AC potential with $>970\text{V}$ headroom.
  * The Gas Discharge Tubes ([GDTs](file:///home/mark/projects/dogfence-1.0/pcb/pcb.kicad_sch)) are non-polar, bidirectional devices.

---

### B. DC TEST Mode (Power Supply Polarity Inversion)
* **Condition:** Applying $+36\text{V DC}$ to **Wire B** (Return) and $0\text{V}$ (Negative) to **Wires A & C** (Supply).
* **Component Impact:** **Zero risk.**
* **Engineering Rationale:**

```
               [ REVERSED DC TEST CONDITION: -36V applied across rung ]

     [ Wire A/C (0V / DC Neg) ]                     [ Wire B (+36V DC) ]
                 │                                            │
                 ├──[ 2.2kΩ 1W ]───[ 1N4007G ]───[ LED ]──────┤
                 │     (R1/R2)       (D1/D2)      (A/C)       │
                 │                                            │
                 ▼                                            ▼
           Current = 0 mA                             Blocks Full 36V
           Power   = 0 W                              (Rated for 1000V)
```

1. **[1N4007G](file:///home/mark/projects/dogfence-1.0/pcb/pcb.kicad_sch) Blocking Diodes ($D_1, D_2$):**
   * Reverse-biased when Wire B is positive relative to Wires A/C.
   * Rated for **1,000V DC blocking**. At $-36\text{V}$, the diode remains fully off, exhibiting only negligible leakage current ($I_R < 50\text{ nA}$ typical at room temperature, $<5\ \mu\text{A}$ max at extreme temperature).
2. **LED Indicators ($J_{LED\_A}, J_{LED\_C}$):**
   * Standard indicator LEDs have a maximum reverse breakdown voltage of $\approx 5\text{ V}$.
   * Because the 1N4007 diode is in series with the LED, almost the entire $36\text{V}$ reverse potential drops across the 1N4007. The LED experiences virtually $0\text{ V}$ reverse bias and zero breakdown stress.
3. **Current-Limiting Resistors ($R_1, R_2$):**
   * With current blocked ($I \approx 0\text{ A}$), power dissipation is $P = I^2 R = 0\text{ W}$ (no heating or thermal stress).
4. **Gas Discharge Tubes ($GDT_1, GDT_2, GDT_3$):**
   * Symmetrical spark gap threshold is $420\text{--}470\text{ V}$. At $\pm 36\text{V}$, they remain open circuits ($>1\text{ G}\Omega$ isolation).
5. **Practical Symptom:** Milestone LEDs will remain **OFF** until polarity is corrected. No component degradation or lifespan reduction occurs.

---

### C. Cable Ring Feed Direction (Start vs. End Loop Feed)
* **Condition:** Connecting the start of the 4km cable to the end terminals.
* **Component Impact:** **Zero risk.**
* **Engineering Rationale:**
  * By routing Start A & C to the +36V supply and End B to the 0V return (the "forward loop" setup), the total cable length traversing any milestone is always exactly 4km. Swapping which physical cable end is designated "Start" vs "End" at the switchboard simply reverses the direction of the diagnostic flow, but maintains perfectly equalized voltage drop and fault isolation.
  * In RUN mode, the SmartFence transmitter sees the continuous 7.5mm² loop regardless of terminal orientation.
---

## 3. Wiring Errors & Accidental Fault Scenarios

| Fault Scenario | Immediate Effect | Component Safety | Resolution / Safeguard |
|:---|:---|:---|:---|
| **LED Flying Leads Inverted (`+` and `-` swapped at `J_LED_A` / `J_LED_C`)** | Affected LED does not light in TEST mode. | **Safe.** Protected by series 1N4007 diode and 2.2kΩ resistor. | Swap wire leads at screw terminal so Anode matches `+` (Left pad). |
| **Pigtail Wires Swapped at `J_IN` (e.g., A into B, B into A)** | Milestone rung logic inverted at that specific box. | **Safe.** 1N4007 diodes block reverse voltages; forward rungs limit current to $<15\text{ mA}$. | Rewire pigtails to match terminal silkscreen (`A`, `B`, `C`). |
| **Short Circuit Between Cores (e.g., Core A shorted to Core B in cable)** | In TEST mode: 36V power supply sees short across loop resistance. In RUN mode: Transmitter impedance shifts. | **Protected.** In TEST mode, the 2A inline power supply fuse blows instantly, protecting wiring and PCB traces. | Clear cable short; replace 2A fast-blow fuse. |
| **Earth Stake Connected at Standard Milestone (Non-Surge Box)** | No operational effect; earth bus connects to GDTs only. | **Safe.** GDTs maintain 470V galvanic isolation between earth and signal lines. | Harmless, but extra ground stakes are only required at the 5 designated surge stations. |
| **Earth Wire Connected Directly to Wire A, B, or C (Bypassing `J_EARTH`)** | Fence loop becomes directly grounded, attenuating the SmartFence RF signal. | **Safe for components; inhibits RF fence boundary.** | Move ground lead to `J_EARTH` terminal so GDT spark gaps isolate earth from RF. |
| **Simultaneous RUN & TEST Mode Activation** | High-voltage DC injected into transmitter output stage. | **Prevented by Hardware.** Break-before-make 4PDT changeover switch physically isolates the DC supply when RUN mode is active. | Use dedicated 4PDT center-off changeover switch as specified in [INSTALL.md](file:///home/mark/projects/dogfence-1.0/INSTALL.md). |

---

## 4. Surge & High-Voltage Transient Risks

* **Direct Lightning Strike / High-Energy Induction:**
  * **Protection:** Ruilon 2R470TD-8 / Bourns 2027-42 GDTs rated for **20,000A (20kA)** impulse discharge ($8/20\ \mu\text{s}$) on all three conductor cores.
  * **PCB Track Sizing:** Fabricated with heavy **2 oz copper (70 µm)** and wide copper pours to carry transient discharge currents to earth rods without trace fusing.
  * **Component Overload Headroom:** 1N4007G diodes tolerate **30A forward surge ($I_{\text{FSM}}$)**; 1W metal film resistors operate at only **50% rated power** during continuous DC test ($0.50\text{ W}$).

---

## 5. Environmental & Long-Term Durability Risks

| Environmental Hazard | Mechanism of Degradation | Mitigating Design & Manufacturing Control |
|:---|:---|:---|
| **Subterranean Moisture & Condensation** | Water ingress causing galvanic corrosion and RF leakage to ground. | **IP68 Potting:** WISKA COMBI 308 enclosures backfilled with re-enterable two-part silicone gel (WISKA MP0100). |
| **Coastal / Marine Salt Air & Fog** | Airborne saline aerosol ($NaCl$) causing crevice corrosion on terminal screws and copper wire wicking. | **100% Potting Encapsulation:** Complete submersion of PCB, WAGOs, and rear LED flying leads leaves zero internal air headspace. |
| **Thermal Cycling (-40°C to +90°C)** | Solder joint fatigue, micro-cracking, and board delamination. | **High-TG Substrate:** Shengyi S1000H TG155 laminate with low Z-axis thermal expansion coefficient. |
| **Copper Oxidation (20+ Year Life)** | Exposed copper tarnishing and increasing terminal contact resistance. | **ENIG 2U" Gold Plating:** Electroless Nickel Immersion Gold creates a pore-free 24k gold barrier over all copper surfaces. |
| **Vibration & Mechanical Stress** | Terminal screw loosening or wire pull-out. | **Rising Cage Clamp Terminals:** Cixi Kefa KF129S/KF128 M3 steel screws clamping on 2.5mm² solid/stranded copper. |

---

## 6. Summary Risk Assessment

$$\begin{array}{|l|c|c|l|}
\hline
\textbf{Event} & \textbf{Likelihood} & \textbf{Component Damage Risk} & \textbf{Fail-Safe Mechanism} \\
\hline
\text{SmartFence Flow Reversal} & \text{Medium} & \textbf{None (0\%)} & \text{AC RF Carrier symmetry} \\
\text{DC Test Polarity Reversal} & \text{Medium} & \textbf{None (0\%)} & \text{1N4007 1000V reverse blocking} \\
\text{Loop Ring Reversal} & \text{Low} & \textbf{None (0\%)} & \text{Closed ring circuit architecture} \\
\text{LED Terminal Inversion} & \text{Low} & \textbf{None (0\%)} & \text{Diode + resistor reverse isolation} \\
\text{Transient Overvoltage / Surge} & \text{High (Rural)} & \textbf{Ultra-Low} & \text{20kA GDTs + 2 oz Cu Ground Bus} \\
\text{Moisture Ingress} & \text{High (Buried)} & \textbf{Ultra-Low} & \text{IP68 Silicone gel encapsulation} \\
\hline
\end{array}$$
