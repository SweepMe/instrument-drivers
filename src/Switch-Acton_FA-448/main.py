# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2021 SweepMe! GmbH

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank TU Dresden/Jakob Wolansky for providing the initial version of this driver.

# SweepMe! device class
# Type: Switch
# Device: Acton FA-448

from EmptyDeviceClass import EmptyDevice #sweepMe base class
import numpy as np

import time

class Device(EmptyDevice):

    description =   """
                        <p><strong>Usage:</strong></p>
                        <ul>
                        <li>If Sweep mode == "Position", the selected Sweep value is used.</li>
                        <li>If Sweep mode == "Wavelength in nm", the filter is selected in accordance to the 'Filter position'.</li>
                        <li>If Sweep mode == "Energy in eV", the filter is selected in accordance to the 'Filter position'.</li>
                        To define custom filter and grating ranges, copy the template file Switch-Acton_FA-448.ini inside this driver folder to the "CustomFiles" folder of your public SweepMe! folder.<br>
                        Define your own filter-wavelength dependencies using the format:<br>
                        wl -> filter slot &lt;- wl -> filter slot &lt;- wl
                        <li>If Sweep mode == "None", the position given in the field 'Value' is used, if button apply is pressed. It can be used as convenience setting for when no sweep is made (equivalent to one value sweep)</li>
                        <li>If button "Apply" is pressed, the position given in the field 'Value' is set except for Sweep Mode "Energy in eV"</li>
                        <li>Home position: position to return to at end of program ("None" = stay) or after pressing "Stop"</li>
                    """

    def __init__(self):

        EmptyDevice.__init__(self)

        # Short name in sequencer
        self.shortname = "FA-448"

        self.variables = ["Position"]
        self.units = ["#"]
        self.plottype = [True] # True to plot data
        self.savetype = [True] # True to save data

        # Filter positions
        self.positions = ["1","2","3","4","5","6"]
        # loads from further Filter configurations from Switch-Acton_FA-448.ini that is expected in public folder "CustomFiles"
        self.positions_to_add = list(self.getConfigOptions("Filter").values())  


        self.port_manager = True
        self.port_types = ["GPIB", "COM"]

        self.port_properties = {
            "GPIB_EOLwrite": "\r",
            "timeout": 10.0,
        }
    
    def set_GUIparameter(self):


        GUIparameter = {
                         "Filter position" : self.positions + self.positions_to_add,
                         "Home position" : ["None"] + self.positions,
                         "SweepMode": ["Position", "None", "Wavelength in nm", "Energy in eV"],
                        }
        
        return GUIparameter   

    def get_GUIparameter(self, parameter={}):
        
        self.sweepmode = parameter["SweepMode"]

        self.pos = (parameter["Filter position"])
        self.filter_readout = self.pos.replace("<", "").replace(">", "").replace("nm", "").replace(" ", "").split("-")
        
        self.pos_list = np.array(self.filter_readout[::2], dtype = int)
        self.filter_wavelengths = np.array(self.filter_readout[1::2], dtype = float)

        self.home = parameter["Home position"]
        
        self.config = parameter["Configuration"]
        

    def connect(self):
        # figure out early whether a connection is established
        self.port.write("?Filter")
        answer = self.port.read()
            
    def disconnect(self):
        pass
 
    def initialize(self):
        ''' set instrument at GUI selected state and ready for next commands'''
        if len(self.config) > 1:
            self.stop_Measurement("Please use a single filter in field 'Configuration' if you choose Set value.")
            return False
        if self.sweepmode == "None":
            if len(self.pos_list) > 1:
                self.stop_Measurement("Please use a single filter in field 'Filter position' if Sweep mode is None.")
                return False
            
    def deinitialize(self):
        if self.home != "None":
            """
            Initializes the filter wheel to the first filter position.
            This command is automatically executed at power-up.
            The filter wheel controller keeps track of filter
            position as long as power is applied. It should not be
            necessary to execute this command under normal
            circumstances, although it is available if desired. This
            command follows the same format as in FILTER above
            for entry and response.
            """
            self.port.write("FHOME")
            self.port.write("?Filter")
            # set individual home position
            self.port.write(str(int(self.home)) + " Filter")
            self.port.write("?Filter")
            answer = self.port.read()
    
    def configure(self):
        pass
        # if self.sweepmode == "None": #case for set value
            # self.port.write(str(int(self.pos)) + " Filter")
            
    def unconfigure(self):
        if self.home != "None":
            """
            Initializes the filter wheel to the first filter position.
            This command is automatically executed at power-up.
            The filter wheel controller keeps track of filter
            position as long as power is applied. It should not be
            necessary to execute this command under normal
            circumstances, although it is available if desired. This
            command follows the same format as in FILTER above
            for entry and response.
            """
            self.port.write("FHOME")
            self.port.write("?Filter")
            # set individual home position
            self.port.write(str(int(self.home)) + " Filter")
            self.port.write("?Filter")
            answer = self.port.read()
            
    def apply(self):
        # if set value is not a filter position, return error
        if self.sweepmode != "Wavelength in nm" and  self.sweepmode != "Energy in eV" and not str(int(self.value)) in self.positions:
            self.stop_Measurement("Filter position %s not in 1-6 range" % str(int(self.value)))
            return False
            
        if self.sweepmode == "Position":
            self.port.write(str(int(self.value)) + " Filter")
            # for apply case: to confirm the latest command, send "?Filter" command
            self.port.write("?Filter")
            answer = (self.port.read())
        elif self.sweepmode == "Wavelength in nm":
            # if self.value is below than 10, it's probably an energy and not a wavelength
            if self.value < 10:
                raise Exception("Check sweepmode. Wavelength expected, but probably energy or position received.")
            # do not send more than three digits after decimal separator
            self.wavelength_to_set = round(float(self.value),3)
            # Based on the wavelength the filter will be chosen
            # 1. step: find the index at which between two wavelengths, the filter has to be changed 
            # 2. step: find the filter slot based on that index
            filter_to_set = self.pos_list[np.sum(np.array(self.filter_wavelengths, dtype = float) < self.wavelength_to_set)]
            # if apply is pressed and not run, then value in "configuration box" is set, otherwise the filter in accordance to the "filter position box" is set
            if self.value in self.positions:
                self.port.write(str(int(self.value)) + " Filter")
                self.port.write("?Filter")
                self.port.write("?Filter")
                answer = (self.port.read())
            else:
                self.port.write(str(int(filter_to_set)) + " Filter")
        elif self.sweepmode == "Energy in eV":
            # if self.value is higher than 10, it's probably a wavelength and not an energy
            if self.value > 10:
                raise Exception("Check sweepmode. Energy expected, but probably wavelength received.")
            # if apply is pressed and not run, then value in "Values" is not set, if "Energy in eV" is selected
            
            # do not send more than three digits after decimal separator
            # change eV into nm 
            self.wavelength_to_set = round(float(4.135667e-15*2.99792e8/(float(self.value)*1e-9)),3)
            # Based on the wavelength the filter will be chosen
            # 1. step: find the index at which between two wavelengths, the filter has to be changed 
            # 2. step: find the filter slot based on that index
            filter_to_set = self.pos_list[np.sum(np.array(self.filter_wavelengths, dtype = float) < self.wavelength_to_set)]
            self.port.write(str(int(filter_to_set)) + " Filter")
        elif self.sweepmode == "None": #case for set value
            self.port.write(str(self.value) + " Filter")
            # for apply case: to confirm the latest command, send "?Filter" command
            self.port.write("?Filter")
            answer = (self.port.read())
            
    def reach(self):
        # makes sure the new filter is reached before the next measurement is done
        self.port.write("?Filter")
        answer = (self.port.read())
        
    def measure(self):
        self.port.write("?Filter") # we ask for the filter in 'measure' and read the result in 'read_result', still necessary after each comment which was sent
    
    def read_result(self):
        self.answer = (self.port.read())
        
    def call(self):
        return self.answer
