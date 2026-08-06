# Scope-RedPitaya_STEMlab

Driver for the fast analog inputs (IN1, IN2) of Red Pitaya STEMlab boards, controlled via the
SCPI server over Ethernet.

## Setup

1. Start the SCPI server on the Red Pitaya (web interface -> Development -> SCPI server).
2. Enter the IP address of the board as the port, e.g. `192.168.178.xxx`.

## Trigger sources

| Option | Command | Use |
| --- | --- | --- |
| Now | `NOW` | Acquire immediately, no edge condition. Best for a continuously running signal. |
| Channel 1 / Channel 2 | `CH1_PE`, `CH2_NE`, ... | Trigger on an edge of the input signal. Gives a stable, repeatable trace. |
| External | `EXT_PE` / `EXT_NE` | External 3V3 CMOS trigger input. |
| Signal | `AWG_PE` / `AWG_NE` | Trigger on the generator. Only fires when the generator is (re)started, so it does not work with a free running continuous signal. |
| None | `DISABLED` | Disables the trigger. The acquisition then never completes; the driver rejects this with a message. |

## Known behavior

- **The trigger is armed after `ACQ:START`, not before.** The manufacturer's acquisition example
  states "Trigger source command must be set after ACQ:START". Arming while the acquisition is
  stopped is lost, which previously made every acquisition after the first one run into the
  trigger timeout.
- **The driver waits for the data buffer to fill** (`ACQ:TRig:FILL?`, OS 2.00-18 and up) before
  reading. The trigger sits in the middle of the 16384 sample data buffer, so the second half of
  the trace is only recorded after the trigger event. On older OS versions the driver waits for
  the calculated fill time instead.
- **Time range**: choose a range that covers at least one period of the signal. I.e. a 1 Hz signal
  needs `1.07 s` or more; at `131 µs` the trace would be a flat line.
- **Trigger timeout** should be larger than the time range, otherwise the acquisition times out
  before the buffer is full. The driver prints a note if it is too short.
- **Input range**: the range is set by the jumper behind each input SMA connector, independently
  per channel: `Low voltage` = +/- 1 V full scale, `High voltage` = +/- 20 V full scale.
  The `Channel<n>_Range` setting does **not** switch anything in hardware on a STEMlab. It only
  selects which calibration coefficients the instrument uses to convert ADC counts into volts.
  (The SIGNALlab 250-12 is the exception, there the same command drives a real 1:20 attenuator.)
  - **A mismatch is a pure scaling error**, by the 1:20 divider ratio, plus a wrong offset because
    each range has its own calibration constants: jumper LV with setting HV reads about 20 times
    too high, jumper HV with setting LV about 20 times too low. Nothing is damaged by the
    mismatch itself.
  - **The setting provides no protection.** What may safely be applied is decided by the jumper
    alone. With LV jumpers, applying a HV level signal damages the input regardless of the
    setting.
  - **A mismatch cannot be detected in software.** The board cannot read the jumper position;
    `ACQ:SOUR<n>:GAIN?` only returns the value that was set.
  - The setting is still required for correct readings, because the driver lets the instrument
    convert to volts (`ACQ:DATA:UNITS VOLTS`). The instrument default is `LV`, but the value
    persists between sessions, so the driver always sends it explicitly.
  - Moving the jumpers changes the input capacitance. Red Pitaya recommends recalibrating the
    board afterwards.
- Data is returned as 1D arrays (one time array plus one array per enabled channel), which
  SweepMe! saves to a separate file from 0D data of other modules in the same branch.

## Using generator and scope of the same board together

The `Signal-RedPitaya_STEMlab` driver can be used in the same setting to generate a signal on OUT1
and read it back on IN1 (SMA cable required). Both drivers open their own connection to the SCPI
server. Use the trigger source `Channel 1` or `Now`, not `Signal`, because the generator is only
triggered once when it is configured.

## Compatibility

All commands used by this driver are available since ecosystem 1.04-18, with one exception:
`ACQ:TRig:FILL?` requires OS 2.00. It is tried once per run. If the instrument does not answer it
within the port timeout, or answers something unexpected, the driver stops using it and waits for
the calculated time the second half of the buffer needs instead. That fallback works on every
ecosystem version tested, down to version 0.98.

The connection is opened with a receive timeout (`self.port_timeout`, 5 s by default). This is
essential on older ecosystems: without it, a command the instrument does not know is never
answered and the driver would wait forever, with no error and no way to stop the run. The timeout
applies to each received chunk rather than to the whole answer, so reading a full data buffer is
not affected.

Board models: the driver works with all boards that provide fast analog inputs, including the
discontinued STEMlab 125-10. The buffer size is read from the instrument (`ACQ:BUF:SIZE?`) rather
than assumed. Note that the 125-10 has a 10 bit ADC, so its quantisation step in the `Low voltage`
range is about 2 mV instead of the 122 µV of the 14 bit boards.

## Reference

Red Pitaya SCPI command list:
https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/command_list/commands-acq.html
