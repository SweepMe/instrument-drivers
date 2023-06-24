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
# Type: Logger
# Device: National Instruments Virtual Bench


from EmptyDeviceClass import EmptyDevice
import numpy as np

import os
import sys

import win32com

from FolderManager import addFolderToPATH
addFolderToPATH()

from ErrorMessage import error, debug

from pyvirtualbench import PyVirtualBench, PyVirtualBenchException, Waveform

class Device(EmptyDevice):

    description = """
                  To use this driver, installation of Virtual Bench hardware driver is needed:
                  https://www.ni.com/de-de/support/downloads/drivers/download.virtualbench-software.html#360047
                  
                  Afterwards Virtual Bench instruments can be found using "Find ports" button.
                  
                  The communication is done via the C library nilcicapi.dll which comes with the driver installation.
                  """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        # to be defined by user
        self.commands = { 
                          "Square": Waveform.SQUARE,
                          "Sine": Waveform.SINE,
                        }
        
        self.shortname = 'VirtualBench'
        
        self.variables = ["Voltage"]
        self.units = ["V"]
        self.plottype = [True] # True to plot data
        self.savetype = [True] # True to save data

        self.modes = {
                        "DC voltage": 0,
                        "AC voltage": 1,
                        "DC current": 2,
                        "AC current": 3,
                        "Resistance": 4,
                        "Diode"     : 5,
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
                        "Mode": list(self.modes.keys()),
                        }
        return GUIparameter
                  
    def get_GUIparameter(self, parameter={}):
        self.port = parameter["Port"]

        self.mode = parameter["Mode"]
        

    def connect(self):

        self.VB = PyVirtualBench(self.port)
        self.mm = self.VB.acquire_digital_multimeter()
            
            
    def initialize(self):
        self.mm.reset_instrument()
        # self.mm.query_dc_voltage()
        # self.mm.query_dc_current()

    def configure(self):
        self.mm.configure_measurement(self.modes[self.mode])
                    
        
    def deinitialize(self):
        self.mm.release()
               

    def apply(self):
        pass
        

    def measure(self):
        pass
        

    def call(self):
        value = self.mm.read()
        return value
        

        
