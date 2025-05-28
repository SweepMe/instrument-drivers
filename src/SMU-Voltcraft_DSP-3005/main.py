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
# Contribution: We like to thank Tjorben Matthes for providing the initial version of this driver.
#
# SweepMe! driver
# * Module: SMU
# * Instrument: Voltcraft DSP 3005

from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Voltcraft DSP 3005 SMU. This driver is used to control the device and read measurements."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Voltcraft3005"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 0.5,
            "EOL": "\r\n",
            "baudrate": 115200,
        }

        self.commands = {
            "Voltage [V]": "VSET",  # remains for compatibility reasons
            "Current [A]": "ISET",  # remains for compatibility reasons
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
        }
        self.source: str = "Voltage in V"  # default source
        self.protection: float = 0.3  # default protection value
        self.voltage: float = 0.0  # measured voltage
        self.current: float = 0.0  # measured current

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
                "SweepMode": ["Voltage in V", "Current in A"],
                "RouteOut": ["Front"],
                "Compliance": 0.3,
                }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.source = parameter["SweepMode"]
        self.protection = float(parameter["Compliance"])

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.port.write("*RST")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.source.startswith("Voltage"):
            self.port.write(f"CURR {self.protection:1.2f}")
        elif self.source.startswith("Current"):
            self.port.write(f"VOLT {self.protection:1.2f}")

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.port.write("OUTP ON")

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.port.write("OUTP OFF")

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.port.write(self.commands[self.source] + f" {float(self.value):1.2f}")

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        self.port.write("MEAS:ALL?")

    def read_result(self) -> None:
        """Read the measured data from a buffer that was requested during 'measure'."""
        voltage, current = self.port.read().split(",")
        self.voltage, self.current = float(voltage), float(current)

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.voltage, self.current]

    def get_identification(self) -> str:
        """Get the identification of the device."""
        self.port.write("*IDN?")
        return self.port.read()
