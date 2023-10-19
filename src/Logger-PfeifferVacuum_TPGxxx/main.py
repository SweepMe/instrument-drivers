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

# Manual: https://www.idealvac.com/files/ManualsII/Pfeiffer_MultiGauge256A_OpInstructions.pdf

# SweepMe! device class
# Type: Logger
# Device: Pfeiffer Vacuum TPGxxx


import time

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):
    """
    <h3>Pfeiffer vacuum Multi Gauge TPGxxx</h3>
    <p>Supported models: TPG 251 A, TPG 252 A,&nbsp;TPG 256 A,&nbsp;TPG 361,&nbsp;TPG 362,&nbsp;TPG 366,&nbsp;</p>
    <p><strong>Usage:</strong></p>
    <p>This driver can be used with controllers for one, two, or six channels. As default, only the first channel is read out. Select further channels to be read out according to the channels your controller provides.</p>
    <p><strong>Manual:</strong>&nbsp;</p>
    <p>TPG256A:&nbsp;<a href="https://www.idealvac.com/files/ManualsII/Pfeiffer_MultiGauge256A_OpInstructions.pdf">https://www.idealvac.com/files/ManualsII/Pfeiffer_MultiGauge256A_OpInstructions.pdf</a></p>
    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "TPGxxx"

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {"EOLread": "\r\n",
                                "timeout": 1,
                                "baudrate": 9600,
                                "bytesize": 8,
                                "stopbits": 1,
                                }
                                
        # The device returns a status as the first digit according to this dict
        self.status = {
                        0:"OK",
                        1:"Underrange",
                        2:"Overrange",
                        3:"Sensor error",
                        4:"Sensor off",
                        5:"No sensor",
                        6:"Identification error"
                      }

       
    def set_GUIparameter(self):

        GUIparameter = {}
        
        for i in range(6): 
        
            j = i + 1
            
            GUIparameter["Use Channel %i" % j] = (True if j == 1 else False)
            GUIparameter["Channel %i" % j] = "Ch %i" % j
 
        return GUIparameter

    def get_GUIparameter(self, parameter={}):
           
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        self.pressure_values = []
        self.status_values = []
        self.channels = []

        for i in range(6):
            
            j = i + 1

            if parameter["Use Channel %i" % j]:
            
                self.channels.append(j)
                
                self.variables.append(parameter["Channel %i" % j] + " pressure")
                self.variables.append(parameter["Channel %i" % j]  + " status")
                self.units += ["mbar", ""]
                self.plottype += [True, True]
                self.savetype += [True, True]
                
                # Variables need to be initialized in order to  loop during call()
                self.pressure_values += [float('nan'), float('nan')]
                self.status_values += ["", ""]


    def initialize(self):
        pass
        # print(self.variables[0])
        # self.variables[0] = self.channel1
        # print(self.variables[0])

    def call(self):
        
        # Empty list to be filled with values
        varlist = []
                  
        for i in self.channels:
        
            self.port.write(f"PR{i}\r")
            self.port.read()
            self.port.write(chr(0x05)) # send ENQ
            readout = self.port.read()
            #print(readout)
            
            status, pressure = readout.split(',')
            
            # append the pressure value
            varlist.append(float(pressure))
            
            # append the status value
            varlist.append(self.status[int(status)])
            
        return varlist


