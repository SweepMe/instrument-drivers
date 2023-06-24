# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 SweepMe! GmbH
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
# Device: National Instruments VirtualBench Scope


from EmptyDeviceClass import EmptyDevice
import numpy as np

import os
import sys

import win32com

from ErrorMessage import error, debug

from FolderManager import addFolderToPATH
addFolderToPATH()

from pyvirtualbench import PyVirtualBench, PyVirtualBenchException, MsoSamplingMode, MsoInputImpedance, MsoTriggerInstance, MsoTriggerType, MsoAcquisitionStatus, EdgeWithEither

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "VirtualBench"

        self.commands = {}

        self.trigger_sources = {
                                "Channel 1": "mso/1",
                                "Channel 2": "mso/2",
                                }

    
        self.trigger_slopes = {
                                "Rising":  EdgeWithEither.RISING,
                                "Falling": EdgeWithEither.FALLING,
                                "Both":    EdgeWithEither.EITHER,
                                }
       

    def find_ports(self):
    
        class USBdevice(object):
            # created in order to collect all properties in one object
            
            props = [  
                            'Availability',
                            'Caption',
                            'ClassGuid', 
                            'ConfigManagerUserConfig', 
                            'CreationClassName', 
                            'Description',
                            'DeviceID', 
                            'ErrorCleared', 
                            'ErrorDescription',
                            'InstallDate', 
                            'LastErrorCode', 
                            'Manufacturer', 
                            'Name', 
                            'PNPDeviceID', 
                            'PowerManagementCapabilities ',
                            'PowerManagementSupported',
                            'Service', 
                            'Status', 
                            'StatusInfo', 
                            'SystemCreationClassName', 
                            'SystemName',
                            ]
            
            def __init__(self):
            
                self.properties = {}
        
        
        # VirtualBenchPorts
        dev_list = []
        resources = []
        
        try:
        
            objSWbemServices = win32com.client.Dispatch("WbemScripting.SWbemLocator").ConnectServer(".","root\cimv2")
            
            for item in objSWbemServices.ExecQuery("SELECT * FROM Win32_PnPEntity"):
                                
                dev = USBdevice()
                
                for name in dev.props:
                    
                    a = getattr(item, name, None)
                                   
                    if a is not None:
                        try:                    
                            dev.properties[name] = str(a)
                        except:
                            pass
                            
                dev_list.append(dev)      

            VirtualBenchController = {}
            VirtualBenchModels = {}              
                                          
            for dev in dev_list:
            
                if "VID" in dev.properties["DeviceID"] and "PID" in dev.properties["DeviceID"]:
                                      
                    if "VID_3923" in dev.properties["DeviceID"] and dev.properties["Service"] == "usbccgp":

                        VID = dev.properties["DeviceID"].split("\\")[1].split("&")[0].split("_")[1]
                        PID = dev.properties["DeviceID"].split("\\")[1].split("&")[1].split("_")[1]
                        ControllerID = dev.properties["DeviceID"].split("\\")[2]
                        
                        # print("VID:", VID)
                        # print("PID:", PID)
                        # print("ControllerID:", ControllerID)
                        
                        VirtualBenchController[VID+PID] = ControllerID

                    if dev.properties["Name"] != None and "NI VB-" in dev.properties["Name"]:  
                    
                        if "Interface 1 of 4" in dev.properties["Name"]:   
                        
                            VID = dev.properties["DeviceID"].split("\\")[1].split("&")[0].split("_")[1]
                            PID = dev.properties["DeviceID"].split("\\")[1].split("&")[1].split("_")[1]
                            Model = dev.properties["Name"].split(" ")[1].replace("-", "")
                            
                            # print("VID:", VID)
                            # print("PID:", PID)
                            # print("Model:", Model)
                            
                            VirtualBenchModels[VID+PID] = Model

            
            for controller in VirtualBenchController:
                for model in VirtualBenchModels:
                    if controller == model:
                    
                        ID = VirtualBenchModels[model] + "-" + VirtualBenchController[controller]
                        
                        resources.append(ID)
                                                    
        except:
            error("Problems with finding NI Virtual Bench. Please contact support@sweep-me.net")
            
        finally:
            return resources
            
            
    def set_GUIparameter(self):
    
        GUIparameter = {    
                        
                        #Trigger:
                        "TriggerSource": list(self.trigger_sources.keys()),
                        "TriggerSlope": list(self.trigger_slopes.keys()) ,
                        "TriggerLevel": 0.0,
                        "TriggerHysteresis": 0.0,
                        "TriggerDelay": 0.0,
                         
                        #Timing:
                        "TimeRange": ["Time range in s", "Time scale in s/div"],
                        "TimeRangeValue": 1e-3,

                        #Channels:
                        "Channel1": True,
                        "Channel2": False,
                        "Channel1_Name": "Ch1",
                        "Channel2_Name": "Ch2",
                        "Channel1_Range": [5.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01],
                        "Channel2_Range": [5.0, 2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01],
                        "Channel1_Offset": 0.0,
                        "Channel2_Offset": 0.0,
                        "Channel1_Coupling": ["DC", "AC"],
                        "Channel2_Coupling": ["DC", "AC"],
                        "Channel1_Probe": ["1x", "10x"],
                        "Channel2_Probe": ["1x", "10x"],                        
                        #"Average": ["Not supported"],
                        # "Slope": ["Rising", "Falling"],
                        # "Acquisition": ["Continuous", "Single"],
                        }
    
        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):

        # print(parameter)
        
        self.port = parameter["Port"]
        
        try:
            self.sampling_rate = float(parameter["SamplingRate"])
        except:
            self.sampling_rate = 1e5

        self.trigger_source = parameter["TriggerSource"]
        self.trigger_slope = parameter["TriggerSlope"]
        self.trigger_level = float(parameter["TriggerLevel"])
        self.trigger_hysteresis = float(parameter["TriggerHysteresis"])
        self.trigger_delay = float(parameter["TriggerDelay"])

        self.channel1 = parameter["Channel1"]
        self.channel2 = parameter["Channel2"]

        if parameter["TimeRange"] == "Time range in s":
            self.time_range = float(parameter["TimeRangeValue"])
        elif parameter["TimeRange"] == "Time scale in s/div":
            self.time_range = float(parameter["TimeRangeValue"])*8.0 # because there are 8 divisions

        self.channel1_range = float(parameter["Channel1_Range"])
        self.channel2_range = float(parameter["Channel2_Range"])

        # it is unclear whether the number is here the range or the voltage per division
        # We must multiply or divide by 8 for one or the other selected voltage range mode
        if parameter["VoltageRange"] == "Voltage range in V:":
            self.channel1_range = self.channel1_range/2.0
            self.channel2_range = self.channel2_range/2.0
        if parameter["VoltageRange"] == "Voltage scale in V/div:":
            self.channel1_range = self.channel1_range*4.0
            self.channel2_range = self.channel2_range*4.0


        self.channel1_offset = -float(parameter["Channel1_Offset"]) # minus because of definition 
        self.channel2_offset = -float(parameter["Channel2_Offset"])

        self.channel1_coupling = parameter["Channel1_Coupling"]
        self.channel2_coupling = parameter["Channel2_Coupling"]
        
        self.channel1_probe = parameter["Channel1_Probe"]
        self.channel2_probe = parameter["Channel2_Probe"]
        
        
        if self.sampling_rate == "":
            self.sampling_rate = 10000000
            
            
        # self.source = parameter["Trigger"]            
        # self.input = parameter["Slope"]            
        # self.frequency = parameter["Average"]


        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True] # True to plot data
        self.savetype = [True]  # True to save data
        
        if self.channel1:
            self.variables += [parameter["Channel1_Name"]]
            self.units += ["V"]
            self.plottype += [True] # True to plot data
            self.savetype += [True]  # True to save data
            
        if self.channel2:
            self.variables += [parameter["Channel2_Name"]]
            self.units += ["V"]
            self.plottype += [True] # True to plot data
            self.savetype += [True]  # True to save data    
            
              
    def connect(self):
    
        self.VB = PyVirtualBench(self.port)
        
        try:
            self.scope = self.VB.acquire_mixed_signal_oscilloscope(reset=False)
        except:
            self.stop_measurement("VirtualBench with port %s cannot be found." % self.port)
            return False
        
        
    def disconnect(self):
        self.scope.release()
               
    def initialize(self): 
        self.scope.reset_instrument()
        
    def deinitialize(self): 
        self.scope.stop()

    def configure(self):
        
        memory_depth = 838860.0
      
        if self.time_range*self.sampling_rate > memory_depth:
            self.sampling_rate = memory_depth/self.time_range/1.01
            self.messageBox("Due to depth of memory, sampling rate has been reduced to %1.2e samples/s." % self.sampling_rate)
            
        
        if self.sampling_rate <= 15259:
            self.sampling_rate = 15260
            self.messageBox("Minimum sampling rate is %0.0f samples/s." % self.sampling_rate)

        pretrigger_time = 1e-9
        sampling_mode = MsoSamplingMode.SAMPLE #  SAMPLE = 0, PEAK_DETECT = 1
        self.scope.configure_timing(self.sampling_rate, self.time_range, pretrigger_time, sampling_mode)
       
        #self.scope.configure_analog_channel(channel, enable_channel, vertical_range, vertical_offset, probe_attenuation, vertical_coupling)
        # vertical coupling 0 = AC, 1 = DC
        # probe attenuation 1 = 1x, 10 = 10x
       
        vertical_coupling1 = 1 if self.channel1_coupling == "DC" else 0 
        vertical_coupling2 = 1 if self.channel2_coupling == "DC" else 0
        probe_attenuation1 = 1 if self.channel1_probe == "1x" else 10
        probe_attenuation2 = 1 if self.channel2_probe == "1x" else 10
       
        self.scope.configure_analog_channel("mso/1", self.channel1, self.channel1_range, self.channel1_offset, probe_attenuation1, vertical_coupling1)
        self.scope.configure_analog_channel("mso/2", self.channel2, self.channel2_range, self.channel2_offset, probe_attenuation2, vertical_coupling2)

        #def configure_analog_edge_trigger(self, trigger_source, trigger_slope, trigger_level, trigger_hysteresis, trigger_instance):
        self.scope.configure_analog_edge_trigger(   self.trigger_sources[self.trigger_source],
                                                    self.trigger_slopes[self.trigger_slope],
                                                    self.trigger_level,
                                                    self.trigger_hysteresis,
                                                    MsoTriggerInstance.A, # we just use the A trigger
                                                    )
        
        # def configure_trigger_delay(self, trigger_delay)
        # self.scope.configure_trigger_delay(self.trigger_delay)
        
        # def configure_analog_channel_characteristics(self, channel, input_impedance, bandwidth_limit):
        #MsoInputImpedance.ONE_MEGA_OHM = 0 # FIFTY_OHMS = 1

        
        
        
        # channels = self.scope.query_enabled_analog_channels()
        # print("channels", channels)
        #print self.scope.query_analog_channel()
        
        


    def apply(self):
        pass
                           
    def start(self):
        pass
        
    def adapt(self):
        
        # status = self.scope.query_acquisition_status()
        # print(status)
        
        # We have to run the scope for each measurement point as long as it is is in single run mode
        self.scope.run()
        
        
    def measure(self):
        pass
        """
        while True:
        
            # STOPPED = 0
            # RUNNING = 1
            # TRIGGERED = 2
            # ACQUISITION_COMPLETE = 3
        
            status = self.scope.query_acquisition_status()
            if status == MsoAcquisitionStatus.ACQUISITION_COMPLETE:
                break
        """
        
        # self.scope.force_trigger()
        
       
       
    def read_result(self):
    
        analog_data, analog_data_stride, analog_t0, digital_data, digital_timestamps, digital_t0, trigger_timestamp, trigger_reason = self.scope.read_analog_digital_u64()

        # print("Trigger reasons:", trigger_reason)
        # print("Trigger timestamp:", self.VB.convert_timestamp_to_values(trigger_timestamp))
        # print("Analog t0", self.VB.convert_timestamp_to_values(analog_t0))

        self.Ch1 = analog_data[0::analog_data_stride]
        self.Ch2 = analog_data[1::analog_data_stride]
        self.Ch3 = analog_data[2::analog_data_stride]
        self.Ch4 = analog_data[3::analog_data_stride]

        timing = self.scope.query_timing()
        print("timing", timing)
        
    def call(self):
        
        result = [1.0*np.array(np.arange(len(self.Ch1)))/len(self.Ch1)*self.time_range]
        
        if self.channel1:
            result += [np.array(self.Ch1)]
    
        if self.channel2:
            result += [np.array(self.Ch2)]
    
        return result

        
