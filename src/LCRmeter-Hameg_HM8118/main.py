# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2019 Axel Fischer (sweep-me.net)
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
# Type: LCRmeter
# Device: Hameg HM8118

import numpy as np

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "HM8118"
        
        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units     = ["V/A", "V/A", "Hz", "V"]
        self.plottype  = [True, True, True, True] # True to plot data
        self.savetype  = [True, True, True, True] # True to save data
        
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        self.port_properties = {
                                "timeout":20,
                                "EOL": "\r",
                                "baudrate": 9600,
                                "delay": 0.15,
                                }
                                
        self.allowed_frequencies = np.asarray([20, 24, 25, 30, 36, 40, 45, 50, 60, 72, 75, 80, 90, 100, 120, 150, 180, 200, 240,  250, 300, 360, 400, 450, 500, 600, 720,  750,  800, 900,  1e3, 1200, 1500, 1800, 2e3, 2400, 2500, 3e3, 3600, 4e3, 4500, 5e3, 6e3, 7200, 7500, 8e3, 9e3, 10e3, 12e3, 15e3, 18e3, 20e3, 24e3, 25e3, 30e3, 36e3, 40e3, 45e3, 50e3, 60e3, 72e3, 75e3, 80e3, 90e3, 100e3, 120e3, 150e3, 180e3, 200e3])
        
    def set_GUIparameter(self):
        # here we set values that are displayed in the graphical user interface (GUI) of the LCRmeter module
        # it is a dictionary and each key is related
        
        GUIparameter = {
                        "Average": ["1", "2", "4", "8", "16", "32", "64"],
                        
                        "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
                        "StepMode": ["None", "Frequency in Hz", "Voltage bias in V"],
                        
                        
                        "Integration": ["Fast", "Medium", "Slow"],
                        
                        "ValueTypeRMS": ["Voltage RMS in V:"],
                        "ValueRMS": 0.1, # minimum possible signal
                        
                        "ValueTypeBias": ["Voltage bias in V:"],
                        "ValueBias": 0.0,
                        
                        "Frequency": 1000.0,
                        
                        "Trigger": ["Internal", "External"],
                        
                        "TriggerDelay": 0.0,
                        
                        "ExternalBias": False,
                        }
                        
        
        return GUIparameter
                                 
    def get_GUIparameter(self, parameter = {}):
        self.sweepmode = parameter['SweepMode']
        self.stepmode = parameter['StepMode']
        
        self.ValueTypeRMS = parameter['ValueTypeRMS']
        self.ValueRMS = float(parameter['ValueRMS'])
        
        self.ValueTypeBias =  parameter["ValueTypeBias"]
        self.ValueBias = float(parameter["ValueBias"])
        
        integration = parameter['Integration']
        if integration == "Fast":
            self.integration_index = 0
        elif integration == "Medium":
            self.integration_index = 1
        elif integration == "Slow":
            self.integration_index = 2
        
        self.average = int(parameter['Average'])
        
        self.trigger_type = parameter['Trigger']
        
        self.trigger_delay = float(parameter['TriggerDelay'])
        
        self.external_bias = parameter['ExternalBias']
        
        self.ValueFrequency = float(parameter['Frequency'])
                      

    def initialize(self):
    
        ### we can do some pre-tests to inform the user about values that are not accepted ###
        
        # Voltage RMS
        if self.ValueRMS < 0.05 or self.ValueRMS > 1.5:
            self.messageBox("The AC signal (Voltage RMS in V) of the Hameg HM8118 must be between 0.05 V and 1.5 V. Please choose a value, accordingly")
            return False
          
        # Voltage bias
        if self.ValueTypeBias.startswith("Voltage bias"):
            if self.ValueBias < 0.00 or self.ValueBias > 5.0:
                self.messageBox("The voltage bias of the Hameg HM8118 must be between 0 V and 5 V. Please choose a value, accordingly")
                return False   
            
        #Frequency
        if self.ValueFrequency < 20 or self.ValueFrequency > 200e3:
            self.messageBox("The frequency of the Hameg HM8118 must be between 20 Hz and 200 kHZ. Please choose a value, accordingly")
            return False  


        # Triggerdelay
        if self.trigger_type == "Internal": 
            if self.trigger_delay < 0.0 or self.trigger_delay > 40:
                self.messageBox("The trigger delay of the Hameg HM8118 must be between 0 s and 40 s. Please choose a value, accordingly")
                return False


        # to check proper communication, we are asking for the identification string
        # can be commented out later
        self.port.write("*IDN?")
        print("Identification string:", self.port.read())
        
        # lets reset the device to default values.
        # This makes sure that we always restore the same configuration
        self.port.write("*RST")
        
        # lock the display so that users cannot interfere with the measurement 
        self.port.write("LOCK 1")
        
        # sets the equivalent circuit to parallel
        self.port.write("CIRC 1")
        
        # measurement range = auto
        # it applies to all possible measurement procedures so it can be set once during initialize
        self.port.write("RNGH 0")
        
        # display normal values
        self.port.write("OUTP 0")

        
    def configure(self):
        
        # integration type : Fast, Medium or Slow
        self.port.write("RATE %i" % self.integration_index)

        # averages
        if self.average <= 1:
            # switch off average mode
            self.port.write("AVGM 0")
        else:
            # switch on average mode
            self.port.write("AVGM 1")   
            # the number of averages can be between 2 and 99
            self.port.write("NAVG %i" % (self.average))
            
        

        # measurement mode    
        self.port.write("PMOD 8") # R-X measures real and imaginary part of the impedance 
        # i=0 : AUTO
        # i=1 : L-Q
        # i=2 : L-R
        # i=3 : C-D
        # i=4 : C-R
        # i=5 : R-Q
        # i=6 : Z-Θ
        # i=7 : Y+Θ
        # i=8 : R+X
        # i=9 : G+B
        # i=10 : N+Θ
        # i=11 : M
        
        # trigger mode
        if self.trigger_type == "Internal": 
            self.port.write("MMOD 1") # internally triggered by software sending *TRG
            # important to trigger a new measurement, to make sure that a former condition or state does not influence the new measurement point, continuous mode might lead to wrong values, e.g. if voltage or frequency quickly changes
        elif self.trigger_type == "External": 
            self.port.write("MMOD 2") # externally triggered by TTL pulse, see manual
            
            self.port.write("$STL %i" % int(float(self.trigger_delay)*1000)) # trigger delay is sent in ms           
            
        else:
            self.port.write("MMOD 0") # no trigger, measurement is running continuously
        
        
        ### setting values defined by the gui ###
        # they might be overwritten by sweep mode or step mode
        
        # frequency
        self.port.write("FREQ %1.5e" % self.ValueFrequency)
        
        # oscillator voltage of the AC signal       
        if self.ValueTypeRMS.startswith("Voltage RMS"):
            self.port.write("VOLT %1.3f" % (self.ValueRMS))   

        # bias
        if self.ValueTypeBias.startswith("Voltage bias"):
            self.port.write("VBIA %1.3e" % self.ValueBias)
            
    def unconfigure(self):
        # standard frequency is 1kHz
        self.port.write("FREQ 1000")
        
        # amplitude is set back to 100 mV
        self.port.write("VOLT 0.10") 
        
        # measurement mode    
        self.port.write("PMOD 3") # C-D to see capacitance if measurement is not running
        
        # trigger mode
        self.port.write("MMOD 0") # continuous measurement 
                
        # when the measurement is finished, the device is set back to 0V to not accidentally apply any voltage to a device
        self.port.write("VBIA 0") 

    def deinitialize(self):
        # after the measurement we remove the lock so that users can use the front panel again
        self.port.write("LOCK 0")

    
    def poweron(self):
        # switch on bias mode
        self.port.write("BIAS 1")
        # use "BIAS 2" to use an external bias, currently not supported by the GUI 
        
    def poweroff(self):
        # switch off bias mode
        self.port.write("BIAS 0") 
                  
    def apply(self):
    
        # lets make sure that we have floats, e.g. in case variables are strings
        self.stepvalue = float(self.stepvalue)
        self.value = float(self.value)

        # here the stepmode as given by an external module is applied
        if self.stepmode.startswith("Voltage bias"):
            self.port.write("VBIA %1.3e" % self.stepvalue)
            
        elif self.stepmode.startswith("Frequency"):
            f_set = self.find_nearest_frequency(float(self.stepvalue))
            self.port.write("FREQ %1.5e" % f_set)


        # here, the sweepmode as given in the module itself is applied
        if self.sweepmode.startswith("Voltage bias"):
            self.port.write("VBIA %1.3f" % self.value)
            
        elif self.sweepmode.startswith("Frequency"):
            f_set = self.find_nearest_frequency(float(self.value))
            self.port.write("FREQ %1.5e" % f_set)
            
            
    def measure(self):
        
        # we only have to trigger a measurement by software if 'Internal' is selected as trigger
        if self.trigger_type == "Internal":
            # we trigger a measurement
            #self.port.write('*TRG')
            #self.port.write("*OPC?")
            
            #alternative: 
            self.port.write("*TRG; *OPC?")
            
            # before the measurment is not completed no further command will be processed by the LCR meter
            # self.port.write('*WAI')


    def request_result(self):
        # lets wait for the result of *OPC? and then we can continue to trigger again
        self.port.read()
        #print(self.port.read())
        #A = self.port.read()
        #print(A)
        
        
        self.port.write("XALL?") # call R and X


    def read_result(self):
        
        # first, we read the answer of XALL?
        answer = self.port.read().split(",")
        #print("variable answer:",answer) # just to check how the output looks like, should be a list of strings, only needed for debugging 
        values = list(map(float, answer)) # create a list of floats
        #print("variable values:",values)
        self.R, self.X = values[0:2] #  the first two values should be R and X
        #print("self.R:",self.R)
        #print("self.X:",self.X)
        
        # now we read the answer of FREQ?
        self.port.write("FREQ?") # call the frequency
        self.F = float(self.port.read())
        #print("self.F:", self.F)
        
        # and finally we read the answer to get the bias by using VBIA?
        self.port.write("VBIA?")     
        self.Bias = float(self.port.read())
            
    def call(self):               
        return [self.R, self.X, self.F, self.Bias]
        
    def finish(self):
        pass
        
        
    #### here functions start that are not called by SweepMe! ####

    def find_nearest_frequency(self, val):
        index = (np.abs(self.allowed_frequencies - val)).argmin()
        return self.allowed_frequencies[index]
        
        
        