# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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


# SweepMe! driver
# * Module: Switch
# * Instrument: CTS CS climate chambers


import socket
import time

from pysweepme.ErrorMessage import error, debug
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description =   """
                    <p><strong>Usage</strong></p>
                    <ul>
                    <li>Starting a run will also start the climate chamber.</li>
                    <li>Parameters like Temperature, Humidity, Compressed air are optional. If they are used, new setvalues are sent to the chamber.</li>
                    <li>The ramp rate for temperature is automatically calculated based on the new and current set value and the given hold time.</li>
                    <li>The ramp rate for humidity is set to the highest value to immediately go to the new set value.</li>
                    <li>The driver also returns a parameter "reached" that can be used to run processes with multiple steps. For example, in combination with the module "Condition" a loop can be skipped to proceed with the next step of a recipe.&nbsp;The parameter "reached" gets True if the set temperature or set humidity are reached by 2&deg;C or 2%rF, respectively.&nbsp;Furthermore, the hold time must be passed to be reached.</li>
                    <li>If you skip hold time by entering "0", "-" or nothing, the new set values for temperature and humidity will be immediately applied</li>
                    <li>Use the parameter syntax {...} to change input parameters during a run.<li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Communication</strong></p>
                    <ul>
                    <li>max. 5 TCPIP connections are allowed. The port is always&nbsp;1080 that is hardcoded in the driver. The standard IP is&nbsp;10.10.1.5&nbsp;</li>
                    <li>To use TCPIP you need a direct Ethernet connection between your PC and the climate chamber. Please use a static IP at the PC, e.g. 10.10.1.200</li>
                    <li>The driver does not support COM port communication and it can be implemented on request.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Known issues</strong></p>
                    <ul>
                    <li>Each CS climate chamber comes with a different configuration of registers so that the currently existing driver will hardly work with your chamber by plug&amp;play. We recommend to create a copy of the driver and modify the register addresses to the ones given in the programming manual that came with your chamber.</li>
                    </ul>
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "CTS CS"

        self.port_properties = {
            "timeout": 3,
            "baudrate": 19200,
            "EOL": "",
            "parity": "O",
        }

        self.STX = 0x02
        self.ADR = 0x81  # 0x81 - 0xA0 (Address 01 - 32); Default address is 01 = 0x81,
        self.ETX = 0x03   

        self.analog_channels_info = {
                            "Temperature":   {
                                            "unit": "°C",
                                            "min": -48.0,
                                            "max": 185.0,
                                        },
                              
                            "Humidity":   {
                                            "unit": "%rF",
                                            "min": 0.0,
                                            "max": 98.0,
                                        },
                                        
                            "Pt100 movable":   {
                                            "unit": "°C",
                                            "min": -48.0,
                                            "max": 185.0,
                                        },
                                        
                            "TempSupplyAir":   {
                                            "unit": "°C",
                                            "min": -48.0,
                                            "max": 185.0,
                                        },
                                        
                            "TempExhAir":   {
                                            "unit": "°C",
                                            "min": -48.0,
                                            "max": 185.0,
                                        },
                            
                            "HumidSupplAir":   {
                                            "unit": "%rF",
                                            "min": 5.0,
                                            "max": 98.0,
                                        },      

                            "HumidExhAir":   {
                                            "unit": "%rF",
                                            "min": 5.0,
                                            "max": 98.0,
                                        },    

                            "Water storage": {
                                                "unit": "l",
                                                "min": 0,
                                                "max": 15.0,
                                              },
                                              
                            "Dew point": {
                                                "unit": "°C",
                                                "min": -50.0,
                                                "max": +150.0,
                                                },
   
                            }

        """
        Wert    Kanal-Nr.   Kanäle                      Grenzen
        Ax      CID
        A0      1           Temper in [°C]              min. -48.00 [°C], max. 185.00 [°C]
        A1      2           Feuchte in [%rF]            min. 0.00 [%rF], max. 98.00 [%rF]
        A2      3           Pt100bew1 in [°C]           min. -48.00 [°C], max. 185.00 [°C]
        A3      4           TempZuluft in [°C]          min. -48.00 [°C], max. 185.00 [°C]
        A4      5           TempAbluft in [°C]          min. -48.00 [°C], max. 185.00 [°C]
        A5      6           FeuchteZul in [%rF]         min. 5.00 [%rF], max. 98.00 [%rF]
        A6      7           FeuchteAbl in [%rF]         min. 5.00 [%rF], max. 98.00 [%rF]
        A7      8           Wassergeh in [g/kg]         min. 0.00 [g/kg], max. 1200.00 [g/kg]
        A8      9           Taupunkt in [°C]            min. -50.00 [°C], max. 100.00 [°C]
        A9      10          PVerflüssigerK in [bar]     min. 0.00 [bar], max. 40.00 [bar]
        A:      11          Überh.K in [K]              min. 0.00 [K], max. 20.00 [K]
        A;      12          SaugdrK in [bar]            min. 8.00 [bar], max. 15.00 [bar]
        A<      13          t Saugd.K in [°C]           min. -100.00 [°C], max. 200.00 [°C]
        A=      14          t SiedeK in [°C]            min. -100.00 [°C], max. 200.00 [°C]
        A>      15          Überh.VK in [K]             min. 0.00 [K], max. 20.00 [K]
        A?      16          SaugdrVK in [bar]           min. 2.00 [bar], max. 6.00 [bar]
        """

        # add the command to readout the channel
        self.analog_channels_get = {
            "Temperature": "A0",
            "Humidity": "A1",
            "Pt100 movable": "A2",
            "TempSupplyAir": "A3",
            "TempExhAir": "A4",
            "HumidSupplAir": "A5",
            "HumidExhAir": "A6",
            "Water storage": "A7",
            "Dew point": "A8",
        }
                            
        self.analog_channels_set = {
            "Temperature": 0,
            "Humidity": 1,
        }

        # index is the number of the parameter, related to the command 'O'
        # 'O' is part of the returned message 
        self.digital_channels_get = {
            "Compressed air": 8,
        }

        # command as related to the command "s"
        self.digital_channels_set = {
            # "Start/Stop": "s1",
            # "Pause": "s3",
            "Compressed air": "s7",
        }
                            
        self.status_channels = {
            2: "Temperature",
            3: "Humidity",
            4: "Door closed",
            5: "Door locked",
            6: "Compressed air",
            7: "RegSupplyAir",
        }
                                
        # "Paused": answer[2] == "1",
        # "Humidity": answer[3] == "1",
        # "Door closed": answer[4] == "1",
        # "Door locked": answer[5] == "1",
        # "Compressed air": answer[6] == "1",
        # "RegZuluft": answer[7] == "1",

        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        for key in self.analog_channels_get:
            self.variables.append(key)
            self.units.append(self.analog_channels_info[key]["unit"])
            self.plottype.append(True)
            self.savetype.append(True)
        
        for key in self.digital_channels_get:
            self.variables.append(key)
            self.units.append("")
            self.plottype.append(True)
            self.savetype.append(True)

        self.variables += ["Remaining hold time", "reached"]  # define as many variables you need
        self.units += ["min", ""]  # make sure that you have as many units as you have variables
        self.plottype += [True, True]   # True to plot data, corresponding to self.variables
        self.savetype += [True, True]   # True to save data, corresponding to self.variables
               
        self._temperature_tolerance = 2.0
        self._humidity_tolerance = 2.0

    def set_GUIparameter(self):
    
        gui_parameter = {
            "SweepMode": ["None"],
            "Port": "10.10.1.5",

            "Temperature in °C": "",
            "Humidity in %rF": "",
            "Reach humidity": "",
            "Compressed air": "",
            "Hold time in min": "",
            "Reference temperature": ["Temper", "Pt100 movable"],
        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.port_string = parameter["Port"]

        self.hold_time_min = parameter["Hold time in min"]
        self.temperature_set = parameter["Temperature in °C"]
        self.humidity_set = parameter["Humidity in %rF"]
        self.reach_humidity = parameter["Reach humidity"]
        self.compressed_air_set = parameter["Compressed air"]
        
        self.reference_temperature = parameter["Reference temperature"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """
    
    def connect(self):
    
        self.comm_type = "TCPIP" 
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.port_string, 1080))  # 1080 is the standard port for the ASCII TCPIP protocol
        self.client.settimeout(3)

    def initialize(self):
        
        it =  self.get_instrument_time()
        # print("Instrument time:", it)
        
        sv = self.get_software_version()
        # print("Software version:", sv)
        
        self.set_program_number(0)  # switch off all programs

    def configure(self):
    
        self.temperature_set = str(self.temperature_set)
        self.humidity_set = str(self.humidity_set)

        self.hold_starttime = time.time()

        if self.hold_time_min == "" or self.hold_time_min == "-": 
            self.hold_time_min = 0.0
           
        self.hold_time_min = float(self.hold_time_min)
             
        self.reach_temperature = False
        
        if self.temperature_set != "" and self.temperature_set != "-":
                
            self._temperature_set_value = float(self.temperature_set)
            
            self.reach_temperature = True
            
            if self.hold_time_min > 0.0:
                # we calculate the ramp based on the current set value
                current_temperature_set = self.get_temperature_set()
                self.set_temperature_ramp_rate( (float(self.temperature_set) - current_temperature_set) / self.hold_time_min )
            else:
                self.set_temperature_ramp_rate(999.9)
            
            # we set temperature after ramp rate to take effect
            self.set_temperature(self._temperature_set_value)
                            
        else:
            self._temperature_set_value = None

        self.reach_humidity = self.reach_humidity == "1" or self.reach_humidity == "True" or self.reach_humidity is True
        
        if self.humidity_set != "" and self.humidity_set != "-":

            self._humidity_set_value = float(self.humidity_set)

            # no ramp rate adjustable ramp rate for humidity, immediately tries to reach the new value
            self.set_humidity_ramp_rate(999.9)

            # code to change humidity within the hold time to the new set value starting from the current humidity
            #if self.hold_time_min > 0.0:
            #    # we calculate the ramp based on the current set value
            #    current_humidity_set = self.get_humidity_set()
            #    self.set_humidity_ramp_rate( (float(self.humidity_set)-current_humidity_set) / self.hold_time_min )
            #else:
            #    self.set_humidity_ramp_rate(999.9)
            
            # we set humidity after ramp rate to take effect
            self.set_humidity(self._humidity_set_value)
                
        else:
            self._humidity_set_value = None
        
        if self.compressed_air_set != "" and self.compressed_air_set != "-":
            
            if self.compressed_air_set in ["On", "on", "1"]:
                self.set_compressed_air(1)
                
            elif self.compressed_air_set in ["Off", "off", "0"]:
                self.set_compressed_air(0)

        # print("Temperature set:", self.get_temperature_set())
        # print("Temperature ramp:", self.get_temperature_ramp_rates())
        
        # print("Humidity set:", self.get_humidity_set())
        # print("Humidity ramp:", self.get_humidity_ramp_rates()) 

        # print("Temperature ramp parameters:", self.get_temperature_ramp_parameters())
        # print("Humidity ramp parameters:", self.get_humidity_ramp_parameters())

    def unconfigure(self):
        pass

    def poweron(self):
        self.start_chamber()
  
    def poweroff(self):
        self.stop_chamber()
        
    def signin(self):
        pass
        # self.hold_starttime = time.time() # this is needed if two times the same step is used and configure is not called.
        # print("CTS CS driver: Hold starttime set back during signin() function.")
        
    """ the following functions are called for each measurement point """

    def measure(self):

        self.results = []
        
        for key in self.analog_channels_get:
            
            self.write_message(self.analog_channels_get[key])
            answer = self.read_message().decode('latin-1')
            vals = answer.split()
            self.results.append(float(vals[1]))
           
        # todo: change to command Aa to read all channels. However, firmware version must support this 
    
        digital_channel_values = self.get_digital_channels()
        
        for key in self.digital_channels_get:
            self.results.append(digital_channel_values[self.digital_channels_get[key]] == "1")

    def call(self):
    
        status = self.get_status()
        # print(status)

        time_to_hold = self.hold_time_min - (time.time() - self.hold_starttime)/60.0
        self.results.append(time_to_hold)

        # only if hold time larger 0, we need to check it, otherwise it is automatically reached
        reached = time_to_hold < 0.0 if self.hold_time_min > 0.0 else True
        
        if self.reach_temperature:
        
            # depending on the user selection, a different temperature sensor will be used for reaching the state
            if self.reference_temperature == "Temper":
                index = 0
            elif self.reference_temperature == "Pt100 movable":
                index = 2
        
            self._is_temperature_reached = abs(self.results[index]-self._temperature_set_value) < self._temperature_tolerance
            reached = reached and self._is_temperature_reached
                
        if self.reach_humidity:
            self._is_humidity_reached = abs(self.results[1]-self._humidity_set_value) < self._humidity_tolerance
            reached = reached and self._is_humidity_reached
            
        # we set back the hold starttime if all steps are reached. 
        # If another process step is started with the same hold time, it has to wait again even if configure was not called
        if reached:
            self.hold_starttime = time.time()
                
        self.results.append(reached)
        
        return self.results
      
    def write_message(self, cmd):
    
        if self.comm_type == "TCPIP":
            self.client.send(cmd.encode("latin-1"))
            
        elif self.commetype == "COM":
        
            # todo: COM port commuication is not implemented yet
            CHK = self.ADR | cmd | 0x80 # Checksum
        
            msg = self.STX + self.ADR + cmd + CHK + self.ETX
            self.port.write(msg)  
            self.last_cmd = cmd
            
    def read_message(self):

        if self.comm_type == "TCPIP":
            answer = self.client.recv(1024)
            # answer = self.port.read()
            return answer
            
        elif self.commetype == "COM":
        
            # todo: COM port commuication is not implemented yet
            answer = self.port.read() 
            
    def get_software_version(self):
        """ get software versions, return a list with SPS-Version, ITC-Version, and SPSNummer """
    
        self.write_message("C")
        answer = self.read_message().decode('latin-1')
        return answer[1:].split(";")
        
    def get_instrument_time(self):
        """ get the internal instrument time """
    
        self.write_message("T")
        answer = self.read_message().decode('latin-1')
        return answer
            
    def get_program_number(self):
        self.write_message("P")
        return self.read_message().decode('latin-1')
        
    def set_program_number(self, value):
        """ set a program number, use 000 to switch off any running program """
    
        self.write_message("p" + "%03d" % int(value))
        return self.read_message().decode('latin-1')
            
    def get_analog_channel(self, channel):
        """ get analog channel value """
        
        self.write_message(self.analog_channels[achannel]["cmd"])
        answer = self.read_message().decode('latin-1')
        vals = answer.split()
          
    def get_analog_channels(self):
        self.write_message("Aa")
        answer =  self.read_message().decode('latin-1')
        channels = answer[1:].split()

    def set_analog_channel(self, channel, value):
        
        """
        Befehl  Kanal-Nr.   Kanäle              Grenzen
        ax      CID
        a0      1           Temper in [°C]      min. -48.00 [°C], max. 185.00 [°C]
        a1      2           Feuchte in [%rF]    min. 0.00 [%rF], max. 98.00 [%rF]
        """
    
        self.write_message("a%i %#05.1f" % (int(channel), float(value) ) ) # command structure: ax_yyy.y
        return self.read_message().decode('latin-1')
         
    def set_temperature(self, value):
        
        answer = self.set_analog_channel(self.analog_channels_set["Temperature"], value)
        return answer

    def set_humidity(self, value):
        
        answer = self.set_analog_channel(self.analog_channels_set["Humidity"], value)
        return answer
        
    """"
    Befehl/Wert     Kanal-Nr.    Kanäle             Grenzen
    u/d/U/E/Rx      CID
    u/d/U/E/R0      1           Temper in [°C]      min. -48.00 [°C], max. 185.00 [°C]
    u/d/U/E/R1      2           Feuchte in [%rF]    min. 0.00 [%rF], max. 98.00 [%rF]
    """ 
    
    def get_temperature_set(self):
        
        self.write_message("E%i" % self.analog_channels_set["Temperature"])
        return float(self.read_message().decode('latin-1').split()[1])

    def get_temperature_ramp_parameters(self):
        """ returns a list with ramp parameters 
            
            1. Channel number
            2. two integers for ramp active and ramp control on
            3. Ramp up
            4. Ramp down
            5. Set value
        """    
         
        self.write_message("R%i" % self.analog_channels_set["Temperature"])
        return self.read_message().decode('latin-1').split()    
        
    def set_temperature_ramp_rate(self, rate):
        
        self.set_temperature_ramp_rate_cooling(rate)
        self.set_temperature_ramp_rate_heating(rate)
 
    def get_temperature_ramp_rates(self):
    
        self.write_message("U%i" % self.analog_channels_set["Temperature"])
        return self.read_message()[2:].decode('latin-1').split()
         
    def set_temperature_ramp_rate_heating(self, value):
    
        value = abs(value)
    
        if float(value) > 999.9:  # max possible value
            value = 999.9
        
        if float(value) < 0.1:
            value = 0.1

        # command structure: ux_yyy.y
        self.write_message("u%i %#05.1f" % (self.analog_channels_set["Temperature"], float(value)))
        return self.read_message().decode('latin-1')
           
    def set_temperature_ramp_rate_cooling(self, value):
    
        value = abs(value)
        
        if float(value) > 999.9:  # max possible value
            value = 999.9
            
        if float(value) < 0.1:
            value = 0.1

        # command structure: dx_yyy.y
        self.write_message("d%i %#05.1f" % (self.analog_channels_set["Temperature"], float(value)) )
        return self.read_message().decode('latin-1')
        
    def get_humidity_set(self):
        
        self.write_message("E%i" % self.analog_channels_set["Humidity"])
        return float(self.read_message().decode('latin-1').split()[1])
        
    def get_humidity_ramp_parameters(self):
        """ Returns a list with ramp parameters

            1. Channel number
            2. two integers for ramp active and ramp control on
            3. Ramp up
            4. Ramp down
            5. Set value
        """  
        
        self.write_message("R%i" % self.analog_channels_set["Humidity"])
        return self.read_message().decode('latin-1').split()
        
    def set_humidity_ramp_rate(self, rate):
        
        self.set_humidity_ramp_rate_cooling(rate)
        self.set_humidity_ramp_rate_heating(rate)    
        
    def get_humidity_ramp_rates(self):
    
        self.write_message("U%i" % self.analog_channels_set["Humidity"])
        return self.read_message()[2:].decode('latin-1').split()
        
    def set_humidity_ramp_rate_heating(self, value):
        
        value = abs(value)
        
        if float(value) > 999.9:  # max possible value
            value = 999.9
            
        if float(value) < 0.1:
            value = 0.1

        # command structure: ux_yyy.y
        self.write_message("u%i %#05.1f" % (self.analog_channels_set["Humidity"], float(value)))
        return self.read_message().decode('latin-1')
           
    def set_humidity_ramp_rate_cooling(self, value):
        
        value = abs(value)
        
        if float(value) > 999.9:  # max possible value
            value = 999.9
            
        if float(value) < 0.01:
            value = 0.01

        # command structure: dx_yyy.y
        self.write_message("d%i %#05.1f" % (self.analog_channels_set["Humidity"], float(value)))
        return self.read_message().decode('latin-1')
    
    def get_status(self):
    
        self.write_message("S")
        answer = self.read_message().decode('latin-1')[1:]
        
        response_dict = {
                        "Started": answer[0] == "1",
                        "Error": answer[1] == "1",
                        
                        "Error number": ord(answer[8]),
                        "Error message": "No error",
                        }

        # "Paused": answer[2] == "1",
        # "Humidity": answer[3] == "1",
        # "Door closed": answer[4] == "1",
        # "Door locked": answer[5] == "1",
        # "Compressed air": answer[6] == "1",
        # "RegZuluft": answer[7] == "1",                

        if response_dict["Error"]:
            # error_number = self.read_error_number()
            # print("Error number", error_number)
            error_messages = self.read_error_messages()
            print()
            print("Error messages:")
            print(error_messages)
        
        return response_dict

        """
        Pos.    Wert            Kanal-Nr.   Kanäle              Typ         Bedeutung
                                CID
        x       '0' oder '1'    -           START / STOPP       SYSTEM      Kammer EIN/AUS?
                0x30
                oder
                0x31
        y                       -           SAMMELSTÖRUNG       SYSTEM      Fehler?
        z1                      1           PAUSE bzw. Temper   Merker 1    Kammer unterbrochen?
        z2                      2           Feuchte             Merker 2    Zustand ein/aus
        z3                      3           Tür zu              Merker 3    Zustand ein/aus
        z4                      4           Türverrieg          Merker 4    Zustand ein/aus
        z5                      1           Druckluft           Softkey 1   Zustand ein/aus
        z6                      2           RegZuluft           Softkey 2   Zustand ein/aus
        w       siehe Tabelle               FEHLERNUMMER        SYSTEM
                Kapitel 4.6.4 
        """
    
    def set_digital_channel(self, cmd, state):
        """ set a digital channel with state 0 or 1"""
    
        state = int(state)

        # command structure: sx_y
        self.write_message("%s %i" % (cmd, state))
        return self.read_message().decode('latin-1')
            
    def get_digital_channels(self):
        
        self.write_message("O")
        return self.read_message().decode('latin-1')  # returns with lead 'O'
        
        """
        Befehl  Kanal-Nr.   Kanäle           Typ        Bedeutung
        sx      CID
        s1      -           START / STOPP   SYSTEM      Kammer ein-/ausschalten
        s2      -           SAMMELSTÖRUNG   SYSTEM      Fehler quittieren
        s3      1           PAUSE           Merker 1    Kammer unterbrechen
        s4      2           Feuchte         Merker 2    nicht änderbar
        s5      3           Tür zu          Merker 3    nicht änderbar
        s6      4           Türverrieg      Merker 4    nicht änderbar
        s7      1           Druckluft       Softkey 1   Softkey kann gesetzt werden!
        s8      2           RegZuluft       Softkey 2   Softkey kann gesetzt werden!
        s9      3           Dig.Ausg1       Softkey 3   Softkey kann gesetzt werden!
        s:      4           Dig.Ausg2       Softkey 4   Softkey kann gesetzt werden!
        """    
        
    def start_chamber(self):
        """ starts the automatic control """
        
        answer = self.set_digital_channel("s1", 1)
        return answer
        
    def stop_chamber(self):  
        """ stops the automatic control """
        
        answer = self.set_digital_channel("s1", 0)
        return answer
        
    def set_compressed_air(self, state):
        """ set compressed air:
            
            0 = off
            1 = on
        """
        
        state = int(state)
        
        if "Compressed air" in self.digital_channels_set:
            answer = self.set_digital_channel(self.digital_channels_set["Compressed air"], state)
            return answer
        else:
            raise Exception("Climate chamber has no digital channel for compressed air. Compressed air cannot be set.")
            
    def read_error_number(self):
        self.write_message("H01")
        answer = self.read_message().decode('latin-1').split()[1]
        return answer
        
    def read_error_messages(self):
        self.write_message("H02")
        answer = self.read_message().decode('latin-1')
        return answer
