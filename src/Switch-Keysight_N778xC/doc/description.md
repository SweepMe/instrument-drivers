# Switch Keysight N778xC

This driver sets the **state of polarization (SOP)** of a Keysight N778xC polarization synthesizer, i.e. the
N7786C or the N7788C. The requested polarization is used as the target of the built-in polarization stabilizer,
so the instrument actively holds the polarization while the measurement runs.

The N7785C is not supported, as it has no built-in polarimeter and can therefore only stabilize with an
external feedback signal.

---

### Requirements:

- The instrument can be connected via the **USB-B** port at the rear and used as a **USBTMC** port, or via
  **Ethernet** and used as a **TCPIP** port.
- The USB connection additionally enumerates as a virtual Ethernet link that assigns itself an IP address from
  the block 100.61.x.x. The instrument can therefore also be used as a TCPIP port without a network cable. If
  no USBTMC port shows up in SweepMe!, look for the instrument in the Keysight Connection Expert and use its
  TCPIP address instead.
- A Keysight IO Libraries / VISA installation is needed for both port types.

---

### Usage:

- Choose the **SweepMode** that matches the way you want to define the polarization and hand over the values
  with the **SweepValue** widget, e.g. as a list of values or from a text file.
- At the start of the run the working memory of the instrument is preset and the polarimeter wavelength is
  set. The settings that are stored in the non-volatile memory of the instrument are kept.
- Each time a new sweep value is applied, the driver switches the stabilizer off, writes the new target SOP,
  switches the stabilizer on again, and reads the target SOP back to verify that the instrument accepted it.
  If the read back value deviates by more than 1e-3 from the requested one, the run stops with an error.

---

### Parameters:

- **SweepMode**: defines how the sweep values are interpreted.
  - **SOP**: the sweep value is a Stokes vector given as three `;`-separated numbers `S1;S2;S3`,
    for example `1;0;0`. The semicolon is used as separator so that the values are not split up by the
    comma-separated value lists of the SweepMe! sequencer. The vector is normalized by the driver to a degree
    of polarization of 1, as the instrument expects a normalized Stokes vector. `0;0;0` is not a valid value.
  - **Waveguide Relative**: the sweep value is the name of a polarization that is aligned to a waveguide.
    Supported values are `TE` (Stokes vector `1;0;0`) and `TM` (Stokes vector `-1;0;0`). The value is
    case-insensitive. This assumes an alignment in which TE corresponds to S1 = +1, so check the orientation
    of your fiber and waveguide before relying on it.
- **Wavelength in nm**: the wavelength of the polarimeter. The polarimeter is wavelength calibrated, so this
  must match the wavelength of your source for the SOP to be measured and stabilized correctly. It is applied
  in `configure()`, as the preset at the start of the run restores the default wavelength.
- **Correction**: `None` sets the SOP at the output of the instrument. `From file` sets the SOP at the end of
  the fiber that connects the instrument to your device, see [Fiber correction](#fiber-correction).
- **Correction file**: only shown for `From file`. Path to the correction file (`.json`).

---

### Fiber correction:

A fiber changes the SOP on its way from the instrument to the device under test. This change is described by a
3x3 transformation matrix M that acts on the normalized Stokes components S1, S2, S3:

`s_fiber_end = M * s_instrument`

M is determined with three linearly independent, known SOPs, e.g. horizontal `1;0;0`, linear 45° `0;1;0` and right
circular `0;0;1`. The set SOPs form the columns of `S_Soll`, the SOPs measured at the fiber end the columns of
`S_Ist`, and `M = S_Ist * S_Soll^-1`.

With **Correction** `From file`, the SOP entered as sweep value (or `TE`/`TM`) refers to the fiber end. The driver
sends `s_Synth = M^-1 * s_Ziel` to the instrument, normalized to unit length as the instrument expects, so that
the fiber turns it into the requested SOP. M only holds for one wavelength and fiber position and drifts with
temperature, so the calibration should be repeated regularly.

The correction file can be created with the CustomFunction script **Polarization_Calibration**, which calculates
M from the SOPs measured with a polarimeter (e.g. Thorlabs PAX1000) at the fiber end, or with any other tool. The
format is shown in `examples/correction_example.json`, whose matrix is only an example. Required are:

- `calibrations`: a list with one entry per wavelength, each with
  - `wavelength_nm`: wavelength of the calibration in nm
  - `transformation_matrix`: M as list of three rows, e.g. `[[1, 0, 0], [0, 1, 0], [0, 0, 1]]` for no correction

All other keys (`description`, `created`, `points`) are optional information. If `created` is given in ISO format
(e.g. `2026-10-01T08:00:00`) and the file is older than one day, a message is printed to the Debug widget (F2).

At the start of the run the driver checks that a calibration exists within 0.5 nm of **Wavelength in nm** (the
closest one is used) and that M has 3x3 elements and can be inverted.

---

### Measurement Output:

- **SOP**: the SOP read back from the instrument (the target SOP of the stabilizer). With a correction, it is
  transformed to the fiber end, i.e. it is the SOP that was requested.
  - In **SOP** mode the value is the normalized Stokes vector in the same `S1;S2;S3` format that is used for
    the input.
  - In **Waveguide Relative** mode the value is `TE` or `TM`. If the Stokes vector matches neither, an empty
    string is returned and a message is printed to the Debug widget (F2).
- **Applied SOP**: only with a correction. The SOP that is set at the instrument output, as `S1;S2;S3`.

The values are saved but not plotted, as they are strings.

---

### Caution:

- The driver reports the **target** SOP of the stabilizer (`:STABilizer:SOP?`), not the polarization that is
  measured by the polarimeter. Use the polarimeter functions of the instrument if you need the actually
  measured Stokes parameters.
- If **Stabilizer invert** is switched on at the instrument, `:STABilizer:SOP?` returns the inverted target
  SOP. The read back check of the driver then fails, so switch it off before the run.
- While the stabilizer is running, most other polarimeter and scrambler commands are blocked by the
  instrument, zeroing among them.
- The polarimeter gain influences the stabilizer bandwidth. Keysight recommends a gain between 0 and 7 for the
  stabilizer mode, as gain 8 and 9 have a bandwidth of only about 10 kHz. The autogain setting is ignored
  while stabilizing. The driver does not change the gain, so set it at the instrument if the stabilization is
  too slow.
- The stabilizer stays switched on when the run ends, so the instrument keeps holding the last polarization.
