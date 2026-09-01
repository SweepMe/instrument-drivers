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

        self.shortname = f"Keithley26xx Ch {self.channel[-1]}"
        self.smu_ab = "smua" if self.channel[-1] == "A" else "smub"

    def connect(self) -> None:
        """Identify the instrument and find out whether this instance is the master of the shared port."""
        self.update_master_state()
        self.port.port.write_termination = "\n"

    def initialize(self) -> None:
        """Reset the channel, clear the error queue and set the autozero mode."""
        if self.pulse_mode:
            self.limit_pulse_times()
            self.tag = "1" if self.smu_ab == "smua" else "2"

        self.reset()
        self.clear_error_queue()

        # Some devices have problems with this command, maybe because they are not the localnode
        # Should this driver get support for nodes in the future, one could include it again.
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

    def unconfigure(self) -> None:
        """Remove this instance from the users of the shared port."""
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
        """Request a current and voltage measurement, or request the pulse buffers in pulse mode."""
        if self.pulse_mode:
            self.measure_pulse()
        else:
            self.request_measurement()

    def call(self) -> list[float]:
        """Return the measured voltage in V and current in A."""
        if self.pulse_mode:
            voltage, current = self.read_pulse_results()
        else:
            current, voltage = self.read_measurement()

        if voltage > self.OVERFLOW_LIMIT or current > self.OVERFLOW_LIMIT:
            return [float("nan"), float("nan")]

        return [voltage, current]

    """ here, further functions start that are used by the semantic standard functions """

    def register_port_usage(self) -> None:
        """Count this instance as user of the shared port and update the master state."""
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

        self.port.write(f"{self.smu_ab}.nvbuffer1.clear()")
        self.port.write(f"{self.smu_ab}.nvbuffer1.appendmode = 1")
        self.set_nplc(self.nplc)
        self.port.write(f"{self.smu_ab}.nvbuffer1.collectsourcevalues = 1")

        level = float(self.value)

        if self.source.startswith("Voltage"):
            self.port.write(f"{self.smu_ab}.source.rangev = {self.protection}")
            self.port.write(f"{self.smu_ab}.measure.rangei = {self.protection}")
            self.port.write(
                f"print(ConfigPulseVMeasureI({self.smu_ab}, {self.pulseofflevel}, {level}, {self.protection}, "
                f"{ton}, {self.toff}, {self.average}, {self.smu_ab}.nvbuffer1, {self.tag}))",
            )
        else:
            self.port.write(f"{self.smu_ab}.source.rangei = {self.protection}")
            self.port.write(f"{self.smu_ab}.measure.rangev = {self.protection}")
            self.port.write(
                f"print(ConfigPulseIMeasureV({self.smu_ab}, {self.pulseofflevel}, {level}, {self.protection}, "
                f"{ton}, {self.toff}, {self.average}, {self.smu_ab}.nvbuffer1, {self.tag}))",
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

            self.port.write(f"printbuffer(1, {self.average}, {self.smu_ab}.nvbuffer1.readings)")
            self.port.write(f"printbuffer(1, {self.average}, {self.smu_ab}.nvbuffer1.sourcevalues)")

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

    """ here, communication commands are wrapped into python convenience functions """

    def get_identification(self) -> str:
        """Return the identification string of the instrument."""
        self.port.write("*IDN?")
        return self.port.read()

    def reset(self) -> None:
        """Reset the channel to its default configuration."""
        self.port.write(f"{self.smu_ab}.reset()")

    def clear_error_queue(self) -> None:
        """Remove all entries from the error queue of the instrument."""
        self.port.write("errorqueue.clear()")

    def set_autozero_once(self) -> None:
        """Perform a single autozero and reuse its reference values for the following measurements."""
        self.port.write(f"{self.smu_ab}.measure.autozero = {self.smu_ab}.AUTOZERO_ONCE")

    def set_source_function(self, function: str) -> None:
        """Set the source function to DC voltage or DC current."""
        output = "OUTPUT_DCVOLTS" if function.startswith("Voltage") else "OUTPUT_DCAMPS"
        self.port.write(f"{self.smu_ab}.source.func = {self.smu_ab}.{output}")

    def set_display_measure_function(self, function: str) -> None:
        """Set the quantity that is shown on the display of the instrument."""
        measure = "MEASURE_DCVOLTS" if function.startswith("Voltage") else "MEASURE_DCAMPS"
        self.port.write(f"display.{self.smu_ab}.measure.func = display.{measure}")

    def set_current_limit(self, limit: float) -> None:
        """Set the current compliance in A that is used in voltage source mode."""
        self.port.write(f"{self.smu_ab}.source.limiti = {limit}")

    def set_voltage_limit(self, limit: float) -> None:
        """Set the voltage compliance in V that is used in current source mode."""
        self.port.write(f"{self.smu_ab}.source.limitv = {limit}")

    def set_source_autorange_voltage(self, state: bool) -> None:
        """Switch the auto range of the voltage source on or off."""
        self.port.write(f"{self.smu_ab}.source.autorangev = {self.smu_ab}.{self.get_autorange_state(state)}")

    def set_source_autorange_current(self, state: bool) -> None:
        """Switch the auto range of the current source on or off."""
        self.port.write(f"{self.smu_ab}.source.autorangei = {self.smu_ab}.{self.get_autorange_state(state)}")

    def set_measure_autorange_voltage(self, state: bool) -> None:
        """Switch the auto range of the voltage measurement on or off."""
        self.port.write(f"{self.smu_ab}.measure.autorangev = {self.smu_ab}.{self.get_autorange_state(state)}")

    def set_measure_autorange_current(self, state: bool) -> None:
        """Switch the auto range of the current measurement on or off."""
        self.port.write(f"{self.smu_ab}.measure.autorangei = {self.smu_ab}.{self.get_autorange_state(state)}")

    @staticmethod
    def get_autorange_state(state: bool) -> str:
        """Return the name of the TSP constant that belongs to the given auto range state."""
        return "AUTORANGE_ON" if state else "AUTORANGE_OFF"

    def set_measure_lowrange_current(self, lowrange: float) -> None:
        """Set the lowest current range in A that the auto range of the measurement may use."""
        self.port.write(f"{self.smu_ab}.measure.lowrangei = {lowrange:1.3e}")

    def set_measure_range_current(self, current_range: float) -> None:
        """Set the fixed current measurement range in A."""
        self.port.write(f"{self.smu_ab}.measure.rangei = {current_range:1.3e}")

    def set_remote_sense(self, state: bool) -> None:
        """Switch between 4-wire (remote) and 2-wire (local) sensing."""
        sense = "SENSE_REMOTE" if state else "SENSE_LOCAL"
        self.port.write(f"{self.smu_ab}.sense = {self.smu_ab}.{sense}")

    def set_filter_count(self, count: int) -> None:
        """Set the number of readings that are averaged by the filter."""
        self.port.write(f"{self.smu_ab}.measure.filter.count = {count:d}")

    def set_filter_enabled(self, state: bool) -> None:
        """Switch the averaging filter on or off."""
        filter_state = "FILTER_ON" if state else "FILTER_OFF"
        self.port.write(f"{self.smu_ab}.measure.filter.enable = {self.smu_ab}.{filter_state}")

    def set_filter_repeat_average(self) -> None:
        """Use the repeating average as filter type."""
        self.port.write(f"{self.smu_ab}.measure.filter.type = {self.smu_ab}.FILTER_REPEAT_AVG")

    def set_nplc(self, nplc: float) -> None:
        """Set the integration time of the measurement in power line cycles."""
        self.port.write(f"{self.smu_ab}.measure.nplc = {nplc}")

    def set_output(self, state: bool) -> None:
        """Switch the output of the channel on or off."""
        self.port.write(f"{self.smu_ab}.source.output = {int(state)}")

    def set_source_level_voltage(self, value: float) -> None:
        """Set the output voltage in V."""
        self.port.write(f"{self.smu_ab}.source.levelv = {value}")

    def set_source_level_current(self, value: float) -> None:
        """Set the output current in A."""
        self.port.write(f"{self.smu_ab}.source.leveli = {value}")

    def request_measurement(self) -> None:
        """Request a combined current and voltage measurement."""
        self.port.write(f"print({self.smu_ab}.measure.iv())")

    def read_measurement(self) -> tuple[float, float]:
        """Read the current in A and the voltage in V of the requested measurement."""
        current, voltage = (float(value) for value in self.port.read().split())
        return current, voltage
