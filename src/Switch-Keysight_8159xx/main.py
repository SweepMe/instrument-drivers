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
# SweepMe! driver
# * Module: Switch
# * Instrument: Keysight 8159xx

from __future__ import annotations

import time
from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight 8159xx."""

    description = """"Driver for the Keysight 8159xx. Can be implemented in Agilent 816x Lightwave Measurement System.

    Also supports The discontinued 81591A, 81591S, 81592A, 81592S, 81594A, 81594S, and 81595A, 81595S

    Choose the slot where your module is installed in the device.
    Select the channel of your module in case its a dual device.
    Set the left and right port as colon separated string, e.g. "A:1" for port A and port 1. Use semicolon to set
    multiple routes, e.g. "A:1;B:2" for port A and port 1 and port B and port 2.
    If you want to set the route before the measurement starts (e.g. in configure), use the "Route" GUI parameter.
    Using the "Route" sweep mode, the route will be set in "apply" according to the sweep value.
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "8159xx"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Route"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB", "COM", "TCPIP"]

        # Measurement parameters
        self.channel: int = 1
        self.slot: int = 1
        self.sweep_mode: str = "None"
        self.available_left_ports: list[str] = []
        self.available_right_ports: list[str] = []
        self.route: str = ""  # Initial route to set in configure

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "Channel": "1",
            "Slot": "1",
            "SweepMode": ["Route", "None"],
            "Route": "A:1",
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Apply the parameters received from the SweepMe GUI or the pysweepme instance to the driver instance."""
        self.port_string = parameters.get("Port", "")
        self.channel = parameters.get("Channel", "")
        self.slot = parameters.get("Slot", "")
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.route = parameters.get("Route", "")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.available_left_ports, self.available_right_ports = self.get_available_ports()
        # Apply initial route if set in GUI
        if self.route:
            self.apply_route_string(self.route)

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweep_mode == "Route":
            self.apply_route_string(self.value)

    def call(self) -> str:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.get_route()

    def get_identification(self) -> str:
        """Return the identification string of the device."""
        return self.port.query("*IDN?")

    # Wrapper Functions

    def apply_route_string(self, route_string: str) -> None:
        """Apply a route string to the device.

        Args:
            route_string (str): The route string to apply, e.g. "A:1;B:2".
        """
        routes = route_string.split(";")
        for route in routes:
            left_port, right_port = route.split(":")
            if left_port not in self.available_left_ports:
                msg = f"Left port '{left_port}' is not available. Available ports: {self.available_left_ports}"
                raise ValueError(msg)

            if right_port not in self.available_right_ports:
                msg = f"Right port '{right_port}' is not available. Available ports: {self.available_right_ports}"
                raise ValueError(msg)

            self.set_route(left_port, right_port)
            self.wait_for_completion()

    def wait_for_completion(self) -> None:
        """Wait for the device to complete the current operation."""
        while True:
            status = self.port.query("*OPC?")
            if status.strip() == "1":
                break

            if self.is_run_stopped():
                break

            time.sleep(0.05)

    def set_route(self, left_port: str, right_port: str) -> None:
        """Set the route for the device.

        Args:
            left_port (str): The left port, must be a single alphabetic character.
            right_port (str): The right port, must be a single digit.
        """
        if len(left_port) != 1 or not left_port.isalpha():
            msg = f"Left port must be a single alphabetic character, got '{left_port}'."
            raise ValueError(msg)

        if len(right_port) != 1 or not right_port.isdigit():
            msg = f"Right port must be a single digit, got '{right_port}'."
            raise ValueError(msg)

        current_route = self.get_route().strip()
        if current_route == f"{left_port},{right_port}":
            return

        command = f":ROUT{self.slot}:CHAN{self.channel} {left_port},{right_port}"
        self.port.write(command)
        # print(f"Response: {response}")
        # if "StatParamError" in response:
        #     msg = f"Invalid route command: {command}. Response: {response}"
        #     raise ValueError(msg)

    def get_route(self) -> str:
        """Get the current route of the device."""
        # todo maybe remove channel if it does not work
        return self.port.query(f":ROUT{self.slot}:CHAN{self.channel}?")

    def get_available_ports(self) -> tuple[list[str], list[str]]:
        """Returns the available ports for left and right for the device."""
        response = self.port.query(f":ROUT{self.slot}:CHAN{self.channel}:CONF?")
        left_port_limits, right_port_limits = response.split(";")

        left_port_min, left_port_max = left_port_limits.split(",")
        left_ports = [chr(i) for i in range(ord(left_port_min), ord(left_port_max) + 1)]

        right_port_min, right_port_max = right_port_limits.split(",")
        right_ports = [str(i) for i in range(int(right_port_min), int(right_port_max) + 1)]

        return left_ports, right_ports
