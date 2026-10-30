# Switch Keysight N773xA

This driver sets the route of a Keysight/Agilent N773xA optical switch. The switch connects its common left
port **A** to one of the numbered right ports. The port number is taken from the sweep value, so the switch
position can be changed from a table, an editor, or any other SweepMe! value source.

---

### Supported instruments:

The driver implements the `ROUTe` subsystem of the Keysight N77xx series programming guide, which covers the
optical switches of the N773xA family:

- **N7731A**
- **N7734A**
- **N7736A**
- **N7738A**

Only 1xN switch configurations are supported, i.e. modules that route the single left port **A** to one of the
numbered right ports. Modules with several left ports and dependent connections, such as the 2x2 crossover
switch, are **not** supported: the driver always routes from port A, and it returns the route string unparsed,
so a parallel connection such as `A,2;B,1` would be reported but could not be set.

Other instruments of the N77xx series — power meters (N774xA, N7747A/48A), attenuators (N775xA, N776xA), and
tunable laser system sources (N7711A, N7714A) — are covered by the drivers `Logger-Keysight_N774x` and
`Switch-Keysight_N777x`.

---

### Requirements:

- The instrument must be connected via **GPIB**, **USBTMC**, or **TCPIP**.
- No further libraries are needed. Communication is handled by the SweepMe! port manager.

---

### Usage:

- Add one instance of the driver per switch that you like to use.
- Hand over the number of the right port to connect to as sweep value, e.g. `1`, `2`, `3`, `4`.
- The driver reads the route back from the instrument after each change so that the actually set configuration
  is saved with the measurement data.

---

### Parameters:

- **SweepMode**: Only `Output port` is supported. The sweep value is the number of the right port.
- **Slot**: Slot number of the switch. Instruments with a single switch use `1`. Instruments with several
  switches have one slot per switch; the slot numbers are printed on the front panel next to each module slot,
  and the installed modules can be listed with `get_options()` (`*OPT?`).

The channel number `[m]` of the `:ROUTe` command is not used. It exists only for compatibility with the
Keysight 816x instruments and is ignored by the N77xx series, which addresses each switch by its slot.

---

### Measurement Output:

- **Route**: The route that is currently set, returned by the instrument as `<left port>,<right port>`,
  e.g. `A,2`.

---

### Known limitations:

- The available right ports are read from the instrument with `:ROUTe[n]:CONFig?` when the driver is used in
  the sequencer, e.g. `A,A;1,4` for a 1x4 switch. A sweep value outside this range stops the run with an error.
- Non-integer sweep values are truncated, e.g. `2.7` selects port `2`.
