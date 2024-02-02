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
# Device: Arduino MCP4728

import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

libs_path = file_dir + os.sep + "libs"
libraries_path = file_dir + os.sep + r"libraries\libs_39_64"
sys.path.append(libraries_path)


import binascii

import ftd2xx as ftd
from pysweepme import EmptyDevice


class Device(EmptyDevice):
    description = """
        Need FTDI driver installed
        Can send initial command when initializing or end command when deinitializing
    """

    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "FTDI245"
        self.variables = []
        self.units = []

        self.port_manager = False
        self.port_types = ["USB"]

    def find_ports(self):
        # print(ftd.listDevices())
        return [dev.decode() for dev in ftd.listDevices()]

    def set_GUIparameter(self):
        return {
            "Command": "Some Command",
            "Encoding": ["HEX", "ASCII"],
            "Init Command": "",
            "End Command": "",
        }

    def get_GUIparameter(self, parameter={}):
        self.encoding = parameter["Encoding"]

        self.port_str = parameter["Port"]
        self.driver_name = parameter["Device"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        # Check if port string is still in list of devices - maybe double?
        if self.port_str not in ftd.listDevices():
            msg = f"FTD Device with serial number {self.port_str} not found"
            raise Exception(msg)

        # Open device
        try:
            self.device = ftd.openEx(self.port_str)
        except ftd.ftd2xx.DeviceError:
            msg = f"Cannot open FTD Device with serial number {self.port_str}"
            raise Exception(msg)


        # Set Name/Number of COM Port as key
        self.instance_key = f"{self.driver_name}_{self.port_str}"

        if self.instance_key not in self.device_communication:
            self.device_communication[self.instance_key] = "Connected"

    def disconnect(self):
        # Close device
        self.device.close()

        if self.instance_key in self.device_communication:
            self.device_communication.pop(self.instance_key)

    def configure(self):
        self.device.setTimeouts(5000, 5000)

    def unconfigure(self):
        # TODO: Timeout?
        pass

    def apply(self):
        # command: 5 Bytes

        if self.encoding == "HEX":
            # length 5
            command = binascii.unhexlify(self.value.replace(" ", ""))
        # elif self.encoding == "ASCII":
        else:
            # length 14
            command = bytes(self.value, "utf-8")

        self.device.write(command)

    def call(self):
        # Number of bytes in queue
        queue = self.device.getQueueStatus()

        # check timeout?

        if queue > 0:
            return(self.device.read(queue))
        else:
            return None

    """ here, convenience functions start """
