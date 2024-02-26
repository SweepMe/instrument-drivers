# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 Axel Fischer (sweep-me.net)
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
# Type: Switch
# Device: MBRAUN SCU101


from FolderManager import addFolderToPATH
addFolderToPATH()

import minimalmodbus
import numpy
import time

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!
# If you like to see the source code of EmptyDevice, take a look at the pysweepme package that contains this file

class Device(EmptyDevice):

    ## here you can add html formatted description to your device class that is shown by modules like 'Logger' or 'Switch' that have a description field.
    description =   """ no description yet  """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "SCU101" # short name will be shown in the sequencer
        self.variables = ["State"] # define as many variables you need
        self.units = [""] # make sure that you have as many units as you have variables
        self.plottype = [True]   # True to plot data, corresponding to self.variables
        self.savetype = [True]   # True to save data, corresponding to self.variables
        
        
        ### use/uncomment the next line to use the port manager
        #self.port_manager = True 
           
        ### use/uncomment the next line to let SweepMe! search for ports of these types. Also works if self.port_manager is False or commented.
        self.port_types = ["COM"]
        
        
        ## "<Name>" : (<Modbus  register>, <has digits>, <EI-Bisync mnemonic>)
        self.registers = {
                            "State": 0, # Modbus only
                            }
            
            
    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        # If you use this template to create a driver for modules other than Logger or Switch, you need to use fixed keys that are defined for each module.
        
        GUIparameter = {
                        "SweepMode": ["State", "None"],
                        }
        
        return GUIparameter

    def get_GUIparameter(self, parameter):

        self.sweepmode = parameter["SweepMode"]

        ### see all available keys you get from the GUI
        # print(parameter)
        
        ### get a value of a GUI item that was created by set_GUIparameter()
        # print(parameter["String"])
        # print(parameter["Check"])
        # print(parameter["Combo"])
        # print(parameter["Int"])
        # print(parameter["Float"])
        # print(parameter["Data path"])
        
        ### the port selected by the user is readout here and saved in a variable that can be later used to open the correct port
        self.port_string = parameter["Port"] # use this string to open the right port object later during 'connect'
        # print("Selected port", self.port_string) 
        
               
        ## Check which communication is selected ##
        
        if ":" in self.port_string:
            port_string_splitted = self.port_string.split(":")
                        
        else:
            port_string_splitted = self.port_string, ""
            
        self.com_port, self.address = port_string_splitted
        

    #### ----------------------------------------------------------------------------------------------------------------------
    """ here, semantic standard functions start that are called by SweepMe! during a measurement """
    ### all functions are overload functions that are called by SweepMe!
    ### remove those function that you do not needed
    
        
    def connect(self):

        if not self.address.isdigit():
            self.stop_Measurement("Please add the Modbus address to the COM port using the following syntax 'COM1:{address}', e.g. 'COM1:3'.")
            return False
        
        self.port = minimalmodbus.Instrument(self.com_port, int(self.address), close_port_after_each_call=False, debug = False)
                 
        ## self.port.serial is the underlying pyserial COM port object of minimalmodbus         
        self.port.serial.timeout = 2
        self.port.serial.baudrate = 19200
        self.port.serial.parity = 'E'
        #self.port.serial.bytesize = 8
        #self.port.serial.stopbits = 1
            
            
    def apply(self):

        if self.sweepmode == "State":
        
            if isinstance(self.value, int):
                if self.value >= 1:
                    set_state = 1
                else:
                    set_state = 0
                    
            elif isinstance(self.value, float):        
                if int(self.value) > 0:
                    set_state = 1
                else:
                    set_state = 0
                 
            elif isinstance(self.value, str):
                
                try:
                    set_state = int(self.value == "True" or self.value == "1" or self.value.lower() == "open" )
                except:
                    self.stop_Measurement("Unable to convert string '%s' to shutter state" % self.value)
                    return False
                    
            elif isinstance(self.value, bool):
                
                set_state = int(self.value)
                
            value = int("0000001%i" % set_state)  # the second bit is set to 1 to change the exectute flag and thus trigger the change.
            self.port.write_register(1, value, 0)
            self.set_state = set_state
    
    def adapt(self):
        
        if self.sweepmode == "State":
        
            while True:
                
                value = self.port.read_register(0, 0)
                
                print("adapt", value)
                
                state_value = value % 16

                if state_value == 0: # State unknown
                    pass
                    
                elif state_value == 1: # Open
                    if self.set_state == 1:
                        break
                
                elif state_value == 2: # Close
                    if self.set_state == 2:
                        break
                
                elif state_value == 3: # Moving
                    pass # Everything is alright, we just have to wait
                
                elif state_value == 4: # Not connected?
                    self.stop_Measurement("Unable to move the shutter as the controller is unable to connect to it.")
                    return False
                
                elif state_value == 5: # Blocked?
                    self.stop_Measurement("Unable to move the shutter as it is blocked.")
                    return False
                
                time.sleep(0.1)
            
            
    def measure(self):

        value = self.port.read_register(0, 0)
        
        print("measure:", value)
            
        state_value = value % 16
        

        if state_value == 1: # Open
            self.state = 1
        
        elif state_value == 2: # Close
            self.state = 0

    def call(self):
        
        return self.state
