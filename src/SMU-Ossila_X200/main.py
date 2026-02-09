# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: SMU
# * Instrument: Ossila X200

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Ossila X200."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "X200"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["COM", "USB", "TCPIP"]

        self.channel = "smu1"  # or smu2

        # Measurement parameters
        self.sweep_mode: str = "None"
        self.compliance: float = 1e-3  # in A

        self.speed_dict = {
            "64": 0,
            "128": 1,
            "256": 2,
            "512": 3,
            "1024": 4,
            "2048": 5,
            "4096": 6,
            "8192": 7,
            "16384": 8,
            "32768": 9,
        }
        self.speed: int = 0  # index of the speed in the speed_dict
        self.average: int = 1

        self.current_ranges = {
            "200 mA": 1,
            "20 mA": 2,
            "2 mA": 3,
            "200 µA": 4,
            "20 µA": 5,
        }
        self.current_range_index: int = 1

        self.voltage_ranges = {
            "333 µV precision (Sourcing mode)": 0,
            "100 µV (Measure mode)": 1,
            "50 µV (Measure mode)": 2,
        }
        self.voltage_range_index: int = 0

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ['None', 'Voltage in V'],
            "Channel": ["SMU1", "SMU2"],
            "Compliance": 1e-3,  # always in A
            "Average": 1,
            "Speed": list(self.speed_dict.keys()),
            "Range": list(self.current_ranges.keys()),
            # "RangeVoltage": list(self.voltage_ranges.keys())  # only for non-sourcing mode
            "ADC 2x Mode": False,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.channel = parameters.get("Channel", "SMU1").lower()
        self.average = parameters.get("Average", 1)

        self.speed = self.speed_dict.get(parameters.get("Speed", "64"), 0)
        if parameters.get("ADC 2x Mode", False):
            self.speed += 10  # if ADC 2x mode is enabled, add 10 to the OSR index according to the manual

        self.current_range_index = self.current_ranges.get(parameters.get("Range", "200 mA"), 0)
        self.voltage_range_index = self.voltage_ranges.get(parameters.get("RangeVoltage", "333 µV precision (Sourcing mode)"), 0)
        self.compliance = float(parameters.get("Compliance", 1e-3))

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        version = self.port.query("version")
        print(f"Device version: {version}")

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.port.write("reset")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        try:
            self.average = int(self.average)
        except ValueError:
            msg = f"Invalid value for Average: {self.average}. Must be an integer."
            raise ValueError(msg)
        self.set_average(self.average)

        self.set_oversample_rate(self.speed)
        self.set_voltage_range(self.voltage_range_index)
        self.set_current_range(self.current_range_index)

        if self.sweep_mode.startswith("Voltage"):
            try:
                self.compliance = float(self.compliance)
            except ValueError:
                msg = f"Invalid value for Compliance: {self.compliance}. Must be a number."
                raise ValueError(msg)
            self.set_current_limit(self.compliance)

    def poweron(self) -> None:
        """Enable the device."""
        self.port.write(f"{self.channel} set enabled 1")

    def poweroff(self) -> None:
        """Disable the device."""
        self.port.write(f"{self.channel} set enabled 0")

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweep_mode.startswith("Voltage"):
            self.set_voltage(float(self.value))

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        response = self.port.query(f"{self.channel} measure")
        voltage, current = response.split(",")
        voltage = float(voltage)
        current = float(current)

        return [voltage, current]

    def set_average(self, average: int) -> None:
        """Set the average value for the measurement."""
        self.port.write(f"{self.channel} set filter {average}")

    def set_current_limit(self, current_limit: float) -> None:
        """Set the positive and negative current limit (compliance) in A for the measurement. Default: 0.225 A."""
        self.port.write(f"{self.channel} set limiti {current_limit}")

    def set_voltage_limit(self, voltage_limit: float) -> None:
        """Set the positive and negative voltage limit (compliance) in V for the measurement. Default: 200 V."""
        self.port.write(f"{self.channel} set limitv {voltage_limit}")

    def set_current_range(self, measure_range_index: int) -> None:
        """Set the current range index for the measurement, which determines maximum measurable current, accuracy, and resolution. The range index can be 1-9. See manual 5.2.3 for reference."""
        try:
            measure_range_index = int(measure_range_index)
        except ValueError:
            msg = f"Invalid value for current Range: {measure_range_index}. Must be an integer between 1 and 9."
            raise ValueError(msg)

        if not (1 <= measure_range_index <= 9):
            msg = f"Invalid value for current Range: {measure_range_index}. Must be an integer between 1 and 9."
            raise ValueError(msg)

        self.port.write(f"{self.channel} set range {measure_range_index}")

    def set_oversample_rate(self, oversample_rate_index: int) -> None:
        """Set the oversample rate for the measurement. The OSR index can be 0-19. See manual 5.2.2 for reference."""
        try:
            oversample_rate_index = int(oversample_rate_index)
        except ValueError:
            msg = f"Invalid value for Speed: {oversample_rate_index}. Must be an integer between 0 and 19."
            raise ValueError(msg)

        if not (0 <= oversample_rate_index <= 19):
            msg = f"Invalid value for Speed: {oversample_rate_index}. Must be an integer between 0 and 19."
            raise ValueError(msg)

        self.port.write(f"{self.channel} set osr {oversample_rate_index}")

    def set_voltage(self, voltage: float) -> None:
        """Set the output voltage."""
        self.port.write(f"{self.channel} set voltage {voltage}")
