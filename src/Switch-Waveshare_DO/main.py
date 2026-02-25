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
# * Instrument: Waveshare DO

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Waveshare DO."""

    description = """
    <h3>Waveshare Digital Output 8CH</h3>
    <p>This driver controls the Waveshare Digital Output 8CH module via Modbus RTU.</p>
    <p><strong>Features:</strong></p>
    <ul>
    <li>8 independent digital output channels</li>
    <li>Modbus RTU communication over RS485</li>
    <li>Configurable Modbus address (default: 1)</li>
    </ul>
    <p><strong>Configuration:</strong></p>
    <ul>
    <li>Set each channel to ON or OFF state</li>
    <li>Default baudrate: 38400, 8N1</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "DO"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 1,
            "baudrate": 38400,
            "stopbits": 1,
            "parity": "N",
            "bytesize": 8,
        }

        self.modbus_address: int = 1

        # Measurement parameters
        self.channel_1: str = "ON"
        self.channel_2: str = "ON"
        self.channel_3: str = "ON"
        self.channel_4: str = "ON"
        self.channel_5: str = "ON"
        self.channel_6: str = "ON"
        self.channel_7: str = "ON"
        self.channel_8: str = "ON"

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "Modbus address": 1,
            "Channel 1": ["ON", "OFF"],
            "Channel 2": ["ON", "OFF"],
            "Channel 3": ["ON", "OFF"],
            "Channel 4": ["ON", "OFF"],
            "Channel 5": ["ON", "OFF"],
            "Channel 6": ["ON", "OFF"],
            "Channel 7": ["ON", "OFF"],
            "Channel 8": ["ON", "OFF"],
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.modbus_address = parameters.get("Modbus address", 1)
        self.channel_1 = parameters.get("Channel 1", "ON")
        self.channel_2 = parameters.get("Channel 2", "ON")
        self.channel_3 = parameters.get("Channel 3", "ON")
        self.channel_4 = parameters.get("Channel 4", "ON")
        self.channel_5 = parameters.get("Channel 5", "ON")
        self.channel_6 = parameters.get("Channel 6", "ON")
        self.channel_7 = parameters.get("Channel 7", "ON")
        self.channel_8 = parameters.get("Channel 8", "ON")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        self.modbus_address = int(self.modbus_address)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        for channel in range(1, 9):
            value = getattr(self, f"channel_{channel}", "ON") == "ON"
            cmd = self.create_command(self.modbus_address, channel, value)
            response = self.port.query(cmd)

    def create_command(self, slave_address: int, channel: int, value: bool) -> bytes:
        """Generate a Modbus RTU command for setting a single register to a bool value."""
        function_code = 5  # Write command
        channel_address = channel - 1  # Map channel 1-8 to register addresses 0-7

        # Build the command payload
        command = bytes([slave_address, function_code])
        command += channel_address.to_bytes(2, byteorder='big')
        # For Modbus FC05, True = 0xFF00, False = 0x0000
        command += (0xFF00 if value else 0x0000).to_bytes(2, byteorder='big')

        # Calculate CRC16
        crc = self.calculate_crc16(command)

        # Append CRC
        command += crc

        return command

    @staticmethod
    def calculate_crc16(data: bytes) -> bytes:
        """Calculate CRC16 for Modbus RTU."""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc = (crc >> 1) ^ 0xA001
                else:
                    crc >>= 1
        # Return as bytes (low byte first, high byte second - little endian)
        return bytes([crc & 0xFF, (crc >> 8) & 0xFF])


