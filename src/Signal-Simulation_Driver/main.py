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

"""SweepMe! driver of a simulated signal generator."""

from __future__ import annotations

from typing import Annotated, Any, Literal

import numpy as np
from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Seconds = Annotated[float, Unit("s")]
Hertz = Annotated[float, Unit("Hz")]
Volts = Annotated[float, Unit("V")]
Waveform = Literal["Sine", "Square", "Triangle", "Sawtooth"]

SWEEP_MODES: list[str] = ["None", "Frequency in Hz", "Period in s", "Amplitude in V", "Phase in deg", "Delay in s"]
WAVEFORMS: list[str] = ["Sine", "Square", "Triangle", "Sawtooth"]

# GUI label of each type dropdown -> the quantity its value field holds
PERIOD_FREQUENCY_TYPES: dict[str, str] = {"Frequency in Hz": "frequency", "Period in s": "period"}
AMPLITUDE_HI_LEVEL_TYPES: dict[str, str] = {"Amplitude in V": "amplitude"}
OFFSET_LO_LEVEL_TYPES: dict[str, str] = {"Offset in V": "offset"}
DELAY_PHASE_TYPES: dict[str, str] = {"Delay in s": "delay", "Phase in deg": "phase"}


class Device(EmptyDevice):
    """Simulated Signal driver.

    The generated signal is shared via device_communication under the key 'Simulated signal', so that a
    Scope-Simulation_Driver used at the same time shows it on channel 1. Without a scope, the driver works on its own.
    """

    SHARED_SIGNAL_KEY: str = "Simulated signal"
    """Key in device_communication under which generate_waveform is shared with the simulated oscilloscope."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Simulation"  # short name will be shown in the sequencer
        self.variables = ["Frequency", "Amplitude", "Simulated Timestamps", "Simulated Signal"]
        self.units = ["Hz", "V", "s", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        # Measurement Parameters
        self.gui_parameters: dict[str, Any] = {}
        self.port_string: str = ""
        self.sweep_mode: str = "None"
        self.waveform: str = "Sine"

        self.period_frequency_mode: str = "Frequency in Hz"
        self.frequency: float = 1e6

        self.amplitude_high_level_mode: str = "Amplitude in V"
        self.amplitude: float = 1.0

        self.offset_low_level_mode: str = "Offset in V"
        self.offset: float = 0.0

        self.delay_phase_mode: str = "Delay in s"
        self.phase: float = 0.0
        self.delay: float = 0.0

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI parameters with their default values."""
        return {
            "SweepMode": SWEEP_MODES,
            "Waveform": WAVEFORMS,
            "PeriodFrequency": list(PERIOD_FREQUENCY_TYPES),
            "PeriodFrequencyValue": "2e3",
            "AmplitudeHiLevel": list(AMPLITUDE_HI_LEVEL_TYPES),
            "AmplitudeHiLevelValue": "1.0",
            "OffsetLoLevel": list(OFFSET_LO_LEVEL_TYPES),
            "OffsetLoLevelValue": "0.0",
            "DelayPhase": list(DELAY_PHASE_TYPES),
            "DelayPhaseValue": "0.0",
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the values of the GUI parameters; configure() converts and checks them."""
        self.gui_parameters = parameters
        self.port_string = parameters.get("Port", "")
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.waveform = parameters.get("Waveform", "Sine")
        self.period_frequency_mode = parameters.get("PeriodFrequency", "Frequency in Hz")
        self.amplitude_high_level_mode = parameters.get("AmplitudeHiLevel", "Amplitude in V")
        self.offset_low_level_mode = parameters.get("OffsetLoLevel", "Offset in V")
        self.delay_phase_mode = parameters.get("DelayPhase", "Delay in s")

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
        """Convert and check the GUI values; it runs at every start of the branch and after a reconfigure."""
        if self.sweep_mode not in SWEEP_MODES:
            msg = f"Sweep mode '{self.sweep_mode}' is not supported. Choose one of {SWEEP_MODES}."
            raise ValueError(msg)
        if self.waveform not in WAVEFORMS:
            msg = f"Waveform '{self.waveform}' is not supported. Choose one of {WAVEFORMS}."
            raise ValueError(msg)

        period_frequency_type = self._lookup("PeriodFrequency", self.period_frequency_mode, PERIOD_FREQUENCY_TYPES)
        amplitude_type = self._lookup("AmplitudeHiLevel", self.amplitude_high_level_mode, AMPLITUDE_HI_LEVEL_TYPES)
        offset_type = self._lookup("OffsetLoLevel", self.offset_low_level_mode, OFFSET_LO_LEVEL_TYPES)
        delay_phase_type = self._lookup("DelayPhase", self.delay_phase_mode, DELAY_PHASE_TYPES)

        period_frequency_value = float(self.gui_parameters.get("PeriodFrequencyValue", 2e3))
        if period_frequency_value <= 0:
            msg = f"The value of '{self.period_frequency_mode}' must be greater than 0, not {period_frequency_value}."
            raise ValueError(msg)
        if period_frequency_type == "frequency":
            self.frequency = period_frequency_value
        else:
            self.frequency = 1 / period_frequency_value

        if amplitude_type == "amplitude":
            self.amplitude = float(self.gui_parameters.get("AmplitudeHiLevelValue", 1.0))

        if offset_type == "offset":
            self.offset = float(self.gui_parameters.get("OffsetLoLevelValue", 0.0))

        delay_phase_value = float(self.gui_parameters.get("DelayPhaseValue", 0.0))
        if delay_phase_type == "delay":
            self.delay = delay_phase_value
        else:
            # A positive phase advances the waveform, which is a negative delay.
            self.phase = delay_phase_value
            self.delay = -self.phase / 360 / self.frequency

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        value = float(self.value)
        if self.sweep_mode == "Frequency in Hz":
            self.frequency = value
        elif self.sweep_mode == "Period in s":
            self.frequency = 1 / value
        elif self.sweep_mode == "Amplitude in V":
            self.amplitude = value
        elif self.sweep_mode == "Phase in deg":
            self.phase = value
            self.delay = -self.phase / 360 / self.frequency
        elif self.sweep_mode == "Delay in s":
            self.delay = value

        # update the signal generator function
        self._share_signal()

    def call(self) -> tuple[float, float, np.ndarray, np.ndarray]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        timestamps = np.linspace(0, 3 / self.frequency, 100)
        signal = np.asarray(self.generate_waveform(timestamps), dtype=float)

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
            signal = np.zeros_like(phase)

        return self.offset + signal * self.amplitude

    # --- Communication commands, used e.g. by the SweepMe! Instrument Control ---
    #
    # The commands do not need 'initialize' or 'configure'.

    @command
    def set_waveform(self, waveform: Waveform) -> None:
        """Set the waveform."""
        self.waveform = waveform

    # check_driver: ignore DC012 - the bound 0 Hz is excluded, which Range cannot express
    @command
    def set_frequency(self, frequency: Annotated[Hertz, Range(0.0, None)]) -> None:
        """Set the frequency in Hz (greater than 0 Hz)."""
        if frequency <= 0:
            msg = f"Frequency {frequency} Hz must be greater than 0 Hz."
            raise ValueError(msg)
        self.frequency = frequency

    @command
    def set_amplitude(self, amplitude: Annotated[Volts, Range(0.0, None)]) -> None:
        """Set the amplitude in V (0 V or more)."""
        self.amplitude = amplitude

    @command
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

    # check_driver: ignore DC012 - the bound 0 s of the duration is excluded, which Range cannot express
    @command(returns=("time", "voltage"))
    def sample_signal(
        self,
        duration: Annotated[Seconds, Range(0.0, None)],
        points: Annotated[int, Range(2, 100000)],
    ) -> tuple[list[Seconds], list[Volts]]:
        """Return (time in s, voltage in V) of the set waveform at 'points' times from 0 s to 'duration' in s."""
        if duration <= 0:
            msg = f"Duration {duration} s must be greater than 0 s."
            raise ValueError(msg)
        time_stamps = np.linspace(0, duration, points)
        signal = self.generate_waveform(time_stamps.copy())
        return time_stamps.tolist(), np.asarray(signal, dtype=float).tolist()

    # --- Helpers ---

    @staticmethod
    def _lookup(key: str, label: str, options: dict[str, str]) -> str:
        """Return the internal value of a dropdown label, or raise a ValueError naming the allowed labels."""
        if label not in options:
            msg = f"{key} '{label}' is not supported. Choose one of {list(options)}."
            raise ValueError(msg)
        return options[label]

    def _share_signal(self) -> None:
        """Put generate_waveform into device_communication, where a simulated oscilloscope can find it.

        The bound method always uses the current settings, so later changes reach the oscilloscope without sharing
        the signal again.
        """
        self.device_communication[self.SHARED_SIGNAL_KEY] = self.generate_waveform
