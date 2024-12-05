# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution:
# We like to thank GRIP Molecular Technologies, Inc/John Myers-Bangsund, Ph.D.
# for providing the initial version of this driver.

# SweepMe! driver
# * Module: Switch
# * Instrument: Keithley 707B


import re  # For regex / string validation
import time

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
        <p><strong>Usage:</strong></p>
        <ul>
        <li>Enter comma separated configurations, e.g "1101; 1201; 1301".</li>
        <li>Only certain cards have a bank. For cards without a bank, just put 1 for the bank number.</li>
        <li>Open means the relay is open/disconnected. No current will flow through. Closed means the relay is closed/
        connected, and current will flow through.</li>
        <li>In the user manual (707B-901-01 Rev. B / January 2015) page 152 you can find how Matrix card channel 
        specifiers are for this instrument.</li>

        </ul>
        <p>&nbsp;</p>
        <p><strong>Known issues:</strong></p>
        <p>In case SweepBox is used as Sweep value, comma-separated configurations can not be used at the moment as the 
        comma is already used by the SweepBox to split the values to be set.</p>
    """

    def __init__(self) -> None:
        """Set up device parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Keithley 707B"

        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP"]
        self.port_properties = {
            "timeout": 5,
            "EOL": "\r",
        }
        self.port_identifications = ["Keithley Instruments,707B", "Keithley Instruments Inc., Model 707B"]

        self.variables = ["Channels"]
        self.units = ["#"]
        self.plottype = [False]
        self.savetype = [True]

        # Measurement parameters
        self.sweepmode: str = "Channels"
        self.switch_settling_time_s: float = 0.004

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Channels"],
            "Switch settling time in ms": 20,  # 4 ms switching time for the 3730 latching electromechanical relays
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.device = parameter["Device"]
        self.switch_settling_time_s = float(parameter["Switch settling time in ms"]) / 1000
        self.sweepmode = parameter["SweepMode"]

    def initialize(self) -> None:
        """Initialize the device."""
        self.open_all()
        self.clear_errorqueue()
        self.clear_dataqueue()
        self.reset_channels()

    def apply(self) -> None:
        """Set new relay configuration."""
        self.open_all()

        channels = str(self.value)
        if bool(re.compile(r"[^a-zA-Z0-9\,\;\:\ ]").search(channels)):
            msg = ("Channel list contains unallowed characters. Only digits, commas, semicolons, colons, or spaces are "
                   "allowed. Some cards use letters.")
            raise ValueError(msg)

        self.exclusiveclose_channel(channels)

    def unconfigure(self) -> None:
        """Restore the initial state of the device."""
        self.clear_errorqueue()
        self.clear_dataqueue()
        self.open_all()

    def reach(self) -> None:
        """Wait for the switch to settle. Could be done with OPC command instead."""
        time.sleep(self.switch_settling_time_s)

    def call(self) -> str:
        """Return the applied state of the matrix as string."""
        return self.value

    """ here, convenience functions start """

    def get_identification(self) -> str:
        """Get the identification string of the device."""
        self.port.write("*IDN?")
        return self.port.read()

    def get_operation_complete(self) -> str:
        """Get the operation complete status of the device."""
        self.port.write("*OPC?")
        return self.port.read()

    def open_all(self) -> None:
        """This function opens all relays."""
        self.port.write('channel.open("allslots")')

    def exclusiveclose_channel(self, channels_to_close: str) -> None:
        """This function closes given channel string."""
        self.port.write('channel.close("%s")' % channels_to_close)

    def open_channel(self, channels_to_open: str) -> None:
        """This function opens given channel string."""
        self.port.write('channel.open("%s")' % channels_to_open)

    def get_closed_channels(self) -> str:
        """Return the closed channels."""
        self.port.write('print(channel.getclose("allslots"))')
        return self.port.read()

    def check_channels(self, channel: str) -> str:
        """Return the state of the given channel."""
        self.port.write('print(channel.getstate("%s"))' % channel)
        return self.port.read()

    def reset_channels(self) -> None:
        """Reset all channels."""
        self.port.write('channel.reset("allslots")')

    def clear_errorqueue(self) -> None:
        """Clear the error queue."""
        self.port.write("errorqueue.clear()")

    def clear_dataqueue(self) -> None:
        """Clear the data queue."""
        self.port.write("dataqueue.clear()")

    def beep(self) -> None:
        """Beep the device."""
        self.port.write("beeper.enable = beeper.ON")
        self.port.write("beeper.beep(2, 2400)")
