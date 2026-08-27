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

import contextlib
from typing import Any, ClassVar

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()
import velox


class Device(EmptyDevice):
    """Driver class for Velox Wafer Prober Systems."""

    NOTCH_DIRECTIONS: ClassVar[dict[int, str]] = {0: "down", 90: "left", 180: "up", 270: "right"}
    """Flat/notch orientation. Velox documents this under ':prob:waf:ori' as "0 is bottom, 90 equals left,
    180 equals top, 270 equals right"; GetWaferMapParams*.FlatAngle uses the same encoding."""

    MAP_ORIGINS: ClassVar[dict[int, str]] = {1: "upper_left", 2: "upper_right", 3: "lower_left", 4: "lower_right"}
    """Corner that die coordinates are counted from, as returned by GetMapOrientation."""

    description = """
    <h3>Velox Wafer Prober</h3>
    <p>This driver controls the prober functions of FormFactor Velox wafer probers.</p>
    <h4>Setup</h4>
    <ul>
        <li>Requires Velox Installation</li>
    </ul>
    <h4>Parameters</h4>
    <ul>
        <li>Port: Use 'localhost' when running SweepMe! on the same PC as Velox. For TCP/IP remote control, enter
         the Velox PCs IP address either as blank string "192.168.XXX.XXX" or containing a specific port 
         "IP:xxx.xxx.xxx.xxx; Port:xxxx" </li>
    </ul>
    """

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
            "SweepValueWafer": ["Wafer table"],  # filled by module
        }

    def get_GUIparameter(self, parameter: dict[str, str]) -> None:  # noqa: N802
        """Handle GUI parameter values."""
        # Read with fallbacks: this also runs before the user has picked a port, and from pysweepme
        # scripts that hand over only some of the parameters.
        self.handle_port_string(parameter.get("Port", ""))
        self.load_angle = float(parameter.get("Load angle", "0.0"))
        self.sweep_mode_wafer = parameter.get("SweepValueWafer", "Wafer table")

    def handle_port_string(self, port_string: str) -> None:
        """Extract IP address and socket from port string."""
        port_string = port_string.strip().lower()
        self.target_socket = 1412

        if not port_string:
            # No port chosen yet. Reporting it here would mean raising from get_GUIparameter, which runs
            # on every parameter edit; connect_to_velox raises a readable error when it is actually needed.
            self.ip_address = ""
        elif "localhost" in port_string:
            self.ip_address = "localhost"
        elif "port" in port_string:
            self.ip_address = port_string.split(";")[0].split(":")[1].strip()
            self.target_socket = int(port_string.split(";")[1].split(":")[1].strip())
        elif "ip" in port_string:
            self.ip_address = port_string.split("ip:")[1].strip()
        else:
            # Try to interpret the port string as an IP address
            self.ip_address = port_string.strip()

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
            self.separate()
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

        self.separate()
        if self.current_die != next_die:
            self.step_to_die(next_die)

        if subsite is not None:
            self.step_to_subsite(subsite)

        self.contact()

    def call(self) -> tuple[str, str, str]:
        """Return the current wafer, die, and subsite."""
        self.update_current_position()
        return self.current_wafer, self.current_die, self.current_subsite

    "--- Wrapper Functions ---"

    def connect_to_velox(self) -> None:
        """Connect to the Velox SDK."""
        if self.msg_server is None:
            if not self.ip_address:
                msg = ("No port selected. Click 'Find Ports' and choose 'localhost' if Velox runs on this "
                       "computer, or enter the address of the Velox PC as 'IP:xxx.xxx.xxx.xxx; Port:xxxx'.")
                raise Exception(msg)

            try:
                self.msg_server = velox.MessageServerInterface(self.ip_address, self.target_socket).__enter__()
            except Exception as e:
                # Check if Velox software is running
                if "The connection to the Velox Message Server was refused." in str(e):
                    msg = "Unable to connect to Velox software. Please start Velox and try again."
                    raise Exception(msg) from e

                if isinstance(e, OSError):
                    # Any other socket-level failure, e.g. WinError 10049 for an address that does not
                    # exist on this machine. On its own that error names neither the address nor the
                    # Port field, which is the only thing the user can act on.
                    msg = (f"Unable to reach the Velox message server at '{self.ip_address}:{self.target_socket}'. "
                           "Check the Port field: use 'localhost' if Velox runs on this computer, or "
                           "'IP:xxx.xxx.xxx.xxx; Port:xxxx' for a remote Velox PC.")
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
                # Add the number to the label to ensure uniqueness, as Velox allows multiple subsites with the same label
                self.subsites[f"#{subsite_number} {label}"] = subsite_number

            subsite_number += 1

        return list(self.subsites.keys())

    def get_wafer_geometry(self) -> dict[str, Any]:
        """Return the physical geometry of the wafer map currently loaded in Velox.

        Lets the wafer map take diameter, die pitch and orientation from the prober instead of having them
        typed in by hand. Every entry is optional: a value whose command is unsupported by this Velox
        version, or which the loaded map does not carry, is returned as None instead of raising, so a
        partial answer is still usable.

        Returns:
            Dictionary with the keys:
                diameter_mm:    Wafer diameter in mm. None for a rectangular map.
                pitch_x_mm:     Die pitch in X (horizontal) in mm.
                pitch_y_mm:     Die pitch in Y (vertical) in mm.
                columns:        Number of dies across.
                rows:           Number of dies down.
                map_type:       "wafer" for a round wafer, "rectangle" for a rectangular map.
                notch:          Notch/flat position: "down", "up", "left" or "right". None for a
                                rectangular map.
                flat_length_mm: Length of the flat in mm. 0.0 on a wafer that has a notch instead.
                origin:         Corner the die coordinates count from, e.g. "upper_left".
        """
        opened_here = self.msg_server is None
        self.connect_to_velox()
        try:
            geometry: dict[str, Any] = {
                "diameter_mm": None,
                "pitch_x_mm": None,
                "pitch_y_mm": None,
                "columns": None,
                "rows": None,
                "map_type": None,
                "notch": None,
                "flat_length_mm": None,
                "origin": None,
            }

            with contextlib.suppress(velox.SciException):
                dims = velox.GetMapDims()
                geometry["map_type"] = "wafer" if str(dims.MapType).upper().startswith("W") else "rectangle"
                # Velox reports the die index in micrometres.
                geometry["pitch_x_mm"] = float(dims.XIndex) / 1000.0
                geometry["pitch_y_mm"] = float(dims.YIndex) / 1000.0
                geometry["columns"] = int(dims.Columns)
                geometry["rows"] = int(dims.Rows)

            if geometry["map_type"] != "rectangle":
                with contextlib.suppress(velox.SciException):
                    # GetWaferMapParams2 differs from GetWaferMapParams only in the units of the X/Y offsets,
                    # which are not used here — so the older command is a fine fallback on older Velox.
                    params_command = getattr(velox, "GetWaferMapParams2", velox.GetWaferMapParams)
                    params = params_command()
                    geometry["diameter_mm"] = float(params.Diameter)
                    geometry["flat_length_mm"] = float(params.FlatLength)
                    geometry["notch"] = self.NOTCH_DIRECTIONS.get(int(params.FlatAngle))
                    if geometry["pitch_x_mm"] is None:
                        geometry["pitch_x_mm"] = float(params.DieWidth) / 1000.0
                        geometry["pitch_y_mm"] = float(params.DieHeight) / 1000.0

            with contextlib.suppress(velox.SciException):
                geometry["origin"] = self.MAP_ORIGINS.get(int(velox.GetMapOrientation().Orientation))

            return geometry
        finally:
            # Only hand back the connection if this call was the one that opened it, so calling this
            # during a run does not tear down the session the measurement is using.
            if opened_here:
                self.disconnect_from_velox()

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

    def contact(self) -> None:
        """Raise the chuck to contact height, so the probes touch the wafer.

        Implementing this function enables the 'Contact' button in the wafer-map panel.
        """
        velox.MoveChuckContact()

    def separate(self) -> None:
        """Lower the chuck to separation height, so the probes come off the wafer.

        Implementing this function enables the 'Separate' button in the wafer-map panel.
        """
        velox.MoveChuckSeparation()
