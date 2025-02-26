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

# SweepMe! driver
# * Module: WaferProber
# * Instrument: Velox

from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()
import velox


class Device(EmptyDevice):
    """Driver class for Velox Wafer Prober Systems."""

    def __init__(self) -> None:
        """Initialize measurement and analysis parameter."""
        EmptyDevice.__init__(self)

        self.shortname = "Velox"
        self.variables = ["Wafer", "Die", "Subsite"]  # defines as much variables you want
        self.units = ["", "", ""]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        # Device Communication
        self.ip_address: str = "localhost"
        self.target_socket: int = 1412
        self.msg_server: velox.MessageServerInterface | None = None

        # Position Parameters
        self.loader_is_connected: bool = False
        self.load_angle: float = 0.
        """Angle in degrees to rotate the wafer during loading."""

        self.subsites: dict = {}
        """Dictionary containing the subsite labels and their corresponding subsite number."""

        self.sweep_mode_wafer: str = "Wafer table"
        self.current_wafer: str = ""
        self.current_die: str = ""
        self.current_subsite: str = ""

    def __del__(self) -> None:
        """Exit Velox Communication before instance is deleted."""
        self.disconnect_from_velox()

    @staticmethod
    def find_ports() -> list[str]:
        """Return a placeholder to enter an IP address and socket."""
        return ["localhost", "IP:xxx.xxx.xxx.xxx; Port:xxxx"]

    def set_GUIparameter(self) -> dict[str, float]:  # noqa: N802
        """Define standard GUI parameter values."""
        return {
            "Load angle": 0.,
        }

    def get_GUIparameter(self, parameter: dict[str, str]) -> None:  # noqa: N802
        """Handle GUI parameter values."""
        self.handle_port_string(parameter["Port"])
        self.load_angle = float(parameter["Load angle"])
        self.sweep_mode_wafer = parameter["SweepValueWafer"]

    def handle_port_string(self, port_string: str) -> None:
        """Extract IP address and socket from port string."""
        if port_string == "localhost":
            self.ip_address = "localhost"
            self.target_socket = 1412
        elif "Port:" in port_string:
            self.ip_address = port_string.split(";")[0].split(":")[1].strip()
            self.target_socket = int(port_string.split(";")[1].split(":")[1].strip())
        elif "IP:" in port_string:
            self.ip_address = port_string.split("IP:")[1].strip()
            self.target_socket = 1412

    def connect(self) -> None:
        """Establish connection to Velox Software."""
        self.connect_to_velox()
        self.loader_is_connected = self.check_loader_status()

    def disconnect(self) -> None:
        """Disconnect from Velox Software."""
        self.disconnect_from_velox()

    def configure(self) -> None:
        """Prepare the device for the measurement."""
        if self.loader_is_connected:
            velox.SetExternalMode("R")  # Enable remote control for loader module

        self.update_current_position()

    def unconfigure(self) -> None:
        """Reset the device after the measurement."""
        # If no wafer sweep was done or no loader is connected, move to separation without unload
        if self.sweep_mode_wafer == "Current wafer" or not self.loader_is_connected:
            velox.MoveChuckSeparation()
        else:
            self.unload_wafer()

        if self.loader_is_connected:
            velox.SetExternalMode("L")  # Restore local mode

    def apply(self) -> None:
        """Move to the next selected wafer, die, and subsite."""
        next_wafer = self.sweepvalues["Wafer"]
        next_die = self.sweepvalues["Die"]
        subsite = self.sweepvalues["Subsite"]

        self.update_current_position()

        # Must not move to Separation before unloading / loading wafer as this will throw an error if the last action
        # was to unload a wafer.
        if self.loader_is_connected and self.current_wafer != next_wafer:
            self.unload_wafer()
            self.load_wafer(next_wafer, self.load_angle)

        velox.MoveChuckSeparation()
        if self.current_die != next_die:
            self.step_to_die(next_die)

        if subsite is not None:
            self.step_to_subsite(subsite)

        velox.MoveChuckContact()

    def reach(self) -> None:
        """After the new position is reached, go to contact."""

    def call(self) -> tuple[str, str, str]:
        """Return the current wafer, die, and subsite."""
        self.update_current_position()
        return self.current_wafer, self.current_die, self.current_subsite

    "--- Wrapper Functions ---"

    def connect_to_velox(self) -> None:
        """Connect to the Velox SDK."""
        if self.msg_server is None:
            try:
                self.msg_server = velox.MessageServerInterface(self.ip_address, self.target_socket).__enter__()
            except Exception as e:
                # Check if Velox software is running
                if "The connection to the Velox Message Server was refused." in str(e):
                    msg = "Unable to connect to Velox software. Please start Velox and try again."
                    raise Exception(msg) from e

                raise e

    def disconnect_from_velox(self) -> None:
        """Disconnect from Velox Software."""
        if self.msg_server is not None:
            self.msg_server.__exit__(None, None, None)
            self.msg_server = None

    def get_probeplan(self) -> tuple[list[str], list[str], list[str]]:
        """Return selected wafers, dies, and subsites. The currently loaded wafermap in VeloxPro is used."""
        self.connect_to_velox()

        wafer = self.get_wafer_list()
        dies = self.get_die_list()
        subsites = self.get_subsite_list()

        self.disconnect_from_velox()

        if wafer:
            return wafer, dies, subsites
        else:
            # If only a single wafer is loaded, return only dies and subsites to avoid displaying an empty wafer label
            return dies, subsites

    def get_wafer_list(self) -> list[str]:
        """Check if a loader is connected and return a list of all available wafers in its cassette."""
        wafer = []
        if self.check_loader_status():
            status_strings = velox.GetCassetteStatus().split(";")
            for status_string in status_strings:
                # status_string: [0] Cassette, [1] Slot, [2] SlotStatus, [3] WaferIDStatus, [4] WaferID (if present)
                slot_status = status_string.split(" ")[2]

                if slot_status in ("Testing", "Present"):
                    wafer_id = status_string.split(" ")[4]  # check here bc if slot is empty, this will fail
                    wafer.append(wafer_id)

            if not wafer:  # Cassette is empty, get only currently loaded wafer
                wafer = [velox.GetWaferID()]

        return wafer

    def get_die_list(self) -> list[str]:
        """Get a list of all selected dies on the current wafer in format x,y."""
        dies = []
        for n in range(1, velox.GetNumSelectedDies() + 1):
            ret = velox.GetDieDataAsNum(n)
            dies.append(f"{ret[1]},{ret[2]}")
        return dies

    def get_subsite_list(self) -> list[str]:
        """Return a list of all enabled subsite labels. Update self.subsites."""
        self.subsites = {}
        subsite_number = 0
        # GetDieInfo returns only the number of selected subsites, not the total number of subsites
        while True:
            try:
                subdie_data = velox.GetSubDieData(subsite_number)
            except IndexError:
                # If no subdie label is defined, velox returns an IndexError. Use subsite number as placeholder label.
                subdie_data = ["", "", "", str(subsite_number)]

            except velox.SciException:
                # End of subdie list reached
                break

            label = subdie_data[3]

            status = velox.GetSubDieStatus(subsite_number)
            if status == "E":  # Enabled
                self.subsites[label] = subsite_number

            subsite_number += 1

        return list(self.subsites.keys())

    def check_loader_status(self) -> bool:
        """Check if a loader is connected to the Velox software."""
        loader_is_connected = True
        try:
            status = velox.GetProbingStatus()
            if status == "Error":
                loader_is_connected = False
        except:
            loader_is_connected = False

        return loader_is_connected

    def get_current_wafer(self) -> str:
        """Return the current wafer ID."""
        return str(velox.GetWaferID())

    def get_current_die(self) -> str:
        """Return the current die position in format [x,y]."""
        self.update_current_position()
        return self.current_die

    def get_current_subsite(self) -> str:
        """Return the current subsite number."""
        self.update_current_position()
        return self.current_subsite

    def update_current_position(self) -> None:
        """Return the current die position and subsite number."""
        self.current_wafer = self.get_current_wafer()

        ret = velox.ReadMapPosition2()
        die_x = ret[0]
        die_y = ret[1]
        subsite = ret[4]

        self.current_die = f"{die_x},{die_y}"
        self.current_subsite = str(subsite)

    def load_wafer(self, wafer: str, alignment_angle: float = 0) -> None:
        """Checks if a wafer is loaded, unloads it if necessary, and loads the new wafer into the prober.

        Currently untested.
        """
        slot_id = -1
        port_id = -1

        # find slot id for given wafer id
        status_strings = velox.GetCassetteStatus().split(";")
        for status_string in status_strings:
            if status_string.split(" ")[2] == "Present":
                wafer_id = status_string.split(" ")[4]
                if wafer_id == wafer:
                    port_id = int(status_string.split(" ")[0])
                    slot_id = int(status_string.split(" ")[1])
                    break

        # TODO: Check if port_id must be chosen differently when using two cassettes
        velox.LoadWafer(port_id, slot_id, str(alignment_angle))
        # Perform wafer alignment on chuck
        velox.ProcessWafer("Prober")

    def unload_wafer(self) -> None:
        """Unloads a wafer from the prober."""
        # Cannot unload if no wafer on chuck
        if self.get_current_wafer() == "":
            return

        if self.loader_is_connected:
            try:
                velox.UnloadWafer()
            except velox.SciException as e:
                # Double check if no wafer is present - unsure if this only occurs in demo mode
                if "does not have a wafer" in str(e):
                    pass
                else:
                    raise e

    def step_to_die(self, position: str) -> None:
        """Move to die with coordinates [x,y]."""
        x, y = position.split(",")
        ret = velox.StepNextDie(int(x), int(y))

        new_x = ret[0]
        new_y = ret[1]
        new_subsite = ret[2]

        self.current_die = f"{new_x},{new_y}"
        self.current_subsite = str(new_subsite)

    def step_to_subsite(self, subsite: str) -> None:
        """Move to subsite with number subsite."""
        subsite_number = self.subsites[subsite]
        ret = velox.StepNextSubDie(subsite_number)
        self.current_subsite = str(ret)
