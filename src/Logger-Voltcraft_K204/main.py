# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018, 2021 Axel Fischer (sweep-me.net)
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
# Device: Voltcraft K204 Datalogger

import struct
from collections import OrderedDict
from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                <p><strong>Usage:</strong></p>
                <ul>
                <li>Select the channels that you need</li>
                <li>Change the variable name of each channel. All variables should be different and not empty</li>
                </ul>
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
    
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 1,
                                    "baudrate": 9600,
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "parity": 'N',
                                    "EOL": "",
                                    }
                                
        self.shortname = "K204"
        
        
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Channel1": True,
                        "Channel1 variable": "Temperature1", 
                        "Channel2": True,
                        "Channel2 variable": "Temperature2", 
                        "Channel3": True,
                        "Channel3 variable": "Temperature3", 
                        "Channel4": True,
                        "Channel4 variable": "Temperature4", 
                        
                        "Unit": ["°C", "°F", "K"]
                        }
        
        return GUIparameter 
        
    def get_GUIparameter(self, parameter):
    
        self.channel1 = parameter["Channel1"]
        self.channel2 = parameter["Channel2"]
        self.channel3 = parameter["Channel3"]
        self.channel4 = parameter["Channel4"]
        
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        self.temperature_unit = parameter["Unit"]
        
        for i in range(1,5):  
            if "Channel%i" % i in parameter:
                if parameter["Channel%i" %i]:
                    self.variables.append(parameter["Channel%i variable"%i])
                    self.units.append(self.temperature_unit)
                    self.plottype.append(True)
                    self.savetype.append(True)


    def initialize(self):
        self.port.write("K")
        self.model = self.port.read(4).strip("\r")
        
        self.port.write("N") # exit AVG/MAX/MIN mode
                
    def call(self):
        
        T1,T2,T3,T4 = float('nan'),  float('nan'),  float('nan'),  float('nan')
        
        self.port.write("A")
        answer = self.port.read_raw(45)
        answer = struct.unpack(45*"B", answer)
        
        byte2_bits_str = "{:08b}".format(answer[1])
        
        unit_degree_F = byte2_bits_str[0] == "0" # True if °F, else False

        # print(answer)
        
        if answer[0] == 2 and answer[-1] == 3:
        
            # We take always the two bytes of each channel to calculate the temperature in °C
            # If the K204 uses °F we convert back to °CLAIM
            # If the user requests a temperature unit other than °C we convert to this unit.
        
            ## Channel 1  
            # if answer[3] > 1: # T1 state ok
            value = 256 * answer[7] + answer[8] - (2**16 if answer[7] > 127 else 0)
            
            if value == 2**15-1 or value == -2**15:
                pass
            else:
                T1 = value / 10.0

                if unit_degree_F:
                    T1 = (T1-32)*5/9
                    
                if self.temperature_unit == "K":
                    T1 += 273.15
                elif self.temperature_unit == "°F":
                    T1 = T1 * 9/5 + 32
                    
                T1 = round(T1,1)
               
            ## Channel 2      
            # if answer[4] > 1: # T2 state ok
            
            value = 256 * answer[9] + answer[10] - (2**16 if answer[9] > 127 else 0)
            
            if value == 2**15-1 or value == -2**15:
                pass
            else:
                T2 = value / 10.0
            
                if unit_degree_F:
                    T2 = (T2-32)*5/9
                    
                if self.temperature_unit == "K":
                    T2 += 273.15
                elif self.temperature_unit == "°F":
                    T2 = T2 * 9/5 + 32
                    
                T2 = round(T2,1)
              
            ## Channel 3          
            # if answer[5] > 1: # T3 state ok
            
            value = 256 * answer[11] + answer[12] - (2**16 if answer[11] > 127 else 0)
            
            if value == 2**15-1 or value == -2**15:
                pass
            else:
                T3 = value / 10.0
                
                if unit_degree_F:
                    T3 = (T3-32)*5/9
                    
                if self.temperature_unit == "K":
                    T3 += 273.15
                elif self.temperature_unit == "°F":
                    T3 = T3 * 9/5 + 32
                    
                T3 = round(T3,1)
                   
            ## Channel 4   
            # if answer[6] > 1: # T4 state ok
            
            value = 256 * answer[13] + answer[14] - (2**16 if answer[13] > 127 else 0)
            
            if value == 2**15-1 or value == -2**15:
                pass
            else:
                T4 = value /10.0
                
                if unit_degree_F:
                    T4 = (T4-32)*5/9
                    
                if self.temperature_unit == "K":
                    T4 += 273.15
                elif self.temperature_unit == "°F":
                    T4 = T4 * 9/5 + 32

                T4 = round(T4,1)

        else:
            print("No data retrieved")
             
        results = []
        
        if self.channel1:
            results.append(T1)
        if self.channel2:
            results.append(T2)
        if self.channel3:
            results.append(T3)    
        if self.channel4:
            results.append(T4)   
            
        return results