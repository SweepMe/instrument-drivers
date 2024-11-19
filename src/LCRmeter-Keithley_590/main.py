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
# * Module: LCRmeter
# * Instrument: Keithley 590

from __future__ import annotations

import os

from pysweepme import FolderManager
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the Keithley 590 LCRmeter."""

    description = ""

    def __init__(self) -> None:
        """Initializes the device class."""
        super().__init__()

        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]
        self.identifier: str = ""
        self.port_string: str = ""

        self.ranges = {
            "Auto": "R0",
            "2pF": "2pF",  # only for 100kHz
            "20pF": "20pF",
            "200pF": "200pF",
            "2nF": "2nF",
            "20nF": "20nF",
        }

        self.frequencies = {
            "100kHz": "100kHz",
            "1MHz": "1MHz",
        }

    def find_ports(self) -> list[str]:
        """Return standard address."""
        return ["15"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set initial GUI parameter in SweepMe!."""
        return {
            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "ValueRMS": 0.02,
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            "Integration": list(self.speeds),
            "Trigger": ["Internal"],
            "TriggerDelay": "0.1",
            "Range": list(self.current_ranges),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Update parameter from SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.value_level_rms = float(parameter["ValueRMS"])
        self.value_bias = float(parameter["ValueBias"])
        self.frequency = float(parameter["Frequency"])
        self.integration = self.speeds[parameter["Integration"]]

        self.trigger_type = parameter["Trigger"]  # currently unused
        self.trigger_delay = float(parameter["TriggerDelay"])
        self.measure_range = parameter["Range"]

        # Only use Resistance and reactance measurement
        self.operating_mode = "RjX"

    def connect(self) -> None:
        """Connect to the Keithley 4200-SCS LCRmeter."""

    def initialize(self) -> None:
        """Initialize the Keithley 4200-SCS LCRmeter."""

    def deinitialize(self) -> None:
        """Reset device and close connection."""

    def configure(self) -> None:
        """Set bias and measurement parameters with start values from GUI."""

    def unconfigure(self) -> None:
        """Reset device."""

    def apply(self) -> None:
        """Apply settings."""

    def measure(self) -> None:
        """Retrieve Impedance results from device."""
        # Only measurement mode RjX is used
        self.resistance, self.reactance = self.measure_impedance()

        self.measured_frequency = self.measure_frequency()
        self.measured_dc_bias = self.measure_dc_bias()

    def call(self) -> list[float]:
        """Return ["R", "X", "Frequency", "Voltage bias" or "Voltage level"]."""
        return [self.resistance, self.reactance, self.measured_frequency, self.measured_dc_bias]

    """ here, convenience functions start """

    def set_range(self, range: str) -> None:
        """Set the measurement range."""


        self.port.write("R0")
        return "R0"
