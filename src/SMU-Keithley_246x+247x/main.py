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
# * Module: SMU
# * Instrument: Keithley 246x+247x

from __future__ import annotations

import math
import re
from typing import Annotated, Any, ClassVar, Literal

from pysweepme.commands import CommandError, Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer. The text choices use the spelling of the TSP constants.
Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]
Function = Literal["FUNC_DC_VOLTAGE", "FUNC_DC_CURRENT"]
Terminals = Literal["TERMINALS_FRONT", "TERMINALS_REAR"]
FilterType = Literal["FILTER_REPEAT_AVG", "FILTER_MOVING_AVG"]


class Device(EmptyDevice):
    """Driver for the Keithley 2460, 2461 and 2470 source measure units using the TSP command set.

    The user documentation is in doc/description.md.
    """

    # Integration time in power line cycles belonging to each speed option
    SPEED_TO_NPLC: ClassVar[dict[str, float]] = {
        "Fast": 0.1,
        "Medium": 1.0,
        "Slow": 10.0,
    }

    # Current ranges in A of all supported models, in ascending order
    CURRENT_RANGES: ClassVar[dict[str, float]] = {
        "10 nA": 1e-8,
        "100 nA": 1e-7,
        "1 µA": 1e-6,
        "10 µA": 1e-5,
        "100 µA": 1e-4,
        "1 mA": 1e-3,
        "10 mA": 1e-2,
        "100 mA": 1e-1,
        "1 A": 1.0,
        "4 A": 4.0,
        "5 A": 5.0,
        "7 A": 7.0,
    }

    # Lowest and highest current range of each supported model. The 10 A range of the 2461 is left out, it can only
    # be used for pulses.
    MODEL_CURRENT_RANGES: ClassVar[dict[str, tuple[str, str]]] = {
        "2460": ("1 µA", "7 A"),
        "2461": ("1 µA", "7 A"),
        "2470": ("10 nA", "1 A"),
    }

    # Option of the 'TSP-Link node' field that addresses the instrument connected to the port
    LOCAL_NODE = "Local"

    # Highest node number that can be assigned to these instruments in a TSP-Link network
    MAX_TSP_LINK_NODE = 63

    # Readings above this value are returned by the instrument if the measurement is not valid
    OVERFLOW_LIMIT = 1e37

    # Event types of the event log, the sum selects several types
    EVENT_ERROR = 1
    EVENT_WARNING = 2

    # With a fixed measurement range, the source limit must be at least 10 % and at most 105 % of the range.
    # The reference manuals are not consistent about the lower bound: section 4 says "more than 0.1 percent", the
    # description of smu.source.xlimit.level "10.6% or higher", and the specifications of the 2460 and 2461
    # "minimum value is 10 % of range". 10 % is used here. If the instrument changes a limit that has passed this
    # check, the run is stopped by the checks at the end of 'configure'.
    MIN_LIMIT_TO_RANGE = 0.1
    MAX_LIMIT_TO_RANGE = 1.05

    # Timeout of the port in s without the time that a measurement takes
    BASE_TIMEOUT = 10.0

    # Duration of a power line cycle in s at 50 Hz, the longer one of the two line frequencies
    POWER_LINE_CYCLE = 0.02

    # Number of integration times that one reading can take: autozero adds a reference and a zero measurement,
    # source readback adds a measurement of the source value
    INTEGRATIONS_PER_READING = 6

    # Number of events that are read from the event log at once
    MAX_EVENTS_READ = 10

    def __init__(self) -> None:
        """Initialize the driver, the returned variables and the port configuration."""
        super().__init__()

        self.shortname = "Keithley 246x/247x"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]
        self.port_properties = {"timeout": self.BASE_TIMEOUT}
        self.port_identifications = [
            "KEITHLEY INSTRUMENTS,MODEL 2460",
            "KEITHLEY INSTRUMENTS,MODEL 2461",
            "KEITHLEY INSTRUMENTS,MODEL 2470",
        ]

        # Set in apply_gui_parameters
        self.gui_parameters: dict[str, Any] = {}
        """Parameters as received from the graphical user interface, never converted in place."""
        self.sweep_mode: str = "Voltage in V"
        self.route_out: str = "Front"
        self.speed: str = "Fast"
        self.range_option: str = "Auto"
        self.four_wire: bool = False
        self.tsp_link_node: str = self.LOCAL_NODE
        self.node_number: int | None = None
        """TSP-Link node number of the instrument, None if the instrument connected to the port is used."""
        self.node_prefix: str = ""
        """Prefix such as 'node[3].' for commands to a remote TSP-Link node, empty for the local node."""

        # Converted from the parameters in convert_parameters
        self.compliance: float = 100e-6
        self.average: int = 1
        self.nplc: float = 0.1
        self.range_mode: str = "Auto"
        """How the current range is selected: 'Auto', 'Limited' or 'Fixed'."""
        self.range_value: float = 0.0
        """Current range in A that belongs to a 'Limited' or 'Fixed' range option."""

        # Set during the run
        self.model: str = ""
        self.voltage: float = float("nan")
        self.current: float = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the fields that are shown in the graphical user interface."""
        del parameters
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Front", "Rear"],
            "Speed": list(self.SPEED_TO_NPLC.keys()),
            "Range": self.get_range_options(),
            "Average": 1,
            "Compliance": 100e-6,
            "4wire": False,
            "TSP-Link node": self.get_node_options(),
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Take over the parameters that were chosen by the user in the graphical user interface."""
        self.gui_parameters = parameters

        self.sweep_mode = parameters.get("SweepMode", "Voltage in V")
        self.route_out = parameters.get("RouteOut", "Front")
        self.speed = parameters.get("Speed", "Fast")
        self.range_option = parameters.get("Range", "Auto")
        self.four_wire = bool(parameters.get("4wire", False))

        self.tsp_link_node = str(parameters.get("TSP-Link node", self.LOCAL_NODE))
        try:
            self.node_number = self.get_node_number(self.tsp_link_node)
        except ValueError:
            # This function is also called with incomplete parameters, the option is checked again in 'initialize'
            self.node_number = None
        self.node_prefix = "" if self.node_number is None else f"node[{self.node_number}]."

        if self.node_number is None:
            self.shortname = "Keithley 246x/247x"
        else:
            self.shortname = f"Keithley 246x/247x Node {self.node_number}"

    def initialize(self) -> None:
        """Check the parameters, the command set, the TSP-Link node and the model, and reset the instrument."""
        self.model = ""
        self.convert_parameters()

        language = self.get_language()
        if language != "TSP":
            msg = (
                f"The instrument uses the command set '{language}', but this driver needs the TSP command set. "
                "Please select TSP on the front panel (MENU > System > Settings > Command Set) or send '*LANG TSP', "
                "and restart the instrument."
            )
            raise ValueError(msg)

        # Both settings are off after power-on. If another program has switched them on for this interface, the
        # instrument writes events and prompts into its answers, which the driver cannot read then.
        self.set_shown_events(0)
        self.set_prompts(False)

        if self.node_number is not None:
            self.check_tsp_link()

        # The event log is cleared first, so that an event caused by the reset shows that the instrument cannot
        # be reached
        self.clear_event_log()
        self.reset()
        try:
            self.check_events("resetting the instrument")
        except CommandError as error:
            if self.node_number is None:
                raise
            msg = (
                f"TSP-Link node {self.node_number} cannot be used. {error} Please check that an instrument with "
                "this node number is part of the TSP-Link network and that the network was initialized after the "
                "last power cycle of any of the linked instruments."
            )
            raise ValueError(msg) from error

        self.model = self.get_model()
        self.check_model()

    def deinitialize(self) -> None:
        """Return to 2-wire sensing, so that the instrument is not left with open sense terminals."""
        if self.model:
            # Only if the instrument was reached and identified in 'initialize'
            self.set_four_wire(False)

    def configure(self) -> None:
        """Configure source and measure function, ranges, limit, integration time, sensing, terminals and filter."""
        self.convert_parameters()
        self.update_port_timeout()

        if self.sweep_mode.startswith("Voltage"):
            self.configure_voltage_source()
        else:
            self.configure_current_source()

        self.set_nplc(self.nplc)
        self.set_four_wire(self.four_wire)
        self.set_terminals("TERMINALS_REAR" if self.route_out == "Rear" else "TERMINALS_FRONT")
        self.configure_averaging()

        # The events are read first, so that the message of the instrument is shown if it has rejected a setting
        self.check_events("configuring the instrument")
        self.check_limit()

    def poweron(self) -> None:
        """Switch on the output."""
        self.set_output(True)
        self.check_events("switching on the output")

    def poweroff(self) -> None:
        """Switch off the output."""
        self.set_output(False)

    def apply(self) -> None:
        """Set the new source level."""
        self.set_source_level(float(self.value))

    def measure(self) -> None:
        """Measure voltage and current.

        The measurement is requested and read in the same phase, so that the answers of several instruments that
        share one port cannot be mixed up.
        """
        self.voltage, self.current = self.get_voltage_and_current()

    def call(self) -> list[float]:
        """Return the measured voltage in V and current in A."""
        return [self.voltage, self.current]

    # Functions that are used by the semantic functions start here

    def get_range_options(self) -> list[str]:
        """Return the current range options that are shown in the graphical user interface.

        "Limited" uses auto ranging with a lowest allowed range, "Fixed" uses a fixed range. The highest range cannot
        be used as lower limit of the auto ranging.
        """
        ranges = list(self.CURRENT_RANGES.keys())
        limited = [f"Limited {value}" for value in ranges[:-1]]
        fixed = [f"Fixed {value}" for value in ranges]

        return ["Auto", *limited, *fixed]

    def get_node_options(self) -> list[str]:
        """Return the TSP-Link node options that are shown in the graphical user interface."""
        return [self.LOCAL_NODE, *[f"Node {number}" for number in range(1, self.MAX_TSP_LINK_NODE + 1)]]

    def get_node_number(self, node_option: str) -> int | None:
        """Convert a node option such as 'Node 3' into the node number, or None for the local node.

        An empty option is treated as the local node. Any other option that is neither 'Local' nor a node number
        from 1 to MAX_TSP_LINK_NODE raises a ValueError, so that no other instrument than the intended one is used.
        """
        option = node_option.strip()
        if option == "" or option.lower() == self.LOCAL_NODE.lower():
            return None

        match = re.fullmatch(r"node\s*(\d+)", option, re.IGNORECASE)
        if match and 1 <= int(match.group(1)) <= self.MAX_TSP_LINK_NODE:
            return int(match.group(1))

        msg = (
            f"'{node_option}' is not a valid option for 'TSP-Link node'. "
            f"Use '{self.LOCAL_NODE}' or 'Node 1' to 'Node {self.MAX_TSP_LINK_NODE}'."
        )
        raise ValueError(msg)

    def convert_parameters(self) -> None:
        """Convert the parameters of the graphical user interface and stop the run if one of them is not valid.

        The converted values are written to attributes of their own, so that applying the parameters again cannot
        overwrite them.
        """
        self.get_node_number(self.tsp_link_node)

        if not self.sweep_mode.startswith(("Voltage", "Current")):
            msg = f"'{self.sweep_mode}' is not a valid SweepMode. Use 'Voltage in V' or 'Current in A'."
            raise ValueError(msg)

        if self.route_out not in ("Front", "Rear"):
            msg = f"'{self.route_out}' is not a valid option for RouteOut. Use 'Front' or 'Rear'."
            raise ValueError(msg)

        if self.speed not in self.SPEED_TO_NPLC:
            msg = f"'{self.speed}' is not a valid option for Speed. Use one of {list(self.SPEED_TO_NPLC)}."
            raise ValueError(msg)
        self.nplc = self.SPEED_TO_NPLC[self.speed]

        try:
            self.compliance = float(self.gui_parameters.get("Compliance", 100e-6))
            self.average = int(self.gui_parameters.get("Average", 1))
        except (TypeError, ValueError) as error:
            msg = "Compliance must be a number and Average must be an integer."
            raise ValueError(msg) from error

        if not self.compliance > 0:
            unit = "A" if self.sweep_mode.startswith("Voltage") else "V"
            msg = f"Compliance must be a positive value in {unit}, but is {self.compliance}."
            raise ValueError(msg)

        max_average = 100
        if not 1 <= self.average <= max_average:
            msg = f"Average must be between 1 and {max_average}, but is {self.average}."
            raise ValueError(msg)

        self.range_mode, self.range_value = self.convert_range_option(self.range_option)

        if self.range_mode == "Fixed" and self.sweep_mode.startswith("Voltage"):
            # The instrument changes a limit below 10 % of a fixed measurement range by itself and cannot reach a
            # limit above 105 % of it
            lowest = self.MIN_LIMIT_TO_RANGE * self.range_value
            highest = self.MAX_LIMIT_TO_RANGE * self.range_value
            tolerance = 1e-9  # the bounds themselves are allowed, whatever the rounding of the product
            if self.compliance < lowest * (1 - tolerance) or self.compliance > highest * (1 + tolerance):
                msg = (
                    f"Compliance {self.compliance:g} A cannot be used with the range '{self.range_option}'. With a "
                    f"fixed range it must be between {lowest:g} A (10 % of the range) and {highest:g} A (105 % of "
                    "the range). Please change the compliance or the range, or use an 'Auto' or 'Limited' range."
                )
                raise ValueError(msg)

    def convert_range_option(self, range_option: str) -> tuple[str, float]:
        """Convert a range option such as 'Limited 1 mA' into the range mode and the current range in A."""
        if range_option == "Auto":
            return "Auto", 0.0

        mode, _, label = range_option.partition(" ")
        if mode in ("Limited", "Fixed") and label in self.CURRENT_RANGES:
            return mode, self.CURRENT_RANGES[label]

        msg = f"'{range_option}' is not a valid option for Range."
        raise ValueError(msg)

    def check_tsp_link(self) -> None:
        """Make sure that the TSP-Link network can be used for an instrument on a remote node.

        The TSP-Link network is not initialized by the driver, so that the configuration used by other software
        is not changed and no output is switched off unexpectedly.
        """
        state = self.get_tsp_link_state()
        if state != "online":
            msg = (
                f"TSP-Link node {self.node_number} cannot be reached because the TSP-Link network is '{state}'. "
                "Please initialize the TSP-Link network on the instrument connected to the port (MENU > System > "
                "Communication > TSP-Link > Initialize, or tsplink.initialize()) and start the run again."
            )
            raise ValueError(msg)

    def check_model(self) -> None:
        """Make sure that the model is supported and that the selected current range exists on it."""
        model = self.model[:4]
        if model not in self.MODEL_CURRENT_RANGES:
            msg = (
                f"The model '{self.model}' is not supported by this driver. "
                f"Supported models are {', '.join(self.MODEL_CURRENT_RANGES)}."
            )
            raise ValueError(msg)

        if self.range_mode == "Auto":
            return

        lowest, highest = (self.CURRENT_RANGES[label] for label in self.MODEL_CURRENT_RANGES[model])
        is_available = lowest <= self.range_value <= highest
        if self.range_mode == "Limited" and self.range_value >= highest:
            # The lower limit of the auto ranging must be below the highest range
            is_available = False

        if not is_available:
            low_label, high_label = self.MODEL_CURRENT_RANGES[model]
            msg = (
                f"The range '{self.range_option}' is not available on the model {model}. Its current ranges go from "
                f"{low_label} to {high_label}, and a 'Limited' range must be below the highest range."
            )
            raise ValueError(msg)

    def check_events(self, action: str) -> None:
        """Read the errors and warnings from the event log and stop the run if there is an error.

        Warnings are reported to the user, as they tell that a setting was changed or not taken over.
        """
        errors = []
        warnings = []
        last_code = 0
        for _ in range(min(self.get_event_count(), self.MAX_EVENTS_READ)):
            code, message, severity, node = self.get_next_event()
            if code == 0:
                break
            text = f"{code}, {message} ({self.get_event_origin(node)})"
            if severity == self.EVENT_ERROR:
                errors.append(text)
                last_code = code
            else:
                warnings.append(text)

        if warnings:
            text = f"{self.shortname}: warning while {action}: {'; '.join(warnings)}"
            self.message_log(text)
            self.message_info(text)

        if errors:
            msg = f"Error while {action}: {'; '.join(errors)}."
            raise CommandError(msg, code=last_code)

    @staticmethod
    def get_event_origin(node: int) -> str:
        """Name the instrument that an event of the event log comes from.

        All linked instruments write into the event log of the instrument connected to the port, so an event can
        belong to another instrument than the one this driver instance controls.
        """
        if node == 0:
            return "reported by the instrument connected to the port"

        return f"reported by TSP-Link node {node}"

    def update_port_timeout(self) -> None:
        """Extend the timeout of the port by the time that one measurement can take.

        A reading with 10 power line cycles and 100 averaged readings takes 20 s at 50 Hz, without autozero and
        source readback. Driver instances that share the port use the longest timeout that one of them needs. The
        value is kept in 'device_communication', which is emptied at the start of each run.
        """
        measurement_time = self.nplc * self.POWER_LINE_CYCLE * self.average * self.INTEGRATIONS_PER_READING
        timeout = self.BASE_TIMEOUT + measurement_time

        key = f"Keithley 246x/247x timeout {self.gui_parameters.get('Port', '')}"
        timeout = max(timeout, self.device_communication.get(key, 0.0))
        self.device_communication[key] = timeout

        # The ports of this driver are VISA resources, whose timeout is given in ms
        self.port.port.timeout = timeout * 1000

    def check_limit(self) -> None:
        """Make sure that the instrument has taken over the compliance.

        The instrument keeps or changes the limit by itself if it does not fit to the selected ranges.
        """
        if self.sweep_mode.startswith("Voltage"):
            limit = self.get_current_limit()
            unit = "A"
        else:
            limit = self.get_voltage_limit()
            unit = "V"

        if not math.isclose(limit, self.compliance, rel_tol=0.01):
            msg = (
                f"The instrument uses a compliance of {limit:g} {unit} instead of the requested {self.compliance:g} "
                f"{unit}. Please check that the compliance fits to the selected range and to the limits of the model."
            )
            raise ValueError(msg)

    def configure_voltage_source(self) -> None:
        """Source voltage and measure current with the selected current measurement range.

        The auto range is switched on before the limit is set, as a fixed measurement range of a previous
        configuration restricts the limit. The range is set afterwards.
        """
        self.set_source_function("FUNC_DC_VOLTAGE")
        self.set_measure_function("FUNC_DC_CURRENT")
        self.set_source_autorange(True)
        self.set_measure_autorange(True)
        self.set_current_limit(self.compliance)

        if self.range_mode == "Limited":
            self.set_measure_autorange_low(self.range_value)
        elif self.range_mode == "Fixed":
            self.set_measure_range(self.range_value)

    def configure_current_source(self) -> None:
        """Source current with the selected current source range and measure voltage with auto ranging.

        The lower limit of a 'Limited' range cannot be applied to the source, so the source uses its auto range.
        """
        self.set_source_function("FUNC_DC_CURRENT")
        self.set_measure_function("FUNC_DC_VOLTAGE")

        if self.range_mode == "Fixed":
            self.set_source_range(self.range_value)
        else:
            self.set_source_autorange(True)

        self.set_measure_autorange(True)
        self.set_voltage_limit(self.compliance)

    def configure_averaging(self) -> None:
        """Switch on the repeating average filter if more than one reading is averaged."""
        if self.average > 1:
            self.set_filter_type("FILTER_REPEAT_AVG")
            self.set_filter_count(self.average)
            self.set_averaging_filter(True)
        else:
            self.set_averaging_filter(False)

    def get_switch_constant(self, state: bool) -> str:
        """Return the TSP constant for on or off of the addressed instrument."""
        return f"{self.node_prefix}smu.{'ON' if state else 'OFF'}"

    # Communication commands start here. The commands address the instrument selected with 'TSP-Link node'.

    @command(returns=("language",), reads="state")
    def get_language(self) -> str:
        """Return the command set of the instrument connected to the port, e.g. TSP or SCPI."""
        return self.port.query("*LANG?").strip()

    @command(returns=("model",), reads="state")
    def get_model(self) -> str:
        """Return the model number of the instrument."""
        node = "localnode" if self.node_number is None else f"node[{self.node_number}]"
        return self.port.query(f"print({node}.model)").strip()

    @command(returns=("tsp_link_state",), reads="state")
    def get_tsp_link_state(self) -> str:
        """Return the state of the TSP-Link network, online or offline."""
        return self.port.query("print(tsplink.state)").strip()

    @command
    def reset(self) -> None:
        """Switch off the output and reset the source and measure settings of the instrument."""
        self.port.write(f"{self.node_prefix}smu.reset()")

    @command
    def clear_event_log(self) -> None:
        """Remove all events from the event log of the instrument connected to the port."""
        self.port.write("eventlog.clear()")

    @command(returns=("event_count",), reads="state")
    def get_event_count(self) -> int:
        """Return the number of unread errors and warnings in the event log."""
        answer = self.port.query(f"print(eventlog.getcount({self.EVENT_ERROR + self.EVENT_WARNING}))")
        return int(float(answer))

    @command(returns=("event_code", "event_message", "event_severity", "event_node"), reads="state")
    def get_next_event(self) -> tuple[int, str, int, int]:
        """Read the oldest unread error or warning: code, message, severity (1 error, 2 warning) and TSP-Link node.

        The node is 0 for an event of the instrument connected to the port.
        """
        answer = self.port.query(f"print(eventlog.next({self.EVENT_ERROR + self.EVENT_WARNING}))")
        # The answer contains event number, message, severity, node and two time values, separated by tabs
        fields = answer.strip().split("\t")
        code = int(float(fields[0]))
        message = fields[1] if len(fields) > 1 else ""
        severity = int(float(fields[2])) if len(fields) > 2 else self.EVENT_ERROR  # noqa: PLR2004
        node = int(float(fields[3])) if len(fields) > 3 else 0  # noqa: PLR2004
        return code, message, severity, node

    @command
    def set_shown_events(self, shown_events: Annotated[int, Range(0, 7)]) -> None:
        """Select the events that the instrument connected to the port writes into its answers: 0 for none.

        The value is the sum of 1 for errors, 2 for warnings and 4 for information.
        """
        self.port.write(f"localnode.showevents = {shown_events:d}")

    @command
    def set_prompts(self, prompts: bool) -> None:
        """Switch the prompts on or off that the instrument connected to the port sends after each command."""
        self.port.write(f"localnode.prompts = localnode.{'ENABLE' if prompts else 'DISABLE'}")

    @command
    def set_source_function(self, source_function: Function) -> None:
        """Set the source function to DC voltage or DC current."""
        self.port.write(f"{self.node_prefix}smu.source.func = {self.node_prefix}smu.{source_function}")

    @command
    def set_measure_function(self, measure_function: Function) -> None:
        """Set the measure function to DC voltage or DC current."""
        self.port.write(f"{self.node_prefix}smu.measure.func = {self.node_prefix}smu.{measure_function}")

    @command
    def set_source_autorange(self, source_autorange: bool) -> None:
        """Switch the auto range of the source on or off."""
        self.port.write(f"{self.node_prefix}smu.source.autorange = {self.get_switch_constant(source_autorange)}")

    @command
    def set_source_range(self, source_range: float) -> None:
        """Set a fixed source range, in V or A depending on the source function. Switches off the auto range."""
        self.port.write(f"{self.node_prefix}smu.source.range = {source_range}")

    @command
    def set_current_limit(self, current_limit: Amperes) -> None:
        """Set the current limit in A that is used while voltage is sourced."""
        self.port.write(f"{self.node_prefix}smu.source.ilimit.level = {current_limit}")

    @command(returns=("current_limit",), reads="setpoint")
    def get_current_limit(self) -> Amperes:
        """Read back the current limit in A that is used while voltage is sourced."""
        return float(self.port.query(f"print({self.node_prefix}smu.source.ilimit.level)"))

    @command
    def set_voltage_limit(self, voltage_limit: Volts) -> None:
        """Set the voltage limit in V that is used while current is sourced."""
        self.port.write(f"{self.node_prefix}smu.source.vlimit.level = {voltage_limit}")

    @command(returns=("voltage_limit",), reads="setpoint")
    def get_voltage_limit(self) -> Volts:
        """Read back the voltage limit in V that is used while current is sourced."""
        return float(self.port.query(f"print({self.node_prefix}smu.source.vlimit.level)"))

    @command
    def set_measure_autorange(self, measure_autorange: bool) -> None:
        """Switch the auto range of the measurement on or off."""
        self.port.write(f"{self.node_prefix}smu.measure.autorange = {self.get_switch_constant(measure_autorange)}")

    @command
    def set_measure_autorange_low(self, measure_autorange_low: float) -> None:
        """Set the lowest range that the auto range of the measurement may use, in V or A."""
        self.port.write(f"{self.node_prefix}smu.measure.autorangelow = {measure_autorange_low}")

    @command
    def set_measure_range(self, measure_range: float) -> None:
        """Set a fixed measurement range, in V or A depending on the measure function. Switches off the auto range."""
        self.port.write(f"{self.node_prefix}smu.measure.range = {measure_range}")

    @command
    def set_nplc(self, nplc: Annotated[float, Range(0.01, 10.0)]) -> None:
        """Set the integration time of the measurement in power line cycles."""
        self.port.write(f"{self.node_prefix}smu.measure.nplc = {nplc}")

    @command
    def set_four_wire(self, four_wire: bool) -> None:
        """Switch between 4-wire (remote) and 2-wire (local) sensing."""
        sense = "SENSE_4WIRE" if four_wire else "SENSE_2WIRE"
        self.port.write(f"{self.node_prefix}smu.measure.sense = {self.node_prefix}smu.{sense}")

    @command(warnings="Switches off the output if it is on while the terminals are changed.")
    def set_terminals(self, terminals: Terminals) -> None:
        """Select the front or the rear terminals."""
        self.port.write(f"{self.node_prefix}smu.terminals = {self.node_prefix}smu.{terminals}")

    @command
    def set_filter_type(self, filter_type: FilterType) -> None:
        """Select the repeating or the moving average as averaging filter."""
        self.port.write(f"{self.node_prefix}smu.measure.filter.type = {self.node_prefix}smu.{filter_type}")

    @command
    def set_filter_count(self, filter_count: Annotated[int, Range(1, 100)]) -> None:
        """Set the number of readings that are averaged by the filter."""
        self.port.write(f"{self.node_prefix}smu.measure.filter.count = {filter_count:d}")

    @command
    def set_averaging_filter(self, averaging_filter: bool) -> None:
        """Switch the averaging filter on or off."""
        self.port.write(f"{self.node_prefix}smu.measure.filter.enable = {self.get_switch_constant(averaging_filter)}")

    @command
    def set_output(self, output: bool) -> None:
        """Switch the output on or off."""
        self.port.write(f"{self.node_prefix}smu.source.output = {self.get_switch_constant(output)}")

    @command
    def set_source_level(self, source_level: float) -> None:
        """Set the output level, in V or A depending on the source function."""
        self.port.write(f"{self.node_prefix}smu.source.level = {source_level}")

    @command(composite=True, returns=("voltage", "current"))
    def get_voltage_and_current(self) -> tuple[Volts, Amperes]:
        """Measure voltage in V and current in A; the sourced quantity is read back by the instrument."""
        # One line of TSP code clears the default buffer, makes the reading, takes the source value that was
        # recorded with it and looks for an error in the event log, with the TSP-Link node it comes from. Sending it
        # as one command needs a single answer per measurement point, which matters for instruments that are
        # reached through TSP-Link.
        node = self.node_prefix
        answer = self.port.query(
            f"{node}defbuffer1.clear() "
            f"local reading = {node}smu.measure.read() "
            'local code, message, severity, origin = 0, "", 0, 0 '
            f"if eventlog.getcount({self.EVENT_ERROR}) > 0 then "
            f"code, message, severity, origin = eventlog.next({self.EVENT_ERROR}) end "
            f"print(reading, {node}defbuffer1.sourcevalues[1], code, origin, message)",
        )

        fields = answer.rstrip("\r\n").split("\t")
        try:
            reading, source_value = float(fields[0]), float(fields[1])
            code, origin = int(float(fields[2])), int(float(fields[3]))
        except (IndexError, ValueError) as error:
            msg = f"Unexpected answer of the instrument to the measurement: {answer!r}."
            raise ValueError(msg) from error

        if code != 0:
            # All linked instruments share the event log, so the error can belong to another instrument
            message = fields[4] if len(fields) > 4 else ""  # noqa: PLR2004
            msg = f"Error during the measurement: {code}, {message} ({self.get_event_origin(origin)})."
            raise CommandError(msg, code=code)

        # Overflow readings are no measurement values
        if abs(reading) > self.OVERFLOW_LIMIT:
            reading = float("nan")
        if abs(source_value) > self.OVERFLOW_LIMIT:
            source_value = float("nan")

        if self.sweep_mode.startswith("Voltage"):
            return source_value, reading

        return reading, source_value
