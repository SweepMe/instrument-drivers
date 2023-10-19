# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018, 2020 Axel Fischer (sweep-me.net)
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
# Device: Keithley 740

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description =   """
                    This device class reads out the temperature from one selected channel. Further improvements are needed to select the type of the temperature sensor or to change the unit. Please feel free to implement and contribute further features.
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "Keithley740"
        
        self.variables = ["Temperature"]
        self.units = ["K"]
        self.plottype = [True]
        self.savetype = [True]

        self.port_manager = True
        self.port_types = ["GPIB"]
        
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Channel" : "1",
                        # "Type" : ["K", "J"],
                        "Unit" : ["K"],
                        }
                      
        return GUIparameter
                        
        
    def get_GUIparameter(self, parameter):
    
        # uncomment the next line to see all parameters which are arriving here
        # print parameter
    
        self.channel = int(parameter["Channel"])
        # self.channel_type = parameter["Type"]

        self.variables = ["Temperature CH%i" % self.channel]
        self.units = ["K"]
        self.plottype = [True]
        self.savetype = [True]
        
    def initialize(self):
        self.port.write("C%iX" % self.channel)
        
    def measure(self):
        self.port.write("C%iX" % self.channel)
        
    def call(self):
        self.port.write("C%iX" % self.channel)
        Temperature = float(self.port.read()[4:14])    
        # print(Temperature)
        return Temperature