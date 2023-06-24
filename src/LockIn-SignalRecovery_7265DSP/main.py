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
# Device: 7265DSP

import time
import numpy as np
from collections import OrderedDict
from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
    <p><strong>Ametek Signal Recovery DSP 7265</strong><br /> <br /> Notes:</p>
    <ul>
    <li>Availability of AC gain range might depend on selected sensitivity value</li>
    <li>AC gain will not work correctly with Auto sensitivity.</li>
    <li>Time constant option "Auto time - 10 periods" means that the time constant is automatically set to 10 periods of
     the signal. You can change the number in front of periods to another value.</li>
    </ul>
    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "7265DSP"

        # here the port handling is done
        # the MeasClass automatically creates the PortObject during in the connect function of the MeasClass
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        
        # self.port_identifications = ['Ametek,7280']
        # port_identifications does not work at the moment

        self.port_properties = { 
                                 "EOL": "\r\n",
                                 "timeout": 2,
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
                                           ("Current B High bandwidth, Front", "IMODE1; REF FRONT"),
                                           ("Current B Low noise, Front", "IMODE2; REF FRONT"),
                                           ("Voltage A, Front", "IMODE0; VMODE 1; REF FRONT"),
                                           ("Voltage -B, Front", "IMODE0; VMODE 2; REF FRONT"),
                                           ("Voltage A-B, Front", "IMODE0; VMODE 3; REF FRONT"),
                                           ("Current B High bandwidth, Rear", "IMODE1; REF REAR"),
                                           ("Current B Low noise, Rear", "IMODE2; REF REAR"),
                                           ("Voltage A, Rear", "IMODE0; VMODE 1; REF REAR"),
                                           ("Voltage -B, Rear", "IMODE0; VMODE 2; REF REAR"),
                                           ("Voltage A-B, Rear", "IMODE0; VMODE 3; REF REAR"),
                                          ])
                        
        self.gains = OrderedDict([
                               ("Auto gain", "AUTOMATIC 1"),
                               ("0 dB", "AUTOMATIC 0; ACGAIN 0"),
                               ("10 dB", "AUTOMATIC 0; ACGAIN 1"),
                               ("20 dB", "AUTOMATIC 0; ACGAIN 2"),
                               ("30 dB", "AUTOMATIC 0; ACGAIN 3"),
                               ("40 dB", "AUTOMATIC 0; ACGAIN 4"),
                               ("50 dB", "AUTOMATIC 0; ACGAIN 5"),
                               ("60 dB", "AUTOMATIC 0; ACGAIN 6"),
                               ("70 dB", "AUTOMATIC 0; ACGAIN 7"),
                               ("80 dB", "AUTOMATIC 0; ACGAIN 8"),
                               ("90 dB", "AUTOMATIC 0; ACGAIN 9"),
                                ])
                                
        self.inv_gains = \
            {int(v[20:]): int(k[:-3]) for k, v in self.gains.items() if v.startswith("AUTOMATIC 0; ACGAIN")}
        # print(self.inv_gains)
                               
        self.timeconstants = OrderedDict([
                                ("10µ", "TC 0"),
                                ("20µ", "TC 1"),
                                ("40µ", "TC 2"),
                                ("80µ", "TC 3"),
                                ("160µ", "TC 4"),
                                ("320µ", "TC 5"),
                                ("640µ", "TC 6"),
                                ("5m", "TC 7"),
                                ("10m", "TC 8"),
                                ("20m", "TC 9"),
                                ("50m", "TC 10"),
                                ("100m", "TC 11"),
                                ("200m", "TC 12"),
                                ("500m", "TC 13"),
                                ("1", "TC 14"),
                                ("2", "TC 15"),
                                ("5", "TC 16"),
                                ("10", "TC 17"),
                                ("20", "TC 18"),
                                ("50", "TC 19"),
                                ("100", "TC 20"),
                                ("200", "TC 21"),
                                ("500", "TC 22"),
                                ("1k", "TC 23"),
                                ("2k", "TC 24"),
                                ("5k", "TC 25"),
                                ("10k", "TC 26"),
                                ("20k", "TC 27"),
                                ("50k", "TC 28"),
                                ("100k", "TC 29"),
                            ])

        self.timeconstants_numbers = [self.value_to_float(x) for x in self.timeconstants]

        self.sensitivities_voltages = OrderedDict([
            ("2 nV", "SEN 1"),
            ("5 nV", "SEN 2"),
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

        self.sensitivities_currents_high_bandwidth = OrderedDict([
            ("2 fA", "SEN 1"),
            ("5 fA", "SEN 2"),
            ("10 fA", "SEN 3"),
            ("20 fA", "SEN 4"),
            ("50 fA", "SEN 5"),
            ("100 fA", "SEN 6"),
            ("200 fA", "SEN 7"),
            ("500 fA", "SEN 8"),
            ("1 pA", "SEN 9"),
            ("2 pA", "SEN 10"),
            ("5 pA", "SEN 11"),
            ("10 pA", "SEN 12"),
            ("20 pA", "SEN 13"),
            ("50 pA", "SEN 14"),
            ("100 pA", "SEN 15"),
            ("200 pA", "SEN 16"),
            ("500 pA", "SEN 17"),
            ("1 nA", "SEN 18"),
            ("2 nA", "SEN 19"),
            ("5 nA", "SEN 20"),
            ("10 nA", "SEN 21"),
            ("20 nA", "SEN 22"),
            ("50 nA", "SEN 23"),
            ("100 nA", "SEN 24"),
            ("200 nA", "SEN 25"),
            ("500 nA", "SEN 26"),
            ("1 µA", "SEN 27")
        ])

        self.sensitivities_currents_low_noise = OrderedDict([
            ("2 fA", "SEN 7"),
            ("5 fA", "SEN 8"),
            ("10 fA", "SEN 9"),
            ("20 fA", "SEN 10"),
            ("50 fA", "SEN 11"),
            ("100 fA", "SEN 12"),
            ("200 fA", "SEN 13"),
            ("500 fA", "SEN 14"),
            ("1 pA", "SEN 15"),
            ("2 pA", "SEN 16"),
            ("5 pA", "SEN 17"),
            ("10 pA", "SEN 18"),
            ("20 pA", "SEN 19"),
            ("50 pA", "SEN 20"),
            ("100 pA", "SEN 21"),
            ("200 pA", "SEN 22"),
            ("500 pA", "SEN 23"),
            ("1 nA", "SEN 24"),
            ("2 nA", "SEN 25"),
            ("5 nA", "SEN 26"),
            ("10 nA", "SEN 27"),
        ])

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

        self.filter2_commands = OrderedDict([
                               ("Sync filter off", "SYNC 0"),
                               ("Sync filter on", "SYNC 1"),
                            ])
        
        self.coupling_commands = OrderedDict([
                                    ("Fast", "CP 0"),
                                    ("Slow", "CP 1"),
                                    ])

    def set_GUIparameter(self):
    
        gui_parameter = {
                         "SweepMode": ["None", "Oscillator frequency in Hz"],
                         "Source": list(self.source_commands.keys()),
                         "OscillatorFrequency": 1000,
                         "OscillatorAmplitude": 0.1,
                         "Input": list(self.input_commands.keys()),
                         "Sensitivity": ["Auto sensitivity"] +
                                        list(self.sensitivities_voltages.keys()) +
                                        list(self.sensitivities_currents_high_bandwidth.keys()),
                         "Filter1": list(self.filter1_commands.keys()),
                         "Filter2": list(self.filter2_commands.keys()),
                         # "Channel1": [],
                         # "Channel2": [],
                         "TimeConstant": list(self.timeconstants.keys()) + ["Auto time - 10 periods"],
                         "Gain": list(self.gains.keys()),
                         "Slope": list(self.slopes.keys()),
                         "Coupling": list(self.coupling_commands.keys()),
                         "Ground": ["Ground", "Float"],
                         "WaitTimeConstants": 4.0,
                        }
                        
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):

        if "OscillatorAmplitude" not in parameter:
            raise Exception("Please update to the latest LockIn module to use the Signal Recovery 7265 driver.")

        self.sweepmode = parameter["SweepMode"]
        self.source = parameter["Source"]
        self.oscillator_frequency = parameter["OscillatorFrequency"]
        self.oscillator_amplitude = parameter["OscillatorAmplitude"]
        self.input = parameter["Input"]
        self.coupling = parameter["Coupling"]
        self.slope = parameter["Slope"]
        self.ground = parameter["Ground"]
        self.sensitivity = parameter["Sensitivity"]
        self.filter1 = parameter["Filter1"]
        self.filter2 = parameter["Filter2"]
        self.gain = parameter["Gain"]
        self.time_constant = parameter["TimeConstant"]
        self.wait_time_constants = float(parameter["WaitTimeConstants"])

        self.variables = ["Magnitude", "Phase", "Frequency", "Sensitivity", "Noise density", "AC Gain", "Time constant"]

        if self.input.startswith("Voltage"):
            self.units = ["V", "deg", "Hz", "V", "V/sqrt(Hz)", "dB", "s"]
        elif self.input.startswith("Current"):
            self.units = ["A", "deg", "Hz", "A", "A/sqrt(Hz)", "dB", "s"]

        self.plottype = [True, True, True, True, True, True, True]
        self.savetype = [True, True, True, True, True, True, True]

    def initialize(self):

        # identifier = self.get_identification()
        # print("Identifier:", identifier)

        # version = self.get_version()
        # print("Version:", version)

        if self.source != "Internal" and self.sweepmode == "Oscillator frequency in Hz":
            raise Exception("To sweep the oscillator frequency, the reference must be 'Internal'. "
                            "Please change and try again.")

        self.set_remote(True)
        self.set_display_light(True)
        self.port.write("ADF 1")  # restore default settings

    def deinitialize(self):
        self.set_remote(False)

    def configure(self):    

        # Source adjustment
        self.port.write(self.source_commands[self.source])
        self.wait_for_complete()

        # Input adjustment
        self.port.write(self.input_commands[self.input])
        self.wait_for_complete()

        # Slope adjustment
        self.port.write(self.slopes[self.slope])
        self.wait_for_complete()

        # Ground adjustment
        self.port.write(self.commands[self.ground])
        self.wait_for_complete()

        # Coupling adjustment
        self.port.write(self.coupling_commands[self.coupling])
        self.wait_for_complete()

        # self.port.write(self.commands[self.reserve])
        self.wait_for_complete()

        # set notch filter
        self.port.write(self.filter1_commands[self.filter1])
        self.wait_for_complete()

        # set notch filter
        self.port.write(self.filter2_commands[self.filter2])
        self.wait_for_complete()

        # Gain adjustment
        self.port.write(self.gains[self.gain])
        self.wait_for_complete()

        # Sensitivity adjustment
        if self.sensitivity != "Auto sensitivity":
            if "Voltage" in self.input:
                self.port.write(self.sensitivities_voltages[self.sensitivity])
                # self.inv_sensitivities = {v: k for k, v in self.sensitivities_voltages.items()}
            elif "Current B High bandwidth" in self.input:
                self.port.write(self.sensitivities_currents_high_bandwidth[self.sensitivity])
                # self.inv_sensitivities = {v: k for k, v in self.sensitivities_currents_high_bandwidth.items()}
            elif "Current B Low noise" in self.input:
                self.port.write(self.sensitivities_currents_low_noise[self.sensitivity])
                # self.inv_sensitivities = {v: k for k, v in self.sensitivities_currents_low_noise.items()}
            self.wait_for_complete()

        # Time constant adjustment
        if not self.time_constant.startswith("Auto time"):
            if self.time_constant in self.timeconstants:
                new_tc_key = self.time_constant
            else:
                new_tc_key = self.find_best_time_constant_key(self.time_constant)
            self.port.write(self.timeconstants[new_tc_key])
            self.wait_for_complete()
        else:
            factor_periods_str = self.time_constant.split("-")[1]
            factor_auto_time_constant = factor_periods_str.replace("period", "").replace("s", "").replace(" ", "")
            self.factor_auto_time_constant = float(factor_auto_time_constant)
       
        if self.source == "Internal":
            if self.sweepmode != "Oscillator frequency in Hz":
                self.set_oscillator_frequency(self.oscillator_frequency)
            self.set_oscillator_amplitude(self.oscillator_amplitude)

        # Phase re-adjustment
        self.adjust_phase()

    def reconfigure(self, parameters, keys):

        if "TimeConstant" in keys:
            self.time_constant = parameters["TimeConstant"]
            if not self.time_constant.startswith("Auto time"):
                if self.time_constant in self.timeconstants:
                    new_tc_key = self.time_constant
                else:
                    new_tc_key = self.find_best_time_constant_key(self.time_constant)
                self.port.write(self.timeconstants[new_tc_key])
                self.wait_for_complete()
            else:
                factor_periods_str = self.time_constant.split("-")[1]
                factor_auto_time_constant = factor_periods_str.replace("period", "").replace("s", "").replace(" ", "")
                self.factor_auto_time_constant = float(factor_auto_time_constant)

    def apply(self):
        
        if self.sweepmode == "Oscillator frequency in Hz":
            self.set_oscillator_frequency(self.value)

    def reach(self):
        pass
   
    def adapt(self):

        # here we need to auto-adjust the time constant based on the frequency
        if "Auto time" in self.time_constant:
            self.auto_time_constant(self.factor_auto_time_constant)

        if self.sensitivity == "Auto sensitivity":
            self.start_autosensitivity()

    def adapt_ready(self):

        if self.sensitivity == "Auto sensitivity":
            self.wait_for_complete()

        self.time_ref = time.time()
            
    def trigger_ready(self):

        self.tc = self.get_time_constant()

        # makes sure that at least several time constants have passed after a new state/situation is achieved.
        delta_time = (self.wait_time_constants * self.tc) - (time.time()-self.time_ref)
        if delta_time > 0.0:
            time.sleep(delta_time)

    def measure(self):
        pass

    def request_result(self):
        pass

    def read_result(self):

        self.frq = self.get_frequency()
        self.r = self.get_magnitude()
        self.phi = self.get_phase()
        self.sen = self.get_sensitivity()

        # Model 7265 can only measure noise density until 60 kHz
        if self.frq <= 60000:
            self.nhz = self.get_noise_density()
        else:
            self.nhz = float('nan')

        self.acg = self.get_acgain()
        self.acg_dB = self.inv_gains[self.acg]

    def call(self):

        return [self.r, self.phi, self.frq, self.sen, self.nhz, self.acg_dB, self.tc]

    # convenience functions start here
        
    def value_to_float(self, value):

        # convert unit and prefix to number
        chars = OrderedDict([ 
                                ("V", ""),
                                ("s", ""),
                                (" ", ""),
                                ("n", "e-9"),
                                ("µ", "e-6"),
                                ("m", "e-3"),
                                ("k", "e3"),
                                ("M", "e6"),
                                ("G", "e9"),
                            ])

        if isinstance(value, str):
            for char in chars:
                value = value.replace(char, chars[char])

        return float(value)

    def find_best_time_constant_key(self, time_constant):

        time_constant = self.value_to_float(time_constant)

        # sum over boolean entries leads to index of new time_constant
        # this also works if the order of the time constants list is lost as the number of True and False
        # remains the same
        tc_index = sum(np.array(self.timeconstants_numbers) < time_constant)  # sum over boolean entries

        if tc_index < len(self.timeconstants):
            new_tc_key = list(self.timeconstants.keys())[tc_index]
        else:
            # if tc_index equals the length of time constants, the request time constant is longer than any possible
            # time constant, so we just return the key of the highest possible one.
            new_tc_key = "100k"

        return new_tc_key

    def auto_time_constant(self, factor=10.0):
        """
        checks the current frequency and adapts the time constant

        Args:
            factor: float, factor by which the time constant is at least higher than the period of the signal

        """

        frq = self.get_frequency()
        period = 1.0/frq
        new_tc = factor*period
        new_tc_key = self.find_best_time_constant_key(new_tc)

        # sending the new time constant command
        self.port.write(self.timeconstants[new_tc_key])
        self.wait_for_complete()

    def wait_for_complete(self):

        starttime = time.time()
        while True:
            # only the direct GPIB status byte call works as it can be acquired even when the lock-in is
            # busy with auto sensitivity operation
            stb = self.port.port.read_stb()
            if stb & 1 == 1:  # first byte indicates whether command is processed or not
                break
            time.sleep(0.01)
            if time.time() - starttime > 20:
                raise Exception("Timeout during wait for completion.")

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

    def set_delimiter(self, value):
        self.port.write("DD %i" % int(value))
        self.wait_for_complete()

    def set_remote(self, state=True):
        """
        changes front panel control

        Args:
            state: bool or integer (0 or 1) to disable or enable front panel control
        """
        self.port.write("REMOTE %i" % int(state))
        self.wait_for_complete()

    def set_display_light(self, state=True):
        """

        Args:
            state:

        Returns:

        """
        self.port.write("LTS %i" % int(state))
        self.wait_for_complete()

    def get_acgain(self):
        self.port.write("ACGAIN")
        return int(self.port.read())

    def set_line_frequency_filter(self, n1, n2):

        """
        # LF [n1 n2] Signal channel line frequency rejection filter control
        # The LF command sets the mode and frequency of the line frequency rejection (notch)
        # filter according to the following tables:
        # n1 Selection #
        # 0 Off
        # 1 Enable 50 or 60 Hz notch filter
        # 2 Enable 100 or 120 Hz notch filter
        # 3 Enable both filters
        # n2 Notch Filter Center Frequencies #
        # 0 60 Hz (and/or 120 Hz)
        # 1 50 Hz (and/or 100 Hz)

        Args:
            n1: (int) Selection
                0 Off
                1 Enable 50 or 60 Hz notch filter
                2 Enable 100 or 120 Hz notch filter
                3 Enable both filters
            n2: (int) Notch Filter Center Frequencies
                0 60 Hz (and/or 120 Hz)
                1 50 Hz (and/or 100 Hz)
        """
        self.port.write("LF %i %i" % (int(n1), int(n2)))
        self.wait_for_complete()

    def set_oscillator_amplitude(self, value):
        """
        sets the amplitude in V

        Args:
            value:

        Returns:

        """
        self.port.write("OA. %i" % int(float(value)*1000))  # value is sent in mV
        self.wait_for_complete()

    def set_oscillator_frequency(self, frequency):
        self.port.write("OF. %1.6E" % float(frequency))
        self.wait_for_complete()

    def start_autosensitivity(self):
        self.port.write("AS")

    def adjust_phase(self):
        self.port.write("AQN")
        self.wait_for_complete()

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
        self.wait_for_complete()

    def get_noise_density(self):
        """
        The noise density can only be measured until 60 kHz according to the manual. At higher frequencies this
        function does not work and will lead to an error or a timeout.

        Returns:
            flaot: noise density in V/sqrt(Hz) or A/sqrt(Hz)
        """
        self.port.write("NHZ.")
        return float(self.port.read())

    def get_time_constant(self):
        """
        Returns:
            float: time constant in s
        """
        self.port.write("TC.")
        return float(self.port.read())
