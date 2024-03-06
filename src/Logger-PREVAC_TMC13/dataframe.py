import struct


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
