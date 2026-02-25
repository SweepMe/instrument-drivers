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
# * Module: Temperature
# * Instrument: JUMO diraTRON

from __future__ import annotations

import struct

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice





class Device(EmptyDevice):
    """Driver for the JUMO diraTRON."""

    description = """
    Works for JUMO diraTRON 104/108/116/132
    - Channel corresponds to the Modbus RTU address
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "diraTRON"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = [
            "Controller Setpoint",  # Sollwert
            "Controller Actual",  # Istwert
            "Control Deviation",  # Regelabweichung
            "Output Level",  # Stellgradanzeige
        ]
        self.units = [""] * len(self.variables)
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

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
        self.sweep_mode: str = "None"

        self.temperature_setpoint: float = 0.0
        self.current_temperature: float = 0.0
        self.temperature_difference: float = 0.0
        self.output_power_percent: float = 0.0

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ['None', 'Setpoint in °C'],
            "Channel": 1,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.modbus_address = parameters.get("Channel", 1)

    def connect(self):
        """Connect to the device."""
        try:
            self.modbus_address = int(self.modbus_address)
        except ValueError:
            msg = f"Invalid Modbus address: {self.modbus_address}. Must be an integer."
            raise ValueError(msg)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweep_mode.startswith("Setpoint"):
            self.set_setpoint(float(self.value))

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        self.read_registers()
        return [
            self.temperature_setpoint,
            self.current_temperature,
            self.temperature_difference,
            self.output_power_percent,
        ]

    # Wrapper functions

    def set_setpoint(self, setpoint: float) -> None:
        """Set the controller setpoint."""
        cmd = self.generate_set_register_command(
            slave_address=self.modbus_address,
            register_address=8468,  # register for the temperature setpoint
            register_value=setpoint,
        )
        print(f"Generated setpoint command: {cmd}")
        response = self.port.query(cmd)
        # TODO: Handle response, check for success, etc.

    def read_registers(self) -> None:
        """Read the 4 relevant 4-byte float values from the device and store them in instance variables."""
        cmd = self.generate_read_command(
            slave_address=self.modbus_address,
            function_code=3,  # read holding registers
            register_address=28688,  # starting register for setpoint, other values follow
            num_registers=8,  # read 8 registers to get all 4 float values (2 registers per float)
        )
        print(f"Sending Read command: {' '.join(f'{byte:02X}' for byte in cmd)}")
        self.port.write(cmd)
        # time.sleep(0.1)  # wait for response

        response = self.port.read(32)  # read up to 32 bytes
        # response = b'\x01\x03\x10\x00\x00B\xc8\x1bLA\xbb9-B\x99\x00\x00B\xc8\xffu'
        print(f"Received response: {response.hex().upper()}")

        # Extract the data payload (skip address, function code, byte count)
        data_start = 3

        # Parse 4 float32 values with word-swapped byte order
        # Each float32 is 4 bytes, but words (2-byte pairs) are swapped
        values = []
        for i in range(4):
            offset = data_start + (i * 4)
            # Get 4 bytes: [0, 1, 2, 3] but they're stored as [2, 3, 0, 1]
            # So we need to swap the word order: read bytes 2,3,0,1
            word1 = response[offset + 2:offset + 4]  # bytes 2,3
            word0 = response[offset:offset + 2]  # bytes 0,1
            # Reconstruct in correct order: word0, word1 (which is bytes 2,3,0,1)
            float_bytes = word1 + word0
            # Unpack as big-endian float
            value = struct.unpack('>f', float_bytes)[0]
            values.append(value)

        self.current_temperature = values[1]
        self.temperature_difference = values[2]
        self.temperature_setpoint = values[0]
        self.output_power_percent = values[3]

    def generate_read_command(self, slave_address: int, function_code: int, register_address: int,
                              num_registers: int) -> bytes:
        """
        Generate a Modbus RTU command for reading registers.

        Args:
            slave_address: Modbus slave address (1-247), typically matches the channel
            function_code: Modbus function code (e.g., 0x03 for read holding registers)
            register_address: Starting register address to read from
            num_registers: Number of registers to read)
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

    def generate_set_register_command(
            self,
            slave_address: int,
            register_address: int,
            register_value: float,
    ) -> bytes:
        """Generate a Modbus RTU command for setting a single register to a float value."""
        function_code = 0x10  # Write command
        num_registers = 0x0002  # 2 for float32
        byte_count = num_registers * 2  # 4 bytes for 2 registers

        # The JUMO device uses word-swapped byte order for float values
        # Bytes come in as [0, 1, 2, 3] but need to be sent as [2, 3, 0, 1]
        float_bytes = struct.pack('>f', register_value)
        swapped_float_bytes = self.swap_bytes(float_bytes)

        # Build the command payload
        command = bytes([slave_address, function_code])
        command += register_address.to_bytes(2, byteorder='big')  # Register address 0x2114 -> 21 14
        command += num_registers.to_bytes(2, byteorder='big')
        command += byte_count.to_bytes(1, byteorder='big')
        command += swapped_float_bytes

        # Calculate CRC16
        crc = self.calculate_crc16(command)

        # Append CRC
        command += crc

        return command

    @staticmethod
    def swap_bytes(data: bytes) -> bytes:
        """
        Swap bytes in pairs for word-swapped order.

        The input [0, 1, 2, 3] becomes [2, 3, 0, 1].
        """
        if len(data) != 4:
            raise ValueError("Data must be exactly 4 bytes for float32 swapping")

        swapped = bytearray(4)
        swapped[0] = data[2]  # byte 2 goes to position
        swapped[1] = data[3]  # byte 3 goes to position
        swapped[2] = data[0]  # byte 0 goes to position
        swapped[3] = data[1]  # byte 1 goes to position

        return bytes(swapped)
