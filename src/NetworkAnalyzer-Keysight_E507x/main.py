# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 - 2022 SweepMe! GmbH
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

# We like to thank Dr. Thomas Windisch (IFW Dresden) for the major contribution to 
# the development of this driver.

# SweepMe! device class
# Type: NetworkAnalyzer
# Device: Keysight ENA E507x


from ErrorMessage import error, debug

import time,datetime
import numpy as np
import os
import FolderManager
FoMa = FolderManager.FolderManager()

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):
    
    def __init__(self):        
        EmptyDevice.__init__(self)
        
        self.shortname = "ENA507x"       # short name will be shown in the sequencer
        self.port_manager = True

        self.port_types = ["GPIB", "TCPIP", "USB"]                           
        self.port_properties = {
                                "timeout": 10.0,
                                }                             
        #self.port_identication = ["Agilent Technologies"] # temporarily not used by SweepMe!  		
        self.data_format_type = "ASC" # ASC or REAL  -> REAL is currently not supported by this driver     
        self.if_bandwidth_values = [10 , 15 , 20 , 30 , 50 , 70 , 100 , 150 , 200 , 300 , 500 , 700 , 1e3 , 1.5e3 , 2e3 , 3e3 , 5e3 , 7e3 , 10e3, 15e3 , 20e3 , 30e3 , 50e3 , 70e3 , 100e3][::-1]
        self.calibration_file_extensions = [".csa", ".cst", ".sta", ".cal"]
                
             
    def find_calibrations(self):                                             
    
        calibration_files = []
        calibration_files += ["None"] # can be used to deselect a calibration
        
        ## return a list of strings that can be selected by the user
        return calibration_files

    def get_calibrationfile_properties(self, port):                                 

        calibration_file_extensions = self.calibration_file_extensions           
        calibration_file_names = [""] # this means any name is accepted
        
        return calibration_file_extensions, calibration_file_names

    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Terminals": "1,2",
                        "Sparameters": "",
                        
                        #"Calibration": self.get_Calibrations(),  
                        
                        "Average": 1,
                        "SourcePower": ["%i" % i for i in range(-55,15,5)],
                        "SourceAttenuation": ["%i" % i for i in range(0,40,5)], # 0 to 35
                        "IFBandwidth": ["%s" % str(int(x)) for x in self.if_bandwidth_values],
                        "Correction": ["On", "Off"],                                            # TD: wird wo verwendet?
                        "Trigger": ["Software", "Internal", "External", "ManualSingle"],
                        "TriggerDelay": 0.0,
                        # All frequencies in Hz
                        "FrequencyStart": 30e6,
                        "FrequencyEnd": 3000e6,
                        #"FrequencyStepPointsType": ["Linear (points)", "Linear (steps in Hz)", "Logarithmic (points)"],
                        "FrequencyStepPointsType": ["Linear (points)", "Logarithmic (points)"],
                        "FrequencyStepPoints": 1e3,                        
                        "Display": True,
                        }
        return GUIparameter
        
    def get_GUIparameter(self, parameter):
        
        self.f_start = float(parameter["FrequencyStart"])
        self.f_end = float(parameter["FrequencyEnd"])
        self.f_type = parameter["FrequencyStepPointsType"]
        self.f_steppoints = float(parameter["FrequencyStepPoints"])
        
       
        self.source_power = parameter["SourcePower"]
        self.source_attenuation = parameter["SourceAttenuation"]
        self.if_bandwidth = parameter["IFBandwidth"]
        self.calibration_file_name = parameter["Calibration"]
        self.number_averages = int(parameter["Average"])
        self.correction = parameter["Correction"]
        self.trigger_state = parameter["Trigger"]
        self.trigger_delay = parameter["TriggerDelay"]
        self.update_display = parameter["Display"]
        
        self.variables = ["Frequency"]
        self.units = ["Hz"]
        self.plottype = [True]
        self.savetype = [True]
        
        self.Sparameters = []
        self.terminals = []
        
        try:
            self.terminals = list(map(int, parameter["Terminals"].replace(" ", "").replace(';', ',').replace(",,", ",").split(',')))
        except:
            self.terminals = []

        try: 
            sparameters = parameter["Sparameters"].replace(" ", "").replace(';', ',').replace(",,", ",").split(",")
        except:
            sparameters = []
        
        is_Spar_correct = [x.startswith("S") and len(x)==3 and x[1:].isdigit() for x in sparameters]
                
        if len(is_Spar_correct) > 0 and all(is_Spar_correct):  # this is the case if the user defines the S-parameter directly, e.g. "S11, S31"        
            self.Sparameters = sparameters
            
        elif not any(is_Spar_correct):  # this is the case if te user defines just the terminal port numbers and we have to construct all possible S-parameters

            # create variable and units depending on the number of terminals
            for i in self.terminals:
                for j in self.terminals:
                    self.Sparameters.append("S%i%i" % (j,i))
        else:
            pass  # this is the case if none above the options is used and self.Sparameters will remain empty so that we can throw an error message
            
        self.variables += self.Sparameters
        self.units += [""] * len(self.Sparameters)
        self.plottype += [False] * len(self.Sparameters)
        self.savetype += [True] * len(self.Sparameters)
        
        # print(self.terminals)
        # print(self.Sparameters)

        number_pars_per_channel = 16
        self.Spar_lists = [[]]
        for Spar in self.Sparameters:
            if len(self.Spar_lists[-1]) == number_pars_per_channel:
                self.Spar_lists.append([])
             
            self.Spar_lists[-1].append(Spar)
            
        # print(self.Spar_lists)
            
            
    def initialize(self):
    
        # check whether S-parameters are correctly defined
        if len(self.Sparameters) == 0:
            raise Exception("Unable to parse S-parameters. Please define S-parameters in the field 'S-parameters' e.g. 'S11, S21'.")
            
        # check whether terminals are defined
        if len(self.terminals) == 0:
            raise Exception("Unable to parse terminal numbers. Please define the terminals to be used in the field 'Terminals' e.g. '1, 2'.")
    
        self.port.write("*CLS") # Clear the event status registers and empty the error queue
        
        self.port.write(":FORM:DATA %s" % self.data_format_type) # as defined in __init__
        
        if self.data_format_type == "ASC":
            self.port.write(":FORM:BORD NORM") # options: NORM or SWAP, SWAP seems not to work with ASC data format
        # else:
            # self.port.write(":FORM:BORD SWAP") #SWAP is needed for data format REAL  
            
        #self.port.write(":FORM:DATA?")
        #answer = self.port.read()
        #print("  Data format:", answer)
         
        
    def deinitialize(self):
        
        #print("  Errors after deinitialize:")
        self.read_errors()

    def configure(self):

        self.port.write(":SYST:PRES")
        # self.port.write("*RST")
       
        self.window_number = 1
        
        for i, Spar_list in enumerate(self.Spar_lists):
        
            channel_number = i+1
            
            self.port.write(":CALC%i:PAR:COUN %i" % (channel_number, len(Spar_list))) # sets traces/parameters for each channel
            # self.port.write(":CALC%i:PAR:COUN?" % (channel_number))
            # print(self.port.read())
            

        ### Measurements ###
        for i, Spar_list in enumerate(self.Spar_lists):
            channel_number = i+1
            for j, spar in enumerate(Spar_list):
                self.port.write(":CALC%i:PAR%i:DEF %s" % (channel_number, j+1, spar)) # sets Tr1 of Ch1 to S11
                # must be placed before the creation of the sweep
                
       
        ### Power levels ###
        # for term in self.terminals:
        self.port.write(":SOUR%i:POW %s"  % (channel_number, self.source_power))
        self.port.write(":SOUR%i:POW:ATT %s" % (channel_number, self.source_attenuation))
                    
        channel_number = 1 # only one channel is needed, each channel represents a measurement that can be configured.
               
        ### IF bandwidth ###       
        self.port.write(":SENS%i:BAND %s" % (channel_number, self.if_bandwidth)) # sets if_bandwidth 
        
        ### Frequency sweep ###
        if self.f_type.startswith("Linear"):
            self.port.write(":SENS%i:SWE:TYPE LIN" % (channel_number)) # Linear frequency sweep
        else:
            self.port.write(":SENS%i:SWE:TYPE LOG" % (channel_number)) # Logarithmic frequency sweep
    
        if "points" in self.f_type:           
            self.number_points = int(self.f_steppoints)
            
            if self.f_type.startswith("Linear"):
                self.frequency_values = np.linspace(float(self.f_start), float(self.f_end), self.number_points)
            elif self.f_type.startswith("Logarithmic"):
                self.frequency_values = np.logspace(np.log10(float(self.f_start)), np.log10(float(self.f_end)), self.number_points)

            self.f_start = float(self.f_start) # Start
            self.f_end = float(self.f_end)     # End
            
        
        self.port.write(":SENS%i:FREQ:STAR %s" % (channel_number, str(self.f_start)))  # Start
        self.port.write(":SENS%i:FREQ:STOP %s" % (channel_number, str(self.f_end)))    # End
        self.port.write(":SENS%i:SWE:POIN %i" % (channel_number, self.number_points))  # Points
        
        ### Sweep time ###    
        self.port.write("SENS%i:SWE:TIME:AUTO ON" % (channel_number)) #  automatic sweep time
        
        self.average_timeout = self.number_points * ( 0.01 + 1.5 / float(self.if_bandwidth))
        #print("Average timeout:", self.average_timeout)
        
    
        ### Display, Windows, and Traces ###
        if not self.update_display:
            self.port.write(":DISP:ENAB OFF")
        else: 
            self.port.write(":DISP:ENAB ON") # Display on
            
            self.port.write(":DISP:WIND%i:ACT" % channel_number)
            
            for i, spar in enumerate(self.Sparameters):
                trace_number = i+1
                self.port.write(":DISP:WIND%i:TRAC%i:STAT ON" % (self.window_number, trace_number))

        ### Average ###
        if self.number_averages > 1:
            self.port.write(":SENS%i:AVER:STAT ON" % (channel_number))
            self.port.write(":SENS%i:AVER:COUN %i" % (channel_number, self.number_averages))  # count 
            self.port.write(":SENS%i:AVER:CLE" % (channel_number))   # starts new averaging cycle
        else:
            self.port.write(":SENS%i:AVER:COUN 1" % (channel_number))  # counts
            self.port.write(":SENS%i:AVER:STAT OFF" % (channel_number))      # state
  
             
        ### Trigger ###         ["Internal", "External", "Software", "ManualPress"]
        if self.trigger_state == "Internal":
            self.port.write(":TRIG:SOUR INT")   # Internal trigger
            self.port.write(":INIT:CONT ON") # switch on continous measurement           
        elif self.trigger_state == "External":
            self.port.write(":TRIG:SOUR EXT")   # External trigger
            self.port.write(":TRIG:DEL %s" % self.trigger_delay) # trigger delay
            self.port.write(":INIT:CONT OFF") # switch off continous measurement  
        elif self.trigger_state == "Software":
            self.port.write(":TRIG:SOUR BUS")   # Bus (software) trigger
            self.port.write(":INIT:CONT OFF") # switch off continous measurement  
        elif self.trigger_state == "ManualSingle":
            self.port.write(":TRIG:SOUR MAN")   # Manual trigger by button press 
            self.port.write(":INIT:CONT OFF") # switch off continous measurement  
        
        # We wait for all commands to be set
        self.port.write("*OPC?")
        answer=self.port.read()

        # print("\nErrors after configure:")
        self.read_errors()
    
        # print("Errors end")

    def unconfigure(self):
        # print("\n")
        # print(time.strftime("%d.%m.%Y %H:%M:%S"))
        
        # abort all ongoing sweeps
        self.port.write(":ABOR")         # Abort ongoing measurements 
        self.port.write(":TRIG:SOUR INT")   # Internal trigger
        self.port.write(":INIT:CONT ON")   # switch on continous measurement      
        self.port.write(":DISP:ENAB ON")   # Display on
        
    def measure(self):
        channel_number = 1    
    
        if self.trigger_state != "Internal":
            self.port.write(":SENS%i:AVER:CLE" % (channel_number))   # starts new averaging cycle       
       
            ## Averages
            for j in range(self.number_averages):

                self.port.write(":INIT%i:IMM" % channel_number)
                
                if self.trigger_state == "Software":
                    self.port.write("TRIG")
                
                self.port.write("*WAI")
                
                # Waiting for trigger completed
                self.port.write("*OPC?")
                answer = self.port.read()
                
                # we have to wait until all averages are finished and we have to trigger each average cycle
                starttime = time.perf_counter()

                while True:
                    self.port.write("STAT:OPER:COND?")
                    answer=self.port.read()
                    #print("  Status operation condition:", answer) 
                    
                    byte_number = int(answer) 
                    bit_string = "{:016b}".format(byte_number)[::-1]
                    if bit_string[4] != "1": # 5th bit (index 4) is measurement is running if equals 1
                        break # breaks the next higher for-loop or while-loop
                        
                    if time.perf_counter() - starttime > self.average_timeout:
                        self.stop_measurement("Timeout to acquire curve is reached.")
                        return False
                    time.sleep(0.2)

    def request_result(self):
        
        """
        self.port.write("*OPC?") # indicates whether all commands are completed, i.e. the measurement has finished
        #self.port.read()
        answer=self.port.read()
        print("  OPC?:", answer)
        """

    def read_result(self):
        
        self.results = []

        ### Frequencies ###
        channel_number = 1
        
        self.port.write(":SENS%i:FREQ:DATA?" % channel_number)
        success, answer = self.read_and_parse_data() # special function to distinguish between different data formats
        if not success:
            return False
             
        self.results.append(answer)

        self.port.write("*WAI") # indicates whether all commands are completed, i.e. the measurement has finished


        for i, Spar_list in enumerate(self.Spar_lists):
            for j, spar in enumerate(Spar_list):

                # for i, spar in enumerate(self.Sparameters):
                
                self.port.write("CALC%i:PAR%i:SEL" %(i+1, j+1))

                self.port.write("CALC%i:DATA:SDAT?" % (i+1))
                success, answer = self.read_and_parse_data() # special function to distinguish between different data formats
                if not success:
                    return False
                
                try:
                    data = answer[::2] + 1j * answer[1::2]
                    self.results.append(data)

                except:
                    error()
                    print(answer)

        #print("\nErrors after reading data:")
        #self.read_errors()
   
    def call(self):
        
        return self.results
        
    def finish(self):
    
        if self.update_display:
            for i, spar in enumerate(self.Sparameters):
                trace_number = i+1
                # self.port.write("DISP:WIND%i:TRAC%i:SEL" % (self.window_number, trace_number))
                self.port.write("DISP:WIND%i:TRAC%i:Y:AUTO" % (self.window_number, trace_number))

    """ further function as needed by this device class are defined here """
    
        
    # used during read_result to read and interpret the returned results
    def read_and_parse_data(self):
        
        if self.data_format_type == "ASC":
            data_in = self.port.read()
            return True, np.array(list(map(float, data_in.split(","))))
           
        elif self.data_format_type == "REAL":
            try:
                data_in = self.port.port.read_raw()
            except:
                data_in = self.port.read_raw() # fallback if device class is used by external scripts
                
            return True, self.binblock_raw(data_in, 'f4')

        else:
            debug("The data format %s is unknown: Use 'ASC', 'REAL'" % self.data_format_type)
            return False, []
        
    def binblock_raw(self, data_in, dtype_in):

        #Grab the beginning section of the data file, which will contain the header.
        Header = str(data_in[0:12])
        # ("Header is " + str(Header))
        
        #Find the start position of the IEEE header, which starts with a '#'.
        startpos = Header.find("#")
        # print("Start Position reported as " + str(startpos))
        
        #Check for problem with start position.
        if startpos < 0:
            raise IOError("No start of block found")
            
        #Find the number that follows '#' symbol.  This is the number of digits in the block length.
        Size_of_Length = int(Header[startpos+1])
        # print("Size of Length reported as " + str(Size_of_Length))
        
        ##Now that we know how many digits are in the size value, get the size of the data file.
        Image_Size = int(Header[startpos+2:startpos+2+Size_of_Length])
        # print("Number of bytes in file are: " + str(Image_Size))
        
        # Get the length from the header
        offset = startpos+Size_of_Length
        
        # Extract the data out into a list.
        return np.frombuffer(data_in[offset:offset+Image_Size],dtype=np.dtype(dtype_in))
    
    def read_errors(self):
        
        # here we read up to 100 possible error messages until no error is returned
        for i in range(100):
            self.port.write("SYST:ERR?")
            answer = self.port.read()
            
            if "No error" in answer:
                break
                
            print("Error %i reported:" % i, answer)
