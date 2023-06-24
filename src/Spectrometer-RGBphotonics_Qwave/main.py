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
# Type: Logger
# Device: RGB photonics Qwave


from EmptyDeviceClass import EmptyDevice
import time
import os
import sys
import numpy as np
import clr

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Qwave"
        
        self.variables = ["Wavelength", "Intensity", "Integration time"]
        self.units = ["nm", "a.u.", "s"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]
                 
    def set_GUIparameter(self):
        GUIparameter = {
                        "SweepMode": ["None", "Integration time [s]"],
                        "Calibration": ["SensitivityCalibration On", "SensitivityCalibration Off"],
                        "IntegrationTime": 0.1,
                        "Trigger": ["Internal", "External Rising", "External Falling"],
                        "Average": 1,
                        }
        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):
        self.integration_time = float(parameter["IntegrationTime"])
        self.integration_time_automatic_max = float(parameter["IntegrationTimeMax"])
        self.sweep_mode = parameter["SweepMode"]
        self.automatic = parameter["IntegrationTimeAutomatic"]
        self.average = int(parameter["Average"])
        self.device_type = parameter["Port"]
        self.calibration = parameter["Calibration"]
        self.trigger_type = parameter["Trigger"]
        self.trigger_delay = float(parameter["TriggerDelay"])  
                   
    def connect(self):
    
        try:    
            clr.AddReference('RgbDriverKit')
            from RgbDriverKit import SimulatedSpectrometer, RgbSpectrometer, SpectrometerStatus
            
        except:
            self.stopMeasurement = "Error for Qwave spectrometer: RgbDriverKit.dll has not been found. Please install the Waves SDK from http://www.rgb-photonics.com/downloads/ and put the dll into the 'External libraries' of your public SweepMe! folder. Furthermore, please check whether access to the file is permitted (right-click -> properties)"
            return False
            
        self.spec_status = SpectrometerStatus
    
        if not ("RGBphotonics_Qwave_port"+self.device_type) in self.device_communication:
           
            if self.device_type == "Simulated spectrometer":
                devices = SimulatedSpectrometer.SearchDevices()
                self.spectrometer = devices[0]
            else:
                devices = RgbSpectrometer.SearchDevices()
                if len(devices) == 1:
                    self.spectrometer = devices[0]
                else:
                    for i in devices:
                        i.Open()
                        if i.DetailedDeviceName == self.device_type:
                            self.spectrometer = i
                            break
                        i.Close()

            self.spectrometer.Open()
            
            self.device_communication["RGBphotonics_Qwave_port"+self.device_type] = self.spectrometer
        
        else:
            self.spectrometer = self.device_communication["RGBphotonics_Qwave_port"+self.device_type]

        
        # print "Model:", self.spectrometer.ModelName
        # print "Serial number:", self.spectrometer.SerialNo
        # print "Device name:", self.spectrometer.DetailedDeviceName
        # print "Temperature:", self.spectrometer.Temperature

    def disconnect(self):
    
        if ("RGBphotonics_Qwave_port"+self.device_type) in self.device_communication:
            self.device_communication["RGBphotonics_Qwave_port"+self.device_type].Close()

    def initialize(self):

        self.integration_time_max = self.spectrometer.MaxExposureTime
        self.integration_time_min = self.spectrometer.MinExposureTime
        
        if self.automatic:
            if self.integration_time_automatic_max > self.integration_time_max:
                self.integration_time_automatic_max = self.integration_time_max
                                          
        self.set_Integration_time()
        
        self.spectrometer.Averaging = int(self.average)
        
        self.wavelengths = self.read_Wavelengths()
        
        if self.calibration == "SensitivityCalibration On":
            self.spectrometer.UseSensitivityCalibration = True
        else:
            self.spectrometer.UseSensitivityCalibration = False
            
        if self.trigger_type == "External Rising" or self.trigger_type == "External Falling":
        
            self.spectrometer.UseExternalTrigger = True
            self.spectrometer.SpectrometerTriggerOptions = 2
            self.spectrometer.ExternalTriggerSource = 1
            
            if self.trigger_type == "External Rising":    
                self.spectrometer.ExternalTriggerRisingEdge = True
            if self.trigger_type == "External Falling":
                self.spectrometer.ExternalTriggerRisingEdge = False
        else:
            self.spectrometer.UseExternalTrigger = False
        
        
    def deinitialize(self):
        pass
        
    def find_Ports(self):
        # returns a list of ports
        # the chosen port is forwarded to initialize where it can be used to start the correct port
    
        try:    
            clr.AddReference('RgbDriverKit')
            from RgbDriverKit import SimulatedSpectrometer, RgbSpectrometer, SpectrometerStatus
            
        except:
            self.abort = "Error for Qwave spectrometer: RgbDriverKit.dll has not been found. Please install the Waves SDK from http://www.rgb-photonics.com/downloads/ and put the dll into the DeviceClass folder %s. Furthermore, please check whether access to the file is permitted (right-click -> properties)" % self.folder
            return False
    
        devices = RgbSpectrometer.SearchDevices()
        
        ports = []
        
        for i in devices:
            i.Open()
            ports.append(i.DetailedDeviceName)
            i.Close()

        if len(ports) == 0:
            devices = SimulatedSpectrometer.SearchDevices()
            for i in devices:
                i.Open()
                ports.append(i.DetailedDeviceName)
                i.Close()
                               
        return ports
        

    def read_Wavelengths(self):
        # must return a list of all wavelengths at which the spectrum is measured

        self.wavelengths = []

        for i in self.spectrometer.GetWavelengths():
            self.wavelengths.append(i)
        
        self.wavelengths = np.asarray(self.wavelengths)
        
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
        
    def trigger(self):
    
        while self.spectrometer.Status != self.spec_status.Idle:
            time.sleep(0.01)
            
        if self.trigger_type == "Internal":       
            self.spectrometer.StartExposure()

    def measure(self):
        while self.spectrometer.Status == self.spec_status.WaitingForTrigger:
            time.sleep(0.01)  
            # if trigger_type == "External": The spectrometer waits for a hardware trigger event. This can freeze the application...
            
    def call(self):
        while self.spectrometer.Status == self.spec_status.TakingSpectrum:
            time.sleep(0.01)
            
        self.spectrum = []

        for i in self.spectrometer.GetSpectrum():
            self.spectrum.append(i)

        #print self.spectrometer.LoadLevel # can be used to adjust the auto level
        self.spectrum = np.asarray(self.spectrum)

        return [self.wavelengths, self.spectrum, self.integration_time]

        
    def read_Integration_time(self):
        pass
        
    def set_Integration_time(self):
        
        if self.integration_time < self.integration_time_min:
            self.integration_time = self.integration_time_min
            
        if self.integration_time > self.integration_time_max:
            self.integration_time = self.integration_time_max
    
        self.spectrometer.ExposureTime = self.integration_time
