# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2020 Axel Fischer (sweep-me.net)
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
# Type: DataImport
# Device: Template


import os

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "<name of the import filter>" # short name will be shown in the sequencer
        self.variables = ["Variable1", "Variable2"] # defines as much variables you want
        self.units = ["Unit1", "Unit2"] # make sure that units and variables have the same amount
        self.plottype = [True, True]   # True to plot data, corresponding to self.variables
        self.savetype = [True, True]   # True to save data, corresponding to self.variables
        
  
    def apply(self):
        """ applying the new setvalue 'self.value' means for DataImport that the new path is available and can be used to read in the data """
    
        filepath_to_load = self.value
        
        print(filepath_to_load)
        
        with open(filepath_to_load) as datafile:
        
            print(datafile)
        
            for line in datafile.readlines():
            
                print(line.strip())
       
                # add your commands to load your files
            
        # and then define your values here    
        self.var1 = [1,2]
        self.var2 = [3,4]
        
          
    def call(self):
        """ return the data according to the defined variables and units """

        return [self.var1, self.var2]
        