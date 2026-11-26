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
# * Module: Camera
# * Instrument: PC Webcam

"""SweepMe! driver that takes pictures with a webcam through OpenCV."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image
from pysweepme import EmptyDevice
from pysweepme.commands import command

FILE_FORMATS: dict[str, str] = {"jpg": "jpg", "png": "png"}
MAX_CAMERA_INDEX = 10  # find_ports stops at the first index that cannot be opened, at the latest here


class Device(EmptyDevice):
    """Driver for a webcam or another camera that OpenCV can open by its index."""

    def __init__(self) -> None:
        """Define the returned variables."""
        super().__init__()

        self.shortname = "Webcam"

        self.variables = ["image path"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [False]

        self.gui_parameters: dict[str, Any] = {}
        self.port_string: str = ""
        self.file_format: str = "jpg"
        self.cam_index: int = 0
        self.webcam: cv2.VideoCapture | None = None
        self.progress: int = 0
        self.progress_digits: int = 3
        self.image_path: str = ""

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields with their defaults."""
        return {
            "SweepMode": ["None"],
            "FileFormat": list(FILE_FORMATS),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selections."""
        self.gui_parameters = parameters
        self.port_string = str(parameters.get("Port", "")).strip()

    # check_driver: ignore DC004 - a hook of the Camera module
    def find_ports(self) -> list[str]:
        """Return the indices of the cameras that can be opened, counting from 0."""
        cameras = []
        webcam = cv2.VideoCapture()
        try:
            for index in range(MAX_CAMERA_INDEX):
                webcam.open(index)
                if not webcam.isOpened():
                    break
                cameras.append(str(index))
                webcam.release()
        finally:
            webcam.release()
        return cameras

    def connect(self) -> None:
        """Open the camera with the index given as port, 0 if the port is empty."""
        if not self.port_string:
            self.cam_index = 0
        elif self.port_string.isdigit():
            self.cam_index = int(self.port_string)
        else:
            msg = f"Port '{self.port_string}' is not a camera index such as 0 or 1."
            raise ValueError(msg)

        self.webcam = cv2.VideoCapture()
        self.webcam.open(self.cam_index)
        if not self.webcam.isOpened():
            self.webcam.release()
            self.webcam = None
            msg = f"The camera with index {self.cam_index} cannot be opened. Is it connected and not used elsewhere?"
            raise ConnectionError(msg)

    def disconnect(self) -> None:
        """Release the camera."""
        if self.webcam is not None:
            self.webcam.release()
            self.webcam = None

    def initialize(self) -> None:
        """Take a first picture, as the first frames of many webcams are dark or not yet focused."""
        self.progress = 0
        self.progress_digits = 3
        self._check_file_format()
        pic_path = Path(self.tempfolder) / f"temp_Webcam{self.cam_index}_before_start.{self.file_format}"
        self.take_picture(str(pic_path))

    def configure(self) -> None:
        """Check the file format."""
        self._check_file_format()

    def measure(self) -> None:
        """Take a picture and save it in the temporary folder of the run."""
        self.progress += 1
        file_name = f"temp_Webcam{self.cam_index}_{self.progress:0{self.progress_digits}d}.{self.file_format}"
        self.image_path = str(Path(self.tempfolder) / file_name)
        self.take_picture(self.image_path)

    def call(self) -> list[str]:
        """Return the path of the picture."""
        return [self.image_path]

    # --- communication commands ---------------------------------------------

    @command(kind="run")
    def take_picture(self, path: str) -> None:
        """Take a picture and save it at path; the file format follows the extension, e.g. .jpg or .png."""
        if self.webcam is None:
            msg = "The camera is not open, call connect first."
            raise RuntimeError(msg)
        success, frame = self.webcam.read()
        if not success:
            msg = f"No image captured from the camera with index {self.cam_index}."
            raise RuntimeError(msg)
        Image.fromarray(frame[:, :, np.array([2, 1, 0])]).save(path)  # OpenCV delivers BGR, PIL expects RGB

    # --- helpers --------------------------------------------------------------

    def _check_file_format(self) -> None:
        """Convert and check the file format."""
        file_format = self.gui_parameters.get("FileFormat", "jpg")
        if file_format not in FILE_FORMATS:
            msg = f"FileFormat must be one of {', '.join(FILE_FORMATS)}, not '{file_format}'."
            raise ValueError(msg)
        self.file_format = FILE_FORMATS[file_format]
