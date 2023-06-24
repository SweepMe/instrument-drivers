# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2020 Axel Fischer (sweep-me.net)
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

# The MIT license does not apply to the file he2325u.dll 
# File he2325u.dll from H. Haftmann (https://www-user.tu-chemnitz.de/~heha/basteln/PC/hid-ser.de.htm)

# SweepMe! device class
# Type: Logger
# Device: UT61E



from EmptyDeviceClass import EmptyDevice
import sys, os
import ctypes

class Device(EmptyDevice):

    description = """ """

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "UT61E"
        
        self.variables = ["Value", "Unit", "Display text", "Coupling"]
        self.units = ["", "", "", ""]
        self.plottype = [True, False, False, False] # define if it can be plotted
        self.savetype = [True, True, True, True] # define if it can be plotted

        # use like:
        # unit: readoutdict{switch_position{unit}
        # multiplicator: readoutdict{switch_position{Bereich}}
        self.readout_dict = {
            0 : {
                "unit": "A",
                0: 1e-3,
            },
            1 : {
                "unit": "Diode",
            },
            2 : {
                "unit": "Hz,%",
                0: 1e-2,
                1: 1e-1,
                3: 1e0,
                4: 1e2,
                5: 1e3,
                6: 1e4,
            },
            3 : {
                "unit": "Ohm",
                0: 1e-2,
                1: 1e-1,
                2: 1e0,
                3: 1e1,
                4: 1e2,
                5: 1e3,
                6: 1e4,

            },
            4 : {
                "unit": "°C",
            },
            5 :{
                "unit": "Beep",
            },
            6 : {
                "unit": "F",
                0: 1e-12,
                1: 1e-11,
                2: 1e-10,
                3: 1e-9,
                4: 1e-8,
                5: 1e-7,
                6: 1e-6,
                7: 1e-5,
            },
            9 : {
                "unit": "A",
            },
            11: {
                "unit": "V",
                0: 1e-4,
                1: 1e-3,
                2: 1e-2,
                3: 1e-1,
                4: 1e-5,
            },
            13: {
                "unit": "A",
                0: 1e-8,
                1: 1e-7,
            },
            14: {
                "unit": "ADP",
            },
            15: {
                "unit": "mA",
                0: 1e-6,
                1: 1e-5,
            },
        }
        
        
    def connect(self):
    
        libs_folder = os.path.dirname(os.path.realpath(__file__)) + os.sep + "libs"
        self.lib =  ctypes.windll.LoadLibrary(libs_folder + os.sep + "he2325u.dll")
        
        # FUNC(void) HeEnum(char List[HE_NUM_MAX]);
        devices = ctypes.create_string_buffer(256)
        self.lib.HeEnum(devices)
        # print(devices.value)
        
        # FUNC(HANDLE) HeOpen(int n DEF(0), long baud DEF(0), DWORD FlagsAndAttributes DEF(0));
        self.handle = self.lib.HeOpen(0, 19200, 0)
        # print(self.handle)
        
    def disconnect(self):
    
        ## did not help but could be helpful at some point
        # libHandle =self.lib._handle
        # del self.lib
        # kernel = ctypes.windll.kernel32
        # kernel.FreeLibrary.argtypes = [ctypes.wintypes.HMODULE]
        # kernel.FreeLibrary(libHandle)
        
        ## this line make sure the handle can be renewed during 'connect'
        ctypes.windll.kernel32.CloseHandle(self.handle)

        
    def measure(self):  
        
        # FUNC(int) HeRead(HANDLE h, BYTE *buf, int blen, UINT IntervalTimeOut DEF(50), UINT TotalTimeOut DEF(1000), LPOVERLAPPED o DEF(NULL));
        self.buf_pointer = ctypes.create_string_buffer(14)
        blen = ctypes.c_int(14)
        IntervalTimeOut = ctypes.c_uint(50)
        TotalTimeOut = ctypes.c_uint(1000)
        res = self.lib.HeRead(self.handle, self.buf_pointer, blen, IntervalTimeOut, TotalTimeOut, 0)
                  
        # print(self.buf_pointer.value)
        
        
        
    def call(self):
    
        value = self.get_value(self.buf_pointer.value)
        unit, cal_factor = self.get_unit(self.buf_pointer.value)
        value = value*cal_factor
        
        display_text = self.get_display_text(value, unit)
        
        coupling = self.get_coupling(self.buf_pointer.value)
         
        return [value, unit, display_text, coupling]
        
        
    def get_fourbit(self, b):
        
        bit_string = "{0:{fill}8b}".format(b, fill='0')
        
        return int(bit_string[-4:],2)
        
        
    def get_value(self, b):
    
        # print("value", b)
        number = "" 
        for bit in b[1:6]:
            number += str(self.get_fourbit(bit))
            
        number = int(number)
        
        return number
        
    
    def get_unit(self, b):
    
        
        self.unit_dict = {
                          0 : "A",
                          1 : "Diode",
                          2 : "Hz,%",
                          3 : "Ohm",
                          4 : "°C",
                          5 : "Beep",
                          6 : "F",
                          9 : "A",
                          11: "V, mV",
                          13: "µA",
                          14: "ADP",
                          15: "mA",
                         }
                         
        switch_byte =  self.get_fourbit(b[6])
        range_byte = self.get_fourbit(b[0])
        # print(f"switch_byte:{switch_byte}        range_byte:{range_byte}")

        unit = self.readout_dict[switch_byte]["unit"]
        calibration_factor = self.readout_dict[switch_byte][range_byte]
        # print(unit, calibration_factor)
        
        return unit, calibration_factor


    def get_display_text(self, value, unit):
        
        if value < 1e-9:
            text = "%1.4f p%s" % (value/1e-12, unit)
        elif value < 1e-6:
            text = "%1.4f n%s" % (value/1e-9, unit)
        elif value < 1e-3:
            text = "%1.4f µ%s" % (value/1e-6, unit)
        elif value < 1.0:
            text = "%1.4f m%s" % (value/1e-3, unit)  
        else:
            text = "%1.4f %s" % (value, unit) 
         
        return text
        
        
    def get_coupling(self, b):
        
        coupling = "-"
        
        bit_string = "{0:{fill}8b}".format(b[10], fill='0')
        
        if bit_string[-3] == "1":
            coupling = "AC"
        elif bit_string[-4] == "1":
            coupling = "DC"
        
        return coupling
        
        