# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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
# Device: KORAD KWR100

import time
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "KWR100"
        
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.port_manager = True
        self.port_types = ["COM"]
        
        self.port_properties = {
            "timeout": 2,
            "EOL": "\n",
            "baudrate": 115200,
            # "delay": 0.05,
            # "Exception": False,
        }
                                 
        self.channel = ""
        self.i = float("nan")
        self.v = float("nan")
        self.source = None
        self.protection = None

    def set_GUIparameter(self):
        
        gui_parameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["None"] + ["%i" % i for i in range(1, 100)],
            "RouteOut": ["Front"],
            "Compliance": 0.1,
        }
                        
        return gui_parameter
                                 
    def get_GUIparameter(self, parameter={}):
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']

        self.set_channel(parameter["Channel"])

    def initialize(self):

        identifier = self.get_identification()
        # print("Identifier:", identifier)
        if "KWR" not in identifier:
            raise Exception("No KWR series power supply connected. Please check COM port.")

    def configure(self):

        if self.source.startswith("Voltage"):
            self.set_current(float(self.protection))
        if self.source.startswith("Current"):
            self.set_voltage(float(self.protection))
           
    def deinitialize(self):
        pass

    def poweron(self):
        self.set_output(True)
        
    def poweroff(self):
        self.set_output(False)
                 
    def apply(self):
        if self.source.startswith("Voltage"):
            self.set_voltage(float(self.value))
        if self.source.startswith("Current"):
            self.set_current(float(self.value))
         
    def measure(self):
        self.i = self.get_current()
        self.v = self.get_voltage()

    def call(self):
        return [self.v, self.i]

    # get/set function start here

    def set_channel(self, channel):

        if channel == "None" or channel is None:
            channel = ""

        self.channel = str(channel)

    def get_identification(self):
        self.port.write("*IDN%s?" % self.channel)
        return self.port.read()

    def get_status(self):
        self.port.write("STATUS%s?" % self.channel)
        return self.port.read()

    def set_output(self, state):
        self.port.write("OUT%s:%i" % (self.channel, int(state)))

    def set_voltage(self, value):
        self.port.write("VSET%s:%1.2f" % (self.channel, float(value)))

    def get_voltage_set(self):
        self.port.write("VSET%s?" % self.channel)
        answer = self.port.read()
        return float(answer)

    def get_voltage(self):
        self.port.write("VOUT%s?" % self.channel)
        answer = self.port.read()
        return float(answer)

    def set_current(self, value):
        self.port.write("ISET%s:%1.3f" % (self.channel, float(value)))

    def get_current_set(self):
        self.port.write("ISET%s?" % self.channel)
        answer = self.port.read()
        return float(answer)

    def get_current(self):
        self.port.write("IOUT%s?" % self.channel)
        answer = self.port.read()
        return float(answer)

    def set_overcurrent_protection(self, value):
        self.port.write("OCP%s:%1.3f" % (self.channel, float(value)))

    def get_overcurrent_protection(self):
        self.port.write("OCP%s?" % self.channel)
        answer = self.port.read()
        return float(answer)

    def set_overvoltage_protection(self, value):
        self.port.write("OVP%s:%1.3f" % (self.channel, float(value)))

    def get_overvoltage_protection(self):
        self.port.write("OVP%s?" % self.channel)
        answer = self.port.read()
        return float(answer)

    def set_overcurrent_protection_state(self, state):
        state = "ON" if bool(state) else "OFF"
        self.port.write("OCP%s:%s" % (self.channel, state))

    def set_overvoltage_protection_state(self, state):
        state = "ON" if bool(state) else "OFF"
        self.port.write("OCV%s:%s" % (self.channel, state))
