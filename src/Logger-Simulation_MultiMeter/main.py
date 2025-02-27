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

# SweepMe! driver
# * Module: Logger
# * Instrument: Simulation MultiMeter

import random

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class to implement functionalities of a simulation multi meter."""
    description = """
                    <h3>Simulated Multi Meter</h3>
                    <p>Setup:</p>
                    <ul>
                    <li>Choose comma-separated list of channels (maximum 4) to read out.</li>
                    </ul>
                    """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Simulation"  # short name will be shown in the sequencer

        # Define the variables that can be measured by the device and that are returned by the 'call' function
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        # Measurement Parameters
        self.voltage_channels: list[int] = []
        self.current_channels: list[int] = []

    def set_GUIparameter(self) -> dict[str, str]:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Voltage Channels": "1,2",
            "Current Channels": "3,4",
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.variables = []
        self.units = []
        self.voltage_channels = list(map(int, parameter["Voltage Channels"].split(",")))
        for channel in self.voltage_channels:
            self.variables.append(f"Voltage CH{channel}")
            self.units.append("V")

        self.current_channels = list(map(int, parameter["Current Channels"].split(",")))
        for channel in self.current_channels:
            self.variables.append(f"Current CH{channel}")
            self.units.append("A")

        # Update plottype and savetype
        self.plottype = []
        self.savetype = []
        for _ in self.variables:
            self.plottype.append(True)
            self.savetype.append(True)

    def find_ports(self) -> list[str]:
        """This function is called whenever the user presses 'Find ports' button.

        Return a list of strings with possible port items.
        """
        return ["Port1", "Port2"]

    def call(self) -> [float, float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        simulated_values = []
        for channel in self.voltage_channels:
            simulated_values.append(self.simulate_voltage(channel))
        for channel in self.current_channels:
            simulated_values.append(self.simulate_current(channel))

        return simulated_values

    @staticmethod
    def simulate_voltage(channel: int) -> float:
        """Simulate the voltage measurement."""
        voltage = channel * 1.0
        # 50mV noise
        noise = random.uniform(-0.05, 0.05)  # noqa: S311
        return voltage + noise

    @staticmethod
    def simulate_current(channel: int) -> float:
        """Simulate the current measurement."""
        current = channel * 0.1
        # 5mA noise
        noise = random.uniform(-0.005, 0.005)  # noqa: S311
        return current + noise
