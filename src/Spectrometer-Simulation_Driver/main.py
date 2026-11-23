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
# * Module: Spectrometer
# * Instrument: Simulation Spectrometer

"""SweepMe! driver of a simulated spectrometer."""

from __future__ import annotations

import math
import random
import time
from pathlib import Path
from typing import Annotated, Any, Literal

import numpy as np
from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Seconds = Annotated[float, Unit("s")]
Nanometers = Annotated[float, Unit("nm")]
NanometersList = list[Nanometers]
SpectrumMode = Literal["Test spectrum.txt", "Raman Spectrum", "Background Spectrum", "Silicon Photonics", "No Noise"]

SWEEP_MODES: list[str] = ["None", "Integration time in s"]
TRIGGER_MODES: list[str] = ["Software", "External"]
TEST_SPECTRUM_FILE: Path = Path(__file__).resolve().parent / "test_spectrum.txt"


class Device(EmptyDevice):
    """Device class to implement functionalities of a simulated spectrometer."""

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
        self.gui_parameters: dict[str, Any] = {}
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

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI parameters with their default values."""
        return {
            "SweepMode": SWEEP_MODES,
            "IntegrationTime": 0.1,
            "Average": 1,
            "Trigger": TRIGGER_MODES,
            "TriggerDelay": 0.0,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the values of the GUI parameters; configure() converts and checks them."""
        self.gui_parameters = parameters
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.trigger_mode = parameters.get("Trigger", "Software")
        self.port_string = parameters.get("Port", self.port_string)
        self._update_units()

    def initialize(self) -> None:
        """Reset the silicon-photonics peak so it does not drift out of range across runs."""
        self.siph_peak_wl = self.SIPH_PEAK_WL_START

    def configure(self) -> None:
        """Convert and check the GUI values; it runs at every start of the branch and after a reconfigure."""
        if self.sweep_mode not in SWEEP_MODES:
            msg = f"Sweep mode '{self.sweep_mode}' is not supported. Choose one of {SWEEP_MODES}."
            raise ValueError(msg)
        if self.trigger_mode not in TRIGGER_MODES:
            msg = f"Trigger '{self.trigger_mode}' is not supported. Choose one of {TRIGGER_MODES}."
            raise ValueError(msg)

        self.integration_time = float(self.gui_parameters.get("IntegrationTime", 0.1))
        if self.integration_time <= 0:
            msg = f"Integration time must be greater than 0 s, not {self.integration_time} s."
            raise ValueError(msg)

        self.average = int(self.gui_parameters.get("Average", 1))
        if self.average < 1:
            msg = f"Average must be at least 1, not {self.average}."
            raise ValueError(msg)

        self.trigger_delay = float(self.gui_parameters.get("TriggerDelay", 0.0))
        if self.trigger_delay < 0:
            msg = f"Trigger delay must be 0 s or more, not {self.trigger_delay} s."
            raise ValueError(msg)

    def apply(self) -> None:
        """Apply the sweep values."""
        if self.sweep_mode == "Integration time in s":
            integration_time = float(self.value)
            if integration_time <= 0:
                msg = f"Integration time must be greater than 0 s, not {integration_time} s."
                raise ValueError(msg)
            self.integration_time = integration_time

    def measure(self) -> None:
        """Trigger acquisition of new data."""
        time.sleep(self.trigger_delay)
        for _ in range(self.average):
            if self.is_run_stopped():
                return
            time.sleep(self.integration_time)

    def call(self) -> list[Any]:
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

    # check_driver: ignore DC004 - a hook of the Spectrometer module, which needs an ndarray back
    def get_wavelengths(self) -> np.ndarray:
        """Return a list of all wavelengths at which the spectrum is measured."""
        if self.port_string == "Silicon Photonics":
            return np.linspace(self.siph_wl_start, self.siph_wl_stop, int(self.siph_n_points))

        # must return a list of all wavelengths at which the spectrum is measured
        spectrum = np.loadtxt(TEST_SPECTRUM_FILE, skiprows=3)
        return spectrum[:, 0]

    # check_driver: ignore DC004 - the hook of older Spectrometer module versions
    def read_Wavelengths(self) -> np.ndarray:  # noqa: N802
        """For compatibility with the old version of the module."""
        return self.get_wavelengths()

    # check_driver: ignore DC004 - a helper of call() and acquire_spectrum, not a command
    def get_intensities(self) -> np.ndarray:
        """Return one raw reading in counts per integration time (dB for 'Silicon Photonics'), not averaged.

        'acquire_spectrum' averages such readings and divides them by the integration time to give counts/s.
        """
        if self.port_string == "Silicon Photonics":
            wavelengths = self.get_wavelengths()
            sigma = self.siph_peak_fwhm_nm / (2.0 * math.sqrt(2.0 * math.log(2.0)))
            gauss = np.exp(-((wavelengths - self.siph_peak_wl) ** 2) / (2.0 * sigma**2))
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
            spectrum = np.loadtxt(TEST_SPECTRUM_FILE, skiprows=3)
            intensities = spectrum[:, 1] - 500  # with offset subtraction

        # Scale intensity with integration time
        intensities = intensities * self.integration_time

        # Add noise
        if self.port_string != "No Noise":
            intensities += self.calculate_noise()

        return np.array(intensities)

    def calculate_background_spectrum(self) -> np.ndarray:
        """Calculate a background spectrum."""
        intensities = 150 * self.calculate_gaussian_peak(750, 250000)
        intensities += 350 * self.calculate_gaussian_peak(450, 50000)
        return intensities

    def calculate_gaussian_peak(self, peak_position: float, peak_width: float) -> np.ndarray:
        """Calculate a gaussian peak with the given parameters."""
        return np.exp(-((self.get_wavelengths() - peak_position) ** 2) / peak_width)

    def calculate_noise(self) -> np.ndarray:
        """Calculate a noise spectrum."""
        noise = []
        for _ in self.get_wavelengths():
            noise.append(50 * random.random() - 25)  # noqa: S311
        return np.array(noise)

    def _update_units(self) -> None:
        """Let the unit of the intensities follow the spectrum mode: dB for 'Silicon Photonics', else counts/s."""
        self.units = ["nm", "dB" if self.port_string == "Silicon Photonics" else "counts/s", "s"]

    # --- Communication commands, used e.g. by the SweepMe! Instrument Control ---
    #
    # The commands do not need 'initialize' or 'configure'. Which spectrum the simulation returns is selected with
    # 'set_spectrum_mode'.

    @command
    def set_spectrum_mode(self, spectrum_mode: SpectrumMode) -> None:
        """Select which spectrum the simulation returns."""
        self.port_string = spectrum_mode
        self._update_units()
        if spectrum_mode == "Silicon Photonics":
            self.siph_peak_wl = self.SIPH_PEAK_WL_START

    @command(returns=("spectrum_mode",), reads="setpoint")
    def get_spectrum_mode(self) -> SpectrumMode:
        """Return the selected simulated spectrum."""
        return self.port_string  # type: ignore[return-value]  # set from the Port field or set_spectrum_mode

    # check_driver: ignore DC012 - the bound 0 s is excluded, which Range cannot express
    @command
    def set_integration_time(self, integration_time: Annotated[Seconds, Range(0.0, 10.0)]) -> None:
        """Set the integration time in s. It must be greater than 0 s."""
        if integration_time <= 0:
            msg = f"Integration time {integration_time} s must be greater than 0 s."
            raise ValueError(msg)
        self.integration_time = integration_time

    @command(returns=("integration_time",), reads="setpoint")
    def get_integration_time(self) -> Seconds:
        """Return the integration time in s."""
        return float(self.integration_time)

    @command
    def set_average(self, average: Annotated[int, Range(1, 100)]) -> None:
        """Set the number of spectra that are averaged for one acquisition."""
        self.average = average

    @command(returns=("average",), reads="setpoint")
    def get_average(self) -> int:
        """Return the number of spectra that are averaged for one acquisition."""
        return int(self.average)

    # no unit on the intensities: counts/s, but dB in the mode 'Silicon Photonics'
    @command(returns=("wavelength", "intensity"))
    def acquire_spectrum(self) -> tuple[NanometersList, list[float]]:
        """Acquire a spectrum. It takes as long as integration time times average.

        Returns the lists of the wavelengths in nm and the intensities in counts/s (in dB for the mode
        'Silicon Photonics'). The integration time is returned by 'get_integration_time'.
        """
        self.measure()
        wavelengths, intensities, _integration_time = self.call()
        return (
            np.asarray(wavelengths, dtype=float).tolist(),
            np.asarray(intensities, dtype=float).tolist(),
        )
