# Hub Wiring And Protection Implementation Plan

**Reviewed and extended for C5:** 2026-09-15. **Station context:** Dog Fence 1.2.1-dev.
**Proposed subsystem:** A shed-cabinet interconnect and TEST-source protection PCB.
**Proposed directory:** `hub-pcb/`, separate from the implemented `pcb/` design.

**Status: reviewed planning document, not an approved circuit or wiring drawing.**
No hub PCB, component selection, switch pinout, surge rating or C5 closure follows
from this review. The [agreed requirements](REMEDIATION.md#agreed-requirements),
[operating matrix](INSTALL.md#functional-matrix) and
[release gates](REMEDIATION.md#release-gates) remain controlling.

## 1. Review Findings

The wiring-consolidation goal is reasonable, but the original draft mixed three
different jobs: cabinet interconnection, incoming-surge protection and interruption
of PSU-fed remote faults. One PCB may support them; one eFuse cannot establish all
three. The following findings replace the draft's implementation-ready claims.

| Priority | Finding | Required disposition |
| :--- | :--- | :--- |
| High | A 1.5 A total-current trip misses documented remote follow-current and resistive-fault cases. | Do not call the hub an arc-quenching solution or close C5. See [fault coverage](#32-remote-fault-coverage). |
| High | SMCJ58CA can exceed the TPS26600 voltage limits before it even reaches its specified clamp current. | Reject that pairing as a completed protection design; budget both power ports and control pins. See [component review](#4-component-review). |
| High | The draft promises RF neutrality and source isolation without the necessary transmitter and switch evidence. | Retain OEM protection, six independent field ends and global transfer isolation. See [RF routing](#21-smartfence-rf-routing). |
| High | Input reverse-polarity protection does not correct field-core swaps, reversed LED leads or field-side surge voltage. | Specify each fault and its safe response separately. See [polarity scope](#31-polarity-and-miswiring). |
| High | A 470 V GDT, a PE terminal and generic 3 mm spacing do not define an entrance protector or protect 60 V electronics. | Separate discharge paths and establish insulation, residual-voltage and failure-containment requirements before layout. |
| Medium | The 37 V/1.4004 A load budget, eFuse resistance/timing and resistor substitution claims are stale or incorrect. | Use current prototype bounds and exact manufacturer conditions; preserve unselected candidates as research only. |
| Medium | The proposed `build/hub/` output can be removed by the existing station transaction; sibling libraries also violate its local-project validation. | Isolate hub outputs and stage complete local dependencies; do not treat `--board hub` as a path-only change. |

**C5 planning decision:** develop a fault-tolerant TEST-source interface **plus**
qualified station recovery/failure protection and a separate cable/joint safety
case. First evaluate retention of the current stations; require an approved local
redesign wherever retention fails. A hub-only implementation is acceptable only
if the remote safety obligations are independently demonstrated, not assumed.
[Section 3](#32-remote-fault-coverage) specifies mechanisms, failure coverage and
finite decision gates; [C5 release evidence](#35-c5-limits-and-release-evidence)
defines what must be delivered before the hold can close.

## 2. Proposed Wiring

### 2.1 SmartFence RF Routing

**Recommended baseline: keep the SmartFence boundary-output pair on its OEM
protected wiring path to the rotary switch's RUN source-side contacts, not through
the TEST power electronics.** "Straight to the switch" does **not** mean bypassing
the OEM lightning/surge protector.

This recommendation assumes "antenna leads" means the two conductors connected to
the transmitter's **`LOOP` socket**. Any separate communications antenna/coax belongs
with its OEM radio equipment and should go through **neither** this switch nor an
ordinary hub-PCB terminal network. Identify the actual connector before wiring.

The [SmartFence owner's guide, Rev. E.1, June 2026][dw-guide], printed pp. 11-12,
specifies the boundary connection through its surge protector, original zip cord
to `LOOP`, and a separate `GND` connection. It does not approve this six-end selector
modification. Preserve the transmitter's OEM supply and any backup arrangement;
do not power it from the 36 V TEST source.

```text
SMARTFENCE RUN BRANCH, outside the PCB's TEST electronics:
  SmartFence LOOP pair
       <-> original OEM wiring / OEM surge protector
       <-> direct paired wiring to RUN source buses T1 and T2
                                             |
                                         RUN throws
                                             |
                                      SIX independent
                                      rotary-switch poles
                                             |
                                       six commons
                                             |
  4 km cable <-> HUB PCB: six separate field-interconnect paths
                 Start A/B/C and End A/B/C

TEST BRANCH, on a segregated section of the SAME hub PCB:
  One LRS-75-36 (+/-), existing fuse/holder pending coordination review
       -> reviewed input/reverse-polarity and port protection
       -> Q: current/OV control and reverse blocking
       -> K1 -> K2: independent normally-open two-pole DC disconnects
       -> protected TEST source harness -> TEST throws of the same switch
          positive to Start A/C throws; negative to Start B throw
          End A/B/C TEST throws remain individually unconnected

ENTRANCE PROTECTION, separate function, topology/parts not yet selected:
  Six field paths -> reviewed surge branches -> accepted earth/discharge bar
  Required PE/OEM grounds remain unswitched, outside the mode-selection paths.
```

This is a **functional proposal**, not physical terminal numbering. T1/T2 have the
meaning defined in INSTALL: protected transmitter connections. RUN grouping is
Start A/B/C to T1 and End A/B/C to T2, only on RUN source-side contacts. The OEM
protector's exact terminals, physical position and permissible switch placement
need regional OEM acceptance. A protector connected only through RUN contacts
cannot be credited with protecting the field-side switch terminals or TEST
electronics in OFF/TEST; the separate entrance stage must address those exposures.

**The six field paths on the PCB still carry RF in RUN**, even when the
transmitter-side pair bypasses the PCB. Keep these paths passive and separate
from the TEST regulator/eFuse, reverse-polarity devices, sensing returns and
control ground. Any protection or sensing branch attached to them needs loading
and isolation assessment in every mode. Do not add a blanket PE/DC-negative plane
under them without a justified coupling and insulation design.

A passive PCB route for the transmitter pair is not inherently forbidden. Regional
[DogWatch dealer evidence][dw-frequency] gives 4/8 kHz at family level, not a verified
frequency or loading allowance for the installed SmartFence. Short traces at those
frequencies are not automatically a controlled-impedance RF design problem. Direct
wiring is preferred here to minimize added interfaces and coupling to TEST circuitry.
If complete RF-harness consolidation is later wanted, use a separately reviewed
passive RF section, never the DC conditioning chain.

Neither a single-point hub clamp nor low-capacitance station GDTs prove acceptable
RF loading. Inter-core and core/earth capacitances are different network elements;
adding every capacitor as though it were across the transmitter is also invalid.
Obtain output/load limits for the exact transmitter and assess the actual cable,
station and hub network. Verify receiver coverage and loop monitoring with required
OEM protection retained in both the reference and modified configurations.

### 2.2 PCB Interfaces And Isolation

The proposed interfaces below define electrical roles, not connector pin numbers.

| Interface | Connection and constraint |
| :--- | :--- |
| PSU input | One LRS-75-36 positive/negative pair, with the existing fuse/holder subject to coordination review. The second PSU stays disconnected as a spare. |
| Protected TEST source harness | Positive split to the two Start A/C TEST throws and negative to the Start B TEST throw. A PCB positive split is permitted only within this source-side harness, not on field/common nets. |
| Switch-common harness | Six separately identified connections, one for each boundary end. No copper bus joining commons. |
| Field terminals | Six individually accessible paths: Start A, Start B, Start C, End A, End B, End C. No permanently paralleled cores or End A/C strap. |
| Surge-earth connection | Only according to the accepted discharge/bonding drawing; not a DC-negative or logic-ground connection by default. |
| Reset/status harness | Touch-safe, appropriately protected control wiring with no hidden bypass around source isolation or input reverse protection. |

Use the complete [RUN/OFF/TEST matrix](INSTALL.md#functional-matrix), not a new
matrix in this plan. OFF disconnects all six ends from the sources **at the hub**;
TEST keeps the three End connections individually open and uses the same-end feed
and return. This does not make the distributed field wiring globally voltage-free.
Preserve the WAGO through-splice/PCB-tap station architecture.

The provisional [CA10.A364/WAA364](pcb/ENVIRONMENT_EVIDENCE.md#ca10a364-switch)
has eight poles, but supplied configuration, DC application and **global
break-before-make in both directions** remain unapproved. All old-source paths
must open before any new-source path closes. Individual-pole timing, centre-off
and an eFuse's off state are not substitutes. Both TEST positive and return must
be disconnected from the field/RF branch in RUN. The two extra poles remain
unassigned; do not assume they provide reset, mode sensing or safety isolation.

Keep the 0 m and 4000 m shed-end stations as the same passive evaluation baseline
as the other 39; do not modify station CAD/BOM in this planning task. If C5 requires
local protection changes, propose them for every applicable station, not just the
two shed ends. A serviceable shed hub is a sensible place for source controls,
but a local hub arrestor does not insert a quenching element into a remote bare-GDT
path. No special-station redesign, doubled-tooling-cost claim or assumed outdoor
mounting of both shed-end boards is needed to justify this proposal.

### 2.3 Mechanical And Earthing Boundary

Target one serviceable low-voltage/field-interface PCB in a guarded cabinet,
with an appropriate 35 mm DIN carrier if accepted. The LRS chassis supply retains
its own mounting/ventilation requirements; it is not inherently DIN-mountable.
Mains distribution and required protective-earth continuity stay outside this PCB.
No required PE connection may depend on a removable ordinary PCB connector/trace.

The draft's 72/108 x 100 mm sizes, 2-layer/2 oz construction, terminal families,
1.50 mm power traces and 3.00 mm separation are **planning candidates, not approved
dimensions or insulation ratings**. Select them from thermal, fault-current,
impulse, pollution/environment, access and enclosure requirements. A 300 V connector
marking does not establish surge withstand or safe interruption; do not hot-unplug
field or power connectors unless specifically rated and authorized.

Keep the field entrance/discharge area physically separated from protected
electronics, with short, direct, suitably rated discharge connections. A reviewed
external DIN surge module may be necessary if impulse paths or failure containment
cannot be supported on the interconnect PCB. The single-PCB wiring goal must not
force high-energy diversion through small control traces or bypass OEM protection.

The qualified installer must accept the actual building PE/electrode bonding,
OEM protector/transmitter grounds and proposed shared shed-end station earth.
Do not copy US outlet-faceplate instructions into an Isle of Man installation,
add arbitrary unbonded rods, directly earth a core, bond DC negative by assumption,
or switch PE. OFF is not demonstrated storm isolation. Do not handle boundary
conductors during storms; follow [INSTALL's safety controls](INSTALL.md#safety-first).

## 3. Protection Requirements

### 3.1 Polarity And Miswiring

| Fault or mistake | Required treatment |
| :--- | :--- |
| Reversed PSU input | Block unsafe energization and protect the complete hub, including auxiliary supplies, sense pins, reset wiring and any externally referenced connections. Specify sustained-voltage/current and temperature limits. |
| Field/load drives the output above the input | Provide reverse-current blocking **and** a separate energy/clamp budget. Blocking alone does not absorb energy or protect an isolated OUT pin. |
| Negative field-side pulse or combined reversed-input/energized-output condition | Check positive and negative limits at every power/control port, including IN-to-OUT differential stress. Input reversal protection is not output surge protection. |
| Start/End or A/B/C swap, short, or wrong switch harness | Prevent with distinct/keyed connectors, permanent labels and isolated continuity checks. Input polarity protection cannot correct these errors; no automatic polarity bridge belongs in the RUN path. |
| Reversed external LED flying leads | The user's acceptance of accidental installation LED damage remains. Verify/correct polarity while isolated; this hub does not make the station LEDs reversal-proof. |
| Foreign supply or mains at a field terminal | Not covered by the nominal 36 V reverse-input function. Prevent by segregation and identification; define credible misconnection withstand/safe-failure requirements rather than imply universal protection. |

Mark field connections by **end and core**, not permanent positive/negative roles,
because all three cores carry RF in RUN. Verify the colour-to-core mapping end to
end. The supplied plain-green core is active, never PE; green/yellow is reserved
for protective earth. The accepted LED-damage risk does not waive hub/source,
earthing, continuous-duty or ordinary-transient safety.

### 3.2 Remote Fault Coverage

**C5 remains open.** Source shutdown can remove PSU follow energy only if the fault
is detected and the actual source paths open. It cannot remove all energy already
stored in the cable or delivered by an external surge.

The existing [powered-fault model](pcb/ELECTRICAL.md#4-powered-faults-c5-open)
already supplies counterexamples to the proposed 1.5 A trip. The following are
conditional DC calculations: 36 V, 41 stations, 27.6 ohm per 4 km core,
2200 ohm/2.8 V branches, 0.25 ohm source-path resistance, and 0.1 ohm slope for
the assumed ignited arcs. They are not measured tube behavior or a dynamic PSU model.

| Modeled AB fault | Total source A | Fault-path A | Fault-path W |
| :--- | ---: | ---: | ---: |
| 10 V ignited arc at 4 km | 0.979810 | 0.259543 | 2.602168 |
| 15 V ignited arc at 4 km | 0.913626 | 0.134598 | 2.020787 |
| 100 ohm fault at 0 km | 1.197071 | 0.357007 | 12.745423 |
| Hard short at 4 km | 1.112913 | 0.507648 | 0 ideal, excluding real contact resistance |

The current [upper-screen fault case](pcb/DESIGN_BOUNDS.md#fault-screen) is also
material: at **40.39597 V**, the declared hot cable/contact corner and zero-Vf
TE R-min loads, a near-source 100 ohm AB fault dissipates **16.052665 W** at only
**1.320771 A total**. This is a separate model case, not a measured worst case
or a reason to reuse the nominal table's inputs for every result.

All are below 1.5 A; some dissipate material local power without reaching either
the eFuse threshold or PSU overload. Normal and fault current ranges overlap.
Lowering a threshold, detecting a current step, or memorizing an assumed healthy
startup load does not establish complete coverage of a cable being tested for damage.
An AC short can also mask a cut without drawing significant additional current.

Do not infer certain holdover or certain extinction from these calculations.
The original "36 V above 135 V" statement was arithmetically wrong. Current Ruilon
data gives typical arc/glow test points of **15 V at 1 A / 135 V at 10 mA** for
SMD5050-470NA and **10 V / 60 V** at those currents for 2R470TD-8. Those are not a
10-50 mA holding-current specification or a 10-100 ms recovery guarantee. The
separate telecom holdover test network is discussed in
[SOURCE_PROTECTION_RESEARCH](pcb/SOURCE_PROTECTION_RESEARCH.md#2-what-holdover-actually-specifies).

Nor is exceeding 2 A a prompt fuse trip: the selected 2 A Littelfuse 217 specifies
**60 minutes minimum at 3 A** under its test conditions. LRS-75 overload is
**110-150% of rated power**, with unestablished actual hiccup/clearing waveforms.
The existing fuse/holder is intended as backup wiring protection, pending
coordination review, not as a remote-arc detector.

#### C5 Resolution Path

Address three independent obligations. Passing the first is not permission to
skip the other two. The proposed default is **retain-and-qualify**, with a required
retain-or-redesign decision before field design freeze, not indefinite research
followed by an unqualified installation.

| Obligation | Exit for retaining the current station/installation | Required response if the exit is not met |
| :--- | :--- | :--- |
| **Powered GDT recovery** | The actual Ruilon population recovers, or undergoes credited safe interruption, within accepted voltage/current/energy/temperature limits on every relevant powered path, including post-stress conditions. | Evaluate the supported DC-recovery cells below or qualified local interruption. Change every affected path; a new device only at the hub leaves remote bare paths intact. |
| **Damaged station/protector safety** | Each credible failed-open, failed-short, intermediate-resistance or tracking state is benign continuously, or a qualified safeguard interrupts/contains it before its limits are exceeded. Include joints, PCB/taps and adjacent materials, not just the tube body. | Prefer qualified local thermal opening at the hazardous path. If no suitable branch assembly can be established, propose a reviewed local module or station redesign. Healthy-tube extinction is not this evidence. |
| **Cable and splice safety** | Credible hazardous shunt and series faults are detectably outside permitted observations before damage, or have a demonstrated benign continuous thermal/containment envelope. | Require an approved spatial sensing/local-protection or cable/installation change. Station GDT protection cannot stand in for protection of the intervening cable. |

The designer and qualified laboratory must define the credible fault set and
abnormal-condition limits from actual materials and exposure. This is not a demand
to detect every infinitesimal leakage or survive arbitrary simultaneous failures.
It must include faults present before TEST starts, faults developing during TEST,
credible common-cause surge damage and failure of a credited protective element.
Neither a successful nominal run nor the user's acceptance of direct-strike
rebuilding removes those obligations.

If a hazardous class is unobservable at the hub and unprotected locally, **C5 cannot
close while station/installation changes are prohibited**. The required output is
a specific approval request describing the necessary change and its impacts, not
a lower current threshold or a claim that supervision makes the fault harmless.
The current station Gate P files remain usable for their authorized evaluation
scope; no station geometry, BOM or field wiring changes are authorized here.

#### Detection Credit

Use instrumentation for the functions it can demonstrate. Do not add increasingly
complicated hub sensing without a measurable separation margin between permitted
operation, including all required clean cuts, and hazardous states.

| Technique | Useful function | Coverage limitation |
| :--- | :--- | :--- |
| Total-current/current-limit trip | Gross overload and some shorts | Misses the documented sub-rated faults. Total-energy accumulation without an independent fault decision would eventually stop healthy continuous TEST. |
| Separate A/C feed measurements | Diagnostics and validated abnormal-current patterns | Clean cuts legitimately create imbalance; symmetrical faults can remain balanced. Fault current can replace some indicator current instead of adding its full value to source current. |
| Residual current, `I_A + I_C - I_B` | Returns outside the monitored conductors | AB/BC paths and two-tube earth loops can have zero residual while heating. It is not a differential-fault or universal earth-fault detector. |
| Surge/voltage/current event latch | Fast shutdown for demonstrated event classes | A remote event can be attenuated or missed; an existing resistive fault need not create a detectable event. Do not credit every station merely because a hub clamp has an event output. |
| ADC/model comparison or startup baseline | Characterization of a bounded network | Resolution cannot remove model ambiguity. Never learn a possibly damaged cable as the healthy reference or attach shared-reference End sensing that creates a hidden return. |
| Local thermal sensing/opening | Acts on heat that hub electrical readings may miss | Must cover the real hot spot with qualified response, coupling, power/failure behavior and interruption. A bulk box-temperature sensor or communications heartbeat alone is insufficient. |

Periodic blanking, polarity alternation or diagnostic voltage excursions are
**not** the baseline solution. They change the TEST waveform/topology and need
explicit approval and renewed functional/transient qualification. Periodic arc
quenching would still not remove a permanent resistive fault; repeated reapplication
can repeat its heating. Normal TEST remains steady, continuous-safe DC with no
session timeout or automatic retry into a known fault.

#### Local Recovery And Failure Protection

Use these ordered evaluation routes, not an interchangeable protection BOM:

| Route | Basis and design action | Limit that must still be closed |
| :--- | :--- | :--- |
| **1. Retain Ruilon** | Request an application envelope for SMD5050-470NA and 2R470TD-8, then perform bounded powered type tests where necessary. Record actual source/cable RLC, recovery voltage, temperature, both pulse polarities, life conditioning, residual current and restart conditions. | [SMD5050 A3][ruilon-smt] and [2RD-8 A6][ruilon-earth] do not supply a powered extinction-time/network guarantee. Check supplied-lot applicability; neither typical arc/glow data nor post-reflow recovery language supplies it. Damaged-device safety is separate. |
| **2. DC-rated stack fallback** | Evaluate **TDK LN8-A1200DC-4 / B88069X1993B501**, version 05, 2019-07-25, with its exact three-capacitor network in each affected path. [The manufacturer][tdk-dc-stack] specifies 48 V +/-20% DC with a **30 A DC-source condition**. This is the preferred already-supported recovery fallback where primary surge capability and a mechanical redesign are acceptable. | Compare the actual source and stored-energy network with the specified test circuit; do not infer arbitrary dynamic recovery. With its capacitors, front voltage is <850 V initially but <1600 V after life under the stated test, not automatically better insulation coordination. Include capacitor/stack failures and local damaged-state protection. |
| **3. Series GDT/MOV alternative** | Evaluate **Bourns GMOV-14D500K** or an equivalently supported series cell if its actual surge/thermal envelope is accepted. The MOV supports the DC voltage after the surge rather than leaving only a bare arc path. | GMOV has **no thermal fuse** according to the [manufacturer's explanation][gmov-failure]. A shorted MOV returns the bare-GDT problem; common-cause damage can defeat both elements. Its surge ratings are not equivalent to every present station tube. Recovery does not close damaged-device containment. |

The detailed historical cells are in
[SOURCE_PROTECTION_RESEARCH](pcb/SOURCE_PROTECTION_RESEARCH.md#4-dc-power-and-mov-alternatives).
They are not current station assemblies. Do not leave an original bare tube in
parallel with a replacement cell, put a blocking element only in the external
EARTH lead, reuse retired AC holes, or treat a carrier as automatically compliant
with [the current physical guardrails](pcb/ASSEMBLY.md#physical-guardrails).

**Preferred damaged-device mechanism: a qualified local opening assembly.** Place
the interruption in the actual surge/fault branch, with thermal coupling to every
credited heat source. It must carry the specified surge waveform/charge/repetition,
interrupt the full DC recovery voltage and relevant current/inductance, operate
before adjacent materials exceed their limits, and remain safely open without
tracking, restrike or hazardous leakage. Qualify aging, soldering, OneGel exposure,
mechanical movement and loss-of-protection indication/service. No reviewed generic
thermal fuse or the previously suggested TMOV establishes this combined duty.

A guaranteed low-resistance fail-short mechanism is an alternative **only** with
limits for pre-activation temperature, final resistance and continuous connection
heating, including low-power faults that might never activate it. Its diagnostic
masking and core/EARTH consequences need explicit acceptance. Do not turn that
fault disposition into an intentional direct core-earth bond. A TCO in a surge
branch is distinct from the required PE conductor: **PE is never opened**.

If branch-local protection cannot be qualified, an alternative proposal is a local
module disconnecting all three **station taps**, leaving WAGO through-splices
intact. It still needs actual sensor coverage, DC/impulse interruption and fit
review; it is a station wiring/protection change, not a hub-only fix. It cannot
isolate a fault in the through-cable or splice. No such module is selected here.

#### Fault Coverage Matrix

For each row, record the exact credited mechanism, numerical limits, failure
assumptions, test/report identifier and final service disposition. A proposed
mechanism or a blank evidence cell is **HELD**, not PASS.

| Fault class | Required coverage and discriminator |
| :--- | :--- |
| AB/BC ignition | Independently qualify both paths' recovery or local interruption over source/cable/load asymmetry. Below-threshold follow current cannot rely on hub overcurrent. |
| AC ignition or short | Include asymmetry, cuts and other fired/failed paths. Equipotential A/C in one healthy case is not universal safety; a short can mask a later cut. |
| Intermediate-resistance GDT/cell/PCB/tap fault | Sweep resistance and location, including the documented multiwatt cases. Demonstrate benign temperature or effective local interruption/detection, not just intact-GDT recovery. |
| Single core/EARTH path | Bound actual leakage, capacitance, common-mode and external energy. Zero steady DC in an ideally floating circuit is not zero voltage or touch-safety evidence. |
| Two earth tubes sharing an unwired EARTH node | Treat as AB/BC/AC differential paths. An external earth-lead device is bypassed; residual-current balance can remain zero. |
| Earth paths between stations | Test actual source/return combinations and site impedances, unequal sharing and one tube already failed short. A surviving element may see full recovery voltage; no DC-negative/PE bond is needed to form the loop. |
| Stable failed-short component | Bound real device/joint resistance and continuous temperature under the actual current ceiling and protective-failure envelope. Zero-ohm model dissipation is not real thermal evidence; record diagnostic masking and replacement. |
| Failed-open protector/local release | Demonstrate safe loss-of-protection indication and a service restriction before renewed reliance. An open DMM reading does not prove a functional arrester. |
| Clean cuts; cuts plus other faults | Preserve all 280 clean-cut diagnoses without tripping simply for low load/imbalance. Apply fault-safety criteria to remaining energized paths in mixed cases; localization may be ambiguous and islands may remain charged. |
| Cable shunt or concentrated series/joint fault | Apply the separate cable safety case below. Current can decrease; local station protection and residual-current sensing cannot cover every such fault. |
| Q shorted; one disconnect or driver stuck closed | The surviving independent shutdown path must remove both TEST source conductors within its accepted energy/time limits. Include upstream PSU capacitance and actual current, not the failed Q's nominal limit. |
| Sensor/reference/controller failure; source OV/dropout | Fault analysis must demonstrate release despite a stuck controller, missing/plausible-stuck sensor, reference fault or repeated hiccup. Shared surge damage and other common causes cannot be labelled independent. |
| Fault before startup; reset held or supply cycled | Startup protections remain active; no automatic re-energization or repeated reset attempts into the fault. Verify a new deliberate reset action and disconnect feedback. |
| Selector contact remains connected | Exact selector/interlock design must prevent unsafe RF/TEST connection. K1/K2 interrupt TEST only and cannot be credited with opening a welded RUN path; obtain an accepted interlock or separately reviewed source-isolation change if needed. |
| External surge/earth rise | Use the coordinated entrance/local discharge and insulation design in all modes. Removing TEST power does not remove externally supplied energy; direct-strike rebuilding is not blanket nearby-event acceptance. |

#### Cable And Joint Coverage

Electrical terminal measurements determine aggregate behavior, not the spatial
distribution of heating. Within a span, the same series resistance can be
distributed through sound cable or concentrated at a bad joint. Establish whether
the observationally overlapping cases are thermally benign; do not infer that
they are harmless from low total current or that every small resistance is hazardous.

If a hazardous cable class cannot be separated with adequate margin, the release
decision must require a qualified physical containment/installation solution or
additional spatial protection. Per-span current comparison could address some
shunt faults, but not every series hot spot; a station thermometer does not monitor
100 m of cable. Any sensing/power/communications design credited for shutdown must
survive the core cuts that TEST is required to diagnose, or provide another safe
means of completing that diagnosis. Do not silently introduce a new feed, a fourth
conductor, wireless safety dependence or a changed TEST waveform. Those need a
specific proposal and user approval.

Use the existing
[failure-coverage record](pcb/SOURCE_PROTECTION_RESEARCH.md#6-failure-coverage-and-prototype-boundary)
as supporting evidence. Recovery, damaged-station safety and cable/joint coverage
must all have accepted dispositions before claiming full C5 closure.

### 3.3 Surge Coordination

Separate these functions in the circuit and acceptance records:

| Function | Boundary |
| :--- | :--- |
| Field-entrance surge diversion | Six distinct field connections; differential and common-mode exposure in RUN/OFF/TEST and during transfer. Must not introduce permanent end ties. |
| OEM transmitter protection | Retained OEM arrangement in the RF branch; not replaced or qualified by the custom hub. |
| TEST electronics protection and shutdown | Positive/negative surges at IN and OUT, control-pin stresses, stored energy, reverse energy, follow current and independent interruption if a semiconductor fails short. |

A **series** GDT/MOV branch and a **parallel** GDT/MOV pair are not interchangeable.
A series MOV can limit follow current in its own branch; a parallel MOV does not
insert impedance into a conducting bare-GDT path. A hub hybrid also leaves remote
bare paths unchanged. Specify firing/clamp coordination and failed-device behavior,
not "series or parallel" as an assembly choice.

MOV capacitance, TVS pulse capability and thermal failure behavior are part-specific.
The draft's blanket station-MOV prohibition and 20-50 A 8/20 us limit for all SMT
TVSs are withdrawn. Small TVSs can be coordinated secondary protection, not assumed
replacements for a high-energy primary. Do not sum all 246 protection capacitances
as one transmitter shunt or assume incident kA currents from GDT component ratings.
A shunt across an LED alone still does not guarantee forward pulse-current control.

Specify residual voltage and energy at the switch, cable, connectors, PCB barriers
and electronics, including lead inductance and clamp tolerances. The cable's 60 V
DC service rating is not impulse withstand; the station GDTs' specified impulse
sparkover can reach 950/1100 V at 1 kV/us. Neither those parts nor a new hub are
qualified by nominal 3 mm gaps, solder mask, gel, copper thickness or kA labels.
Direct-strike survival is not required; ordinary switching/RF and a defined
nearby-lightning scope remain. The entire-boundary energized-cattle-fence
prohibition remains, not a test configuration to reintroduce.

### 3.4 Source Control And Operator State

Recalculate normal input/output limits using
[DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md#evidence-and-inputs), including hub/contact
losses and auxiliary power. The current TE prototype zero-drop/R-min upper screen
is **1.536239 A at 40.39597 V**, before new bypass/auxiliary loads. This voltage is
a declared adjustment/tolerance screen, not an enforced or guaranteed maximum.
The draft's **1.4004 A at 37 V** came from a historical resistor model; neither that
load budget nor the historical 35-37 V window is the current source specification.

Do not freeze 8 kohm current programming, 36.8 V OV or 30 V UV thresholds yet.
Choose operating and fault limits with tolerance, startup, ripple, thermal and
visibility margins. Qualifying the actual normal source range is an alternative
to a precision operating cutoff; source-malfunction protection still needs review.
A lower cutoff alone does not qualify closed-OneGel station temperatures.

#### Independent Shutdown

Adopt the following **functional design target**, not a selected relay/controller
BOM: a single credited protective-device failure must not defeat TEST-source
energy removal, and one welded disconnect must not defeat two-conductor TEST
isolation. Use **Q plus two independently driven, normally-open, two-pole DC
disconnects K1 and K2 in series**. Each disconnect opens positive before its A/C
split and negative before the Start B source contact. One relay plus Q alone is
not redundant galvanic isolation of both conductors under a welded-contact fault.

Q supplies fast limiting/reverse blocking/shutdown. Two protection channels must
be able to release their respective K devices without permission from a common
MCU; each also requests Q shutdown and fault latching. Provide independent
source/output OV supervision and the required fault/health inputs with separate
references/release paths. Shared PSU loss must de-energize the system safely.
Diagnostic software may inhibit or request shutdown, but cannot override a trip.
Do not derive both release channels solely from Q's `FLT` output: a failure of Q
or that signal must not erase the only detection needed to operate the surviving
disconnect. Verify each credited trigger through its applicable independent path.
Detection credit remains limited by the matrix above: duplicating an overcurrent
detector does not detect the sub-rated faults.

Specify actual DC breaking/current/voltage/inductance ratings, contact feedback,
driver failure behavior, coil-suppression release delay and proof-test method.
Prove each isolation path without removing the remaining field-isolation barrier.
Review common-cause surge/contamination, shared-reference faults, and bypasses
through sensing, fuse-holder indicators, auxiliary wiring or test instruments.
Two copies sharing a vulnerable node are not independent protection. External
approved DIN hardware is acceptable where PCB hardware cannot meet the duty.
No SIL/PL or certified functional-safety claim follows from this block diagram.

The exact selector/interlock remains part of the safety case. TEST-position
feedback alone does not prove every RF contact is open. Establish the accepted
mode/isolation proof without assigning spare poles or modifying OEM RF protection
in this plan; if the chosen fault contract needs additional RF isolation, obtain
its separate OEM/design approval.

#### State And Reset Contract

| State | Required behavior |
| :--- | :--- |
| Unarmed | Q disabled, K1/K2 released after initial power-up, brownout/control loss or leaving the permitted mode. Source restoration alone cannot enable TEST. |
| Precheck | Require verified TEST isolation, valid source/references/protection, released reset button and satisfactory disconnect feedback. Do not require a healthy-cable current signature that rejects legitimate cuts. A known fault requires inspection/disposition before reset. |
| Startup | One deliberately requested, energy-bounded transition to normal TEST. Independent OV/OC and local safeguards remain active; bound any device-specific startup flag masking and maximum startup duration. Failure to establish the expected state latches off. |
| TEST enabled | Steady DC, continuous-safe within the qualified normal envelope. Valid clean cuts remain diagnosable; no periodic blanking or session timeout. All credited fault channels remain active. |
| Tripped | Disable Q and release K1/K2, verify the expected contact/output state, record the reason and inhibit retry. Discharge only nodes actually connected to the reviewed discharge network. Persistent feedback failure inhibits reset. |
| Reset | Require fault disposition, valid source/mode, protection readiness and a fresh release-then-press action. A held button, cleared fault flag or mains power cycle is not permission for repeated re-energization. Reset never selects RUN automatically. |

Retain fault/service information across power loss where needed to enforce the
reset restriction. Specify how physical inspection/authorization is recorded;
do not make a fleeting fault LED the only record of a known damaged protector.

Opening a pass FET does not actively force its output to zero. Budget cable/hub
capacitance, inductance, turn-off overshoot and upstream energy through a failed
switch, then establish interruption time, discharge and recovery before reset.
Use measured or justified conservative bounds and `integral(v*i*dt)`; do not assign
an arbitrary safe arc duration. A fault-triggered shutdown is not a timer on healthy
TEST, which must remain continuous-safe.

Label power indication **TEST SOURCE AVAILABLE/ENABLED**, as appropriate to what
is actually sensed, and **TEST FAULT/TRIPPED**, not "NORMAL" or containment health.
Mode labels must independently identify TEST/OFF as **NO CONTAINMENT** and require
deliberate restoration and verification of RUN. Use [INSTALL](INSTALL.md#switch-and-supply).

### 3.5 C5 Limits And Release Evidence

Replace guessed trip values with a **completed numerical fault contract** owned by
the future hub electrical record and accepted test protocol. For each credited
mechanism, specify source voltage/current versus time, permissible output/drop,
IN/OUT/control/common-mode limits, cable/source RLC and stored-energy bounds,
temperature/energy limits at the actual material interfaces, detection uncertainty,
maximum clearing time, recovery/off interval and post-fault service condition.
Record provenance and covered failures for each value. Missing limits hold the
corresponding stress test or release claim, not unrelated bounded evaluation work.

Use these design/acceptance calculations, with valid operating-region assumptions:

```text
Healthy load:
  I_limit,min > I_healthy,max + I_added_downstream,max + design_margin
  P_field + P_interface_loss + P_auxiliary <= accepted_derated_PSU_capacity

Resistive path in a valid linear/CV region:
  I_fault = V_th / (R_th + R_fault)
  P_fault = V_th^2 * R_fault / (R_th + R_fault)^2

Continuous benign-state acceptance at every affected interface:
  T_measured,max + measurement_uncertainty + uncovered_corner_allowance
      <= accepted_temperature_limit
  R_failshort,max <= P_continuous,accepted / I_fault,max^2

Detected-fault interruption:
  t_clear = t_detection + t_logic + t_actuator + t_current_extinction
  E_fault = integral(v_fault(t) * i_fault(t) dt)
  E_C = 0.5 * v^T C v; E_L = 0.5 * i^T L i
  E_stored,max + P_feed,max * t_clear + E_overshoot,max + E_external,max
      <= E_allowable
```

Use a justified local allocation or conservative total-network bound for the
energy inequality; do not double-count the same pulse/capacitor contribution.
`P_feed,max` must remain valid with the credited failed protection element.
If Q is shorted, its former current ceiling no longer bounds feed power or the
upstream PSU capacitor discharge. Check the voltage/time and temperature criteria
as well as joules; an allowable pulse energy is not continuous thermal approval.
If the remaining energy budget is nonpositive, the architecture must change.

The current conditional healthy screen is **1.536239 A / 62.057870 W**, excluding
new bypass/auxiliary loads. Do not double-count leakage already passing through
R1/R2. The old 8 kohm eFuse setting's approximately **1.4236 A minimum** does not
cover that screen. Neither the historical **1.6 A ceiling** nor **0.10 ohm failed
short** is guaranteed; their illustrative **0.256 W** must be recalculated from
the adopted source and failure envelope. Do not raise the current limit without
rechecking local fault energy and source/interface thermal margins.

For a detector credited with remote safety, demonstrate that uncertainty-expanded
permitted observations, including clean cuts, and hazardous observations are
separable **within the allowed clearing interval**. Include sensor saturation,
drift, noise, startup and fault evolution. Overlap requires local protection,
benign-state evidence or an approved requirement/design change, not more ADC bits.

For recovery, qualify the actual current/voltage trajectory, restart conditions
and off time. A lumped `R*C*ln(V_initial/V_reset)` discharge estimate applies only
to the connected network it models, not every cut island or externally charged
core. Neither K.12's 150 ms nor a proposed 10-100 ms interval is a universal safe
duration. Use [the existing energy analysis](pcb/SOURCE_PROTECTION_RESEARCH.md#7-cable-and-source-energy-bounds)
for the distinction between source-fed, stored and external energy.

**Required closure deliverables:**

| Deliverable | Owner and completion criterion |
| :--- | :--- |
| Fault contract | Electrical designer plus qualified reviewer/lab: accepted numerical bounds, credible faults/common causes, safety functions and test stop conditions. No safety-critical TBD remains for the claimed scope. |
| Station retain-or-redesign report | Protection/assembly engineer plus lab: separate recovery and damaged-state evidence for the actual population/process. A failure produces a specific local-change proposal and renewed affected checks, not automatic retention. |
| Cable/joint coverage report | Electrical/site reviewer: demonstrate detector margins or benign physical bounds for each hazardous class. Otherwise specify the required spatial/installation change and obtain approval. |
| Hub implementation package | Hub designer: actual Q/K1/K2/control/port-protection circuit, tolerances, state transitions, failure analysis, single-path proof tests and source/thermal/energy budgets. An unimplemented block diagram does not complete this deliverable. |
| Integrated qualification and service record | Qualified lab/site reviewer: each fault-matrix row linked to actual measurements, protective-failure tests, uncertainty and accepted recovery/replacement/return-to-service instructions; preserve failures and sample history. |

Only after those deliverables support the implemented revision may the design
owner propose evidence-backed C5 closure in REMEDIATION and the machine ledger.
An independently aborted recovery test is a failed DUT recovery result unless a
different **implemented and credited** safeguard achieved the required safe
outcome; the laboratory abort is never that production safeguard. Preserve
separate C4/W3/site/supplier holds. A bounded prototype may defer qualification
explicitly, but full C5 closure cannot contain an unprotected hazardous class.

## 4. Component Review

These corrections retain candidate identities for traceability, not as a hub BOM.

| Draft candidate or claim | Reviewed correction and remaining work |
| :--- | :--- |
| **TPS26600PWPR**, 40 milliohm / <=0.10 W | [TI SLVSDG2G][ti-tps2660] specifies total `R_ON` **150 milliohm typical**, 160 maximum at 25 C and 250 maximum over the specified junction-temperature range. At 1.5 A, `I^2 R` is 0.3375 W typical or 0.5625 W using the full-temperature resistance limit, not <=0.10 W. Limiting-state loss requires `(VIN-VOUT)*I` and transient thermal/SOA assessment. |
| **8.00 kohm +/-0.1% current setting** | `I_OL[A] = 12 / R_ILIM[kohm]` gives 1.50 A nominal. TI's 1.425-1.575 A limits expand to about **1.4236-1.5766 A** with resistor tolerance alone, before TCR and application allowances. Preserve the table's input/drop conditions; not a universal peak ceiling or adequate healthy-load margin. |
| **<250 ns latched disconnect** | Fast-trip response is **250 ns typical**, at roughly `1.87*I_OL + 0.015 A`, not at 1.5 A. The FET subsequently turns back on into limiting. **402 kohm MODE-to-RTN** provides latch-off only after thermal shutdown. MODE-open TPS26600 circuit-breaker operation retries; TPS26601 is a different option. An external latch must account for startup and fault-flag deglitch; no complete maximum disconnect time is established. |
| **SMCJ58CA input TVS** | [Littelfuse][lf-smcj] gives 58 V standoff, **64.4-71.2 V breakdown** and **93.6 V maximum clamp at 16.1 A, 10/1000 us, 25 C**. This is not protection for the eFuse's ordinary 62 V absolute maximum. TI's limited 70 V/10 ms/25 C allowance for IN and IN-OUT is not an unrestricted OUT allowance. Select a coordinated clamp, limiting impedance and adequately rated switch from the complete transient envelope. |
| **Series diode/FET for all polarity faults** | TPS26600 already has conditional reverse-input protection down to -60 V and reverse-current blocking; redundant series parts are not automatically needed. TI requires correct **RTN/GND** treatment: tying them together disables reverse-input protection. OUT-to-RTN remains **-0.3 to 62 V**; reverse-current blocking is not an energy rating. Protect control circuits and combined-port conditions too. |
| **REF5025ID + TLV1701, 36.8 V +/-0.2 V** | [REF5025ID][ti-ref50] has an 18 V maximum input; [TLV1701][ti-tlv1701] operates up to 36 V, with 40 V supply absolute maximum. They need an appropriately protected auxiliary rail. The historical 136.8 kohm/10 kohm divider gives **36.70 V nominal**, with a limited 36.51-36.89 V static screen, not a complete cutoff guarantee. Include bias/offset, temperature, noise, readiness, hysteresis and delay. An output-only monitor cannot validate an excessive input while disconnected before reset. |
| **MOV-14D101K / TMOV14RP115E** | Not interchangeable: [Bourns][bourns-mov] specifies **85 VDC MCOV / 165 V max clamp at 50 A** for the former; [Littelfuse][lf-tmov] specifies **150 VDC / 300 V at 50 A** for the latter. Neither clamps a 62 V power port safely by itself. TMOV's thermal function has specific abnormal-overvoltage conditions and requires containment of possible heating/arcing/venting; it is not proven 36 V damaged-GDT interruption. |
| **GMOV-14D500K station alternative** | [Bourns][bourns-gmov] describes a series GDT/MOV mechanism, not "back-EMF": 65 VDC MCOV, <=4 pF at the stated conditions, up to 800 V front-protection level and 150 V **typical** clamp. Its 16.5 mm diameter/20 mm height maxima do not establish a drop-in or prove every possible mounting impossible. No reviewed fit/recovery/containment is demonstrated; current station outline is **65 x 56 mm**, not 63 x 56. |

Use [the existing source-interface research](pcb/SOURCE_PROTECTION_RESEARCH.md#candidate-source-parts-and-behavior)
for the historical calculations and their limitations, not as permission to
populate those parts. No TVS, relay/disconnect, controller or surge branch is
selected by this review.

### Station Resistors

Do not turn the hub project into a second station BOM or resistor-selection task.
[ASSEMBLY](pcb/ASSEMBLY.md#reviewed-components) owns the implemented TE 35212K2FT
prototype population and [MATERIALS](MATERIALS.md#resistor-procurement-and-history)
owns the unimplemented Yageo production order. TE's nominal 2 W does not qualify
the actual two-layer/OneGel mounting, and prototype results do not qualify Yageo.
Keep station placement, lands, routing and topology unchanged.

Corrections to the draft's alternative table, without selecting replacements:

- **Yageo SR2512FK-7W2K2L:** [SR V.14, 2025-02-14][yageo-sr] gives 2 W for the
  7W option and **500/1000 V family working/overload ceilings**, not 200/500 V.
  Actual working voltage is also power/resistance limited. Pulse, thermal,
  land/process and source/model review remain, not "pending only W3".
- **Bourns CHP2512-FX-2201ELF / CRM2512-FX-2201ELF:** retain as unselected
  candidates. [CHP][bourns-chp] gives **250/500 V**, not 300/600 V, and mounting/
  board-temperature conditions for its 3 W rating; [CRM][bourns-crm] has a stated
  copper-area basis for 2 W. Do not transfer AEC-Q200 status from A/Q variants
  to an ordinary MPN, rank pulse margin from watts, or claim drop-in approval.
- **Vishay CRCW25122K20FKEGHP / TT PWC2512LF2K20F:** remain unselected.
  [CRCW-HP][vishay-hp]'s 1.5 W ambient and 2 W terminal-temperature conditions
  differ; [PWC][tt-pwc]'s 1.5/2 W ratings use different termination copper areas.
  Neither proves this assembly safely dissipates 0.756803 W per resistor.

`950 V / 2200 ohm` and `950^2 / 2200` are instantaneous stress screens only,
not pulse-energy, repetitive endurance or complete branch-voltage predictions.
GDT sparkover timing, clamping, overshoot and exact resistor pulse curves matter.

## 5. Implementation Sequence

The following work is **proposed**, not performed by this review. Keep a bounded
bench-evaluation scope possible without pretending unresolved field safety is
complete. Do not make this hub work a new prerequisite for station Gate P files.

### Phase 1: Interface And Protection Decisions

1. Identify the installed SmartFence/regional model, `LOOP` wiring, OEM protector,
   supply/backup and accepted earthing arrangement. Obtain acceptance of the
   nonstandard loop, selector and entrance protection; record loading limits.
2. Accept the exact switch article, factory links and DC/global-transfer application
   before assigning physical terminals. Produce a six-end harness schedule keyed
   to the canonical INSTALL matrix, including all source and sensing connections.
3. Complete the [C5 fault contract](#35-c5-limits-and-release-evidence) before
   selecting limits or crediting a detector. Establish the independently protected
   fixture scope, numerical stop conditions and sufficient sample allocation.
4. Execute the station retain-or-redesign decision and the separate cable/joint
   coverage assessment. Request approval for any necessary local or installation
   changes; do not freeze a hub-only field design with those obligations unresolved.
5. Implement the proposed independent shutdown/state architecture using actual
   parts and accepted port, thermal and insulation budgets. Complete the hub and
   remote coverage records before claiming a C5-complete design. Bounded prototypes
   can carry explicit qualification deferrals; no board size or arbitrary trip
   threshold substitutes for a resolved protection mechanism.

### Phase 2: Hub Sources And Layout

1. Create `hub-pcb/hub.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, `.kicad_dru`,
   local library tables/definitions, reviewed `BOM.csv` and a hub-specific
   `verification.json`. Use conventional numbered references where practicable;
   station diagnostic exceptions/approval hashes do not authorize hub warnings.
2. Keep libraries within the complete staged hub project using `${KIPRJMOD}`.
   Do not depend on `${KIPRJMOD}/../pcb/DogFence.pretty`: the current validator
   rejects that escape and an isolated hub snapshot would lack the dependency.
   Reused definitions must be deliberately reviewed and snapshotted locally.
3. Capture the field interconnect, TEST-only path, protected auxiliary power,
   Q/K1/K2 shutdown/proof-test paths and actual entrance branches as distinct
   domains. Review every connector pin, source-side tie and failure bypass.
4. Lay out to the accepted carrier, thermal and insulation requirements, with
   independent geometry guards for discharge paths, isolation, copper/drills,
   component seating and service access. Do not transfer station-specific 3 mm
   rules or footprint assumptions into a different surge assembly without review.

### Phase 3: Verification Tooling

1. Preserve existing station targets, `build/`, mirrors and release semantics.
   Prefer separate hub output/staging namespaces such as **`build-hub/`** and
   **`tmp/hub-manufacturing/`**. The station transaction quarantines/removes all
   of `build/`; merely using `build/hub/` is unsafe. Add scoped cleanup, locking
   and cross-board concurrency tests before enabling simultaneous builds.
2. Reuse tested parsing/export primitives, but explicitly separate project names,
   source/note inventories, geometry guards, net/BOM expectations, diagnostic
   reviews, manifests and mirrors. The present `scripts/manufacturing.py` is
   station-specific; a `--board` flag alone does not make its validators generic.
3. Add proposed `check-hub` and `prototype-hub` targets only after the complete
   hub pipeline exists; keep `make check` station behavior unchanged. Both
   transactions must retain strict diagnostics, pre/post source hashes, private
   exports, artifact validation and mode-specific publication gates. Hub holds
   and prototype-file authorization require their own review, not copied approval.
4. Use the CLI resolver's actually probed KiCad 9 invocation, tested here as
   `/snap/bin/kicad.kicad-cli`. Run project-aware native checks in complete
   Snap-accessible staging; retain readable and JSON reports on failure too.
   Extend unsupported geometry with tested validators, never silent exclusions.

### Phase 4: Models And Controlled Records

1. Reuse the 41-station solver, all 280 clean-cut cases and existing 615
   prospective inter-core fault cases. Add focused hub
   connectivity/state/fault tests, including both legacy backfeed/masking
   negative controls. A DC load-line test must not assert GDT extinction.
2. Test actual current/OV tolerances, auxiliary/startup/reset behavior, fast-trip
   versus latch timing, thermal loss, reversed input, energized output, shorted
   switch and port-clamp limits. Include the below-threshold faults in section 3
   as **missed by overcurrent-only protection**, not falsely passing arc-clearing
   tests. Add fault-matrix coverage for floating-EARTH bypasses, mixed cuts/faults,
   sensor/controller failures, Q short, each K/driver stuck closed, reset held,
   brownout and upstream stored energy. Sweep fault resistance/location and
   asymmetric/earth paths; do not treat the existing DC solver as a transient or
   spatial thermal model. Bench-test the actual states and single-path proof tests.
3. Create hub electrical and assembly/DFM records that own the accepted circuit,
   interface schedule, limits, source evidence and unclosed holds. Keep BOM
   identity in CAD/BOM and purchases in MATERIALS. Ship essential context within
   a self-contained hub package rather than relying only on this root plan.
4. Update INSTALL, ACCEPTANCE, RISKS, REMEDIATION and tooling guidance when an
   actual design changes their scope. Record numerical acceptance limits,
   instrumentation/uncertainty and required evidence before hardware tests.
   **Do not mark C5 resolved merely because a hub board or model exists.**

## 6. Verification And Acceptance

### File And Prototype Scope

For a separately authorized hub prototype-file release, require complete current
sources, reviewed exact population/sourcing, local libraries, native DRC/ERC with
no unreviewed warnings, full schematic/PCB/native-netlist/IPC connectivity checks,
and independent source/export geometry checks. Connectivity is compared by
terminal membership and supported coordinate tolerances, not "bit-level parity"
between unlike file formats.

Validate Gerbers/drills, signed-Y CPL, BOM, assembly data and archive contents;
require a matching hub revision/source/artifact manifest and explicit deferred
holds. Exercise failed/stale builds, mixed publication goals, scoped cleanup and
real serial/parallel publication. Rerun affected station regressions and refresh
its matching artifacts if shared tooling or controlled inputs change.

File verification does not authorize uploading, ordering, installation or surge
tests. Supplier CAM/placement, allocated parts, panel/process and received fit
acceptance are separate. The existing station Gate P does not automatically
authorize publication of a new hub design.

### Hardware And Field Scope

1. Verify the full accepted contact matrix and absence of unintended source/field
   ties with sources and field disconnected. Obtain rated DC/global-transfer
   evidence; static continuity alone cannot prove dynamic transfer isolation.
2. Qualify source loss, reversed input, reverse output energy, clamp behavior,
   independent interruption, latch/reset and continuous normal thermal duty
   against declared limits. Verify TEST/OFF labels and deliberate RUN restoration.
3. Measure RF operation with the actual transmitter/receiver and intended cable/
   station network, checking coverage, unwanted responses, branch stress and
   loop-alarm limitations. A resistor-only DC emulator is not an RF-equivalent
   4 km cable; remaining parallel cores can conceal a core break from the OEM alarm.
4. Use a qualified, independently protected fixture for powered recovery/fault/
   surge tests. Measure local branch voltage/current/temperature and energy,
   with independent abort and containment; do not rely on the hub current trip
   being evaluated. Execute every row of the C5 fault matrix and validate the
   numerical fault contract, including fresh/conditioned components, both surge
   polarities and relevant RLC/temperature/source extremes. A resistor mounted
   elsewhere is not proof of a damaged tube's internal/contact hot spot. Test
   residual energy and re-energization, and inhibit repeated restart after a
   failed test. Do not perform ad-hoc field
   lightning tests or use ordinary grounded instruments on exposed surge paths.
5. Complete all [C5 closure deliverables](#35-c5-limits-and-release-evidence),
   including the cable/joint and damaged-device reports, then close only
   evidence-supported scopes in REMEDIATION and the appropriate machine ledger.
   C4/C5/W3 and supplier/site holds remain until their actual
   criteria are met; direct-strike survival and a board-level kA rating are not
   acceptance claims.

### Review Evidence

The **initial 2026-09-15 review** changed the plan and its REMEDIATION handoff only.
It checked project requirements, source/control logic and manufacturer documents;
no schematic, PCB, BOM, library, rule, approval hash or generated artifact changed.
Retrieved PDF text supports the cited specification corrections, not fine drawing
inspection or acceptance of the actual supplied equipment.

| Command run during review | Result and scope |
| :--- | :--- |
| `python3 -B scripts/analyze_limits.py` | Exit 0; reproduced 280 clean-cut cases and the conditional below-threshold fault examples. |
| `python3 -B scripts/design_bounds.py` | Exit 0; reproduced the current TE 1.536239 A / 0.756803 W-per-resistor upper screen and its assumptions. |
| `TMPDIR=/tmp/opencode python3 -B -W error -m unittest discover -s tests -p test_electrical.py -v` | 23 tests PASS. |
| `TMPDIR=/tmp/opencode python3 -B -W error -m unittest discover -s tests -p test_design_bounds.py -v` | 14 tests PASS. |
| `git diff --check` and `git diff --no-index --check /dev/null HubImplementationPlan.md` | PASS, including the untracked plan. |
| Independent document reviews | RF/switch/earthing, protection corrections, local links and current-tooling constraints reviewed; no remaining scoped findings after removing the implied fuse-coordination approval. No full Markdown-renderer or external-link reachability test claimed. |

These are existing model regressions, not hub implementation or physical tests.
No native KiCad check or publication was run for this root-document-only review;
the existing station package was left untouched. No supplier/OEM acceptance,
upload, order, hardware qualification or issue closure is implied.

The **C5 planning follow-up on 2026-09-15** adds the three-obligation resolution
path, limited detector credit, ordered local recovery/failure alternatives,
fault matrix, Q/K1/K2 independence and state requirements, numerical acceptance
equations and five closure deliverables. This is an actionable design and
qualification plan, not a completed C5 protective circuit. Station changes remain
approval-required proposals; the existing station design and all release holds
are untouched. Follow-up verification is recorded in
[REMEDIATION](REMEDIATION.md#hub-c5-closure-planning), separately from the initial
review results above.

## 7. Source Register

Project authorities: [INSTALL](INSTALL.md#hub-wiring),
[ELECTRICAL](pcb/ELECTRICAL.md#4-powered-faults-c5-open),
[DESIGN_BOUNDS](pcb/DESIGN_BOUNDS.md),
[SOURCE_PROTECTION_RESEARCH](pcb/SOURCE_PROTECTION_RESEARCH.md),
[switch evidence](pcb/ENVIRONMENT_EVIDENCE.md#ca10a364-switch),
[ACCEPTANCE](ACCEPTANCE.md) and [REMEDIATION](REMEDIATION.md#issue-register).
Historical research retains its original inputs; this plan does not approve its
candidate circuits or rewrite purchasing history.

Primary references used for the corrections above are linked below. The Yageo
document is manufacturer-authored but distributor-hosted; the 4/8 kHz statement
is regional dealer evidence, not an installed-model manufacturer specification.

[dw-guide]: https://www.dogwatch.com/wp-content/uploads/2026/06/SmartFence_OwnersGuide_Rev.E.1-06.26.pdf
[dw-frequency]: https://dogfence.co.uk/about-us/robotic-lawn-mower-used-with-dog-fence/
[ti-tps2660]: https://www.ti.com/lit/ds/symlink/tps2660.pdf
[lf-smcj]: https://www.littelfuse.com/~/media/electronics/datasheets/tvs_diodes/littelfuse_tvs_diode_smcj_datasheet.pdf.pdf
[ti-ref50]: https://www.ti.com/lit/ds/symlink/ref50.pdf
[ti-tlv1701]: https://www.ti.com/lit/ds/symlink/tlv1701.pdf
[bourns-mov]: https://www.bourns.com/docs/product-datasheets/MOV14D.pdf
[lf-tmov]: https://www.littelfuse.com/~/media/electronics/datasheets/varistors/littelfuse_varistor_tmov_itmov_datasheet.pdf.pdf
[bourns-gmov]: https://www.bourns.com/docs/product-datasheets/GMOV.pdf
[yageo-sr]: https://www.lcsc.com/datasheet/C876850.pdf
[bourns-chp]: https://www.bourns.com/docs/product-datasheets/chp.pdf
[bourns-crm]: https://www.bourns.com/docs/product-datasheets/crm.pdf
[vishay-hp]: https://www.vishay.com/docs/20043/crcwhpe3.pdf
[tt-pwc]: https://www.ttelectronics.com/TTElectronics/media/ProductFiles/Resistors/Datasheets/PWC.pdf
[ruilon-smt]: https://www.ruilon.com.cn/Uploads/pdf/06-smd5050%20series_a3.pdf
[ruilon-earth]: https://www.ruilon.com.cn/Uploads/pdf/017-2rd-8%20series_a6.pdf
[tdk-dc-stack]: https://www.tdk-electronics.tdk.com/inf/100/ds/LN8-A1200DC-4-X1993B501.pdf
[gmov-failure]: https://www.bourns.com/docs/technical-documents/technical-library/gmov/Bourns_Meeting_Sustained_Overvoltage_Protection_with_Hybrid_Drop-In_Replacement_GMOV_White_Paper.pdf
