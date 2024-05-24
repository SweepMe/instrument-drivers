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
# * Instrument: Metrohm Autolab PGSTAT


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the Metrohm Autolab PGSTAT used as LCRmeter."""

    description = "Metrohm Autolab PGSTAT"

    def __init__(self) -> None:
        """Initializes the device class."""
        super().__init__()

        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]
        self.identifier: str = ""
        self.port_string: str = ""

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

    def call(self) -> list[float]:
        """Return ["R", "X", "Frequency", "Voltage bias" or "Voltage level"]."""
        return [self.resistance, self.reactance, self.measured_frequency, self.measured_dc_bias]

    """ here, convenience functions start """

    """ here wrapped functions start """
