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
# * Instrument: QCAL GMS

from __future__ import annotations

import os
import re
import time
from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the QCAL GMS."""
    description = """
    <h3>QCAL 3-Channel Gas Mixing System</h3>
    <p>This driver provides a minimal interface to the QCAL GMS gas mixing software by
    exchanging simple command and status tokens through files in
    <code>C:\ProgramData\QCAL</code>. It allows setting two concentrations (CH2, CH3)
    in Vol% and the total flow in NmL/min and reads back the instrument's reported
    values.</p>

    <h4>Setup</h4>
    <ul>
      <li>Ensure the QCAL GMS application is installed and running on the same machine as the driver.</li>
      <li>In the QCAL GMS application, enable "Setpoints by file".</li>
      <li>The driver reads from <code>zeit.txt</code> and writes commands to <code>extern.txt</code> in
      <code>C:\ProgramData\QCAL</code>. The executing user must have read/write access to that folder.</li>
      <li>No external Python library is required to communicate; the driver uses the file-based protocol the
      QCAL software provides.</li>
    </ul>

    <h4>Parameters</h4>
    <ul>
      <li><strong>Concentration CH2</strong> - concentration of component CH2 in Vol% (0–100).</li>
      <li><strong>Concentration CH3</strong> - concentration of component CH3 in Vol% (0–100).</li>
      <li><strong>Total flow</strong> - total flow in NmL/min (non-negative).</li>
    </ul>
    """

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "GMS"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Concentration CH2", "Concentration CH3", "Total flow"]
        self.units = ["Vol%", "Vol%", "mL/min"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        # Communication Parameters
        self.base_path = r"C:\ProgramData\QCAL"
        self.extern_file = os.path.join(self.base_path, "extern.txt")
        self.zeit_file = os.path.join(self.base_path, "zeit.txt")
        self.timeout_s = 5.0  # the device should read the new setpoints every 1s, so 5s is sufficient

        # Measurement parameters
        self.sweep_mode: str = "None"
        self.concentration_2: float = 0.
        self.concentration_3: float = 0.
        self.total_flow: float = 0.

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        # Use typing.Union for compatibility with type checkers that don't support `|` on types
        new_parameters = {
            "SweepMode": ["None", "Concentration 2 in Vol%", "Concentration 3 in Vol%", "Total flow in NmL/min"],
        }

        selected_sweep_mode = parameters.get("SweepMode", "None")
        if selected_sweep_mode != "Concentration 2 in Vol%":
            new_parameters["Concentration 2 in Vol%"] = 1.0

        if selected_sweep_mode != "Concentration 3 in Vol%":
            new_parameters["Concentration 3 in Vol%"] = 1.0

        if selected_sweep_mode != "Total flow in NmL/min":
            new_parameters["Total flow in NmL/min"] = 10.0

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.sweep_mode = parameters.get("SweepMode", "None")
        self.concentration_2 = parameters.get("Concentration 2 in Vol%", 1.0)
        self.concentration_3 = parameters.get("Concentration 3 in Vol%", 1.0)
        self.total_flow = parameters.get("Total flow in NmL/min", 10.0)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.update_setpoints()
        self.wait_for_confirmation()

    def unconfigure(self) -> None:
        """Set the flow rate to 0. This function is called every time the device is no longer used in the sequencer."""
        self.total_flow = 0.0
        self.update_setpoints()

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweep_mode.startswith("Concentration 2"):
            self.concentration_2 = float(self.value)
        elif self.sweep_mode.startswith("Concentration 3"):
            self.concentration_3 = float(self.value)
        elif self.sweep_mode.startswith("Total flow"):
            self.total_flow = float(self.value)

        self.update_setpoints()
        # do not wait here, as this would block the sequencer too long

    def adapt(self) -> None:
        """Wait until the device acknowledges the new set points."""
        self.wait_for_confirmation()

    def call(self) -> tuple[float, float, float]:
        """Wait until the latest response does not start with "NEW" (indicating setpoints) but with the real values."""
        while True:
            if self.is_run_stopped():
                return -1, -1, -1

            last_line = self.read_response()
            if not "NEW" in last_line:
                break
            time.sleep(0.02)

        return self.extract_setpoints_from_line(last_line)

    def update_setpoints(self) -> None:
        """Update the setpoints based on the current concentrations and total flow."""
        # Ensure correct types
        self.concentration_2 = float(self.concentration_2)
        self.concentration_3 = float(self.concentration_3)
        self.total_flow = float(self.total_flow)

        if self.total_flow < 0:
            msg = f"Invalid total flow value: {self.total_flow}. It must be non-negative."
            raise ValueError(msg)

        if not (0 <= self.concentration_2 <= 100):
            msg = f"Invalid concentration 2 value: {self.concentration_2}. It must be between 0 and 100 Vol%."
            raise ValueError(msg)

        if not (0 <= self.concentration_3 <= 100):
            msg = f"Invalid concentration 3 value: {self.concentration_3}. It must be between 0 and 100 Vol%."
            raise ValueError(msg)


        self.write_setpoints_to_file(self.concentration_2, self.concentration_3, self.total_flow)

    def write_setpoints_to_file(self, concentration_2: float, concentration_3: float, total_flow: float) -> None:
        """Write the given setpoints to extern.txt."""
        # The device expects a single-line token like "c_<c2>d_<c3>v_<flow>e".
        command = f"c_{concentration_2}d_{concentration_3}v_{total_flow}e"
        with open(self.extern_file, "w", encoding="ascii") as f:
            f.write(command)

    def wait_for_confirmation(self) -> None:
        """Wait until the device has confirmed to the new set points."""
        time_start = time.time()
        while True:
            if self.is_run_stopped():
                break

            if (time.time() - time_start) > self.timeout_s:
                msg = "Timeout while waiting for the GMS to acknowledge new setpoints."
                raise TimeoutError(msg)

            last_line = self.read_response()
            # If the total flow was set to 0, the device should respond with '_STOP'
            if self.total_flow == 0.0:
                if "_STOP" in last_line or "Operation stopped" in last_line:
                    break

            if "stop" in last_line.lower():
                msg = "The GMS reported stopped operation unexpectedly."
                raise RuntimeError(msg)

            # Confirmation of new setpoints starts with "NEW"
            if "NEW" in last_line:
                confirmed_c2, confirmed_c3, confirmed_flow = self.extract_setpoints_from_line(last_line)
                if (
                        abs(confirmed_c2 - self.concentration_2) < 1e-3 and
                        abs(confirmed_c3 - self.concentration_3) < 1e-3 and
                        abs(confirmed_flow - self.total_flow) < 1e-3
                ):
                    break

            time.sleep(0.02)

    def read_response(self) -> str:
        """Read the latest response line from zeit.txt."""
        if not os.path.exists(self.zeit_file):
            return ""

        with open(self.zeit_file, "r", encoding="ascii", errors="ignore") as f:
            lines = f.readlines()

        if not lines:
            return ""

        # Return the last line without trailing newline/whitespace.
        return lines[-1].rstrip("\n\r")

    @staticmethod
    def extract_setpoints_from_line(line: str) -> tuple[float, float, float]:
        """Extract the setpoints from a given line.

        Returns:
            A tuple (concentration_ch2, concentration_ch3, total_flow).

        If a value cannot be parsed the corresponding element will be -1.
        """
        def _extract(tag: str) -> float:
            match = re.search(rf"{tag}_([\d.,]+)", line)
            if match:
                return float(match.group(1).replace(",", "."))
            return -1

        concentration_2 = _extract("c")
        concentration_3 = _extract("d")
        total_flow = _extract("v")

        return concentration_2, concentration_3, total_flow
