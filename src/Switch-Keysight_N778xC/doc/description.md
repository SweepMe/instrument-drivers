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

---

### Measurement Output:

The driver returns one variable:

- **SOP**: the target SOP of the stabilizer, read back from the instrument.
  - In **SOP** mode the value is the normalized Stokes vector in the same `S1;S2;S3` format that is used for
    the input.
  - In **Waveguide Relative** mode the value is `TE` or `TM`. If the read back Stokes vector matches neither,
    an empty string is returned and a message is printed to the Debug widget (F2).

The value is saved but not plotted, as it is a string.

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
