# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023-2024 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank Dr. Anton Kirch for providing the initial list sweep feature.

# SweepMe! driver
# * Module: SMU
# * Instrument: Keithley 2400

import time

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Keithley2400"
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]

        self.port_properties = {
            "timeout": 10,
            "EOL": "\r",
            "baudrate": 9600,
        }

        self.commands = {
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
            "Voltage [V]": "VOLT",  # deprecated, remains for compatibility reasons
            "Current [A]": "CURR",  # deprecated, remains for compatibility reasons
        }

        self.outpon = False

    def set_GUIparameter(self):

        gui_parameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Front", "Rear"],
            "Speed": ["Fast", "Medium", "Slow", "Very fast"],
            "Range": [
                "Auto",
                "10 nA",
                "100 nA",
                "1 µA",
                "10 µA",
                "100 µA",
                "1 mA",
                "10 mA",
                "100 mA",
                "1 A",
            ],
            "Compliance": 100e-6,
            "Average": 1,
            "4wire": False,

            "ListSweepCheck": True,
            "ListSweepType": ["Sweep", "Custom"],
            "ListSweepStart": 0.5,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": ["Step width:", "Points (lin.):", "Points (log.):"],
            "ListSweepStepPointsValue": 0.1,
            "ListSweepCustomValues": "",
            "ListSweepDual": False,
            "ListSweepHoldtime": 0.1,
            "ListSweepDelaytime": 0.1,
        }

        return gui_parameter

    def get_GUIparameter(self, parameter={}):

        self.sweepvalue = parameter["SweepValue"]
        self.listtype = parameter["ListSweepType"]
        self.four_wire = parameter["4wire"]
        self.route_out = parameter["RouteOut"]
        self.source = parameter["SweepMode"]
        self.protection = parameter["Compliance"]
        self.range = parameter["Range"]
        self.speed = parameter["Speed"]
        self.average_gui = int(parameter["Average"])
        self.port_string = parameter["Port"]

        self.average = self.average_gui
        if self.average_gui < 1:
            self.average = 1
        if self.average_gui > 100:
            self.average = 100

        if self.sweepvalue == "List sweep" and self.listtype == "Sweep":
            self.listsweep_start = float(parameter["ListSweepStart"])
            self.listsweep_end = float(parameter["ListSweepEnd"])
            self.listsweep_steppoints_type = parameter["ListSweepStepPointsType"]
            self.listsweep_steppoints_value = float(parameter["ListSweepStepPointsValue"])
            self.listsweep_dual = float(parameter["ListSweepDual"])

        if self.sweepvalue == "List sweep" and self.listtype == "Custom":
            self.custom_values = str(parameter["ListSweepCustomValues"])

        # source delay, time between applying source value and measurement
        # use None (later AUTO), if empty
        try:
            self.listsweep_hold = float(parameter["ListSweepHoldtime"])
        except:
            self.listsweep_hold = None

        # trigger delay, time between trigger and applying source value
        # use None (later AUTO), if empty
        try:
            self.listsweep_delay = float(parameter["ListSweepDelaytime"])
        except:
            self.listsweep_delay = None

        # in case of a list sweep, the time stamp of each measurement point must be saved additionally
        # to every (V,I) tuple
        if self.sweepvalue == "List sweep":
            self.variables = ["Voltage", "Current", "Timestamp"]
            self.units = ["V", "A", "s"]
            self.plottype = [True, True, True]  # True to plot data
            self.savetype = [True, True, True]  # True to save data
        else:
            self.variables = ["Voltage", "Current"]
            self.units = ["V", "A"]
            self.plottype = [True, True]  # True to plot data
            self.savetype = [True, True]  # True to save data

    def initialize(self):

        identifier = self.get_identification()

        vendor, model, sn_version, fw_version = identifier.split(",")

        try:
            fw_version_year = int(fw_version.split()[3])
        except ValueError:
            fw_version_year = -1  # unknown version

        # The Keithley 2400 supports two protocols: 488.1 and SCPI
        # The SCPI protocol is better as it works more stable. If several devices are connected at the same time,
        # the 488.1 protocol can lead to timeout errors
        # Lets switch to SCPI protocol if 488.1 is currently selected
        # This is only performed for firmware version later than 1998
        if not self.port_string.startswith("COM") and fw_version_year > 1998:
            try:
                self.port.write("SYST:MEP:STAT?")
                if self.port.read() == "0":
                    self.port.write("SYST:MEP:STAT 1")
                    # A short time is needed before the new protocol works and new commands can be received.
                    time.sleep(0.1)
                    self.port.write("SYST:MEP:STAT?")
                    if self.port.read() == "1":
                        debug("Keithley 2400: GPIB communication protocol was changed to 'SCPI' automatically.")
                    else:
                        debug("Keithley 2400: Not able to select 488.1 protocol. "
                              "Please change manually via Menu -> Communication -> GPIB -> GPIB Protocol")
            except:
                error("Unable to change GPIB communication protocol to 'SCPI' for identifier '%s'" % identifier)

        # once at the beginning of the measurement
        self.reset()
        # time.sleep(0.05) # maybe needed to prevent random "Undefined Header error -113"
        self.clear()

        self.port.write("SYST:BEEP:STAT OFF")  # control-beep off

        if self.average_gui > 100:
            self.message_Box("Maximum allowed average is 100 and average has been changed to 100")

        # if List Sweep is selected, check list start and end values correspond to step width
        if self.sweepvalue == "List sweep" and self.listtype == "Sweep":
            if self.listsweep_steppoints_type.startswith("Step width"):
                if self.listsweep_steppoints_value == 0.0:
                    if self.listsweep_end != self.listsweep_start:
                        msg = "Start and end value must be equal if step width is zero."
                        raise ValueError(msg)

        # if Custom List Sweep is chosen, check if the entered values are a comma-separated list
        if self.sweepvalue == "List sweep" and self.listtype == "Custom":
            try:
                value_list = list(map(float, self.custom_values.split(",")))
            except:
                msg = "Wrong custom values format. Please use comma-separated values for custom list sweeps."
                raise ValueError(msg)

    def configure(self):
        # set trigger count to default = 1 to ensure correct SweepEditor function after ListSweep
        self.port.write(":TRIG:COUNt DEFault")
        self.port.write(":SOUR:CLE:AUTO OFF")

        if self.route_out == "Front":
            self.port.write("ROUT:TERM FRON")  # use front or rear terminal for power supply
        if self.route_out == "Rear":
            self.port.write("ROUT:TERM REAR")  # use front or rear terminal for power supply

        self.range = (self.range.replace(" ", "").replace("p", "e-12").replace("n", "e-9").
                      replace("µ", "e-6").replace("m", "e-3"))

        if self.source.startswith("Voltage"):
            self.port.write(":SOUR:FUNC VOLT")
            # sourcemode = Voltage
            self.port.write(":SOUR:VOLT:MODE FIX")
            # sourcemode fix
            self.port.write(':SENS:FUNC "CURR"')
            # measurement mode
            self.port.write(":SENS:CURR:PROT " + self.protection)
            # Protection with Imax

            if self.range == "Auto":  # it means Auto was selected
                self.port.write(":SENS:CURR:RANG:AUTO ON")  # Autorange for current measurement
            else:
                self.port.write(":SENS:CURR:RANG:AUTO OFF")
                self.port.write(":SENS:CURR:RANG %s" % str(self.range.replace("A", "")))

        elif self.source.startswith("Current"):
            self.port.write(":SOUR:FUNC CURR")
            # sourcemode = Voltage
            self.port.write(":SOUR:CURR:MODE FIX")
            # sourcemode fix
            self.port.write(':SENS:FUNC "VOLT"')
            # measurement mode
            self.port.write(":SENS:VOLT:PROT " + self.protection)
            # Protection with Imax

            if self.range == "Auto":  # it means Auto was selected
                self.port.write(":SOUR:CURR:RANG:AUTO ON")  # Autorange for voltage measurement
            else:
                self.port.write(":SOUR:CURR:RANG:AUTO OFF")
                self.port.write(":SOUR:CURR:RANG %s" % str(self.range.replace("A", "")))

        # Speed / Integration / NPLC
        if self.speed == "Fast":
            self.nplc = 0.1
        elif self.speed == "Very fast":
            self.nplc = 0.01
        elif self.speed == "Medium":
            self.nplc = 1.0
        elif self.speed == "Slow":
            self.nplc = 10.0

        self.port.write(":SENS:CURR:DC:NPLC " + str(self.nplc))
        self.port.write(":SENS:VOLT:DC:NPLC " + str(self.nplc))

        # 4-wire sense
        if self.four_wire:
            self.port.write("SYST:RSEN ON")
        else:
            self.port.write("SYST:RSEN OFF")

        # Averaging
        self.port.write(":SENS:AVER:TCON REP")  # repeatedly take average
        if self.average > 1:
            self.port.write(":SENS:AVER ON")
            self.port.write(":SENSe:AVER:COUN %i" % self.average)  # repeatedly take average
        else:
            self.port.write(":SENS:AVER OFF")
            self.port.write(":SENSe:AVER:COUN 1")

        # If 'List sweep' with type 'Sweep' is selected, generate data from respective input parameters
        # List-sweep options: mode 1 is linear, mode 2 is logarithmic, both single sweep start to stop
        if self.sweepvalue == "List sweep" and self.listtype == "Sweep":
            if self.listsweep_steppoints_type.startswith("Step width"):
                listsweepmode = 1

                if self.listsweep_steppoints_value == 0.0:
                    if self.listsweep_end == self.listsweep_start:
                        listsweep_points = 1
                    else:
                        msg = "Start and end value must be equal if step width is zero."
                        raise ValueError(msg)
                else:
                    listsweep_points = round(abs(self.listsweep_end - self.listsweep_start)
                                             / abs(self.listsweep_steppoints_value) + 1)

            elif self.listsweep_steppoints_type.startswith("Points (lin.)"):
                listsweepmode = 1
                listsweep_points = self.listsweep_steppoints_value

            elif self.listsweep_steppoints_type.startswith("Points (log.)"):
                listsweepmode = 2
                listsweep_points = self.listsweep_steppoints_value

            if self.listsweep_dual:
                # forward and backward sweep (start to start over stop value) is mode 3 for linear and 4 for logarithmic
                # thus 2 larger than the modes without dual sweep/double sweep
                listsweepmode += 2

            self.set_sweep(self.source,
                           listsweepmode,
                           self.listsweep_start,
                           self.listsweep_end,
                           listsweep_points,
                           self.listsweep_delay,
                           self.listsweep_hold)

        # If 'Sweep list/Custom' is selected, get and operate the entered custom values
        if self.sweepvalue == "List sweep" and self.listtype == "Custom":
            list_string = self.custom_values

            # convert custom string to float list, count the list entries,
            # which gives the trigger points for the measurement
            value_list = list(map(float, list_string.split(",")))
            points = len(value_list)

            # hand over dataset to Keithley
            self.set_listvalues(self.source, list_string, points, self.listsweep_delay, self.listsweep_hold)

        # let's ensure all parameters are set before we continue
        self.wait_for_complete()

    def deinitialize(self):
        self.port.write("SYST:RSEN OFF")
        self.port.write("ROUT:TERM FRON")
        self.port.write(":SENS:CURR:DC:NPLC 1")
        self.port.write(":SENS:VOLT:DC:NPLC 1")
        self.port.write(":SENS:AVER OFF")
        self.port.write(":SENSe:AVER:COUN 1")

        self.port.write("SYST:BEEP:STAT OFF")  # control-Beep off

        if self.port_string.startswith("COM"):
            self.port.write("SYST:LOC")  # RS-232/COM-port only
        else:
            self.port.write("GTL")

    def poweron(self):
        self.port.write("OUTP ON")
        self.outpon = True

    def poweroff(self):
        self.port.write("OUTP OFF")
        self.outpon = False

    def apply(self):
        self.port.write(":SOUR:" + self.commands[self.source] + ":LEV %s" % self.value)  # set source

    def reach(self):
        self.wait_for_complete()

    def measure(self):
        self.port.write("READ?")

    def call(self):

        answer = self.port.read().split(",")
        if answer == [""]:
            answer = self.port.read().split(",")

        # answer comes as a string separated by commas, 5 values per source point
        data = np.asarray(answer)
        data = data.reshape((data.shape[0] // 5, 5))
        data = data.astype(np.float64)

        self.v = data[:,0]
        self.i = data[:,1]
        self.t = data[:,3]

        # print time stamps into results file when list sweep is operated
        if self.sweepvalue == "List sweep":
            return [self.v, self.i, self.t]
        else:
            return [float(self.v), float(self.i)]

    def set_sweep(self, source, listsweepmode, start, stop, points, delay, hold):
        """Only applies to 'List sweep/Sweep' mode and sets a staircase sweep for voltage or current.

        Arguments Pcomp and Rmode are not set and use default values

        Arguments:
            source (str): "Voltage [V]" or "Current [A]" (for voltage or current)
            listsweepmode (int):
                1 -> Linear sweep (single stair)
                2 -> Logarithmic sweep (single stair)
                3 -> Linear sweep (double stair)
                4 -> Log sweep (double stair)
            start (float): Start value in V or A
            stop (float): End value in V or A
            points (int): Number of steps
            delay (float): Trigger latency between trigger and source output
            hold (float): Source delay, time between setting a source value and measurement
        """
        source = str(source)
        mode = int(listsweepmode)
        start = float(start)
        stop = float(stop)
        points = int(points)

        if mode == 1:
            # source values run up a linear staircase
            sweep_list = np.linspace(start, stop, points)

        if mode == 2:
            # source values run up a logarithmic staircase
            sweep_list = np.geomspace(start, stop, points)

        if mode == 3:
            # source values run up and down a linear staircase, stop value executed only once
            sweep_list_up = np.linspace(start, stop, points)
            sweep_list = np.append(sweep_list_up, np.flipud(sweep_list_up[:-1]))
            points = len(sweep_list)

        if mode == 4:
            # source values run up and down a logarithmic staircase, stop value executed only once
            sweep_list_up = np.geomspace(start, stop, points)
            sweep_list = np.append(sweep_list_up, np.flipud(sweep_list_up))
            points = len(sweep_list)

        # Keithlety 2400 expects sweep list as a string separated by commas
        list_string = ",".join(format(value, ".6e") for value in sweep_list)

        # hand over dataset to Keithley
        self.set_listvalues(source, list_string, points, delay, hold)

    def set_listvalues(self, source, list_string, points, delay, hold):
        """Only applies to mode 'List sweep' and hands over the list of input data to the Keithley.

        The sweep is only read out after the measurement is completed, which reduces the sweep time.
        Arguments Pcomp and Rmode are not set and use default values.

        Arguments:
            source (str): "Voltage [V]" or "Current [A]" (for voltage or current)
            list_string (str): List sweep values
            points (int): Number of values in list_string --> gives number of trigger points for Keithley
            delay (float): Trigger latency between trigger and source output
            hold (float): Source delay, time between setting a source value and measurement
        """
        source = str(source)
        points = int(points)

        # Keithley 2400 can take up to 100 list values
        if points < 1:
            msg = "Number of steps must be larger than 0."
            raise ValueError(msg)
        if points > 100:
            msg = "Number of steps must be smaller than 101."
            raise ValueError(msg)

        if "Voltage" in source:
            self.port.write(":SOURce:VOLTage:MODE LIST")
            self.port.write(":SOURce:LIST:VOLTage %s" % list_string)
        elif "Current" in source:
            self.port.write(":SOURce:CURRent:MODE LIST")
            self.port.write(":SOURce:LIST:CURRent %s" % list_string)
        else:
            msg = "No source mode identified."
            raise ValueError(msg)

        # set trigger count to measurement points
        self.port.write(":TRIG:COUN %d" % points)

        # set trigger latency, AUTO if no value given
        if type(delay) == float:
            self.port.write(":TRIGger:DELay %.6f" % delay)
        else:
            self.port.write(":TRIGger:DELay AUTO")

        # set hold time between source value and measurement, AUTO if no value given
        if type(hold) == float:
            self.port.write(":SOURce:DELay %.6f" % hold)
        else:
            self.port.write(":SOURce:DELay AUTO")

    def get_identification(self):
        # Retrieves the identification string
        self.port.write("*IDN?")
        return self.port.read()

    def reset(self):
        """Resets the instrument to default parameters."""
        self.port.write("*RST")

    def clear(self):
        """Clears the status register and error queue."""
        self.port.write("*CLS")

    def wait_for_complete(self):
        """Waits for the operation queue to be completed."""
        self.port.write("*OPC?")
        return self.port.read()
