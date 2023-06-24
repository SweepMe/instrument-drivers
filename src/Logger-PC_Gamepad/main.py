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
# Device: Gamepad


import sys
import win32api
import os

import FolderManager
FolderManager.addFolderToPATH()

import XInput
  
from EmptyDeviceClass import EmptyDevice
  
class Device(EmptyDevice):

    description = """
                    <p>This driver retrieves values from a gamepad.</p>
                    <p>&nbsp;</p>
                    <p><strong>Returned values:</strong></p>
                    <ul>
                    <li>Buttons A, B, X, Y, LB, RB, UP, DOWN, LEFT, RIGHT being bool, True if pressed</li>
                    <li>Triggers: LT, and RT being a float between 0 and 1</li>
                    <li>Sticks:&nbsp;SL x, SL y, SR x, SR y being a float between -1 and 1</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Just select a port index and start measuring.</li>
                    </ul>
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "Gamepad"
        
        self.button_names = {
                            "A": "A",
                            "B": "B",
                            "X": "X",
                            "Y": "Y",
                            "LB": "LEFT_SHOULDER",
                            "RB": "RIGHT_SHOULDER",
                            "UP": "DPAD_UP",
                            "DOWN": "DPAD_DOWN",
                            "LEFT": "DPAD_LEFT",
                            "RIGHT": "DPAD_RIGHT",
                            }
        
        self.variables = list(self.button_names.keys())  + ["LT", "RT"] + ["SL x", "SL y", "SR x", "SR y"]
        self.units = ["" for i in self.variables]
        self.plottype = [True for i in self.variables] # define if it can be plotted
        self.savetype = [True for i in self.variables] # define if it can be plotted
        

    def get_GUIparameter(self, parameter = {}):
        self.port_string = parameter["Port"]
                
    def find_ports(self):
    
        connected = XInput.get_connected()

        ports = []
        for i, x in enumerate(connected):
            if x:
                ports.append(str(i))
        
        return ports
        
    def connect(self):
    
        self.port_index = int(self.port_string)
        
    def call(self):
    
        state = XInput.get_state(self.port_index)

        # get_button_values(state) -> dict
        button_state = XInput.get_button_values(state)
        # print("Button state:", button_state)
        
        # get_trigger_values(state) -> (LT, RT) Returns a tuple with the values of the left and right triggers in range 0.0 to 1.0
        trigger_values = XInput.get_trigger_values(state)
        # print("Trigger values:", trigger_values)
        
        # get_thumb_values(state) -> ((LX, LY), (RX, RY))
        thumb_values = XInput.get_thumb_values(state)
        # print("Thumb values:", thumb_values)

        buttons = []
        for x in self.button_names.keys():
            buttons.append(button_state[self.button_names[x]])

        return buttons + list(trigger_values) + list(sum(thumb_values, ()))
       