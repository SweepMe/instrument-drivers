# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
#
# SweepMe! driver
# * Module: Switch
# * Instrument: Keysight Polarization Navigator

from __future__ import annotations

import ctypes

from pysweepme.EmptyDeviceClass import EmptyDevice

DLL_PATH = r"C:\Program Files\Keysight\Polarization Navigator\bin\PolNavClient.dll"


class Device(EmptyDevice):
    """Driver for the Keysight N778xB."""

    description = """
    <h3>Keysight Polarization Navigator</h3>
    <h4>Parameters</h4>
    <ul>
    <li>Sweep mode: SOP: Currently the measured SOP cannot be read out, hence nothing is returned.</li>
    </ul>
    """
    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "N778xB"  # short name will be shown in the sequencer

        # SweepMe! parameters
        # self.variables = ["SOP"]
        # self.units = [""]
        # self.plottype = [False]
        # self.savetype = [True]

        # Communication Parameters
        self.client: ctypes.CDLL | None = None
        """The ctypes client for the Polarization Navigator DLL."""

        self.port_string: str = ""

        # Measurement parameters
        self.mode = "SOP"

    def find_ports(self) -> list[str]:
        """Returns a list of available devices in Polarization Navigator."""
        if self.client is None:
            self.load_polarization_navigator_dll()

        available_devices = self.send_command(command="Dir", target="Global")
        devices = available_devices.split("\r\n")
        if "Global" in devices:
            devices.remove("Global")

        return devices

    def load_polarization_navigator_dll(self) -> None:
        """Load the Polarization Navigator DLL."""
        try:
            self.client = ctypes.CDLL(DLL_PATH)
        except OSError as e:
            msg = f"Failed to load the Polarization Navigator DLL: {e}"
            raise RuntimeError(msg) from e

        # Define argument and return types for the functions we will use
        self.client.PolNavC_SendCommand.argtypes = [
            ctypes.c_char_p,        # Target
            ctypes.c_char_p,        # Command
            ctypes.c_char_p,        # Response buffer (output)
            ctypes.c_int,           # MaxLen
            ctypes.POINTER(ctypes.c_int),  # ResponseLen (output by reference)
        ]
        self.client.PolNavC_SendCommand.restype = ctypes.c_int  # TODO: This is why it crashes when reading the SOP???

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["SOP"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]
        self.mode = parameter["SweepMode"]

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        if self.client is None:
            self.load_polarization_navigator_dll()
        self.send_command("Activate")
        self.send_command("Stabilize")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new set value that is always available as 'self.value'."""
        if self.mode == "SOP":
            try:
                x, y, z = map(float, self.value.split(";"))
            except ValueError as e:
                msg = f"Invalid SOP format. Expected 'x,y,z' format, got '{self.value}'."
                raise ValueError(msg) from e

            self.send_command(f"Set TargetSOP,{x},{y},{z}")
            self.send_command("Set Stabilize,1")

    def send_command(self, command: str, target: str = "", buffer_size: int = 1024, response_type: str = "int") -> str:
        """Send a command to the Polarization Navigator, check the response for error codes, and return the response.

        The target can be either a specific device, a group command like "Global", or the first device as "PolCon*".
        Variables can be set by using the format "Set VariableName,Value".
        Reading the current state can be done with "Get VariableName".
        """
        target = self.port_string if target == "" else target

        # Create response buffer
        response_buffer = ctypes.create_string_buffer(buffer_size)
        response_len = ctypes.c_int()

        send_command = self.client.PolNavC_SendCommand
        send_command.argtypes = [
            ctypes.c_char_p,        # Target
            ctypes.c_char_p,        # Command
            ctypes.c_char_p,        # Response buffer (output)
            ctypes.c_int,           # MaxLen
            ctypes.POINTER(ctypes.c_int),  # ResponseLen (output by reference)
        ]

        if response_type == "str":
            send_command.restype = ctypes.c_char_p
        else:
            send_command.restype = ctypes.c_int

        send_command(
            target.encode("ascii"),
            command.encode("ascii"),
            response_buffer,
            buffer_size,
            response_len,
        )

        # Call the DLL function
        result = self.client.PolNavC_SendCommand(
            ctypes.c_char_p(target.encode("ascii")),
            ctypes.c_char_p(command.encode("ascii")),
            response_buffer,
            ctypes.c_int(buffer_size),
            ctypes.byref(response_len),  # why is this empty?
        )

        # Check for success
        if result != 0:
            msg = f"PolNav_SendCommand failed with error code: {result}"
            print(msg)
            # raise RuntimeError(msg)

        # Return the actual response string
        return response_buffer.value.decode("ascii")

    # Wrapper Functions

    def read(self) -> str:
        """Read the response from Polarization Navigator."""
        return self.client.PolNavC_ReadResponse()

    def get_sop(self) -> str:
        """Get the current SOP from the Polarization Navigator.

        Sending the 'Get CurrentSOPN' command results in an access error, which is why this function is currently not implemented.
        """
        self.send_command("Get CurrentSOPN")
        return self.read()
