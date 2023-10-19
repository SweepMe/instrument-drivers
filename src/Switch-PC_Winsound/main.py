# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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
# Type: Switch
# Device: Winsound

"""
smallest tone: 37 Hz<br>
highest tone: 32767 Hz<br>
Adjust length of tone with duration.<br>
"""

from EmptyDeviceClass import EmptyDevice
import os
import sys

import FolderManager
FolderManager.addFolderToPATH()

import winsound


class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "Winsound"
        
        self.variables = ["Note"]
        self.units = ["Hz"]
        
        # self.c_scale = [264, 297, 330, 352, 396, 440, 495, 528, 594, 660, 704, 792, 880, 990, 1056, 1192] 

    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Note in Hz"],
                        "Duration in s": 0.25,
                        }               
        return GUIparameter
        
    def get_GUIparameter(self, parameter):
        
        self.duration = int(float(parameter["Duration in s"])*1000)
        
    def configure(self): 
        self.note = float('nan')
        self.c_note = float('nan')
        
    def apply(self):
    
        self.note = int(self.value)

        if self.note < 37:
            self.note = 37
         
        if self.note > 32767:
            self.note = 32767

        # self.c_note = min(self.c_scale, key=lambda x:abs(x-self.note))
        self.play_note(self.note, self.duration)
        
    def call(self):
        return self.note
        
    def play_note(self, note, duration):
        winsound.Beep(note, duration)

