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
# * Instrument: Ossila X200

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Ossila X200."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "X200"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Voltage"]
        self.units = ["V"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB", "COM", "TCPIP"]
        self.channel: str = "vsense1"  # or vsense2

        # Measurement parameters
        self.speed_dict = {
            "64": 0,
            "128": 1,
            "256": 2,
            "512": 3,
            "1024": 4,
            "2048": 5,
            "4096": 6,
            "8192": 7,
            "16384": 8,
            "32768": 9,
        }
        self.speed: int = 0  # index of the speed in the speed_dict

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "Channel": ["VSense1", "VSense2"],
            "Speed": list(self.speed_dict.keys()),
            "ADC 2x Mode": False,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.channel = parameters.get("Channel", "VSense1").lower()

        self.speed = self.speed_dict.get(parameters.get("Speed", "64"), 0)
        if parameters.get("ADC 2x Mode", False):
            self.speed += 10  # if ADC 2x mode is enabled, add 10 to the OSR index according to the manual

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.channel not in ["vsense1", "vsense2"]:
            raise ValueError(f"Invalid channel: {self.channel}. Must be 'VSense1' or 'VSense2'.")

        # Validate OSR index (0-19 according to manual)
        if not (0 <= self.speed <= 19):
            msg = f"Invalid OSR index: {self.speed}. Must be between 0 and 19."
            raise ValueError(msg)

        self.port.write(f"{self.channel} set osr {self.speed}")

    def poweron(self) -> None:
        """Enable the device."""
        self.port.write(f"{self.channel} set enabled 1")

    def poweroff(self) -> None:
        """Disable the device."""
        self.port.write(f"{self.channel} set enabled 0")

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        response = self.port.query(f"{self.channel} measure 1")

        try:
            voltage = float(response.strip("[]"))
        except ValueError as e:
            msg = f"Invalid response from the device: {response}. Expected format: '[voltage]'. Error: {e}"
            raise ValueError(msg)

        return voltage

