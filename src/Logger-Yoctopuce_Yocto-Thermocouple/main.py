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
# Device: Yoctopuce Yocto-Thermocouple


from pysweepme.ErrorMessage import error, debug


from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

from yoctopuce.yocto_api import *
from yoctopuce.yocto_temperature import *

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description =   """
                    https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html<br>
                    <br>
                    
                    """
                   

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Yocto-Thermocouple" # short name will be shown in the sequencer

        self.sensor_types = {
                               "Type K": YTemperature.SENSORTYPE_TYPE_K,
                               "Type E": YTemperature.SENSORTYPE_TYPE_E, 
                               "Type J": YTemperature.SENSORTYPE_TYPE_J, 
                               "Type N": YTemperature.SENSORTYPE_TYPE_N, 
                               "Type R": YTemperature.SENSORTYPE_TYPE_R, 
                               "Type S": YTemperature.SENSORTYPE_TYPE_S, 
                               "Type T": YTemperature.SENSORTYPE_TYPE_T, 
        
                            }

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

    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        GUIparameter = {
                        "Sensor type": list(self.sensor_types.keys()),
                        "Temperature unit": ["°C", "K", "°F"],
                        "Sensor1": True,
                        "Sensor2": False,
                        }

        return GUIparameter
        
       
    def get_GUIparameter(self, parameter):
    
        self.port_serial = parameter["Port"]
        
        self.sensor_type = parameter["Sensor type"]
    
        self.temperature_unit = parameter["Temperature unit"]
        
        self.sensor1 = parameter["Sensor1"]
        self.sensor2 = parameter["Sensor2"]
        
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        if self.sensor1:
            self.variables += ["Temperature1"]
            self.units += [self.temperature_unit]
            self.plottype += [True]
            self.savetype += [True]
            
        if self.sensor2:
            self.variables += ["Temperature2"]
            self.units += [self.temperature_unit]
            self.plottype += [True]
            self.savetype += [True]    
            
            
    def connect(self):


        # initialize the API. However, it is anyway done during 'RegisterHub'
        # YAPI.InitAPI()
        

        errmsg=YRefParam()
        if YAPI.RegisterHub("usb", errmsg)!= YAPI.SUCCESS:
            self.stop_Measurement("Error connection to Yoctopuce %s:" % self.shortname + errmsg.value)
            return False

        if self.sensor1:
            self.temperature1 = YTemperature.FindTemperature(self.port_serial + '.temperature1')

        if self.sensor2:
            self.temperature2 = YTemperature.FindTemperature(self.port_serial + '.temperature2')

        
    def disconnect(self):
        
        YAPI.UnregisterHub("usb")
        
        # frees memory, but no further functions can be used
        YAPI.FreeAPI()
        
        
    def initialize(self):
    
        if self.sensor1:
            if not (self.temperature1.isOnline()): 
                self.stop_Measurement("Sensor is not online.")
                return False  
            else:
                self.temperature1.set_unit(self.temperature_unit)
                self.temperature1.set_sensorType(self.sensor_types[self.sensor_type])

        if self.sensor2:
            if not (self.temperature2.isOnline()): 
                self.stop_Measurement("Sensor is not online.")
                return False
            else:
                self.temperature2.set_unit(self.temperature_unit)
                self.temperature2.set_sensorType(self.sensor_types[self.sensor_type])
        

    def configure(self):
        pass

    def call(self):
    
        values = []
    
        if self.sensor1:
            if self.temperature1.isOnline():
                val = self.temperature1.get_currentValue()
                values.append(val)
            else:
                values.append(float('nan'))

        if self.sensor2:
            if self.temperature2.isOnline():
                val = self.temperature2.get_currentValue()
                values.append(val)
            else:
                values.append(float('nan'))

        return values