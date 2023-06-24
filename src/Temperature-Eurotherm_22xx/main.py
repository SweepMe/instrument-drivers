# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021-2022 SweepMe! GmbH (sweep-me.net)
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
# Device: Eurotherm 22xxe

from ErrorMessage import error, debug

import imp
import os
EurothermBaseClass22xxe = imp.load_source("Eurotherm22xxeBaseClass", os.path.dirname(os.path.abspath(__file__)) + os.sep + "EurothermBaseClass.py")
#from EurothermBaseClass import Eurotherm


# class Device(EmptyDevice):
class Device(EurothermBaseClass22xxe.Eurotherm):

    def __init__(self):
        
        EurothermBaseClass22xxe.Eurotherm.__init__(self)
        
        self.shortname = "22xxe"
        
        ## Eurotherm manual:
        ## 1 Start /7 Data / Even parity / 1.5 Stop Bits
        ## 1 Start /8 Data / No Parity / 1 Stop Bit
        
        ## Port properties
        # self.port_properties = {
                                 # "timeout"  : 1,
                                 # "baudrate" : 9600,
                                 # "parity"   : "N",  #None,Even,Odd,Space,Mark
                                 # "bytesize" : 8,
                                 # "stopbits" : 1,
                                 # }
        
        
        ## Registers
        ## can be used to update the registers of the base class if needed
        individual_registers = {}
        self.registers.update(individual_registers)
        