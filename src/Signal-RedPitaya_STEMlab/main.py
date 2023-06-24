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

# Contribution: We like to thank TU Dresden/Toni Bärschneider for providing the initial version of this driver.

# SweepMe! device class
# Type: Signal
# Device: Red pitaya STEMlab


# TODO:
# -> arbitrary wavefunction implementation

import numpy as np
import time

from FolderManager import addFolderToPATH
addFolderToPATH()

import redpitaya_scpi as scpi
from ErrorMessage import error
from collections import OrderedDict

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        EmptyDevice.__init__(self)
        self.shortname = "STEMlab"
        
        self.waveforms = OrderedDict([
                           ("Sine", "SINE"),
                           ("Square", "SQUARE"), 
                           ("Triangle", "TRIANGLE"), 
                           ("Saw up", "SAWU"), 
                           ("Saw down", "SAWD"),
                           ("PWM", "DC"),
                           ("Arbitrary", "ARBITRARY"),
                           ("DC", "PWM")
                        ])
        self.triggertypes = OrderedDict([
                           ("External NE", "EXT_NE"), 
                           ("External PE", "EXT_PE"), 
                           ("Internal", "INT"), 
                           ("Immediately", "IMM"), 
                           ("Gated", "GATED")
                        ])
                        
        self.operationmodes = OrderedDict([
                           ("Continuous", "CONTINUOUS"), 
                           ("Burst", "BURST"), 
                           ("Stream", "STREAM")
                        ])
                        
    def set_GUIparameter(self):
    
        gui_parameter = {
                        "SweepMode": ["None", "Frequency in Hz", "Period in s", "Amplitude in V", "Offset in V", "High level in V", "Low level in V", "Phase in °", "Delay in s"],
                        "Channel": ["1", "2"],
                        "Waveform": list(self.waveforms.keys()),
                        "PeriodFrequency" : ["Frequency in Hz", "Period in s"],
                        "AmplitudeHiLevel" : ["Amplitude in V", "High level in V"],
                        "OffsetLoLevel" : ["Offset in V", "Low level in V"],
                        "DelayPhase": ["Phase in °", "Delay in s"],
                        "DutyCyclePulseWidth": ["Duty cycle in %"],
                        "PeriodFrequencyValue": 1000,
                        "AmplitudeHiLevelValue": 0.9,
                        "OffsetLoLevelValue": 0.0,
                        "DelayPhaseValue": 0,
                        "DutyCyclePulseWidthValue": 50,
                        "Trigger": list(self.triggertypes.keys()),
                        "OperationMode": list(self.operationmodes.keys()),
                        "BurstRepetitions": 1,
                        'BurstSignalRepetitions': 3,
                        "BurstDelay": 0,
                        "ArbitraryWaveformFile": self.get_folder("CUSTOMFILES"),
                        }
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):

        self.device = parameter['Device']
        self.channel = int(parameter['Channel'])
        self.ip_address = parameter["Port"]
        self.sweep_mode                 = parameter['SweepMode'] 
        self.waveform                   = parameter['Waveform'] 
        self.periodfrequency            = parameter['PeriodFrequency']
        self.periodfrequencyvalue       = float(parameter['PeriodFrequencyValue'])
        self.amplitudehilevel           = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue      = float(parameter['AmplitudeHiLevelValue'])
        self.offsetlolevel              = parameter['OffsetLoLevel']
        self.offsetlolevelvalue         = float(parameter['OffsetLoLevelValue'])
        self.dutycyclepulsewidth        = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue   = float(parameter['DutyCyclePulseWidthValue'])
        self.delayphase                 = parameter['DelayPhase']
        self.delayphasevalue            = float(parameter['DelayPhaseValue'])
        self.triggertype                = parameter["Trigger"]
        self.operationmode              = parameter["OperationMode"]
        self.burstnumber                = int(parameter["BurstRepetitions"])
        self.periodnumber               = int(parameter["BurstSignalRepetitions"])
        self.burstdelay                 = float(parameter["BurstDelay"])
        self.waveformarray              = parameter['ArbitraryWaveformFile']  # np.array([1, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        if self.sweep_mode == "None":
            self.variables = []
            self.units     = []
            self.plottype  = []
            self.savetype  = []
            
        else:
            self.variables = [self.sweep_mode.split(" ")[0]]
            self.units = [self.sweep_mode.split(" ")[1][1:-1]]
            self.plottype = [True]
            self.savetype = [True]
  
    def connect(self):
        self.port = scpi.scpi(self.ip_address)
        
        self.port.write = self.port.tx_txt      # redefine scpi-write command
        self.port.read = self.port.rx_txt       # redefine scpi-read command

        # identification = self.get_identification()
        # print("Identification", identification)
  
    def initialize(self): 
        pass
        
    def configure(self):
        self.limits = 1.0       # +/- Voltage limit of frequency generator
        
        # Reset Generator
        self.port.write('GEN:RST')                                                              
        
        # Set waveform
        self.port.write('SOUR{0}:FUNC {1}'.format(self.channel, self.waveforms[self.waveform]))  # Set waveform
        
        # set arbitrary waveform
        if self.waveforms[self.waveform] == "ARBITRARY":
            self.waveformarray = np.loadtxt(self.waveformarray)
            np.set_printoptions(threshold=np.nan)
            self.port.write('SOUR{0}:TRAC:DATA:DATA {1}'.format(self.channel, np.array2string(self.waveformarray, precision=5, separator=",")[1:-1].replace(" ", "").replace("\n", "")))
        
        # Set PWM duty cycle
        if self.waveform == "PWM":
            self.set_duty_cycle()
        
        # set frequency
        self.set_frequency()
        
        # convert Delay to Phase
        self.set_phase()
        
        # convert High level, Low level to Amplitude and Offset
        self.set_amplitude_offset()

    def apply(self):
        # print("SweepValue:", self.value)
        # Frequency or Period SweepMode
        if self.sweep_mode == "Frequency in Hz" or self.sweep_mode == "Period in s":
            self.periodfrequency = self.sweep_mode
            self.periodfrequencyvalue = self.value
            self.set_frequency()
            
        # Amplitude or Offset SweepMode
        elif self.sweep_mode == "Amplitude in V" or self.sweep_mode == "Offset in V" or self.sweep_mode == "High level in V" or self.sweep_mode == "Low level in V":
            # print("sweep:", self.value)
            if self.sweep_mode == "Amplitude in V" or self.sweep_mode == "High level in V":
                self.amplitudehilevel = self.sweep_mode
                self.amplitudehilevelvalue = self.value
            else:
                self.offsetlolevel = self.sweep_mode
                self.offsetlolevelvalue = self.value
            self.set_amplitude_offset()
        
        # Phase or Delay SweepMode
        elif self.sweep_mode == "Phase in °" or self.sweep_mode == "Delay in s":
            self.delayphase = self.sweep_mode
            self.delayphasevalue = self.value
            self.set_phase()
            
    def trigger_ready(self):
        
        # set trigger
        if self.triggertypes[self.triggertype] == "IMM":
            self.port.write('SOUR{0}:TRIG:IMM'.format(self.channel))
            self.port.write('SOUR{0}:BURS:STAT CONTINUOUS'.format(self.channel))
        else:
            self.port.write('SOUR{0}:TRIG:SOUR {1}'.format(self.channel, self.triggertypes[self.triggertype]))
            self.port.write('SOUR{0}:BURS:STAT CONTINUOUS'.format(self.channel))

        # set burst mode (after trigger settings!)
        self.set_burst_mode()                                          # set Burst mode
        
        # enable output
        self.port.write('OUTPUT{0}:STATE ON'.format(self.channel))
        self.port.write('OUTPUT{0}:STATE?'.format(self.channel))        
    
    def measure(self):
        pass
        # self.settings_status()  # print status
    
    def call(self):
        if self.sweep_mode != "None":
            return [self.value]
        else:
            return []
        
    def deinitialize(self):
        # print("Disable Frequency Generator Channel {}!".format(self.channel))
        self.port.write('OUTPUT{0}:STATE OFF'.format(self.channel))     # disable output

    # Functions
    
    def set_amplitude_offset(self):
        # convert Highlevel, LowLevel to Amplitude and Offset
        if self.amplitudehilevel == "High level in V" and self.offsetlolevel == "Low level in V":
            self.amplitude = abs((self.amplitudehilevelvalue - self.offsetlolevelvalue) / 2)
            self.offset = (self.amplitudehilevelvalue + self.offsetlolevelvalue) / 2
        elif self.amplitudehilevel == "High level in V" and self.offsetlolevel == "Offset in V":
            self.amplitude = abs(self.amplitudehilevelvalue - self.offsetlolevelvalue)
            self.offset = self.offsetlolevelvalue
        elif self.amplitudehilevel == "Amplitude in V" and self.offsetlolevel == "Low level in V":
            self.amplitude = self.amplitudehilevelvalue
            self.offset = self.amplitudehilevelvalue + self.offsetlolevelvalue
        elif self.amplitudehilevel == "Amplitude in V" and self.offsetlolevel == "Offset in V":
            self.amplitude = self.amplitudehilevelvalue
            self.offset = self.offsetlolevelvalue
        
        # set limits
        self.set_limits()
        
        # set amplitude
        self.port.write('SOUR{0}:VOLT {1:1.7f}'.format(self.channel, self.amplitude))
        
        # set offset
        self.port.write('SOUR{0}:VOLT:OFFS {1:1.7f}'.format(self.channel, self.offset))

    def set_duty_cycle(self):
        # convert duty cycle
        if self.dutycyclepulsewidthvalue < 0.0:
            self.dutycycle = 0.0
        elif self.dutycyclepulsewidthvalue > 100.0:
            self.dutycycle = 100.0
        else:
            self.dutycycle = self.dutycyclepulsewidthvalue/100.0
            
        # set duty cycle
        self.port.write('SOUR{0}:DCYC {1:1.7f}'.format(self.channel, self.dutycycle))

    def set_phase(self):
        # convert Delay to Phase
        if self.delayphase == "Delay in s":
            self.phase = self.frequency*360*self.delayphasevalue
        else:
            self.phase = self.delayphasevalue
        if abs(self.phase) > 360:
            self.phase = np.sign(self.phase) * (self.phase % 360)
        
        # set phase
        self.port.write('SOUR{0}:PHAS {1:1.7f}'.format(self.channel, self.phase))

    def set_frequency(self):
        # convert period to frequency
        if self.periodfrequency == "Period in s":
            self.frequency = 1.0/self.periodfrequencyvalue
        else:
            self.frequency = self.periodfrequencyvalue
        
        # set frequency
        self.port.write('SOUR{0}:FREQ:FIX {1:1.7f}'.format(self.channel, self.frequency))

    def set_limits(self):
        if self.amplitude > self.limits:
            self.amplitude = self.limits
        if abs(self.offset) > self.limits:
            self.offset = self.limits * np.sign(self.offset)
        if abs(abs(self.offset)+self.amplitude) > self.limits:
            self.offset = np.sign(self.offset) * (self.limits-self.amplitude)

    def settings_status(self):
        print("\nFrequency generator channel {0} settings:".format(self.channel))
        self.port.write('OUTPUT{0}:STATE?'.format(self.channel))
        print("\tOutput status:", self.port.read())
        self.port.write('SOUR{0}:FUNC?'.format(self.channel))
        print("\tWaveform:", self.port.read())
        self.port.write('SOUR{0}:FREQ:FIX?'.format(self.channel))
        print("\tFrequency:", self.port.read())
        self.port.write('SOUR{0}:PHAS?'.format(self.channel))
        print("\tPhase:", self.port.read())
        self.port.write('SOUR{0}:VOLT?'.format(self.channel))
        print("\tAmplitude:", self.port.read())
        self.port.write('SOUR{0}:VOLT:OFFS?'.format(self.channel))
        print("\tOffset:", self.port.read())
        self.port.write('SOUR{0}:DCYC?'.format(self.channel))
        print("\tDuty cycle:", self.port.read())
        self.port.write('SOUR{0}:BURS:STAT?'.format(self.channel))
        print("\tBurst status:", self.port.read())
        self.port.write('SOUR{0}:BURS:NOR?'.format(self.channel))
        print("\tNumber of bursts:", self.port.read())
        self.port.write('SOUR{0}:BURS:NCYC?'.format(self.channel))
        print("\tNumber of periods in burst:", self.port.read())
        self.port.write('SOUR{0}:BURS:INT:PER?'.format(self.channel))
        print("\tBurst period:", self.port.read(), "\n")

    def set_burst_mode(self):
        self.port.write('SOUR{0}:BURS:STAT {1}'.format(self.channel, self.operationmodes[self.operationmode]))  # set OperationMode
        if self.operationmodes[self.operationmode] != "CONTINUOUS":
            self.burstperiod = 10**6 * (self.periodnumber / self.frequency + self.burstdelay)
            self.port.write('SOUR{0}:BURS:INT:PER {1}'.format(self.channel, self.burstperiod))          # set total Burst period (signal + delay)
            self.port.write('SOUR{0}:BURS:NOR {1}'.format(self.channel, self.burstnumber))            # set number of Periods in one Burst
            self.port.write('SOUR{0}:BURS:NCYC {1}'.format(self.channel, self.periodnumber))              # set number of repeated Bursts

    def get_identification(self):

        self.port.write("*IDN?")
        return self.port.read()
