# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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
# Device: Arduino PulseCount

import time
from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Pulse count"
                
        self.variables = ["Count", "Frequency"]
        self.units = ["", "Hz"]

        self.port_manager = True  
        self.port_types = ["COM"]
        self.port_properties = { "timeout":3,
                                 "EOL": "\n",
                                 "baudrate": 57600,
                                }
    
    def initialize(self):
        self.port.read()  # read out the initialization string sent by the Arduino
                
    def configure(self):
        self.last_time = time.time()
        self.last_count = 0
                
    def measure(self): 
        self.port.write("R")

    def call(self):
    
        answer = self.port.read() # reading duration between two pulses in µs
        count, duration_us = map(int, answer.split(","))
        duration = duration_us / 1e6  # transformation from µs to s 
        
        frequency = self.convert_frequency(duration)
        
        # frequencies below 0.5 Hz cannot be correctly measured
        if time.time() - self.last_time > 2.0:
            frequency = 0.0
                        
        if count != self.last_count:  
            self.last_time = time.time()
            self.last_count = count
            
        # first readings are unreliable if there are not at least 2 counts
        if count <= 1:
            frequency = 0.0
            
        

        return count, frequency        


    @staticmethod
    def convert_frequency(duration):
        if duration > 0.0:
            frequency = 1.0 / duration
        else:
            frequency = 0.0
            
        return frequency