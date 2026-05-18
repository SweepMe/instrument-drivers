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
# * Module: Switch
# * Instrument: New Era NE-500 OEM syringe pump

"""SweepMe! driver for New Era NE-500 OEM syringe pumps (RS-232, basic mode)."""

from __future__ import annotations

from typing import Any, ClassVar

from pysweepme.EmptyDeviceClass import EmptyDevice

STX = "\x02"
ETX = "\x03"

MAX_SYRINGE_DIAMETER_MM = 50.0

# Rate unit -> NE-500 RAT command suffix
PUMP_RATE_UNITS: dict[str, str] = {
    "ul/h": "UH",
    "ul/min": "UM",
    "ml/h": "MH",
    "ml/min": "MM",
}

# GUI direction -> NE-500 DIR command argument
PUMP_DIRECTIONS: dict[str, str] = {
    "Infuse": "INF",
    "Withdraw": "WDR",
}

# Status prompt character -> human readable meaning
PUMP_STATUS_PROMPTS: dict[str, str] = {
    "I": "Infusing",
    "W": "Withdrawing",
    "S": "Stopped",
    "P": "Paused",
    "T": "Pause phase",
    "U": "Operational trigger wait",
    "X": "Purging",
}

# Error token returned in the response data field -> human readable meaning
PUMP_ERROR_LIST: dict[str, str] = {
    "?": "command not recognized",
    "?NA": "command currently not applicable",
    "?OOR": "command data out of range",
    "?COM": "invalid communication packet received",
    "?IGN": "command ignored because of simultaneous new phase start",
}


class Device(EmptyDevice):
    """Driver for the New Era NE-500 OEM syringe pump using the basic RS-232 protocol."""

    # Error tokens checked longest-first so '?OOR' is not shadowed by '?'.
    _ERROR_TOKENS: ClassVar[list[str]] = ["?OOR", "?COM", "?IGN", "?NA", "?"]

    def __init__(self) -> None:
        """Initialize the device class and the communication parameters."""
        super().__init__()

        self.shortname = "NE-50x"

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "baudrate": 19200,
            "timeout": 0.5,
            "EOLwrite": "\r",
            "EOLread": ETX,
        }

        self.sweepmode: str = "None"
        self.address: str = "0"
        self.rate_unit: str = "ul/min"
        self.syringe_diameter: float = 8.585
        self.direction: str = "Infuse"
        self.low_noise_mode: bool = True

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI parameter options of the driver."""
        return {
            "SweepMode": ["None", "Flow rate"],
            "Pump address": "0",
            "Rate unit": list(PUMP_RATE_UNITS),
            "Direction": list(PUMP_DIRECTIONS),
            "Syringe diameter in mm": "8.585",
            "Low motor noise": True,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameter selections and define the return variables."""
        self.sweepmode = parameters.get("SweepMode", "Flow rate")
        self.address = str(parameters.get("Pump address", "0"))
        self.rate_unit = parameters.get("Rate unit", "ul/min")
        self.direction = parameters.get("Direction", "Infuse")
        self.syringe_diameter = float(parameters.get("Syringe diameter in mm", "8.585"))
        self.low_noise_mode = bool(parameters.get("Low motor noise mode", True))

        self.variables = ["Flow rate"]
        self.units = [self.rate_unit]
        self.plottype = [True]
        self.savetype = [True]

    def connect(self) -> None:
        """Verify a pump answers on the selected port."""
        # self._write_command("*RESET")  # reset the pump to a known state
        status = self.get_status()
        if status == "":
            msg = "No status returned. Check pump address, baud rate and cabling."
            raise Exception(msg)

    def configure(self) -> None:
        """Stop the pump and apply the static syringe settings."""
        # start basic mode
        self._write_command("\x02\x08SAF0\x55\x43\x03")
        self.stop_pump()
        self.set_low_noise_mode(self.low_noise_mode)
        self.set_syringe_diameter(self.syringe_diameter)
        self.set_pump_direction(self.direction)

        # set zero flow rate to only define the unit
        self.set_flowrate(0.0, self.rate_unit)

    def apply(self) -> None:
        """Set the new flow rate from the sweep value and (re)start pumping."""
        if self.sweepmode == "None":
            return

        try:
            value = float(self.value)
        except ValueError:
            msg = f"Invalid sweep value '{self.value}'. Check the sweep configuration."
            raise Exception(msg)

        self.set_flowrate(value)

    def unconfigure(self) -> None:
        """Stop the pump at the end of the branch."""
        self.stop_pump()

    def call(self) -> float:
        """Return the applied flow rate and the live pump status."""
        return self.get_flowrate()

    # --- Wrapped device commands (ported from the contributed, tested SyringePump) ---------------

    def get_status(self) -> str:
        """Query the pump and return the single-character status prompt."""
        _, status, _ = self._query("ADR")
        return status

    def run(self) -> None:
        """Start pumping."""
        self._write_command(f"{self.address}RUN")

    def stop_pump(self) -> None:
        """Stop pumping."""
        self._write_command(f"{self.address}STP")

    def get_flowrate(self) -> float:
        """Query the pump and return the current flow rate in the set unit."""
        _, _, data = self._query("RAT")
        try:
            return float(data)
        except ValueError:
            msg = f"Invalid flow rate response '{data}'. Check pump address, baud rate and cabling."
            raise Exception(msg)

    def set_flowrate(self, rate: float, unit: str = "") -> None:
        """Set the pumping rate in the given unit (one of PUMP_RATE_UNITS).

        Unit can only be changed if the pump is stopped.
        """
        if unit:
            if unit not in PUMP_RATE_UNITS:
                msg = f"Unknown rate unit '{unit}'. Use one of {list(PUMP_RATE_UNITS)}."
                raise Exception(msg)
            unit = PUMP_RATE_UNITS[unit]
        self._write_command(f"{self.address}RAT{self._format_float(rate)}{unit}")

    def set_syringe_diameter(self, diameter: float) -> None:
        """Set the inner syringe diameter in mm (maximum 50 mm)."""
        if not 0.0 < diameter <= MAX_SYRINGE_DIAMETER_MM:
            msg = f"Syringe diameter {diameter} mm out of range (0 < d <= 50)."
            raise Exception(msg)
        self._write_command(f"{self.address}DIA{self._format_float(diameter)}")

    def set_low_noise_mode(self, low_noise: bool) -> None:
        """Set low noise mode (True or False)."""
        self._write_command(f"{self.address}LNM{low_noise:d}")

    def set_pump_direction(self, direction: str) -> None:
        """Set the pumping direction ('Infuse' or 'Withdraw')."""
        if direction not in PUMP_DIRECTIONS:
            msg = f"Unknown direction '{direction}'. Use one of {list(PUMP_DIRECTIONS)}."
            raise Exception(msg)
        self._write_command(f"{self.address}DIR{PUMP_DIRECTIONS[direction]}")

    def start_basic_mode(self) -> None:
        """Disable safe mode so the pump uses the basic protocol.

        Sends the raw safe-mode 'SAF0' frame directly (bypassing the port-manager EOL).
        Only needed if the pump was previously switched to safe mode.
        """
        self.port.port.write(b"\x02\x08SAF0\x55\x43\x03")

    # --- Low level framing -----------------------------------------------------------------------

    @staticmethod
    def _format_float(value: float) -> str:
        """Format a float for the NE-500 (max 4 digits plus 1 decimal point, max 3 decimals)."""
        ne500_max_digits = 4
        ne500_max_decimals = 3

        if not -1000 < value < 1000:
            msg = f"Value {value} is outside the NE-500 number format (max 4 digits)."
            raise Exception(msg)

        decimals = min(ne500_max_decimals, ne500_max_digits - len(str(int(abs(value)))))
        text = f"{value:.{decimals}f}"

        # rounding may add an integer digit (e.g. 999.95 -> '1000.0'); shrink the decimals
        while decimals > 0 and sum(c.isdigit() for c in text) > ne500_max_digits:
            decimals -= 1
            text = f"{value:.{decimals}f}"

        if sum(c.isdigit() for c in text) > ne500_max_digits:
            msg = f"Value {value} cannot be represented in the NE-500 number format (max 4 digits)."
            raise Exception(msg)

        return text

    def _write_command(self, command: str) -> tuple[str, str, str]:
        """Send an addressed command and validate the framed response."""
        return self._query(command)

    def _query(self, command: str) -> tuple[str, str, str]:
        """Send '<address><command>' and parse the STX/ETX framed response.

        Returns the (pump address, status character, data) triple. Raises on a
        missing frame or on a pump error token in the data field.
        """
        self.port.write(f"{command}")
        response = self.port.read()

        if not response or response[0] != STX:
            msg = "Invalid response (missing STX). Check address, baud rate and cabling."
            raise Exception(msg)

        core = response[1:]  # drop STX; ETX was consumed as the read terminator

        question_pos = core.find("?")
        if question_pos != -1:
            token = core[question_pos:]
            for key in self._ERROR_TOKENS:
                if token.startswith(key):
                    msg = f"NE-500 pump error {key}: {PUMP_ERROR_LIST[key]}"
                    raise Exception(msg)

        pump_address = core[0:2]
        status = core[2:3]
        data = core[3:]
        return pump_address, status, data
