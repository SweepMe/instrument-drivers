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
# * Module: Signal
# * Instrument: BELEKTRONIG BSG0302

"""SweepMe! signal-generator driver for the BELEKTRONIG BSG0302 RF source."""

from __future__ import annotations

import math
from typing import Any, ClassVar

from pysweepme.EmptyDeviceClass import EmptyDevice

FREQUENCY_MIN_MHZ = 1.0
FREQUENCY_MAX_MHZ = 215.0
POWER_MIN_DBM = -30.0
POWER_MAX_DBM = 36.0
POWER_MIN_W = 1e-6
POWER_MAX_W = 3.9
PHASE_MIN_DEG = -180.0
PHASE_MAX_DEG = 180.0


class Device(EmptyDevice):
    """Driver for the BELEKTRONIG BSG0302 two-channel RF signal generator."""

    FREQUENCY_OUTPUT_MODE: ClassVar[dict[str, int]] = {
        "INPUT_POWER_METER": 0,
        "FREQUENCY_GENERATOR": 1,
        "AUTO_MIN_MAX_DETECT": 2,
        "COUPLED_TO_CH_1": 3,
    }
    POWER_OUTPUT_MODE: ClassVar[dict[str, int]] = {
        "SET_AT_DEVICE": 0,
        "SET_AT_PC": 1,
        "COUPLED_TO_CH_1": 2,
    }
    PHASE_MODE: ClassVar[dict[str, int]] = {
        "MANUAL": 0,
        "INVERS_COUPLED_TO_CH_1": 1,
    }
    MODULATION_MODE: ClassVar[dict[str, int]] = {"NONE": 0, "AM": 1, "FM": 2, "PM": 3}
    TRIGGER_MODE: ClassVar[dict[str, int]] = {"INTERNAL": 0, "BY_PC": 1, "EXTERNAL": 2}

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

        self.sweepmode: str = "Frequency in Hz"
        self.channel: int = 1
        self.frequency_hz: float = 100e6
        self.power_setpoint: float = 0.0
        self.phase_deg: float = 0.0
        self.modulation: str = "NONE"
        self.trigger: str = "BY_PC"

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI parameter options of the driver."""
        return {
            "SweepMode": ["None", "Frequency in Hz", "Power in dBm", "Power in W", "Phase in deg"],
            "Channel": ["1", "2"],
            "PeriodFrequency": "Frequency in Hz",
            "PeriodFrequencyValue": "100e6",

            "AmplitudeHiLevel": ["Power in dBm", "Power in W"],
            "AmplitudeHiLevelValue": 1.0,

            "DelayPhase": "Phase in deg",
            "DelayPhaseValue": 0.0,

            # "Modulation": list(self.MODULATION_MODE),
            # "Trigger": list(self.TRIGGER_MODE),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameter selections and define the return variables."""
        self.sweepmode = parameters.get("SweepMode", "Frequency in Hz")
        self.channel = parameters.get("Channel", "1")

        self.frequency_hz = float(parameters.get("PeriodFrequencyValue", "100e6"))
        self.power_unit = parameters.get("AmplitudeHiLevel", "Power in dBm")
        self.power_setpoint = float(parameters.get("AmplitudeHiLevelValue", "0.0"))
        self.phase_deg = float(parameters.get("DelayPhaseValue", "0.0"))

        self.modulation = parameters.get("Modulation", "NONE")
        self.trigger = parameters.get("Trigger", "BY_PC")

        self.variables = ["Frequency", "Output power", "Input power", "Temperature"]
        self.units = ["Hz", "dBm", "dBm", "°C"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

    # --- SweepMe! semantic phases ---------------------------------------------------------------

    def initialize(self) -> None:
        """Verify the device responds and that the selected channel exists."""
        if self.get_serial_number() <= 0:
            msg = "BSG0302: no valid serial number returned. Check port and baud rate."
            raise Exception(msg)
        if self.channel == 2 and not self.get_has_channel2():  # noqa: PLR2004
            msg = "BSG0302: channel 2 selected but this device only has channel 1."
            raise Exception(msg)

    def configure(self) -> None:
        """Set the output modes and the static setpoints not driven by the sweep."""
        self.set_frequency_output_mode(self.channel, "FREQUENCY_GENERATOR")
        self.set_power_output_mode(self.channel, "SET_AT_PC")
        self.set_phase_mode(self.channel, "MANUAL")
        self.set_modulation_mode(self.channel, self.modulation)
        self.set_trigger_mode(self.channel, self.trigger)

        if self.sweepmode != "Frequency in Hz":
            self.set_frequency(self.channel, self.frequency_hz / 1e6)
        if self.sweepmode not in ("Power in dBm", "Power in W"):
            if self.power_unit == "Power in dBm":
                self.set_output_power_dbm(self.channel, self.power_setpoint)
            elif self.power_unit == "Power in W":
                self.set_output_power_watt(self.channel, self.power_setpoint)
        if self.sweepmode != "Phase in deg":
            self.set_signal_phase(self.channel, self.phase_deg)

    def apply(self) -> None:
        """Apply the swept quantity from self.value."""
        if self.sweepmode == "Frequency in Hz":
            self.set_frequency(self.channel, float(self.value) / 1e6)
        elif self.sweepmode == "Power in dBm":
            self.set_output_power_dbm(self.channel, float(self.value))
        elif self.sweepmode == "Power in W":
            self.set_output_power_watt(self.channel, float(self.value))
        elif self.sweepmode == "Phase in deg":
            self.set_signal_phase(self.channel, float(self.value))

    def call(self) -> list[float]:
        """Return frequency, output power, input power and temperature of the channel."""
        return [
            self.get_frequency(self.channel) * 1e6,
            self.get_output_power(self.channel),
            self.get_input_power(self.channel),
            self.get_temperature(self.channel),
        ]

    # --- Wrapped device commands (ported from the contributed, tested pyBSG0302) -----------------

    def set_frequency_output_mode(self, channel: int, mode: str) -> None:
        """Set the frequency output mode (command b1)."""
        if mode not in self.FREQUENCY_OUTPUT_MODE:
            msg = f"Invalid frequency output mode '{mode}'. Available modes: {list(self.FREQUENCY_OUTPUT_MODE)}."
            raise Exception(msg)
        self._write(f"b1{channel}", self.FREQUENCY_OUTPUT_MODE[mode], 1, signed=False)

    def set_power_output_mode(self, channel: int, mode: str) -> None:
        """Set the power output mode (command b2)."""
        if mode not in self.POWER_OUTPUT_MODE:
            msg = f"Invalid power output mode '{mode}'. Available modes: {list(self.POWER_OUTPUT_MODE)}."
            raise Exception(msg)
        self._write(f"b2{channel}", self.POWER_OUTPUT_MODE[mode], 1, signed=False)

    def set_phase_mode(self, channel: int, mode: str) -> None:
        """Set the phase mode (command b3)."""
        if mode not in self.PHASE_MODE:
            msg = f"Invalid phase mode '{mode}'. Available modes: {list(self.PHASE_MODE)}."
            raise Exception(msg)
        self._write(f"b3{channel}", self.PHASE_MODE[mode], 1, signed=False)

    def set_modulation_mode(self, channel: int, mode: str) -> None:
        """Set the modulation mode (command b4)."""
        if mode not in self.MODULATION_MODE:
            msg = f"Invalid modulation mode '{mode}'. Available modes: {list(self.MODULATION_MODE)}."
            raise Exception(msg)
        self._write(f"b4{channel}", self.MODULATION_MODE[mode], 1, signed=False)

    def set_trigger_mode(self, channel: int, mode: str) -> None:
        """Set the trigger mode (command b5)."""
        if mode not in self.TRIGGER_MODE:
            msg = f"Invalid trigger mode '{mode}'. Available modes: {list(self.TRIGGER_MODE)}."
            raise Exception(msg)
        self._write(f"b5{channel}", self.TRIGGER_MODE[mode], 1, signed=False)

    def set_frequency(self, channel: int, frequency_mhz: float) -> None:
        """Set the output frequency in MHz (command f1, 1-215 MHz)."""
        if not FREQUENCY_MIN_MHZ <= frequency_mhz <= FREQUENCY_MAX_MHZ:
            msg = f"Frequency {frequency_mhz} MHz out of range ({FREQUENCY_MIN_MHZ}-{FREQUENCY_MAX_MHZ} MHz)."
            raise Exception(msg)
        self._write(f"f1{channel}", int(frequency_mhz * 1e6), 4, signed=True)

    def set_signal_phase(self, channel: int, phase: float) -> None:
        """Set the signal phase in degrees (command h1, -180 to 180)."""
        if not PHASE_MIN_DEG <= phase <= PHASE_MAX_DEG:
            msg = f"Phase {phase} deg out of range (-{PHASE_MIN_DEG} to {PHASE_MAX_DEG})."
            raise Exception(msg)
        self._write(f"h1{channel}", int(phase * 1 / 2**14), 2, signed=True)

    def set_output_power_dbm(self, channel: int, power_dbm: float) -> None:
        """Set the output power in dBm (command p3, -30 to 36 dBm)."""
        if not POWER_MIN_DBM <= power_dbm <= POWER_MAX_DBM:
            msg = f"Power {power_dbm} dBm out of range ({POWER_MIN_DBM} to {POWER_MAX_DBM} dBm)."
            raise Exception(msg)
        self._write(f"p3{channel}", int(power_dbm * 100), 2, signed=True)

    def set_output_power_watt(self, channel: int, power_w: float) -> None:
        """Set the output power in watt (command p3, 1e-6 to 3.9 W)."""
        if not POWER_MIN_W <= power_w <= POWER_MAX_W:
            msg = f"Power {power_w} W out of range ({POWER_MIN_W} to {POWER_MAX_W} W)."
            raise Exception(msg)
        power_dbm = 10 * math.log10(power_w) + 30
        self._write(f"p3{channel}", int(power_dbm * 100), 2, signed=True)

    def get_frequency(self, channel: int) -> float:
        """Return the output frequency of the channel in MHz (command F1)."""
        return self._query(f"F1{channel}", 4, signed=True) / 1e6

    def get_output_power(self, channel: int) -> float:
        """Return the output power of the channel in dBm (command P1)."""
        return self._query(f"P1{channel}", 2, signed=True) / 100

    def get_input_power(self, channel: int) -> float:
        """Return the input power of the channel in dBm (command P2)."""
        return self._query(f"P2{channel}", 2, signed=True) / 100

    def get_temperature(self, channel: int) -> float:
        """Return the channel temperature in degrees Celsius (command T9)."""
        return self._query(f"T9{channel}", 2, signed=True) / 10

    def get_serial_number(self) -> int:
        """Return the device serial number (command N20)."""
        return self._query("N20", 4, signed=True)

    def get_has_channel2(self) -> bool:
        """Return whether the device has a second channel (device config bit 1)."""
        config = self._query("N50", 4, signed=False)
        return bool(config & (1 << 1))

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
