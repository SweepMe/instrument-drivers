# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023 SweepMe! GmBH (sweep-me.net)
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
# Device: Yoctopuce Yocto-4-20mA-Rx


from pysweepme.ErrorMessage import error, debug

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

from yoctopuce.yocto_api import *
from yoctopuce.yocto_genericsensor import *

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description =   """
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Select the channels to be read out.</li>
                    <li>"Zero level at start": A 'zeroAdjust' is performed during configure if checked which removes the current offset from all further measurement values.</li>
                    <li>"Offset" and "Factor can be used recalculate the measured current into a meaningful value. The formula is:<br />y = factor * (x-0.004)*0.016 + offset</li>
                    </ul>
                    <p><strong>Link to API:</strong></p>
                    <p>https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html<br /><br /></p>
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Yocto-4-20mA-Rx" # short name will be shown in the sequencer


    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        GUIparameter = {
                        "Sensor1": True,
                        "Zero level at start 1": False, 
                        "Custom variable1": "",
                        "Custom unit1": "",
                        "Factor1": 1.0,
                        "Offset1": 0.0,

                        "": None,
                        
                        "Sensor2": True,
                        "Zero level at start 2": False, 
                        "Custom variable2": "",
                        "Custom unit2": "",
                        "Factor2": 1.0,
                        "Offset2": 0.0,
                        
                        }

        return GUIparameter
        
       
    def get_GUIparameter(self, parameter):
        
        self.use_sensor1 = parameter["Sensor1"]
        self.use_sensor2 = parameter["Sensor2"]
        
        self.zero_level1 = parameter["Zero level at start 1"]
        self.zero_level2 = parameter["Zero level at start 2"]
        
        self.offset1 = float(parameter["Offset1"])
        self.offset2 = float(parameter["Offset2"])
        
        self.factor1 = float(parameter["Factor1"])
        self.factor2 = float(parameter["Factor2"])
        
        self.custom_variable1 = parameter["Custom variable1"]
        self.custom_variable2 = parameter["Custom variable2"]
        
        self.custom_unit1 = parameter["Custom unit1"]
        self.custom_unit2 = parameter["Custom unit2"]
        
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        if self.use_sensor1:
            self.variables += ["Current1", "Ratio1"]
            self.units += ["mA", "%"]
            self.plottype += [True, True]
            self.savetype += [True, True]
            
            if self.custom_variable1 != "":
                self.variables += [self.custom_variable1]
                self.units += [self.custom_unit1]
                self.plottype += [True]
                self.savetype += [True] 
            
        if self.use_sensor2:
            self.variables += ["Current2", "Ratio2"]
            self.units += ["mA", "%"]
            self.plottype += [True, True]
            self.savetype += [True, True]
            
            if self.custom_variable2 != "":
                self.variables += [self.custom_variable2]
                self.units += [self.custom_unit2]
                self.plottype += [True]
                self.savetype += [True]
            
            
            
        self.port_serial = parameter["Port"]
      
    def find_Ports(self):
    
        errmsg = YRefParam()

        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            self.stop_Measurement("Error in connecting to %s" % self.shortname + errmsg.value)
            return []
        
        ports = []
        
        YAPI.UpdateDeviceList()
        
        sensor = YGenericSensor.FirstGenericSensor()

        if sensor is None:
            self.stop_Measurement("No Yoctopuce %s connected." % self.shortname)
            return ports
        else:
            # retrieve module serial number
            # serial = sensor.get_module().get_serialNumber()  
            serial = sensor.get_module().get_friendlyName()
            ports.append(serial)
        
            sensor = sensor.nextGenericSensor()
            
            while not sensor is None:
                
                # retreive module serial
                # serial = sensor.get_module().get_serialNumber()     
                serial = sensor.get_module().get_friendlyName()

                if not serial in ports:
                    ports.append(serial)
                
                sensor = sensor.nextGenericSensor()

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


        if self.use_sensor1:
            self.sensor1 = YGenericSensor.FindGenericSensor(self.port_serial + '.genericSensor1')
            # print(self.sensor1.get_resolution())
            # self.sensor1.set_resolution(0.0001)
            
            if not (self.sensor1.isOnline()): 
                self.stop_Measurement("Sensor is not online.")
                return False

            
        if self.use_sensor2:
            self.sensor2 = YGenericSensor.FindGenericSensor(self.port_serial + '.genericSensor2')
        
            if not (self.sensor2.isOnline()): 
                self.stop_Measurement("Sensor is not online.")
                return False

        
        
    def disconnect(self):
        
        YAPI.UnregisterHub("usb")
        
        # frees memory, but no further functions can be used
        YAPI.FreeAPI()
        
        
    def configure(self):
    
        if self.use_sensor1:
            if self.zero_level1:
                self.sensor1.zeroAdjust()
            # print(self.sensor1.get_resolution())
            # self.sensor1.set_resolution(0.001)
            

        if self.use_sensor2:
            if self.zero_level2:
                self.sensor2.zeroAdjust()
            # print(self.sensor2.get_resolution())
            # self.sensor2.set_resolution(0.001)


    def call(self):
    
        values = []
    
        if self.use_sensor1:
            if self.sensor1.isOnline():
                val1 = self.sensor1.get_signalValue()
                
                values.append(val1)
                values.append((val1-4.0)/16.0*100.0)
                if self.custom_variable1 != "":
                    values.append(self.factor1 * (val1-4.0)/16.0 + self.offset1)
                
                # print("channel 1:  %f %s" % (self.sensor1.get_signalValue(), self.sensor1.get_unit()))
            else:
                values.append(float('nan'))
                values.append(float('nan'))
                if self.custom_variable1 != "":
                    values.append(float('nan'))


        if self.use_sensor2:    
            if self.sensor2.isOnline():
                val2 = self.sensor2.get_signalValue()
                values.append(val2)
                values.append((val2-4.0)/16.0*100.0)
                if self.custom_variable2 != "":
                    values.append(self.factor2 * (val2-4.0)/16.0 + self.offset2)
                
                # print("channel 2:  %f %s" % (self.sensor2.get_signalValue(), self.sensor2.get_unit()))
            else:
                values.append(float('nan'))
                values.append(float('nan'))
                if self.custom_variable2 != "":
                    values.append(float('nan'))

        return values