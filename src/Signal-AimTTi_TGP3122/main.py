# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
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
# Device: AIM-TTi TGP3122

from collections import OrderedDict

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    multichannel = [" CH1", " CH2"]

    def __init__(self):
    
    
        EmptyDevice.__init__(self)
        
        self.idlevalue = None
        
        self.port_manager = True
        self.port_types = ['COM']
        
        self.port_properties = {
                                "EOL": "\n",
                                "Baudrate": 9600,
                                "timeout":1,
                                #"query": "*IDN?",
                                }
        #self.port_identifications = ['']
        
        # remains here for compatibility with v1.5.3
        self.multichannel = [" CH1", " CH2"]

        # to be defined by user
        self.commands = {  
                            "Period [s]":"PER", 
                            "Frequency [Hz]":"FREQ", 
                            "HiLevel [V]":"HILVL", 
                            "LoLevel [V]":"LOLVL",
                            "Amplitude [V]":"AMPL",
                            "Offset [V]":"DCOFFS",
                            "Phase [deg]":"PHASE",
                            "Delay [s]": "PHASE",
                        }
                        
        self.waveforms = OrderedDict([
                           ("Sine", "SINE"),
                           ("Square", "SQUARE"), 
                           ("Ramp", "RAMP"), 
                           ("Pulse", "PULSE"), 
                           ("Doublepulse", "DOUBLEPULSE"),
                           ("Noise", "NOISE"),
                           ("Arb", "ARB"),
                           ("Triangle", "TRIANG")
                        ])
        
        self.plottype = [True] # True to plot data
        self.savetype = [True] # True to save data
        
               
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode" : ["Frequency [Hz]", "Period [s]", "Amplitude [V]", "Offset [V]", "HiLevel [V]", "LoLevel [V]", "Phase [deg]", "Delay [s]", "None"],
                        "Waveform": list(self.waveforms.keys()),
                        "PeriodFrequency" : ["Period [s]", "Frequency [Hz]"],
                        "AmplitudeHiLevel" : ["Amplitude [V]", "HiLevel [V]"],
                        "OffsetLoLevel" : ["Offset [V]", "LoLevel [V]"],
                        "DelayPhase": ["Phase [deg]", "Delay [s]"],
                        #"DutyCyclePulseWidth": ["Duty cycle [%]"],
                        "PeriodFrequencyValue": 1000,
                        "AmplitudeHiLevelValue": 1.0,
                        "OffsetLoLevelValue": 0.0,
                        "DelayPhaseValue": 0,
                        #"DutyCyclePulseWidthValue": 50,
                        }
                        
        return GUIparameter
                
    def get_GUIparameter(self, parameter={}):
    
        self.device = parameter['Device']
    
        self.shortname = 'TGP3122' + self.device[-4:]
        self.channel = int(self.device[-1])
        
        # could be part of the MeasClass
        self.sweep_mode                 = parameter['SweepMode'] 
        self.waveform                   = parameter['Waveform'] 
        self.periodfrequency            = parameter['PeriodFrequency' ]
        self.periodfrequencyvalue       = parameter['PeriodFrequencyValue']
        self.amplitudehilevel           = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue      = parameter['AmplitudeHiLevelValue']
        self.offsetlolevel              = parameter['OffsetLoLevel']
        self.offsetlolevelvalue         = parameter['OffsetLoLevelValue']
        self.dutycyclepulsewidth        = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue   = parameter['DutyCyclePulseWidthValue']
        self.delayphase                 = parameter['DelayPhase']
        self.delayphasevalue            = parameter['DelayPhaseValue']
        
        
        if self.sweep_mode == "None":
            self.variables = []
            self.units     = []
            self.plottype  = []     # True to plot data
            self.savetype  = []          # True to save data
            
        else:
            self.variables = [self.sweep_mode.split(" ")[0]]
            self.units = [self.sweep_mode.split(" ")[1][1:-1]]

      
    def initialize(self):
        # self.port.write("BEEPMODE ON")
    
        # self.port.write("BEEP")
        
        self.port.write("BEEPMODE OFF")
    
        self.port.write("CHN %i" % self.channel)

        self.port.write("WAVE %s" % self.waveforms[self.waveform])   

        self.port.write("ALIGN") # aligns the two channel to the same phase 

        
        # set period/frequency
        self.port.write("%s %s" % (self.commands[self.periodfrequency ], self.periodfrequencyvalue))    
        self.port.write("%s %s" % (self.commands[self.amplitudehilevel], self.amplitudehilevelvalue))  
        self.port.write("%s %s" % (self.commands[self.offsetlolevel], self.offsetlolevelvalue)) 
        
        if self.delayphase == "Delay [s]":
            if self.periodfrequency == "Period [s]":
                self.delayphasevalue = 360.0 * float(self.delayphasevalue) / float(self.periodfrequencyvalue)
            else:
                self.delayphasevalue = 360.0 * float(self.delayphasevalue) * float(self.periodfrequencyvalue)
                
            
        self.port.write("%s %s" % (self.commands[self.delayphase], self.delayphasevalue))   
               
        
        # VOLT 3.0 Set amplitude to 3 Vpp
        # VOLT:OFFS -2.5 Set offset to -2.5 Vdc
                        
    def deinitialize(self):
        pass
        # self.port.write("BEEPMODE ON")
    
        # self.port.write("BEEP")
        
        # self.port.write("BEEPMODE OFF")
        #self.port.write("*RST")
        # self.port.write("SYST:LOC")
         
    def poweron(self):
        self.port.write("CHN %i" % self.channel)
        self.port.write("OUTPUT ON")
        
    def poweroff(self):
        self.port.write("CHN %i" % self.channel)
        self.port.write("OUTPUT OFF")
                        
    def apply(self):
        
        if self.sweep_mode != 'None':
            self.port.write("CHN %i" % self.channel)
            if self.sweep_mode == "Delay [s]":
                if self.periodfrequency == "Period [s]":
                
                    self.phasevalue = 360.0 * self.value / float(self.periodfrequencyvalue)
                else:
                    self.phasevalue = 360.0 * self.value * float(self.periodfrequencyvalue)
                
                self.port.write("%s %s" % (self.commands[self.sweep_mode],self.phasevalue))
                    
            else:
                self.port.write("%s %s" % (self.commands[self.sweep_mode],self.value))
            
            
    def measure(self):
        pass
       
    def call(self):
        if self.sweep_mode != "None":
            return [self.value]
        else:
            return []
        
                    