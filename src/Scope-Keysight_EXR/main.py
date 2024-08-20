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


# SweepMe! device class
# Type: Scope
# Device: Keysight EXR/MXR/UXR Series (tested on EXR only)


from pysweepme.EmptyDeviceClass import EmptyDevice
import numpy as np
import time as time


class Device(EmptyDevice):

    description = """
                     Main functions only.
                  """
                  
    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "EXRxxxA"
        
        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data
        
        self.port_manager = True
        self.port_types = ["USB"]
        self.port_identifications = ['Keysight,EXR*'] 
       
        self.port_properties = {
                                "timeout": 10.0,
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

        GUIparameter = { 
             "SweepMode": ["None"],

             "TriggerSlope": ["As is", "Rising", "Falling"],
             "TriggerSource": ["As is", "CHAN1", "CHAN2", "CHAN3", "CHAN4", "AUX", "LINE"],
             # "TriggerCoupling": ["As is", "AC", "DC", "HF", "Auto level"],  # not yet implemented
             "TriggerLevel": 0,
             "TriggerDelay": 0,
             "TriggerTimeout": 2,
             "TimeRange": ["Time range in s", "Time scale in s/div"],
             "TimeRangeValue": 5e-4,
             "TimeOffsetValue": 0.0,
             "SamplingRate": ["10e+3", "100e+3", "1e+6", "10e+6", "100e+6", "1e+9","5e+9","10e+9","16e+9"],
             "SamplingRateType":["BITS10: 10 Bits (16 GSa or Manual)","BITS11: 11 Bits (6.4 GSa)","BITS12: 12 Bits (3.2 GSa)","BITS13: 13 Bits (1.6 GSa)","BITS14: 14 Bits (800 MSa)","BITS15: 15 Bits (400 GSa)","BITS16: 16 Bits (200 GSa)","BITS16_4: 16 Bits (100 GSa)","BITS16_2: 16 Bits (50 GSa)"],
             "Acquisition": ["Continuous", "Single"],
             "Average": ["none", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
             "VoltageRange": ["Voltage range in V"],
        }
                       
        for i in range(1, 5):
            GUIparameter["Channel%i" % i] = True if i == 1 else False
            GUIparameter["Channel%i_Name" % i] = "CH%i" % i
            GUIparameter["Channel%i_Range" % i] = ["4e-2", "8e-2", "2e-1", "4e-1", "8e-1", "2", "4", "8", "20", "40", "80", "200"]
            GUIparameter["Channel%i_Offset" % i] = 0.0
                     
        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        #print(parameter)
    
        self.triggersource = parameter["TriggerSource"]
        self.triggercoupling = parameter["TriggerCoupling"]
        self.triggerslope = parameter["TriggerSlope"]
        self.triggerlevel = parameter["TriggerLevel"]
        self.triggerdelay = parameter["TriggerDelay"]
        self.triggertimeout = parameter["TriggerTimeout"]
        
        self.timerange = parameter["TimeRange"]
        self.timerangevalue = float(parameter["TimeRangeValue"])
        self.timeoffsetvalue = parameter["TimeOffsetValue"]
        self.samplingrate = parameter["SamplingRate"]
        self.samplingratetype = parameter["SamplingRateType"]  # reads the chosen "sampling rate type", here: used to set the ADC resolution to enable resolution increase at the cost of samplingrate and bandwidth
        
        if self.samplingratetype.startswith("BITS16_"):  # chosen ADC resolution is taken from the GUI selection and modified so it can be used as the required parameter in the respective SCPI command
            self.samplingratetype = self.samplingratetype[:8]
        else:
            self.samplingratetype = self.samplingratetype[:6]

        self.acquisition = parameter["Acquisition"]
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
        # self.port.write("*RST")
        
        if len(self.channels) == 0:
            raise Exception("Please select at least one channel to be read out")
        
        if int(10*float(self.triggertimeout)) % 2 != 0:
            # values are multiplied by 10 to allow comparison operation in integer realm
            msg = "Trigger timeout can only be set in steps of 0.2s"
            raise Exception(msg)

        # self.port.write("*IDN?")                # Query device name
        # print("ID Checkup")
        # print(self.port.read())

        self.port.write("*CLS")  # Clears all the event registers, and also clears the error queue.
        
        self.port.write(":WAV:FORM ASC")  # sets encoding to ASCii insetad of BYTE or WORD; BYTE and WORD would allow for a much quicker data transfer, but values would have to be processed first before use.
        self.port.write(":WAV:TYPE RAW")  # sets data type to RAW, transmitting only true sampling points, no interpolation

    def configure(self):

        # Acquisition #
        self.port.write(":ACQ:MODE RTIM")  # use real time aquisition
        
        if self.average =="none":
            self.port.write(":ACQ:AVER OFF")  # diable averaging of triggered shots
        else:
            self.port.write(":ACQ:AVER ON")  # enabling averaging of triggered shots
            self.port.write(":ACQ:AVER:COUN %s" %self.average)  # setting the amount of triggered shots to be used for averaging
        
        self.port.write(":ACQ:POIN:ANAL AUTO")  # set the Memory Depth to AUTO to give priority to sampling rate, mnanual p. 326
        if self.samplingratetype.startswith("BITS10"):
            self.port.write(":ACQ:SRAT:ANAL %s" %self.samplingrate)  # sets the sampling rate, memory auto-adjusts accordingly. Only allowed with 10bits ADC setting!!!
        else:
            self.port.write(":ACQ:SRAT:ANAL AUTO")  # sampling rate to AUTO for all ADC interpolation options
        self.port.write(":ACQ:ADCR %s" %self.samplingratetype)  # sets the "sampling rate type", here: used to set the ADC resolution to enable resolution increase at the cost of samplingrate and bandwidth

        self.port.write(":TIM:REF CENTER")   #sets the timebase reference to center; might be a future GUI option to allow for left or right border choice?
        
        ##self.port.write(":ACQ:AVER %s" %self.average)   # set averages

        # Trigger #
        # setting trigger source and level
        if self.triggersource == "As is":
            pass
        else:
            self.port.write(":TRIG:EDGE:SOUR %s" % self.triggersource)  # set trigger source
            self.port.write(":TRIG:LEV %s,%s" % (self.triggersource, self.triggerlevel))  # set trigger level
        
        if self.triggerlevel == 0:  # if no specific trigger level desired,
            self.port.write(":TRIG:LEV:FIFT")  # sets the trigger level at 50%
     
        if self.triggerslope == "As is":  # set trigger slope
            pass
        elif self.triggerslope== "Rising":
            self.port.write(":TRIG:EDGE:SLOP POS")
        elif self.triggerslope == "Falling":
            self.port.write(":TRIG:EDGE:SLOP NEG")

        self.port.write(":TRIG:DEL:TDEL:TIME %s" % self.triggerdelay) # sets trigger delay; very usefull if scope is combined in a sweepme sequence with other instruments
        self.port.write(":TRIG:SWE TRIG")  # set trigger sweep mode to TRIGGERED

        # Time range #
        if self.timerange == "Time range in s":
            self.port.write(":TIM:RANG %s" %self.timerangevalue)  # set timebase range
        elif self.timerange == "Time scale in s/div":
            self.port.write(":TIM:SCAL %s" %self.timerangevalue)  # set timebase scale
        
        if self.timeoffsetvalue == "As is":
            pass
        else:
            self.port.write(":TIM:POS %s" %self.timeoffsetvalue)  # set timebase offset

        for i in range(1, 5):  # makes sure that only activated channels are displayed
            if i in self.channels:
                self.port.write(":CHAN%s:DISP ON" % i)  # turn on selected channels
                self.port.write(":CHAN%s:SCAL %s" % (i, self.channel_divs[i]))  # scale of channel
                self.port.write(":CHAN%s:OFFS %s" % (i, self.channel_offsets[i]))  # define offset of channel
            else:
                self.port.write(":CHAN%s:DISP OFF" % i)  # turn off unselected channels
            
    def apply(self):
        pass
        
    def measure(self):
        
        if self.average != "none" and self.acquisition.startswith("Cont"):
            self.port.write(":CDIS")  # clear display to reset the averaging counter when using continous trigger
            time.sleep(0.3)
        
        if self.acquisition.startswith("Single"): 
            self.port.write(":SING")  # performs single acquisition
        elif self.acquisition.startswith("Cont"):
            self.port.write(":RUN")  # run continuous aquisition; not required when using single trigger
            
        time.sleep(float(self.triggerdelay))
        trigcounter = 0
        while True:
            self.port.write(":ADER?")  # check if trigger aquisition was successfull; if averaging is enabled, it will return 1 only when all average samples have been taken
            triggerstat=int(self.port.read())
            print("triggerstatus:", triggerstat)
            if triggerstat == 0 and trigcounter < int(round(float(self.triggertimeout),1)*5):  #if no trigger was aquired, wait loops in 0.2s increments
                trigcounter += 1
                time.sleep(0.2)
            elif trigcounter >= int(round(float(self.triggertimeout),1)*5):  #timeout in trigger wait loop, stops the aqusition
                self.port.write(":STOP")
                if self.average == "none":
                    msg = "Oscilloscope could not trigger before timeout"
                    raise Exception(msg)
                else:
                    msg = "Oscilloscope could not trigger for sufficient averaging samples before timeout"
                    raise Exception(msg)
            else:
                break
        
        if self.acquisition.startswith("Cont"):
            self.port.write(":STOP")  # stop continuous aquisition; not required when using single trigger
        
        slot = 0  # run variable for data sorting

        time.sleep(0.2)
        self.port.write(":WAV:PRE?")  # retrieving the waveform preamble
        time.sleep(0.2)
        
        # This section retrieves the preamble which describes all properties of the stroes waveform.
        # While not all attributes are used, they remain included for debugging purposes.
        preamble = self.port.read().split(",")
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
        #print ("wav_format:", wav_format, "acq_mode:", acq_mode, "numberpoints:", numberpoints, "av_count:", av_count, "x_inc:", x_inc, "x_org:", x_orig, "x_ref:", x_ref, "y_inc:", y_inc, "y_org:", y_orig, "y_ref:", y_ref)

        for i in self.channels:
            
            self.port.write(":WAV:SOUR CHAN%s" % i)  # select channel to be read

            if slot == 0:  # only for first measurement
                channels = len(self.channels)  # number of measured channels
                self.voltages = np.zeros((numberpoints, len(self.channels)))  # generate empty array of correct size for channels + data

            self.timecode = np.linspace(x_orig, (x_orig+x_inc*numberpoints), numberpoints)  # generate linear time array FROM, TO, STEPSAMOUNT

            self.port.write(":WAV:DATA?;*OPC")  # retrieve waveform values from scope
            time.sleep(0.2)  # give scope time to prepare waveform data for download
            datapoints = self.port.read().split(",")  # read values from scope
            
            opccounter = 0  # set counter for OPC loop back to zero
            
            while True:
                self.port.write("*OPC?")  # query scope in loop whether [OP]eration of waveform data tranmission is [C]ompleted
                completed = int(self.port.read())
                if completed == 0 and opccounter < 25:  # loop time hardcoded to 5s
                    opccounter += 1
                    time.sleep(0.2)
                else:
                    break
                
            data = []
            for i in np.arange(numberpoints):
                data.append(datapoints[i])  # put waveform values of current channel into data output list
            
            data = np.array(data)  # convert list to data array
            
            self.voltages[:, slot] = data  # inputs voltage data for channel i into correct column of data array
            slot += 1  # set correct column for next channel

    def call(self):
        return [self.timecode] + [self.voltages[:,i] for i in range(self.voltages.shape[1])]
