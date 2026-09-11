# Environment And Hub Evidence

**Hardware 1.2.0-dev; original research at checkpoint 97e202d on 2026-09-07; hybrid checkpoint 6ba2a07; catalogue-switch evidence updated 2026-09-07.**

Controlled environment/hub evidence. The original bounded research edited only
this file; the later documentation synchronization recorded the user's clarified
site scope and the then-implemented PR02/BYG23T circuit using the design BOM and
[DESIGN_BOUNDS.md](DESIGN_BOUNDS.md). The subsequent P2 switch continuation
visually reads the manufacturer's catalogue contact graphic and rechecks its
application restrictions; it does not change the circuit or assign hub wiring.
No supplier acceptance, procurement allocation or physical qualification is
recorded. **C4, C5, W3, W1 and W4 remain open.**

**2026-09-11 resistor correction:** the prototype BOM only selects
**TE Connectivity 35212K2FT / C4129105** (2512 SMT, 2.2 kohm / 2 W / 1%, AEC-Q200,
in stock at JLCPCB). The user confirms **Yageo SR2512FK-7W2K2L /
[C876850](https://jlcpcb.com/partdetail/C876850) ORDERED** with an advised 20-day
wait for future production, not receipt, inspection or job allocation. The prior
Uni-Royal PS12 order was cancelled/refunded due to stockout; [MATERIALS](../MATERIALS.md)
preserves its historical 110-part order separately. Whole-BOM
`allocation_verified` remains `false`. TE prototype results do not establish
Yageo thermal qualification: [ORDERING](../ORDERING.md) requires separate
production-part review, controlled BOM/CAD, library, model and note updates and
reverification before production release.

Use [ELECTRICAL](ELECTRICAL.md) and [DESIGN_BOUNDS](DESIGN_BOUNDS.md) for current
TE evidence from **9-1773463-5, Rev G, 02/2025**. Its +/-100 ppm/C at 2.2 kohm
is supported; the retained 25 C reference and -30..125 C linear screen are
engineering assumptions, not verified TE TCR test conditions. TE page 3's
four-layer, 2 oz outer / 4 oz inner mounting/thermal reference differs from the
actual two-layer board, so P70/derating transfer is conditional, not proof of
two-layer failure. [ASSEMBLY](ASSEMBLY.md) controls the retained alternate
project lands and pending supplier placement/stencil/solder acceptance.
PR02 mounting/thermal arithmetic below and PS12 overload/pulse data are
historical evidence, not TE or Yageo qualification. No new environmental or
switch research, physical qualification or prototype-file gate is added.

## User-Confirmed Corrections

- Cable core colours are **red, black and PLAIN green**, not green/yellow.
  The user subsequently confirmed actual reel labels **CM03/05.100** and
  **"3 CORE (3 x 35/0.30) TINNED BLACK 100 MTR"**. V.3 identifies CM03/05 as
  **3 x 2.5 mm^2**. Product identity/colours are settled; manufacturing-revision
  applicability is not established by those markings. No A/B/C assignment is made here.
- The gel is **WISKA OneGel, NOT MP0100**. This is an identity correction, not
  authorization to transfer MP0100 instructions or substitute another gel.
- **Kraus & Naimer CA10.A364** replaces CA10.A362 as the provisional switch
  candidate. Its current catalogue naming and pole count need the correction
  below; it is not an approved switch or pinout.
- **Two Mean Well LRS-75-36 supplies are ORDERED; one TEST, one disconnected spare.**
  Do not describe them as merely proposed upgrades. ORDERED does not establish
  receipt, inspection, output settings, or serial-number assignment to those roles.
  No parallel, series, separate-channel or opposite-end supply connection is
  specified. Preserve earlier procurement history separately.
- **Energized cattle fencing is prohibited near the entire 4 km boundary cable,
  every station and the hub**, not only the shed. The user explicitly withdrew
  the former **0.5 m / up to 300 m parallel exposure**; it is historical, not a
  current mandatory qualification case. Inspect and maintain the prohibition
  instead of energizer-on/off testing within the accepted installation. If land
  use changes or the hazard returns, reassess before use. No numerical safe
  separation, zero induction or zero lightning exposure is established.
- LED damage from accidental **low-voltage installation polarity errors** is
  accepted with replacement spares, whose quantity is still unallocated. Direct
  lightning-strike rebuilding is accepted, not all ordinary/nearby transient
  damage. **Continuous-safe normal TEST remains mandatory without a timer.**

## AMC Oceanflex Cable

Primary source [C1] is the user's exact **2026 Update V.3**, one-page
"Tinned Copper 3 Core Cables" sheet. AMC's current download directory [C2]
links that exact PDF and its matching page image [C3]. The image was viewed
as well as the PDF text extraction. The extractor reports a publication/file
timestamp of **2026-05-07 13:49:15 GMT**; that timestamp is not a reel date.

| Item | V.3 manufacturer evidence | Correction / boundary |
| :--- | :--- | :--- |
| Conductors | Class 5, tinned copper; CM03/05 row is 3 x 2.5 mm^2, representative 3 x 35/0.30 mm construction | The footnote permits strand configuration to differ. Do not identify a reel from strand count alone. |
| Sheath | PVC; CM03/05 black sheath | The sheet does not separately identify the core-insulation compound. Do not substitute another polymer's properties. |
| Working voltage | 12/24 V applications, **60 V max DC** | Unchanged from the older 60 V assumption. Not mains, megger-test or surge-withstand approval. |
| Operating temperature | **-30 to +70 C** in the cable specification | Replaces the older -15 to +70 C listing for the current documented product, conditional on reel applicability. It is not a +105 C complete-cable rating or a separate installation/flexing-temperature specification. |
| Maximum overall diameter | **7.4 mm** for CM03/05 | Replace 7.3 mm when specifying the current product; choose glands against actual cable dimensions and the accepted range. |
| Core colours / reels | Black, green, red; 30 m and 100 m reels | The user confirms plain green, CM03/05.100 and 100 MTR markings. Lot/date and applicability of the current specification remain separate evidence. |
| Nominal current | 29 A for CM03/05 | Explicitly a guide dependent on application/environment, not the three-core installed cable's guaranteed continuous rating. |
| Chemical / mechanical claims | Corrosion-resistant tinned construction for harsh/marine environments; flame-retardant, high-temperature and chemical-resistant sheathing; resistance to petrol, diesel, lubricating oils, diluted acids, abrasion and cut-through | Qualitative claims, without a coastal service-life, salt-spray duration or mechanical-armour qualification. |
| Standards printed | BS EN 60228:2005; ISO 6722-1:2011; ISO 19642-7; IEC 60332.1.2 | Record the cited editions as printed, not unprovided UV, water-immersion or impulse test results. |
| Bend radius | Printed as **"Min Bend Radius <6x OD"** | Retain the actual wording. The unusual inequality is not an instruction to bend arbitrarily tightly; obtain AMC's applicable static/installation bend limit. |

**Maximum conductor resistance is not numerically stated in V.3.** The
footnote says the cable will meet the "resistance values shown", but neither
the viewed table nor the extracted specification contains a resistance column
or numerical resistance value. Do not invent a value from this dangling
footnote, equate representative strand area with guaranteed resistance, or
promote the model's **6.9 ohm/km / 27.6 ohm per 4 km core** to an AMC maximum.

**UV and wet-conduit qualification remain unestablished.** V.3 does not give
an explicit UV/weathering test, continuous immersion/wet-conduit allowance,
water depth/duration, or impulse withstand. Its sun-like pictogram is labelled
"Navigation Lights (Marine)", not UV resistance. AMC's current marine-range
page [C4] does positively describe OceanFlex resistance to moisture, corrosion
and harsh conditions, and the broader marine range's exposure to moisture and
salt. This is useful application evidence, not a CM03/05 flooded-conduit or
permanent exposed-UV qualification. Do not borrow Arctic-T or Corronex limits.

The precise outstanding AMC evidence is the lot/date and applicable
specification (product identity is now confirmed); maximum DC resistance per core at a stated temperature; and
written applicability to the **0.3-1.0 m elevated, permanently exposed coastal
route and potentially water-filled driveway/gate conduit**. Include installation
bend/temperature limits and cable insulation/impulse data in that response.
Do not reopen the confirmed identity/colour question or assume V.3 upgrades
older stock automatically. [DESIGN_BOUNDS.md](DESIGN_BOUNDS.md) adds a conditional
standard-based 8.21 ohm/km resistance envelope and identifies the 0.30/0.26 mm
strand-construction discrepancy separately from that electrical calculation.

## WISKA OneGel

### Identity And Process

WISKA's UK product entry [G1] identifies **ONEGEL / order no. 10108963**, a
**300 ml transparent-clear cartridge**, as a **mono-component silicone gel**
for junction-box filling, ready for immediate use with **no mixing required**.
The manufacturer's webshop [G3] calls it **ONEGEL-W 300ml WISKA Branded
Cartridge**, SKU OneGel, Luckins **398668015**, and explicitly says mixing
ratio/time **none**, curing time **none**, and re-enterable **yes**.

This supports dispensing ready-to-use gel from a cartridge, not measuring and
mixing two components. It does not establish self-levelling pour behaviour,
viscosity, void-free flow beneath this PCB, a closed fill/vent injection method,
or a fixed millilitre fill. The manufacturer application image [G4] shows
cartridge application into an open wired junction box, not this populated PCB.
Do not prescribe an added catalyst, heat cure or a moisture/acid-cure mechanism.
"Silicone gel" alone does not identify the complete formulation or additives.

WISKA separately lists **MP One - Twist and Go** [G5], with different order
numbers; it is not ONEGEL. Do not import its processing/electrical figures, or
MP0100, Replay, Crystal, resin or WAGO Gelbox formulation claims into OneGel.

### Conflicting Published Fields

The following conflict exists **within WISKA's own public sources**, not just
between a manufacturer and a retailer:

| Property | WISKA product database [G1, G2] | WISKA webshop [G3] | Controlled interpretation |
| :--- | :--- | :--- | :--- |
| Mixing | No mixing, ready to use; generic field says "Mixing Ratio: 1" | No mixing ratio or mixing time | One component; the field "1" is not a 1:1 two-part instruction. |
| Cure / working time | 12 min pot life and 20 min curing at 23 C | Curing time none, immediate use | Do not turn 12/20 min into a station work instruction. Obtain a dated OneGel-specific clarification for the supplied cartridge. |
| Temperature | Family page [G2] says **-20 to +90 C**, labelled only "Temperature range" | **-60 to +200 C**, also labelled "Temperature Range" | Record both; no unqualified selection of the wider range. Neither source provides a separately identified application/dispensing-temperature range or the conditions resolving this difference. |

**Service temperature is not application temperature.** In particular, the
23 C time-test reference is not an installation-temperature range, and the
unexplained -20/+90 C entry must not be relabelled "application temperature"
to make the sources appear consistent. The wider webshop range is not an
approved temperature envelope for the resistor, adhesive, cable or assembly.

Both sources advertise no expiry date, and [G1] says non-toxic. These are
product claims, not a supplied-batch/storage-condition record, indefinite
opened-cartridge cleanliness guarantee, or a substitute for current safety
instructions. Re-enterability establishes access is intended; it does not
promise clean hand-peeling, undamaged adhesive supports, solvent compatibility,
or unrestricted reuse/top-up of removed or contaminated gel.

### Electrical And Thermal Data

- [G1, G2] publish **18 kV/mm dielectric strength**. The readable entry does
  not provide the electrode geometry, test standard, conditioning or an aged,
  contaminated-assembly guarantee. Do not multiply it by the PCB gap to claim
  a qualified insulation or surge voltage.
- [G3] lists **0.6 kV - 1 kV** under voltage. This is not the cable's working
  rating and does not rate the drilled/filled COMBI assembly.
- No numerical **thermal conductivity, thermal resistivity, volume/surface
  electrical resistivity, permittivity or dielectric-loss data** was found in
  the readable OneGel manufacturer sources reviewed. No typical silicone or
  other product's number is adopted. Electrical resistivity and thermal
  resistivity must not be conflated.
- [G3] describes protection from rain, humidity, dust and animal intrusion;
  [G1] markets an IP68 junction-box filler. Neither is an IP68, hermetic,
  structural-support or continuous-thermal qualification of DogFence. The
  raised GDT's physical gap and W3 thermal hold remain unchanged.

The historical **16-part PR02 checkpoint schematic/PCB/BOM** specified **Vishay BCcomponents
PR02000202201FA100**, copper-lead **2.2 kohm / 2 W / 1% / +/-250 ppm/K**, not the
retired MBE0414. Its **0.83 mm maximum lead, 15.24 mm formed pitch and then-retained
1.40/2.40 mm holes/pads** did not establish process acceptance; **>=1.00 mm
body-to-PCB standoff was required at that checkpoint**, not measured or qualified
mounting and not a present SMT requirement. Nominal resistor heat was about
**0.50 W each**. The declared **40.39597 V / zero-drop /
PR02 Rmin = 2120.8275 ohm** screen through 125 C gives **0.769432871 W and
19.047268 mA per branch**, or **1.561875985 A / 63.0935 W for 82 zero-cable
branches**. These are analysis inputs/results, not enforced source limits or
actual hot-spot temperatures; the old 35-37 V window was never implemented.

PR02 is rated **2 W at 70 C local ambient**, derating to zero at **155 C ambient**;
its specific hot-spot maximum is **220 C**, not an allowed OneGel/cable interface
temperature. Its typical **75 K/W mounted example** implies about **57.7 K rise**
at that upper power, not OneGel thermal resistance or a potted prediction. The
proposed 60 C interface / 110 C film development targets in DESIGN_BOUNDS are
not measured results or new user-wide limits. **No closed, gel-filled thermal
test has been performed**; actual local heat flow, solar conditions and all
material limits still govern W3.

The four implemented **Vishay General Semiconductor BYG23T-M3/TR / C145454**
diodes replace the old series 1N4007G parts and add D3/D4 negative output shunts
after D1/D2. They are not forward pulse-current regulators. **75 ns reverse
recovery is not forward-clamp speed**; typical **9 V / 620 ns forward overshoot
at 1.5 A, 12 A/us, 25 C** does not prove <=5 V at the LED. The 1300 V repetitive
reverse rating does not qualify ordinary/nearby-lightning response. D3/D4 do not
alter the upstream GDT paths; **C5 powered recovery is unresolved, not an
observed latched failure**. See DESIGN_BOUNDS and ELECTRICAL for conditional
current/leakage screens, not an inferred environmental qualification.

### Material Compatibility

| Actual interface | Evidence obtained / precise remaining limit |
| :--- | :--- |
| Oceanflex PVC sheath and actual core insulation | PVC sheath is established by [C1]. No OneGel-specific acceptance of this cable's plasticisers/insulation formulation was found. Need compatibility for prolonged gel contact at the accepted internal temperature, not generic PVC chemical-resistance data. |
| COMBI 308 enclosure and gasket | WISKA [M1] identifies **polypropylene (PP)** and **TPE gasket**, not polycarbonate. Published enclosure service is -30 to +100 C; installation -5 to +60 C. These are enclosure limits, not OneGel application limits. Generic junction-box suitability does not establish the modified COMBI 308 assembly's seals, fill level or thermal performance. |
| Nylon/polyamide parts and Essentra LCBSBM-6-01A-RT supports | No OneGel-specific nylon-grade compatibility or acceptance of the exact support/adhesive system was found. Identify the supplied body/adhesive grades and obtain retention/process evidence on the actual PP substrate while exposed to OneGel. Gel is not an alternative load-bearing support. |
| Polycarbonate or other plastics actually fitted | No OneGel-specific PC compatibility statement was found. Do not describe COMBI 308 as PC or infer every transparent connector/indicator plastic's grade. Exact material/stress/temperature conditions matter for acceptance. |
| WAGO 221-613 contacts, housing and levers | General junction-box filling is not exact connector approval. WISKA's "WISKA and WAGO together" leaflet [M2] concerns **COMBI 407 with 221-413**, not OneGel with COMBI 308/221-613. WAGO's Gelbox evidence [M3] covers its own box/connector/**silicone-free polyurethane gel** system, not WISKA silicone OneGel. Neither proves incompatibility; neither closes this combination's acceptance. |

WAGO's current German compatibility page [M3] distinguishes **207-133x for
4 mm^2 connectors** and **207-143x for 6 mm^2 connectors**. The existing optional
207-1331/207-1333 suggestions are therefore not evidence of a 221-613 solution.
No Gelbox substitution, size allocation or enclosure-fit approval is made here.

The specific WISKA response still needed is a dated TDS/process and safety
record for the supplied **OneGel cartridge/lot**, resolving the two temperature
ranges and cure fields, with application/storage conditions, actual thermal
data if available, and acceptance of **AMC PVC, PP/TPE COMBI 308, the exact
Essentra body/adhesive and WAGO 221-613 materials/contacts**. Define removal and
reinstatement without damaging those items. Confirm actual usable cartridge
quantity/yield; the historical 7-8 litre record and 180-190 ml/box estimate do
not establish either. No supplier reply or encapsulated test is yet recorded.

## CA10.A364 Switch

### Program Identification

Kraus & Naimer's **Switch Wiring Diagrams Pocketbook, 10/2025**, pages 5 and
57 [S1], explicitly identifies **WAA364, formerly A364**, as an **eight-pole
double-throw switch with OFF, 60-degree switching**. It identifies **A362 as
six-pole**, not an alternative name for the eight-pole program. The UK Control
& Load Switch Catalogue **2025**, pages 13 and 23 [S2], agrees: WAA364/F071,
eight poles/eight stages, 1-0-2, distinct from A362/six stages.

Thus the requested **CA10.A364 remains a provisional eight-pole-family
candidate**, not a verified six-pole purchase. Obtain the complete offered
order/article code, mounting/handle suffix and contact development, including
factory links, and confirm correspondence to current WAA364. The catalogue
identifies the standard static function, now transcribed from its graphic below,
not an approved physical terminal drawing for the actual switch. No DogFence
terminal assignments or roles for the extra two poles are defined here.

### Catalogue Contact Schedule

The original **2025 catalogue page 23 graphic [S2a]**, top-middle panel headed
`A362, WAA364`, was visually inspected on 2026-09-07. The full **32-terminal
WAA364** programme has eight changeover poles, comprising **16 switched contact
pairs and eight fixed common links**. The shorter A362 boundary in that same
panel is the six-pole programme; do not truncate WAA364 to it or mistake eight
poles for eight terminals.

**Catalogue evidence only, not an installation pinout:** numbers below reproduce
the manufacturer drawing. Row numbers merely enumerate its independent poles;
none is assigned to a cable end, source or auxiliary function. Positions `1`
and `2` are the catalogue detents, not approved RUN/TEST labels or handle poses.

| Catalogue pole | Fixed common link | Contact closed at `1` | Contact closed at `2` |
| :--- | :--- | :--- | :--- |
| 1 | 2-6 | 5-6 | 1-2 |
| 2 | 4-8 | 7-8 | 3-4 |
| 3 | 10-14 | 13-14 | 9-10 |
| 4 | 12-16 | 15-16 | 11-12 |
| 5 | 18-22 | 21-22 | 17-18 |
| 6 | 20-24 | 23-24 | 19-20 |
| 7 | 26-30 | 29-30 | 25-26 |
| 8 | 28-32 | 31-32 | 27-28 |

At `0`, all 16 switched contacts are open, but **the eight fixed common links
remain connected**. The separately drawn links are not a common bus; crossings
do not add connections. For example, the first pole connects the linked `2/6`
common to `5` at `1`, to `1` at `2`, and to neither throw at `0`. Different
field ends must never share a common link. Empty TEST throws would not undo
such a permanent tie, which is the original C3 defect.

This resolves the catalogue's static connectivity, not correspondence to the
offered/supplied article, maximum transfer timing, loaded arc extinction or DC
application approval. Catalogue page 13 [S2] separates switch type, programme
and mounting in its ordering examples and warns that not every function is
standardized for every type. `CA10.A364` alone is not the missing complete code.

### Six-End And Transfer Requirements

Eight available poles can in principle accommodate six independent cable ends,
but that observation does not approve the actual program or link arrangement.
The required **source-side functional ties only** remain:

| Mode | Required boundary connections |
| :--- | :--- |
| RUN | Start A/B/C each switched to T1; End A/B/C each switched to T2. |
| OFF | All six ends separately isolated. |
| TEST | Start A/C to TEST positive, Start B to TEST negative; End A/B/C separately isolated. |

No permanent field-end ties, opposite-end B return, second B return, direction
selector, or new use of the two ordered PSUs follows from choosing eight poles.

**Global break-before-make is not verified by these sources.** Require all
old-source paths to open before any new-source path makes across the complete
used program, in both directions, including specified timing/tolerances and
the applicable loaded interruption conditions. Per-pole non-overlap, common
shaft, centre-off detent and static continuity alone do not prove that. The
manufacturer's general catalogue [S2, page 2] explicitly allows different
contact programs to overlap, advance or lag; the exact program matters.

### DC And Fault Switching

The current **CA10_EN.pdf, v4.2, 2026-08-15 04:24 AM**, page 3 [S3], states:
**"DC switching capacity applies to ON/OFF switches."** Consequently the
family's DC figures cannot automatically approve this changeover function.
The UK DC-selection table [S4, page 11] also says "Switch function on request"
and restricts 60/90-degree switching angles in that DC context to CA...S.
This is an additional application condition, not a claim that ordinary CA10
switches cannot have 60-degree detents.

| Published family datum | Meaning here |
| :--- | :--- |
| Iu/Ith 20 A at 55 C daily ambient with peaks to 60 C; enclosed Ithe 20 A at 35 C with peaks to 40 C [S3] | Thermal carrying ratings, not 20 A DC interruption at 36 V. |
| General DC table: CA10, one series contact, 48 V: DC-21A 14 A (L/R <=1 ms), DC-22A 13 A (<=2.5 ms), DC-23A 12 A (<=15 ms), DC-13 1.7 A (<=100 ms) [S4] | Conditional family reference points, not a 36 V A364 rating. No interpolation, automatic contact-series credit or substitution of CA10S data. |
| Icw 140 A for 1 s and maximum 25 A gG fuse [S3] | Withstand/protection-selection data, not a short-circuit breaking rating or coordination with the project's 2 A 217-series fuse. |
| Ui 690 V and conditioned Uimp 6 kV as switch / 4 kV as switch-disconnector [S3] | The stated supply-system/category/pollution conditions apply. Not outdoor lightning isolation or a rating for the completed hub. |
| Terminal-screw torque 0.60 Nm [S3, page 2] | Family wiring datum, to confirm against the exact supplied assembly/instructions, not an approved hub assembly result. |

The same datasheet [S3, page 3] requires preserving factory-fitted jumper links
when opening terminal clamps, checking that connections are seated, and
tightening **all** terminal screws after wiring. Those instructions do not
authorize adding, removing or relocating links to guess a DogFence pinout.

The manufacturer-specific decision is whether the exact changeover program
can **make and break the actual nominal 36 V DC circuit over its accepted
normal/fault voltage envelope**, not whether normal current is below 20 A.
No enforced 37 V ceiling exists. Provide the accepted normal
current and cable/source RLC conditions; include energizing a short, contact
opening during resistive/cable shorts or GDT follow current, output-capacitor
inrush, PSU hiccup/retry and turn-off energy. A supply's 2.1 A nameplate and a
2 A fuse do not bound every switching transient or ensure prior fault clearing.
No such application approval was found or requested in this research.

Kraus & Naimer's custom-switch service [S5] explicitly offers DC switching
**on request**. A written approval tied to the exact contact development,
global transfer and fault envelope is still needed before physical numbering
or hub energization. Its custom-function form [S6] warns that a customer's
requested contact order may not be technically possible: the effective contact
positions are those in the cam diagram drawn by K&N. A proposed customer matrix
is therefore not the manufacturer's accepted contact development. No supplier
response or physical switch test is recorded. OFF remains ordinary disconnection,
not storm isolation.

## Sources And Retrieval Limits

All sources below were accessed using native webfetch on **2026-09-07**.
Unversioned web pages are dated by retrieval, not treated as formally revised
TDSs. WISKA's main product pages display site "Stand: 06.09.2026 20:09:00";
that is not an identified formulation revision.

- **[C1] AMC exact user-supplied PDF, 2026 Update V.3:** <https://cdn.prod.website-files.com/62deaee72baf3ef3b83165ff/69fc985a23120ee62491a529_14%20-%20AMC%20Datasheet%20%20-%20Oceanflex%20Tinned%20Copper%203%20Core%20Cable%20(2026%20Update)%20V.3.pdf>
- **[C2] AMC current datasheet directory:** <https://www.amc-tcg.com/downloads/data-sheets>
- **[C3] AMC matching V.3 page image, visually reviewed:** <https://cdn.prod.website-files.com/62deaee72baf3ef3b83165ff/69fc985a3e4f790bf60230bc_14%20-%20AMC%20Datasheet%20%20-%20Oceanflex%20Tinned%20Copper%203%20Core%20Cable%20(2026%20Update)%20V.3.jpg>
- **[C4] AMC marine-range application statements:** <https://www.amc-tcg.com/cable-range/marine-cables>
- **[G1] WISKA ONEGEL, 10108963:** <https://www.wiska.co.uk/en/30/pde/10108963/onegel.html>
- **[G2] WISKA ONEGEL family temperature/time table:** <https://www.wiska.co.uk/en/30/pov/1268/onegel.html>
- **[G3] WISKA's own OneGel webshop description:** <https://www.wiskaonline.co.uk/insulating-gel/tubes/onegel-onegel-w-300ml-wiska-branded-cartridge>
- **[G4] WISKA OneGel application image, visually reviewed:** <https://www.wiskaonline.co.uk/All_Media/Product_Media/ONEGEL.jpg>
- **[G5] Distinct MP One product family, not OneGel evidence:** <https://www.wiska.co.uk/en/30/pov/1504/mp-one---twist-and-go.html>
- **[M1] WISKA COMBI 308 LG, 10060400:** <https://www.wiska.co.uk/en/30/pde/10060400/combi-308-lg.html>
- **[M2] WISKA/WAGO Prom/222 leaflet; attached WAGO page Nov 2017, file timestamp 2021-03-12:** <https://www.wiska.co.uk/downloads/WISKA-WAGO--221-Series.pdf>
- **[M3] WAGO Gelbox chemistry/system scope and current 4/6 mm^2 families:** <https://www.wago.com/de/verbindungstechnik/installationsklemmen-entdecken/gelbox-von-wago>; English description: <https://www.wago.com/gb/products/electrical-interconnections/discover-installation-terminal-blocks-and-connectors/gelbox-from-wago>. The English page contains inconsistent size/series text; use the exact current connector/box allocation, not a general 221-family claim.
- **[S1] K&N Switch Wiring Diagrams Pocketbook, pp. 5/57; edition on p. 92 (10/2025):** <https://flippingbook.krausnaimer.com/Switch_wiring_diagrams_pocketbook/5/>, <https://flippingbook.krausnaimer.com/Switch_wiring_diagrams_pocketbook/57/>, <https://flippingbook.krausnaimer.com/Switch_wiring_diagrams_pocketbook/92/>
- **[S2] K&N UK Control & Load Switch Catalogue 2025, pp. 2/13/23:** <https://flippingbook.krausnaimer.com/Control_Load_Switch_Catalogue/2/>, <https://flippingbook.krausnaimer.com/Control_Load_Switch_Catalogue/13/>, <https://flippingbook.krausnaimer.com/Control_Load_Switch_Catalogue/23/>. Edition identified by manufacturer's catalogue directory: <https://www.krausnaimer.com/gb_en/catalogues>.
- **[S2a] Original manufacturer-hosted page 23 graphic, visually reviewed; full WAA364 programme in the top-middle panel:** <https://flippingbook.krausnaimer.com/Control_Load_Switch_Catalogue/Publication/assets/common/page-html5-substrates/page0023_4.jpg>. This resolves the contact/link transcription above, not an order-specific drawing or approval.
- **[S3] K&N CA10 dynamic datasheet v4.2, 2026-08-15:** <https://www.krausnaimer.com/fileadmin/user_upload/Kraus_u_Naimer/PDFs/ElecData/Switches/Dynamic/english/CA10_EN.pdf>
- **[S4] K&N Catalogue 100, p. 46, DC categories/contact-series conditions:** <https://flippingbook.krausnaimer.com/KN100GB/46/>; corroborating 2025 UK table on p. 11: <https://flippingbook.krausnaimer.com/Control_Load_Switch_Catalogue/11/>.
- **[S5] K&N custom-switch/DC-on-request service:** <https://www.krausnaimer.com/gb_en/products/customized-switches>
- **[S6] K&N custom switching-function form, one page, no printed revision identified:** <https://www.krausnaimer.com/fileadmin/user_upload/Kraus_u_Naimer/PDFs/Order_template/Form_for_customized_switch.pdf>. Retrieved 2026-09-07; the extractor's 2020-04-23 server timestamp is not a drawing revision or application approval.

The native reader returned [C1] as raw PDF data. As already documented in
ASSEMBLY.md, public PDF text extraction through `https://r.jina.ai/` prefixed
to the exact manufacturer URL was used for [C1], [S3], [S6] and [M2]. [C3]
additionally allowed visual checking of the cable table and pictograms. The
switch continuation uses the directly viewed [S2a] graphic, not flattened PDF
text, for contact pairs and links. No unreadable drawing details or quantitative
all-pole transfer tolerances are claimed as verified.

The generated OneGel PDF at
<https://www.wiska.co.uk/en/pdf/10108963/ONEGEL.pdf> was reachable as raw PDF,
but text extraction failed (HTTP 422). WISKA's linked gel brochure
<https://www.wiska.co.uk/downloads/Prom_220_Saved_by_the_Gel.pdf> exceeded the
native 5 MB limit; extraction was empty or HTTP 422. The linked 2026/27
catalogue <https://www.wiska.com/downloads/Product-Catalogue-2026-LR.pdf> also
failed text extraction (HTTP 422). No additional OneGel values are inferred
from those inaccessible contents; "not found" above is bounded to the
readable sources, not a claim that the manufacturer has no further evidence.

Historical research validation:
`git diff --no-index --check /dev/null pcb/ENVIRONMENT_EVIDENCE.md` passed.
No KiCad, manufacturing, electrical-model or physical test was part of that
research. The post-ad282e3 documentation update edits only README, INSTALL,
RISKS, ACCEPTANCE, MATERIALS, ORDERING, LED, REVIEW and this file; parent owns
AGENTS, REMEDIATION, ASSEMBLY, ELECTRICAL, the other research records and
integrated native checks. No hold is closed or approval hash refreshed here.
