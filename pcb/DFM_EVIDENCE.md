# DFM Evidence

Research date: **2026-09-07**. Original DFM baseline: **97e202d**; SMT-resistor
review: **02661d8**, followed by the manufacturer-land correction retained below.
**PS12 replacement review: 2026-09-08**, with no geometry change.
Hardware **1.2.0-dev**. Scope: P3/P4 board design and five assembled prototypes.

Dimensions are millimetres unless explicitly marked inches. Global coordinates
use the top-view board convention from ASSEMBLY.md; local coordinates are
identified separately below.

**Current selection:** the user authorizes **Uni-Royal/Royalohm
PS122WF2201T4E / C2793873** for R1/R2 in **both prototype and production**,
2.2 kohm, 2 W, 1%, 2512 SMT. Exact identity and the normal LCSC route are resolved;
the user reports **110 ORDERED into their JLCPCB parts library**, not receipt,
inspection or board-job allocation. Independent PS manufacturer review supports
retaining **1.35 x 3.70 rectangular lands at local X=+/-3.125**, maximum-body
F.Fab **6.45 x 3.40** and courtyard **8.10 x 4.20**. All coordinates, tracks,
courtyards and net/artifact counts remain unchanged; no resistor holes or axial
standoff/forming apply. The HP investigation is [historical](#hp12-investigation-history),
as is prior PR02 forming/sourcing in [ASSEMBLY](ASSEMBLY.md#axial-resistor-history).

D1-D4 remain BYG23T-M3/TR SMA, with D1/D2 moved for straight cathode links as
recorded below. The earlier visual review of Vishay **89429, 25-Feb-2020 p4**
supports the retained **2.50 x 2.00 lands, 1.70 inner gap and 7.20 x 3.60
courtyard**: 1.52/1.68 land minima and 1.88 maximum inner gap were resolved;
5.28 outside span is reference, not a maximum. Kefa/GDT fit envelopes, the metric
Ruilon land selection and all protected copper/vias remain unchanged.

**Evidence and selected design requirements, not supplier approval.** Expected
inventory is **16 parts: eight SMT/eight THT**, eight nets, **34 terminals,
32 PTH hits (18 component +14 via), four NPTH, 52 IPC records, F.Mask 52,
B.Mask 36 and F.Paste 16 apertures**. These are design counts, not a fresh native
verification of the PS12 substitution. The parent owns source/library/BOM/checker
integration and revision-specific verification; [ASSEMBLY.md](ASSEMBLY.md)
controls the physical handoff. Historical diameter-only screens below are
identified separately from the retained current THT design.

For the explicit prototype scope, **`make gerbers` / `make prototype` publish
only after strict file and sourcing checks**. C4/C5/W3/W1/W4 remain visible,
deferred production holds, not closed issues; switch/environmental research or
completed qualification is not required to generate prototype artifacts.
The resolved PS12 identity does not waive any source/sourcing check or establish
publication; the parent must verify integration and actual exports. `make all`,
`make package`, `make release`, `make production` and the other export aliases
retain the holds.
Filenames stay the same: require matching source/artifact hashes and manifest
**status=prototype, mode=prototype**, distinct from production
**status=verified, mode=build**. The generated README markers inside the ZIPs
identify prototype scope and deferred holds. See
[artifact controls](ASSEMBLY.md#prototype-artifacts).
Actual board-order authorization still requires supplier part/process/placement/CAM
acceptance. No email response, allocation or physical test is invented here.

## PS12 SMT Selection

The bounded **2026-09-08** review used the actual **PS Series** document from
**Uniroyal Electronics Global Co., Ltd.**, not the HP datasheet. The cover and
printed footers identify **SMD-SP-007, V.7, 08-Jan-2026**, eleven pages; the
July-2026 upload date is not a drawing revision.

| Source | Readable evidence / limitation |
| :--- | :--- |
| [Original manufacturer PS PDF][ps-pdf] | **V:** pages **1, 2, 4, 5, 6, 7 and 8**: cover, ordering, body/land leaders, ratings/derating, one-pulse curves, TCR/overload and reflow. Public Google PDF-viewer page images were visually read; text extraction was supplementary, not dimensional proof. |
| [Manufacturer PS12 product page][ps-page] | PS12, 2 W, 0.5%/1%/5% options, 0.1 ohm..10 Mohm, **+/-100 ppm/C**, consistent with the PS PDF. Links the PS specification, not HP. |
| [JLCPCB C2793873][ps-jlc] and [LCSC C2793873][ps-lcsc] | Both identify **PS122WF2201T4E, 2.2 kohm, 2 W, 1%, +/-100 ppm/C, 2512**, with a 500-V family label. Public identity is not receipt, inspected lot or board-job allocation. |
| [Stable LCSC datasheet entry][ps-distributed] | Resolves to [this PDF target][ps-target]; attempted retrievals did not yield usable drawing pages. No distributor-PDF revision is established here; the manufacturer PS PDF controls the drawing review. |

Page 2 decodes **PS12 / 2W / F / 2201 / T4 / E** as PS12, 2 W, 1%, 2200 ohm,
tape/reel with a standard 4,000-piece reel, standard feature. It does not require
a full-reel purchase for five prototypes or contradict the reported 110-piece order.

Use **`MPN=PS122WF2201T4E`**, **`LCSC Part #=C2793873`**, **`Sourcing=LCSC`**,
an empty **`Sourcing Reference`**, and [the PS manufacturer PDF][ps-pdf] as
**`Datasheet`**. No NAC external-source row or pending HP code applies to PS.
The reported **110 ORDERED** are not verified received/inspected or allocated.
Five prototypes need **ten fitted resistors plus supplier-defined attrition**;
[ASSEMBLY](ASSEMBLY.md#ps12-smt-resistors) separates those requirements from the
41-station quantity and unassigned order balance. Integration/publication remains
the parent's verification task, not an outcome of this research.

### Body And Lands

PS page 4's body drawing gives **L=6.35 +/-0.10, W=3.20 +/-0.20 and H=0.55 +/-0.10**,
therefore maxima **6.45 x 3.40 x 0.65 mm**. Its top termination length A is
0.60 +/-0.25 and bottom termination length B is 0.50 +/-0.20. Those letters are
body-drawing dimensions, not the separate land-pattern letters on page 5.

PS page 5's original leaders independently identify:

| Land drawing field | Meaning | Manufacturer recommendation, mm |
| :--- | :--- | ---: |
| A | Inner gap between lands | **4.90 +/-0.10** |
| B | One land's longitudinal length | **1.35 +/-0.10** |
| C | Transverse land width | **3.70 +/-0.10** |
| D | Outside span | **7.60 +/-0.10** |

Retain these nominal values as **rectangular, undrilled F.Cu/F.Mask/F.Paste
lands**, with **zero effective mask margin, paste margin and paste ratio**.
They match the current HP-derived geometry exactly; no PS land deviation is
needed. `D = A + 2B` keeps the dimensional choices consistent. The zero margins
are the project's aperture choice, not a manufacturer stencil specification.
Centre pitch is `4.90 + 1.35 = 6.25`, hence local X=**-3.125/+3.125** for
pad 1/pad 2. Each nominal land has **4.995 mm^2** area. Customer F.Paste remains
a source datum, not approval of the assembler's processed aperture or deposit.

The maximum-body F.Fab is **X=+/-3.225, Y=+/-1.70**. The selected courtyard is
**X=+/-4.05, Y=+/-2.10**: lands plus 0.25 per side need **8.10 x 4.20**;
maximum body plus 0.10 projected pose and 0.25 assembly clearance needs
**7.15 x 4.10**, which fits inside it. Body height 0.65 excludes solder seating
height. The chip is not assigned the retired resistor's axial body standoff.

### Placement And Routing

| References | Origin / rotation | Pad 1 / pad 2 global X and nets |
| :--- | :--- | :--- |
| R1 | **(120.00,104.50), 0 deg** | **116.875 WIRE_A / 123.125 Net-(D1-A)**, both Y=104.50 |
| R2 | **(120.00,140.50), 0 deg** | **116.875 WIRE_C / 123.125 Net-(D2-A)**, both Y=140.50 |
| D1, D2 | **(130.80,104.50)/(130.80,140.50), 0 deg** | K1 **132.90 LED_A_POS/LED_C_POS**; A2 **128.70 resistor output** |
| D3, D4 | **(135.00,99.00)/(135.00,146.00), 180 deg** | K1 **132.90 LED_A_POS/LED_C_POS**; A2 **137.10 WIRE_B** |

R1/R2 remain nonpolar; preserve pad numbering and one-way branch order through
D1/D2. The cathode links at **X=132.90** run Y=99.00..104.50 and 140.50..146.00:
each **5.50 mm long and 1.80 mm wide on F.Cu**, with no dogleg. Preserve the
**X=108.38 takeoffs**, **1.80-mm branch copper**, **0.80-mm shunt anode-to-B
routes**, **1.60-mm protected B.Cu returns**, full 3.20-mm rails, fourteen
1.00/1.80-mm vias and the solid isolated EARTH bus. The LED terminals and all
GDT/Kefa geometry remain unchanged. No folded branch or added via is selected.

### Rating And Process

- **PS TCR basis, p7:** +/-100 ppm/C, with reference temperature **25 C or
  specified room temperature** and test temperatures **-55/125 C**. The PS web
  page agrees. These inputs match the existing resistance screen; do not extend
  it to the separate 155 C operating endpoint or borrow PR02's 250 ppm/K model.
- **Power/voltage:** 2 W through 70 C ambient, linear derating to zero at 155 C.
  PS pp4/5 specify **500 V maximum working / 1000 V maximum overload / 500 V
  dielectric withstand**, operating range -55..155 C. The working limit is also
  constrained by `RCWV = sqrt(P*R)`, still **66.33 V** for nominal 2.2 kohm at
  2 W. Page 7's five-second overload test uses the lower of `2.5*RCWV` and
  1000 V, still **165.83 V**, with +/-(1% +0.1 ohm) resistance-change limit
  for the 1% part. The family voltage labels are not allowable continuous
  voltages for every resistance value.
- **One-pulse limits, p6:** PS supplies separate **power-versus-duration and
  voltage-versus-duration curves**; both constrain use. No curve digitization,
  repetitive-pulse rating or assembled-board/transient qualification is claimed.
  The HP review's absence of established pulse curves is not a PS fact.
- **Heat path:** nominal dissipation remains about **0.50 W per resistor**, not
  less because the part family changed. Chip terminations and solder conduct into
  local copper/FR-4; the 1.80-mm tracks do not establish thermal resistance or
  lower chip temperature. The wider cathode links are separated from resistor
  output copper by D1/D2. **PR02's hot-spot limit and 75 K/W mounting example do
  not apply.** No heat reduction or completed continuous-duty test is promised.
- **Reflow:** visually read p8 recommends SAC305, 150..200 C preheat for
  60..120 s, <=3 C/s ramp-up, 217 C liquidus for 60..150 s, **260 C peak**,
  10 s within 5 C below peak, <=6 C/s ramp-down, <=8 minutes from 25 C to peak
  and **two reflow cycles**. The manufacturer explicitly calls for application
  adjustment. Actual mixed-assembly/stencil acceptance remains a supplier fact,
  not permission to apply the most permissive GDT heat-test limit to every part.

These limits inform part selection and the assembly handoff. They do not add
switch/environmental or completed performance qualification as prerequisites for
prototype artifacts; the independent production holds remain deferred, not closed.

## HP12 Investigation History

**Historical 2026-09-07 review of 02661d8, not PS research or current sourcing
instructions.** The then-intended HP122WF2201T4E remained without a verified
JLCPCB/LCSC code. Its manufacturer document was **SMD-SP-003, HP Series, V.7,
08-Jan-2026**, from Uniroyal Electronics Global Co., Ltd., carrying Uni-Royal,
Royalohm and Uniohm branding; the July upload date was not its revision date.

| Historical source | Evidence retained / limitation |
| :--- | :--- |
| [Original manufacturer HP PDF][hp-pdf] | **V:** pages **1, 2, 4, 5, 6 and 8**, including cover, ordering, body/land leaders, ratings/derating, TCR/overload and reflow. **T:** full eleven-page text through [the reader][hp-text]. No dimensions were inferred from an unreadable figure. |
| [Manufacturer HP product listing][hp-page] | HP12, 2 W, 0.5%/1%/5% options. The applicable range was listed at **+/-75 ppm/C**, conflicting with the PDF's **+/-100 ppm/C**. The tighter figure was not adopted. This conflict does not transfer to PS. |
| [LCSC C2791283][hp-wrong-lcsc] and [JLCPCB C2791283][hp-wrong-jlc] | Both identify **HP122WJ0472T4E, 4.7 kohm, 5%, 2 W, 2512**, not HP122WF2201T4E and not selected PS122WF2201T4E. The old mapping was rejected; internal metadata parity could not cure that identity mismatch. |
| [NAC Semi former intended-MPN listing][hp-nac] | Readable **ROYALOHM HP122WF2201T4E, 2512, 2.2 kohm, 1%, 2 W**; retrieved MOQ **3,600**. Former external BOM/source reference, not an accepted small-lot quote, JLCPCB code or allocation. Public stock was indicative only. |

The [HP-associated LCSC PDF][hp-distributed] did not yield usable drawing pages;
no revision or dimensional proof was assigned to it. TME returned HTTP 403 and
Mouser an access-denied page. Exact/prefix searches did not establish an HP code
or packaging-only alternative: the [JLCPCB exact search][hp-search-jlc] and
[known-listed HP122WJ0472T4E control][hp-control-jlc] both returned
JavaScript-dependent zero-result pages; [LCSC search][hp-search-lcsc] returned
`Search by ""` without rows. These were retrieval limitations, not proof of HP
unavailability. No HP supplier response, purchase or board-job allocation was
established by that investigation; none is implied by the later PS order report.

HP p2 decoded **HP12 / 2W / F / 2201 / T4 / E** as 2 W, 1%, 2.2 kohm,
tape/reel with a standard 4,000-piece reel and standard feature, not a requirement
to purchase a full reel. HP's recorded family working/overload limits were
**300/500 V**, with 500 V dielectric withstand and a five-second overload test;
no one-pulse curve was established in that HP review. PS limits above supersede
these as operative part evidence, not by relabelling the old investigation.

**Historical land correction, not approved alternate geometry:** 02661d8 used
1.80 x 3.40 roundrect lands at +/-2.80, 3.80 inner gap and 7.40 outside span,
with 6.30 x 3.20 F.Fab and 7.90 x 3.90 courtyard. Its F.Fab did not bound the
HP12 maximum body; the courtyard was 0.10 short per transverse side under the
stated pose/assembly budget. No neighbour collision was demonstrated. The prior
manufacturer-land correction replaced that deviation; PS independently supports
retaining the corrected geometry. Internal/native consistency was not land-pattern
approval.

## Conclusions

- **PS12 replacement:** exact C2793873 identity is resolved and original PS body
  and land leaders match the retained geometry. All coordinates, tracks, nets
  and counts stay unchanged; the reported 110-piece order is not receipt,
  inspection or board-job allocation. No publication or hardware PASS is claimed.
- Original mechanical figures for **all six requested part families were
  visually read**, including the Kefa tolerance tables and both Ruilon THT
  revisions. Their dimensional associations are no longer a text-reader hold.
- Ruilon **2R470TD-8** has a drawing lead maximum of **1.05 mm**. Its former
  97e202d 1.20 mm hole left only `1.20 - 0.08 - 1.05 = 0.07 mm`, below the
  required 0.10 mm allowance; the retained selected hole is **1.50 mm**. Its
  metric maximum body is **6.30 long x 8.20 diameter**.
- Kefa **KF128-7.62-3P** pins are rectangular, nominal **0.90 x 0.80**.
  **KF129-5.08-2P** has a real source conflict: **0.90 x 0.80** in the
  C475092-distributed drawing versus **0.95 x 0.80** in the manufacturer-linked
  drawing, both marked **A / 21.03.13**. The former 97e202d 1.40/1.30 holes were
  not a tolerance-supported solution; both retained selections use **2.00 mm**.
  In particular, the old KF129 hole failed the project allowance even using the
  smaller nominal pin, before adding pin tolerances.
- The retired Vishay MBE explicitly labels its **0.80 mm lead as nominal**.
  Bencent's original figure labels a **0.80 mm round lead without a tolerance**.
  Neither figure supplies a manufacturer-guaranteed finished lead maximum. A controlled
  **0.90 mm finished acceptance envelope** was proposed for each; it remains
  operative only for **B5G470L**, now with 1.40 mm holes. R1/R2 are SMT.
- Ruilon **SMD5050-470NA**: **X1 is pad centre-to-centre spacing**, not the inner
  gap or outside span. The metric recommendation translates to **5.50 x 1.20 mm
  lands at local Y = +/-2.00** in this board's orientation. The 4.0 mm / 0.165 in
  conflict exists in the original manufacturer PDF too. Use of the metric column
  is an explicit selected engineering choice, not a claimed manufacturer erratum.
- **Standard untented ENIG vias** are a supported alternative to unsupported
  1.00 mm filling/tenting assumptions. Preserve every 1.00/1.80 via and all
  protected copper. No special fill, press-fit tolerance or CAM exception is
  proposed as the solution.

## Figure Access

In the original DFM research, direct PDF requests with native `webfetch` returned
PDF streams rather than rendered pages. That was not treated as evidence that the figures were
unreadable. The original public URLs were then opened through Google's public
PDF viewer, and its page-image endpoints were fetched with native `webfetch`.
The returned image attachments, including dimension arrows and title blocks,
were visually inspected. No terminal network fetch or download script was used.
Existing `tmp/dfm-review/` and `tmp/layout-review/` directory listings were also
inspected without changing their evidence; they did not provide the requested
component drawings in the inspected listings.

The later PS12 review used the same public-viewer method for its own original
PS PDF, independently of those historical THT/GDT/HP retrievals.

Repeatable access method, not an alternative drawing authority:

1. Fetch `https://docs.google.com/gview?embedded=1&url=<URL-encoded-original-URL>`
   as HTML. Some initial requests returned an empty response; retrying succeeded.
2. Use the returned `img?id=...` URL under `https://docs.google.com/viewerng/`,
   with `&page=N-1&w=2400` for printed page N. `page` is zero-based;
   `pagenumber` did not select the requested page in this viewer.
3. Check the actual printed page number, MPN/family, revision and dimension
   leaders. Viewer IDs are temporary, so the permanent evidence links below
   identify the original files, not expiring image tokens.

**V** means original figure visually read; **T** means retrieved text.
**Derived** means arithmetic from published dimensions. **E** means a controlled
procurement/assembly envelope, **not a manufacturer guarantee**.
Original PDFs/images were not added to the workspace in this bounded task.

| Retained or explicitly historical identity | Original source and revision | Access actually used |
| :--- | :--- | :--- |
| Cixi Kefa KF128-7.62-3P / C474957 | [Manufacturer drawing][k128-m] and [C474957 drawing][k128-l], title KF128-7.62, revision A, 21.03.13, one sheet. Manufacturer [product page][k128-page] links the 7.62 drawing separately from 7.5. | V: both sheets, pin leaders, PCB layout and general tolerance table. P=3 applied to the family drawing. |
| Cixi Kefa KF129-5.08-2P / C475092 | [Manufacturer drawing][k129-m] and [C475092 drawing][k129-l], title KF129-5.08, revision A, 21.03.13, one sheet. [Product page][k129-page] identifies the 5.08 drawing. | V: both sheets. Different 0.95/0.90 pin-width labels despite identical revision/date; not silently reconciled. P=2. |
| **Historical, retired:** Vishay MBE04140C2201FC100 / C1368610 | [Document 28766][vishay], revision 11-Jul-2018, p13 dimensions; p4 ordering and p7 construction/assembly. [Document 28721][vishay-pack], revision 16-Jan-2025, packaging. | V: 28766 p13. T: ordering, tin-plated copper construction and packaging. Packaging did not establish a missing lead-diameter maximum. Not a current procurement/forming requirement. |
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
| **Historical, retired:** Vishay MBE04140C2201FC100 | p13's `d_nom = 0.80` is the round wire diameter. `D_max = 4.20` is body diameter; `L_max = 11.90` body length; `l_min = 31.0` each unformed lead; `M_min = 15.0` mounting pitch. | Former **E <=0.90 diameter**, including tin finish, roundness and forming distortion, was a nominal +0.10 design limit, not a Vishay guarantee. No current R1/R2 insertion or forming task. |
| Bencent B5G470L | p2 lead is explicitly round, diameter **0.80**, with no +/- or maximum qualifier. A=62 +/-2 is unformed overall length; B=6 +/-0.20 is body length; C=diameter 5.50 +/-0.20 is body diameter including the end-electrode outline. Copper leads, matte-tin finish are stated. | **E <=0.90 diameter**, for the stated procurement rationale. A/B/C tolerances do not create a tolerance on the separate 0.80 lead callout. Former 1.20 holes passed diameter-only against this E, but not the complete fixed-pattern budget below; selected holes remain **1.40**. |
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
The first table is the **historical 97e202d diameter-only screen**, not the
current hole schedule. The adopted Kefa/GDT position budget follows it; current
R1/R2 have no holes.

```text
H_min = H_nom - 0.08
D_pin = finished round diameter, or sqrt(W_max^2 + T_max^2)
Diameter-only requirement: H_min >= D_pin + 0.10
Nominal ring = (minimum pad width - H_nom) / 2 >= 0.254
```

| Part family | 97e202d hole | H_min minus design pin envelope | Diameter-only minimum on a 0.10 mm hole grid |
| :--- | ---: | ---: | ---: |
| KF128, E diagonal 1.486607 | 1.40 | -0.166607 | 1.70 |
| KF129, E diagonal 1.523975 | 1.30 | -0.303975 | 1.80 |
| MBE0414, E diameter 0.90 | 1.00 | 0.020000 | 1.10 |
| B5G470L, E diameter 0.90 | 1.20 | 0.220000 | 1.10 |
| 2R470TD-8, diameter 1.05 | 1.20 | 0.070000 | 1.30 |

The first two negative results are against the **proposed conservative E**,
not a claim that every nominal connector fails to enter the old board.
Nominal KF128 diagonal is 1.204159, leaving 0.115841 in that former worst hole,
only 0.015841 beyond the required allowance before any pin tolerance. KF129's
smaller nominal diagonal is also 1.204159, leaving **0.015841 total** in its
1.22 worst hole; the larger nominal diagonal is 1.241974 and exceeds that hole.

### Independent Position Budget

The last column above is **not** a complete insertion recommendation. A 0.10
diametral assembly allowance cannot also pay for arbitrary pitch error.
JLCPCB publishes hole position tolerance +/-0.05. Conservatively treating that
as +/-0.05 on each board axis gives radial `e_h = sqrt(2)*0.05 = 0.070711`.

The retained selected Kefa/GDT ordinary-process geometry follows, with a
**separately controlled part-pattern limit `e_p <=0.050 mm radial` per pin**.
This limit applies after one common rigid alignment of the complete pin pattern
to the nominal footprint, through the full insertion length. It includes
non-collinearity, lean and forming errors, not just adjacent pitch. It is an
incoming/formed-part inspection condition, **not a Kefa/GDT guarantee**.

```text
Additional diametral position budget = 2*(e_h + e_p) = 0.241421
Require H_nom - 0.08 - D_pin - 0.241421 >= 0.10
```

| References | Selected hole / retained pad size | Diameter-only clearance | Clearance after separate position budget | Nominal ring |
| :--- | :--- | ---: | ---: | ---: |
| J_IN, J_EARTH | **2.00 / 3.20** | 0.433393 | 0.191972 | 0.60 |
| J_LED_A, J_LED_C | **2.00 / 2.80** | 0.396025 | 0.154604 | 0.40 |
| GDT_AC | **1.40 / 2.80** | 0.420000 | 0.178579 | 0.70 |
| GDT_A_E, GDT_B_E, GDT_C_E | **1.50 / 3.00** | 0.370000 | 0.128579 | 0.75 |

This is the conservative **bounded retained THT design**, not a
requirement to enlarge every hole this much regardless of actual part evidence.
It deliberately trades more solder volume and fixture dependence for insertion
margin without requiring tighter JLCPCB fabrication tolerances. The retained
Kefa/GDT pad shapes, centres, nets and copper dimensions remain unchanged. The
minimum ring is 0.40, above 0.254. Nominal rings are not guarantees of finished
registration, etch tolerance, solder fill or barrel copper.

Smaller holes are supportable only with an independently demonstrated combined
alignment bound `e_h + e_p <= (H_nom - 0.08 - D_pin - 0.10)/2`, or an accepted
forming process that fits the measured actual board pattern. Do not claim that
1.70/1.80 connector holes accommodate the broad general pitch bands on the
Kefa drawings. Conversely, screening an ordinary lot to the explicit E/pattern
limits is a legitimate alternative to waiting for a new manufacturer guarantee;
do not claim the screen has already passed or that its yield is known.

For the retained 15.24-pitch axial GDTs, the radial part-pattern bound limits
two-pin spacing error to at most 0.10. Inspect the actual formed pattern and
overpass height after seating; larger holes must not permit collapse or tilt.
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

Selected assembly control: the actual projected body must remain inside its
listed body box expanded by **0.10 on each side**, including translation and
tilt. This is an inspected projection bound, not permission to add arbitrary
rotation on top of the allowance. Courtyards contain that projection plus at
least 0.25 assembly margin, and existing pads plus 0.25 where pads dominate.

| Footprint family | Selected F.Fab body/envelope box: X; Y | Selected F.CrtYd box: X; Y |
| :--- | :--- | :--- |
| KF128 Input and Earth | **-6.00..5.40; -12.50..12.50** (E) | **-6.35..5.75; -12.85..12.85** |
| KF129 LED A and C | **-5.10..6.40; -6.10..6.10** (E) | **-5.45..6.75; -6.45..6.45** |
| PS12 SMT resistor | **-3.225..3.225; -1.70..1.70** | **-4.05..4.05; -2.10..2.10** |
| B5G470L north-south overpass | **-2.86..2.86; -3.10..3.10** | **-3.25..3.25; -9.30..9.30** |
| 2R470TD-8 east-west | **-3.15..3.15; -4.105..4.105** | **-9.40..9.40; -4.46..4.46** |
| SMD5050-470NA north-south electrode axis | **-2.605..2.605; -2.25..2.25** | **-3.00..3.00; -3.75..3.75**, retained |

These selections do not conceal interference by shrinking courtyards. The
Ruilon SMT-GDT body's shorter Y follows its resolved axial C dimension; its
courtyard Y is deliberately retained. The PS12 maximum body and lands match
the existing explicit envelope. Preserve protected vias, rails, earth copper,
mounts and LEDs; native file verification and actual assembly acceptance remain
different checks.

Retained GDT/Kefa checkpoint-placement calculations, **not a new DRC run**:

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
correction in the retrieved exact-MPN source. **The printed metric 4.00 mm
spacing is explicitly selected**, not an inferred manufacturer erratum. The
duplicated 0.165 also appears as the correct rounded inch value for C=4.2 in the
same table, which is consistent with a copied conversion error, but does not prove
the manufacturer's intended correction. Do not average the numbers, silently
choose a 4.2 pitch, call X1 a gap, or claim written approval.

Retained selected footprint geometry, preserving pad numbers and nonpolar part
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
These are supplier/order and physical-acceptance controls, not additional
qualification prerequisites for prototype artifact generation. Later enclosure,
thermal and protection activities stay separate from the board file workflow.

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
   GDTs are inspected after forming; R1/R2 are undrilled SMT. A tight
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
| Uni-Royal/Royalohm / PS122WF2201T4E / C2793873 | Receipt, applicable lot/revision and board-job allocation for ten fitted prototype parts plus attrition; actual stencil/reflow/placement acceptance. Exact C-code and normal LCSC route are **resolved**; 110 ORDERED is user-reported, not receipt/inspection/allocation. PS body/land leaders **have been visually read** and match existing geometry; PDF/web TCR agree. No HP code search, resistor hole or axial forming response is needed. |
| Bencent / B5G470L | Finished 0.80-wire tolerance and allowable forming/seal-support geometry. Public p2 really contains a round 0.80 callout without its tolerance. A2 body limits are resolved; the current manufacturer download did not supply a newer toleranced lead drawing. Control <=0.90 and accept the actual formed part against the selected envelope. |
| Ruilon / 2R470TD-8 | Exact revision/production code allocated; allowed bend radius/seal setback, post-forming lead condition and ordinary nickel-lead solder process. The 1.05 lead maximum and 6.30/8.20 metric body maxima are **resolved in both drawings**, not unreadable. |
| Ruilon / SMD5050-470NA | Formal resolution of X1=4.0 mm versus 0.165 in, preferably a corrected controlled drawing. Figure association and the selected metric-based implementation are resolved here, without claiming manufacturer correction or approval of the old 5.2 x 2 alternative. |
| JLCPCB / actual assembly | Ordinary-service part allocation, retained drill data, processed mask/stencil, fitting/lead-forming capability, real solder profile and workmanship. Standard untented fabrication does not require a 1 mm fill exception. Any required finished-via/barrel minimum beyond published standard guarantees remains a separate design/supplier decision, not implicitly approved special processing. |

## Verification Scope

**Original 97e202d research record:** read AGENTS.md, all of REMEDIATION.md and
ASSEMBLY.md; inspected the then-current BOM, relevant local footprints and
routing without editing them. Original figure access and primary web evidence
are identified above. The stated diagonals,
hole/position/ring budgets, body conversions and SMT clearances were checked
with a calculation-only `python3 -B -c` invocation using `math.hypot`; it did
not read/write project files or access the network. No KiCad checks or physical
tests were run, and no release hold is closed by this record.
`git diff --no-index --check /dev/null pcb/DFM_EVIDENCE.md` passed as a
documentation whitespace check, not a hardware gate.

**02661d8 read-only review:** the source geometry check and 60 geometry tests
passed; retained native XML/IPC/CPL/BOM/Gerber/drill data matched the reviewed
PCB/schematic hashes, and the retained assembly PDF was inspected. Those results
described the former roundrect resistor lands, **not a validation of the selected
rectangular correction**. The manufacturer/body and C-code findings above were
not disproved by internal file consistency. In-memory probes also showed missing
resistor angle/aperture guards and a body/courtyard test that no longer iterated
R1/R2; the parent owns the checker/test corrections.

**2026-09-08 PS documentation integration edits only ASSEMBLY.md and DFM_EVIDENCE.md.**
The parent owns CAD/libraries/BOM/sourcing metadata, diagnostic review, checker
changes and integrated verification. No shared Make/native workflow, source
synchronization, supplier request, upload, order, commit or physical test is run
by this documentation task. Publish only source-matched artifacts under the
explicit prototype/production distinction; do not refresh approval hashes or
claim supplier/performance acceptance from this evidence record.

## Direct Sources

Exact original URLs behind the linked source tables above:

[ps-pdf]: https://www.uni-royal.cn/en/images/userfile/file/1784854235b7c79f8d8a205c5d.pdf
[ps-page]: https://www.uni-royal.cn/en/article.php?id=10109
[ps-jlc]: https://jlcpcb.com/partdetail/C2793873
[ps-lcsc]: https://www.lcsc.com/product-detail/C2793873.html
[ps-distributed]: https://www.lcsc.com/datasheet/C2793873.pdf
[ps-target]: https://datasheet.lcsc.com/datasheet/pdf/72ec9a363d94a6fd0729e3976f9248d5.pdf?productCode=C2793873
[hp-pdf]: https://www.uni-royal.cn/en/images/userfile/file/1784806233a2e6d381ea80b5d9.pdf
[hp-text]: https://r.jina.ai/https://www.uni-royal.cn/en/images/userfile/file/1784806233a2e6d381ea80b5d9.pdf
[hp-page]: https://www.uni-royal.cn/en/product.php?s=High-Power+Thick+Film+Chip+Res
[hp-wrong-lcsc]: https://www.lcsc.com/product-detail/C2791283.html
[hp-wrong-jlc]: https://jlcpcb.com/partdetail/UniRoyalElec-HP122WJ0472T4E/C2791283
[hp-nac]: https://store.nacsemi.com/products/detail?stock=XSJMZ0000010410
[hp-distributed]: https://datasheet.lcsc.com/datasheet/pdf/72ec9a363d94a6fd0729e3976f9248d5.pdf?productCode=C2791283
[hp-search-jlc]: https://jlcpcb.com/parts/componentSearch?searchTxt=HP122WF2201T4E
[hp-control-jlc]: https://jlcpcb.com/parts/componentSearch?searchTxt=HP122WJ0472T4E
[hp-search-lcsc]: https://www.lcsc.com/search?q=HP122WF2201T4E
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
