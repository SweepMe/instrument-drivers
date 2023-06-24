# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2020 Axel Fischer (sweep-me.net)
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
# Device: Arduino Outputs



import numpy as np
import time

from FolderManager import addFolderToPATH
addFolderToPATH()

from pyfirmata import Arduino, ArduinoNano

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "Arduino Inputs"
        
        self.port_types = ["COM"]


    def set_GUIparameter(self):
    
        pins = []
        
        for i in range(14):
            pins.append("Digital%i" % i)
        
        GUIparameter = {
                        "SweepMode": ["Output"],
                        "Pin":pins,
                        "PWM":False,
                        }

                                
        return GUIparameter
        
    def get_GUIparameter(self, parameter):
        self.port_string = parameter["Port"]
        
        self.pin_number = int(parameter["Pin"].split(" ")[0][7:])
        self.variables = [parameter["Pin"]]
        self.units = [""]
        
        self.PWM = "p" if parameter["PWM"] else "o"
            

        self.plottype = [True for x in self.variables] # True to plot data
        self.savetype = [True for x in self.variables]  # True to save data
        

    def connect(self):
        # self.board = Arduino(self.port_string)
        self.board = ArduinoNano(self.port_string)
        # self.board.digital[13].write(1)
        # time.sleep(1)
        # self.board.digital[13].write(0)
                
        self.pin = self.board.get_pin('d:%i:%s' % (self.pin_number, self.PWM))
        
    def disconnect(self):
        self.board.sp.close()
        
    def apply(self):
        
        self.val = max(0, min(1, float(self.value)))
        self.pin.write(self.val)
       
    def call(self):
        return self.val
