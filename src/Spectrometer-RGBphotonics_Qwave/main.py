# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
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
# * Instrument: RGB Photonics Qwave

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Annotated, Any

import numpy as np
from pysweepme.commands import Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Seconds = Annotated[float, Unit("s")]
Celsius = Annotated[float, Unit("°C")]

DLL_NAME = "RgbDriverKit"
"""The .NET library of RGB Photonics' Waves SDK that drives the spectrometers (RgbDriverKit.dll)."""
SIMULATED = "Simulated spectrometer"
"""The port of the spectrometer the library simulates, offered when no spectrometer is connected."""
SWEEP_INTEGRATION_TIME = "Integration time in s"
"""The sweep mode that sets the integration time; earlier versions called it "Integration time [s]"."""


def load_driver_kit(folders: list[Path]) -> Any:  # noqa: ANN401 - a .NET namespace imported through pythonnet
    """Import RgbDriverKit through pythonnet from the first of `folders` that holds RgbDriverKit.dll."""
    try:
        import clr  # noqa: PLC0415 - pythonnet only when the spectrometer is used; it is not part of pysweepme
    except ImportError as exc:
        msg = (
            "The Qwave spectrometer needs pythonnet ('import clr'), which is not part of pysweepme: "
            "install it with 'pip install pythonnet' (SweepMe! brings it)."
        )
        raise ImportError(msg) from exc
    folder = next((f for f in folders if (f / f"{DLL_NAME}.dll").is_file()), None)
    if folder is None:
        msg = (
            f"{DLL_NAME}.dll was not found in {', '.join(str(f) for f in folders)}. Install the Waves SDK of "
            "RGB Photonics (https://www.rgb-photonics.com/downloads/) and put RgbDriverKit.dll into SweepMe!'s "
            "folder 'ExternalLibraries' in the public SweepMe! folder. If it is there, check in its properties "
            "whether Windows blocks the file."
        )
        raise FileNotFoundError(msg)
    if str(folder) not in sys.path:
        sys.path.append(str(folder))
    clr.AddReference(DLL_NAME)
    import RgbDriverKit  # noqa: PLC0415 - the .NET namespace exists only after AddReference

    return RgbDriverKit


class Device(EmptyDevice):
    """Driver for RGB Photonics' Qwave spectrometers and their simulation through the Waves SDK (RgbDriverKit.dll)."""

    def __init__(self) -> None:
        """Define the returned variables; the library is loaded when a spectrometer is found or connected."""
        super().__init__()

        self.shortname = "Qwave"

        self.variables = ["Wavelength", "Intensity", "Integration time"]
        self.units = ["nm", "a.u.", "s"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        self.port_string: str = ""
        """The port: a spectrometer's detailed device name or the simulated spectrometer."""
        self.sweep_mode: str = "None"
        """The sweep mode of the module."""
        self.integration_time: float = 0.1
        """The integration time in s."""
        self.average: int = 1
        """The number of spectra the spectrometer averages."""
        self.calibration: str = "SensitivityCalibration On"
        """Whether the spectrometer applies its sensitivity calibration."""
        self.trigger: str = "Internal"
        """The trigger: internal, or an external rising or falling edge."""

        self.kit: Any = None
        """The .NET namespace RgbDriverKit, loaded in connect."""
        self.spectrometer: Any = None
        """The open .NET spectrometer object."""
        self.wavelengths: np.ndarray = np.array([])
        """The wavelengths in nm, read in initialize."""
        self.spectrum: np.ndarray = np.array([])
        """The last spectrum in a.u."""

    def set_GUIparameter(self) -> dict[str, Any]:  # noqa: N802 - the Spectrometer module's fixed keys
        """Return the GUI fields of the Spectrometer module."""
        return {
            "SweepMode": ["None", SWEEP_INTEGRATION_TIME],
            "Calibration": ["SensitivityCalibration On", "SensitivityCalibration Off"],
            "IntegrationTime": 0.1,
            "Trigger": ["Internal", "External Rising", "External Falling"],
            "Average": 1,
        }

    def get_GUIparameter(self, parameter: dict[str, Any]) -> None:  # noqa: N802 - the Spectrometer module's fixed keys
        """Keep the selections of the module."""
        self.port_string = str(parameter.get("Port", self.port_string))
        self.sweep_mode = str(parameter.get("SweepMode", "None"))
        self.integration_time = float(parameter.get("IntegrationTime", 0.1))
        self.average = int(parameter.get("Average", 1))
        self.calibration = str(parameter.get("Calibration", "SensitivityCalibration On"))
        self.trigger = str(parameter.get("Trigger", "Internal"))

    def find_ports(self) -> list[str]:
        """Return the names of the connected spectrometers, or the simulated spectrometer when none is connected."""
        kit = self.load_kit()
        ports = []
        for device in kit.RgbSpectrometer.SearchDevices():
            device.Open()
            ports.append(str(device.DetailedDeviceName))
            device.Close()
        return ports or [SIMULATED]

    def connect(self) -> None:
        """Open the spectrometer of the port; instances on one port share it."""
        self.kit = self.load_kit()
        key = f"RGBphotonics_Qwave_port{self.port_string}"
        if key in self.device_communication:
            self.spectrometer = self.device_communication[key]
            return
        if self.port_string == SIMULATED:
            self.spectrometer = self.kit.SimulatedSpectrometer.SearchDevices()[0]
        else:
            devices = list(self.kit.RgbSpectrometer.SearchDevices())
            if not devices:
                msg = "No Qwave spectrometer is connected. Use Find Ports, or choose the simulated spectrometer."
                raise ValueError(msg)
            self.spectrometer = devices[0] if len(devices) == 1 else self.device_named(devices, self.port_string)
        self.spectrometer.Open()
        self.device_communication[key] = self.spectrometer

    def disconnect(self) -> None:
        """Close the spectrometer."""
        key = f"RGBphotonics_Qwave_port{self.port_string}"
        if key in self.device_communication:
            self.device_communication.pop(key).Close()
        self.spectrometer = None

    def initialize(self) -> None:
        """Set integration time, averaging, sensitivity calibration and trigger, and read the wavelengths."""
        self.set_integration_time(self.integration_time)
        self.spectrometer.Averaging = self.average
        calibrated = self.calibration == "SensitivityCalibration On"
        if calibrated and not self.spectrometer.CanUseSensitivityCalibration:
            msg = "This spectrometer has no sensitivity calibration: set Calibration to 'SensitivityCalibration Off'."
            raise ValueError(msg)
        if self.trigger.startswith("External") and not self.spectrometer.CanUseExternalTrigger:
            msg = "This spectrometer has no external trigger: set Trigger to 'Internal'."
            raise ValueError(msg)
        self.spectrometer.UseSensitivityCalibration = calibrated
        if self.trigger.startswith("External"):
            self.spectrometer.UseExternalTrigger = True
            self.spectrometer.SpectrometerTriggerOptions = 2
            self.spectrometer.ExternalTriggerSource = 1
            self.spectrometer.ExternalTriggerRisingEdge = self.trigger == "External Rising"
        else:
            self.spectrometer.UseExternalTrigger = False
        self.wavelengths = np.asarray(list(self.spectrometer.GetWavelengths()), dtype=float)

    def apply(self) -> None:
        """Set the integration time of the sweep (also from sequences of earlier versions)."""
        if self.sweep_mode.startswith("Integration time"):
            self.set_integration_time(float(self.value))

    def measure(self) -> None:
        """Wait until the spectrometer is idle and start an exposure (with an external trigger it waits for it)."""
        while self.spectrometer.Status != self.kit.SpectrometerStatus.Idle:
            if self.is_run_stopped():
                return
            time.sleep(0.01)
        if self.trigger == "Internal":
            self.spectrometer.StartExposure()

    def request_result(self) -> None:
        """Wait for the spectrum; a run that is stopped meanwhile does not wait for an external trigger any more."""
        waiting = (self.kit.SpectrometerStatus.WaitingForTrigger, self.kit.SpectrometerStatus.TakingSpectrum)
        while self.spectrometer.Status in waiting:
            if self.is_run_stopped():
                return
            time.sleep(0.01)

    def read_result(self) -> None:
        """Read the spectrum."""
        self.spectrum = np.asarray(list(self.spectrometer.GetSpectrum()), dtype=float)

    def call(self) -> list[Any]:
        """Return wavelengths in nm, intensities in a.u. and the integration time in s."""
        return [self.wavelengths, self.spectrum, self.integration_time]

    # check_driver: ignore DC004 - a hook of the Spectrometer module, which needs an ndarray back
    def get_wavelengths(self) -> np.ndarray:
        """Return the wavelengths in nm at which the spectrum is measured."""
        return self.wavelengths

    # check_driver: ignore DC004 - the hook of older Spectrometer module versions
    def read_Wavelengths(self) -> np.ndarray:  # noqa: N802 - the name older Spectrometer modules call
        """For compatibility with older versions of the module."""
        return self.wavelengths

    # Communication commands

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the spectrometer's model, serial number and device name."""
        s = self.spectrometer
        return f"RGB Photonics {s.ModelName}, SN {s.SerialNo}, {s.DetailedDeviceName}"

    @command
    def set_integration_time(self, integration_time: Seconds) -> None:
        """Set the integration time in s, within the spectrometer's minimum and maximum exposure time."""
        low, high = float(self.spectrometer.MinExposureTime), float(self.spectrometer.MaxExposureTime)
        if not low <= integration_time <= high:
            msg = f"The integration time {integration_time} s is outside of {low} s to {high} s of this spectrometer."
            raise ValueError(msg)
        self.spectrometer.ExposureTime = integration_time
        self.integration_time = float(integration_time)

    @command(returns=("integration_time",), reads="setpoint")
    def get_integration_time(self) -> Seconds:
        """Return the integration time in s."""
        return float(self.spectrometer.ExposureTime)

    @command(returns=("temperature",))
    def get_temperature(self) -> Celsius:
        """Return the temperature of the spectrometer in °C."""
        return float(self.spectrometer.Temperature)

    # Helpers

    def load_kit(self) -> Any:  # noqa: ANN401 - a .NET namespace
        """Return RgbDriverKit from SweepMe!'s folder of external libraries or from the driver's own folder."""
        return load_driver_kit([Path(self.get_folder("EXTLIBS")), Path(self.get_folder("SELF"))])

    @staticmethod
    def device_named(devices: list[Any], name: str) -> Any:  # noqa: ANN401 - a .NET device
        """Return the device of several with the detailed name `name`; the others are closed again."""
        for device in devices:
            device.Open()
            found = str(device.DetailedDeviceName) == name
            device.Close()
            if found:
                return device
        msg = f"No Qwave spectrometer named '{name}' is connected. Use Find Ports."
        raise ValueError(msg)
