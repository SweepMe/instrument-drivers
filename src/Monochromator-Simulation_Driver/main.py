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

    FILTER: dict[int, tuple[float, float]] = {
        1: (200.0, 400.0),  # Filter 1
        2: (400.0, 700.0),  # Filter 2
        3: (700.0, 1100.0), # Filter 3
        4: (1100.0, 1500.0),# Filter
    }

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "Driver"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Wavelength", "Filter"]
        self.units = ["nm", "#"]
        self.plottype = [True, True]
        self.savetype = [True, True]

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
        self.filter_mode: str = "Auto"
        self.current_filter: int = 1

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": list(self.sweep_mode_units.keys()),
            "Filter": ["Auto"] + list(self.FILTER.keys()),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweep_mode = parameters.get("SweepMode", self.sweep_mode)
        self.filter_mode = parameters.get("Filter", self.filter_mode)
        self.units = [self.sweep_mode_units.get(self.sweep_mode, "nm"), "#"]

    def apply(self) -> None:
        """Set the simulated wavelength and update the filter position."""
        self.value = float(self.value)
        wavelength_nm = self._to_wavelength_nm(self.value)

        if self.filter_mode == "Auto":
            self.current_filter = self._auto_select_filter(wavelength_nm)
        else:
            self.current_filter = int(self.filter_mode)

        if not self._wavelength_is_in_filter_range(wavelength_nm, self.current_filter):
            raise ValueError(f"Wavelength {wavelength_nm:.2f} nm is out of range for filter {self.current_filter}.")

    def call(self) -> list[float | int]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.value, self.current_filter]

    def _to_wavelength_nm(self, value: float) -> float:
        """Convert the current sweep value to wavelength in nm regardless of sweep mode."""
        if self.sweep_mode in ("Wavelength in eV", "Energy in eV"):
            return 1239.84 / value
        if self.sweep_mode == "Wavelength in cm-1":
            return 1e7 / value

        return value  # already nm

    def _auto_select_filter(self, wavelength_nm: float) -> int:
        """Return the filter slot for *wavelength_nm* using the default switching wavelengths."""
        for slot, (low, high) in self.FILTER.items():
            if low <= wavelength_nm <= high:
                return slot

        raise ValueError(f"No filter available for wavelength {wavelength_nm:.2f} nm.")

    def _wavelength_is_in_filter_range(self, wavelength_nm: float, filter_slot: int) -> bool:
        """Check if the given wavelength is within the range of the given filter slot."""
        if filter_slot not in self.FILTER:
            raise ValueError(f"Invalid filter slot: {filter_slot}")
        low, high = self.FILTER[filter_slot]
        return low <= wavelength_nm <= high

