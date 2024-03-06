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

from __future__ import annotations

import struct


class PrevacCommunicationInterface:
    """Class for the communication interface to the Prevac TMC13 device using the Prevac V2.x protocol."""

    def __init__(self, port, host_address: str, channel: str) -> None:
        """Initialize the communication interface."""
        self.port = port
        self.device_address = chr(0x01)
        self.host_address = host_address
        self.channel = channel

        self.start_byte = chr(0xBB)

    def send_data_frame(self, command: int, data: str = "") -> None:
        """Send a Prevac V2.x Protocol data frame to the device.

        Code is an integer of hex format 0x0202 and corresponds to the command
        data is the data that is sent in addition to the command.
        """
        dataframe = SendingDataFrame(
            device=ord(self.device_address),
            host=ord(self.host_address),
            command=command,
            data=data,  # TODO: test if data is a string
        )

        self.port.write(dataframe.command_to_write)

    def receive_data_frame(self) -> bytes:
        """Receive a Prevac V2.x Protocol data frame from the device."""
        header = self.port.read(1)[0]

        if header != ord(self.start_byte):
            msg = f"PREVAC TMC13: Returned message does not start with correct byte {self.start_byte}"
            raise Exception(msg)

        # Read Data Frame
        length = self.port.read(1)  # should be already int because of indexing
        device = self.port.read(1)
        host = self.port.read(1)
        msb = self.port.read(1)
        lsb = self.port.read(1)
        data = self.port.read(length[0])
        checksum = self.port.read(1)

        dataframe = ReceivingDataFrame(
            device=device,
            host=host,
            msb=msb,
            lsb=lsb,
            data=data,
            checksum=checksum,
        )
        dataframe.check_checksum()

        if self.port.in_waiting() > 0:
            msg = f"PREVAC TMC13: There are still Bytes in waiting: {self.port.in_waiting()}."
            raise Exception(msg)

        return data

    """
    The Following functions enable conversion of the received data to the expected format.

    Some calls such as get_device_number might return forbidden characters such as "0x00", which need to be handled.
    """

    def get_double_value(self, command: int) -> float:
        """Return a double value ignoring the channel number."""
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame()
        # Channel number is missing in the answer at position 0
        return struct.unpack(">d", answer[:9])[0]

    def get_double_value_and_channel(self, command: int) -> tuple[int, float]:
        """Return a double value if the answer contains the channel."""
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame()
        channel = answer[0]
        double = struct.unpack(">d", answer[1:9])[0]
        return channel, double

    def get_byte_value(self, command: int) -> int:
        """Return a byte value."""
        self.send_data_frame(command, self.channel)
        return self.receive_data_frame()[0]

    def get_byte_value_and_channel(self, command: int) -> tuple[int, int]:
        """Return a byte value if the answer contains the channel."""
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame()
        channel = answer[0]
        byte_value = answer[1]
        return channel, byte_value

    def check_response_for_errors(self) -> bytes:
        """Read out the response after a setter function and check the data for error codes."""
        error_codes = {
            b"\x91": "Value is too large",
            b"\x92": "Value is too small",
            b"\x93": "Wrong parameter (probably wrong data format or index out of range)",
            b"\x95": "Read only parameter, write prohibited",
            b"\x96": "Host not know and not registered",
            b"\x97": "Host know but not selected to remote control",
            b"\x98": "Device configured to work in local mode",
            b"\x99": "Operation or parameter is not available",
        }

        answer = self.receive_data_frame()
        error_code = bytes(answer[-1:])
        if error_code in error_codes:
            msg = error_codes[error_code]
            raise Exception(msg)

        return answer

    def check_error_status(self) -> None:
        """Check the device status for errors."""
        # TODO: Check if error index needs to be sent as value
        command = 0x7F51
        self.send_data_frame(command)
        answer = self.receive_data_frame()
        # TODO: Check return type
        error = answer[1:]

        error_codes = {
            0x7F01: "Internal communication error",
            0x7F02: "Communication with Anybus module error",
            0x7F03: "Communication with Bluetooth Anybus module error",
            0x7F04: "Critically low disk space",
            # TMC13 Status Codes Page 144:
            0x4101: "DC module is not available",
            0x4102: "The connection to Bus has been lost.",
            0x4103: "DC power supply is damaged or short circuit",
            0x4104: "HV power supply is damaged.",
            0x4105: "HV power supply has short circuit.",
            0x4106: "Main power failure.",
            0x4107: "Safety relay failure",
            # Communication Error Codes page 145: - Maybe called with 0x0216
            0x10: "Crystals head during movement.",
            0x11: "You can not select the stepper motor type for crystals head - assigned to other channel.",
            0x12: "TM assigned to other crystals head.",
            0x13: "The crystals head must 􀏐irst be calibrated.",
            0x14: "Calibration not available.",
            0x15: "The crystals head does not have an assigned TM channel.",
            0x16: "No assigned relay output.",
            0x17: "You can not select the relay output - assigned to another function.",
            0x18: "Parameter for a different type of magazine.",
            # Vacuum Gauges Communication Error Codes page 145:
            0x80: "CTR90 head not selected to set FS.",
            0x81: "MKS870 head not selected to set FS.",
            0x82: "Not selected -define- gas type.",
            0x83: "Meter damaged.",
            0x84: "Selected head does not support degas function.",
            0x85: "Vacuum is too low to start system degassing.",
            0x86: "Selected head does not support emission function.",
        }

        if error in error_codes:
            msg = "Prevac Error: " + error_codes[error]
            raise Exception(msg)

    def check_warning_status(self) -> None:
        """Check the device status for warnings."""
        command = 0x7F52
        self.send_data_frame(command)
        answer = self.receive_data_frame()
        # TODO: Check return type
        warning = answer[1:]

        warning_codes = {
            0x7F80: "Low disk space",
            0x7F06: "Invalid read the internal temperature of the device.",
            0x7F07: "The internal temperature of the device is above safe level.",
            0x7F08: "The internal temperature of the unit is too high. Switching to standby mode.",
            # TMC13 Status Codes Page 144:
            0x4180: "DC no load or the connection is broken.",
            0x4181: "DC current has reached the limit.",
            0x4182: "Emission current has reached the limit.",
            0x4183: "No external interlock.",
            0x4184: "No vacuum interlock.",
        }

        if warning in warning_codes:
            msg = "Prevac Warning: " + warning_codes[warning]
            raise Exception(msg)


class DataFrame:
    """Base class for the PREVAC V2.x Communication Protocol data frame."""

    def __init__(self) -> None:
        """Initialize the data frame. Set everything to 0."""
        # Make everything int and convert to char when needed
        self.host: int = 0x00
        self.device: int = 0x00
        self.command: int = 0x00
        self.data: int = 0x00

        self.msb: int = 0x00
        self.lsb: int = 0x00

        self.length: int = 0x00
        self.checksum: int = 0x00

        self.start_byte = 0xBB

    def generate_checksum(self) -> None:
        """Generate the checksum for the data frame."""
        message_content = [
            self.length,
            self.device,
            self.host,
            self.msb,
            self.lsb,
            *self.data,  # unpack list
        ]
        checksum = 0

        for char in message_content:
            checksum += char

        self.checksum = checksum % 256


class SendingDataFrame(DataFrame):
    """Class for sending. Inherits from DataFrame."""

    def __init__(self, device: int, host: int, command: int, data: [int]) -> None:
        """Initialize the sending data frame."""
        super().__init__()

        self.device = device
        self.host = host
        self.command = command
        self.data = data

        self.generate_length()
        self.generate_msb_lsb()
        self.generate_checksum()

        self.command_to_write: bytes
        self.generate_command_to_write()

    def generate_length(self) -> None:
        """Get the length of the data frame and convert it to a character."""
        self.length = len(self.data)

    def generate_msb_lsb(self) -> None:
        """Generate the most significant and least significant byte for the command."""
        _msb, _lsb = struct.pack(">H", self.command)
        self.msb = _msb
        self.lsb = _lsb

    def generate_command_to_write(self) -> None:
        """Generate the command to write to the TMC13.

        1 - HEADER: First byte is responsible for identifying the serial protocol.
        Header in hexadecimal is 0xBB
        2 - DATA LENGTH: Length of the data field. Maximum data file length is 0xFF
        (256 bytes). Prevac Serial Protocol
        3 - DEVICE ADDRESS: Identification of hardware device address. Default value is 0xC8
        4 - HOST ADDRESS: Host identification address. Assigned to host during the registration process
        (using a unique ID).
        5 - FUNCTION CODE: - MSB First procedure function code byte
        8th (MSB) bit is the read(0)/write(1) select bit
        6 - FUNCTION CODE: - LSB Second procedure function code byte
        [7 + DATA LENGTH] - DATA FIELD: Data capture needed to realize defined functions.
        [7 + DATA LENGTH] + 1(last frame position) - CRC: CRC is simple module 256 calculated without protocol header
        byte (see section 6.5.2.4).
        """
        self.generate_length()
        self.generate_checksum()

        message_components = [
            self.start_byte,
            self.length,
            self.device,
            self.host,
            self.msb,
            self.lsb,
            *self.data,  # unpack list
            self.checksum,
        ]

        message = b""
        for component in message_components:
            message += chr(component).encode("latin1")

        self.command_to_write = message


class ReceivingDataFrame(DataFrame):
    """Class for receiving. Inherits from DataFrame."""

    def __init__(self, device: bytes, host: bytes, msb: bytes, lsb: bytes, data: bytearray, checksum: bytes) -> None:
        super().__init__()
        self.host = host[0]
        self.device = device[0]
        self.msb = msb[0]
        self.lsb = lsb[0]
        self.data = data  # How to transform to int?
        self.received_checksum = checksum[0]

    def check_checksum(self) -> None:
        """Check if the checksum is correct and raise an exception if it is not."""
        self.generate_checksum()

        if self.checksum != self.received_checksum:
            msg = "PREVAC TMC13: Checksums do not match"
            raise Exception(msg)

    def check_error_code(self) -> None:
        """Check if the error code is in the list of PREVAC error codes and raise an exception if it is."""
        error_codes = {
            b"\x91": "Value is too large",
            b"\x92": "Value is too small",
            b"\x93": "Wrong parameter (probably wrong data format or index out of range)",
            b"\x95": "Read only parameter, write prohibited",
            b"\x96": "Host not know and not registered",
            b"\x97": "Host know but not selected to remote control",
            b"\x98": "Device configured to work in local mode",
            b"\x99": "Operation or parameter is not available",
        }

        error_code = bytes(self.data[-1:])
        if error_code in error_codes:
            msg = error_codes[error_code]
            raise Exception(msg)
