2# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)

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


# Contribution: We like to thank TU Dresden (Toni Bärschneider and Jakob Wolansky) for providing the initial version of this driver.

# SweepMe! device class
# Type: Monochromator
# Device: Quantum Design MSH-300

import time
import ctypes
import os
import sys
import numpy as np
import struct
import glob
import pathlib

from collections import OrderedDict

import FolderManager
FoMa = FolderManager.FolderManager()
FolderManager.addFolderToPATH()

from EmptyDeviceClass import EmptyDevice

import lotcontrol # comes with libs folder

class Device(EmptyDevice):

    description = """
                    <p><strong>Keywords:&nbsp;</strong>LOT</p>
                    <p><strong>Models:&nbsp;</strong>MSH-300, MSH-150,&nbsp;MSH-300F, MSH-150F</p>
                    <p>&nbsp;</p>
                    <p><strong>Image:</strong></p>
                    <p><strong><img src="https://wiki.sweep-me.net/images/9/97/Monochromator-MSH-300.png" alt="Quantum Design MSH-300 monochromator" width="400" height="400" /><br /></strong></p>
                    <p><em>MSH-300 monochromator from Quantum Design (former LOT)</em></p>
                    <p>&nbsp;</p>
                    <p><strong>Requirements:</strong></p>
                    <ul>
                    <li>Your .xml configuration file that came with the monochomator must be copied to the public SweepMe! folder "CalibrationFiles"<br />You can create subfolders to organize multiple calibration files. The configuration file names must contain "SN" to be identified.</li>
                    </ul>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Use 'Find Ports' button to list all .xml configuration files.</li>
                    <li>Select the .xml configuration file of your monochromator. If you have multiple monochromators, you can distinguish them by the serial number in the file name.</li>
                    <li>The monochromator automatically changes grating and filters when the wavelength changes according to the .xml configuration file. A custom change of grating and filter is not possible, yet.</li>
                    <li>To sweep wavelengths, select "Wavelength in nm" as Sweep mode.</li>
                    <li>If Sweep mode is "None", the wavelength in the section Parameters is used.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Contribution:</strong></p>
                    <p>We like to thank TU Dresden/Toni B&auml;rschneider for providing the initial version of this driver.</p>
                  """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "MSH-300"
        
        self.variables = ["Wavelength", "Energy", "Filter", "Grating"]
        self.units = ["nm", "eV", "#", "#"]
        self.plottype = [True, True, True, True]  # True to plot data
        self.savetype = [True, True, True, True]  # True to save data
      
        self.calibrationsfolder = FoMa.get_path("CALIBRATIONS")
        
        self.LotDLL = None

        self.filters = [
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        ]

        # We add filter strings from the config file in CustomFiles
        filters_to_add = self.getConfigOptions("Filter")
        for key in filters_to_add :
            self.filters.append(filters_to_add[key])
                        
        self.gratings = [
                         "1",
                         "2",
                         "3", 
                         ]
                         
        gratings_to_add = self.getConfigOptions("Grating")
        for key in gratings_to_add :
            self.gratings.append(gratings_to_add[key])

        self.inport = OrderedDict([
                            ("Axial", 2),
                            ("Lateral", 1),
                            ])

        self.outport = OrderedDict([
                            ("Axial", 2),
                            ("Lateral", 1),
                            ])

        self.slitinputs = OrderedDict([
                            ("Axial", 2),
                            ("Lateral", 3),
                            ])

        self.slitoutputs = OrderedDict([
                            ("Axial", 2),
                            ("Lateral", 3),
                            ])


    def set_GUIparameter(self):

        gui_parameter = {
                         "SweepMode": ["Wavelength in nm", "Energy in eV", "None"],  # "Reflection (zero order)", "Slitwidth [µm]" needs additional fix wavelength option
                         "EndPosition": "",
                         "Input" : list(self.slitinputs.keys()),
                         "Output" : list(self.slitoutputs.keys()),
                         "Filter": ["Auto"] + self.filters,
                         "Grating": ["Auto"] + self.gratings,
                         # "SlitOutput": ["2000 (max)", "1500", "6 (min)"],
                         # "SlitInput": ["2000 (max)", "1500", "6 (min)"],
                         "Wavelength": "550",
                        }
        return gui_parameter
            
    def get_GUIparameter(self, parameter={}):
            
        self.sweep_mode = parameter["SweepMode"]
        self.xml_file = parameter["Port"]
        
        # Wavelength
        self.wavelength = parameter["Wavelength"]
        self.end_position = parameter["EndPosition"]

        # Filter
        self.filter = parameter["Filter"]

        # Grating
        self.grating = parameter["Grating"]

        # Input port
        self.input = parameter["Input"]
        
        # Output port
        self.output = parameter["Output"]
    
    def find_ports(self):

        lot_calibration_files = pathlib.Path(self.calibrationsfolder).rglob("*SN*.xml")  #generator of all files including subfolders
        length = len(self.calibrationsfolder)+1
        ports = [str(f)[length:] for f in lot_calibration_files if f.is_file()]
        
        if len(ports) == 0:
            self.message_Box("No calibration files found!\n\n"\
                             "Please put the .xml configuration file that came with your monochromator "\
                             "into the public SweepMe! folder 'CalibrationFiles'. "\
                             "Files must contain 'SN' to be found. Subfolders are allowed."
                             )

        return ports
    
    def connect(self):
        if sys.maxsize > 2**32:# 64bit system
            dllpath = self.get_folder("SELF").replace(os.sep + "main.py", "") + os.sep + r"libs\LotHW64.dll" #replace: in old sweepMe version self.get_folder("SELF") ended up at main.py
        else: #32 bit system
            dllpath = self.get_folder("SELF").replace(os.sep + "main.py", "") + os.sep + r"libs\LotHW_stdcall.dll" #replace: in old sweepMe version self.get_folder("SELF") ended up at main.py

        key="QuantumDesignMSH-300_DLL_LotControl"
        
        self.monochromator = self.restore_parameter(key)
        if not self.monochromator:
            self.monochromator = lotcontrol.LotControl(configuration_file = self.calibrationsfolder + os.sep + self.xml_file, dllpath = dllpath, verbosity=lotcontrol.ERROR)
            self.store_parameter(key, self.monochromator)
            # print("DLL instance in parameter store")
        else:

            if self.wavelength != "":
                value_c_double = ctypes.c_double(float(self.wavelength)) 
            else:
                value_c_double = ctypes.c_double(550.0)
                
            success = self.monochromator.dll.LOT_select_wavelength(value_c_double)
            
            # print("Success after selecting wavelength:", success)
            
            if success != 0:
                self.monochromator.connect()
                self.monochromator.initialise()

        ## get the number of turrets
        self.number_turrets = 2
    
    def disconnect(self):
        pass
        # self.monochromator.close()
        
    def initialize(self):
        if self.end_position != "":
            self.end_position = float(self.end_position)

    def deinitialize(self):
        if self.end_position != "":
            self.set_wavelength(self.end_position)

    def configure(self):
        self.set_sam_switch_wlns() #set sam options
        self.set_input_port(self.input)
        self.set_output_port(self.output)

        #use posibility to write switching wavelengths for grating and filter to monochromator
        
        if self.grating != "Auto":
            self.set_grating_switch_wlns()  #set grating options
        if self.filter != "Auto":
            self.set_fwheel_switch_wlns()  #set fwheel options
        
        if self.sweep_mode == "None":
            if self.wavelength != "":
                wavelength_to_set = round(float(self.wavelength),3)
                self.set_wavelength(wavelength_to_set)
            else:
                raise Exception("Please define a constant wavelength if Sweep mode is None.")


    
    def apply(self):
        if self.sweep_mode.startswith("Wavelength"):
            print(type(self.value), self.value)
            # if self.value is below than 10, it's probably an energy and not a wavelength
            if float(self.value) < 10:
                raise Exception("Check sweepmode. Wavelength expected, but probably energy received.")
            # Based on the wavelength the grating and the filter will be chosen automatically
            self.set_wavelength(self.value)
        elif self.sweep_mode.startswith("Energy"):
            if float(self.value)>100:
                self.set_wavelength(self.value)
            else:
                wavelength_to_set = round(float(4.135667e-15*2.99792e8/(float(self.value)))*1e9,3) # conversion from eV to nm
                self.set_wavelength(wavelength_to_set)   


    def measure(self):
        self.current_wavelength = self.get_wavelength()
        self.current_grating = int(self.get_grating_pos())
        self.current_filter = self.get_fwheel_pos()

        if self.current_wavelength > 0.0:
            self.current_energy = 1239.41974/self.current_wavelength
        else:
            self.current_energy = float('nan')

    def call(self):
        return [self.current_wavelength, self.current_energy, self.current_filter, self.current_grating]

    """ Start of command wrapping functions """

    def set_input_port(self, value):
        if value == "Axial":
            val_id = 1
        else:
            val_id = 0
        self.monochromator.set("sam1", SAMInitialState, val_id)
        self.monochromator.get("sam1", SAMInitialState)  # probably needed to arrive at the new port

    def set_output_port(self, value):
        if value == "Axial":
            val_id = 1
        else:
            val_id = 0
        self.monochromator.set("sam2", SAMInitialState, val_id)
        self.monochromator.get("sam2", SAMInitialState)  # probably needed to arrive at the new port

    def get_wavelength(self):
        wavelengthOfEachTurret = []
        for k in range(1,self.number_turrets + 1):
            wavelengthOfEachTurret.append(float(self.monochromator.get("mono", MonochromatorCurrentWL, k*10+1)))
        if not all(element == wavelengthOfEachTurret[0] for element in wavelengthOfEachTurret):
            raise Exception("Wavelength of turret1 and turret2 differ!")
        return wavelengthOfEachTurret[0]

    def set_wavelength(self, wl):
        success = self.monochromator.select_wavelength(float(wl))
        return success

    def get_grating_pos(self):
        gratingOfEachTurret = []
        for k in range(1,self.number_turrets + 1):
            gratingOfEachTurret.append(int(self.monochromator.get("mono", MonochromatorCurrentGrating, k*10+1)))
        if not all(element == gratingOfEachTurret[0] for element in gratingOfEachTurret):
            raise Exception("Grating of turret1 and turret2 differ!")
        return gratingOfEachTurret[0]

    def get_fwheel_pos(self):
        fwheel_name = "fwheel"
        return int(self.monochromator.get(fwheel_name, FWheelCurrentPosition, 0))


    """

    # not needed and not properly working 
    def set_fwheel_pos(self, value):
        if not 0<value<=6:
            print('invalid filter wheel index')
            return
        val_f = int(value)
        self.monochromator.set("fwheel", FWheelCurrentPosition, 1, val_f) 
        
    def set_grating_pos(self, value):
        ## if you want to set grating manually, you also need to change the wavelength afterwards, otherwise the turret will not move
        val_f = float(value)
        self.set_auto_grating(0) # deactivate auto selection of grating
        for k in range(1,self.number_turrets + 1):
            print("tempIndex", k*10+value)
            self.monochromator.set("mono", MonochromatorCurrentGrating, k*10+1, val_f) 
        # here the current wavelength is received
        self.current_wavelength = self.get_wavelength()
        self.set_wavelength(self.current_wavelength)

    """




    def unconfigure(self):
        self.close_shutter()

    def close_shutter(self):
        ''' close the shutter '''
        # self.set_fwheel_pos(6)
        print("close_shutter")
        self.monochromator.set("fwheel", FWheelCurrentPosition, 6, 0)


    def set_auto_grating(self, state):
        """
        state: True or False
        """
        value_i = int(state)
        index = 11
        self.monochromator.set("mono", MonochromatorAutoSelectWavelength, index, value_i)

    def set_fwheel_switch_wlns(self):
        ''' set the start wln of each filter in increasing list. 
        position 6 corresponds to shutter, positions with switch value of 0 are not used.
        e.g. [0, 400, 600, 700, 800, 0] corresponding to open, long pass filters and shut
        
        This does not permantly edit the attr file'''

        ### is not working for filter
        ## if only 1 grating should be used, then add the following switching wavelengths
        
        
        self.filter_readout = self.filter.replace("<", "").replace(">", "").replace("nm", "").replace(" ", "").split("-")
        self.filter_list = np.array(self.filter_readout[::2], dtype = int)
        self.filter_wavelengths = np.array(self.filter_readout[1::2], dtype = float)
        
        ## only, if set_fwheel_switch_wlns is used in configure
        self.filter_wavelengths = np.insert(self.filter_wavelengths, 0, 0.0) #blank position
        self.filter_wavelengths = np.append(self.filter_wavelengths, 0.0) #shutter
        
        
        # if only one filter is specified, we overwrite the filter_wavelengths
        if len(self.filter_list) == 1:
            
            highWvl = 10000
            
            self.filter = int(self.filter)
            
            if self.filter > 0 and self.filter < 7:
                self.filter_wavelengths = [0] * (self.filter-1) + [1] + [highWvl] * (6-self.filter)
            else:
                raise Exception("Filter index is not valid")  
                
            self.filter_list = [1, 2, 3, 4, 5, 6]
        
        for number, wln in zip(self.filter_list, self.filter_wavelengths):
            # print("filternumber", number, "wln", wln)
            self.monochromator.set("fwheel", FWheelFilter, wln, int(number))            

    def set_grating_switch_wlns(self):
        ''' set the start wln of each grating in increasing list. 
        e.g. [0, 600, 1200]
        
        This does not permantly edit the attr file'''
        
        self.grating_readout = self.grating.replace("<", "").replace(">", "").replace("nm", "").replace(" ", "").split("-")
        self.grating_list = np.array(self.grating_readout[::2], dtype = int)
        self.grating_wavelengths = np.array(self.grating_readout[1::2], dtype = float)
        self.grating_wavelengths = np.insert(self.grating_wavelengths, 0, 0.0)  #first grating from 0 nm
        
        # print("self.grating_list", self.grating_list, "self.grating_wavelengths", self.grating_wavelengths)
        
        # if only 1 grating should be used, then add the following switching wavelengths
        if len(self.grating_list) == 1:
            highWvl = 10000
            if self.grating == "1":
                self.grating_wavelengths = [0, highWvl, highWvl]
            elif self.grating == "2":
                self.grating_wavelengths = [0, 0, highWvl]
            elif self.grating == "3":
                self.grating_wavelengths = [0, 0, 0]
            else:
                raise Exception("Grating index is not valid")
            self.grating_list = [1, 2, 3]  #for the next for loop important
            
        # print("self.grating_wavelengths", self.grating_wavelengths)
        for k in range(1,self.number_turrets + 1):
            """for i, wln in enumerate(self.grating_wavelengths):
                print("i", i, "wln", wln)
                tempIndex = k*10 + (i+1)
                print("tempIndex", tempIndex, type(tempIndex))
                self.monochromator.set("mono", GratingSwitchWL, wln, tempIndex)"""
            for number, wln in zip(self.grating_list, self.grating_wavelengths):
                # print("Number", number, "wln", wln)
                tempIndex = k*10 + int(number)
                # print("tempIndex", tempIndex, type(tempIndex))
                self.monochromator.set("mono", GratingSwitchWL, wln, tempIndex)

    def set_sam_switch_wlns(self):
        ''' set the start wln of each grating in increasing list. 
        e.g. [0, 600, 1200]
        
        This does not permantly edit the attr file'''
        ## if only 1 grating should be used, then add the following switching wavelengths
        highWvl = 10000
        self.monochromator.set("sam1", SAMSwitchWL, highWvl, 1) #index should be 1 (compare with xml file)
        self.monochromator.set("sam2", SAMSwitchWL, highWvl, 1) #index should be 1 (compare with xml file)


#-----------------------------------------------------------------------------

# DLL Tokens below are taken from DLLTOKEN.txt that is shipped with this driver
# Please have at the top of this file regarding the license and copyright information.

#-----------------------------------------------------------------------------
# Monochromator attributes
#-----------------------------------------------------------------------------
MonochromatorScanDirection = 10
MonochromatorCurrentWL = 11
MonochromatorCurrentGrating = 12
MonochromatorInitialise = 13
MonochromatorModeSwitchNum = 14
MonochromatorModeSwitchState = 15
MonochromatorCanModeSwitch = 16
MonochromatorAutoSelectWavelength = 17
MonochromatorZordSwitchSAM = 18
MonochromatorNumTurrets = 19
MonochromatorCosAlpha = 21
  
TurretNumGratings = 20

GratingDensity = 30
GratingZord = 31
GratingAlpha = 32
GratingSwitchWL = 33
GratingBlaze = 34

#-----------------------------------------------------------------------------
# Filter wheel attributes
#-----------------------------------------------------------------------------
FWheelFilter = 100
FWheelPositions = 101
FWheelCurrentPosition = 102

#-----------------------------------------------------------------------------
# SAM attributes
#-----------------------------------------------------------------------------
SAMInitialState = 300
SAMSwitchWL = 301
SAMState = 302
SAMCurrentState = 303
SAMDeflectName = 304
SAMNoDeflectName = 305
