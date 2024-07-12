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

# SweepMe! driver
# * Module: LCRmeter
# * Instrument: Hewlett Packard LCRmeter 4284A

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "HP4284A"
        
        self.plottype = [True, True, True, True]  # True to plot data
        self.savetype = [True, True, True, True]  # True to save data
        
        self.port_manager = True
        self.port_types = ["GPIB"]
        self.port_properties = {
            "timeout": 20,
        }

        self.operating_modes = {
            "R-X": "RX",
            "Cp-D": "CPD",
            "Cp-Gp": "CPG",
            "Cs-Rs": "CSRS",
        }

        self.commands_to_restore = [
            "FUNC:IMP",                 # Operating mode
            "FUNC:IMP:RANG:AUTO",       # Auto range on/off
            "DISP:LINE",                # Display line
            # "VOLT",                     # Oscillator strength
            # "CURR",                     # current oscillator
            # "BIAS:VOLT",                # bias level
            "APER",                     # average
            "FREQ",                     # Frequency
            "AMPL:ALC",                 # Automatic level control
            "CORR:LENG",                # Correction length
            "FUNC:IMP:RANG",            # Range value -> must be last and
        ]

    def set_GUIparameter(self):
        
        gui_parameter = {
            "Average": ["1", "2", "4", "8", "16", "32", "64"],

            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A", "Voltage RMS in V"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A", "Voltage RMS in V"],

            "ValueTypeRMS": ["Voltage RMS in V:", "Current RMS in A:"],
            "ValueRMS": 0.02,

            "ValueTypeBias": ["Voltage bias in V:" , "Current bias in A:"],
            "ValueBias": 0.0,

            "Frequency": 1000.0,

            "OperatingMode": list(self.operating_modes.keys()),

            "ALC": ["Off", "On"],
            "Integration": ["Short", "Medium", "Long"],

            "Trigger": ["Software", "Internal", "External"],
        }

        return gui_parameter
                                 
    def get_GUIparameter(self, parameter={}):

        self.sweepmode = parameter['SweepMode']
        self.stepmode = parameter['StepMode']
        
        self.ValueTypeRMS = parameter['ValueTypeRMS']
        self.ValueRMS = float(parameter['ValueRMS'])
        
        self.ValueTypeBias = parameter['ValueTypeBias']
        self.ValueBias = float(parameter['ValueBias'])

        self.ALC = parameter['ALC']
        self.integration = parameter['Integration']
        self.average = int(parameter['Average'])
        self.frequency = float(parameter['Frequency'])
        
        self.OperatingMode = parameter['OperatingMode']
        
        if self.sweepmode.startswith("Voltage"):
            self.bias_mode = "VOLT"
        elif self.sweepmode.startswith("Current"):
            self.bias_mode = "CURR"
        else:
            if self.stepmode.startswith("Voltage"):
                self.bias_mode = "VOLT"
            elif self.stepmode.startswith("Current"):
                self.bias_mode = "CURR"
                
            else:
                if self.ValueTypeBias.startswith("Voltage"):
                    self.bias_mode = "VOLT"
                elif self.ValueTypeBias.startswith("Current"):
                    self.bias_mode = "CURR"
                else:
                    self.bias_mode = "VOLT"
               
        self.bias_modes_variables = {"VOLT": "Voltage bias", "CURR":"Current bias"}    
        self.bias_modes_units = {"VOLT": "V", "CURR":"A"}    
            
        if self.OperatingMode == "R-X":
            self.variables = ["R", "X", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units     = ["Ohm", "Ohm", "Hz", self.bias_modes_units[self.bias_mode]]
            
        elif self.OperatingMode == "Cp-D":
            self.variables = ["Cp", "D", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units     = ["F", "", "Hz", self.bias_modes_units[self.bias_mode]]
            
        elif self.OperatingMode == "Cp-Gp":
            self.variables = ["Cp", "Gp", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units     = ["F", "S", "Hz", self.bias_modes_units[self.bias_mode]]
            
        elif self.OperatingMode == "Cs-Rs":
            self.variables = ["Cs", "Rs", "Frequency", self.bias_modes_variables[self.bias_mode]]
            self.units     = ["F", "Ohm", "Hz", self.bias_modes_units[self.bias_mode]]
        
        self.trigger_type = parameter["Trigger"]

    def initialize(self):
                  
        # store the users device setting
        self.vals_to_restore = {}
        for cmd in self.commands_to_restore:
            self.port.write(cmd + "?")
            answer = self.port.read()
            self.vals_to_restore[cmd] = answer
            
        # no reset anymore as the device starts with an oscillator amplitude of 1V
        # which can influence sensitive devices.
        # self.port.write("*RST") #  reset configuration
        
        self.port.write("*CLS")  # clear memory
        
        # self.port.write("DISP:LINE \"Remote control by SweepMe!\"")
            
    def deinitialize(self):

        # restore the users device setting
        for cmd in self.commands_to_restore:
            self.port.write(cmd + " " + self.vals_to_restore[cmd])

    def configure(self):
        
        # Integration and average
        if self.integration == "Short":
            self.integration_string = "SHOR"
        if self.integration == "Medium":
            self.integration_string = "MED"
        if self.integration == "Long":
            self.integration_string = "LONG"
            
        self.port.write("APER %s,%i" % (self.integration_string, self.average))

        # No Cable correction
        self.port.write("CORR:LENG %iM" % 0)  # cable correction set to 0m
        
        # ALC
        if self.ALC == "On":
            self.port.write("AMPL:ALC ON")
        elif self.ALC == "Off": 
            self.port.write("AMPL:ALC OFF")
            
        # Measures real (R) and imaginary (X) part of the impedance
        self.port.write("FUNC:IMP %s" % self.operating_modes[self.OperatingMode])

        # Auto range
        self.port.write("FUNC:IMP:RANG:AUTO ON") 

        # Standard frequency
        self.port.write("FREQ %1.5eHZ" % self.frequency)
        
        # Standard bias
        self.port.write("BIAS:%s %1.3e" % (self.bias_mode, self.ValueBias))

        # Oscillator signal
        if self.ValueTypeRMS.startswith("Voltage RMS"):
            self.port.write("VOLT %s MV" % (self.ValueRMS*1000.0))
        elif self.ValueTypeRMS.startswith("Current RMS"):
            self.port.write("CURR %s MA" % (self.ValueRMS*1000.0))

        # Trigger
        if self.trigger_type == "Software":
            self.port.write("TRIG:SOUR BUS")
            self.port.write("INIT:CONT OFF")
        elif self.trigger_type == "Internal":
            self.port.write("TRIG:SOUR INT")
            self.port.write("INIT:CONT ON")
        elif self.trigger_type == "External":
            self.port.write("TRIG:SOUR EXT")
            self.port.write("INIT:CONT OFF")
        else:
            self.port.write("TRIG:SOUR INT")  # default will be internal trigger, i.e. continuous trigger
            self.port.write("INIT:CONT ON")
            
    def unconfigure(self):
    
        self.port.write("ABOR")  # abort any running command
    
        self.port.write("BIAS:VOLT 0V")
        self.port.write("AMPL:ALC OFF")  # TODO: it is overwritten by the user setting in deinitialize
        # self.port.write("FREQ 1000HZ")
        self.port.write("VOLT 20 MV") 
        # self.port.write("FUNC:IMP CPD") 
        
        self.port.write("TRIG:SOUR INT")  # makes sure the trigger runs again
        self.port.write("INIT:CONT ON")  # starting internal trigger
        
        # Don't ask me why, but asking any value makes sure that the commands above are correctly set
        # or shown on the display
        # self.port.write("*IDN?")
        # self.port.read()

    def poweron(self):
        self.port.write("BIAS:STAT 1")
        
    def poweroff(self):
        self.port.write("BIAS:STAT 0")
                  
    def apply(self):
    
        if self.sweepmode != "None":
            self.sweepvalue = float(self.value)
            
            if self.stepmode != "None": 
                self.stepvalue = float(self.stepvalue)
        
            if self.sweepmode.startswith("Frequency"):
            
                #if self.sweepvalue < 20.0:
                #    self.sweepvalue = 20.0
                #if self.sweepvalue > 1e6:
                #    self.sweepvalue = 1e6
                    
                self.port.write("FREQ %1.5eHZ" % self.sweepvalue)
                                
                if self.stepmode.startswith("Voltage bias") or self.stepmode.startswith("Current bias"):
                    self.port.write("BIAS:%s %1.5e%s" % (self.bias_mode, self.stepvalue, self.bias_modes_units[self.bias_mode]))
                
                elif self.stepmode.startswith("Voltage RMS"):
                    self.port.write("VOLT %s MV" % (self.stepvalue*1000.0))
                    
                elif self.stepmode.startswith("Current RMS"):
                    self.port.write("CURR %s MA" % (self.stepvalue*1000.0))
        
            elif self.sweepmode.startswith("Voltage bias") or self.sweepmode.startswith("Current bias"):
        
                self.port.write("BIAS:%s %1.5e%s" % (self.bias_mode, self.sweepvalue, self.bias_modes_units[self.bias_mode]))
                
                if self.stepmode.startswith("Frequency"):
                    self.port.write("FREQ %1.5eHZ" % self.stepvalue)
                    
                elif self.stepmode.startswith("Voltage RMS"):
                    self.port.write("VOLT %s MV" % (self.stepvalue*1000.0))
                        
                elif self.stepmode.startswith("Current RMS"):
                    self.port.write("CURR %s MA" % (self.stepvalue*1000.0))   

            elif self.sweepmode.startswith("Voltage RMS"):
            
                self.port.write("VOLT %s MV" % (self.sweepvalue*1000.0))
                
                if self.stepmode.startswith("Frequency"):
                    self.port.write("FREQ %1.5eHZ" % self.stepvalue)
                  
                if self.stepmode.startswith("Voltage bias") or self.stepmode.startswith("Current bias"):
                    self.port.write("BIAS:%s %1.5e%s" % (self.bias_mode, self.stepvalue, self.bias_modes_units[self.bias_mode]))

            elif self.sweepmode.startswith("Current RMS"):
            
                self.port.write("CURR %s MA" % (self.sweepvalue*1000.0))
                
                if self.stepmode.startswith("Frequency"):
                    self.port.write("FREQ %1.5eHZ" % self.stepvalue)
                  
                if self.stepmode.startswith("Voltage bias") or self.stepmode.startswith("Current bias"):
                    self.port.write("BIAS:%s %1.5e%s" % (self.bias_mode, self.stepvalue, self.bias_modes_units[self.bias_mode]))

    def measure(self):
    
        # trigger
        if self.trigger_type == "Software":
            # only in case of Software trigger as it will be otherwise created internally or externally
            self.port.write("TRIG:IMM")
            
        # use the next two lines to check whether the last operation is completed,
        # *OPC? returns 1 whenever the last operation is completed and otherwise stop the further procedure.
        # actually needed if the trigger is set to TRIG:SOUR INT, otherwise there will be missing data
        self.port.write("*OPC?")
        self.port.read()  # reading out the answer of the previous *OPC?
                       
    def request_result(self):
        
        self.port.write("FETC?;FREQ?;BIAS:%s?" % self.bias_mode)

    def read_result(self):
    
        answer = self.port.read().split(';')

        self.R, self.X = map(float, answer[0].split(',')[0:2])
        self.F = float(answer[1])
        self.bias = float(answer[2])

    def call(self):
        return [self.R, self.X, self.F, self.bias]
