# Belektronig BSG0302 — Signal Generator

## Purpose

SweepMe! driver for the **Belektronig BSG0302** two-channel RF signal
generator. It configures one channel as a frequency generator and sweeps
frequency, output power (dBm or W) or signal phase.

The S-parameter scan capability of the BSG0302 is provided by the separate
**NetworkAnalyzer-Belektronig_BSG0302** driver.

## Setup

- Connect via RS-232; select the COM port with "Find ports".
- Communication is binary at 9600 baud (0.5 s timeout), commands terminated
  with carriage return.

## Usage

- **Channel** — `1` or `2` (channel 2 must be present on the device).
- **SweepMode**
    - `Frequency in Hz` — sweep the output frequency (1–215 MHz, entered in Hz).
    - `Power in dBm` — sweep the output power (−30 to 36 dBm).
    - `Power in W` — sweep the output power (1e-6 to 3.9 W).
    - `Phase in deg` — sweep the signal phase (−180 to 180°).
    - `None` — only read back values.
- **Frequency in Hz / Power in dBm / Phase in deg** — static setpoints used for
  the quantities that are *not* being swept.

[//]: # (- **Modulation** — `NONE`, `AM`, `FM`, `PM`.)
[//]: # (- **Trigger** — `INTERNAL`, `BY_PC`, `EXTERNAL`.)

### Returned values

- **Frequency** (Hz), **Output power** (dBm), **Input power** (dBm),
  **Temperature** (°C) of the selected channel.

## Notes

- Out-of-range frequency, power or phase values raise an error and stop the
  measurement.
