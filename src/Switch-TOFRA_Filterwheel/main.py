# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2022-2023 SweepMe! GmbH (sweep-me.net)

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

# Contribution: We like to thank TU Dresden/Fred Kretschmer for providing the initial version of this driver.

# SweepMe! device class
# Type: Switch
# Device: TOFRA Filterwheel (107 series and 109 series)

from pysweepme.ErrorMessage import error

from pysweepme.EmptyDeviceClass import EmptyDevice
import numpy as np

import time

class Device(EmptyDevice):

    description =   """
        <p><strong>Usage:</strong></p>
        <ul>
        <li>If Sweep mode == "Position", the selected Sweep value is used.</li>
        <li>If Sweep mode == "Wavelength in nm", the filter is selected in accordance to the 'Filter position'.</li>
        <li>If Sweep mode == "Energy in eV", the filter is selected in accordance to the 'Filter position'.</li>
        Define your own filter-wavelength dependencies in the .ini file using the format:<br>
        wl -> filter slot &lt;- wl -> filter slot &lt;- wl
        <li>If Sweep mode == "None", the position given in the field 'Value' is used, if button apply is pressed. It can be used as convenience setting for when no sweep is made (equivalent to one value sweep)</li>
        <li>If button "Apply" is pressed, the position given in the field 'Value' is set except for Sweep Mode "Energy in eV"</li>
        <li>Home position: position to return to at end of program ("None" = stay) or after pressing "Stop"</li>
    """

    def __init__(self):

        super().__init__()

        # Short name in sequencer
        self.shortname = "TOFRA filterwheel"

        self.variables = ["Filter"]
        self.units = [""]
        self.plottype = [True]
        self.savetype = [True]

        # Filter positions
        self.positions = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]  # 12 filter positions
        
        # loads from further Filter configurations from .ini that is expected in public folder "CustomFiles"
        self.positions_to_add = list(self.get_configoptions("Filter").values())
        
        self.port_manager = True
        self.port_types = ["COM"]

        self.port_properties = {
            "EOL": "\r\n",
            "timeout": 1.0,
            "baudrate": 9600,
        }

    def set_GUIparameter(self):

        GUIparameter = {
                         "Filter position": self.positions + self.positions_to_add,
                         "End position": ["None"] + self.positions,
                         "SweepMode": ["Filter", "None", "Wavelength in nm", "Energy in eV"],  
                        }
        return GUIparameter   

    def get_GUIparameter(self, parameter={}):

        self.sweepmode = parameter["SweepMode"] 
        self.pos = parameter["Filter position"]
        self.filter_readout = self.pos.replace("<", "").replace(">", "").replace("nm", "").replace(" ", "").split("-")
        self.pos_list = np.array(self.filter_readout[::2], dtype = int)
        self.filter_wavelengths = np.array(self.filter_readout[1::2], dtype = float)
        self.end_position = parameter["End position"]

    def connect(self):
        """
        Check, if the motor is connected
        """

        self.port.write("/1&")   # returns the motor identity
        answer = self.port.read()

    def disconnect(self):
        pass

    def initialize(self):

        # set instrument at GUI selected state and ready for next commands
        if self.sweepmode == "None":
            if len(self.pos_list) > 1:
                raise Exception("Please use a single filter in field 'Filter position' if Sweep mode is None.")

    def deinitialize(self):
        pass

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
        #if self.home != "None":
            #self.go_home()
            #self.get_position()

    def configure(self):
        """
        Initialization of filter wheel according to the manual
        http://www.allmotion.com/PDF_Datasheets/Command_Set_EZHR17EN.pdf
        """

        # set number of microsteps to 1/16th of one step
        self.port.write('/1j16R')
        answer = self.port.read()

        # set hold current to 10 % of max current (2A)
        self.port.write('/1h10R')  
        answer = self.port.read()

        # set run current to 75% of of max current (2A)
        self.port.write('/1m75R')  
        answer = self.port.read()

        # set slew velocity
        self.port.write("/1V1000R") 
        answer = self.port.read()

        # set acceleration/deceleration to 12
        self.port.write('/1L12R')
        answer = self.port.read()

        # set flag polarity to 0
        self.port.write('/1f0R')
        answer = self.port.read()

        # disable limits
        self.port.write('/1n0R')
        answer = self.port.read()

        # go to home position
        self.go_home()
        
        if self.sweepmode == "None":  # case for set value
            self.move_to_filter(int(self.value))

        self._current_filter_position = None

    def unconfigure(self):
        if self.end_position != "None":
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
            self.move_to_filter(self.end_position)

    def apply(self):
        if (self.sweepmode != "Wavelength in nm" and self.sweepmode != "Energy in eV" and
                str(int(self.value)) not in self.positions):
            raise Exception("Filter position %s not in 1-12 range" % str(int(self.value)))
            
        if self.sweepmode == "Filter":
            self.move_to_filter(int(self.value))
            
        elif self.sweepmode == "None":
            self.move_to_filter(int(self.value))
            
        elif self.sweepmode == "Wavelength in nm":

            # do not send more than three digits after decimal separator
            self.wavelength_to_set = round(float(self.value), 3)
            # Based on the wavelength the filter will be chosen
            # 1. step: find the index at which between two wavelengths, the filter has to be changed 
            # 2. step: find the filter slot based on that index
            pos = np.sum(np.array(self.filter_wavelengths, dtype=float) < self.wavelength_to_set)
            filter_to_set = self.pos_list[pos]
            
            # if apply is pressed and not run, then value in "configuration box" is set,
            # otherwise the filter in accordance to the "filter position box" is set
            if self.value in self.positions:
                self.move_to_filter(int(self.value))
            else:
                self.move_to_filter(int(filter_to_set))
                
        elif self.sweepmode == "Energy in eV":
            # if apply is pressed and not run, then value in "Values" is not set, if "Energy in eV" is selected
            
            # do not send more than three digits after decimal separator
            # change eV into nm 
            self.wavelength_to_set = round(float(4.135667e-15*2.99792e8/(float(self.value)*1e-9)),3)
            # Based on the wavelength the filter will be chosen
            # 1. step: find the index at which between two wavelengths, the filter has to be changed 
            # 2. step: find the filter slot based on that index
            filter_to_set = self.pos_list[np.sum(np.array(self.filter_wavelengths, dtype = float) < self.wavelength_to_set)]
            self.move_to_filter(int(filter_to_set))

    def call(self):
        return self._current_filter_position

    def move_to_filter(self, filter_number):
        """
        Moves to filter using set_filter by multiple retries in case the new position is not reached.
        
        Args:
            filter_number (str) number of filter
        """

        retries = 3
        
        for i in range(retries):
            set_position = self.set_filter(filter_number)
            try:
                self.reach_position(set_position)
                break
            except:
                error("Unable to reach new filter position")
        
        self._current_filter_position = filter_number

    def set_filter(self, filter_number):
        """
        Moves to filter, according to the initial filter number.
        Converts the filter number to the absolute motor position.
        Initial is the filter number as an integer. 
        Args:
            filter_number (str) number of filter
        """

        filter_number = int(filter_number)
        
        # microsteps 
        micro_steps = 16 
        
        # number of big steps
        big_steps = 200
        
        # number of total steps 
        num_total_steps = micro_steps * big_steps
        
        set_position = int(num_total_steps / 12 * (filter_number - 1))
        self.set_position(set_position)
        self.answer = self.port.read()
        
        return set_position

    def reach_position(self, set_position):
        """
        Checks, if the target position is reached
        Args:
            set_position: (int) motor position of target filter
        """        

        starttime = time.time()
        while True:
            real_position = self.get_position()
            if real_position == set_position:
                break
            time.sleep(0.02)
            if time.time() - starttime > 3:
                raise TimeoutError("Unable to reach new filter position within timeout")
        
    def go_home(self):
        """
        Motor moves to home position of the filter, which is position 1 
        """
        self.port.write("/1Z30000R") 
        answer = self.port.read()
        self.reach_position(0)
        time.sleep(0.02)

    def set_position(self, position):
        """
        set the motor position in steps
        Args:
            position: (int) motor position in steps
        """
        self.port.write('/1A{}R'.format(position))
        time.sleep(0.02)
        
    def get_position(self):
        """
        gets the motor position in steps

        Returns:
            int: motor positions in steps

        """
        self.port.write("/1?0")
        answer = self.port.read()
        return int(answer[4:-1])
