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
                    <p>This driver controls a Keithley switch matrix through the Keithley 4200-SCS Parameter Analyzer.
                     The commands are sent to the 4200-SCS through the Keithley External Control Interface (KXCI). The
                     driver works with Keithely 7174A, 7071, and 7072 switch matrix. Check the Keithley website for 
                     more information.</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>usage</li>
                    <li></li>
                    </ul>
                    <p>&nbsp;</p>
                """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "7x7x"
        
        self.port_manager = True
        self.port_types = ['GPIB', 'TCPIP']
        self.port_properties = {    
                                    "timeout": 10,
                                }

        self.variables = ["Channels"]
        self.units = ["#"]
        #self.plottype = [True]
        #self.savetype = [True]


    def set_GUIparameter(self):
        
        GUIparameter =  {
                        "SweepMode" : ["Channels"],
                        "Switch settling time in ms" : 20, # 4 ms switching time for the 3730 latching electromechanical relays
                        # "Closed backplane relays": "", # Comma-separated list of backplane relays to always close, e.g. 1911
                        # "Closing function": ["exclusiveclose","exclusiveslotclose"] # exclusiveclose opens all other channels in the system, exclusiveslotclose only open channels in the same slot
                        }
        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):
        self.device = parameter['Device']
        self.switch_settling_time_s = float(parameter["Switch settling time in ms"])/1000
        # self.closed_backplane_relays = parameter["Closed backplane relays"]
        self.sweepmode = parameter["SweepMode"]
        # self.closing_function = parameter["Closing function"]
        # self.sweepvalue = parameter["SweepValue"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def initialize(self):
        pass
        # Open all channels (the exlusive close on an empty string opens everything)
        # self.port.write('channel.exclusiveclose("")')
        #self.port.write("channel.reset()") # optional reset to default settings
        
    def connect(self):
        pass

    def configure(self):
        pass
                            
    def unconfigure(self):
        pass
        # Open all channels (the exlusive close on an empty string opens everything)
        # self.port.write('channel.exclusiveclose("")')

    def apply(self):
        self.value = str(self.value)
        # # Check that string contains only digits, commas, semi-colons, spaces, or letters (used with some cards)
        # if bool(re.compile(r'[^a-zA-Z0-9\,\;\:\ ]').search(self.value)):
        #     raise ValueError('Channel list contains unallowed characters. '+
        #                      'Only digits, commas, semicolons, colons, or spaces are allowed. Some cards use letters.')
        # # If the channel configuration is a comma- or semicolon-separated list, check that every element has length==4
        # if any([x in self.value for x in [',',';',':']]):
        #     if not all([len(x)==4 for x in re.split('; |, |,|;|:',self.value)]):
        #         raise ValueError('All channels must have four digits')
        # # Otherwise check that the single channel is the right length
        # else:
        #     # Strip spaces off front or back
        #     if not len(self.value.strip(' '))==4:
        #         raise ValueError('Channel must have four digits')
        #
        # # If there are backplane relays to be closed, append them to the sweep value
        # if not self.closed_backplane_relays == "":
        #     channels_to_close = self.value +  ', ' + self.closed_backplane_relays
        # else:
        #     channels_to_close = self.value
        # # Close the channel(s) of interest, as well as the specified backplane relays
        # self.port.write('channel.' + self.closing_function + '("' + channels_to_close + '")')

    def reach(self):
        pass
        # time.sleep(self.switch_settling_time_s)
        
    def call(self):
        return self.value
        
    """ here, convenience functions start """

    def set_userlib_mode(self):
        """
        This function just sets the KXCI to the user library (usrlib) mode. It needs to be sent before any other
        commands. You need to switch back to normal mode at the end of the program.
        Returns:
            None
        """
        self.port.write("UL")

    def set_normal_mode(self):
        """
        This fucntion sets the KXCI back to standard mode.
        Returns:
            None
        """
        self.port.write("US")   # "DE" also works. :)

    def open_all(self):
        """
        This function opens all the connections of the switch matrix.
        Returns:
            None
        """
        self.port.write("EX matrixulib ConnectPins(OpenAll, 1)")    # p. 1155/1510

    def connect_pin(self, dut_pin, instrument_id):
        """
        This function connect one DUT (Device Under Test) to an instrument. If everything works fine, the switch matrix
        replies with 0.
        Args:
            dut_pin: int
            instrument_id: str

        Returns:
            binary: answer
        """
        self.port.write("EX matrixulib ConnectPins(%d, %s)" % (dut_pin, instrument_id))
        answer = self.port.read()
        return answer
