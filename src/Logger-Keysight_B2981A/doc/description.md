# Keysight B2981A

This driver enables **ultra-low DC current measurements** with the **Keysight B2981A Femto/Picoammeter**.

---

## Features
- Manual or automatic current ranging
- Set integration time in NPLC (number of power line cycles, i.e. 0.02 seconds for 50 Hz)
- Zero-current correction (see below)

---

## Supported Interfaces

- GPIB
- RS-232 (COM)
- USB
- TCP/IP (VXI-11 / Socket)

---

## GUI Parameters

| Parameter        | Description |
|------------------|------------|
| Range            | Fixed current range or Auto |
| NPLC             | Integration time (longer = lower noise) |
| Zero Correction  | Boolean |

---

## Zero Correction (Input Zero Correction)

This driver uses the B2981A **input zero correction** mechanism (`:INPut:ZCORrect`)
to compensate for internal offsets and leakage currents,
which is especially important for fA and pA measurements.
When zero correction is enabled via the driver, the instrument **immediately
acquires a zero reference** using `INP:ZCOR:ACQ` and applies it to all
subsequent measurements.

This behavior assumes that, during the configuration phase of the SweepMe! Sequencer, the input is in a
**known zero-current condition**, for example:
- open input
- DUT disconnected
- well-defined zero-current state


### Warning  
If a non-zero current is present during zero correction acquisition, that
current will be treated as an offset and **subtracted from all following
measurements**. This can lead to systematically incorrect results, especially
at fA-level currents.  
 
Users must therefore ensure proper input conditions before starting a
measurement when zero correction is enabled.
