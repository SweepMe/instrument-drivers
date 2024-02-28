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
# Type: Logger
# Device: PREVAC TMC13
from __future__ import annotations


import struct

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
    TMC13 Thickness Monitor Controller
    """

    actions = ["run_reset_thickness"]

    def __init__(self):
        EmptyDevice.__init__(self)

        self.channel = None
        self.shortname = "TMC13"

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 1,
            "baudrate": 57600,  # default
            "bytesize": 8,
            "stopbits": 1,
            "raw_read": True,
            "raw_write": True,
        }
        self.verbose = True

        # Device Parameter
        self.tooling_factor: float
        self.run_set_tooling: bool = False

        self.acoustic_impedance: float
        self.run_set_acoustic_impedance: bool = False

        self.density: float
        self.run_reset_thickness: bool = False

        self.frequency_min = None
        self.frequency_max = None

        # Prevac V2.x Communication Protocol
        self.startbyte = chr(0xBB)
        # self.device_address = chr(0xC8)
        self.device_address = chr(0x01)
        self.host_address = chr(0xFF)

    def set_GUIparameter(self) -> dict:
        return {
            "Channel": ["1", "2", "3", "4", "5", "6"],
            "Reset thickness": False,  # To avoid accidental resetting when recording
            "Set Tooling": False,
            "Tooling in %": "100.0",
            "Set Density": False,
            "Density in g/cm^3": "1.3",
            "Set Acoustic Impedance": False,
            "Acoustic impedance in 1e5 g/cm²/s": 1.0,
        }


    def get_GUIparameter(self, parameter={}) -> None:
        # TODO: set self parameter as readable string
        channel = parameter["Channel"]
        self.channel = int(channel).to_bytes(1, byteorder="big").decode("latin1")

        # TODO: Convert input to bytes
        self.channel = "\x01"  # , parameter["Channel"]

        self.run_reset_thickness = parameter["Reset thickness"]

        self.run_set_tooling = parameter["Set Tooling"]
        self.tooling_factor = float(parameter["Tooling in %"])

        self.self.run_set_density = parameter["Set Density"]
        self.density = float(parameter["Density in g/cm^3"])

        self.self.run_set_acoustic_impedance = parameter["Set Acoustic Impedance"]
        self.acoustic_impedance = float(parameter["Acoustic impedance in 1e5 g/cm²/s"])

        self.variables = ["Thickness", "Rate", "XTAL life"]
        self.units = ["nm", "A/s", "%"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

    def connect(self):
        # print("get_host")
        self.host_address = self.get_host()
        print("Host address", self.host_address, ord(self.host_address))

        # print("get_serial_number")
        serial_number = self.get_serial_number()
        # print("Serial number:", serial_number)

        # print("get_product_number")
        product_number = self.get_product_number()
        # print("Product number:", product_number)

        # print("get_device_version")
        device_version = self.get_device_version()
        # print("Device version:", device_version[:15])

        print("assign master")
        self.assign_master()

    # def disconnect(self):
    #
    #    print("release master")
    #    self.release_master()

    def initialize(self) -> None:
        if self.run_set_tooling:
            if self.tooling_factor > 0:
                self.set_tooling_factor(self.tooling_factor)
            else:
                msg = f"Unaccepted tooling factor of {self.tooling_factor}. Please enter a float number"
                raise Exception(msg)

        if self.self.run_set_density:
            if self.density > 0:
                self.set_material_density(self.density)
            else:
                msg = f"Unaccepted density of {self.density}. Please enter a float number"
                raise Exception(msg)

        if self.self.run_set_acoustic_impedance:
            if self.acoustic_impedance > 0:
                self.set_material_acoustic_impedance(self.acoustic_impedance)
            else:
                msg = f"Unaccepted acoustic impedance of {self.acoustic_impedance}. Please enter a float number"
                raise Exception(msg)

        self.frequency_min = self.get_minimum_frequency()
        self.frequency_max = self.get_maximum_frequency()

    def configure(self):
        if self.reset_thickness:
            self.reset_thickness()

        if self.self.run_set_density:
            self.set_material_density(float(self.density))

        if self.run_set_tooling:
            self.set_tooling_factor(float(self.tooling_factor))

        if self.self.run_set_acoustic_impedance:
            self.set_material_acoustic_impedance(float(self.acoustic_impedance))

    def call(self) -> list[float]:
        thickness = self.get_thickness()
        rate = self.get_rate()
        crystal_life = self.get_crystal_life()

        return [thickness, rate, crystal_life]


    """ convenience functions """

    # Byte Description
    # 1 - HEADER First byte is responsible for identifying the serial protocol.
    # Header in hexadecimal is 0xBB
    # 2 - DATA LENGTH Length of the data field. Maximum data file length is 0xFF
    # (256 bytes). Prevac Serial Protocol
    # 3 - DEVICE ADDRESS Identification of hardware device address. Default value is
    # 0xC8
    # 4 - HOST ADDRESS Host identification address. Assigned to host during the
    # registration process (using a unique ID).
    # 5 - FUNCTION CODE - MSB First procedure function code byte
    # 8th (MSB) bit is the read(0)/write(1) select bit
    # 6 - FUNCTION CODE - LSB Second procedure function code byte
    # 7 .. [7 + DATA LENGTH] -
    # DATA FIELD
    # Data capture needed to realize defined functions.
    # [7 + DATA LENGTH] + 1(last
    # frame position) - CRC
    # CRC is simple module 256 calculated without protocol
    # header byte(see section 6.5.2.4)

    def send_data_frame(self, command: int, data: str = "") -> None:
        """Send a Prevac V2.x Protocol data frame to the device.
        Code is an integer of hex format 0x0202 and corresponds to the command
        value is the data that is send in addition to the command.
        """
        # Split the most significant and least significant byte of the command
        msb, lsb = struct.pack(">H", command)
        length = chr(len(data))

        message = length + self.device_address + self.host_address + chr(msb) + chr(lsb) + data

        checksum = self.generate_checksum(message)
        cmd_to_write = (self.startbyte + message + checksum).encode("latin1")

        self.port.write(cmd_to_write)

    def generate_checksum(self, message: str) -> str:
        return chr(sum([ord(char) for char in message]) % 256)

    def receive_data_frame(self) -> bytes:
        """Receive a Prevac V2.x Protocol data frame from the device."""
        header = self.port.read(1)

        if int(header) == ord(self.startbyte):
            # Read Data Frame
            length = int(self.port.read(1))  # should be already int because of indexing
            device = self.port.read(1)
            host = self.port.read(1)
            msb = self.port.read(1)
            lsb = self.port.read(1)

            data = self.port.read(length)

            if self.verbose:
                print("Length", "device", "host", "msb", "lsb", "data")
                print(length, device, host, msb, lsb, data)

            # If an error occurs, the last data field is the error code
            error = bytes(data[-1:])
            self.check_error_code(error)

            # checksum control
            # TODO: Create data frame class
            checksum = ord(self.port.read(1))
            received_message = length + device + host + msb + lsb + data
            calc_checksum = ord(self.generate_checksum(received_message.decode("latin1")))

            if checksum != calc_checksum:
                msg = "PREVAC TMC13: Checksums do not match"
                raise Exception(msg)

            # TODO: Check if raise Exception is correct
            if self.port.in_waiting() > 0:
                msg = f"PREVAC TMC13: There are still Bytes in waiting: {self.port.in_waiting()}."
                raise Exception(msg)

            return data  # we cut off the first byte as it is the return error code

        else:
            msg = f"PREVAC TMC13: Returned message does not start with correct byte {self.startbyte}"
            raise Exception(msg)

    def check_error_code(self, error_code: bytes) -> None:
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

        if error_code in error_codes:
            msg = error_codes[error_code]
            raise Exception(msg)

    """ setter/getter functions """

    def get_host(self) -> str:
        command = 0x7FF0
        self.send_data_frame(command)
        host = self.receive_data_frame()

        # TODO: Set self.host_address

        return host.decode("latin1")

    def assign_master(self) -> None:
        # Example assign master
        # BB    01      C8     01    FF F1     01      BB
        # start length  device host  code      value   checksum

        # b'\xbb\x01\x01\x7f\x7f\xf11"'

        command = 0x7FF1
        assign_master_code = "1"
        self.send_data_frame(command, assign_master_code)
        answer = self.receive_data_frame()

        # TODO: Check response
        print(answer)

    def release_master(self) -> None:
        # b'\xbb\x01\x01\x7f\x7f\xf10!'

        command = 0x7FF1
        release_master_command = "0"
        self.send_data_frame(command, release_master_command)
        answer = self.receive_data_frame()

        # TODO: Check response

    def get_product_number(self) -> str:
        """Returns the product number"""
        command = 0x7F01

        self.send_data_frame(command)
        product_number = self.receive_data_frame()

        return product_number.decode("latin1")

    def get_device_version(self) -> str:
        """Returns the device version"""
        command = 0x7F03

        self.send_data_frame(command)
        version = self.receive_data_frame()

        return version.decode("latin1")

    def get_serial_number(self) -> str:
        """Returns the serial number of the device"""
        command = 0x7F02
        self.send_data_frame(command)
        serial_number = self.receive_data_frame()

        return serial_number.decode("latin1")

    def get_thickness(self) -> float:
        """Returns thickness in nm."""
        command = 0x0202
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame()

        # TODO: strip off the channel number?
        thickness_angstrom = struct.unpack(">d", answer)[0]
        # TODO: Check for unit
        return thickness_angstrom / 10

    def get_thickness_unit(self) -> str:
        """Returns the unit in which the thickness is displayed."""
        command = 0x0203
        self.send_data_frame(command, self.channel)

        # strip off the channel number
        answer = self.receive_data_frame().decode("latin1")
        channel = answer[0]
        unit = answer[1:]

        thickness_unit_dict = {
            "0": "A",
            "1": "kA",
            "2": "nm",
        }
        thickness_unit = thickness_unit_dict[unit]
        # TODO: Move due to Do One Thing
        self.units[1] = thickness_unit

        return thickness_unit

    def get_rate(self) -> float:
        """Returns the rate in A/s."""
        command = 0x0204
        self.send_data_frame(command, self.channel)

        answer = self.receive_data_frame()
        rate = struct.unpack(">d", answer)[0]
        # TODO: Check if Channel number is transmitted

        return rate

    # TODO: Add get_rate_unit()

    def get_tooling_factor(self) -> float:
        """Return tooling factor in %."""
        command = 0x020D
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame().decode("latin1")
        channel = answer[0]
        tooling_factor = answer[1:]

        return tooling_factor

    def set_tooling_factor(self, tooling_factor: float) -> None:
        """Set tooling factor in %."""
        command = 0x020D
        value = struct.pack(">d", tooling_factor).decode("latin1")
        print(value, repr(value))
        self.send_data_frame(command, str(self.channel + value))
        value = self.receive_data_frame()

    def get_material_density(self) -> float:
        """Returns density in g/cm³"""
        command = 0x0214
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame()
        # answer = "\x01\x05\x99\x99\x99\x99\x99\x9a"

        return struct.unpack(">d", answer)[0]


    def set_material_density(self, density: float) -> None:
        """Set density in g/cm³."""
        command = 0x0214
        value = "%1.2f" % float(density)
        self.send_data_frame(command, str(self.channel + value))

        # Read out answer to check for error codes
        self.receive_data_frame()

    def set_material_acoustic_impedance(self, impedance: float) -> None:
        """Set acoustic impedance in 1e5g/cm²/s."""
        command = 0x0215
        value = struct.pack(">d", impedance).decode("latin1")
        self.send_data_frame(command, self.channel + value)

        # Read out answer to check for error codes
        self.receive_data_frame()

    def get_crystal_life(self) -> float:
        """Returns crystal life in %."""
        frequency_current = self.get_crystal_frequency()

        life = (frequency_current - self.frequency_min) / (self.frequency_max - self.frequency_min) * 100.0

        return round(life, 2)

    def get_crystal_frequency(self) -> float:
        """Return crystal frequency."""
        command = 0x0201
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame()

        return struct.unpack(">d", answer)[0]


    def get_maximum_frequency(self) -> float:
        """Return maximum crystal frquency."""
        command = 0x020F
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame()

        return struct.unpack(">d", answer)[0]


    def get_minimum_frequency(self) -> float:
        """Return minimum crystal frquency."""
        command = 0x020E
        self.send_data_frame(command, self.channel)
        answer = self.receive_data_frame()

        return struct.unpack(">d", answer)[0]

    def reset_thickness(self) -> None:
        """Reset the thickness to 0.0."""
        command = 0x0211
        self.send_data_frame(command, self.channel)

        # Read out answer to check for error codes
        self.receive_data_frame()

    def get_pressure(self) -> float:
        """Returns the pressure in mbar."""
        command = 0x0101
        self.send_data_frame(command, self.channel)
        value = self.receive_data_frame()

        return struct.unpack(">d", value[1:])[0]

