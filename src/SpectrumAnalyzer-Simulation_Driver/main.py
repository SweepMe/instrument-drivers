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
# * Module: SpectrumAnalyzer
# * Instrument: Simulated Driver

from __future__ import annotations

from typing import Annotated, Literal

import numpy as np
from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Hertz = Annotated[float, Unit("Hz")]
DecibelMilliwatts = Annotated[float, Unit("dBm")]
HertzList = Annotated[list[float], Unit("Hz")]
DecibelMilliwattsList = Annotated[list[float], Unit("dBm")]
TraceMode = Literal["Current", "Max hold", "Min hold", "Average"]


class Device(EmptyDevice):
    description = """
        <h3>Simulated Spectrum Analyzer</h3>
        <p>The <b>Port</b> field is reused to select the simulation mode:</p>
        <ul>
        <li><b>Port 1: Simulated Spectrum</b>: three Gaussian peaks with additive random noise.</li>
        <li><b>Port 2: No Noise</b>: the same spectrum without noise for reproducible tests.</li>
        </ul>
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
        self.port_string: str = "Simulated Spectrum"
        self.frequency_center: float = 5000
        self.frequency_span: float = 5000
        self.frequency_min: float = 5000
        self.frequency_max: float = 5000

        self.reference_level: float = -75
        self.resolution_bandwidth: float = 0.0
        self.video_bandwidth: float = 0.0
        self.return_max_hold: bool = False
        self.video_averaging: bool = False

        # Trace Modes
        self.trace_modes = [
            "Current",
            "Max hold",
            "Min hold",
            "Average",
        ]
        self.trace_mode: str = "Average"
        self.trace_integration: float = 1

        # Measured values
        self.measured_frequency: np.ndarray = np.array([])

    @staticmethod
    def find_ports() -> list[str]:
        """Find available ports."""
        return ["Port 1: Simulated Spectrum", "Port 2: No Noise"]

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
            "Trace mode": self.trace_modes,
            "Trace mode integration type": ["Hold time in s:", "Repetitions:"],
            "Trace mode integration": 1,
            "Video averaging": False,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle GUI inputs."""
        self.port_string = parameter.get("Port", self.port_string)
        self._handle_frequency_input(parameter)

        self.reference_level = float(parameter["Reference level in dBm"])
        self.resolution_bandwidth = self.bandwidth_resolution_values[parameter["Resolution bandwidth"]]
        self.video_bandwidth = self.bandwidth_resolution_values[parameter["Video bandwidth"]]
        self.trace_mode = parameter["Trace mode"]
        self.trace_integration = float(parameter["Trace mode integration"])
        self.video_averaging = parameter["Video averaging"]

    def _handle_frequency_input(self, parameter: dict) -> None:
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
        """Return the measured frequency in Hz and power in dBm, combined over the repetitions of the trace mode."""
        repetitions = 1 if self.trace_mode == "Current" else max(1, int(self.trace_integration))
        spectra = np.array([self.simulate_spectrum(self.measured_frequency) for _ in range(repetitions)])

        if self.trace_mode == "Min hold":
            spectrum = spectra.min(axis=0)
        elif self.trace_mode == "Max hold":
            spectrum = spectra.max(axis=0)
        elif self.trace_mode == "Average":
            spectrum = spectra.mean(axis=0)
        else:
            spectrum = spectra[0]

        return self.measured_frequency.tolist(), spectrum.tolist()

    def simulate_spectrum(self, frequency: np.ndarray) -> np.ndarray:
        """Simulate a spectrum in dBm: -60, -45 and -30 dBm peaks at 10, 30 and 55 % of the span, -90 dBm floor."""
        frequency = np.asarray(frequency, dtype=float)
        position_of_peaks = [0.1, 0.3, 0.55]
        power_of_peaks_dbm = [-60.0, -45.0, -30.0]
        noise_floor_dbm = -90.0
        peak_width = self.frequency_span * 0.02  # standard deviation of each peak in Hz

        power_mw = np.full(len(frequency), 10 ** (noise_floor_dbm / 10))
        if "No Noise" not in self.port_string:
            # The noise power in a bin fluctuates exponentially around its mean, as on a real analyzer.
            rng = np.random.default_rng()
            power_mw = power_mw * rng.exponential(1.0, len(frequency))

        for position, peak_dbm in zip(position_of_peaks, power_of_peaks_dbm):
            peak_frequency = self.frequency_center + (position - 0.5) * self.frequency_span
            power_mw += 10 ** (peak_dbm / 10) * np.exp(-((frequency - peak_frequency) ** 2) / (2 * peak_width**2))

        return 10 * np.log10(power_mw)

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The commands do not need 'initialize' or 'configure'. Set the frequency range before acquiring a trace.
    """

    @command
    def set_frequency_range(
        self,
        min_frequency: Annotated[Hertz, Range(0.0, None)],
        max_frequency: Annotated[Hertz, Range(0.0, None)],
    ) -> None:
        """Set the frequency range of the trace in Hz. The minimum must be lower than the maximum."""
        if max_frequency <= min_frequency:
            msg = "The minimum frequency must be lower than the maximum frequency."
            raise ValueError(msg)
        self.frequency_min = min_frequency
        self.frequency_max = max_frequency
        self.frequency_center = (min_frequency + max_frequency) / 2
        self.frequency_span = max_frequency - min_frequency

    @command(returns=("min_frequency", "max_frequency"), reads="setpoint")
    def get_frequency_range(self) -> tuple[Hertz, Hertz]:
        """Return (minimum frequency in Hz, maximum frequency in Hz)."""
        return float(self.frequency_min), float(self.frequency_max)

    @command
    def set_reference_level(self, reference_level: DecibelMilliwatts) -> None:
        """Set the reference level in dBm, the top of the display. It does not change the simulated trace."""
        self.reference_level = reference_level

    @command
    def set_trace_mode(self, trace_mode: TraceMode, repetitions: Annotated[int, Range(1, 100)] = 1) -> None:
        """Set the trace mode and the number of repetitions that it combines."""
        self.trace_mode = trace_mode
        self.trace_integration = repetitions

    @command
    def set_noise_enabled(self, enabled: bool) -> None:
        """Switch the simulated noise on or off. Without noise the traces are reproducible."""
        self.port_string = "Simulated Spectrum" if enabled else "No Noise"

    @command(returns=("frequency", "power"))
    def acquire_trace(self) -> tuple[HertzList, DecibelMilliwattsList]:
        """Acquire a trace of 100 points over the set frequency range.

        Returns the lists of the frequencies in Hz and the powers in dBm.
        """
        if self.frequency_max <= self.frequency_min:
            msg = "The frequency range is empty. Use 'set_frequency_range' first."
            raise ValueError(msg)
        self.measure()
        frequencies, power = self.call()
        return list(frequencies), list(power)
