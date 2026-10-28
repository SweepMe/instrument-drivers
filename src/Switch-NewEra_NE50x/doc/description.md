# New Era NE-50x

## Purpose

SweepMe! driver for the **New Era NE-50x OEM syringe pumps** (NE-500, NE-501, NE-500L, NE-501L). It sets the
syringe diameter, pumping direction and motor noise mode, and sweeps the flow rate.

## Usage

- **SweepMode**
  - `None` — do not change the rate; only read back the flow rate.
  - `Flow rate` — the sweep value is the pumping rate in the selected unit.
- **Pump address** — network address of the pump (default `0`).
- **Rate unit** — `ul/min`, `ul/h`, `ml/min`, `ml/h`.
- **Direction** — `Infuse` or `Withdraw`.
- **Syringe diameter in mm** — inner diameter of the installed syringe (0 < d ≤ 50 mm). Required for an accurate
  volumetric rate.
- **Low motor noise** — run the motor in low-noise mode (default on).

Per sweep point the driver sets the new rate without stopping the pump. The pump is stopped again at the end of the
branch.

### Returned values

- **Flow rate** — the rate reported by the pump (in the selected unit).

## Notes

- Rates and diameters are sent with at most 4 digits and 3 decimals, as required by the pump; values are rounded
  accordingly, and values of 1000 or more in the selected unit are rejected. Choose a larger rate unit if needed.
- The driver uses the basic communication mode, which is the factory default. A pump that was switched to safe mode
  is returned to basic mode at the start of the run. Safe mode itself is not supported.
- The driver has been tested with the NE-500 model; the NE-501 and the larger NE-500L and NE-501L use the same
  command set.
