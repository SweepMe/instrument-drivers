# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2019 Axel Fischer (sweep-me.net)
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
# Device: Hamamatsu C12918


import time
import ctypes
import ctypes.wintypes
import os
import numpy as np

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description =   """
                    <p><strong>Features:</strong></p>
                    <ul>
                    <li>Select number of points</li>
                    <li>Change clock between 100 kHz and 1 Mhz</li>
                    <li>Call analog signal, counts or both</li>
                    <li>Use internal or external trigger</li>
                    <li>Return the average of the array if needed</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Requirements:</strong></p>
                    <ul>
                    <li>WRange.dll must be copied into the public SweepMe! folder 'ExternalLibraries'. The file can be found on the CD that is shipped with the acquisition unit.</li>
                    <li>'Find ports' lists the IDs of all detected acquisition units and select the ID of the acquisition unit, you would like to control.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Known issues:</strong></p>
                    <ul>
                    <li>The plot gets unresponsive, if a lot of points (&gt;100.000) are taken and if they are not averaged beforehand.</li>
                    </ul>
                    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "C12918"

        self.variables = ["AD", "CD"]
        self.units = ["", ""]
        self.plottype = [True, True] # define if it can be plotted
        self.savetype = [True, True] # define if it can be plotted
        

    def set_GUIparameter(self):
    
        GUIparameter = {
                        "Points" : 1000,
                        "Trigger" : ["Internal", "External"],
                        "Clock": ["1 MHz", "100 kHz"],
                        "Acquisition": ["Both", "Analog", "Counting"],
                        "Average array": True,
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter):

        self.ID = parameter["Port"]
        
        self.NumberMeasurementPoints = int(parameter["Points"])
        
        if parameter["Trigger"] == "Internal":
            self.trigger_type = 0
        elif parameter["Trigger"] == "External":
            self.trigger_type = 1
        else: # default
            self.trigger_type = 0 
            
        if parameter["Clock"] == "1 MHz":
            self.clock_frequency = 1e6
            self.clock_type = 0
        elif parameter["Clock"] == "100 kHz":
            self.clock_frequency = 1e5
            self.clock_type = 1
        else: # default
            self.clock_frequency = 1e6
            self.clock_type =  0    

        if parameter["Average array"]:
            self.do_average = True
            self.variables = []
            self.units = []
            self.plottype = [] # define if it can be plotted
            self.savetype = [] # define if it can be plotted
        else:
            self.do_average = False
            self.variables = ["Time"]
            self.units = ["s"]
            self.plottype = [True] # define if it can be plotted
            self.savetype = [True] # define if it can be plotted
            
            
        if parameter["Acquisition"] == "Analog":
            self.acquisition_mode = 1
            self.variables += ["Analog value"]
            self.units += [""]
            self.plottype += [True] # define if it can be plotted
            self.savetype += [True] # define if it can be plotted
            
            
        elif parameter["Acquisition"] == "Counting": 
            self.acquisition_mode = 2
            self.variables += ["Counts"]
            self.units += [""]
            self.plottype += [True] # define if it can be plotted
            self.savetype += [True] # define if it can be plotted
           

        else: # default or if "Both" has been selected
            self.acquisition_mode = 3
            self.variables += ["Analog value", "Counts"]
            self.units += ["", ""]
            self.plottype += [True, True] # define if it can be plotted
            self.savetype += [True, True] # define if it can be plotted
            
            
  
    def find_Ports(self):
        
        self.load_DLL()
        handles = self.open_Modules()
        self.close_Module()
        
        if len(handles) > 0:
            return list(map(str, handles.keys()))
        else:
            return ["No acquisition units found!"]
       
        
    ### here functions start that are called during the measurement ###    
        
    def connect(self):
        return self.load_DLL() # stops the measurement if the return value is False
        

    def initialize(self):
    
        self.open_Modules()
        
        if self.ID.isdigit():
            self.get_Handle(int(self.ID))
        else:
            self.stop_Measurement("Please use 'Find ports' and select an ID related to the number adjusted at the C12918 acquisition unit.")
            return False
        
        self.get_ModuleInfo()


    def configure(self):
    
        self.set_SetupInfo(points = self.NumberMeasurementPoints, trigger_type = self.trigger_type, clock_type = self.clock_type)
        
        #self.get_SetupInfo()
        #self.get_Status()
        
        #print(self.handle)
               

    def unconfigure(self):
        pass
        #self.get_Status()
        

    def deinitialize(self):
    
        self.close_Module()
        
        
    def measure(self):
    
        #print(self.handle)
        self.start_Module()
        self.get_Status()
               
        
    def request_result(self):
        
        success, size, self.AD, self.CD = self.read_Data()
        
        self.get_Status()
        
        self.stop_Module()
        

    def call(self):
    
        if self.do_average:
            self.AD = np.average(self.AD)
            self.CD = np.average(self.CD)
            res = []
        else:
            res = [np.arange(self.NumberMeasurementPoints) / self.clock_frequency]
        
        if self.acquisition_mode == 1: #Analog
            res += [self.AD]
            
        elif self.acquisition_mode == 2: #Counter
            res += [self.CD]
           
        else: # default or if "Both" has been selected
            res += [self.AD, self.CD]

        return res




    ### here function start that are not called by SweepMe! during the measurement ###
    
    def load_DLL(self):
    
        #print()
        #print("************* Start Loading DLL ******************")
        
        try:
            self.lib = ctypes.windll.LoadLibrary("WRange.dll")
            return True

        except:
            self.stopMeasurement = "No WRange.dll found. Please put the file into the folder 'External libraries' of the public SweepMe! folder."
            return False
            

    def get_Status(self):

        ### GetStatus ###

        lTimeout = ctypes.c_ulong(10000) # timeout in ms

        state = self.lib.WrlGetStatus(self.handle, lTimeout)
        
        # print()
        # print("GetStatus:", status_description[state])
        
        if state == -1:
            self.get_LastError()
        else:
            return state

    def get_LastError(self):
        
        ### GetLastError ###
        error_code = self.lib.WrlGetLastError()
        
        print()
        print("Error:", error_description[error_code])
        

    def get_Version(self):
    
        ### GetVersion ###
        WRL_LIB_VERSION = ctypes.c_int(0)
        WRL_DRV_VERSION = ctypes.c_int(1)

        print("LibraryVersion", self.lib.WrlGetVersion(WRL_LIB_VERSION))
        print("DriverVersion", self.lib.WrlGetVersion(WRL_DRV_VERSION ))
        
    def open_Modules(self):
    
        # search for up to 16 devices
        nCount_ = 16
        nCount = ctypes.c_uint(nCount_)
        
        # define some argument and results types
        self.lib.WrlOpen.restype = ctypes.c_short
        self.lib.WrlOpen.argtypes = [ctypes.POINTER(ctypes.ARRAY(ctypes.wintypes.HANDLE, nCount_)), ctypes.POINTER(ctypes.ARRAY(ctypes.c_uint, nCount_)), ctypes.c_uint]

        # create a pointer array of Handle objects
        pahWrm = (ctypes.wintypes.HANDLE*nCount_)()
        ctypes.cast(pahWrm, ctypes.POINTER(ctypes.wintypes.HANDLE))
        
        # create a pointer array integer to store the ID
        panIDs = (ctypes.c_uint*nCount_)()
        ctypes.cast(panIDs, ctypes.POINTER(ctypes.c_uint))
        
        # 
        NumberFoundModules = self.lib.WrlOpen(ctypes.byref(pahWrm), ctypes.byref(panIDs), nCount)
        
        #print("Open:", NumberFoundModules)
        
        # create a dictionary that stores IDs and handle objects
        self.handles = {}
        
        if NumberFoundModules == -1:
            self.get_LastError()
            return {}
                    
        for i in range(NumberFoundModules):
            self.handles[panIDs[i]] = ctypes.wintypes.HANDLE(pahWrm[i])
                        
        #print("Handles:", self.handles)
        
        return self.handles
        
    def get_Handle(self, ID):
        
        if ID in self.handles:
            self.handle = self.handles[ID]
            return self.handle
        else:
            return None
        
        
    def get_ModuleInfo(self):

        ### GetModuleInfo ###

        pnModuleID = ctypes.c_uint()
        plMaxPoint = ctypes.c_ulong()

        success = self.lib.WrlGetModuleInfo(self.handle, ctypes.byref(pnModuleID), ctypes.byref(plMaxPoint))
        
        if success == 0:
            self.get_LastError()
        else:
            pass
            #print("GetModuleInfo:", success)
            #print("pnModuleID", pnModuleID)
            #print("plMaxPoint", plMaxPoint)
        
        return success, pnModuleID, plMaxPoint
        
    def set_SetupInfo(self, points = 100, trigger_type = 0, clock_type = 0):
        
        ### SetSetupInfo ###

        lPoint = ctypes.c_ulong(points) #points to be measured
        nTrigger = ctypes.c_uint(trigger_type) #internal trigger
        nClock = ctypes.c_uint(clock_type) # 1 MHz rate
        bPower = ctypes.c_bool() # just for compatibility with previous version, it is not actively used

        success = self.lib.WrlSetSetupInfo(self.handle, lPoint, nTrigger, nClock, bPower)
        
        if success == 0:
            self.get_LastError()
        else:
            pass
            #print()
            #print("SetSetupInfo:", success)

    def get_SetupInfo(self):
    
        ### GetSetupInfo ###
        
        pnTrigger = ctypes.c_uint()
        pnClock = ctypes.c_uint()
        plPoint = ctypes.c_ulong()
        pbPower = ctypes.c_bool()

        success = self.lib.WrlGetSetupInfo(self.handle, ctypes.byref(plPoint), ctypes.byref(pnTrigger), ctypes.byref(pnClock), ctypes.byref(pbPower))

        #print()
        #print("GetSetupInfo:", success)
        
        if success == 0:
            self.get_LastError()
        else:
            pass
            #print("plPoint", plPoint)
            #print("pnTrigger", pnTrigger)
            #print("pnClock",  pnClock)
            #print("pbPower", pbPower)
            
        
    def start_Module(self):
                
        ### Start ###

        #self.lib.WrlStart.restype = ctypes.c_short
        #self.lib.WrlStart.argtypes = [ctypes.POINTER(ctypes.ARRAY(ctypes.wintypes.HANDLE, 1)), ctypes.c_uint]

        handleList = [self.handle]
        
        pahWrm = (ctypes.wintypes.HANDLE * 1)(*handleList)
        nCount = ctypes.c_uint(1)
        
        #print(pahWrm.contents)
        
        success = self.lib.WrlStart(pahWrm, nCount)

        # print()
        # print("Start:", success)
        
        if success == 0:
            self.get_LastError()
        
        return success

    def close_Module(self):
        
        ### Close ###
        # works and return 1 if it was able to close else 0
        success = self.lib.WrlClose()
        # print()
        # print("Close:", success)
        
        if success == 0:
            self.get_LastError()
        
        return success
    
    def stop_Module(self):
        
        ### Stop ###
        success = self.lib.WrlStop()
        # print()
        # print("Stop:", success)
        
        if success == 0:
            self.get_LastError()

        return success
        
    def read_Data(self):
    
        ### Read ###
        
        # nType
        # Specifies the type of measurement data to acquire.
        # ･ WRL_READ_TYPE_AD (1) : Acquires data measured by A/D conversion.
        # ･ WRL_READ_TYPE_CD (2) : Acquires data measured by counter.
        # ･ WRL_READ_TYPE_WD (3) : Acquires A/D converted data and counter data at a time.

        nType = ctypes.c_uint(self.acquisition_mode)
                
        pBuffAD = (ctypes.c_ushort * self.NumberMeasurementPoints)()
        pBuffCD = (ctypes.c_byte * self.NumberMeasurementPoints)()
        pBuffMF = (ctypes.wintypes.PBYTE * self.NumberMeasurementPoints)()
        
        lSize = ctypes.c_ulong(self.NumberMeasurementPoints)
        
        success = self.lib.WrlRead(self.handle, nType, pBuffAD, pBuffCD, pBuffMF, lSize)
        
        while True:
            status  = self.get_Status()
            
            if status == 4:
                break
            else:
                print(status)
                #break
                
            time.sleep(0.01)
            
        AD = np.ndarray((self.NumberMeasurementPoints, ), dtype=np.int16, buffer = pBuffAD, order='C')
        CD = np.ndarray((self.NumberMeasurementPoints, ), dtype=np.int8, buffer = pBuffCD, order='C')

             
        if success == 0:
            self.get_LastError()
            AD = None
            CD = None
            
        else:
            return success, lSize, AD, CD


  
status_description = {
                       -1: "The function failed.(Check detailed error information.)",
                        0: "Idle state",
                        1: "Measurement is in progress.",
                        2: "Measurement is completed.",
                        3: "Data is being acquired.",
                        4: "Data acquisition is complete.",
                     }
                            
# WRL_STATE_ERROR (-1) : The function failed.(Check detailed error information.)
# WRL_STATE_IDLE (0) : Idle state
# WRL_STATE_MEAS_START (1) : Measurement is in progress.
# WRL_STATE_MEAS_COMP (2) : Measurement is completed.
# WRL_STATE_READ_START (3) : Data is being acquired.
# WRL_STATE_READ_COMP (4) : Data acquisition is complete.


error_description = {
                     0 : "Ended successfully",
                     1 : "An unknown error was detected",
                     2 : "No device was found",
                     3 : "No driver was found",
                     4 : "System memory is insufficient",
                     5 : "Device is not ready",
                     6 : "Communication timeout occurred",
                     7 : "An error occurred in library",
                    10 : "Not open",
                    11 : "Already open",
                    12 : "No device was found",
                    13 : "Maximum number of devices exceeded",
                    20 : "Measurement has not started",
                    21 : "Measurement has already started",
                    22 : "Master is not specified",
                    23 : "Two or more masters are specified",
                    30 : "Acquisition has not started",
                    31 : "Acquisition has already started",
                    40 : "Handle is invalid",
                    41 : "Device is invalid",
                    42 : "Function is incorrect",
                    43 : "Parameter is incorrect",
                    }

#･ WRS_SUCCESS ( 0) : Ended successfully.
#･ WRS_UNKNOWN ( 1) : An unknown error was detected.
#･ WRS_NO_DEVICE ( 2) : No device was found.
#･ WRS_NO_DRIVER ( 3) : No driver was found.
#･ WRS_NO_MEMORY ( 4) : System memory is insufficient.
#･ WRS_NOT_READY ( 5) : Device is not ready.
#･ WRS_TIMEOUT ( 6) : Communication timeout occurred.
#･ WRS_LIB_ERROR ( 7) : An error occurred in library.
#･ WRS_NOT_READY_OPEN (10) : Not open.
#･ WRS_ALREADY_OPEN (11) : Already open.
#･ WRS_OPEN_NO_DEVICE (12) : No device was found.
#･ WRS_OPEN_FIND_OVER (13) : Maximum number of devices exceeded.
#･ WRS_NOT_READY_MEASS (20) : Measurement has not started.
#･ WRS_ALREADY_MEAS (21) : Measurement has already started.
#･ WRS_MEAS_NO_MASTER (22) : Master is not specified.
#･ WRS_MEAS_MORE_MASTER (23) : Two or more masters are specified.
#･ WRS_NOT_READY_READ (30) : Acquisition has not started.
#･ WRS_ALREADY_READ (31) : Acquisition has already started.
#･ WRS_INVALID_HANDLE (40) : Handle is invalid.
#･ WRS_INVALID_DEVICE (41) : Device is invalid.
#･ WRS_INVALID_FUNCTION (42) : Function is incorrect.
#･ WRS_INVALID_ARGUMENT (43) : Parameter is incorrect.
