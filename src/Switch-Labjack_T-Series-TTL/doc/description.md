# LabJack T4/T7 - digital outputs

This driver sets digital outputs (DIO) of a LabJack T4 or T7 high or low. Digital pins are read with the driver
Logger-Labjack_T-Series-ADC, which reads both digital and analog inputs.

## Requirements

- Install the [LJM software](https://labjack.com/pages/support?doc=/software-driver/installer-downloads/ljm-software-installers-t4-t7-digit/#section-header-two-fhnxc)
  before the first run.

## Connection

The device is identified by its serial number: use *Find ports* and select it.

## Parameters

- **Output pins:** the pins to set, e.g. `EIO0, CIO1`.
- **State (start):** High or Low, set when the branch starts.
- **State (end):** High or Low, set when the branch ends.
- **SweepMode:** *Output* makes the outputs follow the sweep values: 1 is high, 0 is low.

## Notes

- A pin set to output cannot act as an input, and can conflict with a Logger-Labjack_T-Series-ADC reading it.
- Pin names and functions: [digital I/O](https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/130-digital-io-t-series-datasheet/).

## Communication commands

For scripts and agents the driver also offers communication commands, among them `set_digital_output(pin, digital_output)`,
`set_digital_input(pin)`, `get_digital_state(pin)` and the analog commands of the LabJack T-series drivers.
