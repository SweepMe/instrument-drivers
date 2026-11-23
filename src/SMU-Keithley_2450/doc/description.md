# SMU Keithley 2450

This driver sources voltage or current and measures both quantities with a Keithley 2450 SourceMeter. It works with
the TSP command set of the instrument and with the SCPI command set of the Keithley 2400 emulation (`SCPI2400`).

---

### Requirements:

- The instrument must be connected via **USB** (USBTMC), **GPIB** or **TCPIP** (LAN).
- No further libraries are needed. Communication is handled by the SweepMe! port manager. The base timeout is 10 s;
  the driver extends it by the time a measurement can take, see **Average**.
- The command set is read from the instrument with `*LANG?` when the run starts:
  - `TSP`: the TSP commands are used.
  - `SCPI2400`: the SCPI commands of the 2400 emulation are used.
  - `SCPI` (the native SCPI of the 2450): the driver sends the 2400 emulation commands as well, which the native
    command set does not fully understand. Use `TSP` or `SCPI2400` instead: MENU -> System -> Settings ->
    Command Set, then restart the instrument.
  - Any other answer, e.g. none at all, stops the run before the instrument is reset.

---

### Supported instruments:

- Keithley 2450 SourceMeter.
- The driver does not check the source level or the compliance against the limits of the instrument.

---

### Usage:

- The sweep value is the source level: a voltage in V if **SweepMode** is `Voltage in V`, a current in A if
  **SweepMode** is `Current in A`.
- At the start of the run, the instrument is identified with `*IDN?`, reset, and its error queue is cleared. In
  SCPI the status registers are preset and the beeper is switched off.
- Each time the module is used, the averaging filter, source and measure function, compliance, range, integration
  time, sensing and terminals are configured. In TSP, a reading buffer `data` is created, and a single autozero is
  performed. In TSP, the measure unit is set to amperes or volts together with the measure function, as the
  instrument keeps a unit per function that could also be ohms or watts. If the output is on while the terminals
  are changed, it is switched off first.
- When a new source level is set, one measurement is taken right away so that the instrument outputs the new level.
- Each measurement point starts a measurement in the measure phase and reads it in the call phase, so that several
  instruments of one sequencer branch measure at the same time.
- At the end of the run the output is switched off, and the instrument returns to 2-wire sensing and the front
  terminals.

---

### Parameters:

- **SweepMode**: `Voltage in V` or `Current in A`. Selects which quantity is sourced; the other one is measured.
- **RouteOut**: `Front` or `Rear` terminals.
- **Speed**: Integration time in power line cycles: `Fast` = 0.1 NPLC, `Medium` = 1 NPLC, `Slow` = 10 NPLC.
- **Range**:
  - `Auto`: auto ranging down to the lowest current range, also after a `Limited` range in a previous branch.
  - `Limited <range>`: with **SweepMode** `Voltage in V`, auto ranging of the current measurement that does not go
    below `<range>`. With `Current in A`, the current source uses auto ranging without a lower limit.
  - `Fixed <range>`: the current measurement range (`Voltage in V`) or the current source range
    (`Current in A`) is fixed to `<range>`.
  - The voltage source and the voltage measurement always use auto ranging.
  - A range is the expected reading: the instrument selects the lowest range that covers it. If the command set
    does not offer a range as low as the option, e.g. in the 2400 emulation, its lowest range is used.
- **Compliance**: The current limit in A while voltage is sourced, or the voltage limit in V while current is
  sourced. Must be larger than 0.
- **Average**: Number of readings from 1 to 100 that the repeating average filter averages into one value. 1
  switches the filter off. The filter is set for the measure function that the SweepMode selects. One measurement
  integrates for at least Average x NPLC power line cycles, 20 s at 50 Hz for Average 100 and Speed `Slow`. The
  driver allows six integration times per reading for autozero and source readback, so it extends the base timeout
  of 10 s by 120 s to 130 s in that case. A lost answer can block the run that long. As the instrument keeps NPLC
  and filter per measure function, the driver uses the largest NPLC and filter count sent since the last reset;
  the timeout can be too long, never too short.
- **4wire**: If checked, remote sensing (4-wire) is used, otherwise local sensing (2-wire).

---

### Returned values:

- **Voltage** in V and **Current** in A.
- A reading above `1e20` (the instrument reports `9.9e37` when it cannot measure) is returned as `nan`.

---

### Communication commands:

The driver offers its instrument commands for scripts and Instrument Control, e.g. `get_identification`,
`get_language`, `set_output`, `set_voltage`, `set_current`, `set_current_limit`, `set_voltage_limit`, the range,
NPLC, sensing, terminal and filter setters, `set_output_off_mode`, and `get_voltage_and_current`. Each command is
sent in the command set of the instrument. A few commands exist in one command set only and raise in the other:
`preset_status`, `set_beeper` and `set_source_mode` are SCPI only; `clear_default_buffer`, `make_reading_buffer`
and `autozero_once` are TSP only. In TSP, `get_voltage_and_current` needs the reading buffer of
`make_reading_buffer`. TSP commands act on the present source or measure function, so in TSP `set_voltage`,
`set_current` and the current range setters refuse to run when the driver selected another function last
(`set_source_function`, `set_measure_function`; after `reset` the instrument sources voltage and measures
current), and `get_voltage_and_current` refuses when source and measure function are the same. After `connect`
the functions are unknown, so in TSP these commands are refused until `reset` or the function setters ran; the
SweepMe! run does both before it sets a level. `get_voltage_and_current` in TSP likewise needs both functions known
and different, as they decide which value is the voltage and which the current.
