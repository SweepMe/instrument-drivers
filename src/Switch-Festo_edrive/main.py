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
# Module: Switch
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
    protocol, has correct IP address. Also try to restart the controller if a different interface has been used 
    beforehand. 
    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Festo edrive"
        self.variables = ["Position", "Set position"]
        self.units = ["µm", "µm"]
        self.plottype = [True, True] 
        self.savetype = [True, True] 
         
        self.port_manager = False  # we handle the communication in the driver on our own
        self.port_types = ["SOCKET"]  # Still, we let the port manager find some possible TCPIP ports for us
        
        self._verbose_mode = False

        if self._verbose_mode:
            # once switched on it cannot be stopped.
            Logging()

    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode": ["Absolute position in µm"],
                        "Velocity": "5000",
                        "Reach position": True,
                        "Go home after run": True,
                        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.port_string = parameter["Port"]
        self.velocity = parameter["Velocity"]
        self.go_home_after_run = parameter["Go home after run"]
        self.do_reach_position = parameter["Reach position"]        
        
    def connect(self):
    
        self.com = ComModbus(self.port_string)
        # self.com.set_timeout(10)  # not needed right now, but can be used later
        self.edrive = MotionHandler(self.com)
        self.edrive.acknowledge_faults()
          
    def disconnect(self):

        self.com.shutdown()

        # probably not needed, but helps to clean-up
        del self.edrive
        del self.com
        
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

        self.edrive.stop_motion_task()

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

        # We need to overwrite the current position because the real position from position_info_string() is not
        # always up to date
        curr_pos = self.edrive.current_position()
        
        return [curr_pos, set_pos]
