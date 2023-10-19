# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
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
# Device: Keithley 236


import numpy as np

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Keithley236"
        
        self.variables =["Voltage", "Current"]
        self.units =    ["V", "A"]
        self.plottype = [True, True] # True to plot data
        self.savetype = [True, True] # True to save data

        self.port_manager = True
        self.port_types = ["GPIB"]
                                         
                                 
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Voltage [V]", "Current [A]"],
                        "RouteOut": ["Rear"],
                        "Speed": ["Fast", "Medium", "Slow"],
                        "Average":1,
                        "4wire": False,
                        "Compliance": 100e-6,
                        }
                        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
    
        self.four_wire = parameter['4wire']
        self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']
        self.speed = parameter['Speed']
        self.average = int(parameter['Average'])
        
        if self.average < 1:
            self.average = 1
        if self.average > 100:
            self.average = 100
        
    def initialize(self):      
        self.port.write("G5,2,0X") 
        # Output data format
        
        if not int(round(np.log2(self.average))) in [0,1,2,3,4,5]:
            new_readings =  int(round(np.log2(self.average)))
            self.messageBox("Please use 1, 2, 4, 8, 16, or 32 for the number of averages. Changed it to %s." % new_readings)
      
    def configure(self):
            
        if self.source.startswith("Voltage"):
            self.port.write("F0,0X")                  
            # sourcemode = Voltage
      
        if self.source.startswith("Current"):
            self.port.write("F1,0X")  
            # sourcemode = Current
            
        self.port.write("L%s,0X" % self.protection)
        # Protection  
               
        if self.speed == "Fast":
            self.nplc = 0
        if self.speed == "Medium":
            self.nplc = 1
        if self.speed == "Slow":
            self.nplc = 3
            
        self.port.write("S%sX" % self.nplc) #0=0.4ms,1=4ms,2=17ms,3=20ms;
        
        # 4-wire sense
        if self.four_wire:
            self.port.write("O1X")
        else:
            self.port.write("O0X")
            
            
        # averaging    
        if self.average < 32:
            readings = int(round(np.log2(self.average)))
        else:
            readings = 5
                        
        self.port.write("P%sX" % readings)
        
        # Number  Readings    
        # 0       1 (disabled)
        # 1       2
        # 2       4
        # 3       8
        # 4       16
        # 5       32
       
             
    def deinitialize(self):
        self.port.write("O0X")

    def poweron(self):
        self.port.write("N1X") 
        
    def poweroff(self):
        self.port.write("N0X") 
                        
    def apply(self):
    
        # "self.value" is just handed over by SweepMe! with actual Sweep value
       
        self.port.write("B%s,0,0X" % self.value) 
         
    def trigger(self):
        pass
                       
    def measure(self):    
        self.port.write("H0X")                        

    def call(self):

        if self.source.startswith("Voltage"):
            v,i = self.port.read().split(",")
      
        if self.source.startswith("Current"):
            i,v = self.port.read().split(",")

        return [float(v), float(i)]
        
    def finish(self):
        pass
        
        
        