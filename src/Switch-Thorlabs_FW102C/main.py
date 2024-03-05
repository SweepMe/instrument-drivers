# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022-2023 SweepMe! GmbH
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

# Contribution: We like to thank TU Dresden/Jakob Wolansky for providing the initial version of this driver.

# SweepMe! device class
# Type: Switch
# Device: Thorlabs FW102C

import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
        <p><strong>Usage:</strong></p>
        <ul>
        <li>If Sweep mode is "Position", the index of the filter wheel is set.<br /><br /></li>
        <li>If Sweep mode is "Wavelength in nm", the filter is selected according to a given filter-wavelength 
        dependence.<br /><br /></li>
        <li>If Sweep mode is "Energy in eV", the filter is selected according to a given filter-wavelength 
        dependence.<br /><br /></li>
        <li>To define custom filter and grating ranges, copy the template file Switch-Thorlabs_FW102C.ini inside 
        this driver folder to the "CustomFiles" folder of your public SweepMe! folder.<br /><br />Define your own 
        filter-wavelength dependencies using the format:<br />filter slot &lt;- wl -&gt; filter slot &lt;- wl -&gt; 
        filter slot<br />You can define multiple entries. They will appear in the field 
        "Filter position<br /><br /></li>
        <li>If Sweep mode == "None", the position given in the field "Filter position" is used in a measurement run. 
        If the button 'Apply' is pressed, the 'Value' from the Test section is used, which can be used to manually set 
        the filter position. However, the "Apply" functionality only works if the Sweep mode is not "Energy in eV"</li>
        </ul>
        <ul>
        <li>Home position: position to return to at end of program ("None" = stay) or after pressing "Stop"</li>
        </ul>
    """

    def __init__(self):

        super().__init__()

        # Short name in sequencer
        self.shortname = "FW102C"

        self.variables = ["Position"]
        self.units = ["#"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        # Filter positions
        self.filter_positions = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
        # loads from further Filter configurations from Switch-Thorlabs_FW102C.ini that is
        # expected in public folder "CustomFiles"
        self.positions_to_add = list(self.get_configoptions("Filter").values())

        self.port_manager = True
        self.port_types = ["COM"]

        self.port_properties = {
                                "EOLwrite": "\r",
                                "timeout": 2,
                                "baudrate": 115200,
                                }
    
    def set_GUIparameter(self):

        gui_parameter = {
                         "Filter position": self.filter_positions + self.positions_to_add,
                         "Home position": ["None"] + self.filter_positions,
                         "SweepMode": ["Position", "None", "Wavelength in nm", "Energy in eV"],
                        }
        
        return gui_parameter

    def get_GUIparameter(self, parameter={}):
        
        self.sweepmode = parameter["SweepMode"]

        self.pos = parameter["Filter position"]
        self.filter_readout = self.pos.replace("<", "").replace(">", "").replace("nm", "").replace(" ", "").split("-")
        
        self.pos_list = np.array(self.filter_readout[::2], dtype=int)
        self.filter_wavelengths = np.array(self.filter_readout[1::2], dtype=float)

        self.end_position = parameter["Home position"]

    def initialize(self):
    
        # identification = self.get_identification()
        # print("Identification:", identification)
    
        number_filters = self.get_position_count()
        self.positions = list(range(1, number_filters + 1))

        if self.end_position != "None" and int(self.end_position) not in self.positions:
            raise Exception("Filter end position %i must be in range 1-%i" %
                            (int(self.end_position), self.positions[-1]))

    def configure(self):
        self.last_position = self.get_position()

        if self.sweepmode == "None":
            self.pos = int(self.pos)
            if self.pos not in self.positions:
                raise Exception("Filter position %s not in range 1-%i" % (int(self.pos), self.positions[-1]))
            self.set_position(self.pos)

    def unconfigure(self):
        if self.end_position != "None":
            self.set_position(self.end_position)

    def apply(self):

        # This can happen if the Configuration field is used.
        if self.value == "":
            raise Exception("Empty string received. Probably you need to enter a value in the Test section "
                            "of the module.")

        self.value = float(self.value)

        # if set value is not a filter position, return error
        if self.sweepmode in ["Position", "None"]:
            self.value = int(self.value)
            if self.value not in self.positions:
                raise Exception("Filter position %s not in range 1-%i" % (self.value, self.positions[-1]))

            self.set_position(self.value)

        elif self.sweepmode == "Wavelength in nm":
            # do not send more than three digits after decimal separator
            self.wavelength_to_set = round(float(self.value), 3)
            # Based on the wavelength the filter will be chosen
            # 1. step: find the index at which between two wavelengths, the filter has to be changed 
            # 2. step: find the filter slot based on that index
            index = np.sum(np.array(self.filter_wavelengths, dtype=float) < self.wavelength_to_set)
            filter_to_set = self.pos_list[index]
            # if apply is pressed and not run, then value in "configuration box" is set, otherwise the filter in
            # accordance to the "filter position box" is set
            if int(self.value) in self.positions:
                self.set_position(self.value)
            else:
                self.set_position(filter_to_set)

        elif self.sweepmode == "Energy in eV":
            # if apply is pressed and not run, then value in "Values" is not set, if "Energy in eV" is selected
            
            # do not send more than three digits after decimal separator
            # change eV into nm 
            self.wavelength_to_set = round(float(4.135667e-15*2.99792e8/(float(self.value)*1e-9)), 3)
            # Based on the wavelength the filter will be chosen
            # 1. step: find the index at which between two wavelengths, the filter has to be changed 
            # 2. step: find the filter slot based on that index
            index = np.sum(np.array(self.filter_wavelengths, dtype=float) < self.wavelength_to_set)
            filter_to_set = self.pos_list[index]
            self.set_position(filter_to_set)
            # print(str(int(filter_to_set)))

        # We query the position to figure as the instrument answers when the new position is reached
        # The answer will be read in 'reach'
        self.port.write("pos?")

    def reach(self):
        # We read the answer of the position query in 'apply'
        # As 'reach' is only performed if 'apply' is called we can expect an answer in the buffer
        answer_str = self.port.read()
        self.last_position = int(answer_str[answer_str.find("pos?") + len("pos?") + 1])

    def call(self):
        return self.last_position

    """ Here, convenience functions start """

    def get_identification(self):
        
        self.port.write("*idn?")
        answer = self.port.read()
        return answer
        
    def get_position_count(self):
        
        self.port.write("pcount?")
        answer_str = self.port.read()
        number_positions = int(answer_str[answer_str.find("pcount?") + len("pcount?") + 1])
        return number_positions
        
    def set_position(self, pos):
        
        self.port.write("pos=%i" % int(pos))

    def get_position(self):
    
        self.port.write("pos?")
        answer_str = self.port.read()
        position = int(answer_str[answer_str.find("pos?") + len("pos?") + 1])
        
        return position
