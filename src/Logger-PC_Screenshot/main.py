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
# * Instrument: PC Screenshot

"""SweepMe! driver that saves screenshots of a monitor."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Annotated, Any

import mss
import mss.tools
from pysweepme import EmptyDevice
from pysweepme.commands import Range, Selector, Unit, command

Pixels = Annotated[int, Unit("px")]
Monitor = Annotated[int, Selector(), Range(0, None)]  # 0 the whole virtual screen, 1 the primary monitor, ...

# GUI keys of the region; an empty field means the edge of the monitor
REGION_KEYS = ("x1", "y1", "x2", "y2")


class Device(EmptyDevice):
    """Driver that saves a screenshot of a monitor or a region of it as PNG file and returns its path."""

    def __init__(self) -> None:
        """Define the returned variables."""
        super().__init__()

        self.shortname = "Screenshot"

        self.variables = ["Path"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [False]

        self.gui_parameters: dict[str, Any] = {}
        self.label: str = ""
        # names the files instead of the label when it is empty, so unlabelled instances do not share file names
        self.instance_id: str = uuid.uuid4().hex[:8]
        self.monitor_number: int = 1
        self.region: tuple[int, int, int, int] = (0, 0, 0, 0)
        self.file_suffix: str = "_Screenshot"
        self.tempfolder: str = ""
        self.index: int = 0
        self.path_to_file: str = ""

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields with their defaults: leave x1, y1, x2 and y2 empty for the whole monitor."""
        return {
            "x1": "",
            "y1": "",
            "x2": "",
            "y2": "",
            "Monitor": 1,
            "File suffix": "Screenshot",
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selections."""
        self.gui_parameters = parameters
        # pysweepme passes no label; an empty string is used then
        self.label = parameters.get("Label", "")

    def initialize(self) -> None:
        """Start the numbering of the files of this run."""
        self.tempfolder = self.get_folder("TEMP")
        self.index = 0

    def configure(self) -> None:
        """Convert and check monitor, region and file suffix."""
        monitor = self.gui_parameters.get("Monitor", 1)
        try:
            self.monitor_number = int(monitor)
        except ValueError:
            msg = f"Monitor must be a whole number such as 1 for the primary monitor, not '{monitor}'."
            raise ValueError(msg) from None

        width, height = self.get_screen_size(self.monitor_number)
        edges = (0, 0, width, height)
        corners = []
        for key, edge in zip(REGION_KEYS, edges, strict=True):
            text = str(self.gui_parameters.get(key, "")).strip()
            try:
                corners.append(int(text) if text else edge)
            except ValueError:
                msg = f"{key} must be a whole number of pixels or empty for the edge of the monitor, not '{text}'."
                raise ValueError(msg) from None
        x1, y1, x2, y2 = corners
        self.region = (x1, y1, x2, y2)
        self._check_region(self.monitor_number, width, height, self.region)

        file_suffix = str(self.gui_parameters.get("File suffix", "Screenshot"))
        self.file_suffix = f"_{file_suffix}" if file_suffix else ""

    def start(self) -> None:
        """Choose the file of this point in the temporary folder of the run."""
        self.index += 1
        name = self.label or self.instance_id
        self.path_to_file = str(Path(self.tempfolder) / f"temp_{name}{self.file_suffix}_{self.index}.png")

    def measure(self) -> None:
        """Save the screenshot of the region; a file of an earlier run with the same name is replaced."""
        Path(self.path_to_file).unlink(missing_ok=True)
        self.take_screenshot(self.path_to_file, self.monitor_number, *self.region)

    def call(self) -> str:
        """Return the path of the screenshot."""
        return self.path_to_file

    # --- communication commands ---------------------------------------------
    # Coordinates are pixels of the chosen monitor with the origin in its upper left corner. Each command opens its own
    # mss instance, because an mss instance must not be shared between threads and a command may be called from
    # another thread than the one that created the driver.

    @command(returns=("monitors",), reads="state")
    def get_monitors(self) -> list[dict[str, int]]:
        """Return the monitors as dicts with left, top, width and height; 0 is the whole virtual screen, 1 the primary.

        Further monitors follow as 2, 3, ...
        """
        with mss.mss() as sct:
            return [dict(monitor) for monitor in sct.monitors]

    @command(returns=("width", "height"), reads="state")
    def get_screen_size(self, monitor: Monitor) -> tuple[Pixels, Pixels]:
        """Return the size of a monitor as (width, height) in pixels."""
        with mss.mss() as sct:
            screen = self._monitor(sct, monitor)
        return int(screen["width"]), int(screen["height"])

    @command(kind="run")
    def take_screenshot(  # noqa: PLR0913, PLR0917 - path, monitor and the four corners of the region
        self,
        path: str,
        monitor: Monitor,
        x1: Annotated[Pixels, Range(0, None)] = 0,
        y1: Annotated[Pixels, Range(0, None)] = 0,
        x2: Annotated[Pixels, Range(0, None)] = 0,
        y2: Annotated[Pixels, Range(0, None)] = 0,
    ) -> None:
        """Save a screenshot of the region (x1, y1) to (x2, y2) of a monitor as PNG file at path.

        `path` is the full path of the file to write, e.g. in the folder of the running session: it must be absolute,
        end with .png, lie in a folder that exists, and not exist yet - nothing is overwritten. Leave x2 and y2 at 0
        for the whole monitor.
        """
        target = Path(path)
        if not target.is_absolute():
            msg = f"path must be absolute, e.g. inside the session folder, got '{path}'."
            raise ValueError(msg)
        if target.suffix.lower() != ".png":
            msg = f"path must end with .png, got '{path}'."
            raise ValueError(msg)
        if not target.parent.is_dir():
            msg = f"the folder of '{target}' does not exist."
            raise FileNotFoundError(msg)
        if target.exists():
            msg = f"'{target}' exists already - a screenshot never overwrites a file."
            raise FileExistsError(msg)

        with mss.mss() as sct:
            screen = self._monitor(sct, monitor)
            if x2 == 0 and y2 == 0:
                x2, y2 = screen["width"], screen["height"]
            self._check_region(monitor, screen["width"], screen["height"], (x1, y1, x2, y2))
            region = {"left": screen["left"] + x1, "top": screen["top"] + y1, "width": x2 - x1, "height": y2 - y1}
            image = sct.grab(region)
            mss.tools.to_png(image.rgb, image.size, output=str(target))

    # --- helpers --------------------------------------------------------------

    @staticmethod
    def _monitor(sct: mss.base.MSSBase, monitor: int) -> dict[str, int]:
        """Return the geometry of a monitor, or raise if it does not exist."""
        if not 0 <= monitor < len(sct.monitors):
            msg = f"Monitor must be between 0 and {len(sct.monitors) - 1}, got {monitor}."
            raise ValueError(msg)
        return sct.monitors[monitor]

    @staticmethod
    def _check_region(monitor: int, width: int, height: int, region: tuple[int, int, int, int]) -> None:
        """Raise if the region (x1, y1, x2, y2) is not inside the monitor."""
        x1, y1, x2, y2 = region
        if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
            msg = f"Region ({x1}, {y1}) to ({x2}, {y2}) is not inside monitor {monitor} of {width} x {height} pixels."
            raise ValueError(msg)
