# DFM Evidence

Research date: **2026-09-07**. Design baseline: **97e202d**, hardware
**1.2.0-dev**. Scope: P3, principally W1/W4/W5.

Dimensions are millimetres unless explicitly marked inches. Global coordinates
use the top-view board convention from ASSEMBLY.md; local coordinates are
identified separately below.

**Hybrid update after checkpoint ad282e3:** the original six-family research
below remains historical evidence. Current R1/R2 are copper-lead PR02
PR02000202201FA100 (0.83 maximum lead, retained 1.40/2.40 holes/pads,
12.00 x 4.20 conservative body box, >=1.00 standoff). D1-D4 are now
BYG23T-M3/TR SMA; no onsemi diode PTH remains. ASSEMBLY controls the selected
2.50 x 2.00 lands / 1.70 inner gap / 7.20 x 3.60 courtyard and exact orientations.
Parent visually read the original Vishay 89429, 25-Feb-2020 p4 outline/land
leaders through the public PDF viewer; 1.52/1.68 land minima and 1.88 maximum
inner gap are resolved, while 5.28 outside span is a reference dimension.
This is not JLCPCB stencil, part allocation or physical acceptance. All other
protected geometry and the metric GDT land decision remain unchanged.

**Evidence and original integration recommendations, NOT manufacturing approval.**
The bounded research wrote only this record. In the subsequent 2026-09-07
integration, the parent adopted the worked hole/pattern envelopes, body boxes,
courtyards, metric SMT lands and standard untented vias in the PCB/local
footprints. [ASSEMBLY.md](ASSEMBLY.md) now controls those choices and their
unperformed lot/process acceptance. The recommendations below retain their
original calculations and provenance; they do not claim supplier agreement,
physical testing, or approval of a new protection circuit. Current automated
results belong to the REMEDIATION handoff, not the research-only verification
section below. Schematic/BOM identities and all guardrails remain unchanged.

## Conclusions

- Original mechanical figures for **all six requested part families were
  visually read**, including the Kefa tolerance tables and both Ruilon THT
  revisions. Their dimensional associations are no longer a text-reader hold.
- Ruilon **2R470TD-8** has a drawing lead maximum of **1.05 mm**. Its current
  1.20 mm hole leaves only `1.20 - 0.08 - 1.05 = 0.07 mm`, below the required
  0.10 mm allowance. Its metric maximum body is **6.30 long x 8.20 diameter**.
- Kefa **KF128-7.62-3P** pins are rectangular, nominal **0.90 x 0.80**.
  **KF129-5.08-2P** has a real source conflict: **0.90 x 0.80** in the
  C475092-distributed drawing versus **0.95 x 0.80** in the manufacturer-linked
  drawing, both marked **A / 21.03.13**. The present 1.40/1.30 holes are not a
  tolerance-supported solution. In particular, KF129 fails the project allowance
  even using the smaller nominal pin, before adding pin tolerances.
- Vishay explicitly labels its **0.80 mm lead as nominal**. Bencent's original
  figure labels a **0.80 mm round lead without a tolerance**. Neither figure
  supplies a manufacturer-guaranteed finished lead maximum. A controlled
  **0.90 mm finished acceptance envelope** is proposed for each, instead of
  leaving the hole design indefinitely unspecified.
- Ruilon **SMD5050-470NA**: **X1 is pad centre-to-centre spacing**, not the inner
  gap or outside span. The metric recommendation translates to **5.50 x 1.20 mm
  lands at local Y = +/-2.00** in this board's orientation. The 4.0 mm / 0.165 in
  conflict exists in the original manufacturer PDF too. Use of the metric column
  is an explicit proposed engineering choice, not a claimed manufacturer erratum.
- **Standard untented ENIG vias** are a supported alternative to unsupported
  1.00 mm filling/tenting assumptions. Preserve every 1.00/1.80 via and all
  protected copper. No special fill, press-fit tolerance or CAM exception is
  proposed as the solution.

## Figure Access

Direct PDF requests with native `webfetch` returned PDF streams rather than
rendered pages. That was not treated as evidence that the figures were
unreadable. The original public URLs were then opened through Google's public
PDF viewer, and its page-image endpoints were fetched with native `webfetch`.
The returned image attachments, including dimension arrows and title blocks,
were visually inspected. No terminal network fetch or download script was used.
Existing `tmp/dfm-review/` and `tmp/layout-review/` directory listings were also
inspected without changing their evidence; they did not provide the requested
component drawings in the inspected listings.

Repeatable access method, not an alternative drawing authority:

1. Fetch `https://docs.google.com/gview?embedded=1&url=<URL-encoded-original-URL>`
   as HTML. Some initial requests returned an empty response; retrying succeeded.
2. Use the returned `img?id=...` URL under `https://docs.google.com/viewerng/`,
   with `&page=N-1&w=2400` for printed page N. `page` is zero-based;
   `pagenumber` did not select the requested page in this viewer.
3. Check the actual printed page number, MPN/family, revision and dimension
   leaders. Viewer IDs are temporary, so the permanent evidence links below
   identify the original files, not expiring image tokens.

**V** below means original figure visually read; **T** means retrieved text.
**Derived** means arithmetic from published dimensions. **E** means a proposed
controlled procurement/assembly envelope, **not a manufacturer guarantee**.
Original PDFs/images were not added to the workspace in this bounded task.

| Exact selected identity | Original source and revision | Access actually used |
| :--- | :--- | :--- |
| Cixi Kefa KF128-7.62-3P / C474957 | [Manufacturer drawing][k128-m] and [C474957 drawing][k128-l], title KF128-7.62, revision A, 21.03.13, one sheet. Manufacturer [product page][k128-page] links the 7.62 drawing separately from 7.5. | V: both sheets, pin leaders, PCB layout and general tolerance table. P=3 applied to the family drawing. |
| Cixi Kefa KF129-5.08-2P / C475092 | [Manufacturer drawing][k129-m] and [C475092 drawing][k129-l], title KF129-5.08, revision A, 21.03.13, one sheet. [Product page][k129-page] identifies the 5.08 drawing. | V: both sheets. Different 0.95/0.90 pin-width labels despite identical revision/date; not silently reconciled. P=2. |
| Vishay MBE04140C2201FC100 / C1368610 | [Document 28766][vishay], revision 11-Jul-2018, p13 dimensions; p4 ordering and p7 construction/assembly. [Document 28721][vishay-pack], revision 16-Jan-2025, packaging. | V: 28766 p13. T: ordering, tin-plated copper construction and packaging. Packaging did not establish a missing lead-diameter maximum. |
| Bencent B5G470L / C5337217 | [C5337217 PDF][bencent-l], A2 / 2018-01-03, p2. The current [manufacturer product page][bencent-page] supplies [this direct PDF download][bencent-m], also A2 / 2018-01-03. | V: p2 from both sources. The 20260514 upload pathname is not a new drawing revision. Lead diameter is printed directly on the figure, outside its A/B/C table. |
| Ruilon 2R470TD-8 / C2836978 | [Distributed SP-GDT-017][ruilon-tht-l], A3 / 2023-11-02, p3; [manufacturer SP-GDT-017][ruilon-tht-m], A6 / 2025-10-16, p5. Manufacturer listing [page 4][ruilon-page4] links A6 for 2R470TD-8. | V: both dimension figures, specifically the **TD axial** drawing, not the SD surface-mount drawing below it. Mechanical dimensions agree. |
| Ruilon SMD5050-470NA / C39692533 | [Distributed SP-GDT-006][ruilon-smt-l] and [manufacturer SP-GDT-006][ruilon-smt-m], A3 / 2024-08-19, p3. Manufacturer listing [page 5][ruilon-page5] links that file for the exact non-BVL MPN. | V: both p3 figures/tables; X/X1/Y leaders and body axes resolved. T: p5 reflow and p6 solder-bridging caution. No BVL or NB substitution used. |

## THT Dimensions

### Kefa

The printed general linear-tolerance table on **both** families says:
dimensions up to 6: +/-0.20; over 6 to 10: +/-0.30; over 10 to 30: +/-0.50 mm.
Its heading cites **GB/T 14486-2008**, a plastics dimensional-tolerance standard.
There is no separately stated plating/burr allowance for the metal pins.
Applying its +/-0.20 band to pin cross-sections is a conservative, drawing-based
**procurement envelope**, not a claim that the plastics standard independently
guarantees the maximum finished metal pin. The chosen limits must include the
actual tin plating and any permissible stamping/cutting irregularity.

| Association visually read | KF128-7.62, P=3 | KF129-5.08, P=2 |
| :--- | :--- | :--- |
| Rectangular pin cross-section | Front view width 0.90; side view thickness 0.80. | Front view width 0.90 in LCSC copy, 0.95 in manufacturer copy; side view thickness 0.80 in both. |
| Lead length below seating face | 4.30 +/-0.30. The table's "Pin Dimensions 4.3" is length, not diameter. | 4.80 +/-0.30. The table's "Pin Dimensions 4.8" is length, not diameter. |
| Body depth, front to rear | 10.50; pin row to rear face 5.20, hence nominal front projection 5.30. | 10.60; pin row to rear face 4.90, hence nominal front projection 5.70. |
| Body height above seating face | 14.10. Derived general-tolerance upper bound 14.60. | 18.30. Derived general-tolerance upper bound 18.80. |
| Main body length along pin row | P x 7.62 = 22.86; derived upper bound 23.36. | P x 5.08 = 10.16; derived upper bound 10.66. |
| End interlocking projection | Separately dimensioned 0.60; derived upper bound 0.80. Do not omit it from an isolated terminal's envelope. | Separately dimensioned 0.55; derived upper bound 0.75. |
| Actual part pitch callouts | 7.62 and (P-1) x 7.62, without individual +/- labels. General bands would be +/-0.30 on adjacent pitch and +/-0.50 on 15.24 overall span. | 5.08 and (P-1) x 5.08, without individual +/- labels; general band +/-0.20. |
| Recommended PCB, **not a pin tolerance** | Hole diameter 1.40 +0.10/-0.00; pitch 7.62 +/-0.03. | Hole diameter 1.40 +0.10/-0.00; pitch 5.08 +/-0.03. |

The Kefa PCB hole recommendation has **no negative hole tolerance**. A JLCPCB
nominal 1.40 component hole can finish at 1.32; it is not the same requirement.
Likewise the +/-0.03 layout pitch must not be passed off as the tolerance of
the delivered connector pins.

Proposed finished-pin limits:

```text
KF128 E: width <=1.10, thickness <=1.00
         diagonal = sqrt(1.10^2 + 1.00^2) = 1.486607
KF129 E: width <=1.15, thickness <=1.00
         diagonal = sqrt(1.15^2 + 1.00^2) = 1.523975
```

The KF129 envelope covers the larger of the conflicting nominal widths plus
the printed small-dimension tolerance band. These are not promises that an
uninspected allocation meets them. Check the widest insertion section, not
just the tapered tip. Do not clip, grind or squeeze pins into compliance.

Body projections also need tolerance stacking, not just a larger total depth:

```text
KF128 rear max = 5.20 + 0.20 = 5.40
      front max = (10.50 + 0.50) - (5.20 - 0.20) = 6.00
KF129 rear max = 4.90 + 0.20 = 5.10
      front max = (10.60 + 0.50) - (4.90 - 0.20) = 6.40
```

Neither sheet independently dimensions every end-face-to-pin datum. The
pin-row-relative body boxes below are therefore explicit **E acceptance boxes**,
including the end keys, rather than an assertion of exact body centring from
the drawing alone. Their row half-extents are based on half the toleranced
main length plus the entire maximum end key: `23.36/2 + 0.80 = 12.48` and
`10.66/2 + 0.75 = 6.08`, rounded outward to 12.50 and 6.10. Inspect both ends
relative to the actual pin-pattern datum, not only the total body length.

### Axial Parts

| Exact identity | Visually resolved dimensions | Finished-pin design treatment |
| :--- | :--- | :--- |
| Vishay MBE04140C2201FC100 | p13's `d_nom = 0.80` is the round wire diameter. `D_max = 4.20` is body diameter; `L_max = 11.90` body length; `l_min = 31.0` each unformed lead; `M_min = 15.0` mounting pitch. | **E <=0.90 diameter**, including tin finish, roundness and any insertion-section forming distortion. This is nominal +0.10 (12.5%), chosen as a controllable upper acceptance limit, not a Vishay specification. Do not borrow radial MBB0207 tolerances or tape-spacing tolerances. |
| Bencent B5G470L | p2 lead is explicitly round, diameter **0.80**, with no +/- or maximum qualifier. A=62 +/-2 is unformed overall length; B=6 +/-0.20 is body length; C=diameter 5.50 +/-0.20 is body diameter including the end-electrode outline. Copper leads, matte-tin finish are stated. | **E <=0.90 diameter**, for the same stated procurement rationale as Vishay. A/B/C tolerances do not create a tolerance on the separate 0.80 lead callout. Current 1.20 holes pass diameter-only against this E, but not the complete fixed-pattern budget below. |
| Ruilon 2R470TD-8 | TD figure in both revisions: lead diameter **1.00 +/-0.05**; body diameter **8.00 +/-0.20**; axial body length **6.00 +/-0.30**; unformed overall length **62 +/-2**. | Drawing-derived maximum **1.05 diameter**. Require the finished insertion section to remain <=1.05 after forming too; enlarged bends/burrs must not enter the barrel. THT finish is nickel plated in the retrieved manufacturer text. |

The Ruilon A6 version-history text dates its A3 entry 2023-03-31, whereas the
distributed A3 dimension sheet prints 2023-11-02. This does not change the
visually matching mechanical numbers, but retain the exact applicable file/lot;
do not merge electrical or temperature claims across revisions.

Where a metric and a rounded inch body limit differ slightly, the proposed
library bounds below round **the larger converted upper value** outward:

| Body dimension | Metric upper | Inch upper converted | Proposed bound |
| :--- | ---: | ---: | ---: |
| Bencent diameter | 5.700 | (0.217+0.008) x 25.4 = 5.715 | 5.72 |
| Ruilon TD diameter | 8.200 | (0.315+0.008) x 25.4 = 8.2042 | 8.21 |
| Ruilon SMT end-face A/B | 5.200 | (0.197+0.008) x 25.4 = 5.207 | 5.21 |

These small outward roundings avoid needing a controlling-unit assumption for
body clearance. They are not new manufacturer dimensional tolerances. Ruilon's
1.05 metric lead upper limit is already larger than the converted inch upper
limit, `(0.039+0.002) x 25.4 = 1.0414`.

## Hole Recommendations

All hole sizes here are **nominal finished component PTH dimensions**, not
unplated tool diameters. Use ordinary round holes, not press-fit or slots.

```text
H_min = H_nom - 0.08
D_pin = finished round diameter, or sqrt(W_max^2 + T_max^2)
Diameter-only requirement: H_min >= D_pin + 0.10
Nominal ring = (minimum pad width - H_nom) / 2 >= 0.254
```

| Part family | Current hole | H_min minus design pin envelope | Diameter-only minimum on a 0.10 mm hole grid |
| :--- | ---: | ---: | ---: |
| KF128, E diagonal 1.486607 | 1.40 | -0.166607 | 1.70 |
| KF129, E diagonal 1.523975 | 1.30 | -0.303975 | 1.80 |
| MBE0414, E diameter 0.90 | 1.00 | 0.020000 | 1.10 |
| B5G470L, E diameter 0.90 | 1.20 | 0.220000 | 1.10 |
| 2R470TD-8, diameter 1.05 | 1.20 | 0.070000 | 1.30 |

The first two negative results are against the **proposed conservative E**,
not a claim that every nominal connector fails to enter the old board.
Nominal KF128 diagonal is 1.204159, leaving 0.115841 in the current worst hole,
only 0.015841 beyond the required allowance before any pin tolerance. KF129's
smaller nominal diagonal is also 1.204159, leaving **0.015841 total** in its
1.22 worst hole; the larger nominal diagonal is 1.241974 and exceeds that hole.

### Independent Position Budget

The last column above is **not** a complete insertion recommendation. A 0.10
diametral assembly allowance cannot also pay for arbitrary pitch error.
JLCPCB publishes hole position tolerance +/-0.05. Conservatively treating that
as +/-0.05 on each board axis gives radial `e_h = sqrt(2)*0.05 = 0.070711`.

One implementation-ready, ordinary-process choice is the following table, with
a **separately controlled part-pattern limit `e_p <=0.050 mm radial` per pin**.
This limit applies after one common rigid alignment of the complete pin pattern
to the nominal footprint, through the full insertion length. It includes
non-collinearity, lean and forming errors, not just adjacent pitch. It is an
incoming/formed-part inspection condition, **not a Kefa/Vishay/GDT guarantee**.

```text
Additional diametral position budget = 2*(e_h + e_p) = 0.241421
Require H_nom - 0.08 - D_pin - 0.241421 >= 0.10
```

| References | Proposed hole / unchanged pad size | Diameter-only clearance | Clearance after separate position budget | Nominal ring |
| :--- | :--- | ---: | ---: | ---: |
| J_IN, J_EARTH | **2.00 / 3.20** | 0.433393 | 0.191972 | 0.60 |
| J_LED_A, J_LED_C | **2.00 / 2.80** | 0.396025 | 0.154604 | 0.40 |
| R1, R2 | **1.40 / 2.40** | 0.420000 | 0.178579 | 0.50 |
| GDT_AC | **1.40 / 2.80** | 0.420000 | 0.178579 | 0.70 |
| GDT_A_E, GDT_B_E, GDT_C_E | **1.50 / 3.00** | 0.370000 | 0.128579 | 0.75 |

This is a conservative **bounded design option for parent selection**, not a
requirement to enlarge every hole this much regardless of actual part evidence.
It deliberately trades more solder volume and fixture dependence for insertion
margin without requiring tighter JLCPCB fabrication tolerances. All pad shapes,
centres, nets and copper dimensions can remain unchanged. The minimum ring is
0.40, above 0.254. Nominal rings are not guarantees of finished registration,
etch tolerance, solder fill or barrel copper.

Smaller holes are supportable only with an independently demonstrated combined
alignment bound `e_h + e_p <= (H_nom - 0.08 - D_pin - 0.10)/2`, or an accepted
forming process that fits the measured actual board pattern. Do not claim that
1.70/1.80 connector holes accommodate the broad general pitch bands on the
Kefa drawings. Conversely, screening an ordinary lot to the explicit E/pattern
limits is a legitimate alternative to waiting for a new manufacturer guarantee;
do not claim the screen has already passed or that its yield is known.

For 15.24-pitch axial parts, the proposed radial part-pattern bound limits the
two-pin spacing error to at most 0.10. Vishay's formed mounting dimension would
then be at least **15.14 > 15.00**. Inspect actual M after assembly as well;
larger holes must not let the leads collapse inward below the mounting minimum.
The minimum-hole proof covers neither ceramic-seal bending stress nor pullout.

## Body Geometry

Implementation coordinates in this table are **local footprint coordinates**,
using the existing origins/rotations and the two distinct LED pad mappings.
Body boxes include electrodes, moulding projections and end keys, but not the
entire unformed lead length. Retain reference/polarity/lead graphics as needed.
LED A retains local pad 1 at (0,-2.54), pad 2 at (0,+2.54), with footprint
rotation 90 degrees; LED C retains pad 1 at (0,+2.54), pad 2 at (0,-2.54),
with rotation 270 degrees. Both retain global positive X=142.96 and B-return
X=148.04, at Y=103.00/142.00 respectively. Body-outline changes do not authorize
pad-position, pad-angle or net changes.

Proposed assembly control: the actual projected body must remain inside its
listed body box expanded by **0.10 on each side**, including translation and
tilt. This is an inspected projection bound, not permission to add arbitrary
rotation on top of the allowance. Courtyards contain that projection plus at
least 0.25 assembly margin, and existing pads plus 0.25 where pads dominate.

| Footprint family | Proposed F.Fab body/envelope box: X; Y | Proposed F.CrtYd box: X; Y |
| :--- | :--- | :--- |
| KF128 Input and Earth | **-6.00..5.40; -12.50..12.50** (E) | **-6.35..5.75; -12.85..12.85** |
| KF129 LED A and C | **-5.10..6.40; -6.10..6.10** (E) | **-5.45..6.75; -6.45..6.45** |
| MBE0414 | **-5.95..5.95; -2.10..2.10**, unchanged | **-9.10..9.10; -2.50..2.50**, unchanged |
| B5G470L north-south overpass | **-2.86..2.86; -3.10..3.10** | **-3.25..3.25; -9.30..9.30** |
| 2R470TD-8 east-west | **-3.15..3.15; -4.105..4.105** | **-9.40..9.40; -4.46..4.46** |
| SMD5050-470NA north-south electrode axis | **-2.605..2.605; -2.25..2.25** | **-3.00..3.00; -3.75..3.75**; widen X, retain existing Y |

These changes do not conceal interference by shrinking courtyards. The SMT
body's shorter Y follows the newly resolved axial C dimension; its courtyard Y
is deliberately retained. All body/pad proposals are suitable for source
integration without moving protected vias, rails, earth copper, mounts or LEDs.
They still need integrated native DRC and actual assembly acceptance.

Calculated checkpoint-placement checks, **not a DRC run**:

- J_IN courtyard east becomes X=111.75; SMT west is X=116.50: **4.75 gap**.
- SMT east becomes X=122.50; overpass west is X=122.55: **0.05 gap**.
  This is a small drawing-space margin, not demonstrated rework access.
- Overpass east is X=129.05; earth-GDT west is X=129.22: **0.17 gap**.
- Earth-GDT courtyard height is 8.92 on the preserved 9.00 pitch: **0.08 gap**.
  With an 8.21 body bound and the stated 0.10 projected displacement allowance
  for each neighbour, physical body gap is at least
  `9.00 - 8.21 - 2*0.10 = 0.59`. This is **not a 1.00 mm air-gap guarantee**,
  nor an impulse-insulation qualification. Inspect the full bodies/electrodes.
- LED courtyard global X is **139.05..151.95**. The protected H2/H4 courtyard
  west boundary is X=152.05: **0.10 gap**. LED A global courtyard Y is
  **96.25..108.45**; LED C is **136.55..148.75**. No pad/net remapping or
  connector rotation change is needed.
- At unchanged J_EARTH=(155.00,122.50), 180 degrees, the accepted body envelope
  reaches X=161.00 before pose allowance, or **161.10 after it**. Against a
  regular routed east edge as far inward as 159.80, allow **1.30 overhang**,
  not the former nominal 0.30. Its courtyard reaches X=161.35. Check ordinary
  panel orientation/routed spacing and COMBI clearance using this envelope;
  do not trim the outline or shift protected earth copper to hide the overhang.

The Kefa maximum body heights are 14.60 and 18.80 above their seating planes;
seat standoff and solder/lead protrusions are separate. Assuming flush seating
and the standard 1.44..1.76 board-thickness range, untrimmed lead protrusion is
2.24..3.16 for KF128 and 2.74..3.66 for KF129. These calculations do not approve
the support/enclosure fit or the assembler's trimming process.

### Overpass Control

Keep GDT_AC at X=125.80, north-south, pad Y=114.88/130.12, pitch 15.24.
The whole raised body/electrode/lead span must retain **>=2.00 above the highest
finished PCB surface** before encapsulation, as ASSEMBLY.md requires. A
candidate fixture target is body underside **2.50 +/-0.25**, with the complete
assembled projection limited to **8.50 maximum height**: 2.75 + 5.72 = 8.47
for the body alone. Inspect the actual complete span; the body-only calculation
does not account for an upward lead bow or a low bend.

The 15.14 minimum formed pitch and 6.20 maximum body leave 4.47 per end before
body offset and bend geometry. This establishes available geometric room, not
an approved bend radius or seal setback. Manufacturer/assembler limits on seal
support, bend radius, springback and soldering remain specific open facts.
Gel does not preserve an air gap or replace insulation qualification.

## SMT Land Resolution

In both original **SP-GDT-006 A3 / 2024-08-19 p3** figures:

- **X=1.2** spans the width of one narrow rectangular land, along the tube axis.
- **X1=4.0** runs between the dashed centre lines of the two lands.
- **Y=5.5** spans the long dimension of each land, transverse to the tube axis.
- A/B=5.0 +/-0.2 describe the **square end face**, not a 5 x 5 plan body with
  4.2 height. C=4.2 +/-0.3 spans the axial length including end electrodes;
  D=0.5 +/-0.1 describes one end-electrode thickness.

The conversion conflict is substantial, not ordinary display rounding:

```text
4.000 mm / 25.4 = 0.157480 in, not 0.165 in
0.165 in * 25.4 = 4.191 mm
```

The original manufacturer file repeats the contradiction; there was no public
correction in the retrieved exact-MPN source. **Recommend selecting the printed
metric 4.00 mm spacing**, documenting that decision explicitly. The duplicated
0.165 also appears as the correct rounded inch value for C=4.2 in the same
table, which is consistent with a copied conversion error, but does not prove
the manufacturer's intended correction. Do not average the numbers, silently
choose a 4.2 pitch, call X1 a gap, or claim written approval.

Exact proposed footprint geometry, preserving pad numbers and nonpolar part
orientation:

| Pad | Local centre | Copper / nominal mask / nominal paste rectangle |
| :--- | :--- | :--- |
| 1, north | **(0,-2.00)** | **5.50 X x 1.20 Y**, F.Cu/F.Mask/F.Paste |
| 2, south | **(0,+2.00)** | **5.50 X x 1.20 Y**, F.Cu/F.Mask/F.Paste |

Use zero extra mask/paste margins as the source baseline; no custom stencil
process is implied. Inner land gap is **2.80**, outside span **5.20**, width
**5.50**. At the existing origins, all four lands have X=116.75..122.25:

| Part / pad | Global Y bounds |
| :--- | :--- |
| GDT_AB / 1 | 116.09..117.29 |
| GDT_AB / 2 | 120.09..121.29 |
| GDT_BC / 1 | 123.71..124.91 |
| GDT_BC / 2 | 127.71..128.91 |

The metric body/electrode limits give at least 0.40 axial overlap of each
electrode with its land at nominal placement, also with up to +/-0.10 axial
translation when evaluated over C=3.9..4.5 and D=0.4..0.6. This is a geometric
contact check, not a solder-fillet or paste-volume qualification. Transverse
body maximum 5.21 plus +/-0.10 placement fits inside the 5.50 land width.

**Keep the current 3.20-wide connection-stub endpoints** at
(119.50,116.19), (119.50,121.19), (119.50,123.81), (119.50,128.81).
They still overlap the new lands with a full-width incoming section. Do not
blindly extend these wide round-ended tracks to the new pad centres: their
inner copper ends would then leave only 0.80 between opposite nets. Keeping
the old endpoints preserves their existing **1.80 masked-copper gap** beneath
each tube. The 2.80 figure above is the **land/mask/paste gap**, not the minimum
gap of all connected copper. Preserve mask over the extra stub copper and
inspect the processed mask and stencil; no solder bridge may reduce the
insulation distance beneath the arrester.

Closest protected via is still X=115.50 on each adjacent rail. For the new
land corner, dx=1.25 and dy=1.21:

```text
corner distance = sqrt(1.25^2 + 1.21^2) = 1.739713
to full nominal 1.00 drill circle         = 1.239713
to full nominal 1.80 copper/mask opening  = 0.839713
```

Thus untenting the vias does not require moving/shrinking them or filling them
to cure the former SMT collision. If CAM expands apertures or changes drills,
subtract those actual changes and registration allowances and recheck all four
lands. Area per source paste land changes from 10.40 to **6.60 mm^2**, a
**36.54% reduction at equal stencil thickness**. JLCPCB generates its processed
stencil using its own component rules, not necessarily these raw F.Paste
rectangles. This does not specify the actual deposited solder volume.

## Standard Process

The authorized baseline is ordinary **two-layer FR-4, 2 oz on both sides,
nominal 1.6 mm, ENIG**, with green mask a standard choice. Nothing in these
recommendations needs epoxy/copper filling, reliable 1 mm tenting, press-fit
holes, heavier barrel plating by assertion or a special CAM concession.

| Primary public evidence, retrieved 2026-09-07 | What it actually establishes |
| :--- | :--- |
| [Via covering][jlc-via], updated 18-Aug-2026 | Untented vias have no special process requirements; exposed copper receives the selected finish, including ENIG. The <=0.5 mm covering recommendation applies to the other treatments, not untented vias. Untented vias are wettable; solder ingress/beads remain possible. |
| [Pad/via hole tolerance][jlc-holes], updated 24-Apr-2025 | Ordinary component holes: +0.13/-0.08; use pin diagonals and metric one-decimal hole sizes. Ordinary via diameter is **not controlled** and may be adjusted in production. |
| [Rigid PCB capabilities][jlc-pcb], live table | Two-layer 2 oz and ENIG offered; hole position +/-0.05; two-layer/2 oz component PTH ring >=0.254; 1.6 thickness +/-10%; 18 micrometres **average**, not minimum, hole plating. Mask can be 1:1 following the June-2025 LDI update; 2 oz mask bridges require 0.20. |
| [PCBA capabilities][jlc-pcba], live table | Mixed SMT/THT offered in both service tiers. Standard PCBA needs 70 x 70 minimum processing size and rails; Economic lists applicable 1.6/green/ENIG options. These are not allocation or exact 2 oz assembly-quote acceptance. |
| [Stencil preparation][jlc-stencil], updated 16-May-2026 | Stencil apertures are generated from verified production/component data, not simply copied from the customer's paste Gerber. Normally only selected SMT parts receive apertures. |

Adopted via implementation: explicitly **untent all fourteen on both
sides**, with nominal **1.80 circular F.Mask/B.Mask openings**, no via F.Paste,
and select the standard **Untented** order option. The parent has replaced
the checkpoint's global front/back tenting request with this source setting.
Preserve these exact nominal drills/copper/locations:

- Nine rail vias: all combinations of X=112.50,114.00,115.50 and
  Y=114.88,122.50,130.12; **1.00 / 1.80**.
- Five EARTH vias: X=150.00, Y=114.88,118.69,122.50,126.31,130.12;
  **1.00 / 1.80**.

Use coordinate/function identification, never a fill-by-diameter instruction.
Keep all component holes open. Review ordinary production files for preservation
of the fourteen 1.00 nominal drills and unchanged copper; reject an unapproved
CAM reduction rather than accepting it as an implementation detail. Public
standard-via guidance does **not** guarantee a 1.00 finished diameter/tolerance.
If the parent needs a contractual finished-via minimum beyond standard service,
that remains a separate unresolved supplier fact, not authority to order special
processing. An untreated via is not a sealed environmental barrier.

The PCBA FAQ says unused through-holes are protected during wave soldering, but
that is not a coordinate-specific promise for these exposed stitching vias.
Inspect solder ingress, loose beads, hole fill, wetting and cleanliness on actual
boards. Do not depend on fill or mask opacity to make a process acceptable.
Retain 3.20 full-width rails on both layers and the solid earth bus; no thermal
spokes, slits or drill reduction to ease soldering.

The published PCBA reflow table gives Economic 255 +/-5 degrees C and Standard
240 +/-5 degrees C, whereas SP-GDT-006 lists a 260 +0/-5 peak profile. Those
numbers are not interchangeable evidence of an accepted joint/body profile.
Select an ordinary supported assembly service whose actual profile is suitable;
do not presume a special profile is authorized. The 2 oz thermal load, actual
alloy/flux, THT sequence and formed GDTs still require process evidence.

## Independent Acceptance

The E limits make a bounded design possible; **no actual lot or sample was
measured in this research**. A normal procurement inspection can control them
without pretending that the manufacturer guarantees a new dimension.

1. Parent records the adopted finished-pin/body/pattern limits and exact
   drawing/MPN/lot on the procurement and assembly traveller. Obtain an ordinary
   allocated-lot dimensional report or inspect independent actual samples
   before relying on the envelope for the prototype order. Do not approve an
   unallocated catalogue photo or supplier CAD model as this evidence.
2. For the five-board baseline, inspect **every allocated part** in the
   controlled-envelope families, including spares used in assembly. Measure
   both rectangular axes at their largest insertion section and enough axial
   wire orientations to bound ovality. Include plating, burrs and uncertainty:
   accept an upper limit only when `measured maximum + uncertainty <= limit`.
3. Independently measure the complete pin pattern through the insertion depth,
   using a calibrated optical fixture or suitable metrology. Confirm the
   separate 0.050 radial per-pin envelope, not just one nominal pitch. Formed
   axial parts are inspected after forming; preserve Vishay M>=15.0. A tight
   nominal gauge that forces leads into place is not a valid inspection.
4. Check insertion with a dimensional fixture representing the chosen minimum
   finished holes and the accepted pattern budget, then on the actual boards.
   Record free insertion, seating, body projection, lead protrusion and the
   whole-span overpass height. Never ream plated boards or force ceramic seals
   to fit. Larger-hole solder fill/workmanship must be accepted independently.
5. Measure body/end-key extents relative to pin-pattern datums and verify the
   proposed projected-body boxes, neighbour gaps, mounting keepouts and
   J_EARTH overhang. Perform the complete unpotted COMBI/WAGO/support/LED dry-fit,
   including screwdriver access and lid travel, before encapsulation.
6. Inspect processed copper/mask/paste/drills and actual SMT fillets. Keep the
   manufacturer's below-arrester insulation space free of solder. Inspect
   untented vias and do not treat gel as a seal or the drawing as surge proof.
   Retain the unpotted reference and distinguish workmanship from P2/P6
   electrical, thermal, environmental and powered-recovery qualification.

### Remaining Supplier Facts

| Party / part | Precise fact still needed; what no longer needs rediscovery |
| :--- | :--- |
| Kefa / C474957 and C475092 | Which controlled KF129 A/21.03.13 pin-width variant is actually supplied: 0.90 or 0.95? What finished metal-pin tolerances, plating/burr inclusion, pitch/non-collinearity and pin-to-body datums are guaranteed? The rectangular axes, body projections, end keys and drawing general-tolerance bands **have been read**. Adopted E limits plus independent lot acceptance can replace an absent tighter guarantee for that limited lot, not for all future purchases. |
| Vishay / MBE04140C2201FC100 | Finished d_max for the exact neutral C1 part, including pure-tin finish and the straight insertion section, if a manufacturer-guaranteed limit is desired. The public d_nom=0.80 and D/L/M body/mounting limits are already resolved. Otherwise control <=0.90 by procurement inspection, rather than relabelling d_nom as a maximum. |
| Bencent / B5G470L | Finished 0.80-wire tolerance and allowable forming/seal-support geometry. Public p2 really contains a round 0.80 callout without its tolerance. A2 body limits are resolved; the current manufacturer download did not supply a newer toleranced lead drawing. Control <=0.90 and verify the proposed formed envelope if selected. |
| Ruilon / 2R470TD-8 | Exact revision/production code allocated; allowed bend radius/seal setback, post-forming lead condition and ordinary nickel-lead solder process. The 1.05 lead maximum and 6.30/8.20 metric body maxima are **resolved in both drawings**, not unreadable. |
| Ruilon / SMD5050-470NA | Formal resolution of X1=4.0 mm versus 0.165 in, preferably a corrected controlled drawing. Figure association and a complete metric-based implementation are resolved here; parent can explicitly select the metric design without claiming manufacturer correction or approval of the old 5.2 x 2 alternative. |
| JLCPCB / actual assembly | Ordinary-service part allocation, retained drill data, processed mask/stencil, fitting/lead-forming capability, real solder profile and workmanship. Standard untented fabrication does not require a 1 mm fill exception. Any required finished-via/barrel minimum beyond published standard guarantees remains a separate design/supplier decision, not implicitly approved special processing. |

## Verification Scope

Read AGENTS.md, all of REMEDIATION.md and ASSEMBLY.md; inspected the current BOM,
relevant local footprints and routing without editing them. Original figure
access and primary web evidence are identified above. The stated diagonals,
hole/position/ring budgets, body conversions and SMT clearances were checked
with a calculation-only `python3 -B -c` invocation using `math.hypot`; it did
not read/write project files or access the network. No KiCad checks or physical
tests were run, and no release hold is closed by this record.
`git diff --no-index --check /dev/null pcb/DFM_EVIDENCE.md` passed as a
documentation whitespace check, not a hardware gate.

On parent adoption, update the authoritative source/library/body and process
records consistently, preserve all guardrails, then regenerate and inspect
native artifacts with the integrated gates. This task does not authorize
approval-hash refreshes or modification of existing evidence.

## Direct Sources

Exact original URLs behind the linked source tables above:

[k128-page]: https://www.kefaelectronic.com/KF128-7-5-7-62-PCB-Terminal-Block-pd45490974.html
[k128-m]: https://jirorwxhqiillo5p.ldycdn.com/KF128-7.62-aidqiBpqKirRliSqmrqirloj.pdf
[k128-l]: https://datasheet.lcsc.com/datasheet/pdf/2bd9ccda2e0f72df8237e78ea70a6d85.pdf?productCode=C474957
[k129-page]: https://www.kefaelectronic.com/KF129-5-0-5-08-PCB-Terminal-Block-pd47789974.html
[k129-m]: https://irrorwxhqiillo5p.ldycdn.com/KF129-5.08-aidqiBpqKirRljSjorlrqlri.pdf
[k129-l]: https://datasheet.lcsc.com/datasheet/pdf/99269cbb2dd06cf5383cf1cad04f20f7.pdf?productCode=C475092
[vishay]: https://www.vishay.com/docs/28766/mbxsma.pdf
[vishay-pack]: https://www.vishay.com/docs/28721/packaginglinleadres.pdf
[bencent-page]: https://www.bencent.com.cn/index/proinfo/id/35029.html
[bencent-m]: https://www.bencent.com.cn/index/xiazai/name/_upfile_admin_file_20260514_2026051411072672523.pdf.html
[bencent-l]: https://datasheet.lcsc.com/datasheet/pdf/6471acbc3d87a8a4a9e5f7b8a245655d.pdf?productCode=C5337217
[ruilon-tht-l]: https://datasheet.lcsc.com/datasheet/pdf/d0869b141c45d22998b36dee1e5e4d4c.pdf?productCode=C2836978
[ruilon-tht-m]: https://www.ruilon.com.cn/Uploads/pdf/017-2rd-8%20series_a6.pdf
[ruilon-smt-l]: https://datasheet.lcsc.com/datasheet/pdf/ce8e2bf652ab9d180a3e88b2584bb613.pdf?productCode=C39692533
[ruilon-smt-m]: https://www.ruilon.com.cn/Uploads/pdf/06-smd5050%20series_a3.pdf
[ruilon-page4]: https://www.ruilon.com.cn/taociqitifangdianguan/list/40-4.html
[ruilon-page5]: https://www.ruilon.com.cn/taociqitifangdianguan/list/40-5.html
[jlc-via]: https://jlcpcb.com/help/article/pcb-via-covering
[jlc-holes]: https://jlcpcb.com/help/article/difference-and-tolerance-explanation-between-via-and-pad-holes
[jlc-pcb]: https://jlcpcb.com/capabilities/pcb-capabilities
[jlc-pcba]: https://jlcpcb.com/capabilities/pcb-assembly-capabilities
[jlc-stencil]: https://jlcpcb.com/help/article/smt-stencil-data-prepared-for-smt-orders
