# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH
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
# Device: Arduino PWM


import time

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Before using the driver, you need to upload the .ino file that is shipped with this driver to the Arduino.</li>
                    <li>You can set a voltage between 0 and 5 V that will be translated to a PWM value between 0 and 255.</li>
                    <li>The value of "Idle voltage in V" will be set when the branch of the Switch module is entered and left again.</li>
                    <li>The output pin is pin 9 which can be changed by modifying the .ino file before uploading it to the Arduino.</li>
                    </ul>
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Arduino PWM"
        
        self.variables = ["PWM voltage"]
        self.units = ["V"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data
                  
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = { "baudrate": 9600,
                                 "timeout": 2,
                                }

        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["PWM voltage in V"],
                        "Idle voltage in V": "0.0",
                        }
                        
        return GUIparameter
        
    
    def get_GUIparameter(self, parameter={}):
        
        self.idle_voltage = float(parameter["Idle voltage in V"])

    def initialize(self):
    
        self.port.read()  # this is needed as the Arduino sends a first message after startup
        
    def configure(self):
        
        self.set_voltage(self.idle_voltage)
        
    def unconfigure(self):
    
        self.set_voltage(self.idle_voltage)

    def apply(self):
    
        self.value = float(self.value)
        self.set_voltage(self.value)
    
    def call(self):
    
        return [self.value]

    def set_voltage(self, voltage):
    
        voltage = float(voltage)
        
        if voltage > 5.0:
            voltage = 5.0
        elif voltage < 0.0:
            voltage = 0.0
    
        self.port.write("%i" % int(voltage/5.0*255))
        time.sleep(0.015)
        