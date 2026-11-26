# Logger Yokogawa AQ6374

This driver records optical spectra with the Yokogawa AQ6374 optical spectrum analyzer. For each measurement
point, a single sweep is started and the selected trace is read out. Optionally, one of the analysis functions
of the instrument is executed and its results are returned as additional variables.

---

### Requirements:

- The instrument must be connected via **GPIB**, **USBTMC**, or **TCPIP**.
- No further libraries are needed. Communication is handled by the SweepMe! port manager.
- The driver switches the instrument to the AQ637x command set (`CFORM1`) during initialization.

---

### Usage:

- The wavelength range, the resolution, and the sensitivity are applied when the driver is used in the
  sequencer. The number of sampling points is determined automatically by the instrument.
- Each measurement point starts a single sweep and waits until the sweep completion bit of the operation
  event register is set. Stopping the run interrupts the waiting.
- The spectrum is returned as an array and is written to a separate file per measurement point by SweepMe!.

---

### Parameters:

- **Active trace**: Trace that is swept and read out, `TRA` to `TRG`.
- **Start wavelength in nm**: Start of the sweep range.
- **Stop wavelength in nm**: Stop of the sweep range.
- **Resolution in nm**: Resolution bandwidth of the sweep.
- **Sensitivity**: Sensitivity/chop mode. `MID`, `NORMal`, `HIGH1`, `HIGH2`, and `HIGH3` increase the
  sensitivity at the cost of sweep time. `NHLD` is normal/hold and `NAUT` is normal/auto.
- **Analysis**: Analysis function that is executed after each sweep, or `None` to record the spectrum only.
  The selection determines which additional variables the driver returns.
- **SMSR mode**: Only shown if `Analysis` is set to `SMSR`. `SMSR1` and `SMSR2` evaluate one side mode,
  `SMSR3` and `SMSR4` evaluate the side modes on the shorter and on the longer wavelength side separately and
  therefore return twice as many values.

---

### Measurement Output:

The driver always returns the spectrum and the position of its maximum:

- **Wavelength**: Wavelength values of the trace in m (array).
- **Intensity**: Level values of the trace in dBm (array).
- **Marker wavelength**: Wavelength of the trace maximum in m, read from the moving marker.
- **Marker level**: Level of the trace maximum in dBm, read from the moving marker.

The marker values are named differently from the analysis values on purpose. Several analysis functions
return their own `Peak wavelength` and `Peak level`, which are determined more accurately than the marker
position, and the variable names have to stay unique.

If an analysis function is selected, its values are appended. The values and their order are defined by the
instrument, see section 6.7 of the remote control manual:

| Analysis | Returned variables |
|---|---|
| Spectrum width (THRESH / ENVELOPE / PEAK RMS) | Center wavelength, Spectrum width, Mode number |
| Spectrum width (RMS) | Center wavelength, Spectrum width |
| Notch width | Center wavelength, Notch width |
| SMSR (SMSR1, SMSR2) | Peak wavelength, Peak level, 2nd peak wavelength, 2nd peak level, Delta wavelength, SMSR |
| SMSR (SMSR3, SMSR4) | the six values above, but with the 2nd peak, delta, and SMSR values once for the shorter (L) and once for the longer (R) wavelength side |
| Power | Total power |
| DFB-LD | Spectrum width, Peak wavelength, Peak level, Mode offset, SMSR |
| FP-LD | Spectrum width, Peak wavelength, Peak level, Center wavelength, Total power, Mode number |
| LED | Spectrum width, Peak wavelength, Peak level, Center wavelength, Total power |
| PMD | Left mode peak, Right mode peak, PMD |
| Filter peak | Peak wavelength, Peak level, Center wavelength, Spectrum width, Left crosstalk, Right crosstalk, Ripple |
| Filter bottom | Bottom wavelength, Bottom level, Center wavelength, Notch width, Left crosstalk, Right crosstalk |
| Color | Dominant wavelength, x, y, z |

`:CALCulate:DATA?` offers no access by key. It returns one flat, comma separated list whose meaning depends
only on the selected analysis category, so the driver assigns the values by their position. The number of
returned values is checked against the expected number, and a mismatch raises an error instead of silently
mislabelling the data.

---

### Known limitations:

- A sweep must complete within 600 s, otherwise the driver raises a timeout error.
- The analysis functions that return one value set per WDM channel — WDM, EDFA-NF, WDM FIL-PK, and
  WDM FIL-BTM — are not available, because the number of returned values depends on the measured spectrum and
  the driver output variables have to be known before the run starts.
- The parameters of the analysis functions, e.g. the threshold level of a spectrum width analysis, are taken
  as they are set at the instrument. Only the SMSR mode is set by the driver.
