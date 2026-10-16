# SpectrumAnalyzer-RedPitaya_STEMlab

Spectrum analyzer on the fast analog inputs (IN1, IN2) of Red Pitaya STEMlab boards, controlled
via the SCPI server over Ethernet.

The board has no spectrum analyzer commands in its SCPI server (its spectrum analyzer is a web
application on the C API). This driver records a time trace with the acquisition commands the
Scope driver uses as well, and computes the power spectrum itself: a windowed FFT of the buffer,
converted to dBm into the configured impedance.

## Setup

1. Start the SCPI server on the Red Pitaya (web interface -> Development -> SCPI server).
2. Enter the IP address of the board with the TCP port of the SCPI server (5000) as the port,
   e.g. `192.168.178.xxx:5000`. The connection goes through the SweepMe! port manager as a
   socket, so the generator and scope drivers of the same board share the connection.
3. Select the input under `Channel` in the parameter box, and set `Input range` to the jumper
   behind that input's SMA connector (LV +/-1 V, HV +/-20 V) - the setting selects only the
   calibration, the jumper sets the range.

## How the module's settings are mapped

| Setting | What it does here |
| --- | --- |
| Frequency range (center/span or min/max) | The maximum frequency selects the decimation: the smallest power of two with 125 MHz / decimation / 2 >= f_max, i.e. the finest sampling that still covers the range. The returned trace is cut to [f_min, f_max]. |
| Resolution bandwidth | The 16384-sample buffer is split into 1, 2, 4, 8 or 16 segments whose spectra are averaged (Welch's method). More segments: wider bins, smoother trace, same acquisition time. The bin width is 125 MHz / decimation / samples per segment. |
| Video bandwidth | Not applicable, `Auto` only. |
| Trace mode | `Current`: one acquisition. `Max hold` / `Min hold` / `Average` over the given repetitions or hold time; the average is a power average. |
| Reference level | Informational; the range is set by the jumper (see above). |
| Window | Hann (default), Hamming, Blackman, Flat top (amplitude-accurate, wide main lobe), Rectangular. All are amplitude-corrected: a sine of amplitude A reads A^2 / (2 R) at its frequency. |
| Impedance in Ohm | R for the dBm conversion, 50 by default. The inputs are high-impedance; terminate them for a 50 Ohm source. |
| Trigger timeout in s | Bound for one acquisition (the trigger source is `NOW`, so it fires at once; the wait is the buffer fill time, 16384 * decimation / 125 MHz). |

Examples: f_max = 1 MHz gives decimation 32 (3.9 MS/s, Nyquist 1.95 MHz, bin width 238 Hz, 4.2 ms
per acquisition); f_max = 10 kHz gives decimation 4096 (30.5 kS/s, bin width 1.9 Hz, 0.54 s per
acquisition). The largest decimation is 65536 (1.9 kS/s, 8.6 s per acquisition).

The DC component of each segment is removed before the FFT, so the DC bin is meaningless; the
trace starts at the first bin above f_min.

## Communication commands

Besides the sequencer functions, the driver offers one function per SCPI command for use from
pysweepme scripts (`driver.list_functions()`), the same acquisition commands as the Scope driver,
plus the spectrum helpers built on them. `channel` is the input, 1 or 2:

- `get_spectrum(channel, decimation=64, samples=16384, window="Hann", segments=1, impedance=50, timeout=5)`
  - one acquisition and its spectrum, as `(frequencies in Hz, powers in dBm)` from DC to
  125 MHz / decimation / 2
- `acquire_trace(channel, samples=16384, timeout=5)` - one immediate acquisition (start, trigger
  `NOW`, wait for the buffer, read, stop), in V
- `compute_spectrum(trace, samplerate, window, segments, impedance)` - the arithmetic alone
- `decimation_for_frequency(frequency_max)`, `resolution_bandwidth(decimation, samples, segments)`,
  `get_peak(frequencies, powers)`
- `reset_acquisition()`, `start_acquisition()`, `stop_acquisition()`
- `set_decimation(decimation)` / `get_decimation()`, `set_averaging(enabled)` / `get_averaging()`
- `set_data_units(units)` / `get_data_units()`, `get_buffer_size()`
- `set_gain(channel, gain)` / `get_gain(channel)` - LV or HV
- `set_trigger_source(source)` (arms; after `start_acquisition()`), `get_trigger_status()`,
  `set_trigger_level`, `set_trigger_delay(samples)` and their `get_` counterparts,
  `get_buffer_filled()`
- `get_data(channel, samples)`, `get_buffer(channel)`
- `get_settings()` - acquisition settings plus the sample rate, maximum frequency and bin width
  they imply
- `get_identification()`, `get_system_version()`

## Compatibility

Written against the SCPI command set of OS 2.x (STEMlab 125-14). `ACQ:TRig:FILL?` (OS 2.00 and
up) is used to wait for the buffer; if the board does not answer it, the driver waits for the
calculated fill time instead. Boards with a 10 bit ADC (STEMlab 125-10) have a correspondingly
higher noise floor.

## Reference

Red Pitaya SCPI command list:
https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/command_list/commands-acq.html
