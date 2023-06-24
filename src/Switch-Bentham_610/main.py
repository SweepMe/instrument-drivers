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
#
# Contribution: We like to thank TU Dresden/Jakob Wolanski for providing the initial version of this driver.


# SweepMe! device class
# Type: Switch
# Device: Bentham power supply unit 610

from EmptyDeviceClass import EmptyDevice  # SweepMe! base class

from ErrorMessage import error, debug

import FolderManager
FoMa = FolderManager.FolderManager()
FolderManager.addFolderToPATH()

# comes with libs folder
import hid
import bendev

class Device(EmptyDevice):

    description = """ 
        <p>Driver for Bentham Instruments Model PSU 610 Power control for lamp</p>
        <p>&nbsp;</p>
        <p><strong>Usage:</strong></p>
        <ul>
        <li>If Sweep mode is 'None', the value in the filed "Output current in A" will be used.&nbsp;</li>
        <li>If Sweep mode is 'Output current in A', the selected Sweep value will be used as source.</li>
        </ul>
        <p>&nbsp;</p>
        <p><strong>Known issues:</strong></p>
        <ul>
        <li>Reset burn time has no function.</li>
        </ul>
                  """

    def __init__(self):

        EmptyDevice.__init__(self)
        
        self.shortname = "Bentham 610"  # short name will be shown in the sequencer
        self.variables = ["Current", "Voltage", "Power", "Burn time"]  # define as many variables you need
        self.units = ["A", "V", "W", "h"]  # make sure that you have as many units as you have variables
        self.plottype = [True, True, True, True]  # True to plot data, corresponding to self.variables
        self.savetype = [True, True, True, True]  # True to save data, corresponding to self.variables

    def find_ports(self):
        ports = []

        for device_dict in hid.enumerate():
            if device_dict["manufacturer_string"] == "Bentham Instruments" or device_dict["vendor_id"] == "1240":
                if device_dict["product_string"] == "PSU_610":
                    ports.append(device_dict["serial_number"])
        return ports

    def set_GUIparameter(self):
    
        gui_parameter = {
                        "SweepMode": ["None", "Output current in A"],
                        "Output current in A": ["4", "5.4", "6.3", "8.5", "10.4"],  # Why discrete values?
                        "Turn lamp off after run": False,
                        "Reset burn time": False,
                        }
        return gui_parameter

    def get_GUIparameter(self, parameter):
        self.portstring = parameter["Port"]
        self.sweepmode = parameter["SweepMode"]
        self.output_current = parameter["Output current in A"]
        self.reset_burn_time = parameter["Reset burn time"]
        self.turn_lamp_off_after_run = parameter["Turn lamp off after run"]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):

        self.port = bendev.Device(serial_number=self.portstring)

    def initialize(self):

        pass
        # identifier = self.get_identification()
        # print("Identifier:", identifier)
        
    def deinitialize(self):
        pass

    def configure(self):

        # if self.sweepmode == "Output current":
        #     if self.output_current != "variable":
        #         raise Exception("If sweepmode Output current is selected, Output current needs to be variable")
        # else:
        #     if self.sweepmode == "None":
        #         if self.output_current == "variable":
        #             raise Exception("If Sweep mode is None, Output current needs to be a fixed current and not variable.")
        
        if self.reset_burn_time:
            raise Exception("If you really want to reset the burn time, continue.")
            #  self.port.write(":RESE:BUR")  # untested yet

        # Comment AF: Here I would set the current to zero before switching on except the sweep mode is None
        # In this case the fixed value could be set here
        if self.sweepmode == "None":
            self.port.write("SOUR:CURR " + str(self.output_current))
        else:
            self.port.write("SOUR:CURR 0.0")

    def poweron(self):
        # turn output on
        self.port.write(":OUTP ON")

    def unconfigure(self):
        pass

    def poweroff(self):

        if self.turn_lamp_off_after_run:
            # turn output off
            self.port.write(":OUTP OFF")

    def apply(self):

        value = float(self.value)

        # check whether self.value is in limits of PSU
        if (value <= 10.4) and (0 <= value):
            self.port.write("SOUR:CURR " + str(value))
        else:
            raise Exception("Requested supply current exceeds limit of Bentham PSU 610 output. "
                            "0-10.4A are available.")

        #turn output on
        # self.port.write(":OUTP ON")  #

    def measure(self):
        self.latest_voltage = self.port.query("VOLT?")
        self.latest_current = self.port.query("CURR?")
        self.latest_power = self.port.query("POWER?")
        self.latest_burn_time = self.port.query("FETC:BURN?")
        # test = self.port.query("OUTP?")

    def call(self):  
        return [float(self.latest_voltage),
                float(self.latest_current),
                float(self.latest_power),
                float(self.latest_burn_time)]

    """ here, python functions start that wrap the SCPI communication commands """

    def get_identification(self):
        
        answer = self.port.query("*IDN?")
        return answer

    def reset_burn_time(self):
        """
        reset the burn time of the lamp
        """
        self.port.write(":RESE:BUR")
