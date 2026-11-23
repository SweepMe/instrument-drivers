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
# * Instrument: PC Time

"""SweepMe! driver that returns the elapsed time, clock and date of the PC."""

from __future__ import annotations

import datetime as dt
import time
from typing import Any, ClassVar

from pysweepme import EmptyDevice
from pysweepme.commands import command

# GUI label -> the lifecycle step that resets the time to zero
ZERO_TIME_ON: dict[str, str] = {
    "initialize": "initialize",
    "configure": "configure",
    "signin": "signin",
}

# GUI check box -> variable, unit and plottype of the value it adds
TIME_VARIABLES: dict[str, tuple[str, str, bool]] = {
    "Seconds": ("Time", "s", True),
    "Minutes": ("Time", "min", True),
    "Hours": ("Time", "h", True),
    "Days": ("Days", "d", True),
    "Clock": ("Clock", "", False),
    "Date": ("Date", "", False),
    "Timestamp": ("Timestamp", "", False),
}


class Device(EmptyDevice):
    """Driver that returns the time elapsed since a lifecycle step, the clock and the date of the PC."""

    actions: ClassVar[list[str]] = ["zero_time"]  # released to the ActionManager, e.g. for a button

    def __init__(self) -> None:
        """Define the returned variables."""
        super().__init__()

        self.shortname = "Time"

        self.variables = ["Time", "Time", "Time", "Timestamp"]
        self.units = ["s", "min", "h", ""]
        self.plottype = [True, True, True, False]
        self.savetype = [True, True, True, True]

        self.gui_parameters: dict[str, Any] = {}
        self.selected: dict[str, bool] = dict.fromkeys(TIME_VARIABLES, False)
        self.zero_time_on: str = "initialize"

        self.starttime: float = time.perf_counter()  # overwritten by zero_time during the run

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields with their defaults."""
        return {
            "Seconds": True,
            "Minutes": True,
            "Hours": True,
            "Days": False,
            "Clock": False,
            "Date": False,
            "Timestamp": True,
            "Zero time on": list(ZERO_TIME_ON),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selections and define the variables of the checked values."""
        self.gui_parameters = parameters
        defaults = self.update_gui_parameters({})
        self.selected = {key: bool(parameters.get(key, defaults[key])) for key in TIME_VARIABLES}
        self.zero_time_on = parameters.get("Zero time on", "initialize")

        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        for key, (variable, unit, plot) in TIME_VARIABLES.items():
            if self.selected[key]:
                self.variables.append(variable)
                self.units.append(unit)
                self.plottype.append(plot)
                self.savetype.append(True)

    def initialize(self) -> None:
        """Reset the time if it is zeroed at the start of the run."""
        if ZERO_TIME_ON.get(self.zero_time_on) == "initialize":
            self.zero_time()

    def configure(self) -> None:
        """Check the selection and reset the time if it is zeroed when entering the branch."""
        if self.zero_time_on not in ZERO_TIME_ON:
            msg = f"Zero time on must be one of {', '.join(ZERO_TIME_ON)}, not '{self.zero_time_on}'."
            raise ValueError(msg)
        if ZERO_TIME_ON[self.zero_time_on] == "configure":
            self.zero_time()

    def signin(self) -> None:
        """Reset the time if it is zeroed for each variation of the modules above."""
        if ZERO_TIME_ON.get(self.zero_time_on) == "signin":
            self.zero_time()

    def call(self) -> list[Any]:
        """Return the checked values in the order of the variables."""
        duration = time.perf_counter() - self.starttime
        now = time.localtime()

        values: dict[str, Any] = {
            "Seconds": duration,
            "Minutes": duration / 60.0,
            "Hours": duration / 3600.0,
            "Days": duration / 3600.0 / 24.0,
            "Clock": f"'{now.tm_hour:02d}:{now.tm_min:02d}:{now.tm_sec:02d}'",
            "Date": f"{now.tm_year:04d}/{now.tm_mon:02d}/{now.tm_mday:02d}",
            "Timestamp": dt.datetime.now(),  # noqa: DTZ005 - local time of the PC, as before
        }
        return [values[key] for key in TIME_VARIABLES if self.selected[key]]

    # --- communication commands ---------------------------------------------

    @command
    def zero_time(self) -> None:
        """Reset the elapsed time to zero."""
        self.starttime = time.perf_counter()
