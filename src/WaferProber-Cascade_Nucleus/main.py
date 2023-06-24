# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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
# Type: WaferProber
# Device: Cascade Nucleus

import time
import numpy as np

from pysweepme.ErrorMessage import error, debug

from pysweepme.EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Nucleus"
        self.variables = ["Die", "Die x", "Die y", "Subsite", "x", "y", "z"]
        self.units = ["", "", "", "", "mm", "mm", "mm"]
        self.plottype = [True, True, True, True, True, True, True]
        self.savetype = [True, True, True, True, True, True, True]

        self.port_manager = True
           
        # use GPIB as interface
        self.port_types = ["GPIB"]
        
        # port_properties
        self.port_properties = {
                                "timeout": 10,  # 10 seconds timeout should be enough to reach a new die/subsite
                                }
                
        self.DevID = "2"  # Used to control the chuck on Elite Series, Summit 12000-Series, S300 and Alessi 6100

    def get_probeplan(self):

        # wafers
        wafers = []

        # dies
        dies = []

        # Manual: This query returns the number of die marked for testing in the currently active probe plan.
        self.port.write(":prob:ntes? %s" % self.DevID)
        # Manual: If you have not yet loaded a probe plan file, this query returns nothing.
        answer = self.port.read()

        try:
            number_dies = int(answer)
        except ValueError:
            error("No dies have been found. Response was '%s' which cannot be interpreted as integer. "
                  "Please check whether dies are selected." % answer)
            # in case no probe plan is loaded, the answer will be None or 'None' and in this case no die will be added.
            number_dies = 0

        for i in np.arange(number_dies)+1:
            self.port.write(":prob:die:loc? %i" % i)
            answer = self.port.read().replace(" ", ",")
            dies.append(answer)

        # subsites
        subsites = []

        # Manual: Returns the total number of subsites whether they are marked as active or not.
        self.port.write(":prob:subs:tot?")
        answer = self.port.read()

        try:
            number_subsites = int(answer)
        except ValueError:
            error("No subsites have been found. Response was '%s' which cannot be interpreted as integer. "
                  "Please check whether subsites are selected." % answer)
            # in case no probe plan is loaded, the answer is not clear (not described in the manual) and no subsites
            # will be added.
            number_subsites = 0

        for i in range(number_subsites):
            # Returns the test status of a subsite at the given index. 'ON' or 'OFF'
            self.port.write(":prob:set:subs:lab:act? %i" % i)
            answer = self.port.read()
            if answer == "ON":
            
                # lets read the subsite label if the subsite is active
                # Returns the descriptive text field used to identify the subsite.
                self.port.write(":prob:subs:lab? %i" % i)
                label = self.port.read()
                
                if label != "COMPLETE":
                    subsites.append("%i#%s" % (i, label))
                else:
                    # label is unknown and command has returned "COMPLETE"
                    subsites.append("%i" % i)

        return wafers, dies, subsites, probeplan_file

    def get_current_wafer(self) -> str:
        """
        WaferProber module specific function

        Returns: str of current wafer, empty if not available
        """
        return ""

    def get_current_die(self) -> str:
        """
        WaferProber module specific function

        Returns: str of current die, empty if not available
        """

        # current die
        self.port.write(":mov:prob:abs:ind?")
        current_die_testindex = self.port.read()

        self.port.write(":prob:die:loc? %s" % current_die_testindex)
        current_die = self.port.read().replace(" ", ",")

        return current_die

    def get_current_subsite(self) -> str:
        """
        WaferProber module specific function

        Returns: str of current subsite, empty if not available
        """

        self.port.write(":mov:prob:abs:subs?")
        current_subsite_index = self.port.read()

        # Returns the descriptive text field used to identify the subsite.
        self.port.write(":prob:subs:lab? %s" % current_subsite_index)
        label = self.port.read()
                
        if label != "COMPLETE":
            current_subsite = "%s#%s" % (current_subsite_index, label)       
        else:  # label is unknown and command has returned "COMPLETE"
            current_subsite = "%s" % current_subsite_index

        return current_subsite

    # here semantic standard function start

    def connect(self):

        # SUMMIT is the standard SCPI command set.
        self.port.write("$:set:mode summit")

        # Sends an ASCII string “COMPLETE” to the host after each operation is completed unless an error occurs.
        self.port.write("$:set:resp ON")

    def initialize(self):

        # Ask for the identification string
        self.port.write("*idn?")
        print("Identification nucleus:", self.port.read())
        
        # reset
        """ !! Attention: reset is not used at the moment as it is unclear which parameters are reset. 
        In the worst case, the entire probe plan is reset. !! """
        # self.port.write("*rst")  #*rst reset Resets the probe station. This command is the same as the *cls command.
        
        # Ask for the probe plan file
        # self.port.write(":prob:load? %s" % self.DevID)
        # print("Probeplan file:", self.port.read())
        
        # Ask for the wafer diameter
        # self.port.write(":prob:waf? %s" % self.DevID)
        # print("Wafer diameter with DevID:", self.port.read())
        
        # self.port.write(":prob:waf?")
        # print("Wafer diameter without DevID:", self.port.read())
      
        # Ask for the unit
        # self.port.write(":set:unit?")
        # print("Unit:", self.port.read())
        
        # Ask for the z contact distance
        # self.port.write(":set:contact? %s" % self.DevID)
        # print("Contact height:", self.port.read())
        
        # Ask for if the wafer prober is separated
        # self.port.write(":mov:sep? %s" % (self.DevID))
        # print("Is separated?:", self.port.read())

    def deinitialize(self):
        pass
        # can be used to move home at the end of the measurement
        # self.port.write(":move:cont? %s" % (self.DevID))
        # if self.port.read() == "FALSE": # only if the wafer prober is not contacted and returns FALSE, we can go home
        #    self.port.write(":mov:home %s" % self.DevID)

    def configure(self):
    
        # if the wafer prober is contacted, lets make sure the contacts get separated
        self.port.write(":move:cont? %s" % self.DevID)
        if self.port.read() == "TRUE":
            
            # separate
            self.port.write(":mov:sep %s" % self.DevID)
            if not self.read_complete():
                return False
                
            # final check whether the wafer prober is separated
            self.port.write(":move:cont? %s" % self.DevID)
            if self.port.read() == "TRUE":
                self.stop_Measurement("Separation did not succeed. Please take care to separate the contacts before "
                                      "you continue.")
                return False

        # Ask for the probe plan file and save to logbook file
        self.port.write(":prob:load? %s" % self.DevID)
        probeplan_file = self.port.read()
        self.write_Log("Wafer map %s loaded" % probeplan_file)
            
    def unconfigure(self):
    
        # if the wafer prober is still in contact, lets separate it
        self.port.write(":move:cont? %s" % self.DevID)
        if self.port.read() == "TRUE":
        
            # separate
            self.port.write(":mov:sep %s" % self.DevID)
            if not self.read_complete():
                return False
                
            # final check whether the wafer prober is separated
            self.port.write(":move:cont? %s" % self.DevID)
            if self.port.read() == "TRUE":
                self.stop_Measurement("Separation did not succeed. Please take care to separate the contacts before "
                                      "you continue.")
                return False

    def apply(self):

        # print("New value to apply:", self.value)
        if not isinstance(self.value, str):
            self.stop_Measurement("Sweep value must be a string of the 'Die[<x>,<y>]_Sub[<subsite index>#<Label>]'")
            return False

        split_index = self.value.find("_Sub")
        
        # dies
        die_sweepvalue = str(self.value[:split_index])
        
        # format should be "Die<x>,<y>"
        # lets take the last string of the die related sweep value
        self.die_x, self.die_y = die_sweepvalue[4:-1].split(",")

        # subsites
        subsite_sweepvalue = str(self.value[split_index+1:])
        
        # format should be "Sub<index>-Label"
        # lets take the first string the subsite related sweep value and cut "Sub"
        self.current_subsite_index = subsite_sweepvalue[4:-1].split("#")[0]

        # if the wafer prober is still in contact, lets separate it
        self.port.write(":move:cont? %s" % self.DevID)
        if self.port.read() == "TRUE":
        
            # separate
            self.port.write(":mov:sep %s" % self.DevID)
            if not self.read_complete():
                return False
                
            # final check whether the wafer prober is separated
            self.port.write(":move:cont? %s" % self.DevID)
            if self.port.read() == "TRUE":
                self.stop_Measurement("Separation did not succeed. Please take care to separate the contacts before "
                                      "your continue")
                return False

        # move to new die xy and subsite
        self.port.write(':mov:prob:abs:loc %s %s %s' % (self.die_x, self.die_y, self.current_subsite_index))
        
        # not used anymore
        # self.port.write(':mov:prob:abs:ind:subs %i %i' % (int(self.current_die_testindex),
        #                                                   int(self.current_subsite_index)))
        # Manual:This command will move to a specified die and subsite,
        # using the testable die index and the numeric index for the subsite.
        
        if not self.read_complete():
            return False

        # contact
        self.port.write(":mov:cont %s" % self.DevID)
        if not self.read_complete():
            return False
        self.port.write(":mov:cont? %s" % self.DevID)
        if self.port.read() != "TRUE":
            self.stop_Measurement("Contacting did not succeed. Please take care to separate the contacts before "
                                  "you continue.")
            return False

        # Save new position to logbook file
        self.write_Log("Position %s reached" % str(self.value))

        # asking for the x,y coordinate indices of the die
        self.port.write(":mov:prob:abs:die?")
        die_xy = self.port.read()
        self.die_x = int(die_xy.split()[0])
        self.die_y = int(die_xy.split()[1])
        
        # asking for the real die index
        self.port.write(":mov:prob:abs:index?")
        self.die_real_index = self.port.read()

        # once we have arrived, we can ask for the current coordinates, these variable will be used to
        # display the coordinates in the GUI of the WaferProber module
        self.port.write(":mov:abs? %s" % self.DevID)
        coordinates = self.port.read()
        # print("Coordinates:", coordinates)
        self.current_x = float(coordinates.split()[0])/1000.0  # in mm
        self.current_y = float(coordinates.split()[1])/1000.0  # in mm
        self.current_z = float(coordinates.split()[2])/1000.0  # in mm

    def call(self):

        return [int(self.die_real_index),
                int(self.die_x),
                int(self.die_y),
                int(self.current_subsite_index),
                self.current_x,
                self.current_y,
                self.current_z,
                ]

    # here further convenience functions are defined

    def read_complete(self):
        # this function is used whenever 'COMPLETE' is expected as response
        # if the response is not 'COMPLETE', the measurement will be stopped and the error code is returned
        
        status = self.port.read()
        
        # print("read_complete status:", status)
        
        if status == "COMPLETE":
            return True
        else:
            debug(status)
            self.stop_Measurement(status)
            return False
