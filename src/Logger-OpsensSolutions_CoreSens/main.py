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
# Device: Opsens solutions CoreSens


import time
import numpy as np
from scipy.stats import linregress

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!

# needed to import CoreSensComm
import FolderManager
FolderManager.addFolderToPATH()

import CoreSensComm

# only needed for debuggging so that changes in CoreSensComm take action immediately
import importlib 
importlib.reload(CoreSensComm)


class Device(EmptyDevice):

    description =   """
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Besides the IP address of the CoreSens instrument that must be selected in the field 'Port', one needs to provide the local IP of the computer that is running SweepMe!.</li>
                    <li>The driver support two acquisition modes: Infinite acquisition and finite acquisition. To measure infinite time, please enter a zero acqusition time. Then, the system will continuosly send data at the given rate as long as the Logger module is in an active branch of the sequencer. In a finite measurement, the measurement will be started and waited until the acquisition time has passed to query and return the entire data.</li>
                    <li>System Slot #Channel: Insert all channels of the system that have to be readout. Use the following syntax "0103#2" (system 1 slot 3 channel 2). You can add multiple slots/channels by comma-separation. The system is the number of the chassis which ranges from 01 to 50. The Slot is the measurement card in one system which can range from 01 to 13. The channel is either #1 or #2 as each slot has two channels.</li>
                    <li>Rate in Hz: Enter an integer number to define the measurement rate for all given slot and channels.&nbsp;</li>
                    <li>Variable names: Enter a comma-separated list of names with one name per channel that is used to create the variable names.</li>
                    <li>Save time series: This option allows to choose whether the time series data is saved or not. If you are only interested in post-processed values like Min, Max, etc. you can avoid the creation of a 1D data file that contains the full time series. Data can still be post-processed by other modules like Calc or CustomFunction.&nbsp;</li>
                    <li>Post processing: Min, Max, Mean or Slope can be automatically calculated for the last calles time series.</li>
                    <li>Configuring the sensors is not supported by this driver. Please use the Web application to create and setup sensors. This driver just calls the data for already configured channels.</li>
                    <li>Time is given in seconds since 01.01.1970</li>
                    <li>The filter is applied to all channels. "None" switches the filter off. "As is" does not change anything. "Moving average" uses an integer between 2 and 2000 from the field "Moving average". "Adaptive filter" only works for GSX temperature modules and parameters from the field "Adaptive filter" are used which must be 4 comma-separated numbers being&nbsp;TcLow, TcHigh, Threshold, and Proportional Bandwidth.</li>
                    </ul>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "CoreSens" # short name will be shown in the sequencer
      
            
    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        # If you use this template to create a driver for modules other than Logger or Switch, you need to use fixed keys that are defined for each module.
        
        GUIparameter = {
                        "Port": "10.0.10.2",  # this is the address that is assigned if the CoreSens starts in DHCP server mode
                        
                        "IP local": [CoreSensComm.UDPconnection.getIPSuggestions()[0]] + CoreSensComm.UDPconnection.getIPSuggestions()[1],  # this is the IP of the computer where SweepMe! and this driver is running
                        # "Acquisition": ["Finite", "Infinite"],
                        "Acquisition time in s": "0.0 (infinite)",  # 0.0 or inf means infinite mode, any number is the acquisition time
                        "System Slot #Channel": "0101#1, 0101#2",
                        "Variable names": "",
                        "Unit": ["°C"],
                        "Rate in Hz": "10.0",
                        "Save time series": True,
                        
                        "": None,
                        "Filter": ["None", "As is", "Moving average", "Adaptive filter (GSX modules only)"],
                        "Moving average": "2",
                        "Adaptive filter": "1, 430, 0.15, 3",
                         
                        " ": None,
                        "Postprocessing": None,
                        "Min": False,
                        "Max": False,
                        "Mean": False,
                        "Slope": False,
                        }

        
        return GUIparameter

    def get_GUIparameter(self, parameter):

        # self.acquisition_mode = parameter["Acquisition"]
        
        self.port_string = parameter["Port"]
        self.ip_local = parameter["IP local"]
        
        
        # Acquisition time and mode
        if "inf" in parameter["Acquisition time in s"]:
            self.acquisition_time = 0.0
            self.acquisition_mode = "infinite"
        else:
            acquisition_time_str = parameter["Acquisition time in s"].strip().split()[0]
            
            try:
                self.acquisition_time = float(acquisition_time_str)
                if self.acquisition_time == 0.0:
                    self.acquisition_mode = "infinite"
                else:
                    self.acquisition_mode = "finite"
            except:
                self.acquisition_time = None
                self.acquisition_mode = None

        variable_names = [x.strip() for x in parameter["Variable names"].split(",") if x != ""]
        system_slot_channel_names = [x.strip() for x in parameter["System Slot #Channel"].split(",")]

        # System - Slot - Channel
        self.system_slot_channel_list = []
        
        for i, item in enumerate(system_slot_channel_names):
            
            item_dict = {}
            item = item.strip()
           
            item_dict["System"] = item[:2]
            item_dict["Slot"]   = item[2:4]
            item_dict["Channel"]= item[5]
            item_dict["String"] = item
            
            if i < len(variable_names):
                item_dict["Name"] = variable_names[i]  # we replace the String with the name 
            else:
                item_dict["Name"] = item
        
            self.system_slot_channel_list.append(item_dict)
        
        self.rate = int(float(parameter["Rate in Hz"]))
        
        self.filter = parameter["Filter"]
        if self.filter.startswith("Adaptive filter"):
            self.filter = "Adaptive filter"
        self.filter_average = parameter["Moving average"]
        self.filter_adaptive = parameter["Adaptive filter"]
        
        
        # Variables and units       
        self.variables = []
        self.units = []
        self.plottype = [] 
        self.savetype = []
        
        unit = parameter["Unit"]
        
        for item in self.system_slot_channel_list:
        
            self.variables += ["Time " + item["Name"], "Values " + item["Name"]]
            self.units += ["s", unit] 
            self.plottype += [True, True]
            if parameter["Save time series"]:
                self.savetype += [True, True]
            else:
                self.savetype += [False, False]
                
            self.calc_min = parameter["Min"]   
            if self.calc_min:
                self.variables += ["Min " + item["Name"]]
                self.units += [unit] 
                self.plottype += [True]
                self.savetype += [True]
                
            self.calc_max = parameter["Max"]      
            if self.calc_max:
                self.variables += ["Max " + item["Name"]]
                self.units += [unit] 
                self.plottype += [True]
                self.savetype += [True]
            
            self.calc_mean = parameter["Mean"] 
            if self.calc_mean:
                self.variables += ["Mean " + item["Name"]]
                self.units += [unit] 
                self.plottype += [True]
                self.savetype += [True]
                
            self.calc_slope = parameter["Slope"] 
            if self.calc_slope:
                self.variables += ["Slope " + item["Name"]]
                self.units += [unit + "/s"] 
                self.plottype += [True]
                self.savetype += [True]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
    
        # UDP connection is singleton instance that handles comnmuication for all driver instances, e.g. if several slots are used
        self.UDPcomm = CoreSensComm.UDPconnection(self.port_string, self.ip_local)
        self.UDPcomm._verbose_mode = True
        
    def disconnect(self):
        self.UDPcomm.close()

       
    def initialize(self):
        
        
        if self.filter == "Moving average":
            if not self.filter_average.isdigit():
               raise Exception("Average number must be an integer between 2 and 2000.")
        
            if int(self.filter_average) < 2:
                raise Exception("Average number must be larger than 1.")
                
            if int(self.filter_average) > 2000:
                raise Exception("Average number must be smaller than 2001.")
        
        elif self.filter == "Adaptive filter":
        
            params = self.filter_adaptive.split(",")
            
            if len(params) != 4:
                raise Exception("Number of adaptive filter parameters must be 4, being TcLow, TcHigh, Threshold, Proportional Bandwidth, e.g. '1, 430 ,0.15 ,3' respectively.")
        
            for par in params:
                try:
                    float(par)
                except:
                    raise Exception("Unable to convert parameter '%s' of adaptive filter to float." % par)
                    
        
    def configure(self):
        
        # First we disable all channels and then we enable the selected ones
        self.UDPcomm.query("CHannel:DISAble:ALL", multi_package = True)
        
        # Enabling selected channels
        for item in self.system_slot_channel_list:
            self.UDPcomm.query("SYSTEM%s%s:CH%s:ENAB" % (item["System"], item["Slot"], item["Channel"]))
            
        ## Measurement rate
        self.UDPcomm.query("SYSTEMS:MEASURE:RATE %i" % self.rate)
        
        
        ## Filter
        if self.filter != "As is":
            for item in self.system_slot_channel_list:
                
                filter_state = {
                                    "None": "0",
                                    "Moving average": "1",
                                    "Adaptive filter": "2",
                                    }

                filter_properties = {
                                    "None": "",
                                    "Moving average": " " + self.filter_average,
                                    "Adaptive filter": " " + self.filter_adaptive.strip(),
                                    }

                self.UDPcomm.query("SYSTEM%s%s:CH%s:FILTER %s%s" % (item["System"], item["Slot"], item["Channel"], filter_state[self.filter], filter_properties[self.filter] ))
 
                
        
        ## Starting infinite acquistion if requested
        if self.acquisition_mode == "infinite":
            self.UDPcomm.query("SYSTEMS:MEASURE:START INFI")


    def unconfigure(self):
        
        self.UDPcomm.query("SYSTEMS:MEASURE:STOP")
        
        
    def measure(self):
    
        if self.acquisition_mode == "finite":
            self.UDPcomm.query("SYSTEMS:MEASURE:START %i" % int(self.acquisition_time * self.rate))
            
            self.starttime_finite = time.perf_counter()
            
    def request_result(self):
        
        if self.acquisition_mode == "finite":
            
            while True:
                answer = self.UDPcomm.query("SYSTEMS:MEASURE:RUN?")[0]
                
                if answer == "0":
                    break # Acquisition complete
                    
                elif answer == "-1":
                    raise Exception("CoreSens is in infinite mode, although it should be in finite mode.")
                    
                else:
                    print("CoreSens: Data pending ->", answer)
        
                if time.perf_counter() - self.starttime_finite > self.acquisition_time + 5:
                    raise Exception("CoreSens did not stop measuring after acquisition time.")
                    
    def read_result(self):
        self.UDPcomm.read_data() # request to readout buffer

    def call(self):

        result = []
        for item in self.system_slot_channel_list:
            # print(item)
            timestamps, values = self.UDPcomm.get_data(int(item["System"]), int(item["Slot"]), int(item["Channel"]))
            result += [timestamps, values]
            
            if self.calc_min:
                if len(values) > 0:
                    result.append(np.min(values))
                else:
                    result.append(float('nan'))
    
            if self.calc_max:
                if len(values) > 0:
                    result.append(np.max(values))
                else:
                    result.append(float('nan'))

            if self.calc_mean:
                if len(values) > 0:
                    result.append(np.mean(values))
                else:
                    result.append(float('nan'))
                
            if self.calc_slope:
                if len(values) > 0:
                    result.append(linregress(timestamps, values).slope)
                else:
                    result.append(float('nan'))
            
        return result
        
       
        
    """ set/get functions start here """
    
    def get_identifcation(self):
        """ returns a list of identification string, one for each channel """
        
        identification = self.UDPcomm.query("*IDN?", multi_package = True)  # we use multi_package = True as this command can trigger multiple modules/channels to respond with a package
        return identification
    
    def get_systems_count(self):
    
        answer = self.UDPcomm.query("SYSTEMS:COUNt?")[0]
        return int(answer)
        
    def disable_all_channels(self):
    
        self.UDPcomm.query("CHannel:DISAble:ALL")
        
    def enable_all_channels(self):
    
        self.UDPcomm.query("CHannel:ENABle:ALL")

    def is_running(self):
        """ returns a bool being True when the CoreSens is running """
        
        answer = self.UDPcomm.query("SYSTEMS:MEASURE:RUN?")[0]
        if answer == "1":
            return True
        elif answer == "0":
            return False
        else:
            raise Exception("SYSTEMS:MEASURE:RUN? must respond with 0 or 1, but '%s' was received." % answer)


    def get_measure_rate(self):
        
        answer = self.UDPcomm.query("SYSTEMS:MEASURE:RATE?")[0]
        return int(float(answer))
        
    def set_measure_rate(self, value):
        
        self.UDPcomm.query("SYSTEMS:MEASURE:RATE %i" % int(float(value)))

""" """
