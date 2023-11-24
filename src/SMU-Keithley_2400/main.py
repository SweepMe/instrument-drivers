# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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
# Device: Keithley 2400


from EmptyDeviceClass import EmptyDevice
import numpy as np
import time


class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Keithley2400"
        
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        
        self.port_properties = {
            "timeout": 10,
            "EOL": "\r",
            "baudrate": 9600,
        }
                                 
        self.commands = {
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
            "Voltage [V]": "VOLT",  # deprecated, remains for compatibility reasons
            "Current [A]": "CURR",  # deprecated, remains for compatibility reasons
        }
                        
        self.outpon = False 
                                 
    def set_GUIparameter(self):
        
        gui_parameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Front", "Rear"],
            "Speed": ["Fast", "Medium", "Slow"],
            "Range": ["Auto",
                      "10 nA",
                      "100 nA",
                      "1 µA",
                      "10 µA",
                      "100 µA",
                      "1 mA",
                      "10 mA",
                      "100 mA",
                      "1 A", ],
            "Compliance": 100e-6,
            "Average": 1,
            "4wire": False,
        }
                        
        return gui_parameter
                                 
    def get_GUIparameter(self, parameter={}):
        self.four_wire = parameter['4wire']
        self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']
        self.range = parameter['Range']
        self.speed = parameter['Speed']
        self.average_gui = int(parameter['Average'])
        self.port_string = parameter["Port"]

        self.average = self.average_gui
        if self.average_gui < 1:
            self.average = 1
        if self.average_gui > 100:
            self.average = 100

    def initialize(self):

        identifier = self.get_identification()

        vendor, model, sn_version, fw_version = identifier.split(",")
        fw_version_year = int(fw_version.split()[3])

        # The Keithley 2400 supports two protocols: 488.1 and SCPI
        # The SCPI protocol is better as it works more stable. If several devices are connected at the same time,
        # the 488.1 protocol can lead to timeout errors
        # Lets switch to SCPI protocol if 488.1 is currently selected
        # This is only performed for firmware version later than 1998
        if not self.port_string.startswith("COM") and fw_version_year > 1998:
            try:
                self.port.write("SYST:MEP:STAT?")
                if self.port.read() == "0":
                    self.port.write("SYST:MEP:STAT 1")
                    # A short time is needed before the new protocol works and new commands can be received.
                    time.sleep(0.1)
                    self.port.write("SYST:MEP:STAT?")
                    if self.port.read() == "1":
                        debug("Keithley 2400: GPIB communication protocol was changed to 'SCPI' automatically.")
                    else:
                        debug("Keithley 2400: Not able to select 488.1 protocol. "
                              "Please change manually via Menu -> Communication -> GPIB -> GPIB Protocol")
            except:
                error("Unable to change GPIB communication protocol to 'SCPI' for identifier '%s'" % identifier)
        
        # once at the beginning of the measurement
        self.reset()
        # time.sleep(0.05) # maybe needed to prevent random "Undefined Header error -113"
        self.clear()
        
        self.port.write("SYST:BEEP:STAT OFF")  # control-beep off

        if self.average_gui > 100:
            self.message_Box("Maximum allowed average is 100 and average has been changed to 100")
            
    def configure(self):
    
        if self.route_out == "Front":
            self.port.write("ROUT:TERM FRON")  # use front or rear terminal for power supply
        if self.route_out == "Rear":
            self.port.write("ROUT:TERM REAR")  # use front or rear terminal for power supply

        self.range = (self.range.replace(" ", "").replace("p", "e-12").replace("n", "e-9").
                      replace("µ", "e-6").replace("m", "e-3"))
    
        if self.source.startswith("Voltage"):
            self.port.write(":SOUR:FUNC VOLT")                  
            # sourcemode = Voltage
            self.port.write(":SOUR:VOLT:MODE FIX")
            # sourcemode fix
            self.port.write(":SENS:FUNC \"CURR\"")              
            # measurement mode
            self.port.write(":SENS:CURR:PROT " + self.protection)
            # Protection with Imax
            
            if self.range == "Auto":  # it means Auto was selected
                self.port.write(":SENS:CURR:RANG:AUTO ON")  # Autorange for current measurement
            else:
                self.port.write(":SENS:CURR:RANG:AUTO OFF")
                self.port.write(":SENS:CURR:RANG %s" % str(self.range.replace("A", "")))

        elif self.source.startswith("Current"):
            self.port.write(":SOUR:FUNC CURR")                  
            # sourcemode = Voltage
            self.port.write(":SOUR:CURR:MODE FIX")
            # sourcemode fix
            self.port.write(":SENS:FUNC \"VOLT\"")              
            # measurement mode
            self.port.write(":SENS:VOLT:PROT " + self.protection)
            # Protection with Imax
            
            if self.range == "Auto":  # it means Auto was selected
                self.port.write(":SOUR:CURR:RANG:AUTO ON")  # Autorange for voltage measurement
            else:
                self.port.write(":SOUR:CURR:RANG:AUTO OFF")
                self.port.write(":SOUR:CURR:RANG %s" % str(self.range.replace("A", "")))
               
        if self.speed == "Fast":
            self.nplc = 0.1
        elif self.speed == "Medium":
            self.nplc = 1.0
        elif self.speed == "Slow":
            self.nplc = 10.0

        self.port.write(":SENS:CURR:DC:NPLC " + str(self.nplc))
        self.port.write(":SENS:VOLT:DC:NPLC " + str(self.nplc))
        
        # 4-wire sense
        if self.four_wire:
            self.port.write("SYST:RSEN ON")
        else:
            self.port.write("SYST:RSEN OFF")
        
        # averaging
        self.port.write(":SENS:AVER:TCON REP")  # repeatedly take average
        if self.average > 1:
            self.port.write(":SENS:AVER ON") 
            self.port.write(":SENSe:AVER:COUN %i" % self.average)  # repeatedly take average
        else:
            self.port.write(":SENS:AVER OFF")
            self.port.write(":SENSe:AVER:COUN 1")

        # let's ensure all parameters are set before we continue
        self.wait_for_complete()
     
    def deinitialize(self):
        self.port.write("SYST:RSEN OFF")
        self.port.write("ROUT:TERM FRON")
        self.port.write(":SENS:CURR:DC:NPLC 1")
        self.port.write(":SENS:VOLT:DC:NPLC 1")
        self.port.write(":SENS:AVER OFF")
        self.port.write(":SENSe:AVER:COUN 1")  
        
        self.port.write("SYST:BEEP:STAT ON")  # control-Beep on
        
        if self.port_string.startswith("COM"):
            self.port.write("SYST:LOC")  # RS-232/COM-port only
        else:
            self.port.write("GTL")

    def poweron(self):
        self.port.write("OUTP ON")
        self.outpon = True
        
    def poweroff(self):
        self.port.write("OUTP OFF")
        self.outpon = False    
              
    def apply(self):
        self.port.write(":SOUR:" + self.commands[self.source] + ":LEV %s" % self.value)  # set source
        
    def reach(self):
        self.wait_for_complete()

    def measure(self):    
        self.port.write("READ?")                                    

    def call(self):
    
        answer = self.port.read().split(',')
        if answer == [""]:
            answer = self.port.read().split(',')

        self.v = answer[0]
        self.i = answer[1]
        
        if len(self.v) != 13:
            self.v = self.v[1:]

        return [float(self.v), float(self.i)]

    def get_identification(self):
        """
        Retrieves the identification string
        """
        self.port.write("*IDN?")
        return self.port.read()

    def reset(self):
        """
        Resets the instrument to default parameters
        """
        self.port.write("*RST")

    def clear(self):
        """
        Clears the status register and error queue
        """
        self.port.write("*CLS")

    def wait_for_complete(self):
        """
        Waits for the operation queue to be completed
        """
        self.port.write("*OPC")
        return self.port.read()
