# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 Gennaro Tortone (gtortone@gmail.com)
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
# Device: Agilent N6705A

import numpy as np
from collections import OrderedDict
from EmptyDeviceClass import EmptyDevice
from ErrorMessage import debug


class Device(EmptyDevice):

    description = """
                        Agilent N6705A
                        DC power analyzer
                        
                        Agilent N7605A can be equipped with different modules/options that enable different features.
                        
                        - N678x modules:
                            - voltage compliance is monitored sensing 4-wire terminals
                            
                        - Opt 1A option:
                            - 100 uA measurement range
                            
                        - Opt 2A option:
                            - 200 uA measurement range
                    """

    multichannel = ["CH1", "CH2", "CH3", "CH4"]

    def __init__(self):

        super().__init__()

        self.shortname = "Agilent N6705A"

        # remains here for compatibility with v1.5.3
        self.multichannel = ["CH1", "CH2", "CH3", "CH4"]

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["TCPIP", "GPIB"]

        self.channel_model = None

        self.commands = {
            "Voltage [V]": "VOLT",
            "Current [A]": "CURR",
        }

        self.voltage_ranges = OrderedDict([
            ("Auto", "MAX"),
            ("51V", "51"),
            ("5.5V", "5.5")
        ])

        self.current_ranges = OrderedDict([
            ("Auto", "MAX"),
            ("3.06A", "3.06"),
            ("100 mA", "0.1"),
            ("200 uA", "0.0002"),
            ("100 uA", "0.0001")
        ])

    def set_GUIparameter(self):
        GUIparameter = {
            "SweepMode": ["Voltage [V]", "Current [A]"],
            "Range": list(self.current_ranges.keys()),
            "RangeVoltage": list(self.voltage_ranges.keys()),
            "Compliance": 100e-6,
            "Average": 1
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']
        self.vrange = self.voltage_ranges[parameter["RangeVoltage"]]
        self.irange = self.current_ranges[parameter["Range"]]
        self.average = parameter["Average"]

        self.device = parameter['Device']
        self.channel = self.device[-1]

    def initialize(self):
        self.port.port.read_termination = '\n'
        self.port.port.write_termination = '\n'
        # once at the beginning of the measurement
        self.port.write("*RST")

    def configure(self):

        self.port.write(f"SYST:CHAN:MODEL? (@{self.channel})")
        self.channel_model = self.port.read()

        if self.source == "Voltage [V]":
            # sourcemode fix
            self.port.write(f"VOLT:MODE FIX, (@{self.channel})")
            # compliance
            if self.channel_model.startswith('N678'):
                self.port.write(
                    f"CURR:LIMIT {self.protection}, (@{self.channel})")
            else:
                self.port.write(f"CURR {self.protection}, (@{self.channel})")

        if self.source == "Current [A]":
            # sourcemode fix
            self.port.write(f"CURR:MODE FIX, (@{self.channel})")
            # compliance
            if self.channel_model.startswith('N678'):
                self.port.write(
                    f"VOLT:PROT:REMOTE {self.protection}, (@{self.channel})")
            else:
                self.port.write(
                    f"VOLT:PROT {self.protection}, (@{self.channel})")

        self.port.write(f"SENSE:VOLT:RANGE {self.vrange}, (@{self.channel})")
        self.port.write(f"SENSE:CURR:RANGE {self.irange}, (@{self.channel})")

        self.port.write(
            f"SENSE:SWEEP:POINTS {self.average}, (@{self.channel})")

    def deinitialize(self):
        pass

    def poweron(self):
        self.port.write(f"OUTP ON, (@{self.channel})")

    def poweroff(self):
        self.port.write(f"OUTP OFF, (@{self.channel})")

    def apply(self):
        self.port.write(
            f"{self.commands[self.source]} {self.value}, (@{self.channel})")

    def measure(self):
        pass

    def call(self):
        self.port.write(f"MEAS:ARR:VOLT? (@{self.channel})")
        str = self.port.read()
        voltage_array = np.array([float(v) for v in str.split(',')])
        voltage = np.average(voltage_array)

        # modules N6761A and N6762A have simultaneous V/I measurement
        if self.channel_model.startswith('N676'):
            self.port.write(f"FETCH:CURR? (@{self.channel})")
        else:
            self.port.write(f"MEAS:ARR:CURR? (@{self.channel})")

        str = self.port.read()
        current_array = np.array([float(v) for v in str.split(',')])
        current = np.average(current_array)

        return [voltage, current]

    def finish(self):
        pass
