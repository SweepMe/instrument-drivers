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
# Device: KORAD KD3005P

import time
from ErrorMessage import error
from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "KD3005P"
        
        self.variables =["Voltage", "Current"]
        self.units =    ["V", "A"]
        self.plottype = [True, True] # True to plot data
        self.savetype = [True, True] # True to save data

        self.port_manager = True
        self.port_types = ["COM"]
        
        self.port_properties = { "timeout": 0.2,
                                 "EOL": "",
                                 "baudrate": 9600,
                                 "delay": 0.05,
                                 "Exception": False,
                                 }
                                 
        self.commands = {
                        "Voltage [V]" : "VSET",  # remains for compatibility reasons
                        "Current [A]" : "ISET",  # remains for compatibility reasons
                        "Voltage in V" : "VSET",
                        "Current in A" : "ISET",
                        }
                                 
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Voltage in V", "Current in A"],
                        "RouteOut": ["Front"],
                        "Compliance": 0.1,
                        }
                        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']
        # self.average = int(parameter['Average'])
        
        # if self.average < 1:
            # self.average = 1
        # if self.average > 100:
            # self.average = 100
        
    def initialize(self):
        self.port.write("*IDN?")
        time.sleep(0.1)
        identifier = self.port.read(self.port.in_waiting())
        print("Identifier:", identifier)
        
        # if not "3005P" in identifier:
            # self.stopMeasurement = "Returned identification string %s is incorrect. Please check whether the correct device is connected." % identifier
            # return False

    def configure(self):

        if self.source.startswith("Voltage"):
            self.port.write("ISET1:%1.2f" % float(self.protection))
        if self.source.startswith("Current"):
            self.port.write("VSET1:%1.2f" % float(self.protection))
           
    def deinitialize(self):
        pass

    def poweron(self):
        self.port.write("OUT1")
        
    def poweroff(self):
        self.port.write("OUT0")
                 
    def apply(self):
        self.port.write(self.commands[self.source] + "1:%1.2f" % float(self.value))
         
    def measure(self):        
        # self.port.write("VSET1?")
        # self.vset = float(self.port.read(5))
        
        # self.port.write("ISET1?")
        # self.iset = float(self.port.read(6)[:-1])
        
        self.port.write("IOUT1?")
        answer = self.port.read(5)
        try:
            self.i = float(answer)
        except:
            error()
            self.port.write("IOUT1?")
            answer = self.port.read(5)
            try:
                self.i = float(answer)
            except:
                error()
                self.i = float('nan')

        self.port.write("VOUT1?")   
        answer = self.port.read(5)
        try:
            self.v = float(answer)
        except:
            error()
            self.port.write("VOUT1?")   
            answer = self.port.read(5)
            try:
                self.v = float(answer)
            except:
                error()
                self.v = float('nan')   

    def call(self):
        return [self.v, self.i]
        

        
        