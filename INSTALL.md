# Dog Fence Indicator & Surge Protection System (v1.1.0)
**Comprehensive End-to-End Installation & Field Manual**

---

## 1. System Overview & Architecture

This manual covers the complete workshop pre-assembly, field installation, shed switchboard wiring, testing, and marine-grade gel potting for the **4km perimeter dog containment fence**.

```
                           [ CENTRAL SHED SWITCHBOARD ]
           ┌────────────────────────────────────────────────────────┐
           │  • DogWatch SmartFence Transmitter (T1, T2)            │
           │  • 36V DC Diagnostic Power Supply (Mean Well)          │
           │  • Phoenix Contact UK 5-HESILED 60 (2A Fast-Blow Fuse) │
           │  • 4PDT Heavy-Duty Changeover Switch (Center-Off)      │
           └───────────────────────────┬────────────────────────────┘
                                       │
                  ┌────────────────────┴────────────────────┐
                  ▼                                         ▼
         [ Loop Start: A, B, C ]                   [ Loop Return: A, B, C ]
                  │                                         │
                  └───────────────────┬─────────────────────┘
                                      │
               4km 3-Core 2.5mm² Cable Loop (Effective Area: 7.5mm², R ≈ 9.3 Ω)
                                      │
    ┌─────────────────────────────────┴─────────────────────────────────┐
    │                                                                   │
    ▼ (Every 100m)                                                      ▼ (At 0m, 1km, 2km, 3km, 4km)
[ 35× STANDARD MILESTONES ]                                 [ 5× SURGE & GROUNDING MILESTONES ]
• WISKA COMBI 308 Enclosure                                 • WISKA COMBI 308 Enclosure
• Dog Fence PCB (60×52mm, 2 oz Cu, ENIG)                    • Dog Fence PCB (60×52mm, 2 oz Cu, ENIG)
• 2× APEM IP67 Green LEDs (Wires A & C)                     • 2× APEM IP67 Green LEDs (Wires A & C)
• 3× WAGO 221-613 Lever Splices                             • 3× WAGO 221-613 Lever Splices
• Potted with WISKA MP0100 Silicone Gel                     • Dual 2.5mm² Earth Runs into J_EARTH
                                                            • 5/8" UL 467 Copper-Bonded Ground Rod
                                                            • Potted with WISKA MP0100 Silicone Gel
```

---

## 2. Workshop Pre-Assembly Phase (Bench Setup)

Perform these steps in a clean workshop to assemble all 40 junction boxes before heading into the field.

```
       [ STEP 1: LID PREPARATION ]                 [ STEP 2: BASE & PCB PREPARATION ]
       ┌─────────────────────────┐                 ┌─────────────────────────────────┐
       │   (O) LED A   (O) LED C │                 │  [Essentra 9.5mm Standoffs]     │
       │    ▲           ▲        │                 │  Snapped to 4 PCB Corners       │
       │    └─ 10mm ────┘        │                 │                │                │
       │       Holes             │                 │  Wipe Box Base with IPA & Stick │
       └─────────────────────────┘                 └─────────────────────────────────┘
```

### Step 2.1: Drill LED Holes in the WISKA 308 Lids
1. Mark two drilling centers on the faceplate of the **WISKA COMBI 308** lid (spaced $\approx 35\text{--}40\text{ mm}$ apart).
2. Using a **10mm step drill bit** (or 10mm hole punch), drill clean, deburred 10.0mm holes.
3. Insert the [APEM Q10F5SXXSG02E](MATERIALS.md) LEDs (2V Raw Version):
   * Ensure the **black nitrile O-ring** is positioned on the outside face of the lid.
   * From the underside of the lid, install the lock washer and hex nut.
   * Tighten the nut securely ($1.5\text{--}2.0\text{ Nm}$) to compress the O-ring for an IP67 seal.

### Step 2.2: Mount PCB Inside the Enclosure
1. Clean the flat interior floor of the WISKA box using an **Isopropyl Alcohol (IPA) wipe** to remove all plastic mold-release oils. Allow 30 seconds to dry.
2. Take the manufactured **Dog Fence PCB** and snap four [Essentra LCBSBM-6-01A-RT](MATERIALS.md) (9.5mm height) standoffs into the $3.2\text{ mm}$ mounting holes ($H_1, H_2, H_3, H_4$).
3. Peel the protective release film from all four adhesive pads simultaneously.
4. Position the PCB centrally on the enclosure floor with terminal blocks oriented as follows:
   * `J_IN` (3-pin 7.62mm) facing **Left** (toward incoming pigtails).
   * `J_LED_A` & `J_LED_C` (2-pin 5.08mm) facing **Top** and **Bottom** edges (toward LED lid leads).
   * `J_EARTH` (3-pin 7.62mm) facing **Right** (mirrored across from J_IN).
5. Press down firmly for 5 seconds to set the high-tack adhesive.

> [!NOTE]
> **Adhesive Longevity:** Standard self-adhesive pads inevitably fail over 20+ years outdoors due to heat cycling and humidity. However, their only job here is to temporarily hold the PCB off the floor for the 24 hours it takes the WISKA silicone potting gel to cure (see Step 6). Once cured, the solid silicone block permanently suspends the PCB, making the long-term failure of the adhesive completely irrelevant!

### Step 2.3: Pre-Wire Internal PCB Leads
1. **LED Flying Leads:**
   * Wire **LED A** leads into `J_LED_A`: Red/Anode ($+$) to **Pad 1 (`+` Silkscreen)**; Black/Cathode ($-$) to **Pad 2 (`-` Silkscreen)**.
   * Wire **LED C** leads into `J_LED_C`: Red/Anode ($+$) to **Pad 1 (`+` Silkscreen)**; Black/Cathode ($-$) to **Pad 2 (`-` Silkscreen)**.
   * *(Note: the two LED connectors are mirror-placed on the board so one faces each outward side; silkscreen `+`/`-` remains the authoritative guide.)*
2. **Pigtail Tap Wires:**
   * Strip three $\approx 12\text{ cm}$ lengths of $2.5\text{ mm}^2$ wire (Brown = A, Blue = B, Green-Yellow or Black = C).
   * Insert one end of each pigtail into `J_IN` on the PCB (heavy-duty 7.62mm pitch rising cage terminal):
     * Pin 1 = **Wire A**
     * Pin 2 = **Wire B**
     * Pin 3 = **Wire C**
   * Tighten the rising cage screws firmly with a 3.0mm flathead screwdriver.
3. **Pre-Attach WAGO Connectors:**
   * Snap the free end of Pigtail A into Port 1 of a [WAGO 221-613](file:///home/mark/projects/dogfence-1.0/MATERIALS.md).
   * Snap Pigtail B into Port 1 of a second WAGO `221-613`.
   * Snap Pigtail C into Port 1 of a third WAGO `221-613`.
   * Leave Ports 2 & 3 open for the incoming/outgoing 3-core cables in the field.

---

## 3. Field Installation of Milestone Junction Boxes

```
          [ WISKA COMBI 308 MOUNTED ON POST (0.8m–1.2m Height) ]
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                                                                           │
 │  INCOMING 3-CORE CABLE                              OUTGOING 3-CORE CABLE │
 │  (2.5mm² Outdoor SWA/Tough PVC)                     (2.5mm² Outdoor Cable)│
 │          │                                                    │           │
 │          │   ┌────────────────────────────────────────────┐   │           │
 │          └───┤ WAGO 221-613 (Core A In + Out + Pigtail A) ├───┘           │
 │              ├────────────────────────────────────────────┤               │
 │              │ WAGO 221-613 (Core B In + Out + Pigtail B) │               │
 │              ├────────────────────────────────────────────┤               │
 │              │ WAGO 221-613 (Core C In + Out + Pigtail C) │               │
 │              └─────────────────────┬──────────────────────┘               │
 │                                    │ (3x Pigtails)                        │
 │                                    ▼                                      │
 │                            ┌──────────────┐                               │
 │                            │ J_IN (A,B,C) │                               │
 │                            │  (7.62mm P)  │      ┌───────────┐            │
 │                            │              │ ───> │  J_LED_A  │ ──> LED A  │
 │                            │  PCB BOARD   │      └───────────┘     (IP67) │
 │                            │  (60 x 52mm) │                               │
 │                            │              │      ┌───────────┐            │
 │                            │   J_EARTH    │ ───> │  J_LED_C  │ ──> LED C  │
 │                            │  (7.62mm P)  │      └───────────┘     (IP67) │
 │                            └──────┬───────┘                               │
 │                                   │ (3-Pin Mirrored Earth Block)          │
 └───────────────────────────────────┼───────────────────────────────────────┘
                                     │ (Redundant Earth Wires)
                                     ▼ (Only at 5 Surge Boxes: 0, 1k, 2k, 3k, 4k)
                             [ BRONZE B-CLAMP ]
                                     │
                    [ 5/8" UL 467 COPPER-BONDED ROD ]
                                     │
                             (Deep Soil Ground)
```

### Step 3.1: Enclosure Mounting on Fence Posts
* **Height:** Mount the box at **$0.8\text{m} \text{ to } 1.2\text{m}$ above ground level** (keeps it clear of weeds/strimmers and places LEDs at eye level).
* **Fixing:** 
  * *Timber Posts:* Fasten the snap-on mounting clip to the post using two $4.0\text{ mm} \times 35\text{ mm}$ stainless steel woodscrews, then click the box into the bracket. Alternatively, drive 4 screws through the corner holes.
  * *Metal / Pipe Posts:* Secure with heavy-duty UV-resistant cable ties or stainless steel Jubilee clips through the mounting bracket slots.
* **Orientation:** Position cable entry ports facing **downward** and faceplate pointing toward the patrol track.

### Step 3.2: Cable Entry & Termination
1. Route the arriving and departing 3-core $2.5\text{ mm}^2$ cables up to the bottom of the box, forming a **$50\text{ mm}$ downward drip loop** so water runs off the cable away from the entry glands.
2. Strip $\approx 60\text{ mm}$ of the outer cable jacket and strip $13\text{ mm}$ from each core conductor.
3. Terminate into the three WAGO 221-613 connectors:
   * **Wire A:** Incoming Core A into Port 2; Outgoing Core A into Port 3.
   * **Wire B:** Incoming Core B into Port 2; Outgoing Core B into Port 3.
   * **Wire C:** Incoming Core C into Port 2; Outgoing Core C into Port 3.
4. Snap all orange levers closed. Verify bare copper is fully seated with no exposed strands.

### Step 3.3: Earth Grounding Installation (Surge Stations Only: 0m, 1km, 2km, 3km, 4km)
1. Drive the **5/8" UL 467 copper-bonded earth rod** vertically into the soil directly below the milestone post until the top of the rod sits just below ground level (or inside a shallow inspection pit).
2. Attach the heavy bronze/brass rod-to-cable B-clamp to the top of the rod.
3. Strip $25\text{ mm}$ from **two or three separate $2.5\text{ mm}^2$ green/yellow earth wires** and clamp them all firmly under the B-clamp for multi-path redundancy.
4. Route the earth wires into the box through the bottom M20 entry.
5. Terminate the earth wires directly into the PCB's mirrored 3-pin 7.62mm screw terminal (`J_EARTH`):
   * Insert the earth conductors into the poles of `J_EARTH` (all 3 poles are internally bridged by the massive 4.5mm 2 oz copper Earth bus).
   * Tighten all screws firmly.
   * *(Note: Standard non-surge milestone boxes leave `J_EARTH` unpopulated/empty).*

---

## 4. Central Shed Switchboard & Hub Installation

```
             ┌───────────────────────────────────────────────────────────┐
             │            SHED SWITCHBOARD / HUB SCHEMATIC               │
             └───────────────────────────────────────────────────────────┘

           [ 230V AC Mains ]
                  │
                  ▼
       ┌─────────────────────┐
       │ 36V DC Power Supply │ (Mean Well NDR-75-36)
       │    (+V)       (-V)  │
       └─────┬───────────┬───┘
             │           │
    [ Phoenix Contact ]  │
    [ UK 5-HESILED 60 ]  │
    [ 2A Fast-Blow Fuse] │
             │           │
             ▼           │
       [ +36V Bus ]      │
             │           │
             │           └────────────────────────────────┐
             │                                            │
             │   ┌────────────────────────────────────────┼──────────────┐
             ▼   ▼                                        ▼              ▼
     ┌─────────────────────────────────────────────────────────────────────────────┐
     │                      4PDT CHANGEOVER SWITCH (S1)                            │
     │                                                                             │
     │  [Pole 1: Start A,C]  [Pole 2: Start B]   [Pole 3: End A,C]   [Pole 4: End B]│
     │  Pin 1: SmartFence T1 Pin 4: SmartFence T1 Pin 7: SmartFence T2 Pin 10: T2   │
     │  Pin 2: [Start A + C] Pin 5: [Start B]     Pin 8: [End A + C]   Pin 11: End B│
     │  Pin 3: +36V DC Fuse  Pin 6: EMPTY (N/C)   Pin 9: EMPTY (N/C)   Pin 12: 0V   │
     └───────┬───────────────────┬───────────────────┬───────────────────┬─────────┘
             │                   │                   │                   │
             ▼                   ▼                   ▼                   ▼
     [ Start of Cores A,C ] [ Start of Core B ] [ End of Cores A,C ] [ End of Core B ]
```

### Step 4.1: Switchboard Component Mounting
1. Mount a 35mm DIN rail inside a dry wall-mounted enclosure in the shed.
2. Snap the **36V DC Power Supply** and **Phoenix Contact `3004139` (UK 5-HESILED 60)** fuse block onto the DIN rail.
3. Install the **Littelfuse `0217002.MXP` (2A Fast-Blow)** fuse into the fuse holder carrier.
4. Mount the **4PDT Heavy-Duty Switch** onto the enclosure front panel.

### Step 4.2: Switchboard Terminal Connections & 4PDT Pinout Matrix

Viewed from the **rear (pin / terminal side)** of the 4PDT switch (12 pins arranged in 4 columns of 3):

```
       [ REAR VIEW OF 4PDT SWITCH TERMINALS (4 COLUMNS × 3 ROWS) ]
       ┌────────────────────┬────────────────────┬────────────────────┬────────────────────┐
       │ Column 1 (Pole 1)  │ Column 2 (Pole 2)  │ Column 3 (Pole 3)  │ Column 4 (Pole 4)  │
┌──────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤
│Row 1 │ [ Pin 1 ]          │ [ Pin 4 ]          │ [ Pin 7 ]          │ [ Pin 10 ]         │
│(RUN) │ SmartFence T1      │ SmartFence T1      │ SmartFence T2      │ SmartFence T2      │
├──────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤
│Row 2 │ [ Pin 2 ] (COMMON) │ [ Pin 5 ] (COMMON) │ [ Pin 8 ] (COMMON) │ [ Pin 11 ] (COMMON)│
│(COM) │ Start A & Start C  │ Start B            │ End A & End C      │ End B              │
├──────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤
│Row 3 │ [ Pin 3 ]          │ [ Pin 6 ]          │ [ Pin 9 ]          │ [ Pin 12 ]         │
│(TEST)│ +36V DC (via Fuse) │ EMPTY (N/C)        │ EMPTY (N/C)        │ 0V DC Return (-)   │
└──────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘
```

| Switch Pin | Connection Target | Wire Spec | Function |
| :---: | :--- | :---: | :--- |
| **Pin 1** | DogWatch SmartFence **Terminal 1** (T1) | $2.5\text{ mm}^2$ | RF Drive to Start A & C (RUN mode) |
| **Pin 4** | Bridge to **Pin 1** (SmartFence T1) | $2.5\text{ mm}^2$ Jumper | RF Drive to Start B (RUN mode) |
| **Pin 7** | DogWatch SmartFence **Terminal 2** (T2) | $2.5\text{ mm}^2$ | RF Return from End A & C (RUN mode) |
| **Pin 10**| Bridge to **Pin 7** (SmartFence T2) | $2.5\text{ mm}^2$ Jumper | RF Return from End B (RUN mode) |
| **Pin 2** | **Start A** AND **Start C** | $2 \times 2.5\text{ mm}^2$ | Start of the 4km Loop (Cores A & C) |
| **Pin 5** | **Start B** | $2.5\text{ mm}^2$ | Start of the 4km Loop (Core B) |
| **Pin 8** | **End A** AND **End C** | $2 \times 2.5\text{ mm}^2$ | Far end of the 4km Loop (Cores A & C) |
| **Pin 11**| **End B** | $2.5\text{ mm}^2$ | Far end of the 4km Loop (Core B) |
| **Pin 3** | **+36V DC** (From load side of 2A Fuse Block) | $2.5\text{ mm}^2$ | Diagnostic +36V DC Supply (TEST mode) |
| **Pin 6** | **EMPTY** (Leave disconnected) | - | Isolates Start B during TEST mode |
| **Pin 9** | **EMPTY** (Leave disconnected) | - | Isolates End A & C during TEST mode |
| **Pin 12**| **0V DC Return** (Direct to Power Supply `-V`) | $2.5\text{ mm}^2$ | Diagnostic 0V Ground Return (TEST mode) |

#### Electrician's Pro-Tip: The "Forward Loop" Diagnostic Feed
This exact wiring achieves a "forward loop" constant-length circuit in TEST Mode. +36V pushes into Start A & C, flows through the milestone LEDs, and continues forward down Wire B to exit at End B. This perfectly balances voltage drop (meaning uniform brightness at all 40 milestones) AND allows you to easily tell *which* core broke during a fault:
*   **If Wire A/C breaks:** LEDs *before* the break light up; LEDs *after* the break are dark.
*   **If Wire B breaks:** LEDs *before* the break are dark; LEDs *after* the break light up.

#### Switch Plate Labeling
Clearly label the 3 switch positions on your control panel / faceplate:
* **UP:** `FENCE RUN (SMARTFENCE ACTIVE)`
* **CENTER:** `STORM ISOLATE (ALL DISCONNECTED)`
* **DOWN:** `CABLE TEST (+36V DIAGNOSTIC)`


---

## 5. Pre-Potting Electrical Commissioning & Testing

**DO NOT pour potting gel until these three verification checks are complete:**

```
   TEST 1: Loop Resistance Check        TEST 2: DC TEST Mode Illumination     TEST 3: SmartFence RF Collar Check
   ┌───────────────────────────┐        ┌───────────────────────────────┐     ┌────────────────────────────────┐
   │ Multimeter on 4km Loop    │        │ Switch to DOWN (TEST MODE)    │     │ Switch to UP (RUN MODE)        │
   │ Verify R ≈ 9.3 Ω (±2 Ω)   │        │ Verify all 80 LEDs Glow Bright│     │ Walk perimeter with dog collar │
   └───────────────────────────┘        └───────────────────────────────┘     └────────────────────────────────┘
```

1. **Test 1: DC Continuity & Loop Resistance**
   * Set switch to **CENTER (OFF)**.
   * Measure resistance between the Start and End of Wires A, B, and C with a digital multimeter.
   * Total loop resistance for the 4km run should be **$\approx 9.3\ \Omega$** ($\pm 2\ \Omega$).
2. **Test 2: Diagnostic TEST Mode (LED Verification)**
   * Toggle the switch **DOWN (TEST MODE)**.
   * The 36V power supply will energize. Total supply current should read $\approx \mathbf{1.21\text{ A}}$ (80 LEDs × 15 mA nominal before 4km cable drop).
   * Walk or drive the 4km perimeter: **Both green LEDs (LED A and LED C) should illuminate at all 40 milestone boxes**. Expect a **progressive brightness gradient** along the run (the voltage-drop from 41.4Ω combined loop resistance distributes across milestones); near-end boxes glow brightest. Fault-finding compares A vs C *pairing* at each box, not absolute brightness.
   * *If any LED is dark:* Check for reversed flying leads ($+$ and $-$ swapped at `J_LED`) or a loose WAGO lever.
3. **Test 3: SmartFence RUN Mode (RF Transparency)**
   * Toggle the switch **UP (RUN MODE)**.
   * The SmartFence transmitter will engage its $4\text{ kHz}$ or $10.7\text{ kHz}$ carrier.
   * **All milestone LEDs must remain completely DARK.** (The 1N4007 diodes block the RF signal).
   * Walk the perimeter with a DogWatch test receiver collar to verify full, uniform boundary activation.

---

## 6. Marine-Grade Potting & Gel Encapsulation

Once electrical commissioning is 100% verified, encapsulate every junction box for **submersible IP68 marine durability**.

```
                  [ TOP M20 PORT 1 ]                      [ TOP M20 PORT 2 ]
                 Pour Gel Through Funnel                  Acts as Air Vent / Sight Glass
                           │                                         ▲
                           ▼                                         │
              ┌────────────┴─────────────────────────────────────────┴────────────┐
              │               WISKA 308 LID (Fully Screwed Down)                  │
              ├───────────────────────────────────────────────────────────────────┤
              │  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  │ ◄── Stop when gel crowns!
              │  │  [ APEM LED Bodies & Wire Ends 100% Submerged ]              │  │     (100% Full / 0% Air)
              │  │                                                              │  │
              │  │  [ WAGO 221-613 Connectors Submerged ]                       │  │
              │  │                                                              │  │
              │  │  [ PCB, Terminals, Diodes, GDTs Submerged ]                  │  │
              │  │  ════════════════ 9.5mm Standoff Gap ══════════════════════  │  │
              │  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  │
              └───────────────────────────────────────────────────────────────────┘
```

### The "Closed Pour + Top Vent" Procedure (Guarantees 0% Air Headspace):

1. **Secure the Lid:**
   * Close the WISKA COMBI 308 lid and firmly tighten the 4 captive corner screws to compress the perimeter gasket.
2. **Open Two Top Access Ports:**
   * Unscrew the top-left **M20 plug** (Fill Port).
   * Unscrew the top-right **M20 plug** (Air Vent & Sight Glass).
3. **Mix the Gel:**
   * Take the two-part [WISKA MP0100 silicone gel](file:///home/mark/projects/dogfence-1.0/MATERIALS.md) (Part A and Part B).
   * Mix thoroughly for 60 seconds until a uniform translucent blue mixture is achieved.
4. **Pour the Enclosure:**
   * Insert a small funnel into Port 1.
   * Pour the liquid gel slowly. The gel floods the floor, flows under the 9.5mm PCB standoffs, submerges the terminals and WAGOs, and rises toward the ceiling.
   * Air exhausts freely through Port 2.
5. **Stop Point:**
   * The instant gel reaches the roof and **crowns at the lip of Vent Port 2**, stop pouring ($\approx 180\text{--}190\text{ ml}$ total).
6. **Cap & Seal:**
   * Screw both M20 threaded plugs with their rubber O-rings back into the ports.
   * The box is now a **100% solid, void-free silicone block**. It will cure into soft, self-healing elastic gel in 20–30 minutes.

---

## 7. Operational & Fault-Finding Guide

### Switch Positions

| Switch Position | Mode Name | System State & Behavior |
| :---: | :--- | :--- |
| **UP** | **FENCE RUN** | SmartFence transmitter active. All milestone LEDs dark. Loop operates at full containment power. |
| **CENTER** | **STORM ISOLATE** | Completely disconnects the 4km cable loop from both the transmitter and power supply. Recommended during severe electrical storms. |
| **DOWN** | **CABLE TEST** | Disconnects transmitter; injects +36V DC onto Wires A & C. Milestone LEDs light sequentially to indicate continuity. |

---

### How to Pinpoint Cable Faults in TEST Mode

If the fence transmitter alarms for a wire break:

```
[ Shed (0m) ] ───► [ Box 1 (100m) ] ───► [ Box 2 (200m) ] ───► ✕ (BREAK AT 240m) ───► [ Box 3 (300m) ]
  LEDs: ON           LEDs: ON              LEDs: ON              (Wire A severed)        LED A: OFF
                                                                                         LED C: ON
```

1. Flip the switch to **DOWN (CABLE TEST)**.
2. Drive or walk along the perimeter observing the milestone LED pairs:
   * **Both LEDs ON:** Cable cores A, B, and C are healthy up to this point.
   * **LED A OFF / LED C ON:** Core A is broken between this milestone and the preceding box.
   * **LED C OFF / LED A ON:** Core C is broken between this milestone and the preceding box.
   * **Both LEDs OFF:** Core B (Common Return) is broken, or all cores are severed.
3. The exact fault location is isolated to the **specific 100m span** between the last lit box and the first dark box!

---

### Re-Entering a Potted Box for Maintenance
* The cured **WISKA MP0100 silicone gel is non-hardening and re-enterable**.
* If a box ever needs repair or wire changes:
  1. Unscrew the 4 lid screws and pull the lid off.
  2. Peel away the soft silicone gel by hand or with a plastic scraper (it comes away cleanly from the WAGOs and PCB terminals).
  3. Perform your electrical repair or component replacement.
  4. Top the box back up with a small cup of freshly mixed MP0100 gel and recap.
