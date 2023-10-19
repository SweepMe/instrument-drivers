# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 SweepMe! GmbH
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
# Type: Temperature
# Device: Scientific Instruments


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Model 9700"
                
        self.variables =["Temperature"]
        self.units =    ["K"]
        self.plottype = [True] # True to plot data
        self.savetype = [True] # True to save data
                
        self.port_manager = True
        self.port_types = ["GPIB", "COM"]
        
        self.port_properties = { "timeout": 1,
                                 "EOL": "\r",
                                 "baudrate": 9600,
                               }
                               
    """ here function to interact with the GUI are added """                       
                                 
    def set_GUIparameter(self):

        GUIparameter = {
                        "SweepMode": ["Temperature", "None"],
                        "Channel": ["A", "B"],
                        "ZeroPowerAfterSweep": True,
                        "IdleTemperature": "",
                        "TemperatureUnit": ["K"],
                        }
                        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
    
        self.sweepmode = parameter["SweepMode"]
        self.channel = parameter["Channel"]
        self.is_zero_power_after_run = parameter["ZeroPowerAfterSweep"]
        self.idle_temperature = parameter["IdleTemperature"]
        
    """ here semantic standard driver functions start """
        
    def initialize(self):
        identification = self.get_identification()
        
    def deinitialize(self):
        pass
    
    def configure(self):
    
        self.set_sensor(self.channel)
        self.enable_channel(self.channel)
        
        self.port.write("CTYP 1") #?? 
        
        if self.sweepmode == "Temperature":
            self.set_mode(2) # Manual
        else:
            self.set_mode(1) # Stop
        
    def unconfigure(self):
        self.port.write("CHEN %s,0" % self.channel)
        
        if self.idle_temperature != "":
            self.set_temperature(self.idle_temperature)
        
        if self.is_zero_power_after_run:
            self.set_mode(1) # Stop
            
        
    def apply(self):
        if self.sweepmode == "Temperature":
            self.set_temperature(self.value)
   
    def measure(self):
        self.port.write('T%s?' % self.channel)
        
    def call(self):
        T = float(self.port.read()[3:])
        return [T]
        

    """ Here, module specifig function start """

    def measure_temperature(self):
        """ a function specific for the Temperature module that is used by the built-in reach functionality to check the latest temperature value """
        return self.get_temperature()
    
    
    """ Here set/get functions start """
    
    def get_identification(self):
        """ query the identifcation string """
    
        self.port.write('*IDN?')
        identification = self.port.read()
        return identification
    
    def get_model(self):
        """ reading the model name """
        
        self.port.write('N1')
        model = self.port.read()
        return model
        
    def get_serialnumber(self):
        """ reading the serial number """
    
        self.port.write('N2')
        serialnumber = self.port.read()
        return serialnumber
        
    def set_mode(self, mode):
        """  Control Mode
             1 = Stop,
             2 = Manual, 
             3 = Program, 
             4 = AutoTune, 
             5 = Fixed Output    
        """
        
        if mode < 1 or mode > 5:
            raise ValueError("Setting mode not possible because index is out of range")
            
        self.port.write("MODE %i" % int(mode))
       
    
    def set_temperature(self, value):
        """ setting the setpoint temperature """
        
        self.port.write("SET %1.3f" % float(self.value))
        
    def get_setpoint_temperature(self):
        """ query the setpoint temperature """
        
        self.port.write("SET?")
        value = float(self.port.read())
        return value
           
    def get_temperature(self):
        """ query the current temperature """
        
        self.port.write('T%s?' % self.channel)
        T =  float(self.port.read()[3:])
        return T
         
    def get_output(self):

        self.port.write("HTR?")
        output = float(self.port.read())
        return output
         
    def set_sensor(self, sensor):
        """ set the sensor/channel """
    
        self.port.write("CSEN %s" % str(sensor))   # Control sensor
        
    def set_channel(self, channel):
        """ set channel """

        self.set_sensor(channel)
        
    def enable_channel(self, channel):
        """ enanle an channel """
        
        self.port.write("CHEN %s,1" % str(channel))
        
    def disable_channel(self, channel):
        """ disable a channel """

        self.port.write("CHEN %s,0" % str(channel))
     
    def set_control_type(self, control_type):
        """ set the PID control type
                
            1 = Normal (single PID settings)
            2 = Zone (multiple PID settings)

        """
        
        self.port.write("CTYP %i" % int(control_type))
        
        