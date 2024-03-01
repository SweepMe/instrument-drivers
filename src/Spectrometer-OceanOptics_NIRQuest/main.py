# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 - 2023 Axel Fischer (sweep-me.net)
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
# Type: Spectrometer
# Device: Ocean Optics NIR

import time
import os
import sys
import numpy as np

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

import seabreeze.spectrometers as sb

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        super().__init__()
        
        self.shortname = "NIRQuest"
        
        self.variables = ["Wavelength", "Intensity", "Integration time", "Temperature"]
        self.units = ["nm", "uJ", "s", "K"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        self.calibrationfolder = self.get_folder("CALIBRATIONS")
         
    def get_GUIparameter(self, parameter = {}):
        self.integration_time = float(parameter["IntegrationTime"])        
        self.integration_time_automatic_max = float(parameter.get("IntegrationTimeMax", 10.0))
        self.sweep_mode = parameter["SweepMode"]
        self.automatic = parameter.get("IntegrationTimeAutomatic", False)
        self.average = int(parameter["Average"])
        self.device_type = parameter["Port"]
        self.calibration = parameter.get("Calibration", "")
        self.trigger_type = parameter["Trigger"]
        self.trigger_delay = float(parameter.get("TriggerDelay", 0.0))
        
    def set_GUIparameter(self):
        GUIparameter = {
                        "Trigger": ["Internal", "External Rising", "External Falling"],
                        "SweepMode": ["None", "Integration time [s]"],
                        "IntegrationTime": 0.1,
                        "Average": 1, 
                        }
        
        return GUIparameter
        
    def find_Ports(self):
    
        ports = [str(spec) for spec in sb.list_devices()]
    
        # returns a list of ports
        # the chosen port is forwarded to initialize where it can be used to start the correct port
                               
        return ports
        
                   
    def get_CalibrationFile_properties(self, port):
        # returns two string
        # 1 file ending
        # 2 string in file_name

        serialno = str(port[str(port).find(":")+1:-1])
        
        if serialno == "":
            serialno = "noserialnumber"
            

        return [".IrradCal", serialno]

        # Exemplary Calibrationfile
        # USB4F05021_040309.IrradCal
     
                   
    def connect(self):
                    
        devices = sb.list_devices()
        
        for i in devices:
            if str(i) == self.device_type:
                self.spectrometer = sb.Spectrometer(i)    
        try:
            self.spectrometer
        except AttributeError:
            self.stopMeasurement = "Cannot connect to spectrometer."
                        
        #print self.spectrometer.model
        #print self.spectrometer.pixels

    def disconnect(self):
        self.spectrometer.close()

    def initialize(self):
        
        self.integration_time_max = 10.0
    
        if self.spectrometer.model ==  "USB4000":
            self.integration_time_max = 10.0
            
        if self.spectrometer.model ==  "USB2000PLUS":
            self.integration_time_max = 5.0
            
        if self.spectrometer.model ==  "USB2000":
            self.integration_time_max = 30.0
        
        self.integration_time_min = self.spectrometer.minimum_integration_time_micros/1e6 # integration time in s

        if self.automatic:
            if self.integration_time_automatic_max > self.integration_time_max:
                self.integration_time_automatic_max = self.integration_time_max
                                          
        self.set_Integration_time()
        
        # self.spectrometer.Averaging = self.average
        
        self.wavelengths = self.read_Wavelengths()
       
        if self.calibration != "":
            calibration_file = self.calibrationfolder + os.sep + self.calibration

            if not calibration_file.endswith(".IrradCal"):
                calibration_file += ".IrradCal"
            
            IrradCal=np.loadtxt(calibration_file,skiprows=9) # Ocean Optics file
            self.Calibration_array = IrradCal[:,1]
        else:
            self.Calibration_array = np.ones(self.spectrometer.pixels)
       
        if self.spectrometer.pixels != len(self.Calibration_array):
            self.stopMeasurement = "Check your calibration file. Number of pixels is not equal to the pixels your spectrometer has."
        
    def deinitialize(self):
        pass
        
    def read_Wavelengths(self):
        # must return a list of all wavelengths at which the spectrum is measured
        self.wavelengths = self.spectrometer.wavelengths()
        
        return self.wavelengths
        
    def start(self):
        # do some preliminary stuff to prepare the measurement
        pass
        
    def apply(self):
    
        if self.sweep_mode == "Integration time [s]":
    
            try:
                self.integration_time = float(self.value)
            except:
                self.messageBox("Reference spectrum not taken. No support for changing integration time.")
                                              
            self.set_Integration_time()

    def measure(self):
        pass        
                
    def call(self):
    
        self.spectrum = np.zeros(len(self.wavelengths))
        
        for i in np.arange(self.average):
            self.spectrum += np.array(self.spectrometer.intensities(correct_dark_counts=False, correct_nonlinearity=True))
        
        self.spectrum = self.spectrum/self.average*self.Calibration_array
        
        temperature =  self.spectrometer.tec_get_temperature_C() + 273.15
        
        return [self.wavelengths, self.spectrum, self.integration_time, temperature]

        
    def read_Integration_time(self):
        pass
        
    def set_Integration_time(self): 
    
        if self.integration_time < self.integration_time_min:
            self.integration_time = self.integration_time_min
            
        if self.integration_time > self.integration_time_max:
            self.integration_time = self.integration_time_max

        self.spectrometer.integration_time_micros(self.integration_time*1e6)

