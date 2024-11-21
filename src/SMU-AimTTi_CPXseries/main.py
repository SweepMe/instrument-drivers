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

# Contribution: We like to thank Heliatek GmbH/Dustin Fischer for providing the initial version of this driver.


# SweepMe! driver
# * Module: SMU
# * Instrument: AimTTi CPX series

import time
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "CPX"
        
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM"]
        
        self.port_properties = { 
            "timeout": 1,
            "EOL": "\n",
            "baudrate": 9600,
            "delay": 0.1,
        }
                                 
        self.commands = {
            "Voltage in V" : "V",
            "Current in A" : "I",
        }
                                 
    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode" : ["Voltage in V", "Current in A"],
                        "Channel": ["1", "2"],
                        "RouteOut": ["Front"],
                        "Compliance": 0.1,
                        }
                        
        return gui_parameter
                                 
    def get_GUIparameter(self, parameter = {}):
    
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']
        self.channel = parameter['Channel']
                
    def initialize(self):

        identifier = self.get_identification(
        # print("Identifier:", identifier)
        
        # if not "CPX400" in identifier:
        #    msg = "Returned identification string %s is incorrect. Please check whether the correct device is connected." % identifier
        #    raise Exception(msg)

    def configure(self):

        # Protection/Compliance
        if self.source.startswith("Voltage"):
            self.port.write("V%i" % int(self.channel) + " 0.0")
            self.port.write("I%i" % int(self.channel) + " %1.3f" %float(self.protection))  # current limit/protection
        elif self.source.startswith("Current"):
            self.port.write("I%i" % int(self.channel) + " 0.0")
            self.port.write("V%i" % int(self.channel) + " %1.3f" %float(self.protection))  # voltage limit/protection
           
    def poweron(self):
        self.port.write("OP%i 1" % int(self.channel))
        
    def poweroff(self):
        self.port.write("OP%i 0" % int(self.channel))
                 
    def apply(self):
        self.port.write(self.commands[self.source] + self.channel + " %1.3f" % float(self.value))
        
    def measure(self):

        self.port.write("I%i" %int(self.channel) + "O?")
        answer = self.port.read(10)[:-1]
        self.i = float(answer)

        self.port.write("V%i" %int(self.channel) + "O?")   
        answer = self.port.read(10)[:-1]
        self.v = float(answer)
        
    def call(self):
        return [self.v, self.i]
        
    """ command wrapping functions start here """
        
    def get_identification(self):
        self.port.write("*IDN?")
        time.sleep(0.1)
        # Todo: should be possible to read without indicating the number of characters
        identifier = self.port.read(self.port.in_waiting())
        return identifier
        
    def get_current(self):
        
        self.port.write("I%i" % int(self.channel) + "O?")
        answer = self.port.read(10)[:-1]
        return float(answer)
        
    def set_current(self, value):
    
        self.port.write("I%i %1.3f" % (int(self.channel), float(value)))
        
    def get_voltage(self):
        
        self.port.write("V%i" %int(self.channel) + "O?")
        answer = self.port.read(10)[:-1]
        return float(answer)
        
    def set_voltage(self, value):
        self.port.write("V%i %1.3f" % (int(self.channel), float(value)))
        
    def get_target_current(self):
        
        self.port.write("I%i" % int(self.channel) + "?")
        answer = self.port.read(10)[:-1]
        return float(answer)
        
    def get_target_voltage(self):
        
        self.port.write("V%i" % int(self.channel) + "?")
        answer = self.port.read(10)[:-1]
        return float(answer)       
