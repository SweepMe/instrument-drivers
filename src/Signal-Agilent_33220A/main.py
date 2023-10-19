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
# Device: Agilent_33220A

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
    
        EmptyDevice.__init__(self)
        
        self.idlevalue = None
        
        self.port_manager = True
        self.port_types = ['USB', 'GPIB']
        self.port_identifications = ['Agilent Technologies,33220A']

        # to be defined by user
        self.commands = {   "Sine":"SIN",
                            "Square":"SQU", 
                            "Ramp":"RAMP", 
                            "Pulse":"PULS", 
                            "Noise":"NOIS", 
                            "DC":"DC", 
                            "Arb":"USER", 
                            "Period [s]":"PER",  
                            "Frequency [Hz]":"FREQ", 
                            "HiLevel [V]":"VOLT:HIGH",  
                            "LoLevel [V]":"VOLT:LOW",
                            "Amplitude [V]":"VOLT",
                            "Offset [V]":"VOLT:OFFS",
                        }
        
        self.shortname = '33220A'
        
        
        self.plottype = [True] # True to plot data
        self.savetype = [True] # True to save data
        
        # These commands require Option 001, External Timebase Reference (see
        # page 258 for more information).
        # PHASe {<angle>|MINimum|MAXimum}
        # PHASe? [MINimum|MAXimum]
        # PHASe:REFerence
        # PHASe:UNLock:ERRor:STATe {OFF|ON}
        # PHASe:UNLock:ERRor:STATe?
        # UNIT:ANGLe {DEGree|RADian}
        # UNIT:ANGLe?

        
    def get_GUIparameter(self, parameter={}):
        # could be part of the MeasClass
        self.sweep_mode                  = parameter['SweepMode'] 
        self.waveform                    = parameter['Waveform'] 
        self.periodfrequency             = parameter['PeriodFrequency' ]
        self.periodfrequencyvalue        = parameter['PeriodFrequencyValue']
        self.amplitudehilevel            = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue       = parameter['AmplitudeHiLevelValue']
        self.offsetlolevel               = parameter['OffsetLoLevel']
        self.offsetlolevelvalue          = parameter['OffsetLoLevelValue']
        #self.dutycyclepulsewidth         = parameter['DutyCyclePulseWidth']
        #self.dutycyclepulsewidthvalue    = parameter['DutyCyclePulseWidthValue']
        #self.delayphase                  = parameter['DelayPhase']
        

        
        if self.sweep_mode == 'None':
            self.variables =[]
            self.units =    []
            self.plottype = []     # True to plot data
            self.savetype = []     # True to save data
            
        else:
            self.variables = [self.sweep_mode.split(" ")[0]]
            self.units = [self.sweep_mode.split(" ")[1][1:-1]]

        
    def set_GUIparameter(self):
        GUIparameter = {
                        "SweepMode": ["Frequency [Hz]", "Period [s]", "Amplitude [V]", "Offset [V]", "HiLevel [V]", "LoLevel [V]", "Phase [deg]",  "Delay [s]", "None"],
                        "Waveform": ["Sine", "Square", "Ramp", "Pulse", "Noise", "DC", "Arb"],
                        "PeriodFrequency" : ["Period [s]", "Frequency [Hz]"],
                        "AmplitudeHiLevel" : ["Amplitude [V]", "HiLevel [V]"],
                        "OffsetLoLevel" : ["Offset [V]", "LoLevel [V]"],
                        #"DelayPhase": ["Phase [deg]", "Delay [s]"],
                        "PeriodFrequencyValue": 1000,
                        "AmplitudeHiLevelValue": 1.0,
                        "OffsetLoLevelValue": 0.0,
                        #"DelayPhaseValue": 0,
                        #"DutyCyclePulseWidthValue": 50,
                        }
        return GUIparameter
        
    def initialize(self):
        
        self.port.write("*RST")
        
        # Autoranging the voltage port
        self.port.write("VOLT:RANG:AUTO ON")
        
    def configure(self):
        
        # set the wafeform
        self.port.write("FUNC %s" % self.commands[self.waveform])

        # set period/frequency
        self.port.write("%s %s" % (self.commands[self.periodfrequency ],self.periodfrequencyvalue))    
        self.port.write("%s %s" % (self.commands[self.amplitudehilevel],self.amplitudehilevelvalue))  
        self.port.write("%s %s" % (self.commands[self.offsetlolevel],self.offsetlolevelvalue))  
               
                        
    def deinitialize(self):
        self.port.write("*RST")
        self.port.write("SYST:LOC")
         
    def poweron(self):
        self.port.write("OUTP ON")
        
    def poweroff(self):
        self.port.write("OUTP OFF")
                                 
    def apply(self):
        if self.sweep_mode != 'None':
            self.port.write("%s %s" % (self.commands[self.sweep_mode],self.value))
                       
    def measure(self):
        if self.sweep_mode != 'None':
            self.port.write("%s?" % (self.commands[self.sweep_mode]))
            
       
    def call(self):
        # must be part of the MeasClass
        if self.sweep_mode == 'None':
            return []
        else:
            self.realvalue = float(self.port.read())
            return [self.realvalue]
        
                    