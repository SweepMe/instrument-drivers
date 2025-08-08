# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: Keithley 236

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        super().__init__()

        self.shortname = "Keithley236"

        self.variables =["Voltage", "Current"]
        self.units =    ["V", "A"]
        self.plottype = [True, True] # True to plot data
        self.savetype = [True, True] # True to save data

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            # each self.port.write will have the necessary "X" character appended automatically; also gets rid of the "value out of range" error uppon gpib initialisation
            "GPIB_EOLwrite": "X",
            # delay needed to prevent I/O errors during quick switching between warning status register request and reading measurement result
            "delay": 0.1,
        }

        # operating mode
        self.sources = {
            "Voltage in V": "0",
            "Current in A": "1",
        }

        # sourcing range, defines limit and resolution of output value
        self.sranges = {
            "Auto": "0",
            "1 nA | 1.1 V (1.5 V 238 only)": "1",
            "10 nA | 11 V (15 V 238 only)": "2",
            "100 nA | 110 V": "3",
            "1 uA | (1100 V 237 only)": "4",
            "10 uA": "5",
            "100 uA": "6",
            "1 mA": "7",
            "10 mA": "8",
            "100 mA": "9",
            "1A (238 only)": "10",
        }

        # measuring range, defines readback limit and resolution
        self.mranges = {
            "Auto": "0",
            "1 nA | 1.1 V (1.5 V 238 only)": "1",
            "10 nA | 11 V (15 V 238 only)": "2",
            "100 nA | 110 V": "3",
            "1 uA | (1100 V 237 only)": "4",
            "10 uA": "5",
            "100 uA": "6",
            "1 mA": "7",
            "10 mA": "8",
            "100 mA": "9",
            "1A (238 only)": "10",
        }

        # for current compliance check, translates ASCII description into corresponing current limits
        self.cranges = {
            "1 nA | 1.1 V (1.5 V 238 only)": 1E-09,
            "10 nA | 11 V (15 V 238 only)": 1E-08,
            "100 nA | 110 V": 1E-07,
            "1 uA | (1100 V 237 only)": 1E-06,
            "10 uA": 1E-05,
            "100 uA": 1E-04,
            "1 mA": 1E-03,
            "10 mA": 1E-02,
            "100 mA": 1E-01,
            "1A (238 only)": 1,
        }

        # for voltage compliance check, translates ASCII description into corresponing voltage limits
        self.vranges = {
            "1 nA | 1.1 V (1.5 V 238 only)": 1.1,
            "10 nA | 11 V (15 V 238 only)": 11,
            "100 nA | 110 V": 110,
            "1 uA | (1100 V 237 only)": 1100,
        }

    def set_GUIparameter(self):

        GUIparameter = {
                        "SweepMode" : list(self.sources.keys()),
                        "RouteOut": ["Rear"],
                        "Speed": ["Fast", "Medium", "Slow"],
                        "Average":1,
                        "4wire": False,
                        "Compliance": 100e-6,
                        "Sourcing Range": list(self.sranges.keys()),
                        "Measuring Range": list(self.mranges.keys()),
                        "Range Validity Check": ["Enabled", "Disabled"],
                        "Pulse Timing Check": ["Enabled", "Disabled"],
                        "CheckPulse": False,
                        "PulseOnTime": 0.100,
                        "PulseOffTime": 0.100,
                        "PulseOffLevel": 0.0,
                        # multiple pulses currently not supported
                        #"PulseCount": 1,
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter = {}):

        self.four_wire = parameter["4wire"]
        self.route_out = parameter["RouteOut"]
        self.source = parameter["SweepMode"]
        self.protection = parameter["Compliance"]
        self.speed = parameter["Speed"]
        self.average = int(parameter["Average"])
        self.srange = parameter["Sourcing Range"]
        self.mrange = parameter["Measuring Range"]
        self.rangeverify = parameter["Range Validity Check"]
        self.pulseverify = parameter["Pulse Timing Check"]
        self.checkpulse = parameter["CheckPulse"]

        # multiple pulses currently not supported
        #self.pulsecount = parameter['PulseCount']
        self.pulsecount = "1"
        self.ton = parameter["PulseOnTime"]
        self.toff = parameter["PulseOffTime"]
        self.bias = parameter["PulseOffLevel"]

        if self.average < 1:
            self.average = 1
        if self.average > 100:
            self.average = 100

    def initialize(self):
        # get model id to check for model version 236 (standard), 237 (high voltage) or 238 (high current)
        self.port.write("U0")
        self.model_id=self.port.read()

        if int(round(np.log2(self.average))) not in [0,1,2,3,4,5]:
            msg = "Please use 1, 2, 4, 8, 16, or 32 for the number of averages."
            raise Exception(msg)
        # clearing the warning status register
        self.port.write("J0")

    def configure(self):
        # check for model 237 special high voltage mode selection
        if self.source.startswith("Voltage"):
            if not self.model_id.startswith("237"):
                if self.srange == "1 uA | (1100 V 237 only)" or self.mrange == "1 uA | (1100 V 237 only)":
                    msg = "1100V range only available on Keithley 237."
                    raise Exception(msg)

        # check for model 238 special high voltage mode selection
        if self.source.startswith("Current"):
            if not self.model_id.startswith("238"):
                if self.srange == "1A (238 only)" or self.mrange == "1A (238 only)":
                    msg = "1A range only available on Keithley 238."
                    raise Exception(msg)

        # AUTO ranging not possible in pulse mode
        if self.sranges[self.srange] == "0" and self.checkpulse == True:
            msg = ("AUTO sourcing range not possible in pulse mode, please choose manual range.")
            raise Exception(msg)

        if self.mranges[self.mrange] == "0" and self.checkpulse == True:
            msg = ("AUTO measuring range not possible in pulse mode, please choose manual range.")
            raise Exception(msg)

        # checks if the defined compliance is larger than the measuring range
        # "auto" range does not pose a problem so we exclude error handling from it
        if self.mrange != "Auto":
            if self.source.startswith("Voltage"):
                # if sourcing a voltage, the current compliance is checked
                if float(self.protection) > float(self.cranges[self.mrange]):
                    msg = "Error: compliance limit higher than measuring range."
                    raise Exception(msg)
            else:
                # not every measuring range specifies a voltage, some just define a current only;
                # therefore, in case current is sourced and compliance defines a voltage, we check if the selected
                # m(easurement)range is an entry of the list of v(oltage)ranges?
                if self.mrange in self.vranges:
                    # if source = current is selected, the voltage compliance is checked for being below mrange limit:
                    if float(self.protection) > float(self.vranges[self.mrange]):
                        msg = "Error: compliance limit higher than measuring range."
                        raise Exception(msg)
                else:
                    msg = "Error: selected measuring range defines currents only and cannot be used to observe the entered voltage compliance."
                    raise Exception(msg)

        if self.checkpulse == True:
            # Source mode for pulses
            self.port.write("F%s,1" % self.sources[self.source])
            # Output data format for pulse mode
            self.port.write("G5,2,1")
            # Configure trigger for pulses
            self.port.write("T4,8,0,0")
        else:
            # Source mode for DC
            self.port.write("F%s,0" % self.sources[self.source])
            # Output data format for DC mode
            self.port.write("G5,2,0")
            # Configure trigger for DC mode
            self.port.write("T4,0,0,0")

        # Protection
        self.port.write("L%s,%s" % (self.protection, self.mranges[self.mrange]))

        speed_to_nplc = {"Fast": 0, "Medium": 1, "Slow": 3}
        self.nplc = speed_to_nplc[self.speed]

        #NPLC integration, 0=0.4ms,1=4ms,2=17ms,3=20ms;
        self.port.write("S%s" % self.nplc)

        # 4-wire sense
        if self.four_wire:
            self.port.write("O1")
        else:
            self.port.write("O0")

        # Averaging
        if self.average < 32:
            readings = int(round(np.log2(self.average)))
        else:
            readings = 5

        # enable reading filtering over n samples
        self.port.write("P%s" % readings)

        # Number  Readings
        # 0       1 (disabled)
        # 1       2
        # 2       4
        # 3       8
        # 4       16
        # 5       32

        # enable triggers in case they were disabled
        self.port.write("R1")

    def deinitialize(self):
        # set to local sensing
        self.port.write("O0")

    def poweron(self):
        # set unit in operate mode
        self.port.write("N1")

    def poweroff(self):
        # set unit in standby mode
        self.port.write("N0")

    def apply(self):

        if self.checkpulse == False:
            # in case of Sweep Type "DC", the "B" command applies "self.value" as the DC level output and sets the measuring range
            self.port.write("B%s,%s,0" % (self.value, self.sranges[self.srange]))
        else:
            # in case of Sweep Type "Pulse", the "B" command applies "self.bias" as the bias level for the pulses instead, together with the measuring range
            # note: the bias command and the pulse command must use the same sourcing range as otherwise a range switch might occur in between, leading to the instrument not being able to meet the requested pulse times
            self.port.write("B%s,%s,0" % (self.bias, self.sranges[self.srange]))
            # pulses command "Q3,(level),(range),(pulses),(toN),(toFF)"
            # the gui requests all times to be entered in seconds but the instrument expects the time values in full figure milliseconds
            self.port.write("Q3,%s,%s,%s,%s,%s" % (self.value, self.sranges[self.srange], self.pulsecount, int(float(self.ton)*1000), int(float(self.toff)*1000)))

    def measure(self):
        # initiate immediate trigger
        self.port.write("H0")

    def call(self):

        if self.source.startswith("Voltage"):
            v,i = self.port.read().split(",")

        if self.source.startswith("Current"):
            i,v = self.port.read().split(",")

        # U9 requests output of warning status register; register is retrieved after measurement result to clear instruments output buffer first
        self.port.write("U9")
        self.warnings = self.port.read()

        # self.warnings = ASCII string "WRSxx1xxxxxxx" were 1 means "Value Out of Range" error positive
        # Explaination: the V.O.o.T. error will be output when compliance limit is above the measurement range AND/OR the sweep value is above the sourcing range.
        # To be able to differentiate between both cases, we check for compliance limit validity once during setup by value comparison and for sourcing range validity after each sweep by checking for respective errors.
        if self.rangeverify == "Enabled":
            if self.warnings[5] == "1":
                msg = 'Instrument reported "Value Out of Range" warning as it was unable to apply the requested voltage or current within the selected sourcing range.'
                raise Exception(msg)

        # if the instrument was set to output pulses, we check the warning register afterward regarding timing issues
        if self.checkpulse == True and self.pulseverify == "Enabled":
            # self.warnings = ASCII string "WRSxxxxx1xxxx" were 1 means "Pulse Times Not Met" error positive
            if self.warnings[8] == "1":
                msg = 'Instrument reported "Pulse Times Not Met" warning as it was unable to apply the requested voltage or current over the specified time.'
                raise Exception(msg)

        return [float(v), float(i)]

    def finish(self):
        pass
