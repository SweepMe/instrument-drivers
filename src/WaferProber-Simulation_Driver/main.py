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
# * Instrument: Simulated WaferProber

from __future__ import annotations

import math
from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice

# Geometry of the simulated wafer. Both the probe plan and get_wafer_geometry() are derived from
# these numbers, so the wafer map always draws a die grid that matches the geometry it is handed.
WAFER_DIAMETER_MM = 150.0
DIE_PITCH_X_MM = 10.0
DIE_PITCH_Y_MM = 10.0
EDGE_EXCLUSION_MM = 5.0
WAFER_NOTCH = "down"


class Device(EmptyDevice):
    """Simulated WaferProber driver."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Simulation"  # short name will be shown in the sequencer
        # The variables that can be measured by the device:
        self.variables = ["Wafer", "Die", "Die X", "Die Y", "Subsite", "Skip"]
        self.units = ["", "", "", "", "", ""]
        self.plottype = [True, True, True, True, True, True]
        self.savetype = [True, True, True, True, True, True]

        # use/uncomment the next line to use the port manager
        # self.port_manager = True

        # use/uncomment the next line to select the interfaces that should be presented to the user if you have enabled
        # the port manager in the previous step
        # self.port_types = ["COM", "GPIB", "USB"]

        self.current_wafer: str = ""
        self.current_die: str = "0,0"
        self.current_die_x: int = 0
        self.current_die_y: int = 0
        self.current_subsite: str = ""
        self.is_contacted: bool = False

    def find_ports(self) -> list[str]:
        """Find available ports and return them as a list of strings."""
        return [str(x) for x in range(10)]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {}

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]  # can be used to enable device communication

    # here functions start that only exists for the WaferProber module and are called by this module

    def get_probeplan(self) -> tuple[list[str], list[str], list[str]]:
        """This function is called when the 'Update' button is pressed in the GUI.

        If this function is implemented with a 'probeplan: str = ""' parameter, it will open a file dialog to select a
        probeplan file. It reads the probeplan from a given file and returns the lists of wafers, dies, and subsites.
        """
        wafers = ["C1W1", "C1W2", "C2W1"]
        dies = self.generate_dies()
        subsites = ["Pos 100, 50", "Pos 75, 150"]

        return wafers, dies, subsites

    @staticmethod
    def generate_dies() -> list[str]:
        """Return the dies of a round wafer in probing order, as 'column,row' strings.

        The grid is clipped to the usable radius so the wafer map shows a wafer shape rather than a
        rectangle, and rows alternate direction the way a real probe plan does, so the chuck does not
        travel back across the wafer at the end of every row.
        """
        usable_radius_mm = WAFER_DIAMETER_MM / 2.0 - EDGE_EXCLUSION_MM
        columns = int(usable_radius_mm // DIE_PITCH_X_MM)
        rows = int(usable_radius_mm // DIE_PITCH_Y_MM)

        dies = []
        for row in range(rows, -rows - 1, -1):
            row_dies = []
            for column in range(-columns, columns + 1):
                # Measure to the far corner of the die, so a die counts only if it fits completely.
                x_mm = abs(column) * DIE_PITCH_X_MM + DIE_PITCH_X_MM / 2.0
                y_mm = abs(row) * DIE_PITCH_Y_MM + DIE_PITCH_Y_MM / 2.0
                if math.hypot(x_mm, y_mm) <= usable_radius_mm:
                    row_dies.append(f"{column},{row}")

            if (rows - row) % 2:
                row_dies.reverse()
            dies.extend(row_dies)

        return dies

    def get_wafer_geometry(self) -> dict[str, Any]:
        """Return the geometry of the simulated wafer.

        Implementing this function lets the WaferProber module fill in the wafer geometry of its Map tab
        when 'Update' is pressed, instead of the user typing diameter and die pitch by hand.
        """
        usable_radius_mm = WAFER_DIAMETER_MM / 2.0 - EDGE_EXCLUSION_MM
        return {
            "diameter_mm": WAFER_DIAMETER_MM,
            "pitch_x_mm": DIE_PITCH_X_MM,
            "pitch_y_mm": DIE_PITCH_Y_MM,
            "columns": 2 * int(usable_radius_mm // DIE_PITCH_X_MM) + 1,
            "rows": 2 * int(usable_radius_mm // DIE_PITCH_Y_MM) + 1,
            "map_type": "wafer",
            "notch": WAFER_NOTCH,
            "flat_length_mm": 0.0,
            # The simulated dies are counted from the wafer centre, which is none of the four corner
            # origins - so no convention is reported and the module leaves that setting alone.
            "origin": None,
        }

    def get_current_wafer(self) -> str:
        """Returns the current wafer.

        Implementing this function enables the 'get_current_wafer' action of the WaferProber Module.
        """
        return self.current_wafer

    def get_current_die(self) -> str:
        """Returns the current die.

        Implementing this function enables the 'get_current_die' action of the WaferProber Module.
        """
        return self.current_die

    def get_current_subsite(self) -> str:
        """Returns the current subsite.

        Implementing this function enables the 'get_current_subsite' action of the WaferProber Module.
        """
        return self.current_subsite

    def load_wafer(self, wafer: str) -> None:
        """Checks if a wafer is loaded, unloads it if necessary, and loads the new wafer into the prober.

        Implementing this function enables the 'load_wafer' action in the right-click menu of the Wafer table.
        """
        if self.current_wafer != wafer:
            self.current_wafer = wafer

    def unload_wafer(self) -> None:
        """Unloads a wafer from the prober. It is called when 'Unload wafer' action of the wafer table is performed."""
        self.current_wafer = ""

    def step_to_die(self, die: str) -> None:
        """Move to given die. It is called when 'Step to die' action of the die table is performed."""
        if self.current_die != die:
            self.current_die = die

    def step_to_subsite(self, subsite: int | str) -> None:
        """Move to given subsite. It is called when the 'Step to subsite' action of the Subsite table is performed."""
        self.current_subsite = str(subsite)

    def contact(self) -> None:
        """Raise the chuck to contact height, so the probes touch the wafer.

        Implementing this function enables the 'Contact' button in the wafer-map panel.
        """
        print("Contacting wafer...")
        self.is_contacted = True

    def separate(self) -> None:
        """Lower the chuck to separation height, so the probes come off the wafer.

        Implementing this function enables the 'Separate' button in the wafer-map panel.
        """
        print("Separating wafer...")
        self.is_contacted = False

    def get_contact_state(self) -> bool:
        """Return True if the probes are currently in contact with the wafer.

        Implementing this function enables the contact-state indicator in the wafer-map panel.
        """
        return self.is_contacted

    # here functions start that are called by SweepMe! during a measurement

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        wafer = self.sweepvalues["Wafer"]
        die = self.sweepvalues["Die"]
        subsite = self.sweepvalues["Subsite"]

        self.skip = False

        if wafer != self.current_wafer:
            self.load_wafer(wafer)

        if die != self.current_die:
            self.step_to_die(die)

        if subsite != self.current_subsite:
            self.step_to_subsite(subsite)

    def reach(self) -> None:
        """'reach' can be added to make sure the latest setvalue applied during 'apply' is reached."""

    def call(self) -> tuple[str, str, int, int, str, bool]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        # Split die coordinate string into x- and y-integers to allow for a simple heatmap
        try:
            x_str, y_str = self.current_die.split(",")
            self.current_die_x = int(x_str)
            self.current_die_y = int(y_str)
        except ValueError:
            raise ValueError("Die coordinates of the die need to be integers in the format 'x,y'.")

        return (self.current_wafer,
                self.current_die,
                self.current_die_x,
                self.current_die_y,
                self.current_subsite,
                self.skip)
