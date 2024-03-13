# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022, 2024 SweepMe! GmbH (sweep-me.net)
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
from pysweepme.ErrorMessage import error
from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "KD3005P"
        
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM"]
        
        self.port_properties = {
            "timeout": 0.2,
            "EOL": "",
            "baudrate": 9600,
            "delay": 0.05,
            "Exception": False,
            }

        self.commands = {
                        "Voltage [V]": "VSET",  # remains for compatibility reasons
                        "Current [A]": "ISET",  # remains for compatibility reasons
                        "Voltage in V": "VSET",
                        "Current in A": "ISET",
                        }

    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode": ["Voltage in V", "Current in A"],
                        "RouteOut": ["Front"],
                        "Compliance": 0.1,
                        }
                        
        return gui_parameter
                                 
    def get_GUIparameter(self, parameter={}):

        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']

    def initialize(self):

        identifier = self.get_identification()
        # print("Identifier:", identifier)

    def configure(self):
        if self.source.startswith("Voltage"):
            self.port.write("ISET1:%1.2f" % float(self.protection))
        elif self.source.startswith("Current"):
            self.port.write("VSET1:%1.2f" % float(self.protection))

    def poweron(self):
        self.set_output(1)
        
    def poweroff(self):
        self.set_output(0)

    def apply(self):
        self.port.write(self.commands[self.source] + "1:%1.2f" % float(self.value))

    def measure(self):        

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

    # wrapped commands start here

    def get_identification(self):

        self.port.write("*IDN?")
        time.sleep(0.1)
        # When using Virtual COM port, a \x00 character is at the end of the message that cannot be printed
        identifier = self.port.read(self.port.in_waiting()).replace("\x00", "")
        return identifier

    def get_voltage_limit(self):
        self.port.write("VSET1?")
        vset = float(self.port.read(5))
        return vset

    def get_current_limit(self):
        self.port.write("ISET1?")
        iset = float(self.port.read(6)[:-1])
        return iset

    def set_output(self, state):

        if not state:
            state = 0
        else:
            state = 1

        self.port.write("OUT%i" % state)