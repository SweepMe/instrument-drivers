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
# Device: Newport 1835-C
# Maintainer: Axel Fischer

from collections import OrderedDict
from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
    
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        self.port_properties = {    "timeout": 1,
                                    "delay": 0.01,
                                    "baudrate": 9600,
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "parity": 'N',
                                    "EOL": "\n",
                                    }
                                    
        self.port_identification = "NewportCorp,1835-C"
                                
        self.shortname = "1835-C"
        
        self.variables = ["Intensity"]
        self.units = ["W"]
        self.plottype = [True]
        self.savetype = [True]

    def initialize(self): 
    
        # asks whether the ECHO mode for COM port communication is on
        self.port.write("ECHO?")
        answer = self.port.read()
               
        # if ECHO mode is on, it will return ECHO? in case of COM port communication. In case of GPIB, it just return 0 or 1 but does not give an echo
        if answer == "ECHO?":
            # read the answer of the ECHO query which will of course be "> 1"
            self.port.read()
            # now, let's switch off echo mode in order to have similar behavior for COM port and GPIB port communication
            self.port.write("ECHO 0")
            # read the echo which still takes place after this message
            self.port.read()
            # ask again for ECHO mode: 1. to check whether it worked 2. the first command after echo off is still answered with leading ">"           
            self.port.write("ECHO?")
            self.port.read()
            
        
        self.port.write("*IDN?")
        print(self.port.read())
        
        self.port.write("DETMODEL?")
        print(self.port.read()) 
        
        self.port.write("DETSN?\n")
        print(self.port.read())
        
        self.port.write("ATTNSN?\n")
        print(self.port.read())       

        self.port.write("CALDATE?\n")
        print(self.port.read())
        
        self.port.write("UNITS?\n")
        print(self.port.read())
        
        self.port.write("LAMBDA?\n")
        print(self.port.read())
        
        self.port.write("ATTN?")
        print(self.port.read())
               
        self.port.write("AUTO1")
        self.port.write("DCCONT")
        self.port.write("RUN")
        
    def measure(self):
        self.port.write("R?")

    def call(self):
        answer = self.port.read()
        return [float(answer)]
