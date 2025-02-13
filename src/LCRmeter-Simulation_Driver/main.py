# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# * Module: LCRmeter
# * Instrument: Simulated LCRmeter
from __future__ import annotations

from random import random

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Simulated LCRmeter driver."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Simulation"
        self.port_manager = False

        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        # Measurement parameters
        self.sweepmode = "Frequency in Hz"
        self.stepmode = "None"
        self.frequency = 1000
        self.bias_mode = "Voltage bias"
        self.bias = 1
        self.use_list_sweep = False
        self.list_sweep_values: np.array = np.empty((0,))

        # Device under test parameters
        self.inductance = 4e-9  # H
        self.capacitance = 4e-9  # F
        self.resistance = 50  # Ohm
        self.noise_level = 0.05  # percent

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Return a dictionary with GUI parameters."""
        return {
            "SweepMode": ["Frequency in Hz"],
            "SweepValue": ["List"],
            "StepMode": ["None"],
            "Frequency": 1000,
            "OperatingMode": ["R-X"],
            "ValueTypeBias": ["Voltage bias", "Current bias"],
            "ValueBias": 1,

            # List Sweep Parameters
            "ListSweepCheck": True,
            "ListSweepType": ["Sweep"],  # , "Custom"],
            "ListSweepStart": 20,
            "ListSweepEnd": 120,
            "ListSweepStepPointsType": ["Points (lin.):"],
            "ListSweepStepPointsValue": 10,
            "ListSweepCustomValues": "",
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Set the GUI parameters."""
        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.frequency = float(parameter["Frequency"])

        self.bias_mode = parameter["ValueTypeBias"]
        self.bias = float(parameter["ValueBias"])

        # List Mode
        self.use_list_sweep = parameter["SweepValue"] == "List sweep"
        if self.use_list_sweep:
            self.use_list_sweep = True
            list_sweep_values = np.arange(
                float(parameter["ListSweepStart"]),
                float(parameter["ListSweepEnd"]),
                float(parameter["ListSweepStepPointsValue"]),
            )
            # include end value
            self.list_sweep_values = np.append(list_sweep_values, float(parameter["ListSweepEnd"]))

    def apply(self) -> None:
        """Set the device to the sweep and/or step value."""
        if self.sweepmode != "None":
            sweep_value = float(self.value)
            self.handle_set_value(self.sweepmode, sweep_value)

        if self.stepmode != "None":
            step_value = float(self.stepvalue)
            self.handle_set_value(self.stepmode, step_value)

    def handle_set_value(self, mode: str, value: float) -> None:
        """Set value for sweep or step mode."""
        if mode.startswith("Voltage bias"):
            self.bias = value

        if mode.startswith("Current bias"):
            self.bias = value

        elif mode.startswith("Frequency"):
            self.frequency = value

    def call(self) -> list:
        """Simulate data and return as a list."""
        measured_frequency = self.list_sweep_values if self.use_list_sweep else self.frequency
        measured_resistance = self.simulate_resistance(measured_frequency)
        measured_reactance = self.simulate_reactance(measured_frequency)

        return [measured_resistance, measured_reactance, measured_frequency, self.bias]

    """Simulated LCRmeter"""

    def simulate_resistance(self, frequency: float | np.array) -> float:
        """Simulate resistance with weak frequency dependency of the device under test."""
        resistance = self.resistance + frequency / 1000
        return self.simulate_noise(resistance)

    def simulate_reactance(self, frequency: float | np.array) -> float:
        """Simulate reactance of the device under test."""
        angular_frequency = 2 * np.pi * frequency

        # inductive reactance (Inductance)
        x_l = angular_frequency * self.inductance

        # capacitive reactance
        x_c = -1 / (angular_frequency * self.capacitance)

        return self.simulate_noise(x_l + x_c)

    def simulate_noise(self, value: float | np.array) -> float:
        """Simulate noise."""
        return value + value * self.noise_level * random()
