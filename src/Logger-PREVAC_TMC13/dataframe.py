class DataFrame:
    def __init__(self, device, host, msb, lsb, data):
        self.device = device
        self.host = host
        self.msb = msb
        self.lsb = lsb
        self.data = data

        self.checksum = None
        self.start_byte = chr(0xBB)

    def get_length(self) -> None:
        """Get the length of the data frame and convert it to a character."""
        self.length = chr(len(self.data))

    def generate_checksum(self) -> None:
        """Generate the checksum for the data frame."""
        message = self.length + self.device + self.host + self.msb + self.lsb + self.data

        checksum = 0
        for char in message:
            checksum += ord(char)
        checksum = checksum % 256
        self.checksum = chr(checksum)

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


    def command_to_write(self):
        self.get_length()
        self.generate_checksum()
        message = self.length + self.device + self.host + self.msb + self.lsb + self.data
        return (self.start_byte + message + self.checksum).encode("latin1")