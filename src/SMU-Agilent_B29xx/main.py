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
# Type: SMU
# Device: Agilent 29xx

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        super().__init__()

        self.shortname = "Agilent B29xx"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["USB", "GPIB"]

        self.port_properties = {
            # "timeout": 10,
        }

        self.commands = {
            "Voltage [V]": "VOLT",  # deprecated, remains for compatibility
            "Current [A]": "CURR",  # deprecated, remains for compatibility
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
        }

    def set_GUIparameter(self):

        GUIparameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["CH1", "CH2"],
            "4wire": False,
            # "RouteOut": ["Front", "Rear"],
            "Speed": ["Fast", "Medium", "Slow"],
            "Compliance": 100e-6,
            # "Average": 1, # not yet supported
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        self.four_wire = parameter['4wire']
        # self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']

        self.speed = parameter['Speed']

        # not yet supported
        # self.average = int(parameter['Average'])
        #
        # if self.average < 1:
        #     self.average = 1
        # if self.average > 100:
        #     self.average = 100

        self.device = parameter['Device']
        self.channel = str(parameter['Channel'])[-1]

    def initialize(self):
        # once at the beginning of the measurement
        self.port.write("*RST")

        self.port.write("SYST:BEEP:STAT OFF")  # control-Beep off

        self.port.write(":SYST:LFR 50")  # LineFrequency = 50 Hz

        self.port.write(":OUTP%s:PROT ON" % self.channel)  # enables  over voltage / over current protection

    def configure(self):

        if self.source.startswith("Voltage"):
            self.port.write(":SOUR%s:FUNC:MODE VOLT" % self.channel)
            # sourcemode = Voltage
            self.port.write(":SOUR%s:VOLT:MODE FIX" % self.channel)
            # sourcemode fix
            self.port.write(":SENS%s:FUNC:MODE CURR" % self.channel)
            # measurement mode
            self.port.write(":SENS%s:CURR:PROT %s" % (self.channel, self.protection))
            # Protection with Imax
            self.port.write(":SENS%s:CURR:RANG:AUTO ON" % self.channel)
            # Autorange for current measurement


        elif self.source.startswith("Current"):
            self.port.write(":SOUR%s:FUNC:MODE CURR" % self.channel)
            # sourcemode = Voltage
            self.port.write(":SOUR%s:CURR:MODE FIX" % self.channel)
            # sourcemode fix
            self.port.write(":SENS%s:FUNC:MODE VOLT" % self.channel)
            # measurement mode
            self.port.write(":SENS%s:VOLT:PROT %s" % (self.channel, self.protection))
            # Protection with Imax
            self.port.write(":SENS%s:VOLT:RANG:AUTO ON" % self.channel)
            # Autorange for voltage measurement

        if self.speed == "Fast":
            self.nplc = "0.1"
        elif self.speed == "Medium":
            self.nplc = "1.0"
        elif self.speed == "Slow":
            self.nplc = "10.0"

        self.port.write(":SENS%s:CURR:NPLC %s" % (self.channel, self.nplc))
        self.port.write(":SENS%s:VOLT:NPLC %s" % (self.channel, self.nplc))

        self.port.write(":SENS%s:CURR:RANG:AUTO:MODE RES" % self.channel)

        # 4-wire sense
        if self.four_wire:
            self.port.write("SENS:REM ON")
        else:
            self.port.write("SENS:REM OFF")

        # Averaging is not yet supported but the below code might help to implement
        """
        # averaging
        self.port.write(":SENS:AVER:TCON REP")   # repeatedly take average
        if self.average > 1:
            self.port.write(":SENS:AVER ON") 
            self.port.write(":SENSe:AVER:COUN %i" % self.average)   # repeatedly take average
        else:
            self.port.write(":SENS:AVER OFF")
            self.port.write(":SENSe:AVER:COUN 1")  
        """

        # These lines remain here in case somebody needs them in future, e.g. to test something

        # self.port.write(":OUTP:LOW GRO") # LowGround
        # self.port.write(":OUTP:HCAP ON") # High capacity On

    def deinitialize(self):
        if self.four_wire:
            self.port.write("SYST:REM OFF")

        self.port.write(":SENS%s:CURR:NPLC 1" % self.channel)
        self.port.write(":SENS%s:VOLT:NPLC 1" % self.channel)

        # self.port.write(":SENS:AVER OFF")
        # self.port.write(":SENSe:AVER:COUN 1")

    def poweron(self):
        self.port.write(":OUTP%s ON" % self.channel)

    def poweroff(self):
        self.port.write(":OUTP%s OFF" % self.channel)

    def apply(self):

        self.port.write(":SOUR%s:%s %s" % (self.channel, self.commands[self.source], self.value))  # set source

    def call(self):
        self.port.write(":MEAS? (@%s)" % self.channel)

        answer = self.port.read()

        values = answer.split(",")

        voltage = float(values[0])
        current = float(values[1])

        return [voltage, current]
