# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023-2026 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank Dr. Anton Kirch for providing the initial list sweep feature.

# SweepMe! driver
# * Module: SMU
# * Instrument: Keithley 2400

"""SweepMe! driver for the Keithley 2400 SourceMeter."""

from __future__ import annotations

import math
import time
from typing import Annotated, Any, Literal

import numpy as np
import pyvisa
import serial
from pysweepme.commands import Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug, error
from pyvisa import constants

# What the communication commands take and answer. The text choices use the SCPI spelling of the instrument.
Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]
Seconds = Annotated[float, Unit("s")]
# Source and trigger delay: 0 to 999.9999 s (manual 18-83 and 18-122)
MAX_DELAY = 999.9999
Delay = Annotated[Seconds, Range(0.0, MAX_DELAY)]
Function = Literal["VOLT", "CURR"]
SourceMode = Literal["FIX", "LIST", "SWE"]
Source = Annotated[Function, Selector()]
Terminals = Literal["FRON", "REAR"]
FilterType = Literal["REP", "MOV"]
Nplc = Annotated[float, Range(0.01, 10.0)]

# SweepMode option -> source function; the labels in brackets were used by earlier versions of the driver
SOURCE_FUNCTIONS: dict[str, Function] = {
    "Voltage in V": "VOLT",
    "Current in A": "CURR",
    "Voltage [V]": "VOLT",
    "Current [A]": "CURR",
}

# Speed option -> integration time in power line cycles
SPEED_TO_NPLC: dict[str, float] = {
    "Fast": 0.1,
    "Medium": 1.0,
    "Slow": 10.0,
    "Very fast": 0.01,
}

# Range option -> current range in A, None for auto ranging
CURRENT_RANGES: dict[str, float | None] = {
    "Auto": None,
    "10 nA": 1e-8,
    "100 nA": 1e-7,
    "1 µA": 1e-6,
    "10 µA": 1e-5,
    "100 µA": 1e-4,
    "1 mA": 1e-3,
    "10 mA": 1e-2,
    "100 mA": 1e-1,
    "1 A": 1.0,
}

# ListSweepStepPointsType option -> how the sweep values are calculated
STEP_WIDTH = "Step width"
POINTS_LINEAR = "Points (lin.)"
POINTS_LOG = "Points (log.)"
STEP_POINTS_TYPES: dict[str, str] = {
    "Step width:": STEP_WIDTH,
    "Points (lin.):": POINTS_LINEAR,
    "Points (log.):": POINTS_LOG,
}


class Device(EmptyDevice):
    """Driver for the Keithley 2400 SourceMeter using the SCPI command set.

    The user documentation is in doc/description.md.
    """

    # Option of the SMU module's SweepValue field when the driver offers 'ListSweepCheck'
    LIST_SWEEP = "List sweep"

    # The instrument takes at most 100 values in a source list
    MAX_LIST_POINTS = 100

    # Highest number of readings the averaging filter takes
    MAX_AVERAGE = 100

    # Each reading of READ? consists of voltage, current, resistance, time stamp and status
    VALUES_PER_READING = 5

    # Timeout of the port in s without the time that a READ? takes
    BASE_TIMEOUT = 10.0

    # Duration of a power line cycle in s at 50 Hz, the longer one of the two line frequencies
    POWER_LINE_CYCLE = 0.02

    # Number of integration times that one reading can take: voltage and current, each with the reference and
    # zero measurement of autozero
    INTEGRATIONS_PER_READING = 6

    # Longest timeout in s that pyvisa accepts (4,294,967,294 ms)
    MAX_TIMEOUT = 4_294_967.0

    # Longest automatic source delay in s (manual: 1 ms to 3 ms, depending on the range)
    AUTO_SOURCE_DELAY = 0.005

    # Firmware versions up to this year cannot switch the GPIB protocol
    LAST_YEAR_WITHOUT_PROTOCOL_SWITCH = 1998

    def __init__(self) -> None:
        """Define the returned variables and the port."""
        super().__init__()

        self.shortname = "Keithley2400"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        self.port_properties = {
            "timeout": 10,
            "EOL": "\r",
            "baudrate": 9600,
        }

        # GUI parameters as chosen by the user, converted in 'configure'
        self.gui_parameters: dict[str, Any] = {}
        self.port_string: str = ""
        self.list_sweep: bool = False

        # Converted in 'configure'
        self.source_function: Function = "VOLT"
        self.route_out: str = "Front"
        self.compliance: float = 100e-6
        self.current_range: float | None = None
        self.nplc: float = 0.1
        self.four_wire: bool = False
        self.average: int = 1
        self.sweep_values: list[float] = []
        self.source_delay: float | None = None
        """Hold time in s between setting a list value and the measurement, None for AUTO."""
        self.trigger_delay: float | None = None
        """Delay time in s between the trigger and setting a list value, None for the default of 0 s."""

        # Number of readings that one READ? returns, as last set with set_trigger_count; None if unknown
        self.trigger_count: int | None = None

        # Timing as last sent, which sets the timeout of the port; the values after a reset
        self.sent_nplc: dict[str, float] = {"CURR": 1.0, "VOLT": 1.0}
        self.sent_filter_count: int = 10
        self.sent_filter_enabled: bool = False
        self.sent_source_delay: float | None = None
        """None for the automatic source delay."""
        self.sent_trigger_delay: float = 0.0

        # Results of the last measurement
        self.voltages: list[float] = []
        self.currents: list[float] = []
        self.times: list[float] = []

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the fields that are shown in the graphical user interface."""
        del parameters
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Front", "Rear"],
            "Speed": ["Fast", "Medium", "Slow", "Very fast"],
            "Range": list(CURRENT_RANGES),
            "Compliance": 100e-6,
            "Average": 1,
            "4wire": False,
            "ListSweepCheck": True,
            "ListSweepType": ["Sweep", "Custom"],
            "ListSweepStart": 0.5,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": list(STEP_POINTS_TYPES),
            "ListSweepStepPointsValue": 0.1,
            "ListSweepCustomValues": "",
            "ListSweepDual": False,
            "ListSweepHoldtime": 0.1,
            "ListSweepDelaytime": 0.1,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Take over the parameters that were chosen by the user in the graphical user interface."""
        # A copy, so that a later failed update of the parameters does not reach the driver
        self.gui_parameters = dict(parameters)
        self.port_string = str(parameters.get("Port", ""))

        # When this driver is used with pysweepme, the SweepValue parameter might be missing
        self.list_sweep = parameters.get("SweepValue", "SweepEditor") == self.LIST_SWEEP

        # In a list sweep, each point comes with the time stamp of its measurement
        if self.list_sweep:
            self.variables = ["Voltage", "Current", "Timestamp"]
            self.units = ["V", "A", "s"]
            self.plottype = [True, True, True]
            self.savetype = [True, True, True]
        else:
            self.variables = ["Voltage", "Current"]
            self.units = ["V", "A"]
            self.plottype = [True, True]
            self.savetype = [True, True]

    def initialize(self) -> None:
        """Switch a GPIB instrument to the SCPI protocol, reset it and switch off the beeper."""
        identification = self.get_identification()

        # The Keithley 2400 supports two GPIB protocols: 488.1 and SCPI. SCPI works more reliably: with 488.1 several
        # instruments on the bus can lead to timeout errors. The protocol can only be switched with firmware versions
        # later than 1998.
        if (
            not self.port_string.startswith("COM")
            and self.parse_firmware_year(identification) > self.LAST_YEAR_WITHOUT_PROTOCOL_SWITCH
        ):
            self.select_scpi_protocol(identification)

        self.reset()
        self.clear()
        self.set_beeper(False)

    def deinitialize(self) -> None:
        """Return to 2-wire sensing, front terminals, 1 NPLC, no averaging, and give the control back to the panel."""
        self.set_four_wire(False)
        self.set_terminals("FRON")
        self.set_current_nplc(1.0)
        self.set_voltage_nplc(1.0)
        self.set_averaging_filter(False)
        self.set_filter_count(1)
        self.set_beeper(False)
        self.go_to_local()

    def configure(self) -> None:
        """Convert the parameters and set terminals, source, compliance, ranges, speed, sensing and averaging."""
        self.convert_parameters()

        # The trigger count must be 1 for single points, also after a list sweep in a previous branch
        self.set_trigger_count(1)
        self.set_source_auto_clear(False)
        self.set_terminals("REAR" if self.route_out == "Rear" else "FRON")

        self.set_source_function(self.source_function)
        self.set_source_mode(self.source_function, "FIX")
        if self.source_function == "VOLT":
            self.set_sense_function("CURR")
            self.set_current_compliance(self.compliance)
            if self.current_range is None:
                self.set_current_measure_autorange(True)
            else:
                self.set_current_measure_autorange(False)
                self.set_current_measure_range(self.current_range)
        else:
            self.set_sense_function("VOLT")
            self.set_voltage_compliance(self.compliance)
            if self.current_range is None:
                self.set_current_source_autorange(True)
            else:
                self.set_current_source_autorange(False)
                self.set_current_source_range(self.current_range)

        self.set_current_nplc(self.nplc)
        self.set_voltage_nplc(self.nplc)
        self.set_four_wire(self.four_wire)

        self.set_filter_type("REP")
        if self.average > 1:
            self.set_averaging_filter(True)
            self.set_filter_count(self.average)
        else:
            self.set_averaging_filter(False)
            self.set_filter_count(1)

        # The defaults after *RST: automatic source delay and no trigger delay. They must be set again in case a
        # previous branch used the list sweep.
        self.set_delay(None)
        self.set_trigger_delay(None)

        if self.list_sweep:
            self.configure_list_sweep()

        # All settings must be done before the run continues
        self.wait_for_complete()

    def poweron(self) -> None:
        """Switch on the output."""
        self.set_output(True)

    def poweroff(self) -> None:
        """Switch off the output."""
        self.set_output(False)

    def apply(self) -> None:
        """Set the new source level."""
        if self.source_function == "VOLT":
            self.set_voltage(float(self.value))
        else:
            self.set_current(float(self.value))

    def reach(self) -> None:
        """Wait until the source level is set."""
        self.wait_for_complete()

    # check_driver: ignore DC014 - READ? is requested here and read in 'call', so that all instruments of the branch
    # measure at the same time; get_voltage_current_time sends the same command for scripts
    def measure(self) -> None:
        """Start the measurement, or the list sweep."""
        self.port.write("READ?")

    def call(self) -> list[float] | list[list[float]]:
        """Return voltage in V and current in A, and in a list sweep the time stamp in s of each point."""
        answer = self.port.read()
        if answer == "":
            answer = self.port.read()
        self.voltages, self.currents, self.times = self.parse_readings(answer)

        if self.list_sweep:
            return [self.voltages, self.currents, self.times]

        return [self.voltages[0], self.currents[0]]

    # Functions that are used by the semantic functions start here

    @staticmethod
    def parse_firmware_year(identification: str) -> int:
        """Return the year of the firmware from the identification string, or -1 if it is unknown.

        The firmware field looks like 'C30   Mar 17 2006 09:29:29/A02  /K/J'.
        """
        fields = identification.split(",")
        try:
            return int(fields[3].split()[3])
        except (IndexError, ValueError):
            return -1

    def select_scpi_protocol(self, identification: str) -> None:
        """Switch the GPIB protocol from 488.1 to SCPI, if needed."""
        try:
            if self.get_scpi_protocol():
                return

            self.set_scpi_protocol(True)
            # A short time is needed before the new protocol works and new commands can be received
            time.sleep(0.1)
            if self.get_scpi_protocol():
                debug("Keithley 2400: The GPIB protocol was changed to SCPI.")
            else:
                debug(
                    "Keithley 2400: The GPIB protocol could not be changed to SCPI. Please change it on the front "
                    "panel: Menu -> Communication -> GPIB -> GPIB Protocol.",
                )
        except Exception:  # the run continues with the 488.1 protocol
            error(f"Keithley 2400: Unable to change the GPIB protocol to SCPI for the instrument '{identification}'.")

    def convert_parameters(self) -> None:
        """Convert and check the parameters of the graphical user interface."""
        parameters = self.gui_parameters

        sweep_mode = str(parameters.get("SweepMode", "Voltage in V"))
        if sweep_mode not in SOURCE_FUNCTIONS:
            msg = f"SweepMode '{sweep_mode}' is not supported. Use 'Voltage in V' or 'Current in A'."
            raise ValueError(msg)
        self.source_function = SOURCE_FUNCTIONS[sweep_mode]

        self.route_out = str(parameters.get("RouteOut", "Front"))
        if self.route_out not in ("Front", "Rear"):
            msg = f"RouteOut '{self.route_out}' is not supported. Use 'Front' or 'Rear'."
            raise ValueError(msg)

        speed = str(parameters.get("Speed", "Fast"))
        if speed not in SPEED_TO_NPLC:
            msg = f"Speed '{speed}' is not supported. Use one of {', '.join(SPEED_TO_NPLC)}."
            raise ValueError(msg)
        self.nplc = SPEED_TO_NPLC[speed]

        range_option = str(parameters.get("Range", "Auto"))
        if range_option not in CURRENT_RANGES:
            msg = f"Range '{range_option}' is not supported. Use one of {', '.join(CURRENT_RANGES)}."
            raise ValueError(msg)
        self.current_range = CURRENT_RANGES[range_option]

        # The instrument takes signed limits (-1.05 to 1.05 A, -210 to 210 V), so only finite numbers are required
        self.compliance = self.convert_number(parameters.get("Compliance", 100e-6), "Compliance")

        average = self.convert_number(parameters.get("Average", 1), "Average")
        if not 1 <= average <= self.MAX_AVERAGE or average != int(average):
            msg = f"Average must be a whole number from 1 to {self.MAX_AVERAGE}, not {average}."
            raise ValueError(msg)
        self.average = int(average)

        self.four_wire = bool(parameters.get("4wire", False))

        if self.list_sweep:
            self.convert_list_sweep_parameters()

    def convert_list_sweep_parameters(self) -> None:
        """Convert the list sweep fields into sweep values, hold time and delay time."""
        parameters = self.gui_parameters

        if parameters.get("ListSweepType", "Sweep") == "Custom":
            self.sweep_values = self.parse_custom_values(str(parameters.get("ListSweepCustomValues", "")))
        else:
            self.sweep_values = self.calculate_sweep_values()

        if not 1 <= len(self.sweep_values) <= self.MAX_LIST_POINTS:
            msg = (
                f"The list sweep has {len(self.sweep_values)} points, but the instrument takes 1 to "
                f"{self.MAX_LIST_POINTS} points."
            )
            raise ValueError(msg)

        # An empty hold time uses the automatic source delay, an empty delay time the default trigger delay of 0 s
        self.source_delay = self.convert_time(parameters.get("ListSweepHoldtime", 0.1), "Hold time")
        self.trigger_delay = self.convert_time(parameters.get("ListSweepDelaytime", 0.1), "Delay time")

    def calculate_sweep_values(self) -> list[float]:
        """Calculate the sweep values from start value, end value and step width or number of points."""
        parameters = self.gui_parameters

        start = self.convert_number(parameters.get("ListSweepStart", 0.5), "ListSweepStart")
        end = self.convert_number(parameters.get("ListSweepEnd", 1.0), "ListSweepEnd")
        steppoints = self.convert_number(parameters.get("ListSweepStepPointsValue", 0.1), "ListSweepStepPointsValue")

        steppoints_option = str(parameters.get("ListSweepStepPointsType", "Step width:"))
        if steppoints_option not in STEP_POINTS_TYPES:
            msg = (
                f"ListSweepStepPointsType '{steppoints_option}' is not supported. Use one of "
                f"{', '.join(STEP_POINTS_TYPES)}."
            )
            raise ValueError(msg)
        steppoints_type = STEP_POINTS_TYPES[steppoints_option]

        if steppoints_type == STEP_WIDTH:
            if steppoints == 0.0:
                if end != start:
                    msg = "Start and end value of the list sweep must be equal if the step width is 0."
                    raise ValueError(msg)
                points = 1
            else:
                points = round(abs(end - start) / abs(steppoints) + 1)
        else:
            points = int(steppoints)

        if points < 1:
            msg = f"The list sweep needs at least 1 point, not {points}."
            raise ValueError(msg)

        dual = self.convert_flag(parameters.get("ListSweepDual", False))
        self.check_list_size(points, dual, steppoints_type == POINTS_LOG)

        if steppoints_type == POINTS_LOG:
            if start * end <= 0:
                msg = "Start and end value of a logarithmic list sweep must have the same sign and must not be 0."
                raise ValueError(msg)
            values = np.geomspace(start, end, points)
        else:
            values = np.linspace(start, end, points)

        if dual:
            # Back to the start value; the end value is used once in a linear sweep and twice in a logarithmic one
            backwards = np.flipud(values) if steppoints_type == POINTS_LOG else np.flipud(values[:-1])
            values = np.append(values, backwards)

        return [float(value) for value in values]

    def check_list_size(self, points: int, dual: bool, logarithmic: bool) -> None:
        """Refuse a sweep with more values than the instrument takes, before the values are calculated.

        A dual sweep adds the way back: without the end value in a linear sweep, with it in a logarithmic one.
        """
        total_points = points
        if dual:
            total_points = 2 * points if logarithmic else 2 * points - 1
        if total_points > self.MAX_LIST_POINTS:
            msg = f"The list sweep has {total_points} points, but the instrument takes 1 to {self.MAX_LIST_POINTS}."
            raise ValueError(msg)

    @staticmethod
    def parse_custom_values(text: str) -> list[float]:
        """Convert the custom values of the list sweep, separated by commas, into a list of floats."""
        try:
            values = [float(entry) for entry in text.split(",")]
        except ValueError:
            msg = f"The custom values of the list sweep must be numbers separated by commas, not '{text}'."
            raise ValueError(msg) from None

        if not all(math.isfinite(value) for value in values):
            msg = f"The custom values of the list sweep must be finite numbers, not '{text}'."
            raise ValueError(msg)
        return values

    @staticmethod
    def convert_number(value: Any, name: str) -> float:  # noqa: ANN401 - a GUI value of any type
        """Convert a GUI value into a float, with a message naming the field if that is not possible."""
        try:
            number = float(value)
        except (TypeError, ValueError):
            msg = f"{name} must be a number, not '{value}'."
            raise ValueError(msg) from None

        if not math.isfinite(number):
            msg = f"{name} must be a finite number, not '{value}'."
            raise ValueError(msg)

        return number

    @staticmethod
    def check_finite(value: float, name: str) -> None:
        """Raise if a value for the instrument is NaN or infinite, which it would not apply."""
        if not math.isfinite(value):
            msg = f"{name} must be a finite number, not {value}."
            raise ValueError(msg)

    @staticmethod
    def convert_flag(value: Any) -> bool:  # noqa: ANN401 - a GUI value of any type
        """Convert a check box value into a bool; the text "0" or "false" is False, as in earlier versions."""
        if isinstance(value, str):
            text = value.strip().lower()
            if text in ("true", "yes", "on"):
                return True
            try:
                return float(text) != 0
            except ValueError:
                return False
        return bool(value)

    @staticmethod
    def convert_time(value: Any, name: str) -> float | None:  # noqa: ANN401 - a GUI value of any type
        """Convert a time field of the list sweep into seconds, None if the field is empty."""
        if str(value).strip() == "":
            return None

        try:
            time_value = float(value)
        except ValueError:
            msg = f"The {name} of the list sweep must be a number in s or empty, not '{value}'."
            raise ValueError(msg) from None

        if not math.isfinite(time_value) or not 0 <= time_value <= MAX_DELAY:
            msg = f"The {name} of the list sweep must be a number from 0 s to {MAX_DELAY} s, not {time_value} s."
            raise ValueError(msg)

        return time_value

    def configure_list_sweep(self) -> None:
        """Hand the sweep values to the instrument, which steps through them at one READ?."""
        self.set_source_mode(self.source_function, "LIST")
        if self.source_function == "VOLT":
            self.set_voltage_list(self.sweep_values)
        else:
            self.set_current_list(self.sweep_values)

        self.set_trigger_count(len(self.sweep_values))
        self.set_trigger_delay(self.trigger_delay)
        self.set_delay(self.source_delay)

    def update_port_timeout(self) -> None:
        """Extend the timeout of the port by the time that one READ? can take, for all points of a list sweep.

        The instrument answers READ? only when all points are measured, each after its trigger delay, source delay
        and integration time. The time follows the values that the commands sent last.
        """
        readings = self.sent_filter_count if self.sent_filter_enabled else 1
        integration_time = max(self.sent_nplc.values()) * self.POWER_LINE_CYCLE * readings
        source_delay = self.AUTO_SOURCE_DELAY if self.sent_source_delay is None else self.sent_source_delay
        point_time = self.sent_trigger_delay + source_delay + integration_time * self.INTEGRATIONS_PER_READING
        timeout = self.BASE_TIMEOUT + (self.trigger_count or 1) * point_time
        # pyvisa takes at most 4,294,967,294 ms; a longer list sweep cannot be waited for anyway
        timeout = min(timeout, self.MAX_TIMEOUT)

        # Serial ports and the Prologix controller read the timeout in s, a VISA resource in ms. The port properties
        # are updated for all of them, as pysweepme reads the timeout of Prologix there.
        self.port.port_properties["timeout"] = timeout
        if isinstance(self.port.port, pyvisa.resources.Resource):
            self.port.port.timeout = timeout * 1000
        elif isinstance(self.port.port, serial.Serial):
            self.port.port.timeout = timeout

    def parse_readings(self, answer: str) -> tuple[list[float], list[float], list[float]]:
        """Split the answer of READ? into voltages in V, currents in A and time stamps in s."""
        try:
            data = np.array([float(value) for value in answer.split(",")])
            data = data.reshape((-1, self.VALUES_PER_READING))
        except ValueError as exception:
            msg = f"Unexpected answer of the instrument to READ?: {answer!r}."
            raise ValueError(msg) from exception

        # A reply that was cut short would otherwise return fewer points without an error
        if self.trigger_count is not None and len(data) != self.trigger_count:
            msg = f"The instrument returned {len(data)} readings to READ?, but {self.trigger_count} were requested."
            raise ValueError(msg)

        return (
            [float(value) for value in data[:, 0]],
            [float(value) for value in data[:, 1]],
            [float(value) for value in data[:, 3]],
        )

    # Communication commands start here

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        return str(self.port.query("*IDN?"))

    @command(returns=("scpi_protocol",), reads="setpoint")
    def get_scpi_protocol(self) -> bool:
        """Return whether the instrument uses the SCPI protocol (True) or the 488.1 protocol (False) on GPIB."""
        return str(self.port.query("SYST:MEP:STAT?")).strip() == "1"

    @command
    def set_scpi_protocol(self, scpi_protocol: bool) -> None:
        """Select the SCPI protocol (True) or the 488.1 protocol (False) for GPIB."""
        self.port.write(f"SYST:MEP:STAT {int(scpi_protocol)}")

    @command
    def reset(self) -> None:
        """Reset the instrument to its default settings."""
        self.port.write("*RST")
        # The settings after a reset
        self.trigger_count = 1
        self.sent_nplc = {"CURR": 1.0, "VOLT": 1.0}
        self.sent_filter_count = 10
        self.sent_filter_enabled = False
        self.sent_source_delay = None
        self.sent_trigger_delay = 0.0
        self.update_port_timeout()

    @command
    def clear(self) -> None:
        """Clear the status registers and the error queue."""
        self.port.write("*CLS")

    @command
    def wait_for_complete(self) -> None:
        """Wait until all pending commands are completed."""
        self.port.query("*OPC?")

    @command
    def set_beeper(self, beeper: bool) -> None:
        """Switch the beeper on or off."""
        self.port.write(f"SYST:BEEP:STAT {'ON' if beeper else 'OFF'}")

    @command
    def go_to_local(self) -> None:
        """Give the control back to the front panel: SYST:LOC on RS-232, the go-to-local message on GPIB."""
        if self.port_string.startswith("COM"):
            self.port.write("SYST:LOC")
            return

        # GTL is a GPIB interface message, not a SCPI command, so it is sent by the GPIB controller
        control_ren = getattr(self.port.port, "control_ren", None)
        if control_ren is None:
            debug("Keithley 2400: This interface cannot send go-to-local. Press LOCAL on the front panel.")
            return
        control_ren(constants.RENLineOperation.address_gtl)

    @command
    def set_trigger_count(self, trigger_count: Annotated[int, Range(1, 2500)]) -> None:
        """Set the number of source and measure cycles that one READ? runs."""
        self.port.write(f":TRIG:COUN {trigger_count:d}")
        self.trigger_count = trigger_count
        self.update_port_timeout()

    @command
    def set_source_auto_clear(self, source_auto_clear: bool) -> None:
        """Switch the automatic output-off after each measurement on or off."""
        self.port.write(f":SOUR:CLE:AUTO {'ON' if source_auto_clear else 'OFF'}")

    @command(warnings="Switches off the output if it is on while the terminals are changed.")
    def set_terminals(self, terminals: Terminals) -> None:
        """Select the front or the rear terminals."""
        self.port.write(f"ROUT:TERM {terminals}")

    @command
    def set_source_function(self, source_function: Function) -> None:
        """Set the source function to voltage or current."""
        self.port.write(f":SOUR:FUNC {source_function}")

    @command
    def set_source_mode(self, source: Source, source_mode: SourceMode) -> None:
        """Set the source mode of the voltage or current source: fixed level, list or sweep."""
        self.port.write(f":SOUR:{source}:MODE {source_mode}")

    @command
    def set_sense_function(self, sense_function: Function) -> None:
        """Set the measure function to voltage or current."""
        self.port.write(f':SENS:FUNC "{sense_function}"')

    @command
    def set_current_compliance(self, current_compliance: Amperes) -> None:
        """Set the current compliance in A that is used while voltage is sourced."""
        self.check_finite(current_compliance, "current_compliance")
        self.port.write(f":SENS:CURR:PROT {current_compliance}")

    @command
    def set_voltage_compliance(self, voltage_compliance: Volts) -> None:
        """Set the voltage compliance in V that is used while current is sourced."""
        self.check_finite(voltage_compliance, "voltage_compliance")
        self.port.write(f":SENS:VOLT:PROT {voltage_compliance}")

    @command
    def set_current_measure_autorange(self, current_measure_autorange: bool) -> None:
        """Switch the auto range of the current measurement on or off."""
        self.port.write(f":SENS:CURR:RANG:AUTO {'ON' if current_measure_autorange else 'OFF'}")

    @command
    def set_current_measure_range(self, current_measure_range: Amperes) -> None:
        """Set a fixed current measurement range in A."""
        self.port.write(f":SENS:CURR:RANG {current_measure_range}")

    @command
    def set_current_source_autorange(self, current_source_autorange: bool) -> None:
        """Switch the auto range of the current source on or off."""
        self.port.write(f":SOUR:CURR:RANG:AUTO {'ON' if current_source_autorange else 'OFF'}")

    @command
    def set_current_source_range(self, current_source_range: Amperes) -> None:
        """Set a fixed current source range in A."""
        self.port.write(f":SOUR:CURR:RANG {current_source_range}")

    @command
    def set_current_nplc(self, current_nplc: Nplc) -> None:
        """Set the integration time of the current measurement in power line cycles."""
        self.port.write(f":SENS:CURR:DC:NPLC {current_nplc}")
        self.sent_nplc["CURR"] = current_nplc
        self.update_port_timeout()

    @command
    def set_voltage_nplc(self, voltage_nplc: Nplc) -> None:
        """Set the integration time of the voltage measurement in power line cycles."""
        self.port.write(f":SENS:VOLT:DC:NPLC {voltage_nplc}")
        self.sent_nplc["VOLT"] = voltage_nplc
        self.update_port_timeout()

    @command
    def set_four_wire(self, four_wire: bool) -> None:
        """Switch between 4-wire (remote) and 2-wire (local) sensing."""
        self.port.write(f"SYST:RSEN {'ON' if four_wire else 'OFF'}")

    @command
    def set_filter_type(self, filter_type: FilterType) -> None:
        """Select the repeating or the moving average as averaging filter."""
        self.port.write(f":SENS:AVER:TCON {filter_type}")

    @command
    def set_averaging_filter(self, averaging_filter: bool) -> None:
        """Switch the averaging filter on or off."""
        self.port.write(f":SENS:AVER {'ON' if averaging_filter else 'OFF'}")
        self.sent_filter_enabled = averaging_filter
        self.update_port_timeout()

    @command
    def set_filter_count(self, filter_count: Annotated[int, Range(1, 100)]) -> None:
        """Set the number of readings that are averaged by the filter."""
        self.port.write(f":SENS:AVER:COUN {filter_count:d}")
        self.sent_filter_count = filter_count
        self.update_port_timeout()

    @command
    def set_delay(self, source_delay: Delay | None = None) -> None:
        """Set the settling time in s between setting the source level and the measurement, None for auto delay.

        The delay is the same for the voltage and the current source.
        """
        if source_delay is None:
            self.port.write(":SOUR:DEL:AUTO ON")
        else:
            self.port.write(f":SOUR:DEL {source_delay:.6f}")
        self.sent_source_delay = source_delay
        self.update_port_timeout()

    @command
    def set_trigger_delay(self, trigger_delay: Delay | None) -> None:
        """Set the time in s between the trigger and setting the source level, None for the default of 0 s."""
        if trigger_delay is None:
            self.port.write(":TRIG:DEL DEF")
        else:
            self.port.write(f":TRIG:DEL {trigger_delay:.6f}")
        self.sent_trigger_delay = trigger_delay or 0.0
        self.update_port_timeout()

    @command
    def set_voltage_list(self, voltage_list: list[Volts]) -> None:
        """Set the voltages in V that the voltage source steps through in list mode, at most 100."""
        values = ",".join(f"{value:.6e}" for value in voltage_list)
        self.port.write(f":SOUR:LIST:VOLT {values}")

    @command
    def set_current_list(self, current_list: list[Amperes]) -> None:
        """Set the currents in A that the current source steps through in list mode, at most 100."""
        values = ",".join(f"{value:.6e}" for value in current_list)
        self.port.write(f":SOUR:LIST:CURR {values}")

    @command
    def set_output(self, output: bool) -> None:
        """Switch the output on or off."""
        self.port.write(f"OUTP {'ON' if output else 'OFF'}")

    @command
    def set_voltage(self, voltage: Volts) -> None:
        """Set the output voltage in V."""
        self.port.write(f":SOUR:VOLT:LEV {voltage}")

    @command
    def set_current(self, current: Amperes) -> None:
        """Set the output current in A."""
        self.port.write(f":SOUR:CURR:LEV {current}")

    @command(returns=("voltage", "current", "time"))
    def get_voltage_current_time(self) -> tuple[list[Volts], list[Amperes], list[Seconds]]:
        """Measure voltage in V, current in A and time stamp in s, one value per point of the trigger count."""
        return self.parse_readings(self.port.query("READ?"))
