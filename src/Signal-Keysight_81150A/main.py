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
# Type: Signal
# Device: Keysight 811x0A

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = '811x0A'

        self.port_manager = True
        self.port_types = ['USB', 'GPIB', 'TCPIP']
        self.port_properties = {"timeout": 1,
                                # "delay": 0.05,
                                # "Exception": False,
                                }
        # to be defined by user
        # self.commands = {"Sine": "SIN",
        #                  "Square": "SQU",
        #                  "Ramp": "RAMP",
        #                  "Pulse": "PULS",
        #                  "Noise": "NOIS",
        #                  "DC": "DC",
        #                  # "Arbitrary": "ARB",
        #                  "Period [s]": "PER",
        #                  "Frequency [Hz]": "FREQ",
        #                  "HiLevel [V]": "VOLT:HIGH",
        #                  "LoLevel [V]": "VOLT:LOW",
        #                  "Amplitude [V]": "VOLT",
        #                  "Offset [V]": "VOLT:OFFS",
        #                  }

        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

    def set_GUIparameter(self):
        GUIparameter = {
            "SweepMode": ["Frequency in Hz", "Period in s", "Amplitude in V", "HiLevel in V", "Offset in V", "LoLevel in V",
                          "Pulse width in s", "Duty cycle in %", "Delay in s", "Phase in deg", "None"],
            "PeriodFrequency": ["Frequency in Hz", "Period in s"],
            "PeriodFrequencyValue": 1000,
            "AmplitudeHiLevel": ["Amplitude in V", "HiLevel in V"],
            "AmplitudeHiLevelValue": 1.0,
            "OffsetLoLevel": ["Offset in V", "LoLevel in V"],
            "OffsetLoLevelValue": 0.0,
            "DelayPhase": ["Phase in deg", "Delay in s"],
            "DelayPhaseValue": 0,
            "DutyCyclePulseWidth": ["Duty cycle in %", "Pulse width in s"],
            "DutyCyclePulseWidthValue": 50,
            "Waveform": ["Sine", "Square", "Ramp", "Pulse", "Noise", "DC"],
            "Impedance": ["High-Z", "50 Ohm"],
            "Channel": ["Ch1", "Ch2"],
            # "Trigger": ["Not supported yet"]
        }
        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        # could be part of the MeasClass
        self.channel = parameter['Channel'][-1]
        self.sweep_mode = parameter['SweepMode']
        self.waveform = parameter['Waveform']
        self.periodfrequency = parameter['PeriodFrequency']
        self.periodfrequencyvalue = float(parameter['PeriodFrequencyValue'])
        self.amplitudehilevel = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue = float(parameter['AmplitudeHiLevelValue'])
        self.offsetlolevel = parameter['OffsetLoLevel']
        self.offsetlolevelvalue = float(parameter['OffsetLoLevelValue'])
        self.dutycyclepulsewidth = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue = float(parameter['DutyCyclePulseWidthValue'])
        self.delayphase = parameter['DelayPhase']
        self.delayphasevalue = float(parameter['DelayPhaseValue'])
        self.impedance = parameter['Impedance']

        index_to_split_unit = self.sweep_mode.rfind(" ")
        self.variables = [self.sweep_mode[:index_to_split_unit]]



        # must be part of the MeasClass
        if self.sweep_mode == 'Frequency in Hz':
            self.units = ['Hz']
        elif self.sweep_mode == 'Period in s':
            self.units = ['s']
        elif self.sweep_mode == 'DutyCycle in %':
            self.units = ['%']
        elif self.sweep_mode == 'None':
            self.variables = []
            self.units = []
            self.plottype = []  # True to plot data
            self.savetype = []  # True to save data
        else:
            self.units = ['V']

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def initialize(self):

        pass

    def configure(self):

        # Todo: There is some confusion regarding the output and load impedance. Check user maunal page no. 110.
        if self.impedance == "High-Z":
            self.set_source_impedance(self.channel, 'MAX')
        if self.impedance == "50 Ohm":
            self.set_source_impedance(self.channel, '50')

        # Autoranging the voltage port
        self.set_autorange_on(self.channel)

        # if self.sweep_mode == "DelayPhase":
        # self.delayphase = self.value

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

        waveform_type = self.commands[self.waveform]

        self.apply_waveform(self.channel, waveform_type, self.frequency, self.amplitude, self.offset)

        if self.waveform == "Pulse":
            if self.dutycyclepulsewidth == "Pulse width in s":
                self.set_pulse_width(self.channel, self.dutycyclepulsewidthvalue)

            if self.dutycyclepulsewidth == "Duty cycle in %":
                self.set_pulse_duty_cycle(self.channel, self.dutycyclepulsewidthvalue)

        elif self.waveform == "Square":
            if self.dutycyclepulsewidth == "Duty cycle in %":
                self.set_square_duty_cycle(self.channel, self.dutycyclepulsewidthvalue)

        if self.delayphase == "Delay in s":
            self.phase = self.delayphasevalue * self.frequency * 360.0


        elif self.delayphase == "Phase in deg":
            self.phase = self.delayphasevalue

        if not waveform_type == "DC":
            self.set_phase(self.channel, self.phase)

    def deinitialize(self):
        pass

    def poweron(self):
        self.set_output_on(self.channel)

    def poweroff(self):
        self.set_output_off(self.channel)
        # we have to ask to really switch off and we do not know why
        # self.port.write("OUTP?")
        # answer = self.port.read()
        # print(answer)

    def apply(self):

        if self.sweep_mode == 'None':
            pass

        else:

            if self.sweep_mode == "Frequency in Hz":
                self.periodfrequency = "Frequency in Hz"
                self.periodfrequencyvalue = self.value

            if self.sweep_mode == "Period in s":
                self.periodfrequency = "Frequency in Hz"
                self.periodfrequencyvalue = 1.0 / self.value

            if self.sweep_mode == "Amplitude in V":
                self.amplitudehilevel = "Amplitude in V"
                self.amplitudehilevelvalue = self.value

            if self.sweep_mode == "HiLevel in V":
                self.amplitudehilevel = "HiLevel in V"
                self.amplitudehilevelvalue = self.value

            if self.sweep_mode == "Offset in V":
                self.offsetlolevel = "Offset in V"
                self.offsetlolevelvalue = self.value

            if self.sweep_mode == "LoLevel in V":
                self.offsetlolevel = "LoLevel in V"
                self.offsetlolevelvalue = self.value

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
                    self.offset = (self.amplitudehilevelvalue + self.offsetlolevelvalue) / 2.0

            self.set_frequency(self.channel, self.frequency)
            self.set_amplitude(self.channel, self.amplitude)
            self.set_offset(self.channel, self.offset)

            if self.sweep_mode == "Pulse width in s":
                self.dutycyclepulsewidthvalue = self.value

            if self.sweep_mode == "Duty cycle in %":
                self.dutycyclepulsewidthvalue = self.value

            if self.waveform == "Pulse":
                if self.dutycyclepulsewidth == "Pulse width in s":
                    self.set_pulse_width(self.channel, self.dutycyclepulsewidthvalue)

                if self.dutycyclepulsewidth == "Duty cycle in %":
                    self.set_pulse_duty_cycle(self.channel, self.dutycyclepulsewidthvalue)

            if self.sweep_mode == "Delay in s":
                self.phase = self.value * self.frequency * 360.0
                self.set_phase(self.channel, self.phase)

            if self.sweep_mode == "Phase in deg":
                self.phase = self.value
                self.set_phase(self.channel, self.phase)

    def call(self):

        if self.sweep_mode == 'None':
            return []
        else:
            reply = self.inquiry_waveform(self.channel)
            answer = reply[reply.find('+'):].split(",")  # Todo: double-check this. The reply format is:
            # "SIN+5.0000000000000E+03,+3.0000000000000E+00,-2.5000000000000E+00"

            frequency, amplitude, offset = map(float, answer)

            if self.sweep_mode == "Frequency in Hz":
                returnvalue = frequency

            if self.sweep_mode == "Period in s":
                returnvalue = 1.0 / frequency

            if self.sweep_mode == "Amplitude in V":
                returnvalue = amplitude

            if self.sweep_mode == "HiLevel in V":
                returnvalue = offset + amplitude / 2.0

            if self.sweep_mode == "Offset in V":
                returnvalue = offset

            if self.sweep_mode == "LoLevel in V":
                returnvalue = offset - amplitude / 2.0

            if self.sweep_mode == "Duty cycle in %" or self.sweep_mode == "Pulse width in s":
                returnvalue = self.value

            if self.sweep_mode == "Delay in s" or self.sweep_mode == "Phase in deg":
                returnvalue = self.value

            return [returnvalue]

    """ here, convenience functions start """

    def get_identification(self):
        """
        This function return the identification number of the instrument.
        Returns:
            str: identification number
        """
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer

    def get_options(self):
        """
        This function returns the options included in the instrument.
        Returns:
            str: option number
        """
        self.port.write("*OPT?")
        answer = self.port.read()
        return answer

    def reset_instrument(self):
        """
        This function resets the device to its default settings.
        Returns:
            None
        """
        self.port.write("*RST")

    def set_display_on(self):
        """
        This function turns the local display on.
        Returns:
            None
        """
        self.port.write(":DISP ON")

    def set_display_off(self):
        """
        This function turns the local display off. According to the manual, this will increase programming speed.
        Returns:
            None
        """
        self.port.write(":DISP OFF")

    def set_text(self, txt):
        """
        This function displays a text on the front panel display.
        Args:
            txt: str

        Returns:
            None
        """
        self.port.write("DISP:TEXT '%s'" % str(txt))

    def clear_text(self):
        """
        This function clears displayed text from front panel. You should turn the display on afterwards.
        Returns:
            None
        """
        self.port.write("DISP:TEXT:CLE")

    def set_local_on(self):
        """
        This function activates the local panel.
        Returns:
            None
        """
        self.port.write("SYST:COMM:RLST LOC")

    def set_output_on(self, channel):
        """
        This function turns on the front-panel output connector for a selected channel.
        Args:
            channel: int or str

        Returns:
            None
        """
        self.port.write("OUTP%s ON" % channel)

    def set_output_off(self, channel):
        """
        This function turns off the front-panel output connector for a selected channel.
        Args:
            channel: int or str

        Returns:
            None
        """
        self.port.write("OUTP%s OFF" % channel)

    def apply_waveform(self, channel, waveform_type, frequency, amplitude, offset):
        """
        This function sends apply command to the instrument. Apply command performs a series of operations: puts the
        instrument in CW mode, turns on the output, enables voltage autorange, for square waveform, the duty cycle is
        set to 50%, and for ramp, the symmetry setting is set to 100%.

        Args:
            channel: int or str
            waveform_type: str
            frequency: float or str
            amplitude:float or str
            offset:float or str

        Returns:
            None
        """
        if waveform_type in ['SIN', 'SINusoid', 'SQU', 'SQUare', 'RAMP', 'PULS', 'PULSe', 'NOIS', 'NOISe', 'DC', 'USER']:
            self.port.write("SOUR%s:APPL:%s %s, %s, %s" % (channel, waveform_type, frequency, amplitude, offset))
        else:
            raise Exception("The input waveform is not valid.")

    def inquiry_waveform(self, channel):
        """
        This function reads and returns waveform parameters frequency, amplitude, and offset.
        Args:
            channel: int or str

        Returns:
            str: answer
        """
        self.port.write("SOUR%s:APPL?" % channel)
        answer = self.port.read()
        return answer

    def set_frequency(self, channel, frequency):
        """
        This function sets frequency.
        Args:
            channel: int or str
            frequency: float or str

        Returns:
            None
        """
        self.port.write("SOUR%s:FREQ %s" % (channel, frequency))

    # def get_frequency(self, channel):
    #     self.port.write("SOUR%s:FREQ?" % channel)
    #     answer = self.port.read()
    #     return answer

    def set_amplitude(self, channel, amplitude):
        """
        This function sets amplitude.
        Args:
            channel: int or str
            amplitude: float or str

        Returns:
            None
        """
        self.port.write("SOUR%s:VOLT %s" % (channel, amplitude))

    # def get_amplitude(self, channel):
    #     self.port.write("SOUR%s:VOLT?" % channel)
    #     answer = self.port.read()
    #     return answer

    def set_offset(self, channel, offset):
        """
        This function sets offset.
        Args:
            channel: int or str
            offset: float or str

        Returns:
            None
        """
        self.port.write("SOUR%s:VOLT:OFFS %s" % (channel, offset))

    # def get_offset(self, channel):
    #     self.port.write("SOUR%s:VOLT:OFFS?" % channel)
    #     answer = self.port.read()
    #     return answer

    def set_pulse_width(self, channel, pulse_width):
        """
        This function sets pulse width. Use it only when the applied waveform is pulse.
        Args:
            channel: int or str
            pulse_width: float or str

        Returns:
            None
        """
        self.port.write("SOUR%s:FUNC:PULS:WIDT %s " % (channel, pulse_width))

    def set_pulse_duty_cycle(self, channel, duty_cycle):
        """
        This function sets pulse duty cycle. Use it only when the applied waveform is pulse.
        Args:
            channel: int or str
            duty_cycle: float or str

        Returns:
            None
        """
        self.port.write("SOUR%s:FUNC:PULS:DCYC %s " % (channel, duty_cycle))

    def set_square_duty_cycle(self, channel, duty_cycle):
        """
        This function sets square duty cycle. Use it only when the applied waveform is square.
        Args:
            channel: int or str
            duty_cycle: float or str

        Returns:
            None
        """
        self.port.write("SOUR%s:FUNC:SQU:DCYC %s " % (channel, duty_cycle))

    def set_phase(self, channel, phase):
        """
        This function sets phase. Don't use it with DC as output.
        Args:
            channel: int or str
            phase: float or str

        Returns:
            None
        """
        self.port.write("SOUR%s:PHAS %s DEG" % (channel, phase))

    def set_source_impedance(self, channel, impedance):
        """
        This function sets output impedance of the instrument.
        Args:
            channel: int or str
            impedance: str

        Returns:
            None
        """
        self.port.write("OUTP%s:LOAD %s" % (channel, impedance))

    def set_autorange_on(self, channel):
        """
        This function sets on the voltage autorange.
        Args:
            channel: int or str

        Returns:
            None
        """
        self.port.write("SOUR%s:VOLT:RANG:AUTO ON" % channel)