# RGB Photonics Qwave

Driver for the Qwave spectrometers of RGB Photonics. It uses the .NET library `RgbDriverKit.dll` of RGB Photonics'
Waves SDK. Without a connected spectrometer the library offers a simulated spectrometer, so the driver can be tried
without hardware.

## Requirements

- `RgbDriverKit.dll` from the Waves SDK (https://www.rgb-photonics.com/downloads/). Put it into the folder
  `ExternalLibraries` of the public SweepMe! folder (`%PUBLIC%\Documents\SweepMe!\ExternalLibraries`) or into the
  driver folder. If the file was downloaded, check in its properties whether Windows blocks it.
- pythonnet (`import clr`) to load the .NET library. SweepMe! brings it; with pysweepme install it with
  `pip install pythonnet`, since it is not part of pysweepme.

## Usage

- **Port**: Find Ports lists the connected spectrometers by their device names. When none is connected, it offers
  `Simulated spectrometer`.
- **Integration time**: in s. A value outside the spectrometer's minimum and maximum exposure time stops the run with
  a message giving the allowed range; earlier versions of the driver clipped it silently.
- **Average**: the number of spectra the spectrometer averages.
- **Calibration**: `SensitivityCalibration On` applies the spectrometer's sensitivity calibration.
- **Trigger**: `Internal` starts each exposure from the driver. `External Rising` and `External Falling` wait for an
  edge at the trigger input; stopping the run ends the wait.
- **Sweep mode** `Integration time in s` sets the integration time of each point.

## Measurement Output

| Variable | Unit | Description |
|---|---|---|
| Wavelength | nm | the wavelengths of the spectrometer's pixels |
| Intensity | a.u. | the spectrum |
| Integration time | s | the integration time of the spectrum |

## pysweepme

Besides the semantic functions the driver offers the commands `get_identification`, `set_integration_time`,
`get_integration_time` and `get_temperature`.
