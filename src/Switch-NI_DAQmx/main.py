# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025-2026 SweepMe! GmbH (sweep-me.net)
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


# SweepMe! instrument driver
# * Module: Switch
# * Instrument: NI DAQmx


import nidaqmx
from nidaqmx.system import System

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    def __init__(self):
        super().__init__()

        self.variables = ["Voltage"]
        self.units = ["V"]
        self.plottype = [True]
        self.savetype = [True]

        # defining variables
        self.task_ao = None
        self.voltage = 0.0

    def find_ports(self):

        system = System.local()

        # Get all connected devices
        try:
            devices = system.devices
        except nidaqmx.errors.DaqNotFoundError:
            # TODO: add message box to inform user
            raise

        found = []
        for dev in devices:
            found.append(f"{dev.name} ({dev.product_type}, SN:{dev.serial_number})")
        return found

    def set_GUIparameter(self):
        return {
            "SweepMode": ["Voltage in V"],
            "AO Channel": "ao0",
            "Minimum voltage": -10.0,
            "Maximum voltage": 10.0,
        }

    def get_GUIparameter(self, parameter):
        self.port_string = parameter["Port"]
        self.ao_channel = parameter["AO Channel"]
        self.voltage_min = parameter["Minimum voltage"]
        self.voltage_max = parameter["Maximum voltage"]

    def connect(self):

        system = System.local()

        # Get all connected devices
        try:
            devices = system.devices
        except nidaqmx.errors.DaqNotFoundError:
            raise

        self.device_name = None
        for dev in devices:
            identifier = f"({dev.product_type}, SN:{dev.serial_number})"
            if identifier in self.port_string:
                self.device_name = dev.name
                break

        if not self.device_name:
            raise ValueError(f"Device with port {self.port_string} not found.")

    def configure(self):
        if self.task_ao:
            self.task_ao.close()

        self.task_ao = nidaqmx.Task()
        self.task_ao.ao_channels.add_ao_voltage_chan(
            f"{self.device_name}/{self.ao_channel}",
            min_val=self.voltage_min,
            max_val=self.voltage_max,
        )

    def unconfigure(self):
        # changing voltage back to zero
        # could be done based on a GUI parameter
        self.task_ao.write(0.0)

        if self.task_ao:
            self.task_ao.close()
            self.task_ao = None

    def apply(self):
        self.voltage = float(self.value)
        self.task_ao.write(self.voltage)

    def call(self):
        return [self.voltage]