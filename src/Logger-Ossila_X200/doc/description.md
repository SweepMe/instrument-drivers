# Logger Ossila X200

This driver enables voltage measurement using the **VSense1** or **VSense2** channels of the Ossila X200 Source Measure Unit. It is designed for high-precision voltage logging applications.

---

### Requirements:

- The Ossila X200 must be connected to your computer via **GPIB**, **COM**, or **TCPIP**.

---

### Usage:

- **Channel Selection**: Choose between **VSense1** or **VSense2** to select which voltage sense channel to monitor.
- **Speed (Oversampling Rate)**: Select the measurement speed from **64** to **32768** samples. Higher values provide better noise reduction but slower measurements. The oversampling rate (OSR) determines the trade-off between speed and accuracy.
- **ADC 2x Mode**: When enabled, this activates the 2x oversampling mode for enhanced measurement precision. This adds 10 to the OSR index internally (OSR range becomes 10-19).
- The driver automatically enables the selected channel during `poweron()` and disables it during `poweroff()`.
- Voltage measurements are returned in **Volts (V)**.

---

### Parameters:

- **Channel**: Select the voltage sense channel to use
  - **VSense1**: First voltage sense channel
  - **VSense2**: Second voltage sense channel
  
- **Speed**: Oversampling rate (OSR) that controls measurement speed and noise reduction
  - Available values: 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768
  - Lower values: faster measurements, more noise
  - Higher values: slower measurements, better noise reduction
  - See manual 5.2.2 for details on OSR and noise reduction
  
- **ADC 2x Mode**: Enhanced speed mode
  - When enabled, unit's measurement rate is approximately doubled

---

### Measurement Output:

The driver returns a single voltage measurement from the selected channel:
- **Voltage**: Measured voltage in Volts (V)

---

### Related Drivers:

- **SMU-Ossila_X200**: Full source-measure unit driver for voltage sourcing using Channels 1 and 2 and current/voltage measurements
- Use the Logger driver when you only need to monitor voltage using the VSense channels
