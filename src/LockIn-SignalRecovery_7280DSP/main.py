# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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

# SweepMe! device class
# Type: Lockin
# Device: 7280DSP

from EmptyDeviceClass import EmptyDevice
import time
import numpy as np
from collections import OrderedDict

class Device(EmptyDevice):

    description = """
    <b>Ametek Signal Recovery DSP 7280</b><br>
    <br>
    Notes:
    <ul>
    <li>ACGain can only be set to constant value if the sensitivity values allows it.</li>
    <li>ACGain will thus not work correctly with Auto sensitivity.</li>
    <li>Oscillator freqency and amplitude sweep are not yet supported.</li>
    </ul>
    
    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "7280DSP"

        # here the port handling is done
        # the MeasClass automatically creates the PortObject during in the connect function of the MeasClass
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        
        # self.port_identifications = ['Ametek,7280']
        # port_identifications does not work at the moment

        self.port_properties = { 
                                 # "EOL": "\r",
                                 "timeout": 10,
                                 "baudrate": 9600,
                            }

        # I started to define dictionaries to translate GUI-commands into remote commands
        # Attention: No Gui-selection should occur twice
        self.commands = OrderedDict([ 
                               # ("Frequency [Hz]", "FREQ"),
                               # ("Internal", ""),
                               ("Float", "FLOAT 1"),
                               ("Ground", "FLOAT 0"),
                            ])
                            
        self.source_commands = OrderedDict([
                                            ("Internal", "IE 0"),
                                            ("External TTL Rear", "IE 1"),
                                            ("External Analog Front", "IE 2"),
                                            ])
                            
        self.input_commands = OrderedDict([
                                           ("Current B Normal, Front", "IMODE1; REF FRONT"),
                                           ("Current B Low noise, Front", "IMODE2; REF FRONT"),
                                           ("Current B High bandwidth, Front", "IMODE3; REF FRONT"),
                                           ("Voltage A, Front", "IMODE0; VMODE 1; REF FRONT"),
                                           ("Voltage -B, Front", "IMODE0; VMODE 2; REF FRONT"),
                                           ("Voltage A-B, Front", "IMODE0; VMODE 3; REF FRONT"),
                                           ("Current B Normal, Rear", "IMODE1; REF REAR"),
                                           ("Current B Low noise, Rear", "IMODE2; REF REAR"),
                                           ("Current B High bandwidth, Rear", "IMODE3; REF REAR"),
                                           ("Voltage A, Rear", "IMODE0; VMODE 1; REF REAR"),
                                           ("Voltage -B, Rear", "IMODE0; VMODE 2; REF REAR"),
                                           ("Voltage A-B, Rear", "IMODE0; VMODE 3; REF REAR"),
                                          ])
                        
        self.gains =  OrderedDict([  
                               ("Auto gain", "AUTOMATIC 1"),
                               ("0 dB", "AUTOMATIC 0; ACGAIN 0"),
                               ("6 dB", "AUTOMATIC 0; ACGAIN 1"),
                               ("14 dB", "AUTOMATIC 0; ACGAIN 2"),
                               ("20 dB", "AUTOMATIC 0; ACGAIN 3"),
                               ("26 dB", "AUTOMATIC 0; ACGAIN 4"),
                               ("34 dB", "AUTOMATIC 0; ACGAIN 5"),
                               ("40 dB", "AUTOMATIC 0; ACGAIN 6"),
                               ("46 dB", "AUTOMATIC 0; ACGAIN 7"),
                               ("54 dB", "AUTOMATIC 0; ACGAIN 8"),
                               ("60 dB", "AUTOMATIC 0; ACGAIN 9"),
                               ("66 dB", "AUTOMATIC 0; ACGAIN 10")
                                ])
                                
        self.inv_gains = {int(v[20:]): int(k[:-3]) for k, v in self.gains.items() if v.startswith("AUTOMATIC 0; ACGAIN")}
        #print(self.inv_gains)
                               
        self.timeconstants = OrderedDict([
                                ("1 µs", "TC 0; FASTMODE 1"),
                                ("2 µs", "TC 1; FASTMODE 1"),
                                ("5 µs", "TC 2; FASTMODE 1"),
                                ("10 µs", "TC 3; FASTMODE 1"),
                                ("20 µs", "TC 4; FASTMODE 1"),
                                ("50 µs", "TC 5; FASTMODE 1"),
                                ("100 µs", "TC 6; FASTMODE 1"),
                                ("200 µs", "TC 7; FASTMODE 1"),
                                ("500 µs", "TC 8; FASTMODE 0"),
                                ("1 ms", "TC 9; FASTMODE 0"),
                                ("2 ms", "TC 10; FASTMODE 0"),
                                ("5 ms", "TC 11; FASTMODE 0"),
                                ("10 ms", "TC 12; FASTMODE 0"),
                                ("20 ms", "TC 13; FASTMODE 0"),
                                ("50 ms", "TC 14; FASTMODE 0"),
                                ("100 ms", "TC 15; FASTMODE 0"),
                                ("200 ms", "TC 16; FASTMODE 0"),
                                ("500 ms", "TC 17; FASTMODE 0"),
                                ("1 s", "TC 18; FASTMODE 0"),
                                ("2 s", "TC 19; FASTMODE 0"),
                                ("5 s", "TC 20; FASTMODE 0"),
                                ("10 s", "TC 21; FASTMODE 0"),
                                ("20 s", "TC 22; FASTMODE 0"),
                                ("50 s", "TC 23; FASTMODE 0"),
                                ("100 s", "TC 24; FASTMODE 0"),
                                ("200 s", "TC 25; FASTMODE 0"),
                                ("500 s", "TC 26; FASTMODE 0"),
                                ("1 ks", "TC 27; FASTMODE 0"),
                                ("2 ks", "TC 28; FASTMODE 0"),
                                ("5 ks", "TC 29; FASTMODE 0"),
                                ("10 ks", "TC 30; FASTMODE 0"),
                                ("20 ks", "TC 31; FASTMODE 0"),
                                ("50 ks", "TC 32; FASTMODE 0"),
                                ("100 ks", "TC 33; FASTMODE 0"),
                            ])

        self.sensitivities = OrderedDict([
                                    ("Auto sensitivity", "AS"),
                                    ("10 nV", "SEN 3"),
                                    ("20 nV", "SEN 4"),
                                    ("50 nV", "SEN 5"),
                                    ("100 nV", "SEN 6"),
                                    ("200 nV", "SEN 7"),
                                    ("500 nV", "SEN 8"),
                                    ("1 µV", "SEN 9"),
                                    ("2 µV", "SEN 10"),
                                    ("5 µV", "SEN 11"),
                                    ("10 µV", "SEN 12"),
                                    ("20 µV", "SEN 13"),
                                    ("50 µV", "SEN 14"),
                                    ("100 µV", "SEN 15"),
                                    ("200 µV", "SEN 16"),
                                    ("500 µV", "SEN 17"),
                                    ("1 mV", "SEN 18"),
                                    ("2 mV", "SEN 19"),
                                    ("5 mV", "SEN 20"),
                                    ("10 mV", "SEN 21"),
                                    ("20 mV", "SEN 22"),
                                    ("50 mV", "SEN 23"),
                                    ("100 mV", "SEN 24"),
                                    ("200 mV", "SEN 25"),
                                    ("500 mV", "SEN 26"),
                                    ("1 V", "SEN 27")
                                    ])
                                    
        self.inv_sensitivities = {v: k for k, v in self.sensitivities.items()}

        self.slopes = OrderedDict([
                        ("6 dB/octave",  "SLOPE 0"),
                        ("12 dB/octave", "SLOPE 1"),
                        ("18 dB/octave", "SLOPE 2"),
                        ("24 dB/octave", "SLOPE 3"),
                        ])
                        
        self.filter1_commands = OrderedDict([
                        ("Off",  "LF 0 0"),
                        ("50 Hz notch filter", "LF 1 1"),
                        ("60 Hz notch filter", "LF 1 0"),
                        ("100 Hz notch filter", "LF 2 1"),
                        ("120 Hz notch filter", "LF 2 0"),
                        ("50 Hz and 100 Hz notch filter", "LF 3 1"),
                        ("60 Hz and 120 Hz notch filter", "LF 3 0"),
                        ])
                        
        # LF [n1 n2] Signal channel line frequency rejection filter control
        # The LF command sets the mode and frequency of the line frequency rejection (notch)
        # filter according to the following tables:
        # n1 Selection
        # 0 Off
        # 1 Enable 50 or 60 Hz notch filter
        # 2 Enable 100 or 120 Hz notch filter
        # 3 Enable both filters
        # n2 Notch Filter Center Frequencies
        # 0 60 Hz (and/or 120 Hz)
        # 1 50 Hz (and/or 100 Hz)

        self.filter2_commands = OrderedDict([
                               ("Sync filter off", "SYNC 0"),
                               ("Sync filter on", "SYNC 1"),
                            ])
        
        self.coupling_commands = OrderedDict([
                                    ("Fast", "CP 0"),
                                    ("Slow", "CP 1"),
                                    ])
                                                                
    def set_GUIparameter(self):
    
        GUIparameter = {
                         "SweepMode": ["None", "Oscillator frequency in Hz"],
                         "Source": list(self.source_commands.keys()),
                         "Input": list(self.input_commands.keys()),
                         "Sensitivity": list(self.sensitivities.keys()),
                         "Filter1": list(self.filter1_commands.keys()),
                         "Filter2": list(self.filter2_commands.keys()),
                         # "Channel1": [],
                         # "Channel2": [],
                         "TimeConstant": list(self.timeconstants.keys()),  # ["AutoTime"]
                         "Gain": list(self.gains.keys()),
                         "Slope": list(self.slopes.keys()),
                         "Coupling": list(self.coupling_commands.keys()),
                         "Ground": ["Ground", "Float"],
                         "WaitTimeConstants": 4.0,
                        }
                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):
    
        self.sweepmode = parameter["SweepMode"]
        self.source = parameter["Source"]
        self.input = parameter["Input"]
        self.coupling = parameter["Coupling"]
        self.slope = parameter["Slope"]
        self.ground = parameter["Ground"]
        self.sensitivity = parameter["Sensitivity"]
        self.filter1 = parameter["Filter1"]
        self.filter2 = parameter["Filter2"]
        self.gain = parameter["Gain"]
        self.timeconstant = parameter["TimeConstant"]
        self.waittimeconstants = float(parameter["WaitTimeConstants"])
        # self.channel1 = parameter["Channel1"]
        # self.channel2 = parameter["Channel2"]

        self.variables = ["Magnitude", "Phase", "Frequency", "Sensitivity", "AC Gain", "Noise density"]

        if self.input.startswith("Voltage"):
            self.units = ["V", "deg", "Hz", "V", "dB", "V/sqrt(Hz)"]
        elif self.input.startswith("Current"):
            self.units = ["A", "deg", "Hz", "V", "dB", "A/sqrt(Hz)"]

        self.plottype = [True, True, True, True, True, True]
        self.savetype = [True, True, True, True, True, True]

    def initialize(self):

        # backward compatibility with older version that had typo
        if "bandwith" in self.input:
            debug("You are using a new version of the SignalRecovery_7280DSP driver that fixed a typo in the Input"
                  "options. Please reselect the option with 'bandwidth' to remove this message")
            self.input = self.input.replace("bandwith", "bandwidth")
        
        stb = self.get_status_byte()
        print("Status byte:", stb)
               
        self.port.write("REMOTE 1")  # stop front panel control
        self.port.write("LTS 1")  # controls front panel display
        self.port.write("ADF 1")  # restore default settings
        
        # self.port.write("DD 13") # set delimiter to ASCII 13

    def deinitialize(self):
        self.port.write("REMOTE 0")  # enable front panel control

    def configure(self):    
    
        #self.port.write("REFMODE 0")
        #self.port.write("VRLOCK 0")

        # Source adjustment
        self.port.write(self.source_commands[self.source])
        
        # Input adjustment
        self.port.write(self.input_commands[self.input])
        
        # Slope adjustment
        self.port.write(self.slopes[self.slope])
        
        # Ground adjustment
        self.port.write(self.commands[self.ground])
        
        # Coupling adjustment
        self.port.write(self.coupling_commands[self.coupling])
        
        # self.port.write(self.commands[self.reserve])
        
        # set notch filter
        self.port.write(self.filter1_commands[self.filter1])

        # sync filter
        self.port.write(self.filter2_commands[self.filter2])
        
        # Gain adjustment
        self.port.write(self.gains[self.gain])
       
        # Sensitivity adjustment
        if self.sensitivity != "Auto sensitivity":
            self.port.write(self.sensitivities[self.sensitivity])
            
        # Timeconstant adjustment    
        self.port.write(self.timeconstants[self.timeconstant])
        
        # Phase re-adjustment    
        self.port.write("AQN")

        if self.sweepmode == "Oscillator frequency in Hz":
            self.set_oscillator_amplitude(100)  # 100 mV amplitude

    def signin(self):
        pass
            
    def start(self):
        pass

        """
        SEN get sensitivity mode as set number
        SEN. get sensitivity as real value
        LTS 0 or 1 switch off display
        
        """
        
    def apply(self):
        
        if self.sweepmode == "Oscillator frequency in Hz":
            self.set_oscillator_frequency(self.value)

    def reach(self):
        pass
   
    def adapt(self):

        # here we need to auto-adjust the time constant based on the frequency
        frq = self.get_frequency()
        period = 1.0/frq
        time_constant = 10.0*period
        new_tc_key = self.find_next_time_constant()
        self.port.write(self.timeconstants[new_tc_key])

        if self.sensitivity == "Auto sensitivity":
            self.port.write("AS")
               
    def adapt_ready(self):

        # could be used to figure out whether Auto Sensitivity has finished
        # stb = self.get_status_byte()

        self.time_ref = time.time()
            
    def trigger_ready(self):
        # make sure that at least several timeconstants have passed since 'Auto sensitivity' was called
        delta_time = (self.waittimeconstants * self.unit_to_float(self.timeconstant)) - (time.time()-self.time_ref)
        if delta_time > 0.0:
            # wait several timeconstants to allow for a renewal of the result     
            time.sleep(delta_time)
            
        #self.port.write("NC") # clear and reset curve buffer
      
    def measure(self):
        pass
        # self.port.write("CBD 32796") acquire Stores Magnitude, Phase, Sensitivity and Frequency (i.e. bits 2, 3, 4 and 15)

    def request_result(self):
        pass

    def read_result(self):

        self.frq = self.get_frequency()
        self.r = self.get_magnitude()
        self.phi = self.get_phase()
        self.sen = self.get_sensitivity()

        self.nhz = self.get_noise_density()


        self.acg = self.get_acgain()

        self.acg_dB = self.inv_gains[self.acg]

    def call(self):

        return [self.r, self.phi, self.frq, self.sen, self.acg_dB, self.nhz]

    # convenience functions start here
        
    def unit_to_float(self, unit):
        # convert unit and prefix to number
        chars = OrderedDict([ 
                                ("V",""), 
                                ("s",""),
                                (" ",""),
                                ("n","e-9"), 
                                ("µ","e-6"),
                                ("m","e-3")
                            ])

        for char in chars:
            unit = unit.replace(char,chars[char])
        return float(unit)

    # get/set functions start here

    def get_identification(self):
        self.port.write("ID")
        return self.port.read()

    def get_version(self):
        self.port.write("VER")
        return self.port.read()

    def get_status_byte(self):
        self.port.write("ST")
        return int(self.port.read())

    def get_overload_byte(self):
        self.port.write("N")
        return int(self.port.read())

    def get_acgain(self):
        self.port.write("ACGAIN")
        return int(self.port.read())

    def set_oscillator_frequency(self, frequency):
        self.port.write("OF. %1.9E" % float(frequency))

    def set_oscillator_amplitude(self, value):
        """
        sets the amplitude in V

        Args:
            value:

        Returns:

        """
        self.port.write("OA. %i" % int(float(value)*1000))

    def set_autosensitivity(self):
        self.port.write("AS")

    def get_timeconstant(self):
        self.port.write("TC.")
        return self.port.read()

    def set_timeconstant(self, value):
        self.port.write("TC %i" % int(value))

    def get_magnitude(self):
        self.port.write("MAG.")
        return float(self.port.read())

    def get_phase(self):
        self.port.write("PHA.")
        return float(self.port.read())

    def get_frequency(self):
        self.port.write("FRQ.")
        return float(self.port.read())

    def get_sensitivity(self):
        self.port.write("SEN.")
        return float(self.port.read())

    def set_sensitivity(self, value):
        self.port.write("SEN %i" % int(value))

    def get_noise_density(self):
        """
        The noise density can only be measured until 60 kHz according to the manual. At higher frequencies this
        function does not work and will lead to an error or a timeout.

        Returns:
            flaot: noise density in V/sqrt(Hz) or A/sqrt(Hz)
        """
        self.port.write("NHZ.")
        return float(self.port.read())
