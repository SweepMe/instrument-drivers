# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# * Module: Switch
# * Instrument: Keithley 707A

from __future__ import annotations

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
        <p><strong>Usage:</strong></p>
        <ul>
        <li>Enter comma or semicolon separated configurations to close a crosspoint, e.g "A1,A4,C12" or "C3;D4".</li>
        <li>Open means the relay is open/disconnected. No current will flow through. Closed means the relay is closed/
        connected, and current will flow through.</li>
        <li>All crosspoints will be opened before setting a new value.</li>

        </ul>
        <p>&nbsp;</p>
        <p><strong>Known issues:</strong></p>
        <p>In case SweepBox is used as Sweep value, comma-separated configurations can not be used at the moment as the 
        comma is already used by the SweepBox to split the values to be set.</p>
    """

    def __init__(self) -> None:
        """Set up device parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Keithley 707A"

        self.port_manager = True
        self.port_types = ["GPIB"]
        self.port_properties = {
            "timeout": 5,
            "EOL": "\r",
        }

        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        #     Measurement parameters
        self.sweepmode: str = "Channels"

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Channels"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameter["SweepMode"]

    def initialize(self) -> None:
        """Set Trigger on X."""
        self.port.write("T4X")

    def configure(self) -> None:
        """Clear all crosspoints."""
        self.open_all_crosspoints()

    def apply(self) -> None:
        """Open/Close the given cross points.

        Currently, all crosspoints are opened before setting the new value. Another mode could be implemented where the
        crosspoints are not reset but rather building on the previous setup.
        """
        self.open_all_crosspoints()

        crosspoint_string = self.value.replace(";", ",")
        self.close_crosspoints_by_string(crosspoint_string)

    def unconfigure(self) -> None:
        """Open all channels."""
        self.open_all_crosspoints()

    def call(self) -> None:
        """Could return the current state of the matrix as a string via the U2X command."""

    """ Wrapped Functions """

    def open_all_crosspoints(self) -> None:
        """Open all crosspoint relays."""
        self.port.write("P0X")

    def close_crosspoints_by_string(self, command: str) -> None:
        """Enable closing multiple crosspoints at once when given as comma-separated string like A8,C7,C12."""
        # The device can only handle 25 crosspoints at once
        max_commands = 25
        if len(command.split(",")) > max_commands:
            crosspoints = command.split(",")

            for i in range(0, len(crosspoints), max_commands):
                bundled_crosspoints = ",".join(crosspoints[i:i+max_commands])
                self.port.write(f"C{bundled_crosspoints}X")

        else:
            self.port.write(f"C{command}X")

    """Currently unused functions."""

    def open_crosspoint(self, row: str, column: str | int) -> None:
        """Open a crosspoint at a given row and column."""
        command = f"N{row}{column}X"
        self.port.write(command)

    def close_crosspoint(self, row: str, column: str | int) -> None:
        """Close a crosspoint at a given row and column."""
        command = f"C{row}{column}X"
        self.port.write(command)

    def set_settling_time(self, settling_time_ms: int) -> None:
        """Set the settling time for the switch."""
        self.port.write(f"S{int(settling_time_ms)}X")
