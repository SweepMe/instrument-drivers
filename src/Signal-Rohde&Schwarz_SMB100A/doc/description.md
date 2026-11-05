# Rohde & Schwarz SMB100A

Driver for the Rohde & Schwarz SMB100A RF and microwave signal generator (frequency options B101 to B140), used as
a CW source: the driver sets frequency, level and phase of the RF output and reads them back. The instrument commands
follow the "R&S SMB100A Operating Manual", version 23 (firmware 5.00.116).

## Usage

- Connect through USB (USBTMC) or LAN (VISA TCPIP).
- The driver resets the instrument at the start of a run (`*RST`) and locks the front panel controls; the display keeps
  showing the settings. The controls are unlocked again at the end of the run.
- In `configure` the driver sets the level mode and frequency mode to CW, the power unit, the level, the frequency and
  the phase or delay, and switches the RF output on. At the end (`unconfigure`) it reads the error queue of the
  instrument into the SweepMe! log, switches the RF output off and unlocks the front panel.

## Signal module fields

- **SweepMode**: None, Frequency in Hz, Period in s, Amplitude in V, Amplitude in dBm, Amplitude in dBuV, Phase in deg,
  Delay in s. A sweep of the amplitude in a unit other than the one of the AmplitudeHiLevel field switches the power
  unit of the instrument for the value and back again for the read-back.
- **Waveform**: Sinus only (the instrument is a CW source).
- **PeriodFrequency** and **PeriodFrequencyValue**: the frequency in Hz or the period in s. The frequency range depends
  on the installed frequency option (100 kHz up to 1.1 GHz with B101 ... up to 40 GHz with B140), so the driver does
  not limit the value; the instrument refuses a frequency outside its range and reports it in the error queue.
- **AmplitudeHiLevel** and **AmplitudeHiLevelValue**: the RF level in V, dBm or dBuV. The choice sets the power unit of
  the instrument (`UNIT:POW`), in which every level is sent and read back. The level range depends on the frequency
  option and the attenuator, so the driver does not limit the value either. The level is the one shown on the display,
  i.e. including a level offset if one is set (`set_level_offset`).
- **DelayPhase** and **DelayPhaseValue**: the phase in degrees or a delay in seconds. The instrument knows a "Delta
  Phase" relative to a reference phase; the driver sends the phase as this delta, so a phase sweep is relative to the
  reference phase (0 after the reset at the start of the run). A delay is converted to a phase at the frequency set
  last: `phase = delay * frequency * 360`, reduced to +/- 360 degrees, a positive delay giving a positive phase.
- **Impedance**: 50 Ohm (the impedance of the RF output cannot be changed).

Returned values: the frequency in Hz or the period in s (as selected in PeriodFrequency), and "RF Power level", the
level at the RF output connector in the unit of the AmplitudeHiLevel field. The level at the connector excludes a
level offset, while the level set with the amplitude field includes it.

The GUI values can use the parameter syntax of SweepMe!; a changed frequency, amplitude or phase/delay is re-sent
through `reconfigure` without a full reconfiguration.

## Communication commands

One method per instrument command, declared with `@command`, for pysweepme scripts and the Instrument Control:

- `get_identification()` - `*IDN?`
- `reset_instrument()` - `*RST`; switches the RF output off and resets level, frequency, phase and power unit
- `run_self_test()` - `*TST?`; takes longer than a normal query, True when the self test passed
- `get_errors()` - `SYST:ERR:ALL?`; all entries of the error queue as `<code>,<description>`, empty when none
- `set_user_interface_lock(user_interface_lock)` / `get_user_interface_lock()` - `SYST:ULOC DONL|ENAB`; the mode
  `DISabled` (lock with VNC remote operation) is not offered
- `restart_firmware()` - `SYST:REST`; the connection is lost
- `shutdown_device()` - `SYST:SHUT`; the connection is lost, switch the instrument on at the front panel
- `set_data_format(data_format)` / `get_data_format()` - `FORM ASC|PACK`; the readers of this driver expect ASC
- `set_frequency_mode(frequency_mode)` / `get_frequency_mode()` - `SOUR:FREQ:MODE CW|FIX|SWE|LIST`
- `set_frequency(frequency)` / `get_frequency()` - `SOUR:FREQ` in Hz; no range declared, see above
- `set_phase(phase)` / `get_phase()` - `SOUR:PHAS` in degrees (sent in radians, the unit of the command); the delta
  phase relative to the reference phase
- `reset_phase_reference()` - `SOUR:PHAS:REF`; adopts the current phase as the reference, the phase then reads 0
- `set_delay(delay)` - sets the phase from a delay in s at the frequency set last (calls `set_phase`)
- `set_power_mode(power_mode)` / `get_power_mode()` - `SOUR:POW:MODE CW|FIX|SWE`
- `set_power_unit(power_unit)` / `get_power_unit()` - `UNIT:POW DBM|DBUV|V`; the unit of every level value
- `set_amplitude(amplitude)` / `get_amplitude()` - `SOUR:POW:LEV:IMM:AMPL`; the level of the display, offset included
- `get_power_level()` - `SOUR:POW:POW?`; the level at the RF output connector, offset excluded
- `set_level_offset(level_offset)` / `get_level_offset()` - `SOUR:POW:LEV:IMM:OFFS` in dB, -100 to 100
- `set_rf_mode(rf_mode)` / `get_rf_mode()` - `SOUR:POW:LMOD NORM|LOWN|LOWD` (normal, low noise, low distortion)
- `set_output(output)` / `get_output()` - `OUTP ON|OFF`
- `get_impedance()` - `OUTP:IMP?` in Ohm (G50, G1K, G10K or the plain number)
- `set_amplitude_modulation(amplitude_modulation)` / `get_amplitude_modulation()` - `SOUR:AM:STAT ON|OFF`
- `set_amplitude_modulation_type(amplitude_modulation_type)` / `get_amplitude_modulation_type()` -
  `SOUR:AM:TYPE LIN|EXP`; exponential AM needs a frequency option of 12 GHz or higher (B112 to B140)
- `set_linear_modulation_depth(linear_modulation_depth)` / `get_linear_modulation_depth()` - `SOUR:AM:DEPT:LIN` in
  percent, 0 to 100
- `set_exponential_modulation_depth(exponential_modulation_depth)` / `get_exponential_modulation_depth()` -
  `SOUR:AM:DEPT:EXP` in dB, -40 to 40

The amplitude modulation, the level offset, the RF mode and the data format are not used by the sequencer functions;
they are offered for scripts and the Instrument Control only. The modulation source and the sweep and list modes of
the instrument are not covered by this driver.

## Known behaviour

- Only the level offset and the AM depths carry declared ranges; frequency and level depend on the installed options
  and are checked by the instrument. A refused value appears in the error queue, which the driver writes to the
  SweepMe! log at the end of the run.
- The level is specified into 50 Ohm; into a high impedance the voltage at the output is higher than the set one.
- Changing the power unit does not change the output level, only the unit in which levels are sent and read.
