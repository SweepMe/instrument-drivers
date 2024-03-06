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

from pysweepme.EmptyDeviceClass import EmptyDevice
from prevac_v2_communication import PrevacCommunicationInterface


class Device(EmptyDevice):
    """Device class for the PREVAC TMC13 Thickness Monitor Controller."""

    description = """
    TMC13 Thickness Monitor Controller
    Copy .ini to CustomDocuments
    """

    actions = ["reset_thickness"]

    def __init__(self) -> None:
        """Initialize the device class."""
        super().__init__()

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
        self.verbose = False

        # Device Parameter
        self.tooling_factor: float
        self.should_set_tooling: bool = False

        self.acoustic_impedance: float
        self.should_set_acoustic_impedance: bool = False

        self.density: float
        self.should_set_density: bool = False

        self.should_reset_thickness: bool = False

        self.frequency_min = None
        self.frequency_max = None

        # Prevac V2.x Communication Protocol
        self.host_address = chr(0xFF)
        self.unique_id: str = "\x53\x77\x65\x65\x70\x4d\x65"
        
        self.prevac_interface: PrevacCommunicationInterface
        
    def set_GUIparameter(self) -> dict:
        """Get parameters from the GUI and set them as attributes."""
        return {
            "Channel": ["1", "2", "3", "4", "5", "6"],
            "Reset thickness": False,  # To avoid accidental resetting when recording
            "Set tooling": False,
            "Tooling in %": "100.0",
            "Set density": False,
            "Density in g/cm^3": "1.3",
            "Set acoustic impedance": False,
            "Acoustic impedance in 1e5 g/cm²/s": 1.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Get parameters from the GUI and set them as attributes."""
        # Channel number must be of \x01 format
        channel = parameter["Channel"]
        self.channel = int(channel).to_bytes(1, byteorder="big").decode("latin1")

        self.should_reset_thickness = bool(parameter["Reset thickness"])

        self.should_set_tooling = bool(parameter["Set tooling"])
        self.tooling_factor = float(parameter["Tooling in %"])

        self.should_set_density = bool(parameter["Set density"])
        self.density = float(parameter["Density in g/cm^3"])

        self.should_set_acoustic_impedance = bool(parameter["Set acoustic impedance"])
        self.acoustic_impedance = float(parameter["Acoustic impedance in 1e5 g/cm²/s"])

        self.variables = ["Thickness", "Rate", "XTAL life", "Pressure"]
        self.units = ["A", "A/s", "%", "mbar"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

    def connect(self) -> None:
        """Enable Remote Control on the device."""
        self.prevac_interface = PrevacCommunicationInterface(self.port, self.host_address, self.channel)

        self.register_host()
        self.assign_master()

    def disconnect(self) -> None:
        """End the remote control mode on the device."""
        self.release_master()

    def initialize(self) -> None:
        """Get frequency range."""
        self.frequency_min = self.get_minimum_frequency()
        self.frequency_max = self.get_maximum_frequency()

    def configure(self) -> None:
        """Reset thickness if needed and set material properties."""
        if self.reset_thickness:
            self.reset_thickness()

        if self.should_set_tooling:
            if self.tooling_factor > 0:
                self.set_tooling_factor(self.tooling_factor)
            else:
                msg = f"Unaccepted tooling factor of {self.tooling_factor}. Please enter a float number"
                raise Exception(msg)

        if self.should_set_density:
            if self.density > 0:
                self.set_material_density(self.density)
            else:
                msg = f"Unaccepted density of {self.density}. Please enter a float number"
                raise Exception(msg)

        if self.should_set_acoustic_impedance:
            if self.acoustic_impedance > 0:
                self.set_material_acoustic_impedance(self.acoustic_impedance)
            else:
                msg = f"Unaccepted acoustic impedance of {self.acoustic_impedance}. Please enter a float number"
                raise Exception(msg)

    def call(self) -> list[float]:
        """Return the current thickness, rate and crystal life."""
        thickness = self.get_thickness()
        rate = self.get_rate()
        crystal_life = self.get_crystal_life()
        pressure = self.get_pressure()

        return [thickness, rate, crystal_life, pressure]

    """ Getter Functions """

    def get_thickness(self) -> float:
        """Returns thickness in A."""
        command = 0x0202
        thickness_angstrom = self.prevac_interface.get_double_value(command)

        return thickness_angstrom / 10

    def get_thickness_unit(self) -> str:
        """Returns the unit in which the thickness is displayed."""
        command = 0x0203
        unit = self.prevac_interface.get_byte_value(command)
        thickness_unit_dict = {
            0: "A",
            1: "kA",
            2: "nm",
        }

        return thickness_unit_dict[unit]

    def get_rate(self) -> float:
        """Returns the rate in A/s."""
        command = 0x0204
        return self.prevac_interface.get_double_value(command)

    def get_rate_unit(self) -> str:
        """Returns the unit in which the rate is displayed."""
        command = 0x0205
        unit = self.prevac_interface.get_byte_value(command)
        rate_unit_dict = {
            4: "A/s",
            5: "kA/s",
            6: "nm/s",
            8: "A/min",
            9: "kA/min",
            10: "nm/min",
            12: "A/h",
            13: "kA/h",
            14: "nm/h",
        }

        return rate_unit_dict[unit]

    def get_pressure(self) -> float:
        """Returns the pressure in mbar."""
        command = 0x0101
        channel, pressure = self.prevac_interface.get_double_value_and_channel(command)

        return pressure

    def get_pressure_unit(self) -> str:
        """Returns the unit in which the pressure is displayed."""
        command = 0x0103
        channel, unit = self.prevac_interface.get_byte_value_and_channel(command)

        pressure_unit_dict = {
            0: "mbar",
            1: "Torr",
            2: "Pa",
            3: "psia",
        }
        return pressure_unit_dict[unit]

    def get_tooling_factor(self) -> float:
        """Return tooling factor in %."""
        command = 0x020D
        return self.prevac_interface.get_double_value(command)

    def get_material_density(self) -> float:
        """Returns density in g/cm³."""
        # TODO: Currently not working, response is b'\x01@\x05\x99\x99\x99\x99\x99\x9a'
        command = 0x0214
        return self.prevac_interface.get_double_value(command)

    def get_crystal_life(self) -> float:
        """Returns crystal life in %."""
        frequency_current = self.get_crystal_frequency()
        life = (frequency_current - self.frequency_min) / (self.frequency_max - self.frequency_min) * 100.0

        return round(life, 2)

    def get_crystal_frequency(self) -> float:
        """Return crystal frequency."""
        command = 0x0201
        return self.prevac_interface.get_double_value(command)

    def get_maximum_frequency(self) -> float:
        """Return maximum crystal frequency."""
        command = 0x020F
        return self.prevac_interface.get_double_value(command)

    def get_minimum_frequency(self) -> float:
        """Return minimum crystal frequency."""
        command = 0x020E
        return self.prevac_interface.get_double_value(command)

    """ Setter Functions """

    def reset_thickness(self) -> None:
        """Reset the thickness to 0.0."""
        command = 0x8211  # +8 in MSB for write command
        self.prevac_interface.send_data_frame(command, self.channel)
        self.prevac_interface.check_response_for_errors()

    def set_tooling_factor(self, tooling_factor: float) -> None:
        """Set tooling factor in %."""
        command = 0x820D
        value = struct.pack(">d", tooling_factor).decode("latin1")
        self.prevac_interface.send_data_frame(command, str(self.channel + value))
        self.prevac_interface.check_response_for_errors()

    def set_material_density(self, density: float) -> None:
        """Set density in g/cm³."""
        command = 0x8214  # +8 in MSB for write command
        value = "%1.2f" % float(density)
        self.prevac_interface.send_data_frame(command, str(self.channel + value))
        self.prevac_interface.check_response_for_errors()

    def set_material_acoustic_impedance(self, impedance: float) -> None:
        """Set acoustic impedance in 1e5g/cm²/s."""
        command = 0x8215  # +8 in MSB for write command
        value = struct.pack(">d", impedance).decode("latin1")
        self.prevac_interface.send_data_frame(command, self.channel + value)
        self.prevac_interface.check_response_for_errors()

    """ Remote Control Configuration """

    def get_host(self) -> str:
        """Get the host address of the device."""
        command = 0x7FF0
        self.prevac_interface.send_data_frame(command)
        host = self.prevac_interface.receive_data_frame()

        return host.decode("latin1")

    def register_host(self) -> None:
        """Register the host unique ID on the TMC.

        A list of registered hosts can be seen in the TMC GUI under "Remote Control".
        The returned host address is used for further communication.
        """
        command = 0x7FF0
        self.prevac_interface.send_data_frame(command, self.unique_id)
        answer = self.prevac_interface.check_response_for_errors()
        new_host_address = answer.decode("latin1")
        self.host_address = new_host_address
        self.prevac_interface.host_address = new_host_address

    def assign_master(self) -> None:
        """Assign the master code that enables remote control.

        The master pc has to be registered as a host using the register_host function.
        """
        command = 0xFFF1
        assign_master_code = "\x01"  # Set Master
        self.prevac_interface.send_data_frame(command, assign_master_code)
        answer = self.prevac_interface.receive_data_frame()

        if answer != b"\x00":
            msg = "Could not assign master to device"
            raise Exception(msg)

    def get_master_status(self) -> str:
        """Get the master status of the device."""
        command = 0x7FF1
        self.prevac_interface.send_data_frame(command)
        answer = self.prevac_interface.receive_data_frame()

        # TODO: Check if the master status is correct
        status = bin(answer[0])[2:]
        if status[0] == "0":
            msg = "Master status is not correct"
            raise Exception(msg)

        return status

    def release_master(self) -> None:
        """End remote control."""
        command = 0xFFF1
        assign_master_code = "\x00"  # Release Master
        self.prevac_interface.send_data_frame(command, assign_master_code)
        answer = self.prevac_interface.receive_data_frame()

        if answer != b"\x00":
            msg = "Could not release master from device"
            raise Exception(msg)