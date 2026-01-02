# LCRmeter Driver Lakeshore M81: VS-10 + CM-10

## Purpose

This SweepMe! driver turns the **Lakeshore M81 VS-10 (source)** and **CM-10 (current measurement / lock-in)** modules into a **lock-in based impedance measurement frontend** (2-wire).

It is intended to be used together with the **SweepMe! LCRmeter module**, which performs the post-processing (|Z|, phase, R, C, L, etc.).

The driver:
- Applies a **sine excitation voltage** using the VS-10
- Configures and runs the **CM-10 in Lock-In (LIA) mode**
- Measures **in-phase (X)** and **quadrature (Y)** current
- Returns the **complex impedance** to SweepMe!

## Return values to the SweepMe! LCRmeter module

- **R** - Real part of impedance (Ohm)
- **X** - Imaginary part of impedance (Ohm)
- **Frequency** - Lock-in reference frequency (Hz)
- **Voltage bias** - Applied DC offset (V)

## Measurement Principle

The driver implements a classical lock-in impedance measurement:

**Z = V / I = V / (X + jY)**

Where:
- **V** is the applied sine voltage (RMS)
- **X** is the in-phase current component
- **Y** is the quadrature current component

All equivalent-circuit modeling (series/parallel R, C, L) is intentionally **not done in this driver**.

