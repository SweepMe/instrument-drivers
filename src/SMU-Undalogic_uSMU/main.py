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

"""Driver for the Undalogic uSMU, a single-channel USB source measure unit."""

from __future__ import annotations

import time
from typing import Annotated, Any

from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]


class Device(EmptyDevice):
    """Driver for the Undalogic uSMU single-channel source measure unit.

    The uSMU is a compact USB-connected SMU for force-voltage / measure-current
    operation. It supports software-driven I-V sweeps via the standard SweepMe!
    SweepEditor, adjustable oversampling and a current limit.

    The device is single channel: every command addresses CH1, so the channel is
    not an argument. Its firmware has no query commands for the values that are
    set, so the driver declares setters without read-backs; the only reader of
    the source is set_voltage_and_measure, which measures what the output does.
    """

    # Command processing delay (seconds) inserted after every write. The uSMU
    # firmware needs a short settling window between consecutive serial commands;
    # the reference Python library (usmu_py) uses the same 50 ms default.
    DEFAULT_COMMAND_DELAY_S = 0.05

    def __init__(self) -> None:
        """Set the return values, the port and the driver's own state."""
        super().__init__()

        self.shortname: str = "uSMU"

        self.variables: list[str] = ["Voltage", "Current"]
        self.units: list[str] = ["V", "A"]
        self.plottype: list[bool] = [True, True]
        self.savetype: list[bool] = [True, True]

        self.port_manager: bool = True
        self.port_types: list[str] = ["COM"]
        # The read timeout has to cover the slowest measurement the driver allows.
        # A measurement takes about 17.6 ms per averaged sample (measured 2026-11-28:
        # 0.41 s at an oversampling rate of 25, 0.86 s at 50, 1.76 s at 100, 3.56 s at
        # 200), so the declared maximum of 255 needs about 4.5 s. The 1 s of the
        # reference library was therefore too short above an oversampling rate of about
        # 55, and had little margin even at the default of 25: the read returned an
        # empty string while the answer was still on its way, the next command was
        # written into it, and the device stopped answering until it was unplugged.
        self.port_properties: dict[str, Any] = {
            "timeout": 8,
            "baudrate": 9600,
            "EOL": "\n",
        }

        # Raw GUI selection, converted in configure() into the attributes below.
        self.gui_parameters: dict[str, Any] = {}

        self.source: str = "Voltage in V"
        self.compliance: float = 0.02  # 20 mA default compliance, in amperes
        self.oversampling: int = 25

        # Staged sweep value, written in apply() and consumed in measure().
        self._pending_voltage: float = 0.0

        # Measurement buffer
        self._measured_voltage: float = 0.0
        self._measured_current: float = 0.0

        self.command_delay_s: float = self.DEFAULT_COMMAND_DELAY_S

    # --- GUI interaction -------------------------------------------------------

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI fields of the SMU module.

        The uSMU can only source voltage, so SweepMode offers a single entry. The
        compliance is entered in amperes, the SweepMe! convention for SMU drivers.
        """
        return {
            "SweepMode": ["Voltage in V"],
            "Compliance": parameters.get("Compliance", 0.02),
            "Average": parameters.get("Average", 25),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Keep the user's selection; it is converted in configure()."""
        self.gui_parameters = parameters

    # --- Standard semantic functions -------------------------------------------

    def connect(self) -> None:
        """Verify the device identity on the open port.

        The uSMU firmware reports itself as either "uSMU" or "nanoSMU" depending
        on the build variant, so both are accepted.
        """
        identity = self.get_identification()
        if "USMU" not in identity.upper() and "NANOSMU" not in identity.upper():
            msg = (
                f"The instrument on this port answered {identity!r}, which is not an "
                f"Undalogic uSMU. Please check the selected port."
            )
            raise ValueError(msg)

    def configure(self) -> None:
        """Convert the GUI selection and set the instrument up for the run."""
        parameters = self.gui_parameters

        self.source = str(parameters.get("SweepMode", "Voltage in V"))
        self.compliance = float(parameters.get("Compliance", 0.02))
        self.oversampling = int(float(parameters.get("Average", 25)))

        # Out-of-range entries are refused by the declared ranges of the commands,
        # with a message naming the bound.
        self.set_oversample_rate(self.oversampling)
        self.set_current_limit(self.compliance)

    def poweron(self) -> None:
        """Enable the output at a defined 0 V level.

        CH1:ENA only raises the amplifier-enable pin; the DAC keeps whatever
        voltage the previous run left behind, so that voltage would appear at
        the terminals until the first sweep point is applied (visible as an
        LED blink at the start of a run whose predecessor ended at forward
        bias). Drive the DAC to 0 V before enabling so every run starts from
        the same state regardless of what ran before.
        """
        self.set_voltage(0.0)
        self.set_output(True)

    def poweroff(self) -> None:
        """Disable the output, which leaves it high-impedance."""
        self.set_output(False)

    def apply(self) -> None:
        """Stage the requested sweep value.

        The atomic CH1:MEA:VOL command both applies the voltage and returns the
        measurement, so the transfer happens in measure().
        """
        self._pending_voltage = float(self.value)

    def measure(self) -> None:
        """Apply the staged voltage and keep the measured voltage and current."""
        self._measured_voltage, self._measured_current = self.set_voltage_and_measure(
            self._pending_voltage,
        )

    def call(self) -> list[float]:
        """Return the most recent measurement, one value per variable."""
        return [self._measured_voltage, self._measured_current]

    # --- Communication commands ------------------------------------------------

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification string of the device."""
        return self._query("*IDN?")

    @command
    def set_output(self, output: bool) -> None:
        """Switch the output on or off."""
        self._write("CH1:ENA" if output else "CH1:DIS")

    @command
    def set_voltage(self, voltage: Volts) -> None:
        """Set the output voltage without measuring."""
        self._write(f"CH1:VOL {voltage}")

    # check_driver: ignore DC005 - CH1:MEA:VOL sets and measures in one atomic round-trip; a reader by design
    @command(returns=("voltage", "current"))
    def set_voltage_and_measure(self, voltage: Volts) -> tuple[Volts, Amperes]:
        """Set the output voltage and return the measured voltage and current."""
        response = self._query(f"CH1:MEA:VOL {voltage}")
        return self._parse_measurement(response)

    @command
    def set_current_limit(self, current_limit: Amperes) -> None:
        """Set the current limit of the source.

        The value is given in amperes, the SweepMe! convention; the firmware's
        CH1:CUR command expects milliamps, so it is converted here.
        """
        self._write(f"CH1:CUR {current_limit * 1000.0}")

    @command
    def set_oversample_rate(self, oversample: Annotated[int, Range(1, 255)]) -> None:
        """Set how many samples the device averages per measurement."""
        self._write(f"CH1:OSR {oversample}")

    @command(returns=("adc_value",))
    def read_adc(self, adc_channel: int) -> int:
        """Return a differential ADC conversion between adjacent channels.

        Channel 0 reads the difference of channels 0 and 1, channel 2 that of
        channels 2 and 3.
        """
        response = self._query(f"ADC {adc_channel}")
        try:
            return int(response)
        except ValueError as exc:
            msg = f"The device answered {response!r} to an ADC conversion, which is not a number."
            raise ValueError(msg) from exc

    @command
    def set_dac(self, voltage_dac_code: int) -> None:
        """Write the 16-bit voltage DAC directly, for calibration and diagnostics.

        Normal use sets the output with set_voltage.
        """
        self._write(f"DAC {voltage_dac_code}")

    @command
    def set_current_limit_dac(self, current_limit_dac_code: int) -> None:
        """Write the 12-bit current-limit DAC directly, for calibration and diagnostics.

        Normal use sets the limit with set_current_limit.
        """
        self._write(f"ILIM {current_limit_dac_code}")

    @command(
        warnings=("The device no longer behaves as a source until calibration mode is left.",),
    )
    def enable_voltage_calibration_mode(self) -> None:
        """Put the device into voltage calibration mode."""
        self._write("CH1:VCAL")

    # --- Helper functions ------------------------------------------------------

    def _write(self, command_string: str) -> None:
        """Send a command and wait for the firmware's settling window."""
        self.port.write(command_string)
        if self.command_delay_s > 0:
            time.sleep(self.command_delay_s)

    def _query(self, command_string: str) -> str:
        """Send a command and read back a single response line."""
        self._write(command_string)
        return self._sanitize(self.port.read())

    @staticmethod
    def _sanitize(text: str) -> str:
        """Strip the stray null bytes the firmware sometimes prefixes, and whitespace."""
        if text is None:
            return ""
        return text.replace("\x00", "").strip()

    @staticmethod
    def _parse_measurement(response: str) -> tuple[float, float]:
        """Parse a 'voltage,current' answer into two numbers.

        An answer without a comma leaves the current empty and one with more than one
        comma leaves it unparseable, so both end in the same error as non-numbers do.
        """
        voltage_text, _, current_text = response.partition(",")
        try:
            return float(voltage_text), float(current_text)
        except ValueError as exc:
            msg = f"The device answered {response!r} to a measurement, which is not the expected 'voltage,current'."
            raise ValueError(msg) from exc
