# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
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
# Type: Camera
# Device: Basler pylon

from pysweepme import addFolderToPATH
from pysweepme.EmptyDeviceClass import EmptyDevice

addFolderToPATH()

from pypylon import pylon


class Device(EmptyDevice):
    description = """
    This device class is a wrapper for the Basler pylon camera. It is based on the pypylon library.
    """

    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "Basler"  # short name will be shown in the sequencer
        self.instance_key: str
        self.variables = []
        self.units = []

        # Acquisition Parameters
        self.trigger_source: str
        self.gain_auto: str
        self.gain = None
        self.exposure_auto: str
        self.exposure_time: float
        self.file_format: str

        # Image Parameters
        self.preset: str
        self.gamma = None
        self.balance_ratio_red = None
        self.balance_ratio_green = None
        self.balance_ratio_blue = None

        # Camera parameters
        self.tlf = pylon.TlFactory.GetInstance()
        self.cameras_dict: dict = {}
        self.camera = None

    def set_GUIparameter(self) -> dict:
        gui_parameter = {
            "SweepMode": ["None", "Exposure time in s"],
            "Trigger": ["Software"],
            "GainAuto": ["Off", "Once", "Continuous"],
            "ExposureAuto": ["Off", "Once", "Continuous"],
            # "PixelFormat": list(self.PixelBytes.keys()),
            "FileFormat": ["tiff", "tiff + jpg", "tiff + png", "jpg", "png"],
            "Gamma": 1,
            "ExposureTime": 0.1,
            "Gain": 1,
            "Preset": [
                "Off",
                "Daylight5000K (Gamma * 0.45)",
                "Daylight6500K (Gamma * 0.45)",
                "Tungsten2800K (Gamma * 0.45)",
            ],
            "BalanceRatioRed": 1.0,
            "BalanceRatioGreen": 1.0,
            "BalanceRatioBlue": 1.0,
        }

        return gui_parameter

    def get_GUIparameter(self, parameter) -> None:
        """Parse and store GUI options."""
        self.camera_name = parameter["Port"]

        self.sweepmode = parameter["SweepMode"]
        if self.sweepmode == "Exposure time in s":
            self.variables.append("Exposure time")
            self.units.append("s")
            self.plottype.append(True)
            self.savetype.append(True)

        # Acquisition Parameters
        self.trigger_source = str(parameter["Trigger"])
        self.gain_auto = str(parameter["GainAuto"])
        self.gain = parameter["Gain"]
        self.exposure_auto = str(parameter["ExposureAuto"])
        self.exposure_time = float(parameter["ExposureTime"])
        self.file_format = parameter["FileFormat"]

        # Image Parameters
        self.preset = str(parameter["Preset"])
        self.gamma = parameter["Gamma"]
        self.balance_ratio_red = parameter["BalanceRatioRed"]
        self.balance_ratio_green = parameter["BalanceRatioGreen"]
        self.balance_ratio_blue = parameter["BalanceRatioBlue"]

        # self.SelectedFileFormats = parameter["FileFormat"]
        # for key in self.FileFormats.keys():
        #     if key in self.SelectedFileFormats:
        #         self.variables.append("%s image path" % key)
        #         self.units.append("")
        #         self.plottype.append(False)
        #         self.savetype.append(False)

    def find_ports(self) -> list[str]:
        self.get_cameras_dict()
        return list(self.cameras_dict.keys())

    def connect(self) -> None:
        self.get_cameras_dict()

        try:
            _camera = self.cameras_dict[self.camera_name]
            self.camera = pylon.InstantCamera(self.tlf.CreateDevice(_camera))
            self.camera.Open()

            # Register camera in device_communication
            self.instance_key = f"{self.shortname}_{self.camera_name}"
            if self.instance_key not in self.device_communication:
                self.device_communication[self.instance_key] = "Connected"

        except Exception as e:
            msg = f"Error opening connection to camera: {e!s}"
            raise Exception(msg) from e

    def disconnect(self) -> None:
        if self.camera is not None:
            self.camera.Close()

            # Unregister camera in device_communication
            self.device_communication.pop(self.instance_key)

    def initialize(self) -> None:
        pass

    def configure(self) -> None:
        pass

    def unconfigure(self) -> None:
        pass

    def measure(self) -> None:
        try:
            # Starting the grabbing of c_countOfImagesToGrab images.
            self.camera.StartGrabbingMax(1)
            while self.camera.IsGrabbing():
                grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                if grabResult.GrabSucceeded():
                    # Save the image data.
                    self.image = grabResult.GetArray()
                    print(self.image)
                    # pylon.ImageFileHandler().Save(pylon.ImageFileFormat_Png, filename, img)
                grabResult.Release()
        except Exception as e:
            msg = f"Error capturing image: {e!s}"
            raise Exception(msg) from e

    def call(self) -> None:
        pass

    "--- Convenience Functions ---"

    def get_cameras_dict(self):
        cameras = self.tlf.EnumerateDevices()
        for cam in cameras:
            name = cam.GetModelName()
            self.cameras_dict[name] = cam
