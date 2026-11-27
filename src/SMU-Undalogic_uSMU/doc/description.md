# Undalogic uSMU - Single-Channel Source Measure Unit

This driver controls the Undalogic uSMU, a compact USB source-measure unit
for force-voltage / measure-current operation. It is intended for low-cost,
straightforward I-V characterisation and data logging.

## Connection

The uSMU presents itself as a USB virtual COM port. Select the matching COM
port from the Port dropdown. The default baud rate is **9600**.

The device is single channel: every firmware command addresses `CH1`, so no
command takes a channel argument and one instrument is one entity.

## Sweep mode

- **Voltage in V**: Source voltage, measure current.

The uSMU does not support current sourcing.

## Performing voltage sweeps

Use the standard SweepMe! **SweepEditor** to define the list of voltages.
SweepMe! steps through each voltage in turn, and the driver uses the
uSMU's atomic `CH1:MEA:VOL <v>` command to both apply the point and read
back a measurement in one round-trip.

- Data appears in the main data table (one row per point).
- Timing is governed by communication latency plus the per-command 50 ms
  settling delay.

## Compliance / current limit

The **Compliance** field is entered in amperes (matching the SweepMe!
convention across SMU drivers). The driver converts to milliamps before
sending `CH1:CUR`, which is the unit used by the uSMU firmware.

Example: a SweepMe! compliance of `0.02` sends `CH1:CUR 20.0` to the device.

## Current ranging

The uSMU handles current range switching automatically. There are no
user-exposed options for manual range locking.

## Oversampling (Average)

The **Average** field maps to the uSMU's `CH1:OSR` command and controls the
number of samples averaged per measurement. Valid range is **1 to 255**.
The default is `25`, matching the reference Python library. Higher values
reduce noise but increase measurement time.

A measurement takes about **17.6 ms per averaged sample** (measured 2026-11-28:
0.41 s at 25, 0.86 s at 50, 1.76 s at 100, 3.56 s at 200), so the highest
setting needs about 4.5 s. The driver's port timeout is 8 s to cover that. Do
not lower it: if a measurement outlasts the timeout, the read returns an empty
string while the answer is still arriving, the next command is written into it,
and the device stops communicating until it is unplugged.

## Commands

The driver declares its communication commands, so they can be called from
Instrument Control, from scripts and from agents with their units and bounds
checked before the device sees them.

| Command | Kind | Value |
| --- | --- | --- |
| `get_identification()` | read (state) | the device's `*IDN?` string |
| `set_output(output)` | set | `True` enables the output, `False` disables it |
| `set_voltage(voltage)` | set | output voltage in V, without measuring |
| `set_voltage_and_measure(voltage)` | read | sets the voltage and returns the measured voltage in V and current in A |
| `set_current_limit(current_limit)` | set | current limit in A |
| `set_oversample_rate(oversample)` | set | samples averaged per measurement, 1 to 255 |
| `read_adc(adc_channel)` | read | differential ADC conversion between adjacent channels |
| `set_dac(voltage_dac_code)` | set | writes the 16-bit voltage DAC directly |
| `set_current_limit_dac(current_limit_dac_code)` | set | writes the 12-bit current-limit DAC directly |
| `enable_voltage_calibration_mode()` | run | puts the device into voltage calibration mode |

`set_voltage_and_measure` is the command the driver measures with, so a
voltage boundary on a bench has to be set on it as well as on `set_voltage`;
a rule on one does not cover the other.

The last three are for calibration and diagnostics. `set_dac` and
`set_current_limit_dac` write the converters directly and therefore bypass
every voltage and current boundary expressed in volts and amperes;
`enable_voltage_calibration_mode` leaves the device no longer behaving as a
source. Block them on a bench that has a device under test connected.

## Limitations

- The firmware has no query commands for the values that are set, so no
  command reads back the voltage, the current limit, the output state or the
  oversampling rate. Only `set_voltage_and_measure` and `read_adc` read from
  the device.
- The voltage and current ranges of the device are not declared, because the
  firmware documentation available to this driver does not state them. Set the
  bounds that fit what is connected in the bench file.
