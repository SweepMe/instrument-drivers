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
# * Instrument: Keysight 3441xA


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>Keysight 34410A/34411A</strong></p>
                     <p>DMM: Digital Multimeter</p>
                     <p>&nbsp;</p>
                     <p>The 34410A/34411A are 6.5 digit DMM that support measurement of voltage, current, resistance, 
                     capacitance, temperature and 
                     frequency.</p>
                     <p>Two-wire as well as four-wire measurements are possible.</p>
                     <p>The instruments can be driven either via GPIB, USB or Ethernet LAN.</p>
                    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Keysight3441xA"

        self.port_manager = True
        self.port_types = ["GPIB", "USB", "TCPIP"]
        self.port_identifications = ['Agilent Technologies,34410A', 'Agilent Technologies,34411A','Keysight Technologies,34410A', 'Keysight Technologies,34411A'] 

        self.port_properties = {
            "timeout": 10,  # needed for 100 NPLC setting as it needs ~5s to computer
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
            "Capacitance": "CAP",
            "Temperature": "TEMP",
            
            
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
            "Capacitance": "F",
            "Temperature": "deg",
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
            "Range": ["Auto", "As is"],
            "Trigger Slope": ["POS", "NEG"],
            # internal trigger is called IMMediate because triggering is done automatically immediately as soon as possible
            "Trigger Source": ["IMM", "EXT"],
            "Auto-Zero": ["On", "Once", "Off"],
            # T.Unit will be used to overwrite placeholder "deg" set in __init__
            "Temperature Unit": ["C", "F", "K"],
            "Display": ["On", "Off"],
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):

        self.mode = parameter['Mode']
        self.range = parameter['Range']
        self.nplc = parameter ['NPLC']
        self.trigslope = parameter ['Trigger Slope']
        self.trigsource = parameter ['Trigger Source']
        self.autozero = parameter ['Auto-Zero']
        self.tempunit = parameter ['Temperature Unit']
        self.display = parameter['Display']

        self.port_string = parameter["Port"]

        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        # we add the channel name to each variable, e.g "Voltage DC"
        self.variables = [self.mode]
        
        # In case temperature is measured, do not use the general unit "deg" from the dictionary with initialization but the one chosen in GUI
        if self.mode == 'Temperature':
            self.units = self.tempunit
        else:
            self.units = [self.mode_units[self.mode]]

        # True to plot data
        self.plottype = [True]
        
        # True to save data
        self.savetype = [True]

    def initialize(self):
        # once at the beginning of the initialization; STATUS:PRESET to reset registers
        self.port.write("STAT:PRES")
        
        # can be used for text on lower instrument display
        # self.port.write(":DISP:WIND2:TEXT \"DRIVEN BY SWEEPME\"")

        # reset all values
        self.port.write("*CLS")

        # control-Beep off
        self.port.write("SYST:BEEP:STAT OFF")
        
        # setting the chosen unit for temperature measurement
        if self.mode == 'Temperature':
            self.port.write("UNIT:TEMP %s" % self.tempunit)

    def deinitialize(self):

        # control-Beep on
        self.port.write("SYST:BEEP:STAT ON")

    def configure(self):

        # Set Mode and AUTO Range
        if self.mode in ["Temperature", "Frequency", "Period", "Diode", "Continuity"] or self.range == "As is":
             # setting range left out for modes without any range; also if range = "As is" was chosen
            self.port.write("CONF:%s" % self.modes[self.mode])
        else:
            self.port.write("CONF:%s %s" % (self.modes[self.mode], self.range))

        # Speed
        if self.mode not in ["Voltage AC", "Current AC", "Frequency", "Period", "Diode", "Continuity", "Capacitance"]:
            # NPLC only supported in DC Volts, DC Current, 2W- and 4W-Resistance, Temperature
            self.port.write(":SENS:%s:NPLC %s" % (self.modes[self.mode], self.nplc_types[self.nplc]))
            
        # Trigger
        # setting slope of trigger
        self.port.write("TRIG:SLOP %s" % self.trigslope)
        # setting source for triggering
        self.port.write("TRIG:SOUR %s" % self.trigsource)
        
        # Auto-Zero
        if self.mode not in ["Voltage AC", "Current AC", "Frequency", "Period", "Diode", "Continuity", "Capacitance", "4W-Resistance"]:
            # NPLC only supported in DC Volts, DC Current, 2W-Resistance, Temperature
            self.port.write(":SENS:%s:ZERO:AUTO %s" % (self.modes[self.mode], self.autozero))

        # Display
        if self.display == "Off":
            self.port.write(":DISP:WIND1:STAT 0")
            self.port.write(":DISP:WIND2:STAT 0")

    def unconfigure(self):
        if self.display == "Off":
            # We switch Displays on again if it was switched off
            self.port.write(":DISP:WIND1:STAT 1")
            self.port.write(":DISP:WIND2:STAT 1")
            
    def measure(self):
        # triggers a new measurement
        self.port.write("READ?")

    def call(self):
        # here we read the response from the "READ?" request in 'measure'
        answer = self.port.read()
        return [float(answer)]
