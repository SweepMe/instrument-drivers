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
# * Instrument: HP 3457A


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>HP 3457A 6.5 (7.5 over GPIB) DMM.</strong><br><br>
                     Notice: NPLC setting has priority and will interfere with resolution setting under certain conditions.<br><br>
                     7th digit resolution mode is implemented.</p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "HP3457A"

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            "timeout": 10,  # needed for 100 NPLC with Auto-Zero, takes some time
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Voltage DC": "DCV",
            "Voltage AC": "ACV",
            "Voltage AC+DC": "ACDCV",
            "2W-Resistance": "OHM",
            "4W-Resistance": "OHMF",
            "Current DC": "DCI",
            "Current AC": "ACI",
            "Current AC+DC": "ACDCI",
            "Frequency": "FREQ",
            "Period": "PER",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC": "V",
            "Voltage AC": "V",
            "Voltage AC+DC": "V",
            "2W-Resistance": "Ohm",
            "4W-Resistance": "Ohm",
            "Current DC": "A",
            "Current AC": "A",
            "Current AC+DC": "A",
            "Frequency": "Hz",
            "Period": "s",
        }

        # measuring range as dictionary
        # Setting manual ranges is currently not supported as the 3457A expects a floating point input with function
        # dependent maximum values which would require several checks to be implemented to prevent violations
        self.ranges = {
            "Auto": "AUTO",
        }

        # measuring resolution as dictionary; CAUTION: fast NPLC settings enforce low digit displays and will override
        # this setting. Use it only to artificially restrict the number of digits for an exchange of refresh rate at
        # certain NPLC settings
        self.resolutions = {
            "7 Digits (if NPLC set to 10 or 100)": "7",
            "6 Digits (Standard)": "6",
            "5 Digits": "5",
            "4 Digits": "4",
            "3 Digits": "3",
        }

        self.nplc_types = {
            "Fastest (0.0005)": "0.0005",
            "Very Fast (0.01)": "0.01",
            "Fast (0.1)": "0.1",
            "Medium (1)": "1",
            "Slow (10)": "10",
            "Very Slow (100)": "100",
        }

    def set_GUIparameter(self):
        return {
            "RouteOut": ["Front", "Rear"],
            "Mode": list(self.modes.keys()),
            "Resolution": list(self.resolutions.keys()),
            "Range": list(self.ranges.keys()),
            "NPLC": list(self.nplc_types.keys()),
            "Auto-Zero": ["On", "Off"],
            "Display": ["On", "Off"],
        }

    def get_GUIparameter(self, parameter: dict):
        self.route_out = parameter["RouteOut"]
        self.mode = parameter["Mode"]
        self.resolution = parameter["Resolution"]
        self.range = parameter["Range"]
        self.nplc = parameter["NPLC"]
        self.autozero = parameter["Auto-Zero"]
        self.display = parameter["Display"]

        self.port_string = parameter["Port"]

        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        self.variables = [self.mode]  # we add the channel name to each variable, e.g "Voltage DC"

        self.units = [self.mode_units[self.mode]]

        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

    def initialize(self):
        # IMPORTANT: set to use End-Or-Identify command behaviour so that it acts like a usual SCPI based GPIB device
        self.port.write("END 2")

        self.port.write("ID?")
        self.port.write("CSB")  # clearing the status registers
        self.port.write("OFORMAT ASCII")  # makes sure that output is in ASCII format

    def configure(self):
        # route-out is checked for both cases so if needed, the additional special cases "open terminal" and
        # "scanner card" can be added if required
        if self.route_out == "Front":
            self.port.write("TERM 1")  # set to front terminal input
        elif self.route_out == "Rear":
            self.port.write("TERM 2")  # set to front terminal input
        self.port.write("MFORMAT ASCII")  # memory format ascii
        self.port.write("TARM AUTO")  # automatic trigger arming
        self.port.write("NRDGS 1,AUTO")  # number of readings per trigger
        self.port.write("TRIG SGL")  # set single trigger mode

        # Mode and Range
        self.port.write("%s %s" % (self.modes[self.mode], self.ranges[self.range]))

        # Resolution
        if self.resolutions[self.resolution] == "7":  # if a 7th digit of resolution is requested:
            if self.nplc_types[self.nplc] in ("10", "100"):  # if the required amount of NPLC integration cycles is set:
                # apply command for 6 digit resolution and later retrieve the additional resolution digit out of the
                # HIRES register of the RMATH command
                self.port.write("NDIG 6")
            else:
                msg = "7 digit resolution can only be used in combination with a NPLC setting of 10 or 100."
                raise Exception(msg)
        else:
            self.port.write(
                "NDIG %s" % self.resolutions[self.resolution],
            )  # for digits requested to be between 3 and 6, just send the appropiate command

        # NPLC Integration
        self.port.write("NPLC %s" % self.nplc_types[self.nplc])  # apply the set amount of digits

        # Auto-Zero
        if self.autozero == "On":
            self.port.write("AZERO 1")
        else:
            self.port.write("AZERO 0")

        # Display
        if self.display == "Off":
            self.port.write("DISP 0")

    def unconfigure(self):
        if self.display == "Off":
            self.port.write("DISP 1")  # We switch Display on again if it was switched off

    def measure(self):
        self.port.write("?")  # questionmark triggers single measuring event
        self.data = self.port.read()  # retrieves current measurement data from the instrument

        if self.resolutions[self.resolution] == "7":  # if a 7th digit of resolution is requested:
            # request output of the value of the 7th digit; it will be already correctly scaled so that it can just be
            # added to the original 6-digit result by math addition
            self.port.write("RMATH HIRES")
            self.hiresdata = self.port.read()  # retrieve 7th digit resolution measurement value
            self.data = float(self.data) + float(self.hiresdata)  # add the 7th digit to the measurement

    def call(self):
        return [float(self.data)]
