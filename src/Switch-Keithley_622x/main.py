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

# SweepMe! driver
# * Module: Switch
# * Instrument: Keithley 6220, 6221

"""SweepMe! driver for the Keithley 6220 DC current source and the 6221 AC and DC current source."""

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keithley 6220/6221 to source a DC current."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Keithley 622x"

        self.variables = ["Current", "Compliance"]
        self.units = ["A", ""]
        self.plottype = [True, False]
        self.savetype = [True, True]

        self.port_manager = True
        self.port_types = ["GPIB", "COM", "TCPIP"]

        self.port_properties = {
            "timeout": 5,
            "baudrate": 19200,  # factory default
            "EOL": "\n",  # factory default terminator is LF
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOL_read": "\n",
        }

        # source ranges as shown in the GUI and their maximum output in A, including 5 % overrange
        self.current_ranges = {
            "Auto": 105e-3,
            "2 nA": 2.1e-9,
            "20 nA": 21e-9,
            "200 nA": 210e-9,
            "2 µA": 2.1e-6,
            "20 µA": 21e-6,
            "200 µA": 210e-6,
            "2 mA": 2.1e-3,
            "20 mA": 21e-3,
            "100 mA": 105e-3,
        }

        # the nominal range values that are sent to select a fixed range
        self.current_range_values = {
            "2 nA": 2e-9,
            "20 nA": 20e-9,
            "200 nA": 200e-9,
            "2 µA": 2e-6,
            "20 µA": 20e-6,
            "200 µA": 200e-6,
            "2 mA": 2e-3,
            "20 mA": 20e-3,
            "100 mA": 100e-3,
        }

        # voltage compliance limits in V
        self.compliance_min = 0.1
        self.compliance_max = 105.0

        self.output_responses = {
            "Fast": "FAST",
            "Slow": "SLOW",
        }

        self.output_low_connections = {
            "Floating": False,
            "Earth": True,
        }

        self.inner_shield_connections = {
            "Output low": "OLOW",
            "Guard": "GUAR",
        }

        # GUI parameters
        self.sweep_mode: str = "Current in A"
        self.current_range: str = "Auto"
        self.compliance: float = 10.0
        self.analog_filter: bool = False
        self.output_response: str = "Fast"
        self.output_low: str = "Floating"
        self.inner_shield: str = "Output low"

        # instrument state
        self.model: str = ""
        self.current: float = 0.0
        self.in_compliance: bool = False

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI parameters and their options."""
        return {
            "SweepMode": ["Current in A"],
            "Range": list(self.current_ranges.keys()),
            "Compliance in V": 10.0,
            "Analog filter": False,
            "Output response": list(self.output_responses.keys()),
            "Output low": list(self.output_low_connections.keys()),
            "Inner shield": list(self.inner_shield_connections.keys()),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameters selected by the user."""
        self.sweep_mode = parameters.get("SweepMode", "Current in A")
        self.current_range = parameters.get("Range", "Auto")
        self.compliance = float(parameters.get("Compliance in V", 10.0))
        self.analog_filter = bool(parameters.get("Analog filter", False))
        self.output_response = parameters.get("Output response", "Fast")
        self.output_low = parameters.get("Output low", "Floating")
        self.inner_shield = parameters.get("Inner shield", "Output low")

    def initialize(self) -> None:
        """Reset the instrument and identify the model."""
        # identification looks like 'KEITHLEY INSTRUMENTS INC.,MODEL 6221,<serial>,<firmware>'
        identification = self.get_identification().split(",")
        self.model = identification[1].strip() if len(identification) > 1 else ""

        self.reset()
        self.clear_status()

        if not self.compliance_min <= self.compliance <= self.compliance_max:
            msg = (
                f"Compliance of {self.compliance} V is outside the range of {self.compliance_min} V to "
                f"{self.compliance_max} V."
            )
            raise ValueError(msg)

    def configure(self) -> None:
        """Configure the output connections, the range, and the compliance."""
        self.set_output_low_earth(self.output_low_connections[self.output_low])
        self.set_inner_shield(self.inner_shield_connections[self.inner_shield])

        # the output response is only available for the Model 6221 and can only be changed with output off
        if "6221" in self.model:
            self.set_output_response(self.output_responses[self.output_response])

        self.set_analog_filter(self.analog_filter)

        if self.current_range == "Auto":
            self.set_current_autorange(True)
        else:
            self.set_current_range(self.current_range_values[self.current_range])

        self.set_compliance(self.compliance)

        self.print_errors()

    def poweron(self) -> None:
        """Switch the output on."""
        if not self.get_interlock_closed():
            msg = "The interlock of the Keithley 622x is open, the output cannot be switched on."
            raise ConnectionError(msg)

        self.set_output(True)

    def poweroff(self) -> None:
        """Switch the output off."""
        self.set_output(False)

    def apply(self) -> None:
        """Set the new output current."""
        self.current = float(self.value)

        max_current = self.current_ranges[self.current_range]
        if abs(self.current) > max_current:
            msg = (
                f"Current of {self.current} A exceeds the maximum output of ±{max_current} A "
                f"of range {self.current_range}."
            )
            raise ValueError(msg)

        self.set_current(self.current)

    def measure(self) -> None:
        """Read whether the current source is in compliance."""
        self.in_compliance = self.get_compliance_state()

    def call(self) -> list[Any]:
        """Return the set current and the compliance state."""
        return [self.current, self.in_compliance]

    """ here, convenience functions start """

    def print_errors(self) -> None:
        """Read the error queue and print all errors to the debug widget."""
        # the error queue holds up to 10 messages
        for _ in range(10):
            error = self.read_error()
            if int(error.split(",")[0]) == 0:
                break
            print(f"Keithley 622x error: {error}")  # noqa: T201

    """ here, communication commands are wrapped into python convenience functions """

    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        return str(self.port.query("*IDN?"))

    def reset(self) -> None:
        """Reset the instrument to its default settings, which also switches the output off."""
        self.port.write("*RST")

    def clear_status(self) -> None:
        """Clear the status registers and the error queue."""
        self.port.write("*CLS")

    def read_error(self) -> str:
        """Return the oldest message of the error queue."""
        return str(self.port.query(":SYST:ERR?"))

    def set_output_low_earth(self, state: bool) -> None:
        """Connect output low to earth ground (True) or let it float (False)."""
        self.port.write(f":OUTP:LTE {'ON' if state else 'OFF'}")

    def set_inner_shield(self, connection: str) -> None:
        """Connect the triax inner shield to output low ('OLOW') or guard ('GUAR')."""
        self.port.write(f":OUTP:ISH {connection}")

    def set_output_response(self, response: str) -> None:
        """Set the output response to 'FAST' or 'SLOW', only possible with output off (Model 6221 only)."""
        self.port.write(f":OUTP:RESP {response}")

    def set_analog_filter(self, state: bool) -> None:
        """Switch the analog output filter on or off."""
        self.port.write(f":SOUR:CURR:FILT {'ON' if state else 'OFF'}")

    def set_current_autorange(self, state: bool) -> None:
        """Switch the source autorange on or off."""
        self.port.write(f":SOUR:CURR:RANG:AUTO {'ON' if state else 'OFF'}")

    def set_current_range(self, current_range: float) -> None:
        """Select the lowest fixed source range that covers the given current in A, which disables autorange."""
        self.port.write(f":SOUR:CURR:RANG {current_range:g}")

    def set_compliance(self, voltage: float) -> None:
        """Set the voltage compliance in V."""
        self.port.write(f":SOUR:CURR:COMP {voltage:g}")

    def set_current(self, current: float) -> None:
        """Set the DC output current in A."""
        self.port.write(f":SOUR:CURR {current}")

    def get_interlock_closed(self) -> bool:
        """Return True if the interlock is closed and the output can be switched on."""
        return int(self.port.query(":OUTP:INT:TRIP?")) == 1

    def set_output(self, state: bool) -> None:
        """Switch the output on or off."""
        self.port.write(f":OUTP {'ON' if state else 'OFF'}")

    def get_compliance_state(self) -> bool:
        """Return True if the current source is in compliance (bit B3 of the measurement condition register)."""
        return bool(int(self.port.query(":STAT:MEAS:COND?")) & 8)
