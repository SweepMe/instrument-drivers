# Temperature JUMO diraTRON

This driver supports **JUMO diraTRON 104/108/116/132** temperature controllers via **Modbus RTU** over a serial COM interface.

---

### Capabilities

- Reads and logs:
  - **Temperature** (`°C`)
  - **Setpoint** (`°C`)
  - **Deviation** (`K`)
  - **Output Level** (`%`)
- Sets the controller setpoint directly from SweepMe!.
- Supports static operation and setpoint sweeps.

---

### Communication

- Interface: **COM (Modbus RTU)**
- **Channel** in the driver corresponds to the Modbus slave address.
