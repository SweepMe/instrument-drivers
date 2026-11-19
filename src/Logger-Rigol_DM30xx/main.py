# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2021-2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Logger
# * Instrument: Rigol DM3058, DM3058E

from __future__ import annotations

import math
import re
from typing import Annotated, Any, Literal

from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# The commands follow the RIGOL command set of the DM3058/DM3058E Programming Guide (Nov. 2021); page numbers in the
# comments refer to its PDF pages.

# The measurement functions by the names the manual gives them (:FUNCtion? answers, p41-45)
Function = Literal["DCV", "ACV", "DCI", "ACI", "2WR", "4WR", "FREQ", "PERI", "CONT", "DIODE", "CAP"]
# The functions that have a range (:MEASure:<function> <range>, p59-75); FREQ and PERI: the input voltage range
RangeFunction = Literal["DCV", "ACV", "DCI", "ACI", "2WR", "4WR", "FREQ", "PERI", "CAP"]
# The functions that have a rate (:RATE:<function>, p76-81)
RateFunction = Literal["DCV", "ACV", "DCI", "ACI", "2WR", "4WR"]
# The ranges of all functions; each function accepts its own (RANGES)
MeasurementRange = Literal[
    "200 mV", "2 V", "20 V", "200 V", "1000 V", "750 V",
    "200 uA", "2 mA", "20 mA", "200 mA", "2 A", "10 A",
    "200 Ohm", "2 kOhm", "20 kOhm", "200 kOhm", "1 MOhm", "10 MOhm", "100 MOhm",
    "2 nF", "20 nF", "200 nF", "2 uF", "200 uF", "10000 uF",
]  # fmt: skip
Rate = Literal["Fast", "Medium", "Slow"]
InputImpedance = Literal["10 MOhm", ">10 GOhm"]
MathFunction = Literal["NONE", "REL", "DB", "DBM", "MIN", "MAX", "AVERAGE", "TOTAL", "PF"]
TriggerSource = Literal["AUTO", "SINGLE", "EXT"]
ExternalTriggerSlope = Literal["RISE", "FALL", "HIGH", "LOW"]
HoldSensitivity = Literal["0.01 %", "0.1 %", "1 %", "10 %"]
CommandSet = Literal["RIGOL", "AGILENT", "FLUKE"]

Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]
Ohms = Annotated[float, Unit("Ohm")]
Hertz = Annotated[float, Unit("Hz")]
Seconds = Annotated[float, Unit("s")]
Farads = Annotated[float, Unit("F")]
Decibels = Annotated[float, Unit("dB")]
DecibelMilliwatts = Annotated[float, Unit("dBm")]
Milliseconds = Annotated[int, Unit("ms")]

# Function -> the node of its commands
NODES: dict[str, str] = {
    "DCV": "VOLTage:DC",
    "ACV": "VOLTage:AC",
    "DCI": "CURRent:DC",
    "ACI": "CURRent:AC",
    "2WR": "RESistance",
    "4WR": "FRESistance",
    "FREQ": "FREQuency",
    "PERI": "PERiod",
    "CONT": "CONTinuity",
    "DIODE": "DIODe",
    "CAP": "CAPacitance",
}
# What :FUNCtion? answers -> the function; the manual names both the short and the long answers (p42)
FUNCTION_ANSWERS: dict[str, str] = {
    **{name: name for name in NODES},
    "RESISTANCE": "2WR",
    "FRESISTANCE": "4WR",
    "FREQUENCY": "FREQ",
    "PERIOD": "PERI",
    "CONTINUITY": "CONT",
    "CAPACITANCE": "CAP",
}
_VOLTAGE_RANGES = ["200 mV", "2 V", "20 V", "200 V"]
# Per function its ranges in the order of the range codes 0, 1, 2, ... (p59-75)
RANGES: dict[str, list[str]] = {
    "DCV": [*_VOLTAGE_RANGES, "1000 V"],
    "ACV": [*_VOLTAGE_RANGES, "750 V"],
    "DCI": ["200 uA", "2 mA", "20 mA", "200 mA", "2 A", "10 A"],
    "ACI": ["20 mA", "200 mA", "2 A", "10 A"],
    "2WR": ["200 Ohm", "2 kOhm", "20 kOhm", "200 kOhm", "1 MOhm", "10 MOhm", "100 MOhm"],
    "4WR": ["200 Ohm", "2 kOhm", "20 kOhm", "200 kOhm", "1 MOhm", "10 MOhm", "100 MOhm"],
    "FREQ": [*_VOLTAGE_RANGES, "750 V"],
    "PERI": [*_VOLTAGE_RANGES, "750 V"],
    "CAP": ["2 nF", "20 nF", "200 nF", "2 uF", "200 uF", "10000 uF"],
}
RATES: dict[str, str] = {"Fast": "F", "Medium": "M", "Slow": "S"}
RATES_FUNCTIONS: tuple[str, ...] = ("DCV", "ACV", "DCI", "ACI", "2WR", "4WR")
INPUT_IMPEDANCES: dict[str, str] = {"10 MOhm": "10M", ">10 GOhm": "10G"}
HOLD_SENSITIVITIES: list[str] = ["0.01 %", "0.1 %", "1 %", "10 %"]

# The modes of the GUI -> function, and the unit of their value; sequences saved before 2026 say "Periode"
MODES: dict[str, str] = {
    "Voltage DC": "DCV",
    "Voltage AC": "ACV",
    "Current DC": "DCI",
    "Current AC": "ACI",
    "Resistance": "2WR",
    "4W Resistance": "4WR",
    "Capacitance": "CAP",
    "Diode": "DIODE",
    "Continuity": "CONT",
    "Period": "PERI",
    "Frequency": "FREQ",
}
UNITS: dict[str, str] = {
    "DCV": "V",
    "ACV": "V",
    "DCI": "A",
    "ACI": "A",
    "2WR": "Ohm",
    "4WR": "Ohm",
    "CAP": "F",
    "DIODE": "V",
    "CONT": "Ohm",
    "PERI": "s",
    "FREQ": "Hz",
}
AUTO_RANGE = "Auto"
# What a reading of an overloaded input is (9.000000E+15 on the bench, an open resistance input; not in the manual)
OVERLOAD = 9e15
NUMBER = re.compile(r"[-+]?(\d+\.?\d*|\.\d+)([eE][-+]?\d+)?")


def _is_on(answer: str) -> bool:
    """Whether an on/off answer says on: the instrument answers ON or OFF, 1 or 0."""
    return answer.strip().upper() in ("ON", "1")


def _on_off(on: bool) -> str:
    """The instrument's spelling of on or off."""
    return "ON" if on else "OFF"


class Device(EmptyDevice):
    """Driver for the Rigol DM3058 and DM3058E 5 1/2 digit digital multimeters (RIGOL command set)."""

    def __init__(self) -> None:
        """Define the port and the default selections."""
        super().__init__()

        self.shortname = "DM30xx"

        self.port_manager = True
        self.port_types = ["GPIB", "USB", "COM", "TCPIP"]
        self.port_properties = {
            "timeout": 4.0,
            "EOLwrite": "\r\n",  # for COM port
            "EOLread": "\n",  # for COM port
            "baudrate": 9600,
            "bytesize": 8,
            "parity": "N",
            "Exception": True,
            "delay": 0.05,
        }

        self.variables = ["Voltage DC"]
        self.units = ["V"]
        self.plottype = [True]
        self.savetype = [True]

        self.port_string: str = ""
        self.function: str = "DCV"
        self.rate: str = "Slow"
        self.measurement_range: str = AUTO_RANGE
        self.reading: float = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI fields: the range and the rate only where the chosen mode has them."""
        function = MODES.get(self._mode_of(parameters), "DCV")
        new_parameters: dict[str, Any] = {"Mode": list(MODES)}
        if function in RANGES:
            new_parameters["Range"] = [AUTO_RANGE, *RANGES[function]]
        if function in RATES_FUNCTIONS:
            new_parameters["Rate"] = list(RATES)
        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selections; the returned variable is named after the mode."""
        mode = self._mode_of(parameters)
        self.function = MODES.get(mode, "DCV")
        self.rate = str(parameters.get("Rate", "Slow"))
        self.measurement_range = str(parameters.get("Range", AUTO_RANGE))
        self.port_string = str(parameters.get("Port", ""))
        self.variables = [mode if mode in MODES else "Voltage DC"]
        self.units = [UNITS[self.function]]
        self.plottype = [True]
        self.savetype = [True]

    @staticmethod
    def _mode_of(parameters: dict[str, Any]) -> str:
        """The mode of the GUI; sequences saved with the former spelling "Periode" mean "Period"."""
        mode = str(parameters.get("Mode", "Voltage DC"))
        return "Period" if mode == "Periode" else mode

    def initialize(self) -> None:
        """Make sure the RIGOL command set is active and clear the status."""
        if self.measurement_range != AUTO_RANGE and self.measurement_range not in RANGES.get(self.function, []):
            msg = f"The range {self.measurement_range} does not fit the mode {self.variables[0]}."
            raise ValueError(msg)
        # Over RS-232 the command set query is not answered (bench finding of the former driver)
        if not self.port_string.startswith("COM") and self.get_command_set() != "RIGOL":
            self.set_command_set("RIGOL")
        self.clear()

    def configure(self) -> None:
        """Select the function, its rate and its range."""
        if self.get_function() != self.function:
            self.set_function(self.function)
        if self.function in RATES_FUNCTIONS:
            self.set_rate(self.function, self.rate)
        if self.function in RANGES:
            if self.measurement_range == AUTO_RANGE:
                self.set_autorange(True)
            else:
                self.set_range(self.function, self.measurement_range)

    def measure(self) -> None:
        """Take one reading of the selected function."""
        self.reading = self.get_reading(self.function)

    def call(self) -> list[float]:
        """Return the reading."""
        return [self.reading]

    # --- Function, range, rate ------------------------------------------------------------------------------------

    @command
    def set_function(self, measurement_function: Function) -> None:
        """Select the measurement function."""
        self.port.write(f":FUNCtion:{NODES[measurement_function]}")

    @command(returns=("measurement_function",), reads="setpoint")
    def get_function(self) -> str:
        """Return the measurement function (DCV, ACV, DCI, ACI, 2WR, 4WR, FREQ, PERI, CONT, DIODE or CAP)."""
        answer = self.port.query(":FUNCtion?").strip().upper()
        return FUNCTION_ANSWERS.get(answer, answer)

    @command
    def set_range(self, function: RangeFunction, measurement_range: MeasurementRange) -> None:
        """Set the range of a function; for DCV, DCI and ACI this also switches autorange off.

        For FREQ and PERI it is the range of the input voltage.
        """
        ranges = RANGES[function]
        if measurement_range not in ranges:
            msg = f"The range of {function} is one of {', '.join(ranges)}, not {measurement_range}."
            raise ValueError(msg)
        self.port.write(f":MEASure:{NODES[function]} {ranges.index(measurement_range)}")

    @command(returns=("measurement_range",), reads="setpoint")
    def get_range(self, function: RangeFunction) -> str:
        """Return the range of a function; the instrument answers it only while the function is selected."""
        code = int(float(self.port.query(f":MEASure:{NODES[function]}:RANGe?")))
        return RANGES[function][code]

    @command
    def set_autorange(self, autorange: bool) -> None:
        """Switch autorange on, or off to keep the present range (:MEASure AUTO or MANU); there is no query."""
        self.port.write(f":MEASure {'AUTO' if autorange else 'MANU'}")

    # check_driver: ignore DC010 - function is a fixed choice qualifying rate and range (guide 7.5), not a quantity
    @command
    def set_rate(self, function: RateFunction, rate: Rate) -> None:
        """Set the reading rate of a function: Fast (123 readings/s), Medium (20/s) or Slow (2.5/s).

        The interval of the AUTO trigger goes back to the rate's default (8, 50 or 400 ms).
        """
        self.port.write(f":RATE:{NODES[function]} {RATES[rate]}")

    @command(returns=("rate",), reads="setpoint")
    def get_rate(self, function: RateFunction) -> str:
        """Return the reading rate of a function; the instrument answers it only while the function is selected."""
        answer = self.port.query(f":RATE:{NODES[function]}?").strip().upper()  # e.g. SLOW (the manual says S)
        return next((name for name, mark in RATES.items() if answer in (mark, name.upper())), answer)

    @command
    def set_input_impedance(self, input_impedance: InputImpedance) -> None:
        """Set the input impedance of DC voltage; >10 GOhm is available on the 200 mV and 2 V ranges only."""
        self.port.write(f":MEASure:VOLTage:DC:IMPEdance {INPUT_IMPEDANCES[input_impedance]}")

    @command(returns=("input_impedance",), reads="setpoint")
    def get_input_impedance(self) -> str:
        """Return the input impedance of DC voltage: 10 MOhm or >10 GOhm."""
        answer = self.port.query(":MEASure:VOLTage:DC:IMPEdance?").strip().upper()
        return {code: name for name, code in INPUT_IMPEDANCES.items()}.get(answer, answer)

    @command
    def set_dc_voltage_filter(self, dc_voltage_filter: bool) -> None:
        """Switch the AC filter of DC voltage on or off."""
        self.port.write(f":MEASure:VOLTage:DC:FILTer {_on_off(dc_voltage_filter)}")

    @command(returns=("dc_voltage_filter",), reads="setpoint")
    def get_dc_voltage_filter(self) -> bool:
        """Return whether the AC filter of DC voltage is on."""
        return _is_on(self.port.query(":MEASure:VOLTage:DC:FILTer?"))

    @command
    def set_dc_current_filter(self, dc_current_filter: bool) -> None:
        """Switch the AC filter of DC current on or off."""
        self.port.write(f":MEASure:CURRent:DC:FILTer {_on_off(dc_current_filter)}")

    @command(returns=("dc_current_filter",), reads="setpoint")
    def get_dc_current_filter(self) -> bool:
        """Return whether the AC filter of DC current is on."""
        return _is_on(self.port.query(":MEASure:CURRent:DC:FILTer?"))

    @command
    def set_continuity_threshold(self, continuity_threshold: Annotated[Ohms, Range(1, 2000)]) -> None:
        """Set the resistance below which continuity beeps; the instrument has no query."""
        self.port.write(f":MEASure:CONTinuity {round(continuity_threshold)}")

    # --- Readings ---------------------------------------------------------------------------------------------------

    @command(returns=("dc_voltage",))
    def get_dc_voltage(self) -> Volts:
        """Measure the DC voltage."""
        return self._query_reading(":MEASure:VOLTage:DC?")

    @command(returns=("ac_voltage",))
    def get_ac_voltage(self) -> Volts:
        """Measure the AC voltage (true RMS)."""
        return self._query_reading(":MEASure:VOLTage:AC?")

    @command(returns=("dc_current",))
    def get_dc_current(self) -> Amperes:
        """Measure the DC current."""
        return self._query_reading(":MEASure:CURRent:DC?")

    @command(returns=("ac_current",))
    def get_ac_current(self) -> Amperes:
        """Measure the AC current (true RMS)."""
        return self._query_reading(":MEASure:CURRent:AC?")

    @command(returns=("resistance",))
    def get_resistance(self) -> Ohms:
        """Measure the resistance with two wires."""
        return self._query_reading(":MEASure:RESistance?")

    @command(returns=("four_wire_resistance",))
    def get_four_wire_resistance(self) -> Ohms:
        """Measure the resistance with four wires."""
        return self._query_reading(":MEASure:FRESistance?")

    @command(returns=("frequency",))
    def get_frequency(self) -> Hertz:
        """Measure the frequency (20 Hz to 1 MHz)."""
        return self._query_reading(":MEASure:FREQuency?")

    @command(returns=("period",))
    def get_period(self) -> Seconds:
        """Measure the period (1 us to 50 ms)."""
        return self._query_reading(":MEASure:PERiod?")

    @command(returns=("capacitance",))
    def get_capacitance(self) -> Farads:
        """Measure the capacitance."""
        return self._query_reading(":MEASure:CAPacitance?")

    @command(returns=("continuity_resistance",))
    def get_continuity_resistance(self) -> Ohms:
        """Measure the resistance of the continuity test."""
        return self._query_reading(":MEASure:CONTinuity?")

    @command(returns=("diode_voltage",))
    def get_diode_voltage(self) -> Volts:
        """Measure the forward voltage of a diode."""
        return self._query_reading(":MEASure:DIODe?")

    @command(composite=True, returns=("reading",))
    def get_reading(self, function: Function) -> float:
        """Measure the given function, in its unit (V, A, Ohm, Hz, s or F)."""
        readers = {
            "DCV": self.get_dc_voltage,
            "ACV": self.get_ac_voltage,
            "DCI": self.get_dc_current,
            "ACI": self.get_ac_current,
            "2WR": self.get_resistance,
            "4WR": self.get_four_wire_resistance,
            "FREQ": self.get_frequency,
            "PERI": self.get_period,
            "CAP": self.get_capacitance,
            "CONT": self.get_continuity_resistance,
            "DIODE": self.get_diode_voltage,
        }
        return readers[function]()

    @command(returns=("new_reading",), reads="state")
    def is_new_reading(self) -> bool:
        """Return whether the meter reports a new reading (:MEASure?); it answered TRUE in every test."""
        return self.port.query(":MEASure?").strip().upper() == "TRUE"

    # --- Math --------------------------------------------------------------------------------------------------------

    @command
    def set_math_function(self, math_function: MathFunction) -> None:
        """Select the math function: NONE, REL (relative), DB, DBM, MIN, MAX, AVERAGE, TOTAL or PF (pass/fail)."""
        self.port.write(f":CALCulate:FUNCtion {math_function}")

    @command(returns=("math_function",), reads="setpoint")
    def get_math_function(self) -> str:
        """Return the math functions that are on, e.g. NONE or REL+PF."""
        return self.port.query(":CALCulate:FUNCtion?").strip().upper()

    @command
    def set_relative_offset(self, relative_offset: float) -> None:
        """Set the offset subtracted from the readings of the present function, in its unit."""
        self.port.write(f":CALCulate:REL:OFFSet {relative_offset}")

    @command(returns=("relative_offset",), reads="setpoint")
    def get_relative_offset(self) -> float:
        """Return the offset subtracted from the readings of the present function, in its unit."""
        return self._query_float(":CALCulate:REL:OFFSet?")

    @command
    def set_relative_state(self, relative_state: bool) -> None:
        """Switch the relative operation (the offset subtracted) on or off."""
        self.port.write(f":CALCulate:REL:STATe {_on_off(relative_state)}")

    @command(returns=("relative_state",), reads="setpoint")
    def get_relative_state(self) -> bool:
        """Return whether the relative operation is on."""
        return _is_on(self.port.query(":CALCulate:REL:STATe?"))

    @command
    def set_statistics_state(self, statistics_state: bool) -> None:
        """Switch the statistics (minimum, maximum, average, count of the readings) on or off."""
        self.port.write(f":CALCulate:STATistic:STATe {_on_off(statistics_state)}")

    @command(returns=("statistics_state",), reads="setpoint")
    def get_statistics_state(self) -> bool:
        """Return whether the statistics are on."""
        return _is_on(self.port.query(":CALCulate:STATistic:STATe?"))

    @command(returns=("minimum",), reads="last")
    def get_minimum(self) -> float:
        """Return the smallest reading of the statistics, in the unit of the function."""
        return self._query_float(":CALCulate:STATistic:MIN?")

    @command(returns=("maximum",), reads="last")
    def get_maximum(self) -> float:
        """Return the largest reading of the statistics, in the unit of the function."""
        return self._query_float(":CALCulate:STATistic:MAX?")

    @command(returns=("average",), reads="last")
    def get_average(self) -> float:
        """Return the average of the readings of the statistics, in the unit of the function."""
        return self._query_float(":CALCulate:STATistic:AVERage?")

    @command(returns=("count",), reads="last")
    def get_count(self) -> int:
        """Return how many readings the statistics hold."""
        return int(self._query_float(":CALCulate:STATistic:COUNt?"))

    @command
    def set_db_reference(self, db_reference: Annotated[DecibelMilliwatts, Range(-120, 120)]) -> None:
        """Set the reference of the dB operation."""
        self.port.write(f":CALCulate:DB:REFErence {db_reference}")

    @command(returns=("db_reference",), reads="setpoint")
    def get_db_reference(self) -> DecibelMilliwatts:
        """Return the reference of the dB operation."""
        return self._query_float(":CALCulate:DB:REFErence?")

    @command
    def set_db_state(self, db_state: bool) -> None:
        """Switch the dB operation on or off."""
        self.port.write(f":CALCulate:DB:STATe {_on_off(db_state)}")

    @command(returns=("db_state",), reads="setpoint")
    def get_db_state(self) -> bool:
        """Return whether the dB operation is on."""
        return _is_on(self.port.query(":CALCulate:DB:STATe?"))

    @command(returns=("db",), reads="last")
    def get_db(self) -> Decibels:
        """Return the last reading of the dB operation."""
        return self._query_float(":CALCulate:DB?")

    @command
    def set_dbm_reference(self, dbm_reference: Annotated[Ohms, Range(2, 8000)]) -> None:
        """Set the reference resistance of the dBm operation."""
        self.port.write(f":CALCulate:DBM:REFErence {dbm_reference}")

    @command(returns=("dbm_reference",), reads="setpoint")
    def get_dbm_reference(self) -> Ohms:
        """Return the reference resistance of the dBm operation."""
        return self._query_float(":CALCulate:DBM:REFErence?")

    @command
    def set_dbm_state(self, dbm_state: bool) -> None:
        """Switch the dBm operation on or off."""
        self.port.write(f":CALCulate:DBM:STATe {_on_off(dbm_state)}")

    @command(returns=("dbm_state",), reads="setpoint")
    def get_dbm_state(self) -> bool:
        """Return whether the dBm operation is on."""
        return _is_on(self.port.query(":CALCulate:DBM:STATe?"))

    @command(returns=("dbm",), reads="last")
    def get_dbm(self) -> DecibelMilliwatts:
        """Return the last reading of the dBm operation."""
        return self._query_float(":CALCulate:DBM?")

    @command
    def set_lower_limit(self, lower_limit: float) -> None:
        """Set the lower limit of the pass/fail test, in the unit of the function."""
        self.port.write(f":CALCulate:PF:LOWEr {lower_limit}")

    @command(returns=("lower_limit",), reads="setpoint")
    def get_lower_limit(self) -> float:
        """Return the lower limit of the pass/fail test."""
        return self._query_float(":CALCulate:PF:LOWEr?")

    @command
    def set_upper_limit(self, upper_limit: float) -> None:
        """Set the upper limit of the pass/fail test, in the unit of the function."""
        self.port.write(f":CALCulate:PF:UPPEr {upper_limit}")

    @command(returns=("upper_limit",), reads="setpoint")
    def get_upper_limit(self) -> float:
        """Return the upper limit of the pass/fail test."""
        return self._query_float(":CALCulate:PF:UPPEr?")

    @command
    def set_limit_state(self, limit_state: bool) -> None:
        """Switch the pass/fail test on or off."""
        self.port.write(f":CALCulate:PF:STATe {_on_off(limit_state)}")

    @command(returns=("limit_state",), reads="setpoint")
    def get_limit_state(self) -> bool:
        """Return whether the pass/fail test is on."""
        return _is_on(self.port.query(":CALCulate:PF:STATe?"))

    @command(returns=("limit_result",), reads="last")
    def get_limit_result(self) -> str:
        """Return the result of the pass/fail test for the last reading: PASS, HI or LO."""
        return self.port.query(":CALCulate:PF?").strip().upper()

    # --- Trigger -----------------------------------------------------------------------------------------------------

    @command
    def set_trigger_source(self, trigger_source: TriggerSource) -> None:
        """Set how readings are triggered: AUTO (continuously), SINGLE (on a trigger) or EXT (external input)."""
        self.port.write(f":TRIGger:SOURce {trigger_source}")

    @command(returns=("trigger_source",), reads="setpoint")
    def get_trigger_source(self) -> str:
        """Return how readings are triggered: AUTO, SINGLE or EXT."""
        return self.port.query(":TRIGger:SOURce?").strip().upper()

    @command
    def set_auto_trigger_interval(self, auto_trigger_interval: Annotated[Milliseconds, Range(8, 2000)]) -> None:
        """Set the time between readings of the AUTO trigger; at least 8 ms (Fast), 50 ms (Medium), 400 ms (Slow)."""
        self.port.write(f":TRIGger:AUTO:INTErval {auto_trigger_interval}")

    @command(returns=("auto_trigger_interval",), reads="setpoint")
    def get_auto_trigger_interval(self) -> Milliseconds:
        """Return the time between readings of the AUTO trigger."""
        return int(self._query_float(":TRIGger:AUTO:INTErval?"))

    @command
    def set_sample_count(self, sample_count: Annotated[int, Range(1, 2000)]) -> None:
        """Set how many readings a SINGLE trigger takes."""
        self.port.write(f":TRIGger:SINGle {sample_count}")

    @command(returns=("sample_count",), reads="setpoint")
    def get_sample_count(self) -> int:
        """Return how many readings a SINGLE trigger takes."""
        return int(self._query_float(":TRIGger:SINGle?"))

    @command
    def trigger_single(self) -> None:
        """Trigger once, as the front panel's Single key does."""
        self.port.write(":TRIGger:SINGle:TRIGgered")

    @command
    def trigger(self) -> None:
        """Send a bus trigger (*TRG) to an instrument waiting for a trigger."""
        self.port.write("*TRG")

    @command
    def set_external_trigger_slope(self, external_trigger_slope: ExternalTriggerSlope) -> None:
        """Set what the external trigger input reacts to: a rising or falling edge, a high or low level."""
        self.port.write(f":TRIGger:EXT {external_trigger_slope}")

    @command(returns=("external_trigger_slope",), reads="setpoint")
    def get_external_trigger_slope(self) -> str:
        """Return what the external trigger input reacts to: RISE, FALL, HIGH or LOW."""
        return self.port.query(":TRIGger:EXT?").strip().upper()

    @command
    def set_reading_hold(self, reading_hold: bool) -> None:
        """Switch the reading hold on or off: a reading is kept until a stable one differs by the hold sensitivity."""
        self.port.write(f":TRIGger:AUTO:HOLD {_on_off(reading_hold)}")

    @command(returns=("reading_hold",), reads="setpoint")
    def get_reading_hold(self) -> bool:
        """Return whether the reading hold is on."""
        return _is_on(self.port.query(":TRIGger:AUTO:HOLD?"))

    @command
    def set_hold_sensitivity(self, hold_sensitivity: HoldSensitivity) -> None:
        """Set the sensitivity of the reading hold."""
        self.port.write(f":TRIGger:AUTO:HOLD:SENSitivity {HOLD_SENSITIVITIES.index(hold_sensitivity)}")

    @command(returns=("hold_sensitivity",), reads="setpoint")
    def get_hold_sensitivity(self) -> str:
        """Return the sensitivity of the reading hold."""
        return HOLD_SENSITIVITIES[int(self._query_float(":TRIGger:AUTO:HOLD:SENSitivity?"))]

    # --- System ------------------------------------------------------------------------------------------------------

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification (*IDN?): manufacturer, model, serial number and firmware version."""
        return self.port.query("*IDN?").strip()

    @command(warnings="Resets every setting of the instrument to its default.")
    def reset(self) -> None:
        """Reset the instrument to its default settings (*RST)."""
        self.port.write("*RST")

    @command
    def clear(self) -> None:
        """Clear the status registers and the error queue (*CLS)."""
        self.port.write("*CLS")

    @command(returns=("error",), reads="state")
    def get_error(self) -> str:
        """Return the oldest error of the error queue and remove it; 0,"No error" when it is empty."""
        return self.port.query(":SYSTem:ERRor?").strip()

    @command(returns=("self_test_passed",), reads="state")
    def run_self_test(self) -> bool:
        """Run the self test (*TST?) and return whether it passed."""
        return self.port.query("*TST?").strip() == "0"

    @command
    def set_command_set(self, command_set: CommandSet) -> None:
        """Select the command set; this driver speaks the RIGOL command set."""
        self.port.write(f"CMDSET {command_set}")

    @command(returns=("command_set",), reads="setpoint")
    def get_command_set(self) -> str:
        """Return the command set: RIGOL, AGILENT or FLUKE."""
        return self.port.query("CMDSET?").strip().upper()

    @command
    def set_beeper_state(self, beeper_state: bool) -> None:
        """Switch the beeper on or off."""
        self.port.write(f":SYSTem:BEEPer:STATe {_on_off(beeper_state)}")

    @command(returns=("beeper_state",), reads="setpoint")
    def get_beeper_state(self) -> bool:
        """Return whether the beeper is on."""
        return _is_on(self.port.query(":SYSTem:BEEPer:STATe?"))

    @command
    def beep(self) -> None:
        """Beep once, if the beeper is on."""
        self.port.write(":SYSTem:BEEPer")

    # --- Helpers ----------------------------------------------------------------------------------------------------

    def _query_float(self, query: str) -> float:
        """Send a query and read its answer as a number; a unit after it is dropped (the interval answers 400ms)."""
        answer = self.port.query(query).strip()
        number = NUMBER.match(answer)
        if number is None:
            msg = f"The DM30xx answered '{answer}' to {query}, which is no number."
            raise ValueError(msg)
        return float(number.group())

    def _query_reading(self, query: str) -> float:
        """Send a measure query and read the reading; an overload is returned as infinity."""
        reading = self._query_float(query)
        return math.copysign(math.inf, reading) if abs(reading) >= OVERLOAD else reading
