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
    <p>This driver controls Prevac TM13 or TM14 thickness controller.</p>
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
            10: 1,
            4: 2,
            2: 3,
            1: 4,
            0.5: 5,
        }

        # Default Communication Parameters
        self.header = 0xAA
        self.device_address = 0xC8
        self.device_group = 0xA1
        self.logic_group = 0xC8
        self.driver_address = 0x01

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        return {
            "Device": ["TM13", "TM14"],
            "Sample rate in Hz": [10, 4, 2, 1, 0.5],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        self.device_version = parameter["Device"]

        if self.device_version == "TM14":
            self.sample_rate = parameter["Sample rate in Hz"]
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

    """ Getter Functions """

    def get_frequency(self) -> float:
        """Request current frequency in Hz."""
        command = 0x53

        _sample_rate = self.sample_rate_dict[self.sample_rate]
        data = f"{_sample_rate}000"

        self.send_dataframe(command, data)

        response = self.get_dataframe()

        frequency = response[:4]
        response[4]  # 1 microbalance correction connected, 2 not
        response[5]  # measurements are numbered from 0 to 255
        response[6:7]  # duration of the measurement in ms
        response[7]  # 13 for TM13, 14 for TM14

        return frequency / 100

    """ Communication Functions """

    def send_dataframe(self, function_code: int, data: str = "") -> None:
        """Generate the data frame and send it to the device."""
        length = len(data)
        checksum = self.calculate_checksum(
            [
                self.device_address,
                self.device_group,
                self.logic_group,
                self.driver_address,
                function_code,
                length,
                *data,  # Unpack the data field
            ],
        )

        message = [
            self.header,
            length,
            self.device_address,
            self.device_group,
            self.logic_group,
            self.driver_address,
            function_code,
            *data,  # Unpack the data field
            checksum,
        ]

        self.port.write(message)

    @staticmethod
    def calculate_checksum(contents: list[int]) -> int:
        """Generate the checksum for the data frame."""
        checksum = 0
        for char in contents:
            checksum += char

        return checksum % 256

    def get_dataframe(self) -> bytes:
        """Get the response from the device."""
        header = self.port.read(1)[0]

        if header != self.header:
            msg = f"PREVAC TM1x: Header does not match. {self.header} != {header}"
            raise Exception(msg)

        length = self.port.read(1)[0]
        driver_address = self.port.read(1)[0]
        device_group = self.port.read(1)[0]
        logic_group = self.port.read(1)[0]
        device_address = self.port.read(1)[0]
        function_code = self.port.read(1)[0]

        data = self.port.read(length[0])
        received_checksum = self.port.read(1)[0]
        calculated_checksum = self.generate_checksum([
            driver_address,
            device_group,
            logic_group,
            device_address,
            function_code,
            length,
            *data,
        ])

        if received_checksum != calculated_checksum:
            msg = f"PREVAC TM1x: Checksums do not match. {self.checksum} != {self.received_checksum}"
            raise Exception(msg)

        if self.port.in_waiting() > 0:
            msg = f"PREVAC TM1x: There are still Bytes in waiting: {self.port.in_waiting()}."
            raise Exception(msg)

        return data
