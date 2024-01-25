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


# SweepMe! device class
# Type: Logger
# Device: Arduino AllPins


import numpy as np
from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Arduino AllPins"

        self.variables = []
        self.units = []

        for i in np.arange(12) + 2:
            self.variables.append("Digital %i" % i)
            self.units.append("")

        for i in np.arange(8):
            self.variables.append("Analog %i" % i)
            self.units.append("")

        self.plottype = [True for x in self.variables]  # True to plot data
        self.savetype = [True for x in self.variables]  # True to save data

        # self.idlevalue = 0 # motor position to go home

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 3,
            "EOL": "\n",
            "baudrate": 115200,
        }

    def initialize(self):
        # we only need to wait once to receive the setup message
        if self.port.port_properties["NrDevices"] == 0:
            print(self.port.read())  # read out the initialization string sent by the Arduino

        self.port.port_properties["NrDevices"] += 1

    def deinitialize(self):
        self.port.port_properties["NrDevices"] -= 1

    def measure(self):
        self.port.write("R")

    def call(self):
        self.answer = self.port.read()[:-1]
        return list(map(float, self.answer.split(",")))
