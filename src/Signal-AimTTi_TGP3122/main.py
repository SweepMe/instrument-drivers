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

# SweepMe! driver
# * Module: Signal
# * Instrument: AIM-TTi TGP3122

from collections import OrderedDict
from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        EmptyDevice.__init__(self)

        self.idlevalue = None

        self.port_manager = True
        self.port_types = ["COM"]

        self.port_properties = {
            "EOL": "\n",
            "Baudrate": 9600,
            "timeout": 1,
            # "query": "*IDN?",
        }
        # self.port_identifications = [""]

        # to be defined by user
        self.commands = {
            "Period in s": "PER",
            "Frequency in Hz": "FREQ",
            "HiLevel in V": "HILVL",
            "LoLevel in V": "LOLVL",
            "Amplitude in V": "AMPL",
            "Offset in V": "DCOFFS",
            "Phase in deg": "PHASE",
            "Delay in s": "PHASE",
        }

        self.waveforms = OrderedDict([
            ("Sine", "SINE"),
            ("Square", "SQUARE"),
            ("Ramp", "RAMP"),
            ("Pulse", "PULSE"),
            ("Doublepulse", "DOUBLEPULSE"),
            ("Noise", "NOISE"),
            ("Arb", "ARB"),
            ("Triangle", "TRIANG")
        ])

        # Measurement Parameters
        self.sweep_mode: str = "None"
        self.channel: int = 1
        self.waveform: str = "Sine"
        self.period_frequency: str = "Frequency in Hz"
        self.period_frequency_value: float = 1000
        self.amplitude_hi_level: str = "Amplitude in V"
        self.amplitude_hi_level_value: float = 1.0
        self.offset_lo_level: str = "Offset in V"
        self.offset_lo_level_value: float = 0.0
        self.duty_cycle_pulse_width: str = "Duty cycle in %"
        self.duty_cycle_pulse_width_value: float = 50
        self.delay_phase: str = "Phase in deg"
        self.delay_phase_value: float = 0

        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Frequency in Hz", "Period in s", "Amplitude in V", "Offset in V", "HiLevel in V",
                          "LoLevel in V", "Phase in deg", "Delay in s", "None"],
            "Channel": ["1", "2"],
            "Waveform": list(self.waveforms.keys()),
            "PeriodFrequency": ["Period in s", "Frequency in Hz"],
            "AmplitudeHiLevel": ["Amplitude in V", "HiLevel in V"],
            "OffsetLoLevel": ["Offset in V", "LoLevel in V"],
            "DelayPhase": ["Phase in deg", "Delay in s"],
            # "DutyCyclePulseWidth": ["Duty cycle in %"],
            "PeriodFrequencyValue": 1000,
            "AmplitudeHiLevelValue": 1.0,
            "OffsetLoLevelValue": 0.0,
            "DelayPhaseValue": 0,
            # "DutyCyclePulseWidthValue": 50,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.device = parameters.get("Device", "")  # e.g. "COM3"
        self.shortname = "TGP3122" + self.device[-4:]
        self.channel = int(parameters.get("Channel", "1")[-1])

        # could be part of the MeasClass
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.waveform = parameters.get("Waveform", "Sine")
        self.period_frequency = parameters.get("PeriodFrequency", "Frequency in Hz")
        self.period_frequency_value = parameters.get("PeriodFrequencyValue", 1000)
        self.amplitude_hi_level = parameters.get("AmplitudeHiLevel", "Amplitude in V")
        self.amplitude_hi_level_value = parameters.get("AmplitudeHiLevelValue", 1.0)
        self.offset_lo_level = parameters.get("OffsetLoLevel", "Offset in V")
        self.offset_lo_level_value = parameters.get("OffsetLoLevelValue", 0.0)
        self.duty_cycle_pulse_width = parameters.get("DutyCyclePulseWidth", "Duty cycle in %")
        self.duty_cycle_pulse_width_value = parameters.get("DutyCyclePulseWidthValue", 50)
        self.delay_phase = parameters.get("DelayPhase", "Phase in deg")
        self.delay_phase_value = parameters.get("DelayPhaseValue", 0)

        if self.sweep_mode == "None":
            self.variables = []
            self.units = []
            self.plottype = []  # True to plot data
            self.savetype = []  # True to save data

        else:
            self.variables = [self.sweep_mode.split(" ")[0]]
            self.units = [self.sweep_mode.split(" ")[1][1:-1]]

    def initialize(self) -> None:
        """Initialize the device, e.g. set the initial state of the device."""
        self.port.write("BEEPMODE OFF")

        self.port.write("CHN %i" % self.channel)

        self.port.write("WAVE %s" % self.waveforms[self.waveform])

        self.port.write("ALIGN")  # aligns the two channel to the same phase

        # set period/frequency
        self.port.write("%s %s" % (self.commands[self.period_frequency], self.period_frequency_value))
        self.port.write("%s %s" % (self.commands[self.amplitude_hi_level], self.amplitude_hi_level_value))
        self.port.write("%s %s" % (self.commands[self.offset_lo_level], self.offset_lo_level_value))

        if self.delay_phase == "Delay in s":
            if self.period_frequency == "Period in s":
                self.delay_phase_value = 360.0 * float(self.delay_phase_value) / float(self.period_frequency_value)
            else:
                self.delay_phase_value = 360.0 * float(self.delay_phase_value) * float(self.period_frequency_value)

        self.port.write("%s %s" % (self.commands[self.delay_phase], self.delay_phase_value))

        # VOLT 3.0 Set amplitude to 3 Vpp
        # VOLT:OFFS -2.5 Set offset to -2.5 Vdc

    def poweron(self) -> None:
        """Turn on the output and activate the channel."""
        self.port.write("CHN %i" % self.channel)
        self.port.write("OUTPUT ON")

    def poweroff(self) -> None:
        """Turn off the output and deactivate the channel."""
        self.port.write("CHN %i" % self.channel)
        self.port.write("OUTPUT OFF")

    def apply(self) -> None:
        """Apply the sweep value."""
        if self.sweep_mode == "None":
            return

        self.port.write("CHN %i" % self.channel)
        if self.sweep_mode == "Delay in s":
            if self.period_frequency == "Period in s":

                self.phasevalue = 360.0 * self.value / float(self.period_frequency_value)
            else:
                self.phasevalue = 360.0 * self.value * float(self.period_frequency_value)

            self.port.write("%s %s" % (self.commands[self.sweep_mode], self.phasevalue))

        else:
            self.port.write("%s %s" % (self.commands[self.sweep_mode], self.value))

    def call(self) -> list[float]:
        """Return the current sweep value as a 1-element list."""
        if self.sweep_mode != "None":
            return []

        return [float(self.value)]
