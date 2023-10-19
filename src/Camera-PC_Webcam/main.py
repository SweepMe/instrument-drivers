# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
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
# Type: Camera
# Device: Webcam

"""
<h2>Webcam logger</h2>
<br>
Check the parameter 'Time stamp' to have a time label in each picture.<br>
<br>
Available ports are indices starting from 0. Just test to which index your webcam belongs. If you have multiple webcams, they will have different indices.<br>
You can use multiple webcams. Simply put another Logger into the sequencer.<br>
<br>
At the moment, this Device Class does not work with the Module "Make Folder" yet, i.e. all pictures are saved to the main temp folder.
"""

from EmptyDeviceClass import EmptyDevice
import time
import sys
import numpy as np
import os

import cv2

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Webcam"
        
        self.folder = os.path.dirname(__file__)
        
        self.variables = ["image path"]   
        self.units = [""]
        self.plottype = [False]
        self.savetype = [False]
        
         
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["None"],
                        "FileFormat": ["jpg", "png"],
                        }
        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):
                
        self.fileformat = parameter["FileFormat"]        
        
        if parameter["Port"] != "":     
            self.cam_index = int(parameter["Port"])
        else:
            self.cam_index = 0
                      
    def find_Ports(self):
    
        cameras = []
        self.webcam = cv2.VideoCapture()
        i = -1
        while True:
            i+=1
            self.webcam.open(i)
            if self.webcam.isOpened():
                cameras.append(str(i))
                
            else:
                break

        return cameras
        
    def connect(self):    
        self.webcam = cv2.VideoCapture()
        self.webcam.open(self.cam_index)

    def disconnect(self):
        self.webcam.release()
        
    def initialize(self):
        self.progress = 0
        self.progress_digits = 3
        
        if self.fileformat == "jpg":
            pic_path = self.tempfolder + os.sep + "temp_Webcam0_before_start.jpg"
            self.makePicture(pic_path) 
            
        elif self.fileformat == "png":
            pic_path = self.tempfolder+ os.sep + "temp_Webcam0_before_start.png"
            self.makePicture(pic_path) 
        
        
    def measure(self):          
        self.progress += 1
        
        if self.fileformat == "jpg":
            self.webcam_string = self.tempfolder + os.sep + "temp_Webcam" + str(self.cam_index) + "_%0"+str(self.progress_digits)+"d.jpg"
            self.jpg_path = self.webcam_string % (self.progress)
            self.makePicture(self.jpg_path) 

        elif self.fileformat == "png":
            self.webcam_string = self.tempfolder+ os.sep + "temp_Webcam" + str(self.cam_index) + "_%0"+str(self.progress_digits)+"d.png"
            self.png_path = self.webcam_string % (self.progress)
            self.makePicture(self.png_path) 

    def call(self):
    
        values = []
        
        if self.fileformat == "jpg":
            values.append(self.jpg_path)
            
        elif self.fileformat == "png":
            values.append(self.png_path)
            
        return values
 

 
    #### DC specific function ####
       
    def makePicture(self, pic_path):
    
        capture =  self.webcam.read()
        
        if capture[0]:   
            self.picture = capture[1]
            i = np.array([2, 1, 0])
            self.im = Image.fromarray(self.picture[:,:,i])
            
            self.im.save(pic_path)
               
        else:
            print("No image captured from webcam with Index %i" % self.cam_index)
    
