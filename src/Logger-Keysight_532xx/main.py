# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2020-2021 SweepMe! GmbH

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank Peter Andrew Hegarty for providing the initial version of this driver.

# SweepMe! device class
# Type: Logger
# Device: Keysight 532xxA Frequency Counter


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):
    
    description = """ """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Keysight 532xxA"
        self.variables = ["Counts", "Integration time"]
        self.units = ["#","s"]
        self.plottype = [True, True]
        self.savetype = [True, True]
        
        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]
        self.port_properties = {}
        
        
        
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "Channel" : ["1", "2"],
                        "Integration time in s" : "0.05",
                        "Voltage threshhold in V" : "2.5",
                        }
                        
        return GUIparameter
    
    def get_GUIparameter(self, parameter={}):
    
        self.integration_time = float(parameter["Integration time in s"])  # conversion to s
        self.thresh = float(parameter["Voltage threshhold in V"])
        self.channel = str(parameter["Channel"])
        
        
    def connect(self):
    
        pass
        
        # enable USB control of device and verifies the state
        # self.port.write(":SYST:COMM:ENAB ON, USB")
        
        # self.port.write(":SYST:COMM:ENAB? USB")
        # connect = int(self.port.read())
        # print(connect)
        
        # if connect == 1:
            # pass
        # else:
            # self.stopMeasurement = "Device not connected to USB port, please verify connection."
            # return False
            
    def disconnect(self):
        pass
        # self.port.write(":SYST:COMM:ENAB OFF,USB")
        
    def initialize(self):
        pass
        
    def configure(self):
        # set threshhold level to count as a valid event
        self.port.write(":INPut:LEV%s:ABS %s" % (self.channel, self.thresh))
            
           
    def measure(self):
        self.port.write(":MEASure:TOTalize:TIMed? %s,(@%s)" % (self.integration_time, self.channel))


    def call(self):
        self.counts = self.port.read()
        self.integ = float(self.integration_time)
        # print(self.counts)
        return [self.counts, self.integ]


    
    
    
    
    
    