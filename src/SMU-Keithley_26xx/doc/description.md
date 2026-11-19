# SMU Keithley 26xx

This driver sources voltage or current and measures both quantities with source measure units of the
Keithley 2600 series that use the TSP command set. One driver instance controls one channel of the
instrument. Both channels can be used at the same time by adding two instances that share the same
port. A pulse mode based on the `ConfigPulse` factory scripts of the instrument is available, and a
list sweep in which the instrument steps through a list of source values by itself and can send an
output trigger at each step.

---

### Requirements:

- The instrument must be connected via **GPIB**, **USB** (USBTMC), **TCPIP**, or **COM** (RS-232).
- No further libraries are needed. Communication is handled by the SweepMe! port manager. For COM the
  driver uses 115200 baud and `\n` as end-of-line character, the timeout is 10 s for all interfaces.
- The instrument must use the **TSP command set**. If it is switched to the 2400 SCPI emulation mode,
  none of the commands of this driver are understood.
- Instruments that are linked via TSP-Link can be reached through the instrument that is connected to
  the port, see **TSP-Link node**. The TSP-Link network must already be initialized (node numbers set
  and the link reset on the front panel or with `tsplink.reset()`). The reset must be repeated whenever
  one of the linked instruments was switched off or the TSP-Link cabling was changed. The driver does
  not change the TSP-Link configuration.
- The models 2604B, 2614B, and 2634B have no TSP-Link interface and can only be used with
  **TSP-Link node** = `Local`.

---

### Supported instruments:

- Source measure units of the Keithley 2600 series whose channels are addressed as `smua` and `smub`.
- On single channel models only **Channel** = `Ch A` can be used.
- The driver does not know the voltage and current limits of the individual model and does not check
  the source level or the compliance against them.

---

### Usage:

- Add one instance of the driver for each channel that is used. If both channels of one instrument are
  used, both instances must be configured to the same port. The driver counts the instances on the
  port and shares the connection.
- The sweep value is the source level: a voltage in V if **SweepMode** is `Voltage in V`, a current in
  A if **SweepMode** is `Current in A`.
- At the start of the run, the channel is reset, the error queue is cleared, and a single autozero is
  performed whose reference values are reused for all following measurements. Source function, ranges,
  sense mode, filter, and integration time are configured, then the output is switched on.
- For each measurement point the new source level is sent, and voltage and current are read back with
  a single `smuX.measure.iv()` query.
- At the end of the run the output is switched off, the channel returns to local sensing, and the
  averaging filter is switched off. The channel is not reset, so the last source level stays
  programmed while the output is off.
- If the instrument reports a reading above `1e37`, which is its overflow value, both **Voltage** and
  **Current** are returned as `nan` for that measurement point.

---

### Parameters:

- **SweepMode**: `Voltage in V` or `Current in A`. Selects which quantity is sourced. The other
  quantity is measured.
- **Channel**: `Ch A` or `Ch B`, mapped to `smua` and `smub`.
- **TSP-Link node**: `Local` addresses the instrument that is connected to the port. `Node <N>`
  addresses the instrument with TSP-Link node number N through the connected instrument, so all
  commands are sent as `node[N].smua...`. All channels of a TSP-Link network can then share one port,
  e.g. four instances with `Node 1` to `Node 4`. At the start of the run, the driver checks that
  `tsplink.state` is `online` and that the reset of the channel does not create an entry in the error
  queue. Otherwise, e.g. if the node number is not part of the network or the instrument has no
  channel B, the run stops with an error message. Settings saved before this field existed use `Local`.
- **4wire**: If checked, the channel uses remote sensing (`SENSE_REMOTE`), otherwise local sensing
  (`SENSE_LOCAL`). Remote sensing needs the sense terminals to be wired.
- **RouteOut**: Only `Rear` is available, as the 26xx series has no front terminals.
- **Speed**: Integration time of the measurement in power line cycles: `Fast` = 0.1 NPLC,
  `Medium` = 1 NPLC, `Slow` = 10 NPLC. Ignored in pulse mode, see below.
- **Range**: Range of the current measurement. The voltage is always measured with auto ranging.
  - `Auto`: auto ranging without restriction.
  - `Limited <value>`: auto ranging, but the instrument does not range below `<value>`. This avoids
    the settling time of the lowest ranges while keeping the resolution of the higher ones.
  - `Fixed <value>`: auto ranging is switched off and `<value>` is used as fixed range.

  Ignored in pulse mode, where the ranges are derived from **Compliance**.
- **Average**: Number of readings that are averaged. Values above 1 switch on the repeating average
  filter of the instrument. In pulse mode this is the number of pulses per measurement point instead.
- **Compliance**: The limit of the quantity that is not sourced, entered in the SI unit of that
  quantity: a current in A if a voltage is sourced, a voltage in V if a current is sourced. In pulse
  mode the value is additionally used as source range and as measurement range.

The following fields are only used if **CheckPulse** is checked:

- **CheckPulse**: Switches on the pulse mode.
- **PulseMeasTime**: Length of the measurement window inside the pulse, as a percentage of
  **PulseOnTime**. It is converted into an integration time with
  `NPLC = PulseOnTime * PulseMeasTime / 100 * 50`, which assumes a line frequency of 50 Hz. See
  *Known limitations* for the default value of this field.
- **PulseOnTime**: Pulse length in s. Values below 200 µs are raised to 200 µs.
- **PulseOffTime**: Time between two pulses in s. Values above 3 s are reduced to 3 s. Values below
  200 µs are replaced by 200 ms, not by 200 µs.
- **PulseOffLevel**: Source level between the pulses, in V or A depending on **SweepMode**.

The following fields are only used if `List sweep` is selected as **Sweep value** (see *List sweep*):

- **Type**: `Sweep` calculates the source values from start value, end value and step width or number
  of points. `Custom` uses the **Custom values**.
- **Start value**, **End value**: First and last source value, in V or A depending on **SweepMode**.
- **Step width** / **Points (lin.)** / **Points (log.)**: With `Step width` the sweep goes from the
  start value in steps of this width and stops at the last value that does not go beyond the end value.
  `Points (lin.)` and `Points (log.)` distribute the given number of points linearly or logarithmically
  between start and end value, including both. A logarithmic sweep needs start and end value of the
  same sign, both not 0.
- **dual sweep**: Adds the way back from the end value to the start value; the end value is used once.
- **Custom values**: Source values separated by commas, semicolons or line breaks.
- **Hold time in s**: Time between the starts of two steps, set by a trigger timer of the instrument.
  Empty or 0 steps through the list as fast as possible. The hold time must be longer than the
  measurement of one point, see *List sweep*.
- **Delay time in s**: Settling time between setting the source value and the measurement
  (`smuX.measure.delay`). Empty uses the automatic, range dependent delay of the instrument.
- **Trigger out line**: Digital I/O line (1 to 14) that sends an output trigger at each step, or `None`.
- **Trigger out event**: `Source complete` sends the trigger when the new source value is set,
  `Measure complete` when the measurement of the step is done.
- **Trigger out polarity**: `Low pulse` (`digio.TRIG_FALLING`) or `High pulse` (`digio.TRIG_RISINGM`).
- **Trigger out pulse width in s**: Length of the output trigger pulse, 10 µs by default.

---

### Measurement Output:

- **Voltage**: Voltage in V. The sourced value in `Voltage in V` mode, the measured value in
  `Current in A` mode.
- **Current**: Current in A. The measured value in `Voltage in V` mode, the sourced value in
  `Current in A` mode.

In pulse mode both values are the average over the readings of the pulse buffer `nvbuffer1`, whose
length is given by **Average**.

In a list sweep, **Voltage** and **Current** are lists with one value per step, and a third output is
added:

- **Time**: Time in s of each measurement, relative to the first measurement of the sweep.

---

### Note on pulse mode:

- The pulse mode uses the `ConfigPulseVMeasureI` and `ConfigPulseIMeasureV` factory scripts of the
  instrument. The pulse is configured in `apply`, started with `InitiatePulseTest` when the
  measurement point is triggered, and read back from `nvbuffer1`.
- All auto ranges are switched off in pulse mode. Source range and measurement range are set to the
  value of **Compliance**.
- If two instances of the driver run on the same port and **CheckPulse** is checked in both, the
  driver switches to dual pulse mode. Both pulses are then started together with
  `InitiatePulseTestDual`, and the on-time of channel B is extended by 40 µs so that the pulse of
  channel B encloses the pulse of channel A. Channel A reads the buffers of both channels and hands
  the values of channel B over to the second instance.
- In dual pulse mode both channels use the **Average** value of the instance that acts as master.

---

### List sweep:

- In a list sweep, the instrument runs the whole sweep by itself. SweepMe! sends the source values
  once per use of the module and starts the sweep once per measurement point. The instrument then sets
  each source value, waits for the delay time, measures current and voltage, and moves on to the next
  value when the trigger timer expires. All values are read back when the sweep is complete.
- Select `List sweep` as **Sweep value** in the SMU module. The option appears because the driver
  supports the list sweep fields. The SweepEditor and the other sweep value sources are not used.
- The output trigger is a TTL pulse on the selected pin of the DIGITAL I/O connector. It can trigger
  other instruments at each step. The models 2604B, 2614B, and 2634B have no digital I/O trigger lines,
  the run then stops with an error message if a trigger out line is selected.
- Each channel uses its own trigger timer (timer 1 for channel A, timer 2 for channel B). Timer and
  digital I/O line are reset at the end of the run.
- At the end of the sweep the source returns to its idle level, which is 0 after the reset at the
  start of the run.
- The hold time must be longer than the time to measure one point: delay time plus integration time
  times **Average**, plus the time of auto ranging. The driver checks delay time plus integration time
  at a line frequency of 50 Hz. If a step still takes longer than the hold time, the instrument misses
  a timer event and the sweep stops before the last point. The driver then aborts the sweep and stops
  the run with an error message. A fixed **Range** and a fixed delay time avoid this.
- List sweep cannot be combined with the pulse mode or with a remote **TSP-Link node**.
- If both channels run a list sweep, the two sweeps run one after the other, not synchronized.
- The source values are sent as a table named `sweepme_list` to the instrument, in chunks of 50
  values.

---

### Known limitations:

- The conversion of **PulseMeasTime** into NPLC assumes a line frequency of 50 Hz. At 60 Hz the
  measurement window is shorter than requested by the ratio 50/60.
- Only the current measurement range can be selected. The voltage measurement range and both source
  ranges always use auto ranging in the non-pulsed mode.
- The error queue is only cleared at the start of the run. Apart from the check of a remote node at
  the start of the run, the driver does not read it back, so instrument-side errors do not stop the
  measurement and only show up as unexpected readings.
- The driver does not report whether the instrument is in compliance. A reading in compliance looks
  like a regular reading.
- The guard terminals and the high-capacitance mode of the instrument are not supported.
- Pulse mode is only available for **TSP-Link node** = `Local`. A remote node with pulse mode stops
  the run with an error message.
- Instances with a remote node do not count for the dual pulse mode. The two channels of the
  instrument connected to the port can still be pulsed together while further instances on the same
  port measure on remote nodes.
- Measurements on remote nodes are sequential, like the two channels of one instrument. Each reading
  is requested and returned through the instrument connected to the port.
- While the driver communicates through TSP-Link, all linked instruments are in remote operation and
  stay there after the run, until the EXIT (LOCAL) key is pressed on one of them.
- The channel is not reset at the end of the run, and the source level is not returned to zero before
  the output is switched off.
