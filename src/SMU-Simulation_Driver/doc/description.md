Simulation Driver
=================

This driver is a simulated Source-Measure Unit (SMU) measurement of an inorganic diode, photodiode or solar cell.
The simulation models a diode-like device
including saturation current, ideality factor, temperature-dependent thermal
voltage, linear leakage, photocurrent, resolution noise, a parallel shunt and
hysteresis (first-order lag).

Formulas
--------

Thermal voltage:

	V_t = k * T / q

Equilibrium current (Shockley diode equation + leakage + noise + shunt):

	I_eq(V) = I_s * (exp(V / (n * V_t)) - 1)
			  + V / R_leak_linear
			  + noise_term
			  - I_photo
			  + V / R_shunt

Where:
- I_s: saturation_current (A)
- n: ideality_factor (unitless)
- V_t: thermal voltage (V)
- R_leak_linear: internal representation of linear leakage; in the code
  implemented as V / 1e10 * (10**leakage - 1)
- noise_term: resolution noise implemented as (rand() - 1)/1e11 * (10**noise - 1)
- I_photo: photocurrent (A)
- R_shunt: parallel shunt resistance (Ohm)

Hysteresis / first-order lag (exponential relaxation):

	I_meas = I_eq + (I_prev - I_eq) * exp(-dt / tau)

Where:
- I_prev: previous measured current (A)
- tau: hysteresis time constant (a.u.)
- dt: effective time step derived from measurement speed (a.u.)

Compliance clipping is applied to the final current:

	I_meas_clipped = max(min(I_meas, protection), -protection)

Measured voltage (includes speed-dependent noise):

	V_meas = V_applied + rand() * 1e-2 / speed_factor

Inputs / configurable parameters
-------------------------------

The driver exposes the following GUI parameters:

- "Compliance": float (A)
  - Maximum allowed current (positive scalar). Values above 1.0 A are rejected
	by the driver initialize routine.
- "Average": int
  - Number of repeated measurements averaged (1..100)
- "Speed": str
  - One of ["Fast", "Medium", "Slow"]. Maps to an internal speed factor
	that scales the effective dt used for hysteresis and the voltage noise.
- "Saturation Current in A": float (I_s)
- "Ideality Factor": float (n)
- "Temperature in K": float (T)
- "Parallel Shunt in Ohm": float (R_shunt)
- "Photocurrent in A": float (I_photo)
- "Random Noise in a.u.": float (noise)
- "Linear Leakage in a.u.": float (leakage)
- "Hysteresis time constant in a.u.": float (tau)

Notes
-----
- The simulation currently implements voltage sourcing only.
- Units for some internal/auxiliary parameters (leakage, noise, hysteresis
  time constant) are arbitrary units (a.u.) chosen to achieve realistic
  behaviour in the model; see the source code for the exact numeric
  implementation.
- The driver uses the physical constants k (Boltzmann constant) and q
  (elementary charge) to compute the thermal voltage V_t.
- Ideality factor n typically ranges from 1 (ideal diode) to 2 (recombination-dominated); values outside this range are allowed but may produce non-physical results.
- The driver does not currently model temperature dependence of parameters other than the thermal voltage. As visible from the formula, the thermal voltage influences the current in the same way as the ideality factor, so increasing temperature will have a similar effect to decreasing the ideality factor.

