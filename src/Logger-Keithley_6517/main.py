# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2023-2026 SweepMe! GmbH (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank TU Dresden/Jacob Hille for providing the initial version of this driver.

# SweepMe! driver
# * Module: Logger
# * Instrument: Keithley 6517B

"""SweepMe! driver for the Keithley 6517B electrometer."""

from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keithley 6517B electrometer to measure currents, optionally with the built-in voltage source."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "Keithley 6517B"

        self.variables = ["Current"]
        self.units = ["A"]
        self.plottype = [True]
        self.savetype = [True]

        self.port_manager = True
        self.port_types = ["GPIB", "COM"]

        self.port_properties = {
            "timeout": 10.0,
            "baudrate": 9600,
            "EOL": "\r",
        }

        # current ranges as shown in the GUI and the expected reading in A that is sent to the instrument
        self.current_ranges = {
            "Auto": "",
            "20 mA": "20e-3",
            "2 mA": "2e-3",
            "200 µA": "200e-6",
            "20 µA": "20e-6",
            "2 µA": "2e-6",
            "200 nA": "200e-9",
            "20 nA": "20e-9",
            "2 nA": "2e-9",
            "200 pA": "200e-12",
            "20 pA": "20e-12",
            "2 pA": "2e-12",
            "200 fA": "200e-15",
            "20 fA": "20e-15",
            "2 fA": "2e-15",
        }

        self.rates = {
            "Very Fast": 0.01,
            "Fast": 0.1,
            "Medium": 1.0,
            "Slow": 10.0,
        }

        self.source_voltage_ranges = {
            "100 V": 100.0,
            "1000 V": 1000.0,
        }

        # the connection of the voltage source LO to the ammeter LO is needed to source voltage and measure current
        self.source_voltage_connections = {
            "V-SOURCE HI and INPUT HI": True,
            "V-SOURCE HI and V-SOURCE LO": False,
        }

        # measurement function, only currents are supported
        self.mode = "CURR"

        # GUI parameters
        self.current_range: str = "Auto"
        self.nplc: float = 1.0
        self.average_count: int = 1
        self.line_sync: bool = True
        self.perform_zero_check: bool = False
        self.use_zero_correction: bool = False

        self.use_voltage_source: bool = False
        self.source_voltage: float = 0.0
        self.source_voltage_range: float = 100.0
        self.source_voltage_limit: float = 5.0
        self.meter_connect: bool = True

        # measured value
        self.measured_value: float = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI parameters and their options depending on the current selection."""
        use_voltage_source = parameters.get("Use voltage source", False)

        new_parameters: dict[str, Any] = {
            "Range": list(self.current_ranges.keys()),
            "Rate": list(self.rates.keys()),
            "Average": 1,
            "Line sync": True,
            "Perform zero check": False,
            "Use zero correction": False,
            "Use voltage source": False,
        }

        if use_voltage_source:
            new_parameters.update(
                {
                    "Source voltage in V": 0.0,
                    "Source voltage range": list(self.source_voltage_ranges.keys()),
                    "Source voltage limit in V": 5.0,
                    "Source voltage connection": list(self.source_voltage_connections.keys()),
                },
            )

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the GUI parameters selected by the user."""
        self.current_range = parameters.get("Range", "Auto")
        self.nplc = self.rates.get(parameters.get("Rate", "Very Fast"), 0.01)
        self.average_count = int(parameters.get("Average", 1))
        self.line_sync = bool(parameters.get("Line sync", True))
        self.perform_zero_check = bool(parameters.get("Perform zero check", False))
        self.use_zero_correction = bool(parameters.get("Use zero correction", False))

        self.use_voltage_source = bool(parameters.get("Use voltage source", False))
        if self.use_voltage_source:
            self.source_voltage = self.parse_source_voltage(parameters.get("Source voltage in V", 0.0))
            self.source_voltage_range = self.source_voltage_ranges.get(
                parameters.get("Source voltage range", "100 V"),
                100.0,
            )
            self.source_voltage_limit = float(parameters.get("Source voltage limit in V", 5.0))
            self.meter_connect = self.source_voltage_connections.get(
                parameters.get("Source voltage connection", "V-SOURCE HI and INPUT HI"),
                True,
            )

    def initialize(self) -> None:
        """Reset the instrument and check the source voltage settings."""
        self.reset()
        self.clear_status()
        self.set_line_sync(self.line_sync)

        if self.use_voltage_source:
            self.check_source_voltage()

    def configure(self) -> None:
        """Configure the current measurement and the voltage source."""
        # the manual recommends to enable zero check before changing the function
        self.set_zero_check(True)

        self.set_function(self.mode)
        self.set_data_elements("READ")
        self.set_median_filter(False)

        # Averaging
        if self.average_count == 1:
            self.set_average(False)
        else:
            self.set_average(True, self.average_count)

        self.set_nplc(self.nplc)

        # The zero correct value is acquired on the lowest range and is valid for all higher ranges
        if self.perform_zero_check:
            self.set_current_range("20e-12")
            self.acquire_zero_correction()

        self.set_zero_correction(self.use_zero_correction)

        # Range
        if self.current_range == "Auto":
            self.set_current_autorange(True)
        else:
            self.set_current_range(self.current_ranges[self.current_range])

        self.set_zero_check(False)

        if self.use_voltage_source:
            self.configure_voltage_source()

        self.print_errors()

    def reconfigure(self, parameters: dict[str, Any] | None = None, keys: list[str] | None = None) -> None:
        """Change the source voltage directly if it is the only changed parameter, otherwise configure again."""
        parameters = parameters or {}
        keys = keys or []

        if self.use_voltage_source and set(keys) == {"Source voltage in V"}:
            self.source_voltage = self.parse_source_voltage(parameters.get("Source voltage in V", 0.0))
            self.check_source_voltage()
            self.set_source_voltage(self.source_voltage)
        else:
            super().reconfigure(parameters, keys)

    def poweron(self) -> None:
        """Switch the voltage source output on."""
        if self.use_voltage_source:
            self.set_output(True)

    def poweroff(self) -> None:
        """Switch the voltage source output off."""
        if self.use_voltage_source:
            self.set_output(False)

    def measure(self) -> None:
        """Trigger a measurement and read the result.

        Triggering and reading are done in the same phase, so that several driver instances sharing the same
        instrument cannot interleave their requests.
        """
        self.measured_value = self.read_value()

    def call(self) -> list[float]:
        """Return the measured current."""
        return [self.measured_value]

    """ here, convenience functions start """

    def configure_voltage_source(self) -> None:
        """Set range, voltage, limit, and LO connection of the voltage source.

        The order avoids settings conflicts: an enabled limit would clamp a new voltage, and the 100 V range cannot be
        selected while a voltage above 100 V is set.
        """
        self.set_source_voltage_limit_state(False)

        if abs(self.source_voltage) > self.source_voltage_ranges["100 V"]:
            self.set_source_voltage_range(self.source_voltage_range)
            self.set_source_voltage(self.source_voltage)
        else:
            self.set_source_voltage(self.source_voltage)
            self.set_source_voltage_range(self.source_voltage_range)

        self.set_source_voltage_limit(self.source_voltage_limit)
        self.set_source_voltage_limit_state(True)

        self.set_meter_connect(self.meter_connect)

    @staticmethod
    def parse_source_voltage(value: Any) -> float:  # noqa: ANN401
        """Convert the source voltage GUI value to float, an empty field is interpreted as 0 V."""
        if value == "":
            return 0.0
        return float(value)

    def check_source_voltage(self) -> None:
        """Raise an exception if the source voltage exceeds the voltage limit or the selected range."""
        if abs(self.source_voltage) > self.source_voltage_limit:
            msg = (
                f"Source voltage of {self.source_voltage} V exceeds the source voltage limit of "
                f"±{self.source_voltage_limit} V."
            )
            raise ValueError(msg)

        if abs(self.source_voltage) > self.source_voltage_range:
            msg = (
                f"Source voltage of {self.source_voltage} V exceeds the source voltage range of "
                f"±{self.source_voltage_range:g} V."
            )
            raise ValueError(msg)

    def print_errors(self) -> None:
        """Read the error queue and print all errors to the debug widget."""
        # the error queue holds up to 10 messages
        for _ in range(10):
            error = self.read_error()
            # messages look like '-109,"Missing parameter;1;2017/05/06 12:57:04.484"', an empty queue returns 0
            if int(error.split(",")[0]) == 0:
                break
            print(f"Keithley 6517B error: {error}")  # noqa: T201

    """ here, communication commands are wrapped into python convenience functions """

    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        return str(self.port.query("*IDN?"))

    def reset(self) -> None:
        """Reset the instrument to its default settings."""
        self.port.write("*RST")

    def clear_status(self) -> None:
        """Clear the status registers and the error queue."""
        self.port.write("*CLS")

    def set_line_sync(self, state: bool) -> None:
        """Switch the line synchronization on or off."""
        self.port.write(f":SYST:LSYN:STAT {'ON' if state else 'OFF'}")

    def read_error(self) -> str:
        """Return the oldest message of the error queue."""
        return str(self.port.query(":SYST:ERR?"))

    def set_function(self, function: str) -> None:
        """Configure the instrument for one-shot measurements of the given function, e.g. 'CURR'."""
        self.port.write(f":CONF:{function}")

    def set_data_elements(self, elements: str) -> None:
        """Set the elements of the data string, e.g. 'READ' to only return the reading."""
        self.port.write(f":FORM:ELEM {elements}")

    def set_median_filter(self, state: bool) -> None:
        """Switch the median filter on or off."""
        self.port.write(f":SENS:{self.mode}:MED:STAT {'ON' if state else 'OFF'}")

    def set_average(self, state: bool, count: int = 1) -> None:
        """Switch the repeating average filter on or off and set its count."""
        if state:
            self.port.write(f":SENS:{self.mode}:AVER:STAT ON")
            self.port.write(f":SENS:{self.mode}:AVER:TCON REP")
            self.port.write(f":SENS:{self.mode}:AVER:COUN {count}")
        else:
            self.port.write(f":SENS:{self.mode}:AVER:STAT OFF")

    def set_nplc(self, nplc: float) -> None:
        """Set the integration time in number of power line cycles."""
        self.port.write(f":SENS:{self.mode}:NPLC {nplc}")

    def set_current_autorange(self, state: bool) -> None:
        """Switch auto range of the current measurement on or off."""
        self.port.write(f":SENS:{self.mode}:RANG:AUTO {'ON' if state else 'OFF'}")

    def set_current_range(self, current_range: str) -> None:
        """Set the current range by the expected reading in A, which also switches auto range off."""
        self.port.write(f":SENS:{self.mode}:RANG {current_range}")

    def set_zero_check(self, state: bool) -> None:
        """Switch zero check on or off."""
        self.port.write(f":SYST:ZCH {'ON' if state else 'OFF'}")

    def acquire_zero_correction(self) -> None:
        """Acquire the zero correct value, zero check must be enabled."""
        self.port.write(":SYST:ZCOR:ACQ")

    def set_zero_correction(self, state: bool) -> None:
        """Switch zero correction on or off."""
        self.port.write(f":SYST:ZCOR {'ON' if state else 'OFF'}")

    def set_source_voltage_range(self, voltage_range: float) -> None:
        """Set the voltage source range, i.e. 100 V or 1000 V."""
        self.port.write(f":SOUR:VOLT:RANG {voltage_range:g}")

    def set_source_voltage_limit(self, limit: float) -> None:
        """Set the absolute voltage limit of the voltage source in V."""
        self.port.write(f":SOUR:VOLT:LIM {limit:f}")

    def set_source_voltage_limit_state(self, state: bool) -> None:
        """Switch the voltage limit of the voltage source on or off."""
        self.port.write(f":SOUR:VOLT:LIM:STAT {'ON' if state else 'OFF'}")

    def set_source_voltage(self, voltage: float) -> None:
        """Set the voltage of the voltage source in V."""
        self.port.write(f":SOUR:VOLT {voltage:f}")

    def set_meter_connect(self, state: bool) -> None:
        """Connect or disconnect the voltage source LO and the ammeter LO internally."""
        self.port.write(f":SOUR:VOLT:MCON {'ON' if state else 'OFF'}")

    def set_output(self, state: bool) -> None:
        """Switch the voltage source output on (operate) or off (standby)."""
        self.port.write(f":OUTP:STAT {'ON' if state else 'OFF'}")

    def read_value(self) -> float:
        """Trigger a single measurement and return the reading."""
        return float(self.port.query(":READ?"))
