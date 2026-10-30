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

from typing import Annotated, ClassVar, Literal

from pysweepme.commands import Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

MOVE_HAZARD = "Moves the arm; keep the work area clear."

Millimetres = Annotated[float, Unit("mm")]
Axis = Annotated[Literal["x", "y", "z"], Selector()]


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
            if axis not in self.sweepvalues:
                continue
            value = self.sweepvalues[axis]
            if value is None:
                continue
            # str() also catches a float nan, which would slip past the literal "nan" check.
            text = str(value).strip()
            if text.lower() in ("", "nan"):
                continue
            self.position[axis] = float(text)

    def call(self) -> list[float]:
        """Return the simulated current position of each axis."""
        return [self.position["x"], self.position["y"], self.position["z"]]

    @command(hazards=MOVE_HAZARD)
    def go_home(self) -> None:
        """Move all axes to the origin. Called by the 'Go home' button."""
        for axis in self.position:
            self.position[axis] = 0.0

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The simulated robot has three Cartesian axes in mm. Moving is instantaneous, there are no travel limits. The
    commands do not need 'initialize' or 'configure'.
    """

    @command(hazards=MOVE_HAZARD)
    def move_axis(self, axis: Axis, position: Millimetres) -> None:
        """Move one axis to an absolute position in mm."""
        self.position[axis] = position

    @command(kind="run", hazards=MOVE_HAZARD)
    def move_to(self, x: Millimetres, y: Millimetres, z: Millimetres) -> None:
        """Move all three axes to an absolute position in mm."""
        target = {"x": x, "y": y, "z": z}
        self.position.update(target)

    @command(returns=("x", "y", "z"), reads="setpoint")
    def get_position(self) -> tuple[Millimetres, Millimetres, Millimetres]:
        """Return the position (x in mm, y in mm, z in mm)."""
        return self.position["x"], self.position["y"], self.position["z"]
