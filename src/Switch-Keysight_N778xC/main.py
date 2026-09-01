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
# * Module: Switch
# * Instrument: Keysight N778xC

from __future__ import annotations

import math
import time
from typing import Any

from pysweepme import debug
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight N778xC polarization synthesizer."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "N778xC"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["SOP"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [True]

        # Port configuration
        # Besides USBTMC, the instrument can be used as a TCPIP resource. A USB connection also enumerates as
        # a virtual Ethernet link, so the instrument can show up as a TCPIP resource without a network cable.
        self.port_manager = True
        self.port_types = ["USBTMC", "TCPIP"]
        self.port_properties = {
            "timeout": 10,
            "EOL": "\n",
        }

        # Measurement parameters
        self.mode: str = "SOP"
        self.wavelength: float = 1550.0

        # Stokes vectors S1, S2, S3 of the polarizations that are aligned to a waveguide
        self.waveguide_polarizations = {
            "TE": (1.0, 0.0, 0.0),
            "TM": (-1.0, 0.0, 0.0),
        }

        # Maximum deviation between the requested and the read back Stokes parameters
        self.sop_tolerance: float = 1e-3

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["SOP", "Waveguide Relative"],
            "Wavelength in nm": "1550.0",
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.mode = parameters.get("SweepMode", "SOP")
        self.wavelength = float(parameters.get("Wavelength in nm", "1550.0"))

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.clear_status()

        # *RST and :SYSTem:PRESet would additionally erase the settings that the user stored in the
        # non-volatile memory of the instrument, so the working memory is preset instead.
        self.preset_settings()

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        errors = self.check_errors()
        if errors:
            debug(f"Errors of the Keysight N778xC after the measurement: {errors}")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # Polarimeter commands are blocked while the stabilizer is running
        self.set_stabilization(state=False)
        self.set_polarimeter_wavelength(self.wavelength)

    def apply(self) -> None:
        """'apply' is used to set the new set value that is always available as 'self.value'."""
        if self.mode == "SOP":
            stokes_vector = self.parse_sop_string(str(self.value))

        elif self.mode == "Waveguide Relative":
            polarization = str(self.value).strip().upper()
            if polarization not in self.waveguide_polarizations:
                possible_values = "' or '".join(self.waveguide_polarizations)
                msg = f"Invalid waveguide relative polarization '{self.value}'. Use '{possible_values}'."
                raise ValueError(msg)
            stokes_vector = self.waveguide_polarizations[polarization]

        else:
            msg = f"Invalid mode '{self.mode}'. Expected 'SOP' or 'Waveguide Relative'."
            raise ValueError(msg)

        self.set_sop(*stokes_vector)

    def call(self) -> str:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        sop = self.get_sop()

        if self.mode == "Waveguide Relative":
            for polarization, stokes_vector in self.waveguide_polarizations.items():
                if self.is_matching_sop(sop, stokes_vector):
                    return polarization

            debug(f"The read back SOP {sop} does not correspond to a waveguide relative polarization.")
            return ""

        return ";".join(str(parameter) for parameter in sop)

    """ here, communication commands are wrapped into python convenience functions """

    def get_identification(self) -> str:
        """Get the instrument identification string."""
        return str(self.port.query("*IDN?"))

    def reset(self) -> None:
        """Reset the instrument to its default state.

        This also erases the settings that are stored in the non-volatile memory of the instrument.
        Use preset_settings() to keep them.
        """
        self.write_and_wait("*RST")

    def preset_settings(self) -> None:
        """Reset the settings in the working memory, keeping the settings stored in the non-volatile memory."""
        self.write_and_wait(":CONFigure:MEASurement:SETTing:PRESet")

    def clear_status(self) -> None:
        """Clear the instrument status and error queue."""
        self.write_and_wait("*CLS")

    def check_errors(self) -> str:
        """Get error list if any and parse it based on manual."""
        err_count = int(self.port.query(":SYSTem:ERRor:COUNt?"))
        if err_count == 0:
            return ""

        errors = []
        for _ in range(err_count):
            # The response has the format <error number>,"<error description>", e.g. -113,"Undefined header"
            err = self.port.query(":SYSTem:ERRor?")
            if err.split(",")[0].strip().lstrip("+") != "0":
                errors.append(err)

        return ",".join(errors)

    def set_polarimeter_wavelength(self, wavelength_nm: float) -> None:
        """Set the wavelength of the polarimeter in nm, which is needed to correctly measure the SOP."""
        self.write_and_wait(f":POLarimeter:WAVelength {wavelength_nm}NM")

    def set_sop(self, s1: float, s2: float, s3: float) -> None:
        """Set the target state of polarization (SOP) as Stokes parameters S1, S2, and S3."""
        # The instrument normalizes the target SOP to a degree of polarization of 1. Normalizing beforehand
        # makes sure that the read back value can be compared to the requested one.
        target_sop = self.normalize_stokes_vector(s1, s2, s3)

        # The target SOP is only taken over while the stabilizer is switched off
        self.set_stabilization(state=False)
        self.write_and_wait(":STABilizer:SOP {},{},{}".format(*target_sop))
        self.set_stabilization(state=True)

        # Read back the target SOP to make sure that the instrument accepted it
        read_back_sop = self.get_sop()
        if not self.is_matching_sop(read_back_sop, target_sop):
            msg = f"SOP was not correctly applied. Set value: {list(target_sop)}, read back value: {read_back_sop}."
            raise RuntimeError(msg)

    def get_sop(self) -> list[float]:
        """Return the target state of polarization (SOP) of the stabilizer as Stokes parameters S1, S2, and S3."""
        # The optional 'SOP' parameter makes the instrument return the three Stokes parameters. Without it,
        # a fourth element can be appended depending on the stabilizer mode.
        response = self.port.query(":STABilizer:SOP? SOP")
        stokes_parameters = [float(parameter) for parameter in response.split(",")]

        if len(stokes_parameters) < 3:  # noqa: PLR2004
            msg = f"Expected at least three Stokes parameters from the instrument, got '{response}'."
            raise RuntimeError(msg)

        return stokes_parameters[:3]

    def set_stabilization(self, state: bool) -> None:
        """Switch the polarization stabilizer for the SOP function on or off."""
        self.write_and_wait(f":STABilizer:STABilize {int(state)},SOP")

    def write_and_wait(self, command: str) -> None:
        """Writes a command to the device, then waits for the command execution to be completed."""
        self.port.write(command)
        self.wait_for_operation_complete()

    def wait_for_operation_complete(self, timeout: float = 10.0) -> None:
        """Checks the Operation complete query and continues only when it returns 1 (completed)."""
        start_time = time.monotonic()
        while time.monotonic() - start_time < timeout:
            if self.is_run_stopped():
                return

            if self.port.query("*OPC?").strip() == "1":
                return

            time.sleep(0.01)

        msg = f"Timeout waiting for operation to complete after {timeout} seconds."
        raise TimeoutError(msg)

    def parse_sop_string(self, value: str) -> tuple[float, float, float]:
        """Parse a 'S1;S2;S3' string into the three Stokes parameters."""
        try:
            s1, s2, s3 = (float(parameter) for parameter in value.split(";"))
        except ValueError as e:
            msg = f"Invalid SOP format. Expected three ';'-separated Stokes parameters 'S1;S2;S3', got '{value}'."
            raise ValueError(msg) from e

        return s1, s2, s3

    def normalize_stokes_vector(self, s1: float, s2: float, s3: float) -> tuple[float, float, float]:
        """Normalize a Stokes vector to a degree of polarization of 1, as it is expected by the instrument."""
        length = math.sqrt(s1**2 + s2**2 + s3**2)
        if length == 0:
            msg = "The Stokes vector '0;0;0' cannot be normalized to a degree of polarization of 1."
            raise ValueError(msg)

        return s1 / length, s2 / length, s3 / length

    def is_matching_sop(self, sop: list[float], reference: tuple[float, float, float]) -> bool:
        """Check whether a state of polarization matches a reference Stokes vector within the tolerance."""
        if len(sop) != len(reference):
            return False

        # zip() is not used with 'strict' as the drivers must remain compatible with Python 3.9
        return all(abs(sop[index] - target) <= self.sop_tolerance for index, target in enumerate(reference))
