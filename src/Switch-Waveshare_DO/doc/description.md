# Switch Waveshare DO

This Switch driver controls a Waveshare Digital Output 8CH module via Modbus RTU over a serial COM port.

---

### Capabilities

- Controls **8 independent digital output channels**.
- Sets each channel state to:
  - **ON**
  - **OFF**
- Applies all configured channel states during driver configuration.

---

### Communication

- Interface: **COM (Modbus RTU / RS485)**
- Default serial settings:
  - `38400` baud
  - `8` data bits
  - `N` parity
  - `1` stop bit
  - timeout `1 s`
- Function code: **FC05** (Write Single Coil/Register value)
- Channel mapping: channel `1..8` maps to address `0..7`
- **Modbus address** can be configured in the GUI (default `1`).

---

### Command Encoding

- ON is written as `0xFF00`
- OFF is written as `0x0000`
- Modbus RTU CRC16 is appended automatically to each command.
