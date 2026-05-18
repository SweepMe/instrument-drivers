# New Era NE-500

## Purpose

SweepMe! driver for the **New Era NE-500 OEM syringe pump**. It sets the
syringe diameter and pumping direction and sweeps the flow rate while
reporting the live pump status.

## Setup

- Connect the pump's 4-pin RJ-11 port to the PC with a USB-to-RS-232 adapter.
- The pump must be in **basic communication mode** (the factory default).
- Communication: 19200 baud, 0.5 s timeout. Commands are framed `STX … ETX`;
  the driver validates each response and raises a clear error on a pump error
  token (`?`, `?NA`, `?OOR`, `?COM`, `?IGN`).

## Usage

- **SweepMode**
  - `Flow rate` — the sweep value is the pumping rate in the selected unit.
  - `None` — do not change the rate; only report status.
- **Rate unit** — `ul/min`, `ul/h`, `ml/min`, `ml/h`.
- **Direction** — `Infuse` or `Withdraw`.
- **Syringe diameter in mm** — inner diameter of the installed syringe
  (0 < d ≤ 50 mm). Required for an accurate volumetric rate.
- **Pump address** — network address of the pump (default `0`).

Per sweep point the driver stops the pump, sets the new rate, and restarts it.
The pump is stopped again at the end of the branch.

### Returned values

- **Flow rate** — the rate applied at the current point (in the selected unit).
- **Status** — pump status: Infusing, Withdrawing, Stopped, Paused,
  Pause phase, Operational trigger wait, or Purging.

## Notes

- A `start_basic_mode()` helper is available for pumps that were left in safe
  mode, but it is not called automatically to avoid sending a safe-mode frame
  to a pump that is already in basic mode.
