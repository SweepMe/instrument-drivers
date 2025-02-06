# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Keysight 34401A


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>Keysight 34401A</strong></p>
                     <p>DMM: Digital Multimeter</p>
                     <p>&nbsp;</p>
                     <p>The 34401A is a 6.5 digit DMM that supports measurement of voltage, current, resistance and 
                     frequency.</p>
                     <p>Two-wire as well as four-wire measurements are possible.</p>
                     <p>Temperature measurement was special order option and while there are ways to enable it, this 
                     driver does not currently support it.</p>
                    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Keysight34401A"

        self.port_manager = True
        self.port_types = ["COM", "GPIB"]

        self.port_properties = {
            "timeout": 10,  # needed for 100 NPLC setting as it needs ~5s to compute
            "EOL": "\r",
            "baudrate": 9600,  # factory default
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Voltage DC": "VOLT:DC",
            "Voltage AC": "VOLT:AC",
            "Current DC": "CURR:DC",
            "Current AC": "CURR:AC",
            "2W-Resistance": "RES",
            "4W-Resistance": "FRES",
            "Frequency": "FREQ",
            "Period": "PER",
            "Diode": "DIOD",
            "Continuity": "CONT",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC": "V",
            "Voltage AC": "V",
            "Current DC": "A",
            "Current AC": "A",
            "2W-Resistance": "Ohm",
            "4W-Resistance": "Ohm",
            "Frequency": "Hz",
            "Period": "s",
            "Diode": "",
            "Continuity": "",
        }

        # a list of available resolutions as they can be sent to the instrument
        # Currently not used, remains here in case this functionality is added later
        self.resolutions = [
            "0.1",  # i.e., 100.0 V (3½ digits)
            "0.01",  # i.e., 10.00 V (3½ digits)
            "0.001",  # i.e., 1.000 V (3½ digits)
            "0.0001",  # i.e., 1.0000 V (4½ digits)
            "0.00001",  # i.e., 1.00000 V (5½ digits)
            "0.000001",  # i.e., 1.000000 V (6½ digits)
        ]

        # A dictionary of trigger types and their corresponding commands.
        # The trigger types would be shown in the GUI field 'Trigger'
        # Currently not used, remains here in case this functionality is added later
        self.trigger_types = {
            "Immediate": "IMM",
            # "Timer":     "TIM",
            # "Manual":    "MAN",
            "Internal": "BUS",
            # "External":  "EXT",
        }

        self.nplc_types = {
            "Very Fast (0.01)": 0.01,
            "Fast (0.1)": 0.1,
            "Medium (1.0)": 1.0,
            "Slow (10.0)": 10.0,
            "Very slow (100.0)": 100.0,
        }

    def set_GUIparameter(self):

        GUIparameter = {
            "Mode": list(self.modes.keys()),
            "NPLC": list(self.nplc_types.keys()),
            "Range": ["Auto"],
            "Display": ["On", "Off"],
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):

        self.mode = parameter['Mode']
        self.range = parameter['Range']
        self.nplc = parameter['NPLC']
        self.display = parameter['Display']

        self.port_string = parameter["Port"]

        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        # we add the channel name to each variable, e.g "Voltage DC"
        self.variables = [self.mode]
        self.units = [self.mode_units[self.mode]]

        # True to plot data
        self.plottype = [True]
        
        # True to save data
        self.savetype = [True]

    def initialize(self):
        # once at the beginning of the initialization; disabled so manual settings on instrument can be used
        # self.port.write("*RST")

        # reset all registers
        self.port.write("*CLS")

        # control-Beep off
        self.port.write("SYST:BEEP:STAT OFF")

    def deinitialize(self):

        # control-Beep on
        self.port.write("SYST:BEEP:STAT ON")

    def configure(self):

        # Mode
        self.port.write(":SENS:FUNC \"%s\"" % self.modes[self.mode])

        # Speed
        if self.mode not in ["Voltage AC", "Current AC", "Frequency", "Period", "Diode", "Continuity"]:
            # NPLC only supported in DC Volts, DC Current, 2W- and 4W-Resistance
            self.port.write(":SENS:%s:NPLC %s" % (self.modes[self.mode], self.nplc_types[self.nplc]))

        # Range
        # setting RANGE to AUTO if in a mode of operation that supports it
        if self.mode not in ["Frequency", "Period", "Continuity", "Diode"]:
            self.port.write(":SENS:%s:RANG:AUTO ON" % (self.modes[self.mode]))

        # Display
        if self.display == "Off":
            self.port.write(":DISP 0")

    def unconfigure(self):
        if self.display == "Off":
            # We switch Display on again if it was switched off
            self.port.write(":DISP 1")
            
    def measure(self):
        # triggers a new measurement
        self.port.write("READ?")

    def call(self):
        # here we read the response from the "READ?" request in 'measure'
        answer = self.port.read()
        return [float(answer)]
