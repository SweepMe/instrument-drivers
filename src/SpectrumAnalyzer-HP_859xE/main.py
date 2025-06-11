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
# * Module: SpectrumAnalyzer
# * Instrument: HP 859xE


import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for HP 859xE Spectrum Analyzer."""
    description = """<p><strong>HP 859xE Spectrum Analyzer driver.</strong></p></p>
                     <p>Might work for 856xA, 856xE and 859xA instruments as well, but untested.</p>
                     <p>Resolution Bandwidths of 200Hz, 9kHz and 120kHz for EMI measurements only.</p>
                    """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "HP859xE"

        self.variables = ["Frequency", "Power"]
        self.units = ["Hz", "dBm"]

        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            "timeout": 100, # required for very slow sweeps
        }

        # dictionary for available resolution bandwidths;
        # options below 1kHz require HP "Option 130" to be installed in the operated instrument
        self.rbws = {
            "Auto": "AUTO",
            "30 Hz (OPTION 130)": "30HZ",
            "100 Hz (OPTION 130)": "100HZ",
            "200 Hz (for EMI@200Hz FRQ only)": "200HZ",
            "300 Hz (OPTION 130 or uncalibrated w/o)": "300HZ",
            "1 kHz": "1KHZ",
            "3 kHz": "3KHZ",
            "9 kHz (for EMI@9kHz FRQ only)": "9KHZ",
            "10 kHz": "10KHZ",
            "30 kHz": "30KHZ",
            "100 kHz": "100KHZ",
            "120 kHz (for EMI@120kHz FRQ only)": "120KHZ",
            "300 kHz": "300KHZ",
            "1 MHz": "1MHZ",
            "3 MHz": "3MHZ",
            "5 MHz (uncalibrated)": "5MHZ",
        }

        # dictionary for available video bandwidths;
        # options below 30Hz require HP "Option 130" to be installed in the operated instrument
        self.vbws = {
            "Auto": "AUTO",
            "1 Hz (OPTION 130)": "1HZ",
            "30 Hz": "30HZ",
            "100 Hz": "100HZ",
            "300 Hz": "300HZ",
            "1 kHz": "1KHZ",
            "3 kHz": "3KHZ",
            "10 kHz": "10KHZ",
            "30 kHz": "30KHZ",
            "100 kHz": "100KHZ",
            "300 kHz": "300KHZ",
            "1 MHz": "1MHZ",
            "3 MHz": "3MHZ",
        }

        # Trace Modes
        self.trace_modes = [
            "Current",
            "Max hold",
            "Min hold",
            #"Average" # currently not implemented
        ]

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            # Center/Min Frequency label
            "Frequency label 1": ["Center frequency in Hz:", "Min frequency in Hz:"],
            # Center/Min Frequency input
            "Frequency value 1": "900E06",
            # Span/Max Frequency label
            "Frequency label 2": ["Frequency span in Hz:", "Max frequency in Hz:"],
            # Span/Max Frequency input
            "Frequency value 2": "1.8E09",
            # Reference level in dBm
            "Reference level in dBm": 0.00,
            # Resolution bandwidth options from the dictionary
            "Resolution bandwidth": list(self.rbws.keys()),
            # Video bandwidth options from the dictionary
            "Video bandwidth": list(self.vbws.keys()),
            # Video averaging to localise small peaks near the noise level
            "Video averaging": False,
            # Normal sweep record, max hold or min hold
            "Trace mode": self.trace_modes,
            # definition by time disabled as this can lead to interrupted sweeps even for the first sweep when using very small RBW which require a long sweep time
            #"Trace mode integration type": ["Repetitions:", "Hold time in s:"],
            # the amount of single sweeps to use for finding the maximum values
            "Trace mode integration": 10,
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        # store the frequency values into variables
        self.fv1 = "{:.9}".format(parameter["Frequency value 1"])
        self.fv2 = "{:.9}".format(parameter["Frequency value 2"])

        # check for valid selected input frequency mode combinations
        if parameter["Frequency label 1"] == "Center frequency in Hz:" and parameter["Frequency label 2"] != "Frequency span in Hz:":
            msg = "Input with Center frequency requires second frequency to be entered as Span"
            raise Exception(msg)
        if parameter["Frequency label 1"] == "Min frequency in Hz:" and parameter["Frequency label 2"] != "Max frequency in Hz:":
            msg = "Input with Min frequency requires second frequency to be entered as Max"
            raise Exception(msg)

        # recorded spectrum will be defined by two SCPI commands, either setting start & stop frequencies or center & span.
        # this section creates the required two commands as a string, depending on what input format is chosen
        if parameter["Frequency label 1"] == "Center frequency in Hz:":
            #use center frequency command and floating point value with 9 trailing numbers to allow resolution down to 1 Hz within the GHz range
            self.setup_cmd_a = "CF" + self.fv1 +"HZ"
        else:
            #use start frequency command and floating point value with 9 trailing numbers to allow resolution down to 1 Hz within the GHz range
            self.setup_cmd_a = "FA" + self.fv1 +"HZ"
        if parameter["Frequency label 2"] == "Frequency span in Hz:":
            self.setup_cmd_b = "SP" + self.fv2 +"HZ"
        else:
            #use start frequency command and floating point value with 9 trailing numbers to allow resolution down to 1 Hz within the GHz range
            self.setup_cmd_b = "FB" + self.fv2 +"HZ"

        self.reflev = "{:.3}".format(parameter["Reference level in dBm"])
        self.rbw = parameter["Resolution bandwidth"]
        self.vbw = parameter["Video bandwidth"]
        self.vavg = bool(parameter["Video averaging"])
        self.trace_mode = parameter["Trace mode"]
        self.repetitions = int(parameter["Trace mode integration"])

        self.port_string = parameter["Port"]

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # erase TRACE A; will also remove max/min hold function if previously enabled
        self.port.write("BLANK TRA")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # if setup_cmd_a starts with "CF" it means frequencies were entered as Center and Span and a frequency array from center-span/2 to center+span/2 with 401 steps is created
        if self.setup_cmd_a.startswith("CF"):
            self.frequencies = np.linspace(float(self.fv1) - float(self.fv2)/2, float(self.fv1) + float(self.fv2)/2, 401)
        # if setup_cmd_a does not start with "CF" it means frequencies were entered as start and stop frequencies and a frequency array from start to stop with 401 steps is created
        else:
            self.frequencies = np.linspace(float(self.fv1), float(self.fv2), 401)

        # setup Center or Start frequency
        self.port.write(self.setup_cmd_a)

        # setup Span or Stop frequency
        self.port.write(self.setup_cmd_b)

        # setting resolution bandwidth
        self.port.write("RB %s" % self.rbws[self.rbw])

        # setting video bandwidth
        self.port.write("VB %s" % self.vbws[self.vbw])

        # enable/disable video average function
        if self.vavg:
            self.port.write("VAVG ON")
        else:
            self.port.write("VAVG OFF")

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        if self.vavg:
            # disable video averaging if it was enabled before
            self.port.write("VAVG OFF")

        # clears trace a to c, disabling max and min hold functions
        self.port.write("BLANK TRA")
        # makes sure Trace A is the active one
        self.port.write("CLRW TRA")
        # return to continuous sweep upon exit
        self.port.write("CONTS")

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        # set to single sweep
        self.port.write("SNGLS")

        # in case the standard acquisition mode "Current" is used, we ignore the repetitions set via GUI
        if self.trace_mode == "Current":
            # makes sure Trace A is the active one
            self.port.write("CLRW TRA")
            # record sweep
            self.port.write("TS")

        # enable Max/Min Hold function and run multiple aquisitions if set via GUI
        if self.trace_mode == "Max hold":
            # makes sure Trace A is the active one
            self.port.write("CLRW TRA")
            # maximum hold for Trace A
            self.port.write("MXMH TRA")
            for n in range (self.repetitions):
                # record sweep
                self.port.write("TS")

        if self.trace_mode == "Min hold":
            # makes sure Trace A is the active one
            self.port.write("CLRW TRA")
            # maximum hold for Trace A
            self.port.write("MINH TRA")
            for n in range (self.repetitions):
                 # record sweep
                self.port.write("TS")

    def read_result(self) -> None:
        """Read the measured data from a buffer that was requested during 'request_result'."""
        # transfer Trace A in 16bit
        self.port.write("TRA?")
        # retrieves data points from the instrument which are separated by a comma
        try:
            self.data = self.port.read().split(",")
        except Exception as e:
            print("Error reading data from the instrument:", e)
            self.data = []

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.frequencies] + [self.data]
