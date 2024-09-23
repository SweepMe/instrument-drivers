# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021-2024 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank Jakob Wolansky/TU Dresden for contributing
# to the improvement of the driver.


# SweepMe! driver
# * Module: LockIn
# * Instrument: SR830

from pysweepme.EmptyDeviceClass import EmptyDevice
import time
from collections import OrderedDict


class Device(EmptyDevice):

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "SR830"
                
        # self.variables = ["Magnitude", "Phase", "Frequency", "X", "Y", "Channel 1", "Channel 2", "TimeConstant" ]
        # self.units = ["a.u.", "deg", "Hz", "a.u.", "a.u.", "V/sqrt(Hz)", "V/sqrt(Hz)", "s"]
        
        
        # here the port handling is done
        # the MeasClass automatically creates the PortObject during in the connect function of the MeasClass
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        self.port_identifications = ['Stanford Research Instruments,SR8']
        # port_identifications does not work at the moment
        # plan is to hand it over to PortManager who only gives PortObjects back who match at least one of these strings
        # by that multiple devices could be found and related to one DeviceClass              
        self.port_properties = {"EOL": "\r",
                                "timeout": 60,
                                "baudrate": 9600,
                                "Exception": True,
                                }
        # properties are used to change the properties of the PortObject

        # I started to define dictionaries to translate GUI-commands into remote commands
        # Attention: No Gui-selection/key should occur twice
        self.commands = OrderedDict([ 
                               ("Frequency [Hz]", "FREQ"),
                               ("Frequency in Hz", "FREQ"),
                               ("Internal", "FMOD 1"),
                               ("External (Sine)", "FMOD 0; RSLP 0"),
                               ("External (TTL Rising)", "FMOD 0; RSLP 1"),
                               ("External (TTL Falling)", "FMOD 0; RSLP 2"),
                               ("A", "ISRC 0"),
                               ("A-B", "ISRC 1"),
                               ("I@10^6", "ISRC 2"),
                               ("I@10^8", "ISRC 3"),
                               ("Float", "IGND 0"),
                               ("Ground", "IGND 1"),
                               ("AC", "ICPL 0"),
                               ("DC", "ICPL 1"),
                               ("No Filter", "ILIN 0"),
                               ("Line", "ILIN 1"),
                               ("2xLine", "ILIN 2"),
                               ("Line + 2xLine", "ILIN 3"),
                               ("High Reserve", "RMOD 0"),
                               ("Normal", "RMOD 1"),
                               ("Low Noise", "RMOD 2"),
                               ("Sync Filter", "SYNC 1"),
                               ("No Sync Filter", "SYNC 0"),
                               ("6dB", "OFSL 0"),
                               ("12dB", "OFSL 1"),
                               ("18dB", "OFSL 2"),
                               ("24dB", "OFSL 3"),
                               ("AC", "ICPL 0"),
                               ("DC", "ICPL 1"),
                               ("Float", "IGND 0"),
                               ("Ground", "IGND 1"),
                               ("Sensitivity", "SENS"),
                               ("Time constant in s", "OFLT"),
                            ])

        self.sensitivities_old = OrderedDict([
                               ("2 nV or 2 fA", "SENS 0"),
                               ("5 nV or 5 fA", "SENS 1"),
                               ("10 nV or 10 fA", "SENS 2"),
                               ("20 nV or 20 fA", "SENS 3"),
                               ("50 nV or 50 fA", "SENS 4"),
                               ("100 nV or 100 fA", "SENS 5"),
                               ("200 nV or 200 fA", "SENS 6"),
                               ("500 nV or 500 fA", "SENS 7"),
                               ("1 muV or 1 pA", "SENS 8"),
                               ("2 muV or 2 pA", "SENS 9"),
                               ("5 muV or 5 pA", "SENS 10"),
                               ("10 muV or 10 pA", "SENS 11"),
                               ("20 muV or 20 pA", "SENS 12"),
                               ("50 muV or 50 pA", "SENS 13"),
                               ("100 muV or 100 pA", "SENS 14"),
                               ("200 muV or 200 pA", "SENS 15"),
                               ("500 muV or 500 pA", "SENS 16"),
                               ("1 mV or 1 nA", "SENS 17"),
                               ("2 mV or 2 nA", "SENS 18"),
                               ("5 mV or 5 nA", "SENS 19"),
                               ("10 mV or 10 nA", "SENS 20"),
                               ("20 mV or 20 nA", "SENS 21"),
                               ("50 mV or 50 nA", "SENS 22"),
                               ("100 mV or 100 nA", "SENS 23"),
                               ("200 mV or 200 nA", "SENS 24"),
                               ("500 mV or 500 nA", "SENS 25"),
                               ("1 V or 1 muA", "SENS 26"),
                                ])
                                
        self.sensitivities_voltages = OrderedDict([
                               ("2 nV", "SENS 0"),
                               ("5 nV", "SENS 1"),
                               ("10 nV", "SENS 2"),
                               ("20 nV", "SENS 3"),
                               ("50 nV", "SENS 4"),
                               ("100 nV", "SENS 5"),
                               ("200 nV", "SENS 6"),
                               ("500 nV", "SENS 7"),
                               ("1 muV", "SENS 8"),
                               ("2 muV", "SENS 9"),
                               ("5 muV", "SENS 10"),
                               ("10 muV", "SENS 11"),
                               ("20 muV", "SENS 12"),
                               ("50 muV", "SENS 13"),
                               ("100 muV", "SENS 14"),
                               ("200 muV", "SENS 15"),
                               ("500 muV", "SENS 16"),
                               ("1 mV", "SENS 17"),
                               ("2 mV", "SENS 18"),
                               ("5 mV", "SENS 19"),
                               ("10 mV", "SENS 20"),
                               ("20 mV", "SENS 21"),
                               ("50 mV", "SENS 22"),
                               ("100 mV", "SENS 23"),
                               ("200 mV", "SENS 24"),
                               ("500 mV", "SENS 25"),
                               ("1 V", "SENS 26"),
                                ])
                                
        self.sensitivities_currents = OrderedDict([
                               ("2 fA", "SENS 0"),
                               ("5 fA", "SENS 1"),
                               ("10 fA", "SENS 2"),
                               ("20 fA", "SENS 3"),
                               ("50 fA", "SENS 4"),
                               ("100 fA", "SENS 5"),
                               ("200 fA", "SENS 6"),
                               ("500 fA", "SENS 7"),
                               ("1 pA", "SENS 8"),
                               ("2 pA", "SENS 9"),
                               ("5 pA", "SENS 10"),
                               ("10 pA", "SENS 11"),
                               ("20 pA", "SENS 12"),
                               ("50 pA", "SENS 13"),
                               ("100 pA", "SENS 14"),
                               ("200 pA", "SENS 15"),
                               ("500 pA", "SENS 16"),
                               ("1 nA", "SENS 17"),
                               ("2 nA", "SENS 18"),
                               ("5 nA", "SENS 19"),
                               ("10 nA", "SENS 20"),
                               ("20 nA", "SENS 21"),
                               ("50 nA", "SENS 22"),
                               ("100 nA", "SENS 23"),
                               ("200 nA", "SENS 24"),
                               ("500 nA", "SENS 25"),
                               ("1 muA", "SENS 26"),
                                ])
                                
        self.sensitivities_all = {}
        self.sensitivities_all.update(self.sensitivities_old)
        self.sensitivities_all.update(self.sensitivities_voltages)
        self.sensitivities_all.update(self.sensitivities_currents)

        # AF @ 06.07.21: This dict remains for backward compatibility after changing gains to sensitivities
        self.gains = OrderedDict([
                               ("2 nV/fA", "SENS 0"),
                               ("5 nV/fA", "SENS 1"),
                               ("10 nV/fA", "SENS 2"),
                               ("20 nV/fA", "SENS 3"),
                               ("50 nV/fA", "SENS 4"),
                               ("100 nV/fA", "SENS 5"),
                               ("200 nV/fA", "SENS 6"),
                               ("500 nV/fA", "SENS 7"),
                               ("1 muV/pA", "SENS 8"),
                               ("2 muV/pA", "SENS 9"),
                               ("5 muV/pA", "SENS 10"),
                               ("10 muV/pA", "SENS 11"),
                               ("20 muV/pA", "SENS 12"),
                               ("50 muV/pA", "SENS 13"),
                               ("100 muV/pA", "SENS 14"),
                               ("200 muV/pA", "SENS 15"),
                               ("500 muV/pA", "SENS 16"),
                               ("1 mV/nA", "SENS 17"),
                               ("2 mV/nA", "SENS 18"),
                               ("5 mV/nA", "SENS 19"),
                               ("10 mV/nA", "SENS 20"),
                               ("20 mV/nA", "SENS 21"),
                               ("50 mV/nA", "SENS 22"),
                               ("100 mV/nA", "SENS 23"),
                               ("200 mV/nA", "SENS 24"),
                               ("500 mV/nA", "SENS 25"),
                               ("1 V/muA", "SENS 26"),
                                ])
                               
        self.timeconstants = OrderedDict([
                               ("10 µs", "OFLT 0"),
                               ("30 µs", "OFLT 1"),
                               ("100 µs", "OFLT 2"),
                               ("300 µs", "OFLT 3"),
                               ("1 ms", "OFLT 4"),
                               ("3 ms", "OFLT 5"),
                               ("10 ms", "OFLT 6"),
                               ("30 ms", "OFLT 7"),
                               ("100 ms", "OFLT 8"),
                               ("300 ms", "OFLT 9"),
                               ("1 s", "OFLT 10"),
                               ("3 s", "OFLT 11"),
                               ("10 s", "OFLT 12"),
                               ("30 s", "OFLT 13"),
                               ("100 s", "OFLT 14"),
                               ("300 s", "OFLT 15"),
                               ("1 ks", "OFLT 16"),
                               ("3 ks", "OFLT 17"),
                               ("10 ks", "OFLT 18"),
                               ("30 ks", "OFLT 19"),
                            ])
                            
        self.timeconstants_values = OrderedDict([
                               ("10 µs", 1e-5),
                               ("30 µs", 3e-5),
                               ("100 µs", 1e-4),
                               ("300 µs", 3e-4),
                               ("1 ms", 1e-3),
                               ("3 ms", 3e-3),
                               ("10 ms", 1e-2),
                               ("30 ms", 3e-2),
                               ("100 ms", 1e-1),
                               ("300 ms", 3e-1),
                               ("1 s", 1),
                               ("3 s", 3),
                               ("10 s", 1e1),
                               ("30 s", 3e1),
                               ("100 s", 1e2),
                               ("300 s", 3e2),
                               ("1 ks", 1e3),
                               ("3 ks", 3e3),
                               ("10 ks", 1e4),
                               ("30 ks", 3e4),
                            ])

    def set_GUIparameter(self):
    
        gui_parameter = {
                         "SweepMode": ["None", "Frequency in Hz", "Time constant in s", "Sensitivity in V", "Sensitivity in A"],
                         "Source": ["Internal", "External (Sine)", "External (TTL Rising)", "External (TTL Falling)"],
                         "Input": ["A", "A-B", "I@10^6", "I@10^8"],
                         "Reserve": ["Low Noise", "Normal", "High Reserve"],
                         "Filter1": ["No Filter", "Line", "2xLine", "Line + 2xLine"],
                         "Filter2": ["No Sync Filter", "Sync Filter"],
                         "Channel1": ["None", "X", "R", "X noise", "AUX IN 1", "AUX IN 2"],
                         "Channel2": ["None", "Y", "Phi", "Y noise", "AUX IN 3", "AUX IN 4"],
                         "TimeConstant": list(self.timeconstants.keys()),  # ["Auto time", "As is"] +
                         # "Gain": ["Auto gain", "As is"] + list(self.sensitivities.keys()),
                         "Sensitivity": ["Auto", "As is"] + list(self.sensitivities_voltages.keys()) + list(self.sensitivities_currents.keys()), 
                         "Slope": ["6dB", "12dB", "18dB", "24dB"],
                         "Coupling": ["AC", "DC"],
                         "Ground": ["Float", "Ground"],
                         "WaitTimeConstants": 4.0,
                        }
                        
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):
    
        self.sweepmode = parameter["SweepMode"]
        self.source = parameter["Source"]
        self.input = parameter["Input"]
        self.coupling = parameter["Coupling"]
        self.slope = parameter["Slope"]
        self.ground = parameter["Ground"]
        self.reserve = parameter["Reserve"]
        self.filter1 = parameter["Filter1"]
        self.filter2 = parameter["Filter2"]
        self.gain = parameter["Gain"]
        self.sensitivity = parameter["Sensitivity"]
        self.timeconstant = parameter["TimeConstant"]
        self.channel1 = parameter["Channel1"]
        self.channel2 = parameter["Channel2"]
        self.waittimeconstants = float(parameter["WaitTimeConstants"])
        
        self.variables = ["Magnitude", "Phase", "Frequency", "X", "Y"]

        if self.channel1 != "None":
            # in case X is selected at channel 1, it needs a different variable name than the default X variable
            self.variables.append(("Ch1-" if (self.channel1 == "X") else "") + self.channel1)
        if self.channel2 != "None":
            # in case Y is selected at channel 1, it needs a different variable name than the default Y variable
            self.variables.append(("Ch2-" if (self.channel2 == "Y") else "") + self.channel2)

        self.variables.append("TimeConstant")
        self.variables.append("Sensitivity")
        self.units = []
        
        if self.input == "A" or self.input == "A-B":
            self.add_units_channels("V")
            self.input_quantity = "Voltage"
            
        else:
            self.add_units_channels("A")
            self.input_quantity = "Current"

        # Input:
        # "A" -> [V]
        # "A-B" -> [V]
        # "I@10^6" -> [A]
        # "I@10^8" -> [A]

        # Channel 1:
        # "None" -> no variable and unit
        # "X" -> [V or A]
        # "R" -> [V or A]
        # "X noise" -> [V/sqrt(Hz) or A/sqrt(Hz)]
        # "AUX IN 1" -> [V]
        # "AUX IN 2" -> [V]

        # Channel2:
        # "None" -> no variable and unit
        # "Y" -> [V or A]
        # "Phi" -> [deg]
        # "Y noise" -> [V/sqrt(Hz) or A/sqrt(Hz)]
        # "AUX IN 3" -> [V]
        # "AUX IN 4" -> [V]
        
    def add_units_channels(self, AorV="V"):
    
        self.units.append(AorV)
        self.units += ["°", "Hz"]
        self.units += [AorV, AorV]

        if self.channel1 == "None":
            pass

        elif self.channel1 == "X" or self.channel1 == "R":
            self.units.append(AorV)
            
        elif self.channel1 == "X noise":
            self.units.append(AorV+"/sqrt(Hz)")
            
        elif self.channel1 == "AUX IN 1" or self.channel1 == "AUX IN 2":
            self.units.append("V")

        if self.channel2 == "None":
            pass

        elif self.channel2 == "Y":
            self.units.append(AorV)
            
        elif self.channel2 == "Phi":
            self.units.append("°")
            
        elif self.channel2 == "Y noise":
            self.units.append(AorV+"/sqrt(Hz)")
            
        elif self.channel2 == "AUX IN 3" or self.channel2 == "AUX IN 4":
            self.units.append("V") 
            
        self.units += ["s"]
        self.units += [AorV]

    def initialize(self): 

        self.identification = self.get_identification()
        # print("Identification:", self.identification)

        if "SR810" in self.identification and self.channel2 != "None":
            return Exception("Model SR810 has only one channel. Please select 'None' for second channel.")
        
        self.port.write("KCLK 0")  # stop key click
        self.port.write("ALRM 0")  # stop alarm
                        
    def configure(self):
        # command-dictionary makes it quite easy to handover a parameter
        self.port.write(self.commands[self.source])
        self.port.write(self.commands[self.input])
        self.port.write(self.commands[self.coupling])
        self.port.write(self.commands[self.slope])
        self.port.write(self.commands[self.ground])
        self.port.write(self.commands[self.reserve])
        self.port.write(self.commands[self.filter1])
        self.port.write(self.commands[self.filter2])

        if self.sensitivity == "Auto" or self.sensitivity == "As is":
            pass
        else:
            if (self.input_quantity == "Current") and "A" in self.sensitivity:
                self.port.write(self.sensitivities_all[self.sensitivity])
            elif (self.input_quantity == "Voltage") and "V" in self.sensitivity:
                self.port.write(self.sensitivities_all[self.sensitivity])
            else:
                raise Exception('The input mode and sensitivity should match.')

        if self.timeconstant not in ["Auto time", "As is"] and self.timeconstant in self.timeconstants:
            self.port.write(self.timeconstants[self.timeconstant])

    def reconfigure(self, parameter={}, keys=[]):
        """ 
        function to be overloaded if needed
        
        if a GUI parameter changes after replacement with global parameters, the device needs to be reconfigured.
        Default behavior is that all parameters are set again and 'configure' is called.
        The device class maintainer can redefine/overwrite 'reconfigure' with a more individual procedure. 
        """

        """
        if self.sweepmode == "Time constant in s":
            try:
                if self.value == "None":
                    time_constant = self.timeconstants_values[self.timeconstant]
                    if time_constant <= 1:
                        pass
                else:
                    if self.value <= 1:
                        pass
            except:
                time_constant = self.timeconstants_values[self.timeconstant]
                if time_constant <= 1:
                    pass
        else:
            time_constant = self.timeconstants_values[self.timeconstant]
            if time_constant <= 1:
                pass
        """

        self.sensitivity = parameter["Sensitivity"]
        if "Sensitivity" in keys:
            if self.sensitivity == "Auto" or self.sensitivity == "As is":
                pass
            else:
                try:
                    sensitivity = float(self.sensitivity)
                    self.set_sensitivity(sensitivity)
                except:
                    if (self.input_quantity == "Current") and "A" in self.sensitivity:
                        self.set_sensitivity(self.sensitivity)
                    elif (self.input_quantity == "Voltage") and "V" in self.sensitivity:
                        self.set_sensitivity(self.sensitivity)
                    else:
                        raise Exception('The input mode and sensitivity should match.')
          
    def apply(self): 
        if self.sweepmode.startswith("Frequency"):
            self.port.write("FREQ %s" % self.value)
        
        elif self.sweepmode == "Time constant in s":
            
            conversion = {
                1e+3: "ks",
                1e0: "s",
                1e-3: "ms",
                1e-6: "µs",
                }

            for exp_step in list(conversion.keys()):
                
                if self.value >= 0.65*exp_step:
            
                    number = round(self.value/exp_step, 0)

                    for multiplicator in [1, 10, 100]:
                    
                        if number <= 2 * multiplicator:
                            number = 1 * multiplicator
                            break
                               
                        elif number <= 6.5 * multiplicator:
                            number = 3 * multiplicator
                            break
                    break

            self.timeconstant = str(number) + " " + conversion[exp_step]
            self.port.write(self.timeconstants[self.timeconstant])
            
        elif self.sweepmode.startswith("Sensitivity"):
            self.set_sensitivity(self.value)

        """
            sensitivity_unit = self.sweepmode[-1]
            
            conversion = {
                1e0 : ("V or ", "muA"),
                1e-3: ("mV or ", "nA"),
                1e-6: ("muV or ", "pA"),
                1e-9: ("nV or ", "fA"),
                }
            for exp_step in list(conversion.keys()):
                #print("self.value", self.value)
                if self.value >= 0.75*exp_step:
            
                    number = round(self.value/exp_step,0)
                    
                    #print(number)
                    
                    for multiplicator in [1, 10, 100]:
                    
                        if number <= 1.5 * multiplicator:
                            number = 1 * multiplicator
                            break
                            
                        elif number <= 3.5 * multiplicator:
                            number = 2 * multiplicator
                            break
                        
                        elif number <= 7.5 * multiplicator:
                            number = 5 * multiplicator
                            break
                           
                    break

            self.sensitivity = str(number) + " " + conversion[exp_step][0] + str(number) + " " + conversion[exp_step][1]
            #print(self.sensitivity)
            self.port.write(self.sensitivities_all[self.sensitivity])
        """

    def adapt(self):
    
        self.is_auto_gain = False

        if self.sensitivity == "Auto":
            self.port.write("AGAN")
            self.port.write("*STB? 1") 
            self.is_auto_gain = True
                       
    def adapt_ready(self):
    
        if self.is_auto_gain:
            self.port.read()  # read answer of status byte query, should be 1 and thus, Auto Gain is set
               
        self.time_ref = time.perf_counter()

    def trigger_ready(self):
        # make sure that at least several time constants have passed since 'Auto sensitivity' was called
        delta_time = (self.waittimeconstants * self.unit_to_float(self.timeconstant)) - (time.perf_counter()-self.time_ref)
        if delta_time > 0.0:
            # wait several time constants to allow for a renewal of the result
            time.sleep(delta_time)
    
    def measure(self):
        self.port.write("SNAP?1,2,3,4,9")
        if self.channel1 != "None":
            if "SR810" in self.identification:
                self.port.write("OUTR?")
            else:
                self.port.write("OUTR?1")
        if self.channel2 != "None":
            self.port.write("OUTR?2")
        self.port.write("SENS?")
        self.port.write("OFLT?")  # time constant
        
    def read_result(self):
        self.X, self.Y, self.R, self.Phi, self.F = map(float, self.port.read().split(","))
        if self.channel1 != "None":
            self.Ch1 = float(self.port.read())
        if self.channel2 != "None":
            self.Ch2 = float(self.port.read())
        self.sens = self.get_sensitivity()
        self.time_constant = self.get_timeconstant()
    
    def call(self):
        results = [self.R, self.Phi, self.F, self.X, self.Y]
        if self.channel1 != "None":
            results += [self.Ch1]
        if self.channel2 != "None":
            results += [self.Ch2]
        results += [self.time_constant]
        results += [self.sens]

        return results

    @staticmethod
    def unit_to_float(unit):
        """Takes a string representing a sensitivity or time constant and gives back a corresponding float"""
        chars = OrderedDict([ 
                                ("V", ""),
                                ("A", ""),
                                ("s", ""),
                                (" ", ""),
                                ("p", "e-12"),
                                ("n", "e-9"),
                                ("µ", "e-6"),
                                ("mu", "e-6"),
                                ("m", "e-3"),
                                ("k", "e3"),
                            ])

        for char in chars:
            unit = unit.replace(char, chars[char])
        return float(unit)
        
    def get_identification(self):

        self.port.write("*IDN?")
        return self.port.read()

    def set_sensitivity(self, sensitivity):

        if self.input_quantity == "Voltage":  # if sensitivity is already at max limit
            if float(sensitivity) > 1:
                self.sensitivity = str(1) + " V"
                self.port.write(self.sensitivities_voltages[self.sensitivity])
                return
            else:
                conversion = {
                    1e0 : "V",
                    1e-3: "mV",
                    1e-6: "muV",
                    1e-9: "nV",
                    }
        else:
            if float(sensitivity) > 1e-6:  # if sensitivity is already at max limit
                self.sensitivity = str(1) + " muA"
                self.port.write(self.sensitivities_currents[self.sensitivity])
                return
            else:
                conversion = {
                    1e0 : "muA",
                    1e-3: "nA",
                    1e-6: "pA",
                    1e-9: "fA",
                    }
        for exp_step in list(conversion.keys()):
            if sensitivity >= 0.75*exp_step:
        
                number = round(sensitivity/exp_step,0)

                for multiplicator in [1, 10, 100]:
                
                    if number <= 1.5 * multiplicator:
                        number = 1 * multiplicator
                        break
                    elif number <= 3.5 * multiplicator:
                        number = 2 * multiplicator
                        break
                    elif number <= 7.5 * multiplicator:
                        number = 5 * multiplicator
                        break
                       
                break

        self.sensitivity = str(number) + " " + conversion[exp_step]
        if self.input_quantity == "Voltage":
            self.port.write(self.sensitivities_voltages[self.sensitivity])
        else:
            self.port.write(self.sensitivities_currents[self.sensitivity])

    def get_sensitivity(self):
        temp_sens_dev = self.port.read()
        if self.input_quantity == "Current":
            # temp_sens_set is then a python set
            temp_sens_set = {s for s in self.sensitivities_currents if self.sensitivities_currents[s] == ("SENS " + temp_sens_dev)}
        if self.input_quantity == "Voltage":
            # temp_sens_set is then a python set
            temp_sens_set = {s for s in self.sensitivities_voltages if self.sensitivities_voltages[s] == ("SENS " + temp_sens_dev)}

        temp_sens = self.sens_string_to_float(temp_sens_set)

        return temp_sens

    def get_timeconstant(self):
        temp_time_constant_dev = (self.port.read())
        # temp_time_constant_set is then a python set
        temp_time_constant_set = {s for s in self.timeconstants if self.timeconstants[s] == ("OFLT " + temp_time_constant_dev)}
        temp_time_constant = self.time_constant_string_to_float(temp_time_constant_set)

        return temp_time_constant

    def sens_string_to_float(self, sensSet):
        """Takes a sensitivity string and extracts the float number"""
        sensString = sensSet.pop()
        temp_correct_sensitivity_value = self.unit_to_float(sensString)

        return temp_correct_sensitivity_value

    def time_constant_string_to_float(self, time_constant_set):
        """Takes a time constant string and extracts the float number"""

        time_constant_string = time_constant_set.pop()
        time_constant = self.timeconstants_values[time_constant_string]

        return time_constant

    def sens_string_to_float_old(self, sens_set):
        """Takes a sensitivity string and extracts the float number"""

        sens_string = sens_set.pop()
        if self.units[0] == "V":
            index = sens_string.find("or")
            temp_correct_sensitivity_str = sens_string[:index]
            temp_correct_sensitivity_value = self.unit_to_float(temp_correct_sensitivity_str)
        else:
            index = sens_string.find("or") + len("or")
            temp_correct_sensitivity_str = sens_string[index:]
            temp_correct_sensitivity_value = self.unit_to_float(temp_correct_sensitivity_str)

        return temp_correct_sensitivity_value
