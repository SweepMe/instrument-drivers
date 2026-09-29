# Logger Keithley 6517B

This driver measures currents with the Keithley 6517B electrometer. For each measurement point, one reading is
triggered and read back with `READ?`. Optionally, the built-in voltage source applies a constant voltage during the
run, e.g. to source voltage and measure current (SVMI) for high-resistance measurements.

---

### Requirements:

- The instrument must be connected via **GPIB** or **RS-232** (**COM**). The interface must be enabled in the menu of
  the instrument.
- For RS-232, the baud rate of the instrument must be set to 9600 and the terminator to `<CR>`.
- No further libraries are needed. Communication is handled by the SweepMe! port manager.

---

### Usage:

- At the start of the run, the instrument is reset with `*RST`, and line sync is set.
- When the sequencer enters the branch, the current function, filters, integration time, zero correction, and range
  are set. If **Use voltage source** is checked, range, voltage, limit, and LO connection of the voltage source are
  set as well. Errors reported by the instrument afterwards are printed to the Debug widget (F2).
- If **Use voltage source** is checked, the output is switched on after the configuration and switched off at the
  end of the run. If it is not checked, the output of the voltage source is not touched and stays off after `*RST`.
- For each measurement point, one reading is triggered and read back in the same step.
- The **Source voltage in V** can be varied during the run by using a parameter in this field. The new voltage is
  then applied without configuring the instrument again.

---

### Parameters:

- **Range**: Current range, `Auto` or a fixed range from `20 mA` to `2 fA`. The fixed range is set via the expected
  reading, so the instrument selects the lowest range that covers it.
- **Rate**: Integration time: `Very Fast` (0.01 PLC), `Fast` (0.1 PLC), `Medium` (1 PLC), `Slow` (10 PLC).
- **Average**: Number of readings that are averaged by the repeating filter of the instrument. `1` switches the
  filter off.
- **Line sync**: Synchronizes the integration to the power line frequency.
- **Perform zero check**: Acquires a zero correct value with zero check enabled on the 20 pA range. The value is
  valid for all higher ranges.
- **Use zero correction**: Subtracts the zero correct value from the readings. Use it together with
  **Perform zero check** to acquire a new value at the start of the branch.
- **Use voltage source**: Enables the voltage source. The following fields are only shown if it is checked.
- **Source voltage in V**: Voltage of the voltage source. An empty field is interpreted as 0 V.
- **Source voltage range**: `100 V` (5 mV resolution) or `1000 V` (50 mV resolution).
- **Source voltage limit in V**: Absolute voltage limit of the voltage source. The run is stopped if the source
  voltage exceeds this limit or the selected range.
- **Source voltage connection**:
  - `V-SOURCE HI and INPUT HI`: Voltage source LO is connected internally to ammeter LO (SVMI configuration).
  - `V-SOURCE HI and V-SOURCE LO`: The voltage source is used as an independent source.

---

### Measurement Output:

- **Current**: Measured current in A. An overflow reading is returned as `9.9e37`, a reading during zero check as
  `9.91e37`.

---

### Known limitations:

- Only current measurements are supported. Voltage, resistance, and charge measurements of the instrument are not
  available in this driver.
- The fixed ranges `2 pA` to `2 fA` are not listed in the manual of the 6517B, whose lowest current range is 20 pA.
- The voltage source cannot be used as the sweep value of the driver.
- The current limit of the voltage source is given by the range (10 mA for 100 V, 1 mA for 1000 V) and is not set by
  the driver.
- The communication timeout is 10 s. Many averaged readings with a slow rate can exceed it.

---

### Caution:

- The voltage source can output up to 1000 V. Use it with a test fixture that has a safety interlock, such as the
  Keithley 8009 Resistivity Test Fixture.

---

### Related Drivers:

- `Logger-Keithley_6514` and `Logger-Keithley_6485`/`Logger-Keithley_6487` for the other Keithley electrometers and
  picoammeters.
