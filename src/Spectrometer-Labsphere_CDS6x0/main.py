# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
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
# Device: Labsphere CDS6x0

import time
import struct
import ctypes
import os
import sys
import numpy as np
import clr

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "CDS6x0"

        self.variables = ["Wavelength", "Intensity", "Integration time", "Saturation ratio"]
        self.units = ["nm", "a.u.", "s", "%"]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]
           
        self.wavelength_start = 200
        self.wavelength_end = 850
        self.wavelength_step = 1

        self.wavelength_number = int((self.wavelength_end - self.wavelength_start)/self.wavelength_step + 1)
        self.spectrum = np.empty(self.wavelength_number)
        
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["None", "Integration time [s]"],
                        "IntegrationTime": 0.1,
                        "Average": 1,
                        }
                    
        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):
    
        self.device_type = parameter["Port"]
        self.calibration = parameter["Calibration"]
        self.sweep_mode = parameter["SweepMode"]
        self.integration_time = 1000.0 * float(parameter["IntegrationTime"])
        self.integration_time_automatic_max = 1000.0 * float(parameter["IntegrationTimeMax"])
        self.automatic = parameter["IntegrationTimeAutomatic"]
        self.average = int(parameter["Average"])
        self.trigger_type = parameter["Trigger"]
        self.trigger_delay = float(parameter["TriggerDelay"])
        
    def connect(self):
        
        try:
            clr.AddReference("LabsphereLibrary") # Dies fuegt die dll zum Variablenraum von python hinzu, so dass die dll wie ein Modul weiterbearbeitet werden kann
        except:
            self.stopMeasurement = "LabsphereLibrary.dll cannot be loaded. " \
                                   "Please check whether the file is available in the folder 'External libraries' of the public SweepMe! folder. " \
                                   "You can get a copy of this library by contacting Labsphere. " \
                                   "If the file is already there, please change access rights under file properties."
            return False
            
        from Labsphere import SharedLibrary as sl # Einbinden eines Unterpaketes 

        spec = sl.HardwareDevices.Spectrometers.OceanOpticsSpectrometers # hier wird ein Variable gesetzt um nachfolgend einfacher die Funktionen aufrufen zu koennen

        
        if self.device_type == "CDS6x0":
            self.CDS6x0 = spec.CDS6x0("CDS6x0", self.wavelength_start, self.wavelength_end, self.folder)

        if not self.CDS6x0.IsConnected:
            self.CDS6x0.Connect()
            if not self.CDS6x0.IsConnected:
                self.stopMeasurement = "Cannot connect to spectrometer."
                return False
            

    def disconnect(self):
        if self.CDS6x0.IsConnected:
            self.CDS6x0.Disconnect()

    def initialize(self):
    
        self.integration_time_max = self.CDS6x0.MaximumIntegrationTime_mS
        self.integration_time_min = self.CDS6x0.MinimumIntegrationTime_mS
        
        if self.automatic:
            if self.integration_time_automatic_max > self.integration_time_max:
                self.integration_time_automatic_max = self.integration_time_max
                                          
        self.set_Integration_time()
        
        self.CDS6x0.ScansToAverage = self.average
        
        self.wavelengths = self.read_Wavelengths()
        
        
    def deinitialize(self):
        pass
        
    def find_Ports(self):
        # returns a list of ports
        # the chosen port is forwarded to initialize where it can be used to start the correct port
        
        ports = ["CDS6x0"]  
                           
        return ports
        
    def get_CalibrationFile_properties(self, port):
        # returns two string
        # 1 file ending
        # 2 string in file_name

        if "CDS6x0" == port:
            return [".mycalib", ""]
        else:
            # todo generate strings from port to identify correct calibration files
            return [".mycalib", ""]

    def read_Wavelengths(self):
        # must return a list of all wavelengths at which the spectrum is measured
       
        return np.arange(self.wavelength_start, self.wavelength_end + self.wavelength_step, self.wavelength_step)
        
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
        
    def trigger(self):
        self.CDS6x0.RequestAveragedScan()
        
    def measure(self):
        while self.CDS6x0.TakeAveragedScanInProgress:
            time.sleep(0.01)


    def call(self):
    
        scan = self.CDS6x0.LastScanData
       
        satrat = float(scan.SaturationRatio) * 100.0

        spectrum_obj = scan.Spectrum

        #print spectrum_obj.StartLambda
        #print spectrum_obj.EndLambda
        #print spectrum_obj.Length
        #print spectrum_obj.LambdaInterval
        
        data = spectrum_obj.CopyOutDataArray(self.wavelength_start, self.wavelength_end)
        
        for i in np.arange(self.wavelength_number):
            self.spectrum[i] = float(data[0][i])

        return [self.wavelengths, self.spectrum, self.integration_time/1000.0, satrat]

    def read_Integration_time(self):
        pass
        
    def set_Integration_time(self): 
    
        if self.integration_time < self.integration_time_min:
            self.integration_time = self.integration_time_min
            
        if self.integration_time > self.integration_time_max:
            self.integration_time = self.integration_time_max

        self.CDS6x0.SetIntegrationTime_mS(self.integration_time)
