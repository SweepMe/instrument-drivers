# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018, 2020 - 2021 Axel Fischer (sweep-me.net)
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
# Device: BelektroniG HAT control


from EmptyDeviceClass import EmptyDevice
import time
import struct
import sys

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "HAT Control"
       
                
        self.port_manager = True
        self.port_types = ["COM"]
        
        self.port_properties = { "timeout": 1,
                                 "EOL": "\r",
                                 "baudrate": 9600,
                                 "delay": 0.05,
                               }
              
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["None", "Temperature", "Output in %"],
                        "TemperatureUnit": ["K", "°C", "°F"],
                        "ZeroPowerAfterSweep": True,
                        "MeasureT": False,
                        }
                       
        return GUIparameter
                   
    def get_GUIparameter(self, parameter = {}):
        # print(parameter)
                
        self.measureT = parameter["MeasureT"]
        self.reachT = parameter["ReachT"]
        #self.setT = parameter["SetT"]
        
        self.sweep_mode = parameter["SweepMode"]
        self.temperature_unit = parameter["TemperatureUnit"]
        
        self.zero_power_afterwards = parameter["ZeroPowerAfterSweep"]
        
        if self.measureT or not self.sweep_mode == "Temperature":
            self.variables = ["Temperature"]
        else:
            self.variables = ["Temperature, set"]
        self.units =     [self.temperature_unit]
        self.plottype =  [True] # True to plot data
        self.savetype =  [True] # True to save data
        
    
    """ semantic standard functions start here """    
        
    def initialize(self):
   
        pass
        # self.get_mode()
        
        
        """
        Copy this device class to CustomDevices
        Then modify this section to read and write PID parameters
        """
        
        ## setting PID parameters
        # self.set_P(0.6)  # in V/°C
        # self.set_I(10)   # in s
        # self.set_D(10)   # in s
        
        ## readting PID parameters
        # print("P:", self.get_P())
        # print("I:", self.get_I())
        # print("D:", self.get_D())
        
        
    def deinitialize(self):
        pass
        

    def configure(self):
        
        if self.sweep_mode == "Temperature":
            self.set_mode(3)  # 3 = heat and cool
        elif self.sweep_mode == "Output in %":
            self.set_mode(0)  # 0 = read only, also needed to control output directly
        else:
            pass # This is needed for the "Get T" button as this function will set the sweep mode to None to indicate that mode should stay as is.
            
    def unconfigure(self):
            
        if self.zero_power_afterwards:
        
            self.set_temperature_C(20) # let's go back to room temperature

            self.set_mode(0)  # 0 = read only, must be sent before output is changed to 0
            self.set_output(0)
            # self.get_mode()
    
        
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
            
        elif self.sweep_mode == "Output in %":
            self.set_output(float(self.value))
                                  
    def request_result(self):   

        if self.measureT:
            self.port.write('T1') # insert command to request the current temperature to be sent
        
    def read_result(self):
    
        if self.measureT or not self.sweep_mode == "Temperature":
            answer = self.port.read().replace(" ", "")
            answer = answer.rstrip('\x00') # removing those \x00 that can occasionally appear
            answer = answer.replace(' ', '') # removing whitespaces
        
                    
        else:
            answer = self.value # if no measurement is needed 
        
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
                self.answer = (9.0/5*float(answer)) + 32.0  # convert to float in units of °F 
            except:
                self.answer = float('nan') # if something fails, return a nan
        
        
    def call(self):
        return [self.answer]
    

    
    """ button related functions start here """
    def measure_temperature(self):
    
        self.port.write('T1') # insert command to request the current temperature to be sent
        
        answer = self.port.read().replace(" ", "")
        answer = answer.rstrip('\x00') # removing those \x00 that can occasionally appear
        answer = answer.replace(' ', '') # removing whitespaces
    
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
                self.answer = (9.0/5*float(answer)) + 32.0  # convert to float in units of °F 
            except:
                self.answer = float('nan') # if something fails, return a nan

        return self.answer


    """ setter/getter functions start here """
    
    def get_model(self):
        """ get the model name of the instrument """
        
        self.port.write('N1')
        return self.port.read()
        
    def get_serialnumber(self):
        """ get the serial number of the instrument """
        
        self.port.write('N2')
        return self.port.read()

    def get_mode(self):
        """ returns the cooling/heating mode as integer """
        
        # 0 = read only, 1 = heat only, 2 = cool only, 3 = heat and cool
        
        self.port.write('B1') 
        return self.port.read(1)
        
    def set_mode(self, mode):
        """ set the cooling/heating mode for a given integer """
        
        # 0 = read only, 1 = heat only, 2 = cool only, 3 = heat and cool
        
        self.port.write('b1%i' % int(mode))
        
        
    def get_temperature_C(self):
        """ get the temperature in °C """
        
        self.port.write('T1') # insert command to request the current temperature to be sent
        
        answer = self.port.read().replace(" ", "")
        answer = answer.rstrip('\x00') # removing those \x00 that can occasionally appear
        answer = answer.replace(' ', '') # removing whitespaces
    
        return float(answer)
        
    def set_temperature_C(self, value):

        command = "s9"  # set temperature without writing to EEPROM
    
        msg = ''.join( [ chr(ord(x)) for x in command ] )

        if value < 0:
            self.port.write( msg.encode("utf-8") + struct.pack('I', 2**32 + int(value*1000))[::-1] )
        else:
            self.port.write( msg.encode("utf-8") + struct.pack('I', int(value*1000))[::-1] )

        # the instrument needs some time to set the new value   
        time.sleep(0.5)

    def get_output(self):
    
        self.port.write('A1') 
        answer = self.port.read()
        # print(len(answer))
        
        first = ord(answer[0])
        second  = ord(answer[1])
        third  = ord(answer[2])
        
        if first == 0 and second == 0:
            result = third/256* 100.0
        else:
            result = (third - 256) / 256 * 100.0
    
        return round(result,1)
    
    def set_output(self, value):
        """ set output in range -100 ... +100 % """
        
        if value > 100:
            value = 100
            
        elif value < -100:
            value = -100
            
        value = int(value* 2**16/100)
 
        command = "a1"
        
        msg = ''.join( [ chr(ord(x)) for x in command ] )
 
        if value < 0:
            self.port.write( msg.encode("utf-8") + struct.pack('I', 2**32 + value)[::-1] )
        else:
            self.port.write( msg.encode("utf-8") + struct.pack('I', value)[::-1] )
                   
        
    def get_P(self):
        """ get a value in V / °C """
        
        self.port.write('P1')
        P = self.port.read(3)
        # print(ord(P[0]), ord(P[1]))
        return round((ord(P[0])*256 + ord(P[1])) * 0.1, 1) # conversion into V/°C

    def set_P(self, value):
        """ set a value in V/°C """
        
        
        ## example: setting "p1" with "0.6 V/°C is "\x70\x31\x00\x06"
        
        if value > 10 or value < 0:
            raise Exception("P parameter must be within 0 .... 10 V/°C")

        value = int(10 * value) # conversion to the number that must be sent to the instrument      
        
        command = "p1" # command to set the P parameter
        
        msg = ""
        
        msg = ''.join( [ chr(ord(x)) for x in command ] )
            
        last_byte = value%256
        first_byte = int((value - last_byte) / 256)
        
        msg += chr(first_byte)
        msg += chr(last_byte)
       
        # print("p1", msg.encode("utf-8"))
        self.port.write(msg.encode("utf-8")) # as it is a number in 0...100, only the last byte is used
        
        
    def get_I(self):
        """ returns a time in seconds """
    
        self.port.write('I1')
        I = self.port.read(3)
        # print(ord(I[0]), ord(I[1]))
        return ord(I[0])*256 + ord(I[1])
            
            
    def set_I(self, value):
    
        ## example: setting "i1" with "10s" is "\x69\x31\x00\x0a"
        
        if value > 65535 or value < 0:
            raise Exception("P parameter must be within 0…65535s")
        
        command = "i1" # command to set the P parameter
        
        msg = ""
        
        msg = ''.join( [ chr(ord(x)) for x in command ] )
       
        last_byte = value%256
        first_byte = int((value - last_byte) / 256)
        
        msg += chr(first_byte)
        msg += chr(last_byte)
       

        # print("i1", msg)
        self.port.write(msg.encode("utf-8")) # as it is a number in 0...100, only the last byte is used
         
    def get_D(self):
        """ returns a time in seconds """
        
        self.port.write('D1')
        D = self.port.read(3)
        # print(ord(D[0]), ord(D[1]))
        return ord(D[0])*256 + ord(D[1])
        
        
    def set_D(self, value):
    
        ## example: setting "d1" with "10s" is "\x64\x31\x00\x0a"
        
        if value > 65535 or value < 0:
            raise Exception("P parameter must be within 0…65535s")
        
        command = "d1" # command to set the P parameter
        
        msg = ""
        
        msg = ''.join( [ chr(ord(x)) for x in command ] )
            
        last_byte = value%256
        first_byte = int((value - last_byte) / 256)
        
        msg += chr(first_byte)
        msg += chr(last_byte)
       
        # print("d1", msg)
        self.port.write(msg.encode("utf-8")) # as it is a number in 0...100, only the last byte is used