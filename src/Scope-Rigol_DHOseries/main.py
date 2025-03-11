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

# SweepMe! driver
# *Module: Scope
# * Instrument: Rigol DHO1000 Series


import time

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
                     Basic functionality only.
                  """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "DHO1000"

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        self.port_manager = True
        self.port_types = ["TCPIP", "USB"]
        self.port_identifications = ["RIGOL,DHO1*"]

        self.port_properties = {
                                "timeout": 10.0,
                                }


        self.commands = {
                        "Channel 1": "CH1",
                        "Channel 2": "CH2",
                        "Channel 3": "CH3",
                        "Channel 4": "CH4",
                        "External": "EXT",
                        "Line": "ACL",
                        "None": "NONE",
                        "Rising": "POS",
                        "Falling": "NEG",
                        }

        self.aquisitiontypes = {
                                "As is": "As is",
                                "Continuous": ":RUN",
                                "Single": ":SING",
                                }

    def set_GUIparameter(self):

        gui_parameter = {
                         "SweepMode": ["None"],

                         "TriggerSlope": ["As is", "Rising", "Falling"],
                         "TriggerSource": ["As is", "CHAN1", "CHAN2", "CHAN3", "CHAN4", "EXT", "ACL"],
                         "TriggerCoupling": ["As is", "AC", "DC", "LFReject", "HFReject"],
                         "TriggerLevel": 0,
                         "TriggerDelay": 0,
                         "TriggerTimeout": 3,
                         "TimeRange": ["Time range in s", "Time scale in s/div"],
                         "TimeRangeValue": ["As is", "20e-09", "50e-09", "100e-09", "200e-09", "500e-09", \
                         "1e-06", "2e-06", "5e-06", "10e-06", "20e-06", "50e-06", "100e-06", "200e-06", "500e-06", \
                         "1e-03", "2e-03", "5e-03", "10e-03", "20e-03", "50e-03", "100e-03", "200e-03"],
                         "TimeOffsetValue": 0.0,
                         "ADCResolution": ["12bit", "14bit BW limited", "16bit BW limited"],
                         #"SamplingRate": int(16e9), #just supported as a query by SCPI command set; Rigol sets sampling rate via SCPI in relation to chosen memory depth and timebase scale
                         "Acquisition": list(self.aquisitiontypes.keys()),
                         "Average": ["None", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
                         "VoltageRange": ["Voltage range in V"],
                       }

        for i in range(1,5):
            gui_parameter["Channel%i" % i] = i == 1
            gui_parameter["Channel%i_Name" % i] = "CH%i" % i
            gui_parameter["Channel%i_Range" % i] = ["2e-2", "4e-2", "8e-2", "2e-1", "4e-1", "8e-1", "2", "4", "8", "20", "40", "80", "200"]
            gui_parameter["Channel%i_Offset" % i] = 0.0

        return gui_parameter


    def get_GUIparameter(self, parameter: dict):

        self.triggersource = parameter["TriggerSource"]
        self.triggercoupling = parameter["TriggerCoupling"]
        self.triggerslope = parameter["TriggerSlope"]
        self.triggerlevel = parameter["TriggerLevel"]
        self.triggerdelay = parameter["TriggerDelay"]
        self.triggertimeout = int(parameter["TriggerTimeout"])
        self.adcresolution = parameter["ADCResolution"]
        self.aquisitiontype = parameter["Acquisition"]

        self.timerange = parameter["TimeRange"]
        self.timerangevalue = parameter["TimeRangeValue"]
        self.timeoffsetvalue = parameter["TimeOffsetValue"]
        #self.samplingrate = parameter["SamplingRate"]

        self.average = parameter["Average"]

        self.channels = []
        self.channel_names = {}
        self.channel_ranges = {}
        self.channel_divs = {}
        self.channel_offsets = {}

        for i in range(1,5):

            if parameter["Channel%i" % i]:
                self.channels.append(i)

                self.variables.append(self.commands["Channel %i" % i] + " " + parameter["Channel%i_Name" % i])
                self.units.append("V")
                self.plottype.append(True)
                self.savetype.append(True)

                self.channel_names[i] = parameter["Channel%i_Name" % i]
                self.channel_ranges[i] = float(parameter["Channel%i_Range" % i])
                self.channel_divs[i] = self.channel_ranges[i] / 8
                self.channel_offsets[i] = parameter["Channel%i_Offset" % i]


    def initialize(self):
        # This driver does not use Reset yet so that user can do measurements with changing options manually
        #self.port.write("*RST")

        # clears waveform on screen;
        # IMPORTANT! While it is not documented in the programming manual, this also seems to clear the waveform in the memory.
        # If this step is skipped and the driver is run without a successful trigger, essentially running into timeout,
        # it will return the same waveform again that was aquired on the last successful run before as that is still persistent in memory.
        self.port.write(":CLE")

        # stops running aquisitions, if any are active
        self.port.write(":STOP")

        if len(self.channels) == 0:
            msg=("Please select at least one channel to be read out")
            raise Exception(msg)

        # sets encoding to ASCii insetad of BYTE or WORD
        self.port.write("WAV:FORM ASC")
        # normal waveform capture, means capturing screen content
        self.port.write("WAV:MODE NORM")


    def configure(self):

        ### Acquisition ###
        # setting averaging and bit depth for aquisition
        if self.adcresolution.startswith("12"):
            # activate AVERAGING function in standard 12bit ADC resolution mode, the only one wherein it is allowed
            if self.average !="None":
                self.port.write("ACQ:TYPE AVER")
                self.port.write("ACQ:AVER %s" % self.average)
        else:
            # if in any other ADC resolution than 12bit, throw an error if AVERAGING is selected
            if self.average !="None":
                msg=("This scope does not allow combining averaging with HighRes ADC mode")
                raise Exception(msg)

            # use BW limited HighRes Mode if bit depth higher than 12 is selected and AVERAGING is not activated
            self.port.write("ACQ:TYPE HRES")
            # use only first two letters to extract bit depth and use it as SCPI command parameter
            self.port.write("ACQ:BITS %.2s" % self.adcresolution)

        # sets the memory depth automatically and with that, sampling rate as well
        self.port.write("ACQ:MDEP AUTO")

        ### Trigger ###
        # setting trigger coupling
        self.port.write("TRIG:COUP %s" % self.triggercoupling)

        # setting trigger slope and level
        if self.triggersource == "As is":
            pass
        else:
            self.port.write("TRIG:EDGE:SOUR %s" % self.triggersource)

        # set trigger level and makes sure its format fits into SCPI standard
        self.port.write("TRIG:EDGE:LEV %s" % str("{:.4E}".format(float(self.triggerlevel))))

        # set trigger slope
        if self.triggerslope == "As is":
            pass
        elif self.triggerslope== "Rising":
            self.port.write("TRIG:EDGE:SLOP POS")
        elif self.triggerslope == "Falling":
            self.port.write("TRIG:EDGE:SLOP NEG")

        # makes sure that NORMAL sweep (showing only triggered events) instead of AUTO is chosen for continuous triggering
        if self.aquisitiontype == "Continuous":
            self.port.write("TRIG:SWE NORM")

        ### Time range ###
        # setting time range
        if self.timerangevalue == "As is":
            pass
        else:
            t_s = str("{:.3E}".format(float(self.timerangevalue)/10))
            t_div = str("{:.3E}".format(float(self.timerangevalue)))

        if self.timerange == "Time range in s":
            # set timebase range
            self.port.write("TIM:MAIN:SCAL %s" % t_s)
        elif self.timerange == "Time scale in s/div":
            # set timebase scale
            self.port.write("TIM:MAIN:SCAL %s" % t_div)

        # setting timebase offset
        self.port.write("TIM:MAIN:OFFS %s" % self.timeoffsetvalue)

        ### Channel properties ###
        # switch display of channels on/off and set vertical properties
        for i in range(1,5):
            if i in self.channels:
                # turn on selected channels
                self.port.write("CHAN%s:DISP ON" % i)
                self.port.write("CHAN%s:SCAL %s" % (i, self.channel_divs[i]))
                # scale of channel
                if self.channel_offsets[i] != "As is":
                    # define offset of channel
                    self.port.write("CHAN%s:OFFS %s" % (i, self.channel_offsets[i]))
            else:
                # turn off unselected channels
                self.port.write("CHAN%s:DISP OFF" % i)


    def apply(self):
        pass

    def measure(self):

        time.sleep(float(self.triggerdelay))
        trigcounter = 0

        # setting trigger sweep mode / trigger aquisition
        if self.aquisitiontype == "As is":
            pass
        else:
            if self.average !="None" and self.aquisitiontype == "Single":
                msg=("Averaging has to be used with continuous triggering")
                raise Exception(msg)
            # will execute either :RUN oder :SINGle SCPI command depending on choice of aquisition type (continuous or single)
            self.port.write("%s" % self.aquisitiontypes[self.aquisitiontype])

        time.sleep(0.4)
        # The RIGOL does not allow to determine the amount of successful acquired averaging samples.
        # It also returns TD for trigger status during continuous triggering when a trigger was successful, but already waiting for a new one.
        # Therefore, the only solution is to STOP the scope after a manual set trigger timeout period which has to be adjusted accordingly.
        # For normal (non-averaging) use, this is not a problem.

        while True:
            # check if trigger counter ran into timeout limit;
            if trigcounter >= self.triggertimeout:
                self.port.write(":STOP")
                break

            # query the status of the trigger to determine success of triggering
            self.port.write("TRIG:STAT?")
            triggerstat=self.port.read()
            # observing the trigger status in the debug window
            print ("Trigger Status: ", triggerstat)
            # check if trigger is still running; for exiting SINGLE triggering as well as manual stopping the scope via button on instrument
            # also: trigger status TD is only available shortly after triggering. For events with a low frequency of appearance, TD trigger state might be missed and exiting relies on the timeout counter.
            if triggerstat == "STOP":
                break
            # check if an event was triggered in CONTINUOUS mode
            elif self.aquisitiontype.startswith("Cont") == 1 and triggerstat == "TD":
                break
            else:
                trigcounter += 1
                time.sleep(1)


        self.port.write("WAV:PRE?")
        preamble = self.port.read().split(",")

        # splitting preamble values into seperate variables for further use
        wav_format=preamble[0]
        acq_mode=preamble[1]
        numberpoints=int(preamble[2])
        av_count=int(preamble[3])
        x_inc=float(preamble[4])
        x_orig=float(preamble[5])
        x_ref=float(preamble[6])
        y_inc=float(preamble[7])
        y_orig=float(preamble[8])
        y_ref=float(preamble[9])

        slot = 0

        for i in self.channels:
            if "inputarray" in locals():
                del inputarray

            #create empty inputarray array
            inputarray = []

            # select channel to be read
            self.port.write("WAV:SOUR CHAN%s" % i)

            self.port.write("WAV:DATA?")
            inputarray=self.port.read().split(",")

            # only for first measurement
            if slot == 0:
                # number of measured channels
                channels = len(self.channels)
                # generate empty array of correct size for channels + data
                self.voltages = np.zeros((len(inputarray), len(self.channels)))
                # generate linear time array FROM, TO, STEPSAMOUNT
                self.timecode = np.linspace(x_orig, (x_orig+x_inc*(len(inputarray))), len(inputarray))

            data = []
            for n in np.arange(len(inputarray)):
                # sort the values as data
                data.append(inputarray[n])

            # convert list to data array
            data = np.array(data)

            # inputs voltage data for channel i into correct column of data array
            self.voltages[:, slot] = data
            # set correct column for next channel
            slot += 1

    def call(self):
        return [self.timecode] + [self.voltages[:,i] for i in range(self.voltages.shape[1])]
