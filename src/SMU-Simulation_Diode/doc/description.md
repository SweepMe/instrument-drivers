Simulation Diode
===============

This driver provides a short simulation of a diode exhibiting space-charge-limited current (SCLC)-like behavior, as often seen in organic diode devices. The implementation combines a small exponential diode term, a linear leakage term and random noise. The measurement loop also includes a current-dependent effective voltage change (delta_v ∝ sqrt(|I|)) to emulate SCLC-related voltage dynamics during the measurement.

Important differences to the standard `SMU-Simulation_Driver`, which also simulates a diode but with a more detailed classical diode model:

- `SMU-Simulation_Diode` focuses on SCLC-like behavior and simple dynamics useful for testing measurement sequences for organic diodes.
- `SMU-Simulation_Driver` implements a more configurable classical diode model (saturation current, ideality factor, thermal voltage, shunt resistance, photocurrent, noise and hysteresis).

Use this driver when you want a SCLC-style diode simulation rather than the detailed classical diode model in the other simulation driver.