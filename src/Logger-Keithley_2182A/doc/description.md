# Logger Keithley 2182A

This driver reads voltages or thermocouple temperatures from channel 1 or channel 2 of the Keithley 2182A
nanovoltmeter. For each measurement point, one reading is triggered and read back with `READ?`.

---

### Requirements:

- The instrument must be connected via **GPIB** or **RS-232** (**COM**).
- For RS-232, the interface must be enabled in the instrument menu with 19.2k baud, no flow control, and the terminator
  `<CR>`.
- No further libraries are needed. Communication is handled by the SweepMe! port manager.

---

### Usage:

- At the start of the run, the instrument is reset with `*RST` and the beeper is switched off.
- When the sequencer enters the branch, channel, function, integration time, range, filters, and temperature settings
  are set. Continuous initiation is switched off so that each reading is triggered by the driver. Errors reported by
  the instrument afterwards are printed to the Debug widget (F2).
- For each measurement point, one reading is triggered and read back in the same step.
- At the end of the run, the beeper and, if it was switched off, the display are switched on again.
- To read both channels, add one driver instance for each channel with the same port. Each instance sets its own
  channel and settings again before it triggers a reading, if another instance has changed them in the meantime.

---

### Parameters:

- **Channel**: `Channel 1` or `Channel 2`.
- **Mode**: `Voltage` or `Temperature` (thermocouple).
- **Range**: `Auto` or a fixed voltage range. Channel 1: `10 mV` to `100 V`. Channel 2: `100 mV` to `10 V`. Only shown
  if **Mode** is `Voltage`.
- **Thermocouple type**: `J`, `K`, `T`, `E`, `N`, `R`, `S`, or `B`. The internal reference junction is used. Only shown
  if **Mode** is `Temperature`.
- **Temperature unit**: `°C`, `K`, or `°F`. Only shown if **Mode** is `Temperature`.
- **NPLC**: Integration time in number of power line cycles, from `Fastest (0.01)` to `Slowest (50)`. The instrument
  default is 5.
- **Digital filter**: `Off`, `Moving`, or `Repeat` average.
- **Filter count**: Number of readings averaged by the digital filter, 1 to 100. Only shown if **Digital filter** is not
  `Off`.
- **Analog filter**: Enables the low-pass analog filter. It adds about 125 ms settling time to each conversion.
- **Display**: `Off` switches the front panel display off during the measurement.

---

### Measurement Output:

| Mode          | Variable      | Unit                    |
|---------------|---------------|-------------------------|
| `Voltage`     | `Voltage`     | V                       |
| `Temperature` | `Temperature` | as **Temperature unit** |

An overflow reading is returned as `9.9e37`.

---

### Known limitations:

- The communication timeout is calculated from **NPLC**, **Filter count**, and **Analog filter**, with a minimum of
  10 s. Slow settings with a large filter count lead to a long timeout.
- Delta measurements with a Keithley 6221/6220 current source, the ratio and delta functions of the two channels,
  and the simulated reference junction are not available in this driver.
- Autozero and line synchronization keep their instrument defaults.
