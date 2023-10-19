# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018-2020 Axel Fischer (sweep-me.net)
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
# Device: HP 4145

import numpy as np
import time

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):
    
    multichannel = [" CH1", " CH2", " CH3", " CH4"]

    def __init__(self):
    
        EmptyDevice.__init__(self)
       
        # remains here for compatibility with v1.5.3       
        self.multichannel = [" CH1", " CH2", " CH3", " CH4"]

        self.variables = ["Voltage", "Current"]
        self.units     = ["V", "A"]
        self.plottype  = [True, True] # True to plot data
        self.savetype  = [True, True] # True to save data
        
        self.port_manager = True
        self.port_types = ['GPIB']
        self.port_properties = {
                                "delay" : 0.1,
                                "timeout": 5.0,
                                }
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode": ["Voltage in V", "Current in A"],
                        # "Channel": ["CH1", "CH2", "CH3", "CH4"],  # preferred way starting from 1.5.5
                        "RouteOut": ["Rear"],
                        "Speed": ["Fast", "Medium", "Slow"],
                        "Compliance": 1,
                        }
                        
        return GUIparameter
        
        
    def get_GUIparameter(self, parameter={}):
        
        self.device = parameter['Device']
        self.four_wire = parameter['4wire']
        self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        
        if self.source.startswith("Voltage"):
            self.source = "DV"
        elif self.source.startswith("Current"):
            self.source = "DI"

        self.protection = parameter['Compliance']
        self.speed = parameter['Speed']
        # self.pulse = parameter['CheckPulse']   
        # self.pulse_meas_time = parameter['PulseMeasTime']
        
        # self.average = int(parameter['Average'])
        
        self.channel = self.device[-1]
        
        self.shortname = "HP 4145 CH%s" % self.channel
        
        self.port_string = parameter["Port"]
              
        
    def initialize(self):
    
    
        unique_DC_port_string = "HP4145_" + self.port_string

        # initialize commands only need to be sent once, so we check here whether another instance of the same Device Class AND same port did it already. If not, this instance is the first and has to do it.
        if not unique_DC_port_string in self.device_communication:
        
    
            self.port.write("*IDN?")
            print(self.port.read())
        
            # self.port.write("*OPT?")
            # print(self.port.read())
        
            # self.port.write("EM 1,0")# set to 4200 mode for this session
            self.port.write("US")      # user mode
            # self.port.write("CA1")     # autocalibration ON
            self.port.write("BC")      # buffer clear
            self.port.write("DR1")     # data ready service request
            
            self.device_communication[unique_DC_port_string] = True

                    
    def configure(self):
    
        self.range = "0"
        
        '''
        Voltage source mode specified (DV):
        0 Autorange
        1 20 V range
        2 200 V range
        3 200 V range
        Current source mode specified (DI):
        = 0 Autorange
        = 3 100nA 
        = 4 1muA range
        = 5 10muA 
        = 6 100muA
        = 7 1mA 
        = 8 10 mA 
        = 9 100 mA range
        '''                                             


    
        if self.speed == "Fast": # 1 Short (0.1 PLC) preconfigured selection Fast
            self.nplc = 1
        elif self.speed == "Medium": # 2 Medium (1.0 PLC) preconfigured selection Normal
            self.nplc = 2
        elif self.speed == "Slow": # 3 Long (10 PLC) preconfigured selection Quiet
            self.nplc = 3 
        
        self.port.write("IT" + str(self.nplc))
        
    def unconfigure(self):
        pass
        # self.port.write(self.source + self.channel)
    
    def deinitialize(self):
        pass
    
    def poweron(self):
        pass
    
    def poweroff(self):
        self.port.write(self.source + self.channel)
        
    def apply(self):
        self.port.write(self.source + self.channel + ", " + self.range + ", " + f"{self.value:1.4E}" + ", " + self.protection) # value needs to be formated this way to avoid str conversion errors


    def measure(self):
        pass
        
        # I only send TI to trigger the read out, reading voltages via TV will be much faster during call
        # self.port.write("TI" + self.channel)
        # self.port.write("TV" + self.channel) 
    
    def call(self):
    
        self.port.write("TI" + self.channel)
        answer = self.port.read()
        self.i = float(answer[3:])
        
        self.port.write("TV" + self.channel)   
        answer = self.port.read()    
        self.v = float(answer[3:])   

        if self.v > 1e37:
            self.v = float('nan')
        if self.i > 1e37:
            self.i = float('nan')
                   
        return [self.v, self.i]
        
        '''
        X Y Z +-N.NNNN E+-NN
        X The status of the data (where X = N for a normal reading)
        Y The measure channel (Y = A through F)
        Z The measure mode (Z = V or I)
        +-N.NNNN E+-NN is the reading (mantissa and exponent)
        '''


        