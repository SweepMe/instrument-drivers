# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023-2024 SweepMe! GmbH (sweep-me.net)
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

import pypylon



class Device(EmptyDevice):
    description = """
    Description
                """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Camera Basler"  # short name will be shown in the sequencer
        self.variables = []
        self.units = []


    def set_GUIparameter(self):
        gui_parameter = {
            "SweepMode": ["None", "Exposure time [s]"],
            "Trigger": ["Software"],
            "GainAuto": ["Off", "Once", "Continuous"],
            "ExposureAuto": ["Off", "Once", "Continuous"],
            "PixelFormat": list(self.PixelBytes.keys()),
            "FileFormat": ["tiff", "tiff + jpg", "tiff + png", "jpg", "png"],
            "Gamma": 1,
            "ExposureTime": 0.1,
            "Gain": 1,
            "Preset": ["Off", "Daylight5000K (Gamma * 0.45)", "Daylight6500K (Gamma * 0.45)", "Tungsten2800K (Gamma * 0.45)"],
            "BalanceRatioRed": 1.0,
            "BalanceRatioGreen": 1.0,
            "BalanceRatioBlue": 1.0,
        }

        return gui_parameter

    def get_GUIparameter(self, parameter):
        """Parse and store GUI options."""
        if parameter["Port"] != "No Camera connected!" and parameter["Port"] != "":
            self.port = int(parameter["Port"].split(" ")[0])
        else:
            self.port = -1

        self.SelectedFileFormats = parameter["FileFormat"]

        for key in self.FileFormats.keys():
            if key in self.SelectedFileFormats:
                self.variables.append("%s image path" % key)
                self.units.append("")
                self.plottype.append(False)
                self.savetype.append(False)

        self.sweepmode = parameter["SweepMode"]

        if self.sweepmode == "Exposure time [s]":
            self.variables.append("Exposure time")
            self.units.append("s")
            self.plottype.append(True)
            self.savetype.append(True)

        self.parameter = parameter

    def find_ports(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

    def initialize(self):
        pass

    def configure(self):
        pass

    def unconfigure(self):
        try:
            self.imgBuf.Dispose()
            self.imgBuf = None
            self.buf.Dispose()
            self.buf = None
        except:
            pass

    def measure(self):
        pass

    def call(self):
        return self.data
