# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank TU Dresden/Jacob Hille for providing the initial version of this driver.

# SweepMe! driver
# * Module: Signal
# * Instrument: Siglent SDG Series

from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = ["USB", "TCPIP"]
        self.port_identifications = ['']

        # to be defined by user 
        self.commands = {
            "Sine": "SINE",
            "Square": "SQUARE",
            "Ramp": "RAMP",
            "Pulse": "PULSE",
            "Noise": "NOISE",
            "DC": "DC",
            "Arbitrary": "ARB",
        }

        self.waveform_standard_list = ["Sine", "Square", "Ramp", "Pulse", "Noise", "DC"]

        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Channel": ["CH1", "CH2"],
            "SweepMode": ["None",
                          "Frequency in Hz",
                          "Period in s",
                          "Amplitude in V",
                          "High level in V",
                          "Offset in V",
                          "Low level in V",
                          "Pulse width in s",
                          "Duty cycle in %",
                          "Delay in s",
                          "Phase in deg",
                          ],
            "PeriodFrequency": ["Frequency in Hz", "Period in s"],
            "PeriodFrequencyValue": 1000,
            "AmplitudeHiLevel": ["Amplitude in V", "High level in V", "Mean level in V"],
            "AmplitudeHiLevelValue": 1.0,
            "OffsetLoLevel": ["Offset in V", "Low level in V ", "Standard deviation in V"],
            "OffsetLoLevelValue": 0.0,
            # TODO Delay in ms or µs
            "DelayPhase": ["Phase in deg", "Delay in s"],
            "DelayPhaseValue": 0,
            # TODO Pulsewidth in ms or µs
            "DutyCyclePulseWidth": ["Duty cycle in %", "Pulse width in s"],
            "DutyCyclePulseWidthValue": 50,
            # Arbitrary not supported yet
            "Waveform": ["Sine", "Square", "Ramp", "Pulse", "Noise", "DC", "Arbitrary: <file name>"],
            "Impedance": ["High-Z", "50 Ohm"],
            # "Trigger": ["Not supported yet"]
        }

    def get_GUIparameter(self, parameter={}):
        # Channel Names have to be {C1, C2}
        self.channel = "C" + parameter['Channel'][-1]
        self.sweep_mode = parameter['SweepMode']
        self.waveform = parameter['Waveform']
        self.periodfrequency = parameter['PeriodFrequency']
        self.periodfrequencyvalue = float(parameter['PeriodFrequencyValue'])
        self.amplitudehilevel = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue = float(parameter['AmplitudeHiLevelValue'])
        self.offsetlolevel = parameter['OffsetLoLevel']
        self.offsetlolevelvalue = float(parameter['OffsetLoLevelValue'])
        # TODO pulsewidth in ms or µs
        self.dutycyclepulsewidth = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue = float(parameter['DutyCyclePulseWidthValue'])
        # TODO delay in ms or µs
        self.delayphase = parameter['DelayPhase']
        self.delayphasevalue = float(parameter['DelayPhaseValue'])
        self.impedance = parameter['Impedance']

        self.shortname = 'SDG 2000X ' + self.channel

        if self.sweep_mode == 'None':
            self.variables = []
            self.units = []
            self.plottype = []  # True to plot data
            self.savetype = []  # True to save data
        else:
            index_to_split_unit = self.sweep_mode.find(" in")
            self.variables = [self.sweep_mode[:index_to_split_unit]]
            if self.sweep_mode == 'Frequency in Hz':
                self.units = ['Hz']
            elif self.sweep_mode == 'Period in s':
                self.units = ['s']
            elif self.sweep_mode == 'Duty cycle in %':
                self.units = ['%']
            else:
                self.units = ['V']

    def initialize(self):

        pass
        # self.port.write("*IDN?")
        # print(self.port.read())

    def configure(self):

        # Setting the impedance / load of the channel
        if self.impedance == "High-Z":
            self.port.write(f"{self.channel}:OUTP LOAD,HZ")
        if self.impedance == "50 Ohm":
            self.port.write(f"{self.channel}:OUTP LOAD,50")

        # Handling alternative menu options

        if self.periodfrequency == "Period in s":
            self.frequency = 1.0 / self.periodfrequencyvalue
        else:
            self.frequency = self.periodfrequencyvalue

        if self.amplitudehilevel == "Amplitude in V":
            self.amplitude = self.amplitudehilevelvalue

            if self.offsetlolevel == "Offset in V":
                self.offset = self.offsetlolevelvalue
            else:
                self.offset = (self.amplitudehilevelvalue / 2.0 + self.offsetlolevelvalue)

        else:
            if self.offsetlolevel == "Offset in V":
                self.amplitude = (self.amplitudehilevelvalue - self.offsetlolevelvalue) * 2.0
                self.offset = self.offsetlolevelvalue
            else:
                self.amplitude = self.amplitudehilevelvalue - self.offsetlolevelvalue
                self.offset = (self.amplitudehilevelvalue - self.offsetlolevelvalue) / 2.0

        # mean level and standard deviation are used for noise signals
        # TODO error handling if mean and stdev is used for uncompatible wavetypes
        if self.amplitudehilevel == "Mean in V":
            self.mean = self.amplitudehilevelvalue
        if self.offsetlolevel == "Standard deviation in V":
            self.stdev = self.offsetlolevelvalue

        # Set waveform with standard parameters        
        waveform_type = self.commands[self.waveform]
        self.port.write(f"{self.channel}:BSWV "
                        f"WVTP,{waveform_type},"
                        f"FRQ,{self.frequency},"
                        f"AMP,{self.amplitude},"
                        f"OFST,{self.offset}")

        # handling parameters only compatible with specific wavetypes
        # TODO maybe error message if incompatible settings are chosen, however the device is very forgiving
        if self.waveform == "Noise":
            if not hasattr(self, 'mean') or not hasattr(self, 'stdev'):
                raise Exception(f"Noise requires setting a Mean level in V and a Standard deviation in V!")

            self.port.write(f"{self.channel}:BSWV MEAN,{self.mean},STDEV,{self.stdev}")

        elif self.waveform == "Pulse":
            if self.dutycyclepulsewidth == "Pulse width in s":
                self.port.write(f"{self.channel}:BSWV WIDTH,{self.dutycyclepulsewidthvalue}")
            elif self.dutycyclepulsewidth == "Duty cycle in %":
                self.port.write(f"{self.channel}:BSWV DUTY,{self.dutycyclepulsewidthvalue}")

        elif self.waveform == "Square":
            if self.dutycyclepulsewidth == "Duty cycle in %":
                self.port.write(f"{self.channel}:BSWV DUTY,{self.dutycyclepulsewidthvalue}")

        if self.delayphase == "Delay in s":
            self.phase = self.delayphasevalue * self.frequency * 360.0

        elif self.delayphase == "Phase in deg":
            self.phase = self.delayphasevalue

        if waveform_type != "DC":
            self.port.write(f"{self.channel}:BSWV PHSE,{self.phase}")

    def deinitialize(self):
        pass

    def poweron(self):
        self.port.write(f"{self.channel}:OUTP ON")

    def poweroff(self):
        self.port.write(f"{self.channel}:OUTP OFF")

    def apply(self):

        if self.sweep_mode != 'None':

            # updating values from sweep table 
            if self.sweep_mode == "Frequency in Hz":
                self.periodfrequency = "Frequency in Hz"
                self.periodfrequencyvalue = self.value

            elif self.sweep_mode == "Period in s":
                self.periodfrequency = "Frequency in Hz"
                self.periodfrequencyvalue = 1.0 / self.value

            elif self.sweep_mode == "Amplitude in V":
                self.amplitudehilevel = "Amplitude in V"
                self.amplitudehilevelvalue = self.value

            elif self.sweep_mode == "High level in V":
                self.amplitudehilevel = "High Level in V"
                self.amplitudehilevelvalue = self.value

            elif self.sweep_mode == "Offset in V":
                self.offsetlolevel = "Offset in V"
                self.offsetlolevelvalue = self.value

            elif self.sweep_mode == "Low level V":
                self.offsetlolevel = "Low level in V"
                self.offsetlolevelvalue = self.value

            if self.periodfrequency == "Period in s":
                self.frequency = 1.0 / self.periodfrequencyvalue
            else:
                self.frequency = self.periodfrequencyvalue

            # Recalculating amplitudes and offset
            if self.amplitudehilevel == "Amplitude in V":
                self.amplitude = self.amplitudehilevelvalue

                if self.offsetlolevel == "Offset in V":
                    self.offset = self.offsetlolevelvalue
                else:
                    self.offset = (self.amplitudehilevelvalue / 2.0 + self.offsetlolevelvalue)
            else:
                if self.offsetlolevel == "Offset in V":
                    self.amplitude = (self.amplitudehilevelvalue - self.offsetlolevelvalue) * 2.0
                    self.offset = self.offsetlolevelvalue
                else:
                    self.amplitude = self.amplitudehilevelvalue - self.offsetlolevelvalue
                    self.offset = (self.amplitudehilevelvalue + self.offsetlolevelvalue) / 2.0

            self.port.write(f"{self.channel}:BSWV FRQ,{self.frequency},AMP,{self.amplitude},OFST,{self.offset}")

            if self.sweep_mode == "Pulse width in s":
                self.dutycyclepulsewidthvalue = self.value

            elif self.sweep_mode == "Duty cycle in %":
                self.dutycyclepulsewidthvalue = self.value

            # Handling parameters compatible only with specific wavetypes

            if self.waveform == "Pulse":
                if self.dutycyclepulsewidth == "Pulse width in s":
                    self.port.write(f"{self.channel}:BSWV WIDTH,{self.dutycyclepulsewidthvalue}")
                if self.dutycyclepulsewidth == "Duty cycle in %":
                    self.port.write(f"{self.channel}:BSWV DUTY,{self.dutycyclepulsewidthvalue}")

            elif self.waveform == "Square":
                if self.dutycyclepulsewidth == "Duty cycle in %":
                    self.port.write(f"{self.channel}:BSWV DUTY,{self.dutycyclepulsewidthvalue}")

            if self.sweep_mode == "Delay in s":
                self.phase = self.value * self.frequency * 360.0
                self.port.write(f"{self.channel}:BSWV PHSE,{self.phase}")

            elif self.sweep_mode == "Phase in deg":
                self.phase = self.value
                self.port.write(f"{self.channel}:BSWV PHSE,{self.phase}")

    def call(self):
        if self.sweep_mode != 'None':
            return float(self.value)
