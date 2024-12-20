# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 SweepMe! GmbH
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

# Contribution: We like to thank D M S Sultan for providing the initial version of this driver.

# SweepMe! device class
# Type: SMU
# Device: Rohde&Schwarz HMP4000

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """

                  """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "HMP4000"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM", "USBTMC", "TCPIP"]

        self.port_properties = {
            "timeout": 1,
            "EOL": "\n",
            "baudrate": 9600,
            # "delay": 0.05,
            # "Exception": False,
        }

        self.commands = {
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
        }

    def set_GUIparameter(self):
        gui_parameter = {
            "SweepMode": ["Voltage in V", "Voltage in V (with wait)", "Current in A", "Current in A (with wait)"],
            "Channel": [1, 2, 3, 4],
            "RouteOut": ["Front"],
            "Compliance": 5.0,
        }

        return gui_parameter

    def get_GUIparameter(self, parameter={}):
        # print(parameter)
        self.port_string = parameter["Port"]
        self.source = parameter["SweepMode"]
        self.protection = parameter["Compliance"]
        self.channel = int(parameter["Channel"])

    def connect(self):
        if self.port_string.startswith("TCPIP"):
            if self.port_string.endswith("INSTR"):
                raise Exception(
                    "Instrument does not support VXI-11 standard visa runtime address ending with 'INSTR'."
                    "Only socket based connections sending with 'SOCKET' are supported.",
                )
            elif self.port_string.endswith("SOCKET"):
                self.port.port.write_termination = "\n"
                self.port.port.read_termination = "\n"
            else:
                raise Exception("Unhandled TCPIP resource name.")

    def initialize(self):
        pass

        # Use the next two lines to check whether a message remains in the buffer
        # residual_message = self.port.read()
        # print("Residual message in buffer")

        # self.port.write("*CLS")  # clear status and output buffers of the HMP

        # self.port.write("*IDN?")
        # identifier = self.port.read()
        # print("Identifier:", identifier)

    def configure(self):
        self.port.write("INST OUT%i" % self.channel)
        self.port.write("OUTP:SEL ON")

        if self.source.startswith("Voltage"):
            self.port.write("CURR %1.3f" % float(self.protection))
            self.port.write("VOLT 0")

        elif self.source.startswith("Current"):
            self.port.write("VOLT %1.3f" % float(self.protection))
            self.port.write("CURR 0")

    def unconfigure(self):
        self.port.write("INST OUT%i" % self.channel)
        self.port.write("OUTP:SEL OFF")

    def deinitialize(self):
        pass

    def poweron(self):
        self.port.write("INST OUT%i" % self.channel)
        self.port.write("OUTP:GEN ON")

    def poweroff(self):
        self.port.write("INST OUT%i" % self.channel)
        self.port.write("OUTP:GEN OFF")

    def apply(self):
        self.port.write("INST OUT%i" % self.channel)

        if self.source.startswith("Voltage"):
            self.port.write("VOLT %1.3f" % float(self.value))

        elif self.source.startswith("Current"):
            self.port.write("CURR %1.3f" % float(self.value))

        # wait for achieving the set voltage or set current before
        # other channels are changed
        if "(with wait)" in self.source:
            time.sleep(0.5)

    def measure(self):
        self.port.write("INST OUT%i" % self.channel)

        self.port.write("MEAS:VOLT?")
        self.v = float(self.port.read())

        self.port.write("MEAS:CURR?")
        self.i = float(self.port.read())
        # print(self.v, self.i)

    def call(self):
        return [self.v, self.i]
