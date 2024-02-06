# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023-2024 SweepMe! GmbH (sweep-me.net)
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
# Type: SMU
# Device: Keithley 4200-SCS
# Author: Axel Fischer (axel.fischer@sweep-me.net), Shayan Miri (shayan.miri@sweep-me.net)

from pysweepme.ErrorMessage import error, debug
from pysweepme.EmptyDeviceClass import EmptyDevice
import numpy as np
import time
import os

from pysweepme import FolderManager
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
    from pylptlib import lpt
    # import LPT library instrument IDs
    # not available yet -> # from pylptlib import inst
    # import LPT library parameter constants
    from pylptlib import param


class Device(EmptyDevice):

    description = """
    This driver only supports creating pulses in continuous mode
    Communication only via lptlib.dll or lptlib server.
    """

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        # so far this driver only supports communication via lptlib
        # if not RUNNING_ON_4200SCS:
        #     self.port_types = ['GPIB', 'TCPIP']
            # needed to make the code working with pysweepme where port_manager is only used from __init__
            # self.port_manager = True

        # self.port_properties = {
        #     "EOL": "\r\n",
        #     "timeout": 10.0,
        #     "TCPIP_EOLwrite": "\x00",
        #     "TCPIP_EOLread": "\x00",
        # }

        self.pulse_modes = {
            "Burst": 0,
            "Continuous": 1,
            "Trigger burst": 2,
        }

    def find_ports(self):
        # TODO: update SweepMe! to allow finding ports next to the automatically found one

        ports = ["LPTlib via xxx.xxx.xxx.xxx"]

        if RUNNING_ON_4200SCS:
            ports.insert(0, "LPTlib control - no port required")

        return ports
        
    def set_GUIparameter(self):
        
        GUIparameter = {
            "SweepMode": [None],
            "Channel": ["PMU1 - CH1", "PMU1 - CH2"],

            "Waveform": ["Pulse"],
            "PeriodFrequency": ["Period in s"],  # "Frequency in Hz"],
            "PeriodFrequencyValue": 2e-6,
            "AmplitudeHiLevel": ["High level in V"],  # "Amplitude in V"],
            "AmplitudeHiLevelValue": 1.0,
            "OffsetLoLevel": ["Low level in V"],  # "Offset in V"],
            "OffsetLoLevelValue": 0.0,
            "DelayPhase": ["Delay in s"],  # "Phase in deg"],
            "DelayPhaseValue": 0.0,
            "DutyCyclePulseWidth": ["Pulse width in s"],  # "Duty cycle in %",],
            "DutyCyclePulseWidthValue": 1e-6,

            "RiseTime": 100e-9,
            "FallTime": 100e-9,

            "Impedance": ["50", "1e6"],

            # "OperationMode": ["Range 20 V (slow)", "Range 5 V (fast)"]
        }

        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):

        self.port_string = parameter['Port']
        self.identifier = "Keithley_4200-SCS_" + self.port_string

        self.waveform = parameter['Waveform']
        self.periodfrequency = parameter['PeriodFrequency']
        self.periodfrequencyvalue = float(parameter['PeriodFrequencyValue'])
        self.amplitudehilevel = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue = float(parameter['AmplitudeHiLevelValue'])
        self.offsetlolevel = parameter['OffsetLoLevel']
        self.offsetlolevelvalue = float(parameter['OffsetLoLevelValue'])
        self.dutycyclepulsewidth = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue = float(parameter['DutyCyclePulseWidthValue'])
        self.delayphase = parameter['DelayPhase']
        self.delayphasevalue = float(parameter['DelayPhaseValue'])
        self.impedance_value = parameter['Impedance']

        self.rise_time = parameter['RiseTime']
        self.fall_time = parameter['FallTime']

        self.channel = parameter["Channel"]

        self.card_name = self.channel.split("-")[0].strip()
        self.pulse_channel = int(self.channel.split("-")[1][-1])

        self.shortname = "4200-SCS %s" % parameter["Channel"]

        if "lptlib" in self.port_string.lower():
            self.port_manager = False
        else:
            self.port_manager = True

    def connect(self):

        if self.port_manager:
            self.command_set = 'US'  # "US" user mode, "LPTlib", # check manual p. 677/1510

            # very important, triggers a (DCL) in KXCI, seems to be essential to read correct values
            self.port.port.clear()

        else:
            self.command_set = "LPTlib"  # "US" user mode, "LPTlib", # check manual p. 677/1510

            if not RUNNING_ON_4200SCS:
                # overwriting the communication classes with Proxy classes

                tcp_ip_port = self.port_string[11:].strip()  # removing "LPTlib via "
                tcp_ip_port_splitted = tcp_ip_port.split(":")  # in case a port is given
                tcp_ip = tcp_ip_port_splitted[0]
                if len(tcp_ip_port_splitted) == 2:
                    tcp_port = int(tcp_ip_port_splitted[1])
                else:
                    tcp_port = 8888  # default

                self.lpt = Proxy(tcp_ip, tcp_port, "lpt")
                # not supported yet with pylptlib -> # self.inst = Proxy(tcp_ip, tcp_port, "inst")
                self.param = Proxy(tcp_ip, tcp_port, "param")

            else:
                # we directly use pylptlib
                self.lpt = lpt
                # not supported yet with pylptlib -> # self.inst = inst
                self.param = param

            ret = self.lpt.initialize()
            
            self.card_id = self.lpt.getinstid(self.card_name)

    def initialize(self):

        if self.identifier not in self.device_communication:
                 
            if self.command_set == "LPTlib":
                self.lpt.dev_abort()
                self.lpt.tstsel(1)
                self.lpt.devint()  # This command resets all active instruments in the system to their default states.

                # setup pulses/waveform
                self.lpt.pg2_init(self.card_id, mode_id=0)  # set to standard pulse
                self.lpt.pulse_init(self.card_id)  # reset standard pulse settings to default
                self.lpt.pulse_trig_source(self.card_id, source=0)  # software trigger

            elif self.command_set == "US":
                options = self.get_options()
                # print("Options:", options)

                self.clear_buffer()
                self.set_to_4200()
                self.set_command_mode("US")
                self.set_data_service()
                self.set_resolution(7)

            self.device_communication[self.identifier] = {}  # dictionary that can be filled with further information

    def deinitialize(self):

        if self.identifier in self.device_communication:

            if self.command_set == "LPTlib":
                self.lpt.devint()  # restores default values
                self.lpt.tstdsl()  # not implemented yet
                
            del self.device_communication[self.identifier]
                     
    def configure(self):

        self.lpt.rpm_config(self.card_id, self.pulse_channel, self.param.KI_RPM_PATHWAY, self.param.KI_RPM_PULSE)

        # needed for later implementation of burst mode
        # pulse_count = 10
        # self.lpt.pulse_burst_count(self.card_id, self.pulse_channel, pulse_count)

        self.lpt.pulse_load(self.card_id, self.pulse_channel, float(self.impedance_value))

        if float(self.impedance_value) >= 1e6:
            voltage_range_threshold = 10.0
        else:
            voltage_range_threshold = 5.0

        if max(abs(self.amplitudehilevelvalue), abs(self.offsetlolevelvalue)) > voltage_range_threshold:
            voltage_range = 20.0
        else:
            voltage_range = 5.0

        self.lpt.pulse_range(
            self.card_id,
            self.pulse_channel,
            voltage_range,
        )

        self.lpt.pulse_delay(self.card_id, self.pulse_channel, float(self.delayphasevalue))
        self.lpt.pulse_period(self.card_id, self.pulse_channel, float(self.periodfrequencyvalue))
        self.lpt.pulse_width(self.card_id, self.pulse_channel, float(self.dutycyclepulsewidthvalue))
        self.lpt.pulse_rise(self.card_id, self.pulse_channel, float(self.rise_time))
        self.lpt.pulse_fall(self.card_id, self.pulse_channel, float(self.fall_time))
        self.lpt.pulse_vhigh(self.card_id, self.pulse_channel, float(self.amplitudehilevelvalue))
        self.lpt.pulse_vlow(self.card_id, self.pulse_channel, float(self.offsetlolevelvalue))

        # change the mode and triggers the pulse
        # TODO: in case of burst, it must be sent only once for the master

        pulse_mode = self.pulse_modes["Continuous"]
        self.lpt.pulse_trig(self.card_id, pulse_mode)

    def unconfigure(self):
        pass

    def poweron(self):

        self.lpt.pulse_output(
            self.card_id,
            self.pulse_channel,
            out_state=1
        )

    
    def poweroff(self):

        self.lpt.pulse_output(
            self.card_id,
            self.pulse_channel,
            out_state=0
        )

    def apply(self):
        self.value = float(self.value)

    def trigger_ready(self):
        pass

    def measure(self):
        pass

    def request_result(self):
        pass

    def read_result(self):
        pass

    def call(self):
        return []


    # """ here, convenience functions start """


    """ here wrapped functions start """

    def set_command_mode(self, mode):
        """
        mode:
            US -> user mode
            UL -> usrlib
        """

        self.port.write(f"{mode}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def get_identifier(self):
        self.port.write("*IDN?")
        return self.port.read()

    def get_options(self):
        self.port.write("*OPT?")
        return self.port.read()
    
    def set_resolution(self, resolution):
        if self.command_set == 'US':
            self.port.write(f"RS {int(resolution)}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer
        
    def set_current_range(self, channel, current_range, compliance):
        if self.command_set == 'US':
            self.port.write(f"RI {channel}, {current_range}, {compliance}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_current_range_limited(self, channel, current):
        if self.command_set == 'US':
            self.port.write(f"RG {channel}, {current}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def switch_off(self, channel):
        if self.command_set == 'US':
            self.port.write(f"DV{channel}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def clear_buffer(self):
        self.port.write("BC")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_to_4200(self):
        self.port.write("EM 1,0")  # set to 4200 mode for this session

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def enable_user_mode(self):
        self.port.write("US")  # user mode

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_data_service(self):
        if self.command_set == 'US':
            self.port.write("DR0")  # data ready service request

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_integration_time(self, nplc):
        if self.command_set == 'US':
            self.port.write("IT" + str(nplc))

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_current(self, channel, current_range, value, protection):
        if self.command_set == 'US':
            self.port.write(f"DI{channel}, {current_range}, {value}, {protection}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_voltage(self, channel, voltage_range, value, protection):
        if self.command_set == 'US':
            self.port.write(f"DV{channel}, {voltage_range}, {value}, {protection}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def get_voltage(self, channel):
        if self.command_set == 'US':
            self.port.write("TV" + str(channel))
            answer = self.port.read()
            voltage = float(answer[3:])
            if voltage > 1e37:
                voltage = float('nan')
            return voltage
            
        # • N: Normal
        # • L: Interval too short
        # • V: Overflow reading (A/D converter saturated)
        # • X: Oscillation
        # • C: This channel in compliance
        # • T: Other channel in compliance

    def get_current(self, channel):
        if self.command_set == 'US':
            self.port.write("TI" + str(channel))
            answer = self.port.read()
            current = float(answer[3:])
            if current > 1e37:
                current = float('nan')
            return current

    def set_pulse_impedance(self, channel, impedance):
    
        impedance = float(impedance)
        if impedance < 1.0:
            raise ValueError(f"Impedance of {impedance} too low. Must be between 1.0 and 1e6.")
        elif impedance > 1e6:
            raise ValueError(f"Impedance of {impedance} too high. Must be between 1.0 and 1e6.")
    
        self.port.write(f"PD {channel}, {impedance}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_pulse_trigger_mode(self, channel, mode, count):
        """
        
        Mode:
            Burst mode: 0
            Continuous: 1 (default)
            Trigger burst: 2

        Count:
            Burst or trigger burst only: Pulse count in number of pulses: 1 to 232-1; set to 1 for
            continuous (default 1)            
        """
    
        self.port.write(f"PG {channel}, {mode}, {count}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_pulse_stop(self, channel):
    
        self.port.write(f"PH {channel}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_pulse_output(self, channel, output):
        
        self.port.write(f"PO {channel}, {output}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_pulse_reset(self, channel):
    
        self.port.write(f"PS {channel}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_pulse_timing(self, channel, period, width, rise_time, fall_time):
        
        self.port.write(f"PT {channel}, {period}, {width}, {rise_time}, {fall_time}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_pulse_levels(self, pulse_high, pulse_low, range, current_limit):
        """
        This command sets pulse high, pulse low, range, and current limit independently for each channel of the selected
        pulse card.
        """
        self.port.write(f"PV {channel}, {pulse_high}, {pulse_low}, {range}, {current_limit}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_pulse_output_parameters(self, channel, pulse_delay, trigger_polarity):
        """
        This command sets the trigger output parameters for pulse delay and trigger polarity.
        """
        self.port.write(f"TO {channel}, {pulse_delay}, {trigger_polarity}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def set_pulse_source(self, channel, trigger_source):
        """
        This command sets the trigger source that is used to trigger the pulse card to start its output.
        """
        self.port.write(f"TS {channel}, {trigger_source}")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            return answer

    def kult_get_module_description(self, library, module):

        """ returns a description of the Library module

        Attention: only works after EX command has been used before
        """

        self.port.write(f"GD {library} {module}")
        return self.port.read()

    def kult_execute_module(self, library, module, *args):

        arguments = ", ".join([str(x) for x in args])
        self.port.write(f"EX {library} {module}({arguments})")

        if self.port_string.startswith("TCPIP"):
            answer = self.port.read()
            print("EX TCPIP read:", answer)
            # return answer

        return self.port.read()

    def kult_abort(self):
        self.port.write("AB")

    def kult_get_parameter(self, name_or_index, num_values=None):

        """
        retrieves information about the function arguments

        Args:
            name_or_index: define parameter by name using string or by index using integer
            num_values: in case of an array, the number of values can be defined

        Returns:

        """

        if isinstance(name_or_index, str):
            command = f"GN {name_or_index}"
            if num_values:
                command += " %i" % int(num_values)
            self.port.write(command)
        elif isinstance(name_or_index, int):
            command = f"GP {str(name_or_index)}"
            if num_values:
                command += " %i" % int(num_values)
            self.port.write(command)
