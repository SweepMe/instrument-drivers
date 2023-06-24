# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 - 2019 Axel Fischer (sweep-me.net)
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
# Device: Mouse

"""
<b>Device Class to read out the position of the mouse cursor</b>

<ul>
<li>only works with Windows</li>
<li>x and y are the coordinates of the cursor in pixels of the screen</li>
<li>(0,0) is left bottom corner</li>
<li>x_press and y_press are the coordinates if left button is pressed</li>
<li>Left_clicked and Right_clicked indicates whether a button is pressed</li>
</ul>
"""


from EmptyDeviceClass import EmptyDevice
import sys, os
import win32api

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "Mouse"
        
        self.variables = ["x", "y", "x_press", "y_press", "Left_clicked", "Right_clicked"]
        self.units = ["px", "px", "px", "px", "", ""]
        self.plottype = [True, True, True, True, False, False] # define if it can be plotted
        self.savetype = [True, True, True, True, True, True] # define if it can be plotted
        
        self.width = win32api.GetSystemMetrics(0)
        self.height = win32api.GetSystemMetrics(1)
        
    def measure(self):  
        try:
            self.x,self.y = win32api.GetCursorPos()
        except:
            self.x,self.y = float('nan'), float('nan')
        # catches an exception if the TaskManager is opened and no cursor exists

        self.ButtonLeft = win32api.GetKeyState(0x01)
        self.ButtonRight = win32api.GetKeyState(0x02)
            
           
    def process_data(self):
   
        self.y = self.height-self.y-1 # necessary to create a plot that directly corresponds to the cursor position
    
        if self.ButtonLeft < 0:
            self.x_press = self.x
            self.y_press = self.y
        else:
            self.x_press = float('nan')
            self.y_press = float('nan')  
        
    def call(self):
         
        return [self.x, self.y, self.x_press, self.y_press, self.ButtonLeft, self.ButtonRight]
