# Agilent/Keysight E3631A

Driver for the Agilent/Keysight E3631A triple output power supply with a +6 V output (up to 5 A) and two 25 V
outputs, +25 V and -25 V (up to 1 A each).

## Usage

- Choose the output with **Channel**. **Synced +/-25V** switches tracking on: the -25V output follows the +25V output
  with the opposite sign, so a positive voltage sets both. Choosing +25V or -25V switches tracking off when the
  module is configured.
- **Compliance** is the current limit of the output: up to 5 A on +6V, up to 1 A on the 25 V outputs.
- The E3631A switches its three outputs on and off together. Switching the output off in one SweepMe! module also
  stops the other outputs of the same instrument.
- The COM port has not been tested yet. Calibration commands are not implemented.

## Channels

The instrument keeps the selected output (`INST:SEL`), and every command acts on the output selected last. Each
command of the driver therefore takes its `channel` (`+6V`, `+25V`, `-25V` or `TRACK25V`), and the driver selects the
output only when it differs from the one selected last. Several modules or scripts on one instrument share that
knowledge through the port.

- `TRACK25V` is the +25V output with tracking switched on, so it drives both 25 V outputs. The driver declares this,
  so that Instrument Control does not let a bench entry on `TRACK25V` stand beside one on `+25V` or `-25V`.
- A command on `+25V` or `-25V` leaves tracking as it is, so reading the -25V output does not end tracking.
  `set_tracking(False)` switches it off.
- A change made at the front panel, or a raw `INST:SEL` sent past the driver, is not noticed: the next command may
  then act on the wrong output. `reset_instrument` makes the driver select again.

## Communication commands

For scripts and agents the driver offers `set_voltage(channel, voltage)`, `set_current(channel, current)` (the
current limit), their read-backs `get_voltage_setpoint` and `get_current_setpoint`, the measurements `get_voltage`
and `get_current`, `set_output(output)` for all three outputs, `set_tracking(tracking)`, `set_display(display)`,
`clear_status` and `reset_instrument`. The voltages and currents are checked against the rated values of the output.
