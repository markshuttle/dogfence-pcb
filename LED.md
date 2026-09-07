# External LED Indicators

**Selected procurement baseline: APEM Q10F5SXXSG02E. Draft system revision 1.2.0-dev; qualification remains open.**

## Selected Part

The purchased Q10 indicator is the **no-internal-resistor** option, selected to use the PCB's external 2.2 kohm branch resistor rather than an additional internal voltage-rated lamp resistor. The `02` option is **not a regulated 2 V supply input**, nor does the part draw a fixed 20 mA. Forward voltage and current depend on the actual LED, resistor, cable drop, temperature and supply.

| Item | Baseline / limitation |
| :--- | :--- |
| Identity | **APEM Q10F5SXXSG02E**, green, nominal 10 mm panel mounting, flying leads. Verify the supplied label and exact drawing. |
| Current | Published family **20 mA maximum**, not a required or guaranteed operating current. Bound near-source current and pulse current with the final protection circuit. |
| Reverse voltage | **5 V maximum**. A series 1N4007G is not proof this limit is respected. |
| Temperature / ingress | Published Q10 data includes -40 to +85 degrees C and IP67 under specified mounting/sealing conditions. These component conditions are not ratings for the modified WISKA box, cable or complete assembly. |
| Mounting | Use the actual panel cutout, seal and panel-thickness instructions. Published mounting torque is **0.20-0.25 Nm**, subject to the exact supplied model instructions. |
| Procurement | **80 ORDERED**, unchanged from the purchase record. **41 stations need 82**, leaving a **shortfall of 2 before separate prototype use, losses or spares**. See [MATERIALS.md](MATERIALS.md). |

Baseline board wiring is LED anode to `J_LED_A`/`J_LED_C` pad 1 (`+`) and cathode to pad 2 (WIRE_B return). Both connectors have positive on the left and return on the right in board coordinates despite their opposite outward-facing rotations. Verify flying-lead identity from the actual part rather than assuming colours.

**Updated user risk decision, 2026-09-07:** LED damage from accidental low-voltage installation polarity errors is accepted, with spare indicators for replacement. Reversed flying-lead survival is no longer mandatory. Check polarity before power and correct mistakes while isolated; darkness is not a safety test. Spare quantity is not yet allocated or newly ordered.

**C4's remaining scope:** assess the simple 16-part candidate with one antiparallel clamp diode per connector, cathode to LED positive/anode to B, downstream of the existing series diode. This clamps negative connector voltage, not forward pulse current or reversed flying leads. Normal brightness, one-way cut behavior and ordinary RUN/TEST/switching/cattle-fence exposure still need assessment. Direct-strike damage is accepted; other transient risks are not waived wholesale. [ELECTRICAL section 9](pcb/ELECTRICAL.md#9-simplified-indicator-direction) records the candidate, not an implemented or qualified board.

## Current And Visibility

The current forward-only calculation uses 36 V, 27.6 ohms per 4 km core, 2.2 kohm per branch and 2.8 V combined LED/rectifier drop. For 41 stations in same-end TEST it predicts **15.09 mA near source and 8.04 mA at the far end**. An illustrative sensitivity case with **40 ohms/core and 4.0 V combined forward drop gives 6.21 mA at the far end**. These are calculations, not measurements, guaranteed cable limits or a final accepted minimum current. Protection changes require a new calculation.

The agreed target is **4-5 m visibility in full daylight**, with **ON and OFF distinguishable at 5 m**. Test the actual purchased indicators at the **final minimum expected field current**, in their real lid position and viewing direction/angle, including glare and off-axis viewing. An unpowered green lens must not be mistaken for an illuminated indicator. Record current, conditions and results under [ACCEPTANCE.md](ACCEPTANCE.md); a nominal on-axis brightness specification does not close this requirement.

Prefer evaluated optical/mounting improvements before increasing current. Lowering resistance or increasing supply voltage requires renewed near-source current, continuous potted thermal, fault/protection and procurement checks. At nominal near-source current the baseline resistors dissipate about **0.50 W each**; neither a brighter indicator nor a higher-wattage resistor guarantees lower enclosure temperature.

## Unqualified Alternative

**APEM Q14P5BXXHG02E** was previously suggested by Gemini as a larger stainless-steel special-order indicator. Retain it only as a sourcing lead: its exact material, electrical option, optical data, dimensions, lead/polarity details, sealing, availability and assembly compatibility have not been qualified here. **No purchase or approval is recorded; it is not a proven drop-in or proven better in daylight.** A larger bezel or mounting hole is not evidence of better contrast or luminous output at the actual far-end current.

Any change from the purchased Q10 requires manufacturer evidence, minimum-current 5 m visibility testing, electrical/protection/thermal and enclosure-fit review, and explicit procurement approval. The same applies to the older [README alternatives](README.md#5-unapproved-alternatives).

## Sources

- [APEM Q10F5SXXSG02E manufacturer page](https://www.apem.com/led-indicators/professional-grade-panel-mount-led-indicators/q10/q10f5sxxsg02e), including the applicable family/drawing data. Specifications were reviewed in REMEDIATION on 2026-09-06; retain the actual supplied revision for assembly.
- [REMEDIATION.md](REMEDIATION.md) for agreed visibility/current assumptions, C4/C5 issues and release gates; `pcb/ELECTRICAL.md` and `pcb/ASSEMBLY.md` are the electrical and controlled assembly evidence locations for the draft revision.
