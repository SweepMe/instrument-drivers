# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2021, 2024 SweepMe! GmbH (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution:
# We like to thank GRIP Molecular Technologies, Inc/John Myers-Bangsund, Ph.D.
# for providing the initial version of this driver.

# SweepMe! driver
# * Module: Switch
# * Instrument: Keithley 707B


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
        <li>Enter comma separated configurations, e.g "1101; 1201; 1301".</li>
        <li>Only certain cards have a bank. For cards without a bank, just put 1 for the bank number.</li>
        <li>Open means the relay is open/disconnected. No current will flow through. Closed means the relay is closed/connected, and current will flow through.</li>
        <li>In the user manual (707B-901-01 Rev. B / January 2015) page 152 you can find how Matrix card channel specifiers are for this instrument.</li>

        </ul>
        <p>&nbsp;</p>
        <p><strong>Known issues:</strong></p>
        <p>In case SweepBox is used as Sweep value, comma-separated configurations can not be used at the moment as the comma is already used by the SweepBox to split the values to be set.</p>
    """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Keithley 707B"
        
        self.port_manager = True
        self.port_types = ['GPIB', 'TCPIP']
        self.port_properties = {    
                                    "timeout": 5,
                                    "EOL": "\r",
                                }
        self.port_identifications = ['Keithley Instruments,707B', 'Keithley Instruments Inc., Model 707B']
        self.switch_settling_time_s = 0.004                   

        self.variables = ["Channels"]
        self.units = ["#"]
        #self.plottype = [True]
        #self.savetype = [True]

    def set_GUIparameter(self):
        
        GUIparameter = {
            "SweepMode": ["Channels"],
            "Switch settling time in ms": 20,  # 4 ms switching time for the 3730 latching electromechanical relays
        }
        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):
        self.device = parameter['Device']
        self.switch_settling_time_s = float(parameter["Switch settling time in ms"])/1000
        self.sweepmode = parameter["SweepMode"]
    
    def initialize(self):
        # print(self.get_identification())
        self.open_all()
        self.clear_errorqueue()
        self.clear_dataqueue()
        self.reset_channels()
         
    def apply(self):
        self.open_all()
        self.channels = str(self.value)
        if bool(re.compile(r'[^a-zA-Z0-9\,\;\:\ ]').search(self.channels)):
            raise ValueError('Channel list contains unallowed characters. '+
                             'Only digits, commas, semicolons, colons, or spaces are allowed. Some cards use letters.')
   
        self.exclusiveclose_channel(self.channels)   

        # print("Closed channels:", self.get_closed_channels())
        # print("Closed channels:", self.check_channels(self.value))
        
    def unconfigure(self):
        self.clear_errorqueue()
        self.clear_dataqueue()        
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
        self.port.write('channel.open("allslots")')

    def exclusiveclose_channel(self, channels_to_close):
        """
        This function closes given channel string.
        Args:
            channels_to_close: string

        Returns:
            None
        """
        self.port.write('channel.close("%s")' % channels_to_close)
    
    def open_channel(self, channels_to_open):
        """
        This function closes given channel string.
        Args:
            channels_to_close: string

        Returns:
            None
        """
        self.port.write('channel.open("%s")' % channels_to_close)

    def get_closed_channels(self):
        self.port.write('print(channel.getclose("allslots"))')
        answer = self.port.read()
        return answer
    
    def check_channels(self, channel):
        self.port.write('print(channel.getstate("%s"))' %channel)
        answer = self.port.read()
        return answer

    def reset_channels(self):
        self.port.write('channel.reset("allslots")')

    def clear_errorqueue(self):
        self.port.write("errorqueue.clear()")
        
    def clear_dataqueue(self):
        self.port.write("dataqueue.clear()")
        
    def beep(self):
        self.port.write("beeper.enable = beeper.ON")
        self.port.write("beeper.beep(2, 2400)")