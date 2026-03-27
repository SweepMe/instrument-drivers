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
#
# SweepMe! driver
# * Module: Monochromator
# * Instrument: Simulation Driver

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Simulation Driver."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "Driver"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Wavelength"]
        self.units = ["nm"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.port_manager = False

        # Measurement parameters
        self.sweep_mode_units = {
            "Wavelength in nm": "nm",
            "Wavelength in eV": "eV",
            "Wavelength in cm-1": "cm-1",
            "Energy in eV": "eV",
        }
        self.sweep_mode: str = "Wavelength in nm"

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": list(self.sweep_mode_units.keys()),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweep_mode = parameters.get("SweepMode", self.sweep_mode)
        self.units = [self.sweep_mode_units.get(self.sweep_mode, "nm")]

    def apply(self) -> None:
        """This driver simulates a monochromator, so there is no actual apply step."""
        self.value = float(self.value)

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.value

