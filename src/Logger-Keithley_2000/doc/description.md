# Logger Keithley 2000

This driver reads single values from the Keithley 2000 digital multimeter. For each measurement point, one reading
of the selected measurement function is triggered and read back with `READ?`.

---

### Requirements:

- The instrument must be connected via **GPIB** or **RS-232** (**COM**).
- For RS-232, the baud rate of the instrument must be set to 9600 (factory default) and the terminator to `<CR>`.
- No further libraries are needed. Communication is handled by the SweepMe! port manager.

---

### Usage:

- At the start of the run, the instrument is reset with `*RST` and the beeper is switched off.
- When the sequencer enters the branch, the measurement function, the integration time, and auto range are set.
  Continuous initiation is switched off so that each reading is triggered by the driver.
- For each measurement point, one reading is triggered and read back in the same step.
- At the end of the run, the beeper and, if it was switched off, the display are switched on again.
- Several driver instances can use the same instrument, e.g. to log a DC voltage and a frequency on the same input.
  Each instance selects its own measurement function again before it triggers a reading, if another instance has
  changed it in the meantime.

---

### Parameters:

- **Mode**: The measurement function: `Voltage DC`, `Voltage AC`, `Current DC`, `Current AC`, `Resistance`
  (2-wire), `FResistance` (4-wire), `Frequency`, `Period`, `Temperature`, `Diode`, `Continuity`.
- **NPLC**: Integration time in number of power line cycles, from `Fastest (0.01)` to `Slow (10.0)`. Only shown for
  voltage, current, resistance, and temperature. Frequency, period, diode test, and continuity use their fixed rates.
  For the AC functions, `Medium` and `Slow` have no effect on the integration time.
- **Range**: Only `Auto` is available. Auto range is switched on for voltage, current, and resistance. The other
  functions have no auto range.
- **Display**: `Off` switches the front panel display off during the measurement, which can speed up the measurement.
- **Temperature unit**: `°C`, `K`, or `°F`. Only shown if **Mode** is `Temperature`.

---

### Measurement Output:

| Mode                                | Variable      | Unit                     |
|-------------------------------------|---------------|--------------------------|
| `Voltage DC`, `Voltage AC`          | same as Mode  | V                        |
| `Current DC`, `Current AC`          | same as Mode  | A                        |
| `Resistance`, `FResistance`         | same as Mode  | Ohm                      |
| `Frequency`                         | `Frequency`   | Hz                       |
| `Period`                            | `Period`      | s                        |
| `Temperature`                       | `Temperature` | as **Temperature unit**  |
| `Diode`                             | `Diode`       | V                        |
| `Continuity`                        | `Continuity`  | Ohm                      |

An overflow reading is returned as `9.9e37`.

---

### Known limitations:

- Manual ranges, resolution (digits), filters, and the AC bandwidth are not set by the driver.
- For `Temperature`, the thermocouple type and the reference junction are taken from the instrument as they are.
  Set them on the front panel before the run.
- For `Continuity`, the threshold resistance is taken from the instrument as it is.
- The scanner card is not supported.
- The communication timeout is 10 s.
