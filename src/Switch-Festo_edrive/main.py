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
# Device: Festo edrive controller

import time
import os

from pysweepme.ErrorMessage import error, debug
from pysweepme.EmptyDeviceClass import EmptyDevice

# for importing edcon from libraries folder of this driver
from FolderManager import addFolderToPATH
addFolderToPATH()

from edcon.edrive.com_modbus import ComModbus
from edcon.edrive.motion_handler import MotionHandler
from edcon.utils.logging import Logging


class Device(EmptyDevice):

    description = """
    SweepMe! instrument driver for Festo edrive controllers
    
    Communication via TCPIP/Modbus
    If communication fails, please check whether the controller has a valid parameter set, is configured for Modbus
    protocol, correct IP address, 
    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Festo edrive"
        self.variables = ["Position", "Set position"]
        self.units = ["µm", "µm"]
        self.plottype = [True, True] 
        self.savetype = [True, True] 
         
        self.port_manager = False  # we handle the communication in the driver
           
        self.port_types = ["SOCKET"]  # Still, we let the port manager find some TCPIP ports for us
        
        self._verbose_mode = False

        if self._verbose_mode:
            Logging()

    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode": ["Absolute position in µm"],
                        "Velocity in µm/s": "5000",
                        "Reach position": True,
                        "Go home after run": True,
                        }

        return gui_parameter

    def get_GUIparameter(self, parameter):
    
        self.driver_name = parameter["Device"]
        self.port_string = parameter["Port"]
        self.velocity = parameter["Velocity in µm/s"]
        self.go_home_after_run = parameter["Go home after run"]
        self.do_reach_position = parameter["Reach position"]        
        
    def connect(self):
    
        com = ComModbus(self.port_string)
        self.edrive = MotionHandler(com)
        self.edrive.acknowledge_faults()
          
    def disconnect(self):
    
        del self.edrive
        
    def initialize(self):
    
        self.edrive.enable_powerstage()
        
        if not self.edrive.referenced():
            self.edrive.referencing_task()
            
        self.edrive.configure_continuous_update(True)
                             
    def deinitialize(self):
                
        if self.go_home_after_run:       
            self.edrive.position_task(0, int(float(self.velocity)), absolute=True)
            
        self.edrive.shutdown()
         
    def configure(self):
        pass
        
    def unconfigure(self):
        pass

    def apply(self):
    
        value = int(float(self.value))
        self.edrive.position_task(value, int(float(self.velocity)), absolute=True, nonblocking=True)
        
    def reach(self):

        if self.do_reach_position:
            if not self.edrive.target_position_reached():
                self.edrive.wait_for_target_position()

    def call(self):

        position_string = self.edrive.position_info_string()
        values = position_string.split(": ")[1].replace("[","").replace("]", "").split(",")
        set_pos, curr_pos = map(float, values)
        
        return [curr_pos, set_pos]
