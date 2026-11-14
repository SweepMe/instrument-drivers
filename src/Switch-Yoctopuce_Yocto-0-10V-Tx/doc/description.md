# Yoctopuce Yocto-0-10V-Tx

Driver for the Yocto-0-10V-Tx of Yoctopuce, a USB module with two analog outputs of 0 V to 10 V. One instance of the
driver sets one output; use the driver twice, with **Channel** 1 and 2, to set both.

## Requirements

- The module is connected by USB. Yoctopuce's Python library comes with the driver.
- Only one program can use Yoctopuce modules over USB at a time. Close VirtualHub and other programs that use the
  modules, otherwise the driver cannot connect.

## Usage

- **Port**: Find Ports lists the connected Yocto-0-10V-Tx modules by their serial number, e.g. `TX010V01-15BD86`,
  or by their logical name if one was given to the module.
- **Channel**: the output, `1` or `2`.
- **Sweep mode** `Voltage in V` sets the output to the sweep value at each point. With `None` the output is set only
  by the idle voltage and by the driver's commands.
- **Idle voltage in V**: the output is set to this voltage when the run starts and when the driver is no longer used
  in the sequence. Leave the field empty to set no idle voltage.
- The actions **set_voltage_low** and **set_voltage_high** set the output to 0 V and 10 V.

## Measurement Output

| Variable | Unit | Description |
|---|---|---|
| Voltage1 or Voltage2 | V | the voltage the output is set to; the name follows the channel |

The module does not measure its output: the value is the voltage it was asked for.

## Caveats and Limitations

- A voltage outside 0 V to 10 V is refused with a message; it is not clipped.
- After a power cut the module returns to its start-up voltage, 0 V unless `set_voltage_startup` changed it, and
  stays there until a program sets the output again.

## pysweepme

Besides the semantic functions the driver offers the commands `get_identification`, `set_voltage`, `get_voltage`,
`set_voltage_low`, `set_voltage_high`, `set_voltage_startup` and `get_voltage_startup`. `set_voltage_startup` writes
the voltage into the module's flash memory, so that it survives a power cut. Several instances of the driver in one
program share Yoctopuce's USB access; it is closed when the last one disconnects.
