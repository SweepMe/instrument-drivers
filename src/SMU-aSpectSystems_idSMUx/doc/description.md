# SMU aSpectSystems idSMUx

This driver controls the source-measure channels of aSpect Systems idSMU2 modules. Each channel is used by its own
SMU module in the sequencer, and the port names the channel, e.g. `M1.S1.C1`. The active channels of one idSMU2 module
are measured together in one asynchronous readout, and a list sweep of up to 52 points can run on the module itself.
Channels of several modules and several boards can be used in the same run.

---

### Requirements:

- One or more idSMU2 modules on an aSpect Systems board, connected via **USB 3.0**.
- The aSpect device engine (`aspectdeviceengine`) is shipped with the driver for 64-bit SweepMe! with Python 3.9 and
  Python 3.14. No further libraries need to be installed.
- If Windows does not find a driver for the board, install the FTDI D3XX driver:
  https://ftdichip.com/wp-content/uploads/2024/06/FTD3XXDriver_WHQLCertified_v1.3.0.10.zip
- The SweepMe! port manager is not used. Press **Find ports** to list the channels of all connected boards.

---

### Supported instruments:

- idSMU2 modules with four channels each.
- Other modules on the board, e.g. DPS or idSMU1 modules, are not supported. If the port points to such a module, the
  run stops with an error that lists the hardware ids found on the board.

---

### Usage:

- Add one SMU module per channel and select the channel as port. The port has the form `M<board>.S<slot>.C<channel>`,
  e.g. `M1.S2.C3` is channel 3 of the module in slot 2 of board 1.
- **Sweep value**: the value forced on the channel, in V or A depending on **Sweep mode**. Select `List sweep` to run a
  list sweep on the module, see below.
- At the start of a run, the driver opens one engine service for all boards, initializes the boards and puts each
  channel into its source mode before setting the compliance. The output is switched on when the sequencer reaches
  the module and switched off at the end of the branch.
- Each set value is checked against the output range reported by the channel. A value outside raises an error.
- Measurement: the first active channel of a module starts one voltage and one current measurement for all active
  channels of that module. The other channels take their values from this readout. Voltage and current are measured
  one after the other, not at the same time.

#### List sweep:

- Select `List sweep` as **Sweep value** and define the values in the **List sweep** section. The sweep runs on the
  module without PC latency; one measurement point of SweepMe! returns the complete list.
- At most 52 values are allowed, including the returning values of a dual sweep.
- All other active channels of the same module are measured at each point of the list. Channels with a normal sweep
  value hold their present value. Channels that run their own list sweep must use the same number of points.

---

### Parameters:

- **Sweep mode**: `Voltage in V` forces a voltage and measures the current, `Current in A` forces a current and
  measures the voltage.
- **Route out**: only `Front`.
- **Compliance**: symmetric limit (+/- value). It is a current in A when forcing voltage and a voltage in V when forcing
  current. The engine resets the limit whenever a channel changes between forcing voltage and current, so the driver
  sets the mode first and the compliance afterwards.
- **Speed/Integration**: number of samples averaged per measurement: `Very fast` 1, `Fast` 16, `Medium` 256,
  `Slow` 4096, `Very slow` 65536. In a normal measurement, the first active channel of a module reads out all
  active channels of that module, and its setting is the sample count of this voltage and current readout. The
  setting of the other channels of the module does not apply.
- **Current range**:
  - `Auto`: with voltage forced, the driver autoranges every channel set to `Auto` before each measurement. Unlike
    the internal autoranging of the module, this also follows current changes from outside effects (light, gate
    voltage, temperature) at a constant set value. With current forced, the smallest range that can deliver the set
    current is selected. In a list sweep, the internal autoranging of the module is used.
  - Entries ending in `idSMU2` (5 uA, 20 uA, 200 uA, 2 mA, 70 mA): fixed current range of the idSMU2.
  - The entries ending in `DPS` belong to the DPS module, which this driver does not support. Do not select them.
- **List sweep** section (only used with `List sweep` as **Sweep value**):
  - **Type**: `Sweep` creates the values from **Start value**, **End value** and the step selection, `Custom` uses
    the comma-separated **Custom values**.
  - Step selection: `Step width`, `Points (lin.)` or `Points (log.)`. With `Step width`, the end value is always
    added as the last point. `Points (log.)` requires start and end values greater than 0.
  - **dual sweep**: appends the values in reverse order.
  - **Delay time in s**: settling time between setting a value and measuring it. If several channels of a module
    run a list sweep, the first of them in the sequencer is the list master and runs the sweep for all of them. Its
    delay time applies to the entire sweep; the delay times of the other list sweep channels are ignored.

---

### Measurement Output:

| Sweep value | Returned variables |
|---|---|
| any other than `List sweep` | **Voltage** in V, **Current** in A |
| `List sweep` | **Voltage** in V, **Current** in A, **Time stamp** in s |

- In a list sweep, all variables are arrays with one entry per list point. SweepMe! writes them to a separate file
  per measurement point. The forced quantity is returned as set, the other one is measured.
- A channel that takes part in the list sweep of another channel without running its own list returns arrays of
  **Voltage** and **Current**, but no **Time stamp**.

---

### Known limitations:

- When the driver version is changed in SweepMe!, the engine library of the previously loaded version stays in use.
  Restart SweepMe! after selecting another driver version.
- Only one engine service may access the boards at a time. A second one takes the USB handle away from the first.
  Do not press **Find ports** while a measurement or an Instrument Control session uses the boards.
- Pulse mode, 4-wire selection and voltage ranges are not supported.
- **Speed/Integration** is not passed to list sweeps; the module averages 1 sample per list point.
- In a list sweep, only the measured quantity is read from the module. The forced quantity is returned as set, not
  as measured.
