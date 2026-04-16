# Undalogic miniSMU MS01 - 2-Channel Source Measure Unit

This driver controls the Undalogic miniSMU MS01, a dual-channel SMU supporting voltage and current sourcing, hardware-accelerated I-V sweeps, and 4-wire Kelvin sensing.

## Connection

The miniSMU supports two connection methods:

- **USB:** Select the corresponding COM port from the Port dropdown. No additional configuration is needed.
- **WiFi:** Select or enter a SOCKET port in the format `TCPIP0::<ip>::3333::SOCKET`, replacing `<ip>` with the device IP address. The TCP port defaults to **3333** and can be omitted (it will be added automatically).

A template entry is provided in the Port dropdown for WiFi connections.

## Sweep modes

- **Voltage in V** (FVMI): Source voltage, measure current.
- **Current in A** (FIMV): Source current, measure voltage.

## Performing voltage sweeps

There are two ways to run a voltage sweep, each with different trade-offs:

### Option 1: SweepEditor (point-by-point)

Use the standard SweepEditor to define sweep values. SweepMe! steps through each voltage one at a time, measuring at each point. This is the recommended approach for most use cases.

- Data appears in the **main data table** (one row per point).
- Works with both "Voltage in V" and "Current in A" modes.
- Sweep timing depends on communication latency (USB or WiFi).

### Option 2: List Sweep (hardware-accelerated)

Select "List sweep" as the sweep value source to use the miniSMU's onboard sweep engine. The device executes the entire sweep internally with precise timing, then returns all data at once.

- Up to 1000 points with configurable dwell time (0-10000 ms).
- Faster and more consistent timing than point-by-point.
- **Important:** Data is saved to a separate 1D data file (`Data1D_*.txt`), not the main data table. The main table will show `--` for that measurement point. The plot will still display the data correctly.
- **Only available in "Voltage in V" mode.** The onboard sweep does not support current sourcing. For current sweeps, use the SweepEditor.

## 4-wire (Kelvin) sensing

Enable the "4wire" checkbox to use 4-wire measurement mode. In this mode:

- Channel 1 acts as the force/source channel.
- Channel 2 acts as the high-impedance sense channel.
- Measurements return the true DUT voltage (from CH2) and current (from CH1), eliminating lead resistance errors.

4-wire mode is only available when Channel 1 is selected.

## Current ranges

| Range    | Maximum current |
|----------|----------------|
| Auto     | Automatic       |
| 1 uA     | +/- 1 uA       |
| 25 uA    | +/- 25 uA      |
| 650 uA   | +/- 650 uA     |
| 15 mA    | +/- 15 mA      |
| 180 mA   | +/- 180 mA     |

When left set to "Auto", the miniSMU will automatically switch to the most appropriate current range without user intervention

## Oversampling

The oversampling ratio (0-15) controls measurement averaging. Higher values reduce noise but increase measurement time. Each step roughly doubles the number of averaged samples.
