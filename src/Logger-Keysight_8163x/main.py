# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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
# Device: Keysight 819xxA


from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!

class Device(EmptyDevice):

    description =   """
                    Driver for a powermeter from Keysight for the 816xB family of main frames
                    
                    Usage:
                        If SweepMode is Wavelength or Power, the corresponding option will be neglected.
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Keysight 819xxA" 

        self.port_manager = True
        self.port_types = ["GPIB", "TPCIP"]
        self.port_properties = {
                                  "timeout": 5,
                                }
        
        # Probably not needed
        # self.units = {
                    # "W": "W",
                    # "dBm": "DBM,
                    # }
                    
    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        # If you use this template to create a driver for modules other than Logger or Switch, you need to use fixed keys that are defined for each module.
        
        GUIparameter = {
                        "Slot": "1",
                        "Channel": "1",
                        "Power unit": ["dBm", "W"],
                        "Averaging time in s": "0.02",
                        "Operating wavelength in nm": "1350",
                        }
        
        return GUIparameter

    def get_GUIparameter(self, parameter):
    
    
        self.sweepmode = parameter["SweepMode"]
    
        # Comment: only needed for powermeter modules
        self.channel = int(parameter["Channel"])
         
        self.sense_slot = int(parameter["Slot"])
       
        self.power_unit = parameter["Power unit"]
        
        self.variables = ["Power", "Operatingwavelength"]
        self.units = [self.power_unit, "nm"]     
        self.plottype = [True, True]
        self.savetype = [True, True]
        
        self.averaging_time = float(parameter["Averaging time in s"])
        
        self.wavelength_value = float(parameter["Operating wavelength in nm"])

    """ here, semantic standard functions start """

    def initialize(self):
    
        # identification = self.get_identification()
        # print("Identification:", identification)

        self.reset()
        self.clear_status()
        
        self.wl_min = self.get_wavelength_min()
        self.wl_max = self.get_wavelength_max()
        
        print("Wavelength range:", self.wl_min, self.wl_max)
        
        print("Error message after initialize:", self.get_error_message())
    
    def deinitialize(self):
        pass        
                
    def configure(self):
        
        self.set_autorange(1)  # autorange on
        self.set_averaging_time(self.averaging_time)
        self.set_power_unit(self.power_unit)
                
        print("Error message after configure:", self.get_error_message())
        
    def unconfigure(self):
        pass
                       
    def apply(self):
            
        pass

        # TODO: check whether we could handover wavelength also via options + reconfigure
        self.set_wavelength_calibration(self.value)
        
        print("Error message after apply:", self.get_error_message())

    def reach(self):
        # Let's make sure the wavelength is set before we continue
        self.port.write("*OPC?")  # is operation completed query
        self.port.read()
        
        
    def measure(self):
        
        self.wl_meas    = self.get_wavelength_calibration()
        self.power_meas = self.read_power()     

        print("Error message after measure:", self.get_error_message())
                  
    def call(self):  
        return [self.wl_meas, self.power_meas]
        

    """ here, convenience functions start that wrap the communication commands """
    
    def get_identification(self):
        
        self.port.write("*IDN?")
        return self.port.read()

    def reset(self):
        self.port.write("*RST")

    def clear_status(self):
        self.port.write("*CLS")
            
    def set_wavelength_calibration(self, wavelength, slot = None):
    
        if slot is None:
            slot = self.sense_slot
        
        self.port.write("SENS%i:CHAN1:POW:WAV %1.3f" % (int(slot), float(wavelength)))
        
    def get_wavelength_calibration(self, slot = None):
    
        if slot is None:
            slot = self.sense_slot
        
        self.port.write("SENS%i:CHAN1:POW:WAV?" % int(slot))
        
    def set_power_unit(self, unit, slot = None):
        
        """
        Arguments:
            unit:
                DBM
        """
        
        if slot is None:
            slot = self.sense_slot
        
        self.port.write("SENS%i:CHAN1:POW:UNIT %s" % (int(slot), str(unit).upper()))
        
    def set_averaging_time(self, average_time, slot = None):
    
        if slot is None:
            slot = self.sense_slot
    
        self.port.write("SENS%i:CHAN1:POW:ATIME %1.3f" % (int(slot), float(average_time)))
        
    def set_autorange(self, state):
        
        """
        Arguments:
            state: 
                0, "0", or False -> switches autorange off
                1, "1", or True  -> switches autorange on
        
        """
        
        if slot is None:
            slot = self.sense_slot
    
        self.port.write("SENS%i:CHAN1:POW:RANGE:AUTO %i" % (int(slot), int(state)))
    
    def read_power(self, slot = None):
        
        if slot is None:
            slot = self.sense_slot
        
        self.port.write("READ%i:CHAN1:POW?" % int(slot))
        return float(self.port.read())
    
    def fetch_power(self, slot = None):
        
        if slot is None:
            slot = self.sense_slot
        
        self.port.write("FETCH%i:CHAN1:POW?" % int(slot))
        return float(self.port.read())
        
    def get_error_message(self):
    
        self.port.write("SYST:ERR?")
        return self.port.read()
        
""" """