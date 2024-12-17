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


from pysweepme.EmptyDeviceClass import EmptyDevice
import numpy as np

class Device(EmptyDevice):

    description = """
        Most of the Scope module features are not yet supported and many properties must be set manually.
    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "DPO7000"
        
        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data
        
        self.port_manager = True
        self.port_types = ["USB", "GPIB", "TCPIP"]
        self.port_identifications = ['TEKTRONIX,DPO7354C*'] 
       
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
           
    def set_GUIparameter(self):

        gui_parameter = {
            "SweepMode": ["None"],

            "TriggerSlope": ["As is", "Rising", "Falling"],
            "TriggerSource": ["As is", "CH1", "CH2", "CH3", "CH4", "AUX", "LINE"],
            # "TriggerCoupling": ["As is", "AC", "DC", "HF", "Auto level"],  # not yet implemented
            "TriggerLevel": 0,
            "TimeRange": ["Time range in s", "Time scale in s/div", "Record length"],
            "TimeRangeValue": 5e-4,
            "TimeOffsetValue": 0.0,
            "SamplingRate": int(1e7),
            # "Acquisition": ["Continuous", "Single"],
            # Average of 1 is not yet supported
            "Average": ["As is", "1", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
            "VoltageRange": ["Voltage range in V"],
        }
                       
        for i in range(1,5):
            gui_parameter["Channel%i" % i] = True if i == 1 else False
            gui_parameter["Channel%i_Name" % i] = "CH%i" % i
            gui_parameter["Channel%i_Range" % i] = ["1e-2", "2e-2", "5e-2", "1e-1", "2e-1", "5e-1", "1", "2", "5", "10", "20", "50"]
            gui_parameter["Channel%i_Offset" % i] = 0.0
                     
        return gui_parameter

    def get_GUIparameter(self, parameter={}):
    
        self.triggersource = parameter["TriggerSource"]
        # self.triggercoupling = parameter["TriggerCoupling"]  # not yet implemented
        self.triggerslope = parameter["TriggerSlope"]
        self.triggerlevel = parameter["TriggerLevel"]
        
        self.timerange = parameter["TimeRange"]
        self.timerangevalue = float(parameter["TimeRangeValue"])
        self.timeoffsetvalue = parameter["TimeOffsetValue"]
        self.samplingrate = parameter["SamplingRate"]

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
                self.channel_divs[i] = self.channel_ranges[i] / 10
                self.channel_offsets[i] = parameter["Channel%i_Offset" % i]

    def initialize(self): 
    
        # This driver does not use Reset yet so that user can do measurements with changing options manually
        # self.reset()

        if len(self.channels) == 0:
            raise Exception("Please select at least one channel to be read out.")

        identifier = self.get_identification()
        print("Identifier:", identifier)

        self.port.write("DAT:STOP 999999999999")  # ensure that the entire waveform is recorded
        self.port.write("DAT:ENCdg ASCii")  # sets encoding

    def configure(self):

        # Acquisition
        self.port.write("ACQ:STOPAfter SEQ")  # single sequence measurement

        # Averaging

        self.port.write("ACQuire:MODe AVE")  # use acquisition mode "averaged"
        if self.average == "As is":
            self.port.write("ACQ:NUMAV?")  # set averages
            self.number_averages = int(self.port.read())
        else:
            self.number_averages = int(self.average)
            self.port.write("ACQ:NUMAV %i" % self.number_averages)  # set averages

        # Trigger
        # set the trigger settings, first the trigger level and then the slope
        if self.triggersource == "As is" or self.triggersource == "None":
            pass
        else:
            self.port.write("TRIGger:A:EDGE:SOUrce %s" % self.triggersource)
        
        self.port.write("TRIGger:A:EDGE:SOUrce?")
        triggerchannel = self.port.read() 
        
        self.port.write("TRIGger:A:LEVel:%s %s" % (triggerchannel, self.triggerlevel))  # set trigger level
        
        if self.triggerlevel == 0:  # if no specific trigger level desired
            self.port.write("TRIG:A SETLevel;TRIG:B SETLevel")  # sets the trigger level at 50%
     
        if self.triggerslope == "As is":  # set trigger slope
            pass
        elif self.triggerslope == "Rising":
            self.port.write("TRIG:A:EDGE:SLOpe RISe;TRIG:B:EDGE:SLOpe RISe")
        elif self.triggerslope == "Falling":
            self.port.write("TRIG:A:EDGE:SLOpe FALL;TRIG:B:EDGE:SLOpe FALL")

        # Time range

        # The device can operate in three different horizontal scaling modes. As the sampling rate is a parameter
        # set by the user, one of these modes will be disregarded. The user can then decide whether to define
        # the time range/time per division, or the total record length, which will cause the device to switch
        # between auto and manual mode. This is done by checking if the parameter TimeRange is set to 
        # Record length, and then setting the horizontal scaling accordingly.
                
        if self.timerange != "Record length":  # Entering into auto mode

            self.port.write("HORizontal:MODE AUTO")
            if self.timerange == "Time range in s":
                self.divisions = self.timerangevalue / 10.0  # only accepts entries for the time scale
            elif self.timerange == "Time scale in s/div":
                self.divisions = self.timerangevalue
 
            self.port.write("HORizontal:MODE:SCAle %s" % self.divisions)  # set time scale
            
        elif self.timerange == "Record length":
            # set manual mode + RL
            self.port.write("HORizontal:MODE:MANual;HORizontal:MODE:RECOrdlength %s" % self.timerangevalue)

        self.port.write("HORizontal:MODE:SAMPLERate %s" % self.samplingrate)  # set sampling rate in 1/s

        # Channel properties
        for i in self.channels:
            self.port.write("SEL:CH%s ON" % i)  # turn on selected channels
            self.port.write("CH%s:SCAle %s; :CH%s:OFFSet %s" % (i, self.channel_divs[i], i, self.channel_offsets[i]))

    def measure(self):

        # ready acquisition state
        self.port.write("ACQ:STATE RUN")

        # if self.average in ["As is", "Not supported"]:
        #     # avoid an infinite loop
        #     raise Exception("Please select a correct number of averages to avoid an unending loop.")

        # reset averages here

        if self.number_averages > 1:
            while True:  # evaluation only after correct number of averages performed

                if self.is_run_stopped():
                    return False

                average_step = self.get_acquisition_number()

                print("Averaging...", average_step)
                if average_step >= self.number_averages:
                    break

        self.numbers = np.array(self.channels)  # array of channel numbers
        slot = -1  # run variable for data sorting
        self.channel_data = self.numbers.reshape(1, -1)

        for i in self.channels:
            slot += 1  # set correct column for next channel
            self.port.write(f"DAT:SOU CH{i}")  # select channel to be read

            # First step is to obtain all relevant header data and generate an array containing the time value
            # for each data point. The header is queried using WFMO? above, and then split into the relevant entries
            # which are then accessed for the later necessary factors and offsets.
            self.port.write("WFMOutpre?")  # query the preamble for relevant parameters
            preamble = self.port.read().split(";")  # split the header
            # print(preamble)

            # number of time values + units
            # configuration = preamble[5].replace('\"', "").split(", ")
            # timesteps = int(configuration[4].split()[0])  # number of points
            timesteps = int(preamble[6])

            if slot == 0:  # only for first measurement
                record_length = int(preamble[6])  # number of data points
                channels = len(self.channels)  # number of measured channels
                self.voltages = np.zeros((record_length, channels))  # generate array of correct size for channels+data

                x_step, x_offset, x_zero = float(preamble[9]), float(preamble[10]), float(preamble[11])
                self.times = (np.arange(timesteps) - x_zero) * x_step  # generate time array

            # The next section gathers vertical scaling and offset to later calculate the data values from
            # the digitization levels of the oscilloscope
            y_mult, y_offset, y_zero = float(preamble[13]), float(preamble[14]), float(preamble[15])

            data = self.get_waveform()
            volt_data = (data - (y_offset + y_zero)) * y_mult  # calculates correct voltages

            self.voltages[:, slot] = volt_data  # inputs voltage data for channel i into correct column of data array

    def call(self):
        return [self.times] + [self.voltages[:,i] for i in range(self.voltages.shape[1])]

    """ wrapped communication commands """

    def get_identification(self):
        self.port.write("*IDN?")  # Query device name
        answer = self.port.read()
        return answer

    def reset(self):
        self.port.write("*RST")

    def get_waveform(self):
        self.port.write("CURVe?")  # queries the waveform from the oscilloscope
        curve_points = self.port.read().split(",")  # turn str object from query into list
        data = np.array(list(map(float, curve_points)))
        return data

    def get_acquisition_number(self):
        self.port.write("ACQ:NUMACQ?")
        answer = self.port.read()
        return int(answer)