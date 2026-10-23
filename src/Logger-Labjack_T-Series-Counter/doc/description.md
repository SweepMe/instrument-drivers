# LabJack T4/T7 - counters

This driver counts pulses with the high speed counters of a LabJack T4 or T7, in non-stream mode.

## Requirements

- Install the [LJM software](https://labjack.com/pages/support?doc=/software-driver/installer-downloads/ljm-software-installers-t4-t7-digit/#section-header-two-fhnxc)
  before the first run.

## Connection

The device is identified by its serial number: use *Find ports* and select it.

## Parameters

- **Counter read pins:** the pins to count on, e.g. `CIO1, CIO2`.
- **Count time s:** how long is counted, in seconds.
- **Override clock:** for some pins the counter conflicts with the LabJack's internal clock settings if other DIO EF
  functions such as PWM were used. Override makes sure the clocks are set for counting, but may affect other EF
  measurements.
- **Bus time correction in s:** a correction of the measurement duration for the transmission of the stop command over
  USB or Ethernet.

## Notes

- Pin names and functions: [digital I/O](https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/130-digital-io-t-series-datasheet/)
  and [hardware overview](https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/40-hardware-overview-t-series-datasheet/).

## Communication commands

For scripts and agents the driver also offers communication commands, among them `enable_counter(pin)`,
`get_counter(pin)`, `reset_counter(pin)` and `disable_counter(pin)`, and the analog and digital commands of the
LabJack T-series drivers.
