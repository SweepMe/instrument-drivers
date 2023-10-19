# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018-2020 Axel Fischer (sweep-me.net)
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
# Device: Instrument Systems CAS140


import time
import ctypes
import os
import sys
import numpy as np
from configparser import ConfigParser

import FolderManager
FoMa = FolderManager.FolderManager()

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "CAS140 CT"
        
        self.variables = ["Wavelength", "Intensity", "Integration time"]
        self.units = ["nm", "a.u.", "s"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]
      
      
      
        self.folder = os.path.dirname(__file__)

        self.calibrationsfolder = FoMa.get_path("CALIBRATIONS")
        self.extlibs = FoMa.get_path("EXTLIBS")
        
        if not self.folder in os.environ["PATH"].split(os.pathsep):
            os.environ["PATH"] += os.pathsep + self.folder
        
        spectrum = []

    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["None", "Integration time [s]", "Trigger delay [s]"],
                        "IntegrationTime": 0.1,
                        "Average": 1,
                        "Trigger": ["Internal", "External"],
                        "Filter": ["none0", "ODE1", "ODE2", "ODE3", "ODE4", "none5", "none6", "none7"],
                        }
        
        return GUIparameter
            
    def get_GUIparameter(self, parameter={}):
            
        self.integration_time = float(parameter["IntegrationTime"])
        self.integration_time_automatic_max  = float(parameter["IntegrationTimeMax"])
        self.sweep_mode = parameter["SweepMode"]
        self.automatic = parameter["IntegrationTimeAutomatic"]
        self.iterations = int(parameter["Average"])
        self.device_type = parameter["Port"]
        self.calibration = parameter["Calibration"]        
        self.trigger_type = parameter["Trigger"]
        self.trigger_delay = float(parameter["TriggerDelay"])
        self.filter = parameter["Filter"]
        

        if self.sweep_mode == "Trigger delay [s]":
            self.variables.append("Trigger delay")
            self.units.append("s")
            self.plottype.append(True)
            self.savetype.append(True)
            
            
    def find_Ports(self):
        # returns a list of ports
        # the chosen port is forwarded to initialize where it can be used to start the correct port
    
        try:
            self.CAS4DLL = ctypes.windll.CAS4
      
            self.CAS4DLL.casGetXArray.restype = ctypes.c_float
            self.CAS4DLL.casGetData.restype = ctypes.c_float
                       
        except:
            self.stopMeasurement = "Error for Spectrometer CAS140CT from Instrument Systems: Library CAS4.dll has not been found. Please install SpecWin by Instrument Systems. This should automatically put the required file to C:\\Windows\\system32 (64-bit) or C:\\Windows\\SysWOW64 (32bit). Otherwise, contact Instrument Systems to get the library CAS4.dll and copy it to the before mentioned folders or to the DeviceClass folder %s." % self.folder
            return False
    
    
        ports = []      

        for i in range(self.CAS4DLL.casGetDeviceTypes()):
        
            buf = ctypes.create_string_buffer(40)
            #print(buf)
            self.CAS4DLL.casGetDeviceTypeName(i,buf, ctypes.sizeof(buf))
            #print("----", i, buf.value)           
            
            for j in range(self.CAS4DLL.casGetDeviceTypeOptions(i)):

                self.CAS4_device_option = self.CAS4DLL.casGetDeviceTypeOption(i, j) 
                print(self.CAS4_device_option)
                
                if i == 5:
                    ports.append("CAS140 USB " + str(self.CAS4_device_option))
                if  i == 1:
                    ports.append("CAS140 PCI " + str(self.CAS4_device_option))                
               
        #if len(ports) == 0:
        #    ports.append("CAS140 Testmode")
        #        
        return ports
        
    def get_CalibrationFile_properties(self, port):
        # returns two string
        # 1 file ending
        # 2 string in file_name

        if "CAS140 Testmode" == port:
            return [".isc", ""]
        else:
            # todo generate strings from port to identify correct calibration files
            return [".isc", ""]
                    
                    
    def connect(self):
    
        try:
            self.CAS4DLL = ctypes.windll.CAS4
            
            #print(self.CAS4DLL)
      
            self.CAS4DLL.casGetXArray.restype = ctypes.c_float
            self.CAS4DLL.casGetData.restype = ctypes.c_float
            self.CAS4DLL.casGetVisiblePixels.restype = ctypes.c_int16
            self.CAS4DLL.casGetDeadPixels.restype = ctypes.c_int16
            
            
        except:
            self.stopMeasurement = "Error for Spectrometer CAS140CT from Instrument Systems: Library CAS4.dll has not been found. Please install SpecWin by Instrument Systems. This should automatically put the required file to C:\\Windows\\system32 (64-bit) or C:\\Windows\\SysWOW64 (32bit). Otherwise, contact Instrument Systems to get the library CAS4.dll and copy it to the before mentioned folders or to the public folder 'ExternalLibraries' %s." % self.extlibs
            return False
        
    def initialize(self):   

        if self.calibration == "" or self.calibration == "None":
            self.stopMeasurement = "No calibration files found. Please copy your calibration files to the folder %s. There should be two files with the same name and the endings .isc and .ini for each calibration." % self.calibrationsfolder
        
 
        #self.CAS4DLL.casCreateDeviceEx.argtypes = [ctypes.c_uint, ctypes.c_uint]
        
        calibration_file = self.calibrationsfolder + os.sep + self.calibration
        
        if calibration_file.endswith(".isc"):
            calibration_file_isc = calibration_file
            calibration_file_ini = calibration_file.replace(".isc", ".ini")
        else:
            calibration_file_isc = calibration_file + ".isc"
            calibration_file_ini = calibration_file + ".ini"
        
        isc_file = calibration_file_isc.encode("utf-8")
        ini_file = calibration_file_ini.encode("utf-8")
        
        if self.device_type.split(' ')[-1] == "Testmode":
            self.casID = self.CAS4DLL.casCreateDeviceEx(3, 123456)
        
        else:
            if self.device_type.split(' ')[-2] == "USB":
                self.RegID = str(self.device_type.split(' ')[-1])
                #print(self.RegID)
                self.casID = self.CAS4DLL.casCreateDeviceEx(5, int(self.RegID))
                #print("CasID:", self.casID)
                                
                self.CAS4DLL.casSetCalibrationFileName.argtypes = [ctypes.c_uint,  ctypes.c_char_p]
                self.CAS4DLL.casSetConfigFileName.argtypes = [ctypes.c_uint,  ctypes.c_char_p]
               
        
        #print("iscfile:", isc_file)   
        #print("Calibration file:", self.CAS4DLL.casSetCalibrationFileName(self.casID, isc_file))
        self.CAS4DLL.casSetCalibrationFileName(self.casID, isc_file)

        #print(self.calibrationsfolder + os.sep + self.calibration + ".isc", len(self.calibrationsfolder + os.sep + self.calibration + ".isc"))
        #print("Config file:", self.CAS4DLL.casSetConfigFileName(self.casID, ini_file))
        self.CAS4DLL.casSetConfigFileName(self.casID, ini_file)       
        #Calib = ctypes.create_string_buffer(1000)
        #print("Calibrationfile:", self.CAS4DLL.casGetCalibrationFileName(self.casID, Calib))
        
        #print("Initialize:", self.CAS4DLL.casInitialize(self.casID, ctypes.c_int8(0)))
        self.CAS4DLL.casInitialize(self.casID, ctypes.c_int8(0))
        
        """
        Dest = ctypes.create_string_buffer(1000)
        self.CAS4DLL.casGetErrorMessage(self.casID,Dest,ctypes.sizeof(Dest))
        print("Error:", Dest.value)    
        """
        
        self.pix_visible = self.CAS4DLL.casGetVisiblePixels(self.casID)
        self.pix_dead = self.CAS4DLL.casGetDeadPixels(self.casID)
        
        #print(self.casID)
        #print(self.pix_visible, self.pix_dead)
                                        
        self.integration_time_min = int(self.CAS4DLL.casGetIntTimeMin(self.casID))/1000
        self.integration_time_max = int(self.CAS4DLL.casGetIntTimeMax(self.casID))/1000
        
        if self.automatic or self.sweep_mode == "Integration time [s]":
            if self.integration_time_automatic_max < self.integration_time_max:
                self.integration_time_max = self.integration_time_automatic_max
                                                                              
        self.spectrum = np.empty(self.pix_visible)
        
    def configure(self):
        self.CAS4DLL.casSetAccumulations(self.casID, self.iterations) # set iterations of measurements for averaging
        
        filter_number = int(self.filter[-1])
        self.CAS4DLL.casSetFilter(self.casID, filter_number) # replace filter_number by a number in the range 0...7
        
        self.set_Integration_time()
        
        self.CAS4DLL.casSetShutter(self.casID, 0)
                
    def unconfigure(self):
        self.CAS4DLL.casSetShutter(self.casID,1) # close shutter
        
    def deinitialize(self):
        self.CAS4DLL.casDoneDevice(self.casID)   # unmount the CAS140
        
    def read_Wavelengths(self):
        # must return a list of all wavelengths at which the spectrum is measured
    
        self.wavelengths = np.zeros(self.pix_visible)
                
        for i in np.arange(self.pix_visible):
            #get the intensities don't forget about skipping dead pixels
            self.wavelengths[i] = self.CAS4DLL.casGetXArray(self.casID, ctypes.c_int16(i + self.pix_dead))
            
        return self.wavelengths
        
    def start(self):
        if self.trigger_type == "External":
            self.CAS4DLL.casSetTimeout(self.casID, ctypes.c_int16(30000)) # in ms
            self.CAS4DLL.casSetTriggerSource(self.casID, ctypes.c_int8(3)) # trgFlipFlop (3) set trigger source, positive or negative edge
            self.CAS4DLL.casSetLine1FlipFlop(self.casID, ctypes.c_int8(0))
           
            
        else:
            self.CAS4DLL.casSetTriggerSource(self.casID, 0) # trgSoftware
            
    def apply(self):
        
        if self.sweep_mode == "Integration time [s]":
    
            try:
                self.integration_time = float(self.value)
            except:
                self.messageBox("Reference spectrum not taken. No support for changing integration time.")
                                              
            self.set_Integration_time()
            
        if self.sweep_mode == "Trigger delay [s]": 
            self.trigger_delay = self.value
           
            self.CAS4DLL.casSetDelayTime(self.casID, ctypes.c_int16(int(round(self.trigger_delay*1000.0,0))))
           
            
    def trigger(self):
        self.CAS4DLL.casMeasure(self.casID) # waits until the measurement is done or timeout is reached
        
    def measure(self):

        for i in np.arange(self.pix_visible):
            #get the intensities don't forget about skipping dead pixels
            self.spectrum[i] = self.CAS4DLL.casGetData(self.casID, ctypes.c_int16(i+self.pix_dead))

    def call(self):
    
        results = [self.wavelengths, self.spectrum, self.integration_time] # integration time in s
    
        if self.sweep_mode == "Trigger delay [s]":
            results.append(self.trigger_delay)

        return results 

        
    def read_Integration_time(self):
        self.Integration_time = self.CAS4DLL.casGetIntegrationTime(self.casID) / 1000.0 # integration time in s
        return self.Integration_time
    
    def set_Integration_time(self): 
    
        if not self.automatic:
            if self.integration_time < self.integration_time_min:
                self.integration_time = self.integration_time_min
                
            if self.integration_time > self.integration_time_max:
                self.integration_time = self.integration_time_max
                
            self.CAS4DLL.casSetIntegrationTime(self.casID, ctypes.c_int16(int(round(self.integration_time*1000.0,0)))) # int in ms
        else:
            pass
            #self.integration_time = self.CAS4DLL.setAutoIntegration(self.casID)
        
        
        """
        self.CAS4DLL.mpidIntegrationTime        = 1
        self.CAS4DLL.mpidAverages               = 2
        self.CAS4DLL.mpidTriggerDelayTime       = 3
        self.CAS4DLL.mpidTriggerTimeout         = 4
        self.CAS4DLL.mpidCheckStart             = 5
        self.CAS4DLL.mpidCheckStop              = 6
        self.CAS4DLL.mpidColormetricStart       = 7
        self.CAS4DLL.mpidColormetricStop        = 8
        self.CAS4DLL.mpidACQTime                = 10
        self.CAS4DLL.mpidMaxADCValue            = 11
        self.CAS4DLL.mpidMaxADCPixel            = 12
        self.CAS4DLL.mpidTriggerSource          = 14
        self.CAS4DLL.mpidAmpOffset              = 15
        self.CAS4DLL.mpidSkipLevel              = 16
        self.CAS4DLL.mpidSkipLevelEnabled       = 17
        self.CAS4DLL.mpidScanStartTime          = 18
        self.CAS4DLL.mpidAutoRangeMaxIntTime    = 19
        self.CAS4DLL.mpidAutoRangeLevel         = 20
        self.CAS4DLL.mpidAutoRangeMinLevel      = 20
        self.CAS4DLL.mpidDensityFilter          = 21
        self.CAS4DLL.mpidCurrentDensityFilter   = 22
        self.CAS4DLL.mpidNewDensityFilter       = 23
        self.CAS4DLL.mpidLastDCAge              = 24
        self.CAS4DLL.mpidRelSaturation          = 25
        self.CAS4DLL.mpidPulseWidth             = 27
        self.CAS4DLL.mpidRemeasureDCInterval    = 28
        self.CAS4DLL.mpidFlashDelayTime         = 29
        self.CAS4DLL.mpidTOPAperture            = 30
        self.CAS4DLL.mpidTOPDistance            = 31
        self.CAS4DLL.mpidTOPSpotSize            = 32
        self.CAS4DLL.mpidTriggerOptions         = 33
        self.CAS4DLL.mpidForceFilter            = 34
        self.CAS4DLL.mpidFlashType              = 35
        self.CAS4DLL.mpidFlashOptions           = 36
        self.CAS4DLL.mpidACQStateLine           = 37
        self.CAS4DLL.mpidACQStateLinePolarity   = 38
        self.CAS4DLL.mpidBusyStateLine          = 39
        self.CAS4DLL.mpidBusyStateLinePolarity  = 40
        self.CAS4DLL.mpidAutoFlowTime           = 41
        self.CAS4DLL.mpidCRIMode                = 42
        self.CAS4DLL.mpidObserver               = 43
        self.CAS4DLL.mpidTOPFieldOfView         = 44
        self.CAS4DLL.mpidCurrentCCDTemperature  = 46
        self.CAS4DLL.mpidLastCCDTemperature     = 47
        self.CAS4DLL.mpidDCCCDTemperature       = 48
        self.CAS4DLL.mpidAutoRangeMaxLevel      = 49
        self.CAS4DLL.mpidMultiTrackAcqTime      = 50
        self.CAS4DLL.mpidTimeSinceScanStart     = 51
        self.CAS4DLL.mpidCMTTrackStart          = 52
            
        #AWhat parameter constants for DeviceParameter methods below
        self.CAS4DLL.dpidIntTimeMin              = 101
        self.CAS4DLL.dpidIntTimeMax              = 102
        self.CAS4DLL.dpidDeadPixels              = 103
        self.CAS4DLL.dpidVisiblePixels           = 104
        self.CAS4DLL.dpidPixels                  = 105
        self.CAS4DLL.dpidParamSets               = 106
        self.CAS4DLL.dpidCurrentParamSet         = 107
        self.CAS4DLL.dpidADCRange                = 108
        self.CAS4DLL.dpidADCBits                 = 109
        self.CAS4DLL.dpidSerialNo                = 110
        self.CAS4DLL.dpidTOPSerial               = 111
        self.CAS4DLL.dpidTransmissionFileName    = 112
        self.CAS4DLL.dpidConfigFileName          = 113
        self.CAS4DLL.dpidCalibFileName           = 114
        self.CAS4DLL.dpidCalibrationUnit         = 115
        self.CAS4DLL.dpidAccessorySerial         = 116
        self.CAS4DLL.dpidTriggerCapabilities     = 118
        self.CAS4DLL.dpidAveragesMax             = 119
        self.CAS4DLL.dpidFilterType              = 120
        self.CAS4DLL.dpidRelSaturationMin        = 123
        self.CAS4DLL.dpidRelSaturationMax        = 124
        self.CAS4DLL.dpidInterfaceVersion        = 125
        self.CAS4DLL.dpidTriggerDelayTimeMax     = 126
        self.CAS4DLL.dpidSpectrometerName        = 127
        self.CAS4DLL.dpidNeedDarkCurrent         = 130
        self.CAS4DLL.dpidNeedDensityFilterChange = 131
        self.CAS4DLL.dpidSpectrometerModel       = 132
        self.CAS4DLL.dpidLine1FlipFlop           = 133
        self.CAS4DLL.dpidTimer                   = 134
        self.CAS4DLL.dpidInterfaceType           = 135
        self.CAS4DLL.dpidInterfaceOption         = 136
        self.CAS4DLL.dpidInitialized             = 137
        self.CAS4DLL.dpidDCRemeasureReasons      = 138
        self.CAS4DLL.dpidAbortWaitForTrigger     = 140
        self.CAS4DLL.dpidGetFilesFromDevice      = 142
        self.CAS4DLL.dpidTOPType                 = 143
        self.CAS4DLL.dpidTOPSerialEx             = 144
        self.CAS4DLL.dpidAutoRangeFilterMin      = 145
        self.CAS4DLL.dpidAutoRangeFilterMax      = 146
        self.CAS4DLL.dpidMultiTrackMaxCount      = 147
        """