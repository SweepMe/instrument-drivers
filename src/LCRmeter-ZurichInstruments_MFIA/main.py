# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2020 - 2021 Axel Fischer (sweep-me.net)
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
# Type: LCRmeter
# Device: ZurichInstruments MFIA

import numpy as np

from FolderManager import addFolderToPATH
addFolderToPATH()  # needed to import zhinst from libs folder of this device class

from zhinst import ziPython as ziP
__api_level__ = 6 #developed on 6

from collections import OrderedDict

import time

from ErrorMessage import error

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "MFIA"
        
        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units     = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype  = [True, True, True, True] # True to plot data
        self.savetype  = [True, True, True, True] # True to save data
        
        self.timeout_autorange = 20 # in s
        self.sampling_rate = 10.0 # in 1/s
                  
    def find_Ports(self):
        '''use ZI api to find IDs of all devices it can access - USB comm requires driver install'''
        
        dev_explorer = ziP.ziDiscovery()
        devs = dev_explorer.findAll()

        return devs
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        
                        
                        "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A"],
                        "StepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A"],
                        
                        "ValueTypeRMS": ["Voltage RMS in V:", "Current RMS in A:"],
                        "ValueRMS": 0.02,
                        
                        "ValueTypeBias": ["Voltage bias in V:" , "Current bias in A:"],
                        "ValueBias": 0.0,
                        
                        "Frequency": 1000.0,
                        
                        "OperatingMode": ["4-Terminal", "2-Terminal"],
                        
                        
                        "Average": ["1", "2", "4", "8", "16", "32", "64"],
                        # "ALC": ["On", "Off"],
                        "Integration": ["Short -> medium precision", "Medium -> high precision ", "Long -> very high precision"], 

                        # "Trigger": ["Internal", "External"],
                        }
                        
        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
    
        self.devID = str(parameter["Port"]).lower()
    
        self.sweepmode = parameter['SweepMode']
        self.stepmode = parameter['StepMode']
        
        self.ValueTypeRMS = parameter['ValueTypeRMS']
        self.ValueRMS = float(parameter['ValueRMS'])
        
        self.ValueTypeBias = parameter['ValueTypeBias']
        self.ValueBias = float(parameter['ValueBias'])
        
        # self.ALC = parameter['ALC']
        self.integration = parameter['Integration']
        self.average = int(parameter['Average'])
        self.frequency = float(parameter['Frequency'])
        
        self.OperatingMode = 0 if parameter['OperatingMode'] == "4-Terminal" else 1
                    
        # self.trigger_type = parameter["Trigger"]
        
        
        
    def connect(self):
        dev_explorer = ziP.ziDiscovery()
        dev_explorer.find(self.devID)
        cpars = dev_explorer.get(self.devID) 
        if cpars ['apilevel'] != __api_level__:
            print("MFIA lockin warning: api level {i} does not match driver level (6)".format(cpars['apilevel']))
        
        self.daq = ziP.ziDAQServer(cpars['serveraddress'], cpars['serverport'], cpars['apilevel']) #make API session 
        self.daq.connectDevice(self.devID, cpars['interfaces'][0]) #blocking
        
        self.polling_topic = '/%s/imps/0/sample' % (self.devID)
        
        
    def disconnect(self):
        if self.daq:
            self.daq.disconnectDevice(self.devID)

    def initialize(self):
        
        imp_index = 0
        self.curr_index = self.daq.getInt("/%s/imps/%d/current/inputselect" % (self.devID, imp_index))
        self.volt_index = self.daq.getInt("/%s/imps/%d/voltage/inputselect" % (self.devID, imp_index))

            
    def deinitialize(self):
        pass
    

    def configure(self):
    
        retries = 5
        for i in range(retries):
            if self.subscribe_polling_topic():
                break # we can go ahead if the subscribing worked
                
            if i == retries-1: # If there was no success, we stop the measurement at the last retry
                self.stop_Measurement("Unable to subscribe to topic during configure with %i retries" % retries)
                return False
   
        
        # we first collect all settings in a list and send it at the end set them at the end of this function
        settings = []
        
           
       
        # integration and average
        if self.integration.startswith("Short"):
            settings += [
                            ['/%s/system/impedance/precision' % (self.devID), 0],
                        ]
        elif self.integration.startswith("Medium"):
            settings += [
                            ['/%s/system/impedance/precision' % (self.devID), 1],
                        ]
        elif self.integration.startswith("Long"):
            settings += [
                            ['/%s/system/impedance/precision' % (self.devID), 2],
                        ]



        # Cable correction
        settings += [
                        ['/%s/system/impedance/calib/cablelength' % (self.devID), 0],  # cable length correction switched off, feature can be added/changed later
                    ]
  #      
  #      #ALC
  #      settings += [
  #                      ['/%s/????' % (self.devID), 1],
  #                  ]



        settings += [   
                        ['/%s/imps/0/enable/on' % (self.devID), 1],                     # enable impedance measurement, necessary if MFLI is used or if it was disabled beforehand.
                        ['/%s/imps/0/mode' % (self.devID), self.OperatingMode],         # 4-Terminal (0) or 2-Terminal (1)
                        ['/%s/imps/0/auto/inputrange' % (self.devID), 1],               # inputrange is dynamically adjusted for best measurements
                        
                        ['/%s/demods/0/rate' % (self.devID), self.sampling_rate],       # Sampling rate in 1/s
                        
                        ['/%s/imps/0/auto/bw' % (self.devID), 1],                       # automatic bw
                        ['/%s/imps/0/freq' % (self.devID), self.frequency],             # oscillator frequency
                        ['/%s/imps/0/bias/value' % (self.devID), self.ValueBias],       # bias voltage
                        ['/%s/imps/0/output/amplitude' % (self.devID), self.ValueRMS],  # oscillator signal                     
                    ]
        
        
        


  #      # trigger
  #      if self.trigger_type == "Internal":
  #          settings += [
  #                          ['/%s/????' % (self.devID), 1],
  #                      ]
  #      elif self.trigger_type == "External":
  #          settings += [
  #                          ['/%s/????' % (self.devID), 1],
  #                      ]
  #      else:
  #          settings += [
  #                          ['/%s/????' % (self.devID), 1],
  #                      ]
            

        self.daq.set(settings)
        self.daq.sync()
        
        self.time_constant = self.daq.getDouble('/%s/demods/0/timeconstant' % self.devID)
        

    def unconfigure(self):
    
        self.daq.unsubscribe('*')  # unsubscribing all topics
        
        settings = [
                        ['/%s/imps/0/bias/value' % (self.devID), 0.0],        # bias value back to 0 V
                        ['/%s/imps/0/output/amplitude' % (self.devID), 0.02], # oscillator signal back to small value
                    ]
           
        self.daq.set(settings)
        self.daq.sync()
        
    def poweron(self):
    
    
        settings = [
                        ['/%s/imps/0/output/on' % (self.devID), 1],        # output on
                    ]
           
        self.daq.set(settings)
        self.daq.sync()


    def poweroff(self):
        
        settings = [
                        ['/%s/imps/0/output/on' % (self.devID), 0],        # output off
                    ]
           
        self.daq.set(settings)
        self.daq.sync()
          
          
    def apply(self):
    
        settings = []
    
        if self.sweepmode != "None":
        
            self.sweepvalue = float(self.value)
        
            if self.sweepmode.startswith("Frequency"):
            
                settings += [
                                ['/%s/imps/0/freq' % (self.devID), self.sweepvalue],
                            ]
                            
                self.frequency = self.sweepvalue
                 
                if self.stepmode != "None":
                
                    self.stepvalue = float(self.stepvalue)

                    settings += [
                                    ['/%s/imps/0/bias/value' % (self.devID), self.stepvalue],
                                ]

            else:
              
                settings += [
                                ['/%s/imps/0/bias/value' % (self.devID), self.sweepvalue],
                            ]
                    
                if self.stepmode.startswith("Frequency"): 
                    self.stepvalue = float(self.stepvalue)
                     
                    settings += [
                                    ['/%s/imps/0/freq' % (self.devID), self.stepvalue],
                                ]
                               
                    self.frequency = self.stepvalue
                    
                            
        if len(settings) > 0:
            self.daq.set(settings)           
            self.daq.sync()
            
            self.time_constant = self.daq.getDouble('/%s/demods/0/timeconstant' % self.devID)
        
            # print("Time constant:", self.time_constant)
            
    def adapt(self):

        ## 1. we make sure the range is correct
        ## even if 'apply' is not called, external changes might necessitate to trigger autorange again
        trigger_auto_ranging = [
                                    ["/%s/currins/%d/autorange" % (self.devID, self.curr_index), 1],
                                    ["/%s/sigins/%d/autorange" % (self.devID, self.volt_index), 1],
                                ]
                                
        self.daq.set(trigger_auto_ranging)

        t_start = time.time()
        
        finished = False

        while not finished:
            time.sleep(0.01) # to proceed as soon as possible if autoranging has finished
            currins_autorange = self.daq.getInt("/%s/currins/%d/autorange" % (self.devID, self.curr_index))
            sigins_autorange = self.daq.getInt("/%s/sigins/%d/autorange" % (self.devID, self.volt_index))
            
            # We are finished when both nodes have been set back to 0 by the device.
            finished = (currins_autorange == 0) and (sigins_autorange == 0)
            
            if time.time() - t_start > self.timeout_autorange:
                self.stop_Measurement("Unable to autorange before timeout.")
                return False
        
        ## 2. We poll a new value to make sure new values have been arrived
        self.daq.sync() #  needed to empty the buffer

        poll_length = 0.01  # in s, we poll quickly as we want to know when the first value is available
        poll_timeout = 5000  # in ms, in case there is no value, we wait 5000 ms to wait for a new value
        poll_flags = 0
        poll_return_flat_dict = True
        data = self.daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)
        
        # print("First new data after autorange:")
        # print(data)
        
        ## 3. after a new value can be polled, we have to wait for the settling time to have good values in 'measure'
        time.sleep(16.0 * self.time_constant)

    def measure(self):
     
        self.daq.sync() #  needed to empty the buffer, as we don't want to have values from the settling process

        poll_length = (self.average+0.1)/self.sampling_rate # we poll as many values as needed to do the average. 0.1 is added to make sure we have exactly the number of values for averaging or even one more.
        poll_timeout = 10000  # [ms] # in case there is no value, we wait 10000 ms to wait for a new value
        poll_flags = 0
        poll_return_flat_dict = True
        data = self.daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)

        Z = np.mean(data[self.polling_topic]['z']) # we take the average of all polled values
        
        self.R = Z.real
        self.X = Z.imag
        self.F = np.mean(data[self.polling_topic]['frequency']) # we take the last frequency value
        self.Bias = self.daq.get('/%s/imps/0/bias/value' % (self.devID))[self.devID]['imps']['0']['bias']['value']['value'][0]
                       
                       
    def call(self):     
        return [self.R, self.X, self.F, self.Bias]
        

    """ convenience functions """
    
    def subscribe_polling_topic(self):
        """ subscribe to the polling topic """
        
        try:
            # self.daq.getAsEvent(self.polling_topic)
            self.daq.subscribe(self.polling_topic)
            return True
        except:
            error("Unable to subscribe polling topic of Zurich Instrument MFIA") # prints the error message
            return False
        
        
