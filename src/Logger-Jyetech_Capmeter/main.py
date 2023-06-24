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
# Type: Logger
# Device: Jyetech Capmeter

from EmptyDeviceClass import EmptyDevice

import time

class Device(EmptyDevice):

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "Capmeter"
        
        self.variables = ["Capacitance", "Reading", "Time stamp"]
        self.units = ["F", "", "s"]
        self.plottype = [True, True, True] # True to plot data
        self.savetype = [True, False, False]  # True to save data
        
        #self.idlevalue = 0 # motor position to go home
                 
        self.port_manager = True  
        self.port_types = ["COM"]
        self.port_properties = { "timeout":5,
                                 "EOL": "\n\r",
                                 "baudrate": 38400,
                                }
        
        self.suffix = {
                        "p": 1e-12,
                        "n": 1e-9,
                        "u": 1e-6,
                        }
          
    
    def call(self):
       
        while self.port.in_waiting() > 22:
            print(self.port.in_waiting())
            self.port.read()
            
        answer = self.port.read()
            
        print(answer)

        no, stamp, cap = answer.replace("  ", " ").split(" ")
                
        cap = float(cap[:-1]) * self.suffix[cap[-1]]

        return [cap, int(no), float(stamp)]
        

