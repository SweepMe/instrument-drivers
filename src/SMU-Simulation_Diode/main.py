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


# SweepMe! device class
# Type: SMU
# Device: Test diode


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''
This Device Class simulates an SMU that measures a diode.
It can be used to test the SMU module.


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from EmptyDeviceClass import EmptyDevice
import numpy as np
import random

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Test Diode"
        
        self.variables = ["Voltage", "Current"]
        self.units =     ["V", "A"]
        self.plottype =  [True, True] # True to plot data
        self.savetype =  [True, True] # True to save data
        
        self.idlevalue = 0.0

        self.speedvalues = {
                            "Fast": 1.0,
                            "Medium": 3.0,
                            "Slow": 10.0,
                            }
        
    def set_GUIparameter(self):
    
        GUIparameter = {
                        'SweepMode' : ["Voltage in V"],
                        'Compliance' : 1e-3,
                        'Average' : 1,
                        'Speed': ["Fast", "Medium", "Slow"],
                        }
                        
        return GUIparameter
                                                
    def get_GUIparameter(self, parameter = {}):
    
        self.sweepvalue = parameter["SweepValue"]
   
        # self.four_wire = parameter['4wire']
        # self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        self.protection = float(parameter['Compliance'])
        self.speed = parameter['Speed']
        self.average = int(parameter['Average'])
        
        if self.average < 1:
            self.average = 1
        if self.average > 100:
            self.average = 100


     
    def initialize(self):
        if float(self.protection) > 1.0:
            self.stop_Measurement("Aborted because %s" % self.protection)
            return False
                         
    def call(self):
    
        if self.sweepvalue == "List sweep":
            return [v for v in range(10)], [i for i in range(10,20)]

            
        #print type(self.value), np.isnan(self.value)        
                
        self.v, self.i = 1.0,1.0
        
        self.value = float(self.value)
    
        if np.isnan(self.value):
            self.value = 0.0
    
        if self.source.startswith("Voltage"):
        
            for i in range(self.average):
            
                i_list = []
        
                self.deltaV = -1
                
                i = 0
                
                self.v_exp = self.value
                
                while abs(abs(self.value - self.v_exp) - self.deltaV) > 1e-3 and i < 1500: 

                    i += 1

                    self.i = 1e-15 *  ( np.exp(self.v_exp/1.4/0.025) - 1) + self.v_exp/1e9 + random.random()/1e10 # diode with linear leakage and some resolution noise
                    
                    if abs(self.i) > abs(self.protection):
                        if self.i > 0.0:
                            self.i = abs(self.protection)
                        elif self.i < 0.0:
                            self.i = -abs(self.protection)
                        
                                       
                    self.deltaV = 1e2*(abs(self.i))**0.5 # some SCLC
                    
                    if abs(self.v_exp) + self.deltaV > self.value:

                        self.v_exp -= 0.001 * np.sign(self.value)

                self.v = self.value + random.random()*1e-2/self.speedvalues[self.speed] # some more voltage noise
                
                i_list.append(self.i)
                
            self.i = sum(i_list) / self.average
      
        elif self.source.startswith("Current"):
            pass


        return [float(self.v), float(self.i)]

        

        
        