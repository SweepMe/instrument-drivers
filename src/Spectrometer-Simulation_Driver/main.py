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
# * Module: Spectrometer
# * Instrument: Simulation Spectrometer


import os
import random
import time

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class to implement functionalities of a simulated spectrometer."""
    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Simulation"  # short name will be shown in the sequencer

        self.variables = ["Wavelength", "Intensity", "Integration time"]
        self.units = ["nm", "counts/s", "s"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        self.calibrationfolder = self.get_folder("CALIBRATIONS")

        # Measurement Parameters
        self.sweep_mode: str = "None"
        self.port_string: str = "Spectrometer1"

        self.integration_time: float = 0.1
        self.average: int = 1

        self.calibration: str = ""
        self.trigger_mode: str = "Software"
        self.trigger_delay: float = 0.0

    def find_ports(self) -> list[str]:
        """Return a list of strings with possible port items."""
        return ["Spectrometer1", "Spectrometer2", "Spectrometer3"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["None", "Integration time in s"],
            "IntegrationTime": 0.1,
            "Average": 1,
            "Trigger": ["Software", "External"],
            "TriggerDelay": 0.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.integration_time = float(parameter["IntegrationTime"])
        self.sweep_mode = parameter["SweepMode"]
        self.average = int(parameter["Average"])
        self.trigger_mode = parameter["Trigger"]
        self.trigger_delay = float(parameter["TriggerDelay"])
        self.port_string = parameter["Port"]

    def measure(self) -> None:
        """Trigger acquisition of new data."""
        time.sleep(self.trigger_delay)
        for _ in range(self.average):
            time.sleep(self.integration_time)

    def apply(self) -> None:
        """Apply the sweep values."""
        if self.sweep_mode == "Integration time in s":
            self.integration_time = self.value

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        wavelengths = self.get_wavelengths()
        intensities = self.get_intensities()
        for _ in range(self.average - 1):
            intensities += self.get_intensities()

        intensities = intensities / self.average
        intensities_per_second = intensities / self.integration_time

        return [wavelengths, intensities_per_second, self.integration_time]

    def get_wavelengths(self) -> np.array:
        """Return a list of all wavelengths at which the spectrum is measured."""
        # must return a list of all wavelengths at which the spectrum is measured
        spectrum_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + "test_spectrum.txt"
        spectrum = np.loadtxt(spectrum_file, skiprows=3)
        return spectrum[:, 0]

    def get_intensities(self) -> np.array:
        """Return the measured intensities."""
        intensities = np.array([])
        if self.port_string == "Spectrometer2":
            # Simulate Raman spectrum
            wavelengths = self.get_wavelengths()

            peak_position = wavelengths[int(len(wavelengths) * 0.6)]
            peak_width = (wavelengths[-1] - wavelengths[0]) * 0.05
            peak_amplitude = 1000

            intensities = peak_amplitude * self.calculate_gaussian_peak(peak_position, peak_width)
            intensities += self.calculate_background_spectrum()
        elif self.port_string == "Spectrometer3":
            # Simulate background spectrum
            intensities = self.calculate_background_spectrum()
        else:
            # load spectral data from test_spectrum.txt
            spectrum_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + "test_spectrum.txt"
            spectrum = np.loadtxt(spectrum_file, skiprows=3)
            intensities = spectrum[:, 1] - 500  # with offset subtraction

        # Scale intensity with integration time
        intensities = intensities * self.integration_time

        # Add noise
        intensities += self.calculate_noise()

        return np.array(intensities)

    def calculate_background_spectrum(self) -> np.array:
        """Calculate a background spectrum."""
        intensities = 150 * self.calculate_gaussian_peak(750, 250000)
        intensities += 350 * self.calculate_gaussian_peak(450, 50000)
        return intensities

    def calculate_gaussian_peak(self, peak_position: float, peak_width: float) -> np.array:
        """Calculate a gaussian peak with the given parameters."""
        return np.exp(-(self.get_wavelengths() - peak_position) ** 2 / peak_width)

    def calculate_noise(self) -> np.array:
        """Calculate a noise spectrum."""
        noise = []
        for _ in self.get_wavelengths():
            noise.append(50 * random.random() - 25)
        return noise
