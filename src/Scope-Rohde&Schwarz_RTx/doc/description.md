# Scope-Rohde&Schwarz_RTx

Driver for the analog channels of Rohde&Schwarz RTO1000, RTO2000 and RTE1000 oscilloscopes. The commands come
from the "Remote control commands" chapters of the user manuals 1332.9725.02 version 11 (RTO1000 and RTO2000,
firmware 3.70), 1332.9725.02 version 30 (RTO2000, firmware 5.60) and 1326.1032.02 version 21 (RTE1000, firmware
4.80). The RTO6 and RTP share this command set and may work as well, but were not in mind when the driver was
written. The sample rate command `ACQuire:SRReal` needs firmware 3.40 or newer.

The instrument is addressed through the SweepMe! port manager over GPIB, TCPIP (VISA) or USB (USBTMC). The port
timeout is 10 s, because a long waveform in ASCII format takes a while to transfer; it can be changed in the port
dialog.

The model family (RTO, RTE or RTP) and the number of channels (2 or 4) are read from the `*IDN?` answer, whose order
number ends with a variant code such as `1329.7002k24` (RTO2024). A channel the connected model does not have is
refused; the time scale and acquisition time are checked against the maximum of the family (10000 s/div and 100 ks
on an RTO or RTP, 5000 s/div and 50 ks on an RTE). The trigger source "Line" is documented for the RTE only and
refused on the other families.

## Scope module fields the driver uses

| Field | Options | Effect |
| --- | --- | --- |
| Sweep mode | None, Time range in s, Time scale in s/div, Time offset in s | the sweep value sets `TIMebase:RANGe`, `TIMebase:SCALe` or `TIMebase:HORizontal:POSition` |
| Trigger source | As is, Channel 1 to 4, External, Line, Serial bus, Software | `TRIGger1:SOURce` of the A trigger; "Software" leaves the source alone and forces a trigger at every point (`TRIGger:FORCe`); "As is" leaves source and type untouched |
| Trigger level | As is or a number in V | `TRIGger1:LEVel<n>` of the selected channel (n = 1 to 4) or of the external trigger input (n = 5); not sent for "Line" and "Serial bus" |
| Trigger slope | As is, Rising, Falling | `TRIGger1:EDGE:SLOPe`, or `TRIGger1:ANEDge:SLOPe` for the external trigger input |
| Trigger coupling | As is, DC, DCLimit, AC | `TRIGger1:ANEDge:COUPling` of the external trigger input only (DC = 50 Ohm, DCLimit = 1 MOhm, AC); ignored for other sources |
| Trigger timeout | seconds, default 30 | how long a single acquisition may take before the run stops with an error |
| Time range | As is, Time range in s:, Time scale in s/div: | `TIMebase:RANGe` (the acquisition time across the 10 divisions) or `TIMebase:SCALe`, followed by the time offset as `TIMebase:HORizontal:POSition` |
| Time offset | number in s | the time between the reference point and the trigger point; only sent together with a time range or time scale |
| Sampling rate type | As is sampling rate, Auto sampling rate, Sampling rate in Sa/s:, Sample resolution in s:, Samples per time range: | "Auto" keeps the resolution constant (`ACQuire:POINts:AUTO RESolution`); the others send the sampling rate value as `ACQuire:SRReal`, `ACQuire:RESolution` or `ACQuire:POINts` |
| Sampling rate | As is or a number | the value of the sampling rate type |
| Acquisition | As is, Continuous, Single | continuous acquisition (`RUN`), or the acquisition is stopped (`STOP`) and a single acquisition (`SINGle`) is started at every point; "As is" reads whatever the instrument shows |
| Average | As is, 1 to 1024 | `ACQuire:COUNt`, the number of waveforms of a single acquisition and of the average; the waveform arithmetic of the selected channels is set to AVERage for more than 1 and OFF for 1 (`CHANnel<m>:ARIThmetics`) |
| Channel 1 to 4 | check box, name | the channels to read; the name becomes the variable name |
| Channel range | As is or a number in V | `CHANnel<m>:RANGe`, the voltage range across the 10 vertical divisions |
| Channel offset | As is or a number in V | `CHANnel<m>:OFFSet`, the offset voltage subtracted from the signal |
| Channel impedance | As is, 50 Ohm | the 50 Ohm termination is selected through the coupling (`CHANnel<m>:COUPling DC`); together with a 1 MOhm coupling the run stops with an error |
| Channel coupling | As is, DC 50 Ohm, DC 1 MOhm, AC 1 MOhm | `CHANnel<m>:COUPling` DC, DCLimit or AC |

Every selected channel is switched on (`CHANnel<m>:STATe ON`) with the decimation mode SAMPle (`CHANnel<m>:TYPE`);
the unselected channels of the model are switched off, because they may still be on from an earlier run. At least
one channel must be selected. The trigger mode is set to NORMal (`TRIGger:MODE`), so a waveform is only acquired
when a trigger occurs. The driver sends no reset or preset, so everything left "As is" stays as set on the
instrument. The data format is set to ASCII (`FORMat:DATA ASCii`) and the display update is switched on
(`SYSTem:DISPlay:UPDate ON`) once per run.

After the configuration the driver waits for the instrument (`*OPC?`), reads the error queue (`SYSTem:ERRor:ALL?`)
and stops the run with the instrument's messages if a setting was refused, for example a voltage range the probe
does not allow or a trigger level outside the display range.

Not supported: the B and R trigger events, trigger types other than the edge triggers, digital, math and reference
waveforms, probe settings, the high definition mode, fast segmentation and the history.

## Measurement

At every point the average is restarted (`ACQuire:ARESet:IMMediate`). With a single acquisition the status is
cleared (`*CLS`), the acquisition started (`SINGle`), a trigger forced for the "Software" source, and the driver
waits as the manuals' appendix "Command sequence and synchronization" describes for long operations: `*OPC` sets bit
0 of the event status register when the acquisition is complete, and `*ESR?` is polled for it, bounded by the
trigger timeout. With continuous or "As is" acquisition the driver forces a trigger for the "Software" source and
waits with `*OPC?`.

Every selected channel is then read: the header `CHANnel<m>:DATA:HEADer?` gives start time, stop time, record length
and the number of values per sample interval, the waveform `CHANnel<m>:DATA?` the voltages in V. The time axis is
evenly spaced from the start to the stop time over the record length. The result is a 1D time array and one voltage
array per channel, which SweepMe! saves to a separate data file per sequencer iteration. Decimation and arithmetic
modes with two values per sample interval (peak detect, envelope) are refused.

A long record (the record length can reach 1e9 points) takes long to transfer in ASCII; keep the record length or
the sample rate moderate, or raise the port timeout.

## Communication commands

The commands are declared with pysweepme's `@command`, so Instrument Control and scripts can use them directly. The
commands send the long keywords of the manuals; the instrument answers with the short ones (e.g. `DCL` for
`DCLimit`, `ANED` for `ANEDge`), so the read-backs of choices return text rather than the choice. All trigger
commands address the A trigger (suffix 1).

- `get_identification()`: the `*IDN?` string.
- `reset()`: `*RST`.
- `clear_status()`: `*CLS`, clears the status registers and the error queue.
- `request_operation_complete()`: `*OPC`, sets bit 0 of the event status register once all commands are done.
- `get_event_status()`: `*ESR?`, returns and clears the event status register.
- `wait_for_operation_complete()`: `*OPC?`, waits until all preceding commands are done, bounded by the port
  timeout.
- `get_errors()`: `SYSTem:ERRor:ALL?`, all entries of the error queue as `code,message`; `get_error_codes()`:
  `SYSTem:ERRor:CODE:ALL?`, the codes only; `get_error_count()`: `SYSTem:ERRor:COUNt?`.
- `set_data_format(data_format)` / `get_data_format()`: `FORMat:DATA`, ASCii, REAL,32, INT,8 or INT,16; the
  driver reads ASCii.
- `set_byte_order(byte_order)` / `get_byte_order()`: `FORMat:BORDer`, LSBFirst or MSBFirst, for INT,16 data.
- `set_display_update(display_update)` / `get_display_update()`: `SYSTem:DISPlay:UPDate`; off speeds up the
  measurement.
- `run_continuous()`, `run_single()`, `stop()`: `RUN`, `SINGle`, `STOP`.
- `set_time_scale(time_scale)` / `get_time_scale()`: `TIMebase:SCALe` in s/div, 25 ps/div to 10000 s/div (RTO, RTP)
  or 5000 s/div (RTE).
- `set_time_range(time_range)` / `get_time_range()`: `TIMebase:RANGe` in s, 250 ps to 100 ks (RTO, RTP) or 50 ks
  (RTE).
- `set_horizontal_position(horizontal_position)` / `get_horizontal_position()`: `TIMebase:HORizontal:POSition` in s.
- `set_record_length_mode(record_length_mode)` / `get_record_length_mode()`: `ACQuire:POINts:AUTO`, RESolution or
  RECLength is kept constant when the time scale changes.
- `set_sample_rate(sample_rate)` / `get_sample_rate()`: `ACQuire:SRReal` in Sa/s (firmware 3.40 or newer).
- `set_resolution(resolution)` / `get_resolution()`: `ACQuire:RESolution` in s, 1 fs to 0.5 s.
- `set_record_length(record_length)` / `get_record_length()`: `ACQuire:POINts`, 1000 to 1e9 points.
- `set_acquisition_count(acquisition_count)` / `get_acquisition_count()`: `ACQuire:COUNt`, 1 to 16777215.
- `get_acquisition_number()`: `ACQuire:CURRent?`, the acquisitions acquired so far.
- `reset_waveform_arithmetics()`: `ACQuire:ARESet:IMMediate`, restarts the average and envelope calculation.
- `set_trigger_mode(trigger_mode)` / `get_trigger_mode()`: `TRIGger:MODE`, AUTO, NORMal or FREerun.
- `set_trigger_source(trigger_source)` / `get_trigger_source()`: `TRIGger1:SOURce`, CHAN1 to CHAN4, EXTernanalog,
  SBUS or LINE (RTE only).
- `set_trigger_type(trigger_type)` / `get_trigger_type()`: `TRIGger1:TYPE`, the types all manuals list; the driver
  uses EDGE and ANEDge.
- `set_trigger_level(trigger_input, trigger_level)` / `get_trigger_level(trigger_input)`: `TRIGger1:LEVel<n>` in V,
  the input 1 to 4 being the channels and 5 the external trigger input.
- `set_trigger_slope(trigger_slope)` / `get_trigger_slope()`: `TRIGger1:EDGE:SLOPe`, POSitive, NEGative or EITHer.
- `set_external_trigger_coupling(external_trigger_coupling)` / `get_external_trigger_coupling()`:
  `TRIGger1:ANEDge:COUPling`, DC, DCLimit or AC.
- `set_external_trigger_slope(external_trigger_slope)` / `get_external_trigger_slope()`: `TRIGger1:ANEDge:SLOPe`,
  POSitive or NEGative.
- `force_trigger()`: `TRIGger:FORCe`.
- `set_channel_active(channel, active)` / `get_channel_active(channel)`: `CHANnel<m>:STATe`.
- `set_decimation_mode(channel, decimation_mode)` / `get_decimation_mode(channel)`: `CHANnel<m>:TYPE`, SAMPle,
  PDETect, HRESolution or RMS.
- `set_waveform_arithmetics(channel, waveform_arithmetics)` / `get_waveform_arithmetics(channel)`:
  `CHANnel<m>:ARIThmetics`, OFF, ENVelope or AVERage.
- `set_coupling(channel, coupling)` / `get_coupling(channel)`: `CHANnel<m>:COUPling`, DC (50 Ohm), DCLimit (1 MOhm)
  or AC (1 MOhm).
- `set_voltage_range(channel, voltage_range)` / `get_voltage_range(channel)`: `CHANnel<m>:RANGe` in V.
- `set_voltage_scale(channel, voltage_scale)` / `get_voltage_scale(channel)`: `CHANnel<m>:SCALe` in V/div.
- `set_vertical_position(channel, vertical_position)` / `get_vertical_position(channel)`: `CHANnel<m>:POSition`
  in divisions, -5 to 5.
- `set_voltage_offset(channel, voltage_offset)` / `get_voltage_offset(channel)`: `CHANnel<m>:OFFSet` in V.
- `get_waveform_header(channel)`: `CHANnel<m>:DATA:HEADer?`, start time, stop time, record length and values per
  sample interval.
- `get_waveform_values(channel)`: `CHANnel<m>:DATA?`, the waveform in V (ASCII format).
- `get_trace(channel)`: reads header and waveform and returns time in s and voltage in V.

Ranges the manuals state differently per model or make dependent on the probe are left open: the sample rate, the
voltage range, scale and offset, and the trigger level. The instrument refuses what it cannot do; the error check
after the configuration reports it. The `channel` of every channel command is 1 to 4, and 1 to 2 on a two-channel
model.
