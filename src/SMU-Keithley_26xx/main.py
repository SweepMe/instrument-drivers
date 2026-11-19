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

from __future__ import annotations

import re
import time
from typing import Any, ClassVar

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the Keithley 26xx series source measure units using the TSP command set."""

    # Conversion of the SI prefixes used in the range options into exponents
    PREFIX_CONVERSION: ClassVar[dict[str, str]] = {
        "m": "e-3",
        "µ": "e-6",
        "n": "e-9",
        "p": "e-12",
    }

    # Integration time in power line cycles belonging to each speed option
    SPEED_TO_NPLC: ClassVar[dict[str, float]] = {
        "Fast": 0.1,
        "Medium": 1.0,
        "Slow": 10.0,
    }

    # Current ranges that can be used for the measurement
    CURRENT_RANGES = ("1A", "100mA", "10mA", "1mA", "100µA", "10µA", "1µA", "100nA", "10nA", "1nA", "100pA")

    # Readings above this value are returned by the instrument if the measurement is not valid
    OVERFLOW_LIMIT = 1e37

    # Limits of the pulse on and off times that are supported by the instrument
    MIN_PULSE_TIME = 200e-6
    MAX_PULSE_OFF_TIME = 3.0
    DEFAULT_PULSE_OFF_TIME = 200e-3

    # Number of channels that must share the port so that the dual pulse mode can be used
    DUAL_PULSE_NR_DEVICES = 2

    # Option of the 'TSP-Link node' field that addresses the instrument connected to the port
    LOCAL_NODE = "Local"

    # Highest node number that can be used in a TSP-Link network
    MAX_TSP_LINK_NODE = 64

    # Option of the 'SweepValue' field that the SMU module adds when the driver returns the 'ListSweepCheck' key
    LIST_SWEEP = "List sweep"

    # Options of the 'ListSweepStepPointsType' field
    STEP_WIDTH = "Step width"
    POINTS_LINEAR = "Points (lin.)"
    POINTS_LOG = "Points (log.)"

    # Number of sweep values that are sent to the instrument with one command, so that a command stays short
    LIST_CHUNK_SIZE = 50

    # Name of the Lua table on the instrument that holds the sweep values
    LIST_TABLE = "sweepme_list"

    # Highest line number of the digital I/O port that can be used as output trigger
    MAX_DIGIO_LINE = 14

    # Option of the 'Trigger out line' field that disables the output trigger
    NO_TRIGGER_OUT = "None"

    # Trigger events of the SMU that can assert the output trigger, as TSP constant of the trigger model
    TRIGGER_OUT_EVENTS: ClassVar[dict[str, str]] = {
        "Source complete": "SOURCE_COMPLETE_EVENT_ID",
        "Measure complete": "MEASURE_COMPLETE_EVENT_ID",
    }

    # Pulse shape of the output trigger, as digio trigger mode
    TRIGGER_OUT_POLARITIES: ClassVar[dict[str, str]] = {
        "Low pulse": "TRIG_FALLING",
        "High pulse": "TRIG_RISINGM",
    }

    # Models without digital I/O trigger lines
    NO_DIGIO_TRIGGER_MODELS = ("2604B", "2614B", "2634B")

    # Polling interval in s while a list sweep runs
    LIST_POLL_INTERVAL = 0.05

    # Time in s without a new reading after which a running list sweep is considered stuck, added to three steps
    LIST_STALL_TIMEOUT = 5.0

    # Line frequency in Hz that is used to estimate the integration time, 50 Hz gives the longer time
    LINE_FREQUENCY = 50.0

    def __init__(self) -> None:
        """Initialize the driver, the returned variables and the port configuration."""
        EmptyDevice.__init__(self)

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
            # AF@04.08.20: delay maybe needed for TCPIP communication
            # as it seems that some commands are lost
            # "delay": 0.01,  # noqa: ERA001
        }

        self.port_identifications = ["Keithley Instruments,26", "Keithley Instruments Inc., Model 26"]

        # Set in get_GUIparameter
        self.source: str = "Voltage in V"
        self.channel: str = "Ch A"
        self.smu_ab: str = "smua"
        self.tsp_link_node: str = self.LOCAL_NODE
        self.node_number: int | None = None
        """TSP-Link node number of the channel, None if the instrument connected to the port is used."""
        self.node_prefix: str = ""
        """Prefix such as 'node[3].' for commands to a remote TSP-Link node, empty for the local node."""
        self.smu: str = "smua"
        """Full TSP name of the channel, e.g. 'smua' or 'node[3].smua'."""
        self.four_wire: bool = False
        self.route_out: str = "Rear"
        self.protection: float = 100e-6
        self.speed: str = "Fast"
        self.average: int = 1
        self.current_range: str = "Auto"
        self.current_autorange: bool = True
        self.current_autorange_lowlimit: float | None = None
        self.current_range_value: float = 1.0

        # Pulse mode parameters, set in get_GUIparameter
        self.pulse_mode: bool = False
        self.pulse_meas_time: float = 200e-6
        self.ton: float = 200e-6
        self.toff: float = 200e-3
        self.pulseofflevel: float = 0.0

        # List sweep parameters, set in get_GUIparameter and converted in configure. The list sweep is used if
        # 'List sweep' is selected as sweep value; the instrument then runs the whole sweep by itself.
        self.list_sweep: bool = False
        self.list_parameters: dict[str, Any] = {}

        # List sweep values after conversion in configure: the time in s between two sweep points (0 to step as fast
        # as possible), the settling time in s before each measurement (None for the automatic delay), and the digital
        # I/O line (None without output trigger) and pulse width in s of the output trigger
        self.sweep_values: list[float] = []
        self.step_time: float = 0.0
        self.measure_delay: float | None = None
        self.digio_line: int | None = None
        self.digio_pulse_width: float = 10e-6

        # Voltages in V, currents in A and times in s of the last list sweep
        self.list_results: tuple[np.ndarray, np.ndarray, np.ndarray] = (np.array([]), np.array([]), np.array([]))

        # Set during the run
        self.nplc: float = 1.0
        self.tag: str = "1"
        self.master: bool = False
        self.dualpulse: bool = False

        # Tells whether this instance is already counted as user of the shared port
        self.port_manager_registered: bool = False

    def set_GUIparameter(self) -> dict[str, Any]:  # noqa: N802
        """Return the fields that are shown in the graphical user interface."""
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["Ch A", "Ch B"],
            "TSP-Link node": self.get_node_options(),
            "4wire": False,
            "RouteOut": ["Rear"],
            "Speed": list(self.SPEED_TO_NPLC.keys()),
            "Range": self.get_range_options(),
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
            "ListSweepStepPointsType": [self.STEP_WIDTH, self.POINTS_LINEAR, self.POINTS_LOG],
            "ListSweepStepPointsValue": 0.1,
            "ListSweepDual": False,
            "ListSweepCustomValues": "",
            "ListSweepHoldtime": 0.1,
            "ListSweepDelaytime": "",
            "Trigger out line": [self.NO_TRIGGER_OUT, *[str(line) for line in range(1, self.MAX_DIGIO_LINE + 1)]],
            "Trigger out event": list(self.TRIGGER_OUT_EVENTS),
            "Trigger out polarity": list(self.TRIGGER_OUT_POLARITIES),
            "Trigger out pulse width in s": 10e-6,
        }

    def get_GUIparameter(self, parameter: dict[str, Any]) -> None:  # noqa: N802
        """Take over the parameters that were chosen by the user in the graphical user interface."""
        self.source = parameter.get("SweepMode", "Voltage in V")
        self.channel = parameter.get("Channel", "Ch A")
        self.four_wire = bool(parameter.get("4wire", False))
        self.route_out = parameter.get("RouteOut", "Rear")
        self.protection = float(parameter.get("Compliance", 100e-6))
        self.speed = parameter.get("Speed", "Fast")
        self.average = int(parameter.get("Average", 1))

        self.current_range = parameter.get("Range", "Auto")
        self.current_autorange = True
        self.current_autorange_lowlimit = None

        if self.current_range.startswith("Limited"):
            # Auto ranging is used, but the instrument must not range below the given value
            self.current_autorange_lowlimit = self.get_range_value(self.current_range)
        elif self.current_range.startswith("Fixed"):
            self.current_autorange = False
            self.current_range_value = self.get_range_value(self.current_range)

        # Pulse Mode Parameters
        self.pulse_mode = bool(parameter.get("CheckPulse", False))

        if self.pulse_mode:
            self.pulse_meas_time = float(parameter.get("PulseMeasTime", 200e-6))
            self.ton = round(float(parameter.get("PulseOnTime", 200e-6)), 6)
            self.toff = float(parameter.get("PulseOffTime", 200e-3))
            self.pulseofflevel = float(parameter.get("PulseOffLevel", 0.0))

        # List sweep parameters, kept as text and converted in 'configure' where wrong entries can be reported
        self.list_sweep = parameter.get("SweepValue", "") == self.LIST_SWEEP

        if self.list_sweep:
            self.list_parameters = {
                key: value for key, value in parameter.items() if key.startswith(("ListSweep", "Trigger out"))
            }

            # Each point of the sweep comes with the time at which it was measured
            self.variables = ["Voltage", "Current", "Time"]
            self.units = ["V", "A", "s"]
            self.plottype = [True, True, True]
            self.savetype = [True, True, True]
        else:
            self.variables = ["Voltage", "Current"]
            self.units = ["V", "A"]
            self.plottype = [True, True]
            self.savetype = [True, True]

        self.smu_ab = "smua" if self.channel[-1] == "A" else "smub"

        # Older settings do not have this field and use the local node
        self.tsp_link_node = str(parameter.get("TSP-Link node", self.LOCAL_NODE))
        try:
            self.node_number = self.get_node_number(self.tsp_link_node)
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
        """Identify the instrument and find out whether this instance is the master of the shared port."""
        if self.node_number is None:
            self.update_master_state()
        self.port.port.write_termination = "\n"

    def initialize(self) -> None:
        """Check the TSP-Link node, reset the channel, clear the error queue and set the autozero mode."""
        # Stops the run if the option of the 'TSP-Link node' field is not valid
        self.get_node_number(self.tsp_link_node)

        if self.node_number is not None:
            self.check_remote_node()

        if self.list_sweep:
            self.check_list_sweep_support()

        if self.pulse_mode:
            self.limit_pulse_times()
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
        self.nplc = self.SPEED_TO_NPLC[self.speed]
        self.set_nplc(self.nplc)

        if self.list_sweep:
            self.convert_list_sweep_parameters()
            self.configure_list_sweep()

    def unconfigure(self) -> None:
        """Release the output trigger and the timer of a list sweep and remove this instance from the port users."""
        if self.list_sweep:
            self.unconfigure_list_sweep()

        if self.node_number is not None:
            # Channels on remote nodes are not counted, see 'register_port_usage'
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
            self.apply_pulse()
        elif self.source.startswith("Voltage"):
            self.set_source_level_voltage(float(self.value))
        else:
            self.set_source_level_current(float(self.value))

    def trigger_ready(self) -> None:
        """Start the pulse if the pulse mode is used."""
        if not self.pulse_mode:
            return

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
            self.measure_pulse()
        else:
            self.request_measurement()

    def call(self) -> list[float] | list[np.ndarray]:
        """Return the measured voltage in V and current in A, and in a list sweep the time in s of each point."""
        if self.list_sweep:
            return self.get_list_sweep_results()

        if self.pulse_mode:
            voltage, current = self.read_pulse_results()
        else:
            current, voltage = self.read_measurement()

        if abs(voltage) > self.OVERFLOW_LIMIT or abs(current) > self.OVERFLOW_LIMIT:
            return [float("nan"), float("nan")]

        return [voltage, current]

    """ here, further functions start that are used by the semantic standard functions """

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

    def get_range_options(self) -> list[str]:
        """Return the current range options that are shown in the graphical user interface.

        "Limited" uses auto ranging with a lowest allowed range, "Fixed" uses a fixed measurement range.
        """
        limited = [f"Limited {value}" for value in self.CURRENT_RANGES]
        fixed = [f"Fixed {value}" for value in self.CURRENT_RANGES]

        return ["Auto", *limited, *fixed]

    def get_range_value(self, range_option: str) -> float:
        """Convert a range option such as 'Limited 100µA' into a current in A."""
        value = range_option.split()[1]

        for prefix, exponent in self.PREFIX_CONVERSION.items():
            value = value.replace(prefix, exponent)

        return float(value.replace("A", ""))

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
        elif self.source.startswith("Current"):
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
        """Switch on the repeating average filter if more than one reading is averaged."""
        if self.average > 1:
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
        if self.ton < self.MIN_PULSE_TIME:
            self.ton = self.MIN_PULSE_TIME
        if self.toff < self.MIN_PULSE_TIME:
            self.toff = self.DEFAULT_PULSE_OFF_TIME
        if self.toff > self.MAX_PULSE_OFF_TIME:
            self.toff = self.MAX_PULSE_OFF_TIME

    def apply_pulse(self) -> None:
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

        self.port.write(f"{self.smu}.nvbuffer1.clear()")
        self.port.write(f"{self.smu}.nvbuffer1.appendmode = 1")
        self.set_nplc(self.nplc)
        self.port.write(f"{self.smu}.nvbuffer1.collectsourcevalues = 1")

        level = float(self.value)

        if self.source.startswith("Voltage"):
            self.port.write(f"{self.smu}.source.rangev = {self.protection}")
            self.port.write(f"{self.smu}.measure.rangei = {self.protection}")
            self.port.write(
                f"print(ConfigPulseVMeasureI({self.smu}, {self.pulseofflevel}, {level}, {self.protection}, "
                f"{ton}, {self.toff}, {self.average}, {self.smu}.nvbuffer1, {self.tag}))",
            )
        else:
            self.port.write(f"{self.smu}.source.rangei = {self.protection}")
            self.port.write(f"{self.smu}.measure.rangev = {self.protection}")
            self.port.write(
                f"print(ConfigPulseIMeasureV({self.smu}, {self.pulseofflevel}, {level}, {self.protection}, "
                f"{ton}, {self.toff}, {self.average}, {self.smu}.nvbuffer1, {self.tag}))",
            )

        self.port.read()  # remove answer from buffer

    def measure_pulse(self) -> None:
        """Read the answer of the pulse initiation and request the readings of the pulse buffers."""
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

    def read_pulse_results(self) -> tuple[float, float]:
        """Read the pulse buffers and return the averaged voltage in V and current in A."""
        if self.dualpulse:
            if self.master:
                # read all values of smua and smub if dualpulse
                readings_a = self.read_buffer_values()
                sources_a = self.read_buffer_values()
                readings_b = self.read_buffer_values()
                sources_b = self.read_buffer_values()

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
            readings = self.read_buffer_values()
            sources = self.read_buffer_values()

        # Depending on VOLT or CURR mode as source, voltage or current corresponds to .readings or .sourcevalues
        if self.source.startswith("Voltage"):
            return float(np.average(sources)), float(np.average(readings))

        return float(np.average(readings)), float(np.average(sources))

    def read_buffer_values(self) -> list[float]:
        """Read one comma separated list of buffer values from the port."""
        return [float(value) for value in self.port.read().replace("\n", "").split(",")]

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

        if str(self.list_parameters.get("Trigger out line", self.NO_TRIGGER_OUT)) != self.NO_TRIGGER_OUT:
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
        parameters = self.list_parameters

        if parameters.get("ListSweepType", "Sweep") == "Custom":
            self.sweep_values = self.parse_custom_values(str(parameters.get("ListSweepCustomValues", "")))
        else:
            self.sweep_values = self.calculate_sweep_values(
                str(parameters.get("ListSweepStart", "0.0")),
                str(parameters.get("ListSweepEnd", "1.0")),
                str(parameters.get("ListSweepStepPointsType", self.STEP_WIDTH)),
                str(parameters.get("ListSweepStepPointsValue", "0.1")),
            )
            if parameters.get("ListSweepDual", False):
                # The end value is only used once
                self.sweep_values = [*self.sweep_values, *self.sweep_values[-2::-1]]

        self.step_time = self.convert_time(parameters.get("ListSweepHoldtime", "0.1"), "Hold time") or 0.0
        self.measure_delay = self.convert_time(parameters.get("ListSweepDelaytime", ""), "Delay time")

        integration_time = self.nplc / self.LINE_FREQUENCY * self.average
        settling_time = (self.measure_delay or 0.0) + integration_time
        if 0 < self.step_time < settling_time:
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

        self.digio_line = int(line)
        pulse_width = self.convert_time(
            parameters.get("Trigger out pulse width in s", 10e-6),
            "Trigger out pulse width",
        )
        self.digio_pulse_width = pulse_width or 10e-6

    def get_timer_number(self) -> int:
        """Return the trigger timer that paces the list sweep; each channel uses its own timer."""
        return 1 if self.smu_ab == "smua" else 2

    def calculate_sweep_values(
        self,
        start_text: str,
        end_text: str,
        steppoints_type: str,
        steppoints_text: str,
    ) -> list[float]:
        """Calculate the sweep values from start value, end value and step width or number of points."""
        try:
            start = float(start_text)
            end = float(end_text)
            steppoints = float(steppoints_text)
        except ValueError:
            msg = "Start value, end value and step width or points of the list sweep must be numbers."
            raise ValueError(msg) from None

        if steppoints_type.startswith(self.STEP_WIDTH):
            if steppoints == 0.0:
                if start != end:
                    msg = "The step width of the list sweep must not be 0 if start and end value differ."
                    raise ValueError(msg)
                return [start]

            # The sweep stops at the last step that does not go beyond the end value
            step = abs(steppoints) if end >= start else -abs(steppoints)
            points = int(np.floor(abs(end - start) / abs(step) + 1e-9)) + 1
            return [start + step * index for index in range(points)]

        points = int(steppoints)
        if points < 1 or points != steppoints:
            msg = f"The number of points of the list sweep must be a positive integer, but is {steppoints}."
            raise ValueError(msg)

        if steppoints_type.startswith(self.POINTS_LOG):
            if start * end <= 0:
                msg = "Start and end value of a logarithmic list sweep must have the same sign and must not be 0."
                raise ValueError(msg)
            return [float(value) for value in np.geomspace(start, end, points)]

        return [float(value) for value in np.linspace(start, end, points)]

    @staticmethod
    def parse_custom_values(text: str) -> list[float]:
        """Convert custom values, separated by commas, semicolons or line breaks, into a list of floats."""
        entries = [entry for entry in re.split(r"[,;\s]+", text) if entry]
        if not entries:
            msg = "Please enter the custom values of the list sweep, separated by commas."
            raise ValueError(msg)

        try:
            return [float(entry) for entry in entries]
        except ValueError:
            msg = "The custom values of the list sweep must be numbers separated by commas."
            raise ValueError(msg) from None

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

        if value < 0:
            msg = f"The {name} of the list sweep must not be negative, but is {value} s."
            raise ValueError(msg)

        return value

    def configure_list_sweep(self) -> None:
        """Set up the trigger model so that the instrument steps through the sweep values by itself.

        Each step is started by a trigger timer with the hold time as period, or immediately after the previous
        measurement if no hold time is given. At each step, the source value is set, the delay time is waited and
        current and voltage are measured into the two reading buffers. The output trigger is asserted at each step.
        """
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

        timer = self.get_timer_number()
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
            polarity = str(self.list_parameters.get("Trigger out polarity", "Low pulse"))
            event = str(self.list_parameters.get("Trigger out event", "Source complete"))

            self.reset_digio_trigger(self.digio_line)
            self.set_digio_trigger_mode(self.digio_line, self.TRIGGER_OUT_POLARITIES.get(polarity, "TRIG_FALLING"))
            self.set_digio_trigger_pulsewidth(self.digio_line, self.digio_pulse_width)
            event_id = self.TRIGGER_OUT_EVENTS.get(event, "SOURCE_COMPLETE_EVENT_ID")
            self.set_digio_trigger_stimulus(self.digio_line, f"{self.smu}.trigger.{event_id}")

    def unconfigure_list_sweep(self) -> None:
        """Release the output trigger line and the timer that were used by the list sweep."""
        if self.digio_line is not None:
            self.reset_digio_trigger(self.digio_line)
        self.reset_timer(self.get_timer_number())

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

        count = 0
        last_progress = time.perf_counter()
        while count < points:
            if self.is_run_stopped():
                self.abort_sweep()
                return

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

        currents, voltages, times = self.read_list_buffers(points)
        self.list_results = (voltages, currents, times)

    def get_list_sweep_results(self) -> list[np.ndarray]:
        """Return voltages, currents and times of the last list sweep, with invalid readings replaced by NaN."""
        voltages, currents, times = self.list_results

        invalid = (np.abs(voltages) > self.OVERFLOW_LIMIT) | (np.abs(currents) > self.OVERFLOW_LIMIT)
        voltages = np.where(invalid, np.nan, voltages)
        currents = np.where(invalid, np.nan, currents)

        return [voltages, currents, times]

    """ here, communication commands are wrapped into python convenience functions """

    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        self.port.write("*IDN?")
        return self.port.read()

    def get_tsp_link_state(self) -> str:
        """Return the state of the TSP-Link network, 'online' or 'offline'."""
        self.port.write("print(tsplink.state)")
        return self.port.read().strip()

    def reset(self) -> None:
        """Reset the channel to its default configuration."""
        self.port.write(f"{self.smu}.reset()")

    def clear_error_queue(self) -> None:
        """Remove all entries from the error queue of the instrument."""
        self.port.write("errorqueue.clear()")

    def get_error_count(self) -> int:
        """Return the number of entries in the error queue of the instrument."""
        self.port.write("print(errorqueue.count)")
        return int(float(self.port.read()))

    def get_next_error(self) -> tuple[int, str]:
        """Read the oldest entry of the error queue and return its error code and message."""
        self.port.write("print(errorqueue.next())")
        # The answer contains error code, message, severity and node number, separated by tabs
        code, _, rest = self.port.read().strip().partition("\t")
        return int(float(code)), rest.split("\t")[0]

    def set_autozero_once(self) -> None:
        """Perform a single autozero and reuse its reference values for the following measurements."""
        self.port.write(f"{self.smu}.measure.autozero = {self.smu}.AUTOZERO_ONCE")

    def set_source_function(self, function: str) -> None:
        """Set the source function to DC voltage or DC current."""
        output = "OUTPUT_DCVOLTS" if function.startswith("Voltage") else "OUTPUT_DCAMPS"
        self.port.write(f"{self.smu}.source.func = {self.smu}.{output}")

    def set_display_measure_function(self, function: str) -> None:
        """Set the quantity that is shown on the display of the instrument."""
        measure = "MEASURE_DCVOLTS" if function.startswith("Voltage") else "MEASURE_DCAMPS"
        self.port.write(f"{self.node_prefix}display.{self.smu_ab}.measure.func = {self.node_prefix}display.{measure}")

    def set_current_limit(self, limit: float) -> None:
        """Set the current compliance in A that is used in voltage source mode."""
        self.port.write(f"{self.smu}.source.limiti = {limit}")

    def set_voltage_limit(self, limit: float) -> None:
        """Set the voltage compliance in V that is used in current source mode."""
        self.port.write(f"{self.smu}.source.limitv = {limit}")

    def set_source_autorange_voltage(self, state: bool) -> None:
        """Switch the auto range of the voltage source on or off."""
        self.port.write(f"{self.smu}.source.autorangev = {self.smu}.{self.get_autorange_state(state)}")

    def set_source_autorange_current(self, state: bool) -> None:
        """Switch the auto range of the current source on or off."""
        self.port.write(f"{self.smu}.source.autorangei = {self.smu}.{self.get_autorange_state(state)}")

    def set_measure_autorange_voltage(self, state: bool) -> None:
        """Switch the auto range of the voltage measurement on or off."""
        self.port.write(f"{self.smu}.measure.autorangev = {self.smu}.{self.get_autorange_state(state)}")

    def set_measure_autorange_current(self, state: bool) -> None:
        """Switch the auto range of the current measurement on or off."""
        self.port.write(f"{self.smu}.measure.autorangei = {self.smu}.{self.get_autorange_state(state)}")

    @staticmethod
    def get_autorange_state(state: bool) -> str:
        """Return the name of the TSP constant that belongs to the given auto range state."""
        return "AUTORANGE_ON" if state else "AUTORANGE_OFF"

    def set_measure_lowrange_current(self, lowrange: float) -> None:
        """Set the lowest current range in A that the auto range of the measurement may use."""
        self.port.write(f"{self.smu}.measure.lowrangei = {lowrange:1.3e}")

    def set_measure_range_current(self, current_range: float) -> None:
        """Set the fixed current measurement range in A."""
        self.port.write(f"{self.smu}.measure.rangei = {current_range:1.3e}")

    def set_remote_sense(self, state: bool) -> None:
        """Switch between 4-wire (remote) and 2-wire (local) sensing."""
        sense = "SENSE_REMOTE" if state else "SENSE_LOCAL"
        self.port.write(f"{self.smu}.sense = {self.smu}.{sense}")

    def set_filter_count(self, count: int) -> None:
        """Set the number of readings that are averaged by the filter."""
        self.port.write(f"{self.smu}.measure.filter.count = {count:d}")

    def set_filter_enabled(self, state: bool) -> None:
        """Switch the averaging filter on or off."""
        filter_state = "FILTER_ON" if state else "FILTER_OFF"
        self.port.write(f"{self.smu}.measure.filter.enable = {self.smu}.{filter_state}")

    def set_filter_repeat_average(self) -> None:
        """Use the repeating average as filter type."""
        self.port.write(f"{self.smu}.measure.filter.type = {self.smu}.FILTER_REPEAT_AVG")

    def set_nplc(self, nplc: float) -> None:
        """Set the integration time of the measurement in power line cycles."""
        self.port.write(f"{self.smu}.measure.nplc = {nplc}")

    def set_output(self, state: bool) -> None:
        """Switch the output of the channel on or off."""
        self.port.write(f"{self.smu}.source.output = {int(state)}")

    def set_source_level_voltage(self, value: float) -> None:
        """Set the output voltage in V."""
        self.port.write(f"{self.smu}.source.levelv = {value}")

    def set_source_level_current(self, value: float) -> None:
        """Set the output current in A."""
        self.port.write(f"{self.smu}.source.leveli = {value}")

    def request_measurement(self) -> None:
        """Request a combined current and voltage measurement."""
        self.port.write(f"print({self.smu}.measure.iv())")

    def read_measurement(self) -> tuple[float, float]:
        """Read the current in A and the voltage in V of the requested measurement."""
        current, voltage = (float(value) for value in self.port.read().split())
        return current, voltage

    def set_measure_delay(self, delay: float | None) -> None:
        """Set the settling time in s before each measurement, None for the automatic delay."""
        value = f"{self.smu}.DELAY_AUTO" if delay is None else f"{delay}"
        self.port.write(f"{self.smu}.measure.delay = {value}")

    def create_list_table(self, table: str) -> None:
        """Create an empty table on the instrument that takes the sweep values."""
        self.port.write(f"{table} = {{}}")

    def append_list_values(self, table: str, values: list[float]) -> None:
        """Append sweep values to a table on the instrument."""
        numbers = ", ".join(f"{value:.9g}" for value in values)
        self.port.write(f"for _, v in ipairs({{{numbers}}}) do table.insert({table}, v) end")

    def set_trigger_source_list_voltage(self, table: str) -> None:
        """Use the voltages in V of a table on the instrument as source values of the sweep."""
        self.port.write(f"{self.smu}.trigger.source.listv({table})")

    def set_trigger_source_list_current(self, table: str) -> None:
        """Use the currents in A of a table on the instrument as source values of the sweep."""
        self.port.write(f"{self.smu}.trigger.source.listi({table})")

    def set_trigger_source_action(self, source_action: bool) -> None:
        """Switch the source action of the trigger model on or off."""
        self.port.write(f"{self.smu}.trigger.source.action = {self.smu}.{self.get_enable_state(source_action)}")

    def set_trigger_measure_iv(self) -> None:
        """Measure current into reading buffer 1 and voltage into reading buffer 2 at each step of the sweep."""
        self.port.write(f"{self.smu}.trigger.measure.iv({self.smu}.nvbuffer1, {self.smu}.nvbuffer2)")

    def set_trigger_measure_action(self, measure_action: bool) -> None:
        """Switch the measure action of the trigger model on or off."""
        self.port.write(f"{self.smu}.trigger.measure.action = {self.smu}.{self.get_enable_state(measure_action)}")

    @staticmethod
    def get_enable_state(state: bool) -> str:
        """Return the name of the TSP constant that enables or disables an action of the trigger model."""
        return "ENABLE" if state else "DISABLE"

    def set_trigger_endpulse_hold(self) -> None:
        """Keep the source level until the next step of the sweep, i.e. no pulsed sweep."""
        self.port.write(f"{self.smu}.trigger.endpulse.action = {self.smu}.SOURCE_HOLD")

    def set_trigger_endsweep_idle(self) -> None:
        """Return the source to its idle level at the end of the sweep."""
        self.port.write(f"{self.smu}.trigger.endsweep.action = {self.smu}.SOURCE_IDLE")

    def set_trigger_count(self, count: int) -> None:
        """Set the number of steps of the sweep."""
        self.port.write(f"{self.smu}.trigger.count = {count:d}")

    def set_trigger_arm_count(self, count: int) -> None:
        """Set how often the sweep is repeated after it was started."""
        self.port.write(f"{self.smu}.trigger.arm.count = {count:d}")

    def set_trigger_source_stimulus(self, event: str) -> None:
        """Set the event that starts each source step, '0' to step without waiting."""
        self.port.write(f"{self.smu}.trigger.source.stimulus = {event}")

    def reset_timer(self, timer: int) -> None:
        """Reset count, delay, pass-through and stimulus of a trigger timer."""
        self.port.write(f"trigger.timer[{timer:d}].reset()")

    def set_timer_delay(self, timer: int, delay: float) -> None:
        """Set the period in s of a trigger timer."""
        self.port.write(f"trigger.timer[{timer:d}].delay = {delay}")

    def set_timer_count(self, timer: int, count: int) -> None:
        """Set the number of events a trigger timer creates after it was started."""
        self.port.write(f"trigger.timer[{timer:d}].count = {count:d}")

    def set_timer_passthrough(self, timer: int, passthrough: bool) -> None:
        """Let a trigger timer create an event already when it is started."""
        self.port.write(f"trigger.timer[{timer:d}].passthrough = {str(passthrough).lower()}")

    def set_timer_stimulus(self, timer: int, event: str) -> None:
        """Set the event that starts a trigger timer."""
        self.port.write(f"trigger.timer[{timer:d}].stimulus = {event}")

    def reset_digio_trigger(self, line: int) -> None:
        """Reset the trigger settings of a digital I/O line, which also switches off its output trigger."""
        self.port.write(f"digio.trigger[{line:d}].reset()")

    def set_digio_trigger_mode(self, line: int, trigger_mode: str) -> None:
        """Set the trigger mode of a digital I/O line, e.g. 'TRIG_FALLING' for a low pulse as output trigger."""
        self.port.write(f"digio.trigger[{line:d}].mode = digio.{trigger_mode}")

    def set_digio_trigger_pulsewidth(self, line: int, width: float) -> None:
        """Set the length in s of the output trigger pulse of a digital I/O line."""
        self.port.write(f"digio.trigger[{line:d}].pulsewidth = {width}")

    def set_digio_trigger_stimulus(self, line: int, event: str) -> None:
        """Set the event that asserts the output trigger of a digital I/O line."""
        self.port.write(f"digio.trigger[{line:d}].stimulus = {event}")

    def clear_buffer(self, buffer: str) -> None:
        """Remove all readings from a reading buffer of the channel, e.g. 'nvbuffer1'."""
        self.port.write(f"{self.smu}.{buffer}.clear()")

    def set_buffer_append_mode(self, buffer: str, append_mode: bool) -> None:
        """Define whether new readings are appended to a reading buffer or replace its readings."""
        self.port.write(f"{self.smu}.{buffer}.appendmode = {int(append_mode)}")

    def set_buffer_collect_timestamps(self, buffer: str, collect_timestamps: bool) -> None:
        """Define whether a reading buffer stores a timestamp with each reading; the buffer must be empty."""
        self.port.write(f"{self.smu}.{buffer}.collecttimestamps = {int(collect_timestamps)}")

    def get_buffer_count(self, buffer: str) -> int:
        """Return the number of readings in a reading buffer of the channel."""
        self.port.write(f"print({self.smu}.{buffer}.n)")
        return int(float(self.port.read()))

    def initiate_trigger(self) -> None:
        """Start the sweep that was set up in the trigger model."""
        self.port.write(f"{self.smu}.trigger.initiate()")

    def abort_sweep(self) -> None:
        """Stop a running sweep of the channel."""
        self.port.write(f"{self.smu}.abort()")

    def read_list_buffers(self, points: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Read currents in A, voltages in V and times in s of the first points of the two reading buffers."""
        self.port.write(
            f"printbuffer(1, {points:d}, {self.smu}.nvbuffer1.readings, {self.smu}.nvbuffer2.readings, "
            f"{self.smu}.nvbuffer1.timestamps)",
        )
        # The values of the three buffers are interleaved point by point
        values = np.array([float(value) for value in self.port.read().replace("\n", "").split(",")])
        values = values.reshape(-1, 3)
        return values[:, 0], values[:, 1], values[:, 2]
