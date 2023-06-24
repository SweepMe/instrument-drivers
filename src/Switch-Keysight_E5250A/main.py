# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023 SweepMe! GmbH
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
# Device: Keysight E5250A


# See sequencer procedure here: https://wiki.sweep-me.net/wiki/Sequencer_procedure

from collections import OrderedDict

from ErrorMessage import error

from EmptyDeviceClass import EmptyDevice
import time
import re # For regex / string validation

class Device(EmptyDevice):

    description = """
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Enter colon-separated configurations, e.g "11011: 00211: 20311".</li>
                    <li>Set a "Switch settling time" based on the type of switch in your card, in addition to any response time of your device.</li>
                    <li>Open means the relay is open/disconnected. No current will flow through. Closed means the relay is closed/connected, and current will flow through.</li>
                    <li>In the user manual (Keysight E5250A User’s Guide, Edition 12) page 106 you can find details on how channel list and channel configuration are defined
                    for this instrument. In short, the channel string has the format "niioo", where n is the card number, ii is the input port and oo is the output port, all in
                    decimal.</li>

                    </ul>

                    <p>&nbsp;</p>
                    <p><strong>Known issues:</strong></p>
                    <p>In case SweepBox is used as Sweep value, comma-separated configurations can not be used at the moment as the comma is already used by the SweepBox to split the values to be set.</p>
                """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Keysight E5250A"
        
        self.port_manager = True
        self.port_types = ['GPIB']
        self.port_properties = {    
                                    "timeout": 5,
                                    "EOL": "\n",
                                }               

        self.variables = ["Channels"]
        self.units = ["#"]
        #self.plottype = [True]
        #self.savetype = [True]


    def set_GUIparameter(self):
        
        GUIparameter =  {
                        "SweepMode" : ["Channels"],
                        "Switch settling time in ms" : 20, # 4 ms switching time for the 3730 latching electromechanical relays
                        }
        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):
        self.device = parameter['Device']
        self.switch_settling_time_s = float(parameter["Switch settling time in ms"])/1000
        self.sweepmode = parameter["SweepMode"]


    
    def initialize(self):
        print(self.get_identification())
        self.reset()
        self.open_all()
                            
    def unconfigure(self):
        self.open_all()

    def apply(self):
        self.open_all()
        self.value = str(self.value)
        
        # Check that string contains only digits, commas, semi-colons, spaces, or letters (used with some cards)
        if bool(re.compile(r'[^a-zA-Z0-9\,\;\:\ ]').search(self.value)):
            raise ValueError('Channel list contains unallowed characters. '+
                             'Only digits, commas, semicolons, colons, or spaces are allowed. Some cards use letters.')
        # If the channel configuration is a comma- or semicolon-separated list, check that every element has length==5
        if any([x in self.value for x in [',',';',':']]):
            if not all([len(x)==5 for x in re.split('; |, |,|;|:',self.value)]):
                raise ValueError('All channels must have five digits')
        # Otherwise check that the single channel is the right length
        else:
            # Strip spaces off front or back
            
            if not len(self.value.strip(' '))==5:
                raise ValueError('Channel must have five digits')
        
        if ";" in self.value:
            self.value = self.value.replace(';', ",")
        self.close_channel(self.value)

        # print("Closed channels: ", self.get_closed_channels())
    
    def unconfigure(self):
        self.open_all()
        # print("Closed channels: ", self.get_closed_channels())
    
    def reach(self):
        time.sleep(self.switch_settling_time_s)
        
    def call(self):
        return self.value
        
    """ here, convenience functions start """
    
    def get_identification(self):
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer
    
    def get_operation_complete(self):
        self.port.write("*OPC?")
        answer = self.port.read()
        return answer
    
    def open_all(self):
        """
        This function opens all relays.
        Returns:
            None
        """
        self.port.write(":OPEN:CARD ALL")

    def close_channel(self, channels_to_close):
        """
        This function closes given channel string.
        Args:
            channels_to_close: string

        Returns:
            None
        """
        self.port.write(':CLOS (@%s)' % channels_to_close)
    
    def open_channel(self, channels_to_open):
        """
        This function closes given channel string.
        Args:
            channels_to_close: string

        Returns:
            None
        """
        self.port.write(':OPEN (@%s)' % channels_to_open)

    def get_closed_channels(self):
        self.port.write(":CLOS:CARD? 1")
        answer = self.port.read()
        return answer
    
    def check_channels(self, channel):
        self.port.write(":CLOS? (@%s)" %channel)

    
    def reset(self):
        self.port.write("*RST")

        