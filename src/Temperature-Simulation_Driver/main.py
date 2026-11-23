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
# * Module: Temperature
# * Instrument: Simulation Temperature Controller

"""SweepMe! driver of a simulated temperature controller."""

from __future__ import annotations

import math
import time
from random import random
from typing import Annotated, Any, Literal

from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

ABSOLUTE_ZERO = -273.15
"""Absolute zero in °C: the setpoint must lie above it."""

START_TEMPERATURE = 25.25
"""Temperature in °C before any setpoint was set."""

Celsius = Annotated[float, Unit("°C")]
SensorMode = Literal["Realistic", "No Noise"]

# Realistic: exponential settle with TIME_CONSTANT plus measurement noise.
# No Noise: linear ramp with RAMP_RATE without noise, fully reproducible.
SENSOR_MODES: list[str] = ["Realistic", "No Noise"]


class Device(EmptyDevice):
    """Device class to implement functionalities of a simulated temperature controller.

    The temperature, the setpoint and the time of the last update are kept in the parameter store under keys that
    contain the port, so that every instance with the same port sees the same simulated controller.
    """

    TIME_CONSTANT = 5.0
    RAMP_RATE = 0.5  # K/s, the deterministic ramp of the 'No Noise' mode

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Simulation"

        self.variables = ["Temperature"]
        self.units = ["°C"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = False
        self.port_string: str = "0"
        self.sensor: str = "Realistic"

    @property
    def temperature(self) -> float:
        """The current simulated temperature in °C."""
        temperature = self.restore_parameter(self.identifier_temp)
        return START_TEMPERATURE if temperature is None else temperature

    @temperature.setter
    def temperature(self, temperature: float) -> None:
        self.store_parameter(self.identifier_temp, temperature)

    @property
    def temperature_setpoint(self) -> float | None:
        """The setpoint in °C, None before one was set."""
        stored: float | None = self.restore_parameter(self.identifier_settemp)
        return stored

    @temperature_setpoint.setter
    def temperature_setpoint(self, temperature_setpoint: float) -> None:
        self.store_parameter(self.identifier_settemp, temperature_setpoint)

    @property
    def last_time(self) -> float | None:
        """The time of the last temperature update, None while the temperature does not move."""
        stored: float | None = self.restore_parameter(self.identifier_time)
        return stored

    @last_time.setter
    def last_time(self, last_time: float | None) -> None:
        self.store_parameter(self.identifier_time, last_time)

    @property
    def identifier(self) -> str:
        """The prefix of the keys of this simulated controller in the parameter store."""
        return f"Temperature-Test_Instrument-{self.port_string}_"

    @property
    def identifier_temp(self) -> str:
        """The key of the temperature in the parameter store."""
        return f"{self.identifier}Temp"

    @property
    def identifier_settemp(self) -> str:
        """The key of the setpoint in the parameter store."""
        return f"{self.identifier}setTemp"

    @property
    def identifier_time(self) -> str:
        """The key of the time of the last update in the parameter store."""
        return f"{self.identifier}time"

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI parameters with their default values."""
        return {
            "SweepMode": ["None", "Temperature"],
            "TemperatureUnit": ["°C"],
            "Port": "0",
            "Sensor": SENSOR_MODES,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the values of the GUI parameters."""
        self.port_string = str(parameters.get("Port", "0"))
        self.sensor = parameters.get("Sensor", "Realistic")

    def initialize(self) -> None:
        """Reset the ramp timer (and, in no-noise mode, the temperature) at the start of each run."""
        # Drop any stale timestamp so the first measure() does not see a huge elapsed time.
        self.last_time = None
        if self.sensor == "No Noise":
            self.temperature = 25.0

    def configure(self) -> None:
        """Check the GUI values; it runs at every start of the branch and after a reconfigure."""
        if self.sensor not in SENSOR_MODES:
            msg = f"Sensor '{self.sensor}' is not supported. Choose one of {SENSOR_MODES}."
            raise ValueError(msg)

    def poweroff(self) -> None:
        """Turn off the device."""
        self.last_time = None

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.temperature_setpoint = float(self.value)
        self.last_time = time.time()

    def measure(self) -> None:
        """Advance the current temperature towards the setpoint based on elapsed wall-clock time."""
        setpoint = self.temperature_setpoint
        last_time = self.last_time
        if not last_time or setpoint is None or setpoint == self.temperature:
            return

        new_time = time.time()
        time_elapsed = new_time - last_time

        if self.sensor == "No Noise":
            # Deterministic linear ramp at RAMP_RATE K/s, clamped at the setpoint.
            # Use the raw elapsed time; rounding it could give a 0 K step and stall the ramp.
            distance = setpoint - self.temperature
            max_step = Device.RAMP_RATE * time_elapsed
            if abs(distance) <= max_step:
                self.temperature = round(setpoint, 2)
            else:
                self.temperature = round(self.temperature + math.copysign(max_step, distance), 2)
        else:
            # Exponential settle with TIME_CONSTANT.
            fraction = math.exp(-time_elapsed / Device.TIME_CONSTANT)
            self.temperature = fraction * self.temperature + (1 - fraction) * setpoint

        self.last_time = new_time

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        if self.sensor == "No Noise":
            return round(self.temperature, 2)
        # add some noise to the temperature
        return self.temperature + 0.005 * (2 * random() - 1)  # noqa: S311

    # check_driver: ignore DC004 - a hook of the Temperature module, which polls it in its own reach
    def measure_temperature(self) -> float:
        """Return the simulated temperature in °C after letting it move towards the setpoint."""
        self.measure()
        return self.call()

    # --- Communication commands, used e.g. by the SweepMe! Instrument Control ---
    #
    # The simulated temperature controller moves the temperature towards the setpoint while it is read. The commands
    # do not need 'initialize' or 'configure'.

    @command
    def set_temperature_setpoint(self, temperature: Annotated[Celsius, Range(ABSOLUTE_ZERO, 1000.0)]) -> None:
        """Set the target temperature in °C, above absolute zero. The temperature then moves towards it."""
        if temperature <= ABSOLUTE_ZERO:
            msg = f"Temperature {temperature} °C must be above {ABSOLUTE_ZERO} °C."
            raise ValueError(msg)
        self.temperature_setpoint = temperature
        self.last_time = time.time()

    @command(returns=("temperature",), reads="setpoint")
    def get_temperature_setpoint(self) -> Celsius:
        """Return the target temperature in °C that was set last."""
        setpoint = self.temperature_setpoint
        if setpoint is None:
            msg = "No setpoint has been set yet. Use 'set_temperature_setpoint' first."
            raise ValueError(msg)
        return float(setpoint)

    @command(returns=("temperature",))
    def get_temperature(self) -> Celsius:
        """Return the current temperature in °C after letting it move towards the setpoint for the elapsed time."""
        return float(self.measure_temperature())

    @command
    def set_sensor_mode(self, sensor_mode: SensorMode) -> None:
        """Set the sensor to 'Realistic' (exponential settling, noise) or 'No Noise' (linear ramp, reproducible)."""
        self.sensor = sensor_mode

    @command(returns=("sensor_mode",), reads="setpoint")
    def get_sensor_mode(self) -> SensorMode:
        """Return the sensor mode: 'Realistic' or 'No Noise'."""
        return self.sensor  # type: ignore[return-value]  # set from the GUI or set_sensor_mode, both one of SensorMode
