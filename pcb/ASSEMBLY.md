# Controlled Assembly Notes

Document: DF-ASM-1.2.0-dev. Updated 2026-09-07 for hardware **1.2.0-dev**.

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
- `F.Fab` is an assembly aid. Diode, resistor and GDT boxes bound the published
  body dimensions, rounding the larger metric/inch limits outward. Kefa boxes
  are **controlled procurement envelopes**, not newly invented manufacturer
  guarantees. Inspect actual parts against them. Courtyards include the stated
  pose and assembly allowances; a drawing stroke is not extra body tolerance.
  LED arrows indicate the required wire-opening direction.
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
                          diameter <=5.72
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
   The development forming target is body underside **2.50 +/-0.25**, with
   **8.50 maximum complete assembled height** above the top PCB surface. These
   are drawing/inspection limits, not a claim of an accepted forming process.
   After soldering, every portion of the raised body, electrodes and lead span
   must maintain that minimum above the PCB. Only the intentional insertion
   legs descend to the A/C pads, outside the B-crossing corridor. No unsupported
   sag, solder bead or loose clipping may reduce the crossing clearance.
4. Inspect on every assembled board, unpowered and before encapsulation. Use a
   calibrated optical height measurement or non-damaging go/no-go gauge, from
   both sides and across the whole raised span, including its lowest point.
   Record the minimum and measurement uncertainty; accept only when the lower
   bound is at least 2.00. A gauge at the centre alone is insufficient.
5. Check the complete 8.50 height envelope, including lead bows and solder,
   with the actual formed part/fixture. The target's 2.75 upper underside plus
   5.72 body uses 8.47 of headroom. The body calculation alone does not bound
   a bowed lead or prove the COMBI lid clears the complete assembly.
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

The 0.10 is a minimum **diametral** assembly allowance after negative hole
tolerance, not a budget for arbitrary pitch/forming error. The design below
now also allocates `2 * (sqrt(2)*0.05 + 0.05) = 0.241421` diametrally for
independent hole-position and part-pattern errors. This uses the ordinary
JLCPCB +/-0.05 hole-position limit conservatively on each axis, plus a required
**0.050 radial per-pin part-pattern envelope after common rigid alignment**.
Inspect lean/non-collinearity through the full insertion length. This is a
procurement/formed-part acceptance requirement, not a manufacturer promise.

Original figures and tolerance associations have now been visually read in
[DFM_EVIDENCE.md](DFM_EVIDENCE.md). Where a finished-pin maximum is absent, the
following **E limits** are deliberately conservative incoming-part limits.
They make the file design explicit without pretending the allocated lot was
measured. Accept only `measured maximum + uncertainty <= limit`, on every
allocated controlled-envelope part for the five prototypes, including attrition.
No qualified yield or assembler acceptance of these limits is yet recorded.

| THT references / exact BOM identity | Nominal hole / pad | Minimum hole | Supported maximum pin envelope / calculation | Status |
| :--- | :--- | :--- | :--- | :--- |
| D1, D2: onsemi 1N4007G, C232439 | 1.10 / 2.20 | 1.02 | D max 0.86: `1.02 - 0.86 = 0.16 >= 0.10`. Nominal ring 0.55. | Diameter correction supported. Exact forming and assembled insertion still require acceptance. |
| R1, R2: Vishay MBE04140C2201FC100, C1368610 | **1.40 / 2.40** | 1.32 | Published d_nom=0.80; adopt **E diameter <=0.90**, including tin/ovality/forming. `1.32 - 0.90 - 0.241421 = 0.178579 >=0.10`. | File envelope selected; actual E/pattern, solder-fill and forming acceptance HELD. |
| GDT_AC: Bencent B5G470L, C5337217 | **1.40 / 2.80** | 1.32 | Original A2 figure labels round 0.80 without tolerance; adopt **E diameter <=0.90**. Residual allowance **0.178579** after position budget. | File envelope selected; actual E/pattern and overpass forming acceptance HELD. |
| GDT_A_E, GDT_B_E, GDT_C_E: Ruilon 2R470TD-8, C2836978 | **1.50 / 3.00** | 1.42 | A3/A6 TD figures give **1.00 +/-0.05**, max **1.05**. `1.42 - 1.05 - 0.241421 = 0.128579 >=0.10`. | Known undersize corrected. Verify supplied revision, post-forming pin/pattern and nickel-lead process. |
| J_IN, J_EARTH: Cixi Kefa KF128-7.62-3P, C474957 | **2.00 / 3.20** | 1.92 | Nominal 0.90 x 0.80; **E <=1.10 x 1.00**, diagonal **1.486607**. Residual allowance **0.191972** after position budget. | File envelope selected; finished metal-pin/pattern/body lot acceptance HELD. |
| J_LED_A, J_LED_C: Cixi Kefa KF129-5.08-2P, C475092 | **2.00 / 2.80** | 1.92 | Same-revision drawings conflict, width 0.90/0.95 x thickness 0.80. **E <=1.15 x 1.00**, diagonal **1.523975**, covers both nominal variants. Residual allowance **0.154604**. | File envelope selected; actual variant and E/pattern/body lot acceptance HELD. |

- The former 0.90 diode hole could finish at 0.82, smaller than the 0.86 maximum
  lead. It is now 1.10, not a proposal awaiting a source change.
- The onsemi case drawing makes inches controlling. Its 0.034-inch lead limit
  is 0.8636 mm before the rounded metric presentation; the stricter calculation
  is `1.02 - 0.8636 = 0.1564 >= 0.10`, still passing. Its 0.205-inch body length
  is 5.207 mm; the fabrication outline rounds outward to 5.21 x 2.70.
- Kefa's printed small-dimension +/-0.20 general table cites a **plastics**
  tolerance standard. Applying that band to metal cross-sections defines E;
  it does not prove a finished metal-pin guarantee. Its recommended 1.40
  **+0.10/-0.00** PCB hole is also not JLCPCB's ordinary nominal 1.40 process.
  The chosen 2.00 holes trade extra solder volume/fixturing for explicit fit
  margin. Neither stock CAD nor enlargement establishes actual solder fill.
- Nominal component rings are **0.50 resistor, 0.70 GDT_AC, 0.75 earth GDT,
  0.60 KF128, 0.40 KF129**, and 0.55 diode. These exceed the 0.254 nominal
  two-layer/2 oz component-PTH design requirement; finished ring and barrel
  plating still depend on fabrication/registration tolerances and the quote.
- onsemi case 59-10 does not control lead diameter within dimension F, up to
  1.27 from the case. Keep that region out of the insertion hole. The 10.16 pitch
  and 5.207 maximum body length leave about 2.4765 per side before allowing for
  bends. **D1/D2 retain their reviewed diameter-only 1.10 holes**; the 0.241421
  fixed-pattern budget above is not claimed for them. Their separate process
  must form/align the flexible leads to the actual board hole pattern, without
  force at the seals, and inspect insertion. That forming approval stays open.
- Vishay specifies M>=15.0. The 0.050 radial part-pattern limit yields at least
  15.14 formed pitch before assembly; inspect M after seating too. Larger holes
  must not permit inward collapse below 15.0. Do not spend the same allowance
  twice or force a rigid connector to meet a nominal gauge.
- Do not force insertion, clip rectangular pins to make them fit, or ream
  plated finished boards. Resolve the approved part/hole/process in the source,
  then regenerate and inspect production data.

## Body And Courtyard Evidence

| Item | Drawing evidence used | Source representation / remaining hold |
| :--- | :--- | :--- |
| onsemi 1N4007G | 1N4001/D Rev.18, June 2024; case 59-10 issue U, 15-Feb-2005, document 98ASB42045B. Rounded metric body max 5.20 x 2.70, lead max 0.86; controlling-inch conversion accounted for above. | `F.Fab` bounds 5.21 x 2.70; courtyard **X=+/-6.45, Y=+/-1.70** contains the maximum body plus 0.10 pose and 0.25 assembly margin, and the 2.20 pads. |
| Vishay MBE0414 | Document 28766 Rev.11-Jul-2018 p13. L max 11.9, D max 4.2; d nominal 0.8, M min 15.0. | `F.Fab` 11.90 x 4.20; existing 18.20 x 5.00 courtyard retained. Lead maximum remains open. |
| Bencent B5G470L | A2, 2018-01-03 p2: length 6 +/-0.2, diameter 5.5 +/-0.2; overall 62 +/-2. | `F.Fab` **5.72 X x 6.20 Y**, rounding the larger inch diameter outward. Courtyard X=+/-3.25, Y=+/-9.30. |
| Ruilon SMD5050-470NA | SP-GDT-006 A3, 2024-08-19 p3: square **end face** A/B=5.0 +/-0.2; **axial** C=4.2 +/-0.3; electrode D=0.5 +/-0.1. | Corrected `F.Fab` **5.21 X x 4.50 Y**; courtyard X=+/-3.00, Y=+/-3.75. End-face height is not the 4.2 axial dimension. Metric lands selected below. |
| Ruilon 2R470TD-8 | SP-GDT-017 A3, 2023-11-02 p3 and A6, 2025-10-16 p5, visually read TD figures agree: diameter 8 +/-0.2, length 6 +/-0.3. | `F.Fab` **6.30 X x 8.21 Y**, outward inch rounding; courtyard X=+/-9.40, Y=+/-4.46. Retain 9.00 centre pitch. |
| KF128-7.62-3P | Manufacturer and C474957 drawings A / 21.03.13; actual depth/rear datum, general tolerance table and end key now read. | **E body box** X=-6.00..5.40, Y=+/-12.50; courtyard X=-6.35..5.75, Y=+/-12.85. E includes end keys and uncertain pin-to-end datum, with allocated pose margin. Body height bound 14.60 above seating plane. |
| KF129-5.08-2P | Manufacturer and C475092 drawings A / 21.03.13; pin-width conflict retained. Body depth/rear datum, height, end key and table now read. | **E body box** X=-5.10..6.40, Y=+/-6.10; courtyard X=-5.45..6.75, Y=+/-6.45, in each existing local frame. Body height bound 18.80. Both intentional pad mappings remain unchanged. |

Require actual projected bodies to stay within these boxes expanded by **0.10
per side**, including translation/tilt, not additional unbounded rotation.
Courtyards include this projection plus >=0.25 assembly margin. The silk is a
placement aid, not the maximum-body envelope. DFM_EVIDENCE contains the complete
tolerance stack and incoming inspection method.

J_EARTH uses a three-sided silk aid: its west/rear silk edge would cross the
intentional EARTH via mask openings, so that edge is omitted. The full F.Fab
and courtyard envelopes are retained; no physical clearance is concealed.

At J_EARTH the E body reaches **X=161.00**, 1.00 beyond the nominal east edge;
pose increases this to **161.10**. Allow **1.30 overhang** against a routed edge
as far inward as X=159.80. The courtyard reaches **161.35**. Approve panel,
depanelization, COMBI and wire/tool access for that envelope, not the former
nominal 0.30 figure. Do not trim the body/courtyard or move earth copper.

Earth-GDT maximum projected gap is bounded below by
`9.00 - 8.21 - 2*0.10 = 0.59`; courtyard gap is 0.08. This is a dimensional
acceptance condition, **not a 1.00 air gap or an impulse-insulation claim**.
LED courtyards stop at X=151.95, 0.10 before H2/H4's protected courtyard bounds.

## SMT Via Relocation

The source retains the prior relocation and now implements the visually
resolved **metric land recommendation**, without speculative mask reductions:

- GDT_AB and GDT_BC remain at **X=119.50**, Y=118.69/126.31, zero rotation and
  unchanged nets. Lands are now **5.50 X x 1.20 Y at local Y=+/-2.00** for
  copper, mask and paste, with zero additional margins. SP-GDT-006 A3 p3's
  X1 leader is centre spacing, not the inner gap. **Select its printed metric
  4.00 spacing explicitly**; the contradictory 0.165-inch entry is not a
  manufacturer-approved erratum. The decision and tolerance-overlap calculation
  are in DFM_EVIDENCE. Supplier confirmation/processed stencil remain open.
- The four SMT connection stubs moved to X=119.50 and retain their **3.20 width**.
  The full 3.20 A/B/C rails on both layers, their nine 1.00/1.80 vias, all earth
  copper/vias, and the protected B-return routing are unchanged.
- GDT_AC moved from X=124.00 to **125.80**, with its two pads still on the A/C
  rails at Y=114.88/130.12 and with unchanged nets and 15.24 pitch. This makes
  physical room for the relocated SMT footprints without shrinking courtyards;
  the north-south overpass and minimum height control remain mandatory.
- J_IN courtyard ends at global **X=111.75**, SMT begins at **116.50**, gap
  **4.75**. SMT ends at **122.50**, GDT_AC begins **122.55**, gap **0.05**.
  GDT_AC ends **129.05**, earth-GDT courtyards begin **129.22**, gap **0.17**.
  These are drawing-boundary distances, not demonstrated rework clearance.
- Keep the four 3.20-wide stub endpoints at Y=116.19,121.19,123.81,128.81.
  They overlap the new lands without extending the rounded copper further
  beneath the tubes. The land/mask/paste inner gap is **2.80**; the underlying
  connected copper gap is **1.80**. These are different dimensions. Do not
  blindly extend the tracks to the new pad centres and reduce that copper gap.

Historical overlap at A: the via at Y=114.88 with radius 0.50 reached 115.38;
the original SMT aperture started at Y=115.19, overlapping the hole by **0.19**.
The three X positions on each rail lay inside the old aperture's X extent.
All nine rail holes were affected; the three B-rail holes faced both SMT parts.

Now each SMT aperture starts at X=116.75. For the nearest protected via at
X=115.50, the nearest aperture corner is offset by dx=1.25 and dy=1.21:

```text
corner distance                   = sqrt(1.25^2 + 1.21^2) = 1.739713
nominal drill-circle to aperture  = 1.739713 - 0.50       = 1.239713
nominal full annulus to aperture  = 1.739713 - 0.90       = 0.839713
```

The same minimum applies to all four SMT pads for `F.Mask` and `F.Paste` in the
saved zero-margin source. None exposes a protected via annulus. All vias now
have intentional mask openings, so **0.839713** is the nominal open-annulus
to SMT-aperture budget, **not** a registration or solder-process guarantee.
Recheck actual processed mask/stencil apertures,
drill sizes, registration allowances and solder spread, not just pad centres.

**Remaining W1 order/process hold:** figure associations and the selected
metric implementation are resolved, but the manufacturer's contradictory inch
entry and the actual solder process remain to accept. Paste area is now **6.60
mm^2 per land**, down from 10.40 (36.54% at equal stencil thickness). That is
not measured deposited solder volume. Obtain the actual processed stencil and
joint/profile acceptance, preserving the below-tube insulation space.

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

- No filling by size. R1/R2 formerly shared the 1.00 via diameter and now use
  1.40 component holes; hole function, not size, remains controlling. All
  component PTH holes stay open for insertion; no via is an insertion pad.
- Preserve all fourteen via locations, hole diameters and copper diameters.
  Obtain written CAM agreement not to reduce the protected via drills under
  ordinary via-hole adjustment practices.
- **Selected standard process: Untented, both sides, no fill/plug/cap.** Source
  openings are nominal **1.80 circular F.Mask/B.Mask**, no via paste. ENIG is
  exposed and wettable. Adjacent same-net rail-via mask openings intentionally
  overlap at 1.50 pitch; this is not an exception for a component paste opening
  over a hole. No reliable 1.00 tenting or special filling process is required.
- Inspect processed openings/drills and qualify solder ingress, drain-through,
  beads and cleanliness. Standard via drill adjustment is not authorized to
  shrink the protected geometry. Neither untented ENIG nor OneGel seals a hole.
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
5. Clean, dry and inspect before any WISKA **OneGel** encapsulation. It is a
   single-component silicone cartridge, **no mixing**, not MP0100. Resolve the
   manufacturer's conflicting cure/temperature fields and approve the actual
   dispensing, materials, cleanliness, thermal behavior and overpass insulation
   using [OneGel evidence](ENVIRONMENT_EVIDENCE.md#wiska-onegel). Retain **one unpotted
   reference prototype**. Potting and the enclosure's unmodified IP rating do
   not qualify the completed coastal installation.

## Acceptance Record

Before release, retain board serial/revision, BOM/lot and drawing revisions,
approved pin-fit calculations, measured forming/pitch/height, solder profile,
via-coordinate CAM acceptance, processed mask/stencil/drill review, assembler
rotation approval, support/enclosure dry-fit and measured thermal/electrical
results. Basic workmanship on five boards is not field or surge qualification.

Open approvals are now specific: allocated Kefa/Vishay/Bencent parts must meet
the selected E/pattern/body envelopes; actual diode and GDT forming must be
accepted; the KF129 drawing variant, metric SMT interpretation, processed
stencil and solder fill/profile need supplier acceptance; J_EARTH's 1.30
tolerance-budgeted overhang and full COMBI/support fit need inspection. Untented
fabrication is standard, not an unresolved 1.00 filling request. Protected
drills, any required barrel minimum, OneGel compatibility and P2 protection/
continuous-duty design remain held. No lot, CAM or hardware pass is invented.

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
