# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022-2026 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Keithley 26xx

"""SweepMe! driver for the source measure units of the Keithley 2600 series."""

from __future__ import annotations

import contextlib
import math
import re
import time
from typing import Annotated, Any, Literal

import numpy as np
from pysweepme.commands import Elements, Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

# What the communication commands take and answer. The commands address the channel of the driver instance, which
# is selected with the 'Channel' and 'TSP-Link node' fields.
Volts = Annotated[float, Unit("V")]
Amperes = Annotated[float, Unit("A")]
Seconds = Annotated[float, Unit("s")]
VoltageArray = Annotated[np.ndarray, Elements(Volts)]
CurrentArray = Annotated[np.ndarray, Elements(Amperes)]
TimeArray = Annotated[np.ndarray, Elements(Seconds)]
Quantity = Literal["Voltage", "Current"]
Buffer = Annotated[Literal["nvbuffer1", "nvbuffer2"], Selector()]
Timer = Annotated[int, Selector(), Range(1, 8)]
DigioLine = Annotated[int, Selector(), Range(1, 14)]

# Speed option -> integration time in power line cycles
SPEED_TO_NPLC: dict[str, float] = {
    "Fast": 0.1,
    "Medium": 1.0,
    "Slow": 10.0,
}

# Current ranges in A that can be used for the measurement, in the spelling of the Range options
CURRENT_RANGES: dict[str, float] = {
    "1A": 1.0,
    "100mA": 1e-1,
    "10mA": 1e-2,
    "1mA": 1e-3,
    "100µA": 1e-4,
    "10µA": 1e-5,
    "1µA": 1e-6,
    "100nA": 1e-7,
    "10nA": 1e-8,
    "1nA": 1e-9,
    "100pA": 1e-10,
}

# Range option -> how the current range is selected ('Auto', 'Limited' or 'Fixed') and the range in A
RANGE_OPTIONS: dict[str, tuple[str, float]] = {
    "Auto": ("Auto", 0.0),
    **{f"Limited {label}": ("Limited", value) for label, value in CURRENT_RANGES.items()},
    **{f"Fixed {label}": ("Fixed", value) for label, value in CURRENT_RANGES.items()},
}

# ListSweepStepPointsType option -> how the sweep values are calculated; the options with a colon are the spelling
# of the Keithley 2400 driver, so that list sweep settings can be copied from there
STEP_WIDTH = "Step width"
POINTS_LINEAR = "Points (lin.)"
POINTS_LOG = "Points (log.)"
STEP_POINTS_TYPES: dict[str, str] = {
    STEP_WIDTH: STEP_WIDTH,
    POINTS_LINEAR: POINTS_LINEAR,
    POINTS_LOG: POINTS_LOG,
    "Step width:": STEP_WIDTH,
    "Points (lin.):": POINTS_LINEAR,
    "Points (log.):": POINTS_LOG,
}

# Trigger events of the SMU that can assert the output trigger, as TSP constant of the trigger model
TRIGGER_OUT_EVENTS: dict[str, str] = {
    "Source complete": "SOURCE_COMPLETE_EVENT_ID",
    "Measure complete": "MEASURE_COMPLETE_EVENT_ID",
}

# Pulse shape of the output trigger, as digio trigger mode
TRIGGER_OUT_POLARITIES: dict[str, str] = {
    "Low pulse": "TRIG_FALLING",
    "High pulse": "TRIG_RISINGM",
}


class Device(EmptyDevice):
    """Driver for the Keithley 26xx series source measure units using the TSP command set.

    The user documentation is in doc/description.md.
    """

    # Readings above this value are returned by the instrument if the measurement is not valid
    OVERFLOW_LIMIT = 1e37

    # Limits of the pulse on and off times that are supported by the instrument
    MIN_PULSE_TIME = 200e-6
    MAX_PULSE_OFF_TIME = 3.0
    DEFAULT_PULSE_OFF_TIME = 200e-3

    # Highest number of readings the averaging filter takes
    MAX_FILTER_COUNT = 100

    # Number of channels that must share the port so that the dual pulse mode can be used
    DUAL_PULSE_NR_DEVICES = 2

    # Option of the 'TSP-Link node' field that addresses the instrument connected to the port
    LOCAL_NODE = "Local"

    # Highest node number that can be used in a TSP-Link network
    MAX_TSP_LINK_NODE = 64

    # Option of the 'SweepValue' field that the SMU module adds when the driver returns the 'ListSweepCheck' key
    LIST_SWEEP = "List sweep"

    # Part of the time between two steps that the output trigger pulse may last. The rest is left for steps that take
    # less time than the one before, through auto ranging or the automatic delay.
    TRIGGER_PULSE_MARGIN = 0.5

    # Longest hold time in s, the longest delay of a trigger timer
    MAX_HOLD_TIME = 100000.0

    # Highest number of points of a list sweep: a reading buffer stores over 60,000 readings with timestamps
    MAX_LIST_POINTS = 60000

    # Number of sweep values that are sent to the instrument with one command, so that a command stays short
    LIST_CHUNK_SIZE = 50

    # Name of the Lua table on the instrument that holds the sweep values
    LIST_TABLE = "sweepme_list"

    # Highest line number of the digital I/O port that can be used as output trigger
    MAX_DIGIO_LINE = 14

    # Option of the 'Trigger out line' field that disables the output trigger
    NO_TRIGGER_OUT = "None"

    # Models without digital I/O trigger lines
    NO_DIGIO_TRIGGER_MODELS = ("2604B", "2614B", "2634B")

    # Polling interval in s while a list sweep runs
    LIST_POLL_INTERVAL = 0.05

    # Time in s without a new reading after which a running list sweep is considered stuck, added to three steps
    LIST_STALL_TIMEOUT = 5.0

    # Line frequency in Hz that is used to estimate the integration time, 50 Hz gives the longer time
    LINE_FREQUENCY = 50.0

    # Line frequency in Hz for the shortest integration time, used where a lower bound of the step time is needed
    LINE_FREQUENCY_MAX = 60.0

    def __init__(self) -> None:
        """Initialize the driver, the returned variables and the port configuration."""
        super().__init__()

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.port_manager = True
        self.port_types = ["COM", "GPIB", "USB", "TCPIP"]
        self.port_properties = {
            "baudrate": 115200,
            "EOL": "\n",
            "timeout": 10,
            # A delay might be needed for TCPIP communication as it seems that some commands are lost
            # "delay": 0.01,  # noqa: ERA001
        }

        self.port_identifications = ["Keithley Instruments,26", "Keithley Instruments Inc., Model 26"]

        self.gui_parameters: dict[str, Any] = {}

        # Set in apply_gui_parameters
        self.channel: str = "Ch A"
        self.smu_ab: str = "smua"
        self.tsp_link_node: str = self.LOCAL_NODE
        self.node_number: int | None = None
        """TSP-Link node number of the channel, None if the instrument connected to the port is used."""
        self.node_prefix: str = ""
        """Prefix such as 'node[3].' for commands to a remote TSP-Link node, empty for the local node."""
        self.smu: str = "smua"
        """Full TSP name of the channel, e.g. 'smua' or 'node[3].smua'."""
        self.pulse_mode: bool = False
        self.list_sweep: bool = False

        # Converted in convert_parameters
        self.source: str = "Voltage in V"
        self.four_wire: bool = False
        self.route_out: str = "Rear"
        self.protection: float = 100e-6
        self.speed: str = "Fast"
        self.average: int = 1
        self.current_autorange: bool = True
        self.current_autorange_lowlimit: float | None = None
        self.current_range_value: float = 1.0

        # Pulse mode parameters
        self.pulse_meas_time: float = 200e-6
        self.ton: float = 200e-6
        self.toff: float = 200e-3
        self.pulseofflevel: float = 0.0

        # List sweep values after conversion in configure: the time in s between two sweep points (0 to step as fast
        # as possible), the settling time in s before each measurement (None for the automatic delay), and the digital
        # I/O line (None without output trigger), pulse width in s, trigger mode and event of the output trigger
        self.sweep_values: list[float] = []
        self.step_time: float = 0.0
        self.measure_delay: float | None = None
        self.digio_line: int | None = None
        self.digio_pulse_width: float = 10e-6
        self.digio_trigger_mode: str = "TRIG_FALLING"
        self.digio_trigger_event: str = "SOURCE_COMPLETE_EVENT_ID"

        # Voltages in V, currents in A and times in s of the last list sweep
        self.list_results: tuple[np.ndarray, np.ndarray, np.ndarray] = (np.array([]), np.array([]), np.array([]))

        # Set during the run
        self.nplc: float = 1.0
        self.tag: str = "1"
        self.master: bool = False
        self.dualpulse: bool = False

        # Tells whether this instance is already counted as user of the shared port
        self.port_manager_registered: bool = False

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the fields that are shown in the graphical user interface."""
        del parameters
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["Ch A", "Ch B"],
            "TSP-Link node": self.node_options(),
            "4wire": False,
            "RouteOut": ["Rear"],
            "Speed": list(SPEED_TO_NPLC),
            "Range": list(RANGE_OPTIONS),
            "Average": 1,
            "Compliance": 100e-6,
            "CheckPulse": False,
            "PulseMeasTime": 200e-6,
            "PulseOnTime": 200e-6,
            "PulseOffTime": 200e-3,
            "PulseOffLevel": 0.0,
            "ListSweepCheck": True,
            "ListSweepType": ["Sweep", "Custom"],
            "ListSweepStart": 0.0,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": [STEP_WIDTH, POINTS_LINEAR, POINTS_LOG],
            "ListSweepStepPointsValue": 0.1,
            "ListSweepDual": False,
            "ListSweepCustomValues": "",
            "ListSweepHoldtime": 0.1,
            "ListSweepDelaytime": "",
            "Trigger out line": [self.NO_TRIGGER_OUT, *[str(line) for line in range(1, self.MAX_DIGIO_LINE + 1)]],
            "Trigger out event": list(TRIGGER_OUT_EVENTS),
            "Trigger out polarity": list(TRIGGER_OUT_POLARITIES),
            "Trigger out pulse width in s": 10e-6,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Take over the parameters that were chosen by the user in the graphical user interface."""
        # A copy, so that a later failed update of the parameters does not reach the driver
        self.gui_parameters = dict(parameters)

        self.pulse_mode = bool(parameters.get("CheckPulse", False))
        self.list_sweep = parameters.get("SweepValue", "") == self.LIST_SWEEP

        # In a list sweep, each point comes with the time at which it was measured
        if self.list_sweep:
            self.variables = ["Voltage", "Current", "Time"]
            self.units = ["V", "A", "s"]
            self.plottype = [True, True, True]
            self.savetype = [True, True, True]
        else:
            self.variables = ["Voltage", "Current"]
            self.units = ["V", "A"]
            self.plottype = [True, True]
            self.savetype = [True, True]

        # The module passes an empty channel while it refreshes the fields
        self.channel = str(parameters.get("Channel") or "Ch A")
        self.smu_ab = "smub" if self.channel.endswith("B") else "smua"

        # Older settings do not have this field and use the local node
        self.tsp_link_node = str(parameters.get("TSP-Link node", self.LOCAL_NODE))
        try:
            self.node_number = self.parse_node_number(self.tsp_link_node)
        except ValueError:
            # This function is also called with incomplete parameters, the option is checked again in 'initialize'
            self.node_number = None
        self.node_prefix = "" if self.node_number is None else f"node[{self.node_number}]."
        self.smu = f"{self.node_prefix}{self.smu_ab}"

        if self.node_number is None:
            self.shortname = f"Keithley26xx Ch {self.channel[-1]}"
        else:
            self.shortname = f"Keithley26xx Node {self.node_number} Ch {self.channel[-1]}"

    def connect(self) -> None:
        """Find out whether this instance is the master of the shared port."""
        if self.node_number is None:
            self.update_master_state()
        self.port.port.write_termination = "\n"

    def initialize(self) -> None:
        """Check the parameters and the TSP-Link node, reset the channel, clear the error queue, autozero once."""
        self.convert_parameters()

        # Stops the run if the option of the 'TSP-Link node' field is not valid
        self.parse_node_number(self.tsp_link_node)

        if self.node_number is not None:
            self.check_remote_node()

        if self.list_sweep:
            self.check_list_sweep_support()

        if self.pulse_mode:
            self.tag = "1" if self.smu_ab == "smua" else "2"

        if self.node_number is None:
            self.reset()
            self.clear_error_queue()
        else:
            # The error queue is cleared first, so that an error caused by the reset shows that the channel
            # cannot be reached
            self.clear_error_queue()
            self.reset()
            self.check_remote_channel()

        # Some devices have problems with this command, so the line frequency setting is left as it is.
        # self.port.write("localnode.autolinefreq = true")  # noqa: ERA001

        self.set_autozero_once()

    def deinitialize(self) -> None:
        """Return to local sensing and switch off the averaging filter."""
        self.set_remote_sense(False)
        self.set_filter_count(1)
        self.set_filter_enabled(False)

    def configure(self) -> None:
        """Configure source function, ranges, sense mode, averaging and integration time."""
        self.convert_parameters()
        self.register_port_usage()

        if self.pulse_mode:
            # In pulse mode all ranges are set in 'apply' and auto ranging must be switched off
            self.configure_pulse_ranges()
        else:
            self.configure_source()
            self.configure_current_measurement_range()

        self.set_remote_sense(self.four_wire)

        self.configure_averaging()

        # speed of measurement Fast=0.1, Medium=1.0, Slow=10.0, (1 == 20 ms at 50 Hz line frequency)
        self.nplc = SPEED_TO_NPLC[self.speed]
        self.set_nplc(self.nplc)

        if self.list_sweep:
            self.convert_list_sweep_parameters()
            self.configure_list_sweep()

    def unconfigure(self) -> None:
        """Release the output trigger and the timer of a list sweep and remove this instance from the port users."""
        try:
            if self.list_sweep:
                self.unconfigure_list_sweep()
        finally:
            # The port bookkeeping is done also if the list sweep cleanup failed
            self.release_port_usage()

    def release_port_usage(self) -> None:
        """Remove this instance from the users of the shared port, see 'register_port_usage'."""
        if self.node_number is not None:
            # Channels on remote nodes are not counted
            return

        if self.port_manager_registered:
            self.port.port_properties["NrDevices"] -= 1
            self.port_manager_registered = False

        if self.port.port_properties["NrDevices"] == 1:
            self.port.port_properties.update({"Master": False})
        else:
            self.port.port_properties.update({"Slave": False})

    def poweron(self) -> None:
        """Switch on the output of the channel."""
        self.set_output(True)

    def poweroff(self) -> None:
        """Switch off the output of the channel."""
        self.set_output(False)

    def start(self) -> None:
        """Find out whether both channels of the instrument are used in pulse mode."""
        self.dualpulse = (
            self.pulse_mode
            and self.port.port_properties["NrDevices"] == self.DUAL_PULSE_NR_DEVICES
            and self.port.port_properties["Master"] is True
            and self.port.port_properties["Slave"] is True
        )

    def apply(self) -> None:
        """Set the new source level, or configure the pulse if the pulse mode is used."""
        if self.list_sweep:
            # The instrument sets the source levels of a list sweep by itself
            return

        if self.pulse_mode:
            self.prepare_pulse()
        elif self.source.startswith("Voltage"):
            self.set_source_level_voltage(float(self.value))
        else:
            self.set_source_level_current(float(self.value))

    def trigger_ready(self) -> None:
        """Start the pulse if the pulse mode is used."""
        if not self.pulse_mode:
            return

        # The answers of the pulse factory scripts are read in 'request_pulse_buffers'
        if self.dualpulse:
            if self.master:
                # Pulse with tag1 = 2 has to be 40e-6 s longer than Pulse with tag2 = 1, equal toff,
                # pulse of smub always encapsulate pulse of smua
                self.port.write("print(InitiatePulseTestDual(2,1))")
        else:
            self.port.write(f"print(InitiatePulseTest({self.tag}))")

    def measure(self) -> None:
        """Request a current and voltage measurement, request the pulse buffers, or run the list sweep."""
        if self.list_sweep:
            self.run_list_sweep()
        elif self.pulse_mode:
            self.request_pulse_buffers()
        else:
            self.request_measurement()

    def call(self) -> list[float] | list[np.ndarray]:
        """Return the measured voltage in V and current in A, and in a list sweep the time in s of each point."""
        if self.list_sweep:
            return self.list_sweep_results()

        if self.pulse_mode:
            voltage, current = self.collect_pulse_results()
        else:
            current, voltage = self.read_measurement()

        if abs(voltage) > self.OVERFLOW_LIMIT or abs(current) > self.OVERFLOW_LIMIT:
            return [float("nan"), float("nan")]

        return [voltage, current]

    # Functions that are used by the semantic functions start here

    def convert_parameters(self) -> None:
        """Convert and check the parameters of the graphical user interface."""
        parameters = self.gui_parameters

        self.source = str(parameters.get("SweepMode", "Voltage in V"))
        if self.source not in ("Voltage in V", "Current in A"):
            msg = f"SweepMode '{self.source}' is not supported. Use 'Voltage in V' or 'Current in A'."
            raise ValueError(msg)

        self.four_wire = bool(parameters.get("4wire", False))
        self.route_out = str(parameters.get("RouteOut", "Rear"))

        self.speed = str(parameters.get("Speed", "Fast"))
        if self.speed not in SPEED_TO_NPLC:
            msg = f"Speed '{self.speed}' is not supported. Use one of {', '.join(SPEED_TO_NPLC)}."
            raise ValueError(msg)

        range_option = str(parameters.get("Range", "Auto"))
        if range_option not in RANGE_OPTIONS:
            msg = f"Range '{range_option}' is not supported. Use 'Auto', 'Limited <range>' or 'Fixed <range>'."
            raise ValueError(msg)
        range_mode, range_value = RANGE_OPTIONS[range_option]
        # 'Limited' uses auto ranging, but the instrument must not range below the given value
        self.current_autorange = range_mode != "Fixed"
        self.current_autorange_lowlimit = range_value if range_mode == "Limited" else None
        self.current_range_value = range_value if range_mode == "Fixed" else 1.0

        self.protection = self.convert_number(parameters.get("Compliance", 100e-6), "Compliance")

        # In pulse mode, Average is the number of pulses, which the averaging filter does not limit
        average = self.convert_number(parameters.get("Average", 1), "Average")
        if average < 1 or average != int(average):
            msg = f"Average must be a whole number of at least 1, not {average}."
            raise ValueError(msg)
        if not self.pulse_mode and average > self.MAX_FILTER_COUNT:
            msg = f"Average must be a whole number from 1 to {self.MAX_FILTER_COUNT}, not {average}."
            raise ValueError(msg)
        self.average = int(average)

        if self.pulse_mode:
            self.pulse_meas_time = self.convert_number(parameters.get("PulseMeasTime", 200e-6), "PulseMeasTime")
            self.ton = round(self.convert_number(parameters.get("PulseOnTime", 200e-6), "PulseOnTime"), 6)
            self.toff = self.convert_number(parameters.get("PulseOffTime", 200e-3), "PulseOffTime")
            self.pulseofflevel = self.convert_number(parameters.get("PulseOffLevel", 0.0), "PulseOffLevel")
            self.limit_pulse_times()

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

    def register_port_usage(self) -> None:
        """Count this instance as user of the shared port and update the master state.

        Channels on remote TSP-Link nodes are not counted. The count is only used to detect the dual pulse mode of
        the two channels of the instrument connected to the port, and remote nodes cannot be pulsed.
        """
        if self.node_number is not None:
            return

        if not self.port_manager_registered:
            self.port.port_properties["NrDevices"] += 1
            self.port_manager_registered = True

        self.update_master_state()

    def update_master_state(self) -> None:
        """Define whether this instance is the master or the slave of the shared port.

        The distinction is only needed for the dual pulse mode where one channel triggers both pulses.
        """
        if self.port.port_properties["NrDevices"] == 1:
            self.port.port_properties.update({"Master": self.pulse_mode})
            self.master = True
        else:
            self.master = False
            self.port.port_properties.update({"Slave": self.pulse_mode})

    def node_options(self) -> list[str]:
        """Return the TSP-Link node options that are shown in the graphical user interface."""
        return [self.LOCAL_NODE, *[f"Node {number}" for number in range(1, self.MAX_TSP_LINK_NODE + 1)]]

    def parse_node_number(self, node_option: str) -> int | None:
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

    def check_remote_node(self) -> None:
        """Make sure that the TSP-Link network can be used for a channel on a remote node.

        The TSP-Link network is not initialized by the driver, so that the configuration used by other software
        is not changed.
        """
        if self.pulse_mode:
            msg = (
                f"Pulse mode is only supported on the local node, but TSP-Link node {self.node_number} is selected. "
                "Connect the instrument directly or set 'TSP-Link node' to 'Local'."
            )
            raise ValueError(msg)

        state = self.get_tsp_link_state()
        if state != "online":
            msg = (
                f"TSP-Link node {self.node_number} cannot be reached because the TSP-Link network is '{state}'. "
                "Please initialize the TSP-Link network on the instrument connected to the port, e.g. via the "
                "front panel or with tsplink.reset(), and start the run again."
            )
            raise ValueError(msg)

    def check_remote_channel(self) -> None:
        """Make sure that the channel on the remote TSP-Link node exists.

        Must be called after the error queue was cleared and a command was sent to the channel. A command to a node
        or channel that does not exist is not answered, it only creates an entry in the error queue.
        """
        if self.get_error_count() == 0:
            return

        code, message = self.get_next_error()
        msg = (
            f"Channel {self.channel[-1]} of TSP-Link node {self.node_number} cannot be used, the instrument reports "
            f"error {code}: {message}. Please check that an instrument with this node number is part of the TSP-Link "
            "network, that it has this channel, and that the TSP-Link network was reset after the last power cycle "
            "of any of the linked instruments."
        )
        raise ValueError(msg)

    def configure_source(self) -> None:
        """Set source function, displayed measurement function, compliance and auto ranges."""
        if self.source.startswith("Voltage"):
            self.set_source_function("Voltage")
            self.set_display_measure_function("Current")
            self.set_current_limit(self.protection)
        else:
            self.set_source_function("Current")
            self.set_display_measure_function("Voltage")
            self.set_voltage_limit(self.protection)

        self.set_source_autorange_voltage(True)
        self.set_measure_autorange_voltage(True)
        self.set_source_autorange_current(True)

    def configure_current_measurement_range(self) -> None:
        """Set the current measurement range according to the selected range option."""
        if self.current_autorange:
            self.set_measure_autorange_current(True)
            if self.current_autorange_lowlimit is not None:
                self.set_measure_lowrange_current(self.current_autorange_lowlimit)
        else:
            self.set_measure_autorange_current(False)
            self.set_measure_range_current(self.current_range_value)

    def configure_averaging(self) -> None:
        """Switch on the repeating average filter if more than one reading is averaged.

        In pulse mode, an Average above the filter limit is a number of pulses only, and the filter stays off.
        """
        if 1 < self.average <= self.MAX_FILTER_COUNT:
            self.set_filter_count(self.average)
            self.set_filter_enabled(True)
            self.set_filter_repeat_average()
        else:
            self.set_filter_count(1)
            self.set_filter_enabled(False)

    def configure_pulse_ranges(self) -> None:
        """Switch off all auto ranges, which is needed for pulsed measurements."""
        self.set_source_autorange_voltage(False)
        self.set_source_autorange_current(False)
        self.set_measure_autorange_voltage(False)
        self.set_measure_autorange_current(False)

    def limit_pulse_times(self) -> None:
        """Restrict the pulse on and off times to the range that is supported by the instrument."""
        self.ton = max(self.ton, self.MIN_PULSE_TIME)
        if self.toff < self.MIN_PULSE_TIME:
            self.toff = self.DEFAULT_PULSE_OFF_TIME
        self.toff = min(self.toff, self.MAX_PULSE_OFF_TIME)

    # check_driver: ignore DC004 - a step of the pulse mode that needs the pulse settings of the run
    def prepare_pulse(self) -> None:
        """Configure a single pulse using the ConfigPulse factory scripts of the instrument."""
        # converts the percentage value of self.speed into a corresponding speed value
        # multiplies by 50 because of line frequency
        self.nplc = self.ton * self.pulse_meas_time / 100.0 * 50.0

        ton = self.ton

        if self.dualpulse:
            if self.smu_ab == "smub":
                # prolongs SMUb on-time by 40 mus to ensure proper encapsulation of SMUa pulse in DualPulse-mode
                ton = self.ton + 40e-6

            if self.master:
                self.port.average = self.average
            else:
                self.average = self.port.average

        self.clear_buffer("nvbuffer1")
        self.set_buffer_append_mode("nvbuffer1", True)
        self.set_nplc(self.nplc)
        self.set_buffer_collect_source_values("nvbuffer1", True)

        level = float(self.value)

        # The factory scripts ConfigPulseVMeasureI and ConfigPulseIMeasureV answer with their result, which is read
        # right away; they are not wrapped as commands because they need the pulse settings of the run
        if self.source.startswith("Voltage"):
            self.set_source_range_voltage(self.protection)
            self.set_measure_range_current(self.protection)
            self.port.write(
                f"print(ConfigPulseVMeasureI({self.smu}, {self.pulseofflevel}, {level}, {self.protection}, "
                f"{ton}, {self.toff}, {self.average}, {self.smu}.nvbuffer1, {self.tag}))",
            )
        else:
            self.set_source_range_current(self.protection)
            self.set_measure_range_voltage(self.protection)
            self.port.write(
                f"print(ConfigPulseIMeasureV({self.smu}, {self.pulseofflevel}, {level}, {self.protection}, "
                f"{ton}, {self.toff}, {self.average}, {self.smu}.nvbuffer1, {self.tag}))",
            )

        self.port.read()  # remove answer from buffer

    # check_driver: ignore DC004 - requests answers that collect_pulse_results reads in the next phase
    def request_pulse_buffers(self) -> None:
        """Read the answer of the pulse initiation and request the readings of the pulse buffers."""
        # The buffers are requested here and read in 'collect_pulse_results', in the next phase
        if self.dualpulse:
            if not self.master:
                return

            self.port.read()  # remove answer caused by InitiatePulseTestDual in trigger_ready

            # request the values of smua and smub if dualpulse
            for smu in ("smua", "smub"):
                self.port.write(f"printbuffer(1, {self.average}, {smu}.nvbuffer1.readings)")
                self.port.write(f"printbuffer(1, {self.average}, {smu}.nvbuffer1.sourcevalues)")
        else:
            self.port.read()  # remove answer caused by InitiatePulseTest in trigger_ready

            self.port.write(f"printbuffer(1, {self.average}, {self.smu}.nvbuffer1.readings)")
            self.port.write(f"printbuffer(1, {self.average}, {self.smu}.nvbuffer1.sourcevalues)")

    def collect_pulse_results(self) -> tuple[float, float]:
        """Read the pulse buffers and return the averaged voltage in V and current in A."""
        if self.dualpulse:
            if self.master:
                # read all values of smua and smub if dualpulse
                readings_a = self.next_buffer_values()
                sources_a = self.next_buffer_values()
                readings_b = self.next_buffer_values()
                sources_b = self.next_buffer_values()

                # if master, hand over the values of the slave using the port object
                if self.smu_ab == "smua":
                    readings, sources = readings_a, sources_a
                    self.port.buffer = readings_b, sources_b
                else:
                    readings, sources = readings_b, sources_b
                    self.port.buffer = readings_a, sources_a

            # if slave, take the values that the master has put into the port object
            else:
                readings, sources = self.port.buffer
        else:
            readings = self.next_buffer_values()
            sources = self.next_buffer_values()

        # Depending on VOLT or CURR mode as source, voltage or current corresponds to .readings or .sourcevalues
        if self.source.startswith("Voltage"):
            return float(np.average(sources)), float(np.average(readings))

        return float(np.average(readings)), float(np.average(sources))

    # check_driver: ignore DC004 - reads one answer that request_pulse_buffers requested
    def next_buffer_values(self) -> list[float]:
        """Read one comma separated list of buffer values from the port."""
        return [float(value) for value in self.port.read().replace("\n", "").split(",")]

    # check_driver: ignore DC004 - the first half of a measurement that 'read_measurement' reads in the next phase
    def request_measurement(self) -> None:
        """Request a combined current and voltage measurement, read with 'read_measurement'."""
        # Requested in 'measure' and read in 'call', so that all instruments of the branch measure at the same time
        self.port.write(f"print({self.smu}.measure.iv())")

    # check_driver: ignore DC004 - the second half of a measurement that 'request_measurement' started
    def read_measurement(self) -> tuple[float, float]:
        """Read the current in A and the voltage in V of the measurement requested with 'request_measurement'."""
        return self.parse_measurement(self.port.read())

    @staticmethod
    def parse_measurement(answer: str) -> tuple[float, float]:
        """Return current in A and voltage in V from the answer to smuX.measure.iv()."""
        try:
            current, voltage = (float(value) for value in answer.split())
        except ValueError as exception:
            msg = f"Unexpected answer of the instrument to the measurement: {answer!r}."
            raise ValueError(msg) from exception
        return current, voltage

    def check_list_sweep_support(self) -> None:
        """Make sure that the list sweep can be used with the chosen settings and the connected model."""
        if self.pulse_mode:
            msg = "List sweep and pulse mode cannot be used together. Please switch off the pulse mode."
            raise ValueError(msg)

        if self.node_number is not None:
            msg = (
                f"List sweep is only supported on the local node, but TSP-Link node {self.node_number} is selected. "
                "Connect the instrument directly or set 'TSP-Link node' to 'Local'."
            )
            raise ValueError(msg)

        if str(self.gui_parameters.get("Trigger out line", self.NO_TRIGGER_OUT)) != self.NO_TRIGGER_OUT:
            identification = self.get_identification()
            for model in self.NO_DIGIO_TRIGGER_MODELS:
                if model in identification:
                    msg = (
                        f"The Model {model} has no digital I/O trigger lines. Please set 'Trigger out line' to "
                        f"'{self.NO_TRIGGER_OUT}'."
                    )
                    raise ValueError(msg)

    def convert_list_sweep_parameters(self) -> None:
        """Convert the list sweep fields into sweep values, step time, measurement delay and output trigger."""
        parameters = self.gui_parameters

        if parameters.get("ListSweepType", "Sweep") == "Custom":
            self.sweep_values = self.parse_custom_values(str(parameters.get("ListSweepCustomValues", "")))
            self.check_list_size(len(self.sweep_values))
        else:
            self.sweep_values = self.calculate_sweep_values(
                str(parameters.get("ListSweepStart", "0.0")),
                str(parameters.get("ListSweepEnd", "1.0")),
                str(parameters.get("ListSweepStepPointsType", STEP_WIDTH)),
                str(parameters.get("ListSweepStepPointsValue", "0.1")),
                dual=bool(parameters.get("ListSweepDual", False)),
            )

        self.step_time = self.convert_time(parameters.get("ListSweepHoldtime", "0.1"), "Hold time") or 0.0
        if self.step_time > self.MAX_HOLD_TIME:
            msg = f"The Hold time of the list sweep must be at most {self.MAX_HOLD_TIME:g} s, not {self.step_time} s."
            raise ValueError(msg)
        self.measure_delay = self.convert_time(parameters.get("ListSweepDelaytime", ""), "Delay time")

        integration_time = self.nplc / self.LINE_FREQUENCY * self.average
        settling_time = (self.measure_delay or 0.0) + integration_time
        # A single point has no next step that the hold time must leave room for
        if 0 < self.step_time < settling_time and len(self.sweep_values) > 1:
            msg = (
                f"The hold time of {self.step_time} s is shorter than the delay time plus the integration time of "
                f"{settling_time:.3g} s. Please increase the hold time, or reduce the delay time, the speed or the "
                "number of averages."
            )
            raise ValueError(msg)

        line = str(parameters.get("Trigger out line", self.NO_TRIGGER_OUT))
        if line == self.NO_TRIGGER_OUT:
            self.digio_line = None
            return

        try:
            self.digio_line = int(line)
        except ValueError:
            self.digio_line = 0
        if not 1 <= self.digio_line <= self.MAX_DIGIO_LINE:
            msg = (
                f"Trigger out line '{line}' is not supported. Use '{self.NO_TRIGGER_OUT}' or a line from 1 to "
                f"{self.MAX_DIGIO_LINE}."
            )
            raise ValueError(msg)

        polarity = str(parameters.get("Trigger out polarity", "Low pulse"))
        if polarity not in TRIGGER_OUT_POLARITIES:
            msg = f"Trigger out polarity '{polarity}' is not supported. Use one of {', '.join(TRIGGER_OUT_POLARITIES)}."
            raise ValueError(msg)
        self.digio_trigger_mode = TRIGGER_OUT_POLARITIES[polarity]

        event = str(parameters.get("Trigger out event", "Source complete"))
        if event not in TRIGGER_OUT_EVENTS:
            msg = f"Trigger out event '{event}' is not supported. Use one of {', '.join(TRIGGER_OUT_EVENTS)}."
            raise ValueError(msg)
        self.digio_trigger_event = TRIGGER_OUT_EVENTS[event]

        pulse_width = self.convert_time(
            parameters.get("Trigger out pulse width in s", 10e-6),
            "Trigger out pulse width",
        )
        self.digio_pulse_width = pulse_width or 10e-6
        # The shortest step lasts the delay time plus the integration time at 60 Hz, the shorter of both line periods
        shortest_settling_time = (self.measure_delay or 0.0) + self.nplc / self.LINE_FREQUENCY_MAX * self.average
        self.check_trigger_pulse_spacing(shortest_settling_time)

    def check_trigger_pulse_spacing(self, settling_time: float) -> None:
        """Refuse an output trigger pulse that lasts until the next step, where the instrument would skip a pulse.

        With a hold time the steps start at that interval; without one, a step takes at least the delay time plus
        the integration time, estimated at 60 Hz, which gives the shorter time. The trigger events (source or
        measure complete) can come closer together than that, because auto ranging and the automatic delay change
        how long a step takes, so the pulse may last at most half of the interval.
        """
        if len(self.sweep_values) < 2:  # noqa: PLR2004 - two points are the first with a next step
            return

        interval = self.step_time if self.step_time > 0 else settling_time
        max_width = interval * self.TRIGGER_PULSE_MARGIN
        if self.digio_pulse_width > max_width:
            msg = (
                f"The trigger out pulse width of {self.digio_pulse_width} s is longer than half the time between two "
                f"steps of at least {interval:.3g} s, so the output trigger could miss steps. Please use a pulse width "
                f"of at most {max_width:.3g} s or a longer hold time."
            )
            raise ValueError(msg)

    def check_list_size(self, points: int) -> None:
        """Refuse a list sweep with more points than a reading buffer takes, before the values are calculated."""
        if points > self.MAX_LIST_POINTS:
            msg = f"The list sweep has {points} points, but at most {self.MAX_LIST_POINTS} are supported."
            raise ValueError(msg)

    def timer_number(self) -> int:
        """Return the trigger timer that paces the list sweep; each channel uses its own timer."""
        return 1 if self.smu_ab == "smua" else 2

    def calculate_sweep_values(
        self,
        start_text: str,
        end_text: str,
        steppoints_option: str,
        steppoints_text: str,
        *,
        dual: bool = False,
    ) -> list[float]:
        """Calculate the sweep values from start value, end value and step width or number of points.

        A dual sweep adds the way back to the start value; the end value is only used once.
        """
        start, end, steppoints = self.parse_sweep_numbers(start_text, end_text, steppoints_text)

        if steppoints_option not in STEP_POINTS_TYPES:
            msg = (
                f"ListSweepStepPointsType '{steppoints_option}' is not supported. Use '{STEP_WIDTH}', "
                f"'{POINTS_LINEAR}' or '{POINTS_LOG}'."
            )
            raise ValueError(msg)
        steppoints_type = STEP_POINTS_TYPES[steppoints_option]

        if steppoints_type == STEP_WIDTH:
            if steppoints == 0.0:
                if start != end:
                    msg = "The step width of the list sweep must not be 0 if start and end value differ."
                    raise ValueError(msg)
                return [start]

            # The sweep stops at the last step that does not go beyond the end value
            step = abs(steppoints) if end >= start else -abs(steppoints)
            points = int(np.floor(abs(end - start) / abs(step) + 1e-9)) + 1
            self.check_list_size(2 * points - 1 if dual else points)
            values = [start + step * index for index in range(points)]
        else:
            points = int(steppoints)
            if points < 1 or points != steppoints:
                msg = f"The number of points of the list sweep must be a positive integer, but is {steppoints}."
                raise ValueError(msg)
            self.check_list_size(2 * points - 1 if dual else points)

            if steppoints_type == POINTS_LOG:
                if start * end <= 0:
                    msg = "Start and end value of a logarithmic list sweep must have the same sign and must not be 0."
                    raise ValueError(msg)
                values = [float(value) for value in np.geomspace(start, end, points)]
            else:
                values = [float(value) for value in np.linspace(start, end, points)]

        if dual:
            values = [*values, *values[-2::-1]]
        return values

    @staticmethod
    def parse_sweep_numbers(start_text: str, end_text: str, steppoints_text: str) -> tuple[float, float, float]:
        """Convert start value, end value and step width or points of the list sweep into finite numbers."""
        try:
            numbers = (float(start_text), float(end_text), float(steppoints_text))
        except ValueError:
            msg = "Start value, end value and step width or points of the list sweep must be numbers."
            raise ValueError(msg) from None

        if not all(math.isfinite(number) for number in numbers):
            msg = "Start value, end value and step width or points of the list sweep must be finite numbers."
            raise ValueError(msg)
        return numbers

    @staticmethod
    def parse_custom_values(text: str) -> list[float]:
        """Convert custom values, separated by commas, semicolons or line breaks, into a list of floats."""
        entries = [entry for entry in re.split(r"[,;\s]+", text) if entry]
        if not entries:
            msg = "Please enter the custom values of the list sweep, separated by commas."
            raise ValueError(msg)

        try:
            values = [float(entry) for entry in entries]
        except ValueError:
            msg = "The custom values of the list sweep must be numbers separated by commas."
            raise ValueError(msg) from None

        if not all(math.isfinite(value) for value in values):
            msg = "The custom values of the list sweep must be finite numbers."
            raise ValueError(msg)
        return values

    @staticmethod
    def convert_time(text: str | float, name: str) -> float | None:
        """Convert a time field of the list sweep into seconds, None if the field is empty."""
        if str(text).strip() == "":
            return None

        try:
            value = float(text)
        except ValueError:
            msg = f"The {name} of the list sweep must be a number in s, but is '{text}'."
            raise ValueError(msg) from None

        if not math.isfinite(value) or value < 0:
            msg = f"The {name} of the list sweep must be a finite number of at least 0 s, but is {value} s."
            raise ValueError(msg)

        return value

    def configure_list_sweep(self) -> None:
        """Set up the trigger model so that the instrument steps through the sweep values by itself.

        Each step is started by a trigger timer with the hold time as period, or immediately after the previous
        measurement if no hold time is given. At each step, the source value is set, the delay time is waited and
        current and voltage are measured into the two reading buffers. The output trigger is asserted at each step.
        """
        # The line is claimed before anything is sent, so that a second channel cannot take over its trigger
        if self.digio_line is not None:
            self.claim_digio_line(self.digio_line)

        try:
            self._program_list_sweep()
        except Exception:
            # Give the line and the timer back right away, whether or not SweepMe! calls unconfigure after the error
            with contextlib.suppress(Exception):
                self.unconfigure_list_sweep()
            raise

    def _program_list_sweep(self) -> None:
        """Send the sweep values and the trigger model of the list sweep."""
        self.send_list_values(self.sweep_values)
        if self.source.startswith("Voltage"):
            self.set_trigger_source_list_voltage(self.LIST_TABLE)
        else:
            self.set_trigger_source_list_current(self.LIST_TABLE)
        self.set_trigger_source_action(True)

        self.set_measure_delay(self.measure_delay)
        self.prepare_list_buffers()
        self.set_trigger_measure_iv()
        self.set_trigger_measure_action(True)

        self.set_trigger_endpulse_hold()
        self.set_trigger_endsweep_idle()
        self.set_trigger_count(len(self.sweep_values))
        self.set_trigger_arm_count(1)

        timer = self.timer_number()
        self.reset_timer(timer)
        if self.step_time > 0 and len(self.sweep_values) > 1:
            # The first event passes through when the sweep is armed, the timer creates one event per further point
            self.set_timer_delay(timer, self.step_time)
            self.set_timer_count(timer, len(self.sweep_values) - 1)
            self.set_timer_passthrough(timer, True)
            self.set_timer_stimulus(timer, f"{self.smu}.trigger.ARMED_EVENT_ID")
            self.set_trigger_source_stimulus(f"trigger.timer[{timer}].EVENT_ID")
        else:
            self.set_trigger_source_stimulus("0")

        if self.digio_line is not None:
            self.reset_digio_trigger(self.digio_line)
            self.set_digio_trigger_mode(self.digio_line, self.digio_trigger_mode)
            self.set_digio_trigger_pulsewidth(self.digio_line, self.digio_pulse_width)
            self.set_digio_trigger_stimulus(self.digio_line, f"{self.smu}.trigger.{self.digio_trigger_event}")

    def unconfigure_list_sweep(self) -> None:
        """Release the output trigger line and the timer that were used by the list sweep."""
        # The timer is reset also if the reset of the line fails; that error is raised afterwards
        try:
            if self.digio_line is not None and self.release_digio_line(self.digio_line):
                self.reset_digio_trigger(self.digio_line)
        finally:
            self.reset_timer(self.timer_number())

    def digio_line_key(self, line: int) -> str:
        """Return the key under which the channel that uses a digital I/O line of the port is kept."""
        return f"Keithley26xx {self.gui_parameters.get('Port', '')} digio line {line}"

    def claim_digio_line(self, line: int) -> None:
        """Reserve a digital I/O line of the port for this channel; raise if another channel uses it.

        The instrument has one trigger setting per line, so a second channel would replace the first one's trigger.
        The claims are kept in 'device_communication', which is emptied at the start of each run.
        """
        key = self.digio_line_key(line)
        owner = self.device_communication.get(key)
        if owner is not None and owner != self.smu:
            msg = (
                f"Trigger out line {line} is already used by the list sweep of {owner}. Please use a different "
                "trigger out line for each channel."
            )
            raise ValueError(msg)
        self.device_communication[key] = self.smu

    def release_digio_line(self, line: int) -> bool:
        """Release a digital I/O line that this channel claimed; return whether it was this channel's line."""
        key = self.digio_line_key(line)
        if self.device_communication.get(key) != self.smu:
            return False
        del self.device_communication[key]
        return True

    def send_list_values(self, values: list[float]) -> None:
        """Store the sweep values in a table on the instrument, in chunks so that each command stays short."""
        self.create_list_table(self.LIST_TABLE)
        for index in range(0, len(values), self.LIST_CHUNK_SIZE):
            self.append_list_values(self.LIST_TABLE, values[index : index + self.LIST_CHUNK_SIZE])

    def prepare_list_buffers(self) -> None:
        """Clear both reading buffers and collect timestamps with the current readings."""
        for buffer in ("nvbuffer1", "nvbuffer2"):
            self.clear_buffer(buffer)
            self.set_buffer_append_mode(buffer, False)
        self.set_buffer_collect_timestamps("nvbuffer1", True)

    def run_list_sweep(self) -> None:
        """Start the list sweep, wait until all points are measured, and read the results."""
        points = len(self.sweep_values)
        step_time = max(self.step_time, (self.measure_delay or 0.0) + self.nplc / self.LINE_FREQUENCY * self.average)
        stall_timeout = self.LIST_STALL_TIMEOUT + 3 * step_time

        self.clear_buffer("nvbuffer1")
        self.clear_buffer("nvbuffer2")
        self.initiate_trigger()

        self.list_results = (np.array([]), np.array([]), np.array([]))

        try:
            finished = self.wait_for_list_sweep(points, stall_timeout)
        except Exception:
            # The instrument would continue the sweep, e.g. after a failed read of the buffer count
            with contextlib.suppress(Exception):
                self.abort_sweep()
            raise
        if not finished:
            return

        # Successive sweeps without a new configuration can leave stale readings in the buffer cache
        self.clear_buffer_cache("nvbuffer1")
        self.clear_buffer_cache("nvbuffer2")
        currents, voltages, times = self.read_list_buffers(points)
        self.list_results = (voltages, currents, times)

    def wait_for_list_sweep(self, points: int, stall_timeout: float) -> bool:
        """Wait until the buffer holds all points; return False if the run was stopped, raise if the sweep stalls."""
        count = 0
        last_progress = time.perf_counter()
        while count < points:
            if self.is_run_stopped():
                self.abort_sweep()
                return False

            time.sleep(self.LIST_POLL_INTERVAL)
            new_count = self.get_buffer_count("nvbuffer1")
            if new_count > count:
                count = new_count
                last_progress = time.perf_counter()
            elif time.perf_counter() - last_progress > stall_timeout:
                self.abort_sweep()
                msg = (
                    f"The list sweep stopped after {count} of {points} points. If a hold time is used, the "
                    "measurement probably took longer than the hold time, e.g. due to auto ranging or the automatic "
                    "delay. Please increase the hold time or use a fixed range and delay time."
                )
                raise ValueError(msg)
        return True

    def list_sweep_results(self) -> list[np.ndarray]:
        """Return voltages, currents and times of the last list sweep, with invalid readings replaced by NaN."""
        voltages, currents, times = self.list_results

        invalid = (np.abs(voltages) > self.OVERFLOW_LIMIT) | (np.abs(currents) > self.OVERFLOW_LIMIT)
        voltages = np.where(invalid, np.nan, voltages)
        currents = np.where(invalid, np.nan, currents)

        return [voltages, currents, times]

    def autorange_constant(self, autorange: bool) -> str:
        """Return the TSP constant that belongs to the given auto range state."""
        return f"{self.smu}.{'AUTORANGE_ON' if autorange else 'AUTORANGE_OFF'}"

    def action_constant(self, enable: bool) -> str:
        """Return the TSP constant that enables or disables an action of the trigger model."""
        return f"{self.smu}.{'ENABLE' if enable else 'DISABLE'}"

    # Communication commands start here. They address the channel of this driver instance ('Channel' and
    # 'TSP-Link node'), except those that name a TSP-Link network, the error queue, a timer or a digital I/O line.

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the identification string of the instrument connected to the port."""
        return str(self.port.query("*IDN?"))

    @command(returns=("tsp_link_state",), reads="state")
    def get_tsp_link_state(self) -> str:
        """Return the state of the TSP-Link network, 'online' or 'offline'."""
        return str(self.port.query("print(tsplink.state)")).strip()

    @command
    def reset(self) -> None:
        """Reset the channel to its default configuration."""
        self.port.write(f"{self.smu}.reset()")

    @command
    def clear_error_queue(self) -> None:
        """Remove all entries from the error queue of the instrument."""
        self.port.write("errorqueue.clear()")

    @command(returns=("error_count",), reads="state")
    def get_error_count(self) -> int:
        """Return the number of entries in the error queue of the instrument."""
        return int(float(self.port.query("print(errorqueue.count)")))

    @command(returns=("error_code", "error_message"), reads="state")
    def get_next_error(self) -> tuple[int, str]:
        """Read the oldest entry of the error queue and return its error code and message."""
        # The answer contains error code, message, severity and node number, separated by tabs
        code, _, rest = str(self.port.query("print(errorqueue.next())")).strip().partition("\t")
        return int(float(code)), rest.split("\t")[0]

    @command
    def set_autozero_once(self) -> None:
        """Perform a single autozero and reuse its reference values for the following measurements."""
        self.port.write(f"{self.smu}.measure.autozero = {self.smu}.AUTOZERO_ONCE")

    @command
    def set_source_function(self, source_function: Quantity) -> None:
        """Set the source function to DC voltage or DC current."""
        output = "OUTPUT_DCVOLTS" if source_function == "Voltage" else "OUTPUT_DCAMPS"
        self.port.write(f"{self.smu}.source.func = {self.smu}.{output}")

    @command
    def set_display_measure_function(self, display_measure_function: Quantity) -> None:
        """Set the quantity that is shown on the display of the instrument."""
        measure = "MEASURE_DCVOLTS" if display_measure_function == "Voltage" else "MEASURE_DCAMPS"
        self.port.write(f"{self.node_prefix}display.{self.smu_ab}.measure.func = {self.node_prefix}display.{measure}")

    @command
    def set_current_limit(self, current_limit: Amperes) -> None:
        """Set the current compliance in A that is used in voltage source mode."""
        self.port.write(f"{self.smu}.source.limiti = {current_limit}")

    @command
    def set_voltage_limit(self, voltage_limit: Volts) -> None:
        """Set the voltage compliance in V that is used in current source mode."""
        self.port.write(f"{self.smu}.source.limitv = {voltage_limit}")

    @command
    def set_source_autorange_voltage(self, source_autorange_voltage: bool) -> None:
        """Switch the auto range of the voltage source on or off."""
        self.port.write(f"{self.smu}.source.autorangev = {self.autorange_constant(source_autorange_voltage)}")

    @command
    def set_source_autorange_current(self, source_autorange_current: bool) -> None:
        """Switch the auto range of the current source on or off."""
        self.port.write(f"{self.smu}.source.autorangei = {self.autorange_constant(source_autorange_current)}")

    @command
    def set_measure_autorange_voltage(self, measure_autorange_voltage: bool) -> None:
        """Switch the auto range of the voltage measurement on or off."""
        self.port.write(f"{self.smu}.measure.autorangev = {self.autorange_constant(measure_autorange_voltage)}")

    @command
    def set_measure_autorange_current(self, measure_autorange_current: bool) -> None:
        """Switch the auto range of the current measurement on or off."""
        self.port.write(f"{self.smu}.measure.autorangei = {self.autorange_constant(measure_autorange_current)}")

    @command
    def set_measure_lowrange_current(self, measure_lowrange_current: Amperes) -> None:
        """Set the lowest current range in A that the auto range of the measurement may use."""
        self.port.write(f"{self.smu}.measure.lowrangei = {measure_lowrange_current:1.3e}")

    @command
    def set_measure_range_current(self, measure_range_current: Amperes) -> None:
        """Set the fixed current measurement range in A."""
        self.port.write(f"{self.smu}.measure.rangei = {measure_range_current:1.3e}")

    @command
    def set_measure_range_voltage(self, measure_range_voltage: Volts) -> None:
        """Set the fixed voltage measurement range in V."""
        self.port.write(f"{self.smu}.measure.rangev = {measure_range_voltage}")

    @command
    def set_source_range_voltage(self, source_range_voltage: Volts) -> None:
        """Set the fixed voltage source range in V."""
        self.port.write(f"{self.smu}.source.rangev = {source_range_voltage}")

    @command
    def set_source_range_current(self, source_range_current: Amperes) -> None:
        """Set the fixed current source range in A."""
        self.port.write(f"{self.smu}.source.rangei = {source_range_current}")

    @command
    def set_remote_sense(self, remote_sense: bool) -> None:
        """Switch between 4-wire (remote) and 2-wire (local) sensing."""
        sense = "SENSE_REMOTE" if remote_sense else "SENSE_LOCAL"
        self.port.write(f"{self.smu}.sense = {self.smu}.{sense}")

    @command
    def set_filter_count(self, filter_count: Annotated[int, Range(1, 100)]) -> None:
        """Set the number of readings that are averaged by the filter."""
        self.port.write(f"{self.smu}.measure.filter.count = {filter_count:d}")

    @command
    def set_filter_enabled(self, filter_enabled: bool) -> None:
        """Switch the averaging filter on or off."""
        filter_state = "FILTER_ON" if filter_enabled else "FILTER_OFF"
        self.port.write(f"{self.smu}.measure.filter.enable = {self.smu}.{filter_state}")

    @command
    def set_filter_repeat_average(self) -> None:
        """Use the repeating average as filter type."""
        self.port.write(f"{self.smu}.measure.filter.type = {self.smu}.FILTER_REPEAT_AVG")

    @command
    def set_nplc(self, nplc: float) -> None:
        """Set the integration time of the measurement in power line cycles.

        Values below the minimum of the instrument are set to the minimum by the instrument.
        """
        self.port.write(f"{self.smu}.measure.nplc = {nplc}")

    @command
    def set_output(self, output: bool) -> None:
        """Switch the output of the channel on or off."""
        self.port.write(f"{self.smu}.source.output = {int(output)}")

    @command
    def set_source_level_voltage(self, voltage: Volts) -> None:
        """Set the output voltage in V."""
        self.port.write(f"{self.smu}.source.levelv = {voltage}")

    @command
    def set_source_level_current(self, current: Amperes) -> None:
        """Set the output current in A."""
        self.port.write(f"{self.smu}.source.leveli = {current}")

    @command(returns=("voltage", "current"))
    def get_voltage_and_current(self) -> tuple[Volts, Amperes]:
        """Measure voltage in V and current in A."""
        current, voltage = self.parse_measurement(str(self.port.query(f"print({self.smu}.measure.iv())")))
        return voltage, current

    @command
    def set_measure_delay(self, measure_delay: Seconds | None) -> None:
        """Set the settling time in s before each measurement, None for the automatic delay."""
        delay = f"{self.smu}.DELAY_AUTO" if measure_delay is None else f"{measure_delay}"
        self.port.write(f"{self.smu}.measure.delay = {delay}")

    @command(kind="run")
    def create_list_table(self, table: str) -> None:
        """Create an empty table on the instrument that takes the sweep values."""
        self.port.write(f"{table} = {{}}")

    @command(kind="run")
    def append_list_values(self, table: str, list_values: list[float]) -> None:
        """Append sweep values to a table on the instrument."""
        numbers = ", ".join(f"{value:.9g}" for value in list_values)
        self.port.write(f"for _, v in ipairs({{{numbers}}}) do table.insert({table}, v) end")

    @command
    def set_trigger_source_list_voltage(self, voltage_list_table: str) -> None:
        """Use the voltages in V of a table on the instrument as source values of the sweep."""
        self.port.write(f"{self.smu}.trigger.source.listv({voltage_list_table})")

    @command
    def set_trigger_source_list_current(self, current_list_table: str) -> None:
        """Use the currents in A of a table on the instrument as source values of the sweep."""
        self.port.write(f"{self.smu}.trigger.source.listi({current_list_table})")

    @command
    def set_trigger_source_action(self, source_action: bool) -> None:
        """Switch the source action of the trigger model on or off."""
        self.port.write(f"{self.smu}.trigger.source.action = {self.action_constant(source_action)}")

    @command
    def set_trigger_measure_iv(self) -> None:
        """Measure current into reading buffer 1 and voltage into reading buffer 2 at each step of the sweep."""
        self.port.write(f"{self.smu}.trigger.measure.iv({self.smu}.nvbuffer1, {self.smu}.nvbuffer2)")

    @command
    def set_trigger_measure_action(self, measure_action: bool) -> None:
        """Switch the measure action of the trigger model on or off."""
        self.port.write(f"{self.smu}.trigger.measure.action = {self.action_constant(measure_action)}")

    @command
    def set_trigger_endpulse_hold(self) -> None:
        """Keep the source level until the next step of the sweep, i.e. no pulsed sweep."""
        self.port.write(f"{self.smu}.trigger.endpulse.action = {self.smu}.SOURCE_HOLD")

    @command
    def set_trigger_endsweep_idle(self) -> None:
        """Return the source to its idle level at the end of the sweep."""
        self.port.write(f"{self.smu}.trigger.endsweep.action = {self.smu}.SOURCE_IDLE")

    @command
    def set_trigger_count(self, trigger_count: int) -> None:
        """Set the number of steps of the sweep."""
        self.port.write(f"{self.smu}.trigger.count = {trigger_count:d}")

    @command
    def set_trigger_arm_count(self, arm_count: int) -> None:
        """Set how often the sweep is repeated after it was started."""
        self.port.write(f"{self.smu}.trigger.arm.count = {arm_count:d}")

    @command
    def set_trigger_source_stimulus(self, source_stimulus: str) -> None:
        """Set the event that starts each source step, '0' to step without waiting."""
        self.port.write(f"{self.smu}.trigger.source.stimulus = {source_stimulus}")

    @command
    def reset_timer(self, timer: Timer) -> None:
        """Reset count, delay, pass-through and stimulus of a trigger timer."""
        self.port.write(f"trigger.timer[{timer:d}].reset()")

    @command
    def set_timer_delay(self, timer: Timer, timer_delay: Seconds) -> None:
        """Set the period in s of a trigger timer."""
        self.port.write(f"trigger.timer[{timer:d}].delay = {timer_delay}")

    @command
    def set_timer_count(self, timer: Timer, timer_count: int) -> None:
        """Set the number of events a trigger timer creates after it was started."""
        self.port.write(f"trigger.timer[{timer:d}].count = {timer_count:d}")

    @command
    def set_timer_passthrough(self, timer: Timer, timer_passthrough: bool) -> None:
        """Let a trigger timer create an event already when it is started."""
        self.port.write(f"trigger.timer[{timer:d}].passthrough = {str(timer_passthrough).lower()}")

    @command
    def set_timer_stimulus(self, timer: Timer, timer_stimulus: str) -> None:
        """Set the event that starts a trigger timer."""
        self.port.write(f"trigger.timer[{timer:d}].stimulus = {timer_stimulus}")

    @command
    def reset_digio_trigger(self, line: DigioLine) -> None:
        """Reset the trigger settings of a digital I/O line, which also switches off its output trigger."""
        self.port.write(f"digio.trigger[{line:d}].reset()")

    @command
    def set_digio_trigger_mode(self, line: DigioLine, digio_trigger_mode: str) -> None:
        """Set the trigger mode of a digital I/O line, e.g. 'TRIG_FALLING' for a low pulse as output trigger."""
        self.port.write(f"digio.trigger[{line:d}].mode = digio.{digio_trigger_mode}")

    @command
    def set_digio_trigger_pulsewidth(self, line: DigioLine, digio_pulse_width: Seconds) -> None:
        """Set the length in s of the output trigger pulse of a digital I/O line."""
        self.port.write(f"digio.trigger[{line:d}].pulsewidth = {digio_pulse_width}")

    @command
    def set_digio_trigger_stimulus(self, line: DigioLine, digio_stimulus: str) -> None:
        """Set the event that asserts the output trigger of a digital I/O line."""
        self.port.write(f"digio.trigger[{line:d}].stimulus = {digio_stimulus}")

    @command
    def clear_buffer(self, buffer: Buffer) -> None:
        """Remove all readings from a reading buffer of the channel."""
        self.port.write(f"{self.smu}.{buffer}.clear()")

    @command
    def clear_buffer_cache(self, buffer: Buffer) -> None:
        """Remove stale readings from the cache of a reading buffer of the channel."""
        self.port.write(f"{self.smu}.{buffer}.clearcache()")

    @command
    def set_buffer_append_mode(self, buffer: Buffer, append_mode: bool) -> None:
        """Define whether new readings are appended to a reading buffer or replace its readings."""
        self.port.write(f"{self.smu}.{buffer}.appendmode = {int(append_mode)}")

    @command
    def set_buffer_collect_timestamps(self, buffer: Buffer, collect_timestamps: bool) -> None:
        """Define whether a reading buffer stores a timestamp with each reading; the buffer must be empty."""
        self.port.write(f"{self.smu}.{buffer}.collecttimestamps = {int(collect_timestamps)}")

    @command
    def set_buffer_collect_source_values(self, buffer: Buffer, collect_source_values: bool) -> None:
        """Define whether a reading buffer stores the source value with each reading."""
        self.port.write(f"{self.smu}.{buffer}.collectsourcevalues = {int(collect_source_values)}")

    @command(returns=("buffer_count",), reads="state")
    def get_buffer_count(self, buffer: Buffer) -> int:
        """Return the number of readings in a reading buffer of the channel."""
        return int(float(self.port.query(f"print({self.smu}.{buffer}.n)")))

    @command
    def initiate_trigger(self) -> None:
        """Start the sweep that was set up in the trigger model."""
        self.port.write(f"{self.smu}.trigger.initiate()")

    @command
    def abort_sweep(self) -> None:
        """Stop a running sweep of the channel."""
        self.port.write(f"{self.smu}.abort()")

    @command(returns=("current", "voltage", "time"), reads="last")
    def read_list_buffers(self, points: int) -> tuple[CurrentArray, VoltageArray, TimeArray]:
        """Read currents in A, voltages in V and times in s of the first points of the two reading buffers."""
        answer = self.port.query(
            f"printbuffer(1, {points:d}, {self.smu}.nvbuffer1.readings, {self.smu}.nvbuffer2.readings, "
            f"{self.smu}.nvbuffer1.timestamps)",
        )
        # The values of the three buffers are interleaved point by point
        values = np.array([float(value) for value in str(answer).replace("\n", "").split(",")])
        values = values.reshape(-1, 3)
        return values[:, 0], values[:, 1], values[:, 2]
