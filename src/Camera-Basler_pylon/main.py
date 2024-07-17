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

# SweepMe! driver
# * Module: Camera
# * Instrument: Basler pylon

from __future__ import annotations

import os

from pysweepme import addFolderToPATH
from pysweepme.EmptyDeviceClass import EmptyDevice

addFolderToPATH()

from pypylon import pylon


class Device(EmptyDevice):
    """This device class for the Basler pylon camera."""

    def __init__(self) -> None:
        """Declare device parameter."""
        EmptyDevice.__init__(self)

        self.shortname = "Basler"  # short name will be shown in the sequencer
        self.instance_key: str = ""
        self.folder = os.path.dirname(__file__)
        self.variables = ["path"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [True]
        self.sweepmode: str = ""

        # Acquisition Parameters
        self.trigger_source = None
        self.gain: float = 0
        self.exposure_time_s: float = 0
        self.image_width: int = 0
        self.image_height: int = 0
        self.offset_x: int = 0
        self.offset_y: int = 0
        self.file_format: str = ""

        # Image Parameters
        self.preset: str = ""
        self.gamma: float = 0
        self.balance_ratio_red: float = 0
        self.balance_ratio_green: float = 0
        self.balance_ratio_blue: float = 0

        self.save_path: str = ""
        self.progress: int = 0
        self.progress_digits: int = 3

        # Camera parameters
        self.camera_name: str = ""
        self.tlf = pylon.TlFactory.GetInstance()
        self.cameras_dict: dict = {}
        self.camera = None

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Define options for GUI parameter."""
        return {
            "SweepMode": ["None", "Exposure time in s", "Gain"],
            "Trigger": ["Software"],
            # "GainAuto": ["Off"],  # not needed
            # "ExposureAuto": ["Off"],  # not needed
            "PixelFormat": "",
            "FileFormat": ["jpeg", "png", "bmp", "tiff", "raw"],
            "Gamma": 1,
            "ExposureTime": 10,
            "Gain": 1,
            "Preset": [
                "Off",
                "Daylight5000K (Gamma * 0.45)",
                "Daylight6500K (Gamma * 0.45)",
                "Tungsten2800K (Gamma * 0.45)",
            ],
            "ImageWidth": 1920,
            "ImageHeight": 1080,
            "ImageOffsetX": 0,
            "ImageOffsetY": 0,
            "BalanceRatioRed": 2.1731,
            "BalanceRatioGreen": 1.0,
            "BalanceRatioBlue": 1.94409,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Parse and store GUI options."""
        self.camera_name = parameter["Port"]
        self.sweepmode = parameter["SweepMode"]

        if self.sweepmode == "Exposure time in s":
            self.variables.append("Exposure time")
            self.units.append("s")
            self.plottype.append(True)
            self.savetype.append(True)

        if self.sweepmode == "Gain":
            self.variables.append("Gain")
            self.units.append("")
            self.plottype.append(True)
            self.savetype.append(True)

        # Acquisition Parameters
        self.trigger_source = str(parameter["Trigger"])
        self.gain = float(parameter["Gain"])
        self.exposure_time_s = float(parameter["ExposureTime"])
        self.image_width = int(parameter["ImageWidth"])
        self.image_height = int(parameter["ImageHeight"])
        self.offset_x = int(parameter["ImageOffsetX"])
        self.offset_y = int(parameter["ImageOffsetY"])
        self.file_format = parameter["FileFormat"]

        # Image Parameters
        self.preset = str(parameter["Preset"])
        self.gamma = float(parameter["Gamma"])
        self.balance_ratio_red = float(parameter["BalanceRatioRed"])
        self.balance_ratio_green = float(parameter["BalanceRatioGreen"])
        self.balance_ratio_blue = float(parameter["BalanceRatioBlue"])

    def find_ports(self) -> list[str]:
        """Return list of available cameras."""
        self.get_cameras_dict()
        return list(self.cameras_dict.keys())

    def connect(self) -> None:
        """Instantiate camera object."""
        self.get_cameras_dict()
        self.instance_key = f"{self.shortname}_{self.camera_name}"

        try:
            # Check if camera is already registered by SweepMe
            if self.instance_key not in self.device_communication:
                _camera = self.cameras_dict[self.camera_name]
                self.camera = pylon.InstantCamera(self.tlf.CreateDevice(_camera))

                # Register camera in device_communication
                self.device_communication[self.instance_key] = self.camera
            else:
                self.camera = self.device_communication[self.instance_key]

            self.camera.Open()  # Might need to be moved to the initialize function

        except Exception as e:
            msg = f"Error opening connection to camera: {self.camera_name}"
            raise Exception(msg) from e

    def disconnect(self) -> None:
        """Close camera connection and unregister element in device communication."""
        if self.instance_key in self.device_communication:
            self.camera.Close()

            # Unregister camera in device_communication
            self.device_communication.pop(self.instance_key)

    def initialize(self) -> None:
        """Initialize image counter."""
        self.progress = 0
        self.progress_digits = 3

    def configure(self) -> None:
        """Configure camera settings."""
        self.set_gain(self.gain)
        self.set_exposure(self.exposure_time_s)
        self.set_gamma(self.gamma)
        self.set_roi(self.image_width, self.image_height, self.offset_x, self.offset_y)  # new

        self.camera.BalanceRatioSelector.Value = "Red"
        self.camera.BalanceRatio.Value = self.balance_ratio_red
        self.camera.BalanceRatioSelector.Value = "Green"
        self.camera.BalanceRatio.Value = self.balance_ratio_green
        self.camera.BalanceRatioSelector.Value = "Blue"
        self.camera.BalanceRatio.Value = self.balance_ratio_blue

    def measure(self) -> None:
        """Capture image and save."""
        self.progress += 1
        images_to_grab = 1

        self.save_path = f"{self.tempfolder}{os.sep}BASLER_{self.progress:0{self.progress_digits}d}.{self.file_format}"
        img = pylon.PylonImage()

        try:
            # Starting the grabbing of images_to_grab images.
            self.camera.StartGrabbingMax(images_to_grab)
            while self.camera.IsGrabbing():
                # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
                grab_result = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                if grab_result.GrabSucceeded():
                    img.AttachGrabResultBuffer(grab_result)

                    # Save the image data.
                    if self.file_format == "jpeg":
                        img.Save(pylon.ImageFileFormat_Jpeg, self.save_path)
                    elif self.file_format == "png":
                        img.Save(pylon.ImageFileFormat_Png, self.save_path)
                    elif self.file_format == "bmp":
                        img.Save(pylon.ImageFileFormat_Bmp, self.save_path)
                    elif self.file_format == "tiff":
                        img.Save(pylon.ImageFileFormat_Tiff, self.save_path)
                    elif self.file_format == "raw":
                        img.Save(pylon.ImageFileFormat_Raw, self.save_path)
                else:
                    print("Error: ", grab_result.ErrorCode, grab_result.ErrorDescription)
                grab_result.Release()
        except Exception as e:
            msg = f"Error capturing image: {e!s}"
            raise Exception(msg) from e

    def call(self) -> str | tuple[str, float]:
        """Return the path to the saved image and optional sweep values."""
        if self.sweepmode == "Exposure time in s":
            return self.save_path, self.camera.ExposureTime.Value / 1000000

        elif self.sweepmode == "Gain":
            return self.save_path, self.camera.Gain.Value

        else:
            return self.save_path

    def apply(self) -> None:
        """Apply the sweep values to exposure or gain."""
        self.value = float(self.value)

        if self.sweepmode == "Exposure time in s":
            self.set_exposure(self.value)

        elif self.sweepmode == "Gain":
            self.set_gain(self.value)

    "--- Convenience Functions ---"

    def set_gain(self, gain: float) -> None:
        """Set the camera gain value."""
        # Make sure Auto Function is off to write values:
        self.camera.GainAuto.Value = "Off"

        gain_min = 0
        gain_max = 24
        if gain < gain_min:
            gain = gain_min
            self.message_Box("The gain was set to its lower limit: gain = " + str(gain_min))
        elif gain > gain_max:
            gain = gain_max
            self.message_Box("The gain was set to its upper limit: gain = " + str(gain_max))

        self.camera.Gain.Value = gain

    def set_exposure(self, exposure_s: float) -> None:
        """Set the exposure time in seconds."""
        # Make sure Auto Function is off to write values:
        self.camera.ExposureAuto.Value = "Off"

        # Set limits and transfer parameter to the camera:
        exposure = exposure_s * 1000000  # microseconds
        exposure_min = 34
        exposure_max = 2000000

        if exposure < exposure_min:
            exposure = exposure_min
            self.message_Box(
                "The exposure time was set to its lower limit: exposure time = " + str(exposure_min / 1000000) + " s",
            )
        elif exposure > exposure_max:
            exposure = exposure_max
            self.message_Box(
                "The exposure time was set to its upper limit: exposure time = " + str(exposure_max / 1000000) + " s",
            )
        self.camera.ExposureTime.Value = exposure

    def set_gamma(self, gamma: float) -> None:
        """Set the gamma factor."""
        gamma_min = 0
        gamma_max = 3.99998

        if gamma < gamma_min:
            gamma = gamma_min
            self.message_Box("The gamma factor was set to its lower limit: gamma = " + str(gamma_min))
        elif gamma > gamma_max:
            gamma = gamma_max
            self.message_Box("The gamma factor was set to its upper limit: gamma = " + str(gamma_max))
        self.camera.Gamma.Value = gamma

    def set_roi(self, image_width: int, image_height: int, offset_x: int, offset_y: int) -> None:
        """Set the region of interest."""
        width_max = 1920
        height_max = 1080

        if image_width + offset_x > width_max:
            if image_width > width_max:
                image_width = width_max
                self.message_Box(f"The image width was changed to the maximal size of {width_max} pixels.")

            offset_x = width_max - image_width
            self.message_Box(
                f"Image width and x-offset cant exceed the maximal image width of {width_max} pixels. "
                f"The offset was reduced accordingly.",
            )

        if image_height + offset_y > height_max:
            if image_height > height_max:
                image_height = height_max
                self.message_Box(f"The image height was changed to the maximal size of {height_max} pixels.")

            offset_y = height_max - image_height
            self.message_Box(
                f"Image height and y-offset cant exceed the maximal image height of {height_max} pixels."
                f"The offset was reduced accordingly.",
            )

        # Reset camera to avoid errors during parameter handover
        self.camera.OffsetX.Value = 0
        self.camera.OffsetY.Value = 0

        self.camera.Width.Value = image_width
        self.camera.Height.Value = image_height
        self.camera.OffsetX.Value = offset_x
        self.camera.OffsetY.Value = offset_y

    def get_cameras_dict(self) -> None:
        """Get available cameras and set self.cameras_dict, so it also works for find_ports()."""
        cameras = self.tlf.EnumerateDevices()
        for cam in cameras:
            name = cam.GetModelName()
            self.cameras_dict[name] = cam
