# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 Axel Fischer (sweep-me.net)
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
# Device: Optris CT 




from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!
# If you like to see the source code of EmptyDevice, take a look at the pysweepme package that contains this file

class Device(EmptyDevice):

    ## here you can add html formatted description to your device class that is shown by modules like 'Logger' or 'Switch' that have a description field.
    description =   """
                    <p><strong>Communication:</strong></p>
                    <ul>
                    <li>The address number is only needed for RS-485 where each unit has a unique address. In case of RS-232 or USB, the address can be any number and thus the default value 1 can simply be used.</li>
                    <li>The driver uses the default baudrate of 115200.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Parameters:</strong></p>
                    <ul>
                    <li>Epsilon is the emission coefficient in the range 0.1&nbsp; - 1.1 describing the object to be measured.</li>
                    <li>Transmission is a coefficient in the range 0.1 - 1.1, that can be used if the signal is weakened by a medium between sensor and point of interest. Default value is 1.0 which means that no medium or object attenuates the signal.</li>
                    <li>There are two averaging modes:&nbsp;Smart averaging (default) and&nbsp;Normal<br />Smart averaging stops the averaging if there are larger signal changes. Values can be between 0.1 s and 65 s. A value of 0.0 s means that averaging is switched off.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Laser:</strong></p>
                    <p>You can automatically switch on the laser during the measurement and/or after the measurement. Please take care about appropriate laser safety measures.</p>
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Optris CT" # short name will be shown in the sequencer
        self.variables = ["Temperature", "Temperature Head"] # define as many variables you need
        # self.units = ["°C", "°C"] # make sure that you have as many units as you have variables
        self.plottype = [True, True]   # True to plot data, corresponding to self.variables
        self.savetype = [True, True]   # True to save data, corresponding to self.variables
        
        
        ### use/uncomment the next line to use the port manager
        self.port_manager = True 
           
        # use/uncomment the next line to let SweepMe! search for ports of these types. Also works if self.port_manager is False or commented.
        self.port_types = ["COM"]
        self.port_properties = {
                                "timeout": 5,
                                "baudrate": 115200,
                                "EOL": "",
                                "rstrip": False,
                                }
            
            
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "Address": ["%i" % i for i in range(1,256,1)],
                        "": None,
                        "Epsilon": 1.0,
                        "Transmission": 1.0,
                        "Temperature unit": ["°C", "K", "°F"],
                        "Averaging mode": ["Smart averaging", "Normal", "Off"],
                        "Averaging time in s": 0.2,
                        " ": None,
                        "Laser on during run": False,
                        "Laser on afterwards": False,
                        
                        
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter):

        self.address = int(parameter["Address"])

        self.epsilon = float(parameter["Epsilon"])
        self.transmission = float(parameter["Transmission"])
        
        self.temperature_unit = parameter["Temperature unit"]
        self.units = [self.temperature_unit, self.temperature_unit]
        
        self.laser_on_during_run = parameter["Laser on during run"]
        self.laser_on_afterwards = parameter["Laser on afterwards"]
        
        self.averaging_mode = parameter["Averaging mode"]
        self.averaging_time = float(parameter["Averaging time in s"])
        
    def initialize(self):
        
        self.ADDR = chr(ord("\xb0") + self.address)  # this is the address prefix character, only needed for RS-485 communication
        # print(self.ADDR)
        
    def configure(self):
               
        if self.averaging_mode != "Off":     
            self.set_smart_average_mode(self.averaging_mode == "Smart averaging")
            # print(self.is_smart_average_mode())
        
            self.set_average_time(self.averaging_time)
            # print(self.get_average_time())
            
        else:
            self.set_average_time(0.0)
            # print(self.get_average_time())
                       
        self.set_epsilon(self.epsilon)
        # print(self.get_epsilon())
        
        self.set_transmission(self.transmission)
        # print(self.get_transmission())

        if self.laser_on_during_run:
            self.activate_laser()
            # print(self.is_laser_activated())
        else:
            self.deactivate_laser()
            
        # print(self.port.in_waiting())
        
    def unconfigure(self):
        
        if self.laser_on_afterwards:
            self.activate_laser()
            # print(self.is_laser_activated())
        else:
            self.deactivate_laser()
            
    def measure(self):
        
        
        self.temperature = self.get_temperature()
        self.temperature_head = self.get_temperature_head()
        
        if self.temperature_unit == "°C":
            pass
        elif self.temperature_unit == "K":
            self.temperature += 273.15
            self.temperature_head += 273.15
        elif self.temperature_unit == "°F":
            self.temperature = 9/5 * self.temperature + 32
            self.temperature_head = 9/5 * self.temperature_head + 32
             
    def read_result(self):
        
        pass
          
          
    def call(self):
   
        return [self.temperature, self.temperature_head]


    def get_checksum(self, cmd):
        
        checksum = 0
        for char in cmd:
            checksum ^= ord(char)

        return chr(checksum)
        

    def get_temperature(self):
        
        self.port.write(self.ADDR + "\x01")
        answer = self.port.read(2)
        return ((ord(answer[0]) * 256 + ord(answer[1])) - 1000) / 10.0
        
    def get_temperature_head(self):
        
        self.port.write(self.ADDR + "\x02")
        answer = self.port.read(2)       
        return ((ord(answer[0]) * 256 + ord(answer[1])) - 1000) / 10.0
        
    def get_temperature_box(self):
        
        self.port.write(self.ADDR + "\x03")
        answer = self.port.read(2)       
        return ((ord(answer[0]) * 256 + ord(answer[1])) - 1000) / 10.0
        
    def set_epsilon(self, val):

        val = int(val * 1000.0)
        byte1 = (val - val%256) // 256
        byte2 = val%256
        
        msg = "\x84" + chr(byte1) + chr(byte2)
        self.port.write(self.ADDR + msg + self.get_checksum(msg))
        answer = self.port.read(2)
        
    def get_epsilon(self):
        
        self.port.write(self.ADDR + "\x04")
        answer = self.port.read(2)       
        return (ord(answer[0]) * 256 + ord(answer[1])) / 1000.0


    def set_transmission(self, val):

        val = int(val * 1000.0)
        byte1 = (val - val%256) // 256
        byte2 = val%256
        
        msg = "\x85" + chr(byte1) + chr(byte2)
        self.port.write(self.ADDR + msg + self.get_checksum(msg))
        answer = self.port.read(2)
        
    def get_transmission(self):
        
        self.port.write(self.ADDR + "\x05")
        answer = self.port.read(2)       
        return (ord(answer[0]) * 256 + ord(answer[1])) / 1000.0

    def activate_laser(self, state = True):
        
        if state:
            msg = "\xa5\x01" 
        else:
            msg = "\xa5\x00" 
            
        self.port.write(self.ADDR + msg + self.get_checksum(msg))
        answer = self.port.read(1)
        
    def deactivate_laser(self, state = True):
        
        self.activate_laser(not state)

    
    def is_laser_activated(self):
        
        self.port.write(self.ADDR + "\x25")
        answer = self.port.read(1)
        return answer[0] == "\x01"
        
    def set_average_time(self, val):
        
        val = int(val * 10.0)
        byte1 = (val - val%256) // 256
        byte2 = val%256
        
        msg = "\x86" + chr(byte1) + chr(byte2)
        self.port.write(self.ADDR + msg + self.get_checksum(msg))
        
        answer = self.port.read(2)
        # print(repr(answer))
        
        
    def get_average_time(self):
        
        self.port.write(self.ADDR + "\x06")
        
        answer = self.port.read(2)
        # print(repr(answer))
        return (ord(answer[0]) * 256 + ord(answer[1])) / 10.0
        
    def set_smart_average_mode(self, state):

        if state:
            msg = "\x9c\x01" 
        else:
            msg = "\x9c\x00" 
            
        self.port.write(self.ADDR + msg + self.get_checksum(msg))
        answer = self.port.read(1)
        
    def set_normal_average_mode(self, state):
    
        self.set_smart_average_mode(not state)
        
    def is_smart_average_mode(self):
        
        self.port.write(self.ADDR + "\x1c")
        answer = self.port.read(1)       
        return answer[0] == "\x01"
  