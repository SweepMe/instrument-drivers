# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025-2026 SweepMe! GmbH (sweep-me.net)
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

"""SweepMe! driver of a simulated wafer prober."""

from __future__ import annotations

import math
from typing import Any

from pysweepme.commands import command
from pysweepme.EmptyDeviceClass import EmptyDevice

# Geometry of the simulated wafer. Both the probe plan and get_wafer_geometry() are derived from
# these numbers, so the wafer map always draws a die grid that matches the geometry it is handed.
WAFER_DIAMETER_MM = 150.0
DIE_PITCH_X_MM = 10.0
DIE_PITCH_Y_MM = 10.0
EDGE_EXCLUSION_MM = 5.0
WAFER_NOTCH = "down"

WAFERS: list[str] = ["C1W1", "C1W2", "C2W1"]
SUBSITES: list[str] = ["Pos 100, 50", "Pos 75, 150"]


class Device(EmptyDevice):
    """Simulated WaferProber driver."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Simulation"  # short name will be shown in the sequencer
        # The variables that can be measured by the device:
        self.variables = ["Wafer", "Die", "Die X", "Die Y", "Subsite", "Skip"]
        self.units = ["", "", "", "", "", ""]
        self.plottype = [True, True, True, True, True, True]
        self.savetype = [True, True, True, True, True, True]

        self.port_string: str = ""
        self.current_wafer: str = ""
        self.current_die: str = "0,0"
        self.current_die_x: int = 0
        self.current_die_y: int = 0
        self.current_subsite: str = ""
        self.is_contacted: bool = False
        self.skip: bool = False

    def find_ports(self) -> list[str]:
        """Find available ports and return them as a list of strings."""
        return [str(x) for x in range(10)]

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI parameters; the WaferProber module provides all fields itself."""
        return {}

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the values of the GUI parameters."""
        self.port_string = parameters.get("Port", "")

    # here functions start that are called by SweepMe! during a measurement

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        wafer = self.sweepvalues.get("Wafer")
        die = self.sweepvalues.get("Die")
        subsite = self.sweepvalues.get("Subsite")

        self.skip = False
        contacted = self.is_contacted

        # None: the sequence does not sweep it ("Current wafer", ...), so the prober stays where it is
        if wafer is not None and wafer != self.current_wafer:
            self.load_wafer(wafer)

        if die is not None and die != self.current_die:
            self.step_to_die(die)

        if subsite is not None and subsite != self.current_subsite:
            self.step_to_subsite(subsite)

        # a wafer exchange separates the probes: the sweep goes on in contact if it was in contact
        if contacted and not self.is_contacted:
            self.contact()

    def call(self) -> tuple[str, str, int, int, str, bool]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        # Split die coordinate string into x- and y-integers to allow for a simple heatmap
        try:
            x_str, y_str = self.current_die.split(",")
            self.current_die_x = int(x_str)
            self.current_die_y = int(y_str)
        except ValueError:
            msg = f"Die '{self.current_die}' must be given as two integers in the format 'x,y'."
            raise ValueError(msg) from None

        return (
            self.current_wafer,
            self.current_die,
            self.current_die_x,
            self.current_die_y,
            self.current_subsite,
            self.skip,
        )

    # --- Hooks of the WaferProber module ---

    # check_driver: ignore DC004 - a hook of the WaferProber module (Update button)
    def get_probeplan(self) -> tuple[list[str], list[str], list[str]]:
        """This function is called when the 'Update' button is pressed in the GUI.

        If this function is implemented with a 'probeplan: str = ""' parameter, it will open a file dialog to select a
        probeplan file. It reads the probeplan from a given file and returns the lists of wafers, dies, and subsites.
        """
        return list(WAFERS), self.generate_dies(), list(SUBSITES)

    # check_driver: ignore DC004 - a hook of the WaferProber module, which needs a dict back
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

    # check_driver: ignore DC004 - a hook of the WaferProber module; get_status answers it as a command
    def get_contact_state(self) -> bool:
        """Return True if the probes are currently in contact with the wafer.

        Implementing this function enables the contact-state indicator in the wafer-map panel.
        """
        return self.is_contacted

    # --- Communication commands, used e.g. by the SweepMe! Instrument Control ---
    #
    # The functions the WaferProber module calls by name, such as 'load_wafer', 'step_to_die', 'contact' or
    # 'separate', are communication commands as well.

    @command(returns=("wafer",), reads="setpoint")
    def get_current_wafer(self) -> str:
        """Returns the current wafer.

        Implementing this function enables the 'get_current_wafer' action of the WaferProber Module.
        """
        return self.current_wafer

    @command(returns=("die",), reads="setpoint")
    def get_current_die(self) -> str:
        """Returns the current die.

        Implementing this function enables the 'get_current_die' action of the WaferProber Module.
        """
        return self.current_die

    @command(returns=("subsite",), reads="setpoint")
    def get_current_subsite(self) -> str:
        """Returns the current subsite.

        Implementing this function enables the 'get_current_subsite' action of the WaferProber Module.
        """
        return self.current_subsite

    @command
    def load_wafer(self, wafer: str) -> None:
        """Checks if a wafer is loaded, unloads it if necessary, and loads the new wafer into the prober.

        Implementing this function enables the 'load_wafer' action in the right-click menu of the Wafer table.
        """
        if wafer not in WAFERS:
            msg = f"Wafer '{wafer}' is not in the probe plan. Choose one of {WAFERS}."
            raise ValueError(msg)
        if self.current_wafer != wafer:
            self.is_contacted = False
            self.current_wafer = wafer

    @command
    def unload_wafer(self) -> None:
        """Unloads a wafer from the prober. It is called when 'Unload wafer' action of the wafer table is performed."""
        self.is_contacted = False
        self.current_wafer = ""

    @command
    def step_to_die(self, die: str) -> None:
        """Move to given die. It is called when 'Step to die' action of the die table is performed."""
        die = str(die).replace(" ", "")
        if die not in self.generate_dies():
            msg = f"Die '{die}' is not on the wafer. Use 'column,row' as listed by 'get_probeplan'."
            raise ValueError(msg)
        if self.current_die != die:
            self.current_die = die

    @command
    def step_to_subsite(self, subsite: str) -> None:
        """Move to given subsite. It is called when the 'Step to subsite' action of the Subsite table is performed."""
        if str(subsite) not in SUBSITES:
            msg = f"Subsite '{subsite}' is not in the probe plan. Choose one of {SUBSITES}."
            raise ValueError(msg)
        self.current_subsite = str(subsite)

    @command
    def contact(self) -> None:
        """Raise the chuck to contact height, so the probes touch the wafer.

        Implementing this function enables the 'Contact' button in the wafer-map panel.
        """
        if not self.current_wafer:
            msg = "No wafer is loaded. Use 'load_wafer' first."
            raise ValueError(msg)
        self.is_contacted = True

    @command
    def separate(self) -> None:
        """Lower the chuck to separation height, so the probes come off the wafer.

        Implementing this function enables the 'Separate' button in the wafer-map panel.
        """
        self.is_contacted = False

    @command(returns=("wafer", "die", "subsite", "contacted"), reads="setpoint")
    def get_status(self) -> tuple[str, str, str, bool]:
        """Return (loaded wafer, die and subsite the probes stand on, whether they are contacted)."""
        return self.current_wafer, self.current_die, self.current_subsite, bool(self.is_contacted)

    # --- Helpers ---

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
