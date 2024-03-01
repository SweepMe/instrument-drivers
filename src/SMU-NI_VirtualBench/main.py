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
# Type: SMU
# Device: National Instruments Virtual Bench


import os
import sys

from EmptyDeviceClass import EmptyDevice
import numpy as np

import win32com

from ErrorMessage import error, debug

from FolderManager import addFolderToPATH
addFolderToPATH()

from pyvirtualbench import PyVirtualBench, PyVirtualBenchException

class Device(EmptyDevice):

    description = """
                  To use this driver, installation of Virtual Bench hardware driver is needed:
                  https://www.ni.com/de-de/support/downloads/drivers/download.virtualbench-software.html#360047
                  
                  Afterwards Virtual Bench instruments can be found using "Find ports" button.
                  
                  The communication is done via the C library nilcicapi.dll which comes with the driver installation.
                  """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "VirtualBench"
        
        self.variables =["Voltage", "Current", "Voltage, set", "Current, set"]
        self.units =    ["V", "A", "V", "A"]
        self.plottype = [True, True, True, True] # True to plot data
        self.savetype = [True, True, True, True] # True to save data
                        
            
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
                
        GUI_parameter = {
                        "SweepMode" : ["Voltage in V", "Current in A"],
                        "Channel": ["+6V", "+25V", "-25V"],
                        "Compliance": 100e-6,
                        "RouteOut": ["Front"],
                        # "RouteOut" : ["Not supported"],
                        # "Speed": ["Also not supported"],
                        }
                        
        return GUI_parameter
        
    def get_GUIparameter(self, parameter = {}):

        self.device = parameter['Device']
        self.sweepmode = parameter['SweepMode']
        self.protection = float(parameter['Compliance'])
        self.port_str = parameter['Port']
        
        self.channel = u"ps/" + parameter["Channel"]

    def connect(self):

        self.VB = PyVirtualBench(self.port_str)
        self.ps = self.VB.acquire_power_supply()
     
    def disconnect(self):
        self.ps.release()
        
    def initialize(self):
    
        if self.sweepmode.startswith("Voltage"):
            if self.protection < 10e-3:
                self.message_Box("Minimum compliance is 10e-3 A. Compliance has been changed to this value.")
                self.protection = 10e-3
            
            if self.protection > 1.0:
                self.message_Box("Minimum compliance is 1 A. Compliance has been changed to this value.")
                self.protection = 1.0

        elif self.sweepmode.startswith("Current"):
            self.ps.configure_current_output(self.channel, 0.0, self.protection)
    
    
        self.ps.reset_instrument()
                        
        if self.sweepmode.startswith("Voltage"):
            self.ps.configure_voltage_output(self.channel, 0.0, self.protection)
        elif self.sweepmode.startswith("Current"):
            self.ps.configure_current_output(self.channel, 0.0, self.protection)

    def deinitialize(self):
        if self.sweepmode.startswith("Voltage"):
            self.ps.configure_voltage_output(self.channel, 0.0, self.protection)
        elif self.sweepmode.startswith("Current"):
            self.ps.configure_current_output(self.channel, 0.0, self.protection)

    def poweron(self):
        self.ps.enable_all_outputs(True)
        
    def poweroff(self):
        self.ps.enable_all_outputs(False)
                        
    def apply(self):
    
        self.value = float(self.value)

        if self.sweepmode.startswith("Voltage"):
            self.ps.configure_voltage_output(self.channel, self.value, self.protection)
        elif self.sweepmode.startswith("Current"):
            self.ps.configure_current_output(self.channel, self.value, self.protection)

    def measure(self):  
        pass
       
    def call(self):
        
        self.v_set, self.i_set = [i.value for i in self.ps.query_voltage_output(self.channel)]
        
        self.v, self.i = map(float, self.ps.read_output(self.channel)[0:2])
             
        return [self.v, self.i, self.v_set, self.i_set]
        
    def finish(self):
        pass
        
        
        