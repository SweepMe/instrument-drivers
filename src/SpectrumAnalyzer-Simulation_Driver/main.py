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
# * Module: SpectrumAnalyzer
# * Instrument: Simulated Driver

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
        <h3>Simulated Spectrum Analyzer</h3>
        <p>---Modify this description text later to guide your users---</p>
    """

    def __init__(self) -> None:
        """Set up parameters for the simulated spectrum analyzer."""
        super().__init__()

        self.shortname = "Simulation"
        self.variables = ["Frequency", "Power"]
        self.units = ["Hz", "dBm"]
        self.plottype = [True, True]  # define if it can be plotted
        self.savetype = [True, True]  # define if it can be saved

        self.bandwidth_resolution_values: dict[str, float] = {
            "Auto": 0,
            "1 Hz": 1,
            "3 Hz": 3,
        }

        # Measurement parameters
        self.frequency_center: float = 5000
        self.frequency_span: float = 5000
        self.frequency_min: float = 5000
        self.frequency_max: float = 5000

        self.reference_level: float = -75
        self.resolution_bandwidth: float = 0.
        self.video_bandwidth: float = 0.
        self.return_max_hold: bool = False
        self.video_averaging: bool = False

        # Measured values
        self.measured_frequency: np.ndarray = np.array([])

    @staticmethod
    def find_ports() -> list[str]:
        """Find available ports."""
        return ["Simulated Port"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the GUI parameters."""
        return {
            "Frequency label 1": ["Center frequency in Hz:", "Min frequency in Hz:"],
            "Frequency value 1": 5000,
            "Frequency label 2": ["Frequency span in Hz:", "Max frequency in Hz:"],
            "Frequency value 2": 1000,
            "Reference level in dBm": -75,
            "Resolution bandwidth": list(self.bandwidth_resolution_values),
            "Video bandwidth": list(self.bandwidth_resolution_values),
            "Max hold": False,
            "Video averaging": False,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle GUI inputs."""
        self.handle_frequency_input(parameter)

        self.reference_level = float(parameter["Reference level in dBm"])
        self.resolution_bandwidth = self.bandwidth_resolution_values[parameter["Resolution bandwidth"]]
        self.video_bandwidth = self.bandwidth_resolution_values[parameter["Video bandwidth"]]
        self.return_max_hold = parameter["Max hold"]
        self.video_averaging = parameter["Video averaging"]

    def handle_frequency_input(self, parameter: dict) -> None:
        """Calculate the frequency center, span, min, and max from the input values."""
        input_1_type = parameter["Frequency label 1"]
        input_1_value = float(parameter["Frequency value 1"])
        input_2_type = parameter["Frequency label 2"]
        input_2_value = float(parameter["Frequency value 2"])

        if input_1_type == "Center frequency in Hz:":
            self.frequency_center = input_1_value
            if input_2_type == "Frequency span in Hz:":
                self.frequency_span = input_2_value
                self.frequency_min = self.frequency_center - self.frequency_span / 2
                self.frequency_max = self.frequency_center + self.frequency_span / 2
            elif input_2_type == "Max frequency in Hz:":
                self.frequency_max = input_2_value
                self.frequency_span = (self.frequency_max - self.frequency_center) * 2
                self.frequency_min = self.frequency_center - self.frequency_span / 2

        elif input_1_type == "Min frequency in Hz:":
            self.frequency_min = input_1_value
            if input_2_type == "Frequency span in Hz:":
                self.frequency_span = input_2_value
                self.frequency_max = self.frequency_min + self.frequency_span
                self.frequency_center = (self.frequency_min + self.frequency_max) / 2
            elif input_2_type == "Max frequency in Hz:":
                self.frequency_max = input_2_value
                self.frequency_center = (self.frequency_min + self.frequency_max) / 2
                self.frequency_span = self.frequency_max - self.frequency_min

    def measure(self) -> None:
        """Create a measurement."""
        number_of_points = 100
        self.measured_frequency = np.linspace(self.frequency_min, self.frequency_max, number_of_points)

    def call(self) -> tuple[list, list]:
        """Return the measured frequency and amplitude."""
        # TODO: Log scale
        number_of_peaks = 3
        position_of_peaks = [0.1, 0.3, 0.55]
        amplitude_of_peaks = [1, 2, 3]

        amplitude = np.zeros(len(self.measured_frequency))
        for i in range(number_of_peaks):
            peak_position = position_of_peaks[i] * self.frequency_span + self.frequency_center - self.frequency_span / 2
            peak_width = self.frequency_span * 0.15
            peak_amplitude = amplitude_of_peaks[i] * 25
            amplitude += peak_amplitude * np.exp(-(self.measured_frequency - peak_position) ** 2 / peak_width)

        rng = np.random.default_rng()
        noise_level = 0
        noise = rng.normal(noise_level, 3, len(self.measured_frequency))
        amplitude += noise

        return self.measured_frequency.tolist(), amplitude.tolist()
