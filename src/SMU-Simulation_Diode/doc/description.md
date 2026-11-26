Simulation Diode
===============

This driver provides a short simulation of a diode exhibiting space-charge-limited current (SCLC)-like behavior, as often seen in organic diode devices. The implementation combines a small exponential diode term, a linear leakage term and random noise. The measurement loop also includes a current-dependent effective voltage change (delta_v ~ sqrt(|I|)) to emulate SCLC-related voltage dynamics during the measurement.

Important differences to the standard `SMU-Simulation_Driver`, which also simulates a diode but with a more detailed classical diode model:

- `SMU-Simulation_Diode` focuses on SCLC-like behavior and simple dynamics useful for testing measurement sequences for organic diodes.
- `SMU-Simulation_Driver` implements a more configurable classical diode model (saturation current, ideality factor, thermal voltage, shunt resistance, photocurrent, noise and hysteresis).

Use this driver when you want a SCLC-style diode simulation rather than the detailed classical diode model in the other simulation driver.
## Parameters

- **SweepMode** — `Voltage in V`: the sweep value is the forced voltage.
- **Compliance** — current compliance in A, greater than 0 A and at most 1 A.
- **Average** — number of current readings averaged per point, 1 to 100.
- **Speed** — `Fast`, `Medium` and `Slow` set the noise of the measured voltage; `No Noise` switches all noise off
  for reproducible tests.

## Returns

- **Voltage** (V) and **Current** (A).

## Communication commands

Usable from Instrument Control and pysweepme scripts without a sequence: `set_compliance` / `get_compliance`,
`set_speed` / `get_speed`, `set_average` / `get_average`, `set_voltage` / `get_voltage_setpoint`, `set_output` /
`get_output` and `get_voltage_and_current`. As on a real SMU, the output is off after connecting; while it is off,
the diode sees 0 V.

## Scripting with pysweepme

`set_parameters()` applies **SweepMode** and **Speed** at once. **Compliance** and **Average** are converted and
checked only by `configure()`, as in a SweepMe! run, and keep their previous values (the defaults 1 mA and 1)
until it runs. Call it before measuring:

```python
import pysweepme

driver = pysweepme.get_driver("SMU-Simulation_Diode", r"<instrument-drivers>\src", "")
driver.set_parameters({"Compliance": 0.01, "Average": 4, "Speed": "No Noise"})
driver.connect()
try:
    driver.initialize()
    driver.configure()  # applies Compliance and Average
    driver.write(0.6)  # forced voltage in V
    print(driver.read())
finally:
    driver.disconnect()
```

The communication commands (`set_compliance`, `set_average`, `set_speed`, ...) take effect at once, without
`configure()`.
