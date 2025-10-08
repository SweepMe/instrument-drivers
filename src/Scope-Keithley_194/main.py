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
# * Module: Scope
# * Instrument: Keithley 194


import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """<p><strong>Keithley 194/194A High Speed Voltmeter</strong></p>
                     <p>4.5/3.5 digit voltmeter with up to 1MS/s sampling rate.</p>
                     <p>This Scope module only offers the waveform capture mode for a single channel.</p>
                     <p>Use the corresponding Logger module for single value results.</p>
                    """


    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Keithley194Waveform"

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True] # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            "timeout": 10,
            "delay": 0.05
        }

        # measuring range
        self.ranges = {
            # Auto ranging not available in Waveform Mode
            #"Auto": "R0",
            "320 mV": "R1",
            "3.2 V": "R2",
            "32 V": "R3",
            "200 V": "R4",
        }

        # range scales used for calculating measurement result
        self.rangescales = {
            "320 mV": 1E-05,
            "3.2 V": 1E-04,
            "32 V": 1E-03,
            "200 V": 1E-02,
        }

        # choice of trigger; T26&T27 are executed on X command immediately, T6&T7 on external trigger signal, T20-23 on slope of signal
        self.triggers = {
            "Continuous (int)": "T26",
            "Single (int)": "T27",
            "Continuous (ext)": "T6",
            "Single (ext)": "T7",
            "Continuous (pos. slope)": "T20",
            "Single (pos. slope)": "T21",
            "Continuous (neg. slope)": "T22",
            "Single (neg. slope)": "T23",
        }

        # filter settings
        self.filters = {
            "Off": "P0",
            "500kHz": "P1",
            "50kHz": "P2",
        }

        # coupling
        self.couplings = {
            "DC": "I0",
            "AC": "I1",
            "Ground": "I2",
        }

    def update_gui_parameters(self, parameters):
        # retrieve currently set "Trigger" setting, default to "Single (int)" if unset
        trigger = parameters.get("TriggerSource", "Single (int)")

        new_parameters = {
            "SamplingRate": "1E+04",
            "SamplingRateType": ["Samples per s"],
            "TimeRange": ["Time range in s"],
            "TimeRangeValue": "1E-04",
            "TriggerSource": list(self.triggers.keys()),
            "Filter": list(self.filters.keys()),
            "TriggerDelay": 0.000,
        }

        # if the source signal should be used for triggering, setting the trigger level is offered additionally
        if trigger.endswith("slope)"):
            new_parameters["TriggerLevel"] = 0.000

        # apply channel settings for CH1 and CH2:
        for i in range(1, 3):
            new_parameters["Channel%i" % i] = i == 1  # default to channel 1 being selected
            new_parameters["Channel%i_Name" % i] = "CH%i" % i
            new_parameters["Channel%i_Range" % i] = list(self.ranges.keys())
            new_parameters["Channel%i_Coupling" % i] = list(self.couplings.keys())

        return new_parameters

    def apply_gui_parameters(self, parameters):

        self.trigger = parameters.get("TriggerSource", "Single (int)")
        self.srate = parameters.get("SamplingRate")
        self.acqtime = parameters.get("TimeRangeValue")
        self.trigger = parameters.get("TriggerSource")
        if self.trigger.endswith("slope)"):
            self.triggerlevel = parameters.get("TriggerLevel")
        self.filter = parameters.get("Filter")
        self.delay = parameters.get("TriggerDelay")
        self.port_string = parameters.get("Port")

        # reset measurement parameters
        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.channels = []
        self.channel_names = {}
        self.channel_ranges = {}
        self.channel_couplings = {}

        for i in range(1, 3):
            if parameters["Channel%i" % i]:
                self.channels.append(i)
                self.variables.append(parameters["Channel%i_Name" % i])
                self.units.append("V")
                self.plottype.append(True)
                self.savetype.append(True)
                self.channel_names[i] = parameters["Channel%i_Name" % i]
                self.channel_ranges[i] = parameters["Channel%i_Range" % i]
                self.channel_couplings[i] = parameters["Channel%i_Coupling" % i]

    def initialize(self):

        if len(self.channels) == 0:
            msg = "Please select one channel for recording."
            raise Exception(msg)
        elif len(self.channels) > 1:
            msg = "Please select only one channel for recording."
            raise Exception(msg)

        # K0 is used to enable EOI on GPIB communication and disable the holding of the bus
        self.port.write("K2X")

        # Data output format; sets output to binary
        self.port.write("G7X")

        # Clear waveform output, decrement reading buffer pointer
        self.port.write("B0X")

    def configure(self):

        # Waveform Mode;
        # IMPORTANT: setting modes on both channels also disarms the ADC on both
        # This makes sure that the unused channel won't feed results into the output buffer which
        # accidentally get retrieved instead of the ones from the selected channel
        self.port.write("C1XF0X")
        self.port.write("C2XF0X")

        # Channel
        # if channel 1 is selected, transmit selection to instrument
        if 1 in self.channels:
            # set channel 2 to external trigger to disable it
            self.port.write("C2T7X")
            #switch back to channel 1
            self.port.write("C1X")
        # if channel 2 is selected, transmit selection to instrument
        elif 2 in self.channels:
            self.port.write("C1T7X")
            self.port.write("C2X")

        # Sampling Rate (Hz)
        self.port.write("S1,%sX" % "{:.5E}".format(round(float(self.srate))))
        self.port.write("U6X")

        # Acquisition time (s)
        self.port.write("N1,%sX" % "{:.5E}".format(float(self.acqtime)))
        self.port.write("U5X")

        # Range
        # the channels list will always contain just one channel number at index position 0 so it is used as a key to select the measuring range
        self.port.write("%sX" % self.ranges[self.channel_ranges[self.channels[0]]])

        # Filter
        self.port.write("%sX" % self.filters[self.filter])

        # Coupling
        # uses same logic as in "Range"
        self.port.write("%sX" % self.couplings[self.channel_couplings[self.channels[0]]])

        # Delay
        self.port.write("W1,%sX" % self.delay)

        # reading buffer disabled
        self.port.write("Q0X")

    def unconfigure(self):

        # sets the trigger back to continuous trigger
        self.port.write("T0X")

    def measure(self):

        # Trigger arming and releasing for different sources
        if self.trigger.endswith("(int)"):
            self.port.write("%sX" % self.triggers[self.trigger])
        elif self.trigger.endswith("(ext)"):
            self.port.write("%sX" % self.triggers[self.trigger])
        elif self.trigger.endswith("slope)"):
            self.port.write("%s,%sX" % (self.triggers[self.trigger], self.triggerlevel))

    def read_result(self):
        # retrieving the raw data over the GPIB bus
        rawdata = self.port.port.read_raw()
        # get only the first byte from the buffer to analyse header information; header is always unsigned integer 'u1'
        bitmodecheck = np.frombuffer(rawdata,dtype='u1',offset=0, count=1)
        # unpack bit number 6 which indicates 8-bit (=0) or 16-bit (=1) values
        bitmodecheckflag = np.unpackbits(bitmodecheck)[6]

        # the choice between 8-bit (= 1 Byte) and 16-bit (= 2 Byte) sampling values is made by the instrument depending on
        # a) sampling rate being above 100kHz (forces 8-bit instead of 16-bit)
        # b) total amount of samples above 32.768 (forces 8-bit instead of 16-bit)
        # due to rounding errors when entering sampling rate and sampling time instead of the precise amount of sampling points, we determine the used bitdepth by the headerinformation received earlier
        if bitmodecheckflag == 0:
            self.bytecount = 1
            self.bitweight = 256
        else:
            self.bytecount = 2
            self.bitweight = 1

        # processing binary buffer into array;
        if self.bytecount == 1:
            # convert 8-bit raw byte stream behind header bytes (6) into array using 8-bit signed integer
            voltages_received=np.frombuffer(rawdata,dtype='i1',offset=6)
        else:
            # for 16-bit values, we need to inform "frombuffer" that the data is in big endian format by setting dtype ">" integer 16-bit (2-bytes)
            voltages_received=np.frombuffer(rawdata,dtype='>i2',offset=6)

        # create emtpy array to process data in, identical in size to the array that contains the received data
        # warning: the array created by np.frombuffer is writeprotected; even if made writeable via certain means, it does not suit to float modifications
        self.voltages = np.zeros(len(voltages_received))

        for i in range(len(voltages_received)):
            # taking the bitweight of the ADC reading into account and calculate value according to programming manual
            if voltages_received[i] > 0:
                self.voltages[i] = (voltages_received[i]*self.bitweight)-32768
            if voltages_received[i] < 0:
                self.voltages[i] = (voltages_received[i]*self.bitweight)+32768
            # the range to be used for scaling depends on the selected channel
            if 1 in self.channels:
                self.voltages[i]=float(self.voltages[i])*self.rangescales[self.channel_ranges[1]]
            else:
                self.voltages[i]=float(self.voltages[i])*self.rangescales[self.channel_ranges[2]]
        # generate linear time array FROM, TO, STEPSAMOUNT
        self.timecode = np.linspace(0, float(self.acqtime), len(self.voltages))

    def call(self):
        return [self.timecode] + [self.voltages]
