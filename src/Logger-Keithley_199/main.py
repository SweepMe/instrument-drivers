# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
# * Module: Logger
# * Instrument: Keithley 199


from pysweepme.EmptyDeviceClass import EmptyDevice
import time


class Device(EmptyDevice):
    description = """<p><strong>Keithley 199 DMM driver</strong></p></p>
                     <p>5.5 digit DMM, transmits 6.5 digit resolution via GPIB that is used in SweepMe.</p></p>
                     <p>Scanner card currently not supported.</p></p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Keithley_199"

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            # needed for long integration times,
            "timeout": 10,
            # the instrument won't complain but miss commands if no delay is used
            #"delay": 0.1,
            # The Keithley 199 can and will be configured to aceppt commands with the standard CR+LF termination, but it still demands each command to be ended with the character "X" to recognize stacked commands.
            # Instead of adding an "X" to each command, the GPIB_EOL termination is defined including the "X" character
            #"GPIB_EOLwrite": "X\r\n"
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Voltage DC": "F0",
            "Voltage AC": "F1",
            "Voltage AC (db)": "F5",
            "Current DC": "F3",
            "Current AC": "F4",
            "Current AC (db)": "F6",
            "Resistance": "F2",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC": "V",
            "Voltage AC": "V",
            "Voltage AC (db)": "dbV",
            "Current DC": "A",
            "Current AC": "A",
            "Current AC (db)": "dbA",
            "Resistance": "Ohm",
        }
        
        # measuring range
        self.ranges = {
            "Auto": "R0",
            "300 mV|30 mA|300 Ohm": "R1",
            "3 V|3 A|3 kOhm": "R2",
            "30 V|3 A|30 kOhm": "R3",
            "300 V|3 A|300 kOhm": "R4",
            "300 V|3 A|3 MOhm": "R5",
            "300 V|3 A|30 MOhm": "R6",
            "300 V|3 A|300 MOhm": "R7",
        }
        
        # number of displayed digits as dictionary
        self.resolutions = {
            "5.5 digits (default)": "S1",
            "4.5 digits": "S0",
        }
        
        # filter settings
        # refer to manual for details; short version: front panel filter means fixed amount of samples for averaging, internal filter uses range and mode dependend settings
        self.filters = {
            "Off": "P0",
            "Internal Filter": "P1",
            "Front Panel Filter": "P2",
        }

    def update_gui_parameters(self, parameters):
            
        new_parameters = {
            "Mode": list(self.modes.keys()),
            "Range": list(self.ranges.keys()),
            "Resolution": list(self.resolutions.keys()),
            "Filter": list(self.filters.keys()),
            }

        return new_parameters

    def apply_gui_parameters(self, parameters):
       
        self.mode = parameters.get("Mode")
        self.range = parameters.get("Range")
        self.resolution = parameters.get("Resolution")
        self.filter = parameters.get("Filter")
        self.port_string = parameters.get("Port")

        # reset of variables required for GUI handling
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        # set variables and units depending on operation mode
        self.variables = [self.mode]
        self.units = [self.mode_units[self.mode]]

        # True to plot data
        self.plottype = [True]
        # True to save data
        self.savetype = [True]

    def initialize(self):
        
        # K0 is used to enable EOI on GPIB communication and disable the holding of the bus
        self.port.write("K2X")
        
        # defines CR+LF as terminator characters on GPIB communication
        self.port.write("Y0X")

    def configure(self):
    
        # Data output format; sets output to "no prefix", returning only the numerical value
        self.port.write("G1X")

        # Mode
        self.port.write("%sX" % self.modes[self.mode])

        # Range
        self.port.write("%sX" % self.ranges[self.range])

        # Resolution
        self.port.write("%sX" % self.resolutions[self.resolution])

        # Filter
        self.port.write("%sX" % self.filters[self.filter])
        
        # configure to "single trigger" 
        ##but do not execute ("X" missing); this prevents triggering at this point
        self.port.write("T05")

    def unconfigure(self):
        # sets the trigger back to continous trigger
        self.port.write("T0X")

    def measure(self):
        # triggers a measurement
        self.port.write("X")

        # triggers measurement and retrieves current measurement data from the instrument;
        self.data = self.port.read()

    def call(self):
        return [float(self.data)]
