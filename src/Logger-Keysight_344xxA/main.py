# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Logger
# * Instrument: Keysight 344xxA

from __future__ import annotations

import re
import time  # needed for polling status of sampling on 3441xA instruments
from typing import Any

import numpy as np  # needed for creation of empty time list variable during sampling
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>Keysight 344xxA Series</strong></p>
                     <p>DMM: Digital Multimeter</p>
                     <p>&nbsp;</p>
                     <p>Supported devices: The driver has been tested with 34401A, 34410A, 34411A and 34465A. Other versions of the 344xxA  series (e.g. 34461A, 34470A) that share the same SCPI commands should work as well.</p>
                     <p>The 34401A/34410A/34411A/3446xA are 6.5 digit DMM that support measurement of voltage, current, resistance, with some models offering additional capabilities to measure capacitance, temperature and frequency as well.</p>
                     <p>&nbsp;</p>
                     <p>Driver notes:</p>
                     <p>The instruments can be driven either via GPIB, USB or Ethernet LAN, depending on the model in use and its equipped options.</p>
                     <p>Sampling mode (called "Digitizing" by Keysight) is included for those models which support it. The driver will run basic checks regarding model-depending maximum capabilities but certain invalid combinations might still be possible (e.g. Auto-Zero can cause artifacts and should be turned of when using sampling). Depending on the licensed amount of memory, the data buffer can vary among models which is why in sampling mode, the total amount of resulting samples is not checked.</p>
                     <p>If the Trigger Delay default value of 0 is removed and the field is left empty, the AUTO setting will be applied by the instrument natively.</p>
                     <p>If a lower than possible current range is selected for the 34401A, the instrument will default to its lowest possible range without returning an error.</p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Keysight344xxA"

        self.port_manager = True
        self.port_types = ["GPIB", "USB", "TCPIP"]

        self.port_properties = {
            "timeout": 6,  # needed for 100 NPLC setting as it needs ~5s to computer under certain circumstances
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Voltage DC": "VOLT:DC",
            "Voltage AC": "VOLT:AC",
            "Current DC": "CURR:DC",
            "Current AC": "CURR:AC",
            "2W-Resistance": "RES",
            "4W-Resistance": "FRES",
            "Frequency": "FREQ",
            "Period": "PER",
            "Diode": "DIOD",
            "Continuity": "CONT",
            "Capacitance": "CAP",
            "Temperature": "TEMP",
        }

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Voltage DC": "V",
            "Voltage AC": "V",
            "Current DC": "A",
            "Current AC": "A",
            "2W-Resistance": "Ohm",
            "4W-Resistance": "Ohm",
            "Frequency": "Hz",
            "Period": "s",
            "Diode": "V",
            "Continuity": "",
            "Capacitance": "F",
            "Temperature": "deg",
        }

        # range selection depends on mode of operation
        # this nested dictionary takes care of the possible combinations by offering all ranges per mode of operation
        self.ranges = {
            "Voltage DC": {
                "Auto": "AUTO",
                "As is": "",
                "100 mV": "1E-01",
                "1 V": "1",
                "10 V": "10",
                "100 V": "100",
                "1000 V": "1000"
            },
            "Voltage AC": {
                "Auto": "AUTO",
                "As is": "",
                "100 mV": "1E-01",
                "1 V": "1",
                "10 V": "10",
                "100 V": "100",
                "1000 V": "1000"
            },
            "Current DC": {
                "Auto": "AUTO",
                "As is": "",
                "100 uA": "1E-04",
                "1 mA": "1E-03",
                "10 mA": "1E-02",
                "100 mA": "1E-01",
                "1 A": "1",
                "3 A": "3"
            },
            "Current AC": {
                "Auto": "AUTO",
                "As is": "",
                "100 uA": "1E-04",
                "1 mA": "1E-03",
                "10 mA": "1E-02",
                "100 mA": "1E-01",
                "1 A": "1",
                "3 A": "3"
            },
            "2W-Resistance": {
                "Auto": "AUTO",
                "As is": "",
                "100 Ohm": "1E02",
                "1 kOhm": "1E03",
                "10 kOhm": "1E04",
                "100 kOhm": "1E05",
                "1 MOhm": "1E06",
                "10 MOhm": "1E07",
                "100 MOhm": "1E08",
                "1 GOhm": "1E09"
            },
            "4W-Resistance": {
                "Auto": "AUTO",
                "As is": "",
                "100 Ohm": "1E02",
                "1 kOhm": "1E03",
                "10 kOhm": "1E04",
                "100 kOhm": "1E05",
                "1 MOhm": "1E06",
                "10 MOhm": "1E07",
                "100 MOhm": "1E08",
                "1 GOhm": "1E09"
            },
            "Frequency": {
                "Auto": "",
                "As is": "",
                "3 Hz": "3",
                "30 Hz": "3E01",
                "300 Hz": "3E02",
                "3 kHz": "3E03",
                "30 kHz": "3E04",
                "300 kHz": "3E05"
            },
            "Period": {
                "Auto": "",
                "As is": "",
                "336 ns": "336E-9",
                "3.333 us": "3.333E-6",
                "33.333 us": "33.333E-6",
                "333.33 us": "333.33E-6",
                "3.3333 ms": "3.3333E-3",
                "33.333 ms": "33.333E-3",
                "333.33 ms": "333.33E-3"
            },
            "Diode": {
                "Auto": ""
            },
            "Continuity": {
                "Auto": ""
            },
            "Capacitance": {
                "As is": "",
                "Auto": "AUTO",
                "1 nF": "1E-09",
                "10nF": "1E-08",
                "100nF": "1E-07",
                "1uF": "1E-06",
                "10uF": "1E-05"
            },
            "Temperature": {
                "Auto": "",
            }
        }

        # Temperature sensor settings
        self.tempprobes = {
            "2W-RTD": "RTD",
            "4W-RTD": "FRTD",
            "2W-Thermistor": "THER",
            "4W-Thermistor": "FTH",
            "Thermocouple E-Type": "TC,E",
            "Thermocouple J-Type": "TC,J",
            "Thermocouple K-Type": "TC,K",
            "Thermocouple N-Type": "TC,N",
            "Thermocouple R-Type": "TC,R",
            "Thermocouple T-Type": "TC,T",
        }

        self.nplc_types = {
            "0.001 (34411A/34465/34470)": 0.001,
            "0.002 (34411A/34465/34470)": 0.002,
            "0.006 (3441xA/34465/34470)": 0.006,
            "0.02 (344xxA)": 0.02,
            "0.06 (344xxA)": 0.06,
            "0.2 (344xxA)": 0.2,
            "1 (344xxA)": 1,
            "2 (344xxA)": 2,
            "10 (344xxA)": 10,
            "100 (344xxA)": 100
        }

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        self.mode = parameters.get("Mode", "Voltage DC")
        self.sampling = parameters.get("Sampling Mode", False)
        self.trigsource = parameters.get("Trigger Source", "IMM")

        # new_parameters are retrieved in several steps to squeeze in "Sampling Time", Temperature measurement and Trigger options, if required
        new_parameters = {
            "Mode": list(self.modes.keys()),
            "Sampling Mode": False,
        }

        # if sampling mode is activated, additional options for setting the sampling parameters is enabled
        if self.sampling:
            new_parameters.update({
                "Sampling Time in s": 0.00002,
                "Sample Count": 1000,
                # Pre-Trigger Samples allows for trigger timing corrections on a per-sample base as sampling data is aquired into a transit storage
                "Pre-Trigger Samples": 0,
                " ": None,  # empty field for better structuring of GUI
            })

        # if temperature measurement mode is selected, the additional options for the unit and probe type are added
        if self.mode == "Temperature":
            new_parameters.update({
                # Temperature Unit will be used to overwrite placeholder "deg" that is set before in "__init__"
                "Temperature Unit": ["C", "F", "K"],
                "Temperature Probe": list(self.tempprobes.keys())
            })

        # adding additional standard parameters
        new_parameters.update({
            "NPLC": list(self.nplc_types.keys()),
            "Range": list(self.ranges[self.mode].keys()),
            # internal trigger is called IMMediate because triggering is done automatically immediately as soon as possible
            "Trigger Source": ["IMM", "INT", "EXT"],
        })

        # trigger parameters are added depending on the choice of trigger source
        if self.trigsource == "INT":
            new_parameters.update({
                # As INT triggering is based on the input signal, the trigger level and slope needs to be set similar to operating a scope
                "Trigger Level": 0.00,
                "Trigger Slope": ["POS", "NEG"]
            })

        # last addition of standard parameters
        new_parameters.update({
            "Trigger Delay in s": 0.000,
            "Auto-Zero": ["On", "Once", "Off"],
            "Display": ["On", "Off"],
            "Beep": ["On", "Off"]
            # note: SCPI commands are not case-sensitive so "On" and "Off" can be used directly, alternatively to "ON" and "OFF" via a dictionary
        })

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.mode = parameters.get("Mode", "Voltage DC")

        self.sampling = parameters.get("Sampling Mode", False)
        if self.sampling:
            self.samplingtime = parameters.get("Sampling Time in s", 0.00002)
            self.samplecount = parameters.get("Sample Count", 1000)
            self.pretrigger = parameters.get("Pre-Trigger Samples", 0)

        if self.mode == "Temperature":
            self.tempunit = parameters.get("Temperature Unit", "C")
            self.tempprobe = parameters.get("Temperature Probe", "2W-RTD")

        self.range = parameters.get("Range", "Auto")
        self.nplc = parameters.get("NPLC", "0.02 (344xxA)")

        self.trigsource = parameters.get("Trigger Source", "IMM")
        if self.trigsource == "INT":
            self.triglevel = parameters.get("Trigger Level", 0.00)
            self.trigslope = parameters.get("Trigger Slope", "POS")
        self.trigdelay = parameters.get("Trigger Delay in s", 0.000)

        self.autozero = parameters.get("Auto-Zero", "On")
        self.display = parameters.get("Display", "On")
        self.beep = parameters.get("Beep", "On")

        # here, the variables and units are defined, based on the selection of the user
        # Note: Temperature mode is not available for sampling, so unit handling needs only be taken care of for non-sampling operation
        if self.sampling:
            # in sampling mode, the results are in the form of two lists containing time and measurement values instead of just one variable
            self.variables = ["Time", self.mode]
            self.units = ["s", self.mode_units[self.mode]]
            # True to plot data
            self.plottype = [True, True]
            # True to save data
            self.savetype = [True, True]
        else:
            # in non-sampling mode, the driver will return just one variable containing one measurement result value
            self.variables = [self.mode]
            # in case temperature is measured, do not use the general unit "deg" from the dictionary within initialization but the one unit chosen via the GUI
            if self.mode == "Temperature":
                self.units = [self.tempunit]
            else:
                # if anything selse but temperature is measured, assign unit from dictionary
                self.units = [self.mode_units[self.mode]]
            # True to plot data
            self.plottype = [True]
            # True to save data
            self.savetype = [True]

    def initialize(self) -> None:
        """Verify the connection and check the capabilities of the instrument, based on the user settings."""
        # once at the beginning of the initialization, STATUS:PRESET is used to reset registers
        self.port.write("STAT:PRES")

        # run model identification routine
        self.model = self.get_model()

        # run capability checks based on identified model
        if self.sampling:
            # This section contains the capability checks when sampling mode is selected
            if self.model in ["34401A", "34460A", "34461A"]:
                # check if sampling is activated for use with an unsupported model
                msg = f"Sampling mode not supported by model {self.model}."
                raise ValueError(msg)
            if self.mode not in ["Voltage DC", "Current DC"]:
                # check if sampling is activated for a non-supported measurement mode
                msg = f"Sampling mode restricted to Voltage DC and Current DC."
                raise ValueError(msg)
            if self.model in ["34410A"]:
                # check regarding maximum sampling speed for 34410A
                if (self.nplc_types[self.nplc] * 0.02) / float(self.samplingtime) > 0.2:
                    msg = f"Requested sampling too fast. Please reduce NPLC or increase sampling time."
                    raise ValueError(msg)
            if self.model in ["34411A", "34465A", "34470A"]:
                # check regarding maximum sampling speed for 34411A, 34465A and 34470A
                if (self.nplc_types[self.nplc] * 0.02) / float(self.samplingtime) > 1:
                    msg = f"Requested sampling too fast. Please reduce NPLC or increase sampling time."
                    raise ValueError(msg)
            elif self.pretrigger != "0":
                # Pre-Trigger is only supported in 34411A, 34465A and 34470A
                msg = f"PreTrigger not supported by this model, please set to 0."
                raise ValueError(msg)

        if self.model in ["34401A"] and self.mode in ["Temperature", "Capacitance"]:
            # check if an unsupported measurement mode is selected for use with model 34401A
            msg = f"Mode '{self.mode}' is not supported by model {self.model}."
            raise ValueError(msg)

        if self.model in ["34410A", "34411A"] and self.mode in ["Temperature"] and self.tempprobe.startswith(
                "Thermocouple"):
            # check if thermocouple sensors are selected for opperation on 34410A or 34411A
            msg = f"Temperature sensor type '{self.tempprobe}' is not supported by model {self.model}."
            raise ValueError(msg)

        if (self.model in ["34401A", "34460A", "34461A"] and self.nplc_types[self.nplc] < 0.02) or (
                self.model in ["34410A"] and self.nplc_types[self.nplc] < 0.006):
            # check if selected NPLC setting is too fast for some models
            msg = f"Selected NPLC setting is too fast for model {self.model}."
            raise ValueError(msg)

        # can be used on 34410A/34411A to show text on lower instrument display
        # self.port.write(":DISP:WIND2:TEXT \"DRIVEN BY SWEEPME\"")

        # can be used on 3446xA/34470A to show text on display; empty text string resets display to normal behaviour
        # self.port.write(":DISP:TEXT \"Driven by\nSweepMe!\"")
        # self.port.write(":DISP:TEXT \"\"")

        # clears the event registers in all register groups and the error queue
        self.port.write("*CLS")

        # Beep output enable/disable
        self.port.write("SYST:BEEP:STAT %s" % self.beep)

        # setting the chosen unit and probe type for temperature measurement
        if self.mode == "Temperature":
            self.port.write("UNIT:TEMP %s" % self.tempunit)
            self.port.write("TEMP:TRAN:TYPE %s" % self.tempprobes[self.tempprobe])

    def deinitialize(self) -> None:
        """Turn beeper on again."""
        # Beep output enable
        self.port.write("SYST:BEEP:STAT ON")

    def configure(self) -> None:
        """Set the measurement mode, range, speed and trigger settings according to the user settings."""
        # Set Mode and Range
        if self.model in ["34401A"]:
            # if the model is 34401A, mode and range are set separately; we start with setting the mode
            self.port.write("CONF:%s" % self.modes[self.mode])
            # setting the range on the 34401A, which is in the SENSE section rather than the CONFIG sections as for all other 344xxA
            if self.ranges[self.mode][self.range] == "AUTO":
                # for the 34401A, the range "AUTO" does not exist; instead, "AUTO-Ranging" as a feature is switched ON or OFF
                self.port.write("SENSE:%s:RANG:AUTO ON" % self.modes[self.mode])
            elif self.ranges[self.mode] != "As is":
                # if range is not set to "As is" (in which case we just wouldn't touch the range setting), a manual range is set and AUTO-Ranging is deactivated automatically
                self.port.write("SENSE:%s:RANG %s" % (self.modes[self.mode], self.ranges[self.mode][self.range]))
        else:
            # this measurement mode and range command is understood by all models except the 34401A
            # in case of range setting "As is", the value is simply left empty as defined by the range dictionary
            self.port.write("CONF:%s %s" % (self.modes[self.mode], self.ranges[self.mode][self.range]))

        # Speed
        if self.mode not in ["Voltage AC", "Current AC", "Frequency", "Period", "Diode", "Continuity", "Capacitance"]:
            # NPLC only supported in DC Volts, DC Current, 2W- and 4W-Resistance, Temperature
            self.port.write(":SENS:%s:NPLC %s" % (self.modes[self.mode], self.nplc_types[self.nplc]))

        # Trigger
        # setting source for triggering
        self.port.write("TRIG:SOUR %s" % self.trigsource)
        # in case we use the internal trigger which depends on a signal level and slope:
        if self.trigsource == "INT":
            # setting signal level of trigger, representing a voltage or current value, depending on active mode
            self.port.write("TRIG:LEV %s" % self.triglevel)
            # setting slope of trigger
            self.port.write("TRIG:SLOP %s" % self.trigslope)

        # sets the trigger delay
        self.port.write("TRIG:DEL %s" % self.trigdelay)

        # Auto-Zero
        # Auto-Zero only supported in DC Volts, DC Current, 2W-Resistance, Temperature
        # Warning: using Auto-Zero in sampling mode with fast timing settings creates false measurement signals
        if self.mode not in ["Voltage AC", "Current AC", "Frequency", "Period", "Diode", "Continuity", "Capacitance",
                             "4W-Resistance"]:
            if self.model in ["34401A"]:
                # the 34401A AUTO ZERO command is set independingly from the measurement mode
                self.port.write(":SENS:ZERO:AUTO %s" % self.autozero)
            else:
                # all other 344xxA models require the AUTO ZERO command to be called via the selected measurement mode
                self.port.write(":SENS:%s:ZERO:AUTO %s" % (self.modes[self.mode], self.autozero))

        # Display Control
        if self.display == "Off":
            # Display OFF if model is 34410A or 34411A (because of 2-line display):
            if self.model in "3441":
                self.port.write(":DISP:WIND1:STAT 0")
                self.port.write(":DISP:WIND2:STAT 0")
            # Display OFF command for all other models:
            else:
                self.port.write(":DISP:STAT 0")

        # Sampling settings;
        # "self.samplecount" samples will be recorded after each "self.samplingtime"
        # while each sample contains a measurement over the time of "self.nplc"
        # where 1 "N"umberof"P"ower"L"ine"C"ycles means 50Hz in Europe = 0.02s
        if self.sampling:
            # defines time as the source for triggering the single sampling events
            self.port.write("SAMP:SOUR TIM")
            # set sampling intervall time
            self.port.write("SAMP:TIM %s" % self.samplingtime)
            # set sample count
            self.port.write("SAMP:COUN %s" % self.samplecount)
            # set amount of samples before trigger event to be included in the recording
            if self.model in ["34411A", "34465A", "34470A"]:
                self.port.write("SAMP:COUN:PRET %s" % self.pretrigger)
            # deactivation of all calculcations; multiple commands in one line, seperated by semicolon
            if self.model in ["34465A", "34470A"]:
                self.port.write(":CALC:TRAN:HIST 0;:CALC:AVER 0;:CALC:TCH 0")

    def unconfigure(self) -> None:
        """Display ON again if it was switched OFF before"""
        if self.display == "Off":
            # if model is 34410A or 34411A (because of 2-line display):
            if self.model in "3441":
                self.port.write(":DISP:WIND1:STAT 1")
                self.port.write(":DISP:WIND2:STAT 1")
            # Display ON command for all other models:
            else:
                self.port.write(":DISP:STAT 1")

    def measure(self) -> None:
        """Trigger a measurement."""
        if self.sampling:
            # triggering of a sampling measurement
            self.port.write("INIT")
        else:
            # triggers a new measurement and requests the measurement result value to be put into the output buffer
            self.port.write("READ?")

    def call(self) -> list[float] | list[list[float]]:
        """Read the measurement result value(s) from the output buffer and return them as a list.

        In case of sampling, two lists are returned, one for time and one for measurement values.
        """
        if self.sampling:
            # if sampling function is used, we retrieve readings from instrument memory
            # newer models allow the use of the parameter WAIT to wait until completion if not all samples have accumulated yet
            if self.model in ["34465A", "34470A"]:
                self.port.write("DATA:REMove? %s,WAIT" % self.samplecount)
            else:
                # for data retrieving on older 3441xA models, a polling routine is needed
                checksampling = 0
                while checksampling < int(self.samplecount):
                    self.port.write("DATA:POIN?")
                    checksampling = int(self.port.read())
                    print("Sampling Progress:", checksampling, "/", self.samplecount, "Samples |",
                          "{:.2%}".format(checksampling / int(self.samplecount)))
                    # polling frequency set via sleep time
                    time.sleep(0.1)
                self.port.write("DATA:REMove? %s" % self.samplecount)

            self.samplingdata = [float(i) for i in self.port.read().split(',')]

            # generate linear time list with parameters "startpoint", "endpoint", "amount of steps" based on sampling parameters
            self.timecode = np.linspace(0, (float(self.samplecount) - 1) * float(self.samplingtime),
                                        len(self.samplingdata), endpoint=True, dtype=float).tolist()

            return [self.timecode] + [self.samplingdata]

        else:
            # here we read the response from the "READ?" request in 'measure' for single measurements
            answer = self.port.read()
            return [float(answer)]

    def get_model(self) -> str:
        """Returns the device model, such as 34410A, 34411A, etc.

        idn string can be like '34410A,MY12345678,2.35-2.35-0.09-46-09' or 'HEWLETT-PACKARD,34401A,0,11-1-1'
        """
        idn = self.port.query("*IDN?")
        match = re.search(r"344\d{2}A", idn)
        if match:
            return match.group(0)
        else:
            return "Unknown Model"
