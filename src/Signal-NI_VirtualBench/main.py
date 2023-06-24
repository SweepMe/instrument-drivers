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
# Type: Signal
# Device: National Instruments VirtualBench function generator



from EmptyDeviceClass import EmptyDevice
import numpy as np

import os
import sys

import win32com

from ErrorMessage import error, debug

# from pyvirtualbench import PyVirtualBench, PyVirtualBenchException, Waveform, FGenWaveformMode
from FolderManager import addFolderToPATH
addFolderToPATH()

from pyvirtualbench import *

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        # to be defined by user
        self.waveforms = { 
                          "Sine": Waveform.SINE,
                          "Square": Waveform.SQUARE,
                          "Triangle": Waveform.TRIANGLE,
                          "DC": Waveform.DC,
                          "Arbitrary":1,
                        }
        
        self.shortname = 'VirtualBench'
                
                
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
                        "SweepMode": ["Frequency in Hz", "Period in s", "Amplitude in V", "Offset in V", "HiLevel in V", "LoLevel in V", "None"],
                        "Waveform": list(self.waveforms.keys()),
                        "PeriodFrequency" : ["Period in s", "Frequency in Hz"],
                        "AmplitudeHiLevel" : ["Amplitude in V", "HiLevel in V"],
                        "OffsetLoLevel" : ["Offset in V", "LoLevel in V"],
                        # "DelayPhase": ["Phase in deg", "Delay in s"],
                        "DutyCyclePulseWidth": ["Duty cycle in %"], #, "Pulse width in s"],
                        
                        "PeriodFrequencyValue": 1000,
                        "AmplitudeHiLevelValue": 1.0,
                        "OffsetLoLevelValue": 0.0,
                        "DutyCyclePulseWidthValue": 50,
                        "ArbitraryWaveformFile":True,
                        #"DelayPhaseValue": 0,
                        }
                
        return GUIparameter
                  
    def get_GUIparameter(self, parameter={}):
       
        # could be part of the MeasClass
        self.port                       = parameter['Port'] 
        self.sweep_mode                 = parameter['SweepMode'] 
        self.waveform                   = parameter['Waveform'] 
        self.periodfrequency            = parameter['PeriodFrequency']
        self.periodfrequencyvalue       = float(parameter['PeriodFrequencyValue'])
        self.amplitudehilevel           = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue      = float(parameter['AmplitudeHiLevelValue'])
        self.offsetlolevel              = parameter['OffsetLoLevel']
        self.offsetlolevelvalue         = float(parameter['OffsetLoLevelValue'])
        self.dutycyclepulsewidth        = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue   = float(parameter['DutyCyclePulseWidthValue'])
        self.delayphase                 = parameter['DelayPhase']
        self.arbitraryWaveformFilePath = parameter['ArbitraryWaveformFile']
        if self.sweep_mode == 'None':
            self.variables =[]
            self.units =    []
            self.plottype = []     # True to plot data
            self.savetype = []     # True to save data
            
        else:
            self.variables = [self.sweep_mode.split(" ")[0]]
            self.units =  [self.sweep_mode.split(" ")[2]]
            self.plottype = [True]
            self.savetype = [True]
        # print(FGenWaveformMode.ARBITRARY, type(Waveform.SINE))
        # self.fgen.release()
    def connect(self):

        self.VB = PyVirtualBench(self.port)
        self.fgen = self.VB.acquire_function_generator(reset=False)

              
    def initialize(self):  
        pass
        
    def deinitialize(self):
        pass       
        
    def configure(self):
 
        # if self.sweep_mode == "DelayPhase": 
            # self.delayphase = self.value 
        # print(self.waveform)    
        
        if self.periodfrequency.startswith("Period"):
            frequency = 1.0 / self.periodfrequencyvalue
        else:
            frequency = self.periodfrequencyvalue
            
        if self.amplitudehilevel.startswith("Amplitude"):
            amplitude = self.amplitudehilevelvalue
            
            if self.offsetlolevel.startswith("Offset"):
                offset = self.offsetlolevelvalue
            else:
                offset = (self.amplitudehilevelvalue/2.0 + self.offsetlolevelvalue)
              
        else:
            if self.offsetlolevel.startswith("Offset"):
                amplitude = (self.amplitudehilevelvalue - self.offsetlolevelvalue)*2.0
                offset = self.offsetlolevelvalue
            else:
                amplitude = self.amplitudehilevelvalue - self.offsetlolevelvalue
                offset = (self.amplitudehilevelvalue - self.offsetlolevelvalue)/2.0
        
        ###self.fgen.configure_standard_waveform(waveform, amplitude , offset, frequency, duty_cycle)
        

        if self.waveform == "Arbitrary":
            with open(self.arbitraryWaveformFilePath) as file:
                arbitraryWaveform = file.readlines()
                arbitraryWaveform = [float(line.rstrip()) for line in arbitraryWaveform]
            self.fgen.configure_arbitrary_waveform(arbitraryWaveform, 1/frequency)
            # print('hey')    
        else:
            self.fgen.configure_standard_waveform(self.waveforms[self.waveform], amplitude , offset, frequency, self.dutycyclepulsewidthvalue)
            
        self.fgen.run()
            
    def unconfigure(self):
        self.fgen.configure_standard_waveform(self.waveforms[self.waveform], 0.0 , 0.0, 1000, 50.0)
        self.fgen.release()
        self.VB.release()
     

    def apply(self):
    
        if self.sweep_mode.startswith("Frequency"):
            self.periodfrequency = "Frequency in Hz"
            self.periodfrequencyvalue = self.value
            
        elif self.sweep_mode.startswith("Period"):
            self.periodfrequency = "Frequency in Hz"
            self.periodfrequencyvalue = 1.0/self.value

            
        if self.sweep_mode.startswith("Amplitude"):  
            self.amplitudehilevel = "Amplitude in V"
            self.amplitudehilevelvalue = self.value
            
        elif self.sweep_mode.startswith("HiLevel"):
            self.amplitudehilevel = "HiLevel in V"
            self.amplitudehilevelvalue = self.value

               
        if self.sweep_mode.startswith("Offset"): 
            self.offsetlolevel = "Offset in V"
            self.offsetlolevelvalue = self.value   

        elif self.sweep_mode.startswith("LoLevel"):
            self.offsetlolevel = "LoLevel in V"
            self.offsetlolevelvalue = self.value        
        
        if self.sweep_mode == "DelayPhase": 
            self.delayphase = self.value 


        if self.periodfrequency.startswith("Period"):
            frequency = 1.0 / self.periodfrequencyvalue
        else:
            frequency = self.periodfrequencyvalue
            
        if self.amplitudehilevel.startswith("Amplitude"):
            amplitude = self.amplitudehilevelvalue
            
            if self.offsetlolevel.startswith("Offset"):
                offset = self.offsetlolevelvalue
            else:
                offset = (self.amplitudehilevelvalue/2.0 + self.offsetlolevelvalue)
              
        else:
            if self.offsetlolevel.startswith("Offset"):
                amplitude = (self.amplitudehilevelvalue - self.offsetlolevelvalue)*2.0
                offset = self.offsetlolevelvalue
            else:
                amplitude = self.amplitudehilevelvalue - self.offsetlolevelvalue
                offset = (self.amplitudehilevelvalue - self.offsetlolevelvalue)/2.0
                
                
        # self.fgen.configure_standard_waveform(waveform, amplitude , offset, frequency, duty_cycle)
        # self.fgen.configure_standard_waveform(self.waveforms[self.waveform], amplitude , offset, frequency, self.dutycyclepulsewidthvalue)
        if self.waveform == "Arbitrary":
            with open(self.arbitraryWaveformFilePath) as file:
                arbitraryWaveform = file.readlines()
                arbitraryWaveform = [float(line.rstrip()) for line in arbitraryWaveform]
            self.fgen.configure_arbitrary_waveform(arbitraryWaveform, 1/frequency)
            # print('hey2')    
        else:
            self.fgen.configure_standard_waveform(self.waveforms[self.waveform], amplitude , offset, frequency, self.dutycyclepulsewidthvalue)

    def measure(self):
        pass
        

    def call(self):
        if self.sweep_mode == 'None':
            return []
        else:
            return [self.value]
        
