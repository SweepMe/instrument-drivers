# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Keysight N778xB

from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keysight N778xB."""

    description = """
    <h3>Keysight N778xB Polarization Synthesizer</h3>
    <h4>Parameters</h4>
    <ul>
    <li>Sweep mode: Orientation and Retardation: Provide comma-separated string of orientation in rad and retardation in
     fractions of lambda. The format must be Orientation Plate 1, Retardation Plate 1, Orientation Plate 2, ...</li>
     <li>SOP: Provide semicolon separated string of 3 SOP values.</li>
    </ul>
    """
    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "N778xB"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.port_string: str = ""
        self.port_manager = True
        self.port_types = ["GPIB"]

        # Measurement parameters
        self.mode = "Orientation and Retardation"
        self.channel: int = 1

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Orientation and Retardation", "SOP"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.mode = parameter["SweepMode"]
        if self.mode == "SOP":
            self.variables = ["SOP 1", "SOP 2", "SOP 3"]
            self.units = ["", "", ""]
            self.plottype = [False, False, False]
            self.savetype = [True, True, True]

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        print(f"ID: {self.get_identification()}")

        if self.mode == "Orientation and Retardation":
            self.port.write("POLCON:PROGRAM MANUAL")  # Set the device to manual mode for orientation and retardation

        elif self.mode == "SOP":
            self.port.write(":STAB:STAB 1")  # Enable stabilization for SOP mode
            # sequence, manual, scramble, sop stalibtze

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.mode == "Orientation and Retardation":
            self.set_waveplates(self.value)
        elif self.mode == "SOP":
            try:
                stokes_1, stokes_2, stokes_3 = map(float, self.value.split(";"))
            except ValueError as e:
                msg = f"Invalid SOP value: {self.value}. Must be a semicolon-separated string of 3 numbers."
                raise ValueError(msg) from e
            self.set_sop(stokes_1, stokes_2, stokes_3)

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        if self.mode == "SOP":
            return self.get_sop()

        return []

    # Wrapper Functions

    def get_identification(self) -> str:
        """Return the identification string of the device."""
        return self.port.query("*IDN?")

    def set_mode(self, mode: str = "manual") -> None:
        """Set the polarization control mode."""
        supported_modes = ["manual", "scramble", "sequence"]
        if mode.lower() not in supported_modes:
            msg = f"Mode '{mode}' is not supported. Supported modes are: {', '.join(supported_modes)}."
            raise ValueError(msg)

        error = self.port.query(f"POLCON:PROGRAM {mode.upper()}")

    def set_waveplates(self, orientations_and_retardations: str) -> None:
        """Set the orientation and retardation for the 5 waveplates."""
        try:
            orientations_and_retardations = [float(x.strip()) for x in orientations_and_retardations.split(",")]
        except Exception as e:
            msg = f"Invalid sweep value: {orientations_and_retardations}. Must be a comma-separated string of 10 numbers."
            raise ValueError(msg) from e

        if len(orientations_and_retardations) != 10:
            msg = "Sweep Value must contain 10 elements (5 orientations and 5 retardations)."
            raise ValueError(msg)

        configuration = ""
        for n in range(5):
            orientation = orientations_and_retardations[n * 2]
            retardation = orientations_and_retardations[n * 2 + 1]
            if not (0 <= orientation <= 2 * 3.14159):
                msg = f"Orientation {n + 1} must be in the range [0, 2π]."
                raise ValueError(msg)

            max_retardation = 0.5 if n == 2 else 0.25
            if not (0 <= retardation <= max_retardation):
                msg = f"Retardation {n + 1} must be in the range [0, {max_retardation}]."
                raise ValueError(msg)

            configuration += f"{orientation},{retardation},"

        error = self.port.query(f"POLCON:WAVEPL {configuration}")

    def get_sop(self) -> list[float]:
        """Returns a single state of polarization (SOP)."""
        # TODO: could also be 'POLMET:SOP?' - manual page 226, allows NSOP as well
        # or this could return the set value, try :POL:SOP?
        response = self.port.query(":STAB:SOP?")
        return list(map(float, response.split(",")))

    def set_sop(self, stokes_1: float, stokes_2: float, stokes_3: float) -> None:
        """Set the state of polarization."""
        # TODO: Could also be
        self.port.write(f"STAB:SOP {stokes_1}, {stokes_2}, {stokes_3}")
