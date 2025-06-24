# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Velox

from __future__ import annotations

import os

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()
import velox


class Device(EmptyDevice):
    """Device Class for Cameras in Velox Wafer Prober Systems."""

    description = """
    <h3>Velox Camera</h3>
    <p>This driver controls the camera functions of FormFactor Velox wafer probers.</p>
    <h4>Setup</h4>
    <ul>
        <li>Requires Velox Installation</li>
    </ul>
    <h4>Parameters</h4>
    <ul>
        <li>Port: Use 'localhost' when running SweepMe! on the same PC as Velox. For TCP/IP remote control, enter
         the Velox PCs IP address either as blank string "192.168.XXX.XXX" or containing a specific port 
         "IP:xxx.xxx.xxx.xxx; Port:xxxx" </li>
        <li>Custom save folder: Velox allows only for saving the acquired images, but not to send it via TCP/IP. When
         using remote control, choose a folder on the Velox PC or on a common fileshare. For local control, the images
         are saved in the SweepMe! Temp folder together with your other measurement data.</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initialize the Velox Camera."""
        EmptyDevice.__init__(self)

        self.shortname = "Velox"

        self.variables = ["path"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [True]

        # Device Communication
        self.ip_address: str = "localhost"
        self.target_socket: int = 1412
        self.msg_server: velox.MessageServerInterface | None = None

        # Measurement parameters
        self.cameras = [
            "Scope",
            "Platen",
            "Chuck",
            "ContactView",
            "eVue1",
            "eVue2",
            "eVue3",
        ]
        self.camera: str = "Scope"
        self.file_format: str = "bmp"
        self.camera_modes: dict[str, int] = {
            "Raw image": 0,
            "Screenshot": 1,
            # "Both": 2,  # Currently not implemented
        }
        self.camera_mode: int = 0

        self.progress: int = 0
        self.progress_digits: int = 4  # allows up to 9999 images
        self.save_name: str = ""
        self.save_folder: str = "TEMP"
        """If velox runs on a different computer, the save folder must be set to a shared folder."""

        self.save_path: str = ""
        self.keep_only_last: bool = False

    def __del__(self) -> None:
        """Exit Velox Communication before instance is deleted."""
        self.disconnect_from_velox()

    @staticmethod
    def find_ports() -> list[str]:
        """Return a placeholder to enter an IP address and socket."""
        return ["localhost", "IP:xxx.xxx.xxx.xxx; Port:xxxx"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Define standard GUI parameter values."""
        return {
            "FileFormat": ["bmp", "jpg", "png"],
            "KeepLast": False,
            "Camera": list(self.cameras),
            "Mode": list(self.camera_modes),
            "Custom save name": "",
            "Custom save folder": "",
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle GUI parameter values."""
        self.handle_port_string(parameter["Port"])
        self.camera = parameter["Camera"]
        self.camera_mode = self.camera_modes[parameter["Mode"]]
        self.save_name = parameter["Custom save name"]
        self.save_folder = parameter["Custom save folder"]

        self.file_format = str(parameter["FileFormat"]).lower()
        self.keep_only_last = bool(parameter["KeepLast"])

    def handle_port_string(self, port_string: str) -> None:
        """Extract IP address and socket from port string."""
        port_string = port_string.strip().lower()
        self.target_socket = 1412

        if "localhost" in port_string:
            self.ip_address = "localhost"
        elif "port" in port_string:
            self.ip_address = port_string.split(";")[0].split(":")[1].strip()
            self.target_socket = int(port_string.split(";")[1].split(":")[1].strip())
        elif "ip" in port_string:
            self.ip_address = port_string.split("ip:")[1].strip()
        else:
            # Try to interpret the port string as an IP address
            self.ip_address = port_string.strip()

    def connect(self) -> None:
        """Establish connection to Velox Software."""
        self.connect_to_velox()

    def disconnect(self) -> None:
        """Disconnect from Velox Software."""
        self.disconnect_from_velox()

    def initialize(self) -> None:
        """Initialize image counter."""
        self.progress = 0

    def measure(self) -> None:
        """Capture image from camera."""
        self.progress += 1
        self.save_path = self.save_image(self.camera)

    def save_image(self, camera: str) -> str:
        """Save image of given camera and return save path as string."""
        file_name = self.save_name if self.save_name else f"Velox_{camera}"
        file_name += f"_{self.progress:0{self.progress_digits}d}"

        base_path = self.tempfolder if not self.save_folder else self.save_folder
        save_path = f"{base_path}{os.sep}{file_name}.{self.file_format}"

        velox.SnapImage(camera, save_path, self.camera_mode)

        return save_path

    def call(self) -> str:
        """Return the path to the saved image. If cameras = ALL was chosen, return last path."""
        return self.save_path

    "--- Wrapper Functions ---"

    def connect_to_velox(self) -> None:
        """Connect to the Velox SDK."""
        if self.msg_server is None:
            try:
                self.msg_server = velox.MessageServerInterface(self.ip_address, self.target_socket).__enter__()
            except Exception as e:
                # Check if Velox software is running
                if "The connection to the Velox Message Server was refused." in str(e):
                    msg = "Unable to connect to Velox software. Please start Velox and try again."
                    raise Exception(msg) from e

                raise e

    def disconnect_from_velox(self) -> None:
        """Disconnect from Velox Software."""
        if self.msg_server is not None:
            self.msg_server.__exit__(None, None, None)
            self.msg_server = None
