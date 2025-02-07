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
# * Instrument: Datron 10x1/10x2


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>Datron 10x1 DMM driver (plus 10x2 and 1065 derivations)</strong></p></p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "DATRON10x1"

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            # needed for long integration times, model dependend; adjust if required
            "timeout": 10,
            "delay": 0.1,
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        # the switch from 2-wire to 4-wire resistance measurement is either automatic uppon plug in of cables (1065/1065A) or purely manual by switch on frontpanel
        self.modes = {
            "Voltage DC": "F3",
            "Voltage AC": "F2",
            "Voltage DC+AC": "F6",
            "Current DC": "F5",
            "Current AC": "F4",
            "Current DC+AC": "F7",
            "Resistance": "F1",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC": "V",
            "Voltage AC": "V",
            "Voltage AC+DC": "V",
            "Current DC": "A",
            "Current AC": "A",
            "Current DC+AC": "A",
            "Resistance": "Ohm",
        }
        # number of displayed digits as dictionary
        self.ranges = {
            "Auto": "R0",
            "10 Ohm": "R1",
            "100 mV/uA/Ohm": "R2",
            "1 V/mA/kOhm": "R3",
            "10 V/mA/kOhm": "R4",
            "100 V/mA/kOhm": "R5",
            "1000 V/mA/kOhm": "R6",
            "10 MOhm": "R7",
        }

    def set_GUIparameter(self):
        return {
            "Input Select": ["Front", "Rear"],
            "Mode": list(self.modes.keys()),
            "Range": list(self.ranges.keys()),
            "High-Resolution": ["Off", "On"],
            "Filter": ["Off", "On"],
        }

    def get_GUIparameter(self, parameter: dict):
        self.inputselect = ["Input Select"]
        self.mode = parameter["Mode"]
        self.range = parameter["Range"]
        self.highres = parameter["High-Resolution"]
        self.filter = parameter["Filter"]

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
        # device clear command not active to retain manually made settings; uncomment if needed
        #self.port.write("DCL") 
        pass

    def configure(self):

        # Data output format
        # set output as ASCII in scientic notation; some additional information has to be stripped before result is handed over, see later comment
        self.port.write("O0")
        
        # Select input front/rear
        if self.inputselect == "Rear":
            self.port.write("I1")
        else:
            self.port.write("I0") 

        # Mode
        self.port.write("%s" % self.modes[self.mode])

        # Range
        # If the ranges of 10 Ohm or 10 MOhm are selected while not in resistance mode, the instrument will not throw an error but use the next valid one instead.
        # To prevent confusion, this is checked for and blocked.
        if self.range in ["10 Ohm", "10 MOhm"] and self.mode in [
            "Voltage DC",
            "Voltage AC",
            "Voltage AC+DC",
            "Current DC",
            "Current AC",
            "Current DC+AC"
        ]:
            msg = "Currently selected range is restricted to resistance measurement only"
            raise Exception(msg)
        else:
            self.port.write("%s" % self.ranges[self.range])
            
        # High-Resolution; on the 1065A, pressing FILTER on the front panel activates this AND the filter function at the same time; via GPIB, this can be seperated
        if self.highres == "On":
            self.port.write("A2")
        else:
            self.port.write("A0") 

        # AC Filter; in case a 1065A (not 1065), this behaves differently to front panel operation; see previous command
        if self.filter == "On":
            self.port.write("C1")
        else:
            self.port.write("C0")

        # Trigger on HOLD
        # sets the trigger on hold to wait for a manual trigger during the 'measure' routine
        self.port.write("T2")  

    def unconfigure(self):
        # sets the trigger back to INTERNAL to enable the self-triggered measurements on the display again
        self.port.write("T0")

    def measure(self):
        # perform single trigger for a measurement; alternatively, an "@" is accepted as well
        self.port.write("J")
        
        # retrieves current measurement data from the instrument; no seperate SCPI data prepare command necessary
        self.data = self.port.read()  
        
        # removes trailing character that indicates the unit of the result
        self.data = self.data[:-1]
    
        # in AC and DC-coupled-AC mode, the first character is not used for a + or - sign but 
        # for indicating the mode of operation via special characters and these need to be removed
        if self.data[0] == "~" or self.data[0] == "#":
            self.data = self.data[1:]
            
    def call(self):
        return [float(self.data)]
