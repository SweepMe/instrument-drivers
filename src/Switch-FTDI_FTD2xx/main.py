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
# Device: FTDI FTD2xx

from pysweepme import FolderManager
FolderManager.addFolderToPATH()

import binascii

import ftd2xx as ftd
from pysweepme import EmptyDevice


class Device(EmptyDevice):
    description = """
        For FTD 2xx boards such as FTD245R
        Can send initial command when initializing or end command when deinitializing
    """

    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "FTD2xx"
        self.variables = ["Response"]
        self.units = []

        self.port_manager = False

        # Read and write timeout in ms
        self.timeout_ms = 5000

    def find_ports(self):
        return [dev.decode() for dev in ftd.listDevices()]

    def set_GUIparameter(self):
        return {
            "Encoding": ["HEX", "ASCII"],
            "SweepMode": "Command",
            "Start command": "",
            "End command": "",
        }

    def get_GUIparameter(self, parameter={}):
        self.encoding = parameter["Encoding"]
        self.units.append(self.encoding)

        self.start_command = self.convert_to_string(parameter["Start command"])
        self.end_command = self.convert_to_string(parameter["End command"])

        self.port_str = self.convert_to_string(parameter["Port"])
        self.driver_name = parameter["Device"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        # Set Name/Number of COM Port as key
        self.instance_key = f"{self.driver_name}_{self.port_str}"
        if self.instance_key in self.device_communication:
            self.device = self.device_communication[self.instance_key]
        else:
            # Open device
            port_byte = self.port_str.encode()
            try:
                self.device = ftd.openEx(port_byte)
            except ftd.ftd2xx.DeviceError:
                msg = f"Cannot open FTD Device with serial number {port_byte}. Available devices: {ftd.listDevices()}"
                raise Exception(msg)

            self.device_communication[self.instance_key] = self.device

    def disconnect(self):
        self.device.close()

        if self.instance_key in self.device_communication:
            self.device_communication.pop(self.instance_key)

    def configure(self):
        self.device.setTimeouts(self.timeout_ms, self.timeout_ms)
        self.send_string(self.start_command)

    def unconfigure(self):
        self.send_string(self.end_command)

    def apply(self):
        self.send_string(self.value)

    def call(self):
        # Number of bytes in queue
        queue = self.device.getQueueStatus()
        if queue > 0:
            return(self.device.read(queue))
        else:
            return ""

    """ here, convenience functions start """

    def send_string(self, string):
        if self.encoding == "HEX":
            encoded_string = binascii.unhexlify(string.replace(" ", ""))
        else:
            encoded_string = bytes(string, "utf-8")

        self.device.write(encoded_string)

    def convert_to_string(self, input):
        # If port string is given as byte string
        try:
            return input.decode()
        except (UnicodeDecodeError, AttributeError):
            return input