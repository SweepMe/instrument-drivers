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

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


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

    def set_frequency(self, frequency: float) -> None:
        """Set the reference frequency in Hz (greater than 0 Hz)."""
        frequency = float(frequency)
        if frequency <= 0:
            msg = f"Frequency {frequency} Hz must be greater than 0 Hz."
            raise ValueError(msg)
        self.frequency = frequency

    def get_frequency(self) -> float:
        """Return the reference frequency in Hz."""
        return float(self.frequency)

    def set_amplitude(self, amplitude: float) -> None:
        """Set the excitation amplitude in V (0 V or more)."""
        amplitude = float(amplitude)
        if amplitude < 0:
            msg = f"Amplitude {amplitude} V must not be negative."
            raise ValueError(msg)
        self.amplitude = amplitude

    def get_amplitude(self) -> float:
        """Return the excitation amplitude in V."""
        return float(self.amplitude)

    def set_noise_level(self, noise_level: float) -> None:
        """Set the noise level of the simulated readings. Use 0 for a deterministic output."""
        noise_level = float(noise_level)
        if noise_level < 0:
            msg = f"Noise level {noise_level} must not be negative."
            raise ValueError(msg)
        self.noise_level = noise_level

    def get_magnitude_and_phase(self) -> tuple[float, float]:
        """Measure and return (magnitude in V, phase in degrees) at the set frequency and amplitude."""
        magnitude, phase = self._simulate(self.frequency)
        return float(magnitude), float(phase)

    def get_xy(self) -> tuple[float, float]:
        """Measure and return the in-phase and quadrature components (X in V, Y in V)."""
        magnitude, phase = self._simulate(self.frequency)
        phase_rad = np.deg2rad(phase)
        return float(magnitude * np.cos(phase_rad)), float(magnitude * np.sin(phase_rad))

    def measure_frequency_sweep(self, start_frequency: float, stop_frequency: float, points: int) -> dict:
        """Measure at 'points' linearly spaced frequencies from start to stop in Hz (2 to 10000 points).

        Returns a dictionary with the lists 'frequency' in Hz, 'magnitude' in V and 'phase' in degrees. The set
        frequency stays unchanged.
        """
        start_frequency = float(start_frequency)
        stop_frequency = float(stop_frequency)
        points = int(points)
        if start_frequency <= 0 or stop_frequency <= 0:
            msg = "Start and stop frequency must be greater than 0 Hz."
            raise ValueError(msg)
        if not 2 <= points <= 10000:
            msg = f"Points {points} must be between 2 and 10000."
            raise ValueError(msg)
        frequencies = np.linspace(start_frequency, stop_frequency, points)
        results = [self._simulate(float(frequency)) for frequency in frequencies]
        return {
            "frequency": frequencies.tolist(),
            "magnitude": [float(magnitude) for magnitude, _ in results],
            "phase": [float(phase) for _, phase in results],
        }
