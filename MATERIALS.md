# Materials And Procurement Tracker

**Draft hardware revision 1.2.0-dev; reviewed baseline 1.1.0. Reconciled against the 41-station requirements on 2026-09-06.**

This ledger preserves recorded **ORDERED**, **ON HAND**, existing and pending items. ORDERED does not mean delivered, inspected, suitable for the revised design, or allocated to a particular test/field unit. No additional purchase or supplier allocation is asserted by this update. Confirm receipts, exact supplied identities and usable quantities before ordering shortfalls.

The field baseline is **41 stations at 0, 100, ..., 4000 m**, including two separate shed-end boards, with **36 standard + 5 earth-connected stations** and one additional shed control hub. Full rollout and the **five fully assembled JLCPCB prototypes** remain subject to [REMEDIATION release gates](REMEDIATION.md#release-gates), [ORDERING.md](ORDERING.md), and [ACCEPTANCE.md](ACCEPTANCE.md).

## 1. Station Inventory

Field requirements below exclude spare/attrition quantities and additional assemblies retained or consumed by qualification.

| Item | Recorded quantity / status | 41-station requirement | Balance / qualification |
| :--- | :--- | :--- | :--- |
| PCBA | **5 prototypes planned**, no confirmed fabrication order. Earlier 40-board follow-on figure was planning, not a purchase. | **41 installed boards** | Quote five complete prototypes first; determine follow-on quantity using section 2. Standard FR-4, 2 oz both layers, ENIG, nominal 1.6 mm, green mask default; no assumed high-Tg or filled vias. |
| Panel LEDs | **80 APEM Q10F5SXXSG02E, ORDERED** | **82**, two per station | **Shortfall 2**, before separate prototype use/loss or spares. No-internal-resistor model, not a regulated 2 V lamp. Limits and 5 m daylight acceptance: [LED.md](LED.md). |
| Adhesive PCB supports | **160 Essentra LCBSBM-6-01A-RT, ORDERED** | **164**, four per station | **Shortfall 4** before extra assemblies. Nominal 9.53 mm spacing, 3.18 mm support hole and 1.57 mm panel specification; obtain tolerances and verify board/box/adhesive fit. |
| Through-splice connectors | **120 WAGO 221-613, ORDERED** | **123**, three per station | **Shortfall 3** before extra assemblies. Three-way 0.5-6 mm^2 / listed 41 A component series; verify applicable conductor/termination data. Each splices incoming/outgoing core and PCB tap. |
| Junction boxes | Prior plan: **40 WISKA COMBI 308, Pending**; none recorded ordered | **41 field boxes** | All 41 remain to procure, plus any separate test/spare boxes. Nominal external 85 x 85 x 51 mm; dry-fit the complete assembly, not the PCB alone. |
| Boundary cable glands | Prior plan: **80 M20 glands/locknuts, Pending**; none recorded ordered | **82 boundary-cable entry positions** at two per field box | If both entries use glands, procure 82 correctly sized glands, **plus separately determined earth/hub entry hardware**. Select the actual WISKA-compatible gland/seal arrangement and cable diameter range, not M20 thread or an IP68 label alone. |
| MP0100 gel | **Approximately 7-8 litres WISKA MP0100, ORDERED** in the existing record | Estimated **7.38-7.79 litres** for 41 boxes at the old 180-190 ml/box allowance | Actual package volume, formulation, usable yield and fill requirement need confirmation. No proven surplus: allowance excludes mixing/pour waste and separate potted tests. Do not assume an assembled IP68/hermetic rating. |
| Internal PCB tap wire | **Approximately 20 m, ON HAND**, spare 2.5 mm^2 cable strippings | **123 taps**, about **18.45 m of single-conductor wire** at 0.15 m/tap | Verify usable single-core length, colours and actual routing; nominal 1.55 m remainder is before trimming, test use and waste, not reserved spare stock. Never use green/yellow for active A/B/C taps. |
| Optional WAGO housings | Earlier candidates: WAGO **207-1333** size 3 or **207-1331** size 1; optional planning quantity 40 or 120, **no purchase recorded** | Not part of the agreed station baseline | No approved allocation. Confirm exact 221-613 fit, enclosure volume and material compatibility before adopting; MP0100 is not automatic evidence either for or against their need. |

WISKA's published COMBI 308 IP66 membrane / specified IP67 gland arrangements are **component/enclosure conditions**, not a tested rating for drilled LED lids and gel-filled stations. Earth wire entries may need different approved sealing hardware; do not assume multiple single cores seal in an ordinary single-cable gland. Both shed-end boxes and hub-side cable tails must be counted in the final entry drawing.

## 2. Prototype And Spare Allocation

The initial requirement is **five individual fully assembled boards**, including all SMT and THT work and controlled GDT lead forming, with **no field soldering**. The reviewed board has 14 electrical parts (two SMT, twelve THT), but this remains a baseline pending protection approval. Recount from `pcb/` when quoting; `pcb/BOM.csv` is the sourcing authority, not this field-material ledger.

- Retain at least **one unpotted reference**. Identify boards used for destructive tests, gel trials or earlier design revisions; do not automatically count them as field spares or installed boards.
- Let **p** be same-release prototypes individually accepted and allocated to the field, and **s** the explicitly approved field-spare quantity. With one retained reference, **0 <= p <= 4**; more test retention/losses can reduce p. The follow-on assembled-board requirement is **41 - p + s**. Neither p nor s is yet allocated.
- Bench tests can share suitable removable LEDs/harnesses. Do not deduct the same purchased LEDs/supports/WAGOs from both a retained test box and the field inventory. Record actual consumption and recovery.
- If **q extra complete station assemblies** remain outside the 41 field units, those assemblies plus the field require **41 + q boards/boxes, 82 + 2q LEDs, 164 + 4q supports, 123 + 3q WAGOs**, and **82 + 2q boundary glands** where using two glands per box. Count any additional unboxed reference/test boards, loose harnesses, test losses, earth/hub entries, cable, gel and consumables separately. This is an allocation formula, not an order.
- As a budgeting example only, five separately boxed prototypes would use 10 LEDs, 20 supports, 15 WAGOs, five boxes, ten boundary glands and about 2.25 m of single-core tap wire. Not all five need be boxed or potted; preserve the unpotted reference and determine gel use from the test plan. Those items are **not new purchases** recorded here.

The field-only shortfalls of **2 LEDs / 4 supports / 3 WAGOs** are therefore minimums against the recorded orders, not a complete shopping list for qualification and spares. Five prototypes do not imply a purchase of five spare enclosures or ten spare LEDs.

## 3. Shed Hub Inventory

| Item | Recorded quantity / status | Current requirement / action |
| :--- | :--- | :--- |
| Previously described 4PDT centre-off switch | **1, ORDERED** in the historical record; exact received identity not verified | Preserve the purchase record, **not the old wiring design**. That description does not meet the six-independent-cable-end requirement. Keep unapproved for this function pending identity and contact review; no replacement purchase recorded. |
| Six-pole switch candidate | **Kraus & Naimer CA10.A362**, candidate only | Not confirmed purchased. Obtain exact contact program, DC load-breaking suitability and global transfer sequence across all poles. Its 20 A thermal/AC data is not DC or lightning-isolation approval. |
| 36 V PSU | **1, ORDERED**; user believes **Mean Well LRS-35-36** | **Confirm nameplate**. If LRS-35-36, rated 36 V / 1 A / 36 W. Earlier generic larger-supply examples were not proof of a purchased model. Verify actual output setting/limits and wiring. |
| Higher-capacity PSU candidate | **Mean Well LRS-75-36**, candidate only | 36 V / 2.1 A / 75.6 W; user willing to upgrade. Not a confirmed purchase and not a fix for C5 fuse/GDT follow-current coordination. |
| Fuse holder and fuses | **1 Phoenix Contact 3004139 (UK 5-HESILED 60) holder, one working fuse plus 5 spare Littelfuse 0217002.MXP fuses, ORDERED** | Historical specification is 5 x 20 mm, fast 2 A. Verify supplied parts and 36 V indicator operation. Published fuse DC interrupting capability does not demonstrate clearing of every cable-limited fault or a safe powered GDT. |
| Switchboard jumper wire | **Approximately 3 m of 2.5 mm^2 tri-rated single-core copper, ON HAND** | Check usable lengths, insulation, termination and identification against the approved six-pole layout; no fixed unverified terminal numbering. |
| DogWatch SmartFence transmitter and protector | **1 system, Existing** | Confirm actual model, all supply/backup sources and regional OEM requirements for the proposed boundary and earthing. |
| Hub enclosure / mounting plate | **1, Pending** | Select after switch/PSU dimensions, protective segregation, terminal access, ventilation and labeling/indication requirements are established. |

The same-end TEST connection is **Start A/C positive, Start B DC negative, End A/B/C individually isolated**; RUN connects all start cores to T1 and all end cores to T2 using source-side ties. OFF isolates all six cable ends. See the [functional matrix](README.md#hub-contact-matrix); no permanent field-end straps or unverified switch pin assignments. TEST/OFF mean the RF fence is inactive, not storm-safe isolation.

Capacity reference only: the nominal forward-only 41-station cable model draws **0.8477 A / 30.52 W**, five boards near the source **0.1509 A / 5.43 W**, and all 41 near the source **1.2375 A / 44.55 W**. These are calculated loads, not fault/thermal qualification or justification to replace the PSU without coordination analysis. [README.md](README.md#3-electrical-limits-and-open-protection-work) gives assumptions and open C4/C5 work.

## 4. Cable And Site Materials

| Item | Identity / purchase status | Requirement / evidence |
| :--- | :--- | :--- |
| Boundary cable | Likely **Oceanflex CM03/05.100**, supplier code **P01018**, from [12 Volt Planet](https://www.12voltplanet.co.uk/CAB3CTNTW2.5PNT.html). Purchased identity and quantity **unconfirmed**, not newly ordered here. | 4 km route plus measured tails, bends, slack and installation allowance. Listing: three tinned-copper 2.5 mm^2 cores, 35/0.30 mm strands/core, maximum 7.3 mm OD, **60 V maximum, -15 to +70 degrees C complete cable**. Verify actual reel, colours and maximum conductor resistance. |
| Route supports and conduit | No purchase quantity/status recorded | Survey the 0.3-1.0 m elevated timber-fence route and driveway/gate crossings. Verify exposed UV/weather suitability and wet-conduit compatibility; conduit can flood and is not electromagnetic shielding. Do not assume the cable is SWA/armoured or mains-rated. |

The cable's ISO 6722 / 105-degree reference is for its cores, not the complete cable; no -40-degree arctic or impulse-withstand claim is established. The supplier's black/red table does not identify all three core colours. Record A/B/C assignments from the actual cable, with no green/yellow active conductor.

The site is coastal Isle of Man, less than 1 km from the sea, with observed ambient roughly **-10 to +30 degrees C**, rain/salt/condensation and some sun-exposed boxes. These are observations, not lifetime extremes or maximum internal temperatures. A separate energized cattle wire may run **at least 0.5 m away for up to 300 m**; record this qualification exposure rather than claiming separation alone makes it safe. Allow for wire movement and keep the boundary electrically separate from supporting/energized fence wires.

## 5. Earthing Inventory

Earth-connected station locations remain 0, 1000, 2000, 3000 and 4000 m. The proposed shed connection is shared with the DogWatch protector and both shed-end boards. **Five stations do not automatically require five independent electrodes.** A qualified installer's site-specific PE/bonding design and regional OEM instructions determine installed allocation.

| Item | Recorded quantity / status | Action before installation |
| :--- | :--- | :--- |
| Copper-bonded steel rods | **5, ORDERED**. Historical requested specification: UL 467 / BS EN 62561-2, minimum 250 micrometres copper | Confirm actual manufacturer, dimensions and conformity evidence. Preserve stock; do not automatically install one unbonded rod per station or claim a service-life guarantee. |
| Rod clamps | **5, ORDERED**, described as bronze/brass B-clamps for 5/8-inch rods | Verify supplied rod diameter, conductor number/size, torque, corrosion suitability and approval. Do not assume two conductors are permitted in a clamp without its instructions. |
| Green/yellow earth wire | **Approximately 30 m total of 2.5 mm^2 6491X, ORDERED** | Historical plan used two parallel 2.5 mm^2 leads at each earth station. Final size, routing, termination and quantity are subject to the earthing/protection design; combined area is not proof of equal surge sharing or adequacy. |
| Inspection pits | **5, Pending** in the earlier plan | Final count follows actual electrode design and inspection access, not simply station count. |

The PCB's three `J_EARTH` pins are connected together; this does not create a 72 A terminal rating. Do not directly earth a fence core or assume PSU negative should be bonded to earth. Inventory ownership is not installation authorization or evidence of a qualified surge path.

## 6. Tools And Consumables

All tools below were pending in the existing ledger unless explicitly identified as an added requirement. No tool purchase is asserted.

| Tool / item | Recorded status | Use / qualification |
| :--- | :--- | :--- |
| 10 mm step drill / punch | Pending | Nominal Q10 LED cutout; use the exact indicator drawing, tolerance, seal and panel-thickness requirements. |
| Terminal screwdriver | Pending | Earlier suggested 3.0-3.5 mm flat blade; verify actual screw fit and manufacturer's terminal torque. |
| Wire strippers / cutters | Pending | Suit the cable cores and fine LED flying leads without strand damage. |
| IPA cleaning wipes | Pending | Earlier proposed support-base cleaning; verify enclosure/adhesive/gel compatibility and required preparation rather than assuming any solvent process is suitable. |
| Digital multimeter | Pending | De-energized continuity/diode checks and appropriate DC measurements per ACCEPTANCE; not proof of GDT firing, tiny leakage or surge survival. |
| Outdoor labels / tags | Pending | **41 station positions, 0 to 4000 m**, A/B/C identities, LED polarity, and clear hub RUN/OFF/TEST/fence-inactive labeling. |
| Suitable torque tool for LEDs | Required; no purchase recorded | APEM mounting torque **0.20-0.25 Nm**, subject to exact supplied model instructions. Do not substitute terminal screw torque. |
| Thermal logging and qualification equipment | Required scope; no purchase recorded | Determine with ACCEPTANCE and qualified test personnel. Temperature must be measured; touch is not thermal acceptance. |

## 7. Outstanding Procurement Actions

- Confirm receipts/usable stock without changing the historical orders: **80 LEDs, 160 supports, 120 WAGOs**, gel, hub items, rods/clamps/wire and on-hand tap/jumper wire.
- Allocate prototypes, retained reference, test consumption and any spares. Field minimum shortfalls remain **2 LEDs, 4 supports and 3 WAGOs** before those allocations.
- Procure **41 field enclosures** and choose/count **82 boundary gland positions** plus approved earth/hub entries and any separately allocated test/spare boxes. These remain pending, not purchased.
- Confirm PSU nameplate and ordered switch identity. Quote the LRS-75-36 and CA10.A362 only as candidates, subject to their electrical/contact approval.
- Confirm cable identity/length/colours/resistance/environmental evidence, exact MP0100 packages/yield/process, component and enclosure fit, and the site earthing design.
- Request the actual five-board JLCPCB quote, parts/attrition allocation and CAM/placement/solder/forming approvals only when the release gates permit. No new C4/C5 protection parts or alternative LEDs are approved purchases by this ledger.
