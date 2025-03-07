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
# * Module: Signal
# * Instrument: Simulated Signal Generator

from __future__ import annotations

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Simulated Signal driver."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Simulation"  # short name will be shown in the sequencer
        self.variables = ["Frequency", "Amplitude", "Simulated Timestamps", "Simulated Signal"]
        self.units = ["Hz", "V", "s", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        # use/uncomment the next line to use the port manager
        # self.port_manager = True

        # use/uncomment the next line to select the interfaces that should be presented to the user if you have enabled
        # the port manager in the previous step
        # self.port_types = ["COM", "GPIB", "USB"]

        # Measurement Parameters
        self.sweep_mode: str = "None"
        self.waveform: str = "Sine"

        self.period_frequency_mode: str = "Frequency in Hz"
        self.period_frequency_value: float = 1e6
        self.frequency: float = 1e6

        self.amplitude_high_level_mode: str = "Amplitude in V"
        self.amplitude_high_level_value: float = 1.0
        self.amplitude: float = 1.0

        self.offset_low_level_mode: str = "Offset in V"
        self.offset_low_level_value: float = 0.0
        self.offset: float = 0.0

        self.delay_phase_mode: str = "Delay in s"
        self.delay_phase_value: float = 0.0
        self.phase: float = 0.0
        self.delay: float = 0.0

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": [
                "None",
                "Frequency in Hz",
                "Period in s",
                "Amplitude in V",
                "Phase in deg",
                "Delay in s",
            ],
            "Waveform": ["Sine", "Square", "Triangle", "Sawtooth"],
            "PeriodFrequency": ["Frequency in Hz", "Period in s"],
            "PeriodFrequencyValue": "2e3",
            "AmplitudeHiLevel": ["Amplitude in V"],
            "AmplitudeHiLevelValue": "1.0",
            "OffsetLoLevel": ["Offset in V"],
            "OffsetLoLevelValue": "0.0",
            "DelayPhase": ["Delay in s", "Phase in deg"],
            "DelayPhaseValue": "0.0",
            # "Impedance": ["50"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]  # can be used to enable device communication
        self.sweep_mode = parameter["SweepMode"]
        self.waveform = parameter["Waveform"]
        self.period_frequency_mode = parameter["PeriodFrequency"]
        self.period_frequency_value = float(parameter["PeriodFrequencyValue"])

        self.amplitude_high_level_mode = parameter["AmplitudeHiLevel"]
        self.amplitude_high_level_value = float(parameter["AmplitudeHiLevelValue"])

        self.offset_low_level_mode = parameter["OffsetLoLevel"]
        self.offset_low_level_value = float(parameter["OffsetLoLevelValue"])

        self.delay_phase_mode = parameter["DelayPhase"]
        self.delay_phase_value = float(parameter["DelayPhaseValue"])

    # here functions start that are called by SweepMe! during a measurement

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # The generated signal is saved in device_communication to allow the simulated oscilloscope to read it.
        self.device_communication["Simulated signal"] = self.generate_waveform

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.period_frequency_mode.startswith("Frequency"):
            self.frequency = self.period_frequency_value
        else:
            self.frequency = 1 / self.period_frequency_value

        if self.amplitude_high_level_mode.startswith("Amplitude"):
            self.amplitude = self.amplitude_high_level_value
        else:
            self.amplitude = 1

        if self.offset_low_level_mode.startswith("Offset"):
            self.offset = self.offset_low_level_value
        else:
            self.offset = 0

        if self.delay_phase_mode.startswith("Delay"):
            self.delay = self.delay_phase_value
        else:
            self.delay = self.delay_phase_value / 360 * 1 / self.frequency

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweep_mode == "Frequency in Hz":
            self.frequency = self.value
        elif self.sweep_mode == "Period in s":
            self.frequency = 1 / self.value
        elif self.sweep_mode == "Amplitude in V":
            self.amplitude = self.value
        elif self.sweep_mode == "Phase in deg":
            self.phase = self.value
        elif self.sweep_mode == "Delay in s":
            self.delay = self.value

        # update the signal generator function
        self.device_communication["Simulated signal"] = self.generate_waveform

    def call(self) -> [float, float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        timestamps = np.linspace(0, 3 / self.frequency, 100)
        signal = self.generate_waveform(timestamps)

        return self.frequency, self.amplitude, timestamps, signal

    def generate_waveform(self, time_stamp: float | np.array) -> float:
        """Generate a wave signal."""
        time_stamp += self.delay

        if self.waveform == "Sine":
            signal = np.sin(2 * np.pi * self.frequency * time_stamp)
        elif self.waveform == "Square":
            signal = np.sign(np.sin(2 * np.pi * self.frequency * time_stamp))
        elif self.waveform == "Triangle":
            signal = np.arcsin(np.sin(2 * np.pi * self.frequency * time_stamp))
        elif self.waveform == "Sawtooth":
            signal = np.arctan(np.tan(np.pi * self.frequency * time_stamp))
        else:
            signal = 0

        return self.offset + signal * self.amplitude


