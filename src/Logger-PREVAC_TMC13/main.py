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
# Device: PREVAC TMC13
from __future__ import annotations

# Import the communication interface
from imp import load_source
from pathlib import Path

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

prevac_protocol_path = str(Path(__file__).resolve().parent / "libraries" / "prevac_protocol.py")
PrevacCommunication = load_source("prevac_protocol", prevac_protocol_path)


class Device(EmptyDevice):
    """Device class for the PREVAC TMC13 Thickness Monitor Controller."""

    description = """
    <h3>Prevac TMC13</h3>
    <p>This driver controls Prevac TMC13 thickness monitors.</p>
    <h4>Setup</h4>
    <ul>
        <li>Enable remote control in the settings of the TMC device.</li>
    </ul>
    <h4>Parameters</h4>
    <ul>
        <li>Set the channel number according to your hardware.</li>
        <li>Reset thickness: If set True, the thickness will be set to 0 at the start of the measurement.</li>
        <li>Set tooling/density/acoustic impedance: If set True, the given parameters will be set to the device.
            Otherwise, the parameters set in the device GUI will be used. In general, the device does not save the
            changes in the material properties after the measurement.
        </li>
        <li>Read pressure 1/2: Enables readout of pressure sensors in channel 1 and 2.</li>
    </ul>
    """

    actions = ["reset_thickness"]  # Enables the reset_thickness action in the GUI

    def __init__(self) -> None:
        """Initialize the device class."""
        super().__init__()

        # Port Parameters
        self.channel = None
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

        # SweepMe Parameters
        self.shortname = "TMC13"
        self.variables = ["Thickness", "Rate", "XTAL life"]
        self.units = ["nm", "A/s", "%"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        # Device Parameter
        self.should_reset_thickness: bool = False

        self.should_set_tooling: bool = False
        self.tooling_factor: float = 100.0

        self.use_custom_material: bool = False
        self.material_name: str = ""  # Not read out or returned yet, can be used for documentation
        self.acoustic_impedance: float = 1.0
        self.density: float = 1.3

        self.should_read_pressure_1: bool = False
        self.should_read_pressure_2: bool = False

        self.frequency_min = None
        self.frequency_max = None

        # Prevac V2.x Communication Protocol
        self.host_address = chr(0xFF)
        self.unique_id: str = "\x53\x77\x65\x65\x70\x4d\x65"  # "SweepMe"

        self.prevac_interface: PrevacCommunication.PrevacCommunicationInterface

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        return {
            "Channel": ["1", "2", "3", "4", "5", "6"],
            "Reset thickness": False,  # To avoid accidental resetting when recording
            "Set tooling": False,
            "Tooling in %": "100.0",
            "  ": None,
            "Custom material": False,
            "Name": "",
            "Density in g/cm^3": "1.3",
            "Acoustic impedance in 1e5 g/cm²/s": 1.0,
            " ": None,
            "Read pressure 1": False,
            "Read pressure 2": False,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        # Channel number must be of \x01 format
        channel = parameter["Channel"]
        self.channel = int(channel).to_bytes(1, byteorder="big").decode("latin1")

        self.should_reset_thickness = bool(parameter["Reset thickness"])
        self.should_set_tooling = bool(parameter["Set tooling"])
        self.tooling_factor = float(parameter["Tooling in %"])

        # Custom Material Properties
        self.use_custom_material = bool(parameter["Custom material"])
        self.material_name = str(parameter["Name"])
        self.density = float(parameter["Density in g/cm^3"])
        self.acoustic_impedance = float(parameter["Acoustic impedance in 1e5 g/cm²/s"])

        # Pressure Readings
        self.should_read_pressure_1 = bool(parameter["Read pressure 1"])
        if self.should_read_pressure_1:
            self.add_pressure_readings(1)

        self.should_read_pressure_2 = bool(parameter["Read pressure 2"])
        if self.should_read_pressure_2:
            self.add_pressure_readings(2)

    def add_pressure_readings(self, pressure_channel: int) -> None:
        """Add pressure readings to the device."""
        self.variables.append(f"Pressure {pressure_channel}")
        self.units.append("mbar")
        self.plottype.append(True)
        self.savetype.append(True)

    def connect(self) -> None:
        """Enable Remote Control on the device."""
        self.prevac_interface = PrevacCommunication.PrevacCommunicationInterface(
            self.port,
            self.host_address,
            self.channel,
        )

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
        self.check_device_status()
        self.check_vacuum_gauge_status()
        self.check_units()

        if self.should_reset_thickness:
            self.reset_thickness()

        if self.should_set_tooling:
            self.set_tooling_factor(self.tooling_factor)

        if self.use_custom_material:
            self.set_material_name(self.material_name)
            self.set_material_density(self.density)
            self.set_material_acoustic_impedance(self.acoustic_impedance)

    def call(self) -> list[float]:
        """Return the current thickness, rate and crystal life."""
        measured_values = [self.get_thickness(), self.get_rate(), self.get_crystal_life()]

        if self.should_read_pressure_1:
            measured_values.append(self.get_pressure(1))
        if self.should_read_pressure_2:
            measured_values.append(self.get_pressure(2))

        return measured_values

    """ Convenience Functions """
    def check_units(self) -> None:
        """Check that values are communicated in the correct unit. Could add set_unit functions if needed."""
        thickness_unit = self.get_thickness_unit()
        rate_unit = self.get_rate_unit()
        pressure_unit = self.get_pressure_unit()

        # thickness is measured in A and converted to nm by get_thickness
        if thickness_unit != "A":
            msg = f"Thickness unit is {thickness_unit}, but should be A. Change the unit in the device GUI."
            debug(msg)

        if rate_unit != "A/s":
            msg = f"Rate unit is {rate_unit}, but should be A/s. Change the unit in the device GUI."
            debug(msg)

        if pressure_unit != "mbar":
            msg = f"Pressure unit is {pressure_unit}, but should be mbar. Change the unit in the device GUI."
            debug(msg)

    """ Getter Functions """

    def get_thickness(self) -> float:
        """Returns thickness in A."""
        command = 0x0202
        thickness_angstrom = self.prevac_interface.get_double_value(command)

        return thickness_angstrom / 10

    def get_thickness_unit(self) -> str:
        """Returns the unit in which the thickness is communicated by the device."""
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

    def get_pressure(self, channel: int = 1) -> float:
        """Returns the pressure in mbar of the given channel."""
        command = 0x0101

        # Channel number must be of \x01 format
        _channel = channel.to_bytes(1, byteorder="big").decode("latin1")
        channel, pressure = self.prevac_interface.get_double_value_and_channel(command, _channel)

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

    def get_material_name(self) -> str:
        """Return the material name."""
        command = 0x0213
        self.prevac_interface.send_data_frame(command, self.channel)
        answer = self.prevac_interface.receive_data_frame()[1:-1]  # answer contains two additional bytes
        return answer.decode("latin1")

    def get_material_density(self) -> float:
        """Returns density in g/cm³."""
        command = 0x0214
        channel, density = self.prevac_interface.get_double_value_and_channel(command)
        return density

    def get_material_acoustic_impedance(self) -> float:
        """Returns acoustic impedance in 1e5g/cm²/s."""
        command = 0x0215
        channel, acoustic_impedance = self.prevac_interface.get_double_value_and_channel(command)
        return acoustic_impedance

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

    def check_device_status(self) -> None:
        """Check the device status for errors and warnings."""
        command = 0x7F50
        self.prevac_interface.send_data_frame(command)
        status = self.prevac_interface.receive_data_frame()

        number_of_errors = status[0]
        number_of_warnings = status[1]

        if number_of_errors > 0:
            debug(f"{number_of_errors} device errors detected")
            for error_index in range(number_of_errors):
                self.prevac_interface.check_error_status(error_index)
        if number_of_warnings > 0:
            debug(f"{number_of_warnings} device warnings detected")
            for warning_index in range(number_of_warnings):
                self.prevac_interface.check_warning_status(warning_index)

    def check_vacuum_gauge_status(self) -> None:
        """Check the vacuum gauge status for errors and warnings. TMC13 displays Sensor Break! near ambient pressure."""
        command = 0x0105
        channel, status = self.prevac_interface.get_byte_value_and_channel(command)

        status_dict = {
            -1: "Sensor Break!",
            0: "Vacuum",
            1: "Wait for emission",
            2: "No Emission",
            3: "Wait for ignition",
            4: "Not Calibrated",
            5: "Voltage",
            6: "Degasing",
            7: "Exter. Setpoint",
            8: "Low Pressure",
            9: "High Pressure",
            10: "0.00e+00",
        }

        critical_status = [-1]  # Can be extended if needed
        if status in critical_status:
            msg = f"Prevac Warning: {status_dict[status]}"
            debug(msg)

    """ Setter Functions """

    def reset_thickness(self) -> None:
        """Reset the thickness to 0.0."""
        command = 0x8211  # +8 in MSB for write command
        self.prevac_interface.send_data_frame(command, self.channel)
        self.prevac_interface.check_response_for_errors()

    def set_tooling_factor(self, tooling_factor: float) -> None:
        """Set tooling factor in %."""
        min_tooling = 0
        max_tooling = 10000
        if tooling_factor < min_tooling or tooling_factor > max_tooling:
            msg = (f"Unaccepted tooling factor of {tooling_factor}. "
                   f"Please enter a float number between {min_tooling} and {max_tooling}.")
            raise Exception(msg)

        command = 0x820D
        self.prevac_interface.send_double_value_and_channel(command, tooling_factor)
        self.prevac_interface.check_response_for_errors()

    def set_material_name(self, name: str) -> None:
        """Set the name of the material."""
        if name == "":
            msg = "Custom material name cannot be empty."
            raise Exception(msg)

        command = 0x8213  # +8 in MSB for write command
        # TODO: Check if the name is in correct format
        self.prevac_interface.send_data_frame(command, name)
        self.prevac_interface.check_response_for_errors()

    def set_material_density(self, density: float) -> None:
        """Set density in g/cm³."""
        min_density = 0.1
        max_density = 999.99
        if density < min_density or density > max_density:
            msg = (f"Unaccepted material density of {density}. "
                   f"Please enter a float number between {min_density} and {max_density}.")
            raise Exception(msg)

        command = 0x8214  # +8 in MSB for write command
        self.prevac_interface.send_double_value_and_channel(command, density)
        self.prevac_interface.check_response_for_errors()

    def set_material_acoustic_impedance(self, impedance: float) -> None:
        """Set acoustic impedance in 1e5g/cm²/s."""
        min_impedance = 0.1
        max_impedance = 999.99
        if impedance < min_impedance or impedance > max_impedance:
            msg = (f"Unaccepted material acoustic impedance of {impedance}. "
                   f"Please enter a float number between {min_impedance} and {max_impedance}.")
            raise Exception(msg)

        command = 0x8215  # +8 in MSB for write command
        self.prevac_interface.send_double_value_and_channel(command, impedance)
        self.prevac_interface.check_response_for_errors()

    """ Remote Control Configuration """

    def get_host(self) -> str:
        """Get the host address of the device."""
        command = 0x7FF0
        self.prevac_interface.send_data_frame(command)
        host = self.prevac_interface.receive_data_frame()

        return host.decode("latin1")

    def register_host(self, host_id: str | None = None) -> None:
        """Register the host unique ID on the TMC.

        A list of registered hosts can be seen in the TMC GUI under "Remote Control".
        The returned host address is used for further communication.
        """
        command = 0x7FF0
        value = self.unique_id if host_id is None else host_id
        self.prevac_interface.send_data_frame(command, value)
        answer = self.prevac_interface.check_response_for_errors()

        self.host_address = answer.decode("latin1")
        self.prevac_interface.host_address = self.host_address

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

        status = bin(answer[0])[2:]
        # The status might be 11101, but it is still working. Hence, debug instead of raise is called.
        if status[-1] == "0":
            debug("Not working as Master.")

        if status[-3] == "0":
            debug("Device Remote Control not enabled in TMC GUI.")

        if status[-4] == "0":
            debug("Host not registered.")

        if status[-5] == "1":
            debug("Other MASTER host device in system.")

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
