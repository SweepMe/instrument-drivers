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
import mss.tools

import sys, os
import time

#from PIL import ImageGrab
#import win32api

from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = "leave x1, y1, x2, and y2 empty to use fullscreen"

    def __init__(self):
    
        super().__init__()

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

    # --- communication commands ---------------------------------------------
    # Coordinates are pixels of the chosen monitor with the origin in its upper
    # left corner. Each command opens its own mss instance, because an mss
    # instance must not be shared between threads and a command may be called
    # from another thread than the one that created the driver.

    def get_monitors(self) -> list:
        """Return the monitors as a list of dicts with left, top, width and height.

        Index 0 is the whole virtual screen, 1 the primary monitor, 2 the next one.
        """
        with mss.mss() as sct:
            return [dict(monitor) for monitor in sct.monitors]

    def get_screen_size(self, monitor: int = 1) -> tuple:
        """Return the size of a monitor as (width, height) in pixels."""
        with mss.mss() as sct:
            screen = self._monitor(sct, monitor)
        return screen["width"], screen["height"]

    def take_screenshot(self, path: str = "", monitor: int = 1,
                        x1: int = 0, y1: int = 0, x2: int = 0, y2: int = 0) -> str:
        """Save a screenshot as PNG and return the path of the file.

        The region is (x1, y1) to (x2, y2) in pixels of the monitor; leave x2 and
        y2 at 0 for the whole monitor. `path` must end with .png and must not
        exist yet - nothing is overwritten. An empty path saves into SweepMe!'s
        temporary folder under a name with the date and time.
        """
        if path:
            target = os.path.abspath(str(path))
            if not target.lower().endswith(".png"):
                msg = f"path must end with .png, got '{path}'."
                raise ValueError(msg)
            if os.path.exists(target):
                msg = f"'{target}' exists already - a screenshot never overwrites a file."
                raise FileExistsError(msg)
        else:
            stamp = time.strftime("%Y%m%d_%H%M%S")
            target = os.path.join(self.get_folder("TEMP"),
                                  f"screenshot_{stamp}_{time.time_ns() % 10**6:06d}.png")

        with mss.mss() as sct:
            screen = self._monitor(sct, monitor)
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            if x2 == 0 and y2 == 0:
                x2, y2 = screen["width"], screen["height"]
            if not (0 <= x1 < x2 <= screen["width"] and 0 <= y1 < y2 <= screen["height"]):
                msg = (f"region ({x1}, {y1}) to ({x2}, {y2}) is not inside monitor {monitor} "
                       f"of {screen['width']} x {screen['height']} pixels.")
                raise ValueError(msg)
            region = {"left": screen["left"] + x1, "top": screen["top"] + y1,
                      "width": x2 - x1, "height": y2 - y1}
            image = sct.grab(region)
            mss.tools.to_png(image.rgb, image.size, output=target)
        return target

    @staticmethod
    def _monitor(sct, monitor) -> dict:
        monitor = int(monitor)
        if not 0 <= monitor < len(sct.monitors):
            msg = f"monitor must be between 0 and {len(sct.monitors) - 1}, got {monitor}."
            raise ValueError(msg)
        return sct.monitors[monitor]


