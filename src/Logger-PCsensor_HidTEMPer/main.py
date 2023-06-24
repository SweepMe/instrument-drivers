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
# Device: PCsensor HidTEMPer

from EmptyDeviceClass import EmptyDevice
import time
import ctypes
import os


class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "TEMPer"
        
        self.variables = ["Temperature"]
        self.units = ["°C"]
        self.plottype = [True] # define if it can be plotted
        self.savetype = [True] # define if it can be plotted
        

    def find_Ports(self):
    
        self.connect()
    
        return [str(i) for i in range(self.NrDevices)]
        
    def get_GUIparameter(self, parameter):
        
        self.port = int(parameter["Port"])
        
    def connect(self):
        
        try:
            self.lib = ctypes.cdll.LoadLibrary("HidFTDll.dll")
            self.lib.EMyReadHUM.restype = ctypes.c_double
            self.lib.EMyReadTemp.restype = ctypes.c_double
            self.lib.EMyInitConfig.restype = ctypes.c_int
            
            self.NrDevices = self.lib.EMyDetectDevice(ctypes.c_int(0))
        except:

            self.stopMeasurement = "No HidFTDll.dll found. Please put the file into the folder 'External libraries' of the public SweepMe! folder."

        
    def disconnect(self):
        self.lib.EMyCloseDevice()
        
    def initialize(self):
        self.lib.EMySetCurrentDev(ctypes.c_int(self.port))
        self.lib.EMyInitConfig(ctypes.c_bool(True))
               
    def call(self):

        T = self.lib.EMyReadTemp(ctypes.c_bool(True))

        if T == 888.0 or T == 999.0:
            self.stopMeasurement = "Connection lost"
            T = float('nan')
        
        return T

        # temp = ctypes.c_double()
        # hum = ctypes.c_double()

        # print(lib.EMyReadHUM(ctypes.byref(temp), ctypes.byref(hum)))
        # print(temp.value, hum.value)

