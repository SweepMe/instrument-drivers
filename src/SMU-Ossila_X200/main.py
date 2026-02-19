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
            "Auto": 0,
            "200 mA": 1,
            "20 mA": 2,
            "2 mA": 3,
            "200 µA": 4,
            "20 µA": 5,
        }
        self.current_range_limits = {
            1: 0.2,  # 200 mA
            2: 0.02,  # 20 mA
            3: 0.002,  # 2 mA
            4: 0.0002,  # 200 µA
            5: 0.00002,  # 20 µA
        }
        """The current range limits are used for auto-ranging. If the measured current is above 90% of the current range
         limit, the driver will switch to the next higher range. If the measured current is below 10% of the current 
         range limit, the driver will switch to the next lower range. The auto-ranging will stop if the current is 
         within 10-90% of the current range limit or if the minimum or maximum range is reached.
         """

        self.current_range_index: int = 1
        self.auto_range: bool = False

        self.voltage_ranges = {
            "333 µV precision (Sourcing mode)": 0,
            "100 µV (Measure mode)": 1,
            "50 µV (Measure mode)": 2,
        }
        self.voltage_range_index: int = 0

        self.high_impedance_mode: bool = False

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
            # "RangeVoltage": list(self.voltage_ranges.keys()),  # no command found to set the voltage range, so we keep it fixed for now
            "ADC 2x Mode": False,
            "High impedance mode": False,
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

        self.current_range_index = self.current_ranges.get(parameters.get("Range", "200 mA"), -1)  # if the range is invalid, use an invalid index to raise an error later
        self.auto_range = self.current_range_index == 0  # auto range is enabled if the index is 0

        # self.voltage_range_index = self.voltage_ranges.get(parameters.get("RangeVoltage", "333 µV precision (Sourcing mode)"), 0)
        self.compliance = parameters.get("Compliance", "1e-3")

        self.high_impedance_mode = parameters.get("High impedance mode", False)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # Do not call 'reset' here, because it performs a hard reset of the device which also disconnects the communication
        # self.port.write("reset")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        try:
            self.average = int(self.average)
        except ValueError:
            msg = f"Invalid value for Average: {self.average}. Must be an integer."
            raise ValueError(msg)
        self.set_average(self.average)

        self.set_oversample_rate(self.speed)

        if self.auto_range:
            self.current_range_index = 5  # start with the lowest range for auto-ranging

        self.set_current_range(self.current_range_index)

        if self.sweep_mode.startswith("Voltage"):
            try:
                self.compliance = float(self.compliance)
            except ValueError:
                msg = f"Invalid value for Compliance: {self.compliance}. Must be a number."
                raise ValueError(msg)
            self.set_current_limit(self.compliance)

        if self.high_impedance_mode:
            self.port.write(f"{self.channel} set hiz 1")
        else:
            self.port.write(f"{self.channel} set hiz 0")

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
        if self.auto_range:
            self.set_current_range(5)  # start with the lowest range for auto-ranging
            voltage, current = self.get_voltage_and_current()

            while True:
                if self.is_run_stopped():
                    break

                # if the current is above 90% of the current range limit, switch to the next higher range
                if abs(current) > 0.9 * self.current_range_limits[self.current_range_index]:
                    if self.current_range_index > 1:
                        self.current_range_index -= 1
                        self.set_current_range(self.current_range_index)
                        voltage, current = self.get_voltage_and_current()
                    else:
                        # the maximum range is reached, stop auto-ranging
                        break

                else:
                    # Value is within the current range limit, stop auto-ranging
                    break
        else:
            voltage, current = self.get_voltage_and_current()

        return [voltage, current]

    def get_voltage_and_current(self) -> tuple[float, float]:
        """Get the voltage and current measurement results as a tuple."""
        response = self.port.query(f"{self.channel} measure 1")

        try:
            voltage, current = response.split(",")
            voltage = float(voltage.strip("["))
            current = float(current.strip("]"))
        except ValueError as e:
            msg = f"Invalid response from the device: {response}. Expected format: '[voltage,current]'. Error: {e}"
            raise ValueError(msg)

        return voltage, current

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
        """Set the current range index for the measurement, which determines maximum measurable current, accuracy, and
        resolution. The range index can be 1-5. See manual 5.2.4 for reference.
        """
        if not (1 <= measure_range_index <= 5):
            msg = f"Invalid index value for current Range: {measure_range_index}. Must be an integer between 1 and 5."
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

    def get_identification(self) -> str:
        """Get the device identification."""
        return self.port.query("version")
