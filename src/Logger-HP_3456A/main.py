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
            # needed for 100 NPLC
            "timeout": 10,
        }

        # This dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'.
        # 'S0' Makes sure than the SHIFT button is not pressed before requesting the function of choice whereas 'S1' virtually presses the SHIFT button
        self.modes = {
            "Voltage DC": "S0 F1 Z0",
            "Voltage AC": "S0 F2 Z0",
            "Voltage AC+DC": "S0 F3 Z0",
            "2W-Resistance": "S0 F4 Z0",
            "4W-Resistance": "S0 F5 Z0",
            "O.C. 2W-Res.": "S1 F4 Z0",
            "O.C. 4W-Res.": "S1 F5 Z0",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC": "V",
            "Voltage AC": "V",
            "Voltage AC+DC": "V",
            "2W-Resistance": "Ohm",
            "4W-Resistance": "Ohm",
            "O.C. 2W-Res.": "Ohm",
            "O.C. 4W-Res.": "Ohm",
        }
        # measuring range as dictionary
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
        # number of displayed digits as dictionary
        self.resolutions = {
            "6 Digits (Standard)": "6STG",
            "5 Digits": "5STG",
            "4 Digits": "4STG",
            "3 Digits": "3STG",
        }
        # number of power line cycles for measurement (integration time)
        self.nplc_types = {
            "Very Fast (0.01)": ".01STI",
            "Fast (0.1)": ".1STI",
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
            "Trigger Source": ["INT", "EXT"],
            "Display": ["On", "Off"],
        }

    def get_GUIparameter(self, parameter: dict):
        self.mode = parameter["Mode"]
        self.resolution = parameter["Resolution"]
        self.range = parameter["Range"]
        self.nplc = parameter["NPLC"]
        self.autozero = parameter["Auto-Zero"]
        self.filter = parameter["Filter"]
        self.trigsource = parameter["Trigger Source"]
        self.display = parameter["Display"]

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
        # reset instruments via home command; works faster than clearing via CL1 with same functionality
        self.port.write("H")

    def configure(self):
        # Data Output Format
        # makes sure the device is set to the standard, unpacked ASCII format for data output
        self.port.write("P0")

        # End-or-Identify Code
        # use the EOI mode for SCPI compatibility
        self.port.write("O1")

        # Operation Mode
        self.port.write("%s" % self.modes[self.mode])

        # Range
        # check if an resistance-only range was selected in a non-resistance mode of operation
        if self.range in ["10 MOhm", "100 MOhm", "1 GOhm"] and self.mode in [
            "Voltage DC",
            "Voltage AC",
            "Voltage AC+DC",
        ]:
            msg = "Currently selected range is restricted to Resistance measurement only"
            raise Exception(msg)
        else:
            # set measurement range
            self.port.write("%s" % self.ranges[self.range])

        # Resolution
        # set the amount of digits of measurement result value
        self.port.write("%s" % self.resolutions[self.resolution])

        # NPLC Integration
        # set number of power line cycles to define integration time
        self.port.write("%s" % self.nplc_types[self.nplc])

        # Auto-Zero
        if self.autozero == "On":
            # enable Auto-Zero feature in between measureming cycles; will double measurement time
            self.port.write("Z1")
        else:
            # disable Auto-Zero feature
            self.port.write("Z0")

        # Filter
        if self.filter == "On":
            if self.mode in ["2W-Resistance", "4W-Resistance", "O.C. 2W-Res.", "O.C. 4W-Res."]:
                msg = "Filter function cannot be used in Resistance mode"
                raise Exception(msg)
            else:
                # enable AC ripple filter for voltage measurements
                self.port.write("FL1")
        else:
            # disable AC filter
            self.port.write("FL0")

        # Display
        # stops displaying the measurement results on the display but just slashes instead
        if self.display == "Off":
            self.port.write("D0")

        # Trigger on HOLD
        # sets the internal trigger on hold to wait for a manual trigger during the 'measure' routine; 
        # it is done ONLY if INTERNAL trigger is chosen as source; if it is done with external trigger,
        # putting the trigger on hold and setting it to external during measure would result in an invalid value in the output buffer
        # that gets read out by the first self.port.read command instead of it waiting for the result caused by the external trigger
        if self.trigsource == "INT":
            self.port.write("T4")
        else:
            # arm external trigger
            self.port.write("T2")

    def unconfigure(self):
        if self.display == "Off":
            # we switch Display on again if it was switched off
            self.port.write("D1")
        # sets the trigger back to INTERNAL to enable the self-triggered measurements on the display again
        self.port.write("T1")

    def measure(self):
        if self.trigsource == "INT":
            # perform single trigger for a measurement using internal trigger
            self.port.write("T3")
            
        # retrieves current measurement data from the instrument
        self.data = self.port.read()

    def call(self):
        return [float(self.data)]
