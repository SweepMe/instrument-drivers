# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025-2026 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Simulation Diode

from __future__ import annotations

import random
from typing import Annotated, Literal

import numpy as np
from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

MAX_VOLTAGE = 20.0
"""Largest voltage magnitude in V the simulated SMU can force."""

Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]
Speed = Literal["Fast", "Medium", "Slow", "No Noise"]


class Device(EmptyDevice):
    """Driver for a simulated SMU that measures a diode. Can be used to test the SMU module."""
    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Test Diode"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.idlevalue = 0.0

        self.speedvalues = {
            "Fast": 1.0,
            "Medium": 3.0,
            "Slow": 10.0,
        }

        # Defaults, so that the communication commands work before the GUI parameters have been received.
        self.source: str = "Voltage in V"
        self.protection: float = 1e-3
        self.speed: str = "Fast"
        self.average: int = 1
        self.value: float = 0.0
        self.v: float = 0.0
        self.i: float = 0.0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V"],
            "Compliance": 1e-3,
            "Average": 1,
            "Speed": ["Fast", "Medium", "Slow", "No Noise"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.source = parameter["SweepMode"]
        self.protection = float(parameter["Compliance"])
        self.speed = parameter["Speed"]
        self.average = int(parameter["Average"])

        if self.average < 1:
            self.average = 1
        if self.average > 100:
            self.average = 100

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        max_compliance = 1.0
        if float(self.protection) > max_compliance:
            self.stop_Measurement(f"Compliance {self.protection} is higher than the maximum compliance of {max_compliance}.")

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        if self.source.startswith("Voltage"):
            measured_currents = [self.simulate_series_current(self.value) for _ in range(self.average)]

            self.v = self.simulate_voltage(self.value)
            self.i = np.mean(measured_currents)

        elif self.source.startswith("Current"):
            pass

        return [float(self.v), float(self.i)]

    """Simulated Diode"""

    def simulate_series_current(self, applied_voltage: float) -> float:
        """Simulate the current of the diode in series with a space-charge-limited layer, as measured by the SMU.

        The applied voltage divides into the junction voltage and a drop of 100 V * sqrt(I / 1 A) across the layer.
        The junction voltage is found by bisection, so the result holds at any voltage up to the compliance.
        """
        applied_voltage = float(applied_voltage)
        if applied_voltage == 0:
            return 0.0

        low, high = sorted((0.0, applied_voltage))
        current = 0.0
        for _ in range(60):
            junction_voltage = (low + high) / 2
            current = self.simulate_current(junction_voltage)
            residual = junction_voltage + np.sign(applied_voltage) * 1e2 * abs(current) ** 0.5 - applied_voltage
            if residual > 0:
                high = junction_voltage
            else:
                low = junction_voltage
        return float(current)

    def simulate_current(self, applied_voltage: float) -> float:
        """Simulate the current of the bare diode junction (without the series layer), with linear leakage and noise."""
        if applied_voltage == 0:
            return 0

        noise = 0 if self.speed == "No Noise" else (random.random() - 0.5) / 1e10
        current = 1e-15 * (np.exp(applied_voltage / 1.4 / 0.025) - 1) + applied_voltage / 1e9 + noise

        if current > self.protection:
            current = self.protection
        elif current < -self.protection:
            current = -self.protection

        return current

    def simulate_voltage(self, applied_voltage: float) -> float:
        """Simulate the measured voltage including some noise depending on the measurement speed."""
        if self.speed not in self.speedvalues:
            return applied_voltage
        return applied_voltage + (random.random() - 0.5) * 1e-2 / self.speedvalues[self.speed]

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The simulated SMU forces a voltage on a simulated diode and measures voltage and current. The commands do not need
    'initialize' or 'configure' and therefore also work when the instrument was only connected. As on a real SMU, the
    output is off after connecting: switch it on with 'set_output' to measure the diode, otherwise 0 V is forced.
    """

    _voltage_setpoint: float = 0.0
    _output: bool = False

    @command(warnings="A higher compliance lets more current flow through the connected device.")
    def set_compliance(self, compliance: Annotated[Amperes, Range(0.0, 1.0)]) -> None:
        """Set the current compliance in A. It must be greater than 0 A and at most 1 A."""
        if compliance <= 0:
            msg = f"Compliance {compliance} A must be greater than 0 A."
            raise ValueError(msg)
        self.protection = compliance

    @command(returns=("compliance",), reads="setpoint")
    def get_compliance(self) -> Amperes:
        """Return the current compliance in A."""
        return float(self.protection)

    @command
    def set_speed(self, speed: Speed) -> None:
        """Set the measurement speed, which defines the voltage noise; "No Noise" switches the noise off."""
        self.speed = speed

    @command(returns=("speed",), reads="setpoint")
    def get_speed(self) -> Speed:
        """Return the measurement speed."""
        return self.speed  # type: ignore[return-value]  # set from the GUI or set_speed, both one of Speed

    @command
    def set_average(self, average: Annotated[int, Range(1, 100)]) -> None:
        """Set the number of current readings that are averaged for one measurement."""
        self.average = average

    @command(warnings="Changes the voltage at the connected device at once while the output is on.")
    def set_voltage(self, voltage: Annotated[Volts, Range(-MAX_VOLTAGE, MAX_VOLTAGE)]) -> None:
        """Force a voltage in V. The voltage reaches the diode only while the output is enabled."""
        self.source = "Voltage in V"
        self._voltage_setpoint = voltage

    @command(returns=("voltage",), reads="setpoint")
    def get_voltage_setpoint(self) -> Volts:
        """Return the voltage in V that was set with 'set_voltage'."""
        return float(self._voltage_setpoint)

    @command(warnings="Switching the output on applies the set voltage to the connected device.")
    def set_output(self, output: bool) -> None:
        """Switch the output on (True) or off (False). While it is off, the simulated diode sees 0 V."""
        self._output = output

    @command(returns=("output",), reads="setpoint")
    def get_output(self) -> bool:
        """Return True if the output is on."""
        return bool(self._output)

    @command(returns=("voltage", "current"))
    def get_voltage_and_current(self) -> tuple[Volts, Amperes]:
        """Measure (voltage in V, current in A) of the diode behind a space-charge-limited layer, up to the compliance."""
        self.source = "Voltage in V"
        self.value = self._voltage_setpoint if self._output else 0.0
        voltage, current = self.call()
        return float(voltage), float(current)
