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
#
# SweepMe! driver
# * Module: Logger
# * Instrument: HighFinesse WS-6 wavelength meter

from __future__ import annotations

import ctypes
from pathlib import Path

from pysweepme import debug
from pysweepme.EmptyDeviceClass import EmptyDevice

# Base operation constants of the Operation function, see chapter 4.1.8 of the WS-6 manual
CTRL_STOP_ALL = 0
CTRL_START_MEASUREMENT = 2

# Return error values of GetWavelength and GetFrequency
WAVELENGTH_ERRORS = {
    0: "No new measurement value available.",
    -1: "No signal detected.",
    -2: "Signal cannot be calculated.",
    -3: "Signal is too small.",
    -4: "Signal is too large.",
    -5: "Wavelength meter is not active.",
    -6: "Function is not available for this wavelength meter.",
    -8: "Signal could not be divided into separated pulses.",
    -13: "Division by zero.",
    -14: "Signal is out of measurement range.",
}

# All error values of GetTemperature are ErrTemperature (-1000) combined with the error values above
ERR_TEMPERATURE = -1000

# Windows resolves a bare file name from System32/SysWOW64, where the HighFinesse installer puts the dll.
DEFAULT_DLL_PATH = "wlmData.dll"

# Windows error code that LoadLibrary returns if the dll has the wrong architecture
ERROR_BAD_EXE_FORMAT = 193


class Device(EmptyDevice):
    """Driver for the HighFinesse WS-6 wavelength meter."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "WS-6"  # short name will be shown in the sequencer
        self.variables = ["Wavelength", "Frequency", "Temperature"]
        self.units = ["nm", "THz", "°C"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        # The wavelength meter is accessed through wlmData.dll and not through a communication port
        self.port_manager = False

        self._dll: ctypes.WinDLL | None = None

        # Measurement results
        self.wavelength: float = float("nan")
        self.frequency: float = float("nan")
        self.temperature: float = float("nan")

    @property
    def dll(self) -> ctypes.WinDLL:
        """Return the loaded wlmData.dll, raise an error if it has not been loaded in connect()."""
        if self._dll is None:
            msg = "wlmData.dll is not loaded."
            raise RuntimeError(msg)
        return self._dll

    def get_dll_path(self) -> str:
        """Get the path to wlmData.dll from the config file, or the default name if it is not configured.

        The config file is 'Logger-HighFinesse_WS-6.ini' in the 'CustomFiles' folder of the public SweepMe!
        folder. A template is part of this driver folder.
        """
        return self.get_configoptions("DLL").get("path", DEFAULT_DLL_PATH) or DEFAULT_DLL_PATH

    @staticmethod
    def get_dll_error_message(dll_path: str, error: OSError) -> str:
        """Turn a dll loading error into a message that names the likely cause."""
        hint = (
            "The HighFinesse software installs wlmData.dll into the Windows System32 folder, and the 32-bit "
            "version into SysWOW64. Use the config file 'Logger-HighFinesse_WS-6.ini' as described in the "
            "documentation."
        )

        if error.winerror == ERROR_BAD_EXE_FORMAT:
            hint = (
                "The dll has the wrong architecture: a 64-bit SweepMe! can only load a 64-bit dll and a "
                "32-bit SweepMe! only a 32-bit one. The bitness is the second field of the dll version "
                "stamp, e.g. 7.64.263.5 is 64-bit and 7.32.263.5 is 32-bit. Note that the folder names of "
                "the HighFinesse installation do not necessarily tell the bitness."
            )
        elif Path(dll_path).name != dll_path and not Path(dll_path).is_file():
            hint = f"The file does not exist. {hint}"

        return f"Cannot load '{dll_path}'. {hint} Details: {error}"

    def connect(self) -> None:
        """Load wlmData.dll and check that a wavelength meter server application is running."""
        dll_path = self.get_dll_path()

        try:
            self._dll = ctypes.WinDLL(dll_path)
        except OSError as e:
            raise OSError(self.get_dll_error_message(dll_path, e)) from e

        self.define_dll_signatures()

        if self.get_server_count() == 0:
            msg = "No running wavelength meter server found. Please start the HighFinesse software."
            raise RuntimeError(msg)

    def disconnect(self) -> None:
        """Release the handle to wlmData.dll."""
        self._dll = None

    def initialize(self) -> None:
        """Start the measurement of the wavelength meter server application."""
        if self.start_measurement() < 0:
            msg = "Cannot start the measurement via the API. Please start it in the HighFinesse software."
            raise RuntimeError(msg)

    def deinitialize(self) -> None:
        """Stop the measurement of the wavelength meter server application."""
        # Teardown also runs if connect() failed, then there is no dll to talk to
        if self._dll is not None:
            self.stop_measurement()

    def measure(self) -> None:
        """Read wavelength, frequency, and temperature of the last measurement shot."""
        self.wavelength = self.get_wavelength()
        self.frequency = self.get_frequency()
        self.temperature = self.get_temperature()

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.wavelength, self.frequency, self.temperature]

    def define_dll_signatures(self) -> None:
        """Declare the argument and return types of the used wlmData.dll functions.

        This is required because the driver loads the dll directly instead of using the HighFinesse
        Python header 'wlmData.py', which would declare the same signatures. ctypes assumes a c_int
        return value for every function, so without an explicit restype the measurement functions,
        which return a C double, would deliver meaningless numbers.
        """
        self.dll.GetWLMCount.argtypes = [ctypes.c_long]
        self.dll.GetWLMCount.restype = ctypes.c_long

        self.dll.GetWLMVersion.argtypes = [ctypes.c_long]
        self.dll.GetWLMVersion.restype = ctypes.c_long

        self.dll.Operation.argtypes = [ctypes.c_ushort]
        self.dll.Operation.restype = ctypes.c_long

        for function in (self.dll.GetWavelength, self.dll.GetFrequency, self.dll.GetTemperature):
            function.argtypes = [ctypes.c_double]
            function.restype = ctypes.c_double

    # wrapped API commands below

    def get_version(self) -> str:
        """Get the version of the wavelength meter as '<type>.<version>.<revision>.<build>'."""
        return ".".join(str(self.dll.GetWLMVersion(detail)) for detail in range(4))

    def get_server_count(self) -> int:
        """Get the number of running wavelength meter server applications."""
        return int(self.dll.GetWLMCount(0))

    def start_measurement(self) -> int:
        """Start the measurement mode. Returns a negative value if the command failed."""
        return int(self.dll.Operation(CTRL_START_MEASUREMENT))

    def stop_measurement(self) -> int:
        """Stop all measurement activities. Returns a negative value if the command failed."""
        return int(self.dll.Operation(CTRL_STOP_ALL))

    def get_wavelength(self) -> float:
        """Get the wavelength of the last measurement in nm, or nan if no value could be measured."""
        wavelength = float(self.dll.GetWavelength(0.0))
        if wavelength <= 0:
            self.report_error(wavelength)
            return float("nan")
        return wavelength

    def get_frequency(self) -> float:
        """Get the frequency of the last measurement in THz, or nan if no value could be measured."""
        frequency = float(self.dll.GetFrequency(0.0))
        if frequency <= 0:
            self.report_error(frequency)
            return float("nan")
        return frequency

    def get_temperature(self) -> float:
        """Get the temperature inside the optical unit in °C, or nan if it cannot be measured."""
        temperature = float(self.dll.GetTemperature(0.0))
        if temperature <= ERR_TEMPERATURE:
            self.report_error(temperature - ERR_TEMPERATURE)
            return float("nan")
        return temperature

    @staticmethod
    def report_error(error_code: float) -> None:
        """Print the meaning of an API error code to the debug widget."""
        message = WAVELENGTH_ERRORS.get(int(error_code), f"Unknown error code {int(error_code)}.")
        debug(f"HighFinesse WS-6: {message}")
