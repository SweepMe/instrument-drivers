# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018, 2020 - 2021 Axel Fischer (sweep-me.net)
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
# Device: Combivac CM31


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """If sensor is not detected, a float 'not-a-number' is returned."""

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "CM31"
        
        self.channels = ["PM1", "TM1", "TM2"]
        
        self.variables = ["Pressure %s" %x for x in self.channels]
        self.units = ["mbar" for x in self.channels]
        self.plottype = [True for x in self.channels]
        self.savetype = [True for x in self.channels]

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
                                "baudrate": 2400,
                                "timeout": 1,
                                "EOL": "\r",
                                }
                
     
    # def measure(self):
    
        # for chan in self.channels:
            # self.port.write("MES R %s" % chan)
        
    def call(self):
    
        pressure_values = [float('nan') for x in self.channels] # empty value will be returned if not overwritten by read value
            
        for i, chan in enumerate(self.channels):
        
            self.port.write("MES R %s" % chan)
    
            if self.port.read() == chr(6):
                
                result = self.port.read()
                
                result_splitted = result.split(":")
                
                if result_splitted[0] == chan: # checks if the answer starts with the name of the channel

                    if not result_splitted[2] == "NO_SEN" and not result_splitted[2] == "OFF":
                        pressure = float(result_splitted[2])
                        pressure_values[i] = pressure

        return pressure_values
        