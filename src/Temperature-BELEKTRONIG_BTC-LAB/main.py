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
# Device: BELECTRONIG BTC-LAB


from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "BTC"
       
                
        self.port_manager = True
        self.port_types = ["COM"]
        
        self.port_properties = { "timeout": 1,
                                 "EOL": "\r",
                                 "baudrate": 9600,
                                 "delay": 0.001, # a 1 ms delay between sending two commands already helps to get a proper response
                               }
                               
        self._is_connected = False                         
        
              
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["None", "Temperature", "Temperature, heat-only", "Output in %", "Voltage in V"],
                        "TemperatureUnit": ["°C", "K", "°F"],
                        "ZeroPowerAfterSweep": True,
                        "IdleTemperature": "",
                        # "MeasureT": False,
                       }
                       
        return GUIparameter
                   
    def get_GUIparameter(self, parameter = {}):
                
        self.sweep_mode = parameter["SweepMode"]
        self.temperature_unit = parameter["TemperatureUnit"]
        
        self.zero_power_afterwards = parameter["ZeroPowerAfterSweep"]
        
        if "IdleTemperature" in parameter:
            self.idle_temperature = parameter["IdleTemperature"]
        else:
            self.idle_temperature = None
            debug("To support all functions of the BELEKTRONIG BTC-LAB driver, please update to the latest version of the Temperature module.")
          
        self.variables = ["Temperature", "Output"]            
        self.units     = [self.temperature_unit, "%"]
        self.plottype  = [True, True] # True to plot data
        self.savetype  = [True, True] # True to save data
        
    
    """ semantic standard functions start here """    
    
    def connect(self):
        
        self._primary_sensor = self.get_primary_sensor() # must be in 'connect' as it is used by get_temperature_C

        self._output_min, self._output_max = self.get_output_limits() # must be in 'connect' as it is used by set_output
        
        self._voltage_max = self.get_rated_voltage()
        
        self._is_connected = True


    def initialize(self):
   
        dc = self.get_device_configuration()
        if not "BTC" in dc:
            self.stop_measurement("You are not connected to a BelektroniG BTC. Please check the COM port.")
            return False
   
        sn = self.get_serial_number()
        # print(sn)
        
        fw = self.get_firmware_version()
        # print(fw)
        
        df = self.get_device_features()
        # print(df)
        
        # self.get_mode()
        
        
        """
        Copy this device class to CustomDevices
        Then modify this section to read and write PID parameters
        or use the python package pysweepme to use the functions to set PID parameters in your own script
        """
        
        ## reading PID parameters
        # print("P heat:", self.get_P_heating())
        # print("I heat:", self.get_I_heating())
        # print("D heat:", self.get_D_heating())
        # print()
        # print("P cool:", self.get_P_cooling())
        # print("I cool:", self.get_I_cooling())
        # print("D cool:", self.get_D_cooling())
        
        
        ## writing PID parameters
        # self.set_P_heating(6.0)  # in V/°C
        # self.set_I_heating(0.1)   # in V/(s°C)
        # self.set_D_heating(0.0)   # in Vs/°C
        
        # self.set_P_cooling(9.0)  # in V/°C
        # self.set_I_cooling(0.15)   # in V/(s°C)
        # self.set_D_cooling(0.0)   # in Vs/°C
        
    def deinitialize(self):
        pass
        

    def configure(self):
        pass
        
        if self.sweep_mode == "Temperature":
            self.set_mode(3)  # 3 = heat and cool
        elif self.sweep_mode == "Temperature, cool-only": # not available as sweepmode but for completeness
            self.set_mode(2)  # 2 = heat_only
        elif self.sweep_mode == "Temperature, heat-only":
            self.set_mode(1)  # 1 = heat_only
        elif self.sweep_mode == "Output in %" or self.sweep_mode == "Voltage in V":
            self.set_mode(0)  # 0 = read only, also needed to control output directly
        else:
            pass # This is needed for the "Get T" button as this function will set the sweep mode to None to indicate that mode should stay as is.
            
    def unconfigure(self):
            
        if self.zero_power_afterwards:
        
            if self.idle_temperature is None:
                self.set_setpoint_temperature_C(20) # let's go back to room temperature

            self.set_mode(0)  # 0 = read only, must be sent before output is changed to 0
            self.set_output(0)
            # self.get_mode()
    
        if self.idle_temperature != "" and not self.idle_temperature is None:
                    
            if self.temperature_unit == "K":         
                self.set_setpoint_temperature_K(float(self.idle_temperature))
            elif self.temperature_unit == "°C":
                self.set_setpoint_temperature_C(float(self.idle_temperature))
            elif self.temperature_unit == "°F":
                self.set_setpoint_temperature_F(float(self.idle_temperature))
        
    def apply(self):
                
        if self.sweep_mode.startswith("Temperature"):
        
            # conversion to °C         
            if self.temperature_unit == "K":         
                self.set_setpoint_temperature_K(float(self.value))
            elif self.temperature_unit == "°C":
                self.set_setpoint_temperature_C(float(self.value))
            elif self.temperature_unit == "°F":
                self.set_setpoint_temperature_F(float(self.value))
         
        elif self.sweep_mode == "Output in %":
            self.set_output(float(self.value))
          
        elif self.sweep_mode == "Voltage in V":
            self.set_voltage(float(self.value))
               
    
    def measure(self):
                
        # requesting temperature of the primary sensor
        self.port.write('T' + str(self._primary_sensor)) 

    def read_result(self):
    
        self.temperature_value = float('nan')
        
        ## Reading the temperature of the primary sensor
        answer = self.port.read_raw(4)
        answer = int.from_bytes(answer, "big", signed = True) / 1000.0
        
        # conversion to selected temperature unit         
        if self.temperature_unit == "K":   
            self.temperature_value = float(answer) + 273.15 # convert to float in units of K

        elif self.temperature_unit == "°C":  
            self.temperature_value = float(answer) # convert to float in units of °C 

        elif self.temperature_unit == "°F":
            self.temperature_value = (9.0/5*float(answer)) + 32.0  # convert to float in units of °F 
        
        # requesting output value    
        self.port.write('A1') 
           
        # reading output value        
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        self.output_value = value / (2**16-1) * 100        

        
    def call(self):
        return [self.temperature_value, self.output_value]
    

    
    """ button related functions start here """
    def measure_temperature(self):
        """ this function is used by 'reach'-functionality to check the current temperature """
    
        T = float('nan')
    
        # conversion to selected temperature unit         
        if self.temperature_unit == "K":   
            T = self.get_temperature_K()
        elif self.temperature_unit == "°C":  
            T = self.get_temperature_C()
        elif self.temperature_unit == "°F":
            T = self.get_temperature_F()

        return T


    """ setter/getter functions start here """
    
    def get_device_configuration(self):
        """ get the device configuration of the instrument """
        
        self.port.write('N1')
        return self.port.read()
        
    def get_serial_number(self):
        """ get the serial number of the instrument """
        
        self.port.write('N2')
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big")
        # print(value)
        return value
      
    def get_firmware_version(self):
        """ get the firmware version of the instrument """
        
        self.port.write('N3')
        answer = self.port.read_raw(4)
        value  = int.from_bytes(answer, "big")
        # print(value)
        return value
       
    def get_device_features(self):
        """ get the device features of the instrument """
        
        self.port.write('N5')
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big")
        bit_string = "{0:32b}".format(value)
        bit_list = [x == "1" for x in bit_string][::-1]
        return bit_list

    def get_mode(self):
        """ returns the cooling/heating mode as integer 
        
            0 = read only
            1 = heat only
            2 = cool only
            3 = heat and cool
        
        """
        
        self.port.write('B1') 
        return self.port.read(1)
        
    def set_mode(self, mode):
        """ set the cooling/heating mode for a given integer 
        
            0 = read only
            1 = heat only
            2 = cool only
            3 = heat and cool
        
        """
        mode = int(mode)

        mode_byte = mode.to_bytes(1, "big")
        self.port.write('b1' + mode_byte.decode('latin-1'))
        self.port.read_raw(1)
        

        
    def get_output_limits(self):
        """ get the output limits for min and max in % """

        self.port.write('G8') 
        
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        min = value / (2**16-1) * 100
        
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        max = value / (2**16-1) * 100

        return min, max

    def set_output_limits(self, min, max):
        """ set min and max value of output limits in % """
        
        if min > 0.0:
            raise ValueError("Output limit minimum must be equal or lower than 0%")
            
        if max < 0.0:
            raise ValueError("Output limit maximum must be equal or higher than 0%")
            
        if abs(min) > 100.0:
            raise ValueError("Output limit minimum exceeds 100%.")
            
        if abs(max) > 100.0:
            raise ValueError("Output limit maximum exceeds 100%.")


        value_min = int(min/100*(2**16-1))    
        value_min_bytes = value_min.to_bytes(4, "big", signed = True) 
        
        value_max = int(max/100*(2**16-1))    
        value_max_bytes = value_max.to_bytes(4, "big", signed = True) 
        
        self.port.write("g8" + value_min_bytes.decode("latin-1") +  value_max_bytes.decode('latin-1'))
        self.port.read_raw(1)
        
        # reading back the new output limits
        self._output_min, self._output_max = self.get_output_limits()

               
    def get_voltage_limits(self):

        if not self._is_connected:
            self.connect()

        self.port.write('G8') 
        
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        min = value / (2**16-1) * self._voltage_max
        
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        max = value / (2**16-1) * self._voltage_max

        return min, max
        
    def set_voltage_limits(self, min, max):
        """ set min and max value of voltage limits in V """
        
        if not self._is_connected:
            self.connect()
        
        if min > 0.0:
            raise ValueError("Voltage limit minimum must be equal or lower than 0%")
            
        if max < 0.0:
            raise ValueError("Voltage limit maximum must be equal or higher than 0%")

        if abs(min) > self._voltage_max:
            raise ValueError("Voltage limit minimum exceeds maximum rated voltage.")
            
        if abs(max) > self._voltage_max:
            raise ValueError("Voltage limit maximum exceeds maximum rated voltage.")

        value_min = int(min/self._voltage_max*(2**16-1))    
        value_min_bytes = value_min.to_bytes(4, "big", signed = True) 
        
        value_max = int(max/self._voltage_max*(2**16-1))    
        value_max_bytes = value_max.to_bytes(4, "big", signed = True) 
        
        self.port.write("g8" + value_min_bytes.decode("latin-1") +  value_max_bytes.decode('latin-1'))
        self.port.read_raw(1)
        
        # reading back the new output limits
        self._output_min, self._output_max = self.get_output_limits()

        
    def get_primary_sensor(self):
    
        self.port.write("R7")
        answer = self.port.read_raw(1)
        value = int.from_bytes(answer, "big")
        # print("Primary sensor", value)
        return value
        
    def set_primary_sensor(self, sensor):
    
        sensor_byte = sensor.to_bytes(1, "big")
        self.port.write('r7' + sensor_byte.decode('latin-1'))
        self.port.read_raw(1)
    
        # reading back the primary sensor to make it available to other functions
        self._primary_sensor = self.get_primary_sensor()
        
    def get_temperature(self, sensor = 0):
        """ get the temperature in °C """
        
        if not self._is_connected:
            self.connect()
        
        if sensor == 0:
            sensor = self._primary_sensor
        
        self.port.write('T' + str(sensor)) # insert command to request the current temperature to be sent
        
        answer = self.port.read_raw(4)
        # print("T" + str(sensor)"+ ":", answer)
        value = int.from_bytes(answer, "big", signed = True) / 1000
           
        return value
        
    def get_temperature_C(self, sensor = 0):
        """ get the temperature in °C """
        
        value = self.get_temperature(sensor)
           
        return value
        
    def get_temperature_K(self, sensor = 0):
        """ get the temperature in K """
        
        value = self.get_temperature(sensor) + 273.15
           
        return value
        
    def get_temperature_F(self, sensor = 0):
        """ get the temperature in °F """
        
        value = 9.0/5*self.get_temperature(sensor) + 32.0 
           
        return value    
        
    def get_setpoint_temperature(self):
        """ get the setpoint temperature in °C """
        
        self.port.write('S1')
        
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True) / 1000
        
        return value
        
    def get_setpoint_temperature_C(self, sensor = 0):
        """ get the setpoint temperature in °C """
        
        value = self.get_setpoint_temperature(sensor)
           
        return value
        
    def get_setpoint_temperature_K(self, sensor = 0):
        """ get the setpoint temperature in K """
        
        value = self.get_setpoint_temperature(sensor) + 273.15
           
        return value
        
    def get_setpoint_temperature_F(self, sensor = 0):
        """ get the setpoint temperature in °F """
        
        value = 9.0/5*self.get_setpoint_temperature(sensor) + 32.0 
           
        return value    
        
    def set_temperature(self, value):
        """ set the setpoint temperature in °C."""
         
        value = int(float(value) * 1000)  
        value_bytes = value.to_bytes(4, "big", signed = True)   
        self.port.write("s2" + value_bytes.decode("latin-1")) #  The value is not written to the non-volatile memory and will be lost after the next restart of the controller.    
        self.port.read_raw(1)
        
    def set_temperature_C(self, value):
        """ set the setpoint temperature in °C """
            
        self.set_temperature(value)    
       
    def set_temperature_K(self, value):
        """ set the setpoint temperature in K """
            
        self.set_temperature(value-273.15) 
        
    def set_temperature_F(self, value):
        """ set the setpoint temperature in °F """
            
        self.set_temperature(5/9*(value - 32.0)) 
        
    def set_setpoint_temperature(self, value):
        """ set the setpoint temperature in °C """
            
        self.set_temperature(value) 
        
    def set_setpoint_temperature_C(self, value):
        """ set the setpoint temperature in °C """
            
        self.set_setpoint_temperature(value)    
       
    def set_setpoint_temperature_K(self, value):
        """ set the setpoint temperature in K """
            
        self.set_setpoint_temperature(value-273.15) 
        
    def set_setpoint_temperature_F(self, value):
        """ set the setpoint temperature in °F """
            
        self.set_setpoint_temperature(5/9*(value - 32.0)) 
      
    def get_setpoint_temperature_permanent(self):
        """ get the permanent setpoint temperature in °C """
        
        self.port.write('S1')
        
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True) / 1000
        
        return value  
      
    def get_setpoint_temperature_actual(self):
        """ get the actual setpoint temperature in °C """
        
        self.port.write('S2')
        
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True) / 1000
        
        return value
        
    def get_setpoint_temperature_actual_C(self, sensor = 0):
        """ get the actual setpoint temperature in °C """
        
        value = get_setpoint_temperature_actual(sensor)
           
        return value
        
    def get_setpoint_temperature_actual_K(self, sensor = 0):
        """ get the actual setpoint temperature in K """
        
        value = get_setpoint_temperature_actual(sensor) + 273.15
           
        return value
        
    def get_setpoint_temperature_actual_F(self, sensor = 0):
        """ get the actual setpoint temperature in °F """
        
        value = 9.0/5*get_setpoint_temperature_actual(sensor) + 32.0 
           
        return value    

    def get_output(self):
    
        self.port.write('A1') 
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        value = value / (2**16-1) * 100

        return value
    
    def set_output(self, value):
        """ set output in range -100 ... +100 % """
        
        value = float(value)
        
        if value > 100:
            value = 100
            
        elif value < -100:
            value = -100
            
        if not self._is_connected:
            self.connect()
            
        if value > self._output_max:
            debug("Belektronig BTC: Requested output level (%1.1f) exceeds output max limit (%1.1f)." % (value, self._output_max))
            value = self._output_max

        elif value < self._output_min:
            debug("Belektronig BTC: Requested output level (%1.1f) exceeds output min limit (%1.1f)." % (value, self._output_min))
            value = self._output_min
         
        value = int(value*(2**16-1)/100)  # mapping to 2**16-1
            
        value_bytes = value.to_bytes(4, "big", signed = True)  
        self.port.write("a1" + value_bytes.decode("latin-1"))
        self.port.read_raw(1)
        
    def get_voltage(self):
        """ set voltage in V """
        
        if not self._is_connected:
            self.connect()
        
        self.port.write('A1') 
        answer = self.port.read_raw(4)
        
        value = int.from_bytes(answer, "big", signed = True)
        
        value = value / (2**16-1) * self._voltage_max

        return value
    
    def set_voltage(self, value):
        """ set voltage """
        
        value = float(value)
        
        if not self._is_connected:
            self.connect()
        
        if value > self._voltage_max:
            value = self._voltage_max
            
        elif value < -self._voltage_max:
            value = -self._voltage_max
            
        if value > self._output_max/100*self._voltage_max:
            debug("Belektronig BTC: Requested output level (%1.1f) exceeds output max limit (%1.1f)." % (value, self._output_max/100*self._voltage_max))
            value = self._output_max

        elif value < self._output_min/100*self._voltage_max:
            debug("Belektronig BTC: Requested output level (%1.1f) exceeds output min limit (%1.1f)." % (value, self._output_min/100*self._voltage_max))
            value = self._output_min
            
        value = int(value*(2**16-1)/self._voltage_max)  # mapping to 2**16-1
            
        value_bytes = value.to_bytes(4, "big", signed = True)
        # print("Output bytes:", value_bytes)    
        self.port.write("a1" + value_bytes.decode("latin-1"))
        self.port.read_raw(1)
        
    def get_rated_voltage(self):
        
        self.port.write('U1')
        answer = self.port.read_raw(2)
        value = int.from_bytes(answer, "big", signed = True)
        value = round(value/10.0,0) # conversion into V/°C
        
        return value
        
                   
    def get_P_heating(self):
        """ get a value in V / °C for heating """
        
        self.port.write('P1')
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        value = round(value/1000.0,3) # conversion into V/°C

        return value 
        
    def get_P_cooling(self):
        """ get a value in V / °C for cooling """
        
        self.port.write('P2')
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        value = round(value/1000.0,3) # conversion into V/°C

        return value 

    def set_P_heating(self, value):
        """ set a value in V/°C for heating """
        
        value = int(float(value) * 1000)
            
        value_bytes = value.to_bytes(4, "big", signed = True)    
        self.port.write("p1" + value_bytes.decode("latin-1"))
        self.port.read_raw(1)
        
    def set_P_cooling(self, value):
        """ set a value in V/°C for cooling """
        
        value = int(float(value) * 1000)
            
        value_bytes = value.to_bytes(4, "big", signed = True)  
        self.port.write("p2" + value_bytes.decode("latin-1"))
        self.port.read_raw(1)
        
        
    def get_I_heating(self):
        """ get a value in V/(s°C) for heating """
        
        self.port.write('I1')
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        value = round(value/1000.0,3) # conversion into V/°C

        return value
        
    def get_I_cooling(self):
        """ get a value in V / °C for cooling """
        
        self.port.write('I2')
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        value = round(value/1000.0,3) # conversion into V/°C

        return value 
        
    def set_I_heating(self, value):
        """ set a value in V/(s°C) for heating """
        
        value = int(float(value) * 1000)
            
        value_bytes = value.to_bytes(4, "big", signed = True)    
        self.port.write("i1" + value_bytes.decode("latin-1"))
        self.port.read_raw(1)
        
    def set_I_cooling(self, value):
        """ set a value in V/(s°C) for cooling """
        
        value = int(float(value) * 1000)
            
        value_bytes = value.to_bytes(4, "big", signed = True)  
        self.port.write("i2" + value_bytes.decode("latin-1"))
        self.port.read_raw(1)

         
    def get_D_heating(self):
        """ get a value in Vs/°C for heating """
        
        self.port.write('D1')
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        value = round(value/1000.0,3) # conversion into V/°C

        return value   

    def get_D_cooling(self):
        """ get a value in V / °C for cooling """
        
        self.port.write('D2')
        answer = self.port.read_raw(4)
        value = int.from_bytes(answer, "big", signed = True)
        value = round(value/1000.0,3) # conversion into V/°C

        return value 

    def set_D_heating(self, value):
        """ set a value in Vs/°C for heating """
        
        value = int(float(value) * 1000)
            
        value_bytes = value.to_bytes(4, "big", signed = True)    
        self.port.write("d1" + value_bytes.decode("latin-1"))
        self.port.read_raw(1)
        
    def set_D_cooling(self, value):
        """ set a value in Vs/°C for cooling """
        
        value = int(float(value) * 1000)
            
        value_bytes = value.to_bytes(4, "big", signed = True)  
        self.port.write("d2" + value_bytes.decode("latin-1"))
        self.port.read_raw(1)        

""" """
