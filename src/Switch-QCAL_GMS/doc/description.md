# Switch QCAL 3-Channel Gas Mixing System

This driver controls a **QCAL 3-Channel Gas Mixing System** by setting gas concentrations (CH2, CH3) and total flow rates via file-based communication with the QCAL GMS software.

---

## Requirements

- **QCAL GMS Application**: Must be installed and running on the same machine.
- **File Location**: Driver communicates via `C:\ProgramData\QCAL\` folder (created automatically by QCAL GMS).
- **Permissions**: User must have read/write access to the QCAL folder.
- **Configuration**: Enable **"Setpoints by file"** in QCAL GMS application settings.

---

## Parameters

- **Concentration CH2**: 0–100 Vol% (volumetric concentration)
- **Concentration CH3**: 0–100 Vol% (volumetric concentration)
- **Total Flow**: ≥ 0 mL/min (normalized at STP)

Sweep mode allows changing any parameter independently while keeping others constant.

---

## Communication

The driver writes setpoints to `extern.txt` and reads confirmations from `zeit.txt`. Commands follow the format: `c_<CH2>d_<CH3>v_<FLOW>e`. QCAL GMS responds with confirmed values prefixed by `"NEW"`. Typical confirmation time is ~1 second.
