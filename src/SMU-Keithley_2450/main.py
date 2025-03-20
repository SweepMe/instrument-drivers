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
# * Instrument: Keithley 2450

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug


class Device(EmptyDevice):

    def __init__(self):

        super().__init__()

        self.shortname = "Keithley 2450"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["USB", "GPIB"]
        self.port_properties = {"timeout": 10}
        self.port_identifications = ["KEITHLEY INSTRUMENTS,MODEL 2450,"]

        self.is_power_on = False

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Front", "Rear"],
            "Speed": ["Fast", "Medium", "Slow"],
            "Range": ["Auto",
                      "Limited 10 nA",
                      "Limited 100 nA",
                      "Limited 1 µA",
                      "Limited 10 µA",
                      "Limited 100 µA",
                      "Limited 1 mA",
                      "Limited 10 mA",
                      "Limited 100 mA",
                      "Fixed 10 nA",
                      "Fixed 100 nA",
                      "Fixed 1 µA",
                      "Fixed 10 µA",
                      "Fixed 100 µA",
                      "Fixed 1 mA",
                      "Fixed 10 mA",
                      "Fixed 100 mA",
                      "Fixed 1 A"],
            "Average": 1,
            "Compliance": 100e-6,
            "4wire": False,
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.four_wire = parameter["4wire"]
        self.route_out = parameter["RouteOut"]
        self.source = parameter["SweepMode"]
        self.protection = parameter["Compliance"]
        self.speed = parameter["Speed"]
        self.range = parameter["Range"]
        self.average = int(parameter["Average"])

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        self.port.write("*LANG?")
        self.language = self.port.read()  # TSP, SCPI, SCPI2400
        # set language with *LANG SCPI, *LANG TSP, *LANG SCPI2400 and reboot, ask for language *LANG?

        if self.language == "SCPI":
            self.language = "SCPI2400"

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        if self.language == "SCPI2400":
            self.port.write("*IDN?")
            self.vendor, self.model, self.serialno, self.version = self.port.read().split(",")
            # print(self.vendor, self.model, self.serialno, self.version)
            # reset all values
            self.port.write("*rst")
            self.port.write("status:preset")
            self.port.write("*cls")

            self.port.write(":SYST:BEEP:STAT OFF")  # control-Beep off

            # self.port.write(":SYST:LFR 50")  # unused because not everyone has 50 Hz

        if self.language == "TSP":
            self.port.write("print(localnode.vendor)")
            self.vendor = self.port.read()
            self.port.write("print(localnode.model)")
            self.model = self.port.read()
            self.port.write("print(localnode.serialno)")
            self.serialno = self.port.read()
            self.port.write("print(localnode.version)")
            self.version = self.port.read()
            # print(self.vendor, self.model, self.serialno, self.version)

            self.port.write("smu.reset()")
            self.port.write("defbuffer1.clear()")  # clear the default buffer
            self.port.write("errorqueue.clear()")

            # self.port.write("localnode.linefreq = 50")  # unused because not everyone has 50 Hz

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        if self.language == "SCPI2400":

            if self.average > 1:
                self.port.write(":SENS:AVER:COUN %i" % self.average)
                self.port.write(":SENS:AVER:STAT ON")
                self.port.write(":SENS:AVER:TCON REP")
            else:
                self.port.write(":SENS:AVER:COUN 1")
                self.port.write(":SENS:AVER:STAT OFF")

        elif self.language == "TSP":

            if self.average > 1:
                self.port.write("smu.measure.filter.count = %i" % self.average)
                self.port.write("smu.measure.filter.enable = smu.ON")
                self.port.write("smu.measure.filter.type = smu.FILTER_REPEAT_AVG")
            else:
                self.port.write("smu.measure.filter.count = 1")
                self.port.write("smu.measure.filter.enable = smu.OFF")

        if self.source.startswith("Voltage"):
            self.source_volt()

        if self.source.startswith("Current"):
            self.source_curr()

        # Speed/Integration
        self.set_speed(self.speed)

        # 4 wire
        if self.four_wire:
            self.rsen_on()
        else:
            self.rsen_off()

        # Route out
        if self.route_out == "Front":
            self.route_front()

        if self.route_out == "Rear":
            self.route_rear()

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        self.rsen_off()
        self.route_front()

    def poweron(self) -> None:
        """Turn on the device when entering a sequencer branch if it was not already used in the previous branch."""
        if self.language == "SCPI2400":
            self.port.write("OUTP ON")

        elif self.language == "TSP":
            self.port.write("smu.source.output = smu.ON")

        self.is_power_on = True

    def poweroff(self) -> None:
        """Turn off the device when leaving a sequencer branch."""
        if hasattr(self, "language"):
            if self.language == "SCPI2400":
                self.port.write("OUTP OFF")

            elif self.language == "TSP":
                self.port.write("smu.source.output = smu.OFF")

        self.is_power_on = False

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.value = str(self.value)

        source = self.source[0:4].upper()  # VOLT or CURR
        if self.language == "SCPI2400":
            self.port.write(":SOUR:" + source + ":LEV %s" % self.value)

        elif self.language == "TSP":
            self.port.write("smu.source.level = %s" % self.value)

        # needed to trigger a measurement and thus to trigger the final output of the level
        # should be replaced by TSP command 'waitcomplete()' or SCPI '*OPC?' handling
        self.measure()
        self.call()

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        if self.language == "SCPI2400":
            self.port.write("READ?")

        elif self.language == "TSP":
            self.port.write("data = buffer.make(10)")
            self.port.write("smu.measure.read(data)")

            # way to directly trigger sending the reading:
            # self.port.write("print(smu.measure.read(data))")
            # print("Reading", self.port.read())

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        if self.language == "SCPI2400":
            answer = self.port.read().split(",")
            self.v, self.i = answer[0:2]

        elif self.language == "TSP":

            self.port.write("printbuffer(1, 1, data.readings, data.sourcevalues)")
            answer = self.port.read().split(",")

            if self.source.startswith("Voltage"):
                self.i, self.v = list(map(float, answer))
            elif self.source.startswith("Current"):
                self.v, self.i = list(map(float, answer))

        # large values indicate errors
        error_threshold_value = 1e20  # values larger than this indicate an error not a measurement value
        if self.v > error_threshold_value:
            self.v = float("nan")
            debug("Keithley2450: Unable to read voltage.")
        if self.i > error_threshold_value:
            self.i = float("nan")
            debug("Keithley2450: Unable to read current.")

        return [self.v, self.i]

    # Convenience functions start here

    @staticmethod
    def convert_unit_prefix(number_text: str) -> str:
        """This function converts a unit prefix such as n, µ or m to the scientific e notation."""
        number_text = (number_text.replace("f", "e-15")
                       .replace("p", "e-12")
                       .replace("n", "e-9")
                       .replace("µ", "e-6")
                       .replace("u", "e-6")
                       .replace("m", "e-3")
                       .replace("k", "e3")
                       .replace("M", "e6")
                       .replace("G", "e9"))

        return number_text

    # Functions that wrap communication commands start here #

    def route_front(self):

        # if self.language == "SCPI2400":
        #	 self.port.write("ROUT:TERM?")

        # if self.language == "TSP":
        #	 self.port.write("print(smu.measure.terminals)")
        #	 self.port.read()

        if self.is_power_on:
            self.poweroff()

        if hasattr(self, "language"):
            if self.language == "SCPI2400":
                self.port.write(":ROUT:TERM FRON")

            elif self.language == "TSP":
                self.port.write("smu.measure.terminals = smu.TERMINALS_FRONT")

    def route_rear(self):

        if self.is_power_on:
            self.poweroff()

        if self.language == "SCPI2400":
            self.port.write(":ROUT:TERM REAR")

        elif self.language == "TSP":
            self.port.write("smu.measure.terminals = smu.TERMINALS_REAR")

    def set_speed(self, speed):
        if speed == "Fast":
            self.nplc = 0.1
        if speed == "Medium":
            self.nplc = 1.0
        if speed == "Slow":
            self.nplc = 10.0

        if self.language == "SCPI2400":
            self.port.write(":SENS:CURR:DC:NPLC " + str(self.nplc))
            self.port.write(":SENS:VOLT:DC:NPLC " + str(self.nplc))
        elif self.language == "TSP":
            self.port.write("smu.measure.nplc = " + str(self.nplc))

    def source_volt(self):

        range_value = self.range
        range_value = range_value.replace("Limited", "")
        range_value = range_value.replace("Fixed", "")
        range_value = range_value.replace(" ", "")  # removing spaces
        range_value = range_value.replace("A", "")  # removing the Ampere unit
        range_value = self.convert_unit_prefix(range_value)  # convert magnitudes to float

        if self.language == "SCPI2400":
            self.port.write(":SOUR:FUNC VOLT")
            # sourcemode = Voltage
            self.port.write(":SOUR:VOLT:MODE FIX")
            # sourcemode fix
            self.port.write(':SENS:FUNC "CURR"')
            # measurement mode
            self.port.write(":SENS:CURR:PROT " + self.protection)
            # Protection with Imax
            # self.port.write(":SOUR:VOLT:READ:BACK ON")  # does not work and leads to error???

            if "Auto" in self.range:  # Full auto-ranging
                self.port.write(":SENS:CURR:RANG:AUTO ON")
                # self.port.write("SENSe:CURRent:RANGe:AUTO:LLIMit DEF")  # does not work
            elif "Limited" in self.range:  # Limited auto-ranging
                self.port.write(":SENS:CURR:RANG:AUTO ON")
                self.port.write("SENSe:CURRent:RANGe:AUTO:LLIMit %s" % range_value)
            elif "Fixed" in self.range:  # Fixed range
                self.port.write(":SENS:CURR:RANG:AUTO OFF")
                self.port.write(":SENS:CURR:RANG " + range_value)

        elif self.language == "TSP":
            self.port.write("smu.source.func = smu.FUNC_DC_VOLTAGE")
            self.port.write("smu.measure.func = smu.FUNC_DC_CURRENT")
            self.port.write("smu.source.autorange = smu.ON")  # for voltage range
            self.port.write("smu.source.ilimit.level = " + self.protection)

            if "Auto" in self.range:  # Full auto-ranging
                self.port.write("smu.measure.autorange = smu.ON")
                # self.port.write("smu.measure.lowrange = lowRange")  # does not work
            elif "Limited" in self.range:  # Limited auto-ranging
                self.port.write("smu.measure.autorange = smu.ON")
                self.port.write("smu.measure.autorangelow = %s" % range_value)
            elif "Fixed" in self.range:  # Fixed range
                self.port.write("smu.measure.autorange = smu.OFF")
                self.port.write("smu.measure.range = " + range_value)

            self.port.write("smu.measure.autozero.once()")

    def source_curr(self):

        range_value = self.range
        range_value = range_value.replace("Limited", "")
        range_value = range_value.replace("Fixed", "")
        range_value = range_value.replace(" ", "")  # removing spaces
        range_value = range_value.replace("A", "")  # removing the Ampere unit

        range_value = self.convert_unit_prefix(range_value)  # convert magnitudes to float

        if self.language == "SCPI2400":
            self.port.write(":SOUR:FUNC CURR")
            # sourcemode = Voltage
            self.port.write(":SOUR:CURR:MODE FIX")
            # sourcemode fix
            self.port.write(':SENS:FUNC "VOLT"')
            # measurement mode
            self.port.write(":SENS:VOLT:PROT " + self.protection)
            # Protection with Imax
            self.port.write(":SENS:VOLT:RANG:AUTO ON")
            # Autorange for voltage measurement
            # self.port.write(":SOUR:CURR:READ:BACK ON")  ## does not work and leads to error???
            # Read the source value again

            if self.range == "Auto":  # Auto-ranging
                self.port.write(":SOUR:CURR:RANG:AUTO ON")
            elif "Limited" in self.range:
                self.port.write(":SOUR:CURR:RANG:AUTO ON")
            elif "Fixed" in self.range:
                self.port.write(":SOUR:CURR:RANG:AUTO OFF")
                self.port.write(":SOUR:CURR:RANG %s" % range_value)

        elif self.language == "TSP":
            self.port.write("smu.source.func = smu.FUNC_DC_CURRENT")
            self.port.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
            self.port.write("smu.source.vlimit.level = " + self.protection)
            self.port.write("smu.measure.autozero.once()")

            if self.range == "Auto":  # Auto-ranging
                self.port.write("smu.source.autorange = smu.ON")
            elif "Limited" in self.range:
                self.port.write("smu.source.autorange = smu.ON")
            elif "Fixed" in self.range:
                self.port.write("smu.source.autorange = smu.OFF")
                self.port.write("smu.source.range = %s" % range_value)

    def rsen_on(self):
        if self.language == "SCPI2400":
            self.port.write(":SYST:RSEN ON")
        elif self.language == "TSP":
            self.port.write("smu.measure.sense = smu.SENSE_4WIRE")

    def rsen_off(self):

        if hasattr(self, "language"):
            if self.language == "SCPI2400":
                self.port.write(":SYST:RSEN OFF")
            elif self.language == "TSP":
                self.port.write("smu.measure.sense = smu.SENSE_2WIRE")

    def output_mode(self):
        if self.language == "SCPI2400":
            # To set the output-off state to normal,
            self.port.write(":OUTP:SMOD NORM")
            # To set the output-off state to zero
            # self.port.write(":OUTP:SMOD ZERO")
            # To set the output-off state to high impedance
            # self.port.write(":OUTP:SMOD HIMP")
            # To set the output-off state to guard
            # self.port.write(":OUTP:SMOD GUAR")

        elif self.language == "TSP":
            # To set the output-off state to normal,
            self.port.write("smu.source.offmode = smu.OFFMODE_NORMAL")
            # To set the output-off state to zero
            # self.port.write("smu.source.offmode = smu.OFFMODE_ZERO")
            # To set the output-off state to high impedance
            # self.port.write("smu.source.offmode = smu.OFFMODE_HIGHZ")
            # To set the output-off state to guard
            # self.port.write("smu.source.offmode = smu.OFFMODE_GUARD")
