# External LED Indicators

**Draft system revision 1.2.0-dev; external-indicator qualification remains open. Prototype files are not LED or installation approval.**

## Selected Part

The purchased Q10 indicator is the **no-internal-resistor** option, selected to use the PCB's external 2.2 kohm branch resistor rather than an additional internal voltage-rated lamp resistor. The `02` option is **not a regulated 2 V supply input**, nor does the part draw a fixed 20 mA. Forward voltage and current depend on the actual LED, resistor, cable drop, temperature, clamp leakage and supply.

| Item | Baseline / limitation |
| :--- | :--- |
| Identity | **APEM Q10F5SXXSG02E**, green, nominal 10 mm panel mounting, flying leads. Verify the supplied label and exact drawing. |
| Current | Published family **20 mA maximum**, not a required or guaranteed operating current. Bound near-source current and pulse current with the final protection circuit. |
| Reverse voltage | **5 V maximum**. The implemented BYG23T negative shunts are not proof that this limit is respected during transients or with reversed flying leads. |
| Temperature / ingress | Published Q10 data includes -40 to +85 degrees C and IP67 under specified mounting/sealing conditions. These component conditions are not ratings for the modified WISKA box, cable or complete assembly. |
| Mounting | Use the actual panel cutout, seal and panel-thickness instructions. Published mounting torque is **0.20-0.25 Nm**, subject to the exact supplied model instructions. |

Board wiring remains LED anode to `J_LED_A`/`J_LED_C` pad 1 (`+`) and cathode to pad 2 (WIRE_B return). Both connectors have positive on the left and return on the right in the [top-view assembly coordinates](pcb/ASSEMBLY.md#placement-and-polarity) despite their opposite outward-facing rotations. Verify flying-lead identity from the actual part rather than assuming colours.

The PCB's [current population](pcb/ASSEMBLY.md#reviewed-components) is not qualified LED-protection hardware. D1/D2 are series diodes; D3/D4 BYG23T **negative shunts** connect cathode to each LED positive and anode to B, downstream of the series diodes. They provide a forward-conducting path for negative connector voltage, not positive regulation, forward pulse-current limiting or reversed-flying-lead immunity.

Use [MATERIALS' indicator inventory/spare allocation](MATERIALS.md#1-station-inventory) and [resistor procurement history](MATERIALS.md#resistor-procurement-and-history), not this optical guide, for purchasing records. [REMEDIATION](REMEDIATION.md#release-gates) controls file/publication status and remaining holds; prototype-file authorization is not upload or order approval.

**User risk decision, 2026-09-07:** LED damage from accidental low-voltage installation polarity errors is accepted, with spare indicators for replacement. Reversed flying-lead survival is no longer mandatory. Check polarity before power and correct mistakes while isolated; darkness is not a safety test. Spare quantity remains to allocate in MATERIALS, not newly ordered stock. This does not waive continuous TEST safety or normal-operation transient assessment.

**C4 remains open:** reverse recovery does not establish forward-clamp speed or prove that the physical LED stays within its 5 V reverse limit. Normal brightness, leakage-induced OFF glow, RF/switching and nearby-lightning response remain unqualified. See the [diode evidence](pcb/ELECTRICAL.md#7-evidence-register) and [current circuit limits](pcb/ELECTRICAL.md#9-simplified-indicator-direction); separate protection/thermal holds remain open.

Direct-strike rebuilding is accepted, not all ordinary or nearby-lightning damage. Inspect and maintain the [whole-boundary cattle-fence prohibition](INSTALL.md#cattle-fence-prohibition); changed land use or a returning hazard requires reassessment before use, not testing the prohibited configuration.

## Current And Visibility

Use [ELECTRICAL's named historical zero-leakage comparisons](pcb/ELECTRICAL.md#2-calculated-results) separately from [DESIGN_BOUNDS' current normal-current cases](pcb/DESIGN_BOUNDS.md#normal-current). The latter covers the **TE-prototype/BYG23T, 41-station same-end TEST** population, including nonuniform high-drop/clamp-diversion corners, a deliberately loose all-station floor and a zero-drop/zero-diversion upper stress screen. These are not measured or exhaustive minima, physical LED operating points or pulse-current guarantees.

Use **LED current after clamp diversion**, not unadjusted branch current, when evaluating visibility. Clamp leakage is already part of branch/source current, not a second load to add. Actual low-current/full-temperature diode I/V, series-diode reverse leakage and physical OFF glow are not established by high-voltage/high-current datasheet test points or the ideal cut classifier.

The [model inputs](pcb/DESIGN_BOUNDS.md#evidence-and-inputs) include engineering temperature/reference assumptions, not verified TE test endpoints; source screens are **unenforced**, not approved operating limits or a guaranteed field-current minimum. Establish actual source limits and I/V before visibility acceptance. The model and TE prototype results do not qualify the unintegrated Yageo production part; [ORDERING's production change review](ORDERING.md#7-prototype-acceptance-and-later-orders) remains required.

The agreed target is **4-5 m visibility in full daylight**, with **ON and OFF distinguishable at 5 m**. Test the actual purchased indicators at the **final minimum expected field current**, in their real lid position and viewing direction/angle, including glare and off-axis viewing. An unpowered green lens must not be mistaken for an illuminated indicator. Record current, conditions and results under [ACCEPTANCE.md](ACCEPTANCE.md); a nominal on-axis brightness specification does not close this requirement.

Prefer evaluated optical/mounting improvements before increasing current. Lowering resistance or increasing supply voltage requires renewed near-source current, continuous potted thermal, fault/protection and procurement checks. Use the [thermal screens](pcb/DESIGN_BOUNDS.md#thermal-screens) and [alternate-land/mounting controls](pcb/ASSEMBLY.md#2512-smt-resistors), not a catalogue wattage or retired-part thermal/pulse example, to define qualification. Rating transfer remains unverified, not a demonstrated failure; SMT does not remove loss or prove cooler OneGel operation. **Continuous-safe normal TEST remains mandatory without a timer**; no closed/gel-filled thermal test has been performed.

## Unqualified Alternative

**APEM Q14P5BXXHG02E** was previously suggested by Gemini as a larger stainless-steel special-order indicator. Retain it only as a sourcing lead: its exact material, electrical option, optical data, dimensions, lead/polarity details, sealing, availability and assembly compatibility have not been qualified here. **No purchase or approval is recorded; it is not a proven drop-in or proven better in daylight.** A larger bezel or mounting hole is not evidence of better contrast or luminous output at the actual far-end current.

Any change from the purchased Q10 requires manufacturer evidence, minimum-current 5 m visibility testing, electrical/protection/thermal and enclosure-fit review, and explicit procurement approval. The same applies to the older [README alternatives](README.md#5-unapproved-alternatives).

## Sources

- [APEM Q10F5SXXSG02E manufacturer page](https://www.apem.com/led-indicators/professional-grade-panel-mount-led-indicators/q10/q10f5sxxsg02e), including the applicable family/drawing data. Specifications were reviewed in REMEDIATION on 2026-09-06; retain the actual supplied revision for assembly.
- [Board component/drawing provenance](pcb/ASSEMBLY.md#evidence-links) and [analysis inputs/limitations](pcb/DESIGN_BOUNDS.md#evidence-and-inputs). Other resistor families' pulse/thermal data are not evidence for the intended population.
- [Agreed requirements](REMEDIATION.md#agreed-requirements), [issue register](REMEDIATION.md#issue-register) and [release gates](REMEDIATION.md#release-gates). These requirements and records are not passed LED qualification results.
