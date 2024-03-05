# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018, 2020 Axel Fischer (sweep-me.net)
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
# Type: Monochromator
# Device: Cornerstone260



import time
from collections import OrderedDict
import numpy as np

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description =   """
                    Newport 74125 Oriel Cornerstone260 or similar<br>
                    <br>
                    Features:<br>
                    <ul>
                    <li>supports change of filters or gratings at defined wavelengths</li>
                    <li>supports the buttons of the Monochromator module</li>
                    <li>needs SweepMe! version >= 1.5.2.6</li>
                    </ul>
                    <br>
                    To define custom filter and grating ranges, copy the template file Monochromator-Newport_OrielCornerstone260.ini inside this DeviceClass folder to the "Custom files" folder of your public SweepMe! folder.<br>
                    <br>
                    Define your own filter-wavelength dependencies using the format:<br>
                    wl -> filter slot <- wl -> filter slot <- wl<br>
                    <br>      
                    Define your own grating-wavelength dependencies using the format:<br>
                    wl -> grating slot <- wl -> grating slot <- wl<br>
                    """

    def __init__(self):
        super().__init__()

        self.shortname = "Cornerstone260"

        self.variables = ["Wavelength (set)", "Wavelength (real)", "Filter", "Grating"]
        self.units = ["nm", "nm", "#", "#"]
        self.plottype = [True, True, True, True] # True to plot data
        self.savetype = [True, True, True, True] # True to save data

        # here the port handling is done
        # the MeasClass automatically creates the PortObject during in the connect function of the MeasClass
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        # self.port_identifications = ['Ametek,7280']
        # port_identifications does not work at the moment

        self.port_properties = { "EOL": "\r\n",
                                 "timeout": 30,
                                 "baudrate": 9600,
                                 "Exception": True,
                                 "GPIB_EOLwrite": "\r\n",
                                 "GPIB_EOLread": "\r\n",
                                 "delay": 0.05,
                            }
        # properties are used to change the properties of the PortObject
        
                
        self.filters = [
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        ]
            
        filters_to_add = self.get_configoptions("Filter")
        for key in filters_to_add :
            self.filters.append(filters_to_add[key])
                        

        self.gratings = [
                         "1",
                         "2",
                         "3", 
                         ]
                         
        gratings_to_add = self.get_configoptions("Grating")
        for key in gratings_to_add :
            self.gratings.append(gratings_to_add[key])


        # AF 22.05.20: Axial is now 2, and Lateral is now 3, changed after is was other way around in the beginning
        self.slitoutputs = OrderedDict([
                            ("Axial", 2),
                            ("Lateral", 3),
                            ])

        # 29.06.20: outport were changed/switched as well. Axial is now 2, and Lateral is now 1.
        self.outport = OrderedDict([
                            ("Axial", 2),
                            ("Lateral", 1),
                            ])
        
        
    def set_GUIparameter(self):

        GUIparameter = {
                         "SweepMode": ["Wavelength [nm]"], # "Reflection (zero order)", "Slitwidth [µm]" needs additional fix wavelength option
                         "Output" : list(self.slitoutputs.keys()),
                         "Filter": self.filters,
                         "Grating": self.gratings,
                         "SlitOutput": ["As is", "3000 (max)", "1500", "6 (min)"],
                         "SlitInput": [ "As is", "3000 (max)", "1500", "6 (min)"],
                         "Wavelength": "",
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter = {}):

        #Wavelength
        self.wavelength_fixed = parameter["Wavelength"]
        
        #Selected Port
        self.port_string = parameter["Port"]
    
        #SweepMode
        self.sweepmode = parameter["SweepMode"]
        
        # Output port
        self.output = parameter["Output"]
        
        #Filter
        self.filter = parameter["Filter"]
        self.filter_readout = self.filter.replace("<", "").replace(">", "").replace("nm", "").replace(" ", "").split("-")
        
        # print(self.filter_readout)
        self.filter_list = np.array(self.filter_readout[::2], dtype = int)
        self.filter_wavelengths = np.array(self.filter_readout[1::2], dtype = float)
        
        #Grating
        self.grating = parameter["Grating"]
        self.grating_readout = self.grating.replace("<", "").replace(">", "").replace("nm", "").replace(" ", "").split("-")
        
        # print(self.grating_readout)
        self.grating_list = np.array(self.grating_readout[::2], dtype = int)
        self.grating_wavelengths = np.array(self.grating_readout[1::2], dtype = float)
       
        # Slits
        self.slit_input = str(parameter["SlitInput"])
        self.slit_output = str(parameter["SlitOutput"])
        

            
    def initialize(self):
    
        if self.slit_input != "As is":
            
            self.slit_input_number = int(self.slit_input.split(" ")[0])
        
            if self.slit_input_number < 6 or self.slit_input_number > 3000:
                self.stopMeasurement = "Please use an input slit width larger than 6 µm and smaller than 3000 µm!"
                return False
    
        if self.slit_output != "As is":
        
            self.slit_output_number = int(self.slit_output.split(" ")[0])
        
            if self.slit_output_number  < 6 or self.slit_output_number > 3000:
                self.stopMeasurement = "Please use an input slit width larger than 6 µm and smaller than 3000 µm"
                return False
          
        # Status byte  
        self.get_status_byte()

        # Standard wavelength unit is nm
        self.write_cmd("UNITS NM")
                        

    def deinitialize(self):
        # stop any motor wavelength motion
        self.write_cmd("ABORT")
        
    def configure(self):
                
        # change slit width of input port
        if self.slit_input != "As is":
            if not self.change_slit("SLIT1MICRONS", self.slit_input_number): 
                self.stopMeasurement = "Cannot set input slit width. Please check whether your monochromator has a motorized slit control and use the option 'As is' if the slit width is controlled manually. Some models support only 2000 µm as the maximum slit width."
                return False
        
        # change to the right output port and slit width
        if not self.change_state('OUTPORT', self.outport[self.output]):
            return False
          
        # change slit width of output port
        if self.slit_output != "As is":          
            if not self.change_slit("SLIT%iMICRONS" % self.slitoutputs[self.output], self.slit_output_number):
                self.stopMeasurement = "Cannot set output slit width. Please check whether your monochromator has a motorized slit control and use the option 'As is' if the slit width is controlled manually. Some models support only 2000 µm as the maximum slit width."
                return False
                                
        # open the shutter
        if not self.change_state('SHUTTER', 'O'):
            return False
            
           
        if self.sweepmode != "Wavelength [nm]":
            
            self.wavelength_to_set = round(float(self.wavelength_fixed),3)

            filter_to_set = self.filter_list[np.sum(np.array(self.filter_wavelengths, dtype = float) < self.wavelength_to_set)]
            self.change_state('FILTER', filter_to_set)
            
            grating_to_set = self.grating_list[np.sum(np.array(self.grating_wavelengths, dtype = float) < self.wavelength_to_set)]
            self.change_state('GRAT', grating_to_set)
            
            self.write_cmd("GOWAVE %s" % str(self.wavelength_to_set))
            

    def unconfigure(self):
        # close the shutter
        self.change_state('SHUTTER', 'C')


    def apply(self):
    
        if self.sweepmode == "Wavelength [nm]":
            
            # do not send more than three digits after decimal separator or the monochromator will break/no communication anymore
            self.wavelength_to_set = round(float(self.value),3) # self.wavelength_config(self.value)
            
            # Based on the wavelength the grating and the filter will be chosen
            # 1. step: find the index at which between two wavelengths, the filter or the grating has to be changed 
            # 2. step: find the filter or grating slot based on that index
            
            filter_to_set = self.filter_list[np.sum(np.array(self.filter_wavelengths, dtype = float) < self.wavelength_to_set)]
            self.change_state('FILTER', filter_to_set)
            
            grating_to_set = self.grating_list[np.sum(np.array(self.grating_wavelengths, dtype = float) < self.wavelength_to_set)]
            self.change_state('GRAT', grating_to_set)
       
            self.write_cmd("GOWAVE %s" % str(self.wavelength_to_set))
            
    def reach(self):        
        self.write_cmd("WAVE?")
        self.current_wavelength = float(self.port.read())
        self.write_cmd("GRAT?")
        self.current_grating = int(self.port.read().split(',')[0])
        self.set_grating = self.current_grating
        self.write_cmd("FILTER?")
        self.current_filter = int(self.port.read())
        self.set_filter = self.current_filter
    
    def measure(self):
        pass

    def call(self):
        return [self.wavelength_to_set, self.current_wavelength, self.current_filter, self.current_grating]
        
        
    """ """    
        
    def write_cmd(self, cmd):
        """ function to send commands differently for GPIB and COM """
    
        self.port.write(cmd)
    
        if self.port_string.startswith("COM"):
            self.port.read() # reading back the command
        
    """ """      
        
    def get_status_byte(self):
    
        self.write_cmd("STB?")
        
        stb = self.port.read()
        if stb == "20":
            self.write_cmd("ERROR?")
            print("ERROR:", self.port.read())
        
        return stb
    
    def change_state(self, cmd, new_state):
                  
        self.write_cmd("%s %s" % (cmd,str(new_state)))

        self.write_cmd("%s?" % cmd)
        current_state = self.port.read().split(",")[0]
            
        if str(new_state) == current_state:
            return True
        else:
            self.stopMeasurement = "State %s did not change to %s" % (cmd, str(new_state))
            return False
            
    def change_slit(self, cmd, new_state):
              
        self.write_cmd("%s %s" % (cmd,str(new_state)))

        self.write_cmd("%s?" % cmd)
        current_state = int(self.port.read())
            
        if abs(new_state - current_state) < 6:
            return True
        else:
            self.stopMeasurement = "State %s did not change to %s" % (cmd, str(new_state))
            return False
            
        