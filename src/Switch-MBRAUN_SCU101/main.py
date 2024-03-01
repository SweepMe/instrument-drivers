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
# Type: Switch
# Device: MBRAUN SCU101

from __future__ import annotations

import minimalmodbus
from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):
    ## here you can add html formatted description to your device class that is shown by modules like 'Logger' or 'Switch' that have a description field.
    description = """
        <h3>MBRAUN SCU 101 Shutter</h3>
        <p>This driver controls the MBRAUN Shutter Control Unit SCU 101.</p>
        <h4>Hardware Setup</h4>
        <p>In the SCU 101 menu:</p>
        <ul>
        <li>E0: Set the MB Address</li>
        <li>E1-E2: Check baudrate (19200) and parity (E)</li>
        <li>E4: Set MB Type to RS 232</li>
        </ul>
        <h4>Parameters</h4>
        <ul>
        <li>Set the MB Address according to your hardware.</li>
        <li>Choose the shutter number you want to control (1 or 2)</li>
        <li>The SweepValue that sets the shutter state can be either int (1 = open,&nbsp;&ne;1 = close), boolean (True = open, False = close), or string ("open", &ne;"open" = close).</li>
        </ul>
    """

    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "SCU101"  # short name will be shown in the sequencer
        self.variables = ["State"]  # define as many variables you need
        self.units = [""]  # make sure that you have as many units as you have variables
        self.plottype = [True]  # True to plot data, corresponding to self.variables
        self.savetype = [True]  # True to save data, corresponding to self.variables

        self.port_types = ["COM"]

        # Device Parameter
        self.port_string: str
        self.address: int
        self.modbus: None
        self.instance_key = None

        # Device States
        self.shutter_number: int
        self.shutter_state: int
        self.shutter_state_dict = {
            0: "Unknown",
            1: "Open",
            2: "Closed",
            3: "Moving",
            4: "Not connected",
            5: "Blocked",
        }

    def set_GUIparameter(self) -> dict:
        """Get parameters from the GUI and set them as attributes."""
        return {
            "SweepMode": ["State", "None"],
            "MB Address": "1",
            "Shutter Number": ["1", "2"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Get parameters from the GUI and set them as attributes."""
        self.sweepmode = parameter["SweepMode"]

        self.port_string = parameter["Port"]
        self.address = int(parameter["MB Address"])
        self.shutter_number = int(parameter["Shutter Number"])

        max_address = 247
        if self.address < 1 or self.address > max_address:
            msg = "The Modbus address must be between 1 and 247."
            raise Exception(msg)

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self) -> None:
        """Connect to the device."""
        self.modbus = minimalmodbus.Instrument(
            self.port_string,
            self.address,
            close_port_after_each_call=False,
            debug=False,
        )

        self.modbus.serial.timeout = 2
        self.modbus.serial.baudrate = 19200
        self.modbus.serial.parity = "E"

    def disconnect(self) -> None:
        """Disconnect from the device."""
        self.modbus.serial.close()

    def initialize(self) -> None:
        """Initialize the device."""
        self.shutter_state = self.get_shutter_state()

    def apply(self) -> None:
        """Apply the settings."""
        if self.sweepmode == "State":
            target_shutter_state = self.handle_set_state_input(self.value)
            self.set_shutter_state(target_shutter_state)

    def measure(self) -> None:
        """Measure the current state of the shutter."""
        self.shutter_state = self.get_shutter_state()

        if self.shutter_state_dict[self.shutter_state] == "Not connected":
            msg = "Unable to move the shutter as the controller is unable to connect to it."
            raise Exception(msg)
        elif self.shutter_state_dict[self.shutter_state] == "Blocked":
            msg = "Unable to move the shutter as it is blocked."
            raise Exception(msg)

    def call(self) -> str:
        """Return the current state of the device."""
        return self.shutter_state_dict[self.shutter_state]

    """ SCU101 specific functions"""

    def get_shutter_state(self) -> int:
        """Read the current state of the shutter."""
        register_address = 0x0000 if self.shutter_number == 1 else 0x0020
        mask = 0x000F

        return self.read_register(register_address, mask)

    def read_register(self, address: int, mask: hex) -> int:
        """Read a register from the device."""
        response = self.modbus.read_register(address, 0, functioncode=4)
        return response & mask

    def handle_set_state_input(self, set_state_input: float | int | bool) -> hex:
        """Handle the input for the state of the shutter and return hex representation."""
        if isinstance(set_state_input, (float, int)):
            state_hex = 0x0001 if int(set_state_input) == 1 else 0x0002

        elif isinstance(set_state_input, bool):
            state_hex = 0x0001 if set_state_input else 0x0002

        elif isinstance(set_state_input, str):
            state_hex = 0x0001 if set_state_input.lower() == "open" else 0x0002

        else:
            msg = "Input of %s cannot be transformed to allowed shutter states of 0x0001 or 0x0002." % input
            raise Exception(msg)

        return state_hex

    def set_shutter_state(self, target_shutter_state: int) -> None:
        """Set the state of the shutter."""
        register_address = 0x0001 if self.shutter_number == 1 else 0x0021
        shutter_set_mask = 0x0003
        execute_flag_mask = 0x0004

        # Set the new shutter position
        current_value = self.read_register(register_address, shutter_set_mask)

        # Masks for setting and clearing bits
        clear_mask = ~(shutter_set_mask | execute_flag_mask)  # Combine masks and invert to create a clear mask
        # Isolate bits for the new shutter position
        set_shutter_position_mask = target_shutter_state & shutter_set_mask

        # Apply masks to current_value
        # First, clear the bits related to the shutter set and execute flag in the current value
        cleared_current_value = current_value & clear_mask
        # Then, set the shutter position bits in the cleared current value
        value_to_write = cleared_current_value | set_shutter_position_mask

        self.write_register(register_address, value_to_write)

        # Execute the new shutter position
        value_to_write |= execute_flag_mask
        self.write_register(register_address, value_to_write)

    def write_register(self, address: int, value: int) -> None:
        """Write a register to the device."""
        self.modbus.write_register(address, value, functioncode=6)

    def handle_fault_state(self) -> None:
        """Handle the fault state of the shutter."""
        if self.shutter_state_dict[self.shutter_state] == "Not connected":
            msg = "Unable to move the shutter as the controller is unable to connect to it."
            raise Exception(msg)
        elif self.shutter_state_dict[self.shutter_state] == "Blocked":
            msg = "Unable to move the shutter as it is blocked."
            raise Exception(msg)
