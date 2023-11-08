# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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
# Device: Midi output

import time

import os, sys
import numpy as np

from FolderManager import addFolderToPATH
addFolderToPATH()

if sys.version_info[0:2] == (3,6):
    import pyd_importer  # needed to correctly import pyd files from libs folder in Python 3.6
import mido
import mido.backends.rtmidi
mido.set_backend('mido.backends.rtmidi')

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                  <p>Note must be an integer between 0 and 127</p>
                  
                  <p>You might not hear a sound when testing using the Apply-Button, as the Test mode disconnects
                  from the device immediately after applying the value.</p> 
    
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Midi output"
        
        self.variables = ["Note"]
        self.units = [""]
        self.plottype = [True]
        self.savetype = [True]
     
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode" : ["Note"],
                        "Channel": 0,
                        "Velocity": "32",
                        "Time in s": "1.0",
                        }
                        
        return GUIparameter
      
     
    def get_GUIparameter(self, parameter):
        self.port_string = parameter["Port"]
        
        self.channel = int(parameter["Channel"])
        self.velocity = int(float(parameter["Velocity"]))
        self.playtime = float(parameter["Time in s"])
     
    def find_Ports(self):

        ports = mido.get_output_names()
        
        return ports
        
    def connect(self):
        
        if self.port_string in mido.get_output_names():
            self.midiout = mido.open_output(self.port_string)
        else:
            self.midiout = mido.open_output('VirtualMidiPort', client_name=self.port_string)
        
        # print(self.midiout)
        
    def disconnect(self):
       
        self.midiout.close()
        
    def initialize(self):
    
        self.last_note = float('nan')
            
    def deinitialize(self):

        self.midiout.panic()
        
    def apply(self):
             
        note = int(np.clip(float(self.value), 0, 127))
        
        note_on = mido.Message('note_on', channel = self.channel , note = note, velocity=self.velocity, time=self.playtime)
        # print(note_on)
        self.midiout.send(note_on)
        
        self.last_note = note
        
    def call(self):
        
        return self.last_note
