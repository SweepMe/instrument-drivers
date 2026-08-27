# SMU Keithley 26xx

This driver sources voltage or current and measures both quantities with source measure units of the
Keithley 2600 series that use the TSP command set. One driver instance controls one channel of the
instrument. Both channels can be used at the same time by adding two instances that share the same
port. A pulse mode based on the `ConfigPulse` factory scripts of the instrument is available.

---

### Requirements:

- The instrument must be connected via **GPIB**, **USB** (USBTMC), **TCPIP**, or **COM** (RS-232).
- No further libraries are needed. Communication is handled by the SweepMe! port manager. For COM the
  driver uses 115200 baud and `\n` as end-of-line character, the timeout is 10 s for all interfaces.
- The instrument must use the **TSP command set**. If it is switched to the 2400 SCPI emulation mode,
  none of the commands of this driver are understood.
- Only the local node is addressed. Instruments that are reached through TSP-Link as a remote node are
  not supported.

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

---

### Measurement Output:

- **Voltage**: Voltage in V. The sourced value in `Voltage in V` mode, the measured value in
  `Current in A` mode.
- **Current**: Current in A. The measured value in `Voltage in V` mode, the sourced value in
  `Current in A` mode.

In pulse mode both values are the average over the readings of the pulse buffer `nvbuffer1`, whose
length is given by **Average**.

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

### Known limitations:

- The default of **PulseMeasTime** is `200e-6`, which is not a meaningful percentage. Used as it is,
  it results in an integration time far below the minimum of the instrument, so the instrument falls
  back to its smallest NPLC value. Enter a percentage such as `50` instead.
- The conversion of **PulseMeasTime** into NPLC assumes a line frequency of 50 Hz. At 60 Hz the
  measurement window is shorter than requested by the ratio 50/60.
- Only the current measurement range can be selected. The voltage measurement range and both source
  ranges always use auto ranging in the non-pulsed mode.
- The error queue is only cleared at the start of the run. The driver does not read it back, so
  instrument-side errors do not stop the measurement and only show up as unexpected readings.
- The driver does not report whether the instrument is in compliance. A reading in compliance looks
  like a regular reading.
- The guard terminals and the high-capacitance mode of the instrument are not supported.
- The channel is not reset at the end of the run, and the source level is not returned to zero before
  the output is switched off.
