# MIT License
# 
# Copyright (c) 2022 SweepMe! (sweep-me.net)
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
# Device: Joystick


import FolderManager
FolderManager.addFolderToPATH()

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pyd_importer
import pygame
  
from EmptyDeviceClass import EmptyDevice
  
  
class Device(EmptyDevice):

    description = """ 
                    <p>Driver to retrieve values from a joystick. Values of the first 4 buttons and first 4 axes are returned.</p>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <p>Just select the port and start measuring.</p>
                    <p>&nbsp;</p>
                    <p><strong>Known issues:</strong></p>
                    <p>For some reason, SweepMe! crashes if the measurement is started if the joystick for the first time. However, once it works, the measurement can be restarted without further crashes. The reason is unclear. It can help to unplug and plug in a again the joystick before starting the measurement.</p>
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "Joystick"
        
        self.variables = ["Axis%i" % i for i in range(1, 5)] + ["Button%i" % i for i in range(1, 5)]
        self.units = ["" for i in self.variables]
        self.plottype = [True for i in self.variables]
        self.savetype = [True for i in self.variables]
        

    def get_GUIparameter(self, parameter = {}):
        self.port = parameter["Port"]
                
    def find_Ports(self):
    
        pygame.joystick.init() 
        joysticks = []
        for i in range(pygame.joystick.get_count()):  
            joystick = pygame.joystick.Joystick(i)  

            joysticks.append("%i - " % i + joystick.get_name())  
         
        pygame.joystick.quit()
          
        return joysticks
        
    def connect(self):
    
        pygame.joystick.init() 
        pygame.display.init() 
        
        index = self.port.find("-")
        joystick_index = int(self.port[:index-1])
        
        try:
            self.joystick = pygame.joystick.Joystick(joystick_index)
            self.joystick.init() 
        except:
            self.stop_Measurement("Joystick was not found. Please check connection and use 'Find Ports' again.")
          
    def disconnect(self):
        
        pygame.joystick.quit() 
        pygame.display.quit()  
                
    def call(self):
    
        pygame.event.pump()

        axes = []
        for i in range(4):
            try:
                axes.append(self.joystick.get_axis(i))
            except:
                axes.append(float('nan'))
                
        buttons = []
        for i in range(4):
            try:    
                buttons.append(self.joystick.get_button(i))
            except:
                axes.append(float('nan'))
                
        return axes + buttons
        
    def handleJoyEvent(self, e): 

        if e.type == pygame.JOYAXISMOTION:  
            axis = "unknown"  
            
            if (e.dict['axis'] == 0):  
                axis = "X" 
                self.x = float(e.dict['value'])
                
            if (e.dict['axis'] == 1):  
                axis = "Y"  
                self.y = float(e.dict['value'])
      
            if (e.dict['axis'] == 2):  
                axis = "Throttle"  
                self.throttle = float(e.dict['value'])
      
            if (e.dict['axis'] == 3):  
                axis = "Z"  
                self.z = float(e.dict['value'])
      
            # if (axis != "unknown"):  
                # str = "Axis: %s; Value: %f" % (axis, e.dict['value'])  
                # uncomment to debug 
      
        elif e.type == pygame.JOYBUTTONDOWN:  
            # str = "Button: %d" % (e.dict['button'])  
            # uncomment to debug  
            # output(str, e.dict['joy'])  
            # Button 0 (trigger) to quit  
            
            
            for i in range(20):
                if (e.dict['button'] == i):  
                    self.button = i
            # if (e.dict['button'] == 0):  
                # print "Fire"  
            # if (e.dict['button'] == 1):
                # print "linker oberer Knopf"
            # if (e.dict['button'] == 2):
                # print "mittlerer oberer Knopf"
            # if (e.dict['button'] == 3):
                # print "rechter oberer Knopf"
            # if (e.dict['button'] == 4):
                # print "F1"
            # if (e.dict['button'] == 5):
                # print "F2"
            # if (e.dict['button'] == 6):
                # print "F3"
            # if (e.dict['button'] == 7):
                # print "F4"
            # if (e.dict['button'] == 8):
                # print "Pfeile links"
            # if (e.dict['button'] == 9):
                # print "Pfeile rechts"
            # if (e.dict['button'] == 10):
                # print "10"
            # if (e.dict['button'] == 17):
                # print "17"
                
        elif e.type == pygame.JOYBUTTONUP:  
            # str = "Button: %d" % (e.dict['button'])  
            # uncomment to debug  
            # output(str, e.dict['joy'])  
            # Button 0 (trigger) to quit  
            
            
            for i in range(20):
                if (e.dict['button'] == i): 
                    pass
                    #self.button = i
