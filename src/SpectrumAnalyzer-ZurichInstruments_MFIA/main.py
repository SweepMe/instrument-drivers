# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Zurich Instruments MFIA and MFLI (spectrum of the demodulator samples)

# The connection to the LabOne Data Server is the same as in the LCRmeter-ZurichInstruments_MFIA driver; fixes to the
# connection may apply to both drivers.

from __future__ import annotations

import time
from typing import Any

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice
from zhinst import ziPython

API_LEVEL = 6

# GUI label -> value of the DAQ module setting fft/window
WINDOWS = {
    "Hann": 1,
    "Hamming": 2,
    "Blackman-Harris": 3,
    "Flat top": 4,
    "Rectangular": 0,
}
FFT_LENGTHS = ["1024", "256", "512", "2048", "4096", "8192", "16384"]
DEMODULATORS = ["1", "2", "3", "4"]
AS_IS = "As is"

# DAQ module settings
TRIGGER_CONTINUOUS = 0
GRID_MODE_EXACT = 4

# Time the DAQ module may take beyond the pure acquisition time before the driver gives up, in s
ACQUISITION_MARGIN = 30.0


class Device(EmptyDevice):
    """Driver for the spectrum (zoom FFT) of the demodulator samples of Zurich Instruments MFIA and MFLI."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "MFIA FFT"

        self.variables = ["Frequency", "Amplitude"]
        self.units = ["Hz", "V"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.daq: Any = None  # LabOne API session, created in connect()

        # GUI parameters as received from the GUI, converted in configure()
        self.gui_parameters: dict[str, Any] = {}
        self.device_id: str = ""

        # Converted GUI parameters
        self.center_frequency: float | None = None  # None keeps the oscillator frequency of the instrument
        self.frequency_span: float = 1000.0
        self.demodulator: int = 0
        self.fft_length: int = 1024
        self.window: int = 1
        self.averages: int = 1

        # Instrument state
        self.oscillator: int = 0
        self.signal_path: str = ""

        # Results
        self.frequency_values: np.ndarray = np.array([])
        self.amplitude_values: np.ndarray = np.array([])

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI parameters. Fields that are left out are greyed out in the SpectrumAnalyzer module."""
        del parameters  # the fields do not depend on the current selection
        return {
            "Frequency label 1": ["Center frequency in Hz:"],
            "Frequency value 1": AS_IS,
            "Frequency label 2": ["Frequency span in Hz:"],
            "Frequency value 2": "1000",
            # Parameters box
            "Demodulator": DEMODULATORS,
            "FFT length": FFT_LENGTHS,
            "Window": list(WINDOWS),
            "Averages": 1,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameters; they are converted and checked in configure()."""
        self.gui_parameters = parameters
        self.device_id = str(parameters.get("Port", "")).lower()

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def find_ports(self) -> list[str]:
        """Return the IDs of all devices the LabOne Data Server can reach. USB needs the LabOne USB driver."""
        return list(ziPython.ziDiscovery().findAll())

    def connect(self) -> None:
        """Open a LabOne API session and connect the device."""
        if not self.device_id:
            msg = "No device selected. Start the LabOne Data Server, press 'Find ports' and select the device ID."
            raise ValueError(msg)

        discovery = ziPython.ziDiscovery()
        discovery.find(self.device_id)
        properties = discovery.get(self.device_id)
        if properties["apilevel"] != API_LEVEL:
            self.message_log(f"MFIA FFT: API level {properties['apilevel']} does not match driver level {API_LEVEL}.")

        # The zhinst-core library shipped with the driver rarely has exactly the version of the LabOne installation
        # on the user's computer, and the Data Server refuses the connection in that case unless mismatches are
        # allowed explicitly.
        self.daq = ziPython.ziDAQServer(
            properties["serveraddress"],
            properties["serverport"],
            properties["apilevel"],
            allow_version_mismatch=True,
        )
        self.daq.connectDevice(self.device_id, properties["interfaces"][0])  # blocking

    def disconnect(self) -> None:
        """Disconnect the device."""
        # connect() may have failed before the API session was created, e.g. if the device was not found
        if self.daq is not None:
            self.daq.disconnectDevice(self.device_id)

    def configure(self) -> None:
        """Convert and check the GUI parameters, then set up the demodulator."""
        self.read_gui_parameters()

        self.oscillator = self.get_demodulator_oscillator(self.demodulator)
        if self.center_frequency is not None:
            self.set_oscillator_frequency(self.oscillator, self.center_frequency)

        # The span of the spectrum equals the sample rate of the demodulator; the instrument rounds it to a rate it
        # supports, which is reported once
        self.set_demodulator_enabled(self.demodulator, True)
        self.set_demodulator_rate(self.demodulator, self.frequency_span)
        self.daq.sync()
        self.message_log(
            f"MFIA FFT: demodulator {self.demodulator + 1} on oscillator {self.oscillator + 1}, span "
            f"{self.get_demodulator_rate(self.demodulator):g} Hz, resolution "
            f"{self.get_demodulator_rate(self.demodulator) / self.fft_length:g} Hz.",
        )

        # The complex demodulator output gives a spectrum on both sides of the demodulation frequency
        self.signal_path = f"/{self.device_id}/demods/{self.demodulator}/sample.xiy.fft.abs"
        if self.averages > 1:
            self.signal_path += ".avg"

    def measure(self) -> None:
        """Record the samples for the spectrum and read it."""
        module = self.daq.dataAcquisitionModule()
        try:
            for key, value in self.get_acquisition_settings():
                module.set(key, value)
            module.subscribe(self.signal_path)
            module.execute()

            acquisition_time = self.averages * self.fft_length / self.get_demodulator_rate(self.demodulator)
            deadline = time.time() + acquisition_time + ACQUISITION_MARGIN
            while not module.finished():
                if self.is_run_stopped():
                    module.finish()
                    return
                if time.time() > deadline:
                    module.finish()
                    msg = f"The MFIA did not deliver the spectrum within {acquisition_time + ACQUISITION_MARGIN:g} s."
                    raise TimeoutError(msg)
                time.sleep(0.1)

            data = module.read(True)
            module.unsubscribe(self.signal_path)
        finally:
            module.clear()

        self.amplitude_values, bin_width = self.extract_spectrum(data)

        # The FFT axis is centered on the demodulation frequency, which is added to get absolute frequencies
        bin_count = len(self.amplitude_values)
        offsets = (np.arange(bin_count) - bin_count / 2 + 0.5) * bin_width
        self.frequency_values = self.get_demodulator_frequency(self.demodulator) + offsets

    def call(self) -> list[np.ndarray]:
        """Return frequency and amplitude of the spectrum."""
        return [self.frequency_values, self.amplitude_values]

    """ here, helper functions convert the GUI parameters and the results """

    def read_gui_parameters(self) -> None:
        """Convert and check the GUI parameters."""
        parameters = self.gui_parameters

        if parameters.get("Frequency label 1", "Center frequency in Hz:") != "Center frequency in Hz:":
            msg = "This driver only supports center frequency and frequency span."
            raise ValueError(msg)
        center_frequency = str(parameters.get("Frequency value 1", AS_IS)).strip()
        if center_frequency in ("", AS_IS):
            self.center_frequency = None
        else:
            self.center_frequency = self.to_number(center_frequency, "Center frequency")
            if self.center_frequency < 0:
                msg = f"The center frequency must not be negative, but is {self.center_frequency:g} Hz."
                raise ValueError(msg)

        self.frequency_span = self.to_number(parameters.get("Frequency value 2", "1000"), "Frequency span")
        if self.frequency_span <= 0:
            msg = f"The frequency span must be above 0 Hz, but is {self.frequency_span:g} Hz."
            raise ValueError(msg)

        demodulator = parameters.get("Demodulator", DEMODULATORS[0])
        if demodulator not in DEMODULATORS:
            msg = f"Unknown demodulator '{demodulator}'. Choose one of: {', '.join(DEMODULATORS)}."
            raise ValueError(msg)
        self.demodulator = int(demodulator) - 1

        fft_length = str(parameters.get("FFT length", FFT_LENGTHS[0]))
        if fft_length not in FFT_LENGTHS:
            msg = f"Unknown FFT length '{fft_length}'. Choose one of: {', '.join(FFT_LENGTHS)}."
            raise ValueError(msg)
        self.fft_length = int(fft_length)

        window = parameters.get("Window", "Hann")
        if window not in WINDOWS:
            msg = f"Unknown window '{window}'. Choose one of: {', '.join(WINDOWS)}."
            raise ValueError(msg)
        self.window = WINDOWS[window]

        self.averages = int(self.to_number(parameters.get("Averages", 1), "Averages"))
        if self.averages < 1:
            msg = f"Averages must be at least 1, not {self.averages}."
            raise ValueError(msg)

    def get_acquisition_settings(self) -> list[tuple[str, Any]]:
        """Return the DAQ module settings for one spectrum. 'device' must be set first."""
        return [
            ("device", self.device_id),
            ("type", TRIGGER_CONTINUOUS),
            ("grid/mode", GRID_MODE_EXACT),
            ("grid/cols", self.fft_length),
            ("grid/rows", 1),
            ("grid/repetitions", self.averages),
            ("count", 1),
            ("endless", 0),
            ("fft/window", self.window),
        ]

    def extract_spectrum(self, data: dict[str, Any]) -> tuple[np.ndarray, float]:
        """Return the amplitudes and the bin width in Hz of the last spectrum in the data read from the DAQ module."""
        # The keys of the returned data may differ in case from the subscribed path
        paths = {key.lower(): key for key in data}
        if self.signal_path.lower() not in paths:
            msg = f"The MFIA did not return a spectrum for '{self.signal_path}', only for {sorted(data)}."
            raise RuntimeError(msg)

        spectrum = data[paths[self.signal_path.lower()]][-1]  # one entry per recorded grid, the last is the newest
        amplitudes = np.asarray(spectrum["value"][0], dtype=float)
        bin_width = float(spectrum["header"]["gridcoldelta"][0])
        return amplitudes, bin_width

    @staticmethod
    def to_number(value: object, name: str) -> float:
        """Return the value as float, or raise a ValueError with a user-readable message."""
        try:
            return float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            msg = f"'{name}' must be a number, but is '{value}'."
            raise ValueError(msg) from None

    """ here, communication commands are wrapped into python convenience functions """

    def get_demodulator_oscillator(self, demodulator: int) -> int:
        """Return the index of the oscillator that the demodulator uses as reference."""
        return int(self.daq.getInt(f"/{self.device_id}/demods/{demodulator}/oscselect"))

    def set_oscillator_frequency(self, oscillator: int, frequency: float) -> None:
        """Set the frequency of the oscillator in Hz."""
        self.daq.setDouble(f"/{self.device_id}/oscs/{oscillator}/freq", frequency)

    def set_demodulator_enabled(self, demodulator: int, enabled: bool) -> None:
        """Switch the data transfer of the demodulator on or off."""
        self.daq.setInt(f"/{self.device_id}/demods/{demodulator}/enable", 1 if enabled else 0)

    def set_demodulator_rate(self, demodulator: int, rate: float) -> None:
        """Set the sample rate of the demodulator in 1/s. The instrument rounds it to a supported rate."""
        self.daq.setDouble(f"/{self.device_id}/demods/{demodulator}/rate", rate)

    def get_demodulator_rate(self, demodulator: int) -> float:
        """Return the sample rate of the demodulator in 1/s."""
        return float(self.daq.getDouble(f"/{self.device_id}/demods/{demodulator}/rate"))

    def get_demodulator_frequency(self, demodulator: int) -> float:
        """Return the demodulation frequency in Hz."""
        return float(self.daq.getDouble(f"/{self.device_id}/demods/{demodulator}/freq"))
