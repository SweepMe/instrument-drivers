# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 SweepMe! GmbH
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
# Type: Logger
# Device: Advantest R6552


from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!
# If you like to see the source code of EmptyDevice, take a look at the pysweepme package that contains this file

class Device(EmptyDevice):

    ## here you can add html formatted description to your device class that is shown by modules like 'Logger' or 'Switch' that have a description field.
    description =   """
                    Advantest R6552
                    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        
        self.measurement_modes =    {
                                    "DC voltage":  {
                                                    "command": "F1",
                                                    "variable": "DC voltage",
                                                    "unit": "V",
                                                    "token": "DV",
                                                    },
                                                    
                                    "AC voltage":  {
                                                    "command": "F2",
                                                    "variable": "AC voltage",
                                                    "unit": "V",
                                                    "token": "AV",
                                                    },
                                    # "ACV(AC+DC)": {
                                                    # "command": "F7",
                                                    # "variable": "?",
                                                    # "unit": "V",
                                                    # "token": "?",
                                                    # },             
                                    "DC current":   {
                                                    "command": "F5",
                                                    "variable": "DC current",
                                                    "unit": "A",
                                                    "token": "DI",
                                                    },
                                    "AC current":   {
                                                    "command": "F6",
                                                    "variable": "AC current",
                                                    "unit": "A",
                                                    "token": "AI",
                                                    },
                                    # "ACI(AC+DC)": {
                                                    # "command": "F8",
                                                    # "variable": "?",
                                                    # "unit": "A",
                                                    # "token": "?",
                                                    # },
                                    "2-wire resistance":    {
                                                            "command": "F3",
                                                            "variable": "Resistance",
                                                            "unit": "Ohm",
                                                            "token": "R",
                                                            },
                                    "Low power 2-wire resistance":   {
                                                                    "command": "F20",
                                                                    "variable": "Resistance",
                                                                    "unit": "Ohm",
                                                                    "token": "RL",
                                                                    },
                                                                    
                                    "4-wire resistance":     {
                                                             "command": "F4",
                                                             "variable": "Resistance",
                                                             "unit": "Ohm",
                                                             "token": "R",
                                                             },
                                    "Low power 4-wire resistance":  {
                                                                    "command": "F21",
                                                                    "variable": "Resistance",
                                                                    "unit": "Ohm",
                                                                    "token": "RL",
                                                                    },
                                    "Frequency":    {
                                                    "command": "F50",
                                                    "variable": "Frequency",
                                                    "unit": "Hz",
                                                    "token": "FQ",
                                                    },
                                    "Diode":    {
                                                "command": "F13",
                                                "variable" : "Diode voltage",
                                                "unit": "V",
                                                "token:": "D",
                                                },    
                                    "Ripple V":     {
                                                    "command": "F15",
                                                    "variable": "Ripple",
                                                    "unit": "V",
                                                    "token": "RV",
                                                },
                                    }
                                 
        self.sampling_modes =   {
                                "Freerun": "M0",
                                "Hold": "M1",
                                # "Burst": "M2",
                                }
                                 
        self.sampling_rates = {
                                "Fast": "PR1",
                                "Medium": "PR2",
                                "Slow": "PR3",
                                # "Long integral time": "PR4",
                                }
                                
        self.auto_zero_modes = {
                                "Off":  "AZ0",
                                "On":   "AZ1",
                                "Once": "AZ2",
                                }
                                
        self.input_terminals = {
                                "Front": "IN0",
                                "Rear": "IN1",
                                }
        
        ### use/uncomment the next line to use the port manager
        self.port_manager = True 
           
        ### use/uncomment the next line to let SweepMe! search for ports of these types. Also works if self.port_manager is False or commented.
        self.port_types = ["GPIB", "COM"]
        self.port_properties = {
                                "timeout": 5,
                                # "EOL": "\r\n",
                                }
            
            
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Mode": list(self.measurement_modes.keys()),
                        "Range": ["Auto"],
                        "Sampling": list(self.sampling_modes.keys()),
                        "Rate": list(self.sampling_rates.keys()),
                        "Auto zero": list(self.auto_zero_modes.keys()),
                        "Input terminal": ["Front", "Rear"],
                        }


        return GUIparameter

    def get_GUIparameter(self, parameter):

        self.mode = parameter["Mode"]
        self.rate = parameter["Rate"]
        self.sampling = parameter["Sampling"]
        self.auto_zero = parameter["Auto zero"]
        self.port_str = parameter["Port"]
        self.input_terminal = parameter["Input terminal"]
        
        self.shortname = "R6552" # short name will be shown in the sequencer
        self.variables = [self.measurement_modes[self.mode]["variable"]] # define as many variables you need
        self.units = [self.measurement_modes[self.mode]["unit"]] # make sure that you have as many units as you have variables
        self.plottype = [True]   # True to plot data, corresponding to self.variables
        self.savetype = [True]   # True to save data, corresponding to self.variables
        
           

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def initialize(self):
        self.port.write("Z") # reset all parameters
        # self.port.write("DL0") # Block delimiters, EOL, DL0 = CR/LF+EOI (GPIB only)
        self.port.write("H1") # header data format to get addtional error code, other options H0 (no header), H2 (binary data)
        
        
    def configure(self):
       
        # Measurement mode
        self.port.write(self.measurement_modes[self.mode]["command"])
        
        # Auto range
        self.port.write("R0") # Auto range
        
        # Sampling rate
        self.port.write(self.sampling_rates[self.rate])
        
        # Sampling mode
        self.port.write(self.sampling_modes[self.sampling])
        
        # Auto zero
        self.port.write(self.auto_zero_modes[self.auto_zero])
        
        # Input terminal
        self.port.write(self.input_terminals[self.input_terminal])

  
    """ the following functions are called for each measurement point """
       
    def measure(self):
    
        if self.port_str.startswith("COM"):
            self.port.write("MD?")   # triggers the measurement, same as "*TRG" in case of COM
        else:
            self.port.write("E")    # triggers the measurement, same as "*TRG" in case of GPIB
                       
    def read_result(self):
        
        answer = self.port.read()
        # print("Reading R6552 multimeter:", answer)
        self.val = float(answer[3:]) # we remove the three header letters and covert to float

    def call(self):
        return self.val
        
