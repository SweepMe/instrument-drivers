# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 - 2023 SweepMe! (sweep-me.net)
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
# Device: Ocean Optics USB4000

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

        EmptyDevice.__init__(self)
        
        self.shortname = "USBxxxx"
        
        self.variables = ["Wavelength", "Intensity", "Integration time"]
        self.units = ["nm", "µJ", "s"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        self.calibrationfolder = self.get_folder("CALIBRATIONS")

    def find_Ports(self):

        ports = [str(spec) for spec in sb.list_devices()]

        if isinstance(ports, bool):
            ports = []

        if len(ports) == 0:
            self.message_Box(
                "No spectrometer found. Please make sure it is connected and the hardware driver is installed.")

        # returns a list of ports
        return ports

    def get_CalibrationFile_properties(self, port):
        # returns two string
        # 1 file ending
        # 2 string in file_name

        # Example: USB4F05021_040309.IrradCal

        serialno = str(port[str(port).find(":") + 1:-1])

        if serialno == "":
            serialno = "noserialnumber"

        return [".IrradCal", serialno]

    def get_GUIparameter(self, parameter = {}):
        self.integration_time = parameter["IntegrationTime"]
        self.integration_time_automatic_max = parameter.get("IntegrationTimeMax", 10.0)
        self.sweep_mode = parameter["SweepMode"]
        self.automatic = parameter.get("IntegrationTimeAutomatic", False)
        self.average = parameter["Average"]
        self.device_type = parameter["Port"]
        self.calibration = parameter.get("Calibration", "")
        self.trigger_type = parameter["Trigger"]
        self.trigger_delay = parameter.get("TriggerDelay", 0.0)
        
        if self.calibration == "" or self.calibration == "None":
            self.units = ["nm", "", "s"]
        
    def set_GUIparameter(self):
        gui_parameter = {
                        "Trigger": ["Internal", "External Rising", "External Falling"],
                        "SweepMode": ["None", "Integration time in s"],
                        "IntegrationTime": 0.1,
                        "Average": 1,                       
                        }
        
        return gui_parameter

    def connect(self):
                    
        devices = sb.list_devices()
        
        for i in devices:
            if str(i) == self.device_type:
            
                if self.device_type in self.device_communication:
                    self.spectrometer = self.device_communication[self.device_type]
                else:
                    self.spectrometer = sb.Spectrometer(i)
                    self.device_communication[self.device_type] = self.spectrometer
        try:
            self.spectrometer
        except AttributeError:
            self.stopMeasurement = "Cannot connect to spectrometer."
                        
        #print self.spectrometer.model
        #print self.spectrometer.pixels

    def disconnect(self):
    
        if self.device_type in self.device_communication:
            try:
                self.spectrometer.close()
            except:
                pass
            finally:
                del self.device_communication[self.device_type]
                
        else:
            pass

    def initialize(self):

        self.integration_time = float(self.integration_time)
        self.integration_time_automatic_max = float(self.integration_time_automatic_max)
        self.average = int(self.average)
        self.trigger_delay = float(self.trigger_delay)
        
        self.integration_time_max = 10.0
    
        if self.spectrometer.model == "USB4000":
            self.integration_time_max = 10.0
            
        if self.spectrometer.model == "USB2000PLUS":
            self.integration_time_max = 5.0
            
        if self.spectrometer.model == "USB2000":
            self.integration_time_max = 30.0
        
        self.integration_time_min = self.spectrometer.minimum_integration_time_micros/1e6 # integration time in s

        if self.automatic:
            if self.integration_time_automatic_max > self.integration_time_max:
                self.integration_time_automatic_max = self.integration_time_max
                                          
        self.set_Integration_time()
        
        # self.spectrometer.Averaging = self.average
        
        self.wavelengths = self.read_Wavelengths()
       
        if self.calibration != "" and self.calibration != "None":
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
    
        if self.sweep_mode.startswith("Integration time"):
    
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
            # if self.spectrometer._has_nonlinearity_coeffs and self.spectrometer._has_dark_pixels:
            self.spectrum += np.array(self.spectrometer.intensities(correct_dark_counts=self.spectrometer._has_dark_pixels, correct_nonlinearity=self.spectrometer._has_nonlinearity_coeffs))
            
            if float('inf') in self.spectrum:
                # some spectrometers send an array consisting of inf -inf inf -inf .... although _has_nonlinearity_coeffs is True.
                # Setting _has_nonlinearity_coeffs to False solves the problem, even though the nonlinearity coeffs are not applied anymore
                self.spectrometer._has_nonlinearity_coeffs = False
                self.spectrum = np.array(self.spectrometer.intensities(correct_dark_counts=self.spectrometer._has_dark_pixels, correct_nonlinearity=self.spectrometer._has_nonlinearity_coeffs))
        
        self.spectrum = self.spectrum/self.average*self.Calibration_array
        
        return [self.wavelengths, self.spectrum, self.integration_time]

        
    def read_Integration_time(self):
        pass
        
    def set_Integration_time(self): 
    
        if self.integration_time < self.integration_time_min:
            self.integration_time = self.integration_time_min
            
        if self.integration_time > self.integration_time_max:
            self.integration_time = self.integration_time_max

        self.spectrometer.integration_time_micros(self.integration_time*1e6)

