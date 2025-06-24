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
# * Module: Temperature
# * Instrument: Velox

from __future__ import annotations

import time
from enum import Enum

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()
import velox


class Sensor(Enum):
    """Enum class to define available temperature sensors."""
    MAIN = 0
    PT100A = 1
    PT100B = 2


class TemperatureMode(Enum):
    """Enum class to define the temperature mode."""
    SET_TEMPERATURE = "Temperature"
    AUTOMATION_TEMPERATURE = "Ramping using Autonomous Assistant"
    REALIGN_TEMPERATURE = "Ramping using ReAlign"


class Status(Enum):
    """Enum class to define the status of the thermal chuck."""
    UNKNOWN = 0
    HEATING = 1
    COOLING = 2
    AT_TEMPERATURE = 4
    HOLD_READY = 8
    HOLD_MOVE = 16
    POWER_SAVE = 32
    SOAKING = 64
    INTERMEDIATE = 128


class Device(EmptyDevice):
    """Driver class for Velox Temperature Control."""

    description = """
    <h3>Velox Temperature</h3>
    <p>This driver controls the temperature control functions of FormFactor Velox wafer probers.</p>
    <h4>Setup</h4>
    <ul>
        <li>Requires Velox Installation</li>
    </ul>
    <h4>Parameters</h4>
    <ul>
        <li>Port: Use 'localhost' when running SweepMe! on the same PC as Velox. For TCP/IP remote control, enter
         the Velox PCs IP address either as blank string "192.168.XXX.XXX" or containing a specific port 
         "IP:xxx.xxx.xxx.xxx; Port:xxxx" </li>
         <li>Reach Temperature: This driver can only be used with the "Reach Temperature" mode turned on, meaning the 
         device communication is blocked during heating or cooling.</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initialize measurement and analysis parameter."""
        EmptyDevice.__init__(self)

        self.shortname = "Velox"
        self.variables = ["Temperature"]
        self.units = [""]
        self.plottype = [True]
        self.savetype = [True]

        # Device Communication
        self.ip_address: str = "localhost"
        self.target_socket: int = 1412
        self.msg_server: velox.MessageServerInterface | None = None

        # Measurement Parameter
        self.sweep_mode: TemperatureMode = TemperatureMode.SET_TEMPERATURE
        self.use_reach: bool = True
        self.temperature_units = {
            "C": "C",
            "F": "F",
            "K": "K",
        }
        self.temperature_unit: str = "C"
        self.measure_temperature: bool = True
        self.sensor: Sensor = Sensor.MAIN

    def __del__(self) -> None:
        """Exit Velox Communication before instance is deleted."""
        self.disconnect_from_velox()

    @staticmethod
    def find_ports() -> list[str]:
        """Return a placeholder to enter an IP address and socket."""
        return ["localhost", "IP:xxx.xxx.xxx.xxx; Port:xxxx"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Define standard GUI parameter values."""
        return {
            "SweepMode": [mode.value for mode in TemperatureMode], #[TemperatureMode.SET_TEMPERATURE.value],
            "TemperatureUnit": list(self.temperature_units.keys()),
            "MeasureT": True,
            "ReachT": True,
            "Sensor": ["Main", "PT100A", "PT100B"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle GUI parameter values."""
        mode = parameter["SweepMode"]
        # Handle None value for Get/Set T in C actions
        self.sweep_mode = TemperatureMode.SET_TEMPERATURE if mode == "None" else TemperatureMode(mode)

        self.handle_port_string(parameter["Port"])

        self.measure_temperature = bool(parameter["MeasureT"])

        self.sensor = getattr(Sensor, parameter["Sensor"].upper())
        self.temperature_unit = self.temperature_units[parameter["TemperatureUnit"]]
        self.units = [parameter["TemperatureUnit"]]

        self.use_reach = bool(parameter["ReachT"])

    def handle_port_string(self, port_string: str) -> None:
        """Extract IP address and socket from port string."""
        port_string = port_string.strip().lower()
        self.target_socket = 1412

        if "localhost" in port_string:
            self.ip_address = "localhost"
        elif "port" in port_string:
            self.ip_address = port_string.split(";")[0].split(":")[1].strip()
            self.target_socket = int(port_string.split(";")[1].split(":")[1].strip())
        elif "ip" in port_string:
            self.ip_address = port_string.split("ip:")[1].strip()
        else:
            # Try to interpret the port string as an IP address
            self.ip_address = port_string.strip()

    def connect(self) -> None:
        """Establish connection to Velox Software."""
        self.connect_to_velox()

    def disconnect(self) -> None:
        """Disconnect from Velox Software."""
        self.disconnect_from_velox()

    def configure(self) -> None:
        """Configure the device."""
        # Deactivate Standby mode
        try:
            velox.EnableHeaterStandby(0)
        except velox.SciException as e:
            # ignore, station does not support standby mode
            pass

        # Reach temperature must be enabled to use self.reach. Otherwise, velox will immediately go to the next set
        # temperature before reaching the current one.
        if not self.use_reach:
            msg = "Driver cannot be used without 'Reach Temperature'. Please enable 'Reach Temperature' in GUI."
            raise Exception(msg)

    def unconfigure(self) -> None:
        """Unconfigure the device."""
        # Stop pending heating or cooling process and set current temperature as target temperature
        self.stop_heating()

    def apply(self) -> None:
        """Set the target temperature."""
        # ensure IDLE or COLD state
        # Stop previous heating process
        velox.StopHeatChuck()

        if self.sweep_mode == TemperatureMode.SET_TEMPERATURE:
            # Use SetHeaterTemp, because HeatChuck will block any response until the temperature is reached
            velox.SetHeaterTemp(self.value, self.temperature_unit)

        # Currently untested additional modes:
        elif self.sweep_mode == TemperatureMode.AUTOMATION_TEMPERATURE:
            velox.StartAutomationTemperature(self.value)
            # Polling time for Automation mode should be >= 5s
            time.sleep(5.0)

        elif self.sweep_mode == TemperatureMode.REALIGN_TEMPERATURE:
            velox.StartReAlignTemperature(self.value)
            # Polling time for ReAlign mode should be >= 5s
            time.sleep(5.0)

        else:
            msg = f"Temperature mode {self.sweep_mode} is not supported."
            raise Exception(msg)

    def reach(self) -> None:
        """Wait until set temperature is reached."""
        while not self.is_temperature_reached() and not self.is_run_stopped():
            if self.sweep_mode == TemperatureMode.SET_TEMPERATURE:
                time.sleep(0.5)  # A longer waiting time between requests could be used, internal communication is 0.5s
            elif self.sweep_mode in [TemperatureMode.AUTOMATION_TEMPERATURE, TemperatureMode.REALIGN_TEMPERATURE]:
                # Polling time for Automation and ReAlign mode should be >= 5s
                time.sleep(5.0)
            else:
                msg = f"Temperature mode {self.sweep_mode} is not supported."
                raise Exception(msg)

    def call(self) -> float:
        """Return the current temperature."""
        return self.get_temperature()

    "--- Wrapper Functions ---"

    def connect_to_velox(self) -> None:
        """Connect to the Velox SDK."""
        if self.msg_server is None:
            try:
                self.msg_server = velox.MessageServerInterface(self.ip_address, self.target_socket).__enter__()
            except Exception as e:
                # Check if Velox software is running
                if "The connection to the Velox Message Server was refused." in str(e):
                    msg = "Unable to connect to Velox software. Please start Velox and try again."
                    raise Exception(msg) from e

                raise e

    def disconnect_from_velox(self) -> None:
        """Disconnect from Velox Software."""
        if self.msg_server is not None:
            self.msg_server.__exit__(None, None, None)
            self.msg_server = None

    def get_temperature(self) -> float:
        """Reads the current temperature from given sensor."""
        response = velox.GetHeaterTemp(self.temperature_unit, self.sensor.value)
        return float(response[0])

    def get_target_temperature(self) -> float:
        """Reads the target temperature for given sensor."""
        response = velox.GetTargetTemp(self.temperature_unit)
        return float(response[0])

    def is_temperature_reached(self) -> bool:
        """Reads the thermal Chuck status."""
        temperature_reached = True

        if self.sweep_mode == TemperatureMode.SET_TEMPERATURE:
            status = velox.ReadTemperatureChuckStatus()
            status_bit = int(status[0])
            temperature_reached = Status(status_bit) == Status.HOLD_READY or Status(status_bit) == Status.AT_TEMPERATURE

        elif self.sweep_mode == TemperatureMode.AUTOMATION_TEMPERATURE:
            status = velox.GetAutomationTemperatureStatus()
            status_bit = int(status[0])

            if status_bit == 2:
                msg = f"Automation Temperature Error: {status[1]}"
                raise Exception(msg)

            temperature_reached = status_bit == 0

        elif self.sweep_mode == TemperatureMode.REALIGN_TEMPERATURE:
            status = velox.GetReAlignTemperatureStatus()
            status_bit = int(status[0])

            if status_bit == 2:
                msg = f"ReAlign Temperature Error: {status[1]}"
                raise Exception(msg)

            temperature_reached = status_bit == 0

        return temperature_reached

    def stop_heating(self) -> None:
        """Stop heating process."""
        if self.sweep_mode == TemperatureMode.SET_TEMPERATURE:
            velox.StopHeatChuck()
        elif self.sweep_mode == TemperatureMode.AUTOMATION_TEMPERATURE:
            velox.StopAutomationTemperature()
        elif self.sweep_mode == TemperatureMode.REALIGN_TEMPERATURE:
            velox.StopReAlignTemperature()
