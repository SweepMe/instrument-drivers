# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021-2022 SweepMe! GmbH
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
# Type: SMU
# Device: RS RSPD3303C


import time
from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
                  Negative values can be used to switch off the power supply
                  """
                  
    actions = ["set_output_off", "set_output_on"]

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "RSPD3303C"
        
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["USB"]
                                                                         
        self._is_output_on = False
        self._current_channel = None
        
        self.channels = {
                        "CH1": 1,
                        "CH2": 2,
                        }
                        
        self.output_modes = {
                            "Independent": 0,
                            "Series": 1,
                            "Parallel": 2,
                            }
          
        self.write_wait_time = 0.02
        self.read_wait_time = 0.02
                                 
    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode": ["Voltage in V", "Current in A"],
                        "Channel": list(self.channels.keys()),
                        "RouteOut": ["Front"],
                        "Compliance": 1e-3,
                        }
                        
        return gui_parameter
                                 
    def get_GUIparameter(self, parameter={}):
    
        self.port_string = parameter["Port"]
        self.sweepmode = parameter['SweepMode']
        self.protection = parameter['Compliance']

        # this line is important as voltage and currents cannot be set or get as long as the channel is unknown
        self._current_channel = self.channels[parameter["Channel"]]

    def initialize(self):
    
        identification = self.get_identification()
        print("Identification:", identification)

        # other modes are currently not available in combination with the SMU module
        self.set_output_mode("Independent")
        
    def configure(self):
            
        if self.sweepmode.startswith("Voltage"):
            self.set_voltage(0.0)
            self.set_current(float(self.protection))

        elif self.sweepmode.startswith("Current"):
            self.set_current(0.0)
            self.set_voltage(float(self.protection))

    def unconfigure(self):
          
        if self.sweepmode.startswith("Voltage"):
            self.set_voltage(0.0)

        elif self.sweepmode.startswith("Current"):
            self.set_current(0.0)

    def deinitialize(self):
        pass

    def poweron(self):
        self.set_output_on()
        
    def poweroff(self):
        self.set_output_off()

    def apply(self):
            
        if self.sweepmode.startswith("Voltage"):
            print(self.value)
            self.set_voltage(float(self.value))
        
        elif self.sweepmode.startswith("Current"):
            self.set_current(float(self.value))

    def measure(self):
        pass

    def call(self):
    
        voltage = self.get_voltage()
        current = self.get_current()

        return [voltage, current]

    """ set/get functions start here """
        
    def get_identification(self):
        
        time.sleep(self.write_wait_time)
        self.port.write("*IDN?")
        time.sleep(self.read_wait_time)
        return self.port.read()
        
    def save_state(self, name):
        """ saves the current state under name """
        
        time.sleep(self.write_wait_time)
        self.port.write("*SAV %s" % str(name))
        
    def load_state(self, name):
        """ loads the current state of name """
        
        time.sleep(self.write_wait_time)
        self.port.write("*RCL %s" % str(name))

    def set_channel(self, channel=1):
        """ sets the channel:
            1 = Channel1 (default), altenative "CH1"
            2 = Channel2 , alternative "CH2"
        """
        
        # in case channel is a string
        if channel in self.channels:
            channel = self.channels[channel]
        
        channel = int(channel)
        
        if channel not in [1, 2]:
            raise Exception("Channel number can only be 1 or 2.")
    
        time.sleep(self.write_wait_time)
        self.port.write("INST CH%i" % channel)
        
        self._current_channel = channel
        
    def get_channel(self):
        """ gets the current channel
        
            returns an integer
            
            1 = Channel1 (default)
            2 = Channel2
        """
    
        time.sleep(self.write_wait_time)
        self.port.write("INST?")
        time.sleep(self.read_wait_time)
        answer = self.port.read()  # "CH1" or "CH2"
        return self.channels[answer]

    def set_voltage(self, value):
        """ sets the voltage """
        
        if self._current_channel is None:
            raise Exception("Channel number must be defined before voltage can be set.")
        
        time.sleep(self.write_wait_time)
        self.port.write("CH%i:VOLT %1.3f" % (self._current_channel, float(value)))
        
    def get_voltage(self):
        """ gets the measured voltage """
        
        if self._current_channel is None:
            raise Exception("Channel number must be defined before voltage can be queried.")
        
        time.sleep(self.write_wait_time)        
        self.port.write("MEAS:VOLT? CH%i" % self._current_channel)
        time.sleep(self.read_wait_time)
        answer = self.port.read()
        return float(answer)
        
    def set_current(self, value):
        """ sets the current """
        
        if self._current_channel is None:
            raise Exception("Channel number must be defined before current can be set.")
        
        time.sleep(self.write_wait_time)
        self.port.write("CH%i:CURR %1.3f" % (self._current_channel, float(value)))   
        
    def get_current(self):
        """ gets the measured voltage """
        
        if self._current_channel is None:
            raise Exception("Channel number must be defined before current can be queried.")
        
        time.sleep(self.write_wait_time)
        self.port.write("MEAS:CURR? CH%i" % self._current_channel)
        time.sleep(self.read_wait_time)
        answer = self.port.read()
        return float(answer)

    def set_output_on(self):
        """ switches the output on """
        
        if self._current_channel is None:
            raise Exception("Channel number must be defined before output can be switched on.")
        
        time.sleep(self.write_wait_time)
        self.port.write("OUTP CH%i, ON" % self._current_channel)
        self._is_output_on = True
        
    def set_output_off(self):
        """ switches the output off """
        
        if self._current_channel is None:
            raise Exception("Channel number must be defined before output can be switched off.")
        
        time.sleep(self.write_wait_time)
        self.port.write("OUTP CH%i, OFF" % self._current_channel)
        self._is_output_on = False
        
    def set_output_mode(self, mode):
    
        if mode in self.output_modes:
            mode = self.output_modes[mode]
            
        mode = int(mode)
        
        time.sleep(self.write_wait_time)
        self.port.write("OUTP:TRACK %i" % mode)
        
    def get_error(self):
        """ queries the last error code and information """
    
        time.sleep(self.write_wait_time)
        self.port.write("SYST:ERR?")
        answer = self.port.read()
        return answer 
       
    def get_version(self):
        """ queries the system version """
        
        time.sleep(self.write_wait_time)
        self.port.write("SYST:VERS?")
        time.sleep(self.read_wait_time)
        answer = self.port.read()
        return answer
        
    def get_status(self):
        """ queries the status byte
        
        Bit NO.   Corresponding State
        0         0: CH1 CV mode 1: CH1 CC mode
        1         0: CH2 CV mode 1: CH2 CC mode
        2,3       01: Independent mode 10: Parallel mode 11: Series mode
        4         0: CH1 OFF 1: CH1 ON
        5         0: CH2 OFF 1: CH2 ON
        
        This function doey not yet return the value of each byte, but just the hexadecimal value
        """
        
        time.sleep(self.write_wait_time)
        self.port.write("SYST:STAT?")
        time.sleep(self.read_wait_time)
        answer = self.port.read()
        return answer

        
"""
1. *IDN? 
2. *SAV 
3. *RCL 
4. INSTrument {CH1|CH2} 
5. INSTrument ? 
6. MEASure:CURRent? 
7. MEAsure:VOLTage? 
8. [SOURce:]CURRent <current> 
9. [SOURce:]CURRent ? 
10. [SOURce:]VOLTage <volt> 
11. [SOURce:] VOLTage? 
12. OUTPut 
13. OUTPut:TRACk 
14. SYSTem:ERRor? 
15. SYSTem:VERSion?
16. SYSTem: STATus?
"""