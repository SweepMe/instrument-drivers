# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# Device: Keithley 2450

from EmptyDeviceClass import EmptyDevice
import time
import numpy as np
import sys
from collections import OrderedDict

class Device(EmptyDevice):

    def __init__(self):
    
        super().__init__()
        
        self.shortname = "Keithley2450"
        
        self.variables =["Voltage", "Current"]
        self.units =    ["V", "A"]
        self.plottype = [True, True] # True to plot data
        self.savetype = [True, True] # True to save data
        
        self.port_manager = True
        self.port_types = ['USB', 'GPIB']
        self.port_properties = {'timeout':10}
        self.port_identifications = ['KEITHLEY INSTRUMENTS,MODEL 2450,']
        
        self.isPoweron = False
        
        # 10 nA ±10.5 nA
        # 100 nA ±10.6 nA
        # 1 μA ±1.05 μA
        # 10 μA ±1.06 μA
        # 100 μA ±10.6 μA
        # 1 mA ±106 μA
        # 10 mA ±1.06 mA
        # 100 mA ±10.6 mA
        # 1 A ±106 mA


    def set_GUIparameter(self):
        GUIparameter = {
                        "SweepMode": ["Voltage [V]", "Current [A]"],
                        "RouteOut": ["Front", "Rear"],
                        "Speed": ["Fast", "Medium", "Slow"],
                        "Range": ["Auto", "10 nA", "100 nA", "1 µA", "10 µA", "100 µA", "1 mA", "10 mA", "100 mA", "1 A"],                       
                        "Average": 1,
                        "Compliance": 100e-6,
                        "4wire": False,
                        }
        
        return GUIparameter
        

    def get_GUIparameter(self, parameter={}):
              
        self.four_wire = parameter['4wire']
        self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']
        self.speed = parameter['Speed']
        self.range = parameter['Range']
        self.average = int(parameter['Average'])
        
    def connect(self):
    
        self.port.write("*LANG?")
        self.language = self.port.read() # TSP, SCPI, SCPI2400
        # set language with *LANG SCPI, *LANG TSP, *LANG SCPI2400 and reboot, ask for language *LANG? 
        
        if self.language == "SCPI":
            self.language = "SCPI2400"
        
        # print(self.language)
        
    def initialize(self):
       
        if self.language == "SCPI2400":
           
            self.port.write("*IDN?")
            self.vendor, self.model, self.serialno, self.version = self.port.read().split(",")
            # print(self.vendor, self.model, self.serialno, self.version)
            # reset all values
            self.port.write("*rst" )
            self.port.write("status:preset" )
            self.port.write("*cls")
            
            self.port.write(":SYST:BEEP:STAT OFF") # control-Beep off
            
            #self.port.write(":SYST:LFR 50")
            

        if self.language == "TSP":
        

            self.port.write("print(localnode.vendor)")
            self.vendor = self.port.read()
            self.port.write("print(localnode.model)")
            self.model = self.port.read()
            self.port.write("print(localnode.serialno)")
            self.serialno = self.port.read()
            self.port.write("print(localnode.version)")
            self.version = self.port.read()
            # print(self.vendor, self.model, self.serialno, self.version)
            
            self.port.write("smu.reset()")
            self.port.write("errorqueue.clear()")
                                    
            #self.port.write("localnode.linefreq = 50")
            
    
                   
    def configure(self):
    
        if self.language == "SCPI2400":
                       
            if self.average > 1:
                self.port.write(":SENS:AVER:COUN %i" % self.average)
                self.port.write(":SENS:AVER:STAT ON")
                self.port.write(":SENS:AVER:TCON REP")
                
            else:
                self.port.write(":SENS:AVER:COUN 1")
                self.port.write(":SENS:AVER:STAT OFF")

        if self.language == "TSP":
           
            if self.average > 1:
                self.port.write("smu.measure.filter.count = %i" % self.average)
                self.port.write("smu.measure.filter.enable = smu.ON")
                self.port.write("smu.measure.filter.type = smu.FILTER_REPEAT_AVG")
                
            else:
                self.port.write("smu.measure.filter.count = 1")
                self.port.write("smu.measure.filter.enable = smu.OFF")


        if self.source == "Voltage [V]":
            self.source_volt()
            
        if self.source == "Current [A]":
            self.source_curr()
            
            
        ### Speed/Integration ###
        self.set_speed(self.speed)
        
       
        ### 4 wire ###
        if self.four_wire:
            self.rsen_on()
        else:
            self.rsen_off()
            
        ### Route out ###
        if self.route_out == "Front":
            self.route_Fron()
        
        if self.route_out == "Rear":
            self.route_Rear()   

    def deinitialize(self):
        self.rsen_off()
        self.route_Fron()
         
    def poweron(self):
        
        if self.language == "SCPI2400": 
            self.port.write("OUTP ON")
         
        elif self.language == "TSP":
            self.port.write("smu.source.output = smu.ON")
                        
        self.isPoweron = True
        
    def poweroff(self):

        if hasattr(self, "language"):
            if self.language == "SCPI2400": 
                self.port.write("OUTP OFF")
             
            elif self.language == "TSP":
                self.port.write("smu.source.output = smu.OFF")
            
        self.isPoweron = False
                                 
    def apply(self):

        self.value = str(self.value)

        if self.language == "SCPI2400":
            self.port.write(":SOUR:"+self.source[:-4]+":LEV %s" % self.value)
            
        elif self.language == "TSP":
            self.port.write("smu.source.level = %s" % self.value)
                        
        # needed to trigger a measurement and thus to trigger the final output of the level
        self.measure()
        self.call()

    def measure(self):    
             
        if self.language == "SCPI2400":
            self.port.write("READ?")
        
        elif self.language == "TSP":  
            self.port.write("data = buffer.make(10)")
            self.port.write("smu.measure.read(data)")    
           
       
    def call(self):
    
        if self.language == "SCPI2400":
            answer = self.port.read().split(',')
            self.v, self.i = answer[0:2]
        
        elif self.language == "TSP":

            self.port.write("printbuffer(1, 1, data.readings, data.sourcevalues)") 
            answer = self.port.read().split(',')
            
            if self.source == "Voltage [V]":
                self.i, self.v = answer
            elif self.source == "Current [A]":
                self.v, self.i = answer
    
        return [float(self.v), float(self.i)]
                    
    def route_Fron(self):  
    
        # if self.language == "SCPI2400": 
            # self.port.write("ROUT:TERM?")
            
        # if self.language == "TSP":
            # self.port.write("print(smu.measure.terminals)")
            # self.port.read()
        
        if self.isPoweron:
            self.poweroff()
        
        if hasattr(self, "language"):
            if self.language == "SCPI2400": 
                self.port.write(":ROUT:TERM FRON")
             
            elif self.language == "TSP":
                self.port.write("smu.measure.terminals = smu.TERMINALS_FRONT")

 
    def route_Rear(self):
    
        if self.isPoweron:
            self.poweroff()
            
        if self.language == "SCPI2400": 
            self.port.write(":ROUT:TERM REAR")

        elif self.language == "TSP":
            self.port.write("smu.measure.terminals = smu.TERMINALS_REAR")

        
    def set_speed(self, speed):
        if speed == "Fast":
            self.nplc = 0.1
        if speed == "Medium":
            self.nplc = 1.0
        if speed == "Slow":
            self.nplc = 10.0
            
        if self.language == "SCPI2400":    
            self.port.write(":SENS:CURR:DC:NPLC " + str(self.nplc))
            self.port.write(":SENS:VOLT:DC:NPLC " + str(self.nplc))
        elif self.language == "TSP":
            self.port.write("smu.measure.nplc = " + str(self.nplc))
             
    def source_volt(self):
    
        self.range = self.range.replace(" ", "").replace("p", "e-12").replace("n", "e-9").replace("µ", "e-6").replace("m", "e-3")
    
        if self.language == "SCPI2400":
            self.port.write(":SOUR:FUNC VOLT")                  
            # sourcemode = Voltage
            self.port.write(":SOUR:VOLT:MODE FIX")
            # sourcemode fix
            self.port.write(":SENS:FUNC \"CURR\"")              
            # measurement mode
            self.port.write(":SENS:CURR:PROT "+ self.protection)
            # Protection with Imax
            # self.port.write(":SOUR:VOLT:READ:BACK ON") ## does not work and leads to error???
            
            if self.range == "Auto": # it means Auto was selected              
                self.port.write(":SENS:CURR:RANG:AUTO ON")

            else:
                self.port.write(":SENS:CURR:RANG:AUTO OFF")
                self.port.write(":SENS:CURR:RANG %s" % str(self.range.replace("A", "")))
      
        elif self.language == "TSP":
            self.port.write("smu.source.func = smu.FUNC_DC_VOLTAGE")
            self.port.write("smu.measure.func = smu.FUNC_DC_CURRENT")
            self.port.write("smu.source.autorange = smu.ON") # for voltage range
            
            self.port.write("smu.source.ilimit.level = " + self.protection)
            
            if self.range == "Auto": # it means Auto was selected
                self.port.write("smu.measure.autorange = smu.ON")
            else:
                self.port.write("smu.measure.autorange = smu.OFF")
                self.port.write("smu.measure.range = %s" % str(self.range.replace("A", "")))
                
            
            
            self.port.write("smu.measure.autozero.once()")

    def source_curr(self): 

        self.range = self.range.replace(" ", "").replace("p", "E-12").replace("n", "E-9").replace("µ", "E-6").replace("m", "E-3")

                        
        if self.language == "SCPI2400":
            self.port.write(":SOUR:FUNC CURR")                  
            # sourcemode = Voltage
            self.port.write(":SOUR:CURR:MODE FIX")
            # sourcemode fix		
            self.port.write(":SENS:FUNC \"VOLT\"")              
            # measurement mode
            self.port.write(":SENS:VOLT:PROT "+ self.protection)
            # Protection with Imax
            self.port.write(":SENS:VOLT:RANG:AUTO ON")
            # Autorange for voltage measurement
            # self.port.write(":SOUR:CURR:READ:BACK ON")  ## does not work and leads to error???
            # Read the source value again
            
            if self.range == "Auto": # it means Auto was selected
                    
                self.port.write(":SOUR:CURR:RANG:AUTO ON")
            else:
                self.port.write(":SOUR:CURR:RANG:AUTO OFF")
                self.port.write(":SOUR:CURR:RANG %s" % str(self.range.replace("A", "")))

        elif self.language == "TSP":
            self.port.write("smu.source.func = smu.FUNC_DC_CURRENT")
            self.port.write("smu.measure.func = smu.FUNC_DC_VOLTAGE")
            self.port.write("smu.source.vlimit.level = " + self.protection)
            self.port.write("smu.measure.autozero.once()")
            
            if self.range == "Auto": # it means Auto was selected
                    
                self.port.write("smu.source.autorange = smu.ON")
            else:
                self.port.write("smu.source.autorange = smu.OFF")
                self.port.write("smu.source.range = %s" % str(self.range.replace("A", "")))


    def rsen_on(self):
        if self.language == "SCPI2400":
            self.port.write(":SYST:RSEN ON")
        elif self.language == "TSP":
            self.port.write("smu.measure.sense = smu.SENSE_4WIRE")
            
    def rsen_off(self):
    
        if hasattr(self, "language"):
            if self.language == "SCPI2400":
                self.port.write(":SYST:RSEN OFF")
            elif self.language == "TSP":
                self.port.write("smu.measure.sense = smu.SENSE_2WIRE")
                
    def output_mode(self):
        if self.language == "SCPI2400":
            #To set the output-off state to normal,
            self.port.write(":OUTP:SMOD NORM")
            #To set the output-off state to zero
            #self.port.write(":OUTP:SMOD ZERO") 
            #To set the output-off state to high impedance
            #self.port.write(":OUTP:SMOD HIMP")
            #To set the output-off state to guard
            #self.port.write(":OUTP:SMOD GUAR")
            
        elif self.language == "TSP":
            #To set the output-off state to normal,
            self.port.write("smu.source.offmode = smu.OFFMODE_NORMAL")
            #To set the output-off state to zero
            #self.port.write("smu.source.offmode = smu.OFFMODE_ZERO") 
            #To set the output-off state to high impedance
            #self.port.write("smu.source.offmode = smu.OFFMODE_HIGHZ")
            #To set the output-off state to guard
            #self.port.write("smu.source.offmode = smu.OFFMODE_GUARD")
    
