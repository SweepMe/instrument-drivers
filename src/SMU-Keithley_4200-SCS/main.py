# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018-2019, 2022-2023 SweepMe! GmbH (sweep-me.net)
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

import FolderManager
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

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        if not RUNNING_ON_4200SCS:
            self.port_types = ['GPIB', 'TCPIP']
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
        
    def find_ports(self):
        # TODO: update SweepMe! to allow finding ports next to the automatically found one

        ports = ["LPTlib via xxx.xxx.xxx.xxx"]

        if RUNNING_ON_4200SCS:
            ports.insert(0, "LPTlib control - no port required")

        return ports
        
    def set_GUIparameter(self):
        
        GUIparameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Rear"],
            "Channel": ["SMU1", "SMU2", "SMU3", "SMU4", "PMU1 - CH1", "PMU1 - CH2"],
            "Speed": ["Fast", "Very fast", "Medium", "Slow"],
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

        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):

        self.port_string = parameter['Port']
        self.identifier = "Keithley_4200-SCS_" + self.port_string

        # self.four_wire = parameter['4wire']
        self.route_out = parameter['RouteOut']
        self.current_range = parameter['Range']

        self.source = parameter['SweepMode']

        self.protection = parameter['Compliance']
        self.speed = parameter['Speed']
        # self.pulse = parameter['CheckPulse']
        # self.pulse_meas_time = parameter['PulseMeasTime']

        # self.average = int(parameter['Average'])

        self.channel = parameter["Channel"]

        if "PMU" not in self.channel:
            if "SMU" in self.channel:
                self.card_name = self.channel
            else:
                self.card_name = "SMU" + self.channel[-1]
            self.pulse_channel = None
        else:

            self.card_name = self.channel.split("-")[0].strip()
            self.pulse_channel = int(self.channel.split("-")[1][-1])

        self.shortname = "4200-SCS %s" % parameter["Channel"]

        if "lptlib" in self.port_string.lower():
            self.port_manager = False
        else:
            self.port_manager = True

        self.pulse_master = False
        self.pulse_mode = parameter['CheckPulse']
        if self.pulse_mode:
            # backward compatibility as new fields have been added that are not
            # present in older SMU module versions
            try:
                self.pulse_count = parameter['PulseCount']
                self.pulse_meas_start = parameter['PulseMeasStart']
                self.pulse_meas_duration = parameter['PulseMeasTime']
                self.pulse_width = float(parameter["PulseOnTime"])
                self.pulse_period = float(parameter["PulsePeriod"])
                self.pulse_delay = float(parameter["PulseDelay"])
                # self.pulse_toff = float(parameter["PulseOffTime"])
                self.pulse_base_level = parameter['PulseOffLevel']
                self.pulse_rise_time = parameter['PulseRiseTime']
                self.pulse_fall_time = parameter['PulseFallTime']
                self.pulse_impedance = parameter['PulseImpedance']
            except KeyError:
                debug("Please update the SMU module to support all features of the Keithley 4200-SCS instrument driver")

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

        if "PMU" in self.card_name and not self.pulse_mode:
            raise Exception("Please activate pulse mode for %s of the 4200-SCS parameter analyzer!" % self.channel)

        if self.pulse_mode:
            if "PMU" not in self.card_name:
                raise Exception("Please select a PMU channel to use pulse mode.")
            if self.command_set != "LPTlib":
                raise Exception("Pulse mode only supported with using port communication via LPTlib.")
            if float(self.pulse_width) >= float(self.pulse_period):
                raise ValueError("Pulse width must be smaller than pulse period!")
            if float(self.pulse_delay) < 20e-9:
                raise ValueError("Delay must be 20 ns or larger (not clear why)!")

        if self.identifier not in self.device_communication:
                 
            if self.command_set == "LPTlib":
                if self.pulse_mode:
                    self.lpt.dev_abort()  # stops executed pulses
                self.lpt.tstsel(1)
                self.lpt.devint()  # This command resets all active instruments in the system to their default states.

            elif self.command_set == "US":

                if self.current_range != "Auto":
                    raise Exception("When using KXCI only Auto current range is supported.")

                options = self.get_options()
                # print("Options:", options)

                self.clear_buffer()
                self.set_to_4200()
                self.set_command_mode("US")
                self.set_data_service()
                self.set_resolution(7)

            self.device_communication[self.identifier] = {}  # dictionary that can be filled with further information
            
        '''
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
        '''

    def deinitialize(self):

        if self.identifier in self.device_communication:

            if self.command_set == "LPTlib":
                self.lpt.devint()  # restores default values
                self.lpt.tstdsl()  # not implemented yet
                
            del self.device_communication[self.identifier]
                     
    def configure(self):

        if not self.pulse_mode:

            if self.speed == "Very fast":  # 1 Short (0.1 PLC) preconfigured selection Fast
                nplc = None
                nplc_value = 0.01
                if self.command_set == "US":
                    raise ValueError("Speed of 'Very Fast' is not supported for US command set via GPIB/TCPIP. "
                                     "Use control via 'LPTlib' instead.")
            elif self.speed == "Fast":  # 1 Short (0.1 PLC) preconfigured selection Fast
                nplc = 1
                nplc_value = 0.1
            elif self.speed == "Medium":  # 2 Medium (1.0 PLC) preconfigured selection Normal
                nplc = 2
                nplc_value = 1.0
            elif self.speed == "Slow":  # 3 Long (10 PLC) preconfigured selection Quiet
                nplc_value = 10.0
            else:
                raise ValueError("Speed integration option %s unknown" % self.speed)

            if self.command_set == "LPTlib":

                # can be used to change the limit indicator value
                # self.lpt.setmode(self.card_id, self.param.KI_LIM_INDCTR, float(self.protection))

                # added here as not defined in param yet
                self.param.KI_VALUE = 34.0
                self.param.KI_INDICATOR = 35.0

                # return real measured value when in compliance, not indicator value like 7.0e22
                self.lpt.setmode(self.card_id, self.param.KI_LIM_MODE, self.param.KI_VALUE)

                # Protection
                if self.source == "Voltage in V":
                    self.lpt.limiti(self.card_id, float(self.protection))  # compliance/protection
                elif self.source == "Current in A":
                    self.lpt.limitv(self.card_id, float(self.protection))  # compliance/protection

                # Integration/Speed
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

            elif self.command_set == "US":

                # Integration/Speed
                self.set_integration_time(nplc)

                # Current Range
                if "Limited" in self.current_range:
                    current_range = self.current_ranges[self.current_range]
                    self.set_current_range_limited(self.card_name, current_range)  # low range current

            # range = 1e-1
            # compliance = 1e1
            # self.set_current_range(self.card_name, range, compliance)

        else:  # pulse mode

            if "Pulse master" not in self.device_communication[self.identifier]:
                self.pulse_master = True
                self.device_communication[self.identifier]["Pulse master"] = self.channel
            else:
                if self.device_communication[self.identifier]["Pulse master"] == self.channel:
                    raise Exception("Please use two different channels two combine several pulse units of the "
                                    "4200-SCS parameter analyzer.")
                self.pulse_master = False

            self.configure_pulse()

    def unconfigure(self):

        # Pulse
        if self.pulse_mode and self.pulse_master:
            del self.device_communication[self.identifier]["Pulse master"]

    def poweron(self):
        pass
    
    def poweroff(self):

        if not self.pulse_mode:

            if self.command_set == "LPTlib":
                self.lpt.forcev(self.card_id, 0.0)

            elif self.command_set == "US":
                self.switch_off(self.card_name)

        else:
            self.lpt.pulse_output(
                self.card_id,
                self.pulse_channel,
                out_state=0
            )

    def apply(self):

        self.value = float(self.value)

        if not self.pulse_mode:

            if self.command_set == "LPTlib":
                if self.source == "Voltage in V":
                    self.lpt.forcev(self.card_id, self.value)
                elif self.source == "Current in A":
                    self.lpt.forcei(self.card_id, self.value)

            elif self.command_set == "US":

                voltage_range = 0  # auto
                current_range = 0  # auto

                if self.source == "Voltage in V":
                    self.set_voltage(self.card_name, voltage_range, self.value, self.protection)
                elif self.source == "Current in A":
                    self.set_current(self.card_name, current_range, self.value, self.protection)

    def trigger_ready(self):

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
            self.lpt.pulse_output(
                self.card_id,
                self.pulse_channel,
                out_state=1
            )

    def measure(self):

        if self.pulse_mode and self.pulse_master:

            # TODO: only the master driver instance needs to execute
            self.lpt.pulse_exec(
                pulse_mode=1,  # 0 = basic, 1 = advanced
            )

    def request_result(self):

        if self.pulse_mode and self.pulse_master:

            timeout = 30.0
            while not self.is_run_stopped():
                time.sleep(0.1)
                status, elapsed_time = self.lpt.pulse_exec_status()
                print("Execution status:", status, "Time elapsed:", elapsed_time)

                if status != self.param.PMU_TEST_STATUS_RUNNING:
                    break
                if elapsed_time > timeout:
                    self.lpt.dev_abort()

    def read_result(self):

        if self.pulse_mode:

            buffer_size = self.lpt.pulse_chan_status(
                self.card_id,
                self.pulse_channel,
            )
            print("Buffer size:", buffer_size)

            # fetch results
            status_dict, timestamp, v_meas, i_meas = self.lpt.pulse_fetch(
                self.card_id,
                self.pulse_channel,
                start_index=0,
                stop_index=buffer_size,
                )

            print("Pulse fetch status: ", status_dict)
            print("Timestamp:", timestamp)
            print("Voltages:", v_meas)
            print("Currents:", i_meas)

            self.v = np.average(v_meas)
            self.i = np.average(i_meas)

    def call(self):

        if not self.pulse_mode:
    
            if self.command_set == "LPTlib":
                self.v = self.lpt.intgv(self.card_id)
                self.i = self.lpt.intgi(self.card_id)

                # needed to give some time to update the plot
                # it seems that the LPTlib access is somehow blocking the entire program
                time.sleep(0.001)

            elif self.command_set == "US":
                self.v = self.get_voltage(self.card_name)
                self.i = self.get_current(self.card_name)

            '''
            X Y Z +-N.NNNN E+-NN
            X The status of the data (where X = N for a normal reading)
            Y The measure channel (Y = A through F)
            Z The measure mode (Z = V or I)
            +-N.NNNN E+-NN is the reading (mantissa and exponent)
            '''

        else:
            pass

        return [self.v, self.i]

    """ here, convenience functions start """

    def configure_pulse(self):

        self.lpt.rpm_config(
            self.card_id,
            self.pulse_channel,
            modifier=self.param.KI_RPM_PATHWAY,
            modify_value=self.param.KI_RPM_PULSE,
        )

        self.lpt.pulse_meas_sm(
            self.card_id,
            self.pulse_channel,
            acquire_type=0,
            acquire_meas_V_amp=1,
            acquire_meas_V_base=0,
            acquire_meas_I_amp=1,
            aquire_meas_I_base=0,
            aquire_time_stamp=1,
            load_line_effect_comp=1,
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
            power_limit=10.0
        )

        self.lpt.pulse_meas_timing(
            self.card_id,
            self.pulse_channel,
            start_percent=float(self.pulse_meas_start)/100.0,
            stop_percent=(float(self.pulse_meas_start) + float(self.pulse_meas_duration))/100.0,
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

        # self.lpt.pulse_train(
        # self.card_id,
        # self.pulse_channel,
        # v_base=0.0,
        # v_amplitude=1.0,
        # )

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
