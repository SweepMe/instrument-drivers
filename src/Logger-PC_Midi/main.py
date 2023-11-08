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
# Device: Midi input


import time

import os, sys

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
                  Captures Event, Key, and Value.
                  Service run synchronous, i.e. it returns the last known event, key, and value
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Midi input"
        
        self.variables = ["Event", "Key", "Value"]
        self.units = ["", "", ""]
        self.plottype = [True, True, True] # True to plot data
        self.savetype = [True, True, True]  # True to save data
     
    def get_GUIparameter(self, parameter):
        self.port_string = parameter["Port"]
     
    def find_Ports(self):
        ports = mido.get_input_names()
        return ports
        
    def connect(self):
        if self.port_string in mido.get_input_names():
            self.inport = mido.open_input(self.port_string)
            self.inport.callback = self.new_message
        else:
            raise Exception("Unable to find input port. Please use button 'Find Ports' and select one of the available ports.")
        
    def initialize(self):
        self.answer = [float('nan'),float('nan'),float('nan')]  
        # self.answer = [-1,-1,-1]
              
    def disconnect(self):
        self.inport.close()

    def call(self):
        return self.answer
        
    def new_message(self, msg):
        # print(msg)
        self.answer = msg.bytes()
        
        
    """
    # poll a message
    self.inport.poll()
    
    # receive last message from queue
    self.inport.receive()
    
    # get generator with all pending messages from queue
    self.inport.iter_pending():
    """
    
    