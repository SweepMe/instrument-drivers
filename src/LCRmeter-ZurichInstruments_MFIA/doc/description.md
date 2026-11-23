# Zurich Instruments MFIA

Driver for the Zurich Instruments MFIA impedance analyzer. It also works with an MFLI that has
the MF-IA impedance analyzer option, as the driver enables the impedance unit explicitly.

The instrument is not addressed via a serial or GPIB port. The driver uses the LabOne API and
lists the device IDs (e.g. `dev1234`) that the LabOne Data Server can reach. LabOne must be
installed and its Data Server must be running.

## DC bias

The DC bias across the device under test can come from three different sources, selected with
the **BiasSource** field. This matters for C-V measurements, where the bias is the swept quantity.

### Internal

The internal bias source of the instrument is used, nodes `/dev.../imps/0/bias/enable` and
`/dev.../imps/0/bias/value`. No cabling is needed.

The usable range is limited by the input stage. In 4-terminal mode the bias is restricted to
roughly +/-3 V by the common mode input range of the voltage inputs. In 2-terminal mode the
voltage inputs are not connected, so a larger bias is possible.

### Output range

The instrument generates the bias of the sources "Internal" and "Aux Output" as an offset on the
Signal Output. The output range (`/dev.../imps/0/output/range`, 10 mV, 100 mV, 1 V or 10 V) must
cover the drive amplitude plus the bias, otherwise the instrument clamps the bias without an
error, e.g. to +/-1 V in the 1 V range.

The driver therefore selects the smallest output range that covers the peak drive amplitude plus
the bias, but at least the 1 V range when a bias source is used. During a bias sweep the range is
only increased, never decreased, so that the output is not switched back and forth. A smaller
range gives a cleaner signal, so a sweep that reaches more than about 1 V runs in the 10 V range
from that point on.

After every bias change, the driver reads the bias back from the instrument and stops the
measurement if it differs from the requested value, e.g. because of the 4-terminal limit.

The driver also switches off the automatic drive control (`/dev.../imps/0/auto/output`), so that
the drive amplitude entered in SweepMe! is used.

### Aux Output (cable to Aux In 1)

A larger bias range is reached by using an Auxiliary Output as a DC source and adding it to the
Signal Output. This requires a cable on the front panel:

1. connect the selected **Aux Output** to **Aux Input 1**

The driver then sets the Auxiliary Output to Manual mode (`outputselect = -1`, `preoffset = 0`,
`scale = 1`), writes the bias to `/dev.../auxouts/n/offset`, and switches on
`/dev.../sigouts/0/add`, which adds the signal present at Aux Input 1 to the Signal Output.

Notes:

* Aux Input 1 is the only input that the add path reads, so the cable always ends there. The
  **BiasAuxOutput** field only selects which Auxiliary Output the cable starts at.
* The sum of AC drive amplitude and DC bias must stay inside the 10 V full scale of the Signal
  Output.
* With a differential output the added signal acts as a common mode offset.

### External

The bias is supplied by a separate instrument, for example an SMU or a bias tee. The driver does
not change any bias node of the MFIA, and it cannot sweep the bias. Sweep the bias with the driver
of the instrument that supplies it. The returned "Voltage bias" value is not a number in this case.

## List sweep

Select **List sweep** as Sweep value to let the instrument's Sweeper module run a whole frequency or bias sweep at
each measurement point. This is much faster than a sweep point by point through SweepMe!, because the Sweeper sets
each point, waits for the filters and records the result without a round trip to SweepMe!.

* **Sweep mode** selects the swept quantity: `Frequency in Hz` (node `oscs/<n>/freq` of the oscillator that drives the
  impedance unit) or `Voltage bias in V` (node `imps/0/bias/value` for the bias source "Internal",
  `auxouts/<n>/offset` for "Aux Output"). An external bias cannot be swept.
* **Start value**, **End value** and **Step width** or **Points (lin.)** / **Points (log.)** define the sweep. The
  Sweeper only runs equally spaced points, so a step width must divide the range into equal steps, and custom value
  lists are not supported. A logarithmic sweep needs start and end values above 0.
* **dual sweep** adds a second sweep from the end back to the start value.
* **Delay time** is the minimum settling time in s before each point is recorded (`settling/time`).
* **Average** sets the minimum number of samples averaged per point (`averaging/sample`).
* In the Parameters box, **Sweep settling inaccuracy** (`settling/inaccuracy`, 1e-13 to 0.1, default 1e-3) sets how
  far the filters must have settled before a point is recorded, and **Sweep averaging in TC** (`averaging/tc`) sets a
  minimum averaging time in demodulator time constants. The demodulator bandwidth is chosen by the Sweeper (auto).
* The **Step mode** can still change the other quantity between list sweeps, e.g. a bias step for each frequency
  sweep.
* For a bias sweep, the output range is chosen in advance for the largest bias of the sweep.

Each returned variable then holds the values of the whole sweep. While the Sweeper runs, it also controls the input
ranges; the driver does not autorange in list sweep mode.

## Limits

Values below are taken from the MFIA specifications, see "Further reading".

* The current through the device under test should stay below 10 mA, the largest current input
  range of the instrument. Above that the current input overflows and the measurement is invalid.
* Damage thresholds are given as voltages, not as a current: -5 V to +5 V at the Current Signal
  Input, -5 V to +5 V differential at the Voltage Signal Input, and -12 V to +12 V at the Signal
  Output. A bias beyond these values needs an external bias tee that keeps the DC away from the
  instrument inputs.
* The Signal Output DC offset range equals the selected output amplitude range, up to +/-10 V.
  This is what bounds the "Aux Output" bias path, since AC drive and DC bias share that range.
* None of the bias sources can source a current. Selecting "Current bias in A" raises an error.

## Returned values

| Variable | Unit | Description |
| --- | --- | --- |
| R | Ohm | real part of the impedance |
| X | Ohm | imaginary part of the impedance |
| Frequency | Hz | measurement frequency |
| Voltage bias | V | DC bias read back from the selected bias source |

In list sweep mode, each variable is an array with one value per sweep point. In a bias sweep, "Voltage bias" holds
the sweep points.

## Further reading

* MFIA user manual, specifications: <https://docs.zhinst.com/mfia_user_manual/specifications.html>
* MFIA user manual, node tree: <https://docs.zhinst.com/mfia_user_manual/node_definitions.html>
* MFIA user manual, Impedance Analyzer tab:
  <https://docs.zhinst.com/mfia_user_manual/functional_description/impedance_analyzer.html>
* DC biased impedance measurements using an external bias tee:
  <https://www.zhinst.com/americas/en/blogs/dc-biased-impedance-measurements-using-external-bias-tee/>
