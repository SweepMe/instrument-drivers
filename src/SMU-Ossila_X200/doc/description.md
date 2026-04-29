# SMU Ossila X200

This driver enables voltage sourcing and simultaneous voltage/current measurement using the **SMU1** or **SMU2** channels of the Ossila X200 Source Measure Unit.

---

### Requirements:

- The Ossila X200 must be connected to your computer via **COM**, **USB**, or **TCPIP**.
- Ensure the instrument firmware is up to date for optimal performance.

---

### Usage:

- **Channel Selection**: Choose between **SMU1** or **SMU2** to select which source-measure channel to use.
- **Sweep Mode**: Select **None** (measurement only) or **Voltage in V** (source and measure).
- When in **Voltage** sweep mode, the driver sources the specified voltage and measures both voltage and current.
- **Compliance**: Set the current limit (compliance) when sourcing voltage to protect your device under test.
- The driver automatically enables the selected channel during measurements and disables it when finished.
- Measurements are returned in **Volts (V)** and **Amperes (A)**.

---

### Parameters:

- **SweepMode**: Operation mode
  - **None**: Measurement only (no sourcing)
  - **Voltage in V**: Source voltage and measure current/voltage
  
- **Channel**: Select the source-measure channel
  - **SMU1**: First source-measure unit channel
  - **SMU2**: Second source-measure unit channel
  
- **Compliance**: Current limit in Amperes (A) when sourcing voltage
  - Default: 1 mA (1e-3)
  - Protects the device under test from overcurrent
  
- **Average**: Number of measurements to average
  - Reduces noise through hardware averaging
  - Integer value ≥ 1
  
- **Speed**: Oversampling rate (OSR) that controls measurement speed and noise reduction
  - Available values: 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768
  - Lower values: faster measurements, more noise
  - Higher values: slower measurements, better noise reduction
  - Maps to OSR indices 0-9 (see manual section 5.2.2)

- **ADC 2x Mode**: Enhanced speed mode
  - When enabled, unit's measurement rate is approximately doubled
  - Adds 10 to the OSR index internally (OSR range becomes 10-19)
  
- **Range**: Current measurement range
  - **Auto**: Automatically adjusts the current range during measurement to optimize resolution and accuracy
    - Starts at the highest range (200 mA) to avoid clipping
    - Switches to lower ranges automatically if the measured current is below 10% of the current range limit
    - Switches to higher ranges if the device returns an overrange error
  - **Manual ranges**: 200 mA, 20 mA, 2 mA, 200 µA, 20 µA
    - Select appropriate range for your measurement to optimize resolution and accuracy
    - Maps to range indices 1-5 (see manual section 5.2.4)
  
- **High impedance mode**: Input impedance control
  - When enabled, sets the input to high impedance state
  - Useful for sensitive measurements

---

### Measurement Output:

The driver returns two measurement values:
- **Voltage**: Measured voltage in Volts (V)
- **Current**: Measured current in Amperes (A)

---

### Notes:

- The device performs a measurement for each data point, combining the OSR setting with the Average parameter for noise reduction.
- When using voltage sourcing mode, always set an appropriate compliance value to protect your device under test.
- **Auto-ranging**: When the "Auto" range option is selected:
  - During voltage sourcing in the `apply()` step, the driver automatically increases the range if the set voltage cannot be applied in the current range.
  - During measurements in the `call()` step, the driver automatically switches to the most appropriate range for the measured current.
- The driver does not use the hard reset command to avoid disconnecting communication during operation.

---

### Related Drivers:

- **Logger-Ossila_X200**: Voltage measurement using VSense1/VSense2 channels without sourcing capability
- Use the SMU driver when you need to source voltage and/or measure current in addition to voltage
