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

# SweepMe! driver
# * Module: Camera
# * Instrument: PC Webcam

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal

import cv2
import numpy as np
from pysweepme.commands import Elements, Label, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer (checked by @command on every call).
Intensity = Annotated[int, Label("Intensity")]  # one color value of a pixel, 0 to 255
Image = Annotated[np.ndarray, Elements(Intensity)]  # height x width x 3, RGB, uint8
FileFormat = Literal["jpg", "png"]

# Highest camera index find_ports tries; OpenCV numbers the cameras from 0 without gaps.
MAX_CAMERAS = 10


class Device(EmptyDevice):
    """Driver for webcams and other cameras that OpenCV opens by their index (0, 1, ...)."""

    def __init__(self) -> None:
        """Define the returned variable; the camera is opened in connect()."""
        super().__init__()

        self.shortname = "Webcam"

        # The Camera module shows the picture behind the first returned value.
        self.variables = ["image path"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [False]

        self.gui_parameters: dict[str, Any] = {}
        self.port_string: str = ""
        self.file_format: str = "jpg"
        self.camera_index: int = 0
        self.capture: cv2.VideoCapture | None = None
        self.picture_count: int = 0
        self.image_path: str = ""

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields: the file format of the saved pictures."""
        return {
            "SweepMode": ["None"],
            "FileFormat": ["jpg", "png"],
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selections; the port is the camera's index as text."""
        self.gui_parameters = parameters
        self.port_string = str(parameters.get("Port", "")).strip()
        self.file_format = parameters.get("FileFormat", "jpg")

    # check_driver: ignore DC004 - a hook of the Camera module
    def find_ports(self) -> list[str]:
        """Return the indices of the cameras OpenCV can open, as SweepMe!'s Find Ports button asks."""
        cameras = []
        for index in range(MAX_CAMERAS):
            capture = cv2.VideoCapture(index)
            opened = capture.isOpened()
            capture.release()
            if not opened:
                break
            cameras.append(str(index))
        return cameras

    def connect(self) -> None:
        """Open the camera with the index given as port (0 when none is given)."""
        if self.port_string and not self.port_string.isdigit():
            msg = f"The port of a webcam is its index (0, 1, ...), not '{self.port_string}'. Use Find Ports."
            raise ValueError(msg)
        self.camera_index = int(self.port_string) if self.port_string else 0
        self.capture = cv2.VideoCapture(self.camera_index)
        if not self.capture.isOpened():
            self.capture.release()
            self.capture = None
            msg = f"Camera {self.camera_index} cannot be opened. It may be in use by another program."
            raise ValueError(msg)

    def disconnect(self) -> None:
        """Release the camera, so that other programs can use it."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def initialize(self) -> None:
        """Take one picture and drop it: the first pictures of many webcams are too dark."""
        self.picture_count = 0
        self._read_frame()

    def measure(self) -> None:
        """Save a picture into the temporary folder of the run."""
        self.picture_count += 1
        name = f"temp_Webcam{self.camera_index}_{self.picture_count:03d}.{self.file_format}"
        self.image_path = str(Path(self.get_folder("TEMP")) / name)
        self.save_picture(self.image_path)

    def call(self) -> list[str]:
        """Return the path of the saved picture."""
        return [self.image_path]

    # Communication commands

    @command(returns=("image",))
    def get_image(self) -> Image:
        """Take a picture and return its pixels: height x width x 3 color values (RGB) from 0 to 255."""
        return cv2.cvtColor(self._read_frame(), cv2.COLOR_BGR2RGB)

    @command(kind="run")
    def save_picture(self, path: str) -> None:
        """Take a picture and save it to path; the file format follows the extension (.jpg, .jpeg or .png)."""
        suffix = Path(path).suffix.lower()
        if suffix not in (".jpg", ".jpeg", ".png"):
            msg = f"A picture is saved as .jpg, .jpeg or .png, not '{suffix or path}'."
            raise ValueError(msg)
        # imencode and write_bytes instead of imwrite, which fails on paths with non-ASCII characters on Windows.
        Path(path).write_bytes(self._encode(self._read_frame(), suffix))

    # Further functions

    # check_driver: ignore DC004 - answers bytes, which a communication command never does (guide 7.5)
    def get_picture_bytes(self, file_format: FileFormat = "jpg") -> bytes:
        """Take a picture and return it as the bytes of a JPEG or PNG file, e.g. to show it live in a program.

        Not a communication command: answers of commands are no bytes (driver guide, section 7.5), so it is not
        offered as a button or to agents. Scripts and programs call it directly; save_picture writes the same bytes.
        """
        if file_format not in ("jpg", "png"):
            msg = f"The file format is 'jpg' or 'png', not '{file_format}'."
            raise ValueError(msg)
        return self._encode(self._read_frame(), f".{file_format}")

    def makePicture(self, pic_path: str) -> None:  # noqa: N802 - the name of earlier versions
        """Save a picture to pic_path; kept for scripts of earlier versions, use save_picture."""
        self.save_picture(pic_path)

    # Helpers

    def _read_frame(self) -> np.ndarray:
        """Read the next picture from the camera as OpenCV gives it (BGR)."""
        if self.capture is None:
            msg = "The camera is not connected."
            raise RuntimeError(msg)
        captured, frame = self.capture.read()
        if not captured:
            msg = f"Camera {self.camera_index} gave no picture. It may be in use by another program."
            raise RuntimeError(msg)
        return frame

    @staticmethod
    def _encode(frame: np.ndarray, suffix: str) -> bytes:
        """Encode a BGR picture as the file format of suffix (.jpg, .jpeg or .png)."""
        encoded, data = cv2.imencode(suffix, frame)
        if not encoded:
            msg = f"The picture could not be encoded as {suffix}."
            raise RuntimeError(msg)
        return data.tobytes()
