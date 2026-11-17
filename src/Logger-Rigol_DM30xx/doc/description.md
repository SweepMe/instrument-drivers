# Logger Rigol DM30xx

This driver reads the Rigol DM3058 and DM3058E 5½-digit digital multimeters with the RIGOL command set: one reading of
the chosen function per measurement point, with its range and reading rate set when the module is configured.

---

### Requirements:

- The instrument is connected by **GPIB** (DM3058 only; the address is set in Utility, by default 7), **USB**
  (USBTMC), **TCPIP** (DM3058 only) or **COM** (RS-232, 9600 baud, no parity; a null-modem adapter may be needed).
- GPIB and USBTMC need a VISA, e.g. NI-VISA, and for a GPIB adapter its driver (NI-488.2 for an NI GPIB-USB-HS).
- No further libraries are needed. Communication is handled by the SweepMe! port manager.
- Tested with a DM3058 (firmware 01.01.00.02.03.01) over GPIB with an NI GPIB-USB-HS.
- At the start of a run the driver switches the instrument to the RIGOL command set if another one (AGILENT or FLUKE)
  is active. Over COM it does not, since the command set query is not answered there; select RIGOL at the front panel.

---

### Usage:

- Choose the function with **Mode**, its **Range** and, where the function has one, its **Rate**.
- When the module is configured, the driver selects the function, the rate and the range. At every measurement point
  it takes one reading with the function's measure query (`:MEASure:VOLTage:DC?`, ...).
- An overloaded input, e.g. an open resistance input, reads `9.000000E+15`; the driver returns it as `inf`.
- Front-panel settings the driver does not touch (math functions, trigger, reading hold, filter) stay as they are and
  apply to the readings.

---

### Parameters:

- **Mode**: Voltage DC, Voltage AC, Current DC, Current AC, Resistance (two-wire), 4W Resistance, Capacitance, Diode,
  Continuity, Period or Frequency. Sequences saved with the former spelling "Periode" load as Period.
- **Range**: `Auto` or a fixed range of the mode, e.g. `200 mV` to `1000 V` for Voltage DC; for Period and Frequency it
  is the range of the input voltage. Not shown for Diode and Continuity.
- **Rate**: Fast (123 readings/s), Medium (20 readings/s) or Slow (2.5 readings/s). Only shown for voltage, current and
  resistance; the other modes have no rate.

---

### Measurement Output:

- **<Mode>**: the reading, named after the mode, in V (voltage, diode), A (current), Ohm (resistance, continuity), F
  (capacitance), s (period) or Hz (frequency).

---

### Communication commands:

For scripts, Instrument Control and agents the driver offers the instrument's functions as commands: the function
(`set_function`), range (`set_range`, `set_autorange`), rate (`set_rate`), the DC voltage input impedance and the AC
filters, one reader per function (`get_dc_voltage`, `get_resistance`, ...) and `get_reading(function)`, the math
functions (relative offset, statistics, dB, dBm, pass/fail limits), the trigger (source, auto interval, sample count,
single trigger, reading hold), the beeper, the command set, the error queue and the self test. Each has its read-back
where the instrument has a query.

---

### Known limitations:

- Autorange can be switched on and off, but not read back: the instrument has no query for it.
- Setting a fixed range switches autorange off; the manual says so for DC voltage, DC current and AC current.
- The range and rate queries are answered only while their function is selected.
- A reader also selects its function: `get_resistance` switches a meter in DC voltage to resistance.
- Changing the rate sets the interval of the AUTO trigger back to the rate's default (8, 50 or 400 ms).
- `is_new_reading` (`:MEASure?`) answered `TRUE` in every test, also without a new trigger, so it is not a reliable
  sign of a new reading.
- Not supported: the dual display (`:FUNCtion2`), the sensor measurement (only in the AGILENT command set), the
  interface and LAN settings, and the voltmeter-complete output.
- Over COM the measurement stopped after 17 to 25 s with a timeout in an earlier version of this driver; the cause is
  unknown. Afterwards the instrument had to be restarted before it answered on another interface.
