# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022, 2025 SweepMe! GmbH (sweep-me.net
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

# Contribution: We like to thank GRIP Molecular Technologies, Inc/John Myers-Bangsund, Ph.D.
# for providing the initial version of this driver.


# SweepMe! driver
# * Module: Logger
# * Instrument: Keithley 2700


import time

import numpy as np
import pyvisa
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
                  Usage:
                  Scanning: The driver will scan through all channels of the given channel list. Otherwise the driver just returns a reading

                  Info:

                  """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Keithley 2700"
        self.port_manager = True
        self.port_types = ["COM", "GPIB", "TCPIP"]  # Keithley 2701 has Ethernet connection
        self.port_properties = {
            "timeout": 10,
            "EOL": "\r",
            "baudrate": 9600,  # factory default
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Voltage DC":   "VOLT:DC",           # CONFigure:VOLTage[:DC] [<rang>], [<res>], [<clist>] Configure DCV
            "Voltage AC":   "VOLT:AC",           # CONFigure:VOLTage:AC [<rang>], [<res>], [<clist>] Configure ACV
            "Current DC":   "CURR:DC",           # CONFigure:CURRent[:DC] [<rang>], [<res>], [<clist>] Configure DCI
            "Current AC":   "CURR:AC",           # CONFigure:CURRent:AC [<rang>], [<res>], [<clist>] Configure ACI
            "Resistance":   "RES",               # CONFigure:RESistance [<rang>], [<res>], [<clist>] Configure Ω2
            "FResistance":  "FRES",              # CONFigure:FRESistance [<rang>], [<res>], [<clist>] Configure Ω4
            "Frequency":    "FREQ",              # CONFigure:FREQuency [<rang>], [<res>], [<clist>] Configure FREQ
            "Period":       "PER",               # CONFigure:PERiod [<rang>], [<res>], [<clist>] Configure PERIOD
            "Temperature":  "TEMP",              # CONFigure:TEMPerature [<clist>] Configure TEMP
            "Continuity":   "CONT",              # CONFigure:CONTinuity [<clist>] Configure CONT
        }

        # this dictionary sets the variable names of each mode
        self.mode_variables = {
            "Voltage DC":   "DC Voltage",
            "Voltage AC":   "AC Voltage",
            "Current DC":   "DC Current",
            "Current AC":   "AC Current",
            "Resistance":   "Resistance",
            "FResistance":  "FResistance",
            "Frequency":    "Frequency",
            "Period":       "Period",
            "Temperature":  "K",
            "Continuity":   "",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC":   "V",
            "Voltage AC":   "V",
            "Current DC":   "A",
            "Current AC":   "A",
            "Resistance":   "Ohm",
            "FResistance":  "Ohm",
            "Frequency":    "Hz",
            "Period":       "s",
            "Temperature":  "K",
            "Continuity":   "",
        }

        # a list of available resolutions as they can be sent to the instrument
        self.resolutions = [
            "0.1",       # i.e., 100.0 V (3½ digits)
            "0.01",      # i.e., 10.00 V (3½ digits)
            "0.001",     # i.e., 1.000 V (3½ digits)
            "0.0001",    # i.e., 1.0000 V (4½ digits)
            "0.00001",   # i.e., 1.00000 V (5½ digits)
            "0.000001",  # i.e., 1.000000 V (6½ digits)
        ]

        # a dictionary of trigger types and their corresponding commands.
        # The trigger types will be shown in the GUI field 'Trigger'
        self.trigger_types = {
            "Immediate": "IMM",
            "Timer":     "TIM",
            "Manual":    "MAN",
            "Internal":  "BUS",
            "External":  "EXT",
        }

        self.variables=["Variable1"]
        self.units=["Unit1"]
        self.plottype=[True]
        self.savetype=[True]
        self.had_trigger = False


    def set_GUIparameter(self):
        return {
                        "Mode" : list(self.modes.keys()),
                        "Digits": ["4", "5", "6", "7"],  #self.resolutions,
                        "Trigger": list(self.trigger_types.keys()),
                        "Integration speed": ["Fast", "Medium", "Slow"],
                        "Range": ["Auto", "0.1", "1", "10", "100", "1000", "10000", "100000", "1000000"],
                        "Temperature unit": ["°C", "K", "°F"],
                        "Scanning": False,
                        "Channel list": "101:120",
                        }

    def get_GUIparameter(self, parameter = {}):
        #print(parameter)
        self.mode = parameter["Mode"]
        self.digits = parameter["Digits"]  # Digits of resolution
        self.channel_string = parameter["Channel list"]
        intermediate_list = self.channel_string.replace(",",";").split(";")
        self.channel_list = []
        for x in intermediate_list:
            if ":" in x:
                first,last=x.split(":")
                channels_to_add = list(range(int(first),int(last)+1))
                self.channel_list+=[str(x) for x in channels_to_add]
            else:
                self.channel_list+=[x]
        self.channel_names = ["Dev"+x[1:] for x in self.channel_list]
        #self.channel_names = parameter['Channel names'].split(';')
        #self.channel_list = parameter['Channel list']#.replace(" ", "").replace("-", "").split(",")
        self.trigger_type = parameter["Trigger"]
        self.scanning = parameter["Scanning"]

        self.range = parameter["Range"]
        self.integration_speed = parameter["Integration speed"]

        self.temperature_unit = str(parameter["Temperature unit"])

        self.port_string = parameter["Port"]

        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        if self.scanning:
            self.variables = []  #[self.mode+' '+str(x) for x in self.channel_names]
            for i, ch in enumerate(self.channel_list):
                self.variables.append(self.mode + " " + str(self.channel_names[i]))
        else:
            self.variables = [self.mode]
        #self.variables = [self.mode + "@%s" % x for x in parameter['Channel'].replace(" ", "").split(",")]  # we add the channel name to each variable, e.g "Voltage DC@1-03"
        if self.scanning:
            if "Temperature" in self.mode:
                self.units = [self.temperature_unit] * len(self.channel_list)
            else:
                self.units = [self.mode_units[self.mode]] * len(self.channel_list)
            self.plottype = [True] * len(self.channel_list)  # True to plot data
            self.savetype = [True] * len(self.channel_list)
        else:
            self.variables = [self.mode_variables[self.mode]]
            self.units = [self.mode_units[self.mode]]
            self.plottype = [True]  # True to plot data
            self.savetype = [True]

    def connect(self):
        if self.port_string.startswith("TCPIP"):
            self.port.port.set_visa_attribute(pyvisa.constants.VI_ATTR_IO_PROT,4)
            self.port.port.set_visa_attribute(pyvisa.constants.VI_ATTR_TERMCHAR_EN,1)
            self.port.port.set_visa_attribute(pyvisa.constants.VI_ATTR_SEND_END_EN,1)
            # print("Configured %s port for TCPIP communication" % self.shortname)

        # idn = self.get_identification()
        # print("Identification:", idn)

    def initialize(self):
        # once at the beginning of the measurement
        self.port.write("*RST")
        self.port.write("STAT:QUE:CLE")  # clear error queue
        self.port.write("trac:cle")  # clear buffer
        self.port.write("*CLS")  # reset all values
        self.port.write("SYST:BEEP:STAT OFF")  # control-Beep off

    def configure(self):

        # Sense functions
        self.port.write("sense:function '%s', (@%s)" % (self.modes[self.mode], self.channel_string))
        # self.range = self.range.replace(" ", "").replace("p", "e-12").replace("n", "e-9").replace("µ", "e-6").replace("m", "e-3")

        if "Temperature" in self.mode or "Continuity" in self.mode:
            self.port.write("CONF:" + self.modes[self.mode] + " (@%s)" % (self.channel_string) )
        else:
            if self.range == "Auto":
                self.port.write("%s:range:auto on, (@%s)" % (self.modes[self.mode], self.channel_string))
            else:
                #self.port.write("%s:range:auto off, (@%s)" % (self.modes[self.mode], self.channel_string))
                self.port.write("%s:range %s, (@%s)" % (self.modes[self.mode], str(self.range), self.channel_string))

            # Write number of digits resolution
            self.port.write("%s:dig %s, (@%s)" % (self.modes[self.mode], self.digits, self.channel_string) )

        # The following configuration is incompatible with scanning, but may be needed for individual measurements:
        #self.port.write("CONF:%s %s, (@%s)" % (self.modes[self.mode], self.resolution, self.channel_string))  # we send the command of the selected mode and append range, resolution and channel list

        # Trigger
        self.port.write("INIT:CONT OFF")  # disable continuous initiation, needed to use "READ?" command
        self.port.write("TRIG:SOUR %s" % self.trigger_types[self.trigger_type])
        self.port.write("trigger:count 1")  # Only scan through a list once
        self.port.write("TRIG:DEL 0.5")

        # Speed
        if self.integration_speed == "Fast":
            self.nplc = 0.1
        elif self.integration_speed == "Medium":
            self.nplc = 1.0
        elif self.integration_speed == "Slow":
            self.nplc = 10.0
        else:
            self.nplc = 1.0
        self.port.write(":SENS:%s:NPLC %s" % (self.modes[self.mode], str(self.nplc)))

        # Sample count:
        # Note, sample count is the number of measurements that will be returned,
        # not the number of measurements per channel.
        if self.scanning:
            self.port.write("sample:count " + str(len(self.channel_list)))
        else:
            self.port.write("sample:count 1")

        # Scanning
        if self.scanning:
            self.port.write("route:scan (@" + self.channel_string + ")")  # start scan in the background
            self.port.write("ROUT:SCAN:TSO IMM")  # Start scan immediately when enabled and triggered
            self.port.write("ROUT:SCAN:LSEL INT")  # Enable Scan

    def deinitialize(self):
        self.port.write("SYST:BEEP:STAT ON")  # control-Beep on

    def trigger_ready(self):
        self.had_trigger = False
        self.port.write("INIT") #initialize trigger

    #def measure(self):

        #if self.scanning:
        #    self.port.write("form:elem READ,CHAN\n;READ?")
        #else:
        #    self.port.write("form:elem READ\n;READ?") # This returns just the reading

    def request_result(self):
        #wait for trigger
        self.port.write("TRAC:FREE?")
        bytes_in_buffer = self.port.read().split(",")
        bytes_in_use = bytes_in_buffer[1]

        # normally 16 bytes reserved for each entry in buffer: 8 bytes per measure value, 8 bytes per timestamp
        while int(bytes_in_use) < len(self.channel_list)*16:
            stop_measurement = self.is_run_stopped()
            if stop_measurement:
                break

            self.port.write("TRAC:FREE?")
            bytes_in_buffer = self.port.read().split(",")
            bytes_in_use = bytes_in_buffer[1]

            time.sleep(0.5)

        if int(bytes_in_use) > len(self.channel_list)*16:
            self.had_trigger = True

    def call(self):
        if self.had_trigger:
            self.port.write("form:elem READ\n;FETCh?")
            answer = self.port.read()  # here we read the response from the "READ?" request in 'measure'
            readings_list = np.array([float(x) for x in answer.strip("\n").split(",")])
            #print(len(readings_list))
            #print(readings_list)
            #print(len(self.channel_list))
            #print("Response to READ? command:", answer)

            if self.scanning:
                # Currently averaging is not implemented for scanning
                return [x for x in readings_list] #[np.mean(x) for x in np.split(readings_list,len(self.channel_list))]
            else:
                return [np.mean(readings_list)]

    # here, command-wrapping functions are defined

    def get_identification(self):

        self.port.write("*IDN?")
        return self.port.read()
