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
# Device: PREVAC TMC13-Shutter
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
    <h3>Prevac TMC13 Shutter</h3>
    <p>This driver enables using the Prevac TMC13 as shutter control unit.</p>
    <h4>Setup</h4>
    <ul>
        <li>Enable remote control in the settings of the TMC device.</li>
    </ul>
    <h4>Parameters</h4>
    <ul>
        <li>Set the channel number according to your hardware.</li>
    </ul>
    """
    
    actions = ["close_shutter", "open_shutter"]

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
        self.shortname = "TMC13 Shutter"
        self.variables = ["State", "Open"]
        self.units = ["", ""]
        self.plottype = [False, True]
        self.savetype = [True, True]

        # Shutter Properties
        self.shutter_number: int = 1
        self.shutter_state: int
        self.start_state: bool = False
        self.end_state: bool = False
        self.shutter_state_dict = {
            0: "Closed",
            1: "Open",
        }

        # Prevac V2.x Communication Protocol
        self.host_address = chr(0xFF)
        self.unique_id: str = "\x53\x77\x65\x65\x70\x4d\x65"  # "SweepMe"

        self.prevac_interface: PrevacCommunication.PrevacCommunicationInterface = None

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        return {
            "Channel": ["1", "2", "3", "4", "5", "6"],
            "SweepMode": ["None", "State"],
            "Shutter number": ["1", "2"],
            "State at start": ["As is", "Open", "Closed"],
            "State at end": ["As is", "Open", "Closed"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Get parameters from the GUI and set them as attributes."""
        
        self.port_string = parameter["Port"]
        
        # Channel number must be of \x01 format
        channel = parameter["Channel"]
        self.channel = int(channel).to_bytes(1, byteorder="big").decode("latin1")

        self.sweepmode = parameter["SweepMode"]

        self.shutter_number = int(parameter["Shutter number"])
        self.start_state = str(parameter["State at start"])
        self.end_state = str(parameter["State at end"])

    def connect(self) -> None:
        """Enable Remote Control on the device."""

        self.prevac_interface = PrevacCommunication.PrevacCommunicationInterface(
            self.port,
            self.host_address,
            self.channel,
        )

        self.register_host()
        self.unique_identifier = "PREVAC_TMC13 - " + self.port_string
        if self.unique_identifier not in self.device_communication:
            self.assign_master()
        self.get_master_status()

    def disconnect(self) -> None:
        """End the remote control mode on the device."""
        if self.unique_identifier in self.device_communication:
            self.release_master()
            del self.device_communication[self.unique_identifier]

    def configure(self) -> None:
        """Set initial state."""
        if self.start_state != "As is":
            self.set_shutter_state(self.start_state)

    def unconfigure(self) -> None:
        """Set end state."""
        if self.end_state != "As is":
            self.set_shutter_state(self.end_state)

    def apply(self) -> None:
        """Set the shutter state."""
        if self.sweepmode == "State":
            self.set_shutter_state(self.value)

    def measure(self) -> None:
        """Measure the current state of the shutter."""
        self.shutter_state = self.get_shutter_state()

    def call(self) -> str:
        """Return the current state of the device."""
        return self.shutter_state_dict[self.shutter_state], bool(self.shutter_state)

    """ TMC13 Shutter Control Functions """

    def get_shutter_state(self) -> int:
        """Return the current state of the shutter."""
        command = 0x0207
        data = f"{self.channel}0"
        self.prevac_interface.send_data_frame(command, data)
        answer = self.prevac_interface.receive_data_frame()
        shutter_state =  bool(ord(answer))
        return shutter_state
    
    def close_shutter(self):
        self.set_shutter_state(0)
        
    def open_shutter(self):
        self.set_shutter_state(1)

    def set_shutter_state(self, target_state: str | int | float | bool) -> None:
        """Set the state of the shutter.

        From the TMC13 Manual page 155:
        Order number 0x0207
        Byte 1: Index (INT) possible values 0-6. Might refer to the TMCs output channel.
        Byte 2: State (INT) possible values 0 or 1. 0 = closed, 1 = open.

        The shutter channel is probably different from the Thickness control channel, which was used in the Logger driver.
        It might need another input in the GUI to set the shutter channel.
        """
        target_state = chr(self.handle_set_state_input(target_state))

        command = 0x8207  # +8 in MSB for write command

        # TODO: I am unsure if this is the correct way to define the data
        # data is needed in str format
        data = f"{self.channel}{target_state}"
        
        self.prevac_interface.send_data_frame(command, data)
        self.prevac_interface.check_response_for_errors()

    @staticmethod
    def handle_set_state_input(target_state: str | int | float | bool) -> int:
        """Handle the input for the set_shutter_state function."""
                
        if isinstance(target_state, str):
            if target_state.lower() == "open":
                target_state = 1
            elif target_state.lower() == "closed":
                target_state = 0
            else:
                msg = f"Invalid state input {target_state}. Use 'open' or 'closed'."
                raise ValueError(msg)

        elif isinstance(target_state, (bool, float)):
            target_state = int(target_state)

        elif isinstance(target_state, int):
            if target_state not in [0, 1]:
                msg = f"Invalid state input {target_state}. Use 0 or 1."
                raise ValueError(msg)

        else:
            msg = f"Invalid state input {target_state}. Use 'open', 'closed', 0 or 1."
            raise ValueError(msg)

        return target_state

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
