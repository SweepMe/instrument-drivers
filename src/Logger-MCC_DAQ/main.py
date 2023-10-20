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

# Contribution: We like to thank TU Dresden/Shayan Miri for providing the initial version of this driver.

# SweepMe! device class
# Type: Logger
# Device: Measurement Computing Corporation DAQ devices

from pysweepme import addFolderToPATH
from pysweepme.ErrorMessage import error, debug
from pysweepme.EmptyDeviceClass import EmptyDevice

addFolderToPATH()

from mcculw.enums import ScanOptions, FunctionType, Status, AnalogInputMode, InterfaceType


class Device(EmptyDevice):

    description = """
                  To use this driver, installation of MCC DAQ Software, including Universal Library™ is needed. 
                  Please download it here: https://www.mccdaq.com/Software-Downloads
                  """
    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "MCC-DAQ"  # short name will be shown in the sequencer
        self.variables = []
        self.units = []

        self.port_manager = False

        self.board_num = 0  # only fixed board 0 supported at the moment

        self.data = []  # object to store results before they are returned in 'call'

    def set_GUIparameter(self):

        gui_parameter = {
            "Analog input mode": AnalogInputMode._member_names_,
            "Analog inputs": "1, 2",
        }
        return gui_parameter

    def get_GUIparameter(self, parameter):
        """ parse and store GUI options"""
        self.port_string = parameter["Port"]
        self.analog_input_mode = parameter["Analog input mode"]
        self.analog_inputs_list = parameter["Analog inputs"].split(",")
        self.analog_inputs = [int(s.strip()) for s in self.analog_inputs_list]

        for i in range(len(self.analog_inputs)):
            self.variables.append("AI%d" % self.analog_inputs[i])
            self.units.append("V")

    def find_ports(self):

        self.import_mcculw()

        ul.ignore_instacal()
        ul.release_daq_device(self.board_num)

        device_list = self.create_device_list()

        if len(device_list) > 0:
            return device_list
        else:
            return ["No device was found"]

    def connect(self):

        self.import_mcculw()

        ul.ignore_instacal()

        inventory = ul.get_daq_device_inventory(InterfaceType.ANY)
        device_list = self.create_device_list()

        if self.port_string in device_list:
            self.descriptor = inventory[device_list.index(self.port_string)]
        elif self.port_string == "No device was found":
            msg = "Please use 'Find Ports' and select a valid port to continue."
            raise Exception(msg)
        else:
            msg = "Selected port was not found. Please use 'Find ports' and check whether the port still exists."
            raise Exception(msg)

        ul.create_daq_device(self.board_num, self.descriptor)
        ul.flash_led(self.board_num)

    def disconnect(self):
        ul.release_daq_device(self.board_num)

    def initialize(self):
        # Set input mode
        ul.a_input_mode(self.board_num, AnalogInputMode[self.analog_input_mode])

        daq_dev_info = DaqDeviceInfo(self.board_num)
        if not daq_dev_info.supports_analog_input:
            msg = "The DAQ device does not support analog inputs."
            raise Exception(msg)
        self.ai_info = daq_dev_info.get_ai_info()

        # print("Number of analog inputs:", self.ai_info.num_chans)

    def measure(self):

        ai_range = self.ai_info.supported_ranges[0]  # fixed range so far

        self.data = []

        for ai in self.analog_inputs:

            # Get a value from the device
            if self.ai_info.resolution <= 16:
                # Use the a_in method for devices with a resolution <= 16
                value = ul.a_in(self.board_num, ai, ai_range)
                # Convert the raw value to engineering units
                eng_units_value = ul.to_eng_units(self.board_num, ai_range, value)
            else:
                # Use the a_in_32 method for devices with a resolution > 16
                # (optional parameter omitted)
                value = ul.a_in_32(self.board_num, ai, ai_range)
                # Convert the raw value to engineering units
                eng_units_value = ul.to_eng_units_32(self.board_num, ai_range, value)

            # print("value for input %d:" % i, eng_units_value)
            self.data.append(eng_units_value)

    def call(self):
        return self.data

    def import_mcculw(self):

        try:
            from mcculw import ul
            from mcculw.ul import ULError
            from mcculw.device_info import DaqDeviceInfo
        except:
            error("Unable to import mcculw library for MCC DAQ driver. Make sure the MCC DAQ Software, "
                  "including Universal Library™ is installed.")

    def create_device_list(self):

        device_list = []
        inventory = ul.get_daq_device_inventory(InterfaceType.ANY)
        if len(inventory) > 0:
            for device in inventory:
                device_list.append(str(device) + "_" + device.unique_id)

        return device_list
