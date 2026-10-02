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

import datetime
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
from pysweepme import debug
from pysweepme.EmptyDeviceClass import EmptyDevice

# Maximum deviation between the wavelength of a correction file and the wavelength set in the GUI
CORRECTION_WAVELENGTH_TOLERANCE_NM = 0.5

# A warning is printed to the Debug widget if the correction file is older than this
CORRECTION_MAXIMUM_AGE = datetime.timedelta(days=1)


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

        # Correction of the polarization change of the fiber between the instrument and the device under test.
        # The transformation matrix M maps a Stokes vector at the instrument output onto the Stokes vector at the
        # fiber end: s_fiber_end = M * s_instrument. None means that no correction is applied.
        self.correction: str = "None"
        self.correction_file: str = ""
        self.transformation_matrix: np.ndarray | None = None
        self.inverse_matrix: np.ndarray | None = None

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameters: dict[str, Any] = {
            "SweepMode": ["SOP", "Waveguide Relative"],
            "Wavelength in nm": "1550.0",
            "Correction": ["None", "From file"],
        }

        if parameters.get("Correction", "None") == "From file":
            # The file dialog starts at the example file, which documents the expected format
            default_file = Path(self.get_folder("SELF")) / "examples" / "correction_example.json"
            gui_parameters["Correction file"] = Path(parameters.get("Correction file") or default_file)

        return gui_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.mode = parameters.get("SweepMode", "SOP")
        self.wavelength = float(parameters.get("Wavelength in nm", "1550.0"))
        self.correction = parameters.get("Correction", "None")
        self.correction_file = str(parameters.get("Correction file", ""))

        # With a correction, the SOP at the fiber end is returned and additionally the SOP set at the instrument
        if self.correction == "From file":
            self.variables = ["SOP", "Applied SOP"]
        else:
            self.variables = ["SOP"]
        self.units = [""] * len(self.variables)
        self.plottype = [False] * len(self.variables)
        self.savetype = [True] * len(self.variables)

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
        # The correction file is checked first, so that an invalid file stops the run before the instrument changes
        if self.correction == "From file":
            self.transformation_matrix = self.load_correction_file(self.correction_file)
            self.inverse_matrix = np.linalg.inv(self.transformation_matrix)
        else:
            self.transformation_matrix = None
            self.inverse_matrix = None

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

        # The requested SOP refers to the fiber end. The instrument has to set s_Synth = M^-1 * s_Ziel, which the
        # fiber turns into the requested SOP. set_sop() normalizes the vector, as the instrument expects it.
        if self.inverse_matrix is not None:
            stokes_vector = tuple(self.inverse_matrix @ np.array(stokes_vector, dtype=float))

        self.set_sop(*stokes_vector)

    def call(self) -> str | list[str]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        applied_sop = self.get_sop()

        if self.transformation_matrix is None:
            return self.format_sop(applied_sop)

        # The SOP at the fiber end is M * s_Synth, normalized to unit length like the requested SOP
        sop_at_fiber_end = self.transformation_matrix @ np.array(applied_sop, dtype=float)
        sop_at_fiber_end = sop_at_fiber_end / np.linalg.norm(sop_at_fiber_end)

        # Rounding removes the numerical noise of the transformation, adding 0.0 turns -0.0 into 0.0
        sop_at_fiber_end = [round(float(parameter), 6) + 0.0 for parameter in sop_at_fiber_end]
        return [self.format_sop(sop_at_fiber_end), ";".join(str(parameter) for parameter in applied_sop)]

    def format_sop(self, sop: list[float]) -> str:
        """Return the SOP in the format of the selected SweepMode."""
        if self.mode == "Waveguide Relative":
            for polarization, stokes_vector in self.waveguide_polarizations.items():
                if self.is_matching_sop(sop, stokes_vector):
                    return polarization

            debug(f"The read back SOP {sop} does not correspond to a waveguide relative polarization.")
            return ""

        return ";".join(str(parameter) for parameter in sop)

    """ here, the correction of the fiber polarization change is handled """

    def load_correction_file(self, file_path: str) -> np.ndarray:
        """Load the transformation matrix M for the set wavelength from a correction file and check that it is valid.

        See examples/correction_example.json for the format. Only 'calibrations', and in each calibration the keys
        'wavelength_nm' and 'transformation_matrix', are required.
        """
        path = Path(file_path)
        if not path.is_file():
            msg = f"Correction file '{file_path}' does not exist."
            raise FileNotFoundError(msg)

        with path.open(encoding="utf-8") as file:
            content = json.load(file)

        try:
            calibrations = content["calibrations"]
            calibration = min(calibrations, key=lambda entry: abs(float(entry["wavelength_nm"]) - self.wavelength))
            calibration_wavelength = float(calibration["wavelength_nm"])
            transformation_matrix = np.array(calibration["transformation_matrix"], dtype=float)
        except (KeyError, TypeError, ValueError) as e:
            msg = (
                f"Correction file '{file_path}' has an invalid format. It needs a list 'calibrations' with the keys "
                f"'wavelength_nm' and 'transformation_matrix'. See examples/correction_example.json of this driver."
            )
            raise ValueError(msg) from e

        if abs(calibration_wavelength - self.wavelength) > CORRECTION_WAVELENGTH_TOLERANCE_NM:
            msg = (
                f"Correction file '{file_path}' has no calibration for {self.wavelength} nm. The closest one is at "
                f"{calibration_wavelength} nm."
            )
            raise ValueError(msg)

        if transformation_matrix.shape != (3, 3):
            msg = f"The transformation matrix in correction file '{file_path}' must have 3x3 elements."
            raise ValueError(msg)

        # M^-1 is applied to the requested SOP, so M must be invertible
        if np.linalg.matrix_rank(transformation_matrix) < 3:  # noqa: PLR2004
            msg = f"The transformation matrix in correction file '{file_path}' is not invertible."
            raise ValueError(msg)

        created = content.get("created")
        if created:
            try:
                # The calibration script writes the local time without time zone
                age = datetime.datetime.now() - datetime.datetime.fromisoformat(created)  # noqa: DTZ005
            except ValueError:
                debug(f"N778xC: cannot read the creation time '{created}' of the correction file.")
            else:
                if age > CORRECTION_MAXIMUM_AGE:
                    debug(f"N778xC: the correction file '{file_path}' was created {age.days} day(s) ago.")

        return transformation_matrix

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
