# Monochromator (Simulation Driver)

**Module**: Monochromator

## Description

A simulated monochromator for developing and testing Monochromator sequences without
hardware. It takes a sweep value, converts it to a wavelength in nm, picks the filter
slot that covers that wavelength, and reports the wavelength together with the active
filter. No instrument connection is required.

## Usage

1. Add the Monochromator module and select this *Simulation Driver*.
2. Pick a **SweepMode** (the unit of the swept value, see below).
3. Pick a **Filter**: `Auto` selects the slot whose range contains the wavelength, or
   choose a fixed slot (1–4) to force it.
4. Sweep the value. The driver returns the wavelength and the active filter.

## Parameters

- **SweepMode** — unit of the swept value:
  - `Wavelength in nm` — value is used directly as nm.
  - `Wavelength in eV` / `Energy in eV` — converted with `nm = 1239.84 / value`.
  - `Wavelength in cm-1` — converted with `nm = 1e7 / value`.

  The swept value must be positive; non-positive values raise a descriptive error.

- **Filter** — `Auto` or a fixed filter slot. The simulated filter ranges are:
  - Filter 1: 200–400 nm
  - Filter 2: 400–700 nm
  - Filter 3: 700–1100 nm
  - Filter 4: 1100–1500 nm

  A wavelength outside the selected filter's range raises a descriptive error.

## Returns

- **Wavelength** — the swept value in the selected SweepMode unit (nm, eV, or cm⁻¹).
- **Filter** (`#`) — the active filter slot (1–4).
