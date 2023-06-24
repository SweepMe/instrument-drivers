# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2020 Axel Fischer (sweep-me.net)
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
# Device: Linkam T95


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "T95"
        
        self.port_manager = True
        self.port_types = ["COM"]
        
        self.port_properties = { "timeout": 1,
                                 "EOL": "\r",
                                 "baudrate": 19200,
                                 "delay": 0.05,
                               }
              
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["None", "Temperature"],
                        "TemperatureUnit": ["K", "°C", "°F"],
                        "ZeroPowerAfterSweep": True,
                        "MeasureT": True,
                        "Rate": "20.0",
                        }
                       
        return GUIparameter
                   
    def get_GUIparameter(self, parameter = {}):
        # print(parameter)
                
        self.measureT = parameter["MeasureT"]
        self.reachT = parameter["ReachT"]
        #self.setT = parameter["SetT"]
        
        self.sweep_mode = parameter["SweepMode"]
        self.temperature_unit = parameter["TemperatureUnit"]
        self.rate = parameter["Rate"]
        
        self.zero_power_afterwards = parameter["ZeroPowerAfterSweep"]
        
        self.variables = ["Temperature"]
        self.units =     [self.temperature_unit]
        self.plottype =  [True] # True to plot data
        self.savetype =  [True] # True to save data
        
    
    """ semantic standard functions start here """    
        
    def initialize(self):
        temperature = self.get_temperature_C()  # the manual says that first command must be 'T' to retrieve the temperature

  
    def deinitialize(self):
        pass
        

    def configure(self):
    
        if self.rate != "":
            self.set_rate(float(self.rate))
            
    def unconfigure(self):
            
        if self.zero_power_afterwards:
        
            self.set_temperature_C(20) # let's go back to room temperature

            self.set_stop()


    def apply(self):
                
        if self.sweep_mode == "Temperature":
        
            # conversion to °C         
            if self.temperature_unit == "K":         
                self.value = float(self.value) - 273.15
            elif self.temperature_unit == "°C":
                self.value = float(self.value)
            elif self.temperature_unit == "°F":
                self.value = 5/9*(float(self.value) - 32.0)
         
            self.set_temperature_C(self.value)
            

        
    def read_result(self):
          

        answer = self.get_temperature_C()
        
        # conversion to selected temperature unit         
        if self.temperature_unit == "K":   
            try:
                self.answer = float(answer) + 273.15 # convert to float in units of K
            except:
                self.answer = float('nan') # if something fails, return a nan
        
        elif self.temperature_unit == "°C":  
            try:
                self.answer = float(answer) # convert to float in units of °C 
            except:
                self.answer = float('nan') # if something fails, return a nan
            
            
        elif self.temperature_unit == "°F":
            try:
                self.answer = (9.0/5*float(answer))+32.0  # convert to float in units of °F 
            except:
                self.answer = float('nan') # if something fails, return a nan


    def call(self):
        
        return [self.answer]
    

    
    """ button related functions start here """
    
    def measure_temperature(self):
        """ called by 'Get T' button """
    
        self.read_result()
        temperature = self.call()[0]
        
        return temperature


    """ setter/getter functions start here """
          
    
    def set_start(self):
        self.port.write("S")
        self.port.port.read()  # reads the carriage return character "\r"
        
    def set_stop(self):
        self.port.write("E")
        self.port.port.read()  # reads the carriage return character "\r"
        
    def set_hold(self):
        self.port.write("O")
        self.port.port.read()  # reads the carriage return character "\r"
        
    def set_heat(self):
        self.port.write("H")
        self.port.port.read()  # reads the carriage return character "\r"
        
    def set_cool(self):
        self.port.write("C")
        self.port.port.read()  # reads the carriage return character "\r"
        
    def get_status(self):
        
        self.port.write("SB1")
        answer = self.port.read()  # reads the carriage return character "\r"
        
        # Value Function
        # 01H Stopped
        # 10H Heating
        # 20H Cooling
        # 30H Holding at the limit or limit reached end of a ramp
        # 40H Holding the limit time
        # 50H Holding the current temperature (used in heating/cooling for quick hold)
        
        return answer
        
        
    def set_rate(self, value):
    
        digits = int(round(float(value) * 100.0, 0))  # we multiply with 100 and make sure it is an integer
        
        self.port.write("R1%i" % digits)
        self.port.port.read()  # reads the carriage return character "\r"
        
    def set_limit(self, value):
    
        digits = int(round(float(value) * 10.0, 0))  # we multiply with 10 and make sure it is an integer
        self.port.write("L1%i" % digits)
        self.port.port.read()  # reads the carriage return character "\r"
        
    def get_temperature_C(self):
        """ get the temperature in °C """
        
        ## Byte processing needed here
        
        # Byte 0 Status byte SB1 Information about what the programmer is currently doing
        # Byte 1 Error byte EB1 Indicates sources of errors in the programmer
        # Byte 2 Pump byte PB1 Current speed of the LNP Cooling Unit
        # Byte 3 Gen status GS1 Reserved for use by Linkam software
        # Byte 4 Not used
        # Byte 5 Not used
        # Byte 6 Temperature MSB
        # Byte 7 Temperature Temperature *10 sent as a signed integer ASCII hex value
        # Byte 8 Temperature
        # Byte 9 Temperature LSB
        # Byte 10 Carriage Return
        
        # To save sending the decimal point the temperature is multiplied by 10. This value is converted to a signed integer value covering the range -1960 to 15000 as F858H to 3A98H. These are then transmitted as :
        # MSB ‘F’ 46H ‘3’ 33H
        # ‘8’ 38H ‘A’ 41H
        # ‘5’ 35H ‘9’ 39H
        # LSB ‘8’ 38H ‘8’ 38H
        
        self.port.write('T') # insert command to request the current temperature to be sent
          
                
        answer_raw = self.port.port.read(11)  # we use the 'read' method of the real pyserial COM port object to get the raw bytes 
        
        temperature_bytes = answer_raw[6:10]
        
        temperature_bytes = temperature_bytes.decode('latin-1')

        temperature = int('0x'+ temperature_bytes,0)  #  0x is needed for int() to convert as hex

        if temperature > 2**15:
            temperature = temperature - 2**16
            
        temperature = temperature*0.1
            
        return temperature  # temperature was sent, multiplied by 10, and now needs to be divided by the same factor
        
        
    def set_temperature_C(self, value):

        self.set_limit(value)
        self.set_start()

    
