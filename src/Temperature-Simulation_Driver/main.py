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
#
# SweepMe! device class
# * Type: Temperature
# * Instrument: Simulation Temperature Controller

import math
import time
from random import random
from typing import Annotated, Any, Literal

from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

ABSOLUTE_ZERO = -273.15
"""Absolute zero in °C: the setpoint must lie above it."""

Celsius = Annotated[float, Unit("°C")]
SensorMode = Literal["Realistic", "No Noise"]


class Device(EmptyDevice):
    """Device class to implement functionalities of a simulated temperature controller."""
    TIME_CONSTANT = 5.0
    RAMP_RATE = 0.5  # K/s — deterministic ramp used in 'No Noise' mode

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Simulation"

        self.variables = ["Temperature"]
        self.units = ["°C"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = False
        self.sensor: str = "Realistic"  #
        """
        Realistic: exponential settle with TIME_CONSTANT plus measurement noise 
        No Noise:  jump straight to the setpoint and skip the noise. fast and fully reproducible.
        """

    @property
    def temperature(self) -> float:
        """Returns the current temperature from the parameter store."""
        temperature = self.restore_parameter(self.identifier_temp)
        return temperature or 25.25

    @temperature.setter
    def temperature(self, value: float) -> None:
        self.store_parameter(self.identifier_temp, value)

    # check_driver: ignore DC004 - a property holding the setpoint across instances, not a command
    @property
    def set_temperature(self) -> float:
        temperature = self.restore_parameter(self.identifier_settemp)
        return temperature

    # check_driver: ignore DC004 - the setter of the set_temperature property, not a command
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
            "Port": "0",
            "Sensor": ["Realistic", "No Noise"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port = parameter["Port"]
        self.sensor = parameter.get("Sensor", "Realistic")

    def initialize(self) -> None:
        """Reset the ramp timer (and, in no-noise mode, the temperature) at the start of each run."""
        # Drop any stale timestamp so the first measure() does not see a huge elapsed time.
        self.last_time = None
        if self.sensor == "No Noise":
            self.temperature = 25.0

    def poweroff(self) -> None:
        """Turn off the device."""
        self.last_time = None

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.set_temperature = float(self.value)
        self.last_time = time.time()

    def measure(self) -> None:
        """Advance the current temperature towards the setpoint based on elapsed wall-clock time."""
        if not self.last_time or self.set_temperature is None or self.set_temperature == self.temperature:
            return

        new_time = time.time()
        time_elapsed = new_time - self.last_time

        if self.sensor == "No Noise":
            # Deterministic linear ramp at RAMP_RATE K/s — clamped at the setpoint.
            # Use the raw elapsed time; rounding it could give a 0 K step and stall the ramp.
            distance = self.set_temperature - self.temperature
            max_step = Device.RAMP_RATE * time_elapsed
            if abs(distance) <= max_step:
                self.temperature = round(self.set_temperature, 2)
            else:
                self.temperature = round(self.temperature + math.copysign(max_step, distance), 2)
        else:
            # Exponential settle with TIME_CONSTANT.
            fraction = math.exp(-time_elapsed / Device.TIME_CONSTANT)
            self.temperature = fraction * self.temperature + (1 - fraction) * self.set_temperature

        self.last_time = new_time

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        if self.sensor == "No Noise":
            return round(self.temperature, 2)
        # add some noise to the temperature
        return self.temperature + 0.005 * (2 * random() - 1)

    # check_driver: ignore DC004 - the simulation model used by call(), not a command
    def measure_temperature(self) -> float:
        """Returns the calculated temperature."""
        self.measure()
        return self.call()

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The simulated temperature controller moves the temperature towards the setpoint while it is read. The commands do
    not need 'initialize' or 'configure'.
    """

    @command(hazards="Heats or cools the connected sample.")
    def set_temperature_setpoint(self, temperature: Annotated[Celsius, Range(ABSOLUTE_ZERO, 1000.0)]) -> None:
        """Set the target temperature in °C, above absolute zero. The temperature then moves towards it."""
        if temperature <= ABSOLUTE_ZERO:
            msg = f"Temperature {temperature} °C must be above {ABSOLUTE_ZERO} °C."
            raise ValueError(msg)
        self.set_temperature = temperature
        self.last_time = time.time()

    @command(returns=("temperature",), reads="setpoint")
    def get_temperature_setpoint(self) -> Celsius:
        """Return the target temperature in °C that was set last."""
        setpoint = self.set_temperature
        if setpoint is None:
            msg = "No setpoint has been set yet. Use 'set_temperature_setpoint' first."
            raise ValueError(msg)
        return float(setpoint)

    @command(returns=("temperature",))
    def get_temperature(self) -> Celsius:
        """Return the current temperature in °C after letting it move towards the setpoint for the elapsed time."""
        return float(self.measure_temperature())

    @command
    def set_sensor_mode(self, sensor: SensorMode) -> None:
        """Set the sensor to 'Realistic' (exponential settling, noise) or 'No Noise' (linear ramp, reproducible)."""
        self.sensor = sensor
