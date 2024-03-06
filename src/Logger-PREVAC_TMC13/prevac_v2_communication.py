from __future__ import annotations

import struct

from dataframe import ReceivingDataFrame, SendingDataFrame


class PrevacCommunicationInterface:
    """Class for the communication interface to the Prevac TMC13 device."""

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
