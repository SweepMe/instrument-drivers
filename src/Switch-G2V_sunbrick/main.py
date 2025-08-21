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
    Stabilization time: the wait time after setting a new spectrum or intensity to wait until the device is settled.
    """

    description = """
    <h3>G2V Sunbrick Sun Simulator</h3>
    <p>This driver controls the G2V Sunbrick, a programmable LED-based sun simulator.</p>
    <h4>Parameters</h4>
    <ul>
    <li><b>Mode:</b> The driver currently can sweep Intensity, Spectrum, or None.</li>
    <li><b>Nodes:</b> Specify which nodes to control.
        <ul>
            <li>Use a comma-separated list (e.g., <code>1,2,3</code>) to select specific nodes.</li>
            <li>Use <code>0</code> to select all nodes.</li> 
        </ul>
    </li>
    <li><b>Channels:</b> Specify which LED channels to control within the selected nodes.
        <ul>
            <li>Use a comma-separated list (e.g., <code>1,2,3</code>) to select specific channels.</li>
            <li>Use <code>0</code> to select all channels.</li>
        </ul>
    </li>
    <li><b>Stabilization Time:</b> Defines the wait time (in seconds) after setting a new spectrum or intensity before
     the measurement continues, allowing the system to adapt. The recommended stabilization time can differ depending on
      the device and should be tested.</li> </ul>
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
        self.spectrum: Path = Path()

        self.stabilization_time: str | float = 0.5
        self.timestamp_of_last_change: float = 0.

        self.node_string: str = "0"
        self.nodes: list[int] = [0]  # default to all nodes
        self.channels_string: str = "0"
        self.channels: list[int] = [0]  # default to all channels
        self.intensity: str | float = 100

    def update_gui_parameters(self, parameter: dict[str, Any]) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        # Currently (SweepMe! 1.5.7.5), dynamic GUI parameters do not check for changes in the SweepMode parameter
        # TODO: For Intensity mode hide 'Intensity', and for Spectrum mode hide 'Spectrum', 'Nodes', 'Channels'.
        del parameter
        return {
            "SweepMode": ["Intensity", "Spectrum", "None"],
            "Stabilization time in s": "0.5",
            "Spectrum" : Path("my.spectrum"),
            "Nodes" : "0",
            "Channels" : "0",
            "Intensity in %" : "100",
        }

    def apply_gui_parameters(self, parameter: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameter["SweepMode"]

        self.stabilization_time = parameter.get("Stabilization time in s", "0.5")
        self.spectrum = parameter.get("Spectrum", "")
        self.node_string = parameter.get("Nodes", "0")
        self.channels_string = parameter.get("Channels", "0")
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
        try:
            self.stabilization_time = float(self.stabilization_time)
        except ValueError:
            msg = f"Unsupported value for stabilization time: {self.stabilization_time}. Parameter must be float."
            raise ValueError(msg)

        # check if the provided nodes and channels are supported
        if self.sweepmode != "Spectrum":
            self.set_spectrum_and_update_timestamp_of_last_change(str(self.spectrum))
            self.handle_nodes()
            self.handle_channels()

        if self.sweepmode != "Intensity":
            try:
                intensity = float(self.intensity)
            except ValueError as e:
                msg = f"Invalid value for intensity: {self.intensity}. Must be between 0 and 100%."
                raise ValueError(msg) from e
            self.sunbrick.set_intensity_factor(intensity)
            self.update_timestamp_of_last_change()

        if self.timestamp_of_last_change - time.time() < self.stabilization_time:
            self.wait_for_device_to_stabilize()

    def update_timestamp_of_last_change(self) -> None:
        """Set the timestamp of last change to the current timestamp to handle stabilization times."""
        self.timestamp_of_last_change = time.time()

    def handle_nodes(self) -> None:
        """Verify the chosen nodes."""
        nodes = self.node_string
        try:
            self.nodes = [int(node.strip()) for node in nodes.split(",")]
        except ValueError as e:
            msg = f"Invalid node format: {nodes}. Use comma separated list or '0' to select all nodes."
            raise ValueError(msg) from e

        if 0 in self.nodes:
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

        if 0 in self.channels:
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

            self.update_timestamp_of_last_change()

        elif self.sweepmode == "Spectrum":
            self.set_spectrum_and_update_timestamp_of_last_change(self.value)

    def reach(self) -> None:
        """Wait for the device to apply the new parameters."""
        self.wait_for_device_to_stabilize()

    def wait_for_device_to_stabilize(self) -> None:
        """Wait until the stabilization time has passed after changing the last value (spectrum or intensity)."""
        if self.stabilization_time > 0:
            time_since_last_change = time.time() - self.timestamp_of_last_change

            # Split the sleep time in 1s intervals to check every interval if the run has been aborted
            sleep_interval_length = 1

            while time_since_last_change < self.stabilization_time:
                if self.is_run_stopped():
                    break
                stabilization_time_left = self.stabilization_time - time_since_last_change
                # In case the remaining time is <1s, do not wait for the complete 1s
                sleep_time = min(stabilization_time_left, sleep_interval_length)
                time.sleep(sleep_time)

                time_since_last_change = time.time() - self.timestamp_of_last_change

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

    def set_spectrum_and_update_timestamp_of_last_change(self, spectrum_file: str) -> None:
        """Set the spectrum of the sunbrick.

        Args:
            spectrum_file: The path to the json file containing the spectrum.
        """
        if not Path(spectrum_file).is_file():
            msg = f"The spectrum file {spectrum_file} does not exist."
            raise ValueError(msg)

        self.sunbrick.set_spectrum(spectrum_file)
        self.update_timestamp_of_last_change()

    def get_identification(self) -> str:
        """Get the sunbrick ID."""
        return self.sunbrick.brick_id
