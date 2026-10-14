# Scope Keysight InfiniiVision 3000T

This driver reads the analog channels of Keysight InfiniiVision 3000T X-Series oscilloscopes. For every measurement
point, one single acquisition is started, the driver waits until it is complete, and the waveforms of all selected
channels are read out as binary data.

---

### Requirements:

- The oscilloscope must be connected via **USB**, **TCPIP** (LAN), or **GPIB** (optional GPIB module).
- No further libraries are needed. Communication is handled by the SweepMe! port manager. The waveform data is read
  as IEEE 488.2 binary block through the underlying pyvisa resource.
- The driver was developed with an MSO-X 3024T running firmware `07.40.2021031200`.

---

### Supported instruments:

- DSOX3000T and MSOX3000T models with 4 analog channels, e.g. `MSO-X 3024T`, `DSO-X 3034T`, `MSO-X 3104T`.
- The digital channels of the MSO models are not read.

---

### Usage:

- Add one **Scope** module and select this driver. All channels of the oscilloscope are handled by one instance.
- Every combo box has an `As is` option, and the level and offset fields accept `As is`. With `As is`, the driver
  sends no command for this setting, so the oscilloscope can be set up at the front panel and only read out.
- At the start of a branch, the driver stops the oscilloscope, clears the error queue, and applies the settings in the
  order channels, timebase, acquisition, trigger. Unused channels are switched off, so that the used channels get more
  acquisition memory. Afterwards the error queue is read. If the oscilloscope rejected or clipped a setting, the run is
  stopped with a message such as `The oscilloscope did not accept all settings: -222,"Data out of range"`.
- For every measurement point, `:SINGle` is sent and the Run bit of the operation status register is polled until the
  acquisition is complete. With averaging, one single acquisition includes as many triggers as set in **Average**.
- If no trigger arrives within **Timeout**, the acquisition is stopped and the run ends with an error.
- At the end of the run, the oscilloscope stays stopped and shows the last acquisition.

---

### Parameters:

- **Sweep mode**: the setting that follows the sweep value.
  - `None`: no setting is changed per measurement point.
  - `Time range in s`: full horizontal range of 10 divisions, `:TIMebase:RANGe`.
  - `Time scale in s/div`: horizontal scale, `:TIMebase:SCALe`.
  - `Time offset in s`: time from the trigger event to the time reference point on the screen, `:TIMebase:POSition`.
  - `Trigger level in V`: level of the edge trigger of the current trigger source.
- **Trigger source**: `Channel 1` to `Channel 4`, `External`, `Line`, or `Software`. The driver always uses the edge
  trigger. `Software` leaves the trigger settings unchanged and forces a trigger with `:TRIGger:FORCe` while the
  acquisition is running, which is the right choice for a free running signal.
- **Slope**: `Rising`, `Falling`, `Either`, or `Alternating`. Not shown for `Software`.
- **Coupling**: trigger coupling `DC`, `AC`, or `LF reject`. Not shown for `Line` and `Software`.
- **Level**: trigger level in V, or `As is`. Not shown for `Line` and `Software`.
- **Timeout**: maximum time in s to wait for the acquisition to complete, including all triggers of an average.
  Default `10`.
- **Time range**: `Time range in s` sets the full horizontal range, `Time scale in s/div` the scale per division. The
  value and the time offset fields are only shown if this is not `As is`. The time offset is the time from the trigger
  event to the time reference point, which is the screen center unless it was changed at the front panel.
- **Acquisition**: acquisition type `Normal`, `Average`, `High resolution`, or `Peak detect`.
- **Average**: number of averages from `2` to `65536`. Only shown if **Acquisition** is `Average`.
- **Sampling rate**: the sampling rate itself cannot be set on these oscilloscopes, it follows from the timebase and
  the acquisition memory. Instead, the number of transferred points is selected.
  - `Maximum points`: the complete acquisition record, up to several million points per channel.
  - `Number of points`: the record is decimated to at most the selected number of points. The oscilloscope rounds
    down to a value it can deliver, e.g. `10000` can result in `8333` points.
- **Voltage range**: whether the channel **Range** is the full vertical range of 8 divisions in V
  (`:CHANnel<n>:RANGe`) or the scale in V/div (`:CHANnel<n>:SCALe`). The offered values change accordingly.
- **Channel 1** to **Channel 4**: enables the channel. Channel 1 is enabled by default. The following fields are only
  shown for enabled channels.
  - **Name**: used in the variable name.
  - **Range**: range or scale as selected in **Voltage range**, at the probe tip.
  - **Offset**: voltage in V at the center of the screen, or `As is`.
  - **Coupling**: input coupling `DC` or `AC`.
  - **Impedance**: input impedance `1 MOhm` or `50 Ohm`.
  - **Probe**: probe attenuation `1:1`, `10:1`, or `100:1`. `As is` keeps the attenuation that is set or detected
    by the oscilloscope.

  Probe and impedance are set before range and offset, because the allowed ranges depend on them.

---

### Measurement Output:

- **Time**: time axis in s, array. `0` is the trigger event.
- **CH<n> <Name>**: voltage in V of every enabled channel, array, in the order of the channel numbers.

All values are arrays that SweepMe! writes to a separate file per measurement point.

---

### Note on peak detect:

In `Peak detect` mode, the oscilloscope transfers a minimum and a maximum value for every time interval, so the
waveform contains twice as many values as the preamble reports points. Both values of a pair get the time of their
interval, so the time axis contains every time twice. Plotted as a line, this gives the same envelope as on the
oscilloscope screen.

---

### Known limitations:

- **Only the edge trigger is supported.** Other trigger types and their settings have to be selected at the front
  panel and used with **Trigger source** `As is`.
- **A single acquisition does not auto-trigger.** With `:SINGle`, the oscilloscope waits for a trigger even if the
  trigger mode is set to Auto at the front panel. Use `Software` to read a signal without a trigger event.
- **With `Software`, the oscilloscope can show the message "Selection not possible in this mode".** A forced trigger
  that arrives just after the acquisition has finished is rejected by the oscilloscope. The acquired data is not
  affected, and the resulting entry in the error queue is cleared at the start of the next branch.
- **Averaging returns a reduced record.** With `Average`, the oscilloscope only provides the averaged measurement
  record, which has far fewer points than the acquisition memory, independent of **Sampling rate**.
- **Clipped values are not marked.** Signal parts outside the digitizer range are returned as the limit value of the
  digitizer.
- **Digital channels, math functions, segmented memory, and serial decoding are not read.**
- **The oscilloscope stays stopped after the run.** Press **Run/Stop** to continue the live display.
