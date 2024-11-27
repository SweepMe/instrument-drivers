# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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

# Contribution: We like to thank Heliatek GmbH/Dustin Fischer for providing the initial version of this driver.


# SweepMe! driver
# * Module: Switch
# * Instrument: Power supply EA-PS 20xx


# use the next two lines to add the folder of this device class to the PATH variable
from FolderManager import addFolderToPATH
addFolderToPATH()

import ea_psu_controller

import time

from pysweepme.ErrorMessage import error, debug
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "EA Power supply"  # short name will be shown in the sequencer
        self.variables = ["Voltage", "Current"]  # define as many variables you need
        self.units = ["V", "A"]  # make sure that you have as many units as you have variables
        self.plottype = [True, True]  # True to plot data, corresponding to self.variables
        self.savetype = [True, True]  # True to save data, corresponding to self.variables

        self.port_manager = True
        self.port_types = ["COM"]

        self.port_properties = {
            "baudrate": 115200,
        }

    def set_GUIparameter(self):
    
        gui_parameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["1", "2"],
            "RouteOut": ["Front"],
            "Compliance": 1,
        }

        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):
        self.sweepmode = parameter["SweepMode"]
        self.channel = parameter["Channel"]
        self.protection = parameter["Compliance"]
        self.port_string = parameter["Port"]

    def connect(self):

        # function to monkey patch the PsuEA class to accept a SweepMe! COM port object
        def new_init(self, port):

            self._port = None
            self._baud = None

            self.psu = port  # here we use the SweepMe! COM por to overwrite the self.psu object
            self.__nom_voltage = 0.0
            self.__nom_current = 0.0
            self.__nom_power = 0.0
            self.__act_voltage = 0.0
            self.__max_current = 0.0
            self.__output1_connected = False
            self.__output2_connected = False

            # self.__find_devices(comport, sn, desi)

            #self.connect()
            self.get_config()

        def new_del(self):
            pass

        ea_psu_controller.PsuEA.__init__ = new_init  # where the monkey-patching happens
        ea_psu_controller.PsuEA.__del__ = new_del  # where the monkey-patching happens
        try:
            self.psu = ea_psu_controller.PsuEA(self.port.port)
        except ea_psu_controller.psu_ea.ExceptionTimeout:
            msg = "Unable to connect to EA PS2000 power supply"
            raise Exception(msg)

        self.channel = int(self.channel)-1

        self.psu.remote_on(self.channel)

    def initialize(self):

        desription = self.psu.get_device_description(self.channel)
        print("Description:", description)

    def deinitialize(self):

        if hasattr(self, "psu"):
            self.psu.remote_off(self.channel)

    def disconnect(self):
        pass

        # not needed anymore as we the SweepMe! COM port is closed by the port manager
        #self.psu.close(False, False)  # only close COM port
        
    def configure(self):

        # Compliance/Protection
        if self.sweepmode.startswith("Voltage"):
            self.psu.set_voltage(0, self.channel)
            self.psu.set_ocp(float(self.protection), self.channel)
        elif self.sweepmode.startswith("Current"):
            self.psu.set_current(0, self.channel)
            self.psu.set_ovp(float(self.protection), self.channel)

    def unconfigure(self):
        pass
        
    def poweron(self):
        self.psu.output_on(self.channel)

    def poweroff(self):
        self.psu.output_off(self.channel)

    def apply(self):

        if self.sweepmode.startswith("Voltage"):
            self.psu.set_voltage(float(self.value), self.channel)
        elif self.sweepmode.startswith("Current"):
            self.psu.set_current(float(self.value), self.channel)

    def measure(self):

        answer = self.psu.get_current(self.channel)
        self.i = float(answer)

        answer = self.psu.get_voltage(self.channel)
        self.v = float(answer)

    def call(self):
        return [self.v, self.i]
