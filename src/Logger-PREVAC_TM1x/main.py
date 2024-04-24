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

import time

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the PREVAC TM13 or TM14 Thickness Monitor."""

    description = """
    <h3>Prevac TMC1x</h3>
    <p>This driver controls Prevac TM13 or TM14 thickness monitors.</p>
    <h4>Parameters</h4>
    <ul>
    <li>The sample rate can only be set for TM14.</li>
    </ul>
    """

    actions = ["reset_thickness"]  # Enables the reset_thickness action in the GUI

    def __init__(self) -> None:
        """Initialize the device class."""
        super().__init__()

        # Port Parameters
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "baudrate": 57600,  # default
            "stopbits": 1,
            "parity": "N",
            "timeout": 2.5,  # in case sampling rate is 0.5 Hz
        }

        # SweepMe Parameters
        self.shortname = "TM1x"
        self.variables = ["Frequency", "Thickness", "Rate", "XTAL life"]
        self.units = ["Hz", "nm", "A/s", "%"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        # Device Parameter
        self.device_version: str = ""
        self.sample_rate: float = 1.0
        self.sample_rate_dict = {
            "10.0": 1,
            "4.0": 2,
            "2.0": 3,
            "1.0": 4,
            "0.5": 5,
        }

        self.frequency_max: float = 6.0
        self.frequency_min: float = 5.2
        self.tooling_factor: float = 1.0

        # Default Communication Parameters
        self.header = 0xAA
        self.device_address = 0xC8
        self.device_group = 0xA1  # 0xA1 for TM13 and TM14
        self.logic_group = 0xC8
        self.driver_address = 0x01

        # Material Properties
        self.initial_frequency: int = 0
        self.material_density: float = 0  # g/cm^3
        self.impedance_ratio: float = 1.0

        self.previous_thickness: float = 0
        self.previous_time: float = 0
        self.previous_rate: float = 0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        return {
            "TM14 sample rate in Hz": list(self.sample_rate_dict),
            "Material density in g/cm^3": 1.0,
            "Impedance ratio": 1.0,
            "Tooling factor": 1.0,
            "Max frequency in MHz": 6.0,
            "Min frequency in MHz": 5.2,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        self.sample_rate = float(parameter["TM14 sample rate in Hz"])

        self.material_density = float(parameter["Material density in g/cm^3"])
        self.impedance_ratio = float(parameter["Impedance ratio"])
        self.tooling_factor = float(parameter["Tooling factor"])

        self.frequency_max = float(parameter["Max frequency in MHz"])
        self.frequency_min = float(parameter["Min frequency in MHz"])

    def initialize(self) -> None:
        """Get initial frequency."""
        self.device_version = self.get_device_version()
        self.reset_thickness()

        if self.initial_frequency == 0:
            msg = "PREVAC TM1x: Initial frequency is 0. Check the connection to crystal head."
            raise Exception(msg)

    def call(self) -> (float, float):
        """Return the current frequency."""
        frequency = self.get_frequency()

        thickness = self.calculate_thickness(
            frequency,
            self.initial_frequency,
            self.material_density,
            self.impedance_ratio,
        )
        thickness *= self.tooling_factor

        rate = self.calculate_rate(thickness)
        crysta_life = self.calculate_crysta_life(frequency)

        return [frequency, thickness, rate, crysta_life]

    """ Device Functions """

    def get_device_version(self) -> int:
        """Get the device version from the response to get_frequency."""
        # Send a dummy request for the sample rate to get the device version
        command = 0x53
        _rate = self.sample_rate_dict[str(self.sample_rate)]
        data = [_rate, 0, 0, 0]

        self.send_dataframe(command, data)
        response = self.get_dataframe()
        print(f"Device version response: {response}")
        print(f"Device version: {response[7]}")

        return response[7]

    def get_frequency(self) -> float:
        """Request current frequency in Hz.

        response[:4]    frequency in Hz with 0.01 Hz resolution
        response[4]     1 microbalance correction connected, 2 not
        response[5]     measurements are numbered from 0 to 255
        response[6:7]   duration of the measurement in ms
        response[7]     13 for TM13, 14 for TM14
        """
        command = 0x53

        tm14 = 14
        standard_rate = 4  # Byte value key for 1 Hz standard rate
        _rate = self.sample_rate_dict[str(self.sample_rate)] if self.device_version == tm14 else standard_rate
        data = [_rate, 0, 0, 0]

        self.send_dataframe(command, data)
        response = self.get_dataframe()

        frequency_bytes = response[:4].encode("latin-1")
        frequency = int.from_bytes(frequency_bytes, "big")

        return frequency / 100

    @staticmethod
    def calculate_thickness(
        frequency: float,
        initial_frequency: float,
        density_material: float,
        impedance_ratio: float,
    ) -> float:
        """Calculate the thickness from the frequency using Sauerbreys equation."""
        freq_constant = 1.668e5  # Hz * cm
        density_quartz = 2.648  # g/cm^3

        normalization = (
            density_quartz * freq_constant / (np.pi * density_material * impedance_ratio * initial_frequency)
        )
        ratio = np.arctan(impedance_ratio * np.tan(np.pi * (frequency - initial_frequency) / frequency))

        # TODO: Check unit
        # Convert from cm to nm
        return normalization * ratio * 1e7 * -1

    def reset_thickness(self) -> None:
        """Reset thickness by updating initial frequency."""
        self.initial_frequency = self.get_frequency()

    def calculate_rate(self, thickness: float) -> float:
        """Calculate the rate of the thickness change in A/s."""
        # TODO: Check if the device measures without given command at every sample rate interval.
        # If yes, the rate should be calculated using the sample rate instead of the time stamp if time stamp is smaller
        time_stamp = time.time()

        # First measurement or after reset_thickness
        if self.previous_thickness == 0 or self.previous_time == 0:
            rate = 0
            self.previous_time = time_stamp

        # Time stamp is the same as the previous time stamp, would give division by 0 error.
        elif time_stamp == self.previous_time:  # noqa: SIM114
            rate = self.previous_rate

        # If calculate_rate is called faster than the sampling rate of the device, the thickness does not change.
        # This would lead to a rate of 0. To avoid this, the rate is set to the previous rate.
        elif thickness == self.previous_thickness and time_stamp - self.previous_time < 1 / self.sample_rate:
            rate = self.previous_rate

        #  Standard case. Set previous_time to the time stamp of the current measurement.
        else:
            rate = (thickness - self.previous_thickness) / (time_stamp - self.previous_time)
            rate *= 10  # nm/s -> A/s
            self.previous_time = time_stamp

        self.previous_thickness = thickness
        self.previous_rate = rate

        return rate

    def calculate_crysta_life(self, frequency: float) -> float:
        """Calculate the crystal life in %."""
        frequency_mhz = frequency / 1e6
        life = (frequency_mhz - self.frequency_min) / (self.frequency_max - self.frequency_min) * 100.0

        return round(life, 2)

    """ Communication Functions """

    def send_dataframe(self, function_code: int, data: [int]) -> None:
        """Generate the data frame and send it to the device."""
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

        print(f"Sent message: {message}")

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

        # Problem is that self.port.read() uses rstrip to remove trailing whitespaces, LF/CR or tab characters
        # TODO: use of self.port.read_raw() instead of self.port.read()
        # TODO: or use of self.port_properties["rstrip"] = False
        # TODO: or use of self.port_properties["raw_read"] = True
        # TODO: bytewise reading of the protocol

        header = self.port.read_raw(1)
        if ord(header) != self.header:
            msg = f"PREVAC TM1x: Header does not match. {self.header} != {header}"
            raise Exception(msg)

        length = self.port.read_raw()
        length = ord(length)

        data = self.port.read_raw(length)

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

    """ Currently unused functions. """

    def get_product_number(self) -> str:
        """Request the product number. Works without connected crystal head."""
        command = 0xFD
        data = [0, 0, 0, 0]
        self.send_dataframe(command, data)

        return self.get_dataframe()

    def get_serial_number(self) -> str:
        """Request the serial number. Works without connected crystal head."""
        command = 0xFE
        data = [0, 0, 0, 0]
        self.send_dataframe(command, data)

        return self.get_dataframe()

    """
    WARNING: The following functions to change device address and logic group should be used with caution. They enable
    serial communication with multiple devices.
    Changing the device address or logic group can lead to communication problems with the device, as future sent
    commands are not received by the device. If by accident the device address or logic group is changed, use the
    detect_logic_group function to find the correct logic group.
    """

    def set_device_address(self, address: int) -> bool:
        """Set the device address. Only use if you know what you are doing."""
        command = 0x58
        min_address = 1
        max_address = 254
        if address < min_address or address > max_address:
            msg = f"PREVAC TM1x: Address must be between {min_address} and {max_address}."
            raise ValueError(msg)

        data = [0, 0, 0, address]
        self.device_address = 0xFF
        self.send_dataframe(command, data)

        # Timeout might be needed
        time.sleep(1)

        # If it worked, the device should respond
        if self.port.in_waiting() > 0:
            self.port.read()  # Clear the buffer
            self.device_address = address
            return True

        return False

    def set_logic_group(self, group: int) -> bool:
        """Set the logic group. Only use if you know what you are doing."""
        command = 0x59
        min_group = 0
        max_group = 254
        if group < min_group or group > max_group:
            msg = f"PREVAC TM1x: Group must be between {min_group} and {max_group}."
            raise ValueError(msg)

        data = [0, 0, 0, group]
        self.send_dataframe(command, data)

        # Timeout might be needed
        time.sleep(1)

        # If it worked, the device should respond
        if self.port.in_waiting() > 0:
            self.port.read()  # Clear the buffer
            self.logic_group = group
            return True

        return False

    def detect_logic_group(self, timeout: float = 0.1) -> int:
        """If the logic group has been changed, this function checks which logic group responds.

        Change this function if a search for the device address is needed.
        """
        for logic_group in range(254):
            # self.logic_group is changed to generate the message. Might be needed to change back afterward.
            self.logic_group = logic_group
            self.port.clear_internal()

            # Create a dummy request to check if the device responds
            command = 0xFE
            data = [0, 0, 0, 0]
            self.send_dataframe(command, data)

            # Timeout is important, otherwise the response might be detected at a later logic group
            time.sleep(timeout)
            if self.port.in_waiting() > 0:
                self.port.read()
                return logic_group

        return -1
