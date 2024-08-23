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

# SweepMe! driver
# * Module: SMU
# * Instrument: Agilent/Keysight E3631A

import time

# from pysweepme.ErrorMessage import error
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """
    description =
    <p><strong>Notes:</strong></p>
    <ul>
    <li>COM Port untested as of 20240807</li>
    <li>Calibration commands not implemented</li>
    <li>-</li>
    </ul>
    """

    def __init__(self):

        super().__init__()

        self.shortname = "E3631A"
        
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM", "GPIB"]

        self.port_properties = {
            "timeout": 3,
        }

        self.channels_commands = {
            "+6V": "P6V",
            "+25V": "P25V",
            "-25V": "N25V",
            "Synced +/-25V": "TRACK25V",  # only a positive voltage is handed over
        }

    def set_GUIparameter(self):

        gui_parameter = {
            "SweepMode": ["Voltage in V"],
            "Channel": list(self.channels_commands.keys()),
            "RouteOut": ["Front"],
            "Compliance": 1,
            # "RangeVoltage": ["15 V / 7 A", "30 V / 4 A"],  # no voltage range per channel on the E3631A
        }

        return gui_parameter

    def get_GUIparameter(self, parameter={}):
        self.port_string = parameter["Port"]
        self.source = parameter["SweepMode"]
        #self.route_out = parameter["RouteOut"]
        self.currentlimit = parameter["Compliance"]
        
        self.device = parameter['Device']

        channel_selection = parameter['Channel']
        self.channel = self.channels_commands[channel_selection]

    def initialize(self):
        # self.port.write("*IDN?")
        # identifier = self.port.read()
        # print("Identifier:", identifier)  # can be used to check the instrument

        self.port.write("*CLS")

    def configure(self):

        # NOT AVAILABLE ON E3631A: self.port.write("VOLT:PROT:STAT OFF") # output voltage protection disabled
        # NOT AVAILABLE ON E3631A: self.port.write("CURR:PROT:STAT OFF") # output current protection disabled

        # NOT AVAILABLE ON E3631A:
        # hardcoded overvoltage protection limit, causes switch-off of channel; set to PSU protection default value
        # self.port.write("VOLT:PROT:LEV 32")

        # NOT AVAILABLE ON E3631A:
        # hardcoded overcurrent protection limit, causes switch-off of channel; set to PSU protection default value
        # self.port.write("CURR:PROT:LEV 7.5")

        # checking if requested compliance is within PSU capabilities and
        # enabling TRACK mode if channel option was selected in GUI"
        if self.channel == "P6V":
            if float(self.currentlimit) > 5:
                msg = "Lower compliance limit to max 5 A"
                raise Exception(msg)
        
        elif self.channel == "P25V" or self.channel == "N25V" or self.channel == "TRACK25V":
            if float(self.currentlimit) > 1:
                msg = "Lower compliance limit to max 1 A"
                raise Exception(msg)
            if self.channel == "TRACK25V":
                self.port.write("OUTPUT:TRAC:STAT ON")  # activate sync of both 25V channels
            else:
                self.port.write("OUTPUT:TRAC:STAT OFF")  # make sure, sync of +25V and -25V channel is disabled
        else:
            msg = "The input channel selection is not valid."
            raise Exception(msg)
        
        self.select_channel()
        # set compliance limit for selected channel.
        self.port.write("CURR:LEV:IMM %1.4f" % float(self.currentlimit))
        
    def unconfigure(self):
        self.select_channel()

        # Safety measure, setting voltage back to minimum before output switch-off. hint: this command differs
        # slightly from the one used in the E3632A driver
        self.port.write("VOLT:LEV MIN")

        # if self.port_string.startswith("COM"):
        #     self.port.write("SYST:LOC")  # On the E3631A, ONLY ALLOWED WITH RS232

    def deinitialize(self):
        pass

    def poweron(self):
        self.port.write("OUTP:STAT ON")

    def poweroff(self):
        self.port.write("OUTP:STAT OFF")

    def apply(self):
        if self.channel == "P6V" and self.value > 6:
            msg = "Requested voltage out of range for this channel (max. 6 V)"
            raise Exception(msg)
        
        if self.channel == "P25V" or self.channel == "TRACK25V":
            if abs(self.value) > 25:
                msg = "Requested voltage out of range for this channel (max. +25 V)"
                raise Exception(msg)
            elif self.channel == "TRACK25V" and self.value < 0:
                msg = "Use positive values only in TRACK mode to request symmetric voltage on both channels."
                raise Exception(msg)
        
        if self.channel == "N25V":
            if abs(self.value) > 25:
                msg = "Requested voltage out of range for this channel (max. -25 V)"
                raise Exception(msg)
            elif self.value > 0:
                msg = "Positive voltages not possible on this channel (N25V)."
                raise Exception(msg)
        
        self.select_channel()
        self.port.write("VOLT:LEV:IMM %1.4f" % float(self.value))

    def measure(self):
        self.select_channel()
        self.port.write("MEAS:VOLT?")
        self.v = float(self.port.read())
        self.port.write("MEAS:CURR?")
        self.i = float(self.port.read())

    def call(self):
        return [self.v, self.i]

    def display_off(self):

        self.port.write("DISP:STAT OFF")
        # wait for display shutdown procedure to complete
        # time.sleep(0.5)

    def display_on(self):

        self.port.write("DISP:STAT ON")
        # wait for display switch-on procedure to complete
        # time.sleep(0.5)
        
    def select_channel(self):
        """Selects the current channel as the receipt for following SCPI configuration commands.
        """

        if self.channel == "TRACK25V":
            # when in TRACK mode (synced +/-25V channels), voltage on both channels can be set by
            # setting P25V channel or N25V channel arbitrarily.
            # Here, P25V is used to positive values can be used
            # as the negative channel only accepts negative voltage values.
            self.port.write("INST:SEL P25V")
        else:
            # select channel to configure
            self.port.write("INST:SEL %s" % self.channel)
