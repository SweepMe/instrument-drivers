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
            0x11: "You can not select the stepper motor type for crystals head ‑ assigned to other channel.",
            0x12: "TM assigned to other crystals head.",
            0x13: "The crystals head must 􀏐irst be calibrated.",
            0x14: "Calibration not available.",
            0x15: "The crystals head does not have an assigned TM channel.",
            0x16: "No assigned relay output.",
            0x17: "You can not select the relay output ‑ assigned to another function.",
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
