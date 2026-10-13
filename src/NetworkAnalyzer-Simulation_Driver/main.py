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

from __future__ import annotations

import time

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class to implement a simulated network analyzer."""

    # Complex S-parameter noise standard deviation at 0 dBm source power.
    REFERENCE_NOISE_STD: float = 0.01

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

        self.power: float = 0.0  # dBm
        self.no_noise: bool = False

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
            "SourcePower": ["0", "10", "20", "-10", "-20", "No Noise"],

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

        # Strip spaces and drop empty tokens so blank, whitespace-only, or trailing-comma input is handled.
        self.terminals = [int(t) for t in parameter["Terminals"].replace(" ", "").split(",") if t]

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

        # SourcePower is a dropdown of dBm levels plus "No Noise"; the power sets the SNR/noise floor.
        source_power = parameter.get("SourcePower", "0")
        self.no_noise = source_power == "No Noise"
        self.power = 0.0 if self.no_noise else float(source_power)

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        # simulate frequencies
        if self.frequency_type == "Frequency step in Hz":
            frequencies = np.arange(self.frequency_start, self.frequency_end, self.f_steps_points)
        elif self.frequency_type == "Logarithmic points":
            frequencies = np.linspace(self.frequency_start, self.frequency_end, int(self.f_steps_points))
        else:
            frequencies = np.arange(1E9, 5E9, 1E8)
        results = [frequencies]

        # S-parameters simulation
        for counter, _var in enumerate(self.variables[1:]):
            simulated_parameter = self.simulate_s_parameter(len(frequencies), phase=counter)
            results.append(simulated_parameter)

        return results

    def simulate_s_parameter(self, array_length: int, phase: float) -> np.ndarray:
        """Simulate an S-parameter trace of length *array_length*.

        S-parameters are dimensionless wave ratios and do not scale with the source power.
        A higher source power instead improves the SNR, so the additive measurement noise
        floor shrinks as the power increases. In "No Noise" mode the clean trace is returned
        for reproducible tests.
        """
        # A passive device: the magnitude stays between 0.05 and 0.95 (-26 dB to -0.4 dB) and the phase rolls off
        # linearly over the sweep, wrapping around +/-180 deg, as for a line with a delay.
        x = np.arange(array_length) / 5
        magnitude = 0.05 + 0.9 * np.sin(x - phase) ** 2
        s_param = magnitude * np.exp(-1j * (x + phase))

        if self.no_noise:
            return s_param

        # Source power sets the noise floor: higher power -> higher SNR -> smaller noise.
        noise_std = self.REFERENCE_NOISE_STD * 10 ** (-self.power / 20)
        rng = np.random.default_rng()
        noise = rng.normal(0.0, noise_std, array_length) + 1j * rng.normal(0.0, noise_std, array_length)
        return s_param + noise


    def find_calibrations(self, *args, **kwargs) -> list:
        """Return the names of the simulated calibrations; called by the NetworkAnalyzer module, arguments are ignored."""
        return ["Calibration1", "Calibration2", "Calibration3"]

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The commands do not need 'initialize' or 'configure'.
    """

    _points: int = 51

    def set_frequency_range(self, start_frequency: float, stop_frequency: float, points: int) -> None:
        """Set the sweep to 'points' linearly spaced frequencies from start to stop in Hz (2 to 10001 points)."""
        start_frequency = float(start_frequency)
        stop_frequency = float(stop_frequency)
        points = int(points)
        if start_frequency <= 0 or stop_frequency <= start_frequency:
            msg = "The start frequency must be greater than 0 Hz and lower than the stop frequency."
            raise ValueError(msg)
        if not 2 <= points <= 10001:
            msg = f"Points {points} must be between 2 and 10001."
            raise ValueError(msg)
        self.frequency_start = start_frequency
        self.frequency_end = stop_frequency
        self._points = points

    def get_frequency_range(self) -> tuple[float, float, int]:
        """Return (start frequency in Hz, stop frequency in Hz, number of points) of the sweep."""
        return float(self.frequency_start), float(self.frequency_end), int(self._points)

    def set_source_power(self, power: float) -> None:
        """Set the source power in dBm (-60 dBm to 30 dBm). A higher power lowers the noise of the traces."""
        power = float(power)
        if not -60 <= power <= 30:
            msg = f"Power {power} dBm must be between -60 dBm and 30 dBm."
            raise ValueError(msg)
        self.power = power

    def get_source_power(self) -> float:
        """Return the source power in dBm."""
        return float(self.power)

    def set_noise_enabled(self, enabled: bool) -> None:
        """Switch the simulated noise on or off. Without noise the traces are reproducible."""
        self.no_noise = not enabled

    def measure_s_parameter(self, s_parameter: str = "S21") -> dict:
        """Measure one S-parameter over the sweep, e.g. 'S11' or 'S21'.

        Returns a dictionary with the lists 'frequency' in Hz, 'magnitude_db' in dB and 'phase_deg' in degrees.
        """
        name = str(s_parameter).strip().upper()
        if len(name) != 3 or name[0] != "S" or not name[1:].isdigit() or "0" in name[1:]:
            msg = f"'{s_parameter}' is not an S-parameter. Use a name like 'S11' or 'S21'."
            raise ValueError(msg)
        frequencies = np.linspace(self.frequency_start, self.frequency_end, self._points)
        trace = self.simulate_s_parameter(len(frequencies), phase=float(int(name[1]) + int(name[2])))
        return {
            "frequency": frequencies.tolist(),
            "magnitude_db": (20 * np.log10(np.abs(trace) + 1e-12)).tolist(),
            "phase_deg": np.angle(trace, deg=True).tolist(),
        }
