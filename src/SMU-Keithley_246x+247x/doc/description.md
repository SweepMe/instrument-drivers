# SMU Keithley 246x+247x

This driver sources voltage or current and measures both quantities with the Keithley source measure
units 2460, 2461 and 2470 using the TSP command set. One driver instance controls one instrument.
Several instruments that are linked via TSP-Link can be controlled through a single port.

---

### Requirements:

- The instrument must be connected via **USB** (USBTMC), **GPIB** or **TCPIP** (LAN).
- No further libraries are needed. Communication is handled by the SweepMe! port manager. The timeout
  is 10 s plus the time that one measurement can take with the selected **Speed** and **Average**.
- The driver uses the communication commands of pysweepme and needs SweepMe! 1.6.1.5 or newer.
- The instrument must use the **TSP command set**. It is selected on the front panel with MENU >
  System > Settings > Command Set, or with the command `*LANG TSP`, followed by a restart of the
  instrument. With the SCPI command set the run stops with an error message.
- To reach instruments via TSP-Link, see *TSP-Link* below.

---

### Supported instruments:

| Model | Current ranges | Highest source values |
|-------|----------------|-----------------------|
| 2460  | 1 uA to 7 A    | 105 V, 7.35 A         |
| 2461  | 1 uA to 7 A    | 105 V, 7.35 A         |
| 2470  | 10 nA to 1 A   | 1100 V, 1.05 A        |

- The 10 A range and the pulse and digitize functions of the 2461 are not supported.
- Other models of the series, e.g. the 2450, are rejected at the start of the run.
- The driver does not check the source level against the limits of the model. A level that the
  instrument does not accept stops the run at the next measurement, see *Error handling*.

---

### Usage:

- Add one instance of the driver for each instrument.
- The sweep value is the source level: a voltage in V if **SweepMode** is `Voltage in V`, a current in
  A if **SweepMode** is `Current in A`.
- At the start of the run, the driver checks the command set and the model, clears the event log and
  resets the source and measure settings of the instrument (`smu.reset()`). It also switches off the
  automatic output of events and prompts (`localnode.showevents`, `localnode.prompts`) for the
  interface in use, in case another program has switched them on.
- Source function, ranges, compliance, integration time, sensing, terminals and filter are configured,
  then the output is switched on.
- For each measurement point the new source level is sent and one reading is made. The measured
  quantity and the source value that the instrument recorded with it are returned.
- At the end of the run the output is switched off and the instrument returns to 2-wire sensing. The
  last source level stays programmed while the output is off.

---

### Parameters:

- **SweepMode**: `Voltage in V` or `Current in A`. Selects which quantity is sourced. The other
  quantity is measured.
- **RouteOut**: `Front` or `Rear` terminals.
- **Speed**: Integration time of the measurement in power line cycles: `Fast` = 0.1 NPLC,
  `Medium` = 1 NPLC, `Slow` = 10 NPLC.
- **Range**: Current range. If voltage is sourced, it is the range of the current measurement:
  - `Auto`: auto ranging without restriction.
  - `Limited <range>`: auto ranging, but the instrument does not range below `<range>`. This avoids
    the settling time of the lowest ranges.
  - `Fixed <range>`: auto ranging is switched off and `<range>` is used. **Compliance** must then be
    between 10 % and 105 % of the range, otherwise the run stops with an error message. With the
    default compliance of 100 uA, only the fixed ranges 100 uA and 1 mA can be used.

  If current is sourced, it is the range of the current source: `Fixed <range>` selects a fixed source
  range, `Auto` and `Limited <range>` both use the auto range of the source. The voltage is always
  measured with auto ranging.

  The list contains the ranges of all supported models. A range that the connected model does not
  have stops the run with an error message.
- **Average**: Number of readings that are averaged, 1 to 100. Values above 1 switch on the repeating
  average filter of the instrument.
- **Compliance**: The limit of the quantity that is not sourced: a current in A if voltage is sourced,
  a voltage in V if current is sourced. After the configuration the driver reads the limit back and
  stops the run if the instrument uses another value.
- **4wire**: If checked, the instrument uses 4-wire (remote) sensing. The sense terminals must be
  wired.
- **TSP-Link node**: `Local` addresses the instrument that is connected to the port. `Node <N>`
  addresses the instrument with TSP-Link node number N through the connected instrument, see
  *TSP-Link*.

---

### Measurement Output:

- **Voltage**: Voltage in V.
- **Current**: Current in A.

The sourced quantity is the value that the instrument measured at its output (source readback), not
the programmed level. If the instrument is in compliance, it therefore shows the level that was
actually reached. A reading above `1e37`, which is the overflow value of the instrument, is returned as
`nan`.

---

### TSP-Link:

- Connect the instruments with each other at their TSP-Link connectors and connect one of them to the
  computer. This instrument must be a 2460, 2461 or 2470 as well. When instruments of older series
  such as the 2600B are part of the network, the manual asks for a 246x or 2470 as the instrument
  that is connected to the computer.
- Each instrument needs its own node number from 1 to 63 (MENU > System > Communication > TSP-Link).
- The TSP-Link network must be initialized before the run (button Initialize on the same screen, or
  `tsplink.initialize()`). This must be repeated whenever one of the linked instruments was switched
  off, a node number was changed or the TSP-Link cabling was changed. The driver does not initialize
  the network itself, because this switches off the outputs of all linked instruments.
- Add one instance per instrument, all with the same port. The instrument connected to the port uses
  **TSP-Link node** = `Local`, the others `Node <N>`. All commands to them are sent as
  `node[N].smu...`.
- At the start of the run, the driver checks for a remote node that `tsplink.state` is `online` and
  that the reset of the instrument does not create an error. A node number that is not part of the
  network stops the run with an error message.
- Measurements on several instruments are made one after the other, not at the same time.
- While the driver communicates through TSP-Link, all linked instruments are in remote operation.

---

### Error handling:

- The driver reads the event log of the instrument connected to the port after the reset, after the
  configuration, after switching on the output and with every measurement. An error stops the run and
  shows the message of the instrument, e.g. for a source level outside the range or an output that is
  blocked by the interlock. Warnings during the configuration are shown in the info box and written
  to the logbook.
- All instruments of a TSP-Link network write into the event log of the instrument connected to the
  port. An error can therefore be reported by another driver instance than the one that caused it.
  The message names the instrument it comes from: the instrument connected to the port or the
  TSP-Link node number.
- The event log is cleared at the start of the run.

---

### Known limitations:

- The driver has been written from the reference manuals of the three models (2460-901-01 Rev. C,
  2461-901-01 Rev. B, 2470-901-01 Rev. D) and has not been tested with an instrument yet.
- Only the TSP command set is supported, as TSP-Link is not available with SCPI commands.
- The reference manuals give different values for the lowest compliance with a fixed range (0.1 %,
  10.6 % and, in the specifications of the 2460 and 2461, 10 % of the range). The driver uses 10 %.
  If the instrument does not accept a compliance that the driver has let through, the run stops after
  the configuration, before the output is switched on.
- The timeout assumes a line frequency of 50 Hz and up to six integration times per reading (autozero
  and source readback). Range changes of the auto ranging are not included.
- Autozero, source readback and the output-off mode keep the reset defaults of the instrument:
  autozero and source readback are on, the output-off mode is normal.
- With auto ranging, the instrument limits the output to 105 % of the present current measurement
  range until the next measurement selects a higher range (see "autorange rebound" in the reference
  manual). After a step from a small to a large current, the output can therefore be limited for a
  short time below **Compliance**.
- Without the safety interlock, the 2460 and 2461 limit the 100 V range and the 2470 the 200 V and
  1000 V ranges to about 42 V. The driver does not read the interlock state.
- The overvoltage protection of the instrument is not set by the driver.
- The driver does not report whether the instrument is in compliance. In compliance, the sourced
  quantity is below the programmed level and the measured quantity is equal to **Compliance**.
- Pulses, sweeps that run inside the instrument, and the trigger model are not supported.
