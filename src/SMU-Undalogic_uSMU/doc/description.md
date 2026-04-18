# Undalogic uSMU - Single-Channel Source Measure Unit

This driver controls the Undalogic uSMU, a compact USB source-measure unit
for force-voltage / measure-current operation. It is intended for low-cost,
straightforward I-V characterisation and data logging.

## Connection

The uSMU presents itself as a USB virtual COM port. Select the matching COM
port from the Port dropdown. The default baud rate is **9600**.

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
