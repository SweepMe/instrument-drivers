# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 Gennaro Tortone (Istituto Nazionale di Fisica Nucleare - Sezione di Napoli - tortone@na.infn.it)
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
# Type: Logger
# Device: Fluke 8842A

import time
from EmptyDeviceClass import EmptyDevice
from Ports import GPIBport
from ErrorMessage import debug


class Device(EmptyDevice):

    description =   """
                        Fluke 8842A
                        Digital multimeter
                    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Fluke8842A"

        self.measurement_modes = {
            "DC voltage":  {
                "command": "F1",
                "variable": "DC voltage",
                "unit": "V",
            },
            "AC voltage":  {
                "command": "F2",
                "variable": "AC voltage",
                "unit": "V",
            },
            "2-wire resistance":    {
                "command": "F3",
                "variable": "Resistance",
                "unit": "Ohm",
            },
            "4-wire resistance":     {
                "command": "F4",
                "variable": "Resistance",
                "unit": "Ohm",
            },
            "DC current":   {
                "command": "F5",
                "variable": "DC current",
                "unit": "A",
            },
            "AC current":   {
                "command": "F6",
                "variable": "AC current",
                "unit": "A",
            }
        }

        self.measurement_ranges = {
            "Autorange ON": {
                "command": "R0",
            },
            "200 mV, 200 Ohm": {
                "command": "R1",
            },
            "2 V, 2 kOhm": {
                "command": "R2",
            },
            "20 V, 20 kOhm": {
                "command": "R3",
            },
            "200 V, 200 kOhm, 200 mA": {
                "command": "R4",
            },
            "1000 V DC, 700 V AC, 2 MOhm, 2000 mA": {
                "command": "R5",
            },
            "20 MOhm": {
                "command": "R6",
            },
            "20 mV, 20 Ohm": {
                "command": "R8",
            },
        }

        self.sampling_rates = {
            "Fast": {
                "command": "S2",
            },
            "Medium": {
                "command": "S1",
            },
            "Slow": {
                "command": "S0",
            }
        }

        self.trigger_modes = {
            "Auto":{
                "command": "T0",
            },
            "External with settling delay": {
                "command": "T1",
            },
            "External without settling delay": {
                "command": "T3",
            }
        }

        # Time until external trigger must happen
        self.triggertimeout = 30

        self.port_manager = True
        self.port_types = ['GPIB']
        self.port_properties = {
            "timeout": 5,
        }
        
    def set_GUIparameter(self):

        GUIparameter = {
            "Mode": list(self.measurement_modes.keys()),
            "Rate": list(self.sampling_rates.keys()),
            "Range": list(self.measurement_ranges.keys()),
            "Trigger": list(self.trigger_modes.keys()),
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):

        self.device = parameter['Device']
        self.mode = parameter["Mode"]
        self.rate = parameter["Rate"]
        self.range = parameter["Range"]
        self.triggermode = parameter["Trigger"]

        self.variables = [self.measurement_modes[self.mode]["variable"], 'overrange']
        self.units = [self.measurement_modes[self.mode]["unit"], 'bool']
        self.plottype = [True, False]
        self.savetype = [True, True]

    # monkey patching close_internal method due to instrument reset on clear()
    def connect(self):
        def custom_close_internal(obj):
            obj.port.close()
        GPIBport.close_internal = custom_close_internal

    def initialize(self):

        self.port.write("*")        # reset to initial settings
        self.port.write("X0")       # clear error register
        self.port.write("Y1")       # enable suffix
        self.port.write("N17 P1")   # enable SRQ for overrange (stb[0]) and data available (stb[5])

    def configure(self):

        # Measurement mode
        self.port.write(self.measurement_modes[self.mode]["command"])

        # Range
        self.port.write(self.measurement_ranges[self.range]["command"])

        # Sampling rate
        self.port.write(self.sampling_rates[self.rate]["command"])

        # Trigger mode
        self.port.write(self.trigger_modes[self.triggermode]["command"])

    def measure(self):
        self.port.write("")

    def read_result(self):
        dataavail = True
        stb = self.port.port.read_stb()
        if self.triggermode != "Auto":
            telapsed = 0
            dataavail = False
            while telapsed < self.triggertimeout:
                stb = self.port.port.read_stb()
                if stb & (1 << 5):
                    dataavail = True
                    break
                time.sleep(0.5)
                telapsed += 0.5

        if dataavail:
            answer = self.port.read()
            value, label = answer.split(',')
            self.val = float(value)
            self.overrange = stb & 1
        else:
            raise Exception("Trigger timeout")

    def call(self):
        return [self.val, self.overrange]
