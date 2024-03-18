# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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


# SweepMe! device class
# Device: FTDI FTD2xx

from __future__ import annotations

import binascii

from pysweepme import EmptyDevice, ErrorMessage, FolderManager

FolderManager.addFolderToPATH()

import ftd2xx as ftd


class Device(EmptyDevice):
    """FTDI FTD2xx Device Class."""

    description = """
        <h3>FTDI FTD 2xx</h3>
        <p>This driver allows to send byte strings to FTD boards such as the FTD245R.</p>
        <h4>Setup</h4>
        <p>
        The FTDI driver needs to be installed, which can be found <a href="https://ftdichip.com/drivers/">here</a>.
        </p>
        <h4>Parameters</h4>
        <p>
        The <em>Start Command </em>and <em>End command </em>are sent at the configure and unconfigure steps,
        respectively.
        </p>
        <p>
        The Readout length can be set if responses with a set length are expected.
        Set Readout length = 0 to read out the full buffer.
        </p>
        <p><em>Timeout </em>is set for both reading and writing.</p>
    """

    def __init__(self) -> None:
        """Initialize SweepMe parameters."""
        EmptyDevice.__init__(self)

        # SweepMe parameters
        self.shortname = "FTD2xx"
        self.variables = ["Response"]
        self.units = []
        self.port_manager = False

        self.port_str: str = ""
        self.driver_name: str = "FTD2xx"
        self.instance_key: str = ""
        self.device = None

        # FTDI parameters
        self.encoding: str = ""
        self.start_command: str = ""
        self.end_command: str = ""
        self.readout_length: int = 0
        self.timeout_ms: int = 5000  # Read and write timeout in ms

        self.verbose = False  # Set to True to print out the sent and received strings for testing

    @staticmethod
    def find_ports() -> list[str]:
        """Read available devices and return list of serial numbers."""
        return [dev.decode() for dev in ftd.listDevices()]

    def set_GUIparameter(self) -> dict[str, list[str] | str | int]:  # noqa: N802
        """Set default parameters for SweepMe GUI."""
        return {
            "Encoding": ["HEX", "ASCII"],
            "SweepMode": "Command",
            "Start command": "",
            "End command": "",
            "Readout length": 0,
            "Timeout in ms": 5000,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Read parameters from SweepMe GUI and check their type."""
        self.encoding = parameter["Encoding"]
        self.units.append(self.encoding)

        self.start_command = self.handle_bytestring(parameter["Start command"])
        self.end_command = self.handle_bytestring(parameter["End command"])

        self.readout_length = int(parameter["Readout length"])
        self.timeout_ms = int(parameter["Timeout in ms"])

        self.port_str = self.handle_bytestring(parameter["Port"])
        self.driver_name = parameter["Device"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self) -> None:
        """Open connection to FTDI."""
        # Set Name/Number of COM Port as key
        self.instance_key = f"{self.driver_name}_{self.port_str}"

        if self.instance_key in self.device_communication:
            self.device = self.device_communication[self.instance_key]
        else:
            # Open device
            port_byte = self.port_str.encode()
            try:
                self.device = ftd.openEx(port_byte)
            except ftd.ftd2xx.DeviceError as e:
                msg = f"Cannot open FTD Device with serial number {port_byte}. Available devices: {ftd.listDevices()}"
                raise Exception(msg) from e

            self.device_communication[self.instance_key] = self.device

    def disconnect(self) -> None:
        """Close connection to FTDI."""
        self.device.close()

        if self.instance_key in self.device_communication:
            self.device_communication.pop(self.instance_key)

    def configure(self) -> None:
        """Handle device configurations and start command."""
        self.device.setTimeouts(self.timeout_ms, self.timeout_ms)
        self.send_command(self.start_command)

    def unconfigure(self) -> None:
        """Handle device unconfigurations and end command."""
        self.send_command(self.end_command)

    def apply(self) -> None:
        """Send the command to the device."""
        self.send_command(self.value)

    def call(self) -> str:
        """Read the response from the device."""
        if self.readout_length > 0:
            answer = self.device.read(self.readout_length)
        else:
            queue = self.device.getQueueStatus()
            answer = self.device.read(queue)

        self.print_verbose(f"Answer: {answer}, Converted: {self.handle_bytestring(answer)}")

        return self.handle_bytestring(answer)

    """ here, convenience functions start """

    def send_command(self, command: str) -> None:
        """Encode and send command to the device."""
        encoded_string = self.encode_string(command)
        self.print_verbose(f"Sending: {command}, Converted: {encoded_string}")
        self.device.write(encoded_string)

    def encode_string(self, string: str) -> bytes:
        """Encode string´depending on given encoding."""
        if self.encoding == "HEX":
            encoded_string = binascii.unhexlify(string.replace(" ", ""))
        else:
            encoded_string = bytes(string, "utf-8")

        return encoded_string

    @staticmethod
    def handle_bytestring(bytestring: str | bytes) -> str:
        """Try to convert given bytestring to str."""
        try:
            return bytestring.decode()
        except (UnicodeDecodeError, AttributeError):
            return bytestring

    def print_verbose(self, string: str) -> None:
        """Print string if verbose is set to True."""
        if self.verbose:
            ErrorMessage.debug(string)
