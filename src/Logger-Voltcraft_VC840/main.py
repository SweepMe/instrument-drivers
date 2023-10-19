# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2019 - 2020 Axel Fischer (sweep-me.net)
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
# Device: Voltcraft VC840

"""
A Device Class to readout a Voltcraft Multimeter model VC840 or similar device.
The communication is based on COM port communication using a FS9721-LPX protocol. Any other multimeter using this standard can be read out as well.
Switching the mode of the multimeter during a measurement is not recommended any may lead to errorneous values.
The first return value is a float of the displayed value. The second value is a string of the momentary unit.
"""

import os, sys
import time
from ErrorMessage import error

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!

class Device(EmptyDevice):

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "VC840"
        self.variables = ["Value", "Unit"]
        self.units = ["", ""]
        self.plottype = [True, False]   # True to plot data, corresponding to self.variables
        self.savetype = [True, True]   # True to save data, corresponding to self.variables
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
                                "baudrate": 2400,
                                "timeout": 3,
                                "dtr": True,
                                "rts": False,
                                "raw_read": True,
                                }
                                
        self.all = {
                    1  : ["RS232", "AUTO", "DC", "AC"],
                    2  : ["A1", "A6", "A5", "Minus"],
                    3  : ["A2", "A7", "A3", "A4"],
                    4  : ["B1", "B6", "B5", "P1"],
                    5  : ["B2", "B7", "B3", "B4"],
                    6  : ["C1", "C6", "C5", "P2"],
                    7  : ["C2", "C7", "C3", "C4"],
                    8  : ["D1", "D6", "D5", "P3"],
                    9  : ["D2", "D7", "D3", "D4"],
                    10 : ["Diode", "k", "n", "µ"],
                    11 : ["Beep", "M", "%", "m"],
                    12 : ["Hold", "Delta", "Ohm", "F"],
                    13 : ["Batt.", "Hz", "V", "A"],
                    14 : ["°C", "", "", ""],
                    }
                    
        self.numbers = {
                    0 : [1, 2, 3, 4, 5, 6], 
                    1 : [2, 3],
                    2 : [1, 2, 4, 5, 7],
                    3 : [1, 2, 3, 4, 7],
                    4 : [2, 3, 6, 7],
                    5 : [1, 3, 4, 6, 7],
                    6 : [1, 3, 4, 5, 6, 7],
                    7 : [1, 2 ,3],
                    8 : [1, 2, 3, 4, 5, 6, 7],
                    9 : [1, 2, 3, 4, 6, 7],
                    "L" : [4,5,6],
                    }
                    
        self.unit_types = ["Ohm", "F", "Hz", "V", "A", "°C", "%"]
        
        self.magnitudes =  {
                            "n" : 1e-9,
                            "µ" : 1e-6,
                            "m" : 1e-3,
                            "k" : 1e3,
                            "M" : 1e6,
                           }
                           
                           
        self.readout_timeout = 2.0 # in seconds
        
                
        
    def get_GUIparameter(self, parameter):
        self.port = parameter["Port"]
                                
    def call(self):
    
    
        # this routine makes sure that old messages are thrown away
        # readout is always done until the last byte (14) to make sure a value reading is related to a correlated set of bytes
        while self.port.in_waiting() > 14:
        
            for i in range(14):
                message_byte = self.port.read(1)
                byte_string = "{0:8b}".format(message_byte[0]) 
                byte_upper = byte_string[:4].replace(" ", "0")
                byte_index = int(byte_upper,2)
                
                if byte_index == 14:
                    break
            
        #print("final", self.port.in_waiting())

        infos = {}
        
        # has to be improved: reading 14 bytes can lead to the error that a part of the bytes is from a previous reading
        
        index_dict = {}
        
        starttime = time.perf_counter()
        while True:
            message_byte = self.port.read(1)
                
            if len(message_byte) > 0:
            
                byte_string = "{0:8b}".format(message_byte[0]) 
                byte_upper = byte_string[:4].replace(" ", "0")
                byte_index = int(byte_upper,2)
                byte_lower = byte_string[4:]

                for i, bit in enumerate(byte_lower[::-1]):
                    if bit == "1" and byte_index in self.all:
                        
                        infos[self.all[byte_index][i]] = True
                
                        index_dict[byte_index] = byte_index
                
                # if the last byte is reached and the first byte is also in, we can assume that a full data set is acquired
                if byte_index == 14 and 1 in index_dict.keys():
                    break
                    

            if time.perf_counter() - starttime > self.readout_timeout:
                return [float('nan'), 'no value']
                break
                
        infos_values = list(infos.keys())
        #print(infos_values)
                    
        
        # There are four 7-digit-display segments, being A, B, C, and D
        # here, for each numbers the dashes used to construct the 7-digit number are appended to individual lists
        
        As = [int(j[1]) for j in infos_values if len(j) == 2 and j[0] == "A" and j != "AC"]
        Bs = [int(j[1]) for j in infos_values if len(j) == 2 and j[0] == "B"]
        Cs = [int(j[1]) for j in infos_values if len(j) == 2 and j[0] == "C"]
        Ds = [int(j[1]) for j in infos_values if len(j) == 2 and j[0] == "D" and j != "DC"]
        
        #print(As,Bs,Cs,Ds)
        
        # The combination of these dashes of the each 7-digit-segment can be used to reconstruct the real vale using self.numbers
        for key in self.numbers:
            if sorted(As) == self.numbers[key]:
                A = key  
                break
                
        for key in self.numbers:
            if sorted(Bs) == self.numbers[key]:
                B = key  
                break
                
        for key in self.numbers:
            if sorted(Cs) == self.numbers[key]:
                C = key  
                break
                
        for key in self.numbers:
            if sorted(Ds) == self.numbers[key]:
                D = key  
                break
          
          
        try:
            if B == 0 and C == "L": # Overload
                
                #print("B:", type(B), B)
                self.result = float('nan')
                unit = "overload"
                
                return [self.result, unit]
                
        except:
            self.result = float('nan')
            unit = "error"
           
           
        # get result  
        try:
            self.result = A*1000.0 + B*100.0 + C*10.0 + D*1.0
            
            if "P1" in infos_values:
                self.result /= 1000.0
            elif "P2" in infos_values:
                self.result /= 100.0
            elif "P3" in infos_values:
                self.result /= 10.0    
             
            for key in self.magnitudes:
                if key in infos_values:
                    self.result *= self.magnitudes[key]
                    break
                
            if "Minus" in infos:
                self.result *= -1.0
                
        except:
            error()
            self.result = float('nan')
            unit = "error"
            return [self.result, unit]
         
         
        # find unit
        unit = ""
        for key in self.unit_types:
            if key in infos_values:
                unit = key
                break
        
        return [self.result, unit]

    