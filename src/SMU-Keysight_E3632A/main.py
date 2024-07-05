# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022-2023 SweepMe! GmbH (sweep-me.net)
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
# Type: SMU
# Device: Agilent E3632A

import time  # needed for waiting until PSU has set the requested voltage

# from pysweepme.ErrorMessage import error
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """
    description =
    <p><strong>Notes:</strong></p>
    <ul>
    <li>COM Port untested as of 20240619</li>
    <li>Calibration commands not implemented</li>
    <li>-</li>
    </ul>
    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "E3632A"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM", "GPIB"]

        self.port_properties = {"timeout": 1,
                                # "delay": 0.05,
                                # "Exception": False,
                                }

    #       self.commands = {
    #                      "Voltage in V" : "VOLT",
    #                      "Current in A" : "CURR",
    #                      }

    def set_GUIparameter(self):

        gui_parameter = {
            "SweepMode": ["Voltage in V"],
            # "Channel": [1], NOT NEEDED with E3632A as it is a single channel instrument but will be used for other E36xxA instruments later.
            "RouteOut": ["Front"],
            "Compliance": 1,
            "RangeVoltage": ["15 V / 7 A", "30 V / 4 A"],
        }

        return gui_parameter

    def get_GUIparameter(self, parameter={}):
        self.port_string = parameter["Port"]
        self.source = parameter["SweepMode"]
        self.route_out = parameter["RouteOut"]
        self.currentlimit = parameter["Compliance"]
        # self.channel = int(parameter["Channel"]) #NOT NEEDED with E3632A as it is a single channel instrument but will be used for other E36xxA instruments later.
        self.voltage_range = parameter["RangeVoltage"]

    def connect(self):
        pass  # No LAN port on E3632A
        # if self.port_string.startswith("TCPIP"):
        #    if self.port_string.endswith("SOCKET"):
        #        self.port.port.write_termination = '\n'
        #        self.port.port.read_termination = '\n'

    def initialize(self):
        self.port.write("*IDN?")
        identifier = self.port.read()
        print("Identifier:", identifier)  # can be used to check the instrument
        self.port.write("*RST")

    def configure(self):
        # self.port.write("VOLT:PROT:STAT OFF") # output voltage protection disabled
        # self.port.write("CURR:PROT:STAT OFF") # output current protection disabled
        self.port.write(
            "VOLT:PROT:LEV 32")  # hardcoded overvoltage protection limit, causes switch-off of channel; set to PSU protection default value
        self.port.write(
            "CURR:PROT:LEV 7.5")  # hardcoded overcurrent protection limit, causes switch-off of channel; set to PSU protection default value

        if self.voltage_range.startswith("30 V"):
            if float(self.currentlimit) > 4.12:
                raise Exception("Lower compliance limit to max 4.12A")
            self.port.write("CURR:LEV:IMM %1.4f" % float(self.currentlimit))
            self.port.write("SOUR:VOLT:RANG P30V")
        elif self.voltage_range.startswith("15 V"):
            if float(self.currentlimit) > 7.21:
                raise Exception("Lower compliance limit to max 7.21A")
            self.port.write("CURR:LEV:IMM %1.4f" % float(self.currentlimit))
            self.port.write("SOUR:VOLT:RANG P15V")
        else:
            raise Exception("The input voltage range is not valid.")

        self.port.write("SOUR:VOLT MIN")

    def unconfigure(self):
        self.port.write("SOUR:VOLT MIN")
        # self.port.write("SYST:LOC") #On the E3632A, ONLY ALLOWED WITH RS232

    def deinitialize(self):
        pass

    def poweron(self):
        self.port.write("OUTP:STAT ON")

    def poweroff(self):
        self.port.write("OUTP:STAT OFF")

    def apply(self):
        if self.value > 15.45 and float(self.currentlimit) > 4.12:
            raise Exception(
                "The next requested step would exceed 15.45 V with current limit higher than 4.12 A.\n\nPlease either stop at 15.45 V max or lower current compliance limit to 4.12 A max.")
        else:
            self.port.write("VOLT:LEV:IMM %1.4f" % float(self.value))

    def measure(self):
        self.port.write("MEAS:VOLT?")
        self.v = float(self.port.read())
        self.port.write("MEAS:CURR?")
        self.i = float(self.port.read())
        # print(self.v, self.i)

    def call(self):
        return [self.v, self.i]

    def display_off(self):
        # For further use.

        self.port.write("DISP:STAT OFF")
        # wait for display shutdown procedure to complete
        # time.sleep(0.5)

    def display_on(self):
        # For further use.

        self.port.write("DISP:STAT ON")
        # wait for display switch-on procedure to complete
        # time.sleep(0.5)