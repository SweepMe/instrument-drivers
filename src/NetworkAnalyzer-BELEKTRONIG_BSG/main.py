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
# * Module: NetworkAnalyzer
# * Instrument: BELEKTRONIG BSG0302

"""SweepMe! network-analyzer driver for BELEKTRONIG BSG0302 S-parameter scans."""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray
from pysweepme.EmptyDeviceClass import EmptyDevice

FREQUENCY_MIN_HZ = 1e6
FREQUENCY_MAX_HZ = 215e6
POWER_MIN_DBM = -30.0
POWER_MAX_DBM = 36.0
POINTS_MIN = 2
POINTS_MAX = 65535
SCAN_BLOCK_POINTS = 8
VALID_SPARAMETERS = ("S11", "S12", "S21", "S22")


class Device(EmptyDevice):
    """Driver for BELEKTRONIG BSG0302 reflection/transmission S-parameter scans."""

    def __init__(self) -> None:
        """Initialize the device class and the communication parameters."""
        super().__init__()

        self.shortname = "BSG0302"

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "baudrate": 9600,
            "timeout": 0.5,
            "EOL": "\r",
        }

        self.sparameters: list[str] = ["S11"]
        self.frequency_start_hz: float = FREQUENCY_MIN_HZ
        self.frequency_stop_hz: float = FREQUENCY_MAX_HZ
        self.points: int = 101
        self.unit: str = "lin"

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI parameter options of the driver."""
        return {
            "Sparameters": "S11",
            "SourcePower": "0.0",  # max 10dbm

            "FrequencyStart": "1e6",
            "FrequencyEnd": "215e6",

            "FrequencyStepPointsType": ["Linear (points)"],
            "FrequencyStepPoints": "101",
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameter selections and define the return variables."""
        self.sparameters = parameters.get("Sparameters", "S11").replace(" ", "").split(",")
        try:
            self.source_power = float(parameters.get("SourcePower", 0.0))
            self.frequency_start_hz = float(parameters.get("FrequencyStart", 1e6))
            self.frequency_stop_hz = float(parameters.get("FrequencyEnd", 215e6))
            self.points = int(parameters.get("FrequencyStepPoints", 101))
        except:
            pass
        self.unit = parameters.get("Unit", "lin")

        self.variables = ["Frequency", *self.sparameters]
        self.units = ["Hz", *(["dB"] * len(self.sparameters))]
        self.plottype = [True, *([False] * len(self.sparameters))]
        self.savetype = [True, *([True] * len(self.sparameters))]

    # --- SweepMe! semantic phases ---------------------------------------------------------------

    def initialize(self) -> None:
        """Validate the scan settings and that the device responds."""
        for param in self.sparameters:
            if param not in VALID_SPARAMETERS:
                msg = f"invalid S-parameter '{param}'. Use any of {VALID_SPARAMETERS}."
                raise Exception(msg)

        if not FREQUENCY_MIN_HZ <= self.frequency_start_hz < self.frequency_stop_hz <= FREQUENCY_MAX_HZ:
            msg = f"Frequency range must satisfy {FREQUENCY_MIN_HZ * 1E-6} MHz <= start < stop <= {FREQUENCY_MAX_HZ * 1E-6} MHz."
            raise Exception(msg)

        if not POINTS_MIN <= self.points <= POINTS_MAX:
            msg = f"Points {self.points} out of range ({POINTS_MIN}-{POINTS_MAX})."
            raise Exception(msg)

        if self.get_identification() <= 0:
            msg = "No valid serial number returned. Check port and baud rate."
            raise Exception(msg)

    def configure(self) -> None:
        """Configure measurement parameters."""
        # TODO: unsure if this is correct
        for channel in (1, 2):
            self.set_output_power_dbm(channel, int(self.source_power))

    def call(self) -> list[NDArray[np.float64]]:
        """Run each requested S-parameter scan and return the frequency and S arrays."""
        frequencies = np.linspace(self.frequency_start_hz, self.frequency_stop_hz, self.points)
        results: list[NDArray[np.float64]] = [frequencies]
        for param in self.sparameters:
            results.append(self.get_s_scan(param))
        return results

    # --- Wrapped device commands --------------------------------------------------------------------------------

    def get_identification(self) -> int:
        """Return the device serial number (command N20)."""
        return self._query("N20", 4, signed=True)

    def set_output_power_dbm(self, channel: int, power_dbm: float) -> None:
        """Set the output power in dBm (command p3, -30 to 36 dBm)."""
        if not POWER_MIN_DBM <= power_dbm <= POWER_MAX_DBM:
            msg = f"Power {power_dbm} dBm out of range ({POWER_MIN_DBM} to {POWER_MAX_DBM} dBm)."
            raise Exception(msg)
        self._write(f"p3{channel}", int(power_dbm * 100), 2, signed=True)

    def get_s_scan(self, param: str) -> NDArray[np.float64]:
        """Configure, trigger and read a reflection or transmission scan.

        S11/S22 use a reflection scan, S12/S21 a transmission scan. The channel
        is 2 for S2x and 1 otherwise. Returns the S array in dB.
        """
        channel = 2 if param.startswith("S2") else 1
        direction = "transmission" if param in ("S12", "S21") else "reflection"

        self.set_scan_points(channel, self.points, direction)
        self.set_start_frequency(channel, self.frequency_start_hz, direction)
        self.set_stop_frequency(channel, self.frequency_stop_hz, direction)
        self.trigger_measurement(channel, direction)

        return self._read_scan_data(self.points)

    def _read_scan_data(self, points: int) -> NDArray[np.float64]:
        """Read back the scan points in blocks of 8 as big-endian int16 (value/100 = dB)."""
        bsg_int16 = np.dtype(np.int16).newbyteorder(">")
        s_values = np.array([])
        remaining = points
        while remaining > 0:
            count = SCAN_BLOCK_POINTS if remaining > SCAN_BLOCK_POINTS else remaining
            need = count * 2
            self.port.write("S50")
            block = b""
            attempts = 0
            while len(block) < need and attempts < 100:  # noqa: PLR2004
                block += self.port.read_raw(need - len(block))
                attempts += 1
            value_db = np.frombuffer(block, count=count, dtype=bsg_int16) / 100
            s_values = np.append(s_values, value_db)
            remaining -= SCAN_BLOCK_POINTS
        return s_values

    # --- Scan settings -----------------------------------------------------------------------

    def set_start_frequency(self, channel: int, frequency_hz: float, direction: str) -> None:
        """Set the start frequency for a scan (command d3x for reflection, d4x for transmission)."""
        if not FREQUENCY_MIN_HZ <= frequency_hz <= FREQUENCY_MAX_HZ:
            msg = f"Frequency {frequency_hz} Hz out of range ({FREQUENCY_MIN_HZ}-{FREQUENCY_MAX_HZ} Hz)."
            raise ValueError(msg)

        command = f"d{self._direction_command(direction)}{channel}"
        self._write(command, int(frequency_hz), 4, signed=True)

    def set_stop_frequency(self, channel: int, frequency_hz: float, direction: str) -> None:
        """Set the stop frequency for a scan (command g3x for reflection, g4x for transmission)."""
        if not FREQUENCY_MIN_HZ <= frequency_hz <= FREQUENCY_MAX_HZ:
            msg = f"Frequency {frequency_hz} Hz out of range ({FREQUENCY_MIN_HZ}-{FREQUENCY_MAX_HZ} Hz)."
            raise ValueError(msg)

        command = f"g{self._direction_command(direction)}{channel}"
        self._write(command, int(frequency_hz), 4, signed=True)

    def set_scan_points(self, channel: int, points: int, direction: str) -> None:
        """Set the number of points for a scan (command q3x for reflection, q4x for transmission)."""
        if not POINTS_MIN <= points <= POINTS_MAX:
            msg = f"Points {points} out of range ({POINTS_MIN}-{POINTS_MAX})."
            raise ValueError(msg)

        command = f"q{self._direction_command(direction)}{channel}"
        self._write(command, points, 2, signed=False)

    def trigger_measurement(self, channel: int, direction: str) -> None:
        """Trigger a scan measurement (command t3x for reflection, t4x for transmission)."""
        command = f"t{self._direction_command(direction)}{channel}"
        self._write(command, 1, 1, signed=False)

    @staticmethod
    def _direction_command(direction: str) -> str:
        """Return the command prefix for the given direction."""
        if direction == "reflection":
            return "3"
        elif direction == "transmission":
            return "4"
        else:
            msg = f"Invalid direction '{direction}'. Use 'reflection' or 'transmission'."
            raise ValueError(msg)

    # --- Low level framing -----------------------------------------------------------------------

    def _write(self, command: str, parameter: int, num_bytes: int, *, signed: bool) -> None:
        """Send a write command with a big-endian parameter and check the status byte."""
        payload = command + parameter.to_bytes(num_bytes, "big", signed=signed).decode("latin-1")
        self.port.write(payload)
        status = self.port.read_raw(1)
        self._check_error(int.from_bytes(status, "big"))

    def _query(self, command: str, num_ret_bytes: int, *, signed: bool) -> int:
        """Send a read command and return the big-endian integer response."""
        self.port.write(command)
        return int.from_bytes(self.port.read_raw(num_ret_bytes), "big", signed=signed)

    @staticmethod
    def _check_error(status: int) -> None:
        """Raise on the BSG status byte error bits (0 means no error / no response)."""
        errors = {
            1 << 1: "no active command",
            1 << 2: "incorrect channel number",
            1 << 3: "parameter out of range",
            1 << 5: "incorrect termination character",
        }
        for bit, message in errors.items():
            if status & bit:
                msg = f"BSG0302 communication error: {message}."
                raise Exception(msg)
