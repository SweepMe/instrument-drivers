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
# Device: Oxford Instruments Mercury iTC


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description  = """\
                   Goto Settings and set "Remote Lock" to off.
                   For Isobus/RS-232, change "Remote Access" to 'Isobus'
                   Change the protocol below from 'Legacy' to 'SCPI' if not already done. 
                   """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Mercury iTC"
        
        self.port_manager = True
        self.port_types = ["COM", "GPIB", "TCPIP"]
        
        self.port_properties = { "timeout": 1,
                                 "EOL": "\n",
                                 "baudrate": 9600,  # 9600, 19200, 38400, 57600, 115200
                                 "stopbits": 1,
                                 "parity": "N",
                                 "delay": 0.05,
                               }
              
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["None", "Temperature", "Output in %"],
                        "TemperatureUnit": ["K", "°C", "°F"],
                        "ZeroPowerAfterSweep": True,
                        "MeasureT": True,
                        # "Rate": "20.0",
                        }
                       
        return GUIparameter
                   
    def get_GUIparameter(self, parameter = {}):
        # print(parameter)
                
        self.measureT = parameter["MeasureT"]
        self.reachT = parameter["ReachT"]
        #self.setT = parameter["SetT"]
        
        self.sweep_mode = parameter["SweepMode"]
        self.temperature_unit = parameter["TemperatureUnit"]
        # self.rate = parameter["Rate"]
        
        self.zero_power_afterwards = parameter["ZeroPowerAfterSweep"]
        
        self.variables = ["Temperature", "Power"]
        self.units =     [self.temperature_unit, "W"]
        self.plottype =  [True, True] # True to plot data
        self.savetype =  [True, True] # True to save data
        
    
    """ semantic standard functions start here """    
        
    def connect(self):
    
        # self.port.write("SET:SYS:RST")
       
        self.port.write("*IDN?")
        identification = self.port.read()
        # print("Identification:", identification)

        self.port.write("READ:SYS:CAT")
        catalogue = self.port.read()

        ## typical response: STAT:SYS:CAT:DEV:MB0.H1:HTR:DEV:MB1.T1:TEMP
        
        boards = catalogue.split(":DEV:")[1:]  # first element is "STAT:SYS:CAT" which is kicked out, the rest are the boards
        
        for board in boards:
            
            if board.startswith("MB"):  # a ma
                
                if board.endswith("HTR"):  # we have a heater
                    self.board_heater = board
                    
                elif board.endswith("TEMP"):  # we have a temperature sensor
                    self.board_temp = board
                    
                elif board.endswith("AUX"):  # we have an external controller
                    self.board_aux = board
                
                else:
                    pass # other types are not supported yet, but maybe there anyway no other types
            
            elif board.startswith("DB"):  # a daughter board    
                pass  # not handled yet, and can be added later
              

    def initialize(self):
        
        self.port.write("SET:SYS:LOCK:SOFT") # options: OFF:SOFT:ON
        self.port.read()
   
        # self.power_max = self.get_power_max()
        # print("PMAX:", self.power_max)
        # print("RES:", self.get_heater_resistance())
        # print("VLIM:", self.get_heater_voltage_limit())
  
    def deinitialize(self):
    
        self.port.write("SET:SYS:LOCK:OFF") # options: OFF:SOFT:ON
        self.port.read()
        

    def configure(self):

        # enable or disable ramp
        # self.port.write("SET:DEV:MB1.T1:TEMP:LOOP:RENA:OFF")

        # if self.rate != "":
            # todo: set rate
            
        if self.sweep_mode == "Temperature":
            self.enable_loop()
            # print("Temperature loop enabled")
        elif self.sweep_mode == "Output in %":
            self.disable_loop()
        else: # None
            pass
            
            # self.disable_loop()
            # self.set_heater_loop(0)
            
            
        # self.set_power(1)
            
    def unconfigure(self):
    
        if self.zero_power_afterwards:
            self.disable_loop()
            self.set_heater_loop(0)
            
        else:
            pass
            # Comment: at the moment it will stay at the last temperature after the sweep

    def apply(self):
                
        if self.sweep_mode == "Temperature":
        
            self.value = float(self.value)

            if self.temperature_unit == "K":         
                pass
            elif self.temperature_unit == "°C":
                self.value = float(self.value) + 273.15
            elif self.temperature_unit == "°F":
                self.value = 5/9*(float(self.value + 273.15) - 32.0)
         
         
            self.set_temperature_loop(self.value)
         
            # self.set_temperature(self.value)
            
            
        elif self.sweep_mode == "Output in %":
        
            self.set_heater_loop(self.value)
            
            # self.set_power(self.value)

        
    def read_result(self):
          

        answer = self.get_temperature()
        
        # conversion to selected temperature unit         
        if self.temperature_unit == "K":   
            self.answer = float(answer) # convert to float in units of K

        elif self.temperature_unit == "°C":  
            self.answer = float(answer) - 273.15 # convert to float in units of °C 
   
        elif self.temperature_unit == "°F":
            self.answer = (9.0/5*(float(answer) - 273.15))+32.0  # convert to float in units of °F 

        self.output_power = self.get_power()

    def call(self):
        
        return [self.answer, self.output_power]
    

    
    """ button related functions start here """
    
    def measure_temperature(self):
        """ called by 'Get T' button """
    
        self.read_result()
        temperature = self.call()[0]
        
        return temperature


    """ setter/getter functions start here """
          
    def enable_ramp_rate(self):

        self.port.write("SET:DEV:%s:LOOP:RENA:ON" % (self.board_temp)) 
        ret = self.port.read()
        
    def disable_ramp_rate(self):

        self.port.write("SET:DEV:%s:LOOP:RENA:OFF" % (self.board_temp))
        ret = self.port.read()
        
    def set_ramp_rate(self, value):

        self.port.write("SET:DEV:%s:LOOP:RSET:%1.2f" % (self.board_temp, float(value))) # in K / min
        ret = self.port.read()
        

    def get_temperature(self):
        """ get the temperature in K """
        
        self.port.write("READ:DEV:%s:SIG:TEMP" % (self.board_temp))
        ret = self.port.read()
        index = ret.rfind(":")
        temperature = float(ret[index+1:-1])
          
        return temperature  # temperature was sent, multiplied by 10, and now needs to be divided by the same factor
        
        
    def set_temperature(self, value):
        """ set the temperature in K """
    
        self.port.write("SET:DEV:%s:TSET:%1.4f" % (self.board_temp, float(value)))
        ret = self.port.read()
        
    def set_heater_loop(self, value):
        """ set the heater power in % """
    
        self.port.write("SET:DEV:%s:LOOP:HSET:%1.4f" % (self.board_temp, float(value)))
        ret = self.port.read()

    def set_temperature_loop(self, value):
        """ set the temperature in K """
    
        self.port.write("SET:DEV:%s:LOOP:TSET:%1.4f" % (self.board_temp, float(value)))
        ret = self.port.read()
        
    def enable_loop(self):
        """ enable heater loop """
    
        self.port.write("SET:DEV:%s:LOOP:ENAB:ON" % (self.board_temp))
        ret = self.port.read()
    
    def disable_loop(self):
        """ enable heater loop """
    
        self.port.write("SET:DEV:%s:LOOP:ENAB:OFF" % (self.board_temp))
        ret = self.port.read()
    
        
    def set_power(self, value):
    
        self.port.write("SET:DEV:%s:SIG:POWR:%1.4f" % (self.board_heater, float(value)))
        ret = self.port.read()
        
    def get_power(self):

        self.port.write("READ:DEV:%s:SIG:POWR" % (self.board_heater))
        ret = self.port.read()
        index = ret.rfind(":")
        power = ret[index+1:]
        
        if power == "N/A":
            return float('nan')
        else:
            return float(power[:-1])


    def get_power_max(self):

        self.port.write("READ:DEV:%s:PMAX" % (self.board_heater))
        ret = self.port.read()
        index = ret.rfind(":")
        value = ret[index+1:]
        
        if value == "N/A":
            return float('nan')
        else:
            return float(value[:-1])
    
    def set_power_max(self, value):
    
        self.port.write("SET:DEV:%s:PMAX:%1.4f" % (self.board_heater, float(value)))
        ret = self.port.read()
        
        
    def get_heater_resistance(self):

        self.port.write("READ:DEV:%s:RES" % (self.board_heater))
        ret = self.port.read()
        index = ret.rfind(":")
        value = ret[index+1:]
        
        if value == "N/A":
            return float('nan')
        else:
            return float(value)
    
    def set_heater_resistance(self, value):
    
        self.port.write("SET:DEV:%s:RES:%1.4f" % (self.board_heater, float(value)))
        ret = self.port.read()
        
        
    def get_heater_voltage_limit(self):

        self.port.write("READ:DEV:%s:VLIM" % (self.board_heater))
        ret = self.port.read()
        index = ret.rfind(":")
        value = ret[index+1:]
        
        if value == "N/A":
            return float('nan')
        else:
            return float(value)
    
    def set_heater_voltage_limit(self, value):
    
        self.port.write("SET:DEV:%s:VLIM:%1.4f" % (self.board_heater, float(value)))
        ret = self.port.read()
        
    def calibrate_heater(self):
        """ calibrates the hardware of the heater board """
    
        self.port.write("SET:DEV:%s:CAL" % (self.board_heater))
        ret = self.port.read()
    