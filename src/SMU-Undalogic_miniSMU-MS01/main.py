# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 Undalogic Ltd
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
# * Module: SMU
# * Instrument: Undalogic miniSMU MS01

from __future__ import annotations

import json
import re
import time

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice

# Current range indices mapped to their maximum current magnitude in amperes
CURRENT_RANGE_LIMITS = {
    0: 1e-6,    # Range 0: +/- 1 uA
    1: 25e-6,   # Range 1: +/- 25 uA
    2: 650e-6,  # Range 2: +/- 650 uA
    3: 15e-3,   # Range 3: +/- 15 mA
    4: 180e-3,  # Range 4: +/- 180 mA
}


class Device(EmptyDevice):
    """Driver for the Undalogic miniSMU MS01 dual-channel source measure unit.

    Supports voltage and current sourcing with measurement, hardware-accelerated
    I-V sweeps, 4-wire Kelvin sensing, and both USB and WiFi connectivity.
    """

    description = """
        <h3>Undalogic miniSMU MS01</h3>
        <p>2-channel Source Measure Unit with FVMI/FIMV modes.</p>
        <p><b>Connection:</b> USB (COM port) or WiFi (SOCKET port)</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Force Voltage / Measure Current (FVMI)</li>
            <li>Force Current / Measure Voltage (FIMV)</li>
            <li>Hardware-accelerated I-V sweep (up to 1000 points)</li>
            <li>4-wire Kelvin sensing mode</li>
            <li>5 current measurement ranges (1 uA to 180 mA)</li>
            <li>Configurable oversampling (0-15)</li>
        </ul>
        <p>For WiFi connections, select the SOCKET port corresponding to the
        device IP address and port (default TCP port: 3333).</p>
    """

    def __init__(self) -> None:
        super().__init__()

        self.shortname = "miniSMU"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.port_manager = True
        self.port_types = ["COM", "SOCKET"]
        self.port_properties = {
            "timeout": 1,
            "baudrate": 115200,
            "EOL": "\n",
            # The miniSMU firmware TCP command parser uses strcmp() and does NOT
            # strip newlines, so commands must be sent without a trailing EOL.
            # Responses do include \n terminators over both USB and TCP.
            "SOCKET_EOLwrite": "",
            "SOCKET_EOLread": "\n",
            "SOCKET_timeout": 5,
        }

        # Source mode command mapping
        self.source_modes: dict[str, str] = {
            "Voltage in V": "FVMI",
            "Current in A": "FIMV",
        }

        # Source set commands per mode
        self.source_commands: dict[str, str] = {
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
        }

        # Voltage range mapping
        self.voltage_ranges: dict[str, str] = {
            "Auto": "AUTO",
            "Low": "LOW",
            "High": "HIGH",
        }

        # Current range mapping (display name -> range index)
        self.current_ranges: dict[str, int] = {
            "Auto": -1,
            "1 uA": 0,
            "25 uA": 1,
            "650 uA": 2,
            "15 mA": 3,
            "180 mA": 4,
        }

        # State
        self.source: str = "Voltage in V"
        self.channel: int = 1
        self.compliance: float = 0.01
        self.voltage_range: str = "Auto"
        self.current_range: str = "Auto"
        self.oversampling: int = 0
        self.four_wire: bool = False
        self.four_wire_was_enabled: bool = False
        self.output_on: bool = False

        # List sweep state
        self.use_list_sweep: bool = False
        self.listsweep_start: float = 0.0
        self.listsweep_end: float = 1.0
        self.listsweep_points: int = 100
        self.listsweep_dwell_ms: int = 50

        # Measurement result buffer
        self._measured_voltage: float = 0.0
        self._measured_current: float = 0.0
        self._sweep_voltages: np.ndarray = np.array([])
        self._sweep_currents: np.ndarray = np.array([])
        self._sweep_timestamps: np.ndarray = np.array([])

    # --- GUI interaction -------------------------------------------------------

    def set_GUIparameter(self) -> dict:
        """Define available GUI parameters for the SMU module.

        Uses the SMU module's built-in GUI fields where possible:
        - "Range" for current measurement ranges
        - "RangeVoltage" for voltage source ranges
        - "Compliance", "4wire", "Channel" are standard SMU keys
        - "Oversampling" is miniSMU-specific (custom parameter)
        """
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["1", "2"],
            "Compliance": self.compliance,
            "RangeVoltage": list(self.voltage_ranges.keys()),
            "Range": list(self.current_ranges.keys()),
            "4wire": False,
            "Oversampling": [str(i) for i in range(16)],

            # List sweep parameters for hardware I-V sweep
            "ListSweepCheck": True,
            "ListSweepType": ["Sweep"],
            "ListSweepStart": 0.0,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": ["Points (lin.):"],
            "ListSweepStepPointsValue": 100,
            "ListSweepDual": False,
            "ListSweepHoldtime": 0.05,
        }

    def get_GUIparameter(self, parameter: dict = {}) -> None:
        """Read and store user-selected GUI parameters."""
        self.source = str(parameter.get("SweepMode", "Voltage in V"))
        self.channel = int(parameter.get("Channel", "1"))
        self.compliance = float(parameter.get("Compliance", 0.01))
        self.voltage_range = str(parameter.get("RangeVoltage", "Auto"))
        self.current_range = str(parameter.get("Range", "Auto"))
        self.oversampling = int(parameter.get("Oversampling", "0"))
        self.four_wire = bool(parameter.get("4wire", False))

        self.port_string = str(parameter.get("Port", ""))

        # Determine if using list sweep
        self.sweepvalue = parameter.get("SweepValue", "SweepEditor")
        self.use_list_sweep = self.sweepvalue == "List sweep"

        if self.use_list_sweep:
            self.listsweep_start = float(parameter.get("ListSweepStart", 0.0))
            self.listsweep_end = float(parameter.get("ListSweepEnd", 1.0))
            self.listsweep_points = int(float(parameter.get("ListSweepStepPointsValue", 100)))
            holdtime = float(parameter.get("ListSweepHoldtime", 0.05))
            self.listsweep_dwell_ms = int(holdtime * 1000)

            self.variables = ["Voltage", "Current", "Timestamp"]
            self.units = ["V", "A", "s"]
            self.plottype = [True, True, True]
            self.savetype = [True, True, True]
        else:
            self.variables = ["Voltage", "Current"]
            self.units = ["V", "A"]
            self.plottype = [True, True]
            self.savetype = [True, True]

    # --- Communication layer ---------------------------------------------------

    def _send_command(self, command: str) -> str:
        """Send a command to the device and return the response.

        Uses the SweepMe! port manager for both USB (COM) and WiFi (SOCKET)
        connections. The port manager handles EOL differences between the two
        transports via the port_properties configured in __init__.

        The miniSMU may return chunked JSON responses that span multiple reads,
        so non-trivial responses are accumulated by _read_response.

        Args:
            command: Command string to send (e.g. "SOUR1:VOLT 3.3" or "MEAS1:VOLT?").

        Returns:
            Response string from the device.
        """
        self.port.write(command)
        return self._read_response(command)

    def _read_response(self, command: str) -> str:
        """Read the device response, handling chunked JSON data.

        The miniSMU may split large JSON responses (e.g. sweep data, WiFi status)
        across multiple packets. This method accumulates chunks until a complete
        JSON object is received or a timeout is reached.

        Args:
            command: Original command sent (used to detect expected response type).

        Returns:
            Complete response string from the device.
        """
        initial_response = self.port.read()

        # Simple non-JSON responses can be returned immediately
        if not initial_response.startswith("{") and not initial_response.startswith("["):
            return initial_response

        # JSON response - may need to accumulate chunks
        response_buffer = [initial_response]
        current_response = initial_response

        if self._is_likely_complete_json(current_response):
            try:
                json.loads(current_response)
                return current_response
            except json.JSONDecodeError:
                pass

        # Read additional chunks until complete or timeout
        max_timeout_iterations = 10
        timeout_count = 0

        while timeout_count < max_timeout_iterations:
            try:
                chunk = self.port.read()
                if chunk:
                    if chunk.strip() and self._is_valid_chunk(chunk):
                        response_buffer.append(chunk)
                    timeout_count = 0

                    current_response = "".join(response_buffer)

                    # Only attempt expensive json.loads when braces/brackets
                    # are balanced, avoiding redundant parsing on every chunk.
                    if not self._is_likely_complete_json(current_response):
                        continue

                    try:
                        json.loads(current_response)
                        return current_response
                    except json.JSONDecodeError:
                        cleaned = self._clean_json_response(current_response)
                        try:
                            json.loads(cleaned)
                            return cleaned
                        except json.JSONDecodeError:
                            continue
                else:
                    timeout_count += 1
            except Exception:
                timeout_count += 1

        # Final attempt
        final_response = "".join(response_buffer)
        if final_response.startswith("{") or final_response.startswith("["):
            try:
                json.loads(final_response)
                return final_response
            except json.JSONDecodeError:
                cleaned = self._clean_json_response(final_response)
                try:
                    json.loads(cleaned)
                    return cleaned
                except json.JSONDecodeError:
                    pass

        return final_response

    def _is_likely_complete_json(self, text: str) -> bool:
        """Check if a JSON string appears complete by counting braces/brackets.

        Args:
            text: Text to check.

        Returns:
            True if JSON appears structurally complete.
        """
        if not text:
            return False

        text = text.strip()
        if text.startswith("{"):
            return text.count("{") == text.count("}") and text.count("}") > 0
        elif text.startswith("["):
            return text.count("[") == text.count("]") and text.count("]") > 0

        return True

    def _is_valid_chunk(self, chunk: str) -> bool:
        """Validate that a data chunk contains reasonable text.

        Rejects chunks with excessive control characters or Unicode replacement
        characters that indicate corrupted data.

        Args:
            chunk: Text chunk to validate.

        Returns:
            True if the chunk appears valid.
        """
        if not chunk:
            return False

        control_count = sum(1 for c in chunk if ord(c) < 32 and c not in "\t\n\r")
        replacement_count = chunk.count("\ufffd")
        total = len(chunk)

        if total > 0 and (control_count + replacement_count) / total > 0.2:
            return False

        return True

    def _clean_json_response(self, json_str: str) -> str:
        """Clean corrupted JSON response fields.

        Handles known corruption patterns in WiFi status responses where IP
        addresses and other fields may contain invalid characters.

        Args:
            json_str: Raw JSON string that may contain corrupted data.

        Returns:
            Cleaned JSON string.
        """
        json_str = re.sub(
            r'"ip":\s*"[^"]*[\u0000-\u001f\u007f-\u009f][^"]*"',
            '"ip": "0.0.0.0"',
            json_str,
        )
        json_str = re.sub(
            r'"gateway":\s*"[^"]*[\u0000-\u001f\u007f-\u009f][^"]*"',
            '"gateway": "0.0.0.0"',
            json_str,
        )
        for field in ["subnet", "ssid"]:
            pattern = f'"{field}":\\s*"[^"]*[\\u0000-\\u001f\\u007f-\\u009f][^"]*"'
            json_str = re.sub(pattern, f'"{field}": ""', json_str)

        return json_str

    # --- Connection management -------------------------------------------------

    def find_ports(self) -> list[str]:
        """Provide a SOCKET port template with the default miniSMU TCP port.

        The miniSMU firmware listens on TCP port 3333. This template lets the
        user replace only the IP address without needing to remember the port.
        """
        return ["TCPIP0::<ip>::3333::SOCKET"]

    def connect(self) -> None:
        """Open a connection to the miniSMU and verify the device identity.

        The SweepMe! port manager handles both USB (COM) and WiFi (SOCKET)
        connections automatically based on the user's port selection.
        """
        identity = self.get_identification()
        if "miniSMU" not in identity and "MS01" not in identity:
            msg = f"Unexpected device identity: {identity}"
            raise Exception(msg)

    # --- Standard semantic functions -------------------------------------------

    def initialize(self) -> None:
        """Configure the miniSMU for the selected operating mode.

        Sets the source mode (FVMI/FIMV), voltage range, current range,
        oversampling, compliance limits, and optionally enables 4-wire mode.
        """
        # Validate 4-wire mode constraints
        if self.four_wire and self.channel != 1:
            msg = "4-wire mode is only available on Channel 1 (CH1 forces, CH2 senses)."
            raise Exception(msg)

        # Validate list sweep parameters
        if self.use_list_sweep:
            if self.source == "Current in A":
                msg = (
                    "The onboard hardware I-V sweep only supports voltage sourcing. "
                    "Please use 'Voltage in V' mode with List Sweep, or switch to "
                    "the standard SweepEditor for current sweeps."
                )
                raise Exception(msg)
            if self.listsweep_points < 1 or self.listsweep_points > 1000:
                msg = "Number of sweep points must be between 1 and 1000."
                raise Exception(msg)
            if self.listsweep_dwell_ms < 0 or self.listsweep_dwell_ms > 10000:
                msg = "Sweep dwell time must be between 0 and 10000 ms."
                raise Exception(msg)

        # Set source mode
        mode_cmd = self.source_modes[self.source]
        self._send_command(f"SOUR{self.channel}:{mode_cmd} ENA")

        # Configure voltage range
        range_cmd = self.voltage_ranges[self.voltage_range]
        self._send_command(f"SOUR{self.channel}:VOLT:RANGE {range_cmd}")

        # Configure current range
        range_idx = self.current_ranges[self.current_range]
        if range_idx == -1:
            self._send_command(f"CH{self.channel}:AUTORANGE:ENA")
        else:
            self._send_command(f"CH{self.channel}:AUTORANGE:DIS")
            self._send_command(f"CH{self.channel}:IRANGE {range_idx}")

        # Set oversampling ratio
        self._send_command(f"MEAS{self.channel}:OSR {self.oversampling}")

        # Set compliance / protection limits
        if self.source == "Voltage in V":
            self._send_command(f"SOUR{self.channel}:CURR:PROT {self.compliance}")
        else:
            self._send_command(f"SOUR{self.channel}:VOLT:PROT {self.compliance}")

        # Enable 4-wire Kelvin mode if requested
        if self.four_wire:
            response = self._send_command("SYST:4WIR ENA")
            if isinstance(response, str) and response.startswith("ERROR"):
                msg = f"Failed to enable 4-wire mode: {response}"
                raise Exception(msg)
            self.four_wire_was_enabled = True

    def deinitialize(self) -> None:
        """Restore the miniSMU to a safe default state."""
        # Disable 4-wire mode if we enabled it
        if self.four_wire_was_enabled:
            self._send_command("SYST:4WIR DIS")

        # Re-enable autoranging
        self._send_command(f"CH{self.channel}:AUTORANGE:ENA")

    def configure(self) -> None:
        """Configure sweep parameters for the current measurement.

        For list sweep mode, uploads the hardware sweep configuration to the device.
        """
        if self.use_list_sweep:
            ch = self.channel
            self._send_command(f"SOUR{ch}:SWEEP:VOLT:START {self.listsweep_start}")
            self._send_command(f"SOUR{ch}:SWEEP:VOLT:END {self.listsweep_end}")
            self._send_command(f"SOUR{ch}:SWEEP:POINTS {self.listsweep_points}")
            self._send_command(f"SOUR{ch}:SWEEP:DWELL {self.listsweep_dwell_ms}")
            self._send_command(f"SOUR{ch}:SWEEP:AUTO:ENA")
            # Use JSON format so the chunked JSON reader can accumulate the full
            # multi-packet response.  CSV is line-delimited and the USB reader
            # returns after the first line, which causes only 1 point to be stored.
            self._send_command(f"SOUR{ch}:SWEEP:FORMAT JSON")

    def poweron(self) -> None:
        """Enable the output of the selected channel."""
        self._send_command(f"OUTP{self.channel} ON")
        self.output_on = True

    def poweroff(self) -> None:
        """Disable the output of the selected channel."""
        self._send_command(f"OUTP{self.channel} OFF")
        self.output_on = False

    def apply(self) -> None:
        """Apply the current sweep value to the source.

        Sets the voltage or current depending on the selected sweep mode.
        Not called during list sweep mode.
        """
        if not self.use_list_sweep:
            cmd = self.source_commands[self.source]
            self._send_command(f"SOUR{self.channel}:{cmd} {self.value}")

    def measure(self) -> None:
        """Trigger a measurement or execute a hardware sweep.

        In normal mode, sends an atomic voltage+current query.
        In list sweep mode, executes the onboard sweep and polls until complete.
        """
        if self.use_list_sweep:
            # Execute hardware sweep
            self._send_command(f"SOUR{self.channel}:SWEEP:EXECUTE")

            # Poll for completion with timeout
            # Timeout = generous estimate based on sweep parameters plus overhead
            expected_duration_s = (self.listsweep_points * self.listsweep_dwell_ms) / 1000.0
            timeout_s = expected_duration_s + 30.0
            start_time = time.time()

            while True:
                elapsed = time.time() - start_time
                if elapsed > timeout_s:
                    msg = (
                        f"Hardware I-V sweep timed out after {elapsed:.1f} s "
                        f"(expected ~{expected_duration_s:.1f} s). "
                        f"Device may be unresponsive."
                    )
                    raise Exception(msg)

                status_str = self._send_command(f"SOUR{self.channel}:SWEEP:STATUS?")
                parts = status_str.split(",")
                status = parts[0] if parts else "IDLE"

                if status == "COMPLETED":
                    break
                elif status == "ABORTED":
                    msg = "Hardware I-V sweep was aborted."
                    raise Exception(msg)
                elif status == "RUNNING":
                    time.sleep(0.1)
                else:
                    break
        else:
            # Normal point-by-point measurement
            response = self._send_command(f"MEAS{self.channel}:VOLT:CURR?")
            parts = response.split(",")
            if len(parts) != 2:
                msg = (
                    f"Unexpected measurement response format: '{response}'. "
                    f"Expected 'voltage,current'."
                )
                raise Exception(msg)
            self._measured_voltage = float(parts[0])
            self._measured_current = float(parts[1])

    def call(self) -> list:
        """Return measured data.

        In normal mode, returns [voltage, current].
        In list sweep mode, retrieves JSON sweep data from the device and returns
        [voltage_array, current_array, timestamp_array].

        Returns:
            List of measurement values matching the defined variables.
        """
        if self.use_list_sweep:
            raw_data = self._send_command(f"SOUR{self.channel}:SWEEP:DATA?")

            # Parse the JSON response.  The chunked JSON reader in
            # _read_response guarantees we receive the complete object.
            try:
                sweep_json = json.loads(raw_data)
            except (json.JSONDecodeError, TypeError) as e:
                msg = f"Failed to parse sweep data response: {e}"
                raise Exception(msg) from e

            data_points = sweep_json.get("data", [])
            if not data_points:
                msg = "Sweep data response contains no data points."
                raise Exception(msg)

            timestamps = np.array([float(p["t"]) / 1000.0 for p in data_points])  # ms to s
            voltages = np.array([float(p["v"]) for p in data_points])
            currents = np.array([float(p["i"]) for p in data_points])

            self._sweep_voltages = voltages
            self._sweep_currents = currents
            self._sweep_timestamps = timestamps

            return [self._sweep_voltages, self._sweep_currents, self._sweep_timestamps]
        else:
            return [self._measured_voltage, self._measured_current]

    # --- Convenience wrapper functions -----------------------------------------

    def set_source_mode(self, channel: int, mode: str) -> None:
        """Set the source mode on a channel.

        Args:
            channel: Channel number (1 or 2).
            mode: Source mode ("FVMI" or "FIMV").
        """
        self._send_command(f"SOUR{channel}:{mode} ENA")

    def set_sweep_parameters(
        self, channel: int, start: float, end: float, points: int, dwell_ms: int,
    ) -> None:
        """Configure hardware sweep parameters on a channel.

        Args:
            channel: Channel number (1 or 2).
            start: Start voltage in volts.
            end: End voltage in volts.
            points: Number of sweep points (1-1000).
            dwell_ms: Dwell time per point in milliseconds.
        """
        self._send_command(f"SOUR{channel}:SWEEP:VOLT:START {start}")
        self._send_command(f"SOUR{channel}:SWEEP:VOLT:END {end}")
        self._send_command(f"SOUR{channel}:SWEEP:POINTS {points}")
        self._send_command(f"SOUR{channel}:SWEEP:DWELL {dwell_ms}")
        self._send_command(f"SOUR{channel}:SWEEP:AUTO:ENA")
        self._send_command(f"SOUR{channel}:SWEEP:FORMAT JSON")

    def execute_sweep(self, channel: int) -> None:
        """Start a hardware sweep on a channel.

        Args:
            channel: Channel number (1 or 2).
        """
        self._send_command(f"SOUR{channel}:SWEEP:EXECUTE")

    def get_sweep_status(self, channel: int) -> str:
        """Query the sweep status on a channel.

        Args:
            channel: Channel number (1 or 2).

        Returns:
            Status string (e.g. "RUNNING,50,100,..." or "COMPLETED").
        """
        return self._send_command(f"SOUR{channel}:SWEEP:STATUS?")

    def get_sweep_data(self, channel: int) -> str:
        """Retrieve the sweep data from a completed hardware sweep.

        Args:
            channel: Channel number (1 or 2).

        Returns:
            Raw JSON string containing sweep data points.
        """
        return self._send_command(f"SOUR{channel}:SWEEP:DATA?")

    def enable_output(self, channel: int) -> None:
        """Enable the output on a channel.

        Args:
            channel: Channel number (1 or 2).
        """
        self._send_command(f"OUTP{channel} ON")

    def disable_output(self, channel: int) -> None:
        """Disable the output on a channel.

        Args:
            channel: Channel number (1 or 2).
        """
        self._send_command(f"OUTP{channel} OFF")

    def get_identification(self) -> str:
        """Query the device identification string.

        Returns:
            Device identification string from *IDN? query.
        """
        return self._send_command("*IDN?")

    def reset(self) -> None:
        """Reset the device to factory defaults."""
        self._send_command("*RST")

    def set_voltage(self, channel: int, voltage: float) -> None:
        """Set the output voltage on a channel.

        Args:
            channel: Channel number (1 or 2).
            voltage: Voltage value in volts.
        """
        self._send_command(f"SOUR{channel}:VOLT {voltage}")

    def set_current(self, channel: int, current: float) -> None:
        """Set the output current on a channel.

        Args:
            channel: Channel number (1 or 2).
            current: Current value in amperes.
        """
        self._send_command(f"SOUR{channel}:CURR {current}")

    def get_voltage_and_current(self, channel: int) -> tuple[float, float]:
        """Query both voltage and current on a channel atomically.

        Args:
            channel: Channel number (1 or 2).

        Returns:
            Tuple of (voltage in V, current in A).
        """
        response = self._send_command(f"MEAS{channel}:VOLT:CURR?")
        parts = response.split(",")
        if len(parts) != 2:
            msg = (
                f"Unexpected measurement response format: '{response}'. "
                f"Expected 'voltage,current'."
            )
            raise Exception(msg)
        return float(parts[0]), float(parts[1])

    def set_compliance(self, channel: int, value: float, source_mode: str) -> None:
        """Set the protection/compliance limit for a channel.

        Args:
            channel: Channel number (1 or 2).
            value: Compliance limit value.
            source_mode: Source mode string ("Voltage in V" or "Current in A").
        """
        if source_mode == "Voltage in V":
            self._send_command(f"SOUR{channel}:CURR:PROT {value}")
        else:
            self._send_command(f"SOUR{channel}:VOLT:PROT {value}")

    def set_oversampling(self, channel: int, osr: int) -> None:
        """Set the measurement oversampling ratio.

        Args:
            channel: Channel number (1 or 2).
            osr: Oversampling ratio (0-15, represents 2^osr samples averaged).
        """
        if not 0 <= osr <= 15:
            msg = "Oversampling ratio must be between 0 and 15."
            raise Exception(msg)
        self._send_command(f"MEAS{channel}:OSR {osr}")

    def set_voltage_range_cmd(self, channel: int, range_type: str) -> None:
        """Set the voltage range on a channel.

        Args:
            channel: Channel number (1 or 2).
            range_type: Range type string ("AUTO", "LOW", or "HIGH").
        """
        self._send_command(f"SOUR{channel}:VOLT:RANGE {range_type}")

    def set_current_range_cmd(self, channel: int, range_index: int) -> None:
        """Manually set the current measurement range.

        Autoranging must be disabled first for this to take effect.

        Args:
            channel: Channel number (1 or 2).
            range_index: Range index (0-4).
        """
        if not 0 <= range_index <= 4:
            msg = "Current range index must be between 0 and 4."
            raise Exception(msg)
        self._send_command(f"CH{channel}:IRANGE {range_index}")

    def get_temperatures(self) -> tuple[float, float, float]:
        """Query the device temperature sensors.

        Returns:
            Tuple of (ADC temperature, CH1 temperature, CH2 temperature) in degrees C.
        """
        response = self._send_command("SYST:TEMP?")
        return tuple(float(x) for x in response.split(","))
