# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2021-2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Switch
# * Instrument: PC Mouse

"""SweepMe! driver that moves the mouse cursor and clicks."""

from __future__ import annotations

from typing import Annotated, Any

import win32api
import win32con
from pysweepme import EmptyDevice
from pysweepme.commands import Unit, command

Pixels = Annotated[int, Unit("px")]

# GUI label, current and earlier ones -> what is swept
SWEEP_MODES: dict[str, str] = {
    "Coordinates in px": "coordinates",
    "Position x in px": "x",
    "Position y in px": "y",
    "Coordinates [(pix;pix)]": "coordinates",
    "Position x [pix]": "x",
    "Position y [pix]": "y",
}


class Device(EmptyDevice):
    """Driver that moves the mouse cursor to the sweep value and clicks if wanted (Windows only)."""

    def __init__(self) -> None:
        """Define the returned variables."""
        super().__init__()

        self.shortname = "Mouse"

        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        self.gui_parameters: dict[str, Any] = {}
        self.sweep_mode: str = "Coordinates in px"
        self.sweep_target: str = "coordinates"
        self.left_click_after_move: bool = False

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields with their defaults."""
        return {
            "SweepMode": ["Coordinates in px", "Position x in px", "Position y in px"],
            "Leftclick": False,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selections."""
        self.gui_parameters = parameters
        self.sweep_mode = parameters.get("SweepMode", "Coordinates in px")
        self.left_click_after_move = bool(parameters.get("Leftclick", False))

    def configure(self) -> None:
        """Check the sweep mode."""
        if self.sweep_mode not in SWEEP_MODES:
            allowed = ", ".join(self.update_gui_parameters({})["SweepMode"])
            msg = f"SweepMode must be one of {allowed}, not '{self.sweep_mode}'."
            raise ValueError(msg)
        self.sweep_target = SWEEP_MODES[self.sweep_mode]

    def apply(self) -> None:
        """Move the cursor to the sweep value and click if wanted."""
        if self.sweep_target == "coordinates":
            x_position, y_position = self._parse_coordinates(self.value)
        else:
            x_position, y_position = self.get_position()
            if self.sweep_target == "x":
                x_position = int(float(self.value))
            else:
                y_position = int(float(self.value))

        self.set_position(x_position, y_position)

        if self.left_click_after_move:
            self.left_click()

    # --- communication commands ---------------------------------------------
    # Coordinates are pixels of the primary screen with the origin in the LOWER left corner, x to the right and y
    # upwards - the convention of this driver's sweep values and of Logger-PC_Mouse, so a position read there can be
    # swept here as it is. Positions on other monitors lie outside the primary screen and are allowed.

    @command(returns=("width", "height"), reads="state")
    def get_screen_size(self) -> tuple[Pixels, Pixels]:
        """Return the size of the primary screen as (width, height) in pixels."""
        width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        return int(width), int(height)

    @command(returns=("x_position", "y_position"), reads="setpoint")
    def get_position(self) -> tuple[Pixels, Pixels]:
        """Return the cursor position as (x, y) in pixels, origin lower left."""
        x_position, y_position = win32api.GetCursorPos()
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        return int(x_position), int(height - 1 - y_position)

    @command
    def set_position(self, x_position: Pixels, y_position: Pixels) -> None:
        """Move the cursor to (x, y) in pixels, origin lower left."""
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        win32api.SetCursorPos((int(x_position), int(height - 1 - y_position)))

    @command
    def left_click(self) -> None:
        """Click the left mouse button at the current cursor position."""
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    @command(composite=True)
    def double_click(self) -> None:
        """Double-click the left mouse button at the current cursor position."""
        self.left_click()
        self.left_click()

    @command
    def right_click(self) -> None:
        """Click the right mouse button at the current cursor position."""
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

    # --- helpers --------------------------------------------------------------

    @staticmethod
    def _parse_coordinates(value: object) -> tuple[int, int]:
        """Return '(x;y)', 'x;y' or 'x,y' as two integers."""
        text = str(value).strip().strip("()[] ").replace(";", ",")
        parts = [part.strip() for part in text.split(",")]
        if len(parts) != 2:  # noqa: PLR2004 - x and y
            msg = f"Coordinates must be given as (x;y), got '{value}'."
            raise ValueError(msg)
        return int(float(parts[0])), int(float(parts[1]))
