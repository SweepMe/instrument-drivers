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
# Type: Temperature
# Device: CreaPhys RCU001


import time

from ErrorMessage import debug
from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
    """
    
    actions = ["reset_thickness", "reset_time"]
    
    def __init__(self):
    
    
        EmptyDevice.__init__(self)
        
        self.shortname = "RCU001"
    
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 0.5,
                                    "baudrate": 9600,
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "EOL": "\r",
                                    }

       
        self.STX = chr(0x02)
        self.EOT = chr(0x03)
        self.ADDR = chr(0x41) # address, seems to be always 0x41
        self.ERROR = chr(0x21) # error character ! (0x21) that specifies something went wrong
        
        
        self.error_codes = {
                            "A": "Check-sum Error", # ASCII 'A' 
                            "B": "CMD Code unknown", # ASCII 'B' 
                            "C": "MEM Address unknown", # ASCII 'C'
                            "D": "MEM Address not Writable", # ASCII 'D' 
                            "E": "Value out of bounds", # ASCII 'E' 
                            }
        
        # ASCII 'A' (0x41) – Check-sum Error
        # ASCII 'B' (0x42) – CMD Code unknown
        # ASCII 'C' (0x43) – MEM Address unknown
        # ASCII 'D' (0x43) – MEM Address not Writable
        # ASCII 'E' (0x44) – Value out of bounds
        
        
        ## used to test the checksum generation
        # self.create_checksums(msg = self.STX + self.ADDR + "0" + self.EOT)
        # self.create_checksums(msg = self.STX + self.ADDR + "!" + "A76" + self.EOT)
        # self.create_checksums(msg = self.STX + self.ADDR + "1" + "ts" + self.EOT)
        # self.create_checksums(msg = self.STX + self.ADDR + "1" + "ts" + "1.1" + self.EOT)
        # self.create_checksums(msg = self.STX + self.ADDR + "2" + "ts" + "100" + self.EOT)
        # self.create_checksums(msg = self.STX + self.ADDR + "1" + "ts" + "100.0" + self.EOT)

        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode": ["Temperature", "Output in %", "None"],
                        "TemperatureUnit": ["°C", "K", "°F"],
                        "ZeroPowerAfterSweep": True,
                        }
                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}): 
    
        # print(parameter)
    
        self.sweepmode = parameter["SweepMode"]
        self.temperature_unit = parameter["TemperatureUnit"]
    
        self.variables = ["Temperature", "Output"]
        self.units = [self.temperature_unit, "%"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.zero_power_afterwards = parameter["ZeroPowerAfterSweep"] # must be changed to user selection
       
    """ Here, semantic standard functions start """
       
    def initialize(self):
    
        pass
 
        
    def configure(self): 
    
        if self.sweepmode.startswith("Temperature"):
            self.set_temperature_control()
           
        elif self.sweepmode.startswith("Output"):
            self.set_output_control()

        else:            
            self.set_idle()
            
            
    def unconfigure(self):
        
        if self.zero_power_afterwards:
            self.set_idle()
        
    def apply(self):
        
        
        if self.sweepmode.startswith("Temperature"):
           
            if self.temperature_unit == "°C":
                value = self.value
                
            elif self.temperature_unit == "K":
                
                value = float(self.value) - 273.15
            
            elif self.temperature_unit == "°F":
            
                value = 5/9*(float(self.value) - 32.0)
           
            self.set_temperature(float(value))
           
        elif self.sweepmode.startswith("Output"):
            
            self.set_output(float(self.value))
        

    def call(self):
       
        temperature = self.get_temperature()
        
        if self.temperature_unit == "°C":
            pass
            
        elif self.temperature_unit == "K":
            
            temperature = temperature +  273.15
        
        elif self.temperature_unit == "°F":
        
            temperature = (9.0/5*temperature) + 32.0
        
        output = self.get_output()
        
        return [temperature, output]
        
        
        
    def measure_temperature(self):
        
        temperature = self.call()[0]
        
        return temperature
      
    
    """ Here, communication functions start """  

         
    def write_message(self, MEM = "", DATA = ""):
        
        # <STX><ADDR><CMD>[MEM]...[DATA]...<EOT><CHK1><CHK2><CR>
    
        # STX start of transmission character 0x02
        # ADDR address of the instrument (always 0x41 for now)
        # CMD "1" to read data field, "2" to write data field, "0" to request communications version
        # MEM are always two characters
        # DATA some values in case of writing a a data field
        # EOT End of transmission character 0x03
        # CR is not appended as this is done by the port manager of SweepMe!
        

        if MEM == "":
            CMD = "0"
        
        else:
            # If there is data to be sent, then we know that we have to write a data field
            if len(str(DATA)) > 0:
                CMD = "2"
            else:
                CMD = "1"
          
        
        msg = self.STX + self.ADDR + str(CMD) + MEM + str(DATA) + self.EOT
        
        checksums = self.create_checksums(msg)
        
        msg += checksums
        
        self.port.write(msg)
        # self.port.write(msg.encode("latin1"))


    def read_message(self):
            
        answer = self.port.read()
        
        if answer[0] == self.STX:
        
            # Address should be 'A' 0x41
            ADDR = answer[0]
            
            # Typically 1 
            CMD = answer[1] # read or write
            
            if CMD == self.ERROR:
            
                error_code = answer[2]

                if error_code in self.error_codes:
                    
                    print("RCU001 responded with error message:", self.error_codes[chr(error_code)])
                
                    # in case of 0x41, the expected checksum is returned
                               
                    # ERR_CODE : Error Code can be one of the following:
                    # ASCII 'A' (0x41) – Check-sum Error
                    # ASCII 'B' (0x42) – CMD Code unknown
                    # ASCII 'C' (0x43) – MEM Address unknown
                    # ASCII 'D' (0x43) – MEM Address not Writable
                    # ASCII 'E' (0x44) – Value out of bounds
            
            else:
                MEM = answer[3:5]

            eot_index = answer.find(self.EOT)
            data = answer[5:eot_index]
            
            checksums = answer[eot_index+1:]
            
            calculated_checksums = self.create_checksums(answer[:eot_index+1])
            
            # let's do some checksum check here
            if calculated_checksums != checksums:
                print("RCU001: Returned checksum of RCU001 does not match to retrieved message")

            if data.isdigit():
                return int(data)
            else:
                try:
                    return float(data)
                except:
                    return data
                  

        
    def create_checksums(self, msg):
                
        sum = 0
        
        for char in msg:
            
            sum += ord(char)
            
            while sum > 255:
                sum -= 256
            
        C1 = int(sum / 16) + 0x30
        C2 = int(sum % 16) + 0x30

        return chr(C1) + chr(C2)


    """ Here, convenience functions start """ 
        
        
    def is_temperature_sensor_ok(self):
    
        self.write_message("tf")
        return self.read_message() == "0"
        
        
    def is_rate_sensor_ok(self):
    
        self.write_message("of")
        return self.read_message() == "0"
        
    def get_temperature(self):
        
        self.write_message("ct")
        return float(self.read_message())

    def set_temperature(self, value):
    
        value = round(float(value),1)
        
        if value < 0.0:
            value = 0.0
            debug("RCU001: Set temperature cannot be below 0.0 and was changed accordingly. Please check your setting.") 
        elif value > 999.9:
            value = 999.9
            debug("RCU001: Set temperature cannot be above 999.9 and was changed accordingly. Please check your setting.")
        
        self.write_message("ts", value)
        return self.read_message()
    
    def get_output(self):
        
        self.write_message("co")
        return float(self.read_message())
     
    def set_output(self, value):
       
        value = round(float(value),1)
        
        if value < 0.0:
            value = 0.0
            debug("RCU001: Output value cannot be below 0.0 and was changed accordingly. Please check your setting.") 
        elif value > 100.0:
            value = 100.0
            debug("RCU001: Output value cannot be above 100.0 and was changed accordingly. Please check your setting.") 
        
        self.write_message("os", value)
        return self.read_message()
        
        
    def get_thickness(self):
        
        self.write_message("ft")
        return float(self.read_message())
        
    def get_rate(self):
    
        self.write_message("rf")
        return float(self.read_message())
        
    def get_crystal_life(self):
        
        self.write_message("ol")
        return float(self.read_message())

    def reset_time(self):
        
        self.write_message("zt", 1)
        return self.read_message()

    def reset_thickness(self):
        
        self.write_message("zf", 1)
        return self.read_message()

    def set_idle(self):
        
        self.write_message("cc", 1) # the manual says to send 0 but 1 works and sets idle
        return self.read_message()
    
    def set_temperature_control(self): 
    
        self.write_message("cc", 0) # the manual says to send 2 but 0 works and sets power control
        return self.read_message()
    
    def set_power_control(self):
    
        self.write_message("cc", 2) # the manual says to send 1 but 2 works and sets power control
        return self.read_message()
        
    def set_output_control(self):
    
        return self.set_power_control()

        
"""

mem min max description

tf 0 1 Temperature Sensor Status (read-only)
0: Sensor Good
1: Sensor Fail

of 0 1 Rate Monitor Status (read-only)
0: Sensor Good
1: Sensor Fail

ct 0.0 999.9 Current Temperature (readonly)
Note: This will read 999.9 when Sensor Fails

sl 0.0 999.9 Internal Temperature Setpoint (read-only)

co 0.0 100.0 Output Power (read-only)
For Power Setpoint see “os”

ru Current Rate (read-only) unfiltered by the RCU001

ft Current Film Thickness (read-only)

ol 0.00 100.00 Oscillator Life (read-only)

pt 0 356,400 Process Time in seconds (read-only)

zt 0 1 Zero Process Time
Writing a '1' to this field will reset the Process Time

zf 0 1 Zero Film Thickness
Writing a '1' to this field will reset the Film Thickness

rf 0.000 999.999 Current Rate (read-only) filtered by RCU001

rs 0.00 999.99 Rate Setpoint
When Control Mode is “Rate Control”, this is the
target Setpoint

ts 0.0 999.9 Temperature Setpoint
When Control Mode is “Temperature Control”, this
is the target Setpoint

os 0.0 100.0 Power Setpoint
When Control Mode is “Power Control”, this is the
target Setpoint

cc 0 4 The currently active Control Mode:
0: Idle
1: Power Control
2: Temperature Control
3: Rate Control
4: Autotune (read-only)
5: Startup (read-only)

Comment: Idle=1, Power=2, Temperature=3 (figured out by trial and error) 

"""