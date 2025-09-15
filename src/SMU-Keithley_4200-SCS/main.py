# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022-2025 SweepMe! GmbH (sweep-me.net)
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
import ctypes as c
import platform
import time
from pathlib import Path

import numpy as np
from pysweepme import FolderManager
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

FolderManager.addFolderToPATH()


def running_on_device() -> bool:
    """Check if the driver is executed directly on the Keithley 4200-SCS hardware by trying to import the lptlib.dll."""
    dll_path = r"C:\s4200\sys\bin\lptlib.dll"

    # If Clarius is not installed and the dll is not available, the driver is not running on the device
    if not Path(dll_path).exists():
        return False

    # If the dll is available and can be imported, the driver is running on the device
    try:
        _dll = c.WinDLL(dll_path)
    except:
        # if the dll is available but cannot be imported, check the Python interpreter bitness
        if platform.architecture()[0] != "32bit":
            print(
                "Keithley 4200-SCS: Installation of Clarius detected, but lptlib.dll cannot be loaded. Using remote "
                "control via LPTlib server instead. If you are trying to run the driver directly on the device, use "
                "32-Bit version of Python/SweepMe!.",
            )
            return False

        return False

    return True


RUNNING_ON_4200SCS = running_on_device()

if RUNNING_ON_4200SCS:
    # import LPT library functions
    # import LPT library instrument IDs
    # not available yet -> # from pylptlib import inst
    # import LPT library parameter constants
    from pylptlib import lpt, param
else:
    import importlib

    import ProxyClass

    importlib.reload(ProxyClass)

    from ProxyClass import Proxy


class Device(EmptyDevice):
    """Keithley 4200-SCS driver."""

    description = """
        <h3>Keithley 4200-SCS</h3>

        <h4>Setup</h4>
        This driver can be used in three different ways:
        <ul>
        <li>Using the KXCI software running on the device and a GPIB connection.</li>
        <li>Using the LPTlib server application running on the device and a TCP/IP connection.</li>
        <li>Running SweepMe! directly on the device.</li>
        </ul>
        <p>Please note that for the KXCI mode, some features like Pulse Mode, List Mode, and fast acquisition are not
        supported yet.</p>

        <h4>Parameters</h4>
        <ul>
        <li>Current range: Limited: Sets the lowest current range of the SMU to be used when measuring with auto range
        to save time. Current range denotes the measurement range. The source range is set to 'auto' by default.</li>
        </ul>
        """

    def __init__(self) -> None:
        """Initialize device parameters."""
        EmptyDevice.__init__(self)

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        if not RUNNING_ON_4200SCS:
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
        self.current_range: str = "Auto"
        self.current_ranges = {
            "Auto": 0,
            "Fixed 10 mA": 1e-2,
            "Fixed 1 mA": 1e-3,
            "Fixed 100 µA": 1e-4,
            "Fixed 10 µA": 1e-5,
            "Fixed 1 µA": 1e-6,
            "Fixed 100 nA": 1e-7,
            "Fixed 10 nA": 1e-8,
            "Fixed 1 nA": 1e-9,
            "Fixed 100 pA": 1e-10,
            "Fixed 10 pA": 1e-11,
            "Fixed 1 pA": 1e-12,
            "Limited 10 mA": 1e-2,
            "Limited 1 mA": 1e-3,
            "Limited 100 µA": 1e-4,
            "Limited 10 µA": 1e-5,
            "Limited 1 µA": 1e-6,
            "Limited 100 nA": 1e-7,
            "Limited 10 nA": 1e-8,
            "Limited 1 nA": 1e-9,
            "Limited 100 pA": 1e-10,
            "Limited 10 pA": 1e-11,
            "Limited 1 pA": 1e-12,
        }

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

        self.lpt: lpt | Proxy | None = None
        self.param: param | Proxy | None = None

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

        self.card_name = "SMU" + self.channel[-1]
        self.pulse_channel = None

        self.measured_voltage: float = 0.0
        self.measured_current: float = 0.0

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
        return ["LPTlib"] if RUNNING_ON_4200SCS else ["LPTlib via xxx.xxx.xxx.xxx"]

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

        if sweep_value == "List sweep":
            self.list_master = True
            self.list_receiver = False
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
                # Remove leading and trailing commas
                custom_values = custom_values.strip(",")

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

            if self.list_master:
                msg = "List sweep is not supported with US command set via GPIB. Use control via 'LPTlib' instead."
                raise Exception(msg)
        else:
            self.command_set = "LPTlib"  # "US" user mode, "LPTlib", # check manual p. 677/1510

            if not RUNNING_ON_4200SCS:
                # overwriting the communication classes with Proxy classes
                tcp_ip_port = self.port_string[11:].strip()  # removing "LPTlib via "
                tcp_ip_port_splitted = tcp_ip_port.split(":")  # in case a port is given

                tcp_ip = tcp_ip_port_splitted[0]
                tcp_port = int(tcp_ip_port_splitted[1]) if len(tcp_ip_port_splitted) == 2 else 8888

                self.lpt = Proxy(tcp_ip, tcp_port, "lpt")
                # not supported yet with pylptlib -> # self.inst = Proxy(tcp_ip, tcp_port, "inst")
                self.param = Proxy(tcp_ip, tcp_port, "param")

            else:
                # we directly use pylptlib
                self.lpt = lpt
                # not supported yet with pylptlib -> # self.inst = inst
                self.param = param

            try:
                self.lpt.initialize()
            except ConnectionRefusedError as e:
                msg = ("Unable to connect to a lptlib server application running on the 4200-SCS. Please check your"
                       "network settings and make sure the server application is running.")
                raise ConnectionRefusedError(msg) from e
            except Exception as e:
                msg = "Error during lpt.initialize"
                raise Exception(msg) from e

            self.card_id = self.lpt.getinstid(self.card_name)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.check_test_parameter()

        if self.identifier not in self.device_communication:
            if self.command_set == "LPTlib":
                if self.pulse_mode:
                    self.lpt.dev_abort()  # stops executed pulses
                self.lpt.tstsel(1)  # select test station 1 and load instrument configuration. Choose 0 to deselect
                self.lpt.devint()  # This command resets all active instruments in the system to their default states.
                # calls devclr, clrcon (only for switching matrix), clrtrg, clrscn, kibdefint

            elif self.command_set == "US":
                self.get_options()  # TODO use

                self.clear_buffer()
                self.set_to_4200()
                self.set_command_mode("US")
                self.set_data_service()
                self.set_resolution(7)

            self.device_communication[self.identifier] = {}  # dictionary that can be filled with further information

        # If this channel should run the list sweep, register it as 'List master'
        # Checking if the list receiver should be used will be done in 'configure' after all channels are initialized
        if self.list_master:
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
            raise Exception("Please activate pulse mode for %s of the 4200-SCS parameter analyzer!" % self.channel)

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

        elif self.command_set == "LPTlib":
            if float(self.averages) > 1:
                msg = "Averaging is not supported yet with LPTlib command set."
                raise NotImplementedError(msg)
            self.configure_lptlib()

        elif self.command_set == "US":
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
            current_range_float = self.current_ranges[self.current_range]
            if "Limited" in self.current_range:
                self.set_current_range_limited(self.card_name[-1], current_range_float)

            elif self.current_range == "Auto":
                # Use the lowest current range for auto-ranging
                self.set_current_range_limited(self.card_name[-1], 0)

            else:
                self.set_current_range(self.card_name[-1], current_range_float, self.protection)

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

        # Current Range
        if self.current_range == "Auto" or "Limited" in self.current_range:
            self.lpt.rangei(self.card_id, 0)  # auto-ranging

            if "Limited" in self.current_range:
                current_range = self.current_ranges[self.current_range]
                self.lpt.lorangei(self.card_id, current_range)  # minimum current range for auto-ranging
        else:
            current_range = self.current_ranges[self.current_range]
            self.lpt.rangei(self.card_id, current_range)  # fixed range

        # self.lpt.lorangev(self.card_id, 1e-1)  # low range voltage

        # Range delay off
        self.lpt.setmode(self.card_id, self.param.KI_RANGE_DELAY, 0.0)  # disable range delay

    def start(self) -> None:
        """Preparation before applying a new value."""
        if self.list_master:
            # Clear the result arrays
            self.lpt.clrscn()

            # Update list length in case variable lists are used (e.g. by using ParameterSyntax of SweepMe)
            list_length = len(self.list_sweep_values)
            if list_length == 0:
                msg = "List for List Sweep is empty."
                raise ValueError(msg)

            self.device_communication[self.identifier]["List length"] = list_length

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        if self.pulse_mode and self.pulse_master:
            del self.device_communication[self.identifier]["Pulse master"]

        if self.list_master:
            self.lpt.reset_measurement_cache()

    def poweroff(self) -> None:
        """Turn off the device."""
        if self.pulse_mode:
            self.lpt.pulse_output(self.card_id, self.pulse_channel, out_state=0)
        elif self.command_set == "LPTlib":
            self.lpt.forcev(self.card_id, 0.0)
        elif self.command_set == "US":
            self.switch_off(self.card_name[-1])

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.pulse_mode:
            return

        self.value = float(self.value)

        if self.command_set == "LPTlib":
            if self.source == "Voltage in V":
                self.lpt.forcev(self.card_id, self.value)
            elif self.source == "Current in A":
                self.lpt.forcei(self.card_id, self.value)

        elif self.command_set == "US":
            # These ranges are the source ranges, not the compliance or measurement ranges
            voltage_source_range = 0  # auto
            # Currently, the current source range is always set to auto - should issue a warning
            current_source_range = 0  # auto

            if self.source == "Voltage in V":
                self.set_voltage(self.card_name[-1], voltage_source_range, self.value, float(self.protection))
            elif self.source == "Current in A":
                self.set_current(self.card_name[-1], current_source_range, self.value, float(self.protection))

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

        # Register result arrays for list mode
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

        if self.list_master:
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
        """Wait for pulse measurements to finish."""
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
                averages = int(self.averages)
                voltages = []
                currents = []

                for _ in range(averages):
                    voltages.append(self.get_voltage(self.card_name[-1]))

                for _ in range(averages):
                    currents.append(self.get_current(self.card_name[-1]))

                self.measured_voltage = np.mean(voltages)
                self.measured_current = np.mean(currents)

            """
            X Y Z +-N.NNNN E+-NN
            X The status of the data (where X = N for a normal reading)
            Y The measure channel (Y = A through F)
            Z The measure mode (Z = V or I)
            +-N.NNNN E+-NN is the reading (mantissa and exponent)
            """

        return [self.measured_voltage, self.measured_current]

    """ here, convenience functions start """

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

    def get_identifier(self) -> str:
        """Return IDN."""
        self.port.write("*IDN?")
        return self.port.read()

    def get_options(self) -> str:
        """Return OPT."""
        self.port.write("*OPT?")
        return self.port.read()

    def set_resolution(self, resolution: int) -> str:
        """Set the resolution of the device."""
        if self.command_set == "US":
            self.port.write(f"RS {int(resolution)}")
        return self.read_tcpip_port()

    def set_current_range(self, channel: str, current_range: float, compliance: float) -> str:
        """Set the current range of the device. Requires to set the compliance as well.

        When the SMU channel is used as a voltage source, the compliance is overwritten when setting the set value.
        """
        if self.command_set == "US":
            self.port.write(f"RI {channel}, {current_range}, {compliance}")
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
            "fast" : "1",  # = short
            "short": "1",
            "medium" : "2",  # medium
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
            voltage = float(answer[3:])
            if voltage > overflow_value:
                voltage = float("nan")
        return voltage

        # • N: Normal
        # • L: Interval too short
        # • V: Overflow reading (A/D converter saturated)
        # • X: Oscillation
        # • C: This channel in compliance
        # • T: Other channel in compliance

    def get_current(self, channel: str) -> float:
        """Request current of given channel."""
        current = float("nan")
        overflow_value = 1e37
        if self.command_set == "US":
            answer = self.port.query("TI" + str(channel))
            current = float(answer[3:])
            if current > overflow_value:
                current = float("nan")
        return current

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
