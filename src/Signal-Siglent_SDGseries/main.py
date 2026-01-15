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

# Contribution: We like to thank TU Dresden/Jacob Hille for providing the initial version of this driver.

# SweepMe! driver
# * Module: Signal
# * Instrument: Siglent SDG Series

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class to implement functionalities of a Siglent SDG Series Function/Arbitrary Waveform Generator."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

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

        # Sweep Parameters
        self.channel: str = "C1"
        self.sweep_mode: str = "None"

        # Measurement Parameters
        self.waveform: str = "Sine"

        # Frequency / Period
        self.period_or_frequency_mode: str = "Frequency in Hz"
        self.period_or_frequency_value: float = 1000.0
        self.frequency: float = 1000.0

        # Amplitude / High-Low / Offset
        self.amplitude_or_high_level_mode: str = "Amplitude in V"
        self.amplitude_or_high_level_value: float = 1.0
        self.amplitude: float = 1.0
        self.offset_or_low_level_mode: str = "Offset in V"
        self.offset_or_low_level_value: float = 0.0
        self.offset: float = 0.0

        # Noise specific
        self.mean: float = 0.0
        self.stdev: float = 0.1

        self.duty_cycle_or_pulse_width_mode: str = "Duty cycle in %"
        self.duty_cycle_or_pulse_width_value: float = 50.0
        self.delay_or_phase_mode: str = "Delay in s"
        self.delay_or_phase_value: float = 0.0
        self.phase: float = 0.0

        self.impedance: str = "High-Z"

    def set_GUIparameter(self) -> dict[str, Any]:
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
            "OffsetLoLevel": ["Offset in V", "Low level in V", "Standard deviation in V"],
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

    def get_GUIparameter(self, parameter: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        # Channel Names have to be {C1, C2}
        self.channel = "C" + parameter['Channel'][-1]
        self.sweep_mode = parameter['SweepMode']
        self.waveform = parameter['Waveform']
        self.period_or_frequency_mode = parameter['PeriodFrequency']
        self.period_or_frequency_value = float(parameter['PeriodFrequencyValue'])
        self.amplitude_or_high_level_mode = parameter['AmplitudeHiLevel']
        self.amplitude_or_high_level_value = float(parameter['AmplitudeHiLevelValue'])
        self.offset_or_low_level_mode = parameter['OffsetLoLevel']
        self.offset_or_low_level_value = float(parameter['OffsetLoLevelValue'])
        # TODO pulsewidth in ms or µs
        self.duty_cycle_or_pulse_width_mode = parameter['DutyCyclePulseWidth']
        self.duty_cycle_or_pulse_width_value = float(parameter['DutyCyclePulseWidthValue'])
        # TODO delay in ms or µs
        self.delay_or_phase_mode = parameter['DelayPhase']
        self.delay_or_phase_value = float(parameter['DelayPhaseValue'])
        self.impedance = parameter['Impedance']

        self.shortname = 'SDG Series ' + self.channel

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

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.set_impedance(self.impedance)
        self.update_generated_signal()

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        self.port.write(f"{self.channel}:OUTP ON")

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.port.write(f"{self.channel}:OUTP OFF")

    def apply(self) -> None:
        """Update the generated signal according to the current sweep value."""
        if self.sweep_mode == "None":
            return

        self.update_signal_parameters_with_sweep_value()
        self.update_generated_signal()

    def call(self) -> float | None:
        if self.sweep_mode != 'None':
            return float(self.value)
        return None

    # Convenience Functions

    def update_generated_signal(self) -> None:
        """Update the generated signal according to the current settings."""
        self.calculate_frequency()
        self.calculate_amplitude_and_offset()
        self.calculate_phase()

        # Set waveform with standard parameters
        if self.waveform not in ["Noise", "DC"]:
            self.set_frequency(self.frequency)

            if self.waveform not in ["Pulse"]:
                self.set_phase(self.phase)

        self.set_amplitude(self.amplitude)
        self.set_offset(self.offset)
        self.set_waveform(self.waveform)

        # handling parameters only compatible with specific wave types
        if self.waveform == "Noise":
            if self.amplitude_or_high_level_mode != "Mean in V" or self.offset_or_low_level_mode != "Standard deviation in V":
                raise Exception("Mean and Standard Deviation have to be selected for Noise waveform.")
            self.port.write(f"{self.channel}:BSWV MEAN,{self.mean},STDEV,{self.stdev}")

        elif self.waveform == "Pulse":
            if self.duty_cycle_or_pulse_width_mode.startswith("Pulse width"):
                self.set_pulse_width(self.duty_cycle_or_pulse_width_value)
            elif self.duty_cycle_or_pulse_width_mode.startswith("Duty cycle"):
                self.set_duty_cycle(self.duty_cycle_or_pulse_width_value)

        elif self.waveform == "Square":
            if self.duty_cycle_or_pulse_width_mode.startswith("Duty cycle"):
                self.set_duty_cycle(self.duty_cycle_or_pulse_width_value)

    def calculate_frequency(self) -> None:
        """Handle frequency and period settings."""
        if self.period_or_frequency_mode.startswith("Period"):
            self.frequency = 1.0 / self.period_or_frequency_value
        else:
            self.frequency = self.period_or_frequency_value

    def calculate_amplitude_and_offset(self) -> None:
        """Handle amplitude/high level and offset/low level settings."""
        if self.amplitude_or_high_level_mode.startswith("Amplitude"):
            self.amplitude = self.amplitude_or_high_level_value

            if self.offset_or_low_level_mode.startswith("Offset"):
                self.offset = self.offset_or_low_level_value
            else:  # Amplitude/2 + Low level
                self.offset = (self.amplitude_or_high_level_value / 2.0 + self.offset_or_low_level_value)

        elif self.amplitude_or_high_level_mode.startswith("High level"):
            if self.offset_or_low_level_mode.startswith("Offset"):
                # amplitude = (high level - offset) * 2
                self.amplitude = (self.amplitude_or_high_level_value - self.offset_or_low_level_value) * 2.0
                self.offset = self.offset_or_low_level_value
            else:  # Low level
                self.amplitude = self.amplitude_or_high_level_value - self.offset_or_low_level_value
                # offset = (high level - low level) / 2
                self.offset = (self.amplitude_or_high_level_value - self.offset_or_low_level_value) / 2.0

        elif self.amplitude_or_high_level_mode.startswith("Mean"):
            self.mean = self.amplitude_or_high_level_value
            if self.offset_or_low_level_mode.startswith("Standard deviation"):
                self.stdev = self.offset_or_low_level_value

    def calculate_phase(self) -> None:
        """Calculate phase from delay or vice versa."""
        if self.delay_or_phase_mode.startswith("Delay"):
            self.phase = self.delay_or_phase_value * self.frequency * 360.0

        elif self.delay_or_phase_mode.startswith("Phase"):
            self.phase = self.delay_or_phase_value

    def update_signal_parameters_with_sweep_value(self) -> None:
        """Update the signal parameters according to the current sweep mode and value."""
        if self.sweep_mode.startswith("Frequency"):
            self.period_or_frequency_mode = "Frequency in Hz"
            self.period_or_frequency_value = self.value

        elif self.sweep_mode.startswith("Period"):
            self.period_or_frequency_mode = "Frequency in Hz"
            self.period_or_frequency_value = 1.0 / self.value

        elif self.sweep_mode.startswith("Amplitude"):
            self.amplitude_or_high_level_mode = "Amplitude in V"
            self.amplitude_or_high_level_value = self.value

        elif self.sweep_mode.startswith("High level"):
            self.amplitude_or_high_level_mode = "High level in V"
            self.amplitude_or_high_level_value = self.value

        elif self.sweep_mode.startswith("Offset"):
            self.offset_or_low_level_mode = "Offset in V"
            self.offset_or_low_level_value = self.value

        elif self.sweep_mode.startswith("Low level"):
            self.offset_or_low_level_mode = "Low level in V"
            self.offset_or_low_level_value = self.value

        elif self.sweep_mode.startswith("Pulse width"):
            self.duty_cycle_or_pulse_width_value = self.value

        elif self.sweep_mode.startswith("Duty cycle"):
            self.duty_cycle_or_pulse_width_value = self.value

    # Wrapped Functions

    def get_identification(self) -> str:
        """Get the identification string of the instrument."""
        return self.port.query("*IDN?")

    def set_impedance(self, impedance: str) -> None:
        """Set the output impedance of the selected channel."""
        if impedance.lower().startswith("high"):
            self.port.write(f"{self.channel}:OUTP LOAD,HZ")
        elif impedance.lower().startswith("50"):
            self.port.write(f"{self.channel}:OUTP LOAD,50")

    def set_phase(self, phase: float) -> None:
        """Set the phase in degrees of the selected channel."""
        if self.waveform in ["DC", "Noise", "Pulse"]:
            raise Exception("Phase cannot be set for DC, Pulse, or Noise waveforms.")
        self.port.write(f"{self.channel}:BSWV PHSE,{phase}")

    def set_pulse_width(self, pulse_width: float) -> None:
        """Set the pulse width in s of the selected channel."""
        if self.waveform != "Pulse":
            raise Exception("Pulse width can only be set for Pulse waveforms.")
        self.port.write(f"{self.channel}:BSWV WIDTH,{pulse_width}")

    def set_duty_cycle(self, duty_cycle: float) -> None:
        """Set the duty cycle in % of the selected channel."""
        if self.waveform != "Pulse" and self.waveform != "Square":
            raise Exception("Duty cycle can only be set for Pulse or Square waveforms.")
        if duty_cycle < 0.0 or duty_cycle > 100.0:
            raise Exception("Duty cycle must be between 0 and 100 %.")
        self.port.write(f"{self.channel}:BSWV DUTY,{duty_cycle}")

    def set_frequency(self, frequency: float) -> None:
        """Set the frequency in Hz of the selected channel."""
        self.port.write(f"{self.channel}:BSWV FREQ,{frequency}")

    def set_amplitude(self, amplitude: float) -> None:
        """Set the amplitude in V of the selected channel."""
        self.port.write(f"{self.channel}:BSWV AMP,{amplitude}")

    def set_offset(self, offset: float) -> None:
        """Set the offset in V of the selected channel."""
        self.port.write(f"{self.channel}:BSWV OFST,{offset}")

    def set_waveform(self, waveform: str) -> None:
        """Set the waveform type of the selected channel."""
        waveform_type = self.commands[waveform]
        self.port.write(f"{self.channel}:BSWV WVTP,{waveform_type}")
