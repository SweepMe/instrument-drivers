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
# Device: Arduino Inputs



import numpy as np
import time

from FolderManager import addFolderToPATH
addFolderToPATH()

from pyfirmata import Arduino, ArduinoNano, util

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "Arduino Inputs"
        
        self.port_types = ["COM"]


    def set_GUIparameter(self):
        
        GUIparameter = {}
        
        for i in range(8):
            GUIparameter["Analog%i" % i] = False
            
        for i in range(14):
            GUIparameter["Digital%i" % i] = False

                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter):
        self.port_string = parameter["Port"]
        
        self.variables = []
        self.units = []
        
        self.analog_pins = []
        self.digital_pins = []
        
        for i in range(8):
            if "Analog%i" % (i) in parameter:
                if parameter["Analog%i" % i]:
                    self.analog_pins.append(i)
                    self.variables.append("Analog%i" % i)
                    self.units.append("")
                    
        for i in range(14):
            if "Digital%i" % (i) in parameter:
                if parameter["Digital%i" % i]:
                    self.digital_pins.append(i)
                    self.variables.append("Digital%i" % i)
                    self.units.append("")

        self.plottype = [True for x in self.variables] # True to plot data
        self.savetype = [True for x in self.variables]  # True to save data
        

    def connect(self):
        # self.board = Arduino(self.port_string)
        self.board = ArduinoNano(self.port_string)
        # self.board.digital[13].write(1)
        # time.sleep(1)
        # self.board.digital[13].write(0)
        
        for i in self.analog_pins:
            self.board.analog[i].enable_reporting()
            
        # for i in self.digital_pins:
            # self.board.digital[i].enable_reporting()
        
        it = util.Iterator(self.board)
        it.start()
        
    def initialize(self):
        pass
        # analog0 = self.board.analog[0].read()
        
        # print(self.board.analog)
        
    def disconnect(self):
        self.board.sp.close()
        
    def measure(self):
        pass
        
       
    def call(self):
        
        values = []
        for i in self.analog_pins:
            values.append(self.board.analog[i].read())
            
        for i in self.digital_pins:
            values.append(self.board.digital[i].read())

        return values
