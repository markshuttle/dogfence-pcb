# External LED Indicators

**Selected procurement baseline: APEM Q10F5SXXSG02E. Draft system revision 1.2.0-dev; qualification remains open.**

## Selected Part

The purchased Q10 indicator is the **no-internal-resistor** option, selected to use the PCB's external 2.2 kohm branch resistor rather than an additional internal voltage-rated lamp resistor. The `02` option is **not a regulated 2 V supply input**, nor does the part draw a fixed 20 mA. Forward voltage and current depend on the actual LED, resistor, cable drop, temperature, clamp leakage and supply.

| Item | Baseline / limitation |
| :--- | :--- |
| Identity | **APEM Q10F5SXXSG02E**, green, nominal 10 mm panel mounting, flying leads. Verify the supplied label and exact drawing. |
| Current | Published family **20 mA maximum**, not a required or guaranteed operating current. Bound near-source current and pulse current with the final protection circuit. |
| Reverse voltage | **5 V maximum**. The implemented BYG23T negative shunts are not proof that this limit is respected during transients or with reversed flying leads. |
| Temperature / ingress | Published Q10 data includes -40 to +85 degrees C and IP67 under specified mounting/sealing conditions. These component conditions are not ratings for the modified WISKA box, cable or complete assembly. |
| Mounting | Use the actual panel cutout, seal and panel-thickness instructions. Published mounting torque is **0.20-0.25 Nm**, subject to the exact supplied model instructions. |
| Procurement | **80 ORDERED**, unchanged from the purchase record. **41 stations need 82**, leaving a **shortfall of 2 before separate prototype use, losses or spares**. See [MATERIALS.md](MATERIALS.md). |

Board wiring remains LED anode to `J_LED_A`/`J_LED_C` pad 1 (`+`) and cathode to pad 2 (WIRE_B return). Both connectors have positive on the left and return on the right in board coordinates despite their opposite outward-facing rotations. Verify flying-lead identity from the actual part rather than assuming colours.

The user-authorized **16-part hybrid is now implemented in the schematic/PCB/BOM**, not yet qualified hardware. R1/R2 are **Vishay BCcomponents PR02000202201FA100**, copper-lead **2.2 kohm / 2 W / 1% / +/-250 ppm/K**. D1-D4 are **Vishay General Semiconductor BYG23T-M3/TR / C145454**: D1/D2 remain series parts; D3/D4 are **negative shunts**, cathode to each LED positive/anode to B, downstream of the series diodes. The old 1N4007G/MBE0414 are retired design selections, not default replacements.

**Updated user risk decision, 2026-09-07:** LED damage from accidental low-voltage installation polarity errors is accepted, with spare indicators for replacement. Reversed flying-lead survival is no longer mandatory. Check polarity before power and correct mistakes while isolated; darkness is not a safety test. Spare quantity is not yet allocated or newly ordered.

**C4 remains open:** D3/D4 provide a forward-conducting path for negative connector voltage, not positive regulation, forward pulse-current limiting or reversed-flying-lead immunity. BYG23T's **1300 V repetitive reverse rating and 75 ns reverse recovery do not establish forward-clamp speed**. Its typical **9 V / 620 ns forward overshoot at 1.5 A and 12 A/us, 25 C** is not proof of <=5 V at the physical LED. Normal brightness, leakage-induced OFF glow, RF/switching and nearby-lightning response remain unqualified. [ELECTRICAL section 9](pcb/ELECTRICAL.md) records implementation and remaining limits; C5/W3/W1/W4 also remain open.

Direct-strike rebuilding is accepted, not all ordinary or nearby-lightning damage. The user prohibits energized cattle fencing near the **whole 4 km boundary cable, every station and the hub**; the former **0.5 m / 300 m parallel exposure is withdrawn and historical**, not a current energizer-on/off qualification requirement. Inspect and maintain that prohibition and reassess before use if land use changes or the hazard returns. No safe distance or zero induction/lightning risk is asserted.

## Current And Visibility

The **historical zero-leakage comparison** uses 36 V, 27.6 ohms per 4 km core, 2.2 kohm per branch and 2.8 V combined LED/rectifier drop. For 41 stations in same-end TEST it predicts **15.09 mA near source and 8.04 mA at the far end**. The old **40 ohms/core, 4.0 V combined-drop** sensitivity gives **6.21 mA far-end**. These are not measured BYG23T forward-voltage/current data, guaranteed cable limits or accepted minimum currents.

The [updated PR02/BYG23T study](pcb/DESIGN_BOUNDS.md#normal-current) uses a **5.2 V high-drop screen** and **50 uA conditional clamp diversion**, giving **4.090396 mA** at the named nonuniform far-end LED corner at **35 V**, versus 5.636756 mA with uniform high-drop/Rmax loads. These are not measured or exhaustive minima. The intentionally loose all-station comparison floor is **0.195041 mA after diversion**, not predicted installed brightness. Neither the diode's 1.9 V test point at 1 A nor its leakage maximum at 1300 V is a guaranteed low-current/full-temperature LED-voltage bound. Actual series-diode reverse leakage and physical OFF glow are not solved by the ideal cut classifier. Clamp leakage diverts branch current; it is not an extra source-current load to add twice.

At the declared **40.39597 V** upper source screen, PR02 1% / 250 ppm/K resistance screening through 125 C gives **Rmin = 2120.8275 ohms** and **19.047268 mA maximum branch current with zero drops and zero diversion**, not a physical operating point or pulse-current guarantee. The old **35-37 V proposal was never hardware-enforced**. Source limits, actual I/V and 5 m visibility still need evidence; the disconnected spare LRS-75-36 adds no capacity to the one TEST unit.

The agreed target is **4-5 m visibility in full daylight**, with **ON and OFF distinguishable at 5 m**. Test the actual purchased indicators at the **final minimum expected field current**, in their real lid position and viewing direction/angle, including glare and off-axis viewing. An unpowered green lens must not be mistaken for an illuminated indicator. Record current, conditions and results under [ACCEPTANCE.md](ACCEPTANCE.md); a nominal on-axis brightness specification does not close this requirement.

Prefer evaluated optical/mounting improvements before increasing current. Lowering resistance or increasing supply voltage requires renewed near-source current, continuous potted thermal, fault/protection and procurement checks. The selected PR02 resistors still dissipate about **0.50 W each** at the nominal comparison point, with **0.769432871 W each** in the upper zero-drop screen. Their 2 W rating and required **>=1.00 mm body-to-PCB standoff** are not actual mounting/process or OneGel thermal acceptance. **Continuous-safe normal TEST remains mandatory without a timer**; no closed/gel-filled thermal test has been performed.

## Unqualified Alternative

**APEM Q14P5BXXHG02E** was previously suggested by Gemini as a larger stainless-steel special-order indicator. Retain it only as a sourcing lead: its exact material, electrical option, optical data, dimensions, lead/polarity details, sealing, availability and assembly compatibility have not been qualified here. **No purchase or approval is recorded; it is not a proven drop-in or proven better in daylight.** A larger bezel or mounting hole is not evidence of better contrast or luminous output at the actual far-end current.

Any change from the purchased Q10 requires manufacturer evidence, minimum-current 5 m visibility testing, electrical/protection/thermal and enclosure-fit review, and explicit procurement approval. The same applies to the older [README alternatives](README.md#5-unapproved-alternatives).

## Sources

- [APEM Q10F5SXXSG02E manufacturer page](https://www.apem.com/led-indicators/professional-grade-panel-mount-led-indicators/q10/q10f5sxxsg02e), including the applicable family/drawing data. Specifications were reviewed in REMEDIATION on 2026-09-06; retain the actual supplied revision for assembly.
- [Vishay BYG23T-M3, 89429, 25-Feb-2020](https://www.vishay.com/docs/89429/byg23t.pdf) and [PR01/PR02/PR03, 28729, 08-Jul-2025](https://www.vishay.com/docs/28729/pr010203.pdf), with test conditions and limitations recorded in [DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md).
- [REMEDIATION.md](REMEDIATION.md) for agreed visibility/current assumptions, C4/C5 issues and release gates; `pcb/ELECTRICAL.md` and `pcb/ASSEMBLY.md` are the electrical and controlled assembly evidence locations for the draft revision.
