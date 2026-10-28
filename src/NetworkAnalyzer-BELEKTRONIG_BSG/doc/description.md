# BELEKTRONIG BSG0302 — Network Analyzer

## Purpose

SweepMe! driver for the **BELEKTRONIG BSG0302** S-parameter scan capability. It triggers reflection and
transmission scans and returns the frequency axis together with the selected S-parameters.

Signal generation (frequency/power/phase sweeps) is provided by the separate **Signal-BELEKTRONIG_BSG** driver.

## Setup

- Connect via RS-232; select the COM port with "Find ports".
- Communication is binary at 9600 baud, commands terminated with carriage return.

## Usage

- **Sparameters** — comma-separated list of `S11`, `S12`, `S21`, `S22`.
  - `S11`, `S22` → reflection scan; `S12`, `S21` → transmission scan.
  - The channel is `2` for `S2x` and `1` otherwise.
- **SourcePower** — output power in dBm, set on every channel used by the selected S-parameters.
- **FrequencyStart / FrequencyEnd** — scan range in Hz (1 MHz ≤ start < stop ≤ 215 MHz).
- **FrequencyStepPoints** — number of scan points (2–65535), linearly spaced.

### Returned values

- **Frequency** — Hz, linearly spaced between start and stop.
- One array per requested S-parameter in dB, aligned with the frequency axis. The device measures magnitudes only,
  no phase.

## Notes

- A scan can take noticeably longer than a single command; the block readback retries until the expected number of
  bytes has arrived and stops with an error if the data stays incomplete.
