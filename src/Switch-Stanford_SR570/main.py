# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2019-2023 SweepMe! GmbH (sweep-me.net)
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

# We like to thank Jakob Wolansky/TU Dresden for contributing to the improvement
# of the driver.

# SweepMe! device class
# Type: Switch
# Device: Stanford SR570


from collections import OrderedDict

from ErrorMessage import error

from EmptyDeviceClass import EmptyDevice

import numpy as np

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "SR570"
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {"EOL" : "\r\n",
                                "timeout": 3,
                                "baudrate": 9600,
                                "stopbits": 2,
                                # "delay": 0.02,
                                }
        
        # Text from the manual about the RS-232 communication #
        """                  
        The SR570 is equipped with a standard DB-25 RS-232 connector on the rear panel for remote control of all 
        instrument functions. The interface is configured as 
            listen-only, 
            9600 baud DCE, 
            8 data bits, 
            no parity, 
            2 stop bits, 
            and is optically isolated to prevent any noise or grounding problems.
        The ERROR LED on the front panel will light if the SR570 receives an unknown or improperly worded command. 
        The LED will remain lit until a proper command is received.
        Data are sent to the instrument on pins 2 and 3, which are shorted together. 
        The data flow control pins (5,6,8,20) are shorted to each other.
        The ground pins (1 & 7) are connected to each other but optically isolated from the amplifier circuit ground 
        and the chassis ground.
        """

        self.variables = ["Sensitivity", "Bias"]
        self.units = ["A/V", "V"]
        self.plottype = [True, True]
        self.savetype = [True, True]
       
        self.sensitivities = {
                              "1 pA/V": 0,
                              "2 pA/V": 1,
                              "5 pA/V": 2,
                              
                              "10 pA/V": 3,
                              "20 pA/V": 4,
                              "50 pA/V": 5,
                              
                              "100 pA/V": 6,
                              "200 pA/V": 7,
                              "500 pA/V": 8,
                              
                              "1 nA/V": 9,
                              "2 nA/V": 10,
                              "5 nA/V": 11,
                              
                              "10 nA/V": 12,
                              "20 nA/V": 13,
                              "50 nA/V": 14,
                              
                              "100 nA/V": 15,
                              "200 nA/V": 16,
                              "500 nA/V": 17,

                              "1 µA/V": 18,
                              "2 µA/V": 19,
                              "5 µA/V": 20,   

                              "10 µA/V": 21,
                              "20 µA/V": 22,
                              "50 µA/V": 23,    

                              "100 µA/V": 24,
                              "200 µA/V": 25,
                              "500 µA/V": 26,                                                            

                              "1 mA/V": 27,
                            }
                            
        self.sentivities_value = {
                              "1 pA/V": 1e-12,
                              "2 pA/V": 2e-12,
                              "5 pA/V": 5e-12,
                              
                              "10 pA/V": 10e-12,
                              "20 pA/V": 20e-12,
                              "50 pA/V": 50e-12,
                              
                              "100 pA/V": 100e-12,
                              "200 pA/V": 200e-12,
                              "500 pA/V": 500e-12,
                              
                              "1 nA/V": 1e-9,
                              "2 nA/V": 2e-9,
                              "5 nA/V": 5e-9,
                              
                              "10 nA/V": 10e-9,
                              "20 nA/V": 20e-9,
                              "50 nA/V": 50e-9,
                              
                              "100 nA/V": 100e-9,
                              "200 nA/V": 200e-9,
                              "500 nA/V": 500e-9,

                              "1 µA/V": 1e-6,
                              "2 µA/V": 2e-6,
                              "5 µA/V": 5e-6,   

                              "10 µA/V": 10e-6,
                              "20 µA/V": 20e-6,
                              "50 µA/V": 50e-6,    

                              "100 µA/V": 100e-6,
                              "200 µA/V": 200e-6,
                              "500 µA/V": 500e-6,                                                            

                              "1 mA/V": 1e-3,
                            }
                            
        self.current_offset = {
                              "1 pA": 0,
                              "2 pA": 1,
                              "5 pA": 2,
                              
                              "10 pA": 3,
                              "20 pA": 4,
                              "50 pA": 5,
                              
                              "100 pA": 6,
                              "200 pA": 7,
                              "500 pA": 8,
                              
                              "1 nA": 9,
                              "2 nA": 10,
                              "5 nA": 11,
                              
                              "10 nA": 12,
                              "20 nA": 13,
                              "50 nA": 14,
                              
                              "100 nA": 15,
                              "200 nA": 16,
                              "500 nA": 17,

                              "1 µA": 18,
                              "2 µA": 19,
                              "5 µA": 20,   

                              "10 µA": 21,
                              "20 µA": 22,
                              "50 µA": 23,    

                              "100 µA": 24,
                              "200 µA": 25,
                              "500 µA": 26,                                                            

                              "1 mA": 27,
                              "1 mA": 28,  # TODO: Is this correct?
                              "1 mA": 29,  # TODO: Is this correct?
                            }
                            
        self.frequencies = {
                           "0.03 Hz": 0,
        
                           "0.1 Hz": 1,
                           "0.3 Hz": 2,
                           
                           "1 Hz": 3,
                           "3 Hz": 4,
                           
                           "10 Hz": 5,
                           "30 Hz": 6,
                           
                           "100 Hz": 7,
                           "300 Hz": 8,
                           
                           "1 kHz": 9,
                           "3 kHz": 10,
                           
                           "10 kHz": 11,
                           "30 kHz": 12,
                           
                           "100 kHz": 13,
                           "300 kHz": 14,
                           
                           "1 MHz": 15,
                           }
                           
        self.gain_modes = {        
                            "Low noise": 0,
                            "High bandwidth": 1,
                            "Low drift": 2,
                            }
                            
        self.filters = {
                        "6 db highpass": 0,
                        "12 db highpass": 1,
                        "6 db bandpass": 2,
                        "6 db lowpass": 3,
                        "12 db lowpass": 4,
                        "None" : 5,
                        }        
                            
        # defined but not used at the moment
        unit_conversion = { 
                            " pA/V": "1e-12",
                            " nA/V": "1e-9",
                            " µA/V": "1e-6",
                            " mA/V": "1e-3",
                           }
                           
        self.commands = {
                        "Negative": 0,
                        "Positive": 1, 
                        }

    def set_GUIparameter(self):
        
        gui_parameter =  {
                        "SweepMode" : ["None", "Sensitivity in A/V", "Voltage in V"],
                        
                        "Bias voltage:" : None,
                        "Use bias voltage": False,
                        "Bias voltage -5..+5 [V]": "0.0",
                        
                        "Input offset current:" : None,
                        "Use input offset current" :  False,
                        "Input offset current sign": ["Negative", "Positive"],
                        "Input offset current" : list(self.current_offset.keys()),
                        "Input offset uncalibrated": False,
                        "Uncalibrated input offset vernier -100..+100 [%]": 0.0,
                        
                        "Filter:" : None,
                        "Filter": list(self.filters.keys()),
                        "High pass filter": list(self.frequencies.keys())[0:-4], # only from 0.03 Hz to 10 kHz supported
                        "Low pass filter": list(self.frequencies.keys())[::-1],
                        
                        "Sensitivity:" : None,
                        "Sensitivity" : list(self.sensitivities.keys())[::-1], 
                        "Sensitivity uncalibrated": False,
                        "Uncalibrated sensitivity vernier 0..100 [%]": 0,
                        
                        "Other:" : None,
                        "Gain mode": list(self.gain_modes.keys()),
                        "Invert signal": False,
                        "Blank front-end output": False,
                        }
        
        return gui_parameter
        
    def get_GUIparameter(self, parameter = {}):
        
        self.sensitivity = parameter["Sensitivity"]
        
        self.sensitivity_uncalibration = parameter["Sensitivity uncalibrated"]
        self.uncalibrated_sensitivity_vernier = int(parameter["Uncalibrated sensitivity vernier 0..100 [%]"])
        if self.uncalibrated_sensitivity_vernier > 100:
            self.uncalibrated_sensitivity_vernier = 100
        elif self.uncalibrated_sensitivity_vernier < 0:
            self.uncalibrated_sensitivity_vernier = 0
         
        self.use_input_offset_current = parameter["Use input offset current"]
        self.input_offset_current = parameter["Input offset current"]
        self.input_offset_current_sign = parameter["Input offset current sign"]
        self.input_offset_uncalibration = parameter["Input offset uncalibrated"]
        self.uncalibrated_input_offset = float(parameter["Uncalibrated input offset vernier -100..+100 [%]"])
        if self.uncalibrated_input_offset > 100:
            self.uncalibrated_input_offset = 100
        elif self.uncalibrated_input_offset < -100:
            self.uncalibrated_input_offset = -100

        self.ground_mode = parameter["Gain mode"]
        
        self.signal_inverted = parameter["Invert signal"]

        self.use_bias_voltage = parameter["Use bias voltage"]

        if (parameter["Bias voltage -5..+5 [V]"]) == "":
            self.bias_voltage = 0
        else:
            self.bias_voltage = float(parameter["Bias voltage -5..+5 [V]"])
            
        if self.bias_voltage > 5.0:
            self.bias_voltage = 5.0
        elif self.bias_voltage < -5.0:
            self.bias_voltage = -5.0
        
        self.filter = parameter["Filter"]
        
        self.lowpass = parameter["Low pass filter"]
        self.highpass = parameter["High pass filter"]
        
        self.blank_frontend = parameter["Blank front-end output"]

        self.sweepmode = parameter["SweepMode"]
        # self.sweepvalue = parameter["SweepValue"]

    def initialize(self):
        self.port.write("*RST") # reset to default settings
        answer = self.port.read()
       
    def connect(self):
    
        if self.filter == "6 db bandpass":
            if self.frequencies[self.lowpass] <= self.frequencies[self.highpass]:
                self.stop_Measurement("Measurement stopped: Please make sure that your low pass frequency is below your "
                                      "high pass frequency")

    def configure(self):
    
        self.port.write("ROLD") # Resets the filter capacitors to clear an overload condition.
        answer = self.port.read()
        
        # Sensitivity
        self.port.write("SENS %i" % self.sensitivities[self.sensitivity])
        answer = self.port.read()
        
        # Sensitivity calibration mode
        self.port.write("SUCM %i" % self.sensitivity_uncalibration) # The manual says: 0 = cal, 1 = uncal. but in reality it switches off with 0 ???? 
        answer = self.port.read()
        
        # Uncalibrated sensitivity vernier
        self.port.write("SUCV %i" % self.uncalibrated_sensitivity_vernier) #[0 ≤ n ≤ 100] (percent of full scale).
        answer = self.port.read()
        
        # Input offset current
        self.port.write("IOON %i" % self.use_input_offset_current) # IOON n Turn the input offset current on (n=1) or off (n=0).
        answer = self.port.read()
        
        # Input offset current
        self.port.write("IOLV %i" % self.current_offset[self.input_offset_current]) # IOLV n Sets the calibrated input offset current level
        answer = self.port.read()
        
        # Uncalibrated input offset vernier
        self.port.write("IOUV %i" % int(round(self.uncalibrated_input_offset*10))) # IOUV n Sets the uncalibrated input offset vernier
        answer = self.port.read()
        
        # Input offset current sign
        self.port.write("IOSN %i" % self.commands[self.input_offset_current_sign]) # IOSN n Sets the input offset current sign
        answer = self.port.read()
        
        # Input offset calibration mode
        self.port.write("IOUC %i" % self.input_offset_uncalibration) # IOUC n Sets the input offset cal mode. 0 = cal, 1 = uncal.
        answer = self.port.read()
        
        # Gain mode
        self.port.write("GNMD %i" % self.gain_modes[self.ground_mode]) # Sets the gain mode of the amplifier.
        answer = self.port.read()
        
        # Signal inverted
        self.port.write("INVT %i" % self.signal_inverted) # Sets the signal invert sense. 0=noninverted, 1=inverted.
        answer = self.port.read()
        
        # Use bias voltage
        self.port.write("BSON %i" % self.use_bias_voltage) # Turn the bias voltage on (n=1) or off (n=0).
        answer = self.port.read()
        
        # Bias voltage
        self.port.write("BSLV %i" % int(round(self.bias_voltage * 1000))) # Sets the bias voltage level in the range. [-5000 ≤ n ≤ +5000] (-5.000 V to +5.000 V).
        answer = self.port.read()
        
        # Filter type
        self.port.write("FLTT %i" % self.filters[self.filter]) # FLTT n Sets the filter type
        answer = self.port.read()
        
        # Low pass
        self.port.write("LFRQ %i" % self.frequencies[self.lowpass]) # Sets the value of the lowpass filter     
        answer = self.port.read()
        
        # High pass
        self.port.write("HFRQ %i" % self.frequencies[self.highpass]) # Sets the value of the lowpass filter
        answer = self.port.read()
        
        # Blank front-end output
        self.port.write("BLNK %i" % self.blank_frontend) # Blanks the front-end output of the amplifier.
        answer = self.port.read()

    def apply(self):
        
        if self.sweepmode.startswith("Sensitivity"):
        
            conversion = {
                            1e-3: "mA/V",
                            1e-6: "µA/V",
                            1e-9: "nA/V",
                            1e-12: "pA/V",
                            }
        
            # print(self.value)
            self.value = float(self.value)
            
            for exp_step in list(conversion.keys()):
                
                if self.value > 0.75*exp_step:
            
                    number = round(self.value/exp_step,0)
                    # print(number)
                    
                    for multiplicator in [1, 10, 100]:
                    
                        if number <= 1.5 * multiplicator:
                            number = 1 * multiplicator
                            break
                               
                        elif number <= 3.5 * multiplicator:
                            number = 2 * multiplicator
                            break
                        
                        elif number <= 7.5 * multiplicator:
                            number = 5 * multiplicator
                            break
                           
                    break
                
            self.sensitivity = str(number) + " " + conversion[exp_step]
            # print(sensitivity)
            self.port.write("SENS %i" % self.sensitivities[self.sensitivity])
            answer = self.port.read()

        if self.sweepmode == "Voltage in V":
            # Use bias voltage
            self.port.write("BSON 1")  # Turn the bias voltage on (n=1) or off (n=0).
            answer = self.port.read()
            
            # Bias voltage
            # Sets the bias voltage level in the range. [-5000 ≤ n ≤ +5000] (-5.000 V to +5.000 V).
            self.port.write("BSLV %i" % int(round(self.value * 1000)))
            answer = self.port.read()
            
            self.bias_voltage = self.value

    def unconfigure(self):
        self.port.write("ROLD") # Resets the filter capacitors to clear an overload condition.
        answer = self.port.read()
        # Turn bias voltage off
        self.port.write("BSON 0") # Turn the bias voltage on (n=1) or off (n=0).
        
    def call(self):
        if not self.use_bias_voltage:
            self.bias_voltage = 0.0
        return self.sentivities_value[self.sensitivity], self.bias_voltage
