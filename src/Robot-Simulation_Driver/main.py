# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Robot
# * Instrument: Simulated Robot

from __future__ import annotations

from typing import ClassVar

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Simulated Robot driver with three Cartesian axes."""

    axes: ClassVar[dict[str, dict[str, float]]] = {
        "x": {"Value": 0.0},
        "y": {"Value": 0.0},
        "z": {"Value": 0.0},
    }

    def __init__(self) -> None:
        """Initialize the device class and default parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Simulation"
        self.port_manager = False

        self.variables = ["x", "y", "z"]
        self.units = ["mm", "mm", "mm"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        self.position: dict[str, float] = {"x": 0.0, "y": 0.0, "z": 0.0}

        self.go_home_start: bool = True
        self.go_home_end: bool = False

    def find_ports(self) -> list[str]:
        """Return a single simulated port."""
        return ["Simulated Port"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Return defaults for the Robot module checkboxes."""
        return {
            "GoHomeStart": True,
            "GoHomeEnd": False,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Read the user's GUI selections."""
        self.go_home_start = bool(parameter.get("GoHomeStart", True))
        self.go_home_end = bool(parameter.get("GoHomeEnd", False))

    def initialize(self) -> None:
        """Optionally move to the home position before the run."""
        if self.go_home_start:
            self.go_home()

    def deinitialize(self) -> None:
        """Optionally move to the home position after the run."""
        if self.go_home_end:
            self.go_home()

    def apply(self) -> None:
        """Move each axis to the target value provided by the Robot module."""
        for axis in self.position:
            if axis in self.sweepvalues:
                value = self.sweepvalues[axis]
                if value not in (None, "", "nan"):
                    self.position[axis] = float(value)

    def call(self) -> list[float]:
        """Return the simulated current position of each axis."""
        return [self.position["x"], self.position["y"], self.position["z"]]

    def go_home(self) -> None:
        """Move all axes to the origin. Called by the 'Go home' button."""
        for axis in self.position:
            self.position[axis] = 0.0
