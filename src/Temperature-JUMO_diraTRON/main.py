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
    - Channel corresponds to the Modnbus RTU address
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "diraTRON"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = [
            # "Analog Input",
            "Controller Setpoint",  # Sollwert
            "Controller Actual",  # Istwert
            "Control Deviation",  # Regelabweichung
            "Output Level",  # Stellgradanzeige
            # "Analog Output"
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
            "baudrate": 9600,
            "stopbits": 1,
            "parity": "N",
            "bytesize": 8,
            "EOL": "",  # Modbus RTU does not use EOL characters
        }
        self.modbus_address: int = 1

        # Measurement parameters
        self.sweep_mode: str = "None"

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ['None', 'Setpoint in °C'],
            "Modbus address": 1,
            "Channel": 1,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.modbus_address = parameters.get("Modbus address", 1)

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
        setpoint = self.get_setpoint()
        actual = self.get_actual_value()
        deviation = self.get_control_deviation()
        output_level = self.get_output_level()

        return [
            # self.analog_input,
            setpoint,
            actual,
            deviation,
            output_level,
            # self.analog_output,
        ]

    # Wrapper functions

    def set_setpoint(self, setpoint: float) -> None:
        """Set the controller setpoint."""
        self.write_float(0x7002, setpoint)

    def get_setpoint(self) -> float:
        """Get the controller setpoint (Regler Sollwert)."""
        return self.read_float(0x7002)

    def get_actual_value(self) -> float:
        """Get the controller actual value (Regler IstWert)."""
        return self.read_float(0x7012)

    def get_control_deviation(self) -> float:
        """Get the control deviation (Regler Differenz)."""
        return self.read_float(0x7014)

    def get_output_level(self) -> float:
        """Get the output level (Regler Stellgradanzeige)."""
        return self.read_float(0x7016)

    # Modbus RTU functions

    def read_float(self, address: int) -> float:
        """Reads a FLOAT (2 words) from the given Modbus address"""
        request = self.build_request_read(address, 2)
        self.port.write_raw(request)
        response: bytes = self.port.read_bytes(9)
        raw = response[3:7]
        reordered = raw[2:4] + raw[0:2]
        return struct.unpack(">f", reordered)[0]

    def write_float(self, address: int, value: float) -> None:
        """Writes a FLOAT (2 words) to the given Modbus address"""
        packed = struct.pack(">f", value)
        reordered = packed[2:4] + packed[0:2]
        data = list(reordered)
        request = self.build_request_write_n_words(address, data)
        self.port.write_raw(request)
        self.port.read_bytes(8)  # read ack

    def build_request_read(self, address: int, num_words: int) -> bytes:
        """Builds a Modbus RTU request to read 'num_words' words starting from 'address'."""
        data = [
            self.modbus_address,
            0x03,
            (address >> 8) & 0xFF,
            address & 0xFF,
            (num_words >> 8) & 0xFF,
            num_words & 0xFF,
        ]
        crc = self.crc16(data)
        return bytes(data + crc)

    def build_request_write_n_words(self, address: int, byte_data: list[int]) -> bytes:
        word_count = len(byte_data) // 2
        data = [
            self.modbus_address,
            0x10,
            (address >> 8) & 0xFF,
            address & 0xFF,
            (word_count >> 8) & 0xFF,
            word_count & 0xFF,
            len(byte_data),
        ] + byte_data
        crc = self.crc16(data)
        return bytes(data + crc)

    @staticmethod
    def crc16(data: list[int]) -> list[int]:
        """CRC16 (Modbus RTU) calculation"""
        crc = 0xFFFF
        for pos in data:
            crc ^= pos
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return [crc & 0xFF, (crc >> 8) & 0xFF]
