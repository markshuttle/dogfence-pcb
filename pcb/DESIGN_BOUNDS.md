# Conditional Design Bounds

Hardware **1.2.0-dev**, analysis/evidence 2026-09-07. Owns only
`scripts/design_bounds.py`, `tests/test_design_bounds.py` and this note.
The existing solver, source, shared notes, build/staging and approval records
are unchanged by this work. Parent owns integration documentation. These are
calculations, not measurements, hardware qualification or closure of C4/C5/W3.

## Evidence And Inputs

- **User-confirmed reels:** `CM03/05.100`, labelled
  `3 CORE (3 x 35/0.30) TINNED BLACK 100 MTR`. Identity is settled, not measured
  conductor resistance. The user also confirmed **one LRS-75-36 for TEST and
  the second as a spare**, not interconnected supplies.
- **Resistance source:** IEC 60228:2004, edition 3, section 6.2 and Table 3,
  printed page 11, gives **8.21 ohm/km maximum at 20 C** for Class 5,
  metal-coated 2.5 mm^2 copper [1]. The plain-copper column is 7.98, not the
  tinned value. Section 2.1 explicitly includes tin in "metal-coated".
  Nexans reproduces the same values in its February 2021 table, page 3 [2].
- AMC's exact **2026 Update V.3** specifies Class 5 tinned conductors,
  **BS EN 60228:2005**, CM03/05 = 3 x 2.5 mm^2, and -30..70 C [3]. This
  supports using the standard maximum **conditionally**, without demanding an
  absent AMC numerical resistance column. BSI identifies the British edition
  as identical to EN 60228:2005 [4]; no claim is made that it is the latest edition.
- **Separate construction discrepancy:** Table 3 limits wires to **0.26 mm**;
  AMC's representative construction/reel label says **0.30 mm**. AMC permits
  representative strand configurations to differ. Do not call the label proof
  of complete Class 5 compliance or of measured resistance. Retain the 8.21
  conditional design ceiling while the construction declaration is reconciled.
- **Declared model envelope:** 41 stations at 100 m spacing; same-end A/C
  positive and B return; six independent ends, no new branch circuit. Source
  nominal 36 V; **35 V floor is a new explicit analysis requirement**, not a
  deduction from nominal. Proposed **37 V ceiling includes ripple and is NOT
  enforced**. The floor must include hub/interface/contact losses at the feeds.
  LRS adjustment up to 39.6 V and 41.4..48.6 V OVP do not enforce 37 V [5].
- **Cable/contact corner:** 70 C with the existing copper approximation
  `alpha = 0.00393/K`. Each core in **each 100 m span** is allowed 0.025 ohm of
  additional contacts/splices at service temperature: 1.00 ohm per 4 km core.
  This is a declared budget, not a WAGO specification or a measured result.
  It must bound the individual spans, not merely the whole-core sum. The script
  accepts separate A/B/C budgets and does not apply copper TCR to contacts.
- **R/Vf:** MBE04140C2201FC100 = 2200 ohm, +/-1%, +/-50 ppm/K [6]. The declared
  -30..125 C resistor range gives **2166.5655..2233.6655 ohm** relative to 20 C.
  Temperature is an input, not a calculated self-heating equilibrium. Aging,
  assembly drift and unbudgeted tap/harness losses are excluded. Total high Vf
  **4.4 V = 3.3 LED + 1.1 rectifier** is a brightness/headroom screen, not an
  exact SG full-temperature guarantee; all other loads may have **zero** Vf.

Sources were retrieved with native webfetch on 2026-09-07; PDF text was read
through `https://r.jina.ai/` prefixed to the exact source URL. This is text
extraction, not an archived original, unreadable-figure approval or vendor reply.

1. [IEC 60228:2004 public standard preview, including Table 3](https://cdn.standards.iteh.ai/samples/12024/921fee9a88c24612b68340a7330c2262/IEC-60228-2004.pdf), with [IEC edition metadata](https://webstore.iec.ch/en/publication/1065).
2. [Nexans IEC 60228 classification, February 2021](https://www.nexans.be/en/dam/jcr:efe5d9a2-f346-4047-87b4-99d1e319d768/IEC60228_ENG.pdf).
3. [AMC Tinned Copper 3 Core Cables, 2026 Update V.3](https://cdn.prod.website-files.com/62deaee72baf3ef3b83165ff/69fc985a23120ee62491a529_14%20-%20AMC%20Datasheet%20%20-%20Oceanflex%20Tinned%20Copper%203%20Core%20Cable%20(2026%20Update)%20V.3.pdf).
4. [BSI BS EN 60228:2005 metadata](https://knowledge.bsigroup.com/products/conductors-of-insulated-cables).
5. [Mean Well LRS-75 specification, 2025-04-07](https://www.meanwell.com/Upload/PDF/LRS-75/LRS-75-SPEC.PDF).
6. [Vishay 28766, MBE/SMA 0414, 11-Jul-2018](https://www.vishay.com/docs/28766/mbxsma.pdf), pp. 2-4/8/11: rating modes, ordering, TCR reference and derating.

## Normal Current

At 20 C the conditional conductor maximum is **32.84 ohm/core**, versus the
old nominal **27.60 ohm/core**. At 70 C it is **39.29306 ohm/core**, or
**40.29306 ohm/core** including the declared contact budgets.

| Case | Feed V | Far-end A LED mA | Source A |
| :--- | ---: | ---: | ---: |
| Old 6.9 ohm/km, 20 C, nominal 2.8 V Vf / 2200 ohm | 36 | 8.0448 | 0.847705 |
| Standard maximum, 20 C, no contacts, same nominal loads | 36 | 7.3003 | 0.804701 |
| Declared 70 C cable/contact corner, same nominal loads | 36 | 6.4107 | 0.752464 |
| Uniform high Vf / Rmax at every branch | 35 | 5.8796 | 0.686642 |
| Only A40 high Vf; all other Vf zero; Rmax everywhere | 35 | 4.8016 | 0.784529 |
| Only A40 high Vf / Rmax; all other Vf zero / Rmin | 35 | 4.6681 | 0.800350 |
| Previous case with the other positive rail C at zero ohms | 35 | 4.1843 | 0.857530 |
| Zero cable/contact R, zero Vf / Rmin everywhere | 37 | 17.0777 | 1.400373 |

Uniform Vf overstates A40 current by **1.0780 mA** even before the additional
**0.1335 mA** reduction from asymmetric resistor tolerance. Lower resistance
in C can increase shared B loading and further reduce A current. Mirrored
C40 cases are also calculated; they agree only for symmetric cable inputs.
The named corners are **not** an exhaustive joint-tolerance minimum.

For a conservative all-station floor without assuming equal source contacts
or uniform loads, two independent comparisons reuse the existing solver:
ground B and load the positive rail with Rmin/zero Vf at the **35 V floor**;
then hold A/C ideal at the **37 V ceiling** and load B with both Rmin/zero-Vf
channels. Actual positive potentials cannot be lower than the first comparison,
and actual B cannot exceed the second, within the stated healthy passive
envelope. Their worst differences occur at the far end. Subtract the declared
maximum Vf and divide by Rmax, clipped at zero. This intentionally loose floor
is **1.4946 mA**, reported separately from the much higher coupled-corner
currents; it is not a prediction of installed brightness. No daylight threshold
or guarantee follows.

The independent upper bound is **17.0777 mA/branch**, **1.400373 A / 51.813804 W**
for 82 branches, and **34.1554 mA at the local PCB B tap**. WAGO through-splices
carry distributed perimeter current, not just that tap current. One LRS-75-36
needs at least **68.54%** of its rated current/power capacity available for this
upper load, before auxiliary/interface losses. Actual input/thermal derating
still applies; its spare contributes no capacity.

## Thermal Requirements

Standard mode is **0.65 W at local ambient <=70 C**, derating linearly to zero
at **125 C maximum film** [6]. The 1 W power-mode rating is not substituted.

| Source-end condition | Branch mA | One resistor W | Two resistors W | Rating-only local ambient ceiling C |
| :--- | ---: | ---: | ---: | ---: |
| 36 V, nominal R / 2.8 V Vf | 15.0909 | 0.501018 | 1.002036 | 82.606 |
| 36 V, Rmin / zero Vf | 16.6162 | 0.598182 | 1.196364 | 74.385 |
| Proposed 37 V, Rmin / zero Vf | 17.0777 | 0.631876 | 1.263751 | 71.534 |
| Existing 40.39597 V adjustment/tolerance screen | 18.6452 | 0.753190 | 1.506379 | None |

At 37 V only **0.018124 W** remains below standard P70. Above-P70 operation
does not become acceptable by extrapolating the derating line below 70 C.
At 70 C, the zero-drop thermal source ceiling is **37.5269 V**; at 75 C it is
**35.7805 V**. The corresponding minimum nominal resistances at 37 V are
**2138.66 / 2352.52 ohm**, respectively, including the declared tolerance/TCR.
These are arithmetic envelopes, not approved substitutions. Fixed-current
thermal ceilings use **Rmax**, whereas voltage-fed worst power uses **Rmin**;
the two worst cases must not be combined as if they occurred simultaneously.

**Bulk/local interfaces:** an example target of **60 C** at controlled bulk and
local ambient interfaces leaves 10 K to the complete cable's 70 C limit. An
example **110 C film** target leaves 15 K to standard-mode film maximum.
Film, body, adjacent gel and cable-entry hot spots are different temperatures.
Measure or otherwise establish each with uncertainty; a cool bulk reading
does not establish safe cable or gel contact temperature near a hot resistor.
OneGel's conflicting service fields and missing thermal data remain as recorded
in ENVIRONMENT_EVIDENCE.md; adhesive, connector and LED limits also apply.

For the **two existing branches only**, assigning all their electrical input to
heat bounds it by **1.263751 W** at 37 V. At an illustrative 30 C outside / 60 C
bulk target, allowable **effective** bulk-to-outside resistance is at most
**23.7388 K/W**. At 60 C local ambient / 110 C film, the paired-load effective
film-to-local allowance is **79.1295 K/W per resistor**. These are required
heat-rejection capabilities, **not OneGel properties or self-heating claims**.
Add through-contact/auxiliary heat, mutual heating and solar exposure before
using the budget for a real enclosure. 30 C observed outdoor ambient is not a
guaranteed design maximum. No normal TEST timer substitutes for this envelope.

## Fault Screen

The existing solver supplies only selected AB/CB prospective CV examples,
with explicitly illustrative **0.25 ohm source series R** and **0.1 ohm arc
slope**. At 37 V / declared cable / zero-Vf Rmin loads, a near-source 100 ohm
fault dissipates **13.467593 W** with just **1.207124 A total**, below even the
healthy upper envelope. A hub overcurrent threshold is not complete coverage.
The near-source ideal short's 148 A is **invalid CV demand, not LRS current**.

K.12's known 135 V / 1300 ohm DC-feed comparison is retained from
SOURCE_PROTECTION_RESEARCH.md, sections 2/9 [N1,N2]. Ignoring the test diode
drop gives **103.846 / 96.154 / 92.308 mA** at **0 / 10 / 15 V**. The old
nominal far 10 V arc remains **0.259543 A / 2.602168 W**. Ratios in the new CLI
use the actual modeled terminal voltage, including arc slope, not just its
10 V knee. A simple 37 V source would need at least **356.2963 ohm** for this
sufficient pointwise DC-feed dominance, not an acceptable rail-resistor design.
This does not prove dynamic extinction or non-extinction; K.12 also has surge/
RC conditions and does not qualify this powered fence by voltage comparison.
The **0.256 W** bound for a <=0.1 ohm failed-short path requires an **actually
enforced 1.6 A** ceiling and does not cover resistive damage or external energy.

## Reproduction

```bash
python3 -B scripts/design_bounds.py
python3 -B scripts/design_bounds.py --json
python3 -B -W error -m unittest discover -s tests -p test_design_bounds.py -v
python3 -B -W error -m unittest discover -s tests -p test_electrical.py -v
```

CLI output is deterministic and offline, with explicit units and no file writes.
Focused tests reuse `analyze_limits.cut_sweep` for all **280 cuts** at an
asymmetric corner; no second network solver or cut implementation is introduced.
On **Python 3.14.4**, the focused bounds suite passed **11 tests**, and the
unchanged electrical suite passed **21 tests**. Human and JSON CLIs exited 0.
The bounds suite includes direct-file CLI execution, JSON determinism, invalid/
nonfinite/overflow inputs, independent current comparisons, thermal boundary
conditions and the reused cut sweep. `git diff --no-index --check /dev/null`
passed separately for each of the three owned files. These checks verify the
declared analysis, not any proposed source interface or physical temperature.
No `make check`, manufacturing/staging operation, approval refresh, commit,
order or physical test is part of this work.
