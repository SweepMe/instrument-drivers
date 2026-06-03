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
