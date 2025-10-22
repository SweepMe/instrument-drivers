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
# * Instrument: Agilent B1500

from __future__ import annotations
from collections import OrderedDict

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    multichannel = [" CH1", " CH2", " CH3", " CH4", " CH5", " CH6"]

    def __init__(self):

        EmptyDevice.__init__(self)

        # remains here for compatibility with v1.5.3        
        self.multichannel = [" CH1", " CH2", " CH3", " CH4", " CH5", " CH6"]

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ['GPIB', 'USB']
        self.port_properties = {
            "timeout": 5,
            # "delay": 0.1,
        }

        self.port_identifications = ['Agilent Technologies,B1500A']

        self.current_ranges = OrderedDict([
            ("Auto", "0"),
            ("1 pA limited auto", "8"),
            ("10 pA limited auto", "9"),
            ("100 pA limited auto", "10"),
            ("1 nA limited auto", "11"),
            ("10 nA limited auto", "12"),
            ("100 nA limited auto", "13"),
            ("1 μA limited auto", "14"),
            ("10 μA limited auto", "15"),
            ("100 μA limited auto", "16"),
            ("1 mA limited auto", "17"),
            ("10 mA limited auto", "18"),
            ("100 mA limited auto", "19"),
            ("1 A limited auto", "20"),
        ])

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage [V]", "Current [A]"],
            "RouteOut": ["Rear"],
            "Speed": ["Fast", "Medium", "Slow"],
            "Range": list(self.current_ranges.keys()),
            "Compliance": 100e-6,
            "Average": 1,
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.device = parameter['Device']
        self.four_wire = parameter['4wire']
        self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        self.port_string = parameter['Port']

        self.irange = self.current_ranges[parameter['Range']]

        self.protection = parameter['Compliance']
        self.speed = parameter['Speed']
        self.pulse = parameter['CheckPulse']
        self.pulse_meas_time = parameter['PulseMeasTime']

        self.average = int(parameter['Average'])

        self.channel = self.device[-1]

        self.shortname = "B1500 CH%s" % self.channel

        # voltage autoranging 
        self.vrange = "0"

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        unique_DC_port_string = "Agilent_B1500_" + self.port_string

        # initialize commands only need to be sent once, so we check here whether another instance of the same Device Class AND same port did it already. If not, this instance is the first and has to do it.
        if not unique_DC_port_string in self.device_communication:
            # self.port.write("*IDN?") # identification
            # print(self.port.read())

            self.port.write("*RST")  # reset to initial settings

            self.port.write("BC")  # buffer clear

            self.port.write("AZ 0")  # Auto-Zero off for faster measurements

            self.port.write("FMT 2")  # use to change the output format

            # if initialize commands have been sent, we can add the the unique_DC_port_string to the dictionary that is seen by all Device Classes
            self.device_communication[unique_DC_port_string] = True

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        ### The command CN has to be sent at the beginning as it resets certain parameters
        ### If the command CN would be used later, e.g. durin  'poweron', it would overwrite parameters that are defined during 'configure'
        self.port.write("CN " + self.channel)  # switches the channel on

        if self.speed == "Fast":  # 1 Short (0.1 PLC) preconfigured selection Fast
            self.port.write("AIT 0,0,1")
            self.port.write("AAD %s,0" % self.channel)
        elif self.speed == "Medium":  # 2 Medium (1.0 PLC) preconfigured selection Normal
            self.port.write("AIT 1,0,1")
            self.port.write("AAD %s,1" % self.channel)
        elif self.speed == "Slow":  # 3 Long (10 PLC) preconfigured selection Quiet
            self.port.write("AIT 1,2,10")
            self.port.write("AAD %s,1" % self.channel)

        if self.source == "Voltage [V]":
            self.port.write(
                "DV " + self.channel + "," + self.vrange + "," + "0.0" + "," + self.protection + ", 0" + "," + self.irange)

        if self.source == "Current [A]":
            self.port.write(
                "DI " + self.channel + "," + self.irange + "," + "0.0" + "," + self.protection + ", 0" + "," + self.vrange)

        # RI and RV #comments to adjust the range, autorange is default

        self.port.write("AV %i" % self.average)

        # *LRN? is a function to ask for current status of certain parameters,
        # 0 = output on or off
        # self.port.write("*LRN? 0")
        # print(self.port.read())

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        self.port.write("IN" + self.channel)
        # resets to zero volt
        # self.port.write("DZ")

        """
        Enables channels CN [chnum ... [,chnum] ... ]
        Disables channels CL [chnum ... [,chnum] ... ]
        Sets filter ON/OFF [FL] mode[,chnum ... [,chnum] ... ]
        Sets series resistor ON/OFF [SSR] chnum,mode
        Sets integration time
        (Agilent B1500 can use
        AAD/AIT instead of AV.)
        [AV] number[,mode]
        [AAD] chnum[,type]
        [AIT] type,mode[,N]
        Forces constant voltage DV chnum,range,output
        [,comp[,polarity[,crange]]]
        Forces constant current DI
        Sets voltage measurement
        range
        [RV] chnum,range
        Sets current measurement
        range
        [RI] chnum,range
        [RM] chnum,mode[,rate]
        Sets measurement mode MM 1,chnum[,chnum ... [,chnum] ... ]
        Sets SMU operation mode [CMM] chnum,mode
        Executes measurement XE
        """

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        pass
        # In a previous version, the CN command was sent here. However, this leads to a reset of all parameters previously changed during 'configure' 
        # Therefore, the CN command should not be used here, but has been moved to the beginning of 'configure'

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        self.port.write("CL " + self.channel)  # switches the channel off

    def apply(self) -> None:
        """This function is called if the set value has changed. Applies the new value available as self.value."""
        self.value = str(self.value)

        if self.source == "Voltage [V]":
            self.port.write("DV " + self.channel + "," + self.vrange + "," + self.value)
            # self.port.write("DV " + self.channel + "," + self.vrange + "," + self.value + "," + self.protection + ", 0" + "," + self.irange)

        if self.source == "Current [A]":
            self.port.write("DI " + self.channel + "," + self.irange + "," + self.value)
            # self.port.write("DI " + self.channel + "," + self.irange + "," + self.value + "," + self.protection + ", 0" + "," + self.vrange)

    # def trigger(self):
    # pass
    # software trigger to start the measurement
    # self.port.write("XE")

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        self.port.write("TI" + self.channel + ",0")
        self.port.write("TV" + self.channel + ",0")

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        answer = self.port.read()
        # print("Current:", answer)

        # If NAI comes first, we have to strip it. Please toggle the lines, if needed.
        i = float(answer)
        # i = float(answer[3:])

        answer = self.port.read()
        # print("Voltage:", answer)

        # If NAV comes first, we have to strip it. Please toggle the lines, if needed.
        v = float(answer)
        # v = float(answer[3:])

        return [v, i]
