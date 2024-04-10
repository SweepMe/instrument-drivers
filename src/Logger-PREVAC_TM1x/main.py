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
# Device: PREVAC TM1x
from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the PREVAC TM13 or TM14 Thickness Monitor."""

    description = """
    <h3>Prevac TMC1x</h3>
    <p>This driver controls Prevac TM13 or TM14 thickness monitor.</p>
    <p>Sample rate only for TM14</p>
    """

    def __init__(self) -> None:
        """Initialize the device class."""
        super().__init__()

        # Port Parameters
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "baudrate": 57600,  # default
            "stopbits": 1,
            # "parity": "N",
        }

        # SweepMe Parameters
        self.shortname = "TM1x"
        self.variables = ["Frequency"]
        self.units = ["Hz"]
        self.plottype = [True]
        self.savetype = [True]

        # Device Parameter
        self.device_version: str = ""
        self.sample_rate: int = 4
        self.sample_rate_dict = {
            "10": 1,
            "4": 2,
            "2": 3,
            "1": 4,
            "0.5": 5,
        }

        # Default Communication Parameters
        self.header = 0xAA
        self.device_address = 0xC8
        self.device_group = 0xA1  # 0xA1 for TM13 and TM14
        self.logic_group = 0xC8
        self.driver_address = 0x01

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        return {
            "Model": ["TM13", "TM14"],
            "Sample rate in Hz": [10, 4, 2, 1, 0.5],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        self.device_version = parameter["Model"]

        if self.device_version == "TM14":
            self.sample_rate = self.sample_rate_dict[parameter["Sample rate in Hz"]]
        else:
            self.sample_rate = 4  # TM13 standard sample rate

    def connect(self) -> None:
        """Enable Remote Control on the device."""
        # TODO: Add device address and set_device_address command

    def disconnect(self) -> None:
        """End the remote control mode on the device."""

    def initialize(self) -> None:
        """Get frequency range."""

    def configure(self) -> None:
        """Reset thickness if needed and set material properties."""

    def call(self) -> float:
        """Return the current frequency."""
        return self.get_frequency()

    """ Device Functions """

    def get_frequency(self) -> float:
        """Request current frequency in Hz.

        response[:4]    frequency in Hz with 0.01 Hz resolution
        response[4]     1 microbalance correction connected, 2 not
        response[5]     measurements are numbered from 0 to 255
        response[6:7]   duration of the measurement in ms
        response[7]     13 for TM13, 14 for TM14
        """
        command = 0x53
        data = [self.sample_rate, 0, 0, 0]

        self.send_dataframe(command, data)
        response = self.get_dataframe()

        frequency_bytes = response[:4].encode("latin-1")
        frequency = int.from_bytes(frequency_bytes, "big")

        return frequency / 100

    """ Communication Functions """

    def send_dataframe(self, function_code: int, data: [int]) -> None:
        """Generate the data frame and send it to the device."""
        # data_int = [int(symbol) for symbol in data]  # convert to [int]
        data_int = data
        length = len(data)

        # Calculate the checksum
        checksum = self.calculate_checksum(
            [
                self.device_address,
                self.device_group,
                self.logic_group,
                self.driver_address,
                function_code,
                length,
                *data_int,  # Unpack the data field
            ],
        )

        # Generate the message as bytes
        message = b""
        for char in [
            self.header,
            length,
            self.device_address,
            self.device_group,
            self.logic_group,
            self.driver_address,
            function_code,
            *data_int,  # Unpack the data field
            checksum,
        ]:
            message += chr(char).encode("latin1")

        # print(message)
        self.port.write(message)

    @staticmethod
    def calculate_checksum(contents: list[int]) -> int:
        """Generate the checksum for the data frame."""
        checksum = 0
        for char in contents:
            checksum += char

        return checksum % 256

    def get_dataframe(self) -> str:
        """Get the response from the device."""
        message = self.port.read()
        header = message[0]
        if ord(header) != self.header:
            msg = f"PREVAC TM1x: Header does not match. {self.header} != {header}"
            raise Exception(msg)

        length = ord(message[1])

        data = message[7:7+length]

        # Checksum is not working, some commands do not return a checksum
        # received_checksum = ord(message[-1])
        # calculated_checksum = self.calculate_checksum([ord(char) for char in message[2:-2]])
        #
        # if received_checksum != calculated_checksum:
        #     msg = f"PREVAC TM1x: Checksums do not match. {received_checksum} != {calculated_checksum}"
        #     raise Exception(msg)

        if self.port.in_waiting() > 0:
            msg = f"PREVAC TM1x: There are still {self.port.in_waiting()} Bytes in waiting."
            raise Exception(msg)

        return data

    """ Currently unused functions """

    def set_device_address(self, address: int) -> None:
        """Set the device address."""
        command = 0x58
        min_address = 1
        max_address = 254
        if address < min_address or address > max_address:
            msg = f"PREVAC TM1x: Address must be between {min_address} and {max_address}."
            raise ValueError(msg)

        data = f"000{chr(address)}"
        data = [0, 0, 0, address]
        self.device_address = 0xFF
        self.send_dataframe(command, data)
        response = self.get_dataframe()
        print(response)

    def set_logic_group(self, group: int) -> None:
        """Set the logic group."""
        command = 0x59
        min_group = 0
        max_group = 254
        if group < min_group or group > max_group:
            msg = f"PREVAC TM1x: Group must be between {min_group} and {max_group}."
            raise ValueError(msg)

        data = f"000{group}"
        data = [0, 0, 0, group]
        self.send_dataframe(command, data)

        response = self.get_dataframe()
        print(response)

    def get_product_number(self) -> str:
        """Request the product number."""
        command = 0xFD
        data = "0000"
        data = [0, 0, 0, 0]
        self.send_dataframe(command, data)

        return self.get_dataframe()

    def get_serial_number(self) -> str:
        """Request the serial number."""
        command = 0xFE
        data = "0000"
        data = [0, 0, 0, 0]
        self.send_dataframe(command, data)

        return self.get_dataframe()