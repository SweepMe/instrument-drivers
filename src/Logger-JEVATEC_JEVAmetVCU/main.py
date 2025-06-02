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
# * Instrument: JEVATEC JEVAmet VCU

from __future__ import annotations

from typing import Any

from pysweepme import debug
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver to read out the JEVATEC JEVAmet VCU vacuum controller."""

    description = """
        <h3>JEVAmet® VCU</h3>
        <p>This driver communicates with the JEVATEC JEVAmet VCU vacuum controller.</p>

        <h4>Setup</h4>
        <ul>
            <li>Set the communication interface in the device menu under <b>Config → Gen → rS</b> to either RS232 or
             RS485. Changes take effect after a device restart.</li>
            <li>Set the baud rate in the device menu under <b>Config → Gen → bAud</b> to 38.4 (38400).</li>
            <li>If using <b>RS232</b>:
                <ul>
                    <li>Connect the device using a standard 9-pin straight-through serial cable.</li>
                </ul>
            </li>
            <li>If using <b>RS485</b>:
                <ul>
                    <li>Follow the custom RS485 pin assignment as documented in section 5.3.7 of the manual.</li>
                    <li>Older models might not be able to set/read the RS485 address from the device menu.</li>
                    <li>Workaround: Read/set the address via RS232 communication (<code>RSA[XX]</code>) or use FF as
                     address, which will communicate with all devices.</li>
                </ul>
            </li>
            <li>Connect a supported vacuum sensor to one of the available measurement channels (CH1, CH2, CH3),
             depending on your device model.</li>
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

        self.shortname = "VCU"  # short name will be shown in the sequencer

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
            "EOL": "\x0D",
            "timeout": 2,
        }
        self.use_rs485: bool = False
        self.address: str = "FF"  # RS485 address, default is 1
        self.last_error: str = ""
        """Save the last error message to display it in the GUI only if it changes."""

        # Measurement parameters
        self.channel: int = 1  # default channel
        self.unit: str = "mbar"
        self.supported_units = {
            "mbar": 0,
            "Pa": 1,
            "Torr": 2,
        }

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        communication = parameters.get("Communication", "RS232")

        new_parameters = {
            "Channel": [1, 2, 3],
            "Unit": list(self.supported_units.keys()),
            "Communication": ["RS232", "RS485"],
        }

        if communication == "RS485":
            new_parameters["RS485 Address"] = "FF"

        return new_parameters

    def apply_gui_parameters(self, parameters: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.channel = parameters.get("Channel", 1)
        self.unit = parameters.get("Unit", "mbar")
        # Update the return parameter
        self.units = [self.unit]

        self.use_rs485 = parameters.get("Communication", "RS232") == "RS485"

        # Reset address
        self.address = "FF"
        if self.use_rs485:
            self.address = parameters.get("RS485 Address", "FF")

    def configure(self) -> None:
        """Verify the RS485 address, if needed."""
        self.set_general_parameter()

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.get_pressure()

    def get_pressure(self) -> float:
        """Get the pressure value. If an error occurs, display the error message and return float('nan')."""
        self.write(f"RPV{self.channel}")
        response = self.port.read()

        split_response = response.split("\t")
        pressure = float("nan")
        if len(split_response) == 2:
            # If the device is working correctly, it responds with '[Status],\t[Pressure]'
            status = self.handle_status(split_response[0].strip(","))
            pressure = float(split_response[1])
        elif len(split_response) == 3:
            # If no sensor is connected, the device responds with '?\tS,\t[ChannelNum]' - Err S means sensor error
            # This is not denoted in the manual, but has been observed in practice
            status = f"Err {split_response[1].strip(',')}"
        else:
            # If the response is not in the expected format, handle it as an error
            status = "Unknown"

        if status != "OK":
            pressure = float("nan")
            if self.last_error != status:
                self.last_error = status
                debug(f"Error in pressure response: {status}")
        else:
            self.last_error = ""

        return pressure

    def set_general_parameter(self) -> None:
        """Configure the device according to manual section 8.3.14."""
        if self.unit not in self.supported_units:
            msg = f"Unit {self.unit} not supported. Choose from {self.supported_units}."
            raise ValueError(msg)

        unit = self.supported_units[self.unit]
        decimals = 1  # 3 Decimals
        display_brightness = 1  # low brightness
        baudrate = 2  # 38400 baud
        communication = 1 if self.use_rs485 else 0

        # unit, decimals, display brightness, baudrate, communication
        command = f"SGP{unit},{decimals},{display_brightness},{baudrate},{communication}"
        self.write(command)
        response = self.port.read()
        if response != "OK":
            msg = f"Device returned error during configuration: {response}"
            raise ValueError(msg)

    # Communication functions

    def write(self, command: str) -> None:
        """Write a command to the device."""
        if self.use_rs485:
            address = self.create_rs485_address(self.address)
            command_string = f"{address}{command}"
        else:
            command_string = command

        # No EOL character needed as the port manager appends it
        self.port.write(command_string)

    @staticmethod
    def handle_status(status: str) -> str:
        """Handle the status of the device."""
        status_dict = {
            "0": "OK",
            "1": "Underrange (below measurement range)",
            "2": "Overrange (above measurement range)",
            "3": "Significantly below range (Err Lo)",
            "4": "Significantly above range (Err Hi)",
            "5": "Sensor off (OFF)",
            "6": "HV on (HU on)",
            "7": "Sensor error (Err S)",
            "8": "BA error (Err bA)",
            "9": "No sensor connected (no Sen)",
            "10": "No switchpoint configured (notrig)",
            "11": "Pressure limit exceeded (Err P)",
            "12": "ATMION® Pirani error (Err Pi)",
            "13": "Operating voltage failure (Err 24)",
            "15": "Filament defect (FiLbr)",
        }

        if status not in status_dict:
            return f"Invalid status code: {status}"

        return status_dict[status]

    @staticmethod
    def create_rs485_address(address_str: str) -> str:
        """Constructs the RS485 address as two ASCII characters representing a hexadecimal value."""
        if address_str == "FF":
            return address_str

        try:
            _address = int(address_str)
        except ValueError as e:
            msg = f"Cannot convert RS485 address {address_str} to integer."
            raise ValueError(msg) from e

        if not (1 <= _address <= 126):
            msg = f"Invalid RS485 address {address_str}. Address must be between 1 and 126."
            raise ValueError(msg)

        return f"{_address:02X}"

    # Currently not needed wrapper functions

    def get_identification(self) -> str:
        """Get the identification string."""
        self.write("RVN")
        return self.port.read()

    def print_address(self) -> None:
        """Get the RS485 address."""
        self.write("RSA")
        address = self.port.read()
        print(f"RS485 address: {address}")
