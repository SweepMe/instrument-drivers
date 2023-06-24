# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 - 2019 Axel Fischer (sweep-me.net)
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


# SweepMe! device class
# Type: Scope
# Device: HMO3004


import numpy as np
import time

from ErrorMessage import error

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "HMO3004"
                       
        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True] # True to plot data
        self.savetype = [True]  # True to save data
        
        # here the port handling is done
        # the MeasClass automatically creates the PortObject during in the connect function of the MeasClass
        self.port_manager = True
        self.port_types = ["USB"]
        self.port_identifications = ['Rohde&Schwarz,HMO3054'] 
       
        # port_identifications does not work at the moment
        # plan is to hand it over to PortManager who only gives PortObjects back who match at least one of these strings
        # by that multiple devices could be found and related to one DeviceClass 

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
                        
        self.max_time = 10.0
                        
    def set_GUIparameter(self):
    
        GUIparameter = { 
                         "SweepMode": ["None", "Time range in s", "Time scale in s/div", "Time offset in s"],
                         
                         
                         "TriggerSlope": ["As is", "Rising", "Falling"],
                         "TriggerSource": ["As is", "Channel 1", "Channel 2", "Channel 3", "Channel 4", "External", "Line", "None"],
                         "TriggerCoupling": ["As is", "AC", "DC", "HF", "Auto level"],
                         "TriggerLevel": "As is",
                         
                         
                         "TimeRange": ["Time range in s:", "Time scale in s/div:"],
                         "TimeRangeValue": 1e-3,
                         "TimeOffsetValue": 0.0,
                         
                         "Acquisition": ["Continuous", "Single"],
                         "Average": ["As is", "1", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
                         
                         "SamplingRateType": ["Auto sampling rate", "Maximum waveform rate"]  # "Maximum sample rate", "Sampling rate in 1/s:", "Samples per time range:", "Samples per time per div:"],
                         #"SamplingRate": "As is",
                         
                        }
                        
        for i in np.arange(4)+1:
            GUIparameter["Channel%i" % i] = False        
            GUIparameter["Channel%i_Name" % i] = "Ch%i" %i
            GUIparameter["Channel%i_Range" % i] = "1"
            GUIparameter["Channel%i_Offset" % i] = "As is"
     
                        
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
        
        self.average = parameter["Average"]
        self.samplingratetype = parameter["SamplingRateType"]
        self.samplingrate = parameter["SamplingRate"]
        
        self.channels = []
        for i in np.arange(4)+1:
            if parameter["Channel%i" % i]:
                #self.channels[i] = parameter["Channel%i" % i]
                self.channels.append(i)
        
        self.channel_names = {}
        self.channel_ranges = {}
        self.channel_offsets = {}
        
        for i in self.channels:
            self.channel_names[i] = parameter["Channel%i_Name" % (i)]
            self.channel_ranges[i] = parameter["Channel%i_Range" % (i)]
            self.channel_offsets[i] = parameter["Channel%i_Offset" % (i)]
         
            self.variables.append(self.commands["Channel %i" % i] + " " + parameter["Channel%i_Name" % i])
            self.units.append("V")
            self.plottype.append(True)
            self.savetype.append(True)
  
    def initialize(self): 
        pass
        self.port.write("*CLS")
        # dont' use *RST as it will destroy all settings which is in conflict with using 'As is'
    
        #self.port.write("*IDN?")
        #print(self.port.read())
        
        
    def configure(self):

  
        ########################## time ########################################################
        
        if self.timerangevalue != "" and self.timerangevalue != "0":
        
            if self.timerange == "Time range in s":
                self.port.write("TIM:RANG %s" % self.timerangevalue)
            if self.timerange == "Time scale in s/div:":
                self.port.write("TIM:SCAL %s" % self.timerangevalue)
            
        if self.timeoffsetvalue != "":    
            self.port.write("TIM:POS %s" % self.timeoffsetvalue)
        
        
        ########################## trigger #####################################################
        
        self.port.write("TRIG:B:ENAB OFF")
        
        self.port.write("TRIG:A:MODE AUTO")

        if self.triggersource != "As is":
        
            self.port.write("TRIG:A:SOUR %s" % self.commands[self.triggersource]) 

            if self.triggersource.startswith("External"):
                if self.triggercoupling == "HF" or self.triggercoupling == "Auto level":
                    self.triggercoupling == "AC"
                self.port.write("TRIG:EXT:COUP %s" % self.triggercoupling)  # AC or DC
            else:
                if self.triggerlevel == "Auto level":
                    self.triggerlevel = "ALEV"
                self.port.write("TRIG:A:EDGE:COUP %s" % self.triggercoupling)# AC, DC, HF, Auto level

            self.port.write("TRIGger:A:TYPE EDGE")
        
        if self.triggerslope != "As is":
        
            self.port.write("TRIG:A:EDGE:SLOP %s" % self.commands[self.triggerslope])
        
        if self.triggerlevel != "" or self.triggerlevel != "As is":
        
            self.triggerlevel = float(self.triggerlevel)
        
            if self.triggersource.startswith("Channel"):
                self.port.write("TRIG:A:LEV%s %s" %(self.triggersource[-1], self.triggerlevel))
            
            if self.triggersource.startswith("External"):
                self.port.write("TRIG:A:LEV5 %s" % self.triggerlevel)
           
        ########################## acquisition #####################################################
              
        self.port.write("ACQ:HRES AUTO") # use High resolution if possible
        
        # using REFR puts it to average mode and not to refresh mode as expected.
        #self.port.write("ACQ:TYPE REFR")
        self.port.write("ACQ:TYPE AVER")
        #self.port.write("ACQ:TYPE?")
        #print(self.port.read())
        
        if self.average != "As is":
            self.port.write("ACQ:AVER:COUN %s" % self.average)
        #self.port.write("ACQ:AVER:COUN?")
        #print(self.port.read())
            
            
        if self.samplingratetype == "Auto sampling rate":
            self.port.write("ACQ:WRAT AUTO")
            #To display the best waveform, the instrument selects the optimum
            #combination of waveform acquisition rate and sample rate using the full
            #memory depth.
            
        elif self.samplingratetype == "Maximum waveform rate":
            self.port.write("ACQ:WRAT MWAV")
            #Maximum waveform rate: The instrument combines sample rate and
            #memory depth to acquire at maximum waveform acquisition rate. In
            #combination with persistence fuction, the mode can display rare signal
            #anomalies.
 
        elif self.samplingratetype == "Maximum sample rate":
            self.port.write("ACQ:WRAT MSAM")
            #Maximum sample rate: The instrument acquires the signal at maximum
            #sample rate and uses the full memory depth. The result is a waveform
            #with maximum number of
                         
            
        else:
            if samplingrate != "As is":
                       
            
                if self.samplingratetype == "Sampling rate in 1/s:":
                    pass
                    
                elif self.samplingratetype == "Samples per time range:":
                    pass
                
                elif self.samplingratetype == "Samples per time per div:":
                    pass
                    
  
            
        #self.port.write("FORM?") # Waveform rate auto
        #print(self.port.read())
        
        #self.port.write("CHANnel<m>:ARIThmetics <TrArithmetic>O") #OFF | ENVelope | AVERage | FILTer
        # self.port.write("RUN")
        
        # here all channels that are not selected are switched off as they may be activated from the last run
        for i in np.arange(4)+1:
            if not i in self.channels:
                self.port.write("CHAN%i:STAT OFF" %i)
        
        # now we switch on the channels that have to be used
        for i in self.channels:
            #self.port.write("CHAN%i:STAT?")
            #print(self.port.read())
            self.port.write("CHAN%i:TYPE SAMP" %i)
            self.port.write("CHAN%i:STAT ON" %i)
            
           
            if self.channel_ranges[i] != "As is":
                
                range_value = float(self.channel_ranges[i])
                self.port.write("CHAN%i:RANG %s " % (i, range_value))

            if self.channel_offsets[i] != "As is":
                # fill in your command
                offset_value = float(self.channel_offsets[i])
                self.port.write("CHAN%i:POS %s " % (i, offset_value))



    def apply(self):
        
        if self.sweepmode != "None":
        
            self.value = float(self.value)

            if self.sweepmode == "Time range in s":
                self.port.write("TIM:RANG %s" % self.value)
                
            elif self.sweepmode == "Time scale in s/div":
                self.port.write("TIM:SCAL %s" % self.value)
                
            elif self.sweepmode == "Time offset in s":
                self.port.write("TIM:POS %s" % self.value)
                

        #self.port.write("AUT")
        
        # self.port.write("CHAN1:DATA:POIN?")
        # self.NrPoints = int(self.port.read())
        
    def measure(self):

        starttime = time.perf_counter()
        while True:
            
            self.port.write("ACQ:AVER:COMP?")
            answer = self.port.read()

            if answer == "1":
                break
            else:   
                time.sleep(0.01)
              
            if time.perf_counter()-starttime > self.max_time:
                break

        self.channel_data = []  
                
        for i in self.channels:

           
            data = []
            self.port.write("CHAN%i:DATA?" %i)
            answer = self.port.read().split("\r\n")[2:-1]
            for line in answer:
                data.append(float(line.split(",")[1]))
             
            data = np.array(data)
            
            # test if this works                
            # data = np.array(map(float, self.port.read().split(",")))  
                    
            self.channel_data.append(data)
        
        self.port.write("CHAN%i:DATA:HEAD?" % self.channels[0])
        Time_header_data = np.array(self.port.read().split(","))
        self.Time_values = np.linspace(float(Time_header_data[0]), float(Time_header_data [1]), int(Time_header_data[2]))
        

    def call(self):
            
        return [self.Time_values] + self.channel_data

        