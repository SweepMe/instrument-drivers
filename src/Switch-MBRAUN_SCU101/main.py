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

# from FolderManager import addFolderToPATH
# addFolderToPATH()
# TODO: LibraryBuilder2 -> minimalmodbus
import time

import minimalmodbus
from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):
    ## here you can add html formatted description to your device class that is shown by modules like 'Logger' or 'Switch' that have a description field.
    description = """ set correct MB Type RS 232  """

    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "SCU101"  # short name will be shown in the sequencer
        self.variables = ["State"]  # define as many variables you need
        self.units = [""]  # make sure that you have as many units as you have variables
        self.plottype = [True]  # True to plot data, corresponding to self.variables
        self.savetype = [True]  # True to save data, corresponding to self.variables

        self.port_types = ["COM"]

        ## "<Name>" : (<Modbus  register>, <has digits>, <EI-Bisync mnemonic>)
        self.registers = {
            "State": 0,  # Modbus only
        }

        # Device Parameter
        self.port_string: str
        self.address: int
        self.modbus: None

        self.shutter_state: int
        self.shutter_state_dict = {
            0: "Unknown",
            1: "Open",
            2: "Closed",
            3: "Moving",
            4: "Not connected",
            5: "Blocked",
        }

        self.set_state = None

    def set_GUIparameter(self) -> dict:
        """Get parameters from the GUI and set them as attributes."""
        return {
            "SweepMode": ["State", "None"],
            "MB Address": "1",
        }

    def get_GUIparameter(self, parameter) -> dict:
        """Get parameters from the GUI and set them as attributes."""
        self.sweepmode = parameter["SweepMode"]

        self.port_string = parameter["Port"]
        self.address = int(parameter["MB Address"])

        max_address = 247
        if self.address < 1 or self.address > max_address:
            msg = "The Modbus address must be between 1 and 247."
            raise Exception(msg)

    #### ----------------------------------------------------------------------------------------------------------------------
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

    def handle_set_state_input(self, input: float | int | bool) -> hex:
        """Handle the input for the state of the shutter and return hex representation."""
        if isinstance(input, (float, int)):
            state_hex = 0x0001 if int(input) >= 1 else 0x0002

        elif isinstance(input, bool):
            state_hex = 0x0001 if input else 0x0002

        elif isinstance(input, str):
            state_hex = 0x0001 if input.lower() == "open" else 0x0002

        if state_hex not in [0x0001, 0x0002]:
            msg = "Input of %s cannot be transformed to allowed shutter states of 0x0001 or 0x0002." % input
            raise Exception(msg)

        return state_hex

    def set_shutter_state(self, target_shutter_state: int) -> None:
        """Set the state of the shutter."""
        register_address = 1
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
        print("write_register:", address, value)
        self.modbus.write_register(address, value, functioncode=6)

    def adapt(self) -> None:
        """Adapt the settings if GUI parameters have changed."""
        if self.sweepmode == "State":
            while True:
                self.shutter_state = self.get_shutter_state()
                shutter_position = self.shutter_state_dict[self.shutter_state]

                if self.shutter_state_dict[self.shutter_state] == "Not connected":
                    msg = "Unable to move the shutter as the controller is unable to connect to it."
                    raise Exception(msg)
                elif self.shutter_state_dict[self.shutter_state] == "Blocked":
                    msg = "Unable to move the shutter as it is blocked."
                    raise Exception(msg)

                if shutter_position == "Open":
                    self.set_state = 1
                    break
                elif shutter_position == "Closed":
                    self.set_state = 2
                    break

                time.sleep(0.1)

    def measure(self) -> None:
        """Measure the current state of the device."""
        self.shutter_state = self.get_shutter_state()

    def call(self) -> str:
        """Return the current state of the device."""
        return self.shutter_state_dict[self.shutter_state]

    def get_shutter_state(self) -> int:
        """Read the current state of the shutter."""
        addr = 0
        mask = 0x000F

        return self.read_register(addr, mask)

    def read_register(self, address: int, mask: hex) -> int:
        """Read a register from the device."""
        print("read_register. address: ", address, "mask: ", mask)
        response = self.modbus.read_register(address, 0, functioncode=4)
        return response & mask
