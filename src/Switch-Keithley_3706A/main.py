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

# Contribution: We like to thank GRIP Molecular Technologies, Inc/John Myers-Bangsund, Ph.D. for providing the initial version of this driver.

# SweepMe! device class
# Type: Switch
# Device: Keithley 3706A


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
                    <li>Enter comma separated configurations, e.g "1101, 1201, 1301".</li>
                    <li>The driver will send this list to the tsp command <code>channel.exclusiveclose(channel_list)</code>, which will close the listed channels and open every channel in the system that is not included in this list. Alternatively, the list will be sent to <code>channel.exclusiveslotclose(channel_list)</code>, which will close the listed slots and open only the channels in the slots used in the channel list (a slot is one matrix card in the system). &nbsp;</li>
                    <li>The "Closing function" parameter allows the user to select between the <code>channel.exclusiveclose(channel_list)</code> and <code>channel.exclusiveslotclose(channel_list)</code> functions.&nbsp;</li>
                    <li>Set a "Switch settling time" based on the type of switch in your card, in addition to any response time of your device. For example, the 3730 card has latching electromechanical relays with a switching time of 4 ms. The 3731 card has high speed reed relays with a switching time of 1 ms.</li>
                    <li>For typical matrix cards, the channel format is: Slot#Row#Column##<br />e.g. to connect row 3 to column 2 on a card in slot 4, close channel 4302. See the card reference manual for details about your specific card.</li>
                    <li>The analog backplane relay format is: Slot# 9 Bank# Backplane Relay#<br />e.g. to connect the analog backplane 2 to a card in slot 4, close channel 4912</li>
                    <li>Only certain cards have a bank. For cards without a bank, just put 1 for the bank number.</li>
                    <li>Open means the relay is open/disconnected. No current will flow through. Closed means the relay is closed/connected, and current will flow through.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Known issues:</strong></p>
                    <p>In case SweepBox is used as Sweep value, comma-separated configurations can not be used at the moment as the comma is already used by the SweepBox to split the values to be set.</p>
                """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "K3706"
        
        self.port_manager = True
        self.port_types = ['GPIB', 'USB', 'TCPIP']
        self.port_properties = {    
                                    "timeout": 10,
                                }
        self.port_identifications = ['Keithley Instruments,37', 'Keithley Instruments Inc., Model 37']
        self.switch_settling_time_s = 0.004                   

        self.variables = ["Channels"]
        self.units = ["#"]
        #self.plottype = [True]
        #self.savetype = [True]


    def set_GUIparameter(self):
        
        GUIparameter =  {
                        "SweepMode" : ["Channels"],
                        "Switch settling time in ms" : 20, # 4 ms switching time for the 3730 latching electromechanical relays
                        "Closed backplane relays": "", # Comma-separated list of backplane relays to always close, e.g. 1911
                        "Closing function": ["exclusiveclose","exclusiveslotclose"] # exclusiveclose opens all other channels in the system, exclusiveslotclose only open channels in the same slot
                        }
        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):
        self.device = parameter['Device']
        self.switch_settling_time_s = float(parameter["Switch settling time in ms"])/1000
        self.closed_backplane_relays = parameter["Closed backplane relays"]
        self.sweepmode = parameter["SweepMode"]
        self.closing_function = parameter["Closing function"]
        # self.sweepvalue = parameter["SweepValue"]

    
    def initialize(self):
        # Open all channels (the exlusive close on an empty string opens everything)
        self.port.write('channel.exclusiveclose("")')
        #self.port.write("channel.reset()") # optional reset to default settings
        
    def connect(self):
        pass

    def configure(self):
        pass
                            
    def unconfigure(self):
        # Open all channels (the exlusive close on an empty string opens everything)
        self.port.write('channel.exclusiveclose("")')

    def apply(self):
        self.value = str(self.value)
        # Check that string contains only digits, commas, semi-colons, spaces, or letters (used with some cards)
        if bool(re.compile(r'[^a-zA-Z0-9\,\;\:\ ]').search(self.value)):
            raise ValueError('Channel list contains unallowed characters. '+
                             'Only digits, commas, semicolons, colons, or spaces are allowed. Some cards use letters.')
        # If the channel configuration is a comma- or semicolon-separated list, check that every element has length==4
        if any([x in self.value for x in [',',';',':']]):
            if not all([len(x)==4 for x in re.split('; |, |,|;|:',self.value)]):
                raise ValueError('All channels must have four digits')
        # Otherwise check that the single channel is the right length
        else:
            # Strip spaces off front or back
            if not len(self.value.strip(' '))==4:
                raise ValueError('Channel must have four digits')
            
        # If there are backplane relays to be closed, append them to the sweep value
        if not self.closed_backplane_relays == "":
            channels_to_close = self.value +  ', ' + self.closed_backplane_relays
        else:
            channels_to_close = self.value
        # Close the channel(s) of interest, as well as the specified backplane relays
        self.port.write('channel.' + self.closing_function + '("' + channels_to_close + '")')

    def reach(self):
        time.sleep(self.switch_settling_time_s)
        
    def call(self):
        return self.value
        
