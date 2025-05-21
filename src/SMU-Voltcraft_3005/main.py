# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2025 Tjorben Matthes (TU Munich)
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
# * Instrument: Voltcraft DSP 3005


from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import error


class Device(EmptyDevice):

    def __init__(self):

        super().__init__()

        self.shortname = "Voltcraft3005"
        
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 0.5,
            "EOL": "\r\n",
            "baudrate": 115200,
        }

        self.commands = {
            "Voltage [V]": "VSET",  # remains for compatibility reasons
            "Current [A]": "ISET",  # remains for compatibility reasons
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
        }

        # self.outpon = False

    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode": ["Voltage in V", "Current in A"],
                        "RouteOut": ["Front"],
                        "Compliance": 0.3,
                        }
                        
        return gui_parameter
                                 
    def get_GUIparameter(self, parameter={}):
        self.source = parameter['SweepMode']
        self.protection = float(parameter['Compliance'])

    def initialize(self):
        pass

    def configure(self):
        if self.source.startswith("Voltage"):
            self.port.write(f'CURR {self.protection:1.2f}')
        elif self.source.startswith("Current"):
            self.port.write(f'VOLT {self.protection:1.2f}')

    def poweron(self):
        self.port.write('OUTP ON')
        
    def poweroff(self):
        self.port.write('OUTP OFF')

    def apply(self):
        self.port.write(self.commands[self.source] + f' {float(self.value):1.2f}')

    def measure(self):
        self.port.write('MEAS:ALL?')

    def read_result(self):
        self.v, self.i = self.port.read().split(',')
        self.v, self.i = float(self.v), float(self.i)

    def call(self):
        return [self.v, self.i]

    def get_identification(self):
        self.port.write("*IDN?")
        self.port.read()


