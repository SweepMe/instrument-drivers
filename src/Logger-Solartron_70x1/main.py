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
# * Instrument: Solartron 70x1


import time

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>Driver for Solartron 70x1 series digital multimeters.</strong></p>
                     <p>Channel scanner function currently not implemented. Also "Output Fast" is not implemented as
                     its restrictions make a use in today's applications rather unlikely.</p>
                     <p>Selected combination of "Mode" and "Range" not checked for validity as this is model dependent.
                     </p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "SI70x1"

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            "timeout": 22,  # needed for 1000 NPLC; adjust if 1000 NPLC are not needed
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        # The True Ohms Mode is a resistance measurement specifically for low resistances involving thermally induced voltages
        # The Reference Voltage Modes are for maintenance only and can be activated via uncommenting if required
        self.modes = {
            "Voltage DC": "MODE VDc",
            "Voltage AC": "MODE VAc",
            "Current DC": "MODE IDc",
            "Current AC": "MODE IAc",
            "Resistance": "MODE Kohm",
            "True Ohm Resistance": "MODE Trueohm",
            # "0 V DC-Reference": "0vdc",
            # "10 V DC-Reference": "10vdc",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC": "V",
            "Voltage AC": "V",
            "Current DC": "A",
            "Current AC": "A",
            "Resistance": "Ohm",
            "True Ohm Resistance": "Ohm",
            # "0 V DC-Reference": "V",
            # "10 V DC-Reference": "V",
        }
        # measuring range as dictionary
        # range "fixed" will fix the currently selected range when the initialisation is run
        self.ranges = {
            "Auto": "RANge Auto",
            "Fixed": "RANge Fixed",
            "0.1": "RANge 0.1",
            "1": "RANge 1",
            "10": "RANge 10",
            "100": "RANge 100",
            "1000": "RANge 1000",
            "10000": "RANge 10000",
        }

        # number of displayed digits as dictionary
        # 8 digits are only available on the Solartron 7081, 7 digits only on the 7071 and 7061
        self.resolutions = {
            "8 Digits (7081)": "DIGits 8",
            "7 Digits (7071/7061)": "DIGits 7",
            "6 Digits": "DIGits 6",
            "5 Digits": "DIGits 5",
            "4 Digits": "DIGits 4",
        }

        # 0.1s will yield 5 digits and is the fastest setting overall if not using burst mode
        # 0.2s is the fastest for 6 digits and resembles classic 10 PLC@50Hz
        # 2.0s is the fastest for 7 digits and resembles classic 100 PLC@50Hz
        # 20s resembles 1000 PLC@50Hz
        self.nplc_types = {
            "Default (set by # of Digits)": "ITime Normal",
            "Fast (0.1s)": "ITime User=0000.1",
            "Normal (0.2s)": "ITime User=0000.2",
            "Slow (2.0s)": "ITime User=0002.0",
            "Very Slow (20.0s)": "ITime User=0020.0",
        }

    def set_GUIparameter(self):
        return {
            "Mode": list(self.modes.keys()),
            "Resolution": list(self.resolutions.keys()),
            "Range": list(self.ranges.keys()),
            "NPLC": list(self.nplc_types.keys()),
            "Filter": ["OFF", "ON"],
            "Drift Correction": ["ON", "OFF"],
            "Use stored NULL comp.": ["OFF", "ON"],
            "Initialize on Start": ["OFF", "ON"],
            "External Trigger": ["OFF", "ON"],
            "Ext. Trig. Edge": ["Pos", "Neg"],
            # debouncing mechanical trigger relays
            "Ext. Trig. Debounce": ["OFF", "ON"],
        }

    def get_GUIparameter(self, parameter: dict):
        self.mode = parameter["Mode"]
        self.resolution = parameter["Resolution"]
        self.range = parameter["Range"]
        self.nplc = parameter["NPLC"]
        self.drift = parameter["Drift Correction"]
        self.filter = parameter["Filter"]
        self.nullcomp = parameter["Use stored NULL comp."]
        self.initonstart = parameter["Initialize on Start"]
        self.exttrig = parameter["External Trigger"]
        self.exttrigedge = parameter["Ext. Trig. Edge"]
        self.exttrigdebo = parameter["Ext. Trig. Debounce"]

        self.port_string = parameter["Port"]

        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        self.variables = [self.mode]  # we add the channel name to each variable, e.g "Voltage DC"

        self.units = [self.mode_units[self.mode]]

        # True to plot data
        self.plottype = [True]

        # True to save data
        self.savetype = [True]

    def initialize(self):
        # Initializing the device; same as cold start
        if self.initonstart == "ON":
            self.port.write("INItialise")
            # Initialization takes some time
            time.sleep(3)

        ## Device Clear Command; similar to the initialize command but with some values being kept; refer to manual for details (Appendix A) and use if needed instead of INIT
        # self.port.write("DCl")

        ## Clears only the measurement results buffer; can also be used if needed instead of initializing the device.
        # self.port.write("History Clear")

        # make sure GPIB communication is activated
        self.port.write("GPib Output ON")

        # set EOI as command delimiter for SCPI compatibility
        self.port.write("GPib Delimit Eoi")

    def configure(self):
        # Data Output Format; using both commands will allow SweepMe to process the result as a float variable directly
        # sets output to scientific notation
        self.port.write("FOrmat Engineering")
        # forces a numeric-output only without unit and channel descriptors
        self.port.write("LIterals OFF")

        # Mode
        self.port.write("%s" % self.modes[self.mode])

        # Resolution
        self.port.write("%s" % self.resolutions[self.resolution])

        # Range
        self.port.write("%s" % self.ranges[self.range])

        # NPLC Integration
        self.port.write("%s" % self.nplc_types[self.nplc])

        # Filter
        self.port.write("FIlter %s" % self.filter)

        # Drift Correction (every 15min, first time instantly here when command is sent)
        self.port.write("DRift %s" % self.drift)

        # NULL offset compensation; value must have been stored in the instrument manually before use
        self.port.write("NUll %s" % self.nullcomp)

        # deactivate scanning channels as this is currently not supported
        self.port.write("SCan OFF")

        # Trigger usage
        # set internal trigger usage
        if self.exttrig == "OFF":
            # disable internal Auto-Trigger / "Track" in Solartron terms
            self.port.write("TRAck OFF")
            # perform a single measurement uppon trigger
            self.port.write("ONTRigger Sample=1")

    def unconfigure(self):
        # enable the auto-triggering again for updated values on the display of the instrument
        self.port.write("TRAck ON")

    def measure(self):
        if self.exttrig == "OFF":
            # perform internal trigger for a measurement
            self.port.write("TRIgger")
        else:
            # arm external trigger with chosen slope and debounce setting
            self.port.write("EXTtrig Edge %s Debounce %s" % (self.exttrigedge, self.exttrigdebo))

        # retrieves current measurement data from the instrument; in case EXT TRIG is used, it will wait for the result until timeout
        self.data = self.port.read()

    def call(self):
        return [float(self.data)]
