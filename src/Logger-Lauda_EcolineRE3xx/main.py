# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2021 SweepMe! GmbH

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank Shayan Miri A. S. for providing the initial version of this driver.

# SweepMe! device class
# Type: Logger
# Device: Logger Lauda Ecoline RE3xx


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                    <p>The Ecoline Staredition RE 3xx is a series of lab thermostats. This driver provides a simple interface for this device. The first output of this module (PV 00) is the outflow or bath temperature. The second output is the status of the machine. (check Operating Instructions page 70).</p>
                    <p>Three main parameters can be set:</p>
                    <ul>
                    <li>The pump power can be 0,1,...,5, where 0 is off.</li>
                    <li>The bath temprature which is right now limited between -8 and +10</li>
                    <li>The operating mode of the refrigerator. Leave it at auto to set the temperature.</li>
                    </ul>
                """

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "RE3xx"
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
                                "baudrate": 9600,
                                "timeout": 1,
                                "EOL": "\r\n",
                                }
                                
        
        self.channels = ["IN PV 00", "STAT"]
        self.operating_mode_dict = {"Off":0, "On 50%":1, "On 100%":2, "Auto":3}
                
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Pump power": [0, 1, 2, 3, 4, 5],
                        "Operating mode": ["Auto", "Off", "On 50%", "On 100%"],
                        "Temperature" : 0,
                        "Temperature unit": ["°C"], # only °C so far but can be extended later on
                        }
                        
        return GUIparameter
    
    def get_GUIparameter(self, parameter = {}):  
    
        self.PumpPower = parameter["Pump power"]
        self.Operating_Mode = parameter["Operating mode"]
        self.Temperature = parameter["Temperature"]
        self.TemperatureUnit = parameter["Temperature unit"]
        
        self.variables = ["Outflow temperature", "Diagnosis"]
        self.units = [self.TemperatureUnit, ""]
        self.plottype = [True for x in self.channels]
        self.savetype = [True for x in self.channels]
        
    def initialize(self):
        
        # Check whether temperature is in applicable range
        if float(self.Temperature) < -8 and float(self.Temperature) > 10:
            self.stop_Measurement("SP (Temperature) is not in the range!")
            return False
        
    def configure(self):

        # Pump power
        self.port.write("OUT SP 01 %s" % self.PumpPower)
        self.port.read()
        
        # Operating mode
        Operating_Mode = self.operating_mode_dict.get(self.Operating_Mode)
        self.port.write("OUT SP 02 %s" % Operating_Mode)
        self.port.read()

        # Temperature
        self.port.write("OUT SP 00 %s" % self.Temperature)
        self.port.read()


    def call(self):
    
        Data = [float('nan') for x in self.channels]
               
        for i, chan in enumerate(self.channels):

            self.port.write("%s" % chan)
            result = self.port.read()

            Data[i] = result
        
        return Data
        