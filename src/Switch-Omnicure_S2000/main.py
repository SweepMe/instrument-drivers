# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2020-2021 Axel Fischer (sweep-me.net)

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

# SweepMe! device class
# Type: Switch
# Device: Omnicure S2000

import os, sys
import time

from EmptyDeviceClass import EmptyDevice
from ErrorMessage import error

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "S2000"
        self.command_attempts = 5
        self.variables = ["Intensity"]
        self.units = ["%"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data
         
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = { "timeout" : 1,
                                 "baudrate": 19200,
                                 "EOL": "\r",
                                 "Exception": False, 
                               }
                               
        self.command_dictionary = { "CONN": "READY",
                                    "DCON": "CLOSED",
                                    "LOC": "Received",
                                    "ULOC": "Received",
                                    "CLR": "Received",
                                    "GUS": "integer",
                                    "RUN": "Received",
                                    "OPN": "Received",
                                    "CLS": "Received",
                                    "TON": "Received",
                                    "TOF": "Received",
                                    "GLH": "integer",
                                    "CLH": "integer",
                                    "GIL": "integer",
                                    "CLC": "Done",
                                    "GTM": "integer",
                                    "VEB": "integer",
                                    "VIO": "integer",
                                    "GSN": "integer",
                                    "GLG": "integer",
                                    "GPW": "integer",
                                    "GIR": "integer",
                                    "GIM": "integer",
                                    "GMP": "integer",
                                    "SIL": "Received",
                                    "STM": "Received",
                                    "SPW": "Received",
                                    "SIR": "Received",
                                    "GPM": "integer",
                                    "SPM": "integer",
                                    }                       
        """
        VEB # get software version from mainboard
        VIO # get software version from i/o board
        GSN # get serial number
        GLG # get light guide diameter
        LOC # lock
        ULOC # unlock
        
        DCON # disconnect
        
        SILn # set iris level n must be an integer number 0 < n <= 100
        TON # Turn on light
        TOF # Turn off light
        GIL # Get iris level (0% - 100%)
        OPN # Open shutter
        
        CLS # Close shutter
        """   

        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Intensity in %"],
                        "Shutdown lamp": False,
                        }
                        
        return GUIparameter
    

    def get_GUIparameter(self, parameter={}):
        self.port_str = parameter["Port"]
        self.shutdown_lamp = parameter["Shutdown lamp"]
        
    def connect(self):
        if ("OmnicureS2000" + self.port_str) in self.device_communication:
            if not self.device_communication["OmnicureS2000" + self.port_str]:
                self.sendCommand("CONN")
                self.device_communication["OmnicureS2000" + self.port_str] = True
        else:
            self.sendCommand("CONN")
            self.device_communication["OmnicureS2000" + self.port_str] = True
        
        
        #self.port.write('CONN18') # or self.sendCommand("CONN")  
        #answer = self.port.read()
        #if answer.startswith("READY0A"):
        #    print("Connection to Omnicure S2000 established")
            
            
        # self.sendCommand('LOC') # lock
    
        
    def initialize(self):
            
         
        self.sendCommand("VEB")   
        self.sendCommand("VIO")   
        self.sendCommand("GSN")
        
        while True:
            if self.get_status()["LampOn"]:
                print("Lamp is on!")
                break
            else:
                self.sendCommand("TON")
                print("Turn on Lamp.")
                time.sleep(1)
        
        print("waiting for Lamp!")
        while True:
            if self.get_status()["LampReady"]:
                print("lamp ready!")
                break
            else:
                time.sleep(1)
        #self.sendCommand("GLG")   
        
        
    # def poweron(self):
        # self.sendCommand("TON") 
    
    # def poweroff(self):
        # self.sendCommand("TOF") 
         
    def deinitialize(self):
        if ("OmnicureS2000" + self.port_str) in self.device_communication:
            if self.device_communication["OmnicureS2000" + self.port_str]:
                for i in range(10):             # needs to be send 10x to change initial properties
                    self.sendCommand("SIL1")
                
                if self.get_status()["ShutterOpen"]:
                    self.sendCommand("CLS")
                    print("omnicure shutter closing...")
                    if self.get_status()["ShutterOpen"]:
                        print("Omnicure shutter still open!!!")
                    else:
                        print("Omnicure shutter closed!")
                
                if self.get_status()["LampOn"] and self.shutdown_lamp:
                    self.sendCommand("TOF")
                    print("Lamp turning off...")
                    if self.get_status()["LampOn"]:
                        print("Lamp still on!!!")
                    else:
                        print("Lamp off.")
                    
                
                self.sendCommand("DCON")
                self.device_communication["OmnicureS2000" + self.port_str] = False
                print("Omnicure disconnected.")
        else:
            print("Omnicure not found in ports!")
        
    def disconnect(self):
        pass
        #self.sendCommand("DCON")  

          
    def apply(self):
        self.iris_level = int(self.value)
        self.set_iris(self.iris_level)
    
        
    def call(self):
        return self.iris_level
        

    def sendCommand(self, cmd):
        
        csum = self.calculate_crc(cmd) 
        sleep_time = 0.2 if "SIL" in cmd else 0.02          
        
        for i in range(self.command_attempts):
            self.port.write(cmd + csum)
            time.sleep(sleep_time)
            try:
                ans = self.port.read()[:-2] # empty the read buffer
            except:
                self.port.write(cmd + csum)
                time.sleep(sleep_time)
                try:
                    ans = self.port.read()[:-2]
                except:
                    self.port.write(cmd + csum)
                    time.sleep(sleep_time)
                    try:
                        ans = self.port.read()[:-2]
                    except:
                        print("Not able to send/read commands to/from Omnicure!")
                        error()
            
            if self.check_command_answer(cmd, ans):
                break
            else:
                if i==(self.command_attempts-1):
                    print("Not able to receive correct answer")
                        
        return ans
        
        
    def check_command_answer(self, cmd, ans):
        for key in self.command_dictionary:
            if key in cmd:
                req_ans = self.command_dictionary[key]
                if req_ans == "integer":
                    try:
                        int(ans)
                        return True
                    except ValueError:
                        print("wrong answer received, expected integer, got: {}".format(ans))
                        return False
                else:
                    if ans == req_ans:
                        return True
                    else:
                        print("wrong answer received. Expected: {0} Got: {1}".format(req_ans, ans))
                        return False
    
    def calculate_crc(self, msg):
    
        checksum = 0x00
        for x in msg:
            index = checksum & 0xFF ^ ord(x) & 0xFF
            checksum = crcTable[index]
        csum=hex(checksum)[2:].upper() 
        if len(csum) == 1:
            
            csum = "0" + csum
        return csum
    
    def get_status(self):
        bit_str = '{0:08b}'.format(int(self.sendCommand("GUS")[:2]))[::-1]
        #print(bit_str)
        status_prop = {"AlarmOn": bit_str[0]==str(1), 
                            "LampOn": bit_str[1]==str(1),
                            "ShutterOpen": bit_str[2]==str(1),
                            "ShutterFault": bit_str[3]==str(1),
                            "LampReady": bit_str[4]==str(1),
                            "LockOn": bit_str[5]==str(1),
                            "Calibration": bit_str[6]==str(1),
                            "ExposureFault": bit_str[7]==str(1),
                            }
        #print(status_prop)
        return status_prop
    
    def set_iris(self, level):
        if level < 0:
            level = 0
            
        if level > 100:
            level = 100
            
        if level == 0:
            if self.get_status()["ShutterOpen"]:
                self.sendCommand("CLS")
                print("omnicure shutter closed")
                
        else:   
            if int(self.sendCommand("GIL")) != level:
                self.sendCommand("SIL%i" % level)
                print("Change iris level.")
            
            if self.get_status()["ShutterOpen"] == False:
                self.sendCommand("OPN")
                print("omnicure shutter opened")
        
            
        


# A specific table has been generated for the Omnicure S2000
# http://www.sunshine2k.de/coding/javascript/crc/crc_js.html
# CRC8_MAXIM
# reflected lookup
# exactly needed for Omnicure S2000
                 
crcTable = (   
                0x00, 0x5E, 0xBC, 0xE2, 0x61, 0x3F, 0xDD, 0x83, 0xC2, 0x9C, 0x7E, 0x20, 0xA3, 0xFD, 0x1F, 0x41, 
                0x9D, 0xC3, 0x21, 0x7F, 0xFC, 0xA2, 0x40, 0x1E, 0x5F, 0x01, 0xE3, 0xBD, 0x3E, 0x60, 0x82, 0xDC, 
                0x23, 0x7D, 0x9F, 0xC1, 0x42, 0x1C, 0xFE, 0xA0, 0xE1, 0xBF, 0x5D, 0x03, 0x80, 0xDE, 0x3C, 0x62, 
                0xBE, 0xE0, 0x02, 0x5C, 0xDF, 0x81, 0x63, 0x3D, 0x7C, 0x22, 0xC0, 0x9E, 0x1D, 0x43, 0xA1, 0xFF, 
                0x46, 0x18, 0xFA, 0xA4, 0x27, 0x79, 0x9B, 0xC5, 0x84, 0xDA, 0x38, 0x66, 0xE5, 0xBB, 0x59, 0x07, 
                0xDB, 0x85, 0x67, 0x39, 0xBA, 0xE4, 0x06, 0x58, 0x19, 0x47, 0xA5, 0xFB, 0x78, 0x26, 0xC4, 0x9A, 
                0x65, 0x3B, 0xD9, 0x87, 0x04, 0x5A, 0xB8, 0xE6, 0xA7, 0xF9, 0x1B, 0x45, 0xC6, 0x98, 0x7A, 0x24, 
                0xF8, 0xA6, 0x44, 0x1A, 0x99, 0xC7, 0x25, 0x7B, 0x3A, 0x64, 0x86, 0xD8, 0x5B, 0x05, 0xE7, 0xB9, 
                0x8C, 0xD2, 0x30, 0x6E, 0xED, 0xB3, 0x51, 0x0F, 0x4E, 0x10, 0xF2, 0xAC, 0x2F, 0x71, 0x93, 0xCD, 
                0x11, 0x4F, 0xAD, 0xF3, 0x70, 0x2E, 0xCC, 0x92, 0xD3, 0x8D, 0x6F, 0x31, 0xB2, 0xEC, 0x0E, 0x50, 
                0xAF, 0xF1, 0x13, 0x4D, 0xCE, 0x90, 0x72, 0x2C, 0x6D, 0x33, 0xD1, 0x8F, 0x0C, 0x52, 0xB0, 0xEE, 
                0x32, 0x6C, 0x8E, 0xD0, 0x53, 0x0D, 0xEF, 0xB1, 0xF0, 0xAE, 0x4C, 0x12, 0x91, 0xCF, 0x2D, 0x73, 
                0xCA, 0x94, 0x76, 0x28, 0xAB, 0xF5, 0x17, 0x49, 0x08, 0x56, 0xB4, 0xEA, 0x69, 0x37, 0xD5, 0x8B, 
                0x57, 0x09, 0xEB, 0xB5, 0x36, 0x68, 0x8A, 0xD4, 0x95, 0xCB, 0x29, 0x77, 0xF4, 0xAA, 0x48, 0x16, 
                0xE9, 0xB7, 0x55, 0x0B, 0x88, 0xD6, 0x34, 0x6A, 0x2B, 0x75, 0x97, 0xC9, 0x4A, 0x14, 0xF6, 0xA8, 
                0x74, 0x2A, 0xC8, 0x96, 0x15, 0x4B, 0xA9, 0xF7, 0xB6, 0xE8, 0x0A, 0x54, 0xD7, 0x89, 0x6B, 0x35,
            )