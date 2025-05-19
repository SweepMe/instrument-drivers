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
# * Module: Logger
# * Instrument: jevatec JEVAmet VCU active

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver to read out the JEVAmet® VCU active vacuum controller."""

    description = """
        <h3>JEVAmet® VCU active</h3>
        <p>This driver communicates with the JEVAmet® VCU active vacuum controller.</p>

        <h4>Setup</h4>
        <ul>
            <li>Set the communication interface in the device menu under <b>System → COM Port</b> (choose RS232 or RS485) and ensure the settings match those configured in the driver GUI.</li>
            <li>Set the baud rate in the device menu under <b>System → Data Rate</b> (choose 38400).</li>
            <li>If using <b>RS232</b>, connect the device with a standard 9-pin straight-through serial cable.</li>
            <li>If using <b>RS485</b>:
                <ul>
                    <li>Follow the custom RS485 pin assignment as documented in section 5.3.7 of the manual.</li>
                    <li>Set the RS485 address in the device system menu and enter the same address in the driver GUI.</li>
                </ul>
            </li>
            <li>Connect a supported vacuum sensor to one of the available measurement channels (CH1, CH2, CH3), based on your device type.</li>
        </ul>


        <p>The available number of channels depends on the device type:</p>
        <ul>
            <li><b>Type AM</b> and <b>BM</b>: 3 channels</li>
            <li><b>Type C</b>: 2 channels</li>
            <li><b>Type A0</b> and <b>B0</b>: 1 channel</li>
        </ul>
        """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "VCU active"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Pressure"]
        self.units = ["mbar"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "baudrate": 38400,
            "EOL": "\x04",
            "timeout": 2,
        }
        self.use_rs485: bool = False
        self.address: int = -1

        self.read_bit = "\x0F"
        self.write_bit = "\x0E"
        self.ack = "\x06"
        self.nack = "\x15"

        # Measurement parameters
        self.channel: int = 1  # default channel
        self.supported_units = ["mbar", "Torr", "Pa", "Micron", "psi"]

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        communication = parameters.get("Communication", "RS232")

        new_parameters = {
            "Channel": [1, 2, 3],
            "Unit": self.supported_units,
            "Communication": ["RS232", "RS485"],
        }

        if communication == "RS485":
            new_parameters["RS485 Address"] = "1"

        return new_parameters

    def apply_gui_parameters(self, parameters: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.channel = parameters["Channel"]
        self.unit = parameters["Unit"]
        # Update the return parameter
        self.units = [self.unit]

        self.use_rs485 = parameters["Communication"] == "RS485"

        # Reset address
        self.address = -1
        if self.use_rs485:
            self.address = parameters.get("RS485 Address", -1)

    def configure(self) -> None:
        """Verify the RS485 address, if needed."""
        self.set_unit(self.unit)

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.get_pressure()

    def get_pressure(self) -> float:
        """Get the pressure value."""
        command = self.build_read_command(self.channel, 29)
        self.port.write(command)
        return float(self.get_read_response())

    def set_unit(self, unit: str = "mbar") -> None:
        """Set the unit to mbar."""
        if unit not in self.supported_units:
            msg = f"Unit {unit} not supported. Choose from {self.supported_units}."
            raise ValueError(msg)

        command = self.build_write_command(5, 4, unit)
        self.port.query(command)

    # Communication functions

    def build_read_command(self, parameter_group: int, parameter_number: int) -> str:
        """Builds a read command string with checksum."""
        base = f"{self.read_bit}{parameter_group};{parameter_number}"  # removed ;
        checksum = self.calculate_checksum(base)

        if self.use_rs485:
            address = self.create_rs485_address(self.address)
            base = f"{address}{base}"

        # No EOL character needed as the port manager appends it
        return f"{base}{checksum}"

    def get_read_response(self) -> str:
        """Read the response from the device and handle command structure."""
        response = self.port.read()
        if self.use_rs485:
            # remove the leading address
            response = response[2:]

        if response[0] != self.ack:
            msg = f"Device returned NACK or invalid data: {response}"
            raise ValueError(msg)

        # Remove the ACK and CRC characters
        return response[1:-1].strip()

    def build_write_command(self, parameter_group: int, parameter_number: int, value: str) -> str:
        """Builds a write command string with checksum."""
        base = f"{self.write_bit}{parameter_group};{parameter_number};{value} "
        checksum = self.calculate_checksum(base)
        if self.use_rs485:
            address = self.create_rs485_address(self.address)
            base = f"{address}{base}"

        return f"{base}{checksum}"

    @staticmethod
    def create_rs485_address(address_str: str) -> str:
        """Constructs the RS485 address as two ASCII characters representing a hexadecimal value."""
        try:
            _address = int(address_str)
        except ValueError as e:
            msg = f"Cannot convert RS485 address {address_str} to integer."
            raise ValueError(msg) from e

        if not (1 <= _address <= 126):
            msg = f"Invalid RS485 address {address_str}. Address must be between 1 and 126."
            raise ValueError(msg)

        return f"{_address:02X}"

    @staticmethod
    def calculate_checksum(message: str) -> str:
        """Calculates the CRC as defined in manual 8.2.2.4.

        CRC = 255 - (sum of bytes % 256)
        If result < 32 (control char range), add 32
        Returns the ASCII character representation of the CRC.
        """
        checksum = 255 - (sum(ord(c) for c in message) % 256)
        if checksum < 32:
            checksum += 32
        return chr(checksum)

    # Currently not needed wrapper functions

    def get_identification(self) -> str:
        """Get the identification string."""
        command = self.build_read_command(5, 2)
        self.port.write(command)
        return self.get_read_response()
