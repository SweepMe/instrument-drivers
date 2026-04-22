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
# * Instrument: Undalogic uSMU

from __future__ import annotations

import time

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Undalogic uSMU single-channel source measure unit.

    The uSMU is a compact USB-connected SMU for force-voltage / measure-current
    operation. It supports software-driven I-V sweeps via the standard SweepMe!
    SweepEditor, adjustable oversampling, current-limiting, and manual current
    range locking.
    """

    # Command processing delay (seconds) inserted after every write. The uSMU
    # firmware needs a short settling window between consecutive serial commands;
    # the reference Python library (usmu_py) uses the same 50 ms default.
    DEFAULT_COMMAND_DELAY_S = 0.05

    def __init__(self) -> None:
        super().__init__()

        self.shortname = "uSMU"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 1,
            "baudrate": 9600,
            "EOL": "\n",
        }

        # State
        self.source: str = "Voltage in V"
        self.compliance: float = 0.02  # 20 mA default compliance (in amperes)
        self.oversampling: int = 25
        self.port_string: str = ""

        # Staged sweep value written in apply(), consumed in measure()
        self._pending_voltage: float = 0.0

        # Measurement buffer
        self._measured_voltage: float = 0.0
        self._measured_current: float = 0.0

        self.command_delay_s: float = self.DEFAULT_COMMAND_DELAY_S

    # --- GUI interaction -------------------------------------------------------

    def set_GUIparameter(self) -> dict:
        """Define available GUI parameters for the SMU module.

        The uSMU only supports voltage sourcing, so "SweepMode" is restricted
        to a single entry. Current compliance is expressed in amperes (the
        SweepMe! convention) and converted to milliamps when sent to the
        device.
        """
        return {
            "SweepMode": ["Voltage in V"],
            "Compliance": self.compliance,
            "Average": self.oversampling,
        }

    def get_GUIparameter(self, parameter: dict = {}) -> None:
        """Read and store user-selected GUI parameters."""
        self.source = str(parameter.get("SweepMode", "Voltage in V"))
        self.compliance = float(parameter.get("Compliance", 0.02))
        self.oversampling = int(float(parameter.get("Average", 25)))

        self.port_string = str(parameter.get("Port", ""))

    # --- Communication layer ---------------------------------------------------

    def _sanitize(self, text: str) -> str:
        """Strip null bytes and surrounding whitespace from a response.

        The uSMU firmware occasionally emits stray null bytes at the start of
        a response line; the reference library strips them before parsing.
        """
        if text is None:
            return ""
        return text.replace("\x00", "").strip()

    def _write(self, command: str) -> None:
        """Send a command without reading a response.

        Sleeps for ``command_delay_s`` after writing to give the device time
        to process before the next command arrives.
        """
        self.port.write(command)
        if self.command_delay_s > 0:
            time.sleep(self.command_delay_s)

    def _query(self, command: str) -> str:
        """Send a command and read back a single response line."""
        self._write(command)
        return self._sanitize(self.port.read())

    def _parse_measurement(self, response: str) -> tuple[float, float]:
        """Parse a ``voltage,current`` response into a numeric tuple.

        Shared by :meth:`measure` and :meth:`set_voltage_and_measure` so the
        response format only has to be maintained in one place.
        """
        parts = response.split(",")
        if len(parts) != 2:
            msg = (
                f"Unexpected measurement response format: {response!r}. "
                f"Expected 'voltage,current'."
            )
            raise Exception(msg)

        try:
            return float(parts[0]), float(parts[1])
        except ValueError as exc:
            msg = f"Could not parse measurement response {response!r}: {exc}"
            raise Exception(msg) from exc

    def _validate_oversampling(self, value: int) -> None:
        """Raise if ``value`` is outside the firmware-accepted OSR range."""
        if not 1 <= value <= 255:
            msg = "Oversampling (Average) must be between 1 and 255."
            raise Exception(msg)

    # --- Connection management -------------------------------------------------

    def connect(self) -> None:
        """Open the connection and verify the device identity.

        The uSMU firmware may report itself as either "uSMU" or "nanoSMU"
        depending on build variant, so both are accepted.
        """
        identity = self.get_identification()
        identity_upper = identity.upper()
        if "USMU" not in identity_upper and "NANOSMU" not in identity_upper:
            msg = f"Unexpected device identity: {identity!r}"
            raise Exception(msg)

    # --- Standard semantic functions -------------------------------------------

    def initialize(self) -> None:
        """Configure the uSMU for the selected operating mode."""
        self.set_oversample_rate(self.oversampling)
        self.set_current_limit(self.compliance)

    def deinitialize(self) -> None:
        """Return the uSMU to a safe state.

        SweepMe! calls ``poweroff()`` before ``deinitialize()``, so the output
        is already disabled here. No additional teardown is needed.
        """

    def poweron(self) -> None:
        """Enable the output."""
        self.enable_output()

    def poweroff(self) -> None:
        """Disable the output (high impedance)."""
        self.disable_output()

    def apply(self) -> None:
        """Stage the requested sweep value.

        The uSMU's atomic ``CH1:MEA:VOL`` command both sets the voltage and
        returns the measurement, so the actual transfer happens in
        ``measure()``. We simply cache the value here.
        """
        self._pending_voltage = float(self.value)

    def measure(self) -> None:
        """Apply the staged voltage and record the measured V and I."""
        voltage, current = self.set_voltage_and_measure(self._pending_voltage)
        self._measured_voltage = voltage
        self._measured_current = current

    def call(self) -> list:
        """Return the most recent (voltage, current) measurement."""
        return [self._measured_voltage, self._measured_current]

    # --- Convenience wrapper functions -----------------------------------------

    def get_identification(self) -> str:
        """Query the device identification string.

        Returns:
            Device identification string from the ``*IDN?`` query.
        """
        return self._query("*IDN?")

    def enable_output(self) -> None:
        """Enable the uSMU output (CH1:ENA)."""
        self._write("CH1:ENA")

    def disable_output(self) -> None:
        """Disable the uSMU output (CH1:DIS)."""
        self._write("CH1:DIS")

    def set_voltage(self, voltage: float) -> None:
        """Set the output voltage without triggering a measurement.

        Args:
            voltage: Voltage value in volts.
        """
        self._write(f"CH1:VOL {voltage}")

    def set_voltage_and_measure(self, voltage: float) -> tuple[float, float]:
        """Set the voltage and atomically read back measured V and I.

        Args:
            voltage: Voltage value in volts.

        Returns:
            Tuple of (measured voltage in V, measured current in A).
        """
        response = self._query(f"CH1:MEA:VOL {voltage}")
        return self._parse_measurement(response)

    def set_current_limit(self, current_A: float) -> None:
        """Set the source/sink current limit in amperes.

        The uSMU firmware's ``CH1:CUR`` command expects milliamps, but the
        SweepMe! convention across SMU drivers is to express currents in
        amperes, so the conversion is done here.

        Args:
            current_A: Current limit in amperes (e.g. 0.02 for 20 mA).
        """
        self._write(f"CH1:CUR {current_A * 1000.0}")

    def set_oversample_rate(self, oversample: int) -> None:
        """Set the measurement oversampling rate.

        Args:
            oversample: Number of samples averaged per measurement (1-255).
        """
        self._validate_oversampling(oversample)
        self._write(f"CH1:OSR {oversample}")

    def set_dac(self, value: int) -> None:
        """Write directly to the 16-bit voltage DAC.

        Intended for calibration and diagnostics; normal use should prefer
        :meth:`set_voltage`.
        """
        self._write(f"DAC {value}")

    def set_current_limit_dac(self, value: int) -> None:
        """Write directly to the 12-bit current-limit DAC.

        Intended for calibration and diagnostics; normal use should prefer
        :meth:`set_current_limit`.
        """
        self._write(f"ILIM {value}")

    def read_adc(self, adc_channel: int) -> int:
        """Perform a differential ADC conversion.

        Reads a differential conversion between adjacent ADC channels
        (e.g. ``0`` = channels 0+1, ``2`` = channels 2+3).

        Args:
            adc_channel: ADC channel index.

        Returns:
            Signed 16-bit ADC value.
        """
        response = self._query(f"ADC {adc_channel}")
        try:
            return int(response)
        except ValueError as exc:
            msg = f"Unexpected ADC response: {response!r}"
            raise Exception(msg) from exc

    def enable_voltage_calibration_mode(self) -> None:
        """Enable voltage calibration mode on the device."""
        self._write("CH1:VCAL")
