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
        self.variables = ["path"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [True]

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
        self.preset: str
        self.gamma: float
        self.balance_ratio_red: float
        self.balance_ratio_green: float
        self.balance_ratio_blue: float

        # Camera parameters
        self.tlf = pylon.TlFactory.GetInstance()
        self.cameras_dict: dict = {}
        self.camera = None

        self.preset: str = ""
        self.gamma: float = 0
        self.balance_ratio_red: float = 0
        self.balance_ratio_green: float = 0
        self.balance_ratio_blue: float = 0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Define options for GUI parameter."""
        return {
            "SweepMode": ["None", "Exposure time in ms", "Gain"],
            "Trigger": ["Software"],
            # "GainAuto": ["Off"],  # not needed
            # "ExposureAuto": ["Off"],  # not needed
            "PixelFormat": "",
            "FileFormat": ["jpeg"],  # currently only jpeg
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

        # These are the parameters of the previous version of the driver
        self.sweepmode = parameter["SweepMode"]

        if self.sweepmode == "Exposure time in ms":
            self.variables.append("Exposure time")
            self.units.append("ms")
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
        self.image_width = int(parameter["ImageWidth"])  # new
        self.image_height = int(parameter["ImageHeight"])  # new
        self.offset_x = int(parameter["ImageOffsetX"])  # new
        self.offset_y = int(parameter["ImageOffsetY"])  # new
        self.file_format = parameter["FileFormat"]  # broken

        # Image Parameters
        self.preset = str(parameter["Preset"])
        self.gamma = float(parameter["Gamma"])
        self.balance_ratio_red = float(parameter["BalanceRatioRed"])
        self.balance_ratio_green = float(parameter["BalanceRatioGreen"])
        self.balance_ratio_blue = float(parameter["BalanceRatioBlue"])

        # Currently saving as jpeg is hard coded in self.measure()
        self.SelectedFileFormats = parameter["FileFormat"]

    def find_ports(self) -> list[str]:
        self.get_cameras_dict()
        return list(self.cameras_dict.keys())

    def connect(self) -> None:
        self.get_cameras_dict()

        try:
            # Check if camera is already registered by SweepMe
            self.instance_key = f"{self.shortname}_{self.camera_name}"
            if self.instance_key not in self.device_communication:
                _camera = self.cameras_dict[self.camera_name]
                self.camera = pylon.InstantCamera(self.tlf.CreateDevice(_camera))

                # Register camera in device_communication
                self.device_communication[self.instance_key] = self.camera
            else:
                self.camera = self.device_communication[self.instance_key]

            self.camera.Open()  # Might need to be moved to the initialize function

        except Exception as e:
            msg = f"Error opening connection to camera: {e!s}"
            raise Exception(msg) from e

    def disconnect(self) -> None:
        if self.instance_key in self.device_communication:
            #        if self.camera is not None:
            self.camera.Close()

            # Unregister camera in device_communication
            self.device_communication.pop(self.instance_key)

    def initialize(self) -> None:
        pass

    def configure(self) -> None:
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

    def unconfigure(self) -> dict:
        pass

    def measure(self) -> None:
        images_to_grab = 1
        self.filename = r"C:\Users\Public\Documents\SweepMe!\Measurement\saved_pypylon_img.jpeg"
        img = pylon.PylonImage()

        try:
            # Starting the grabbing of images_to_grab images.
            self.camera.StartGrabbingMax(images_to_grab)
            while self.camera.IsGrabbing():
                # Wait for an image and then retrieve it. A timeout of 5000 ms is used.
                grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                if grabResult.GrabSucceeded():
                    img.AttachGrabResultBuffer(grabResult)

                    # Save the image data.
                    img.Save(pylon.ImageFileFormat_Jpeg, self.filename)
                else:
                    print("Error: ", grabResult.ErrorCode, grabResult.ErrorDescription)
                grabResult.Release()
        except Exception as e:
            msg = f"Error capturing image: {e!s}"
            raise Exception(msg) from e

    def call(self) -> None:
        return self.filename

    def apply(self):
        self.value = float(self.value)

        if self.sweepmode == "Exposure time in s":
            self.set_exposure(self.value)

        elif self.sweepmode == "Gain":
            self.set_gain(self.value)

    "--- Convenience Functions ---"

    def set_gain(self, gain: float) -> None:
        # Make sure Auto Function is off to write values:
        self.camera.GainAuto.Value = "Off"

        # Set limits and transfer parameter to the camera:
        gainMin = 0
        gainMax = 24
        if gain < gainMin:
            gain = gainMin
            self.message_Box("The gain was set to its lower limit: gain = " + str(gainMin))
        elif gain > gainMax:
            gain = gainMax
            self.message_Box("The gain was set to its upper limit: gain = " + str(gainMax))
        self.camera.Gain.Value = gain

    def set_exposure(self, exposure_s: float) -> None:
        """Set the exposure time in seconds."""
        # Make sure Auto Function is off to write values:
        self.camera.ExposureAuto.Value = "Off"

        # Set limits and transfer parameter to the camera:
        exposure = exposure_s * 1000  # microseconds
        exposureMin = 34
        exposureMax = 2000000

        if exposure < exposureMin:
            exposure = exposureMin
            self.message_Box(
                "The exposure time was set to its lower limit: exposure time = " + str(exposureMin / 1000) + " ms",
            )
        elif exposure > exposureMax:
            exposure = exposureMax
            self.message_Box(
                "The exposure time was set to its upper limit: exposure time = " + str(exposureMax / 1000) + " ms",
            )
        self.camera.ExposureTime.Value = exposure

    def set_gamma(self, gamma):
        # Set limits and transfer parameter to the camera:
        gammaMin = 0
        gammaMax = 3.99998

        if gamma < gammaMin:
            gamma = gammaMin
            self.message_Box("The gamma factor was set to its lower limit: gamma = " + str(gammaMin))
        elif gamma > gammaMax:
            gamma = gammaMax
            self.message_Box("The gamma factor was set to its upper limit: gamma = " + str(gammaMax))
        self.camera.Gamma.Value = gamma

    def set_roi(self, image_width, image_height, offset_x, offset_y):
        # Set limits and transfer parameter to the camera:
        WidthMax = 1920
        HeightMax = 1080

        if image_width + offset_x > WidthMax:
            if image_width > WidthMax:
                image_width = WidthMax
                self.message_Box("The image width was changed to the maximal size of " + str(WidthMax) + " pixels.")
            offset_x = WidthMax - image_width
            self.message_Box(
                "Image width and x-offset cant exceed the maximal image width of "
                + str(WidthMax)
                + " pixels. The offset was reduced accordingly.",
            )

        if image_height + offset_y > HeightMax:
            if image_height > HeightMax:
                image_height = HeightMax
                self.message_Box("The image height was changed to the maximal size of " + str(HeightMax) + " pixels.")
            offset_y = HeightMax - image_height
            self.message_Box(
                "Image height and y-offset cant exceed the maximal image height of "
                + str(HeightMax)
                + "pixels. The offset was reduced accordingly.",
            )

        self.camera.Width.Value = image_width
        self.camera.Height.Value = image_height
        self.camera.OffsetX.Value = offset_x
        self.camera.OffsetY.Value = offset_y

    def get_cameras_dict(self):
        cameras = self.tlf.EnumerateDevices()
        for cam in cameras:
            name = cam.GetModelName()
            self.cameras_dict[name] = cam
