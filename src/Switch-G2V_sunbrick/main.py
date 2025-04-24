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

from pathlib import Path
from typing import Any

from g2vsunbrick import G2VSunbrick
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the G2V sunbrick.

    Use comma separated list for specific nodes: 1,2,3 or 'All'.
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "sunbrick"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Temperature", "Channel Value"]
        self.units = ["C", "%"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["COM"]

        self.sunbrick: G2VSunbrick | None = None

        # Measurement parameters
        self.sweepmode: str = "Intensity"
        self.channel: int = 1
        self.set_all_channels: bool = False

        self.nodes: list[int] = [0]  # default to all nodes

    def update_gui_parameters(self, parameter: dict[str, Any]) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        new_parameters = {
            "SweepMode": ["Intensity", "Spectrum"],
            "Nodes": "All",
        }

        sweepmode = parameter.get("SweepMode", "Intensity")
        if sweepmode == "Intensity":
            new_parameters["Channel"] = "1"
            new_parameters["Set all Channels"] = False

        return new_parameters

    def apply_gui_parameters(self, parameter: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameter["SweepMode"]

        self.node_string = parameter["Nodes"]


        if self.sweepmode == "Intensity":
            self.set_all_channels = parameter["Set all Channels"]

            if not self.set_all_channels:
                self.channel = int(parameter["Channel"])
                self.variables = ["Temperature", "Channel Value"]
            else:
                self.variables = ["Temperature", "Intensity Factor"]

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        self.sunbrick = G2VSunbrick(self.port)

        # Handle node selection
        self.handle_nodes()

    def handle_nodes(self) -> None:
        """Verify the chosen nodes."""
        nodes = self.node_string
        if nodes.strip().lower() == "all":
            self.nodes = [0]
        else:
            try:
                self.nodes = [int(node.strip()) for node in nodes.split(",")]
            except:
                msg = f"Invalid node format: {nodes}. Use comma separated list or 'All'."
                raise ValueError(msg)

        available_nodes = self.sunbrick.node_list
        # TODO: Check the if
        if any (node not in available_nodes for node in self.nodes):
            msg = f"Unsupported nodes: {self.nodes}. Device supports only {available_nodes}"
            raise ValueError(msg)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # check if the provided channel is supported
        if not self.set_all_channels:
            channel_list = self.sunbrick.channel_list
            if self.channel not in channel_list:
                msg = f"The channel {self.channel} is not supported. Supported channels are: {channel_list}."
                raise ValueError(msg)

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def poweroff(self) -> None:
        """Set the channel value to 0."""
        self.sunbrick.turn_off()

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweepmode == "Intensity":
            if self.set_all_channels:
                self.sunbrick.set_intensity_factor(value=float(self.value))
            else:
                self.set_intensity(channel=self.channel, value=float(self.value))

        elif self.sweepmode == "Spectrum":
            self.set_spectrum(self.value)

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        average_temperature = self.sunbrick.get_avg_temperature()

        if self.set_all_channels:
            intensity = self.sunbrick.get_intensity_factor()
        else:
            intensity = self.sunbrick.get_channel_value(self.channel)

        return [average_temperature, intensity]

    # Wrapped Commands

    def set_intensity(self, channel: int, value: float) -> None:
        """Set the intensity of the specified channel for all nodes of self.node.

        Args:
            channel: The channel number (1-n).
            value: The intensity value in percent (0-100).
        """
        if value < 0.0 or value > 100.0:
            msg = f"The intensity value {value} is not valid. It must be between 0 and 100."
            raise ValueError(msg)

        if self.sunbrick is None:
            msg = "The sunbrick is not connected."
            raise RuntimeError(msg)

        for node in self.nodes:
            ret = self.sunbrick.set_channel_value(channel, value, node)

            if ret is None or ret is False:
                msg = f"Failed to set the intensity of node {node} and channel {channel} to {value}."
                raise RuntimeError(msg)

    def set_spectrum(self, spectrum_file: str) -> None:
        """Set the spectrum of the sunbrick.

        Args:
            spectrum_file: The path to the json file containing the spectrum.
        """
        if not Path(spectrum_file).is_file():
            msg = f"The spectrum file {spectrum_file} does not exist."
            raise ValueError(msg)

        if self.sunbrick:
            self.sunbrick.set_spectrum(spectrum_file)

    def get_identification(self) -> str:
        """Get the sunbrick ID."""
        return self.sunbrick.brick_id
