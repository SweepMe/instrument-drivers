# New Era NE-500

## Purpose

SweepMe! driver for the **New Era NE-50x OEM syringe pumps** (NE-500, NE-501, NE-500L, NE-501L). It sets the
syringe diameter and pumping direction and sweeps the flow rate while
reporting the live pump status.

## Usage

- **SweepMode**
  - `None` — do not change the rate; only report status.
  - `Flow rate` — the sweep value is the pumping rate in the selected unit.
- **Pump address** — network address of the pump (default `0`).
- **Rate unit** — `ul/min`, `ul/h`, `ml/min`, `ml/h`.
- **Direction** — `Infuse` or `Withdraw`.
- **Syringe diameter in mm** — inner diameter of the installed syringe
  (0 < d ≤ 50 mm). Required for an accurate volumetric rate.

Per sweep point the driver sets the new rate without stopping the pump.
The pump is stopped again at the end of the branch.

### Returned values

- **Flow rate** — the rate applied at the current point (in the selected unit).

## Notes

- The current implementation uses basic communication mode, which is the factory default. The pump also
  supports an advanced mode with a more complex command verification; this is not
  currently implemented.
- The driver has been tested with the NE-500 model, but it should work with the NE-501 and the larger NE-500L and NE-501L models as well.
