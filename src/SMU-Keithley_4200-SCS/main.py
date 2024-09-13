# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022-2024 SweepMe! GmbH (sweep-me.net)
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

import os
import time

import numpy as np
from pysweepme import FolderManager
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

FolderManager.addFolderToPATH()

import importlib

import ProxyClass

importlib.reload(ProxyClass)

from ProxyClass import Proxy

# standard path for LPTlib.dll
# If it exists, SweepMe! is running on the instruments PC
RUNNING_ON_4200SCS = os.path.exists(r"C:\s4200\sys\bin\lptlib.dll")

if RUNNING_ON_4200SCS:
    # import LPT library functions
    # import LPT library instrument IDs
    # not available yet -> # from pylptlib import inst
    # import LPT library parameter constants
    from pylptlib import lpt, param


class Device(EmptyDevice):
    """Keithley 4200-SCS driver."""
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
        }

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
        self.speed: str = "Very fast"
        self.channel: str = "SMU1"

        self.card_name = "SMU" + self.channel[-1]
        self.pulse_channel = None

        # Pulse Mode Parameters
        self.pulse_master = False
        self.pulse_mode: bool = False

        self.pulse_count: int = 1
        self.pulse_meas_start: float = 50
        self.pulse_meas_duration: float = 20
        self.pulse_width: float = 0.5e-6
        self.pulse_period: float = 2e-6
        self.pulse_delay: float = 1e-9
        self.pulse_base_level: float = 0.0
        self.pulse_rise_time: float = 100e-9
        self.pulse_fall_time: float = 100e-9
        self.pulse_impedance: float = 1e6

    @staticmethod
    def find_ports() -> list[str]:
        """Find available ports."""
        return ["LPTlib"] if RUNNING_ON_4200SCS else ["LPTlib via xxx.xxx.xxx.xxx"]

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Rear"],
            "Channel": ["SMU1", "SMU2", "SMU3", "SMU4", "PMU1 - CH1", "PMU1 - CH2"],
            "Speed": list(self.speed_dict.keys()),
            "Compliance": 100e-6,
            "Range": list(self.current_ranges.keys()),
            "CheckPulse": False,
            "PulseCount": 1,
            "PulseMeasStart": 50,
            "PulseMeasTime": 20,
            "PulseOnTime": 0.5e-6,
            "PulseWidth": 1e-6,
            "PulsePeriod": 2e-6,
            "PulseDelay": 1e-9,
            "PulseOffLevel": 0.0,
            "PulseRiseTime": 100e-9,
            "PulseFallTime": 100e-9,
            "PulseImpedance": 1e6,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]
        self.identifier = "Keithley_4200-SCS_" + self.port_string

        self.route_out = parameter["RouteOut"]
        self.current_range = parameter["Range"]

        self.source = parameter["SweepMode"]

        self.protection = parameter["Compliance"]
        self.speed = parameter["Speed"]

        self.channel = parameter["Channel"]

        # The channel can be either "SMU1", "SMU2", "PMU1 - CH1" or "PMU1 - CH2"
        # It means that in case of PMU the pulse channel is additionally added after the card name
        # The card name is now always "SMU1", "SMU2", or "PMU1" etc.
        if "PMU" in self.channel:
            self.card_name = self.channel.split("-")[0].strip()
            self.pulse_channel = int(self.channel.split("-")[1][-1])
        elif "SMU" in self.channel:
            self.card_name = self.channel
            self.pulse_channel = None
        else:
            # This is a fallback, when channels have been just "1", "2", "3", "4". After adding PMU, it became
            # necessary to distinguish between SMU and PMU
            self.card_name = "SMU" + self.channel[-1]
            self.pulse_channel = None

        self.shortname = "4200-SCS %s" % parameter["Channel"]

        self.port_manager = "lptlib" not in self.port_string.lower()

        self.pulse_master = False
        self.pulse_mode = parameter["CheckPulse"]
        if self.pulse_mode:
            # backward compatibility as new fields have been added that are not
            # present in older SMU module versions
            try:
                self.pulse_count = parameter["PulseCount"]
                self.pulse_meas_start = parameter["PulseMeasStart"]
                self.pulse_meas_duration = parameter["PulseMeasTime"]
                self.pulse_width = float(parameter["PulseOnTime"])
                self.pulse_period = float(parameter["PulsePeriod"])
                self.pulse_delay = float(parameter["PulseDelay"])
                self.pulse_base_level = parameter["PulseOffLevel"]
                self.pulse_rise_time = parameter["PulseRiseTime"]
                self.pulse_fall_time = parameter["PulseFallTime"]
                self.pulse_impedance = parameter["PulseImpedance"]
            except KeyError:
                debug("Please update the SMU module to support all features of the Keithley 4200-SCS instrument driver")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if self.port_manager:
            self.command_set = "US"  # "US" user mode, "LPTlib", # check manual p. 677/1510

            # very important, triggers a (DCL) in KXCI, seems to be essential to read correct values
            self.port.port.clear()

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
            except ConnectionRefusedError:
                debug(
                    "Unable to connect to a lptlib server application running on the 4200-SCS. Please check your "
                    "network settings and make sure the server application is running.",
                )
                raise

            self.card_id = self.lpt.getinstid(self.card_name)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.check_test_parameter()

        if self.identifier not in self.device_communication:
            if self.command_set == "LPTlib":
                if self.pulse_mode:
                    self.lpt.dev_abort()  # stops executed pulses
                self.lpt.tstsel(1)
                self.lpt.devint()  # This command resets all active instruments in the system to their default states.

            elif self.command_set == "US":
                if self.current_range != "Auto":
                    msg = "When using KXCI only Auto current range is supported."
                    raise Exception(msg)

                self.get_options()

                self.clear_buffer()
                self.set_to_4200()
                self.set_command_mode("US")
                self.set_data_service()
                self.set_resolution(7)

            self.device_communication[self.identifier] = {}  # dictionary that can be filled with further information

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
            self.configure_lptlib()

        elif self.command_set == "US":
            # Integration/Speed
            if self.speed == "Very fast":
                msg = (
                    "Speed of 'Very Fast' is not supported for US command set via GPIB/TCPIP. "
                    "Use control via 'LPTlib' instead."
                )
                raise ValueError(msg)
            nplc = 1 if self.speed == "Fast" else 2
            self.set_integration_time(nplc)

            # Current Range
            if "Limited" in self.current_range:
                current_range = self.current_ranges[self.current_range]
                self.set_current_range_limited(self.card_name[-1], current_range)  # low range current

            # TODO: needs to be tested how to see a fixed current range
            # range = 1e-1
            # compliance = 1e1
            # self.set_current_range(self.card_name[-1], range, compliance)

    def configure_lptlib(self) -> None:
        """Configure the device using lptlib commands."""
        # can be used to change the limit indicator value
        # self.lpt.setmode(self.card_id, self.param.KI_LIM_INDCTR, float(self.protection))

        # return real measured value when in compliance, not indicator value like 7.0e22
        self.lpt.setmode(self.card_id, self.param.KI_LIM_MODE, self.param.KI_VALUE)

        # Protection
        if self.source == "Voltage in V":
            self.lpt.limiti(self.card_id, float(self.protection))  # compliance/protection
        elif self.source == "Current in A":
            self.lpt.limitv(self.card_id, float(self.protection))  # compliance/protection

        # Integration/Speed
        nplc_value = self.speed_dict[self.speed]
        self.lpt.setmode(self.card_id, self.param.KI_INTGPLC, nplc_value)  # integration time

        # Current Range
        if self.current_range == "Auto" or "Limited" in self.current_range:
            self.lpt.rangei(self.card_id, 0)  # auto-ranging
        else:
            current_range = self.current_ranges[self.current_range]
            self.lpt.rangei(self.card_id, current_range)  # fixed range

        if "Limited" in self.current_range:
            current_range = self.current_ranges[self.current_range]
            self.lpt.lorangei(self.card_id, current_range)  # low range current

        # self.lpt.lorangev(self.card_id, 1e-1)  # low range voltage

        # Range delay off
        self.lpt.setmode(self.card_id, self.param.KI_RANGE_DELAY, 0.0)  # disable range delay

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        if self.pulse_mode and self.pulse_master:
            del self.device_communication[self.identifier]["Pulse master"]

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
            voltage_range = 0  # auto
            current_range = 0  # auto

            if self.source == "Voltage in V":
                self.set_voltage(self.card_name[-1], voltage_range, self.value, self.protection)
            elif self.source == "Current in A":
                self.set_current(self.card_name[-1], current_range, self.value, self.protection)

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

    def measure(self) -> None:
        """Start the pulse measurement if in pulse mode."""
        if self.pulse_mode and self.pulse_master:
            # TODO: only the master driver instance needs to execute
            self.lpt.pulse_exec(mode=self.param.PULSE_MODE_SIMPLE)  # Alternatively self.param.PULSE_MODE_ADVANCED

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

            self.v = np.average(v_meas)
            self.i = np.average(i_meas)

    def call(self) -> list:
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables."""
        if not self.pulse_mode:
            if self.command_set == "LPTlib":
                self.v = self.lpt.intgv(self.card_id)
                self.i = self.lpt.intgi(self.card_id)

                # needed to give some time to update the plot
                # it seems that the LPTlib access is somehow blocking the entire program
                time.sleep(0.001)

            elif self.command_set == "US":
                self.v = self.get_voltage(self.card_name[-1])
                self.i = self.get_current(self.card_name[-1])

            """
            X Y Z +-N.NNNN E+-NN
            X The status of the data (where X = N for a normal reading)
            Y The measure channel (Y = A through F)
            Z The measure mode (Z = V or I)
            +-N.NNNN E+-NN is the reading (mantissa and exponent)
            """

        return [self.v, self.i]

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

    def set_current_range(self, channel: str, current_range: str, compliance: str) -> str:
        """Set the current range of the device."""
        if self.command_set == "US":
            self.port.write(f"RI {channel}, {current_range}, {compliance}")
        return self.read_tcpip_port()

    def set_current_range_limited(self, channel: str, current: float) -> str:
        """Set the current range of the device."""
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
        self.port.write("EM 1,0")  # set to 4200 mode for this session
        return self.read_tcpip_port()

    def enable_user_mode(self) -> str:
        """Enable user mode."""
        self.port.write("US")  # user mode
        return self.read_tcpip_port()

    def set_data_service(self) -> str:
        """Set data ready service."""
        if self.command_set == "US":
            self.port.write("DR0")  # data ready service request
        return self.read_tcpip_port()

    def set_integration_time(self, nplc: int) -> str:
        """Set the integration time of the device."""
        if self.command_set == "US":
            self.port.write("IT" + str(nplc))
        return self.read_tcpip_port()

    def set_current(self, channel: str, current_range: int, value: float, protection: float) -> str:
        """Set the current of the given channel."""
        if self.command_set == "US":
            self.port.write(f"DI{channel}, {current_range}, {value}, {protection}")
        return self.read_tcpip_port()

    def set_voltage(self, channel: str, voltage_range: int, value: float, protection: float) -> str:
        """Set the voltage of the given channel."""
        if self.command_set == "US":
            self.port.write(f"DV{channel}, {voltage_range}, {value}, {protection}")
        return self.read_tcpip_port()

    def get_voltage(self, channel: str) -> float:
        """Request voltage of given channel."""
        voltage = float("nan")
        overflow_value = 1e37
        if self.command_set == "US":
            self.port.write("TV" + str(channel))
            answer = self.port.read()
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
            self.port.write("TI" + str(channel))
            answer = self.port.read()
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
