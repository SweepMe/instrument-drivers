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
# * Module: Signal
# * Instrument: Rohde&Schwarz RTA

import numpy as np

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the signal generator functions of Rohde&Schwarz RTA Oscilloscope."""

    def __init__(self) -> None:
        """Initialize the Device Class."""
        EmptyDevice.__init__(self)

        self.shortname = "RTA"

        # Communication Parameters
        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP", "USB"]
        self.port_properties = {
            "timeout": 2.0,
        }

        # SweepMe Parameters
        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard SweepMe GUI parameters."""
        return {}

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle the SweepMe GUI parameters."""

    def initialize(self) -> None:
        """Initialize the device."""
        self.port.write("*CLS")

        # do not use "SYST:PRES" as it will destroy all settings which is in conflict with using 'As is'
        print("Scope R&S RTA ID:", self.get_idn())

    def deinitialize(self) -> None:
        """Deinitialize the device."""
        self.port.write("SYST:KLOC OFF")  # unlocks the local control during measurement
        self.read_errors()  # read out the error queue

    def configure(self) -> None:
        """Configure the measurement."""

    def apply(self) -> None:
        """Apply the sweep value."""

    def measure(self) -> None:
        """Start the measurement."""

    def call(self) -> list:
        """Return the measurement result."""
        return [1]

    """ Wrapped commands """

    def read_errors(self) -> None:
        """Reads out all errors from the error queue and prints them to the debug."""
        self.port.write("SYST:ERR:COUN?")
        err_count = self.port.read()
        if int(err_count) > 0:
            self.port.write("SYST:ERR:CODE:ALL?")
            answer = self.port.read()
            for err in answer.split(","):
                print("Scope R&S RTA error:", err)

    def get_idn(self) -> str:
        """Return the identification of the device."""
        self.port.write("*IDN?")
        return self.port.read()











