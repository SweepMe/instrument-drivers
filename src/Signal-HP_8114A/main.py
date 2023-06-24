# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2019 - 2020 Axel Fischer (sweep-me.net)
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
# Type: Signal
# Device: HP 8114A

"""
The protection limits are switched off.
It can happen that the pulse generator does not switch off after the measurement for unknown reason.
"""


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.idlevalue = None
        
        self.port_manager = True
        self.port_types = ['GPIB']
        #self.port_identifications = ['']

        # to be defined by user
        self.commands = {
                            "Period [s]":":PULS:PER %sS",  
                            "Frequency [Hz]":"FREQ %s", 
                            "HiLevel [V]":":VOLT:HIGH %sV",  
                            "LoLevel [V]":":VOLT:LOW %sV",
                            "Phase [deg]": "PHAS %s",
                            "Delay [s]": ":PULS:DEL %sS",
                            "PulseWidth [s]": ":PULS:WIDT %sS",
                            "DutyCycle [%]":":PULS:DCYC %s",
                            "50 Ohm" : ":OUTP:IMP:EXT 50OHM",
                            "High-Z" : ":OUTP:IMP:EXT 999KOHM",
                        }
        
        
        # to be defined by user
        self.ask_commands = {
                            "Period [s]":":PULS:PER?",  
                            "Frequency [Hz]":"FREQ?", 
                            "HiLevel [V]":":VOLT:HIGH?",  
                            "LoLevel [V]":":VOLT:LOW?",
                            "Phase [deg]": "PHAS?",
                            "Delay [s]": ":PULS:DEL?",
                            "PulseWidth [s]": ":PULS:WIDT?",
                            "DutyCycle [%]":":PULS:DCYC?",
                        }
        
        self.shortname = 'HP8114A'
        
        
        
    def set_GUIparameter(self):
        GUIparameter = {
                        "SweepMode": ["None", "Frequency [Hz]", "Period [s]", "HiLevel [V]", "LoLevel [V]", "Phase [deg]",  "Delay [s]", "Pulse width [s]", "Duty cycle [%]"],
                        "Waveform": ["Pulse positive", "Pulse negative"],
                        "PeriodFrequency" : ["Frequency [Hz]", "Period [s]"],
                        "AmplitudeHiLevel" : ["HiLevel [V]"],
                        "OffsetLoLevel" : ["LoLevel [V]"],
                        "DelayPhase": ["Phase [deg]", "Delay [s]"],
                        "PeriodFrequencyValue": 1000,
                        "AmplitudeHiLevelValue": 1.0,
                        "OffsetLoLevelValue": 0.0,
                        "DelayPhaseValue": 0,
                        "DutyCyclePulseWidth": ["DutyCycle [%]", "PulseWidth [s]"], 
                        "DutyCyclePulseWidthValue": 50,
                        "Impedance" : ["50 Ohm", "High-Z"],
                        }
        return GUIparameter               
        
        
        
    def get_GUIparameter(self, parameter={}):

        self.sweep_mode                  = parameter['SweepMode'] 
        self.waveform                    = parameter['Waveform'] 
        self.periodfrequency             = parameter['PeriodFrequency' ]
        self.periodfrequencyvalue        = float(parameter['PeriodFrequencyValue'])
        self.hilevel                     = parameter['AmplitudeHiLevel']
        self.hilevelvalue                = float(parameter['AmplitudeHiLevelValue'])
        self.lolevel                     = parameter['OffsetLoLevel']
        self.lolevelvalue                = float(parameter['OffsetLoLevelValue'])
        self.dutycyclepulsewidth         = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue    = float(parameter['DutyCyclePulseWidthValue'])
        self.delayphase                  = parameter['DelayPhase']
        self.delayphasevalue             = parameter['DelayPhaseValue']
        self.impedance                   = parameter['Impedance']
        

        if self.sweep_mode == 'None':
            self.variables =[]
            self.units =    []
            self.plottype = []     # True to plot data
            self.savetype = []     # True to save data
            
        else:
            self.variables = [self.sweep_mode.split(" ")[0]]
            self.units = [self.sweep_mode.split(" ")[1][1:-1]]
            self.plottype = [True] # True to plot data
            self.savetype = [True] # True to save data
            
        
    def initialize(self):
    
        #if self.impedance == "50 Ohm":
        #    if float(self.amplitudehilevelvalue) <= 1.0:
        #        self.stop_Measurement("Please choose an amplitude above 1 V")
        #        return False
        #        
        #else:
        #    if float(self.amplitudehilevelvalue) <= 2.0:
        #        self.stop_Measurement("Please choose an amplitude above 2 V")
        #        return False
            
        self.port.write("*RST") # Reset to standard parameter
        #self.port.write("*IDN?")
        #print(self.port.read())
        
        self.port.write(":OUTP:POS")  # has nothing to do with positive and negative mode
        
        self.port.write(":VOLT:LIM:STAT OFF")
        
    def deinitialize(self):
        self.port.write(":SYST:KEY 19")   # figure out why it does not go back to LOCAL    
        
        
    def poweron(self):
        self.port.write(":OUTP ON")
        
    def poweroff(self):
        self.port.write(":OUTP OFF")

        
    def configure(self):
    
        # set negative or positive
        if self.waveform == "Pulse positive":
            self.port.write("OUTP:POL POS")
        elif self.waveform == "Pulse negative":
            self.port.write("OUTP:POL NEG")
        else:
            self.port.write("OUTP:POL POS")
        
        # set the impedance value
        self.port.write("%s" % (self.commands[self.impedance]))    
        
        # period or frequency      
        self.port.write(self.commands[self.periodfrequency] % self.periodfrequencyvalue)  
        
        # Voltage system
        self.port.write(":HOLD VOLT")
        
        self.port.write(":VOLT:HIGH %sV" % self.hilevelvalue) # amplitude
        self.port.write(":VOLT:LOW %sV" % self.lolevelvalue) # amplitude
        
        # Delay / Phase
        self.port.write(self.commands[self.delayphase] % self.delayphasevalue) 
        
        # Pulse width / Duty cycle
        self.port.write(self.commands[self.dutycyclepulsewidth] % self.dutycyclepulsewidthvalue)  

                                 
    def apply(self):
        if self.sweep_mode != 'None':
            self.port.write(self.commands[self.sweep_mode] % self.value) 
            
          
    def measure(self):
        if self.sweep_mode != 'None':
            self.port.write("%s" % (self.ask_commands[self.sweep_mode]))
      

    def call(self):
        # must be part of the MeasClass
        if self.sweep_mode == 'None':
            return []
        else:
            realvalue = float(self.port.read())
            #print(realvalue)
            return [realvalue]
                   