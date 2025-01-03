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
# * Instrument: HP 3456A


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>HP 3456A 6.5 digit ohm- and voltmeter</strong></p></p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "HP3456A"

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            "timeout": 10,  # needed for 100 NPLC
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        # 'S0' Makes sure than the SHIFT button is not pressed before requesting the function of choice whereas 'S1' virtually pressed the Shift button
        self.modes = {
            "Voltage DC": "S0 F1 Z0",
            # "Voltage DC with Auto-Zero": "F1 Z1", #Auto-Zero shorts the inputs to ground between measurements; doubles measurement time but removes zero point drift
            "Voltage AC": "S0 F2 Z0",
            # "Voltage AC with Auto-Zero": "F2 Z1",
            "Voltage AC+DC": "S0 F3 Z0",
            # "Voltage AC+DC with Auto-Zero": "F3 Z1",
            # "Current DC": "CURR:DC", #current not available on 3456A
            # "Current AC": "CURR:AC",
            "2W-Resistance": "S0 F4 Z0",
            # "2W-Resistance with Auto-Zero": "F4 Z1",
            "4W-Resistance": "S0 F5 Z0",
            # "4W-Resistance with Auto-Zero": "F5 Z1",
            "O.C. 2W-Res.": "S1 F4 Z0",
            # Offset-Compensated 2-Wire Resistance Measurement; measurement function is selected just like on the frontpanel by pressing the SHIFT key (S1 command) first
            # "O.C. 2W-Res. with Auto-Zero": "S1 F4 Z1",
            "O.C. 4W-Res.": "S1 F5 Z0",
            # Offset-Compensated 4-Wire Resistance Measurement; measurement function is selected just like on the frontpanel by pressing the SHIFT key (S1 command) first
            # "O.C. 4W-Res. with Auto-Zero": "S1 F5 Z1",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC": "V",
            # "Voltage DC with Auto-Zero": "V",
            "Voltage AC": "V",
            # "Voltage AC with Auto-Zero": "V",
            "Voltage AC+DC": "V",
            # "Voltage AC+DC with Auto-Zero": "V",
            "2W-Resistance": "Ohm",
            # "2W-Resistance with Auto-Zero": "Ohm",
            "4W-Resistance": "Ohm",
            # "4W-Resistance with Auto-Zero": "Ohm",
            "O.C. 2W-Res.": "Ohm",
            # "O.C. 2W-Res. with Auto-Zero": "Ohm",
            "O.C. 4W-Res.": "Ohm",
            # "O.C. 4W-Res. with Auto-Zero": "Ohm",
        }
        # number of displayed digits as dictionary
        self.ranges = {
            "Auto": "R1",
            "100 mV or 0.1 kOhm": "R2",
            "1 V or 1 kOhm": "R3",
            "10 V or 10 kOhm": "R4",
            "100 V or 100 kOhm": "R5",
            "1000 V or 1 MOhm": "R6",
            "10 MOhm": "R7",
            "100 MOhm": "R8",
            "1 GOhm": "R9",
        }

        # measuring range as dictionary
        self.resolutions = {
            "6 Digits (Standard)": "6STG",
            "5 Digits": "5STG",
            "4 Digits": "4STG",
            "3 Digits": "3STG",
        }

        self.nplc_types = {
            "Medium (1)": "1STI",
            "Slow (10)": "10STI",
            "Very Slow (100)": "100STI",
        }

    def set_GUIparameter(self):
        return {
            "Mode": list(self.modes.keys()),
            "Resolution": list(self.resolutions.keys()),
            "Range": list(self.ranges.keys()),
            "NPLC": list(self.nplc_types.keys()),
            "Auto-Zero": ["On", "Off"],
            "Filter": ["Off", "On"],
            "Display": ["On", "Off"],
        }

    def get_GUIparameter(self, parameter: dict):
        self.mode = parameter["Mode"]
        self.resolution = parameter["Resolution"]
        self.range = parameter["Range"]
        self.nplc = parameter["NPLC"]
        self.autozero = parameter["Auto-Zero"]
        self.filter = parameter["Filter"]
        self.display = parameter["Display"]

        self.port_string = parameter["Port"]

        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        self.variables = [self.mode]  # we add the channel name to each variable, e.g "Voltage DC"

        self.units = [self.mode_units[self.mode]]

        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

    def initialize(self):
        self.port.write("CL1")  # reset all values

    def configure(self):
        # Data Output Format
        self.port.write("P0")  # makes sure the device is set to the standard, unpacked ASCII format for data output

        # End-or-Identify Code
        self.port.write("O1")  # use the EOI mode for SCPI compatibility

        # Mode
        self.port.write("%s" % self.modes[self.mode])

        # Resolution
        if self.resolution in ["10 MOhm", "100 MOhm", "1 GOhm"] and self.mode in [
            "Voltage DC",
            "Voltage AC",
            "Voltage AC+DC",
        ]:
            msg = "Currently selected resolution is restricted to resistance measurement only"
            raise Exception(msg)
        else:
            self.port.write("%s" % self.resolutions[self.resolution])

        # Range
        self.port.write("%s" % self.ranges[self.range])

        # NPLC Integration
        self.port.write("%s" % self.nplc_types[self.nplc])

        # Auto-Zero
        if self.autozero == "On":
            self.port.write("Z1")
        else:
            self.port.write("Z0")

        # Filter
        if self.filter == "On":
            if self.mode in ["2W-Resistance", "4W-Resistance", "O.C. 2W-Res.", "O.C. 4W-Res."]:
                msg = "Filter function cannot be used in Resistance mode"
                raise Exception(msg)
            else:
                self.port.write("FL1")
        else:
            self.port.write("FL0")

        # Display
        if self.display == "Off":
            self.port.write("D0")

        # Trigger on HOLD
        self.port.write("T4")  # sets the trigger on hold to wait for a manual trigger during the 'measure' routine

    def unconfigure(self):
        if self.display == "Off":
            self.port.write("D1")  # We switch Display on again if it was switched off
        self.port.write("T1") # sets the trigger back to INTERNAL to enable the self-triggered measurements on the display again

    def measure(self):
        self.port.write("T3")  # perform single trigger for a measurement
        self.data = self.port.read()  # retrieves current measurement data from the instrument; no seperate SCPI data prepare command necessary

    def call(self):
        return [float(self.data)]
