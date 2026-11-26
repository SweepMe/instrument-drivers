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
  - `Silicon Photonics` — a Gaussian transmission peak in dB that drifts during the run.
  - `No Noise` — the Raman spectrum without random noise, for reproducible tests.
- **IntegrationTime** — integration time in s, greater than 0 s; it can also be swept with the SweepMode
  `Integration time in s`. The intensities are returned per second.
- **Average** — number of spectra averaged per point, at least 1.
- **TriggerDelay** — waiting time in s before each acquisition. **Trigger** has no effect in the simulation.

## Returns

- **Wavelength** (nm) — the wavelengths of the spectrum.
- **Intensity** (counts/s) — the intensity at each wavelength; in `Silicon Photonics` mode the transmission in dB.
- **Integration time** (s) — the integration time in use.

## Communication commands

Usable from Instrument Control and pysweepme scripts without a sequence: `set_spectrum_mode` / `get_spectrum_mode`
(the spectrum otherwise selected in the Port field), `set_integration_time` / `get_integration_time`,
`set_average` / `get_average` and `acquire_spectrum`.

## Scripting with pysweepme

`set_parameters()` applies **SweepMode** and the spectrum selected in the **Port** field at once. **IntegrationTime**,
**Average** and **TriggerDelay** are converted and checked only by `configure()`, as in a SweepMe! run, and keep
their previous values (the defaults 0.1 s, 1 and 0 s) until it runs. Call it before measuring:

```python
import pysweepme

driver = pysweepme.get_driver("Spectrometer-Simulation_Driver", r"<instrument-drivers>\src", "No Noise")
driver.set_parameters({"IntegrationTime": 0.5, "Average": 4, "TriggerDelay": 0.2})
driver.connect()
try:
    driver.initialize()
    driver.configure()  # applies IntegrationTime, Average and TriggerDelay
    print(driver.read())
finally:
    driver.disconnect()
```

The communication commands (`set_spectrum_mode`, `set_integration_time`, `set_average`, ...) take effect at once,
without `configure()`.
