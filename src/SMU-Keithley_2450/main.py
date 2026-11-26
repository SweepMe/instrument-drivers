# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024-2026 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Keithley 2450

"""SweepMe! driver for the Keithley 2450 SourceMeter."""

from __future__ import annotations

import math
from typing import Annotated, Any, Literal

import pyvisa
from pysweepme.commands import Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

# What the communication commands take and answer. The text choices use the spelling of the SCPI commands; the
# commands translate them into TSP if the instrument uses the TSP command set.
Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]
Function = Literal["VOLT", "CURR"]
Source = Annotated[Function, Selector()]
Measure = Annotated[Function, Selector()]
SourceMode = Literal["FIX", "LIST", "SWE"]
Terminals = Literal["FRON", "REAR"]
FilterType = Literal["REP", "MOV"]
OutputOffMode = Literal["NORM", "ZERO", "HIMP", "GUAR"]

# Spelling of the choices in the TSP command set
TSP_FUNCTIONS: dict[str, str] = {"VOLT": "FUNC_DC_VOLTAGE", "CURR": "FUNC_DC_CURRENT"}
TSP_QUANTITIES: dict[str, str] = {"VOLT": "voltage", "CURR": "current"}
TSP_UNITS: dict[str, str] = {"VOLT": "UNIT_VOLT", "CURR": "UNIT_AMP"}
TSP_TERMINALS: dict[str, str] = {"FRON": "TERMINALS_FRONT", "REAR": "TERMINALS_REAR"}
TSP_FILTER_TYPES: dict[str, str] = {"REP": "FILTER_REPEAT_AVG", "MOV": "FILTER_MOVING_AVG"}
TSP_OUTPUT_OFF_MODES: dict[str, str] = {
    "NORM": "OFFMODE_NORMAL",
    "ZERO": "OFFMODE_ZERO",
    "HIMP": "OFFMODE_HIGHZ",
    "GUAR": "OFFMODE_GUARD",
}

# SweepMode option -> source function
SOURCE_FUNCTIONS: dict[str, Function] = {"Voltage in V": "VOLT", "Current in A": "CURR"}

# Speed option -> integration time in power line cycles
SPEED_TO_NPLC: dict[str, float] = {"Fast": 0.1, "Medium": 1.0, "Slow": 10.0}

# Current ranges in A that the Range options use
CURRENT_RANGES: dict[str, float] = {
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

# Range option -> how the current range is selected ('Auto', 'Limited' or 'Fixed') and the range in A
RANGE_OPTIONS: dict[str, tuple[str, float]] = {
    "Auto": ("Auto", 0.0),
    **{f"Limited {label}": ("Limited", value) for label, value in CURRENT_RANGES.items() if value < 1.0},
    **{f"Fixed {label}": ("Fixed", value) for label, value in CURRENT_RANGES.items()},
}

# Highest number of readings the averaging filter takes
MAX_AVERAGE = 100

# Lowest current range in A, the default lower limit of the current auto range
LOWEST_CURRENT_RANGE = 1e-8


class Device(EmptyDevice):
    """Driver for the Keithley 2450 SourceMeter, using the TSP or the SCPI 2400 command set of the instrument.

    The user documentation is in doc/description.md.
    """

    # Values above this are no measurement values but indicate an error
    ERROR_THRESHOLD = 1e20

    # Timeout of the port in s without the time that a measurement takes
    BASE_TIMEOUT = 10.0

    # Duration of a power line cycle in s at 50 Hz, the longer one of the two line frequencies
    POWER_LINE_CYCLE = 0.02

    # Number of integration times that one reading can take: autozero adds a reference and a zero measurement,
    # source readback adds a measurement of the source value
    INTEGRATIONS_PER_READING = 6

    def __init__(self) -> None:
        """Define the returned variables and the port."""
        super().__init__()

        self.shortname = "Keithley 2450"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]
        self.port_properties = {"timeout": self.BASE_TIMEOUT}
        self.port_identifications = ["KEITHLEY INSTRUMENTS,MODEL 2450,"]

        self.gui_parameters: dict[str, Any] = {}

        # Converted in 'configure'
        self.source_function: Function = "VOLT"
        self.route_out: str = "Front"
        self.compliance: float = 100e-6
        self.range_mode: str = "Auto"
        self.range_value: float = 0.0
        self.nplc: float = 0.1
        self.average: int = 1
        self.four_wire: bool = False

        # Set during the run
        self.language: str = ""
        """Command set of the instrument: 'TSP' or 'SCPI2400', empty before 'connect'."""
        self.identification: str = ""
        self.active_source_function: Function | None = None
        """Source function the driver selected last, None while it is unknown."""
        self.active_measure_function: Function | None = None
        """Measure function the driver selected last, None while it is unknown."""
        # The largest integration time and filter count sent since the last reset, and whether a filter was switched
        # on, which set the timeout of the port. The values are the defaults after a reset.
        self.max_nplc: float = 1.0
        self.max_filter_count: int = 10
        self.filter_switched_on: bool = False
        self.is_power_on: bool = False
        self.voltage: float = float("nan")
        self.current: float = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the fields that are shown in the graphical user interface."""
        del parameters
        return {
            "SweepMode": list(SOURCE_FUNCTIONS),
            "RouteOut": ["Front", "Rear"],
            "Speed": list(SPEED_TO_NPLC),
            "Range": list(RANGE_OPTIONS),
            "Average": 1,
            "Compliance": 100e-6,
            "4wire": False,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Take over the parameters that were chosen by the user in the graphical user interface."""
        # A copy, so that a later failed update of the parameters does not reach the driver
        self.gui_parameters = dict(parameters)

    def connect(self) -> None:
        """Find out which command set the instrument uses."""
        # The instrument reports TSP, SCPI or SCPI2400. It is switched with *LANG <name> and a restart.
        language = self.get_language()
        if language not in ("TSP", "SCPI", "SCPI2400"):
            msg = (
                f"The instrument answered '{language}' to *LANG?, expected TSP, SCPI or SCPI2400. Please check the "
                "connection and that the instrument is a Keithley 2450."
            )
            raise ValueError(msg)
        self.language = "SCPI2400" if language == "SCPI" else language

        # The functions the instrument has are unknown until the driver resets it or selects them
        self.active_source_function = None
        self.active_measure_function = None

    def initialize(self) -> None:
        """Identify and reset the instrument and clear its errors."""
        self.identification = self.get_identification()

        self.reset()
        if self.language == "TSP":
            self.clear_default_buffer()
            self.clear_errors()
        else:
            self.preset_status()
            self.clear_errors()
            self.set_beeper(False)

    def deinitialize(self) -> None:
        """Return to 2-wire sensing and the front terminals."""
        if not self.language:
            return

        self.set_four_wire(False)
        self.select_terminals("FRON")

    def configure(self) -> None:
        """Configure averaging, source and measure function, compliance, ranges, speed, sensing and terminals."""
        self.convert_parameters()

        if self.language == "TSP":
            self.make_reading_buffer()

        if self.source_function == "VOLT":
            self.configure_voltage_source()
        else:
            self.configure_current_source()

        # The instrument keeps the filter settings per measure function, so they follow the function selection
        if self.average > 1:
            self.set_filter_count(self.average)
            self.set_averaging_filter(True)
            self.set_filter_type("REP")
        else:
            self.set_filter_count(1)
            self.set_averaging_filter(False)

        self.set_nplc(self.nplc)
        self.set_four_wire(self.four_wire)
        self.select_terminals("REAR" if self.route_out == "Rear" else "FRON")

    def poweron(self) -> None:
        """Switch on the output."""
        self.set_output(True)
        self.is_power_on = True

    def poweroff(self) -> None:
        """Switch off the output."""
        if self.language:
            self.set_output(False)
        self.is_power_on = False

    def apply(self) -> None:
        """Set the new source level."""
        if self.source_function == "VOLT":
            self.set_voltage(float(self.value))
        else:
            self.set_current(float(self.value))

        # A measurement is needed so that the instrument outputs the new level
        self.measure()
        self.call()

    # check_driver: ignore DC014 - the measurement is started here and read in 'call', so that all instruments of the
    # branch measure at the same time; get_voltage_and_current sends the same commands for scripts
    def measure(self) -> None:
        """Start the measurement."""
        if self.language == "TSP":
            # Refuse unknown or equal functions before the measurement starts, not only when the answer is parsed
            self.tsp_source_function()
            self.port.write("data.clear()")
            self.port.write("smu.measure.read(data)")
        else:
            self.port.write("READ?")

    # check_driver: ignore DC014 - reads the measurement that was started in 'measure'
    def call(self) -> list[float]:
        """Return the measured voltage in V and current in A."""
        if self.language == "TSP":
            self.port.write("printbuffer(1, 1, data.readings, data.sourcevalues)")
        self.voltage, self.current = self.parse_measurement(self.port.read())
        return [self.voltage, self.current]

    # Functions that are used by the semantic functions start here

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
        if range_option not in RANGE_OPTIONS:
            msg = f"Range '{range_option}' is not supported. Use 'Auto', 'Limited <range>' or 'Fixed <range>'."
            raise ValueError(msg)
        self.range_mode, self.range_value = RANGE_OPTIONS[range_option]

        try:
            self.compliance = float(parameters.get("Compliance", 100e-6))
            average = float(parameters.get("Average", 1))
        except (TypeError, ValueError):
            msg = "Compliance and Average must be numbers."
            raise ValueError(msg) from None

        if not math.isfinite(self.compliance) or self.compliance <= 0:
            msg = f"Compliance must be a finite number larger than 0, not {self.compliance}."
            raise ValueError(msg)

        if not 1 <= average <= MAX_AVERAGE or average != int(average):
            msg = f"Average must be a whole number from 1 to {MAX_AVERAGE}, not {average}."
            raise ValueError(msg)
        self.average = int(average)

        self.four_wire = bool(parameters.get("4wire", False))

    def configure_voltage_source(self) -> None:
        """Source voltage, measure current, and set the current compliance and range."""
        self.set_source_function("VOLT")
        if self.language == "TSP":
            self.set_measure_function("CURR")
            self.set_source_autorange("VOLT", True)
            self.set_current_limit(self.compliance)
        else:
            self.set_source_mode("VOLT", "FIX")
            self.set_measure_function("CURR")
            self.set_current_limit(self.compliance)

        if self.range_mode == "Auto":
            self.set_measure_autorange("CURR", True)
            # The lower limit of a 'Limited' range in a previous branch must not remain
            self.set_current_measure_autorange_low(LOWEST_CURRENT_RANGE)
        elif self.range_mode == "Limited":
            self.set_measure_autorange("CURR", True)
            self.set_current_measure_autorange_low(self.range_value)
        else:
            self.set_measure_autorange("CURR", False)
            self.set_current_measure_range(self.range_value)

        if self.language == "TSP":
            self.autozero_once()

    def configure_current_source(self) -> None:
        """Source current, measure voltage, and set the voltage compliance and the current source range."""
        self.set_source_function("CURR")
        if self.language == "TSP":
            self.set_measure_function("VOLT")
            self.set_voltage_limit(self.compliance)
            self.autozero_once()
        else:
            self.set_source_mode("CURR", "FIX")
            self.set_measure_function("VOLT")
            self.set_voltage_limit(self.compliance)
            self.set_measure_autorange("VOLT", True)

        # 'Limited' has no lower limit for the source range, it uses auto ranging
        if self.range_mode == "Fixed":
            self.set_source_autorange("CURR", False)
            self.set_current_source_range(self.range_value)
        else:
            self.set_source_autorange("CURR", True)

    def update_port_timeout(self) -> None:
        """Extend the timeout of the port by the time that one measurement can take.

        A reading with 10 power line cycles and 100 averaged readings takes 20 s at 50 Hz, without autozero. The
        instrument keeps NPLC and filter per measure function in TSP and shares the filter in SCPI2400, so the time
        uses the largest NPLC and the largest filter count sent since the last reset, the count only once a filter
        was switched on. The moving average is counted like the repeating one. The timeout can be too long, never
        too short.
        """
        readings = self.max_filter_count if self.filter_switched_on else 1
        measurement_time = self.max_nplc * self.POWER_LINE_CYCLE * readings * self.INTEGRATIONS_PER_READING
        timeout = self.BASE_TIMEOUT + measurement_time

        # Raw sockets, serial ports and the Prologix controller read the timeout in s from the port properties;
        # a VISA resource has a timeout of its own, in ms
        self.port.port_properties["timeout"] = timeout
        if isinstance(self.port.port, pyvisa.resources.Resource):
            self.port.port.timeout = timeout * 1000

    def select_terminals(self, terminals: Terminals) -> None:
        """Switch off the output if it is on, then select the front or the rear terminals."""
        if self.is_power_on:
            self.poweroff()
        self.set_terminals(terminals)

    def parse_measurement(self, answer: str) -> tuple[float, float]:
        """Return voltage in V and current in A from the answer to a measurement; NaN for an invalid reading."""
        try:
            values = [float(value) for value in answer.split(",")]
            if self.language == "TSP":
                # The answer is the reading of the measure function followed by the value of the source function
                reading, source_value = values[0], values[1]
                if self.tsp_source_function() == "VOLT":
                    voltage, current = source_value, reading
                else:
                    voltage, current = reading, source_value
            else:
                # The answer starts with voltage and current, followed by resistance, time and status
                voltage, current = values[0], values[1]
        except (IndexError, ValueError) as exception:
            msg = f"Unexpected answer of the instrument to the measurement: {answer!r}."
            raise ValueError(msg) from exception

        if voltage > self.ERROR_THRESHOLD:
            voltage = float("nan")
            debug("Keithley 2450: Unable to read the voltage.")
        if current > self.ERROR_THRESHOLD:
            current = float("nan")
            debug("Keithley 2450: Unable to read the current.")

        return voltage, current

    def tsp_source_function(self) -> Function:
        """Return the source function of a TSP measurement; it must differ from the measure function.

        The functions are those the driver selected last. Both must be known, else the values could not be
        assigned to voltage and current.
        """
        source_function = self.active_source_function
        if source_function is None or self.active_measure_function is None:
            msg = (
                "The source and measure functions of the instrument are unknown, so voltage and current cannot be "
                "told apart. Select them with set_source_function and set_measure_function, or call reset."
            )
            raise RuntimeError(msg)
        if self.active_measure_function == source_function:
            msg = (
                f"The instrument sources and measures {TSP_QUANTITIES[source_function]}, so voltage and current "
                "cannot be told apart. Select different source and measure functions."
            )
            raise RuntimeError(msg)
        return source_function

    def require_function(self, kind: str, active: Function | None, required: Function, name: str) -> None:
        """In TSP, raise if a command needs another source or measure function than the one the driver selected.

        TSP commands such as smu.source.level act on the present function, so they would set the wrong quantity.
        While the function is unknown, i.e. after connect and before reset or set_<kind>_function, the command is
        refused as well.
        """
        if self.language != "TSP" or active == required:
            return
        present = "an unknown function" if active is None else TSP_QUANTITIES[active]
        msg = (
            f"{name} needs the {kind} function {TSP_QUANTITIES[required]}, but the instrument has {present}. "
            f"Select it first with set_{kind}_function, or call reset."
        )
        raise RuntimeError(msg)

    def require_language(self, language: str, name: str) -> None:
        """Raise if the instrument does not use the command set that a command needs."""
        if self.language != language:
            msg = f"{name} needs the {language} command set, but the instrument uses '{self.language}'."
            raise RuntimeError(msg)

    # Communication commands start here. Each command is sent in the command set of the instrument: TSP or the
    # SCPI of the Keithley 2400 emulation. Commands that exist in one command set only raise in the other.

    @command(returns=("language",), reads="state")
    def get_language(self) -> str:
        """Return the command set of the instrument: TSP, SCPI or SCPI2400."""
        return str(self.port.query("*LANG?")).strip()

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        return str(self.port.query("*IDN?"))

    @command
    def reset(self) -> None:
        """Reset the instrument to its default settings."""
        if self.language == "TSP":
            self.port.write("smu.reset()")
        else:
            self.port.write("*rst")
        # After a reset, the instrument sources voltage and measures current, with 1 NPLC and the filter off
        self.active_source_function = "VOLT"
        self.active_measure_function = "CURR"
        self.max_nplc = 1.0
        self.max_filter_count = 10
        self.filter_switched_on = False
        self.update_port_timeout()

    @command
    def preset_status(self) -> None:
        """Set the status registers to their preset values. SCPI only."""
        self.require_language("SCPI2400", "preset_status")
        self.port.write("status:preset")

    @command
    def clear_errors(self) -> None:
        """Clear the error queue; in SCPI also the status registers."""
        if self.language == "TSP":
            self.port.write("errorqueue.clear()")
        else:
            self.port.write("*cls")

    @command
    def clear_default_buffer(self) -> None:
        """Remove all readings from the default reading buffer. TSP only."""
        self.require_language("TSP", "clear_default_buffer")
        self.port.write("defbuffer1.clear()")

    @command
    def set_beeper(self, beeper: bool) -> None:
        """Switch the beeper on or off. SCPI only."""
        self.require_language("SCPI2400", "set_beeper")
        self.port.write(f":SYST:BEEP:STAT {'ON' if beeper else 'OFF'}")

    @command
    def set_filter_count(self, filter_count: Annotated[int, Range(1, 100)]) -> None:
        """Set the number of readings that are averaged by the filter."""
        if self.language == "TSP":
            self.port.write(f"smu.measure.filter.count = {filter_count:d}")
        else:
            self.port.write(f":SENS:AVER:COUN {filter_count:d}")
        self.max_filter_count = max(self.max_filter_count, filter_count)
        self.update_port_timeout()

    @command
    def set_averaging_filter(self, averaging_filter: bool) -> None:
        """Switch the averaging filter on or off."""
        if self.language == "TSP":
            self.port.write(f"smu.measure.filter.enable = smu.{'ON' if averaging_filter else 'OFF'}")
        else:
            self.port.write(f":SENS:AVER:STAT {'ON' if averaging_filter else 'OFF'}")
        self.filter_switched_on = self.filter_switched_on or averaging_filter
        self.update_port_timeout()

    @command
    def set_filter_type(self, filter_type: FilterType) -> None:
        """Select the repeating or the moving average as averaging filter."""
        if self.language == "TSP":
            self.port.write(f"smu.measure.filter.type = smu.{TSP_FILTER_TYPES[filter_type]}")
        else:
            self.port.write(f":SENS:AVER:TCON {filter_type}")

    @command
    def make_reading_buffer(self) -> None:
        """Create the reading buffer 'data' with 10 readings that the measurements use. TSP only."""
        self.require_language("TSP", "make_reading_buffer")
        self.port.write("data = buffer.make(10)")

    @command
    def set_source_function(self, source_function: Function) -> None:
        """Set the source function to voltage or current."""
        if self.language == "TSP":
            self.port.write(f"smu.source.func = smu.{TSP_FUNCTIONS[source_function]}")
        else:
            self.port.write(f":SOUR:FUNC {source_function}")
        self.active_source_function = source_function

    @command
    def set_source_mode(self, source: Source, source_mode: SourceMode) -> None:
        """Set the source mode of the voltage or current source: fixed level, list or sweep. SCPI only."""
        self.require_language("SCPI2400", "set_source_mode")
        self.port.write(f":SOUR:{source}:MODE {source_mode}")

    @command
    def set_measure_function(self, measure_function: Function) -> None:
        """Set the measure function to voltage or current; in TSP also its unit to volts or amperes."""
        if self.language == "TSP":
            self.port.write(f"smu.measure.func = smu.{TSP_FUNCTIONS[measure_function]}")
            # The instrument keeps a unit per function, which could also be ohms or watts
            self.port.write(f"smu.measure.unit = smu.{TSP_UNITS[measure_function]}")
        else:
            self.port.write(f':SENS:FUNC "{measure_function}"')
        self.active_measure_function = measure_function

    @command
    def set_current_limit(self, current_limit: Amperes) -> None:
        """Set the current limit in A that is used while voltage is sourced."""
        if self.language == "TSP":
            self.port.write(f"smu.source.ilimit.level = {current_limit}")
        else:
            self.port.write(f":SENS:CURR:PROT {current_limit}")

    @command
    def set_voltage_limit(self, voltage_limit: Volts) -> None:
        """Set the voltage limit in V that is used while current is sourced."""
        if self.language == "TSP":
            self.port.write(f"smu.source.vlimit.level = {voltage_limit}")
        else:
            self.port.write(f":SENS:VOLT:PROT {voltage_limit}")

    @command
    def set_source_autorange(self, source: Source, source_autorange: bool) -> None:
        """Switch the auto range of the voltage or current source on or off.

        In TSP, the command applies to the present source function, which must be the one named.
        """
        self.require_function("source", self.active_source_function, source, "set_source_autorange")
        if self.language == "TSP":
            self.port.write(f"smu.source.autorange = smu.{'ON' if source_autorange else 'OFF'}")
        else:
            self.port.write(f":SOUR:{source}:RANG:AUTO {'ON' if source_autorange else 'OFF'}")

    @command
    def set_current_source_range(self, current_source_range: Amperes) -> None:
        """Set a fixed current source range in A. In TSP, current must be the source function."""
        self.require_function("source", self.active_source_function, "CURR", "set_current_source_range")
        if self.language == "TSP":
            self.port.write(f"smu.source.range = {current_source_range}")
        else:
            self.port.write(f":SOUR:CURR:RANG {current_source_range}")

    @command
    def set_measure_autorange(self, measure: Measure, measure_autorange: bool) -> None:
        """Switch the auto range of the voltage or current measurement on or off.

        In TSP, the command applies to the present measure function, which must be the one named.
        """
        self.require_function("measure", self.active_measure_function, measure, "set_measure_autorange")
        if self.language == "TSP":
            self.port.write(f"smu.measure.autorange = smu.{'ON' if measure_autorange else 'OFF'}")
        else:
            self.port.write(f":SENS:{measure}:RANG:AUTO {'ON' if measure_autorange else 'OFF'}")

    @command
    def set_current_measure_autorange_low(self, current_measure_autorange_low: Amperes) -> None:
        """Set the lowest range in A that the current auto range may use. In TSP, current must be measured."""
        self.require_function("measure", self.active_measure_function, "CURR", "set_current_measure_autorange_low")
        if self.language == "TSP":
            self.port.write(f"smu.measure.autorangelow = {current_measure_autorange_low}")
        else:
            self.port.write(f"SENSe:CURRent:RANGe:AUTO:LLIMit {current_measure_autorange_low}")

    @command
    def set_current_measure_range(self, current_measure_range: Amperes) -> None:
        """Set a fixed current measurement range in A. In TSP, current must be the measure function."""
        self.require_function("measure", self.active_measure_function, "CURR", "set_current_measure_range")
        if self.language == "TSP":
            self.port.write(f"smu.measure.range = {current_measure_range}")
        else:
            self.port.write(f":SENS:CURR:RANG {current_measure_range}")

    @command
    def autozero_once(self) -> None:
        """Refresh the reference and zero measurements once. TSP only."""
        self.require_language("TSP", "autozero_once")
        self.port.write("smu.measure.autozero.once()")

    @command(composite=True)
    def set_nplc(self, nplc: Annotated[float, Range(0.01, 10.0)]) -> None:
        """Set the integration time of the voltage and the current measurement in power line cycles."""
        if self.language == "TSP":
            self.port.write(f"smu.measure.nplc = {nplc}")
        else:
            # SCPI sets the integration time of each measure function with a command of its own
            self.port.write(f":SENS:CURR:DC:NPLC {nplc}")
            self.port.write(f":SENS:VOLT:DC:NPLC {nplc}")
        self.max_nplc = max(self.max_nplc, nplc)
        self.update_port_timeout()

    @command
    def set_four_wire(self, four_wire: bool) -> None:
        """Switch between 4-wire (remote) and 2-wire (local) sensing."""
        if self.language == "TSP":
            self.port.write(f"smu.measure.sense = smu.{'SENSE_4WIRE' if four_wire else 'SENSE_2WIRE'}")
        else:
            self.port.write(f":SYST:RSEN {'ON' if four_wire else 'OFF'}")

    @command(warnings="Switches off the output if it is on while the terminals are changed.")
    def set_terminals(self, terminals: Terminals) -> None:
        """Select the front or the rear terminals."""
        if self.language == "TSP":
            self.port.write(f"smu.measure.terminals = smu.{TSP_TERMINALS[terminals]}")
        else:
            self.port.write(f":ROUT:TERM {terminals}")

    @command
    def set_output(self, output: bool) -> None:
        """Switch the output on or off."""
        if self.language == "TSP":
            self.port.write(f"smu.source.output = smu.{'ON' if output else 'OFF'}")
        else:
            self.port.write(f"OUTP {'ON' if output else 'OFF'}")

    @command
    def set_output_off_mode(self, output_off_mode: OutputOffMode) -> None:
        """Select the state of the output when it is off: normal, zero, high impedance or guard."""
        if self.language == "TSP":
            self.port.write(f"smu.source.offmode = smu.{TSP_OUTPUT_OFF_MODES[output_off_mode]}")
        else:
            self.port.write(f":OUTP:SMOD {output_off_mode}")

    @command
    def set_voltage(self, voltage: Volts) -> None:
        """Set the output voltage in V. In TSP, voltage must be the source function."""
        self.require_function("source", self.active_source_function, "VOLT", "set_voltage")
        if self.language == "TSP":
            self.port.write(f"smu.source.level = {voltage}")
        else:
            self.port.write(f":SOUR:VOLT:LEV {voltage}")

    @command
    def set_current(self, current: Amperes) -> None:
        """Set the output current in A. In TSP, current must be the source function."""
        self.require_function("source", self.active_source_function, "CURR", "set_current")
        if self.language == "TSP":
            self.port.write(f"smu.source.level = {current}")
        else:
            self.port.write(f":SOUR:CURR:LEV {current}")

    @command(composite=True, returns=("voltage", "current"))
    def get_voltage_and_current(self) -> tuple[Volts, Amperes]:
        """Measure voltage in V and current in A. TSP needs the reading buffer of make_reading_buffer."""
        if self.language == "TSP":
            # Unknown or equal functions are refused before the measurement starts
            self.tsp_source_function()
            # TSP stores the reading in a buffer and prints it with a second command, SCPI answers READ? directly
            self.port.write("data.clear()")
            self.port.write("smu.measure.read(data)")
            answer = self.port.query("printbuffer(1, 1, data.readings, data.sourcevalues)")
        else:
            answer = self.port.query("READ?")
        return self.parse_measurement(str(answer))
