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
# Device: Keysight 815xxA

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):

    description = """
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Keysight 815xxA"  # short name will be shown in the sequencer
        self.variables = ["Attenuation"]  # define as many variables you need
        self.units = ["dB"]  # make sure that you have as many units as you have variables
        self.plottype = [True]  # True to plot data, corresponding to self.variables
        self.savetype = [True]  # True to save data, corresponding to self.variables

        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP"]
        self.port_properties = {
                                  "timeout": 5,
                                }

        self._last_attenuation = float('nan')

    def set_GUIparameter(self):
    
        gui_parameter = {
                        "SweepMode": ["None", "Attenuation in dB"],
                        "Channel": ["1", "2"],
                        "Slot": "1",
                        "Attenuation in dB": "0",
                        }
        
        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.sweepmode = parameter["SweepMode"]
        self.input_slot = parameter["Slot"]
        self.attenuation = float(parameter["Attenuation in dB"])
        self.channel = int(parameter["Channel"])

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """
        
    def initialize(self):

        # identification = self.get_identification()
        # print("Identification:", identification)

        self.reset()
        
    def deinitialize(self):
        pass

    def configure(self):
        if self.sweepmode == "None":
            self.set_attenuation(self.attenuation)

    def unconfigure(self):
        pass

    def apply(self):
        self.set_attenuation(self.value)
                        
    def measure(self):
        pass
                  
    def call(self):  
        return [self._last_attenuation]

    """ here, python functions start that wrap the SCPI communication commands """

    def get_identification(self):
        
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer

    def reset(self):
        self.port.write("*RST")
        
    def set_attenuation(self, value, channel=None, slot=None):
        """ set the attenuation in dB """
        
        if slot is None:
            slot = self.input_slot

        if channel is None:
            channel = self.channel

        self._last_attenuation = float(value)
        self.port.write("INP%i:CHAN%i:ATT %1.3fdB" % (int(slot), int(channel), self._last_attenuation))

    def get_attenuation(self, channel=None, slot=None):
        """ get the attenuation in dB """
        
        if slot is None:
            slot = self.input_slot

        if channel is None:
            channel = self.channel
    
        self.port.write("INP%i:CHAN%i:ATT?" % (int(slot), int(channel)))
        return float(self.port.read())

    def set_offset(self, value, channel=None, slot=None):
        """ set the offset in dB """
        
        if slot is None:
            slot = self.input_slot

        if channel is None:
            channel = self.channel
        
        self.port.write(":INP%i:CHAN%i:OFFS %1.3fdB" % (int(slot), int(channel), float(value)))
        
    def get_offset(self, channel=None, slot=None):
        """ get the offset in dB """
        
        if slot is None:
            slot = self.input_slot

        if channel is None:
            channel = self.channel
        
        self.port.write(":INP%i:CHAN%i:OFFS?" % (int(slot), int(channel)))
        return float(self.port.read())
        
    def set_wavelength(self, value, channel=None, slot=None):
        """ set the operating wavelength """ 
        
        if slot is None:
            slot = self.input_slot

        if channel is None:
            channel = self.channel
        
        self.port.write(":INP%i:CHAN%i:WAV %1.3e" % (int(slot), int(channel), float(value)))
        
    def get_wavelength(self, channel=None, slot=None):
        """ get the operating wavelength """
        
        if slot is None:
            slot = self.input_slot

        if channel is None:
            channel = self.channel
        
        self.port.write(":INP%i:CHAN%i:WAV?" % (int(slot), int(channel)))
        return float(self.port.read())
        
    def get_error_message(self):
    
        self.port.write("SYST:ERR?")
        return self.port.read()
        