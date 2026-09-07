# Controlled Assembly Notes

Document: DF-ASM-1.2.0-dev. Prepared 2026-09-06 for hardware **1.2.0-dev**.

**DEVELOPMENT / MANUFACTURING HOLD.** These instructions control the present
14-part baseline, not a released protection design. There are two top-side SMT
parts and twelve top-side THT parts, plus four unpopulated mechanical holes.
No additional LED protection or powered-GDT shutdown circuit is approved or
implemented. See [REMEDIATION.md](../REMEDIATION.md), [ELECTRICAL.md](ELECTRICAL.md)
and the controlled `verification.json` for release decisions. A DRC or
geometry-check pass does not establish insertion fit, solderability, enclosure
fit, continuous thermal safety, or surge performance.

## Drawing Conventions

- Dimensions are millimetres unless stated otherwise. Coordinates below are
  **top-view KiCad board coordinates**, X increasing east/right and Y increasing
  south/down. North is the edge at Y=94.50. Do not mirror these identification
  coordinates when identifying vias to CAM.
- Board outline: (97.00, 94.50) to (160.00, 150.50), 63.00 x 56.00. Mounting
  holes H1-H4 are 3.20 NPTH at (101.50, 99.00), (155.50, 99.00),
  (101.50, 146.00), (155.50, 146.00). Preserve their 3.45-radius front/back
  mechanical courtyards; supports must not contact functional copper.
- `F.Fab` is an assembly aid. Diode, resistor and Bencent outlines use the
  supported maximum body dimensions listed below. The SMT outline bounds the
  published A/B dimensions. KF128 and earth-GDT outlines are explicitly
  **nominal/provisional**, not maximum-body acceptance. LED connector arrows
  indicate the required wire-opening direction; their body maxima are still
  held. A line's drawing stroke is not an extra body tolerance.
- Local footprint origins are preserved except for the documented SMT/overpass
  relocation below. Use the native generated CPL, not a hand-maintained positive
  screen-Y table: native placement Y is negative for these positive board Y
  coordinates. Rotations -90 and 270 degrees are equivalent. The assembler must
  approve its actual model origin, orientation and any centroid correction.

## Placement And Polarity

| References | Origin / rotation | Required placement and inspection |
| :--- | :--- | :--- |
| J_IN | (106.00, 122.50), 0 deg | Wire openings west. Pin 1 A at (106.00, 114.88), pin 2 B at (106.00, 122.50), pin 3 C at (106.00, 130.12). |
| J_EARTH | (155.00, 122.50), 180 deg | Wire openings east. Pin 1 at Y=130.12, pin 2 at Y=122.50, pin 3 at Y=114.88; all X=155.00 and all on EARTH. This does not establish a 72 A assembled rating or equal impulse sharing. |
| J_LED_A | (145.50, 103.00), 90 deg | Openings north. Pin 1 positive at (142.96, 103.00); pin 2 WIRE_B return at (148.04, 103.00). |
| J_LED_C | (145.50, 142.00), 270 deg | Openings south. Pin 1 positive at (142.96, 142.00); pin 2 WIRE_B return at (148.04, 142.00). |
| D1, D2 | (132.50, 104.50) / (132.50, 140.50), 0 deg | **Cathode band east/right**, pin 1 at X=137.58. Anode pin 2 west/left at X=127.42. Formed pitch 10.16. Inspect actual band, pin mapping and nets, not a stock-footprint orientation convention. |
| R1, R2 | (116.00, 104.50) / (116.00, 140.50), 0 deg | Vishay MBE04140C2201FC100, 2.2 kohm, 1%. Formed pitch 15.24; pads X=108.38 and 123.62. Nonpolar. Do not substitute a higher-wattage part without new fit/thermal review. |
| GDT_AB, GDT_BC | (119.50, 118.69) / (119.50, 126.31), 0 deg | Ruilon SMD5050-470NA. Pad 1 north, pad 2 south. AB connects A/B; BC connects B/C. Nonpolar tube, but preserve the specified footprint/net mapping. |
| GDT_AC | (125.80, 122.50), 0 deg | Bencent B5G470L, internally north-south geometry despite 0-degree footprint rotation. Pad 1 A at (125.80, 114.88); pad 2 C at (125.80, 130.12). Apply the overpass drawing below. |
| GDT_A_E, GDT_B_E, GDT_C_E | (138.62, 113.50), (138.62, 122.50), (138.62, 131.50), 0 deg | Ruilon 2R470TD-8, horizontal formed pitch 15.24. Pin 1 west at X=131.00 on A/B/C respectively; pin 2 east at X=146.24 on EARTH. Preserve 9.00 body-centre pitch; do not bend bodies together to ease insertion. |

J_LED_A and J_LED_C intentionally have **different local pad-number mappings**.
Their 180-degree outward flip still leaves positive on the left in the top view.
Use `DogFence:KF129_5.08_2P_LED_A` and `DogFence:KF129_5.08_2P_LED_C` respectively;
never replace both with the same stock-library footprint. The local diode symbol
also explicitly names its anode-left/cathode-right mapping. Underside reference
text is mirrored for reading from below; it does not change electrical polarity.

## GDT_AC Forming Drawing

Side view looking along X, through X=125.80; **not to scale**. Z=0 is the highest
finished top PCB surface under the crossing, including its mask. The minimum is
not measured from the bottom of the board or from the component centreline.

```text
                         B5G470L, axis north-south
                         body length <=6.20
                         diameter <=5.70
                  +---------------------------+
       formed lead|        ceramic body       |formed lead
       +----------+---------------------------+----------+
       |          ^                           ^          |
       |          | g >=2.00 throughout the  |          |
       |          | raised body/lead overpass|          |
 Z=0 ==|==========v===========================v==========|== PCB top
       |                    WIRE_B                       |
       |              Y=120.90 to 124.10                 |
       |                                                 |
     A PTH                                             C PTH
   Y=114.88                                          Y=130.12
       |<--------------- pitch 15.24 ------------------->|

                    board centre Y=122.50
             X of both insertion legs =125.80
```

1. Use a supported lead-forming fixture before insertion. Support the lead
   between each bend and the body; do not transmit bending, twisting, or pulling
   force into the ceramic-to-metal seal. Do not bend against the PCB or re-form
   a soldered tube. Reject cracked, dropped, loose or otherwise damaged parts.
2. Form the vertical insertion legs to the 15.24 board pitch. The final forming
   drawing must specify approved bend radius, distance from the seal, pitch and
   height tolerances, springback, lead protrusion, and the process needed to
   hold them. **Those manufacturer/assembler approvals remain open.** Do not
   infer permissible bends from the 62 +/-2 unformed overall length.
3. Fixture the raised span with positive height margin above the 2.00 minimum.
   After soldering, every portion of the raised body, electrodes and lead span
   must maintain that minimum above the PCB. Only the intentional insertion
   legs descend to the A/C pads, outside the B-crossing corridor. No unsupported
   sag, solder bead or loose clipping may reduce the crossing clearance.
4. Inspect on every assembled board, unpowered and before encapsulation. Use a
   calibrated optical height measurement or non-damaging go/no-go gauge, from
   both sides and across the whole raised span, including its lowest point.
   Record the minimum and measurement uncertainty; accept only when the lower
   bound is at least 2.00. A gauge at the centre alone is insufficient.
5. Establish the maximum assembled height with the actual formed part and fit
   fixture. A 2.00 gap plus the 5.70 maximum body diameter alone uses 7.70 of
   headroom above the board; forming margin increases the requirement. This is
   not a maximum-height specification or proof that the COMBI lid will clear it.
6. This is a pre-encapsulation clearance check. Filling the space with gel does
   not preserve an air gap or prove equivalent impulse insulation. Any gel in
   this region requires the approved insulation/material process and relevant
   electrical qualification; do not count gel as an accepted substitute.

## Hole Fit Evidence

Use the selected part's **maximum finished** pin envelope, including plating and
any forming distortion. With the ordinary JLCPCB component-PTH tolerance:

```text
minimum finished hole = nominal finished hole - 0.08
round pin envelope    = maximum finished pin diameter
rectangular envelope  = sqrt(maximum width^2 + maximum thickness^2)
require: minimum finished hole >= maximum envelope + 0.10
```

The 0.10 is a minimum **diametral** project assembly allowance after the negative
hole tolerance, not an allocation that can also be spent on arbitrary pitch or
forming error. Resolve connector pin pitch, drill position and forming
tolerances separately. An unknown maximum is not a passing calculation.

| THT references / exact BOM identity | Nominal hole / pad | Minimum hole | Supported maximum pin envelope / calculation | Status |
| :--- | :--- | :--- | :--- | :--- |
| D1, D2: onsemi 1N4007G, C232439 | 1.10 / 2.20 | 1.02 | D max 0.86: `1.02 - 0.86 = 0.16 >= 0.10`. Nominal ring 0.55. | Diameter correction supported. Exact forming and assembled insertion still require acceptance. |
| R1, R2: Vishay MBE04140C2201FC100, C1368610 | 1.00 / 2.40 | 0.92 | Drawing gives **d nominal 0.80**, not maximum. Current hole requires max envelope <=0.82. | HOLD: maximum finished wire diameter and formed-pitch tolerance. |
| GDT_AC: Bencent B5G470L, C5337217 | 1.20 / 2.80 | 1.12 | Retrieved A2 table gives body/overall lengths, not a maximum lead diameter. Current hole requires max envelope <=1.02. | HOLD: maximum finished lead diameter and approved overpass forming. |
| GDT_A_E, GDT_B_E, GDT_C_E: Ruilon 2R470TD-8, C2836978 | 1.20 / 3.00 | 1.12 | Maximum lead dimensions were not recoverable from the retrieved drawing image. Current hole requires max envelope <=1.02. | HOLD: exact delivered drawing/revision and lead/forming tolerances. |
| J_IN, J_EARTH: Cixi Kefa Elec KF128-7.62-3P, C474957 | 1.40 / 3.20 | 1.32 | Current hole requires rectangular/round max envelope <=1.22. The supplementary family drawing's nominal 0.90 x 0.80 would give 1.2042, leaving only 0.1158 before pin tolerances; it is not maximum-pin evidence for this supplied part. | HOLD: exact finished pin dimensions, tolerances and pitch. Do not assume fit. |
| J_LED_A, J_LED_C: Cixi Kefa Elec KF129-5.08-2P, C475092 | 1.30 / 2.80 | 1.22 | Current hole requires max envelope <=1.12. Exact maximum rectangular pin width/thickness not established. | HOLD: exact finished pin dimensions, tolerances and pitch. |

- The former 0.90 diode hole could finish at 0.82, smaller than the 0.86 maximum
  lead. It is now 1.10, not a proposal awaiting a source change.
- The onsemi case drawing makes inches controlling. Its 0.034-inch lead limit
  is 0.8636 mm before the rounded metric presentation; the stricter calculation
  is `1.02 - 0.8636 = 0.1564 >= 0.10`, still passing. Its 0.205-inch body length
  is 5.207 mm; the fabrication outline rounds outward to 5.21 x 2.70.
- A supplier CAD hole of 1.60 is not a pin drawing. Even 1.60 permits only a
  maximum envelope of 1.42 under this rule; it is not an automatically qualified
  connector-hole replacement. Connector holes have **not** been resized.
- Remaining nominal component rings are 0.70 for resistors, 0.80 for GDT_AC,
  0.90 for earth GDTs/KF128, and 0.75 for KF129. These exceed the 0.254 nominal
  two-layer/2 oz component-PTH design requirement; finished ring and barrel
  plating still depend on fabrication/registration tolerances and the quote.
- onsemi case 59-10 does not control lead diameter within dimension F, up to
  1.27 from the case. Keep that region out of the insertion hole. The 10.16 pitch
  and 5.207 maximum body length leave about 2.4765 per side before allowing for
  the bend geometry. Obtain a forming instruction that respects the case/seal.
- Vishay specifies minimum mounting dimension M=15.0; the 15.24 nominal pitch
  is only 0.24 above it. Include hole-position and forming tolerances rather
  than assuming that the nominal pitch proves compliance.
- Do not force insertion, clip rectangular pins to make them fit, or ream
  plated finished boards. Resolve the approved part/hole/process in the source,
  then regenerate and inspect production data.

## Body And Courtyard Evidence

| Item | Drawing evidence used | Source representation / remaining hold |
| :--- | :--- | :--- |
| onsemi 1N4007G | 1N4001/D Rev.18, June 2024; case 59-10 issue U, 15-Feb-2005, document 98ASB42045B. Rounded metric body max 5.20 x 2.70, lead max 0.86; controlling-inch conversion accounted for above. | `F.Fab` bounds 5.21 x 2.70; existing courtyard +/-6.45 x +/-1.60 includes maximum body and 2.20 pads with at least 0.25 nominal margin. |
| Vishay MBE0414 | Document 28766 Rev.11-Jul-2018 p13. L max 11.9, D max 4.2; d nominal 0.8, M min 15.0. | `F.Fab` 11.90 x 4.20; existing 18.20 x 5.00 courtyard retained. Lead maximum remains open. |
| Bencent B5G470L | A2, 2018-01-03 p2. Body B=6 +/-0.2, C=5.5 +/-0.2; overall A=62 +/-2. | `F.Fab` 5.70 east-west x 6.20 north-south. Courtyard widened from +/-3.05 to +/-3.10 in X, retaining +/-9.30 in Y; maximum body plus 0.25 lateral margin. |
| Ruilon SMD5050-470NA | SP-GDT-006 A3, 2024-08-19 p3: A/B=5.0 +/-0.2, C=4.2 +/-0.3, D=0.5 +/-0.1. | `F.Fab` 5.20 x 5.20 envelope. Existing 5.70 x 7.50 courtyard retained around existing pads. Exact recommended land-pattern interpretation/acceptance is still held below. |
| Ruilon 2R470TD-8 | LCSC-distributed SP-GDT-017 A3, 2023-11-02; manufacturer site now offers A6, 2025-10-16. Text gives nominal diameter 8 x length 6; dimension figure was not decoded. | `F.Fab` 6 x 8 and courtyard 18.80 x 8.50 are nominal/provisional. Retain 9.00 pitch, but obtain maximum body dimensions. Do not claim a guaranteed 1.00 physical air gap from nominal diameter alone. |
| KF128-7.62-3P | Manufacturer-linked drawing title `45-2-KF128-7.62 Model (1)` is image/vector-only in the available text reader. A supplementary KF128 family drawing shows nominal depth 10.50, pin row 5.20 from rear, height 14.10, and length P x pitch, but no maximum tolerances or exact order identification. | Nominal `F.Fab`: X=-5.30..5.20, Y=-11.43..11.43. Both courtyards bound X=-5.55..5.45, Y=-11.68..11.68. J_IN's former east boundary +5.10 incorrectly cut through its own +5.20 body outline; it is corrected to +5.45, not shrunk. Maximum-body/order confirmation remains held. |
| KF129-5.08-2P | Exact manufacturer-linked and LCSC drawings located, but dimension figures not decoded. | No new maximum-body box asserted. Existing nominal/legacy silk and courtyard preserved, with `F.Fab` references, pad-1 markers and outward arrows only. Require actual maximum envelope and access review. |

At J_EARTH the same provisional KF128 body reaches X=160.30, 0.30 beyond the
board edge; its courtyard reaches 160.55. The shorter existing silk is not a
smaller physical component. Approve actual body overhang, panel clearance and
COMBI/wire access with the exact part, or obtain a guardrail-compliant redesign.
Do not trim the body/courtyard or move the protected earth copper to hide this.

## SMT Via Relocation

The present source solution is **relocation, not speculative mask editing**:

- GDT_AB and GDT_BC moved from X=114.00 to **119.50**, retaining Y=118.69 and
  126.31, zero rotation, all nets, and the original four **5.20 x 2.00** copper,
  mask and paste pads at local Y=+/-2.50. There are no added negative mask/paste
  margins or unapproved apertures over via holes.
- The four SMT connection stubs moved to X=119.50 and retain their **3.20 width**.
  The full 3.20 A/B/C rails on both layers, their nine 1.00/1.80 vias, all earth
  copper/vias, and the protected B-return routing are unchanged.
- GDT_AC moved from X=124.00 to **125.80**, with its two pads still on the A/C
  rails at Y=114.88/130.12 and with unchanged nets and 15.24 pitch. This makes
  physical room for the relocated SMT footprints without shrinking courtyards;
  the north-south overpass and minimum height control remain mandatory.
- Corrected J_IN courtyard ends at global X=111.45; the relocated SMT courtyard
  starts at X=116.65, a **5.20** nominal gap. SMT courtyard ends at X=122.35;
  the widened GDT_AC courtyard starts at X=122.70, a **0.35** gap. GDT_AC ends
  at X=128.90; earth-GDT courtyards start at X=129.22, a **0.32** gap. These are
  courtyard-boundary distances, not measured physical or rework clearances.

Historical overlap at A: the via at Y=114.88 with radius 0.50 reached 115.38;
the original SMT aperture started at Y=115.19, overlapping the hole by **0.19**.
The three X positions on each rail lay inside the old aperture's X extent.
All nine rail holes were affected; the three B-rail holes faced both SMT parts.

Now each aperture starts at X=116.90. For the nearest protected via at
X=115.50, the nearest aperture corner is offset by dx=1.40 and dy=0.31:

```text
corner distance                   = sqrt(1.40^2 + 0.31^2) = 1.433911
nominal drill-circle to aperture  = 1.433911 - 0.50       = 0.933911
nominal full annulus to aperture  = 1.433911 - 0.90       = 0.533911
```

The same minimum applies to all four SMT pads for `F.Mask` and `F.Paste` in the
saved zero-margin source. None of these apertures exposes a protected via
annulus. The 0.533911 figure is a conservative geometric mask-barrier budget
even if the full annulus were wettable; it is **not** a supplier registration or
solder-process guarantee. Recheck actual processed mask/stencil apertures,
drill sizes, registration allowances and solder spread, not just pad centres.

**Remaining land-pattern/process hold:** SP-GDT-006 A3 p3 lists recommended
land dimensions X=1.2, X1=4.0, Y=5.5. Those are not the existing 5.2 x 2 pads;
the X1 inch entry (0.165) also needs reconciliation with its 4.0 mm entry.
The text extraction did not establish every dimension's figure association.
Do not claim this retained pattern is the manufacturer's recommended pattern.
Obtain the exact applicable drawing and either implement its verified land
pattern with renewed checks or receive written manufacturer/assembler approval
for this alternative and its solder volume. Relocation removes the demonstrated
via-aperture collision; it does not close the full W1 manufacturing hold.

## Stitching Via Identification

Every listed location is a **via**, with 1.00 drill / 1.80 copper diameter through
F.Cu and B.Cu. IDs below are drawing identifiers, not extra electrical parts.
Compare this table with processed CAM by coordinates; do not select by drill
diameter alone.

| ID | Net | X | Y |
| :--- | :--- | ---: | ---: |
| VA1 | WIRE_A | 112.50 | 114.88 |
| VA2 | WIRE_A | 114.00 | 114.88 |
| VA3 | WIRE_A | 115.50 | 114.88 |
| VB1 | WIRE_B | 112.50 | 122.50 |
| VB2 | WIRE_B | 114.00 | 122.50 |
| VB3 | WIRE_B | 115.50 | 122.50 |
| VC1 | WIRE_C | 112.50 | 130.12 |
| VC2 | WIRE_C | 114.00 | 130.12 |
| VC3 | WIRE_C | 115.50 | 130.12 |
| VE1 | EARTH | 150.00 | 114.88 |
| VE2 | EARTH | 150.00 | 118.69 |
| VE3 | EARTH | 150.00 | 122.50 |
| VE4 | EARTH | 150.00 | 126.31 |
| VE5 | EARTH | 150.00 | 130.12 |

```text
TOP VIEW, X east ->          112.50  114.00  115.50           150.00
Y south
 114.88  WIRE_A                VA1     VA2     VA3               VE1
 118.69                                                        VE2
 122.50  WIRE_B                VB1     VB2     VB3               VE3
 126.31                                                        VE4
 130.12  WIRE_C                VC1     VC2     VC3               VE5
                                                               EARTH
```

- No filling by size: R1/R2 insertion pads also have 1.00 holes. All component
  PTH holes must remain open for insertion; no ordinary via is an insertion pad.
- Preserve all fourteen via locations, hole diameters and copper diameters.
  Obtain written CAM agreement not to reduce the protected via drills under
  ordinary via-hole adjustment practices.
- Source tenting flags remain a mask request only. Normal reliable tenting/ink
  plugging guidance is around <=0.5 holes; published filled-and-capped upper
  limits of 0.5/0.55 also do not establish support for these 1.00 holes. No fill,
  plugging, capping, sealing or exception approval is assumed. Agree the actual
  treatment by these coordinates and inspect the returned CAM data.
- If vias remain open or incompletely tented, qualify the soldering process
  against solder ingress, drain-through, beads and subsequent environmental
  exposure. Gel, an opaque tent, or a filled-order checkbox proves no seal.
- 70 micrometre surface copper is **not** 70 micrometre barrel copper. Agree and
  record any required minimum finished barrel copper separately from exterior
  copper weight and the fabricator's published average plating value.

## Thickness And Process

The source stackup is reconciled arithmetically to nominal **1.60**:

| Layer | Model thickness |
| :--- | ---: |
| F.Mask | 0.010 |
| F.Cu | 0.070 |
| FR-4 core | 1.440 |
| B.Cu | 0.070 |
| B.Mask | 0.010 |
| Total | 1.600 |

The former 1.510 core made the listed total 1.670. Copper remains 70 micrometres
on each side. The core value is a reconciled design model, not evidence of a
supplier's exact stock laminate. Confirm the finished-thickness measurement
convention, over-mask thickness, tolerance and ENIG process in the quote.
Essentra LCBSBM-6-01A-RT listings give nominal 3.18 support hole, 1.57 panel and
9.53 spacing; they do not prove that the full finished-board tolerance fits.
Obtain the exact support drawing and approve latch engagement on actual boards
without changing the protected 3.20 mounting holes.

1. Confirm the exact order/lots, drawings, BOM identities, pin fit and forming
   approval before assembly. Do not substitute optional parts by pitch or a
   standard-looking footprint name. Approve five individual assembled boards,
   not five multi-up panels; allocate any process samples/attrition explicitly.
2. Obtain order-specific acceptance for 2 oz both sides, ENIG, mixed SMT/THT,
   nickel/tin lead finishes, heavy solid-copper thermal load and any selective
   solder tooling. SMT reflow followed by controlled THT soldering is a candidate
   sequence, not an approved universal profile.
3. Establish a compatible profile for **all** installed parts. onsemi permits
   260 degrees C maximum for 10 seconds at 1/16 inch from the case; the retrieved
   Ruilon/Bencent wave tables use up to 280 degrees C and 2-5 seconds. Different
   measurement locations and heat-test limits are not permission to expose
   every part to the most permissive number. Record actual joint/body
   temperatures, time, preheat and the approved alloy/flux/cleaning process.
4. Do not narrow the 3.20 rails, delete vias, add restrictive thermal spokes,
   slit the earth bus or reduce isolation to ease soldering. Inspect wetting,
   hole fill, cold joints, solder volume and damage using accepted workmanship
   criteria for the agreed process. Escalate an incompatible process to design
   review instead of altering surge geometry in CAM.
5. Approve manufacturer-added panel rails, fiducials, tooling and depanelization
   clearance, including J_EARTH overhang. No cuts/holes are permitted in protected
   copper or mounting keepouts. Check the actual processed top paste and mask,
   separate PTH/NPTH drills and placement model; raw exports alone are not CAM
   acceptance. Retain the agreed coordinate transform and sign convention.

## COMBI Dry-Fit Hold

Use an actual WISKA COMBI 308, actual Essentra supports and fully formed/soldered
board before potting. Its published **85 x 85 x 51 external** dimensions are not
usable internal space. Assembly height, tolerances and tool access are not
simulated by DRC.

1. Dry-fit the board/supports, three WAGO 221-613 through-splices, incoming and
   outgoing cable, actual glands, taps, earth wiring and lid-mounted indicators.
   Include cable bend radii, conductor stripping/ferrules if approved, wire
   opening directions, screwdriver reach, lid travel and service slack.
2. Measure minimum lid-to-component/lead clearance, GDT_AC height, connector
   overhang and support engagement. Nothing may press on the raised arrester,
   seals, solder joints or PCB. Record photographs and toleranced measurements;
   do not infer fit from a 63 x 56 bare-board rectangle.
3. Keep each A/B/C through-splice intact and connect the PCB as a tap, not a
   serial perimeter-current link. Keep EARTH separate from fence conductors and
   connect it only under the approved site bonding design. Do not directly bond
   a fence core or assume that TEST negative is protective earth.
4. Verify actual APEM Q10F5SXXSG02E polarity and mounting requirements. Family
   guidance is 0.20-0.25 Nm, not the legacy 1.5-2.0 Nm; use the exact supplied
   model instructions. Do not perform powered reversal tests until the
   protection design and controlled test method are approved.
5. Clean, dry and inspect before any WISKA MP0100 encapsulation. Approve the
   actual formulation, mixing/cure method, materials, cleanliness, thermal
   behavior and effect on the overpass insulation. Retain **one unpotted
   reference prototype**. Potting and the enclosure's unmodified IP rating do
   not qualify the completed coastal installation.

## Acceptance Record

Before release, retain board serial/revision, BOM/lot and drawing revisions,
approved pin-fit calculations, measured forming/pitch/height, solder profile,
via-coordinate CAM acceptance, processed mask/stencil/drill review, assembler
rotation approval, support/enclosure dry-fit and measured thermal/electrical
results. Basic workmanship on five boards is not field or surge qualification.

Open approvals in this bounded P3 state: exact connector/other THT maximum pins;
connector and earth-GDT maximum bodies; KF128 overhang and COMBI access; SMT
recommended pattern or approved alternative/solder volume; via treatment and
barrel requirements; forming/soldering/gel compatibility; and the unresolved
P2 protection and continuous-duty design. Keep manufacturing on hold until the
engineering release process accepts the applicable evidence.

## Evidence Links

Retrieved/reviewed 2026-09-06. Primary PDFs that the native web reader returned
as binary were also queried through public `r.jina.ai/https://...` text
extraction. Image-only dimensions and conflicting revisions remain open; this
is not a claim to have visually verified inaccessible drawing details.

- [onsemi 1N4001/D family/case drawing](https://www.onsemi.com/pdf/datasheet/1n4001-d.pdf), [C232439 onsemi identity](https://www.lcsc.com/product-detail/C232439.html).
- [Vishay document 28766](https://www.vishay.com/docs/28766/mbxsma.pdf).
- [Bencent B5G470L A2 via LCSC](https://datasheet.lcsc.com/datasheet/pdf/6471acbc3d87a8a4a9e5f7b8a245655d.pdf?productCode=C5337217).
- [Ruilon SMD5050 SP-GDT-006 A3 via LCSC](https://datasheet.lcsc.com/datasheet/pdf/ce8e2bf652ab9d180a3e88b2584bb613.pdf?productCode=C39692533).
- [Ruilon 2RD-8 SP-GDT-017 A3 via LCSC](https://datasheet.lcsc.com/datasheet/pdf/d0869b141c45d22998b36dee1e5e4d4c.pdf?productCode=C2836978), [manufacturer A6](https://www.ruilon.com.cn/Uploads/pdf/017-2rd-8%20series_a6.pdf). Confirm the revision applying to the allocated parts; do not merge differing temperature/other claims without approval.
- [Kefa KF128 manufacturer product/drawing links](https://www.kefaelectronic.com/KF128-7-5-7-62-PCB-Terminal-Block-pd45490974.html), [manufacturer KF128-7.62 drawing](https://jirorwxhqiillo5p.ldycdn.com/KF128-7.62-aidqiBpqKirRliSqmrqirloj.pdf), [exact C474957 distributed drawing](https://datasheet.lcsc.com/datasheet/pdf/2bd9ccda2e0f72df8237e78ea70a6d85.pdf?productCode=C474957).
- [Kefa KF129 manufacturer product/drawing links](https://www.kefaelectronic.com/KF129-5-0-5-08-PCB-Terminal-Block-pd47789974.html), [manufacturer KF129-5.08 drawing](https://irrorwxhqiillo5p.ldycdn.com/KF129-5.08-aidqiBpqKirRljSjorlrqlri.pdf), [exact C475092 distributed drawing](https://datasheet.lcsc.com/datasheet/pdf/99269cbb2dd06cf5383cf1cad04f20f7.pdf?productCode=C475092).
- [Supplementary KF128 family drawing image](https://www.alldatasheet.com/htmldatasheet2/1253243/ETC1/KF128/109/1/KF128.png), viewed at full resolution. This secondary, insufficiently identified nominal drawing does not replace the exact Kefa maximum/tolerance drawing. Manufacturer product-page and distributor ratings also differ; obtain exact supplied-part ratings rather than selecting the largest claim.
- [JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [component-hole tolerance](https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes), [via covering](https://jlcpcb.com/help/article/pcb-via-covering).
- [WISKA COMBI 308 LG](https://www.wiska.co.uk/en/30/pde/10060400/combi-308-lg.html), [Essentra support listing](https://www.digikey.com/en/products/detail/essentra-components/LCBSBM-6-01A-RT/392198), [APEM indicator](https://www.apem.com/led-indicators/professional-grade-panel-mount-led-indicators/q10/q10f5sxxsg02e).
