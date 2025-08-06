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

import pathlib

import time
from pathlib import Path
from typing import Any

from g2vsunbrick import G2VSunbrick
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the G2V sunbrick.

    Nodes are only supported in intensity mode. Channel only makes sense in intensity mode.
    Use comma separated list for specific nodes: 1,2,3 or 0 for all.
    Use comma separated list for specific channels: 1,2,3 or 0 for all.
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "sunbrick"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Temperature"]
        self.units = ["C"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["COM"]

        self.sunbrick: G2VSunbrick | None = None

        # Measurement parameters
        self.sweepmode: str = "Intensity"

        self.node_string: str = "0"
        self.nodes: list[int] = [0]  # default to all nodes
        self.channels_string: str = "0"
        self.channels: list[int] = [0]  # default to all channels
        self.intensity: str | float = 100

    def update_gui_parameters(self, parameter: dict[str, Any]) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        new_parameters = {
            "SweepMode": ["Intensity", "Spectrum", "None"],
        }

        sweepmode = parameter.get("SweepMode", "Intensity")
        if sweepmode == "Intensity":
            new_parameters["Spectrum"] = pathlib.Path("my.spectrum")  # TODO
            new_parameters["Nodes"] = "0"
            new_parameters["Channels"] = "0"
        elif sweepmode == "Spectrum":
            new_parameters["Intensity in %"] = "100"

        return new_parameters

    def apply_gui_parameters(self, parameter: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameter["SweepMode"]

        self.node_string = parameter.get("Nodes", "")
        self.channels_string = parameter.get("Channels", "")
        self.intensity = parameter.get("Intensity in %", "100")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        self.sunbrick = G2VSunbrick(self.port.port)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # check if the provided nodes and channels are supported
        if self.sweepmode == "Intensity":
            self.handle_nodes()
            self.handle_channels()
        elif self.sweepmode == "Spectrum":
            try:
                intensity = float(self.intensity)
            except ValueError as e:
                msg = f"Invalid value for intensity: {self.intensity}. Must be between 0 and 100%."
                raise Exception(msg) from e
            self.sunbrick.set_intensity_factor(intensity)
            # Wait for the new value to be applied
            time.sleep(1)

    def handle_nodes(self) -> None:
        """Verify the chosen nodes."""
        nodes = self.node_string
        try:
            self.nodes = [int(node.strip()) for node in nodes.split(",")]
        except Exception as e:
            msg = f"Invalid node format: {nodes}. Use comma separated list or '0' to select all nodes."
            raise ValueError(msg) from e

        if len(self.nodes) == 0:
            self.nodes = [0]  # default to all nodes
        elif 0 in self.nodes:
            self.nodes = [0]  # If 0 is in the list, set all nodes
        else:
            available_nodes = self.sunbrick.node_list
            for node in self.nodes:
                if node not in available_nodes:
                    msg = f"Unsupported node: {node}. Device supports only {available_nodes}"
                    raise ValueError(msg)

    def handle_channels(self) -> None:
        """Verify the chosen channels."""
        channels = self.channels_string
        try:
            self.channels = [int(channel.strip()) for channel in channels.split(",")]
        except Exception as e:
            msg = f"Invalid channel format: {channels}. Use comma separated list or '0' to select all channels."
            raise ValueError(msg) from e

        if self.channels == 0:
            self.channels = [0]  # default to all channels
        elif 0 in self.channels:
            self.channels = [0]  # If 0 is in the list, set all channels
        else:
            available_channels = self.sunbrick.channel_list
            for channel in self.channels:
                if channel not in available_channels:
                    msg = f"Unsupported channel: {channel}. Device supports only {available_channels}"
                    raise ValueError(msg)

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def poweroff(self) -> None:
        """Set the channel value to 0."""
        self.sunbrick.turn_off()

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweepmode == "Intensity":
            if self.channels == [0]:
                self.sunbrick.set_intensity_factor(value=float(self.value))
            else:
                for channel in self.channels:
                    self.set_intensity(channel=channel, value=float(self.value))

        elif self.sweepmode == "Spectrum":
            self.set_spectrum(self.value)
            # Wait for the new spectrum to be applied
            time.sleep(1)

    def call(self) -> float:
        """Return the average temperature."""
        return self.sunbrick.get_avg_temperature()

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
            status = self.sunbrick.set_spectrum(spectrum_file)
            # todo: check status

    def get_identification(self) -> str:
        """Get the sunbrick ID."""
        return self.sunbrick.brick_id
