# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 SweepMe! GmbH
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
# Device: Manson HCS-3xxx


from EmptyDeviceClass import EmptyDevice
import numpy as np
import time

class Device(EmptyDevice):

    description = """
                  Negative values can be used to switch off the power supply
                  """
                  
    actions = ["set_output_off", "set_output_on"]

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "HCS-3xxx"
        
        self.variables =["Voltage", "Current"]
        self.units =    ["V", "A"]
        self.plottype = [True, True] # True to plot data
        self.savetype = [True, True] # True to save data

        self.port_manager = True
        self.port_types = ["COM"]
        
        self.port_properties = { "timeout": 2,
                                 "EOL": "\r",
                                 "baudrate": 9600,
                                 "Exception": False,
                                 }
                                 
        self.commands = {
                        "Voltage [V]" : "VOLT", # remains for compatibility reasons
                        "Current [A]" : "CURR", # remains for compatibility reasons
                        "Voltage in V" : "VOLT",
                        "Current in A" : "CURR",
                        }
                        
        self.retry_attempts = 5
        
        self._is_output_on = False
                                 
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Voltage in V", "Current in A"],
                        "RouteOut": ["Front"],
                        "Compliance": 100e-6,
                        }
                        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
        self.sweepmode = parameter['SweepMode']
        self.protection = parameter['Compliance']
        # self.average = int(parameter['Average'])
        
        # if self.average < 1:
            # self.average = 1
        # if self.average > 100:
            # self.average = 100
        
    def initialize(self):

        self.port.write("GMAX")
        answer = self.port.read()
        success = self.port.read()
        #print("GMAX", answer)
        
        self.port.write("GOCP")
        answer = self.port.read()
        success = self.port.read()
        #print(answer)
        
        
    def configure(self):
            
        if self.sweepmode.startswith("Voltage"):
            self.port.write("VOLT008")
            success = self.port.read()
            
            self.port.write("SOCP%03d" % (int(float(self.protection) * 10)))
            success = self.port.read()
            
            self.port.write("CURR%03d" % (int(float(self.protection) * 10)))
            success = self.port.read()

        elif self.sweepmode.startswith("Current"):
            self.port.write("CURR000")
            success = self.port.read()
            
            new_value = int(float(self.protection)*10)
        
            if new_value < 8:
                new_value = 8
                
            self.port.write("SOVP%03d" % new_value)
            success = self.port.read()
            
            self.port.write("VOLT%03d" % new_value)
            success = self.port.read()
            
    def unconfigure(self):
    
                
        if self.sweepmode.startswith("Voltage"):
            self.port.write("VOLT008")
            success = self.port.read()

        elif self.sweepmode.startswith("Current"):
            self.port.write("CURR000")
            success = self.port.read()
           
           
    def deinitialize(self):
        pass

    def poweron(self):
        self.set_output_on()
        
    def poweroff(self):
        self.set_output_off()
        
                        
    def apply(self):
    
        # a value smaller than 0 cannot be set and is used to switch off the output completely
        if float(self.value) < 0 and self._is_output_on == True:
            self.set_output_off()
                    
        else:          
            if self.sweepmode.startswith("Voltage"):
                new_value = int(float(self.value)*10)
                if new_value < 8:
                    new_value = 8
            
            elif self.sweepmode.startswith("Current"):
                new_value = int(float(self.value)*10)
               
               
            # we retry because serial communication is rather unstable
            try:
                self.port.write("%s%03d" % (self.commands[self.sweepmode], new_value))
                success = self.port.read()
            except:
                for i in range(self.retry_attempts):
                    try:
                        self.port.write("%s%03d" % (self.commands[self.sweepmode], new_value))
                        success = self.port.read()
                        break
                    except:
                        pass
             
        # if the output was switched off (due to a negative value), we have to switch the output on again if the new value is positive or 0.0
        if float(self.value) >= 0.0 and self._is_output_on == False:
            self.set_output_on()
                               
    def measure(self):
        if self._is_output_on == True:
            self.port.write("GETD")

    def call(self):
    
        if self._is_output_on == True:
            # we use try-except because sometimes the request does not succeed and we have to ask again
            try:
                answer = self.port.read()
            except:
                for i in range(self.retry_attempts):
                    try:
                        self.port.write("GETD")
                        answer = self.port.read()
                        break
                    except:
                        pass
                
            success = self.port.read()
            
            voltage = int(answer[0:4])/100.0
            current = int(answer[4:8])/100.0
            state = answer[-1]
            # print(state, success)
            
        else:
            voltage = float('nan')
            current = float('nan')

        return [voltage, current]
        
        
    def set_output_on(self):
        self.port.write("SOUT0") # 0 switches output on
        success = self.port.read()
        self._is_output_on = True
        
    def set_output_off(self):
        self.port.write("SOUT1") # 1 switches output off
        success = self.port.read()
        self._is_output_on = False