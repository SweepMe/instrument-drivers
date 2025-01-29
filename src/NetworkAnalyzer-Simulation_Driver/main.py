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
# * Module: NetworkAnalyzer
# * Instrument: Simulated Network Analyzer


import time

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class to implement a simulated network analyzer."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        # Sequencer Parameters
        self.shortname = "Simulation"

        self.variables = ["Frequency"]
        self.units = ["Hz"]
        self.plottype = [True]
        self.savetype = [True]

        # Measurement Parameters
        self.frequency_start: float = 1e9
        self.frequency_end: float = 5e9
        self.frequency_type: str = "Frequency step in Hz"
        self.f_steps_points: float = 0.1e9

        self.terminals: list[int] = []
        self.s_parameter: str = ""

    def find_ports(self) -> list[str]:
        """This function is called whenever the user presses 'Find ports' button.

        Return a list of strings with possible port items.
        """
        return ["Port1", "Port2"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Terminals": "1,2",
            "Sparameters": "",

            # All frequencies in Hz
            "FrequencyStart": 1e9,
            "FrequencyEnd": 5e9,
            "FrequencyStepPointsType": ["Frequency step in Hz", "Logarithmic points"],
            "FrequencyStepPoints": 0.1e9,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.frequency_start = float(parameter["FrequencyStart"])
        self.frequency_end = float(parameter["FrequencyEnd"])
        self.frequency_type = parameter["FrequencyStepPointsType"]
        self.f_steps_points = float(parameter["FrequencyStepPoints"])

        self.terminals = list(map(int, parameter["Terminals"].strip(" ").replace(",,", ",").split(",")))

        # Reset return parameters
        self.variables = ["Frequency"]
        self.units = ["Hz"]
        self.plottype = [True]
        self.savetype = [True]

        self.s_parameter = parameter["Sparameters"]

        if self.s_parameter != "":
            self.variables += self.s_parameter.replace(" ", "").split(",")
        else:
            # create variable and units depending on the number of terminals
            for i in self.terminals:
                for j in self.terminals:
                    self.variables.append(f"S{i}{j}")

        self.units += [""] * (len(self.variables) - 1)
        self.plottype += [False] * (len(self.variables) - 1)
        self.savetype += [True] * (len(self.variables) - 1)

    def call(self) -> [float, float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        # simulate frequencies
        if self.frequency_type == "Frequency step in Hz":
            frequencies = np.arange(self.frequency_start, self.frequency_end, self.f_steps_points)
        elif self.frequency_type == "Logarithmic points":
            frequencies = np.linspace(self.frequency_start, self.frequency_end, int(self.f_steps_points))
        else:
            frequencies = np.arange(1E9, 5E9, 1E8)
        results = [frequencies]

        # S-parameter
        simulated_parameter = self.simulate_s_parameter(len(frequencies))
        for _var in self.variables[1:]:
            results.append(simulated_parameter)

        return results

    def simulate_s_parameter(self, array_length: int) -> np.array:
        """Simulate s parameter result of length array_length."""
        phase = time.perf_counter() * self.frequency_end
        return np.array((np.sin(np.arange(array_length) / 5 - phase)) ** 2 + (
            np.cos(np.arange(array_length) / 5)) ** 2 * 1j, dtype=complex)
