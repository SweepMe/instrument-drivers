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


# SweepMe! device class
# Type: SMU
# Device: TDK-Lambda Genesys

import time
from ErrorMessage import error
from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Genesys"
        
        self.variables = ["Voltage", "Current"]
        self.units =     ["V", "A"]
        self.plottype =  [True, True] # True to plot data
        self.savetype =  [True, True] # True to save data

        self.port_manager = True
        self.port_types = ["COM"] # can be both RS-232 or RS-485. It depends on the adapter used.
        
        self.port_properties = { "timeout": 1,
                                 "EOL": "\r",
                                 "baudrate": 9600, # factory default
                                 # "delay": 0.1,
                                 }
                                 
                                 
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Voltage in V", "Current in A", "Manual control"],
                        "RouteOut": ["Rear"],
                        "Channel": ["6"] + [str(x) for x in range(1,31,1)], # 6 is the default channel
                        "Compliance": 0.1,
                        }
                        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
        self.sweepmode = parameter['SweepMode']
        self.protection = parameter['Compliance']
        self.channel = parameter['Channel']
        self.port_str = parameter['Port']
        self.device_name = parameter['Device']
        
    def initialize(self):
    
        self.change_address()        
        
        identification = self.get_identification()
        # print("Identifier:", identification)
                
        serial_number = self.get_serial_number()
        # print("Serial number:", serial_number)
        
        if self.sweepmode != "Manual control":
            self.set_remote_mode("REM")  # remote mode, alternative: RMT LLO (local lockout)
        else:
            self.set_remote_mode("LOC")
        

    def deinitialize(self):
        pass
        #self.set_remote_mode("LOC")  # back to local mode

    def configure(self):

        if self.sweepmode.startswith("Voltage"):
            self.set_current(float(self.protection))
            if self.sweepmode != "Manual control":
                self.set_voltage(0.0)
            
        elif self.sweepmode.startswith("Current"):
            self.set_voltage(float(self.protection))
            if self.sweepmode != "Manual control":
                self.set_current(0.0)   
         
           
    def unconfigure(self):
        pass

    def poweron(self):
        if self.sweepmode != "Manual control":
            self.set_output_on()
        
    def poweroff(self):
        if self.sweepmode != "Manual control":
            self.set_output_off()
                 
    def apply(self):
    
        if self.sweepmode.startswith("Voltage"):
            self.set_voltage(float(self.value))
            
        elif self.sweepmode.startswith("Current"):
            self.set_current(float(self.value))

         
    def measure(self):        

        self.v = self.get_measured_voltage()
        self.i = self.get_measured_current()
        
        # alternative (maybe faster)
        # MV, PV, MC, PC =  self.get_status()
        

    def call(self):
        return [self.v, self.i]
        
        
    def change_address(self):

        if not self.device_name + self.port_str + "Address" in self.device_communication or self.device_communication[self.device_name + self.port_str + "Address"] != self.channel:

            self.port.write("ADR %i" % int(self.channel))
            ret = self.port.read()
            # print("Address ok?", ret)
        
            self.device_communication[self.device_name + self.port_str + "Address"] = self.channel
        


    """ setter/getter functions """
    
    
    def get_identification(self):
    
        self.change_address()  
        self.port.write("*IDN?")
        return self.port.read()
        
    def get_serial_number(self):
    
        self.change_address()  
        self.port.write("*SN?")
        return self.port.read()
    
    def get_remote_mode(self):
        
        self.change_address()
        self.port.write("RMT?")
        return self.port.read()
        
    def set_remote_mode(self, mode):

        # RMT 0 or RMT LOC, sets the power supply into Local mode.
        # RMT 1 or RMT REM, sets the unit into remote mode.
        # RMT 2 or RMT LLO, sets the unit into Local Lockout mode (latched remote mode).

        self.change_address()  
        self.port.write("RMT %s" % str(mode))
        self.port.read()
      
    def get_status(self):
    
        # MV<actual (measured) voltage> PC<programmed (set) current>
        # PV<programmed (set) voltage> SR<status register, 2-digit hex>
        # MC<actual (measured) current> FR<fault register, 2-digit hex>
        
        self.change_address()  
        self.port.write("STT?")
        answer = self.port.read()
        
        MV, PV, MC, PC, SR, FR = answer.split(",")
        
        return float(MV[3:-1]), float(PV[3:-1]), float(MC[3:-1]), float(PC[3:-1])
        
    def set_voltage(self, value):
        
        self.change_address()  
        self.port.write("PV %1.4f" % float(value))
        self.port.read()        
        
    def get_measured_voltage(self):
        
        self.change_address()  
        self.port.write("MV?")
        answer = self.port.read()
        return float(answer)

        
    def set_current(self, value):
        
        self.change_address()  
        self.port.write("PC %1.4f" % float(value))
        self.port.read()        
        
    def get_measured_current(self):
        
        self.change_address()  
        self.port.write("MC?")
        answer = self.port.read()
        return float(answer)
        
    def set_output(self, value):

        # OUT 1 (or OUT ON)-Turn On.
        # OUT 0 (or OUT OFF)-Turn Off

        self.change_address()  
        self.port.write("OUT %s" % value)
        self.port.read()
        
    def get_output(self):
        
        self.change_address()  
        self.port.write("OUT?")
        answer = self.port.read()
        return answer

    def set_output_on(self):

        self.change_address()  
        self.set_output("ON")
    
    def set_output_off(self):

        self.change_address()  
        self.set_output("OFF")