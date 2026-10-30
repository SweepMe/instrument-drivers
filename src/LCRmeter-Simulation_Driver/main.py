# MIT License
#
# Copyright (c) 2024-2026 SweepMe! GmbH (sweep-me.net)
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
from typing import Annotated, Literal

import numpy as np
from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Hertz = Annotated[float, Unit("Hz")]
Ohms = Annotated[float, Unit("Ohm")]
HertzList = Annotated[list[float], Unit("Hz")]
OhmsList = Annotated[list[float], Unit("Ohm")]
BiasMode = Literal["Voltage bias", "Current bias"]


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
        self.average = 1
        self.use_list_sweep = False
        self.list_sweep_values: np.ndarray = np.empty((0,))

        # Device under test parameters
        self.inductance = 4e-9  # H
        self.capacitance = 4e-9  # F
        self.resistance = 50  # Ohm
        self.noise_level = 0.05  # percent
        self.bias_coefficient = 0.05

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Return a dictionary with GUI parameters."""
        return {
            "SweepMode": ["Frequency in Hz", "Voltage bias in V"],
            "StepMode": ["None"],
            "Frequency": 1000,
            "OperatingMode": ["R-X"],
            "ValueTypeBias": ["Voltage bias", "Current bias"],
            "ValueBias": 1,
            "Average": "1",

            "Noise level": 0.05,

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
        self.average = int(float(parameter["Average"]))
        self.noise_level = float(parameter["Noise level"])

        # List Mode
        self.use_list_sweep = parameter.get("SweepValue", "None") == "List sweep"
        if self.use_list_sweep:
            self.use_list_sweep = True
            list_sweep_values = np.linspace(
                float(parameter["ListSweepStart"]),
                float(parameter["ListSweepEnd"]),
                int(float(parameter["ListSweepStepPointsValue"])),
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
        if mode.startswith(("Voltage bias", "Current bias")):
            self.bias = value
        elif mode.startswith("Frequency"):
            self.frequency = value
        else:
            msg = f"Mode '{mode}' is not supported. Use 'Frequency...', 'Voltage bias...' or 'Current bias...'."
            raise ValueError(msg)

    def call(self) -> list:
        """Simulate data and return as a list."""
        if self.use_list_sweep:
            measured_frequency = self.list_sweep_values
            measured_resistance = self.simulate_resistance(measured_frequency)
            measured_reactance = self.simulate_reactance(measured_frequency)

        else:
            measured_frequency = self.frequency
            measured_resistance = np.mean([self.simulate_resistance(measured_frequency) for _ in range(self.average)])
            measured_reactance = np.mean([self.simulate_reactance(measured_frequency) for _ in range(self.average)])

        return [measured_resistance, measured_reactance, measured_frequency, self.bias]

    """Simulated LCRmeter"""

    def simulate_resistance(self, frequency: float | np.ndarray) -> float | np.ndarray:
        """Simulate the resistance of the device under test: 50 Ohm plus 1 Ohm per kHz, scaled by the bias."""
        # Calculate the base resistance, rising linearly with the frequency
        base_resistance = self.resistance + frequency / 1000.0
        # Adjust resistance based on the bias (using an arbitrary coefficient of 0.01)
        adjusted_resistance = base_resistance * (1 + self.bias_coefficient * self.bias)
        return self.simulate_noise(adjusted_resistance)

    def simulate_reactance(self, frequency: float | np.ndarray) -> float | np.ndarray:
        """Simulate reactance of the device under test."""
        angular_frequency = 2 * np.pi * frequency

        # Calculate inductive reactance (Inductance) and capacitive reactance
        x_l = angular_frequency * self.inductance
        x_c = -1 / (angular_frequency * self.capacitance)
        base_reactance = x_l + x_c

        # Adjust reactance based on the bias (using an arbitrary coefficient of 0.01)
        adjusted_reactance = base_reactance * (1 + self.bias_coefficient * self.bias)

        return self.simulate_noise(adjusted_reactance)

    def simulate_noise(self, value: float | np.ndarray) -> float | np.ndarray:
        """Add relative noise of up to +/- noise_level to the value; the mean stays at the value."""
        return value * (1 + self.noise_level * (2 * random() - 1))

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The simulated LCR meter measures a series resonant circuit. The commands do not need 'initialize' or 'configure'.
    """

    @command
    def set_frequency(self, frequency: Annotated[Hertz, Range(0.0, None)]) -> None:
        """Set the measurement frequency in Hz. It must be greater than 0 Hz."""
        if frequency <= 0:
            msg = f"Frequency {frequency} Hz must be greater than 0 Hz."
            raise ValueError(msg)
        self.frequency = frequency

    @command(returns=("frequency",), reads="setpoint")
    def get_frequency(self) -> Hertz:
        """Return the measurement frequency in Hz."""
        return float(self.frequency)

    @command(hazards="Applies a DC bias voltage or current to the connected device.")
    def set_bias(self, bias: float) -> None:
        """Set the bias value. Its unit is V for the mode 'Voltage bias' and A for 'Current bias'."""
        self.bias = bias

    @command(returns=("bias",), reads="setpoint")
    def get_bias(self) -> float:
        """Return the bias value."""
        return float(self.bias)

    @command
    def set_bias_mode(self, bias_mode: BiasMode) -> None:
        """Set the bias mode."""
        self.bias_mode = bias_mode

    @command
    def set_average(self, average: Annotated[int, Range(1, None)]) -> None:
        """Set the number of readings that are averaged for one measurement."""
        self.average = average

    @command
    def set_noise_level(self, noise_level: Annotated[float, Range(0.0, None)]) -> None:
        """Set the relative noise of the simulated readings as a fraction, e.g. 0.05 for 5 %. Use 0 for no noise."""
        self.noise_level = noise_level

    @command(returns=("resistance", "reactance"))
    def get_resistance_and_reactance(self) -> tuple[Ohms, Ohms]:
        """Measure at the set frequency and bias and return (resistance R in Ohm, reactance X in Ohm)."""
        resistance = np.mean([self.simulate_resistance(self.frequency) for _ in range(self.average)])
        reactance = np.mean([self.simulate_reactance(self.frequency) for _ in range(self.average)])
        return float(resistance), float(reactance)

    @command(returns=("frequency", "resistance", "reactance"))
    def measure_frequency_sweep(
        self,
        start_frequency: Annotated[Hertz, Range(0.0, None)],
        stop_frequency: Annotated[Hertz, Range(0.0, None)],
        points: Annotated[int, Range(2, 10000)],
    ) -> tuple[HertzList, OhmsList, OhmsList]:
        """Measure R and X at 'points' linearly spaced frequencies from start to stop in Hz.

        Returns the lists of the frequencies in Hz, the resistances R in Ohm and the reactances X in Ohm.
        """
        if start_frequency <= 0 or stop_frequency <= 0:
            msg = "Start and stop frequency must be greater than 0 Hz."
            raise ValueError(msg)
        frequencies = np.linspace(start_frequency, stop_frequency, points)
        return (
            frequencies.tolist(),
            np.asarray(self.simulate_resistance(frequencies), dtype=float).tolist(),
            np.asarray(self.simulate_reactance(frequencies), dtype=float).tolist(),
        )
