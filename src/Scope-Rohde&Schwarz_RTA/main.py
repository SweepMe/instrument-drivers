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


from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "RTB"

        self.port_manager = True
        self.port_types = ["GPIB", "TCPIP"]

        self.port_properties = {
            "timeout": 2.0,
        }

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

        self.trigger_source_levels = {
            "Channel 1": "1",
            "Channel 2": "2",
            "Channel 3": "3",
            "Channel 4": "4",
            "External": "5",
        }

        self.couplings = {
            "DC 50 Ohm": "DC",
            "DC 1 MOhm": "DCLimit",
            "AC 1 MOhm": "AC",
        }

        self.max_time = 10.0
        self.data_format = "ASC"  # ASC | REAL,32 | INT,8 | INT,16

    def set_GUIparameter(self):
        GUIparameter = {
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
            GUIparameter["Channel%i" % i] = False
            GUIparameter["Channel%i_Name" % i] = "Ch%i" % i
            GUIparameter["Channel%i_Range" % i] = ["As is", "1"]
            GUIparameter["Channel%i_Offset" % i] = "As is"
            GUIparameter["Channel%i_Coupling" % i] = ["As is", *list(self.couplings.keys())]

        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        self.sweepmode = parameter["SweepMode"]

        self.triggersource = parameter["TriggerSource"]
        self.triggercoupling = parameter["TriggerCoupling"]
        self.triggerslope = parameter["TriggerSlope"]
        self.triggerlevel = parameter["TriggerLevel"]

        self.timerange = parameter["TimeRange"]
        self.timerangevalue = parameter["TimeRangeValue"]
        self.timeoffsetvalue = parameter["TimeOffsetValue"]

        self.acquisition_mode = ["Acquisition"]
        self.average = parameter["Average"]
        self.samplingratetype = parameter["SamplingRateType"]
        self.samplingrate = parameter["SamplingRate"]

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

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
            self.channel_names[i] = parameter["Channel%i_Name" % (i)]
            self.channel_ranges[i] = parameter["Channel%i_Range" % (i)]
            self.channel_offsets[i] = parameter["Channel%i_Offset" % (i)]
            self.channel_couplings[i] = parameter["Channel%i_Coupling" % (i)]

            self.variables.append(self.commands["Channel %i" % i] + " " + parameter["Channel%i_Name" % i])
            self.units.append("V")
            self.plottype.append(True)
            self.savetype.append(True)

    def initialize(self):
        self.port.write("*CLS")

        # dont' use "SYST:PRES" as it will destroy all settings which is in conflict with using 'As is'

        self.port.write("*IDN?")
        self.port.read()

        self.port.write(":FORM:DATA %s" % self.data_format)  # set the data format

        if self.data_format == "INT,16":
            self.port.write(
                ":FORM:BORD LSBF",
            )  # set if data sequence, only import for high-definition mode, LSBFirst | MSBFirst, default = LSBF

        self.port.write("SYST:DISP:UPD ON")  # display can be switched on or off
        self.port.write("SYST:KLOC ON")  # locks the local control during measurement

        if self.timerange != "As is":
            if self.timerangevalue == "":
                self.stop_measurement("Emtpy time range. Please enter a number.")
                return False

            if float(self.timerangevalue) == 0.0:
                self.stop_measurement("Time range cannot be zero. Please enter a positive number.")
                return False

            if self.timeoffsetvalue == "":
                self.stop_measurement("Empty time offset. Please enter a number.")
                return False
            return None
        return None

    def deinitialize(self):
        self.port.write("SYST:KLOC OFF")  # unlocks the local control during measurement
        self.read_errors()  # this functions reads out the error queue

    def configure(self):
        ########################## time ########################################################

        if self.timerange != "As is":
            if self.timerange == "Time range in s:":
                self.port.write("TIM:RANG %s" % self.timerangevalue)
            elif self.timerange == "Time scale in s/div:":
                self.port.write("TIM:SCAL %s" % self.timerangevalue)

            self.port.write("TIM:HOR:POS %s" % self.timeoffsetvalue)


        ########################## trigger #####################################################

        self.port.write("TRIG1:MODE NORM")  # measurement is only done if a trigger is received

        if self.triggersource != "As is" and self.triggersource != "Software":
            self.port.write("TRIG1:SOUR %s" % self.commands[self.triggersource])

            if self.triggersource in list(self.trigger_source_levels.keys()):
                if self.triggerlevel != "" or self.triggerlevel != "As is":
                    self.port.write(
                        f"TRIG1:LEV{self.trigger_source_levels[self.triggersource]} {float(self.triggerlevel):1.3e}",
                    )  # LEV{1-4} is the trigger level of the four channels

        if self.triggersource.startswith("External"):
            self.port.write("TRIG1:TYEP ANED")  # ANalogEdge

            if self.triggercoupling != "As is":
                self.port.write("TRIG1:ANED:COUP %s" % self.triggercoupling)  # AC or DC

            if self.triggerslope != "As is":
                self.port.write("TRIG1:ANED:SLOP %s" % self.commands[self.triggerslope])  # POS or NEG

        else:
            self.port.write("TRIG1:TYPE EDGE")

            if self.triggerslope != "As is":
                self.port.write("TRIG1:EDGE:SLOP %s" % self.commands[self.triggerslope])

        ########################## acquisition #####################################################

        ## Modes ##
        # RUNContinous -> Starts the continuous acquisition, same like RUN
        # RUN -> Starts the continuous acquisition.
        # RUNSingle -> Starts a defined number of acquisition cycles. The number of cycles is set with ACQuire:COUNt.
        # SINGle -> Starts a defined number of acquisition cycles. The number of cycles is set with ACQuire:COUNt.
        # STOP -> Stops the running acquistion.

        if self.acquisition_mode == "Continuous":
            self.port.write("RUN")
        elif self.acquisition_mode == "Single":
            self.port.write("STOP")  # we stop any acquistion to to perform a single run during measure

        if self.average != "As is":
            self.port.write("ACQ:COUN %s" % self.average)

        self.port.write("ACQ:COUN?")
        self.port.read()

        if self.samplingratetype != "As is sampling rate":
            if self.samplingratetype == "Auto sampling rate":
                self.port.write("ACQ:POIN:AUTO RES")  # possible options RESolution | RECLength

            else:
                if self.samplingrate != "As is":
                    if self.samplingratetype == "Sampling rate in Sa/s:":
                        self.port.write("ACQ:SRR %s" % self.samplingrate)

                    elif self.samplingratetype == "Samples per time range:":
                        self.port.write("ACQ:POIN:VAL %s" % self.samplingrate)

                    elif self.samplingratetype == "Sample resolution in s:":
                        self.port.write("ACQ:RES %s" % self.samplingrate)

                    elif self.samplingratetype == "Samples per time per div:":
                        pass

        # here all channels that are not selected are switched off as they may be activated from the last run
        for i in np.arange(4) + 1:
            if i not in self.channels:
                self.port.write("CHAN%i:STAT OFF" % i)

        # now we switch on the channels that have to be used
        for i in self.channels:
            self.port.write("CHAN%i:TYPE SAMP" % i)
            self.port.write("CHAN%i:STAT ON" % i)

            ## Range
            if self.channel_ranges[i] != "As is":
                range_value = float(self.channel_ranges[i])
                self.port.write("CHAN%i:RANG %s" % (i, range_value))

            ## Position
            if self.channel_offsets[i] != "As is":
                offset_value = float(self.channel_offsets[i])
                self.port.write("CHAN%i:POS %s" % (i, offset_value))

            ## Coupling
            if self.channel_couplings[i] != "As is":
                coupling_value = self.couplings[self.channel_couplings[i]]
                self.port.write("CHAN%i:COUP %s" % (i, coupling_value))

            ## Impedance
            # if self.channel_impedances[i] != "As is":

            ## All channel related properties
            # CHANnel<m>:STATe
            # CHANnel<m>:COUPling
            # CHANnel<m>:GND
            # CHANnel<m>:SCALe
            # CHANnel<m>:RANGe
            # CHANnel<m>:POSition
            # CHANnel<m>:OFFSet
            # CHANnel<m>:INVert
            # CHANnel<m>:BANDwidth
            # CHANnel<m>:CPLing
            # CHANnel<m>:IMPedance
            # CHANnel<m>:OVERload

        # let's make sure all previous commands are processed
        self.port.write("*OPC?")
        self.port.read()

    def apply(self):
        if self.sweepmode != "None":
            self.value = float(self.value)

            if self.sweepmode == "Time range in s":
                self.port.write("TIM:RANG %s" % self.value)

            elif self.sweepmode == "Time scale in s/div":
                self.port.write("TIM:SCAL %s" % self.value)

            elif self.sweepmode == "Time offset in s":
                self.port.write("TIM:POS %s" % self.value)

    def measure(self):
        # resets the averaging immediately, done to collect fresh data
        self.port.write("ACQ:ARES:IMM")

        if self.acquisition_mode == "Single":
            self.port.write("SING")

        if self.triggersource == "Software":
            self.port.write("TRIG1:FORC")  # we do a Software triggering

        self.port.write("*OPC?")
        self.port.read()

    def request_result(self):
        pass
        # not used at the moment, but would be nice to split requesting and reading the results

    def read_result(self):
        self.channel_data = []

        for i in self.channels:
            data = []
            self.port.write("CHAN%i:DATA?" % i)
            answer = self.port.read()
            answer = answer.split(",")

            data = np.array(answer, dtype=np.float)

            self.channel_data.append(data)

        self.port.write("CHAN%i:DATA:HEAD?" % self.channels[0])
        Time_header_data = np.array(self.port.read().split(","))
        self.Time_values = np.linspace(float(Time_header_data[0]), float(Time_header_data[1]), int(Time_header_data[2]))

    def call(self):
        return [self.Time_values, *self.channel_data]

    ### convenience function start here ###

    def read_errors(self):
        """Reads out all errors from the error queue and prints them to the debug."""
        self.port.write("SYST:ERR:COUN?")
        err_count = self.port.read()
        if int(err_count) > 0:
            self.port.write("SYST:ERR:CODE:ALL?")
            answer = self.port.read()
            for err in answer.split(","):
                print("Scope R&S RTE error:", err)
