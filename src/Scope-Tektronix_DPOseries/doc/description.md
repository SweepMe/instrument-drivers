# Scope-Tektronix_DPOseries

Driver for the analog channels of Tektronix DPO7000 series oscilloscopes. The commands come from the programmer
manual 077-0010-26 (MSO/DPO5000/B, DPO7000/C, DPO70000/B/C/D/DX/SX, DSA70000/B/C/D and MSO70000/C/DX series), whose
command set these families share, so the siblings may work as well. Only the DPO7000 series was in mind when the
driver was written; the driver does not check the model.

The instrument is addressed through the SweepMe! port manager over USB (USBTMC), GPIB or TCPIP (VISA). The port
properties keep a delay of 1 s between writes, as in earlier versions of this driver, so the configuration of a
measurement takes a few seconds.

## Scope module fields the driver uses

| Field | Options | Effect |
| --- | --- | --- |
| Trigger source | As is, CH1 to CH4, AUX, LINE, None | `TRIGger:A:EDGE:SOUrce`; "None" and "As is" leave the trigger untouched |
| Trigger level | number in V | `TRIGger:A:LEVel`; a level of 0 lets the instrument set the level to 50 % of the signal (`TRIGger:A SETLevel`) |
| Trigger slope | As is, Rising, Falling, Either | `TRIGger:A:EDGE:SLOpe`; "Either" is not available on MSO/DPO5000 |
| Trigger coupling | As is, DC, AC, HF rejection, LF rejection, Noise rejection | `TRIGger:A:EDGE:COUPling` |
| Trigger timeout | seconds, default 30 | how long a single sequence may take before the run stops with an error |
| Time range | Time range in s, Time scale in s/div, Record length | automatic horizontal mode with the scale (a range is divided by the 10 horizontal divisions), or manual mode with the record length |
| Sampling rate | samples per second | `HORizontal:MODE:SAMPLERate` |
| Acquisition | As is, Single, Continuous | single sequence (`ACQuire:STOPAfter SEQUENCE`), continuous (`RUNSTOP`), or whatever the instrument is set to |
| Average | As is, 1 to 1024 | `ACQuire:NUMAVg` with the acquisition mode AVERAGE, or SAMPLE for 1 |
| Channel 1 to 4 | check box, name | the channels to read; the name becomes the variable name |
| Channel range | As is, 10 mV to 50 V | the full vertical range, divided by the 10 vertical divisions into `CH<x>:SCAle` |
| Channel offset | number in V | `CH<x>:OFFSet` |
| Channel impedance | As is, 50, 1e6 | `CH<x>:TERmination`; 50 Ohm needs an input that offers it |
| Channel coupling | As is, DC, AC, DC reject, Ground | `CH<x>:COUPling`; DC reject needs a probe with that feature |

Every selected channel is switched on (`SELect:CH<x> ON`). At least one channel must be selected. The driver sends no
reset, so everything left "As is" stays as set on the instrument.

Fields the driver shows but does not use: *Time offset* (kept so that saved sequences load; the horizontal position
is not changed), *Sampling rate type* and *Voltage range* (one option each).

Not supported: the B trigger, trigger types other than edge, digital and math or reference waveforms, probe settings,
FastFrame, FastAcq and the roll mode.

## Measurement

With a single sequence the driver starts the acquisition at every point (`ACQuire:STATE RUN`) and waits until
`ACQuire:STATE?` answers 0 and, when averaging, until `ACQuire:NUMACq?` has reached the number of averages; the wait
is bounded by the trigger timeout. With continuous acquisition the currently displayed waveform is read. Every
channel is then selected as data source (`DATa:SOUrce`), its preamble (`WFMOutpre?`) and its curve (`CURVe?`, ASCII,
2 bytes per point, the whole record) are read, and the curve is scaled with the preamble: time =
XZERO + XINCR * (n - PT_OFF), voltage = YZERO + YMULT * (level - YOFF). The result is a 1D time array and one
voltage array per channel, which SweepMe! saves to a separate data file per sequencer iteration.

After the configuration the driver reads the event queue (`*ESR?`, `EVMsg?`) and stops the run with the
instrument's messages if a command, execution or device error (event codes below 400) was reported; other events go
into the log file.

## Communication commands

The commands are declared with pysweepme's `@command`, so Instrument Control and scripts can use them directly. The
instrument answers with `HEADer OFF` and `VERBose ON`, which `initialize()` sets, so read-backs match the choices of
the commands; the commands send the full-length keywords of the manual.

- `get_identification()`: the `*IDN?` string.
- `reset()`: `*RST`, factory defaults of the programmable settings; the DATa settings are kept.
- `clear_status()`: `*CLS`.
- `get_event_status()`: `*ESR?`, which also loads the event queue.
- `get_events()`: the pending events as `code,"message"` entries (`EVMsg?`), read after `get_event_status()`.
- `set_header(header)` / `get_header()`: response headers on query answers (`HEADer`).
- `set_verbose(verbose)` / `get_verbose()`: full-length keywords in answers (`VERBose`).
- `set_acquisition_running(acquisition_running)` / `get_acquisition_running()`: `ACQuire:STATE` RUN or STOP; the
  read-back is False once a single sequence has completed.
- `set_acquisition_type(acquisition_type)` / `get_acquisition_type()`: `ACQuire:STOPAfter`, RUNSTOP or SEQUENCE.
- `set_acquisition_mode(acquisition_mode)` / `get_acquisition_mode()`: `ACQuire:MODe`, SAMPLE, PEAKDETECT, HIRES,
  AVERAGE, WFMDB or ENVELOPE. At or above the base sample rate HIRES and PEAKDETECT silently become SAMPLE.
- `set_averages(averages)` / `get_averages()`: `ACQuire:NUMAVg`.
- `get_acquisition_number()`: `ACQuire:NUMACq?`, acquisitions since the last start.
- `set_trigger_source(trigger_source)` / `get_trigger_source()`: `TRIGger:A:EDGE:SOUrce`, AUXILIARY, CH1 to CH4 or
  LINE.
- `set_trigger_slope(trigger_slope)` / `get_trigger_slope()`: `TRIGger:A:EDGE:SLOpe`, RISE, FALL or EITHER.
- `set_trigger_coupling(trigger_coupling)` / `get_trigger_coupling()`: `TRIGger:A:EDGE:COUPling`, AC, DC, HFREJ,
  LFREJ or NOISEREJ.
- `set_trigger_level(trigger_level)` / `get_trigger_level()`: `TRIGger:A:LEVel` in V.
- `autoset_trigger_level()`: `TRIGger:A SETLevel`, the level at 50 % of the trigger signal.
- `set_horizontal_mode(horizontal_mode)` / `get_horizontal_mode()`: `HORizontal:MODE`, AUTO, CONSTANT or MANUAL.
- `set_horizontal_scale(horizontal_scale)` / `get_horizontal_scale()`: `HORizontal:MODE:SCAle` in s/div.
- `set_record_length(record_length)` / `get_record_length()`: `HORizontal:MODE:RECOrdlength` (MANUAL mode).
- `set_sample_rate(sample_rate)` / `get_sample_rate()`: `HORizontal:MODE:SAMPLERate` in S/s.
- `set_display(channel, display)` / `get_display(channel)`: `SELect:CH<x>`.
- `set_vertical_scale(channel, vertical_scale)` / `get_vertical_scale(channel)`: `CH<x>:SCAle` in V/div.
- `set_offset(channel, offset)` / `get_offset(channel)`: `CH<x>:OFFSet` in V.
- `set_coupling(channel, coupling)` / `get_coupling(channel)`: `CH<x>:COUPling`, AC, DC, DCREJECT or GND.
- `set_impedance(channel, impedance)` / `get_impedance(channel)`: `CH<x>:TERmination`, 50 or 1000000 Ohm.
- `select_data_source(channel)` / `get_data_source()`: `DATa:SOUrce`, the channel the preamble and curve answer.
- `set_data_encoding(data_encoding)` / `get_data_encoding()`: `DATa:ENCdg`; the driver uses ASCII.
- `set_data_width(data_width)` / `get_data_width()`: `WFMOutpre:BYT_Nr`, 1, 2, 4 or 8 bytes per point.
- `set_data_start(data_start)` / `get_data_start()`, `set_data_stop(data_stop)` / `get_data_stop()`: `DATa:STARt`
  and `DATa:STOP`, the first and last point of a transfer.
- `get_waveform_preamble()`: `WFMOutpre?` as a dictionary (BYT_NR, NR_PT, XINCR, XZERO, PT_OFF, YMULT, YOFF, YZERO,
  ...).
- `get_curve()`: `CURVe?`, the digitizing levels of the selected source.
- `get_waveform(channel)`: selects the source, reads preamble and curve and returns time in s and voltage in V.

Ranges the manual does not state are left open: the number of averages, the sample rate, the horizontal scale, the
record length, the vertical scale (depends on the probe), the offset and the trigger level. The instrument refuses
or clips what it cannot do; the event check after the configuration reports it. The `channel` of every channel
command is 1 to 4.
