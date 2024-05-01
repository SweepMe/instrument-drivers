# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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

# SweepMe! driver
# * Module: Logger
# * Instrument: PCsensor HidTEMPer

import time
import ctypes
import os

import pysweepme.FolderManager as FoMa
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "TEMPer"
        
        self.variables = ["Temperature"]
        self.units = ["°C"]
        self.plottype = [True]  # define if it can be plotted
        self.savetype = [True]  # define if it can be plotted
        
        extlibs_path = FoMa.get_path("EXTLIBS")
        self.dll_file_path = extlibs_path + os.sep + "HidFTDll.dll"
        
    def find_ports(self):
    
        self.lib = ctypes.cdll.LoadLibrary(self.dll_file_path)
       
        n_devices = self.detect_devices()
        ports = [str(i) for i in range(n_devices)]
        return ports
        
    def get_GUIparameter(self, parameter):
        
        self.port = parameter["Port"]
        
    def connect(self):
    
        if os.path.exists(self.dll_file_path):
            self.lib = ctypes.cdll.LoadLibrary(self.dll_file_path)
        else:
            msg = ("No HidFTDll.dll found. Please put the file into the folder 'External libraries' of the public "
                   "SweepMe! folder.")
            raise Exception(msg)
            
        self.lib.EMyReadHUM.restype = ctypes.c_double
        self.lib.EMyReadTemp.restype = ctypes.c_double
        self.lib.EMyInitConfig.restype = ctypes.c_int
        
        # must be always used at the start
        self.detect_devices()
                
    def initialize(self):
    
        self.lib.EMySetCurrentDev(ctypes.c_int(int(self.port)))
        self.lib.EMyInitConfig(ctypes.c_bool(True))
    
    def deinitialize(self):
        self.lib.EMyCloseDevice()
               
    def call(self):

        temperature = self.lib.EMyReadTemp(ctypes.c_bool(True))

        if temperature == 888.0 or temperature == 999.0:
            msg = "Incorrect temperature reading, connection lost"
            raise ValueError(msg)
        
        return temperature

        # temp = ctypes.c_double()
        # hum = ctypes.c_double()
        # print(lib.EMyReadHUM(ctypes.byref(temp), ctypes.byref(hum)))
        # print(temp.value, hum.value)

    def detect_devices(self):
            
        n_devices = self.lib.EMyDetectDevice(ctypes.c_int(0))
        
        return n_devices
