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
# * Module: Scope
# * Instrument: Rohde&Schwarz RTA

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Device class for the Rohde&Schwarz RTA Oscilloscope."""

    def __init__(self) -> None:
        """Initialize the Device Class."""
        EmptyDevice.__init__(self)

        self.shortname = "RTA"

        # Communication Parameters
        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP", "USB"]
        self.port_properties = {
            "timeout": 2.0,
        }

        # SweepMe Parameters
        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        # Measurement Parameters
        self.sweepmode: str = "None"
        self.commands = {
            "Channel 1": "CHAN1",
            "Channel 2": "CHAN2",
            "Channel 3": "CHAN3",
            "Channel 4": "CHAN4",
            "External": "EXT",
            "Serial bus": "SBUS",
            "Line": "LINE",
            "None": "NONE",
            "Rising": "POS",
            "Falling": "NEG",
        }

        self.couplings = {
            "DC 50 Ohm": "DC",
            "DC 1 MOhm": "DCLimit",
            "AC 1 MOhm": "AC",
        }

        self.max_time = 10.0
        self.data_format = "ASC"  # ASC | REAL,32 | INT,8 | INT,16

        # Trigger
        self.trigger_source: str = "As is"
        self.trigger_source_levels = {
            "Channel 1": "1",
            "Channel 2": "2",
            "Channel 3": "3",
            "Channel 4": "4",
            "External": "5",
        }
        self.trigger_coupling: str = "As is"
        self.trigger_slope: str = "As is"
        self.trigger_level: str = "As is"

        # Timing
        self.time_range: str = "As is"
        self.time_range_value: float = 1e-3
        self.time_offset_value: float = 0.0
        self.time_values: np.ndarray = np.array([])

        self.acquisition_mode: str = "As is"
        self.average: str = "As is"
        self.sampling_rate_type: str = "As is"
        self.sampling_rate: str = "As is"

        # Channels
        self.channels: list = []
        self.channel_names: dict = {}
        self.channel_ranges: dict = {}
        self.channel_offsets: dict = {}
        self.channel_couplings: dict = {}
        self.channel_impedances: dict = {}
        self.channel_data: list = []

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard SweepMe GUI parameters."""
        gui_parameter = {
            "SweepMode": ["None", "Time range in s", "Time scale in s/div", "Time offset in s"],
            "TriggerSlope": ["As is", "Rising", "Falling"],
            "TriggerSource": [
                "As is",
                "Channel 1",
                "Channel 2",
                "Channel 3",
                "Channel 4",
                "External",
                "Line",
                "Serial bus",
                "Software",
            ],
            "TriggerCoupling": ["As is", "DC", "DCLimit", "AC"],
            "TriggerLevel": "As is",
            "TimeRange": ["As is", "Time range in s:", "Time scale in s/div:"],
            "TimeRangeValue": 1e-3,
            "TimeOffsetValue": 0.0,
            "Acquisition": ["As is", "Continuous", "Single"],
            "Average": ["As is", "1", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
            "SamplingRateType": [
                "As is sampling rate",
                "Auto sampling rate",
                "Sampling rate in Sa/s:",
                "Sample resolution in s:",
                "Samples per time range:",
            ],
            "SamplingRate": "As is",
        }

        for i in np.arange(4) + 1:
            gui_parameter["Channel%i" % i] = False
            gui_parameter["Channel%i_Name" % i] = "Ch%i" % i
            gui_parameter["Channel%i_Range" % i] = ["As is", "1"]
            gui_parameter["Channel%i_Offset" % i] = "As is"
            gui_parameter["Channel%i_Impedance" % i] = ["As is", "50 Ohm"]
            gui_parameter["Channel%i_Coupling" % i] = ["As is", *list(self.couplings.keys())]

        return gui_parameter

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle the SweepMe GUI parameters."""
        self.sweepmode = parameter["SweepMode"]

        self.trigger_source = parameter["TriggerSource"]
        self.trigger_coupling = parameter["TriggerCoupling"]
        self.trigger_slope = parameter["TriggerSlope"]
        self.trigger_level = parameter["TriggerLevel"]

        self.time_range = parameter["TimeRange"]
        self.time_range_value = parameter["TimeRangeValue"]
        self.time_offset_value = parameter["TimeOffsetValue"]

        self.acquisition_mode = ["Acquisition"]
        self.average = parameter["Average"]
        self.sampling_rate_type = parameter["SamplingRateType"]
        self.sampling_rate = parameter["SamplingRate"]

        # Adding the selected channels
        self.channels = []
        for i in range(1, 5):
            if parameter["Channel%i" % i]:
                self.channels.append(i)

        self.channel_names = {}
        self.channel_ranges = {}
        self.channel_offsets = {}
        self.channel_couplings = {}
        self.channel_impedances = {}

        for i in self.channels:
            self.channel_names[i] = parameter[f"Channel{i}_Name"]
            self.channel_ranges[i] = parameter[f"Channel{i}_Range"]
            self.channel_offsets[i] = parameter[f"Channel{i}_Offset"]
            self.channel_couplings[i] = parameter[f"Channel{i}_Coupling"]
            self.channel_impedances[i] = parameter[f"Channel{i}_Impedance"]

            self.variables.append(self.commands[f"Channel {i}"] + " " + parameter[f"Channel{i}_Name"])
            self.units.append("V")
            self.plottype.append(True)
            self.savetype.append(True)

    def initialize(self) -> None:
        """Initialize the device."""
        self.port.write("*CLS")
        # do not use "SYST:PRES" as it will destroy all settings which is in conflict with using 'As is'

        self.port.write(":FORM:DATA %s" % self.data_format)  # set the data format

        if self.data_format == "INT,16":
            self.port.write(
                ":FORM:BORD LSBF",
            )  # set if data sequence, only import for high-definition mode, LSBFirst | MSBFirst, default = LSBF

        self.port.write("SYST:DISP:UPD ON")  # display can be switched on or off
        self.port.write("SYST:KLOC ON")  # locks the local control during measurement

        if self.time_range != "As is":
            if self.time_range_value == "":
                msg = "Empty time range. Please enter a number."
                raise ValueError(msg)

            if float(self.time_range_value) == 0.0:
                msg = "Time range cannot be zero. Please enter a positive number."
                raise ValueError(msg)

            if self.time_offset_value == "":
                msg = "Empty time offset. Please enter a number."
                raise ValueError(msg)

    def deinitialize(self) -> None:
        """Deinitialize the device."""
        self.port.write("SYST:KLOC OFF")  # unlocks the local control during measurement
        self.read_errors()  # read out the error queue

    def configure(self) -> None:
        """Configure the measurement."""
        self.set_time_range()
        self.set_trigger()

        # Modes
        # RUNContinous -> Starts the continuous acquisition, same like RUN
        # RUN -> Starts the continuous acquisition.
        # RUNSingle -> Starts a defined number of acquisition cycles. The number of cycles is set with ACQuire:COUNt.
        # SINGle -> Starts a defined number of acquisition cycles. The number of cycles is set with ACQuire:COUNt.
        # STOP -> Stops the running acquistion.

        if self.acquisition_mode == "Continuous":
            self.port.write("RUN")
        elif self.acquisition_mode == "Single":
            self.port.write("STOP")  # we stop any acquisition to perform a single run during measure

        if self.average != "As is":
            self.port.write("ACQ:COUN %s" % self.average)

        self.set_sample_rate()

        # here all channels that are not selected are switched off as they may be activated from the last run
        for channel in np.arange(4) + 1:
            if channel not in self.channels:
                self.set_channel_state(channel, False)

        # now we switch on and configure the channels that have to be used
        for channel in self.channels:
            self.configure_channel(channel)

        # let's make sure all previous commands are processed
        self.port.write("*OPC?")
        self.port.read()

    def set_time_range(self) -> None:
        """Set the time range."""
        if self.time_range != "As is":
            if self.time_range == "Time range in s:":
                self.port.write("TIM:RANG %s" % self.time_range_value)
            elif self.time_range == "Time scale in s/div:":
                self.port.write("TIM:SCAL %s" % self.time_range_value)

            self.port.write("TIM:HOR:POS %s" % self.time_offset_value)

    def set_trigger(self) -> None:
        """Set the trigger mode."""
        self.port.write("TRIG1:MODE NORM")  # measurement is only done if a trigger is received

        if self.trigger_source not in ("As is", "Software"):
            self.port.write("TRIG1:SOUR %s" % self.commands[self.trigger_source])

            if self.trigger_source in list(self.trigger_source_levels.keys()):
                if self.trigger_level != "" or self.trigger_level != "As is":
                    self.port.write(
                        f"TRIG1:LEV{self.trigger_source_levels[self.trigger_source]} {float(self.trigger_level):1.3e}",
                    )  # LEV{1-4} is the trigger level of the four channels

        if self.trigger_source.startswith("External"):
            self.port.write("TRIG1:TYEP ANED")  # ANalogEdge

            if self.trigger_coupling != "As is":
                self.port.write("TRIG1:ANED:COUP %s" % self.trigger_coupling)  # AC or DC

            if self.trigger_slope != "As is":
                self.port.write("TRIG1:ANED:SLOP %s" % self.commands[self.trigger_slope])  # POS or NEG

        else:
            self.port.write("TRIG1:TYPE EDGE")

            if self.trigger_slope != "As is":
                self.port.write("TRIG1:EDGE:SLOP %s" % self.commands[self.trigger_slope])

    def configure_channel(self, channel: int) -> None:
        """Set the channel properties.

        All channel related properties:
            CHANnel<m>:STATe
            CHANnel<m>:COUPling
            CHANnel<m>:GND
            CHANnel<m>:SCALe
            CHANnel<m>:RANGe
            CHANnel<m>:POSition
            CHANnel<m>:OFFSet
            CHANnel<m>:INVert
            CHANnel<m>:BANDwidth
            CHANnel<m>:CPLing
            CHANnel<m>:IMPedance
            CHANnel<m>:OVERload
        """
        self.port.write("CHAN%i:TYPE SAMP" % channel)
        self.port.write("CHAN%i:STAT ON" % channel)

        # Range
        channel_range = self.channel_ranges[channel]
        if channel_range != "As is":
            self.set_channel_range(channel, float(channel_range))

        # Position
        channel_offset = self.channel_offsets[channel]
        if channel_offset != "As is":
            self.set_channel_offset(channel, float(channel_offset))

        # Coupling
        channel_coupling = self.channel_couplings[channel]
        if channel_coupling != "As is":
            self.set_channel_coupling(channel, channel_coupling)

        # Impedance can only be set if an active probe is connected. Otherwise, 1 MOhm is automatically set.
        if self.channel_impedances[channel] == "50 Ohm":
            # Use the DC coupling for 50 Ohm impedance. Other modes (DCLimit, ACLimit, GND) are untested.
            self.port.write(f"CHANnel{channel}:COUPling DC")

    def set_channel_state(self, channel: int, state: bool = False) -> None:
        """Switch on or off the channel."""
        if state:
            self.port.write(f"CHAN{channel}:STAT ON")
        else:
            self.port.write(f"CHAN{channel}:STAT OFF")

    def set_channel_range(self, channel: int, range_value: float) -> None:
        """Set the range of the channel."""
        self.port.write("CHAN%i:RANG %s" % (channel, range_value))

    def set_channel_offset(self, channel: int, offset_value: float) -> None:
        """Set the offset of the channel."""
        self.port.write("CHAN%i:POS %s" % (channel, offset_value))

    def set_channel_coupling(self, channel: int, coupling: str) -> None:
        """Set the coupling of the channel."""
        self.port.write("CHAN%i:COUP %s" % (channel, self.couplings[coupling]))

    def set_sample_rate(self) -> None:
        """Set the sample rate."""
        if self.sampling_rate_type == "As is sampling rate":
            return

        if self.sampling_rate_type == "Auto sampling rate":
            self.port.write("ACQ:POIN:AUTO RES")  # possible options RESolution | RECLength

        elif self.sampling_rate != "As is":
            if self.sampling_rate_type == "Sampling rate in Sa/s:":
                self.port.write("ACQ:SRR %s" % self.sampling_rate)

            elif self.sampling_rate_type == "Samples per time range:":
                self.port.write("ACQ:POIN:VAL %s" % self.sampling_rate)

            elif self.sampling_rate_type == "Sample resolution in s:":
                self.port.write("ACQ:RES %s" % self.sampling_rate)

            elif self.sampling_rate_type == "Samples per time per div:":
                pass

    def apply(self) -> None:
        """Apply the sweep value."""
        if self.sweepmode != "None":
            value = float(self.value)

            if self.sweepmode == "Time range in s":
                self.port.write("TIM:RANG %s" % value)

            elif self.sweepmode == "Time scale in s/div":
                self.port.write("TIM:SCAL %s" % value)

            elif self.sweepmode == "Time offset in s":
                self.port.write("TIM:POS %s" % value)

    def measure(self) -> None:
        """Start the measurement."""
        # resets the averaging immediately, done to collect fresh data
        self.port.write("ACQ:ARES:IMM")

        if self.acquisition_mode == "Single":
            self.port.write("SING")

        if self.trigger_source == "Software":
            self.port.write("TRIG1:FORC")  # we do a Software triggering

        self.port.write("*OPC?")
        self.port.read()

    def request_result(self):
        """Not used at the moment, but would be nice to split requesting and reading the results."""

    def read_result(self) -> None:
        """Read the measurement result."""
        self.channel_data = []

        for i in self.channels:
            self.port.write("CHAN%i:DATA?" % i)
            answer = self.port.read()
            answer = answer.split(",")

            data = np.array(answer, dtype=float)

            self.channel_data.append(data)

        self.port.write("CHAN%i:DATA:HEAD?" % self.channels[0])
        time_header_data = np.array(self.port.read().split(","))
        self.time_values = np.linspace(float(time_header_data[0]), float(time_header_data[1]), int(time_header_data[2]))

    def call(self) -> list:
        """Return the measurement result."""
        return [self.time_values, *self.channel_data]

    def read_errors(self) -> None:
        """Reads out all errors from the error queue and prints them to the debug."""
        self.port.write("SYST:ERR:COUN?")
        err_count = self.port.read()
        if int(err_count) > 0:
            self.port.write("SYST:ERR:CODE:ALL?")
            answer = self.port.read()
            for err in answer.split(","):
                print("Scope R&S RTx error:", err)

    def get_identification(self) -> str:
        """Get the identification of the device."""
        self.port.write("*IDN?")
        return self.port.read()
