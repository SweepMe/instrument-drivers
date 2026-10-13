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


import math
import os
import random
import time

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class to implement functionalities of a simulated spectrometer."""

    description = """
        <h3>Simulated Spectrometer</h3>
        <p>The <b>Port</b> field is reused to select which spectrum the simulation returns:</p>
        <ul>
        <li><b>Test spectrum.txt</b>: replays the bundled <i>test_spectrum.txt</i> file.</li>
        <li><b>Raman Spectrum</b>: a Gaussian Raman peak on a simulated background.</li>
        <li><b>Background Spectrum</b>: the background only, without the Raman peak.</li>
        <li><b>Silicon Photonics</b>: a Gaussian transmission dip in dB that drifts during the run.</li>
        <li><b>No Noise</b>: the Raman spectrum without random noise for reproducible tests.</li>
        </ul>
        """

    # Initial silicon-photonics peak wavelength in nm; reset in initialize() so it does not drift across runs.
    SIPH_PEAK_WL_START: float = 1530.0

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
        self.port_string: str = "Test spectrum.txt"

        self.integration_time: float = 0.1
        self.average: int = 1

        self.calibration: str = ""
        self.trigger_mode: str = "Software"
        self.trigger_delay: float = 0.0

        # Silicon-photonics simulation parameters (only used when port_string == "Silicon Photonics")
        self.siph_wl_start: float = 1480.0
        self.siph_wl_stop: float = 1580.0
        self.siph_n_points: int = 501
        self.siph_peak_wl: float = self.SIPH_PEAK_WL_START
        self.siph_peak_height_db: float = -3.0
        self.siph_peak_floor_db: float = -25.0
        self.siph_peak_fwhm_nm: float = 4.0
        self.siph_noise_std_db: float = 0.5

    def find_ports(self) -> list[str]:
        """Return a list of strings with possible port items."""
        return ["Test spectrum.txt", "Raman Spectrum", "Background Spectrum", "Silicon Photonics", "No Noise"]

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
        self.port_string = parameter.get("Port", self.port_string)

    def initialize(self) -> None:
        """Reset the silicon-photonics peak so it does not drift out of range across runs."""
        self.siph_peak_wl = self.SIPH_PEAK_WL_START

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

        if self.port_string == "Silicon Photonics":
            # The peak drifts once per acquisition; the readings of one acquisition are averaged in dB, the unit in
            # which the noise is simulated.
            self.siph_peak_wl += 3
            readings = [self.get_intensities() for _ in range(max(1, int(self.average)))]
            return [wavelengths, np.mean(readings, axis=0), self.integration_time]

        intensities = self.get_intensities()
        for _ in range(self.average - 1):
            intensities += self.get_intensities()

        intensities = intensities / self.average
        intensities_per_second = intensities / self.integration_time
        return [wavelengths, intensities_per_second, self.integration_time]

    def get_wavelengths(self) -> np.ndarray:
        """Return a list of all wavelengths at which the spectrum is measured."""
        if self.port_string == "Silicon Photonics":
            return np.linspace(self.siph_wl_start, self.siph_wl_stop, int(self.siph_n_points))

        # must return a list of all wavelengths at which the spectrum is measured
        spectrum_file = os.path.dirname(os.path.abspath(__file__)) + os.sep + "test_spectrum.txt"
        spectrum = np.loadtxt(spectrum_file, skiprows=3)
        return spectrum[:, 0]

    def read_Wavelengths(self) -> np.ndarray:
        """For compatibility with the old version of the module."""
        return self.get_wavelengths()

    def get_intensities(self) -> np.ndarray:
        """Return one raw reading in counts per integration time (dB for 'Silicon Photonics'), not averaged.

        'acquire_spectrum' averages such readings and divides them by the integration time to give counts/s.
        """
        if self.port_string == "Silicon Photonics":
            wavelengths = self.get_wavelengths()
            sigma = self.siph_peak_fwhm_nm / (2.0 * math.sqrt(2.0 * math.log(2.0)))
            gauss = np.exp(-((wavelengths - self.siph_peak_wl) ** 2) / (2.0 * sigma ** 2))
            transmission_db = self.siph_peak_floor_db + (self.siph_peak_height_db - self.siph_peak_floor_db) * gauss
            rng = np.random.default_rng()
            transmission_db = transmission_db + rng.normal(0.0, self.siph_noise_std_db, len(wavelengths))
            return np.array(transmission_db)

        intensities = np.array([])
        if self.port_string in ("Raman Spectrum", "No Noise"):
            # Simulate Raman spectrum
            wavelengths = self.get_wavelengths()

            peak_position = wavelengths[int(len(wavelengths) * 0.6)]
            peak_width = (wavelengths[-1] - wavelengths[0]) * 0.05
            peak_amplitude = 1000

            intensities = peak_amplitude * self.calculate_gaussian_peak(peak_position, peak_width)
            intensities += self.calculate_background_spectrum()
        elif self.port_string == "Background Spectrum":
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
        if not self.port_string == "No Noise":
            intensities += self.calculate_noise()

        return np.array(intensities)

    def calculate_background_spectrum(self) -> np.ndarray:
        """Calculate a background spectrum."""
        intensities = 150 * self.calculate_gaussian_peak(750, 250000)
        intensities += 350 * self.calculate_gaussian_peak(450, 50000)
        return intensities

    def calculate_gaussian_peak(self, peak_position: float, peak_width: float) -> np.ndarray:
        """Calculate a gaussian peak with the given parameters."""
        return np.exp(-(self.get_wavelengths() - peak_position) ** 2 / peak_width)

    def calculate_noise(self) -> np.ndarray:
        """Calculate a noise spectrum."""
        noise = []
        for _ in self.get_wavelengths():
            noise.append(50 * random.random() - 25)
        return np.array(noise)

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The commands do not need 'initialize' or 'configure'. Which spectrum the simulation returns is selected with
    'set_spectrum_mode'.
    """

    def set_spectrum_mode(self, mode: str) -> None:
        """Select: 'Test spectrum.txt', 'Raman Spectrum', 'Background Spectrum', 'Silicon Photonics' or 'No Noise'."""
        valid_modes = self.find_ports()
        if mode not in valid_modes:
            msg = f"Spectrum mode '{mode}' is not supported. Choose one of {valid_modes}."
            raise ValueError(msg)
        self.port_string = mode
        if mode == "Silicon Photonics":
            self.siph_peak_wl = self.SIPH_PEAK_WL_START

    def get_spectrum_mode(self) -> str:
        """Return the selected simulated spectrum."""
        return str(self.port_string)

    def set_integration_time(self, integration_time: float) -> None:
        """Set the integration time in s (greater than 0 s and at most 10 s)."""
        integration_time = float(integration_time)
        if not 0 < integration_time <= 10:
            msg = f"Integration time {integration_time} s must be greater than 0 s and at most 10 s."
            raise ValueError(msg)
        self.integration_time = integration_time

    def get_integration_time(self) -> float:
        """Return the integration time in s."""
        return float(self.integration_time)

    def set_average(self, average: int) -> None:
        """Set the number of spectra that are averaged for one acquisition (1 to 100)."""
        average = int(average)
        if not 1 <= average <= 100:
            msg = f"Average {average} must be between 1 and 100."
            raise ValueError(msg)
        self.average = average

    def acquire_spectrum(self) -> dict:
        """Acquire a spectrum. It takes as long as integration time times average.

        Returns a dictionary with the lists 'wavelength' in nm and 'intensity' in counts/s (in dB for the mode
        'Silicon Photonics') and the 'integration_time' in s.
        """
        self.measure()
        wavelengths, intensities, integration_time = self.call()
        return {
            "wavelength": np.asarray(wavelengths, dtype=float).tolist(),
            "intensity": np.asarray(intensities, dtype=float).tolist(),
            "integration_time": float(integration_time),
        }
