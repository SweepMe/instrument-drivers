# Bronkhorst Propar

## Purpose

SweepMe! driver for Bronkhorst flow and pressure instruments that speak the
**propar** protocol: EL-FLOW, ES-FLOW, (mini) CORI-FLOW, IQ+FLOW, EL-PRESS and
Flexi-Flow mass flow controllers.

Communication is handled by the bundled `bronkhorst-propar` package, so the
SweepMe! port manager is **not** used. Select the COM port via "Find ports".

## Setup

- Connect the instrument via RS-232 or FLOW-BUS (RS-485).
- **Address**: choose `RS232` for a direct serial connection, or the matching
  `FLOW-BUS address` of the unit.
- **Baudrate**: only relevant for RS-232 (default `38400`).

## Usage

### Sweep value

- **Flow in %** — the sweep value is the setpoint in percent (0–100).
- **Flow in custom unit** — define a custom unit and the flow value at 100 %
  ("Flow in c.u. at 100%"); the sweep value is then interpreted in that unit.

### Returned values

Always returned: `Flow`, `Flow setpoint`, `Temperature`, `Density`
(plus the custom-unit columns when a custom unit is configured).

Optional columns (enable via the corresponding checkbox):

- **Measure capacity** — readout value at 100 % in the device capacity unit.
- **Measure valve output** — valve drive signal in %.
- **Measure inlet pressure** / **Measure outlet pressure** — inlet/outlet
  pressure in bar. Requires a device with the corresponding pressure
  sensor (e.g. Flexi-Flow).

### Gas type

The **Gas type** field controls the fluidset:

- **Do not set** — leave the gas/fluid selection unchanged on the device.
- **Read only** — do not change it, but add a `Gas type` column reporting the
  active fluid name.
- **N2 / Air / O2 / H2 / Ar / He / CH4 / CO2** — select that gas (writes the
  fluidset index) before the run.

## Limitations

- Not all device types have been tested; returned variables may need to be
  adapted for specific controller models.

## Acknowledgement

Based on the [bronkhorst-propar](https://pypi.org/project/bronkhorst-propar/)
package, released under the MIT license by Bronkhorst.
