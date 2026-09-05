# Project Bill of Materials & Procurement Tracker
**Dog Fence Indicator & Surge Protection System (v1.1.0)**

---

## 1. Overview

This document tracks all physical hardware, enclosures, switchgear, cabling, grounding, and consumables required for the 4km perimeter installation (40 milestone junction boxes + 1 central shed switchboard hub). 

---

## 2. Central Control Station & Shed Switchboard

| Component | Description / Specification | Qty | Part Number / Supplier | Status | Notes |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **4PDT Changeover Switch** | Heavy-Duty **Center-Off (ON-OFF-ON)** Toggle or Rotary Cam Switch (min 2A, 250VAC) | 1 | *4PDT ON-OFF-ON Switch* | ✅ **ORDERED** | Toggles between **RUN** (SmartFence), **OFF** (Storm isolate), and **TEST** (+36V DC). |
| **36V DC Power Supply** | 36V DC 2A–5A DIN Rail or Enclosed Supply | 1 | *e.g., Mean Well NDR-75-36 / LRS-75-36* | ✅ **ORDERED** | Powers diagnostic LEDs along the 4km run in TEST mode. |
| **DC Fuse Holder & Fuse** | **5×20mm Fast-Blow 2A Fuse (F2A 250V)** + DIN Rail LED Fuse Terminal | 1 (plus 5× spares) | **Phoenix Contact `3004139` (UK 5-HESILED 60)**<br>+ **Littelfuse `0217002.MXP` (5×20mm 2A Fast)** | ✅ **ORDERED** | Integrated LED glows RED if fuse blows. Protects 36V supply against short circuits. |
| **Switchboard Jumper Wire** | **2.5mm² (13–14 AWG)** Tri-rated copper hookup wire | ~3m | *Spare 2.5mm² Single Core* | ✅ **ON HAND** | For interconnecting switch poles, DC supply, and transmitter terminals. |
| **SmartFence Transmitter** | DogWatch SmartFence Base Station + Surge Protector | 1 | *DogWatch SmartFence* | ⏳ Existing | System base transmitter. |
| **Switch Enclosure / Plate** | Wall-mount enclosure or DIN-rail control box | 1 | *Standard ABS / Metal Enclosure* | ⏳ Pending | Houses switch, 36V PSU, and fuse in shed. |

---

## 3. Milestone Junction Boxes (40 Stations along 4km)

| Component | Description / Specification | Qty | Part Number / Supplier | Status | Notes |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **PCBA Boards** | **Dog Fence Indicator & Surge 1.1.0** (60×45mm, 2 oz Cu, ENIG, High-TG FR4, 6-GDT Full-Hybrid) | 40 | JLCPCB / PCBWay Turnkey PCBA (see ORDERING.md) | ⏳ Pending | 35 standard milestones + 5 surge milestones. Ready to order via ORDERING.md. |
| **Panel LED Indicators** | IP67 Green LED Panel Indicator (10mm mount, 2V standard version) | 80 | **APEM `Q10F5SXXSG02E`** | ✅ **ORDERED** | 2 per box. Wire anode to the silkscreen `+` pad on the board mirrored LED connectors. |
| **Adhesive Board Standoffs** | Self-Adhesive Snap-Lock Nylon PCB Supports (9.5mm / 3/8" height, 3.2mm hole) | 160 | **Essentra `LCBSBM-6-01A-RT`** | ✅ **ORDERED** | 4 per box. Elevates PCB by 9.5mm for 360° silicone gel encapsulation. |
| **Silicone Potting Gel** | Re-enterable two-part silicone encapsulation gel (~180–190ml per box) | ~7–8 Litres | **WISKA MP0100** | ✅ **ORDERED** | Submersible IP68 hermetic seal. Poured into WISKA boxes after wiring & testing. |
| **Internal Pigtail Tap Wire** | 2.5mm² solid/stranded copper wire (~15cm per tap) | ~20m total | *Spare 2.5mm² 3-core Cable Strippings* | ✅ **ON HAND** | Connects each WAGO 221 lever tap into PCB `J_IN` (`A`, `B`, `C`). |
| **Continuous Cable Connectors** | 3-Way Compact Lever Splicing Connector (**0.5–6mm² / 41A**) | 120 | **WAGO `221-613`** | ✅ **ORDERED** | 3 per box (Wires A, B, C continuous through-splice; 6mm² series for easy insertion). |
| **WAGO Gelbox (Optional)** | IPX8 Pre-filled Gel Housing | 40 or 120 | **WAGO `207-1333`** (Size 3)<br>or **`207-1331`** (Size 1) | ⏳ Optional | *Note: WISKA MP0100 pour-in gel already encapsulates WAGOs.* |
| **Junction Box Enclosures** | IP66/IP67 Outdoor Junction Box (85 × 85 × 51 mm) | 40 | **WISKA COMBI 308** | ⏳ Pending | UV-resistant, threaded M20 entries + puncture membranes. |
| **Cable Glands (Optional)** | M20 IP68 Cable Glands with Locknuts | 80 | *Standard M20 IP68 Nylon Glands* | ⏳ Pending | Recommended if using SWA armoured cable or exterior conduit. |

---

## 4. Earth Grounding Stations (5 Locations: 0m, 1km, 2km, 3km, 4km)

| Component | Description / Specification | Qty | Part Number / Supplier | Status | Notes |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **Earth Ground Rods** | **UL 467 / BS EN 62561-2 Certified** Copper-Bonded Steel Earth Rods (min 250µm Cu) | 5 | *UL 467 Copper-Bonded Rods* | ✅ **ORDERED** | Driven deep at 0m, 1km, 2km, 3km, 4km marks for multi-decade lightning protection. |
| **Earth Rod Clamps** | High-strength bronze/brass rod-to-cable B-clamps | 5 | *Standard 5/8" Earth Rod Clamp* | ✅ **ORDERED** | Clamps both 2.5mm² earth wires to driven copper rod. |
| **Dual Earth Cable** | **Dual 2.5mm² (5.0mm² total)** Green/Yellow Earth Wire | ~30m total | *2.5mm² 6491X Earth Cable* | ✅ **ORDERED** | Runs 2 parallel 2.5mm² wires into Pole 1 & Pole 2 of `J_EARTH` on each surge PCB. |
| **Earth Inspection Pits** | Small polymer / concrete earth rod inspection box (optional) | 5 | *Standard Earth Housing Pit* | ⏳ Pending | Protects top of rod and clamp; allows inspection. |

---

## 5. Tools & Installation Consumables

| Tool / Item | Specification / Purpose | Status |
| :--- | :--- | :---: |
| **10mm Step Drill Bit / Punch** | Clean 10mm cutout in WISKA 308 box lids for the APEM LED indicators | ⏳ Pending |
| **Terminal Screwdriver** | Small 3.0mm–3.5mm flathead for PCB rising cage screw terminals | ⏳ Pending |
| **Wire Strippers & Cutters** | Stripping 2.5mm² cable cores and fine LED flying leads | ⏳ Pending |
| **IPA Surface Cleaning Wipes** | Isopropyl alcohol wipes to degrease enclosure base before applying adhesive standoffs | ⏳ Pending |
| **Digital Multimeter** | Continuity, DC voltage check, and diode test during commissioning | ⏳ Pending |
| **Outdoor Label Maker / Tags** | Labeling boxes 1–40 and marking wire cores A, B, C | ⏳ Pending |

---

## 6. Procurement Progress Summary

* **Milestone LEDs:** ✅ **Complete** (80× APEM `Q10F5SXXSG02E` ordered)
* **Board Standoffs:** ✅ **Complete** (160× Essentra `LCBSBM-6-01A-RT` ordered)
* **PCBA Manufacturing:** ⏳ **Pending** (40× boards v1.1.0 ready for order via ORDERING.md)
* **Silicone Potting Gel:** ✅ **Complete** (WISKA MP0100 ordered)
* **36V Power Supply:** ✅ **Complete** (Ordered)
* **Shed Changeover Switch:** ✅ **Complete** (4PDT ON-OFF-ON Switch ordered)
* **Earth Clamps:** ✅ **Complete** (5× 5/8" Rod B-clamps ordered)
* **Earth Rods & Earth Cable:** ✅ **Complete** (5× UL 467 rods & dual 2.5mm² cable ordered)
* **Internal Pigtail Tap Wire:** ✅ **Complete** (Using spare 2.5mm² cable)
* **WAGO Splicing Connectors:** ✅ **Complete** (WAGO `221-613` 6mm² series ordered)
* **DC Fusing:** ✅ **Complete** (Phoenix Contact `3004139` + Littelfuse `0217002.MXP` ordered)
* **Enclosures:** ⏳ Pending (40× WISKA COMBI 308)

