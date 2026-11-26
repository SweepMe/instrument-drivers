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
# * Instrument: Keithley 4200-SCS

from __future__ import annotations

import contextlib
import re
import time
from pathlib import Path
from typing import Any

import numpy as np
from pysweepme import FolderManager
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

FolderManager.addFolderToPATH()

# This driver only works with the pylptlib server running on the 4200-SCS device. Get it here: https://sweep-me.net/dashboard
# Communication with the server is done via the ProxyClass

import importlib
import ProxyClass

importlib.reload(ProxyClass)

from ProxyClass import Proxy

# Debug a warning when a KXCI reading reports that the SMU channel is in compliance (status letter "C")
WARN_ON_COMPLIANCE = True

# KXCI list sweeps (system mode, commands VL/IL): limits from the KXCI manual
KXCI_MAX_LIST_POINTS = 4096
KXCI_MAX_SWEEP_DELAY = 6.553  # s, command DT
KXCI_MAX_LIST_FUNCTIONS = 6  # number of names the LI command accepts
KXCI_LIST_POLL_INTERVAL = 0.2  # s between two checks whether the list sweep finished
KXCI_OVERFLOW_VALUE = 1e37  # readings above, like 99.09999E+36, mark an overflow or a value not measured


def format_kxci_number(value: float) -> str:
    """Format a number for a KXCI command, which accepts at most 12 characters per value."""
    return f"{float(value):.6g}"


def parse_kxci_number(reading: str) -> float:
    """Convert a KXCI reading like 'N+1.2345E-03' (status letter, then the value) to a float; overflow becomes NaN."""
    value = float(reading.strip().lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ").replace(" ", ""))
    if abs(value) > KXCI_OVERFLOW_VALUE:
        return float("nan")
    return value


class Device(EmptyDevice):
    """Keithley 4200-SCS driver."""

    def __init__(self) -> None:
        """Initialize device parameters."""
        EmptyDevice.__init__(self)

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_types = ["GPIB", "TCPIP"]
        # needed to make the code working with pysweepme where port_manager is only used from __init__
        self.port_manager = True

        self.port_properties = {
            "EOL": "\r\n",
            "timeout": 10.0,
            "TCPIP_EOLwrite": "\x00",
            "TCPIP_EOLread": "\x00",
        }

        # unclear whether all ranges exist as the documentation does not get clear about it
        self.current_ranges = {
            "Auto": 0,
        }
        # Add current ranges from 1 pA to 100 mA for limited and fixed mode
        for mode in ["Fixed", "Limited"]:
            for prefix in ["m", "µ", "n", "p"]:
                for number in [100, 10, 1]:
                    exponent = {"m": -3, "µ": -6, "n": -9, "p": -12}[prefix]
                    value = number * 10 ** exponent
                    key = f"{mode} {number} {prefix}A"
                    self.current_ranges[key] = value
        self.current_range: str = "Auto"

        self.speed_dict = {
            "Very fast": 0.01,
            "Fast": 0.1,
            "Medium": 1.0,
            "Slow": 10.0,
            "Custom": 10,
        }
        """Speed names as keys and PLC values as values."""

        # Communication Parameter
        self.port_string: str = "192.168.0.1"
        self.identifier: str = "Keithley_4200-SCS_" + self.port_string
        self.command_set: str = "LPTlib"
        self.card_id: int = 1

        self.lpt: Proxy | None = None
        self.param: Proxy | None = None

        # Measurement parameter
        self.route_out: str = "Rear"
        self.source: str = "Voltage in V"
        self.protection: float = 100e-6
        self.channel: str = "SMU1"

        # Speed
        self.speed: str = "Very fast"
        self.delay_factor: str = "0"
        self.filter_factor: str = "0"
        self.ad_aperture_time: str = "0.01"
        self.averages: str = "1"

        self.card_name = "SMU" + self.channel[-1]
        self.pulse_channel = None

        self.measured_voltage: float = 0.0
        self.measured_current: float = 0.0

        self.reading_status: str = "N"
        """Status letter of the last KXCI reading.

        N: Normal, L: Interval too short, V: Overflow reading (A/D converter saturated), X: Oscillation,
        C: This channel in compliance, T: Other channel in compliance
        """

        self.setvalue_is_fresh: bool = False
        """KXCI only: True if DV/DI was sent since the last TI/TV reading, so the next reading returns a fresh value.

        Re-sending DV/DI right before reading is avoided when possible, because it resets devices whose state depends
        on their history, e.g. after a hold time.
        """

        self.last_applied_value: float | None = None
        """KXCI only: the set value of the last DV/DI, to re-send it in 'start' when SweepMe! skips 'apply'."""

        self.kxci_current_range_index: int = 0
        """KXCI only: index of the fixed current range, used for RI and as the DI source range. 0 means auto."""

        # Pulse Mode Parameters
        self.pulse_master = False
        self.pulse_mode: bool = False

        self.pulse_count: int = 1
        self.pulse_meas_start: float = 50
        self.pulse_meas_duration: float = 20
        self.pulse_width: float = 0.5e-6
        self.pulse_period: float = 2e-6
        self.pulse_delay: float = 20e-9
        self.pulse_base_level: float = 0.0
        self.pulse_rise_time: float = 100e-9
        self.pulse_fall_time: float = 100e-9
        self.pulse_impedance: float = 1e6

        # List Mode Parameters
        self.list_master: bool = False
        """Only one channel can run the list sweep and is the master."""

        self.list_receiver: bool = False
        """If another channel runs a list sweep, the measurement must be done as list receiver."""

        self.list_sweep_values: list[float] = []
        self.list_measurement_keys = {
            "voltage": "voltage",
            "current": "current",
            "time": "time",
        }
        """The keys are used to register and receive the list sweep values."""

        self.list_delay_single: float = 0.0
        """The constant delay in seconds between each step and the measurement of a list sweep."""

        self.list_delay_list: list[float] = []
        """A list of delays in seconds between each step and the measurement of a list sweep."""

    @staticmethod
    def find_ports() -> list[str]:
        """Find available ports."""
        # If the lptlib.dll exists, the driver is probably running on the device.
        # Exemption: If Clarius is installed on the PC running SweepMe!, the dll also exists there.
        dll_path = r"C:\s4200\sys\bin\lptlib.dll"
        return ["LPTlib via localhost"] if Path(dll_path).exists() else ["LPTlib via xxx.xxx.xxx.xxx"]

    def update_gui_parameters(self, parameters: dict) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        new_parameters = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Rear"],
            "Channel": ["SMU1", "SMU2", "SMU3", "SMU4", "PMU1 - CH1", "PMU1 - CH2"],
            "Speed": list(self.speed_dict.keys()),
            "Compliance": 100e-6,
            "Range": list(self.current_ranges.keys()),
            "Average": "1",

            # Pulse Mode Parameters
            "CheckPulse": False,
            "PulseCount": 1,
            "PulseMeasStart": 50,
            "PulseMeasTime": 20,
            "PulseOnTime": 0.5e-6,
            "PulsePeriod": 2e-6,
            "PulseDelay": 20e-9,
            "PulseOffLevel": 0.0,
            "PulseRiseTime": 100e-9,
            "PulseFallTime": 100e-9,
            "PulseImpedance": 1e6,

            # List Mode Parameters
            "ListSweepCheck": False,
            "ListSweepType": ["Sweep", "Custom"],
            "ListSweepCustomValues": "",
            "ListSweepStart": 0.0,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": ["Step width:", "Points (lin.):", "Points (log.):"],
            "ListSweepStepPointsValue": 0.1,
            "ListSweepDual": False,
            "ListSweepDelaytime": "0.0",
        }

        if parameters.get("Speed", "Slow") == "Custom":
            new_parameters["Delay factor"] = "0"
            new_parameters["Filter factor"] = "0"
            new_parameters["A/D aperture time"] = "0.01"

        return new_parameters

    def apply_gui_parameters(self, parameters: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameters.get("Port", "")
        self.identifier = "Keithley_4200-SCS_" + self.port_string

        self.route_out = parameters.get("RouteOut", "")
        self.current_range = parameters.get("Range", "")

        self.source = parameters.get("SweepMode", "")

        self.protection = parameters.get("Compliance", "")
        self.speed = parameters.get("Speed", "")
        self.averages = parameters.get("Average", "1")

        self.channel = parameters.get("Channel", "SMU1")
        self.shortname = "4200-SCS %s" % parameters.get("Channel", "")

        self.port_manager = "lptlib" not in self.port_string.lower()

        # Custom speed parameters
        if self.speed == "Custom":
            self.delay_factor = parameters.get("Delay factor", "0")
            self.filter_factor = parameters.get("Filter factor", "0")
            self.ad_aperture_time = parameters.get("A/D aperture time", "0.01")

        # Reset returned values and units
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Pulse Mode Parameters
        self.pulse_master = False
        self.pulse_mode = parameters.get("CheckPulse", "")
        if self.pulse_mode:
            # backward compatibility as new fields have been added that are not
            # present in older SMU module versions
            try:
                self.pulse_count = parameters.get("PulseCount", "")
                self.pulse_meas_start = parameters.get("PulseMeasStart", "")
                self.pulse_meas_duration = parameters.get("PulseMeasTime", "")
                self.pulse_width = float(parameters.get("PulseOnTime", ""))
                self.pulse_period = float(parameters.get("PulsePeriod", ""))
                self.pulse_delay = float(parameters.get("PulseDelay", ""))
                self.pulse_base_level = parameters.get("PulseOffLevel", "")
                self.pulse_rise_time = parameters.get("PulseRiseTime", "")
                self.pulse_fall_time = parameters.get("PulseFallTime", "")
                self.pulse_impedance = parameters.get("PulseImpedance", "")
            except KeyError:
                debug("Please update the SMU module to support all features of the Keithley 4200-SCS instrument driver")

        # List Mode Parameters
        try:
            sweep_value = parameters.get("SweepValue", "")
        except KeyError:
            # this might be the case when driver is used with pysweepme
            # then, "SweepValue" is not defined during set_GUIparameter
            sweep_value = None

        # Reset the flags, so that a channel switched back from 'List sweep' is no longer the list master
        self.list_master = sweep_value == "List sweep"
        self.list_receiver = False
        if self.list_master:
            self.handle_list_sweep_parameter(parameters)

        # The list keys must be updated with the channel name
        self.list_measurement_keys = {
            "voltage": f"voltage_{self.channel}",
            "current": f"current_{self.channel}",
            "time": f"time_{self.channel}",
        }

    def handle_list_sweep_parameter(self, parameter: dict) -> None:
        """Read out the list sweep parameters and create self.list_sweep_values."""
        list_sweep_type = parameter["ListSweepType"]

        if list_sweep_type == "Sweep":
            # Create the list sweep values
            start = float(parameter["ListSweepStart"])
            end = float(parameter["ListSweepEnd"])

            step_points_type = parameter["ListSweepStepPointsType"]
            step_points_value = float(parameter["ListSweepStepPointsValue"])

            if step_points_type.startswith("Step width"):
                list_sweep_values = np.arange(start, end, step_points_value)
                # include end value
                list_sweep_values = np.append(list_sweep_values, end)

            elif step_points_type.startswith("Points (lin.)"):
                list_sweep_values = np.linspace(start, end, int(step_points_value))

            elif step_points_type.startswith("Points (log.)"):
                list_sweep_values = np.logspace(np.log10(start), np.log10(end), int(step_points_value))

            else:
                msg = f"Unknown step points type: {step_points_type}"
                raise ValueError(msg)

        elif list_sweep_type == "Custom":
            custom_values = parameter["ListSweepCustomValues"]
            if custom_values == "":
                list_sweep_values = np.array([])
            else:
                # Remove leading and trailing quotes and commas
                custom_values = custom_values.strip('"').strip("',")
                list_sweep_values = np.array([float(value) for value in custom_values.split(",")])

        else:
            msg = f"Unknown list sweep type: {list_sweep_type}"
            raise ValueError(msg)

        # Add the returning values in reverse order to the list
        if parameter["ListSweepDual"]:
            list_sweep_values = np.append(list_sweep_values, list_sweep_values[::-1])

        self.list_sweep_values = list_sweep_values.tolist()

        # If a single value is given, use the delay for all points. Otherwise, create a delay list
        delay_values = parameter["ListSweepDelaytime"]
        if len(delay_values.split(",")) > 1:
            # TODO: use ListSweepHoldTime as input?
            self.list_delay_single = 0.0

            # Remove leading and trailing commas
            delay_values = delay_values.strip(",")
            self.list_delay_list = [float(value) for value in delay_values.split(",")]
        else:
            self.list_delay_single = float(delay_values)
            self.list_delay_list = []

        # Add time staps to return values
        self.variables.extend(["Time stamp", "Time stamp zeroed"])
        self.units.extend(["s", "s"])
        self.plottype.extend([True, True])
        self.savetype.extend([True, True])

    def handle_card_name(self) -> None:
        """Extract the card name and pulse channel from the selected channel.

        The channel can be either "SMU1", "SMU2", "PMU1 - CH1" or "PMU1 - CH2"
        It means that in case of PMU the pulse channel is additionally added after the card name
        The card name is now always "SMU1", "SMU2", or "PMU1" etc.
        """
        try:
            if "PMU" in self.channel:
                self.card_name = self.channel.split("-")[0].strip()
                self.pulse_channel = int(self.channel.split("-")[1][-1])
            elif "SMU" in self.channel:
                self.card_name = self.channel.strip()
                self.pulse_channel = None
            else:
                # This is a fallback, when channels have been just "1", "2", "3", "4". After adding PMU, it became
                # necessary to distinguish between SMU and PMU
                self.card_name = "SMU" + self.channel[-1]
                self.pulse_channel = None
        except Exception as e:
            msg = f"Unknown channel name: {self.channel}. Please use 'SMU1', 'SMU2', 'PMU1 - CH1' or 'PMU1 - CH2'."
            raise ValueError(msg) from e

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        self.handle_card_name()
        if self.port_manager:
            self.command_set = "US"  # "US" user mode, "LPTlib", # check manual p. 677/1510

            # very important, triggers a (DCL) in KXCI, seems to be essential to read correct values
            self.port.port.clear()

            if self.pulse_mode:
                msg = "Pulse mode is not supported with US command set via GPIB. Use control via 'LPTlib' instead."
                raise Exception(msg)
        else:
            self.command_set = "LPTlib"  # "US" user mode, "LPTlib", # check manual p. 677/1510
            self.connect_to_lptlib_server()
            self.card_id = self.lpt.getinstid(self.card_name)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.check_test_parameter()

        if self.identifier not in self.device_communication:
            installed_smus: list[str] = []
            if self.command_set == "LPTlib":
                if self.pulse_mode:
                    self.lpt.dev_abort()  # stops executed pulses
                self.lpt.tstsel(1)  # select test station 1 and load instrument configuration. Choose 0 to deselect
                self.lpt.devint()  # This command resets all active instruments in the system to their default states.
                # calls devclr, clrcon (only for switching matrix), clrtrg, clrscn, kibdefint

            elif self.command_set == "US":
                installed_smus = self.get_installed_smu_channels()

                self.clear_buffer()
                self.set_to_4200()
                self.set_command_mode("US")
                self.set_data_service()
                self.set_resolution(7)

            self.device_communication[self.identifier] = {}  # dictionary that can be filled with further information

            if self.command_set == "US":
                # A KXCI list sweep switches off every installed SMU that does not take part in it
                self.device_communication[self.identifier]["Installed SMUs"] = installed_smus

        # If this channel should run the list sweep, register it as 'List master'. Via KXCI, this is done per branch in
        # 'configure' instead. Checking if the list receiver should be used will be done in 'trigger_ready'.
        if self.list_master and self.command_set == "LPTlib":
            if "List master" in self.device_communication[self.identifier]:
                msg = "Please use only one channel for list sweep."
                raise Exception(msg)

            self.device_communication[self.identifier]["List master"] = self.channel
            self.device_communication[self.identifier]["List length"] = len(self.list_sweep_values)
            # Reset the dictionary of list results here before all channels register their arrays in 'configure'
            self.lpt.reset_measurement_cache()

    def check_test_parameter(self) -> None:
        """Check if the selected parameters can be run with the selected mode."""
        if "PMU" in self.card_name and not self.pulse_mode:
            msg = f"Please select pulse mode to use the PMU channel {self.channel}."
            raise Exception(msg)

        if self.pulse_mode:
            if "PMU" not in self.card_name:
                msg = "Please select a PMU channel to use pulse mode."
                raise Exception(msg)
            if self.command_set != "LPTlib":
                msg = "Pulse mode only supported with using port communication via LPTlib."
                raise Exception(msg)
            if float(self.pulse_width) >= float(self.pulse_period):
                msg = "Pulse width must be smaller than pulse period!"
                raise ValueError(msg)

            min_pulse_delay = 20e-9
            if float(self.pulse_delay) < min_pulse_delay:
                msg = "Delay must be 20 ns or larger (not clear why)!"
                raise ValueError(msg)

        """
         Voltage source mode specified (DV):
        0 Autorange
        1 20 V range
        2 200 V range
        3 200 V range
        Current source mode specified (DI):
        = 0 Autorange
        = 3 100nA
        = 4 1muA range
        = 5 10muA
        = 6 100muA
        = 7 1mA
        = 8 10 mA
        = 9 100 mA range
        """

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        if self.identifier in self.device_communication:
            if self.command_set == "LPTlib":
                self.lpt.devint()  # restores default values
                self.lpt.tstdsl()  # not implemented yet

            del self.device_communication[self.identifier]

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.pulse_mode:
            # Pulse mode is only supported with LPTlib command set
            if "Pulse master" not in self.device_communication[self.identifier]:
                self.pulse_master = True
                self.device_communication[self.identifier]["Pulse master"] = self.channel
            else:
                if self.device_communication[self.identifier]["Pulse master"] == self.channel:
                    msg = (
                        "Please use two different channels two combine several pulse units of the "
                        "4200-SCS parameter analyzer."
                    )
                    raise Exception(msg)
                self.pulse_master = False

            self.configure_pulse()

        elif float(self.averages) > 1:
            # KXCI needs a DV/DI right before every reading, which resets devices whose state depends on their history
            msg = "Averaging is not supported by the 4200-SCS driver. Use a Loop module to repeat a point instead."
            raise NotImplementedError(msg)

        elif self.command_set == "LPTlib":
            self.configure_lptlib()

        elif self.command_set == "US":
            self.configure_kxci()

    def configure_kxci(self) -> None:
        """Configure the device using KXCI commands (user mode, US)."""
        self.setvalue_is_fresh = False
        self.last_applied_value = None

        # Integration/Speed
        if self.speed == "Very fast":
            msg = (
                "Speed of 'Very Fast' is not supported for US command set via GPIB/TCPIP. "
                "Use control via 'LPTlib' or custom speed instead."
            )
            raise ValueError(msg)

        if self.speed == "Custom":
            self.set_speed_mode(
                self.speed,
                float(self.delay_factor),
                float(self.filter_factor),
                float(self.ad_aperture_time),
            )
        else:
            self.set_speed_mode(self.speed)

        # Current Range - the KXCI implementation has not been tested yet
        self.kxci_current_range_index = 0
        current_range_float = self.current_ranges[self.current_range]
        if "limited" in self.current_range.lower():
            self.set_current_range_limited(self.card_name[-1], current_range_float)

        elif "auto" in self.current_range.lower():
            # Use the lowest current range for auto-ranging
            self.set_current_range_limited(self.card_name[-1], 0)

        else:
            self.kxci_current_range_index = self.get_kxci_current_range_index(self.current_range)
            self.set_current_range(self.card_name[-1], self.kxci_current_range_index, self.protection)

        # A list sweep in a previous branch left KXCI in system mode, where DV/DI/TV/TI are not valid
        self.set_command_mode("US")
        self.list_receiver = False

        if self.list_master:
            self.configure_kxci_list_sweep()

    def configure_kxci_list_sweep(self) -> None:
        """Check the list sweep parameters for KXCI and register this channel as list master for this branch.

        The other channels of the instrument find out in 'start' whether they take part in the list sweep as receivers.
        The master is registered per branch, so that the channels of another branch run in user mode again.
        """
        if self.list_delay_list:
            msg = (
                "A list of delay times is not supported via KXCI, which uses one delay time for all points. "
                "Enter a single value or use control via 'LPTlib'."
            )
            raise ValueError(msg)

        if not 0.0 <= self.list_delay_single <= KXCI_MAX_SWEEP_DELAY:
            msg = f"The list sweep delay time must be between 0 and {KXCI_MAX_SWEEP_DELAY} s via KXCI."
            raise ValueError(msg)

        communication = self.device_communication[self.identifier]
        if "List master" in communication:
            msg = "Please use only one channel for list sweep."
            raise Exception(msg)

        communication["List master"] = self.channel
        communication["List receivers"] = {}

    def configure_lptlib(self) -> None:
        """Configure the device using lptlib commands."""
        # can be used to change the limit indicator value
        # self.lpt.setmode(self.card_id, self.param.KI_LIM_INDCTR, float(self.protection))

        # After installation of PMU cards or running auto-configuration, the device might respond to applying a
        # Voltage or current source with "K4200Error('Cannot force when not connected.')"
        # Currently unclear why, but running the PMU-specific rpm_config seems to solve the issue
        with contextlib.suppress(Exception):
            self.lpt.rpm_config(
                instr_id=self.card_id,
                chan=self.card_id,
                modifier=self.param.KI_RPM_PATHWAY,
                value=self.param.KI_RPM_SMU,
            )

        # return real measured value when in compliance, not indicator value like 7.0e22
        self.lpt.setmode(self.card_id, self.param.KI_LIM_MODE, self.param.KI_VALUE)

        # Protection
        if self.source == "Voltage in V":
            # The device raises an error if the current compliance is larger than the current measurement range.
            # Therefore, we set the current measurement range to auto first, before updating it again later.
            self.lpt.rangei(self.card_id, 0)  # auto-ranging
            self.lpt.limiti(self.card_id, float(self.protection))  # compliance/protection
        elif self.source == "Current in A":
            self.lpt.limitv(self.card_id, float(self.protection))  # compliance/protection

        # Integration/Speed for intgX and sintgX commands. Allowed values are from 0.01 to 10
        if self.speed.lower() == "custom":
            msg = "Custom speed mode can only be used with US command set via GPIB."
            raise NotImplementedError(msg)

            # ad factor = KI_INTGPLC (NPLC up to 100)
            # delay factor = KI_DELAY_FACTOR
            # filter factor =

        # TODO: lptlib allows for setting NPLC integration to custom values between 0.01 and 10
        # but we cannot set filter factor (only for CVU cards)
        # we could set the delay factor, but it does not make much sense because we can also use SweepMes Hold

        nplc_value = self.speed_dict[self.speed]
        self.lpt.setmode(self.card_id, self.param.KI_INTGPLC, nplc_value)

        # Current measurement Range
        current_range_value = self.current_ranges[self.current_range]
        if "auto" in self.current_range.lower() or "limited" in self.current_range.lower():
            self.lpt.rangei(self.card_id, 0)  # auto-ranging

            if "limited" in self.current_range.lower():
                self.lpt.lorangei(self.card_id, current_range_value)  # minimum current range for auto-ranging
        else:
            self.lpt.rangei(self.card_id, current_range_value)  # fixed range

        # self.lpt.lorangev(self.card_id, 1e-1)  # low range voltage

        # Range delay off
        self.lpt.setmode(self.card_id, self.param.KI_RANGE_DELAY, 0.0)

    def start(self) -> None:
        """Preparation before applying a new value."""
        if self.list_master:
            if self.command_set == "LPTlib":
                # Clear the result arrays
                self.lpt.clrscn()

            # Update list length in case variable lists are used (e.g. by using ParameterSyntax of SweepMe)
            list_length = len(self.list_sweep_values)
            if list_length == 0:
                msg = "List for List Sweep is empty."
                raise ValueError(msg)

            if self.command_set == "US" and list_length > KXCI_MAX_LIST_POINTS:
                msg = f"A list sweep via KXCI can have at most {KXCI_MAX_LIST_POINTS} points, not {list_length}."
                raise ValueError(msg)

            self.device_communication[self.identifier]["List length"] = list_length

        elif self.command_set == "US" and not self.pulse_mode:
            communication = self.device_communication[self.identifier]
            self.list_receiver = "List master" in communication

            if self.list_receiver:
                # Another channel runs a list sweep in this branch: this channel takes part as a constant source,
                # which the list master defines in 'measure'. It is registered at every point, because SweepMe! calls
                # 'apply' only if the set value changed.
                communication["List receivers"][self.card_name[-1]] = {
                    "source": self.source,
                    "value": float(self.value),
                    "compliance": float(self.protection),
                    "source_range": self.get_kxci_fixed_source_range(),
                }

            elif not self.setvalue_is_fresh and float(self.value) == self.last_applied_value:
                # SweepMe! calls 'apply' only if the set value changed. For a repeated value, re-send DV/DI here,
                # before the hold time, so the reading in 'call' needs no DV/DI right before it and the hold time stays
                # effective.
                self.apply()

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        if self.pulse_mode and self.pulse_master:
            del self.device_communication[self.identifier]["Pulse master"]

        if self.list_master:
            if self.command_set == "LPTlib":
                self.lpt.reset_measurement_cache()
            else:
                communication = self.device_communication.get(self.identifier, {})
                for key in ("List master", "List receivers", "List length", "List names"):
                    communication.pop(key, None)

    def poweroff(self) -> None:
        """Turn off the device."""
        if self.pulse_mode:
            self.lpt.pulse_output(self.card_id, self.pulse_channel, out_state=0)
        elif self.command_set == "LPTlib":
            self.lpt.forcev(self.card_id, 0.0)
        elif self.command_set == "US":
            # After a list sweep, KXCI is in system mode, where the user mode command DV is not valid
            self.set_command_mode("US")
            self.switch_off(self.card_name[-1])

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.pulse_mode:
            return

        if self.command_set == "US" and (self.list_master or self.list_receiver):
            # Via KXCI, the list master defines the sources of all channels and runs the whole sweep in 'measure'
            return

        self.value = float(self.value)

        if self.command_set == "LPTlib":
            if self.source == "Voltage in V":
                self.lpt.forcev(self.card_id, self.value)
            elif self.source == "Current in A":
                self.lpt.forcei(self.card_id, self.value)

        elif self.command_set == "US":
            # These ranges are the source ranges, not the compliance or measurement ranges. The voltage is always
            # sourced with auto range. A current source uses the fixed current range, because with auto range it drops
            # to its lowest range at 0 A and the next step reads mid-transient while it ranges up again.
            voltage_source_range = 0  # auto
            current_source_range = self.kxci_current_range_index  # 0 = auto, unless a fixed range is selected

            if self.source == "Voltage in V":
                self.set_voltage(self.card_name[-1], voltage_source_range, self.value, float(self.protection))
            elif self.source == "Current in A":
                self.set_current(self.card_name[-1], current_source_range, self.value, float(self.protection))
            self.setvalue_is_fresh = True
            self.last_applied_value = self.value

    def trigger_ready(self) -> None:
        """Start the pulse output if in pulse mode."""
        if self.pulse_mode:
            # needed because of bug in SweepMe! that changes type of
            # self.value to float64
            self.value = float(self.value)

            # configuring a single pulse
            self.lpt.pulse_sweep_linear(
                self.card_id,
                self.pulse_channel,
                sweep_type=self.param.PULSE_AMPLITUDE_SP,
                start=self.value,
                stop=self.value,
                step=0.0,
            )

            # needed otherwise no voltage is applied
            self.lpt.pulse_output(self.card_id, self.pulse_channel, out_state=1)

        # Register result arrays for list mode. Via KXCI, the list master reads the results in 'call' instead.
        if self.command_set != "LPTlib":
            return

        if self.list_master:
            self.configure_list_sweep(len(self.list_sweep_values))
        elif "List master" in self.device_communication[self.identifier]:
            # Check if another channel is running a list sweep
            self.list_receiver = True
            self.configure_list_sweep(self.device_communication[self.identifier]["List length"])

    def configure_list_sweep(self, array_size: int) -> None:
        """When using list mode, the results arrays must be registered to be read out in parallel."""
        # Do not reset the measurement dictionary as maybe another channel has already registered arrays
        current_key = self.list_measurement_keys["current"]
        self.lpt.prepare_measurement("smeasi", current_key, self.card_id, array_size=array_size)

        voltage_key = self.list_measurement_keys["voltage"]
        self.lpt.prepare_measurement("smeasv", voltage_key, self.card_id, array_size=array_size)

        # For now only the list master returns the time stamps as the list receivers are too late to change the number
        # of their return values
        if self.list_master:
            time_key = self.list_measurement_keys["time"]
            self.lpt.prepare_measurement("smeast", time_key, self.card_id, array_size=array_size)

    def measure(self) -> None:
        """Start the pulse or list measurements. This cannot be done in 'apply' as the sweep value does not change."""
        if self.pulse_mode and self.pulse_master:
            # TODO: only the master driver instance needs to execute
            self.lpt.pulse_exec(mode=self.param.PULSE_MODE_SIMPLE)  # Alternatively self.param.PULSE_MODE_ADVANCED

        if self.list_master and self.command_set == "US":
            self.run_kxci_list_sweep()

        elif self.list_master:
            # Set the array of individual delay time
            if self.list_delay_list:
                if len(self.list_delay_list) != len(self.list_sweep_values):
                    msg = (f"The number of delay times ({len(self.list_delay_list)}) must match the number of list "
                           f"values {len(self.list_sweep_values)})")
                    raise ValueError(msg)
                # all delays must be floats larger than 0
                if any((not isinstance(delay, (float, int)) or delay < 0) for delay in self.list_delay_list):
                    msg = "All delay times must be numbers larger or equal to 0."
                    raise ValueError(msg)
                self.lpt.adelay(self.list_delay_list)

            if self.source == "Voltage in V":
                self.lpt.asweepv(self.card_id, self.list_sweep_values, self.list_delay_single)
            elif self.source == "Current in A":
                self.lpt.asweepi(self.card_id, self.list_sweep_values, self.list_delay_single)

    def request_result(self) -> None:
        """Wait for pulse measurements or a KXCI list sweep to finish."""
        if self.list_master and self.command_set == "US":
            self.wait_for_kxci_list_sweep()

        if self.pulse_mode and self.pulse_master:
            timeout = 30.0
            while not self.is_run_stopped():
                time.sleep(0.1)
                status, elapsed_time = self.lpt.pulse_exec_status()

                if status != self.param.PMU_TEST_STATUS_RUNNING:
                    break
                if elapsed_time > timeout:
                    self.lpt.dev_abort()
                    break

    def read_result(self) -> None:
        """Read out results of pulse measurement."""
        if self.pulse_mode:
            buffer_size = self.lpt.pulse_chan_status(
                self.card_id,
                self.pulse_channel,
            )

            # fetch results
            v_meas, i_meas, timestamp, status_dict = self.lpt.pulse_fetch(
                instr_id=self.card_id,
                chan=self.pulse_channel,
                start_index=0,
                stop_index=buffer_size,
            )

            self.measured_voltage = np.average(v_meas)
            self.measured_current = np.average(i_meas)

    def call(self) -> list:
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables."""
        if (self.list_master or self.list_receiver) and self.command_set == "US":
            return self.read_kxci_list_sweep()

        if self.list_master or self.list_receiver:
            # Read out the registered lists of measured values
            voltage = self.lpt.read_measurement(self.list_measurement_keys["voltage"])
            current = self.lpt.read_measurement(self.list_measurement_keys["current"])
            if self.list_master:
                time_stamps = self.lpt.read_measurement(self.list_measurement_keys["time"])
                time_stamps_zeroed = [stamp - time_stamps[0] for stamp in time_stamps]  # start at 0
                return [voltage, current, time_stamps, time_stamps_zeroed]
            else:
                return [voltage, current]

        if not self.pulse_mode:
            if self.command_set == "LPTlib":
                self.measured_voltage = self.lpt.intgv(self.card_id)
                self.measured_current = self.lpt.intgi(self.card_id)

                # needed to give some time to update the plot
                # it seems that the LPTlib access is somehow blocking the entire program
                time.sleep(0.001)

            elif self.command_set == "US":
                # The KXCI command to read out measurement values only retrieves a new value if the set voltage or set
                # current command has been called before. Otherwise, NaN is returned.
                # Only the first TV/TI after DV/DI returns a fresh value of the measured quantity, later ones return
                # the 99.09999E+36 sentinel. The sourced quantity reads back in any order, so query the measured first.
                # 'apply' or 'start' sent DV/DI before the hold time. It is only re-sent here as a fallback, because
                # re-sending it after the hold time resets devices whose state depends on their history.
                if not self.setvalue_is_fresh:
                    self.apply()
                self.setvalue_is_fresh = False

                if self.source == "Voltage in V":
                    self.measured_current = self.get_current(self.card_name[-1])
                    self.measured_voltage = self.get_voltage(self.card_name[-1])
                else:
                    self.measured_voltage = self.get_voltage(self.card_name[-1])
                    self.measured_current = self.get_current(self.card_name[-1])

                if WARN_ON_COMPLIANCE and self.reading_status == "C":
                    unit = "A" if self.source == "Voltage in V" else "V"
                    debug(f"Warning: 4200-SCS {self.channel} is in compliance at {self.protection} {unit}.")

            """
            X Y Z +-N.NNNN E+-NN
            X The status of the data (where X = N for a normal reading)
            Y The measure channel (Y = A through F)
            Z The measure mode (Z = V or I)
            +-N.NNNN E+-NN is the reading (mantissa and exponent)
            """

        return [self.measured_voltage, self.measured_current]

    """ here, the KXCI list sweep is assembled from the wrapped commands """

    def run_kxci_list_sweep(self) -> None:
        """Define the list sweep and all other channels of the instrument in KXCI system mode and start it.

        The list master sweeps (VL/IL); every channel that registered as receiver in 'start' becomes a constant source
        (VC/IC); every other installed SMU is switched off, because in system mode all SMUs take part in a test.
        """
        communication = self.device_communication[self.identifier]
        receivers: dict[str, dict[str, Any]] = communication.get("List receivers", {})
        master = self.card_name[-1]

        channels: dict[str, dict[str, Any]] = {
            master: {
                "source": self.source,
                "compliance": float(self.protection),
                "source_range": self.get_kxci_fixed_source_range(),
            },
            **receivers,
        }

        # Channel definition page: source mode 1 = voltage, 2 = current; source function 1 = VAR1, 3 = constant
        self.set_kxci_page("DE")
        for channel, setup in channels.items():
            source_mode = 1 if setup["source"] == "Voltage in V" else 2
            source_function = 1 if channel == master else 3
            self.define_kxci_channel(channel, f"V{channel}", f"I{channel}", source_mode, source_function)

        for channel in communication.get("Installed SMUs", []):
            if channel not in channels:
                self.switch_off_kxci_channel(channel)

        for channel, setup in channels.items():
            self.set_kxci_source_range(channel, setup["source_range"])

        # Source setup page
        self.set_kxci_page("SS")
        self.set_kxci_list_sweep(master, self.source, float(self.protection), self.list_sweep_values)
        for channel, setup in receivers.items():
            self.set_kxci_constant_source(channel, setup["source"], setup["value"], setup["compliance"])
        self.set_kxci_sweep_delay(self.list_delay_single)
        self.set_kxci_sweep_hold_time(0.0)  # SweepMe!'s hold time already ran before 'measure'

        # Measurement setup page: list display mode and the measured functions. LI accepts at most 6 names, so the
        # measured quantities come first; a sourced quantity that does not fit is returned as its set value.
        measured_names = []
        sourced_names = []
        for channel, setup in channels.items():
            if setup["source"] == "Voltage in V":
                measured_names.append(f"I{channel}")
                sourced_names.append(f"V{channel}")
            else:
                measured_names.append(f"V{channel}")
                sourced_names.append(f"I{channel}")
        list_names = (measured_names + sourced_names)[:KXCI_MAX_LIST_FUNCTIONS]
        communication["List names"] = list_names

        self.set_kxci_page("SM")
        self.set_kxci_display_mode(2)
        self.set_kxci_list_functions(list_names)

        # Measurement control page
        self.set_kxci_page("MD")
        self.start_kxci_test()

    def wait_for_kxci_list_sweep(self) -> None:
        """Wait until the last point of the list sweep has a timestamp, as KXCI offers no service request via TCPIP."""
        list_length = len(self.list_sweep_values)
        timestamp_name = self.get_kxci_measured_name() + "T"

        # Generous upper limit: delay plus up to 1 s for integration and ranging per point
        timeout = 30.0 + list_length * (self.list_delay_single + 1.0)
        start_time = time.time()

        while not self.is_run_stopped():
            if self.get_kxci_realtime_reading(timestamp_name, list_length) != 0.0:
                return

            if time.time() - start_time > timeout:
                self.abort_kxci_test()
                msg = f"The KXCI list sweep of {list_length} points did not finish within {timeout:.0f} s."
                raise TimeoutError(msg)

            time.sleep(KXCI_LIST_POLL_INTERVAL)

        self.abort_kxci_test()

    def read_kxci_list_sweep(self) -> list[list[float]]:
        """Return the lists of voltage and current (and the timestamps for the master) of a KXCI list sweep."""
        communication = self.device_communication[self.identifier]
        list_names = communication.get("List names", [])
        list_length = communication.get("List length", len(self.list_sweep_values))
        channel = self.card_name[-1]

        if self.list_master:
            set_values = list(self.list_sweep_values)
        else:
            set_values = [communication["List receivers"][channel]["value"]] * list_length

        voltage_name = f"V{channel}"
        current_name = f"I{channel}"
        voltage = self.get_kxci_readings(voltage_name) if voltage_name in list_names else set_values
        current = self.get_kxci_readings(current_name) if current_name in list_names else set_values

        if not self.list_master:
            return [voltage, current]

        time_stamps = self.get_kxci_readings(self.get_kxci_measured_name() + "T")
        time_stamps_zeroed = [stamp - time_stamps[0] for stamp in time_stamps] if time_stamps else []
        return [voltage, current, time_stamps, time_stamps_zeroed]

    def get_kxci_measured_name(self) -> str:
        """Return the KXCI name of the quantity this channel measures: the current of a voltage source and v.v."""
        channel = self.card_name[-1]
        return f"I{channel}" if self.source == "Voltage in V" else f"V{channel}"

    def get_kxci_fixed_source_range(self) -> float:
        """Return the fixed source range in A for a current source with a 'Fixed' range, else 0 (auto range)."""
        if self.source == "Current in A" and self.current_range.startswith("Fixed"):
            return float(self.current_ranges[self.current_range])
        return 0.0

    """ here, convenience functions start """

    def connect_to_lptlib_server(self) -> None:
        """Connect to the LPTlib server running on the 4200-SCS device."""
        if "localhost" in self.port_string.lower():
            # SweepMe! is running on the 4200-SCS device
            tcp_ip = "localhost"
            tcp_port = 8888

        else:
            tcp_ip_port = self.port_string[11:].strip()  # removing "LPTlib via "
            tcp_ip_port_split = tcp_ip_port.split(":")  # in case a port is given

            tcp_ip = tcp_ip_port_split[0]
            tcp_port = int(tcp_ip_port_split[1]) if len(tcp_ip_port_split) == 2 else 8888

        self.lpt = Proxy(tcp_ip, tcp_port, "lpt")
        self.param = Proxy(tcp_ip, tcp_port, "param")

        try:
            self.lpt.initialize()
        except ConnectionRefusedError as e:
            msg = ("Unable to connect to a lptlib server application running on the 4200-SCS. Please check your"
                   "network settings and make sure the server application is running.")
            raise ConnectionRefusedError(msg) from e
        except Exception as e:
            msg = "Error during lpt.initialize"
            raise Exception(msg) from e

    def configure_pulse(self) -> None:
        """Configure pulses for pulse mode."""
        self.lpt.pg2_init(
            instr_id=self.card_id,
            mode_id=0,  # Standard pulse mode
        )

        self.lpt.rpm_config(
            instr_id=self.card_id,
            chan=self.pulse_channel,
            modifier=self.param.KI_RPM_PATHWAY,
            value=self.param.KI_RPM_PULSE,
        )

        self.lpt.pulse_meas_sm(
            instr_id=self.card_id,
            chan=self.pulse_channel,
            acquire_type=0,
            acquire_meas_v_ampl=1,
            acquire_meas_v_base=0,
            acquire_meas_i_ampl=1,
            acquire_meas_i_base=0,
            acquire_time_stamp=1,
            llecomp=1,
        )

        self.lpt.pulse_ranges(
            self.card_id,
            self.pulse_channel,
            v_src_range=10.0,
            v_range_type=0,
            v_range=10.0,
            i_range_type=0,
            i_range=0.2,
        )

        self.lpt.pulse_limits(
            self.card_id,
            self.pulse_channel,
            v_limit=5.0,
            i_limit=1.0,
            power_limit=10.0,
        )

        self.lpt.pulse_meas_timing(
            self.card_id,
            self.pulse_channel,
            start_percent=float(self.pulse_meas_start) / 100.0,
            stop_percent=(float(self.pulse_meas_start) + float(self.pulse_meas_duration)) / 100.0,
            num_pulses=int(self.pulse_count),
        )

        self.lpt.pulse_source_timing(
            self.card_id,
            self.pulse_channel,
            period=float(self.pulse_period),
            delay=float(self.pulse_delay),
            width=float(self.pulse_width),
            rise=float(self.pulse_rise_time),
            fall=float(self.pulse_fall_time),
        )

        self.lpt.pulse_load(
            self.card_id,
            self.pulse_channel,
            load=float(self.pulse_impedance),
        )

    """ here wrapped functions start """

    def read_tcpip_port(self) -> str:
        """Read out port buffer if using TCP/IP."""
        answer = ""
        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
        return answer

    def set_command_mode(self, mode: str) -> str:
        """Set the command mode to either user mode (US) or usrlib (UL)."""
        if mode not in ["US", "UL"]:
            msg = "Mode must be 'US' or 'UL'."
            raise ValueError(msg)
        self.port.write(f"{mode}")
        return self.read_tcpip_port()

    def get_identification(self) -> str:
        """Return IDN."""
        return self.port.query("*IDN?")

    def get_options(self) -> str:
        """Return OPT."""
        return self.port.query("*OPT?")

    def set_resolution(self, resolution: int) -> str:
        """Set the resolution of the device."""
        if self.command_set == "US":
            self.port.write(f"RS {int(resolution)}")
        return self.read_tcpip_port()

    @staticmethod
    def get_kxci_current_range_index(current_range: str) -> int:
        """Return the KXCI index of a fixed current range such as 'Fixed 100 µA', or 0 (auto) if KXCI has none.

        The index is looked up by the range name, because the range values are computed floats: 100 * 10 ** -6 is
        9.999999999999999e-05 and never equals the 1e-4 of a float-keyed table.
        """
        current_range_index = {
            "100 mA": 9,
            "10 mA": 8,
            "1 mA": 7,
            "100 µA": 6,
            "10 µA": 5,
            "1 µA": 4,
            "100 nA": 3,
        }
        range_name = current_range.removeprefix("Fixed").strip()
        if range_name in current_range_index:
            return current_range_index[range_name]

        debug(f"Warning: Current range {current_range} not supported via KXCI. Using autorange instead.")
        return 0

    def set_current_range(self, channel: str, current_range_index: int, compliance: float) -> str:
        """Set the current range of the device. Requires to set the compliance as well.

        When the SMU channel is used as a voltage source, the compliance is overwritten when setting the set value.
        In US mode, the current range must be set as an index instead of the actual value.
        """
        if self.command_set == "US":
            self.port.write(f"RI {channel}, {current_range_index}, {compliance}")
        return self.read_tcpip_port()

    def set_current_range_limited(self, channel: str, current: float) -> str:
        """Set the lowest current range of the SMU to be used when measuring."""
        if self.command_set == "US":
            self.port.write(f"RG {channel}, {current}")
        return self.read_tcpip_port()

    def switch_off(self, channel: str) -> str:
        """Switch off the device."""
        if self.command_set == "US":
            self.port.write(f"DV{channel}")
        return self.read_tcpip_port()

    def clear_buffer(self) -> str:
        """Clear the buffer of the device."""
        self.port.write("BC")
        return self.read_tcpip_port()

    def set_to_4200(self) -> str:
        """Set the device to 4200 mode."""
        # First parameter: 0 - 4145 Emulation, 1 - 4200A
        # Second parameter: 0 - this session only, 1 - permanently (Write to KCON)
        self.port.write("EM 1,0")
        return self.read_tcpip_port()

    def enable_user_mode(self) -> str:
        """Enable user mode."""
        self.port.write("US")  # user mode
        return self.read_tcpip_port()

    def set_data_service(self) -> str:
        """Set data ready service.

        Use a service request to wait until operations are complete before downloading data.
        """
        if self.command_set == "US":
            self.port.write("DR0")  # data ready service request
        return self.read_tcpip_port()

    def set_speed_mode(self, speed: str, delay_factor: float = 1., filter_factor: float = 1., ad_integration_time: float = 1.) -> str:
        """Set the integration time of the device (KXCI Integration).

        Allowed values for speed are:
        fast - 0.1 PLC (named short in the manual)
        medium - 1 PLC
        slow - 10 PLC (named long in the manual)
        custom
        Keep the naming of previous drivers for compatibility (fast + slow) and allow manual naming (short + long).

        Custom (4200A command set only) - command 4: Requires delay factor (0 - 100), filter factor (0 - 100),
        and A/D integration time (0.01 - 10 NPLC) to be set.
        """
        commands = {
            "fast": "1",  # = short
            "short": "1",
            "medium": "2",  # medium
            "slow": "3",  # = long
            "long": "3",
            "custom": "4",
        }
        if speed.lower() not in commands:
            msg = f"Speed must be one of {list(commands.keys())}."
            raise ValueError(msg)

        if self.command_set != "US":
            msg = "set_speed_mode can only be set when using US command set via KXCI controls."
            raise NotImplementedError(msg)

        if speed.lower() == "custom":
            if delay_factor < 0 or delay_factor > 100:
                msg = "Delay factor must be between 0 and 100."
                raise ValueError(msg)

            if filter_factor < 0 or filter_factor > 100:
                msg = "Filter factor must be between 0 and 100."
                raise ValueError(msg)

            if ad_integration_time < 0.01 or ad_integration_time > 10:
                msg = "A/D integration time must be between 0.01 and 10 (NPLC)."
                raise ValueError(msg)

            self.port.write(f"IT4, {delay_factor}, {filter_factor}, {ad_integration_time}")

        else:
            self.port.write("IT" + commands[speed.lower()])  # IT1 short, IT2 medium, IT3 long

        return self.read_tcpip_port()

    def set_current(self, channel: str, current_range: int, value: float, voltage_compliance: float) -> str:
        """Set the current of the given channel.

        Current source ranges:
        Auto - 0
        1 nA - 1 (only with preamplifier)
        10 nA - 2 (only with preamplifier)
        100 nA - 3
        1 uA - 4
        10 uA - 5
        100 uA - 6
        1 mA - 7
        10 mA - 8
        100 mA - 9
        1 A - 10 (only with 4210 or 4211-SMU)
        1 pa - 11 (only with preamplifier)
        10 pa - 12 (only with preamplifier)
        100 pa - 13 (only with preamplifier)
        """
        if self.command_set == "US":
            self.port.write(f"DI{channel}, {current_range}, {value}, {voltage_compliance}")
        return self.read_tcpip_port()

    def set_voltage(self, channel: str, voltage_range: int, value: float, current_compliance: float) -> str:
        """Set the voltage of the given channel."""
        if self.command_set == "US":
            self.port.write(f"DV{channel}, {voltage_range}, {value}, {current_compliance}")
        return self.read_tcpip_port()

    def get_voltage(self, channel: str) -> float:
        """Request voltage of given channel."""
        voltage = float("nan")
        overflow_value = 1e37
        if self.command_set == "US":
            answer = self.port.query("TV" + str(channel))
            self.reading_status = answer[0]
            voltage = float(answer[3:])
            if voltage > overflow_value:
                voltage = float("nan")
        return voltage

    def get_current(self, channel: str) -> float:
        """Request current of given channel."""
        current = float("nan")
        overflow_value = 1e37
        if self.command_set == "US":
            answer = self.port.query("TI" + str(channel))
            self.reading_status = answer[0]
            current = float(answer[3:])
            if current > overflow_value:
                current = float("nan")
        return current

    def get_installed_smu_channels(self) -> list[str]:
        """Return the channel numbers of the installed SMUs from *OPT?, e.g. ['1', '2'] for 'SMU1,HPSMUPA2,CVU1'."""
        options = self.get_options()
        channels = []
        for slot in options.split(","):
            match = re.fullmatch(r"(?:HP)?SMU(?:PA)?(\d)", slot.strip())
            if match:
                channels.append(match.group(1))
        return channels

    def set_kxci_page(self, page: str) -> None:
        """Select a page of the KXCI system mode: DE (channels), SS (sources), SM (measurement), MD (control)."""
        self.port.write(page)
        self.read_tcpip_port()

    def define_kxci_channel(
        self,
        channel: str,
        voltage_name: str,
        current_name: str,
        source_mode: int,
        source_function: int,
    ) -> None:
        """Define a SMU channel on the DE page (CH).

        Source mode: 1 voltage, 2 current, 3 common. Source function: 1 VAR1, 2 VAR2, 3 constant, 4 VAR1'.
        """
        self.port.write(f"CH{channel},'{voltage_name}','{current_name}',{source_mode},{source_function}")
        self.read_tcpip_port()

    def switch_off_kxci_channel(self, channel: str) -> None:
        """Remove a SMU channel from the test on the DE page (CH without parameters)."""
        self.port.write(f"CH{channel}")
        self.read_tcpip_port()

    def set_kxci_source_range(self, channel: str, source_range: float) -> None:
        """Set a fixed source range in A on any system mode page (SR); 0 is auto range."""
        self.port.write(f"SR {channel}, {format_kxci_number(source_range)}")
        self.read_tcpip_port()

    def set_kxci_list_sweep(self, channel: str, source: str, compliance: float, values: list[float]) -> None:
        """Set up the list sweep of the master channel on the SS page (VL or IL, master mode 1)."""
        command = "VL" if source == "Voltage in V" else "IL"
        list_values = ",".join(format_kxci_number(value) for value in values)
        self.port.write(f"{command}{channel},1,{format_kxci_number(compliance)},{list_values}")
        self.read_tcpip_port()

    def set_kxci_constant_source(self, channel: str, source: str, value: float, compliance: float) -> None:
        """Set a channel to a constant voltage or current on the SS page (VC or IC)."""
        command = "VC" if source == "Voltage in V" else "IC"
        self.port.write(f"{command}{channel},{format_kxci_number(value)},{format_kxci_number(compliance)}")
        self.read_tcpip_port()

    def set_kxci_sweep_delay(self, delay: float) -> None:
        """Set the delay in s between setting a sweep step and measuring it on the SS page (DT)."""
        self.port.write(f"DT {format_kxci_number(delay)}")
        self.read_tcpip_port()

    def set_kxci_sweep_hold_time(self, hold_time: float) -> None:
        """Set the hold time in s before the first sweep step on the SS page (HT)."""
        self.port.write(f"HT {format_kxci_number(hold_time)}")
        self.read_tcpip_port()

    def set_kxci_display_mode(self, display_mode: int) -> None:
        """Select the display mode on the SM page (DM): 1 graphics, 2 list."""
        self.port.write(f"DM{display_mode}")
        self.read_tcpip_port()

    def set_kxci_list_functions(self, names: list[str]) -> None:
        """Select the voltages and currents (by their CH names) that are measured in list display mode (LI)."""
        self.port.write("LI " + ",".join(f"'{name}'" for name in names))
        self.read_tcpip_port()

    def start_kxci_test(self) -> None:
        """Run a single trigger test into the cleared buffer on the MD page (ME1)."""
        self.port.write("ME1")
        self.read_tcpip_port()

    def abort_kxci_test(self) -> None:
        """Abort a running test (ME4)."""
        self.port.write("ME4")
        self.read_tcpip_port()

    def get_kxci_realtime_reading(self, name: str, index: int) -> float:
        """Return reading 'index' (from 1) of the named function while a test runs (RD); 0 if not measured yet."""
        answer = self.port.query(f"RD '{name}', {int(index)}")
        return parse_kxci_number(answer)

    def get_kxci_readings(self, name: str) -> list[float]:
        """Return all readings of the named function after a test (DO). Append 'T' to the name for the timestamps."""
        answer = self.port.query(f"DO '{name}'")
        return [parse_kxci_number(reading) for reading in answer.split(",") if reading.strip()]

    def set_pulse_impedance(self, channel: str, impedance: str) -> str:
        """Set the pulse impedance of the device."""
        impedance = float(impedance)
        minimum_impedance = 1.0
        maximum_impedance = 1e6
        if impedance < minimum_impedance:
            msg = f"Impedance of {impedance} too low. Must be between 1.0 and 1e6."
            raise ValueError(msg)
        if impedance > maximum_impedance:
            msg = f"Impedance of {impedance} too high. Must be between 1.0 and 1e6."
            raise ValueError(msg)

        self.port.write(f"PD {channel}, {impedance}")

        return self.read_tcpip_port()

    def set_pulse_trigger_mode(self, channel: str, mode: int, count: int) -> str:
        """Set pulse trigger mode.

        Mode:
            Burst mode: 0
            Continuous: 1 (default)
            Trigger burst: 2

        Count:
            Burst or trigger burst only: Pulse count in number of pulses: 1 to 232-1; set to 1 for
            continuous (default 1)
        """
        self.port.write(f"PG {channel}, {mode}, {count}")
        return self.read_tcpip_port()

    def set_pulse_stop(self, channel: str) -> str:
        """Stop pulse output for given channel."""
        self.port.write(f"PH {channel}")
        return self.read_tcpip_port()

    def set_pulse_output(self, channel: str, output: str) -> str:
        """Set pulse output of given channel."""
        self.port.write(f"PO {channel}, {output}")
        return self.read_tcpip_port()

    def set_pulse_reset(self, channel: str) -> str:
        """Reset pulse for given channel."""
        self.port.write(f"PS {channel}")
        return self.read_tcpip_port()

    def set_pulse_timing(self, channel: str, period: str, width: str, rise_time: str, fall_time: str) -> str:
        """Set pulse timing for given channel."""
        self.port.write(f"PT {channel}, {period}, {width}, {rise_time}, {fall_time}")
        return self.read_tcpip_port()

    def set_pulse_levels(self, channel: str, pulse_high: str, pulse_low: str, range: str, current_limit: str) -> str:
        """This command sets pulse high, pulse low, range, and current limit independently the given channel."""
        self.port.write(f"PV {channel}, {pulse_high}, {pulse_low}, {range}, {current_limit}")
        return self.read_tcpip_port()

    def set_pulse_output_parameters(self, channel: str, pulse_delay: str, trigger_polarity: str) -> str:
        """This command sets the trigger output parameters for pulse delay and trigger polarity."""
        self.port.write(f"TO {channel}, {pulse_delay}, {trigger_polarity}")
        return self.read_tcpip_port()

    def set_pulse_source(self, channel: str, trigger_source: str) -> str:
        """This command sets the trigger source that is used to trigger the pulse card to start its output."""
        self.port.write(f"TS {channel}, {trigger_source}")
        return self.read_tcpip_port()

    def kult_get_module_description(self, library: str, module: str) -> str:
        """Returns a description of the Library module.

        Attention: only works after EX command has been used before.
        """
        self.port.write(f"GD {library} {module}")
        return self.port.read()

    def kult_execute_module(self, library: str, module: str, *args) -> str:
        arguments = ", ".join([str(x) for x in args])
        self.port.write(f"EX {library} {module}({arguments})")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            print("EX TCPIP read:", answer)

        return self.port.read()

    def kult_abort(self) -> None:
        """Abort KULT."""
        self.port.write("AB")

    def kult_get_parameter(self, name_or_index: str | int, num_values=None) -> None:
        """Retrieves information about the function arguments.

        Args:
            name_or_index: define parameter by name using string or by index using integer
            num_values: in case of an array, the number of values can be defined
        """
        if isinstance(name_or_index, str):
            command = f"GN {name_or_index}"
            if num_values:
                command += " %i" % int(num_values)
            self.port.write(command)
        elif isinstance(name_or_index, int):
            command = f"GP {name_or_index!s}"
            if num_values:
                command += " %i" % int(num_values)
            self.port.write(command)
