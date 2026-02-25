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
# * Module: Logger
# * Instrument: Waveshare AI

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Waveshare AI."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "AI"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Voltage"]
        self.units = ["V"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["COM"]

        # Modbus RTU configuration
        self.port_properties = {
            "timeout": 1,
            "baudrate": 38400,
            "stopbits": 1,
            "parity": "N",
            "bytesize": 8,
        }

        self.modbus_address: int = 1

        # Measurement parameters
        self.mode: str = "Voltage in V"
        self.channels: list[int] = [1, 2, 3, 4]

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "Modbus address": 1,
            "Channel": "1,2,3,4",
            "Mode": ["Current in A", "Voltage in V"],
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.modbus_address = parameters["Modbus address"]
        self.mode = parameters.get("Mode", "Voltage in V")

        channels = parameters.get("Channel", "1,2,3,4")
        try:
            self.channels = [int(ch.strip()) for ch in channels.split(",")]
        except:
            self.channels = []

        self.variables = [f"Ch {num}" for num in self.channels]
        self.units = ["V" if self.mode == "Voltage in V" else "A"] * len(self.channels)
        self.plottype = [True] * len(self.channels)
        self.savetype = [True] * len(self.channels)

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        try:
            self.modbus_address = int(self.modbus_address)
        except ValueError:
            msg = f"Invalid Modbus address: {self.modbus_address}. Must be an integer."
            raise ValueError(msg)

    def call(self) -> list:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        results = []
        for channel in self.channels:
            voltage = self.read_channel(channel)
            if self.mode == "Current in A":
                current = voltage / 5 * 20  # 20A/5V
                results.append(current)
            else:
                results.append(voltage)

        return results

    def read_channel(self, channel: int) -> float:
        """Read the value of the given channel in V, which measures with 1 mV resolution."""
        # Waveshare AI channel mapping: channel 1 = register 0, channel 2 = register 1, etc.
        register_address = channel - 1

        cmd = self.generate_read_command(
            slave_address=self.modbus_address,
            function_code=4,  # read input register (FC04)
            register_address=register_address,
            num_registers=1,  # read 1 register (16-bit value)
        )
        print(f"Generated command for channel {channel}: {cmd.hex()}")
        response = self.port.query(cmd)

        # Validate response length
        # Response structure: [slave_addr][func_code][byte_count][data...][CRC_low][CRC_high]
        # For 1 register: [addr][0x04][0x02][high_byte][low_byte][CRC][CRC] = 7 bytes
        if len(response) < 5:
            msg = f"Invalid response length: {len(response)} bytes, expected at least 5"
            raise ValueError(msg)

        # Extract the 16-bit value from bytes 3-4 (after addr, func_code, byte_count)
        word = response[3:5]
        value = int.from_bytes(word, byteorder='big')
        return value / 1000  # Convert from mV to V

    def generate_read_command(self, slave_address: int, function_code: int, register_address: int,
                              num_registers: int) -> bytes:
        """
        Generate a Modbus RTU command for reading registers.

        Args:
            slave_address: Modbus slave address (1-247)
            function_code: Modbus function code (e.g., 0x04 for read input registers)
            register_address: Starting register address to read from
            num_registers: Number of registers to read

        Returns:
            Complete Modbus RTU command with CRC16 checksum
        """
        command = bytes([slave_address, function_code])
        command += register_address.to_bytes(2, byteorder='big')
        command += num_registers.to_bytes(2, byteorder='big')
        command += self.calculate_crc16(command)
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

