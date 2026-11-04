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
# * Module: Logger
# * Instrument: Yokogawa AQ6374 optical spectrum analyzer

from __future__ import annotations

import time
from typing import Any

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice

# Bit 0 of the operation event register is set when a sweep has been completed.
SWEEP_COMPLETE_BIT = 1

# A sweep can take several minutes for high sensitivity modes and small resolutions.
SWEEP_TIMEOUT_S = 600.0
SWEEP_POLL_INTERVAL_S = 0.1

# Analysis functions and the values that ':CALCulate:DATA?' returns for them, see sections 6.6 and 6.7 of the
# AQ6374 remote control manual. ':CALCulate:DATA?' has no key based access: it returns one flat, comma separated
# list whose meaning is defined by the selected ':CALCulate:CATegory', so the fields must be assigned by position.
# Each entry maps the GUI label to the category parameter and to the (name, unit) of each returned value in order.
ANALYSIS_FUNCTIONS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "None": ("", []),
    "Spectrum width (THRESH)": (
        "SWTHresh",
        [("Center wavelength", "m"), ("Spectrum width", "m"), ("Mode number", "")],
    ),
    "Spectrum width (ENVELOPE)": (
        "SWENvelope",
        [("Center wavelength", "m"), ("Spectrum width", "m"), ("Mode number", "")],
    ),
    "Spectrum width (PEAK RMS)": (
        "SWPKrms",
        [("Center wavelength", "m"), ("Spectrum width", "m"), ("Mode number", "")],
    ),
    "Spectrum width (RMS)": (
        "SWRMs",
        [("Center wavelength", "m"), ("Spectrum width", "m")],
    ),
    "Notch width": (
        "NOTCh",
        [("Center wavelength", "m"), ("Notch width", "m")],
    ),
    "SMSR": ("SMSR", []),  # the returned values depend on the SMSR mode, see SMSR_MODE_FIELDS
    "Power": (
        "POWer",
        [("Total power", "dBm")],
    ),
    "DFB-LD": (
        "DFBLd",
        [
            ("Spectrum width", "m"),
            ("Peak wavelength", "m"),
            ("Peak level", "dBm"),
            ("Mode offset", "m"),
            ("SMSR", "dB"),
        ],
    ),
    "FP-LD": (
        "FPLD",
        [
            ("Spectrum width", "m"),
            ("Peak wavelength", "m"),
            ("Peak level", "dBm"),
            ("Center wavelength", "m"),
            ("Total power", "dBm"),
            ("Mode number", ""),
        ],
    ),
    "LED": (
        "LED",
        [
            ("Spectrum width", "m"),
            ("Peak wavelength", "m"),
            ("Peak level", "dBm"),
            ("Center wavelength", "m"),
            ("Total power", "dBm"),
        ],
    ),
    "PMD": (
        "PMD",
        [("Left mode peak", "Hz"), ("Right mode peak", "Hz"), ("PMD", "ps")],
    ),
    "Filter peak": (
        "FILPk",
        [
            ("Peak wavelength", "m"),
            ("Peak level", "dBm"),
            ("Center wavelength", "m"),
            ("Spectrum width", "m"),
            ("Left crosstalk", "dB"),
            ("Right crosstalk", "dB"),
            ("Ripple", "m"),
        ],
    ),
    "Filter bottom": (
        "FILBtm",
        [
            ("Bottom wavelength", "m"),
            ("Bottom level", "dBm"),
            ("Center wavelength", "m"),
            ("Notch width", "m"),
            ("Left crosstalk", "dB"),
            ("Right crosstalk", "dB"),
        ],
    ),
    "Color": (
        "COLor",
        [("Dominant wavelength", "m"), ("x", ""), ("y", ""), ("z", "")],
    ),
}

# The SMSR analysis returns a different set of values per SMSR mode. SMSR1 and SMSR2 evaluate one side mode,
# SMSR3 and SMSR4 evaluate the side mode on the shorter (L) and on the longer (R) wavelength side.
SMSR_MODE_FIELDS: dict[str, list[tuple[str, str]]] = {
    "SMSR1": [
        ("Peak wavelength", "m"),
        ("Peak level", "dBm"),
        ("2nd peak wavelength", "m"),
        ("2nd peak level", "dB"),
        ("Delta wavelength", "m"),
        ("SMSR", "dB"),
    ],
    "SMSR3": [
        ("Peak wavelength", "m"),
        ("Peak level", "dBm"),
        ("2nd peak wavelength L", "m"),
        ("2nd peak level L", "dB"),
        ("Delta wavelength L", "m"),
        ("SMSR L", "dB"),
        ("2nd peak wavelength R", "m"),
        ("2nd peak level R", "dB"),
        ("Delta wavelength R", "m"),
        ("SMSR R", "dB"),
    ],
}
SMSR_MODE_FIELDS["SMSR2"] = SMSR_MODE_FIELDS["SMSR1"]
SMSR_MODE_FIELDS["SMSR4"] = SMSR_MODE_FIELDS["SMSR3"]


class Device(EmptyDevice):
    """Driver for the Yokogawa AQ6374 optical spectrum analyzer."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "AQ6374"  # short name will be shown in the sequencer
        # will be extended by the fields of the selected analysis function in apply_gui_parameters
        self.variables = ["Wavelength", "Intensity", "Marker wavelength", "Marker level"]
        self.units = ["m", "dBm", "m", "dBm"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        # Port configuration
        self.port_manager = True
        self.port_types = ["GPIB", "USBTMC", "TCPIP"]
        self.port_properties = {
            "timeout": 20,
        }

        self.traces = ["TRA", "TRB", "TRC", "TRD", "TRE", "TRF", "TRG"]
        self.sensitivity_modes = ["MID", "NORMal", "HIGH1", "HIGH2", "HIGH3", "NHLD", "NAUT"]

        # Measurement parameters, the numbers are kept as GUI strings and converted in configure()
        self.trace: str = "TRA"
        self.start_wavelength_string: str = "1545.0"
        self.stop_wavelength_string: str = "1565.0"
        self.resolution_string: str = "0.1"
        self.start_wavelength_nm: float = 1545.0
        self.stop_wavelength_nm: float = 1565.0
        self.resolution_nm: float = 0.1
        self.sensitivity: str = "MID"
        self.analysis: str = "None"
        self.analysis_category: str = ""
        self.analysis_fields: list[tuple[str, str]] = []
        self.smsr_mode: str = "SMSR1"

        # Measurement results
        self.wavelengths: np.ndarray[Any, Any] = np.array([])
        self.intensities: np.ndarray[Any, Any] = np.array([])
        self.peak_wavelength: float = float("nan")
        self.peak_level: float = float("nan")
        self.analysis_values: list[float] = []

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        new_parameters = {
            "Active trace": self.traces,
            "Start wavelength in nm": parameters.get("Start wavelength in nm", "1545.0"),
            "Stop wavelength in nm": parameters.get("Stop wavelength in nm", "1565.0"),
            "Resolution in nm": parameters.get("Resolution in nm", "0.1"),
            "Sensitivity": self.sensitivity_modes,
            "Analysis": list(ANALYSIS_FUNCTIONS.keys()),
        }

        # The SMSR analysis returns a different number of values per mode, so the mode must be known beforehand
        if parameters.get("Analysis", "None") == "SMSR":
            new_parameters["SMSR mode"] = list(SMSR_MODE_FIELDS.keys())

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.trace = parameters.get("Active trace", "TRA")
        self.start_wavelength_string = str(parameters.get("Start wavelength in nm", "1545.0"))
        self.stop_wavelength_string = str(parameters.get("Stop wavelength in nm", "1565.0"))
        self.resolution_string = str(parameters.get("Resolution in nm", "0.1"))
        self.sensitivity = parameters.get("Sensitivity", "MID")

        self.analysis = parameters.get("Analysis", "None")
        if self.analysis not in ANALYSIS_FUNCTIONS:
            self.analysis = "None"
        self.analysis_category, self.analysis_fields = ANALYSIS_FUNCTIONS[self.analysis]
        if self.analysis == "SMSR":
            self.smsr_mode = parameters.get("SMSR mode", "SMSR1")
            self.analysis_fields = SMSR_MODE_FIELDS.get(self.smsr_mode, SMSR_MODE_FIELDS["SMSR1"])

        # Only the values of the selected analysis function are returned. The marker values are named
        # differently than the analysis values so that the variable names stay unique for every analysis.
        self.variables = ["Wavelength", "Intensity", "Marker wavelength", "Marker level"]
        self.units = ["m", "dBm", "m", "dBm"]
        for name, unit in self.analysis_fields:
            self.variables.append(name)
            self.units.append(unit)

        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

        self.analysis_values = [float("nan")] * len(self.analysis_fields)

    def initialize(self) -> None:
        """Initialize the instrument. This function is called only once at the start of the measurement."""
        self.reset()
        self.set_command_format()
        self.clear_status()
        self.set_ascii_data_format()

    def configure(self) -> None:
        """Configure the instrument. This function is called every time the driver is used in the sequencer."""
        self.start_wavelength_nm = self.to_float(self.start_wavelength_string, "Start wavelength in nm")
        self.stop_wavelength_nm = self.to_float(self.stop_wavelength_string, "Stop wavelength in nm")
        self.resolution_nm = self.to_float(self.resolution_string, "Resolution in nm")

        self.set_active_trace(self.trace)
        self.set_start_wavelength(self.start_wavelength_nm)
        self.set_stop_wavelength(self.stop_wavelength_nm)
        self.set_resolution(self.resolution_nm)
        self.set_sensitivity(self.sensitivity)
        self.set_sampling_points_auto(state=True)

        self.set_sweep_mode_single()
        self.set_marker_auto(state=True)

        if self.analysis_category:
            self.set_analysis_category(self.analysis_category)
            if self.analysis == "SMSR":
                self.set_smsr_mode(self.smsr_mode)

    def measure(self) -> None:
        """Trigger the acquisition of a new spectrum."""
        self.clear_status()  # the sweep completion is detected via the operation event register
        self.start_sweep()

    def request_result(self) -> None:
        """Wait until the sweep has finished and read out the spectrum and the analysis results."""
        self.wait_for_sweep_completion()

        self.wavelengths = self.get_trace_x(self.trace)
        self.intensities = self.get_trace_y(self.trace)
        self.peak_wavelength, self.peak_level = self.get_marker_maximum()

        if self.analysis_category:
            self.analysis_values = self.get_analysis_data()

    def call(self) -> list[np.ndarray[Any, Any] | float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [
            self.wavelengths,
            self.intensities,
            self.peak_wavelength,
            self.peak_level,
            *self.analysis_values,
        ]

    def wait_for_sweep_completion(self) -> None:
        """Poll the operation event register until the sweep is completed, aborted, or the timeout is reached."""
        deadline = time.monotonic() + SWEEP_TIMEOUT_S

        while not self.is_sweep_completed():
            if self.is_run_stopped():
                self.abort_sweep()
                return

            if time.monotonic() > deadline:
                self.abort_sweep()
                msg = f"Sweep did not finish within the timeout period of {SWEEP_TIMEOUT_S} s."
                raise TimeoutError(msg)

            time.sleep(SWEEP_POLL_INTERVAL_S)

    @staticmethod
    def to_float(value: str, name: str) -> float:
        """Convert a GUI value to float, raise an error that names the GUI field if this is not possible."""
        try:
            return float(value)
        except ValueError:
            msg = f"Cannot interpret '{value}' of '{name}' as a number."
            raise ValueError(msg) from None

    # wrapped communication commands below

    def get_identification(self) -> str:
        """Get the instrument identification string."""
        return str(self.port.query("*IDN?"))

    def reset(self) -> None:
        """Reset the instrument to its default state."""
        self.port.write("*RST")

    def clear_status(self) -> None:
        """Clear the status registers and the error queue."""
        self.port.write("*CLS")

    def set_command_format(self) -> None:
        """Switch the instrument to the AQ637x command set."""
        self.port.write("CFORM1")

    def set_ascii_data_format(self) -> None:
        """Return trace and analysis data as ASCII instead of binary blocks."""
        self.port.write(":FORMat:DATA ASCii")

    def set_active_trace(self, trace: str) -> None:
        """Set the trace that is swept and read out, e.g. 'TRA'."""
        if trace not in self.traces:
            msg = f"Invalid trace {trace}. Choose from {self.traces}."
            raise ValueError(msg)
        self.port.write(f":TRACe:ACTive {trace}")

    def set_start_wavelength(self, wavelength_nm: float) -> None:
        """Set the start wavelength of the sweep in nm."""
        self.port.write(f":SENSe:WAVelength:STARt {wavelength_nm}NM")

    def set_stop_wavelength(self, wavelength_nm: float) -> None:
        """Set the stop wavelength of the sweep in nm."""
        self.port.write(f":SENSe:WAVelength:STOP {wavelength_nm}NM")

    def set_resolution(self, resolution_nm: float) -> None:
        """Set the resolution bandwidth in nm."""
        self.port.write(f":SENSe:BANDwidth:RESolution {resolution_nm}NM")

    def set_sensitivity(self, sensitivity: str) -> None:
        """Set the sensitivity/chop mode, e.g. 'MID' or 'HIGH1'."""
        if sensitivity not in self.sensitivity_modes:
            msg = f"Invalid sensitivity {sensitivity}. Choose from {self.sensitivity_modes}."
            raise ValueError(msg)
        self.port.write(f":SENSe:SENSe {sensitivity}")

    def set_sampling_points_auto(self, state: bool) -> None:
        """Let the instrument choose the number of sampling points from span and resolution."""
        self.port.write(f":SENSe:SWEep:POINts:AUTO {'ON' if state else 'OFF'}")

    def set_sweep_mode_single(self) -> None:
        """Set the sweep mode to single sweep."""
        self.port.write(":INITiate:SMODe 1")

    def start_sweep(self) -> None:
        """Start a sweep."""
        self.port.write(":INITiate")

    def abort_sweep(self) -> None:
        """Stop a running sweep."""
        self.port.write(":ABORt")

    def is_sweep_completed(self) -> bool:
        """Check the sweep completion bit of the operation event register.

        The register is cleared when it is read, so a set bit is only reported once.
        """
        status = int(self.port.query(":STATus:OPERation:EVENt?"))
        return bool(status & SWEEP_COMPLETE_BIT)

    def get_trace_x(self, trace: str) -> np.ndarray[Any, Any]:
        """Get the wavelength values of the given trace in m."""
        return self.query_values(f":TRACe:X? {trace}")

    def get_trace_y(self, trace: str) -> np.ndarray[Any, Any]:
        """Get the level values of the given trace in dBm."""
        return self.query_values(f":TRACe:Y? {trace}")

    def set_marker_auto(self, state: bool) -> None:
        """Enable or disable the automatic marker placement."""
        self.port.write(f":CALCulate:MARKer:AUTO {'ON' if state else 'OFF'}")

    def get_marker_maximum(self) -> tuple[float, float]:
        """Move the moving marker to the maximum of the trace and return its wavelength in m and level in dBm."""
        self.port.write(":CALCulate:MARKer:MAXimum")
        wavelength = float(self.port.query(":CALCulate:MARKer:X? 0"))
        level = float(self.port.query(":CALCulate:MARKer:Y? 0"))
        return wavelength, level

    def set_analysis_category(self, category: str) -> None:
        """Set the analysis function that is executed by ':CALCulate', e.g. 'SMSR'."""
        self.port.write(f":CALCulate:CATegory {category}")

    def set_smsr_mode(self, mode: str) -> None:
        """Set the side mode that the SMSR analysis evaluates, 'SMSR1' to 'SMSR4'."""
        if mode not in SMSR_MODE_FIELDS:
            msg = f"Invalid SMSR mode {mode}. Choose from {list(SMSR_MODE_FIELDS.keys())}."
            raise ValueError(msg)
        self.port.write(f":CALCulate:PARameter:CATegory:SMSR:MODE {mode}")

    def get_analysis_data(self) -> list[float]:
        """Execute the configured analysis and return its results in the order defined by the analysis function."""
        self.port.write(":CALCulate")
        values = self.query_values(":CALCulate:DATA?")

        if len(values) != len(self.analysis_fields):
            msg = (
                f"The '{self.analysis}' analysis returned {len(values)} values, but "
                f"{len(self.analysis_fields)} were expected: {[name for name, _ in self.analysis_fields]}."
            )
            raise ValueError(msg)

        return [float(value) for value in values]

    def query_values(self, command: str) -> np.ndarray[Any, Any]:
        """Send a query and interpret the comma separated ASCII response as an array of floats."""
        response = self.port.query(command)
        return np.array(response.split(","), dtype=float)

    def get_error_message(self) -> str:
        """Get the oldest entry of the instrument error queue."""
        return str(self.port.query(":SYSTem:ERRor?"))
