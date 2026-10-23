# LabJack T4/T7 - analog and digital inputs

This driver reads the analog inputs (AIN) and digital inputs (DIO) of a LabJack T4 or T7. It supports basic DIO
reads, basic AIN reads and the AIN extended features (EF).

## Requirements

- Install the [LJM software](https://labjack.com/pages/support?doc=/software-driver/installer-downloads/ljm-software-installers-t4-t7-digit/#section-header-two-fhnxc)
  before the first run.

## Connection

The device is identified by its serial number: use *Find ports* and select it.

## Parameters

- **Analog read pins:** the analog pins to read, e.g. `AIN1, AIN2`.
- **Digital read pins:** the digital pins to read, e.g. `EIO0, FIO4`.
- **Extended AIN mode:** applies an EF mode to all selected analog pins. It can also be configured with Kipling or
  the EF config string.
- **EF config string:** EF options parsed into a dictionary, applied to all selected analog pins, e.g.
  `A: 100, B: 3, C: , D:, E:, F:, G:` or `A: 100, B: 4`. See
  [AIN extended features](https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/141-ain-extended-features-t-series-datasheet/).

## Notes

- The EF settings apply to all pins of the read list. To measure two different EFs on the same LabJack, add a second
  logger with the same serial number but other pins and functions.
- Invalid EF parameters lead to errors when the values are read; see the
  [LJM error codes](https://labjack.com/pages/support/software/?doc=/software-driver/ljm-users-guide/error-codes/).
- Thermocouple modes are only available on the T7.
- The flexible pins of the T4 can also be used as analog inputs.
- Pin names and functions: [digital I/O](https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/130-digital-io-t-series-datasheet/)
  and [hardware overview](https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/40-hardware-overview-t-series-datasheet/).

## Communication commands

For scripts and agents the driver also offers communication commands, among them `get_voltage(pin)`,
`set_dac_voltage(channel, voltage)`, digital pins, high speed counters and streaming of analog inputs
(`start_stream`, `read_stream`, `stop_stream`, `acquire_stream`).
