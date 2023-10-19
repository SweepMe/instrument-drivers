# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)

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


# SweepMe! device class
# Type: Switch
# Device: Keysight B2200

from pysweepme.EmptyDeviceClass import EmptyDevice
import time
import re  # For regex / string validation


class Device(EmptyDevice):

    description = """
        <p><strong>Usage:</strong></p>
        <ul>
        <li>Enter semicolon separated configurations, e.g "11011; 12011; 13011".</li>
        <li>Open means the relay is open/disconnected. No current will flow through. Closed means the relay
         is closed/connected, and current will flow through.</li>
        <li>In the user manual (Edition 5, September 2015) page 99 you can find how channel list is 
        constructed for this instrument. One channel string consists of 5 digits. First digit is the card number,
        next two digits are input port, and last two digits are output.</li>

        </ul>
        <p>&nbsp;</p>
        <p><strong>Known issues:</strong></p>
        <p>In case SweepBox is used as Sweep value, comma-separated configurations can not be used at the 
        moment as the comma is already used by the SweepBox to split the values to be set.</p>
    """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "B2200"
        
        self.port_manager = True
        self.port_types = ['GPIB']
        self.port_properties = {    
                                    "timeout": 5,
                                    "EOL": "\r",
                                }

        self.variables = ["Channels"]
        self.units = [""]
        self.channel_delimiters = [";", ":", ","]

    def set_GUIparameter(self):
        
        gui_parameter = {
            "SweepMode": ["Channels"],
            "Switch settling time in ms": 20,
        }
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):
        self.device = parameter['Device']
        self.switch_settling_time_s = float(parameter["Switch settling time in ms"])/1000
        self.sweepmode = parameter["SweepMode"]
        self.sweepvalue = parameter["SweepValue"]

    def initialize(self):

        identification = self.get_identification()
        print("Identification:", identification)
        # self.open_all()
        self.reset_channels()

    def unconfigure(self):
        self.open_all()
        # print("Closed channels: ", self.get_closed_channels())
         
    def apply(self):
        # self.open_all()
        channels_string = str(self.value)

        # split channels for all defined delimiters and strip whitespaces, line feed, etc.
        channels_list = re.split('|'.join(self.channel_delimiters), channels_string)
        channels_list = [channel.strip() for channel in channels_list]

        # check whether the string has wrong characters. I don't check for the length of each channel, as this
        # instrument accepts channels strings without the leading zeros.
        if not all(channel.isnumeric() for channel in channels_list):
            raise ValueError("Channels list '%s' contains unallowed characters. " % str(channels_list) +
                             "Only digits, commas, semicolons, colons, or spaces are allowed.")
        # for debug reasons
        print("B2200 selected channels:", channels_list)
        self.close_channel(",".join(channels_list))

        # print("Closed channels:", self.get_closed_channels())
        # print("Closed channels:", self.check_channels(self.value))

    def reach(self):
        time.sleep(self.switch_settling_time_s)
        
    def call(self):
        return self.value
        
    """ here, convenience functions start """

    def get_identification(self):
        """
        This function gets instrument's identification string.
        Returns:
            answer: str
        """
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer

    def reset_channels(self):
        """
        This function resets the instrument.
        Returns:
            answer: str
        """
        self.port.write('*RST')

    def open_all(self):
        """
        This function opens all relays.
        Returns:
            None
        """
        self.port.write(':OPEN:CARD ALL')

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
            channels_to_open: string

        Returns:
            None
        """
        self.port.write(':OPEN (@%s)' % channels_to_open)

    def get_closed_channels(self):
        """
        This function gets closed channel list.

        Returns:
            answer: str
        """
        self.port.write(':CLOS:CARD? 0')
        answer = self.port.read()
        return answer
    
    def check_channels(self, channels):
        """
        This function closes given channel string.
        Args:
            channels: string

        Returns:
            answer: str
        """
        self.port.write(':CLOS? (@%s)' % channels)
        answer = self.port.read()
        return answer
