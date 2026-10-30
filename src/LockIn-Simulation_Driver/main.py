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
# * Module: LockIn
# * Instrument: Simulated Lock-in Amplifier

from __future__ import annotations

from random import random
from typing import Annotated

import numpy as np
from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Hertz = Annotated[float, Unit("Hz")]
Volts = Annotated[float, Unit("V")]
Degrees = Annotated[float, Unit("deg")]
HertzList = list[Hertz]
VoltsList = list[Volts]
DegreesList = list[Degrees]


class Device(EmptyDevice):
    """Simulated Lock-in amplifier driver."""

    def __init__(self) -> None:
        """Initialize the device class and default parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Simulation"
        self.port_manager = False

        self.variables = ["Magnitude", "Phase", "Frequency", "X", "Y"]
        self.units = ["V", "°", "Hz", "V", "V"]
        self.plottype = [True, True, True, True, True]
        self.savetype = [True, True, True, True, True]

        self.sweep_mode: str = "None"
        self.noise_level: float = 0.01  # set to 0 for deterministic output

        # Internal state — written by apply() when swept, otherwise stays at the default.
        self.frequency: float = 1000.0
        self.amplitude: float = 1.0

        # Simulated DUT: Lorentzian magnitude response centred at 1 kHz.
        self.f_resonance: float = 1000.0
        self.bandwidth: float = 200.0
        self.peak_magnitude: float = 0.1  # fraction of excitation amplitude at resonance

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Return the GUI parameters."""
        return {
            "SweepMode": ["None", "Frequency in Hz", "Amplitude in V"],
            "Noise level": 0.01,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Store the values picked in the GUI."""
        self.sweep_mode = parameter["SweepMode"]
        self.noise_level = float(parameter["Noise level"])

    def apply(self) -> None:
        """Apply the sweep value to frequency or amplitude."""
        if self.sweep_mode == "Frequency in Hz":
            self.frequency = float(self.value)
        elif self.sweep_mode == "Amplitude in V":
            self.amplitude = float(self.value)

    def call(self) -> list[float]:
        """Simulate one measurement point."""
        magnitude, phase = self._simulate(self.frequency)
        phase_rad = np.deg2rad(phase)
        x = magnitude * np.cos(phase_rad)
        y = magnitude * np.sin(phase_rad)
        return [magnitude, phase, self.frequency, float(x), float(y)]

    def _simulate(self, frequency: float) -> tuple[float, float]:
        """Lorentzian magnitude with phase rolling from +180° below resonance to -180° above."""
        detuning = (frequency - self.f_resonance) / self.bandwidth
        magnitude = self.peak_magnitude * self.amplitude / (1.0 + detuning ** 2)
        phase = -float(np.rad2deg(np.arctan(detuning))) * 2.0

        magnitude += self.noise_level * (random() - 0.5)
        phase += self.noise_level * 100.0 * (random() - 0.5)
        return magnitude, phase

    """Communication commands, used e.g. by the SweepMe! Instrument Control.

    The simulated lock-in amplifier measures a device with a resonance at 1 kHz. The commands do not need
    'initialize' or 'configure'.
    """

    @command
    def set_frequency(self, frequency: Annotated[Hertz, Range(0.0, None)]) -> None:
        """Set the reference frequency in Hz. It must be greater than 0 Hz."""
        if frequency <= 0:
            msg = f"Frequency {frequency} Hz must be greater than 0 Hz."
            raise ValueError(msg)
        self.frequency = frequency

    @command(returns=("frequency",), reads="setpoint")
    def get_frequency(self) -> Hertz:
        """Return the reference frequency in Hz."""
        return float(self.frequency)

    @command(warnings="Changes the excitation voltage at the connected device at once.")
    def set_amplitude(self, amplitude: Annotated[Volts, Range(0.0, None)]) -> None:
        """Set the excitation amplitude in V."""
        self.amplitude = amplitude

    @command(returns=("amplitude",), reads="setpoint")
    def get_amplitude(self) -> Volts:
        """Return the excitation amplitude in V."""
        return float(self.amplitude)

    @command
    def set_noise_level(self, noise_level: Annotated[float, Range(0.0, None)]) -> None:
        """Set the noise: magnitude +/- noise_level/2 in V, phase +/- 50 * noise_level in deg. 0 is deterministic."""
        self.noise_level = noise_level

    @command(returns=("magnitude", "phase"))
    def get_magnitude_and_phase(self) -> tuple[Volts, Degrees]:
        """Measure and return (magnitude in V, phase in degrees) at the set frequency and amplitude."""
        magnitude, phase = self._simulate(self.frequency)
        return float(magnitude), float(phase)

    @command(returns=("x", "y"))
    def get_xy(self) -> tuple[Volts, Volts]:
        """Measure and return the in-phase and quadrature components (X in V, Y in V)."""
        magnitude, phase = self._simulate(self.frequency)
        phase_rad = np.deg2rad(phase)
        return float(magnitude * np.cos(phase_rad)), float(magnitude * np.sin(phase_rad))

    @command(returns=("frequency", "magnitude", "phase"))
    def measure_frequency_sweep(
        self,
        start_frequency: Annotated[Hertz, Range(0.0, None)],
        stop_frequency: Annotated[Hertz, Range(0.0, None)],
        points: Annotated[int, Range(2, 10000)],
    ) -> tuple[HertzList, VoltsList, DegreesList]:
        """Measure at 'points' linearly spaced frequencies from start to stop in Hz.

        Returns the lists of the frequencies in Hz, the magnitudes in V and the phases in degrees. The set frequency
        stays unchanged.
        """
        if start_frequency <= 0 or stop_frequency <= 0:
            msg = "Start and stop frequency must be greater than 0 Hz."
            raise ValueError(msg)
        frequencies = np.linspace(start_frequency, stop_frequency, points)
        results = [self._simulate(float(frequency)) for frequency in frequencies]
        return (
            frequencies.tolist(),
            [float(magnitude) for magnitude, _ in results],
            [float(phase) for _, phase in results],
        )
