# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2020 - 2021 Axel Fischer (sweep-me.net)
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
# Type: Temperature
# Device: Eurotherm 350x

from ErrorMessage import error, debug

import imp
import os
EurothermBaseClass35xx = imp.load_source("Eurotherm35xxBaseClass", os.path.dirname(os.path.abspath(__file__)) + os.sep + "EurothermBaseClass.py")

# class Device(EmptyDevice):
class Device(EurothermBaseClass35xx.Eurotherm):

    def __init__(self):
        
        EurothermBaseClass35xx.Eurotherm.__init__(self)
        
        self.shortname = "35xx"   
        
        ## Eurotherm manual:
        ## 1 Start /7 Data / Even parity / 1.5 Stop Bits
        ## 1 Start /8 Data / No Parity / 1 Stop Bit
        
        ## Modbus default: 1 Start / 8 Data / No Parity / 1 Stop Bit / 19200
        self.default_port_properties_Modbus = {
                                                     "timeout"  : 1,
                                                     "baudrate" : 19200,  #  Default is 19200
                                                     "parity"   : "N",  #None,Even,Odd -> Default is None
                                                     "bytesize" : 8,
                                                     "stopbits" : 1,
                                                    }
      
        self.channels_available = ["1", "2"]
        
        self.registers["Resolution"] =  (21258, 0, "h6"),  # Modbus only
        # self.registers["Resolution"] =  (21204, 0, "h6"),  # Modbus only
        # self.registers["Resolution"] =  (21130, 0, "h6"),  # Modbus only
                        
    
    def get_decimal_positions(self):
        
        decimal_point_positions = self.get_resolution() # in case of 350x PV resolution is directly the number of digits
            
        return decimal_point_positions
        
    
    def get_digits(self, key):
        """ a function that can be overloaded by the drivers individual classes """
        
        if key.startswith("SetPointRampRate"):
            return self._digits + 1 # Setpoint ramprate of 32 series has always one digit more than PV which has the decimal places as readout.
            
        else:   
            return self._digits    

    