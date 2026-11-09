# Switch Keithley 622x

This driver uses the Keithley 6220 DC current source or the 6221 AC and DC current source as a DC current source.
The sweep value is the output current. For each measurement point, the driver also reads whether the current source is
in voltage compliance.

---

### Requirements:

- The instrument must be connected via **GPIB** or **RS-232** (**COM**). The Ethernet interface of the 6221 is not
  supported.
- For RS-232, the instrument must use 19.2k baud (factory default), no flow control, and the terminator `<LF>`
  (factory default).
- An interlock switch must be connected to the INTERLOCK connector on the rear panel and must be closed. Otherwise the
  output cannot be switched on and the instrument reports error `+402 Output blocked by interlock`. If no interlock
  switch is used, short-circuit the two screw terminals of the INTERLOCK connector on the rear panel, e.g. with a wire
  jumper. See "INTERLOCK" on page 2-4 of the Model 6220/6221 Reference Manual.
- No further libraries are needed. Communication is handled by the SweepMe! port manager.

---

### Usage:

- At the start of the run, the model is read with `*IDN?` and the instrument is reset with `*RST`.
- When the sequencer enters the branch, output low, inner shield, output response, analog filter, range, and
  compliance are set. Errors reported by the instrument afterwards are printed to the Debug widget (F2). Then the
  output is switched on. If the interlock is open, the run stops with an error message.
- When the sweep value changes, the new current is set.
- For each measurement point, the compliance state is read from the measurement condition register.
- At the end of the run, the output is switched off.
- The 622x does not measure. To measure the voltage across the device, use a voltmeter such as the Keithley 2182A with
  its own driver.

---

### Parameters:

- **SweepMode**: `Current in A`. The sweep value is the DC output current from -105 mA to 105 mA.
- **Range**: `Auto` or a fixed source range from `2 nA` to `100 mA`. Each range allows 5 % overrange. The run stops if
  the current exceeds the selected range.
- **Compliance in V**: Voltage compliance from 0.1 V to 105 V. Default 10 V.
- **Analog filter**: Enables the analog output filter, which reduces noise but slows down the output response.
- **Output response**: `Fast` or `Slow`. Only set for the Model 6221.
- **Output low**: `Floating` or connected to `Earth`.
- **Inner shield**: Connects the triax inner shield to `Output low` or to `Guard`.

---

### Measurement Output:

- **Current**: The set output current in A. This is the programmed value, not a measured current.
- **Compliance**: `True` if the current source is in compliance, i.e. the set current is not delivered to the load.

---

### Known limitations:

- Only DC current output is supported. Sweeps of the instrument, the AC waveform generator, Delta mode, Pulse Delta,
  and Differential Conductance are not available in this driver.
- For the Model 6220, the **Output response** is not set because the 6220 does not have this setting.
