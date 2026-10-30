# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025-2026 SweepMe! GmbH (sweep-me.net)
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

from typing import Annotated, Literal

import numpy as np
from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Seconds = Annotated[float, Unit("s")]
Hertz = Annotated[float, Unit("Hz")]
Volts = Annotated[float, Unit("V")]
Waveform = Literal["Sine", "Square", "Triangle", "Sawtooth"]


class Device(EmptyDevice):
    """Simulated Signal driver.

    The generated signal is shared via device_communication under the key 'Simulated signal', so that a
    Scope-Simulation_Driver used at the same time shows it on channel 1. Without a scope, the driver works on its own.
    """

    SHARED_SIGNAL_KEY: str = "Simulated signal"
    """Key in device_communication under which generate_waveform is shared with the simulated oscilloscope."""

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
        self.port_string = parameter.get("Port", "")  # can be used to enable device communication
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

    def connect(self) -> None:
        """Share the signal with a simulated oscilloscope, also when only the communication commands are used."""
        self._share_signal()

    def disconnect(self) -> None:
        """Stop sharing the signal, so that a simulated oscilloscope falls back to its own waveform."""
        if self.device_communication.get(self.SHARED_SIGNAL_KEY) == self.generate_waveform:
            del self.device_communication[self.SHARED_SIGNAL_KEY]

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self._share_signal()

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
            # A positive phase advances the waveform, which is a negative delay.
            self.phase = self.delay_phase_value
            self.delay = -self.phase / 360 / self.frequency

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
            self.delay = -self.phase / 360 / self.frequency
        elif self.sweep_mode == "Delay in s":
            self.delay = self.value

        # update the signal generator function
        self._share_signal()

    def call(self) -> tuple[float, float, np.ndarray, np.ndarray]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        timestamps = np.linspace(0, 3 / self.frequency, 100)
        signal = self.generate_waveform(timestamps)

        return self.frequency, self.amplitude, timestamps, signal

    def generate_waveform(self, time_stamp: float | np.ndarray) -> float | np.ndarray:
        """Generate a wave signal."""
        # A positive delay shifts the waveform to later times. Subtracting creates a new array, so the time stamps
        # of the caller are not changed.
        time_stamp = np.asarray(time_stamp, dtype=float) - self.delay
        phase = 2 * np.pi * self.frequency * time_stamp

        if self.waveform == "Sine":
            signal = np.sin(phase)
        elif self.waveform == "Square":
            signal = np.sign(np.sin(phase))
        elif self.waveform == "Triangle":
            # arcsin(sin(x)) spans +/- pi/2, normalized to +/- 1
            signal = 2 / np.pi * np.arcsin(np.sin(phase))
        elif self.waveform == "Sawtooth":
            # rises linearly from -1 to 1 within each period, 0 at t = 0
            cycles = self.frequency * time_stamp
            signal = 2 * (cycles - np.floor(cycles + 0.5))
        else:
            signal = 0

        return self.offset + signal * self.amplitude

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The commands do not need 'initialize' or 'configure'.
    """

    @command
    def set_waveform(self, waveform: Waveform) -> None:
        """Set the waveform."""
        self.waveform = waveform

    @command
    def set_frequency(self, frequency: Annotated[Hertz, Range(0.0, None)]) -> None:
        """Set the frequency in Hz (greater than 0 Hz)."""
        if frequency <= 0:
            msg = f"Frequency {frequency} Hz must be greater than 0 Hz."
            raise ValueError(msg)
        self.frequency = frequency

    @command(hazards="Changes the signal level at the connected device at once.")
    def set_amplitude(self, amplitude: Annotated[Volts, Range(0.0, None)]) -> None:
        """Set the amplitude in V (0 V or more)."""
        self.amplitude = amplitude

    @command(hazards="Changes the signal level at the connected device at once.")
    def set_offset(self, offset: Volts) -> None:
        """Set the offset in V."""
        self.offset = offset

    @command
    def set_delay(self, delay: Seconds) -> None:
        """Set the delay of the signal in s. A positive delay shifts the waveform to later times."""
        self.delay = delay

    @command(returns=("waveform", "frequency", "amplitude", "offset", "delay"), reads="setpoint")
    def get_settings(self) -> tuple[Waveform, Hertz, Volts, Volts, Seconds]:
        """Return (waveform, frequency in Hz, amplitude in V, offset in V, delay in s)."""
        return (
            self.waveform,  # type: ignore[return-value]  # set from the GUI or set_waveform, both one of Waveform
            float(self.frequency),
            float(self.amplitude),
            float(self.offset),
            float(self.delay),
        )

    @command(returns=("time", "voltage"))
    def sample_signal(
        self,
        duration: Annotated[Seconds, Range(0.0, None)],
        points: Annotated[int, Range(2, 100000)],
    ) -> tuple[Annotated[list[float], Unit("s")], Annotated[list[float], Unit("V")]]:
        """Return (time in s, voltage in V) of the set waveform at 'points' times from 0 s to 'duration' in s."""
        if duration <= 0:
            msg = f"Duration {duration} s must be greater than 0 s."
            raise ValueError(msg)
        time_stamps = np.linspace(0, duration, points)
        signal = self.generate_waveform(time_stamps.copy())
        return time_stamps.tolist(), np.asarray(signal, dtype=float).tolist()

    def _share_signal(self) -> None:
        """Put generate_waveform into device_communication, where a simulated oscilloscope can find it.

        The bound method always uses the current settings, so later changes reach the oscilloscope without sharing
        the signal again.
        """
        self.device_communication[self.SHARED_SIGNAL_KEY] = self.generate_waveform
