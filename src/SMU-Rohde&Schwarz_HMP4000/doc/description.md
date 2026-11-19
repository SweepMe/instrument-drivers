# Rohde & Schwarz HMP2020, HMP2030, HMP4030, HMP4040

Laboratory power supplies of the R&S HMP series with two (HMP2020), three (HMP2030, HMP4030) or four (HMP4040)
galvanically isolated channels of 0 to 32 V. The maximum current per channel is 5 A (HMP2030) or 10 A (HMP4030 and
HMP4040), reduced above 16 V by the channel's power limit (80 W or 160 W); the two channels of the HMP2020 differ,
see its specifications. Every channel is a separate instance of this driver (the SMU module's `Channel` field);
all instances share the port.

The driver follows the R&S HMP Series user manual, version 05 (firmware V2.7x and later). The model is read from
`*IDN?` at the start of a run: a channel the connected model does not have is refused with a message naming the model.

## Connection

One of the optional interface modules is needed:

- LAN (HO732): raw socket only, `TCPIP::<ip address>::5025::SOCKET`. A VXI-11 resource (`...::INSTR`) is refused.
- USB (HO720, HO732): as USBTMC, or as a virtual COM port with the R&S VCP driver.
- RS-232 (HO720): 9600 baud by default; match the baud rate, stop bits and parity of the instrument's interface
  settings. Without handshake the manual asks for 50 to 100 ms between commands; raise the port's `delay` in the
  port dialog if commands get lost.
- GPIB (HO740).

## How the SMU module fields map

- `SweepMode`:
  - `Voltage in V`: the sweep value is the voltage setpoint, `Compliance` is the current limit in A.
  - `Current in A`: the sweep value is the current limit setpoint, `Compliance` is the voltage setpoint in V. The HMP
    is a constant-voltage/constant-current supply, not a current source: it delivers the set current only while the
    load lets it reach the current limit (CC mode, the channel key lights red); otherwise it stays at the set
    voltage (CV mode).
  - `... (with wait)`: the driver waits 0.5 s after every new value before the other channels are set.
- `Channel`: 1 to 4; only the channels of the connected model are accepted.
- `Compliance`: the limit of the quantity that is not swept (see `SweepMode`).
- `RouteOut`: the HMP has front terminals only.
- Returned variables: `Voltage` and `Current`, measured by the instrument (`MEAS:VOLT?`, `MEAS:CURR?`).

Lifecycle: `configure` writes the limit and starts the swept quantity at 0 with the output still off; `poweron`
arms the channel (`OUTP:SEL 1`) and switches the general output on (`OUTP:GEN 1`); `poweroff` disarms the channel
only (`OUTP:SEL 0`), so other channels used in the same sequence keep delivering. The general output stays on after
a run; with no channel armed nothing delivers. Note that `OUTP:GEN 1` switches on every armed channel, also one
armed from the front panel (a blinking channel key).

## Communication commands

The channel is a stateful selector: the driver sends `INST OUT<n>` only when a command addresses another channel
than the one selected last.

- `get_identification()`: `*IDN?` (state).
- `get_error()`: oldest entry of the error queue, `SYST:ERR?` (state).
- `reset_instrument()`: `*RST`, every setting back to default, outputs off.
- `clear_status()`: `*CLS`.
- `set_voltage(channel, voltage)`: voltage setpoint, 0 to 32.05 V (`VOLT`).
- `get_voltage_setpoint(channel)`: read back the voltage setpoint (`VOLT?`).
- `get_voltage(channel)`: measure the voltage (`MEAS:VOLT?`).
- `set_current(channel, current)`: current limit (`CURR`); at most 5 A on the HMP2030, 10 A on the HMP40x0, not
  checked on the HMP2020. The lower limit is the instrument's own (`CURR? MIN`).
- `get_current_setpoint(channel)`: read back the current limit (`CURR?`).
- `get_current(channel)`: measure the current (`MEAS:CURR?`).
- `set_output_armed(channel, output_armed)`: arm or disarm the channel (`OUTP:SEL`); an armed channel delivers
  while the general output is on.
- `set_general_output(general_output)`: the general output for all armed channels (`OUTP:GEN`).
- `set_output(channel, output)`: composite; on = arm and general output on, off = disarm.
- `get_output(channel)`: whether the channel's output is on (`OUTP?`).
- `unlock_local_interface()`: back to front-panel control (`SYST:LOC`).

Not wrapped: `APPLy` (voltage and current in one command), `OUTPut[:STATe]` as a setter (the manual does not say
what `OUTP 0` does to the general output of the other channels), the fuse, overvoltage protection, arbitrary and
status subsystems. `OUTP:SEL?` and `OUTP:GEN?` are not documented as queries and are not used.

## Not tested

The driver was converted from the manual without an instrument: the per-channel `poweroff` (`OUTP:SEL 0` while
the general output stays on), the `OUTP?` read-back and the model names in `*IDN?` should be checked on the
instrument first.
