# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
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
# Device: Mouse


from EmptyDeviceClass import EmptyDevice
import win32api, win32con
import sys
import os

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "Mouse"
        
        self.variables = []
        self.units = []
        self.plottype = [] # define if it can be plotted
        self.savetype = [] # define if it can be plotted
        
        self.width = win32api.GetSystemMetrics(0)
        self.height = win32api.GetSystemMetrics(1)
        
        # self.mouse = Controller()
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Coordinates [(pix;pix)]", "Position x [pix]", "Position y [pix]"],
                        "Leftclick" : False,
                        }               
        return GUIparameter
        
    def get_GUIparameter(self, parameter):

        self.function = parameter["SweepMode"]

        self.Leftclick = parameter["Leftclick"]
        
    def apply(self):

        x_pos, y_pos = self.get_position()

        if self.function == "Position x [pix]":
            x_pos = int(float(self.value))

        if self.function == "Position y [pix]":
            y_pos = int(float(self.value))

        if self.function == "Coordinates [(pix;pix)]":
            x_pos, y_pos = self._parse_coordinates(self.value)

        self.set_position(x_pos, y_pos)

        if self.Leftclick:
            self.left_click()

    @staticmethod
    def _parse_coordinates(value) -> tuple:
        """'(x;y)', 'x;y' or 'x,y' as two integers."""
        text = str(value).strip().strip("()[] ").replace(";", ",")
        parts = [part.strip() for part in text.split(",")]
        if len(parts) != 2:
            msg = f"Coordinates must be given as (x;y), got '{value}'."
            raise ValueError(msg)
        return int(float(parts[0])), int(float(parts[1]))

    # --- communication commands ---------------------------------------------
    # Coordinates are pixels of the primary screen with the origin in the
    # LOWER left corner, x to the right and y upwards - the convention of this
    # driver's sweep values, so a position read here can be swept as it is.

    def get_screen_size(self) -> tuple:
        """Return the size of the primary screen as (width, height) in pixels."""
        return self.width, self.height

    def get_position(self) -> tuple:
        """Return the cursor position as (x, y) in pixels, origin lower left."""
        x_pos, y_pos = win32api.GetCursorPos()
        return x_pos, self.height - 1 - y_pos

    def set_position(self, x: int, y: int) -> None:
        """Move the cursor to (x, y) in pixels, origin lower left."""
        win32api.SetCursorPos((int(x), self.height - 1 - int(y)))

    def left_click(self) -> None:
        """Click the left mouse button at the current cursor position."""
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    def double_click(self) -> None:
        """Double-click the left mouse button at the current cursor position."""
        self.left_click()
        self.left_click()

    def right_click(self) -> None:
        """Click the right mouse button at the current cursor position."""
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
