# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
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
from __future__ import annotations

# SweepMe! driver
# * Module: Signal
# * Instrument: Agilent_33600A

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = ["USB", "GPIB"]
        self.port_identifications = ["Agilent Technologies,336", "Agilent Technologies,335"]

        # to be defined by user
        self.commands = {"Sine": "SIN",
                         "Square": "SQU",
                         "Ramp": "RAMP",
                         "Pulse": "PULS",
                         "Noise": "NOIS",
                         "Triangle": "TRI",
                         "DC": "DC",
                         "Arbitrary": "ARB",
                         "Period in s": "PER",
                         "Frequency in Hz": "FREQ",
                         "HiLevel in V": "VOLT:HIGH",
                         "LoLevel in V": "VOLT:LOW",
                         "Amplitude in V": "VOLT",
                         "Offset in V": "VOLT:OFFS",
                         }

        self.waveform_standard_list = ["Sine", "Square", "Ramp", "Pulse", "Noise", "Triangle", "DC"]

        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        # Measurement Parameters
        self.channel: str = "1"
        self.sweep_mode: str = "None"
        self.waveform: str = "Sine"
        self.period_frequency: str = "Frequency in Hz"
        self.period_frequency_value:float = 1000
        self.amplitude_hi_level: str = "Amplitude in V"
        self.amplitude_hi_level_value:float = 1.0
        self.offset_lo_level: str = "Offset in V"
        self.offset_lo_level_value:float = 0.0
        self.duty_cycle_pulse_width: str = "Duty cycle in %"
        self.duty_cycle_pulse_width_value:float = 50
        self.delay_phase: str = "Phase in deg"
        self.delay_phase_value:float =  0
        self.impedance: str = "High-Z"

        # These commands require Option 001, External Timebase Reference (see
        # page 258 for more information).
        # PHASe {<angle>|MINimum|MAXimum}
        # PHASe? [MINimum|MAXimum]
        # PHASe:REFerence
        # PHASe:UNLock:ERRor:STATe {OFF|ON}
        # PHASe:UNLock:ERRor:STATe?
        # UNIT:ANGLe {DEGree|RADian}
        # UNIT:ANGLe?

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Frequency in Hz", "Period in s", "Amplitude in V", "HiLevel in V", "Offset in V",
                          "LoLevel in V", "Pulse width in s", "Duty cycle in %", "Delay in s", "Phase in deg", "None"],
            "Channel": ["1", "2"],
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
            "Waveform": ["Sine", "Square", "Ramp", "Pulse", "Noise", "Triangle", "DC", "Arbitrary: <file name>"],
            "Impedance": ["High-Z", "50 Ohm"],
            # "Trigger": ["Not supported yet"]
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.channel = parameters.get("Channel", "1")
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.waveform = parameters.get("Waveform", "Sine")
        self.period_frequency = parameters.get("PeriodFrequency", "Frequency in Hz")
        self.period_frequency_value = float(parameters.get("PeriodFrequencyValue", 1000))
        self.amplitude_hi_level = parameters.get("AmplitudeHiLevel", "Amplitude in V")
        self.amplitude_hi_level_value = float(parameters.get("AmplitudeHiLevelValue", 1.0))
        self.offset_lo_level = parameters.get("OffsetLoLevel", "Offset in V")
        self.offset_lo_level_value = float(parameters.get("OffsetLoLevelValue", 0.0))
        self.duty_cycle_pulse_width = parameters.get("DutyCyclePulseWidth", "Duty cycle in %")
        self.duty_cycle_pulse_width_value = float(parameters.get("DutyCyclePulseWidthValue", 50))
        self.delay_phase = parameters.get("DelayPhase", "Phase in deg")
        self.delay_phase_value = float(parameters.get("DelayPhaseValue", 0))
        self.impedance = parameters.get("Impedance", "High-Z")

        index_to_split_unit = self.sweep_mode.rfind(" ")

        self.variables = [self.sweep_mode[:index_to_split_unit]]

        self.shortname = "33600A CH" + self.channel

        # must be part of the MeasClass
        if self.sweep_mode == "Frequency in Hz":
            self.units = ["Hz"]
        elif self.sweep_mode == "Period in s":
            self.units = ["s"]
        elif self.sweep_mode == "DutyCycle in %":
            self.units = ["%"]
        elif self.sweep_mode == "None":
            self.variables = []
            self.units = []
            self.plottype = []  # True to plot data
            self.savetype = []  # True to save data
        else:
            self.units = ["V"]

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.impedance == "High-Z":
            self.port.write("OUTP%s:LOAD INF" % (self.channel))
        if self.impedance == "50 Ohm":
            self.port.write("OUTP%s:LOAD 50" % (self.channel))

        # Autoranging the voltage port
        self.port.write("SOUR%s:VOLT:RANG:AUTO ON" % self.channel)

        # if self.sweep_mode == "DelayPhase":
        # self.delayphase = self.value

        if self.period_frequency == "Period in s":
            self.frequency = 1.0 / self.period_frequency_value
        else:
            self.frequency = self.period_frequency_value

        if self.amplitude_hi_level == "Amplitude in V":
            self.amplitude = self.amplitude_hi_level_value

            if self.offset_lo_level == "Offset in V":
                self.offset = self.offset_lo_level_value
            else:
                self.offset = (self.amplitude_hi_level_value / 2.0 + self.offset_lo_level_value)

        else:
            if self.offset_lo_level == "Offset in V":
                self.amplitude = (self.amplitude_hi_level_value - self.offset_lo_level_value) * 2.0
                self.offset = self.offset_lo_level_value
            else:
                self.amplitude = self.amplitude_hi_level_value - self.offset_lo_level_value
                self.offset = (self.amplitude_hi_level_value - self.offset_lo_level_value) / 2.0

        ### Get Arbitrary Waveform ###

        if self.waveform.startswith("Arbitrary:") or self.waveform not in self.waveform_standard_list:

            # we strip off all file extensions and whitespaces and also the leading "Arbitrary:" if it has been used
            # further we only use uppercase as the device as anyway just knows uppercase file names 
            waveform_command = self.waveform.replace("Arbitrary:", "").strip().replace(".ARB", "").replace(".arb",
                                                                                                           "").replace(
                ".Arb", "").upper()

            self.port.write("SOUR%s:FUNC ARB" % (self.channel))
            self.port.write("FUNC:USER %s" % (waveform_command))

            # check if function is set correctly
            self.port.write("FUNC:USER?")
            answer = self.port.read()

            if answer != waveform_command:
                self.stop_Measurement(
                    "Cannot find the selected user function %s (check spelling/uppercases) " % waveform_command)
                return False

            waveform_type = "USER"

        else:

            waveform_type = self.commands[self.waveform]

        self.port.write(
            "SOUR%s:APPL:%s %s, %s, %s" % (self.channel, waveform_type, self.frequency, self.amplitude, self.offset))

        if self.waveform == "Pulse":
            if self.duty_cycle_pulse_width == "Pulse width in s":
                self.port.write("SOUR%s:FUNC:PULS:WIDT %s " % (self.channel, self.duty_cycle_pulse_width_value))

            if self.duty_cycle_pulse_width == "Duty cycle in %":
                self.port.write("SOUR%s:FUNC:PULS:DCYC %s " % (self.channel, self.duty_cycle_pulse_width_value))

        elif self.waveform == "Square":
            if self.duty_cycle_pulse_width == "Duty cycle in %":
                self.port.write("SOUR%s:FUNC:SQU:DCYC %s " % (self.channel, self.duty_cycle_pulse_width_value))

        if self.delay_phase == "Delay in s":
            self.phase = self.delay_phase_value * self.frequency * 360.0


        elif self.delay_phase == "Phase in deg":
            self.phase = self.delay_phase_value

        if waveform_type != "DC":
            self.port.write("SOUR%s:PHAS %s DEG" % (self.channel, self.phase))

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.port.write("OUTP%s ON" % self.channel)

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.port.write("OUTP%s OFF" % self.channel)

        # we have to ask to really switch off and we do not know why
        self.port.write("OUTP?")
        answer = self.port.read()
        # print(answer)

    def apply(self) -> None:
        """'apply' is used to set the new set value that is always available as 'self.value'."""
        if self.sweep_mode == "None":
            return

        if self.sweep_mode == "Frequency in Hz":
            self.period_frequency = "Frequency in Hz"
            self.period_frequency_value = self.value

        if self.sweep_mode == "Period in s":
            self.period_frequency = "Frequency in Hz"
            self.period_frequency_value = 1.0 / self.value

        if self.sweep_mode == "Amplitude in V":
            self.amplitude_hi_level = "Amplitude in V"
            self.amplitude_hi_level_value = self.value

        if self.sweep_mode == "HiLevel in V":
            self.amplitude_hi_level = "HiLevel in V"
            self.amplitude_hi_level_value = self.value

        if self.sweep_mode == "Offset in V":
            self.offset_lo_level = "Offset in V"
            self.offset_lo_level_value = self.value

        if self.sweep_mode == "LoLevel in V":
            self.offset_lo_level = "LoLevel in V"
            self.offset_lo_level_value = self.value

        if self.period_frequency == "Period in s":
            self.frequency = 1.0 / self.period_frequency_value
        else:
            self.frequency = self.period_frequency_value

        if self.amplitude_hi_level == "Amplitude in V":
            self.amplitude = self.amplitude_hi_level_value

            if self.offset_lo_level == "Offset in V":
                self.offset = self.offset_lo_level_value
            else:
                self.offset = (self.amplitude_hi_level_value / 2.0 + self.offset_lo_level_value)

        else:
            if self.offset_lo_level == "Offset in V":
                self.amplitude = (self.amplitude_hi_level_value - self.offset_lo_level_value) * 2.0
                self.offset = self.offset_lo_level_value
            else:
                self.amplitude = self.amplitude_hi_level_value - self.offset_lo_level_value
                self.offset = (self.amplitude_hi_level_value + self.offset_lo_level_value) / 2.0

        self.port.write("SOUR%s:FREQ %s" % (self.channel, self.frequency))
        self.port.write("SOUR%s:VOLT %s" % (self.channel, self.amplitude))
        self.port.write("SOUR%s:VOLT:OFFS %s" % (self.channel, self.offset))

        if self.sweep_mode == "Pulse width in s":
            self.duty_cycle_pulse_width_value = self.value

        if self.sweep_mode == "Duty cycle in %":
            self.duty_cycle_pulse_width_value = self.value

        if self.waveform == "Pulse":
            if self.duty_cycle_pulse_width == "Pulse width in s":
                self.port.write("SOUR%s:FUNC:PULS:WIDT %s " % (self.channel, self.duty_cycle_pulse_width_value))

            if self.duty_cycle_pulse_width == "Duty cycle in %":
                self.port.write("SOUR%s:FUNC:PULS:DCYC %s " % (self.channel, self.duty_cycle_pulse_width_value))

        if self.sweep_mode == "Delay in s":
            self.phase = self.value * self.frequency * 360.0
            self.port.write("SOUR%s:PHAS %s DEG " % (self.channel, self.phase))

        if self.sweep_mode == "Phase in deg":
            self.phase = self.value
            self.port.write("SOUR%s:PHAS %s DEG " % (self.channel, self.phase))

    def call(self) -> float | None:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        if self.sweep_mode == "None":
            return None

        self.port.write("SOUR%s:APPL?" % (self.channel))
        answer = self.port.read().replace("\"", "").split(" ")[1].split(",")

        frequency, amplitude, offset = map(float, answer)

        if self.sweep_mode == "Frequency in Hz":
            return frequency

        elif self.sweep_mode == "Period in s":
            return 1.0 / frequency

        elif self.sweep_mode == "Amplitude in V":
            return amplitude

        elif self.sweep_mode == "HiLevel in V":
            return offset + amplitude / 2.0

        elif self.sweep_mode == "Offset in V":
            return offset

        elif self.sweep_mode == "LoLevel in V":
            return offset - amplitude / 2.0

        elif self.sweep_mode == "Duty cycle in %" or self.sweep_mode == "Pulse width in s":
            return float(self.value)

        elif self.sweep_mode == "Delay in s" or self.sweep_mode == "Phase in deg":
            return float(self.value)

        else:
            # Fallback for other sweep modes
            return float(self.value)
