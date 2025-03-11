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
# SweepMe! device class
# * Type: Temperature
# * Instrument: Simulation Temperature Controller

import math
import time
from random import random
from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class to implement functionalities of a simulated temperature controller."""
    TIME_CONSTANT = 5.0

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Simulation"

        self.variables = ["Temperature"]
        self.units = ["°C"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = False

    @property
    def temperature(self) -> float:
        """Returns the current temperature from the parameter store."""
        temperature = self.restore_parameter(self.identifier_temp)
        return temperature or 25.25

    @temperature.setter
    def temperature(self, value: float) -> None:
        self.store_parameter(self.identifier_temp, value)

    @property
    def set_temperature(self) -> float:
        temperature = self.restore_parameter(self.identifier_settemp)
        return temperature

    @set_temperature.setter
    def set_temperature(self, value: float) -> None:
        self.store_parameter(self.identifier_settemp, value)

    @property
    def last_time(self) -> float:
        last_time = self.restore_parameter(self.identifier_time)
        return last_time

    @last_time.setter
    def last_time(self, value: float) -> None:
        self.store_parameter(self.identifier_time, value)

    @property
    def identifier(self) -> str:
        return f"Temperature-Test_Instrument-{self.port}_"

    @property
    def identifier_temp(self) -> str:
        return f"{self.identifier}Temp"

    @property
    def identifier_settemp(self) -> str:
        return f"{self.identifier}setTemp"

    @property
    def identifier_time(self) -> str:
        return f"{self.identifier}time"

    def set_GUIparameter(self) -> dict[str, Any]:
        return {
            "SweepMode": ["None", "Temperature"],
            "TemperatureUnit": ["°C"],
            "Port": "0"
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port = parameter["Port"]

    def poweroff(self) -> None:
        """Turn off the device."""
        self.last_time = None

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.set_temperature = float(self.value)
        self.last_time = time.time()

    def measure(self) -> None:
        """Calculate the current temperature based on the elapsed time and the time constant."""
        if self.last_time and self.set_temperature and self.set_temperature != self.temperature:
            new_time = time.time()
            time_elapsed = new_time - self.last_time
            fraction = math.exp(-time_elapsed / Device.TIME_CONSTANT)
            self.temperature = fraction * self.temperature + (1 - fraction) * self.set_temperature
            self.last_time = new_time

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        # add some noise to the temperature
        return self.temperature + 0.005 * (2 * random() - 1)

    def measure_temperature(self) -> float:
        """Returns the calculated temperature."""
        self.measure()
        return self.call()
