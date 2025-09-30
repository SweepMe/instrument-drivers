# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022, 2024 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank TU Dresden/Toni Bärschneider for providing the initial version of this driver.

# SweepMe! device class
# Type: Scope
# Device: Red pitaya STEMlab
# Red Pitaya OS: 2.05-37

# TODO
#-> comments
#-> test NOW and Disabled
#-> remove sleeptime stuff

import numpy as np
import time

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

import redpitaya_scpi as scpi
from pysweepme.ErrorMessage import error
from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "STEMlab"
                       
        self.commands = {
            "Channel 1": "CH1",
            "Channel 2": "CH2",
            "External": "EXT",
            "Software": "EXT",
            "Signal": "AWG",
            "Now": "NOW",
            "None": "DISABLED",
            "Rising": "_PE",
            "Falling": "_NE",
            "High voltage": "HV",
            "Low voltage": "LV",
            "Averaged decimation on": "ON", 
            "Averaged decimation off": "OFF",
            }
                        
        self.max_time = 10.0
                        
    def set_GUIparameter(self):
    
        GUIparameter = { 
            "SweepMode": ["None", "Time range in s", "Trigger delay in s"],

            "TriggerSlope": ["Rising", "Falling"],
            "TriggerSource": ["None", "Channel 1", "Channel 2", "External", "Software", "Signal"],
            "TriggerCoupling": ["DC"],
            "TriggerLevel": 0,
            "TriggerDelay": 0.0, 
            "TriggerTimeout": 5.0,
            "TriggerHysteresis": 0.0,

            "Acquisition": ["Averaged decimation on", "Averaged decimation off"],
            "Average": ["1", "2", "4", "8", "16", "32", "64", "128", "256", "512", "1024"],
            "SamplingRateType": ["Samples"],
            "SamplingRate": ["16384", "8192", "4096", "2048", "1024", "512", "256"],

            "TimeRange": ["Time range in s:"],
            "TimeRangeValue": ["131 µs", "262 µs", "524 µs", "1.04 ms", "2.09 ms", "4.19 ms", "8.38 ms", "16.7 ms", "33.5 ms", "67.1 ms", "134 ms", "268 ms", "536 ms", "1.07 s", "2.14 s", "4.29 s", "8.60 s"],
            "TimeOffsetValue": 0.0,
            }
        
        # Channel specific Gui parameter                
        for i in np.arange(2)+1:
            GUIparameter["Channel%i" % i] = False        
            GUIparameter["Channel%i_Name" % i] = "Ch%i" % i
            GUIparameter["Channel%i_Range" % i] = ["Low voltage", "High voltage"]
            GUIparameter["Channel%i_Offset" % i] = "0.0"

        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):
        
        self.sweepmode = parameter["SweepMode"]
        self.ip_address = parameter["Port"]
        
        # Trigger Parameter
        self.triggermode = parameter["TriggerSource"]
        self.triggercoupling = parameter["TriggerCoupling"]
        self.triggerslope = parameter["TriggerSlope"]
        self.triggerlevel = float(parameter["TriggerLevel"])
        self.triggerdelay = float(parameter["TriggerDelay"])
        self.triggertimeout = float(parameter["TriggerTimeout"])
        self.triggerhysteresis = float(parameter["TriggerHysteresis"])
        
        # Time range and aquisition Parameter
        self.timerange = parameter["TimeRangeValue"]
        self.timeoffsetvalue = float(parameter["TimeOffsetValue"])
        self.acquisiton = parameter["Acquisition"]
        self.averages = int(parameter["Average"])
        self.samplingratetype = parameter["SamplingRateType"]
        self.samples = int(parameter["SamplingRate"])
        
        # channel specific
        self.channels = []
        for i in np.arange(2)+1:
            if parameter["Channel%i" % i]:
                # self.channels[i] = parameter["Channel%i" % i]
                self.channels.append(i)
        
        self.channel_names = {}
        self.channel_ranges = {}
        self.channel_offsets = {}
        
        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data
        
        for i in self.channels:
            self.channel_names[i] = parameter["Channel%i_Name" % i]
            self.channel_ranges[i] = parameter["Channel%i_Range" % i]
            self.channel_offsets[i] = float(parameter["Channel%i_Offset" % i])
         
            self.variables.append(self.commands["Channel %i" % i] + " " + parameter["Channel%i_Name" % i])
            self.units.append("V")
            self.plottype.append(True)
            self.savetype.append(True)

    def connect(self):
        self.port = scpi.scpi(self.ip_address)
        
        self.port.write = self.port.tx_txt  # wrap write-scpi command
        self.port.read = self.port.rx_txt   # wrap read-scpi command

        # identification = self.get_identification()
        # print("Identification", identification)
        
        # system_version = self.get_system_version()
        # print("System version:", system_version)
  
    def initialize(self): 
        pass

    def configure(self):
        # general settings

        self.reset_acquisition()  # Reset Device

        self.port.write("ACQ:DATA:Units VOLTS")  # set Units
        
        self.port.write("ACQ:BUF:SIZE?")  # get buffersize from device
        self.buffersize = int(self.port.read())
        self.samplerate = 125e6  # sampling rate
                                                            
        if self.triggermode == "Software":
            self.averages = 1  # no averages in Software synchronization
        
        for i in self.channels:  # set Gain for channels
            self.port.write("ACQ:SOUR{0}:GAIN {1}".format(i, self.commands[self.channel_ranges[i]]))
        
        # time settings
        self.time_settings()
        if self.triggertimeout < (self.buffersize*self.decimation/self.samplerate):
            print("Trigger timeout is to short! This causes trigger issues. Please increase the trigger timeout.")
        
        # trigger settings
        self.trigger_settings()
        
        # send settings to RedPitaya
        self.send_settings()

        # print settings
        # self.settings_status()
        
    def apply(self):
        
        if self.sweepmode == "Time range in s":
            self.timerange = self.value
            self.time_settings()
            self.send_settings()
        
        elif self.sweepmode == "Trigger delay in s":
            self.triggerdelay = self.value
            self.trigger_settings()
            self.send_settings()
        
    def measure(self):

        # creating data list
        self.channel_data = [None for i in self.channels]
        
        for avg in range(self.averages):
        
            # trigger settings
            self.trigger_settings()
            
            # send settings to RedPitaya
            self.send_settings()

            # print settings
            # self.settings_status()
            
            self.start_acquisition()
            self.starttime = time.time()  # set starttime, required for filling buffer

            # self.sleeptime = self.triggerdelay + self.starttime - time.time()  # wait for new trigger event -> fill buffer with data pre trigger data
            # print("sleeptime 1:", self.sleeptime)
            # time.sleep(self.sleeptime if self.sleeptime > 0 else 0)

            while True:
                status = self.get_trigger_status()  # check trigger status
                # print("Trigger status:", status)
                if status == "TD":
                    self.starttime = time.time()
                    break
                elif time.time()-self.starttime > self.triggertimeout:
                    msg = "Red Pitaya Scope Trigger timeout!"
                    raise Exception(msg)

            # OS 2.00-18 or higher
            while True:
                self.port.write("ACQ:TRig:FILL?")
                buffer_fill = self.port.read()
                if buffer_fill == "1":
                    break

            # Waiting for the buffer to fill
            # self.sleeptime = self.timerange - self.triggerdelay + self.starttime - time.time()
            # print("Sleeptime2:", self.sleeptime)
            # time.sleep(max(self.sleeptime, 0))  # wait for filling buffer

            # status = self.get_trigger_status()  # check trigger status
            # print("Trigger status:", status)

            self.read_data()  # reading data
            
            self.stop_acquisition()

        for i in range(len(self.channels)):  # average data and add offsets
            self.channel_data[i] /= self.averages
            self.channel_data[i] += self.channel_offsets[self.channels[i]]
            
        self.stop_acquisition()

        # specify time values
        self.time_values = (np.linspace(0, self.read_samples/self.real_samplerate, len(self.channel_data[0])) +
                            self.triggerdelay + self.timeoffsetvalue)

    def call(self):
        return [self.time_values] + self.channel_data

    # Functions
    
    def read_data(self):
        for i in range(len(self.channels)):
            self.port.write("ACQ:SOUR{0}:DATA:Old:N? {1}".format(self.channels[i], self.read_samples))    #! Check the intended functionality
            self.buffer = self.port.read()
            try:
                self.data = list(map(float, self.buffer.strip('{}\n\r').replace("  ", "").split(',')))
            except:
                self.data = list(map(float, self.buffer.strip('{}ERR!\n\r').replace("  ", "").split(',')))
                print("Error in Readout!")
            if self.channel_data[i] is None:
                self.channel_data[i] = np.array(self.data)
            else:
                self.channel_data[i] += np.array(self.data)

    def trigger_settings(self):
        # create trigger command
        self.triggersource = self.commands[self.triggermode]
        if self.triggersource != "NOW" and self.triggersource != "DISABLED":    #!
            self.triggersource += self.commands[self.triggerslope]

        self.triggerdelaysamples = int(self.triggerdelay*self.real_samplerate+self.buffersize*0.5)

    def time_settings(self):
        # calculates decimation and read samples parameters
        if isinstance(self.timerange, str):
            try:
                self.timerange = float(self.timerange.replace("ms", "e-3").replace("µs", "e-6").replace("ns", "e-9").replace("us", "e-6").replace("s", "").replace(" ", ""))
            except:
                print("Please enter a number for time range. Time range is set to 8.6s")
                self.timerange = 8.6
        
        # calculate decimation factor based on time range
        self.decimation = 2**(int(2 + np.log((self.timerange*self.samplerate)/self.samples)/(np.log(2)))-1)
        
        # set upper limit for decimation
        if self.decimation > 2**16:
            self.decimation = 2**16
        
        # samples per second
        self.real_samplerate = self.samplerate/self.decimation
        
        # calculate samples to read
        self.read_samples = 2 + int(self.timerange*self.real_samplerate)
        
        # upper limit for samples to read
        if self.read_samples > self.buffersize:
            self.read_samples = self.buffersize

    def send_settings(self):
        # Shows current status of RedPitayas settings
        self.port.write("ACQ:DEC {0}".format(self.decimation))                      # set decimation
        self.port.write("ACQ:AVG {0}".format(self.commands[self.acquisiton]))       # set decimation average
        self.port.write("ACQ:TRig {}".format(self.triggersource))                   # set trigger source
        
        if self.triggersource != "NOW" and self.triggersource != "DISABLED":
            self.port.write("ACQ:TRig:LEV {0}".format(self.triggerlevel))           # set trigger level
            self.port.write("ACQ:TRig:HYST {0}".format(self.triggerhysteresis))     # set trigger hysteresis
            self.port.write("ACQ:TRig:DLY {0}".format(self.triggerdelaysamples))    # set trigger delay

    def settings_status(self):
        self.port.write("ACQ:DATA:Units?")                  # Data units
        print("Data Units:", self.port.read())
        self.port.write("ACQ:DEC?")                         # Decimation
        print("Decimation:", self.port.read())
        self.port.write("ACQ:AVG?")                         # Decimation averaging
        print("Averaging:", self.port.read())
        self.port.write("ACQ:TRig:LEV?")                    # Trigger Level
        print("Trigger Level:", self.port.read())
        self.port.write("ACQ:TRig:HYST?")                   # Trigger Hysteresis
        print("Trigger Hysteresis:", self.port.read())
        self.port.write("ACQ:TRig:DLY?")                    # Trigger Delay
        print("Trigger Delay:", self.port.read())
        self.port.write("ACQ:SOUR1:GAIN?")                  # Channel 1 Gain
        print("Channel 1 Gain:", self.port.read())
        self.port.write("ACQ:SOUR2:GAIN?")                  # Channel 2 Gain
        print("Channel 2 Gain:", self.port.read())
        self.port.write("ACQ:TRig:STAT?")                   # Trigger status
        print("Trigger Status:", self.port.read())

    def get_identification(self):
        self.port.write("*IDN?")
        return self.port.read()

    def get_system_version(self):
        self.port.write("SYSTem:VERS?")        #!
        return self.port.read()
        
    def start_acquisition(self):
        self.port.write("ACQ:START")
        
    def stop_acquisition(self):
        self.port.write("ACQ:STOP")

    def reset_acquisition(self):
        self.port.write("ACQ:RST")
        
    def get_trigger_status(self):
        """Returns the trigger status.        
        
        Returns:
            status: 
                -> "WAIT" if not trigger is received yet
                -> "TD" if the measurement was triggered
        """
        
        self.port.write("ACQ:TRig:STAT?")
        return self.port.read()
        
    def set_average(self, state):

        self.port.write("ACQ:AVG %s" % str(state))
        
    def get_average(self):

        self.port.write("ACQ:AVG?")
        return self.port.read()
