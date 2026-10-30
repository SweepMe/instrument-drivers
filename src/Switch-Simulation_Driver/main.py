# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025-2026 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Simulation Driver

from typing import Annotated

from pysweepme.commands import Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Volts = Annotated[float, Unit("V")]


class Device(EmptyDevice):
    """Device class to simulate a switch to turn on a Voltage source."""
    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Simulation"  # short name will be shown in the sequencer

        # Define the variables that can be measured by the device and that are returned by the 'call' function
        self.variables = ["Voltage"]
        self.units = ["V"]
        self.plottype = [True]
        self.savetype = [True]

        # Measurement Parameters
        self.sweepmode: str = "None"
        self.voltage: float = 0.0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V", "None"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameter["SweepMode"]

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweepmode == "Voltage in V":
            self.voltage = self.value

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.voltage

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The commands do not need 'initialize' or 'configure'.
    """

    @command(hazards="Changes the voltage at the connected device at once.")
    def set_voltage(self, voltage: Volts) -> None:
        """Set the voltage in V that the simulated switch passes on."""
        self.voltage = voltage

    @command(returns=("voltage",), reads="setpoint")
    def get_voltage(self) -> Volts:
        """Return the voltage in V that the simulated switch passes on."""
        return float(self.voltage)
