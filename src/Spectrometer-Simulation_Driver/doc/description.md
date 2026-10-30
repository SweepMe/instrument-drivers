# Spectrometer (Simulation Driver)

**Module**: Spectrometer

## Description

A simulated spectrometer for developing and testing Spectrometer sequences without hardware. It returns one of
several simulated spectra. No instrument connection is required.

## Usage

1. Add the Spectrometer module and select this *Simulation Driver*.
2. Choose the spectrum in the **Port** field (see below).
3. Set the integration time and the average, then run the sequence.

## Parameters

- **Port** — selects the spectrum the simulation returns:
  - `Test spectrum.txt` — replays the bundled `test_spectrum.txt` file.
  - `Raman Spectrum` — a Gaussian Raman peak on a simulated background.
  - `Background Spectrum` — the background only, without the Raman peak.
  - `Silicon Photonics` — a Gaussian transmission dip in dB that drifts during the run.
  - `No Noise` — the Raman spectrum without random noise, for reproducible tests.

## Returns

- **Wavelength** (nm) — the wavelengths of the spectrum.
- **Intensity** (counts/s) — the intensity at each wavelength; in `Silicon Photonics` mode the transmission in dB.
