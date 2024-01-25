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


from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
        <h3>Arduino AllPins</h3>
        <p>This driver allows to read out given digital and analog pins.</p>
        <p>&nbsp;</p>
    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Arduino AllPins"

        self.variables = []
        self.units = []

        self.plottype = [True for x in self.variables]  # True to plot data
        self.savetype = [True for x in self.variables]  # True to save data

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 3,
            "EOL": "\n",
            "baudrate": 115200,
        }

        self.max_voltage = 5

        self.unit_dict = {
            "Volt": "V",
            "Bit": " ",
        }

    def set_GUIparameter(self):
        return {
            "Digital channel": "2,3,4,5,6,7,8,9,10,11,12,13",
            "Analog channel": "0,1,2,3,4,5,6,7",
            "Analog unit": ["Volt", "Bit"],
            "Resolution in Bit": 10,
        }

    def get_GUIparameter(self, parameter={}):
        self.variables = []
        self.units = []

        if parameter["Digital channel"] != "":
            for pin in parameter["Digital channel"].split(","):
                self.variables.append("Digital %i" % int(pin))
                self.units.append("")

        if parameter["Analog channel"] != "":
            for pin in parameter["Analog channel"].split(","):
                self.variables.append("Analog %i" % int(pin))
                self.units.append(self.unit_dict[parameter["Analog unit"]])

        self.resolution = 2 ** int(parameter["Resolution in Bit"]) - 1

    def initialize(self):
        # we only need to wait once to receive the setup message
        if self.port.port_properties["NrDevices"] == 0:
            print(self.port.read())  # read out the initialization string sent by the Arduino

        self.port.port_properties["NrDevices"] += 1

    def deinitialize(self):
        self.port.port_properties["NrDevices"] -= 1

    def measure(self):
        command_string = "R"
        for var in self.variables:
            if "Digital" in var:
                pin = int(var.replace("Digital ", ""))
                command_string += f"{pin}D,"
            elif "Analog" in var:
                pin = int(var.replace("Analog ", ""))
                command_string += f"{pin}A,"

        self.port.write(command_string)

    def call(self):
        self.answer = self.port.read()[:-1]

        ret = []
        for n, val in enumerate(self.answer.split(",")):
            value = float(val)

            if self.units[n] == "V":
                value *= self.max_voltage / self.resolution

            ret.append(value)

        return ret
