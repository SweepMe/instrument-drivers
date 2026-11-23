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
# * Instrument: PC Variable Wait

"""SweepMe! driver that adds a swept hold or delay time."""

from __future__ import annotations

import time
from typing import Any

from pysweepme import EmptyDevice

# GUI label, current and earlier ones -> kind of wait
WAIT_MODES: dict[str, str] = {
    "Hold in s": "Hold",
    "Delay in s": "Delay",
    "Hold [s]": "Hold",
    "Delay [s]": "Delay",
}

POLL_INTERVAL_S = 0.01  # how often a wait checks whether the run was stopped


class Device(EmptyDevice):
    """Driver that adds a hold or delay time given by the sweep value."""

    def __init__(self) -> None:
        """Define the returned variables."""
        super().__init__()

        self.shortname = "VariableWait"

        self.variables = ["Hold time"]
        self.units = ["s"]
        self.plottype = [True]
        self.savetype = [True]

        self.gui_parameters: dict[str, Any] = {}
        self.sweep_mode: str = "Hold in s"
        self.wait_mode: str = "Hold"
        self.wait_time: float = float("nan")
        self.ref_time: float = float("-inf")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields with their defaults."""
        return {
            "SweepMode": ["Hold in s", "Delay in s"],
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the sweep mode and name the variable after it: 'Hold time' or 'Delay time'."""
        self.gui_parameters = parameters
        self.sweep_mode = parameters.get("SweepMode", "Hold in s")
        self.wait_mode = WAIT_MODES.get(self.sweep_mode, "Hold")
        self.shortname = self.wait_mode
        self.variables = [f"{self.wait_mode} time"]

    def initialize(self) -> None:
        """Start without a previous point, so the first delay does not wait."""
        self.ref_time = float("-inf")

    def configure(self) -> None:
        """Check the sweep mode."""
        if self.sweep_mode not in WAIT_MODES:
            allowed = ", ".join(self.update_gui_parameters({})["SweepMode"])
            msg = f"SweepMode must be one of {allowed}, not '{self.sweep_mode}'."
            raise ValueError(msg)
        self.wait_mode = WAIT_MODES[self.sweep_mode]

    def start(self) -> None:
        """Read the wait time; a delay waits here until the time since the start of the previous point passed."""
        self.wait_time = float(self.value)
        if self.wait_time < 0:
            msg = f"The {self.wait_mode.lower()} time must not be negative, got {self.wait_time} s."
            raise ValueError(msg)

        if self.wait_mode == "Delay":
            self._wait_until(self.ref_time + self.wait_time)
            self.ref_time = time.perf_counter()

    def adapt(self) -> None:
        """A hold waits here, after all modules of the branch applied and reached their values."""
        if self.wait_mode == "Hold":
            self._wait_until(time.perf_counter() + self.wait_time)

    def call(self) -> float:
        """Return the wait time."""
        return self.wait_time

    # --- helpers --------------------------------------------------------------

    def _wait_until(self, end_time: float) -> None:
        """Wait until perf_counter reaches end_time or the run is stopped."""
        while time.perf_counter() < end_time and not self.is_run_stopped():
            time.sleep(min(POLL_INTERVAL_S, max(0.0, end_time - time.perf_counter())))
