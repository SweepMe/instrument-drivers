# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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
#
# The following DLL files CmdLib3502.dll, NpChopperLib.dll, NpChopperLibWrap.dll,
# and NpHIDLib.dll have been kindly provided by MKS Instruments, Inc. and are not
# part of the above MIT License. If you like to redistribute this driver please 
# make sure your are allowed to ship the DLL files as well.

# Contribution: We like to thank TU Dresden/Jonas Kublitski for providing the initial version of this driver.


# SweepMe! device class
# Type: Switch
# Device: Newport 3502 Optical Chopper

import numpy as np
import time 
import clr
import os
from System.Text import StringBuilder

from EmptyDeviceClass import EmptyDevice  # SweepMe! base class

from ErrorMessage import error, debug


class Device(EmptyDevice):

    description = """ 
                    <p>Driver for Newport Model 3502 Optical Chopper</p>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Applied frequencies are always round to integers.</li>
                    <li>In the folder of the driver, you need allow file access for the dll files in the libs folder. 
                    Right click on the .dll files and select "Properties".<br /> --&gt; under tab 'General' check the 
                    checkbox "Unblock" or "Allow permisison"</li>
                    <li>The frequency range depends on the installed wheel, please consult the manual.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Acknowledgement:</strong></p>
                    <p>DLL files that are shipped with this driver are kindly provided by MKS Instruments, Inc.</p>
                  """

    def __init__(self):

        EmptyDevice.__init__(self)
        
        # Short name in sequencer
        self.shortname = "Newport 3502"

        self.frequencies = {
            "SYNC IN": 'FR1?',
            "F outer": 'FR2?',
            "OUT 1": 'FR3?',
            "OUT 2": 'FR4?',
        }
        
        self.wheels_dict = {
            "60": 'WHL0',
            "42/30": 'WHL1',
            "7/5": 'WHL2',
            "2": 'WHL3',
            "100": 'WHL4',
        }
                          
        self.sync_dict = {
            "INT": 'SYN3',
            "EXT-": 'SYN2',
            "EXT+": 'SYN1',
            "V ext": 'SYN0',
        }
                          
        self.mode_dict = {
            "Normal": 'MOD2',
            "+/-": 'MOD1',
            "H/S": 'MOD0',
        }
                          
        # Here, I'm not sure about the frequencies. 
        self.variables = list(self.frequencies.keys())
        self.units = ["Hz"] * len(self.variables)
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

    def find_Ports(self):
    
        try:
            # please update to 1.5.5.44 if the path below does not work
            clr.AddReference(self.get_folder("SELF").replace(os.sep + "main.py", "") +
                             os.sep + "libs" + os.sep + "NpChopperLibWrap.dll")
            # clr.AddReference("NpChopperLibWrap.dll") # Just does not work

        except:
            error()
            self.stop_Measurement("NpChopperLibWrap.dll cannot be loaded. Please change access rights under "
                                  "file properties.")
                  
            # Comment AF @ 16.03.22: It might be possible to unblock dll files using
            # powershell.exe -Command Unblock-File -Path "c:\path\to\blocked file.ps1"

            return False
    
        import Newport.Chopper
        
        lib = Newport.Chopper.USB(True)
        lib.Logging = False
        lib.Discover()        
             
        devices_c_array = lib.GetDeviceKeys() # returns an C# array
        ports = []       
        
        if devices_c_array:  # ports is None if no devices are connected
            for dev in devices_c_array:
                ports.append(dev)
                
                id = StringBuilder()
                lib.Query(dev, 'IDN?', id)
                # print(id.ToString())  # JK: Not sure if it's useful to print the device ID
                
            lib.Shutdown()
            # returns a list of ports
            # the chosen port is forwarded to initialize where it can be used to start the correct port
        else:
            return []
        
        lib.Shutdown()
        
        return ports
    
    def set_GUIparameter(self):

        GUIparameter = {
                        "SweepMode":                  ["Frequency in Hz"],
                        "Wheel":                      list(self.wheels_dict.keys()),
                        "Sync":                       list(self.sync_dict.keys()), 
                        "Mode":                       list(self.mode_dict.keys()), 
                        "Phase in °":                 "0.0", 
                        "Harmonic multiplier H":      ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"], 
                        "Subharmonic divide ratio S": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
                        }        
        return GUIparameter 

    def get_GUIparameter(self, parameter={}):
        
        self.device_key = parameter["Port"]
        self.sweepmode = parameter["SweepMode"]
        self.wheel_gui = parameter["Wheel"]
        self.sync = parameter["Sync"]
        self.mode = parameter["Mode"]
        self.phase = parameter["Phase in °"]
        self.harmonic = parameter["Harmonic multiplier H"]
        self.subharmonic = parameter["Subharmonic divide ratio S"]    
      
    def connect(self):
    
        if self.device_key == "":
            raise Exception("No port selected! Please make sure a Newport Model 3502 Optical chopper is connected.")

        try:
            # clr.AddReference("NpChopperLibWrap.dll")
            clr.AddReference(self.get_folder("SELF").replace(os.sep + "main.py", "") +
                             os.sep + "libs" + os.sep + "NpChopperLibWrap.dll")

        except:
            error()
            self.stop_Measurement("NpChopperLibWrap.dll cannot be loaded. Please change access rights under "
                                  "file properties.")
            return False

        import Newport.Chopper

        self.lib = Newport.Chopper.USB(True)
        self.lib.Logging = False
        self.lib.Discover()

    def disconnect(self):
        self.lib.Shutdown()

    def initialize(self):

        if self.wheels_dict[self.wheel_gui] != "WHL0":
            debug("Newport 3502: Check which wheel is installed and consult the manual to see the frequency range")

    def configure(self):

        # Wheel type
        self.lib.Write(self.device_key, self.wheels_dict[self.wheel_gui])
        
        # Sync
        self.lib.Write(self.device_key, self.sync_dict[self.sync])
        
        # Mode
        self.lib.Write(self.device_key, self.mode_dict[self.mode])
        
        # Harmonic multiplier
        self.lib.Write(self.device_key, 'HAR'+self.harmonic)
        
        # Subharmonic divide ratio
        self.lib.Write(self.device_key, 'SUB'+self.subharmonic)
        
        if float(self.phase) >= -180.0 and float(self.phase) <= 179.0:
            self.lib.Write(self.device_key, 'PHS'+str(self.phase).replace('.', ''))
        else:
            self.stop_Measurement('Phase must be between -180° and 179°.')
        
    """    
    def unconfigure(self):
        
        # Sets the wheel type to 60
        self.lib.Write(self.device_key, 'WHL0')
        # Sets Sync to INT
        self.lib.Write(self.device_key, 'SYN3')
        # Sets Mode to "Normal"
        self.lib.Write(self.device_key, 'MOD2')
        # Sets Phase to zero
        self.lib.Write(self.device_key, 'PHS00')
        # Sets H to one
        self.lib.Write(self.device_key, 'HAR1')
        # Sets S to one
        self.lib.Write(self.device_key, 'SUB1')
    """

    def apply(self):

        self.value_float = float(self.value)
        
        wheel = StringBuilder('')
        self.lib.Query(self.device_key, 'WHL?', wheel)
        wheel = wheel.ToString()
        
        if wheel == 'WHL0':
            if self.value_float < 120.0:
                self.stop_Measurement('For this wheel, the lowest frequency is 120 Hz')
            elif self.value_float > 6.4*1e3:
                self.stop_Measurement('For this wheel, the highest frequency is 6.4 kHz')

        # TODO: add frequency range for all available wheels
        # if wheel != 'WHL0':
            # Here I kept with "message_Info", because somebody else using this driver can have another wheel installed,
            # so the measurement cannot stop
            # debug('Check which wheel is installed and consult the manual to check the frequency range')
        
        self.lib.Write(self.device_key, 'OSC'+'{0:.0f}'.format(self.value_float)+'00')
                
    def reach(self):
       
        starttime = time.perf_counter()
        
        while True:
            
            # Timeout
            if time.perf_counter()-starttime > 5.0:
                break
                
            self.f_reach = StringBuilder('')
            # TODO: Should we use SyncIn Frequency ??? R: I think we can use the one measured by the sensor at the
            # wheel, Fouter (FR2?), but for now I'm using SyncIn because the wheel connected.
            self.lib.Query(self.device_key, 'FR1?', self.f_reach)
            self.f_reach = self.f_reach.ToString()
            self.f_reach = float(self.f_reach[2:])
            
            # Frequency reached condition
            if abs(self.f_reach - self.value_float) < 0.01 * self.value_float:
                break
                
            time.sleep(0.1)
    
    def measure(self):
        
        self.measured_frequencies = []
        
        for var in self.variables:

            cmd = self.frequencies[var]
        
            f_str = StringBuilder('')      
            self.lib.Query(self.device_key, cmd, f_str)
            f_str = f_str.ToString()
            self.measured_frequencies.append(float(f_str[2:]))

    def call(self):
        return self.measured_frequencies
