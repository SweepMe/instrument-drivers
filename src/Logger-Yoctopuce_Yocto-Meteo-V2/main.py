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
# Device: Yoctopuce Yocto-Meteo-V3


from pysweepme.ErrorMessage import error, debug

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

from yoctopuce.yocto_api import *
from yoctopuce.yocto_temperature import *
from yoctopuce.yocto_humidity import *
from yoctopuce.yocto_pressure import *

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description =   """
                    https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html<br>
                    <br>
                    
                    
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Yocto-Meteo-V2" # short name will be shown in the sequencer

        self.variables = ["Temperature", "Humidity", "Pressure"]
        self.units = ["°C", "%", "mbar"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]
        
        

    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        GUIparameter = {
                        }

        return GUIparameter
        
       
    def get_GUIparameter(self, parameter):
        
        self.port_serial = parameter["Port"]
      
    def find_Ports(self):
    
        errmsg = YRefParam()

        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            self.stop_Measurement("Error in connecting to %s" % self.shortname + errmsg.value)
            return []
        
        ports = []
        
        YAPI.UpdateDeviceList()
                
        sensor = YTemperature.FirstTemperature()

        if sensor is None:
            self.stop_Measurement("No Yoctopuce %s connected." % self.shortname)
            return ports
        else:
            # retrieve module serial number
            # serial = sensor.get_module().get_serialNumber()  
            serial = sensor.get_module().get_friendlyName()
            ports.append(serial)
        
            sensor = sensor.nextTemperature()
            
            while not sensor is None:
                
                # retreive module serial
                # serial = sensor.get_module().get_serialNumber()     
                serial = sensor.get_module().get_friendlyName()

                if not serial in ports:
                    ports.append(serial)
                
                sensor = sensor.nextTemperature()
                
                
        YAPI.UnregisterHub("usb")
        YAPI.FreeAPI()
        
        return ports
            

        
    def connect(self):

        
        # initialize the API. However, it is anyway done during 'RegisterHub'
        # YAPI.InitAPI()
        

        errmsg=YRefParam()
        if YAPI.RegisterHub("usb", errmsg)!= YAPI.SUCCESS:
            self.stop_Measurement("Error connection to Yoctopuce %s:" % self.shortname + errmsg.value)
            return False


        self.temperature_sensor = YTemperature.FindTemperature(self.port_serial + '.temperature')
        self.humidity_sensor = YHumidity.FindHumidity(self.port_serial + '.humidity')
        self.pressure_sensor = YPressure.FindPressure(self.port_serial + '.pressure')

        
        if not (self.temperature_sensor.isOnline()): 
            self.stop_Measurement("Temperature sensor is not online.")
            return False
            
        if not (self.humidity_sensor.isOnline()): 
            self.stop_Measurement("Humidity sensor is not online.")
            return False
            
        if not (self.pressure_sensor.isOnline()): 
            self.stop_Measurement("Pressure sensor is not online.")
            return False


        
    def disconnect(self):
        
        YAPI.UnregisterHub("usb")
        
        # frees memory, but no further functions can be used
        YAPI.FreeAPI()
        
        
    def initialize(self):
        
        pass

    def configure(self):
        
        pass


    def call(self):
    
        values = []
    
        if self.temperature_sensor.isOnline():
            val1 = self.temperature_sensor.get_currentValue()
            values.append(val1)
        else:
            values.append(float('nan'))
            
            
        if self.humidity_sensor.isOnline():
            val1 = self.humidity_sensor.get_currentValue()
            values.append(val1)
        else:
            values.append(float('nan'))
            
            
        if self.pressure_sensor.isOnline():
            val1 = self.pressure_sensor.get_currentValue()
            values.append(val1)
        else:
            values.append(float('nan'))


        return values
