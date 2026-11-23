# SMU Keithley 2400

This driver sources voltage or current with a Keithley 2400 SourceMeter, using its SCPI command set, and returns
voltage and current: the measured value of the quantity that is not sourced, and for the sourced one the
programmed level or its measurement, see *Usage*. Besides single source and measure points, it offers a list
sweep in which the instrument steps through up to 100 source values by itself and returns all readings at once.

---

### Requirements:

- The instrument must be connected via **GPIB** or **COM** (RS-232).
- No further libraries are needed. Communication is handled by the SweepMe! port manager.
- For COM, the driver uses 9600 baud and `\r` (CR) as end-of-line character. Set the same on the front panel:
  MENU -> COMMUNICATION -> RS-232 (baud rate 9600, terminator `<CR>`).
- The base timeout of the port is 10 s. The driver extends it by the time a `READ?` can take: for each point the
  trigger delay, the source delay (5 ms for the automatic delay) and six times the integration time (NPLC x 20 ms x
  Average). A list sweep of 100 points with 0.1 s + 0.1 s delays at Speed `Fast` therefore gets about 21 s more.
- For GPIB, the driver switches the instrument from the 488.1 protocol to the SCPI protocol at the start of the run
  if the firmware is newer than 1998, as the 488.1 protocol can lead to timeout errors with several instruments on
  the bus. If that fails, select SCPI on the front panel: MENU -> COMMUNICATION -> GPIB -> GPIB PROTOCOL.

---

### Supported instruments:

- Keithley 2400 SourceMeter.
- Other models of the 24xx series with the same SCPI command set are likely to work too, but the driver does not
  know their voltage and current limits and does not check the source level or the compliance against them.

---

### Usage:

- The sweep value is the source level: a voltage in V if **SweepMode** is `Voltage in V`, a current in A if
  **SweepMode** is `Current in A`.
- At the start of the run, the instrument is reset, the status registers are cleared and the beeper is switched off.
  Terminals, source function, compliance, range, integration time, sensing and averaging are configured, then the
  output is switched on.
- For each measurement point the new source level is set, the driver waits until the instrument has completed it
  (`*OPC?`), and one `READ?` returns voltage and current. For a quantity that is not measured, the instrument
  returns the programmed source level. The driver selects the measured quantity with `:SENS:FUNC` (as earlier
  versions did); with concurrent sensing, the default, this adds a function and leaves the others on. After the
  reset at the start of the run only current is measured, so:
  - in voltage-source mode **Voltage** is the programmed level and **Current** the measurement, unless a
    current-source branch ran before in the same run, which also switched on the voltage measurement;
  - in current-source mode both **Voltage** and **Current** are measurements.
- The readings are requested in the measure phase and read in the call phase, so that several instruments of one
  sequencer branch measure at the same time.
- At the end of the run the output is switched off, the instrument returns to 2-wire sensing, front terminals,
  1 NPLC and no averaging, and the control goes back to the front panel.

---

### Parameters:

- **SweepMode**: `Voltage in V` or `Current in A`. Selects which quantity is sourced; the other one is measured.
  Sequences saved with the former labels `Voltage [V]` and `Current [A]` still work.
- **RouteOut**: `Front` or `Rear` terminals.
- **Speed**: Integration time in power line cycles: `Very fast` = 0.01 NPLC, `Fast` = 0.1 NPLC, `Medium` = 1 NPLC,
  `Slow` = 10 NPLC.
- **Range**: `Auto` or a fixed current range from 10 nA to 1 A. With **SweepMode** `Voltage in V` it is the current
  measurement range, with `Current in A` the current source range. The voltage range always uses auto ranging.
  The 2400 has no 10 nA and 100 nA ranges: the value is the expected reading, and the instrument selects the lowest
  range that covers it, so both options select its lowest range, 1 µA. The options stay for saved sequences and
  for 24xx models with lower ranges.
- **Compliance**: The current limit in A while voltage is sourced, or the voltage limit in V while current is
  sourced. Must be a finite number; the instrument takes signed values (2400: -1.05 to 1.05 A, -210 to 210 V)
  and checks the range itself.
- **Average**: Number of readings from 1 to 100 that the repeating average filter of the instrument averages into
  one value. 1 switches the filter off.
- **4wire**: If checked, remote sensing (4-wire) is used, otherwise local sensing (2-wire).

### List sweep

Select `List sweep` as sweep value of the SMU module to let the instrument run a whole sweep at one measurement
point. The driver then returns the variable **Timestamp** in addition, and each of the three variables is a list
with one value per sweep point.

- **ListSweepType**: `Sweep` calculates the values from start, end and step width or points; `Custom` takes the
  values from **ListSweepCustomValues**, separated by commas.
- **ListSweepStart**, **ListSweepEnd**: First and last source value of a `Sweep`.
- **ListSweepStepPointsType**: `Step width:` derives the number of values from **ListSweepStepPointsValue** as
  `round(|end - start| / |width| + 1)`, the one added before rounding, and spaces the values evenly between start
  and end value. The actual distance can differ from the width entered: from 0 to 1 V with 0.4 V gives
  `round(3.5) = 4` values 0.333 V apart, with 2 V `round(1.5) = 2` values. A width of 0 needs start and end value to
  be equal and gives one point. A sweep of one point uses the start value only. `Points (lin.):` and
  `Points (log.):` use the value as number of linearly or logarithmically spaced values. A logarithmic sweep needs
  start and end values of the same sign, neither of them 0.
- **ListSweepDual**: If checked, the sweep returns to the start value. A linear sweep uses the end value once, a
  logarithmic sweep twice.
- **ListSweepHoldtime**: Source delay in s between setting a source value and its measurement. Empty uses the
  automatic delay of the instrument. 0 to 999.9999 s.
- **ListSweepDelaytime**: Trigger delay in s between the trigger and setting the source value. Empty uses the
  default trigger delay of 0 s. 0 to 999.9999 s.
- The instrument takes at most 100 values, the way back of a dual sweep included; a sweep with more points stops
  the run with an error message before anything is sent.
- If the instrument returns fewer readings than the sweep has points, the run stops with an error message.
- Outside a list sweep, the driver sets the automatic source delay and a trigger delay of 0 s, so the settings of a
  list sweep in a previous branch do not remain.

---

### Returned values:

- **Voltage** in V and **Current** in A, and in a list sweep **Timestamp** in s, the time stamp of each reading.
- The instrument returns `+9.9e37` for an overflow reading and `+9.91e37` (not a number) for a value that was not
  measured. The driver passes both on unchanged.

---

### Communication commands:

The driver offers its instrument commands for scripts and Instrument Control, among others `get_identification`,
`set_output`, `set_voltage`, `set_current`, `set_current_compliance`, `set_voltage_compliance`, the range, NPLC,
sensing and filter setters, `set_voltage_list` / `set_current_list` with `set_trigger_count` for list sweeps, and
`get_voltage_current_time`, which runs one `READ?` and returns voltages, currents and time stamps.

A list sweep from a script, after `reset()` (which senses current):

```python
driver.set_source_function("VOLT")
driver.set_source_mode("VOLT", "LIST")  # the list itself does not select list mode
driver.set_sense_function("CURR")  # for a current list: set_sense_function("VOLT")
driver.set_voltage_list([0.0, 0.5, 1.0])  # for a current list: set_current_list
driver.set_trigger_count(3)  # the number of values
driver.set_source_auto_clear(False)
driver.set_output(True)  # the output must be on before READ?
try:
    voltages, currents, times = driver.get_voltage_current_time()
finally:
    driver.set_output(False)  # automatic output-off is off, so the output stays on otherwise
```

For a current list use `"CURR"` in the first two calls. `set_trigger_delay` and `set_delay` set the delays.

The methods `set_sweep` and `set_listvalues` of earlier versions are gone. They were helpers of the list sweep of
the SMU module and took GUI texts; their steps are the commands above. `set_delay` now names its parameter
`source_delay` instead of `delay_in_s`: scripts that pass it as a keyword must use the new name, positional calls
are unchanged.

---

### Known limitations:

- On GPIB, the control is returned to the front panel with the go-to-local message of the GPIB controller. If the
  interface cannot send it, a note is written to the debug log; press LOCAL on the front panel then.
