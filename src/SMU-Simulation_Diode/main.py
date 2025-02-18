# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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


import random

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


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

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V"],
            "Compliance": 1e-3,
            "Average": 1,
            "Speed": ["Fast", "Medium", "Slow"],
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
            applied_voltage = self.value
            measured_currents = []

            for _ in range(self.average):
                self.deltaV = -1

                i = 0
                v_exp = self.value

                # Measure the current until the current is stable or 1500 iterations are reached
                while abs(abs(self.value - v_exp) - self.deltaV) > 1e-3 and i < 1500:
                    i += 1

                    measured_current = self.simulate_current(applied_voltage)
                    self.deltaV = 1e2 * (abs(measured_current)) ** 0.5  # some SCLC

                    # Measured voltage cannot be higher than the applied voltage
                    if abs(v_exp) + self.deltaV > self.value:
                        v_exp -= 0.001 * np.sign(self.value)

                self.v = self.simulate_voltage(self.value)
                measured_currents.append(measured_current)

            self.i = np.mean(measured_currents)

        elif self.source.startswith("Current"):
            pass

        return [float(self.v), float(self.i)]

    """Simulated Diode"""

    def simulate_current(self, applied_voltage: float) -> float:
        """Simulate the current of a diode with linear leakage and some resolution noise."""
        if applied_voltage == 0:
            return 0

        current = 1e-15 * (np.exp(applied_voltage / 1.4 / 0.025) - 1) + applied_voltage / 1e9 + random.random() / 1e10

        if current > self.protection:
            current = self.protection
        elif current < -self.protection:
            current = -self.protection

        return current

    def simulate_voltage(self, applied_voltage: float) -> float:
        """Simulate the measured voltage including some noise depending on the measurement speed."""
        return applied_voltage + random.random() * 1e-2 / self.speedvalues[self.speed]

