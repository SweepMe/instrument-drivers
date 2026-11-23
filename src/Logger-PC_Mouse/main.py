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
# * Module: Logger
# * Instrument: PC Mouse

"""SweepMe! driver that reads the mouse cursor position and the mouse buttons."""

from __future__ import annotations

from typing import Annotated

import win32api
import win32con
from pysweepme import EmptyDevice
from pysweepme.commands import Unit, command

Pixels = Annotated[int, Unit("px")]


class Device(EmptyDevice):
    """Driver that reads the position of the mouse cursor and the state of the mouse buttons (Windows only)."""

    def __init__(self) -> None:
        """Define the returned variables."""
        super().__init__()

        self.shortname = "Mouse"

        self.variables = ["x", "y", "x_press", "y_press", "Left_clicked", "Right_clicked"]
        self.units = ["px", "px", "px", "px", "", ""]
        self.plottype = [True, True, True, True, False, False]
        self.savetype = [True, True, True, True, True, True]

        self.x: float = float("nan")
        self.y: float = float("nan")
        self.x_press: float = float("nan")
        self.y_press: float = float("nan")
        self.button_left: int = 0
        self.button_right: int = 0

    def measure(self) -> None:
        """Read the cursor position and the button states."""
        try:
            self.x, self.y = self.get_position()
        except win32api.error:
            # no cursor exists while a secure desktop is shown, e.g. the Task Manager with elevated rights
            self.x, self.y = float("nan"), float("nan")

        self.button_left, self.button_right = self.get_button_states()

    def process_data(self) -> None:
        """Keep the position as press position while the left button is down."""
        if self.button_left < 0:
            self.x_press = self.x
            self.y_press = self.y
        else:
            self.x_press = float("nan")
            self.y_press = float("nan")

    def call(self) -> list[float]:
        """Return position, press position and button states."""
        return [self.x, self.y, self.x_press, self.y_press, self.button_left, self.button_right]

    # --- communication commands ---------------------------------------------
    # Coordinates are pixels of the primary screen with the origin in the LOWER left corner, x to the right and y
    # upwards, as in Switch-PC_Mouse, so a position read here can be swept there as it is.

    @command(returns=("width", "height"), reads="state")
    def get_screen_size(self) -> tuple[Pixels, Pixels]:
        """Return the size of the primary screen as (width, height) in pixels."""
        width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        return int(width), int(height)

    @command(returns=("x_position", "y_position"))
    def get_position(self) -> tuple[Pixels, Pixels]:
        """Return the cursor position as (x, y) in pixels, origin lower left."""
        x_position, y_position = win32api.GetCursorPos()
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        return int(x_position), int(height - 1 - y_position)

    @command(returns=("left_button_state", "right_button_state"), reads="state")
    def get_button_states(self) -> tuple[int, int]:
        """Return the Windows key state of the left and right button: negative while the button is pressed."""
        return int(win32api.GetKeyState(win32con.VK_LBUTTON)), int(win32api.GetKeyState(win32con.VK_RBUTTON))
