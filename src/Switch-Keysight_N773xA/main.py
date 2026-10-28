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
# * Module: Switch
# * Instrument: Keysight/Agilent N773xA optical switch

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice

# The driver addresses 1xN switches, whose common port is the left port A. Only the numbered right port changes.
INPUT_PORT = "A"


class Device(EmptyDevice):
    """Driver for the Keysight/Agilent N773xA optical switches."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "N773xA"  # short name will be shown in the sequencer
        self.variables = ["Route"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [True]

        # Port configuration
        self.port_manager = True
        self.port_types = ["GPIB", "USBTMC", "TCPIP"]
        self.port_properties = {
            "timeout": 5,
        }

        self.slot_string: str = "1"
        self.slot: int = 1
        self.sweepmode: str = "Output port"
        self.route: str = ""
        self.output_max: int = 13
        self.output_min: int = 1

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Output port"],
            "Slot": parameters.get("Slot", "1"),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweepmode = parameters.get("SweepMode", "Output port")
        self.slot_string = str(parameters.get("Slot", "1"))

    def initialize(self) -> None:
        """Initialize the instrument. This function is called only once at the start of the measurement."""
        self.clear_status()

    def configure(self) -> None:
        """Check the slot number and read the available routes."""
        try:
            self.slot = int(self.slot_string)
        except ValueError:
            msg = f"Cannot interpret the slot '{self.slot_string}' as a number."
            raise ValueError(msg) from None

        self.update_available_routes()

    def apply(self) -> None:
        """This function is called if the set value has changed. Applies the new value available as self.value."""
        try:
            output_port = int(float(self.value))
        except ValueError:
            msg = f"Cannot interpret the sweep value '{self.value}' as an output port number."
            raise ValueError(msg) from None

        if output_port < self.output_min or output_port > self.output_max:
            msg = (
                f"Output port number {output_port} is out of range. "
                f"Valid range is {self.output_min} to {self.output_max}."
            )
            raise ValueError(msg)

        self.set_route(INPUT_PORT, output_port)

    def measure(self) -> None:
        """Read back the route that is currently set at the switch."""
        self.route = self.get_route()

    def call(self) -> list[str]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.route]

    # wrapped communication commands below

    def get_identification(self) -> str:
        """Get the instrument identification string."""
        return str(self.port.query("*IDN?"))

    def clear_status(self) -> None:
        """Clear the instrument status and error queue."""
        self.port.write("*CLS")

    def get_options(self) -> str:
        """Get the installed switch modules, e.g. 'N7736A-008,N7736A-008' for an instrument with two switches."""
        return str(self.port.query("*OPT?"))

    def set_route(self, input_port: str, output_port: int) -> None:
        """Connect the given left port, e.g. 'A', to the given numbered right port of the switch.

        The channel number is omitted because the N77xx series ignores it. It only exists for
        compatibility with the Keysight 816x instruments, where it addressed modules within a slot.
        """
        self.port.write(f":ROUTe{self.slot} {input_port},{int(output_port)}")

    def get_route(self) -> str:
        """Get the currently set route as '<left port>,<right port>', e.g. 'A,2'."""
        return str(self.port.query(f":ROUTe{self.slot}?"))

    def update_available_routes(self) -> None:
        """Update the available routes from the instrument."""
        available_routes = self.get_route_configuration()
        input_ports, output_ports = available_routes.split(";")
        self.output_min = int(output_ports.split(",")[0])
        self.output_max = int(output_ports.split(",")[1])

    def get_route_configuration(self) -> str:
        """Get the available ports as '<first left>,<last left>;<min right>,<max right>', e.g. 'A,A;1,4'."""
        return str(self.port.query(f":ROUTe{self.slot}:CONFig?"))

    def get_error_message(self) -> str:
        """Get the oldest entry of the instrument error queue."""
        return str(self.port.query(":SYSTem:ERRor?"))
