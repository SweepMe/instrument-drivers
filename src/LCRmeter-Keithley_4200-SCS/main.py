# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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

# SweepMe! device class
# Device: Keithley 4200-SCS
from __future__ import annotations

import os

from pysweepme import FolderManager
from pysweepme.EmptyDeviceClass import EmptyDevice

FolderManager.addFolderToPATH()

import importlib

import ProxyClass

importlib.reload(ProxyClass)

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
    """Device class for the Keithley 4200-SCS used as LCRmeter."""

    description = "This driver supports two CVU card models: 4210-CVU and 4215-CVU"

    def __init__(self) -> None:
        """Initializes the device class."""
        super().__init__()

        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]
        self.identifier: str = ""

        # block below is needed if KXCI handling will be implemented in future
        # where commands can be sent via GPIB or TCPIP
        # if not RUNNING_ON_4200SCS:

        # self.port_types = ["GPIB", "TCPIP"]
        # needed to make the code working with pysweepme where port_manager is only used from __init__
        # self.port_manager = True

        # self.port_properties = {
        #     "EOL": "\r\n",
        #     "timeout": 10.0,
        #     "TCPIP_EOLwrite": "\x00",
        #     "TCPIP_EOLread": "\x00",
        # }

        # Currently, only auto range is used
        self.current_ranges = {
            "Auto": 0,
        }

        self.operating_mode: str = ""
        self.operating_modes = {
            "ZTH": 0,  # "KI_CVU_TYPE_ZTH"
            "RjX": 1,  # "KI_CVU_TYPE_RJX"
            "CpGp": 2,  # "KI_CVU_TYPE_CPGP"
            "CsRs": 3,  # "KI_CVU_TYPE_CSRS"
            "CpD": 4,  # "KI_CVU_TYPE_CPD"
            "CsD": 5,  # "KI_CVU_TYPE_CSD"
            "YTH": 7,  # "KI_CVU_TYPE_YTH"
        }

        self.speed: str = ""
        self.speeds = {
            "Fast": 0,  # "KI_CVU_SPEED_FAST"
            "Normal": 1,  # "KI_CVU_SPEED_NORMAL",
            "Quiet": 2,  # "KI_CVU_SPEED_QUIET",
        }

        # Device specific properties
        self.frequency: int = 0

        # in case there is more than one CVU card possible, we need to use the option "Channel" which however
        # does not yet exist for the LCRmeter module and needs to be added in this case
        self.card_name = "CVU1"
        self.card_id: int = 0  # placeholder value

        self.measured_dc_bias: float = 0.0
        self.measured_frequency: float = 0.0
        self.resistance: float = 0.0
        self.reactance: float = 0.0

        self.bias_mode: str = ""

        self.integration = None
        self.ALC = None
        self.stepmode = None
        self.sweepmode = None
        self.shortname = "Keithley 4200-SCS"

    def find_ports(self) -> list:
        """Finds the available ports for the Keithley 4200-SCS LCRmeter."""
        ports = ["LPTlib via xxx.xxx.xxx.xxx"]

        if RUNNING_ON_4200SCS:
            ports.insert(0, "LPTlib control - no port required")

        return ports

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set initial GUI parameter in SweepMe!."""
        return {
            # "Average": ["1", "2", "4", "8", "16", "32", "64"],  # TODO: check
            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
            "ValueRMS": 0.02,  # TODO: Is it the RMS value or the amplitude
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            "Integration": list(self.speeds),
            "ALC": ["Off"],  # TODO: check
            "Trigger": ["Internal"],
            "TriggerDelay": "0.1",
            "Range": list(self.current_ranges),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Update parameter from SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.value_level_rms = float(parameter["ValueRMS"])
        self.value_bias = float(parameter["ValueBias"])
        self.frequency = float(parameter["Frequency"])
        self.integration = self.speeds[parameter["Integration"]]

        self.trigger_type = parameter["Trigger"]  # TODO: check
        self.trigger_delay = parameter["TriggerDelay"]  # TODO: needs to be processed somewhere
        self.range = self.current_ranges[parameter["Range"]]

        # Only use Resistance and reactance measurement
        self.operating_mode = self.operating_modes["RjX"]

    def connect(self) -> None:
        """Connect to the Keithley 4200-SCS LCRmeter."""
        if self.port_manager:
            pass  # not used at the moment because KXCI communication is not supported yet
            # self.command_set = "US"  # "US" user mode, "LPTlib", # check manual p. 677/1510
            #
            # # very important, triggers a (DCL) in KXCI, seems to be essential to read correct values
            # self.port.port.clear()

        else:
            self.command_set = "LPTlib"  # "US" user mode, "LPTlib", # check manual p. 677/1510

            if not RUNNING_ON_4200SCS:
                # overwriting the communication classes with Proxy classes
                tcp_ip_port = self.port_string[11:].strip()  # removing "LPTlib via "
                tcp_ip_port_splitted = tcp_ip_port.split(":")  # in case a port is given
                tcp_ip = tcp_ip_port_splitted[0]

                tcp_port = int(tcp_ip_port_splitted[1]) if len(tcp_ip_port_splitted) == 2 else 8888

                self.lpt = ProxyClass.Proxy(tcp_ip, tcp_port, "lpt")
                # not supported yet with pylptlib -> # self.inst = Proxy(tcp_ip, tcp_port, "inst")
                self.param = ProxyClass.Proxy(tcp_ip, tcp_port, "param")

            else:
                # we directly use pylptlib
                self.lpt = lpt
                # not supported yet with pylptlib -> # self.inst = inst
                self.param = param

            self.lpt.initialize()

            self.card_id = self.lpt.getinstid(self.card_name)

    def initialize(self) -> None:
        """Initialize the Keithley 4200-SCS LCRmeter."""
        # check for correct use of sweep mode and step mode
        if self.stepmode != "None" and self.sweepmode == self.stepmode:
            msg = "Sweep and step mode cannot be the same."
            raise Exception(msg)

        self.identifier = "Keithley_4200-SCS_" + self.port_string

        if self.identifier not in self.device_communication:
            if self.command_set == "LPTlib":
                self.lpt.tstsel(1)
                self.lpt.devint()  # This command resets all active instruments in the system to their default states.

            elif self.command_set == "US":
                pass  # not used at the moment because KXCI communication is not supported yet
                # if self.current_range != "Auto":
                #     msg = "When using KXCI only Auto current range is supported."
                #     raise Exception(msg)
                #
                # self.clear_buffer()
                # self.set_to_4200()
                # self.set_command_mode("US")
                # self.set_data_service()
                # self.set_resolution(7)

            self.device_communication[self.identifier] = {}  # dictionary that can be filled with further information

    def deinitialize(self) -> None:
        """Reset device and close connection."""
        if self.identifier in self.device_communication:
            if self.command_set == "LPTlib":
                self.lpt.devint()  # restores default values
                self.lpt.tstdsl()  # deselects test station

            del self.device_communication[self.identifier]

    def configure(self) -> None:
        """Set bias and measurement parameters with start values from GUI."""
        self.set_ac_frequency(self.frequency)
        self.set_delay(self.trigger_delay)

        self.set_dc_bias(self.value_bias)
        self.set_ac_voltage(self.value_level_rms)

        self.set_measure_range()

    def unconfigure(self) -> None:
        """Reset device."""
        self.reset_cvu()

    def apply(self) -> None:
        """Apply settings."""
        if self.sweepmode != "None":
            sweep_value = float(self.value)
            self.handle_set_value(self.sweepmode, sweep_value)

        if self.stepmode != "None":
            step_value = float(self.stepvalue)
            self.handle_set_value(self.stepmode, step_value)

    def measure(self) -> None:
        """Retrieve Impedance results from device."""
        # Only measurement mode RjX is used
        self.resistance, self.reactance = self.measure_impedance()

        self.measured_frequency = self.measure_frequency()
        self.measured_dc_bias = self.measure_dc_bias()

    def call(self) -> list[float]:
        """Return ["R", "X", "Frequency", "Voltage bias" or "Voltage level"]."""
        return [self.resistance, self.reactance, self.measured_frequency, self.measured_dc_bias]

    """ here, convenience functions start """

    def handle_set_value(self, mode: str, value: float) -> None:
        """Set value for sweep or step mode."""
        if mode == "Voltage bias in V":
            self.set_dc_bias(value)

        elif mode == "Voltage level in V":
            self.set_ac_voltage(value)

        elif mode == "Frequency in Hz":
            self.set_ac_frequency(value)

    """ here wrapped functions start """

    def set_dc_bias(self, dc_bias: float) -> None:
        """Set DC bias in Volt."""
        self.lpt.forcev(self.card_id, dc_bias)

    def set_ac_voltage(self, ac_voltage: float) -> None:
        """Set AC voltage in Volt."""
        self.lpt.setlevel(self.card_id, ac_voltage)

    def set_ac_frequency(self, ac_frequency: float) -> None:
        """Set AC frequency in Hz."""
        self.lpt.setfreq(self.card_id, ac_frequency)

    def set_delay(self, delay: float) -> None:
        """Set delay in seconds."""
        self.lpt.rdelay(delay)

    def set_measure_range(self) -> None:
        """Set measure range."""
        # Currently, only auto range is used
        if self.range == 0:
            self.lpt.setauto(self.card_id)

    def measure_impedance(self) -> list[float]:
        """Measure impedance."""
        result1, result2 = self.lpt.measz(self.card_id, self.operating_mode, self.speed)
        return [result1, result2]

    def measure_frequency(self) -> float:
        """Measure frequency sourced during single measurement."""
        return self.lpt.measf(self.card_id)

    def measure_dc_bias(self) -> float:
        """Measure DC bias sourced during single measurement."""
        return self.lpt.measv(self.card_id)

    def reset_cvu(self) -> None:
        """Reset CVU."""
        self.lpt.devint()
