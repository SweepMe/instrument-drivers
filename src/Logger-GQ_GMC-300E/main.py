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
# Device: GQ_GMC-300E


from ErrorMessage import error

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):

        EmptyDevice.__init__(self)
        
        self.shortname = "GMC-300"
        
        self.port_manager = True
        self.port_types = ['COM']
        self.port_properties = {
                                "baudrate": 57600,
                                "timeout": 1.0,
                                "EOL": "",
                                }

        self.variables =["Counts"]
        self.units = ["1/min"]
        self.plottype = [True]
        self.savetype = [True]

        
    def initialize(self):
        pass
        # self.port.write("<GETVER>>")
        # self.version = self.port.read(14)
        # print(self.version)
        
    def call(self):
        self.port.write("<GETCPM>>")

        try:            
            answer = self.port.read(2)
            cpm = 256*ord(answer[0]) + ord(answer[1])
        except:
            error()
            cpm = float('nan')
            
        return [cpm]