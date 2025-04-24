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
#
# SweepMe! driver
# * Module: Switch
# * Instrument: G2V sunbrick

from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the G2V sunbrick."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "sunbrick"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB", "COM", "TCPIP"]

        # Measurement parameters
        self.on_value: int = 100
        self.use_specific_channels: bool = False
        self.channel_list: str = "1,3,5"
        self.target_node: int = 0

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "ON Value": [100, 0, 255, 'int'],
            "Use Specific Channels": False,
            "Channel List": "1,3,5",
            "Target Node": [0, 1, 2, 3, 4, 5, 6, 7, 8],
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]
        self.on_value = parameter["ON Value"]
        self.use_specific_channels = parameter["Use Specific Channels"]
        self.channel_list = parameter["Channel List"]
        self.target_node = parameter["Target Node"]

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.voltage, self.current]

