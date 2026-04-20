# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# SweepMe! driver
# * Module: SMU
# * Instrument: Simulation Driver

from __future__ import annotations

import random

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice
import math


def proof_average(average) -> int:
    try:
        avg = int(average)
    except ValueError as e:
        raise ValueError(f"Average must be an integer: {e}")
    if avg < 1:
        raise ValueError("Average must be at least 1.")
    if avg > 100:
        raise ValueError("Average must be at most 100.")
    return avg


def proof_shunt(shunt) -> float:
    try:
        shunt = float(shunt)
    except ValueError as e:
        raise ValueError(f"Shunt resistance must be a float: {e}")
    if not shunt > 0:
        raise ValueError("Shunt resistance must be greater than 0.")
    return shunt


class Device(EmptyDevice):
    """Driver for a simulated SMU that measures a diode. Can be used to test the SMU module."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname: str = "Simulation Driver"

        self.variables: list[str] = ["Voltage", "Current"]
        self.units: list[str] = ["V", "A"]
        self.plottype: list[bool] = [True, True]  # True to plot data
        self.savetype: list[bool] = [True, True]  # True to save data

        self.idlevalue: float = 0.0

        self.speedvalues: dict[str, float] = {
            "Fast": 1.0,
            "Medium": 3.0,
            "Slow": 10.0,
        }
        self.k: float = 1.38e-23  # Boltzmann constant, J/K
        self.q: float = 1.6e-19  # Elementary charge, C
        # Initialize GUI/configuration related variables with sensible defaults.
        # These will be overwritten by `get_GUIparameter` before a measurement,
        # but having defaults avoids AttributeError and documents expected types.
        self.source: str = "Voltage in V"
        self.protection: float = 1e-3
        self.speed: str = "Fast"
        self.average: int = 1
        self.saturation_current: float = 1e-15
        self.ideality_factor: float = 1.4
        self.temperature: float = 300.0
        self.photocurrent: float = 0.0
        self.noise: float = 1.0
        self.shunt_resistance: float = float("inf")
        self.leakage: float = 1.0
        self.hysteresis: float = 0.0  # time constant (a.u.). 0 = no hysteresis
        self.v_t: float = 0.025

        # Measurement state / last setpoint
        self.value: float = (
            0.0  # applied source value (voltage or current depending on mode)
        )
        self.v: float = 0.0  # last measured voltage
        self.i: float = 0.0  # last measured current

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V"],
            "Compliance": 1e-3,
            "Average": 1,
            "Speed": ["Fast", "Medium", "Slow"],
            "Saturation Current in A": 1e-15,
            "Ideality Factor": 1.4,
            "Temperature in K": 300,
            "Parallel Shunt in Ohm": [float("inf"), 100, 1000, 1e4, 1e5],
            "Photocurrent in A": 0.0,
            "Random Noise in a.u.": 1.0,
            "Linear Leakage in a.u.": 1.0,
            "Hysteresis time constant in a.u.": 0.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.source = parameter.get("SweepMode")
        self.protection = parameter.get("Compliance")
        self.speed = parameter.get("Speed")
        self.average = parameter.get("Average")
        self.saturation_current = parameter.get("Saturation Current in A")
        self.ideality_factor = parameter.get("Ideality Factor")
        self.temperature = parameter.get("Temperature in K")
        self.photocurrent = parameter.get("Photocurrent in A")
        self.noise = parameter.get("Random Noise in a.u.")
        self.shunt_resistance = parameter.get("Parallel Shunt in Ohm")
        self.leakage = parameter.get("Linear Leakage in a.u.")
        self.hysteresis = parameter.get("Hysteresis time constant in a.u.")

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        max_compliance = 1.0
        if float(self.protection) > max_compliance:
            self.stop_Measurement(
                f"Compliance {self.protection} is higher than the maximum compliance of {max_compliance}."
            )
        self.average = proof_average(self.average)
        self.protection = float(self.protection)
        self.saturation_current = float(self.saturation_current)
        self.ideality_factor = float(self.ideality_factor)
        self.temperature = float(self.temperature)
        self.v_t = self.k * self.temperature / self.q
        self.photocurrent = float(self.photocurrent)
        self.noise = float(self.noise)
        self.shunt_resistance = proof_shunt(self.shunt_resistance)
        self.leakage = float(self.leakage)
        self.hysteresis = float(self.hysteresis)

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        if self.source.startswith("Voltage"):
            measured_currents = []
            for _ in range(self.average):
                measured_current = self.simulate_current(self.value)
                measured_currents.append(measured_current)
                self.i = measured_current
            self.v = self.simulate_voltage(self.value)
            # store mean as float
            self.i = float(np.mean(measured_currents))

        elif self.source.startswith("Current"):
            self.stop_Measurement(
                "Current sourcing is not implemented in this simulation driver."
            )

        return [float(self.v), float(self.i)]

    """Simulated Diode"""

    def simulate_current(self, applied_voltage: float) -> float:
        """Simulate the current of a diode with linear leakage and some resolution noise."""
        # equilibrium current (no hysteresis)
        equilibrium = (
            (
                self.saturation_current
                * (np.exp(applied_voltage / self.ideality_factor / self.v_t) - 1)
                + applied_voltage / 1e10 * (10**self.leakage - 1)
                + (random.random() - 0.5) / 1e11 * (10**self.noise - 1)
            )
            - self.photocurrent
        ) + applied_voltage / self.shunt_resistance

        # Apply first-order lag (exponential relaxation) to model hysteresis/lag.
        # Measured current relaxes from previous measured value (self.i) to the
        # new equilibrium with time constant tau = self.hysteresis. The effective
        # time step is approximated by the speed values: slower measurement ->
        # larger dt -> more relaxation (less hysteresis).
        if self.hysteresis > 0:
            # previous measured current (memory). Use self.i which stores the
            # last reported mean current from previous call; default 0.0.
            prev = float(self.i)
            tau = float(self.hysteresis)
            dt = float(self.speedvalues.get(self.speed, 1.0))
            # alpha = exp(-dt/tau) -> fraction of previous value remaining
            try:
                alpha = math.exp(-dt / tau)
            except OverflowError:
                alpha = 0.0
            current = equilibrium + (prev - equilibrium) * alpha
        else:
            current = equilibrium

        if applied_voltage == 0:
            current = 0 - self.photocurrent

        # Compliance clipping
        if current > self.protection:
            current = self.protection
        elif current < -self.protection:
            current = -self.protection

        return float(current)

    def simulate_voltage(self, applied_voltage: float) -> float:
        """Simulate the measured voltage including some noise depending on the measurement speed."""
        return (
            applied_voltage
            + (random.random() - 0.5) * 1e-2 / self.speedvalues[self.speed]
        )
