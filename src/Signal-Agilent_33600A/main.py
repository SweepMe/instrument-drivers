# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018-2020 Axel Fischer (sweep-me.net)
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
# Device: Agilent_33600A

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    multichannel = [" CH1", " CH2"]

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.port_manager = True
        self.port_types = ['USB', 'GPIB']
        self.port_identifications = ['Agilent Technologies,336', 'Agilent Technologies,335']
        
        # remains here for compatibility with v1.5.3
        self.multichannel = [" CH1", " CH2"]

        # to be defined by user
        self.commands = {   "Sine":"SIN",
                            "Square":"SQU", 
                            "Ramp":"RAMP", 
                            "Pulse":"PULS", 
                            "Noise":"NOIS",
                            "Triangle":"TRI",
                            "DC":"DC", 
                            "Arbitrary":"ARB", 
                            "Period [s]":"PER",  
                            "Frequency [Hz]":"FREQ", 
                            "HiLevel [V]":"VOLT:HIGH",  
                            "LoLevel [V]":"VOLT:LOW",
                            "Amplitude [V]":"VOLT",
                            "Offset [V]":"VOLT:OFFS",
                        }
        
        self.waveform_standard_list = ["Sine", "Square", "Ramp", "Pulse", "Noise", "Triangle", "DC"]

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
        
    def set_GUIparameter(self):
        GUIparameter = {
                        "SweepMode": ["Frequency [Hz]", "Period [s]", "Amplitude [V]", "HiLevel [V]", "Offset [V]", "LoLevel [V]", "Pulse width [s]", "Duty cycle [%]", "Delay [s]", "Phase [deg]", "None"],
                        "PeriodFrequency" : ["Frequency [Hz]", "Period [s]"],
                        "PeriodFrequencyValue": 1000,
                        "AmplitudeHiLevel" : ["Amplitude [V]", "HiLevel [V]"],
                        "AmplitudeHiLevelValue": 1.0,
                        "OffsetLoLevel" : ["Offset [V]", "LoLevel [V]"],
                        "OffsetLoLevelValue": 0.0,
                        "DelayPhase": ["Phase [deg]", "Delay [s]"],
                        "DelayPhaseValue": 0,
                        "DutyCyclePulseWidth": ["Duty cycle [%]", "Pulse width [s]"],
                        "DutyCyclePulseWidthValue": 50,
                        "Waveform" : ["Sine", "Square", "Ramp", "Pulse", "Noise", "Triangle", "DC", "Arbitrary: <file name>"],
                        "Impedance": ["High-Z", "50 Ohm"],
                        #"Trigger": ["Not supported yet"] 
                        }
        return GUIparameter

        
    def get_GUIparameter(self, parameter={}):
        # could be part of the MeasClass
        self.channel                  = parameter['Device'][-1]
        self.sweep_mode               = parameter['SweepMode'] 
        self.waveform                 = parameter['Waveform'] 
        self.periodfrequency          = parameter['PeriodFrequency' ]
        self.periodfrequencyvalue     = float(parameter['PeriodFrequencyValue'])
        self.amplitudehilevel         = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue    = float(parameter['AmplitudeHiLevelValue'])
        self.offsetlolevel            = parameter['OffsetLoLevel']
        self.offsetlolevelvalue       = float(parameter['OffsetLoLevelValue'])
        self.dutycyclepulsewidth      = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue = float(parameter['DutyCyclePulseWidthValue'])
        self.delayphase               = parameter['DelayPhase']
        self.delayphasevalue          = float(parameter['DelayPhaseValue'])
        self.impedance                = parameter['Impedance']
        
        
        index_to_split_unit = self.sweep_mode.rfind(" ")
        
        self.variables = [self.sweep_mode[:index_to_split_unit]]
        
        self.shortname = '33600A CH' + self.channel
        
        # must be part of the MeasClass
        if self.sweep_mode == 'Frequency [Hz]':
            self.units =    ['Hz']
        elif self.sweep_mode == 'Period [s]':
            self.units =    ['s']    
        elif self.sweep_mode == 'DutyCycle [%]':
            self.units =    ['%']
        elif self.sweep_mode == 'None':
            self.variables =[]
            self.units =    []
            self.plottype = []     # True to plot data
            self.savetype = []     # True to save data
        else:
            self.units =    ['V']
        

        
    def initialize(self):
    
        pass   
        #self.port.write("*IDN?")
        #print(self.port.read())
        
        # self.port.write("*RST")
        
    def configure(self):
        
        if self.impedance == "High-Z":
            self.port.write("OUTP%s:LOAD INF" % (self.channel))
        if self.impedance == "50 Ohm":
            self.port.write("OUTP%s:LOAD 50" % (self.channel))
        
        # Autoranging the voltage port
        self.port.write("SOUR%s:VOLT:RANG:AUTO ON" % self.channel)

        
        
        # if self.sweep_mode == "DelayPhase": 
            # self.delayphase = self.value 

        if self.periodfrequency == "Period [s]":
            self.frequency = 1.0/self.periodfrequencyvalue
        else:
            self.frequency = self.periodfrequencyvalue
            
            
        if self.amplitudehilevel == "Amplitude [V]":
            self.amplitude = self.amplitudehilevelvalue
            
            if self.offsetlolevel == "Offset [V]":
                self.offset = self.offsetlolevelvalue
            else:
                self.offset = (self.amplitudehilevelvalue/2.0 + self.offsetlolevelvalue)
              
        else:
            if self.offsetlolevel == "Offset [V]":
                self.amplitude = (self.amplitudehilevelvalue - self.offsetlolevelvalue)*2.0
                self.offset = self.offsetlolevelvalue
            else:
                self.amplitude = self.amplitudehilevelvalue - self.offsetlolevelvalue
                self.offset = (self.amplitudehilevelvalue - self.offsetlolevelvalue)/2.0
                

        ### Get Arbitrary Waveform ###
        
        if self.waveform.startswith("Arbitrary:") or self.waveform not in self.waveform_standard_list:
        
            # we strip off all file extensions and whitespaces and also the leading 'Arbitrary:" if it has been used
            # further we only use uppercase as the device as anyway just knows uppercase file names 
            waveform_command = self.waveform.replace("Arbitrary:","").strip().replace(".ARB","").replace(".arb","").replace(".Arb","").upper() 
            
            self.port.write("SOUR%s:FUNC ARB" % (self.channel))
            self.port.write("FUNC:USER %s" % (waveform_command))

            # check if function is set correctly
            self.port.write("FUNC:USER?")
            answer = self.port.read()

            #print(answer,waveform_command)

            if answer != waveform_command:
                self.stop_Measurement("Cannot find the selected user function %s (check spelling/uppercases) " % waveform_command)
                return False
                
            waveform_type = "USER"
        
        else:
            
            waveform_type = self.commands[self.waveform]
            

        self.port.write("SOUR%s:APPL:%s %s, %s, %s" % (self.channel, waveform_type, self.frequency, self.amplitude, self.offset))
            
        
        
        if self.waveform == "Pulse":
            if self.dutycyclepulsewidth ==  "Pulse width [s]":
                self.port.write("SOUR%s:FUNC:PULS:WIDT %s " % (self.channel ,self.dutycyclepulsewidthvalue))
                
            if self.dutycyclepulsewidth ==  "Duty cycle [%]":
                self.port.write("SOUR%s:FUNC:PULS:DCYC %s " % (self.channel ,self.dutycyclepulsewidthvalue))
                
        elif self.waveform == "Square":
            if self.dutycyclepulsewidth ==  "Duty cycle [%]":
                self.port.write("SOUR%s:FUNC:SQU:DCYC %s " % (self.channel ,self.dutycyclepulsewidthvalue))
                
                
        if self.delayphase ==  "Delay [s]": 
            self.phase = self.delayphasevalue * self.frequency * 360.0

                    
        elif self.delayphase ==  "Phase [deg]":
            self.phase = self.delayphasevalue
            
        
        if not waveform_type == "DC":
            self.port.write("SOUR%s:PHAS %s DEG" % (self.channel, self.phase))

                                  
    def deinitialize(self):
        pass
        # self.port.write("*RST")
        # self.port.write("SYST:LOC")
         
    def poweron(self):
        self.port.write("OUTP%s ON" % self.channel)
        
    def poweroff(self):
        self.port.write("OUTP%s OFF" % self.channel)
        
        # we have to ask to really switch off and we do not know why
        self.port.write("OUTP?")
        answer = self.port.read()
        #print(answer)
                                 
    def apply(self):
    
        if self.sweep_mode == 'None':
            pass
            
        else:
        
            if self.sweep_mode == "Frequency [Hz]":
                self.periodfrequency = "Frequency [Hz]"
                self.periodfrequencyvalue = self.value
            
            if self.sweep_mode == "Period [s]":
                self.periodfrequency = "Frequency [Hz]"
                self.periodfrequencyvalue = 1.0/self.value
                
            if self.sweep_mode == "Amplitude [V]":  
                self.amplitudehilevel = "Amplitude [V]"
                self.amplitudehilevelvalue = self.value
                
            if self.sweep_mode == "HiLevel [V]":
                self.amplitudehilevel = "HiLevel [V]"
                self.amplitudehilevelvalue = self.value
                   
            if self.sweep_mode == "Offset [V]": 
                self.offsetlolevel = "Offset [V]"
                self.offsetlolevelvalue = self.value   

            if self.sweep_mode == "LoLevel [V]":
                self.offsetlolevel = "LoLevel [V]"
                self.offsetlolevelvalue = self.value        
        
            if self.periodfrequency == "Period [s]":
                self.frequency = 1.0 / self.periodfrequencyvalue
            else:
                self.frequency = self.periodfrequencyvalue
                
            if self.amplitudehilevel == "Amplitude [V]":
                self.amplitude = self.amplitudehilevelvalue
                
                if self.offsetlolevel == "Offset [V]":
                    self.offset = self.offsetlolevelvalue
                else:
                    self.offset = (self.amplitudehilevelvalue/2.0 + self.offsetlolevelvalue)
                  
            else:
                if self.offsetlolevel == "Offset [V]":
                    self.amplitude = (self.amplitudehilevelvalue - self.offsetlolevelvalue)*2.0
                    self.offset = self.offsetlolevelvalue
                else:
                    self.amplitude = self.amplitudehilevelvalue - self.offsetlolevelvalue
                    self.offset = (self.amplitudehilevelvalue + self.offsetlolevelvalue)/2.0
           
            
            self.port.write("SOUR%s:FREQ %s" % (self.channel, self.frequency))  
            self.port.write("SOUR%s:VOLT %s" % (self.channel, self.amplitude))  
            self.port.write("SOUR%s:VOLT:OFFS %s" % (self.channel, self.offset))  
                
            if self.sweep_mode == "Pulse width [s]":
                self.dutycyclepulsewidthvalue = self.value
                
            if self.sweep_mode == "Duty cycle [%]":
                self.dutycyclepulsewidthvalue = self.value
                
            if self.waveform == "Pulse":
                if self.dutycyclepulsewidth ==  "Pulse width [s]":
                    self.port.write("SOUR%s:FUNC:PULS:WIDT %s " % (self.channel, self.dutycyclepulsewidthvalue))
                    
                if self.dutycyclepulsewidth ==  "Duty cycle [%]":
                    self.port.write("SOUR%s:FUNC:PULS:DCYC %s " % (self.channel, self.dutycyclepulsewidthvalue))
                 
                 
            if self.sweep_mode == "Delay [s]": 
                self.phase = self.value * self.frequency * 360.0
                self.port.write("SOUR%s:PHAS %s DEG " % (self.channel, self.phase))
                
            if self.sweep_mode == "Phase [deg]":
                self.phase = self.value
                self.port.write("SOUR%s:PHAS %s DEG " % (self.channel, self.phase))
            
            
    def measure(self):

        if self.sweep_mode != 'None':
            self.port.write("SOUR%s:APPL?" % (self.channel))
            
    
    def call(self):
        
        if self.sweep_mode == 'None':
            return []
        else:
        
            answer = self.port.read().replace("\"", "").split(" ")[1].split(",")
            
            frequency, amplitude, offset = map(float, answer)
            
            if self.sweep_mode == "Frequency [Hz]":
                returnvalue = frequency
            
            if self.sweep_mode == "Period [s]":
                returnvalue = 1.0/frequency
                
            if self.sweep_mode == "Amplitude [V]":  
                returnvalue = amplitude
                
            if self.sweep_mode == "HiLevel [V]":
                returnvalue = offset + amplitude/2.0
                   
            if self.sweep_mode == "Offset [V]": 
                returnvalue = offset

            if self.sweep_mode == "LoLevel [V]":
                returnvalue = offset - amplitude/2.0
                
            if self.sweep_mode == "Duty cycle [%]" or self.sweep_mode == "Pulse width [s]":
                returnvalue = self.value
                
            if self.sweep_mode == "Delay [s]" or self.sweep_mode == "Phase [deg]":
                returnvalue = self.value

            return [returnvalue]
        
                    