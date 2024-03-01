# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 SweepMe! GmbH
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
# Device: Screenshot

"""
<b>Making a screenshot</b>

<ul>
<li>only works with Windows</li>
<li>x and y are the coordinates of the cursor in pixels of the screen</li>
<li>origin of coordinates is top, left corner of the screen</li>
<li>based on pyscreenshot module</li>
</ul>
"""

from FolderManager import addFolderToPATH
addFolderToPATH()

import mss

import sys, os

#from PIL import ImageGrab
#import win32api

from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = "leave x1, y1, x2, and y2 empty to use fullscreen"

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "Screenshot"
        
        self.variables = ["Path"]
        self.units = [""]
        self.plottype = [False] # define if it can be plotted
        self.savetype = [False] # define if it can be plotted
        
        self.sct = mss.mss()
        
        monitor = self.sct.monitors[1]
        
        self.width =  monitor["width"]
        self.height =  monitor["height"]
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "x1" : "",
                        "y1" : "",
                        "x2" : "",
                        "y2" : "",
                        "Monitor": 1,
                        "File suffix": "Screenshot",
                        }
         
        return GUIparameter
    
    def get_GUIparameter(self, parameter):

        # in pysweepme there is no label and we use an empty string as default
        self.label = parameter.get("Label", "")
        
        try:
            self.x1 = int(parameter["x1"])
        except:
            self.x1 = 0
            
        try:    
            self.y1 = int(parameter["y1"])
        except:
            self.y1 = 0
            
        try:    
            self.x2 = int(parameter["x2"])
        except:
            self.x2 = int(self.width)
            
        try:
            self.y2 = int(parameter["y2"])
        except:
            self.y2 = int(self.height)
            
        self.monitor_number = int(parameter["Monitor"])
        
        self.file_suffix = parameter["File suffix"]
        
        if len(self.file_suffix) > 0:
            self.file_suffix = "_" + self.file_suffix
        
    def initialize(self):
        self.tempfolder = self.get_folder("TEMP")
        self.i = 0
        
        monitor = self.sct.monitors[self.monitor_number]
        
        self.width =  monitor["width"]
        self.height =  monitor["height"]
        
    def start(self):
        self.i += 1
        self.path_to_file = self.tempfolder + os.sep + 'temp_%s%s_%i.png' % (self.label, self.file_suffix, self.i)
        
    def measure(self):
        #im=ImageGrab.grab(bbox=(self.x1, self.y1, self.x2, self.y2))
        #im.save(self.path_to_file)
        
        bbox=(self.x1, self.y1, self.x2, self.y2)
        
        im = self.sct.grab(bbox)

        # Save it!
        mss.tools.to_png(im.rgb, im.size, output=self.path_to_file)
        #filename = self.sct.shot(output=self.path_to_file)
        
    def call(self):
        return self.path_to_file
        

