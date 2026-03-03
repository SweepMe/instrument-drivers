# Logger Waveshare AI

This Logger driver reads analog input values from a Waveshare AI module via Modbus RTU over a serial COM port.

---

### Capabilities

- Reads up to 4 channels in one measurement step.
- Supports two output modes:
  - **Voltage in V**
  - **Current in A** (scaled from measured voltage)
- Returns one logged value per selected channel (e.g. `Ch 1`, `Ch 2`, ...).

---

### Communication

- Interface: **COM (Modbus RTU)**
- Default serial settings:
  - `38400` baud
  - `8` data bits
  - `N` parity
  - `1` stop bit
  - timeout `1 s`
- Function code: **FC04** (Read Input Registers)
- Register mapping: channel `1..4` maps to register `0..3`
- **Modbus address** can be configured in the GUI (default `1`).

---

### Value Conversion

- Raw register values are interpreted as millivolts with 1 mV resolution.
- Voltage conversion:
  - `V = raw_value / 1000`
- Current conversion (when `Current in A` is selected):
  - `I = V / 5 * 20`
