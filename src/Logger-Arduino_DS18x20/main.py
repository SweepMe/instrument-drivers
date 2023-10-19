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
# Type: Logger
# Device: Arduino DS18x20


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                    <p>Use this driver to read one or multiple temperature sensor of the DS18x20 family using an Arduino.</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Enter the number of connected sensors so that the driver can check whether all sensors are connected.</li>
                    <li>Use the field "Variable names" to give each sensor a specific meaning. You can keep the field free to us standard names like "Temperature 1" etc.</li>
                    <li>To speed up readings, the field "Wait for conversion" is switched off by default. In this case, the Arduino continuously triggers new readings in an internal loop and the requested value is the last known value. In order to trigger a new reading when requesting a temperature, please check "Wait for conversion".</li>
                    </ul>
                    <p><strong>Preparations:</strong></p>
                    <p>Before the first measurement, one has to upload the ino file that comes with this driver to the Arduino using the Arduino IDE. The libraries OneWire.h and DallasTemperature.h need to be installed using the ArduinoIDE as well. You can update them using the Library manager of the Arduino IDE The readout pin is D2.</p>
                    <p>Please connect the data wire of your sensor to this readout pin D2.</p>
                    <p>Typically, a 4.7KOhm resistor is needed between +5V and the readout pin. An existing parasite mode, meaning that Vdd gets power from the data line via the resistor, is not recommended. Multiple sensors can be connected to the same readout pin D2 of the Arduino. If many sensors are used, it could help to add 100 Ohm resistors into the data line of each sensor to prevent cross-talk. The sensors are found and enumerated always in the same way depending on their unique ID.</p>
                    <p>To get a list of all addresses, one can send the command "Addresses?" using the Arduino IDE.&nbsp;</p>
                  """


    def __init__(self):

        EmptyDevice.__init__(self)
        
        self.shortname = "Arduino DS18x20"
       
        self.variables = ["Temperature"]
        self.units = ["°C"]
        self.plottype = [True] # True to plot data
        self.savetype = [True]  # True to save data
        
        self.port_manager = True  
        self.port_types = ["COM"]
        self.port_properties = { "timeout":3,
                                 "EOL": "\n",
                                 "baudrate": 9600,
                                }
                                
        self.sensors_count = 1
                                                                        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Unit": ["°C", "°F", "K"],
                        "Connected sensors": self.sensors_count,
                        "Resolution in bit": [12, 11, 10, 9],
                        "Variable names": "",
                        "Wait for conversion": False,
                        # "Readout pin": ["D%i" % (i+2) for i in range(12)],
                        
                        }
                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter):
        
        # self.readout_pin = parameter["Readout pin"]
        self.unit_user = parameter["Unit"]
        self.connected_sensors = int(parameter["Connected sensors"])
        
        self.resolution = int(parameter["Resolution in bit"])
        
        self.wait_for_conversion = parameter["Wait for conversion"]
        
        self.variable_names = parameter["Variable names"]
        if parameter["Variable names"].strip() == "":
            self.variables = ["Temperature %i" % (i+1) for i in range(self.connected_sensors)]
        else:
            self.variables = [x.strip() for x in parameter["Variable names"].split(",")]
        self.units = [self.unit_user for i in self.variables]
        self.plottype = [True for i in self.variables]
        self.savetype = [True for i in self.variables]

    def initialize(self):


        ## This line is very important as the driver needs to wait until the Arduino performed the setup function.
        answer = self.port.read() # read out the initialization string sent by the Arduino
        #print("Startup message:", answer)
        
        ## this part is needed to make sure that as many sensors are connected as asked for by the user.
        self.port.write("Sensors?")
        self.sensors_count = int(self.port.read())
        #print("Detected sensors:", self.sensors_count)
        if self.sensors_count != self.connected_sensors:
            self.stop_Measurement("Number of detected sensors: %i. Please change 'Connected sensors' accordingly or prove your devices." % self.sensors_count)
            
            
        if len(self.variables) != self.sensors_count and self.variable_names.strip() != "":
            raise Exception("Please define as many variable names as you have connected sensors. Use comma-separated strings.")
        
        ## the next lines can be used to retrieve the hex-based addresses of all sensors
        #self.port.write("Addresses?")
        #for i in range(self.sensors_count):
            #answer = self.port.read()
            #print("Address of sensor %i:" % (i+1), answer )
            
        ## the next lines show how to retrieve the current resolution
        #self.port.write("Resolution?")
        #answer = self.port.read()
        #print("Resolution:", answer)
        
        ## the next lines show how to retrieve the WaitForConversion property (0 = Off, 1 = On)
        #self.port.write("WaitForConversion?")
        #answer = self.port.read()
        #print("WaitForConversion:", answer)
            
            
        
    def configure(self):
    
        self.port.write("Resolution=%i" % self.resolution)
        res = self.port.read()    
        # print("Resolution set:", res)
        
        self.port.write("WaitForConversion=%i" % int(self.wait_for_conversion))
        answer = self.port.read()
        # print("WaitForConversion set:", answer)

            
    def measure(self):  
    
        if self.unit_user in ["°C", "K"]:
            self.port.write("ReadC?")
        else:
            self.port.write("ReadF?")

    def call(self):  
    
        temperatures = []
    
        answer = self.port.read().split(",")
        
        for temp in answer:
            temperature = float(temp)
        
            if self.unit_user == "K":
                temperature += 273.15
             
            temperatures.append(temperature)
        
        return temperatures
        
