# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2021 Axel Fischer und Felix Kaschura GbR ("SweepMe!")

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank Heliatek GmbH/Dr. Ivan Ramirez for providing the initial version of this driver.

# SweepMe! device class
# Type: Switch
# Device: Picard Industries USB-Filterwheel

from EmptyDeviceClass import EmptyDevice #sweepMe base class
from ErrorMessage import error #sweepMe utlity
from FolderManager import addFolderToPATH #sweepMe utlity

import time

#deal with dlls
import ctypes #picard instruments dll reading
import struct


#add dlls to path
addFolderToPATH()

class Device(EmptyDevice):

    description =   """
                        <p>USB controlled filter wheel by Picard Industries</p>
                        <p><strong>Usage:</strong></p>
                        <ul>
                        <li>Please replace the placeholder X with your serial number in the field 'Port'.</li>
                        <li>If Sweep mode == "Position", the selected Sweep value is used.</li>
                        <li>If Sweep mode == "None", the position given in the field 'Filter position' is used. It can be used as convenience setting for when no sweep is made (equivalent to one value sweep)</li>
                        <li>Home position: position to return to at end of program ("None" = stay)</li>
                        </ul>
                        <p><strong>Known issues:</strong></p>
                        <p>The repeatability of the filter wheel position is not perfect and cannot be further improved within this driver as it is related to the hardware or the interface library.&nbsp;</p>
                        <p>&nbsp;</p>
                    """

    def __init__(self):
        '''the class file is reloaded everytime sweepMe sequencer starts. --> 
        __init__ is called at each runtime___'''
        EmptyDevice.__init__(self)

        #sweepMe
        self.shortname = "USB Filterwheel"

        self.variables = ["Position"]
        self.units = ["#"]
        self.plottype = [True] # True to plot data
        self.savetype = [False] # True to save data

        #hardware and backend
        self.usb_fw_ptr = None #a pointer to the device
        self.positions = [1,2,3,4,5,6]

        self.errors = { 
                        0: "no error", 
                        1: "PI device not found", 
                        2: "PI object not found",
                        3: "PI cannot create object", 
                        4: "PI invalid dev handle", 
                        5: "Read Timeout",
                        6: "read thread abandoned", 
                        7: "PI read failed", 
                        8: "PI invalid parameter", 
                        9: "PI write fail",
                       }
        
        
    # def find_Ports(self):
        # '''overload base class method to look for system cfg. file instead of ports
        # the cfg. file specifies the USB vendor id from which dll will find appropriate instrument
        
        # Unfortunately sweepMe doesnt allow for user dialog here so we need to make a list using os or glob'''

        # return ["SNXXX"]    
        
    def set_GUIparameter(self):


        GUIparameter = {
                         "Settle delay in ms": 1600,
                         "Port" : "SNXXX",
                         "Filter position" : 1,
                         "Home position" : ["None"] + [str(x) for x in self.positions],
                         "SweepMode": ["Position", "None"],
                        }
        
        return GUIparameter   

    def get_GUIparameter(self, parameter={}):
        
        self.sweepmode = parameter["SweepMode"]
        self.SN = parameter["Port"] #not actually a port, but the serial number

        self.pos = int(parameter["Filter position"])

        self.s_delay = int(parameter["Settle delay in ms"])
        
        self.home = parameter["Home position"]
        
        
        

    def connect(self):
        '''needs to be overloaded like find_ports
        https://wiki.sweep-me.net/wiki/Sequencer_procedure '''
        
        
        ## Loading the dll library
        self.py_arch = struct.calcsize("P")*8
        if self.py_arch == 64:
            self.dll = ctypes.WinDLL(r"PiUsb64.dll") #stdcall covention
        elif self.py_arch == 32:
            self.dll = ctypes.WinDLL(r"PiUsb32.dll") #stdcall convention
        else: #seems very unlikely!
            self.stop_Measurement("Error unexpected python architecture loading picard dll")
            return False
        
        
        ## Repackage the dll functions to get workable returns
        #when pointer is specified in args use byref
        #when c_void_p use c_void_p(handle)
        self.piConnectFilter = self.dll.piConnectFilter
        self.piConnectFilter.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.c_int]
        self.piConnectFilter.restype = ctypes.c_void_p
        
        self.piSetFilterPosition = self.dll.piSetFilterPosition
        self.piSetFilterPosition.argtypes = [ctypes.c_int, ctypes.c_void_p]
        self.piSetFilterPosition.restype = ctypes.c_int
        
        self.piDisconnectFilter = self.dll.piDisconnectFilter
        self.piDisconnectFilter.argtypes = [ctypes.c_void_p]
        
        self.piGetFilterPosition = self.dll.piGetFilterPosition
        self.piGetFilterPosition.argtypes = [ctypes.POINTER(ctypes.c_int),  ctypes.c_void_p]
        self.piGetFilterPosition.restype = ctypes.c_int
        
        ## Serial number format check
        try:
            self.SN = int(self.SN[2:])
        except ValueError:
            self.stop_Measurement("Serial number %s did not have expected SNxxx (x = digit) format" % str(self.SN))
            return False
            
        ## Connect to the filter    
        err = ctypes.c_int(0)
        self.usb_fw_ptr = self.piConnectFilter(ctypes.byref(err), ctypes.c_int(self.SN))
        
        ## Check for errors
        if type(err) != int: 
            err = err.value
        if err !=0:
            self.stop_Measurement("ERROR connectiong to Picard USB FW: %s" % self.errors[err])
            return False
        
    def disconnect(self):
        
        self.piDisconnectFilter(ctypes.c_void_p(self.usb_fw_ptr))
        self.usb_fw_ptr = None
 
    def initialize(self):
        ''' set instrument at GUI selected state and ready for next commands'''
        
        if self.sweepmode != "Position" and not self.pos in self.positions:
            self.stop_Measurement("Filter position %s not in 1-6 range" % str(self.pos))
            return False
            
    def deinitialize(self):

        if self.home != "None":
            self.goto(int(self.home)) #home
            # print("Picard FW SN%s homing to pos %s"%(self.SN, self.home))
           
    
    def configure(self):
        '''apply user option for position in case there is no sweep'''

        if self.sweepmode != "Position":
            self.goto(self.pos)


    def unconfigure(self):
        # close the shutter 
        pass
         

    def apply(self):
    
        if self.sweepmode == "Position":
            self.goto(int(self.value))
            
    def measure(self):
        '''return the current config info - make sure the hardware ID matches your config file
        some commands are multi index - such as the SAM switch wlns'''
        
        self.curr_filter = ctypes.c_int(0)
        err = self.piGetFilterPosition(ctypes.byref(self.curr_filter), ctypes.c_void_p(self.usb_fw_ptr))
        
        # Checking for errors
        if type(err) != int: 
            err = err.value
        if err != 0:
            self.stop_Measurement("ERROR getting Picard USB FW position: %s" % self.errors[err])
            return False    
                    

    def call(self):
    
        return self.curr_filter.value


    def goto(self, pos):
        # print("Picard FW SN%s going to pos %s"%(self.SN, pos))
        self.piSetFilterPosition(ctypes.c_int(pos), ctypes.c_void_p(self.usb_fw_ptr))
        time.sleep(self.s_delay/1000)

                 



        