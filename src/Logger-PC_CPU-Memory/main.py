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
# Device: CPU and Memory usage

import os
import psutil

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.variables = ["CPU usage", "Memory usage", "Disk (C:) usage", "SweepMe! memory usage"]
        self.units = ["%", "%", "%", "%"]
        self.plottype = [True, True, True, True] # True to plot data
        self.savetype = [True, True, True, True]  # True to save data
                                
         
    def initialize(self):
        self.SweepMe_process = psutil.Process(os.getpid())
                       
    def call(self):

        CPU_usage = psutil.cpu_percent()
        Memory_usage = psutil.virtual_memory()[2]
        Disk_usage = psutil.disk_usage("c:")[3]
            
        SweepMe_mem = self.SweepMe_process.memory_percent()


        return [CPU_usage, Memory_usage, Disk_usage, SweepMe_mem]
