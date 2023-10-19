# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 - 2022 SweepMe! GmbH
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
# Device: Zaber Motion

from FolderManager import addFolderToPATH
addFolderToPATH()

from zaber_motion import Units
from zaber_motion.ascii import Connection
from zaber_motion import Library

import time
import os

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!


class Device(EmptyDevice):

    description =   """
                    <p>This driver can be used to control all motorized stages from Zaber with motor controllers that work with the&nbsp;Zaber Motion Library. Modern Zaber devices communicate in the ASCII protocol but also the legacy Binary protocol is supporeted used by older devices.</p>
                    <p>&nbsp;</p>
                    <p><strong>Communication:</strong></p>
                    <ul>
                    <li>COM port: Baudrate = 115200 (fixed)</li>
                    <li>Channel = Device address (Each daisy chained motor needs a unique device address that you can set using 'Zaber Console' or 'Zaber Launcher')</li>
                    <li>Axis = The axis number of a device. Linear stages just have one axis.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>At first use, the driver will contact the Zaber server to download information about the device, e.g.&nbsp; to allow for unit conversion.</li>
                    <li>The only Sweep mode is "Absolute position" and the unit can be selected in the parameter field "Unit".</li>
                    <li>Rotary stages are supported as well. Angles can be handed over by using units deg, &deg;, or rad. deg and &deg; are equal.</li>
                    <li>Velocity can be changed externally using Zaber Console or Zaber Launcher.</li>
                    <li>The driver makes a home positioning at the start if no reference position is known.</li>
                    <li>The field "Reach position" is True by default and the driver waits until the stage has reached the new position before the measurement continues. If you uncheck this field, you can quickly change the set position, e.g. when controlling the stage using sliders or external values.</li>
                    <li>You can make use of a Zaber's Virtual Device (<a href="https://software.zaber.com/virtual-device/home">https://software.zaber.com/virtual-device/home</a>) where you get a Cloud ID that you can copy into the field "Port" of the driver and all further instrument communication will run via the web service of the Virtual Device.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Privacy policy:</strong></p>
                    <p>When starting a run, the driver contacts the Zaber server to download information from a database about device specific properties as needed for correct unit conversion. The database information are then stored locally and the online database is not contacted again, except a new device is used. Also if you use a Virtual Device, the driver will communicate with the Zaber server. Before you use the driver, please inform yourself about Zaber's privacy policy (<a href="https://www.zaber.com/privacy-policy">https://www.zaber.com/privacy-policy</a>&nbsp;and <a href="https://software.zaber.com/privacy-policy">https://software.zaber.com/privacy-policy</a>).</p>
                    <p>&nbsp;</p>
                    <p><strong>Programming manual:&nbsp;</strong><a href="https://www.zaber.com/software/docs/motion-library/ascii/" target="_blank" rel="nofollow noreferrer noopener">https://www.zaber.com/software/docs/motion-library/ascii/</a></p>
                    """
                    
                    

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Zaber motion"
        self.variables = ["Position"]
        self.units = ["steps"] # will be overwritten by user setting
        self.plottype = [True] 
        self.savetype = [True] 
         
        self.port_manager = False  # we handle the communication in the driver
           
        self.port_types = ["COM"]  # Still, we let the port manager find some COM ports for us
        
        self._verbose_mode = False
                
        self.unit_types = {
                      "steps": Units.NATIVE,
                      "m": Units.LENGTH_METRES,
                      "cm": Units.LENGTH_CENTIMETRES,
                      "mm": Units.LENGTH_MILLIMETRES,
                      "µm": Units.LENGTH_MICROMETRES,
                      "nm": Units.LENGTH_NANOMETRES,
                      "inch": Units.LENGTH_INCHES,
                      "deg" : Units.ANGLE_DEGREES,
                      "°" : Units.ANGLE_DEGREES,
                      "rad" : Units.ANGLE_RADIANS,
                    }
                    
                    
    # def find_ports(self):
        ## this function could be used in future to provide a COM port and a device number
        # pass
        

    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode": ["Absolute position"],
                        "Channel": list(range(1, 256, 1)),
                        "Axis": list(range(1, 5, 1)),
                        "Unit": list(self.unit_types.keys()),
                        
                        "Reach position": True,
                        "Go home after run": True,
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter):
    
        self.driver_name = parameter["Device"]
        self.port_string = parameter["Port"]
        self.channel = int(parameter["Channel"])
        self.axis_id = int(parameter["Axis"])
        self.go_home_after_run = parameter["Go home after run"]
        
        self.do_reach_position = parameter["Reach position"]
        
        self.unit = self.unit_types[parameter["Unit"]]
        
        self.units = [parameter["Unit"]] 
        
        
    def connect(self):
    
        # We store the database in public SweepMe! folder "DataDevices"
        # The database is contacted once and then the data is stored locally
        db_store = self.get_folder("DATADEVICES") + os.sep + self.driver_name
        if not os.path.exists(db_store):
            os.mkdir(db_store)
        Library.enable_device_db_store(db_store)
        
    
        connection_identifier = "Zaber_motion_%s" % self.port_string
        
        # We make sure that the connection is only created once and shared with other driver instances
        # if the connection was already created and multiple devices are interfaces via one communication port
        if connection_identifier in self.device_communication:
            self.connection = self.device_communication[connection_identifier]
        else:  
            if self.port_string.startswith("COM"):
                self.connection = Connection.open_serial_port(self.port_string)
            
            # a connection to a Virtual Device using Zaber's web service, enter the Cloud ID in the field 'Port' to use it
            elif len(self.port_string.split("-")) == 5:
                self.connection = Connection.open_iot_unauthenticated(self.port_string)
                
            self.device_communication[connection_identifier] = self.connection
            

        device_list = self.connection.detect_devices()
        
        if not self.channel in [dev.device_address for dev in device_list]:
            raise Exception("Device ID is not used by any found device.")

        device = self.connection.get_device(self.channel)
        
        if self.axis_id > device.axis_count:
            raise Exception("Axis number is higher than the number of axes the device has.")
    
        self.axis = device.get_axis(self.axis_id)
        

    def disconnect(self):
    
        connection_identifier = "Zaber_motion_%s" % self.port_string
        if connection_identifier in self.device_communication:
            self.connection.close()
            del self.device_communication[connection_identifier]
        

        
    def initialize(self):
       
        self.axis.unpark()
       
        self.is_finding_reference = False
        if "WR" in self.axis.warnings.get_flags():
            self.axis.home(wait_until_idle = False)
            self.is_finding_reference = True

                
    def deinitialize(self):
                
        if self.go_home_after_run:       
            self.axis.home(wait_until_idle = False) 
            

    def configure(self):
        
        if self.is_finding_reference:
            self.reach_position()
    
        
    def unconfigure(self):
        
        self.reach_position()
        self.axis.stop(wait_until_idle = True)
        self.axis.park()

 
    def apply(self):
    
        self.axis.move_absolute(float(self.value), unit = self.unit, wait_until_idle = False)
      
      
    def reach(self):

        if self.do_reach_position:
            self.reach_position()
        

    def call(self):
    
        pos = self.axis.get_position(unit = self.unit)
        
        return [pos]
        
        
    def reach_position(self):
    
        i=0
        while self.axis.is_busy():
            i+=1
            # print(i, "busy", self.axis.get_position(unit = self.unit))
            time.sleep(0.05)
    

        
 