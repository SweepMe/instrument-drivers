# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022-2023 SweepMe! GmbH (sweep-me.net)
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
# Type: Switch
# Device: Keysight N77xxA

import numpy as np

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):

    description = """
    <p><strong>Usage:</strong></p>
    <ul>
    <li>Add one module per channel that you like to use.</li>
    <li>To change the operating wavelength, use the parameter syntax {...} and handover the value from another module.</li>
    </ul>  
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "N774x"
        
        self.port_manager = True 
           
        self.port_types = ["GPIB", "TCPIP"]
        
        self.port_properties = {
            "timeout": 5,
        }

        # conversion dictionary between user selection and programming command units
        self.power_units = {
            "dBm": "DBM",  # default
            "W": "Watt",
            "mW": "Watt"
            # "µW": "UW",
            # "mW": "MW",
            # "nW": "NW",
            # "pW": "PW",
        }

        # conversion dictionary between user selection and programming command units
        self.wavelength_units = {
            "nm": "NM",
            "µm": "UM",
            "mm": "MM",
            "m": "M",
            "pm": "PM",
        }

        # conversion dictionary between user selection of wavelength units and conversion factors to m
        self.wavelength_conversion = {
            "nm": 1e-9,
            "µm": 1e-6,
            "mm": 1e-3,
            "m": 1e0,
            "pm": 1e-12,
        }

        self._wavelength_calibration = float('nan')
            
    def set_GUIparameter(self):
    
        gui_parameter = {
            "Channel": ["%i" % i for i in range(1, 5)],
            "Power unit": list(self.power_units.keys()),
            "Wavelength unit": list(self.wavelength_units.keys()),
            "Operating wavelength": "1500",
            "Range": ["Auto"],
            "Averaging time in s": "0.02",
            "Auto gain": ["As is", "On", "Off"],  # only newer models have this feature
        }

        return gui_parameter

    def get_GUIparameter(self, parameter):
    
        self.channel = int(parameter["Channel"])

        self.power_unit = parameter["Power unit"]
        self.wavelength_unit = parameter["Wavelength unit"]

        self.variables = ["Power", "Operating wavelength"]
        self.units = [self.power_unit, self.wavelength_unit]
        self.plottype = [True, True]
        self.savetype = [True, True]
        
        self.wavelength_value = float(parameter["Operating wavelength"])
        self.range_value = parameter["Range"] 
        self.averaging_time_s = float(parameter["Averaging time in s"])
        self.autogain_value = parameter["Auto gain"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def initialize(self):

        identification = self.get_identification()
        # print("Identification:", identification)

        self.reset()

    def deinitialize(self):
        pass
        
    def reconfigure(self, parameters, keys):
    
        # print("N77xxA reconfigure:", keys)
        
        if "Operating wavelength" in keys:
            value = float(parameters["Operating wavelength"])
            # print("N77xxA new operating wavelength:", value)
            self.set_wavelength_calibration(value, self.wavelength_units[self.wavelength_unit])
                
        else:
            self.get_GUIparameter(parameters)
            self.configure()
                
    def configure(self):

        self.set_power_reference_state(0)  # absolute power reference state
        # print("Power reference state N77xxA:", self.get_power_reference_state())

        # all results are returned without any offset or reference relation
        self.set_power_reference(0.0, "Watt")
        # print("Power reference N77xxA:", self.get_power_reference())

        self.set_power_unit(self.power_units[self.power_unit])

        # print("Power unit N77xxA", self.get_power_unit())

        # Operating wavelength
        self.set_wavelength_calibration(self.wavelength_value, self.wavelength_units[self.wavelength_unit])
        
        # Range
        if self.range_value == "Auto":
            self.set_autorange(True)
        else:
            self.set_autorange(False)
            self.set_range(self.range_value)
        
        # Averaging time
        self.set_averaging_time(self.averaging_time_s)
        
        # Auto gain
        if self.autogain_value == "On":
            self.set_autogain(True)
        elif self.autogain_value == "Off":
            self.set_autogain(False)
        
        # Trigger
        self.set_trigger_continuous(False)

    def unconfigure(self):
        self.set_trigger_continuous(True)            

    def measure(self):
        self.power_value = self.read_power()  # this value is in Watt independent from the set power unit, unclear why

        if self.power_unit == "mW":
            self.power_value = self.power_value*1000.0
            
    def call(self):
        return [self.power_value, self._wavelength_calibration]

    """ here, convenience functions start """

    @staticmethod
    def convert_W_to_dBm(power):
    
        return 10*np.log10(power*1e3)

    """ here, functions start that wrap communication commands """

    def get_identification(self):
        
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer

    def get_options(self):

        self.port.write("*OPT?")
        answer = self.port.read()
        return answer

    def reset(self):
        self.port.write("*RST")

    def read_power(self, channel=None):
        """
        This functions always returns Watt so far in absolute mode
        It is unclear why
        """
    
        if channel is None:
            channel = self.channel
        
        self.port.write(":READ%i:POW?" % int(channel))
        answer = self.port.read()
        return float(answer)
        
    def fetch_power(self, channel=None):
        
        if channel is None:
            channel = self.channel
        
        self.port.write(":FETCH%i:POW?" % int(channel))
        answer = self.port.read()
        return float(answer)
       
    def get_power_unit(self, channel=None):
    
        if channel is None:
            channel = self.channel
        
        self.port.write(":SENS%i:POW:UNIT?" % int(channel))
        
        answer = self.port.read()
        # print(answer)
        if answer == "+0":
            return "dBm"
        elif answer == "+1":
            return "W"

    def set_power_unit(self, unit, channel=None):

        """

        Args:
            unit: 0 or DBM
                  1 or Watt
            channel:

        Returns:

        """
    
        if channel is None:
            channel = self.channel

        if str(unit).upper() == "DBM":
            unit = "DBM"
            # unit = 0

        elif str(unit).upper() == "W" or str(unit).upper() == "WATT":
            unit = "WATT"
            # unit = 1

        self.port.write(":SENS%i:POW:UNIT %s" % (int(channel), str(unit)))
        # self.port.write(":SENS%i:POW:UNIT %i" % (int(channel), int(unit)))

    def get_power_reference_state(self, channel=None):
        """

        Args:
            channel:

        Returns:
            int: power reference state
                0 -> absolute
                1 -> relative
        """

        if channel is None:
            channel = self.channel

        self.port.write(":SENS%i:POW:REF:STAT?" % int(channel))
        return int(self.port.read())

    def set_power_reference_state(self, state, channel=None):
        """

        Args:
            state: OFF (0) absolute or ON (1) relative
            channel:

        Returns:
            None
        """

        if channel is None:
            channel = self.channel

        if state == "ON":
            state = 1
        elif state == "OFF":
            state = 0

        self.port.write(":SENS%i:POW:REF:STAT %i" % (int(channel), int(state)))

    def get_power_reference(self, channel=None):

        if channel is None:
            channel = self.channel

        self.port.write(":SENS%i:POW:REF? TOREF" % (int(channel)))
        return float(self.port.read())

    def set_power_reference(self, value, unit, channel=None):

        if channel is None:
            channel = self.channel

        self.port.write(":SENS%i:POW:REF TOREF,%1.3f%s" % (int(channel), float(value), str(unit)))

    def get_wavelength_calibration(self, channel=None):

        """
        Args:
            channel:

        Returns:
            Wavelength in m
        """
        
        if channel is None:
            channel = self.channel

        self.port.write(":SENS%i:POW:WAV?" % int(channel))
        return float(self.port.read())

    def set_wavelength_calibration(self, wavelength, unit, channel=None):
        
        if channel is None:
            channel = self.channel

        self._wavelength_calibration = float(wavelength)
        self.port.write(":SENS%i:POW:WAV %1.3f%s" % (int(channel), self._wavelength_calibration, str(unit).upper()))
        
    def get_autorange(self, channel=None):
    
        if channel is None:
            channel = self.channel
        
        self.port.write(":SENS%i:POW:RANG:AUTO?" % int(channel))
        answer = self.port.read()
        
        return int(answer)
        
    def set_autorange(self, state, channel=None):
    
        if channel is None:
            channel = self.channel
    
        self.port.write(":SENS%i:POW:RANG:AUTO %i" % (int(channel), int(state)))
        
    def get_range(self, channel=None):
        
        if channel is None:
            channel = self.channel
            
        self.port.write(":SENS%i:POW:RANG?" % int(channel))
        
    def set_range(self, measure_range, channel=None):
        
        if channel is None:
            channel = self.channel
            
        self.port.write(":SENS%i:POW:RANG %1.3e" % (int(channel), float(measure_range)))
        
    def get_averaging_time(self, channel=None):
    
        if channel is None:
            channel = self.channel
        
        self.port.write(":SENS%i:POW:ATIME?" % int(channel))
        answer = self.port.read()
        return float(answer)

    def set_averaging_time(self, averaging_time, channel=None):
        """

        Args:
            averaging_time: Float of time in seconds
            channel: Integer of the channel number

        Returns:

        """
    
        if channel is None:
            channel = self.channel
        
        self.port.write(":SENS%i:POW:ATIME %1.3f" % (int(channel), float(averaging_time)))
             
    def get_trigger_continuous(self, channel=None):
    
        if channel is None:
            channel = self.channel
    
        self.port.write(":INIT%i:CONT?" % int(channel))
        answer = self.port.read()
        if answer == "ON":
            return True
        elif answer == "OFF":
            return False
   
    def set_trigger_continuous(self, state, channel=None):
    
        if channel is None:
            channel = self.channel
    
        if state:
            self.port.write(":INIT%i:CONT ON" % int(channel))
        else:
            self.port.write(":INIT%i:CONT OFF" % int(channel))
            
    def trigger_immediate(self, channel=None):
    
        if channel is None:
            channel = self.channel
        
        self.port.write(":INIT%i:IMM" % int(channel))
        
    def get_autogain(self, channel=None):
        
        if channel is None:
            channel = self.channel
        
        self.port.write(":SENS%i:POW:GAIN:AUTO?" % int(channel))
        answer = self.port.read()
        
        if "0" in answer:
            return False
        elif "1" in answer:
            return True
        else:
            raise Exception("Response ('%s') to 'get_autogain' cannot be processed." % answer)
           
    def set_autogain(self, state, channel=None):
        
        if channel is None:
            channel = self.channel

        if bool(state):
            self.port.write(":SENS%i:POW:GAIN:AUTO 1" % int(channel))
        else:
            self.port.write(":SENS%i:POW:GAIN:AUTO 0" % int(channel))
            
    def get_error_message(self):
    
        self.port.write("SYST:ERR?")
        return self.port.read()

    