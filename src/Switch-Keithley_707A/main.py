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
        <li>Enter comma separated configurations to close a crosspoint, e.g "A1,A4,B14,C12".</li>
        <li>Only certain cards have a bank. For cards without a bank, just put 1 for the bank number.</li>
        <li>Open means the relay is open/disconnected. No current will flow through. Closed means the relay is closed/connected, and current will flow through.</li>
        <li>All crosspoints will be opened before setting a new value.</li>

        </ul>
        <p>&nbsp;</p>
        <p><strong>Known issues:</strong></p>
        <p>In case SweepBox is used as Sweep value, comma-separated configurations can not be used at the moment as the comma is already used by the SweepBox to split the values to be set.</p>
    """

    def __init__(self) -> None:
        """Set up device parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Keithley 707A"

        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP"]
        self.port_properties = {
            "timeout": 5,
            "EOL": "\r",
        }
        self.port_identifications = ["Keithley Instruments,707B", "Keithley Instruments Inc., Model 707B"]
        self.switch_settling_time_s = 0.004

        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Channels"],
            "Switch settling time in ms": 20,  # 4 ms switching time for the 3730 latching electromechanical relays
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.switch_settling_time_s = int(parameter["Switch settling time in ms"])
        self.sweepmode = parameter["SweepMode"]

    def initialize(self) -> None:
        """Initialize the device."""
        # Set Trigger on X
        self.port.write("T4X")

    def configure(self) -> None:
        """Set the switch settling time."""
        self.set_settling_time(self.switch_settling_time_s)
        self.clear_all_relays()

    def apply(self) -> None:
        """Open/Close the given cross points."""
        # TODO: Should the complete setup be cleared before applying the new setup?
        self.clear_all_relays()

        value = str(self.value)
        # TODO: check if value is semicolon-separated list of multiple channels
        # TODO: If more than 25 channels are given, split the list and apply in multiple steps
        self.close_crosspoints_by_string(value)

        # TODO: Other SweepModes needed?
        #  Maybe one where crosspoints are not reset but rather building on the previous setup

    def unconfigure(self) -> None:
        """Open all channels."""
        self.clear_all_relays()

    def call(self) -> None:
        """TODO: Return values?"""
        # U2 command

    """ Wrapped Functions """

    def clear_all_relays(self) -> None:
        """Open all crosspoint relays."""
        self.port.write("P0X")

    def close_crosspoints_by_string(self, command: str) -> None:
        """Enable closing multiple crosspoints at once when given as comma-seperated string like A8,C7,C12."""
        self.port.write(f"C{command}X")

    def close_crosspoint(self, row: str, column: str | int) -> None:
        """Close a crosspoint at a given row and column."""
        command = f"C{row}{column}X"
        self.port.write(command)

    def open_crosspoint(self, row: str, column: str | int) -> None:
        """Open a crosspoint at a given row and column."""
        command = f"N{row}{column}X"
        self.port.write(command)

    def set_settling_time(self, settling_time_ms: int) -> None:
        """Set the settling time for the switch."""
        self.port.write(f"S{int(settling_time_ms)}X")
