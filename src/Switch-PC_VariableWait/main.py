# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2019 Axel Fischer (sweep-me.net)
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
# Type: Switch
# Device: VariableWait

"""
Use this DeviceClass to introduce a variable hold or delay time.<br>
<br>
Hold: Wait the given time after all Sweep values are applied and reached by all modules of the current branch of the sequencer.<br>
Delay: Wait the given time since measuring the last point started. If the wait time is already passed, e.g. due to the time the meausurement anyway takes, it will immediately continue.<br>
<br>
Caution: Once this Device Class starts to wait, it cannot be stopped using the program buttons<br>
Caution: Delay only works if the corresponding delay time is longer than it takes to measure one point. Otherwise, Delay will apply not additional wait time.
"""


from EmptyDeviceClass import EmptyDevice
import time

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "VariableWait"
        
        self.variables = ["Wait time"]
        self.units = ["s"]
        self.plottype = [True] # define if it can be plotted
        self.savetype = [True] # define if it will be saved
                
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Hold [s]", "Delay [s]"],
                        }               
        return GUIparameter
        
    def get_GUIparameter(self, parameter):

        self.sweepmode = parameter["SweepMode"]
        
        self.shortname = self.sweepmode.split(" ")[0]
        self.variables = [self.shortname + " time"]
        
    def initialize(self):
        self.ref_time = float("-inf")
        
    def start(self):
        self.value = float(self.value)
        
        if self.sweepmode == "Delay [s]": 
            
            if(time.perf_counter() - self.ref_time) < self.value:
                #print("Delay: start waiting %1.3g seconds" % (self.value - (time.perf_counter() - self.ref_time)))
                while (time.perf_counter() - self.ref_time) < self.value:
                    time.sleep(0.01)
            # else:
                # print("Delay: no wait time was used")
        
            self.ref_time = time.perf_counter()
        
    def adapt(self):
        if self.sweepmode == "Hold [s]":
            time.sleep(float(self.value))
            
            
    def call(self):
        return(self.value)
        
        
    
