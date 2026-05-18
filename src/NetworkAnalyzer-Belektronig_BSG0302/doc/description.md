# Belektronig BSG0302 — Network Analyzer

## Purpose

SweepMe! driver for the **Belektronig BSG0302** S-parameter scan capability.
It triggers reflection and transmission scans and returns the frequency axis
together with the selected S-parameters.

Signal generation (frequency/power/phase sweeps) is provided by the separate
**Signal-Belektronig_BSG0302** driver.

## Setup

- Connect via RS-232; select the COM port with "Find ports".
- Communication is binary at 9600 baud, commands terminated with carriage
  return.

## Usage

- **Sparameters** — comma-separated list of `S11`, `S12`, `S21`, `S22`.
  - `S11`, `S22` → reflection scan; `S12`, `S21` → transmission scan.
  - The channel is `2` for `S2x` and `1` otherwise.
- **FrequencyStart / FrequencyEnd** — scan range in Hz (1 MHz ≤ start <
  stop ≤ 215 MHz).
- **Points** — number of scan points (2–65535).
- **Unit**
  - `lin` — linear magnitude (10^(dB/20)).
  - `db` — magnitude in dB as returned by the device.

### Returned values

- **Frequency** — Hz, linearly spaced between start and stop.
- One array per requested S-parameter, aligned with the frequency axis.

## Notes

- A scan can take noticeably longer than a single command; the block readback
  retries until the expected number of bytes has arrived.
