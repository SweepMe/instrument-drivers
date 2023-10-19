# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
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
# Type: Logger
# Device: Yoctopuce Yocto-0-10V-Tx


from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

from pysweepme.ErrorMessage import error, debug

from yoctopuce.yocto_api import *
from yoctopuce.yocto_voltageoutput import *

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description =   """
                    https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html<br>
                    <br>
                    The idle voltage is set at the beginning and whenever the device is unconfigured.
                    Leave the idle voltage field empty to not set any idle voltage.
                    """
                    
    actions = ["set_voltage_low", "set_voltage_high"]

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Yocto-0-10V-Tx" # short name will be shown in the sequencer


    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        GUIparameter = {
                        "SweepMode": ["Voltage in V"],
                        "Channel": ["1", "2"],
                        "Idle voltage in V": "0",
                        }

        return GUIparameter
        
       
    def get_GUIparameter(self, parameter):
        
        self.channel = parameter["Channel"]
        
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        self.variables.append("Voltage%s" % self.channel)
        self.units.append("V")
        self.plottype.append(True)
        self.savetype.append(True)
            
        self.port_serial = parameter["Port"]
        self.idle_voltage = None if (parameter["Idle voltage in V"] == "") else float(parameter["Idle voltage in V"])
      
    def find_Ports(self):
    
        errmsg = YRefParam()

        # print(YAPI)
        # print(errmsg)
        
        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            self.stop_Measurement("Error in connecting to Yoctopuce %s" % self.shortname + errmsg.value)
            return []
        
        ports = []
        
        YAPI.UpdateDeviceList()
        
        # find all devices
        sensor = YVoltageOutput.FirstVoltageOutput()
        
        if sensor is None:
            self.stop_Measurement("No Yoctopuce %s connected." % self.shortname)
            return ports
        else:
        
            # retrieve module serial or friendly name
            # serial = sensor.get_module().get_serialNumber()     
            serial = sensor.get_module().get_friendlyName()    
            
            ports.append(serial)
        
            sensor = sensor.nextVoltageOutput()
            
            while not sensor is None:
                
                # retrieve module serial or friendly name
                # serial = sensor.get_module().get_serialNumber()     
                serial = sensor.get_module().get_friendlyName()   

                if not serial in ports:
                    ports.append(serial)
                
                sensor = sensor.nextVoltageOutput()
                
        YAPI.UnregisterHub("usb")
        
        ## frees memory, but no further functions can be used
        YAPI.FreeAPI()

        return ports
            
        
        
    def connect(self):

        ## initialize the API. However, it is anyway done during 'RegisterHub'
        # YAPI.InitAPI("usb")
        
        errmsg = YRefParam()
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            self.stop_Measurement("Error connection to Yocto-0-10V-Tx: " + errmsg.value)
            return False
            
        self.voltage_output = YVoltageOutput.FindVoltageOutput(self.port_serial + '.voltageOutput%s' % self.channel)

        if not (self.voltage_output.isOnline()): 
            self.stop_Measurement("Device is not connected.")
            return False
            
    
    def disconnect(self):
        
        YAPI.UnregisterHub("usb")
        
        ## frees memory, but no further functions can be used
        YAPI.FreeAPI()
            
            
    def initialize(self):
        if not self.idle_voltage is None:
            self.voltage_output.set_currentVoltage(self.idle_voltage)
            

    def deinitialize(self):
        pass
        # self.voltage_output.set_voltageAtStartUp(0.0)
        
        
    def unconfigure(self):
        #let's switch the output to the given idle value if the device is no more used
        if not self.idle_voltage is None:
            self.voltage_output.set_currentVoltage(self.idle_voltage)
    
    
    def apply(self):
    
        # print(self.value)
        
        if self.voltage_output.isOnline():
            self.voltage_output.set_currentVoltage(float(self.value))

    
    def measure(self):
    
        # might not be needed as is just returns the set voltage and not the measured voltage
        # todo: check which voltage is returned and remove if it just the set voltage
        if self.voltage_output.isOnline():
            self.voltage_current = self.voltage_output.get_currentVoltage()
    
          
    def call(self):

        return self.voltage_current
        
        
    """ setter/getter functions """
    
    def set_voltage(self, value):
        self.voltage_output.set_currentVoltage(float(value))
    
    def get_voltage(self):
        return self.voltage_output.get_currentVoltage()
    
    def set_voltage_low(self):
        self.voltage_output.set_currentVoltage(0.0)
    
    def set_voltage_high(self):
        self.voltage_output.set_currentVoltage(10.0)
        
    def set_voltage_startup(self, value):
        self.voltage_output.set_voltageAtStartUp(float(value))
        
        
