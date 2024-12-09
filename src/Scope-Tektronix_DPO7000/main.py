# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank Peter Hegarty (TU Dresden) for providing the initial version of this driver.

# SweepMe! driver
# * Module: Scope
# * Instrument: Tektronix DPO7000
from __future__ import annotations

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the Tektronix DPO7000 Oscilloscope."""

    description = """
        Most of the Scope module features are not yet supported and many properties must be set manually.
    """

    def __init__(self) -> None:
        """Initialize device and measurement parameters."""
        EmptyDevice.__init__(self)

        self.shortname = "DPO7000"

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]
        self.port_identifications = ["TEKTRONIX,DPO7354C*"]

        self.port_properties = {
            "timeout": 5.0,
            "delay": 1.0,
        }

        self.commands = {
            "Channel 1": "CH1",
            "Channel 2": "CH2",
            "Channel 3": "CH3",
            "Channel 4": "CH4",
            "External": "EXT",
            "Line": "LINE",
            "None": "NONE",
            "Rising": "POS",
            "Falling": "NEG",
        }

        # Measurement Parameters
        self.trigger_source: str = "As is"
        self.trigger_slope: str = "As is"
        self.trigger_level: float = 0

        self.timerange: str = "Time range in s"
        self.time_range_value: float = 5e-4
        self.time_offset_value: float = 0.0
        self.sampling_rate: int = int(1e7)

        self.average: str = "2"

        # Channel Properties
        self.channels = []
        self.channel_names = {}
        self.channel_ranges = {}
        self.channel_divs = {}
        self.channel_offsets = {}

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        gui_parameter = {
            "SweepMode": ["None"],
            "TriggerSlope": ["As is", "Rising", "Falling"],
            "TriggerSource": ["As is", "CH1", "CH2", "CH3", "CH4", "AUX", "LINE", "None"],
            # "TriggerCoupling": ["As is", "AC", "DC", "HF", "Auto level"],  # not yet implemented
            "TriggerLevel": 0,
            "TimeRange": ["Time range in s", "Time scale in s/div", "Record length"],
            "TimeRangeValue": 5e-4,
            "TimeOffsetValue": 0.0,
            "SamplingRate": int(1e7),
            # "Acquisition": ["Continuous", "Single"],
            # Average of 1 is not yet supported
            "Average": ["2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
            "VoltageRange": ["Voltage range in V"],
        }

        for i in range(1, 5):
            gui_parameter["Channel%i" % i] = i == 1
            gui_parameter["Channel%i_Name" % i] = "CH%i" % i
            gui_parameter["Channel%i_Range" % i] = [
                "1e-2",
                "2e-2",
                "5e-2",
                "1e-1",
                "2e-1",
                "5e-1",
                "1",
                "2",
                "5",
                "10",
                "20",
                "50",
            ]
            gui_parameter["Channel%i_Offset" % i] = 0.0

        return gui_parameter

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.trigger_source = parameter["TriggerSource"]
        # self.triggercoupling = parameter["TriggerCoupling"]  # not yet implemented
        self.trigger_slope = parameter["TriggerSlope"]
        self.trigger_level = parameter["TriggerLevel"]

        self.timerange = parameter["TimeRange"]
        self.time_range_value = float(parameter["TimeRangeValue"])
        self.time_offset_value = parameter["TimeOffsetValue"]
        self.sampling_rate = parameter["SamplingRate"]

        self.average = parameter["Average"]

        self.channels = []
        self.channel_names = {}
        self.channel_ranges = {}
        self.channel_divs = {}
        self.channel_offsets = {}

        for i in range(1, 5):
            if parameter["Channel%i" % i]:
                self.channels.append(i)

                self.variables.append(self.commands["Channel %i" % i] + " " + parameter["Channel%i_Name" % i])
                self.units.append("V")
                self.plottype.append(True)
                self.savetype.append(True)

                self.channel_names[i] = parameter["Channel%i_Name" % i]
                self.channel_ranges[i] = float(parameter["Channel%i_Range" % i])
                self.channel_divs[i] = self.channel_ranges[i] / 10
                self.channel_offsets[i] = parameter["Channel%i_Offset" % i]

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # This driver does not use Reset yet so that user can do measurements with changing options manually
        # self.port.write("*RST")

        if len(self.channels) == 0:
            msg = "Please select at least one channel to be read out"
            raise Exception(msg)

        # self.port.write("*IDN?")  # Query device name
        # print("ID Checkup")
        # print(self.port.read())

        self.port.write("ACQ:STOPAfter SEQ")  # single sequence measurement

        self.port.write("DAT:STOP 999999999999")  # ensure that the entire waveform is recorded
        self.port.write("DAT:ENCdg ASCii")  # sets encoding

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # Acquisition
        self.port.write("ACQuire:MODe AVE")  # use acquisition mode "averaged"
        self.port.write("ACQ:NUMAV %s" % self.average)  # set averages

        self.configure_trigger()
        self.configure_time_range()

        self.port.write("HORizontal:MODE:SAMPLERate %s" % self.sampling_rate)  # set sampling rate in 1/s

        # Channel properties
        for i in self.channels:
            self.port.write("SEL:CH%s ON" % i)  # turn on selected channels
            self.port.write("CH%s:SCAle %s; :CH%s:OFFSet %s" % (i, self.channel_divs[i], i, self.channel_offsets[i]))

    def configure_trigger(self) -> None:
        """Set trigger settings, first trigger level and then slope."""
        # Trigger
        # set the trigger settings, first the trigger level and then the slope
        if self.trigger_source in ("As is", "None"):
            pass
        else:
            self.port.write("TRIGger:A:EDGE:SOUrce %s" % self.trigger_source)

        self.port.write("TRIGger:A:EDGE:SOUrce?")
        trigger_channel = self.port.read()

        self.port.write("TRIGger:A:LEVel:%s %s" % (trigger_channel, self.trigger_level))  # set trigger level

        if self.trigger_level == 0:  # if no specific trigger level desired,
            self.port.write("TRIGger:A SETLevel;TRIGger:B SETLevel")  # sets the trigger level at 50%

        if self.trigger_slope == "As is":  # set trigger slope
            pass
        elif self.trigger_slope == "Rising":
            self.port.write("TRIG:A:EDGE:SLOpe RISe;TRIG:B:EDGE:SLOpe RISe")
        elif self.trigger_slope == "Falling":
            self.port.write("TRIG:A:EDGE:SLOpe FALL;TRIG:B:EDGE:SLOpe FALL")

    def configure_time_range(self) -> None:
        """Configure the time range of the device.

        The device can operate in three different horizontal scaling modes. As the sampling rate is a parameter set by
        the user, one of these modes will be disregarded. The user can then decide whether to define the time range/time
        per division, or the total record length, which will cause the device to switch between auto and manual mode.
        This is done by checking if the parameter TimeRange is set to Record length, and then setting the horizontal
        scaling accordingly.
        """
        if self.timerange != "Record length":  # Entering into auto mode
            self.port.write("HORizontal:MODE AUTO")
            if self.timerange == "Time range in s":
                self.divisions = self.time_range_value / 10.0  # only accepts entries for the time scale
            elif self.timerange == "Time scale in s/div":
                self.divisions = self.time_range_value

            self.port.write("HORizontal:MODE:SCAle %s" % self.divisions)  # set time scale

        elif self.timerange == "Record length":
            # set manual mode + RL
            self.port.write("HORizontal:MODE:MANual;HORizontal:MODE:RECOrdlength %s" % self.time_range_value)

    def apply(self):
        pass

    def measure(self) -> None:
        """Trigger the acquisition of new data."""
        # ready acquisition state
        self.port.write("ACQ:STATE RUN")

        if self.average in ["As is", "Not supported"]:
            # avoid an infinite loop
            msg = "Please select a correct number of averages to avoid an unending loop."
            raise Exception(msg)

        # Manual averaging
        # TODO: Handle > 10 averages
        n = 0
        while True:  # evaluation only after correct number of averages performed
            n += 1
            self.port.write("ACQ:NUMACQ?")
            answer = self.port.read()

            if int(answer) >= int(self.average):
                break
            else:
                print("Averaging...", n, answer)
            if n > 10:  # Here, the while loop stops after 10 iterations which needs improvement
                msg = (
                    "Unable to achieve acquisitions for averaging. "
                    "Please contact support@sweep-me.net if you need an improved driver."
                )
                raise Exception(msg)

        self.numbers = np.array(self.channels)  # array of channel numbers
        slot = 0  # run variable for data sorting
        self.channel_data = self.numbers.reshape(1, -1)

        for i in self.channels:
            self.port.write("DAT:SOU CH%i" % i)  # select channel to be read
            self.port.write("WFMOutpre?")  # query the preamble for relevant parameters

            # First step is to obtain all relevant header data and generate an array containing the time value
            # for each data point. The header is queried using WFMO? above, and then split into the relevant entries
            # which are then accessed for the later necessary factors and offsets.

            preamble = self.port.read().split(";")  # split the header
            # print(Preamble)

            # number of time values + units
            timesteps, time_unit = int(preamble[5].split(",")[4].split()[0]), preamble[-9]

            if slot == 0:  # only for first measurement
                record_length = int(preamble[-11])  # number of data points
                channels = len(self.channels)  # number of measured channels
                self.voltages = np.zeros((record_length, channels))  # generate array of correct size for channels+data

            # The next section gathers the horizontal and vertical scaling and offset
            # to later calculate the data values from
            # the digitization levels of the oscilloscope.
            x_step, x_offset, x_zero = float(preamble[-8]), float(preamble[-7]), float(preamble[-6])
            y_mult, y_offset, y_zero, y_unit = (
                float(preamble[-4]),
                float(preamble[-2]),
                float(preamble[-3]),
                preamble[-5],
            )

            self.Times = (np.arange(timesteps) - x_zero) * x_step  # generate time array

            self.port.write("CURVe?")  # queries the waveform from the oscilloscope
            curve_points = self.port.read().split(",")  # turn str object from query into list

            data = []
            for i in np.arange(len(curve_points)):
                data.append(int(curve_points[i]))  # sort the values as data
            data = np.array(data)  # convert list to data array

            volt_data = (data - (y_offset + y_zero)) * y_mult  # calculates correct voltages

            self.voltages[:, slot] = volt_data  # inputs voltage data for channel i into correct column of data array
            slot += 1  # set correct column for next channel

    def call(self) -> list[float]:
        """Return the measured values."""
        return [self.Times] + [self.voltages[:, i] for i in range(self.voltages.shape[1])]
