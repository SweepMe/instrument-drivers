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

# SweepMe! device class
# Type: Switch
# Device: Labjack T-series

import imp
import os

# adding the libs folder to path is needed so that the BaseClass can find the labjack ljm package
from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

main_path = os.path.dirname(os.path.abspath(__file__))
driver_name = os.path.basename(main_path)

# We assign a module name that depends on the driver name to make sure each driver imports its own version
# of the Base class as this reduces friction when SweepMe! labjack drivers use different versions of the base class.
Labjack_T_Series_BaseClass = imp.load_source("Labjack_T_Series_BaseClass_" + driver_name,
                                             main_path + os.sep + "Labjack_T_Series_BaseClass.py")

html_docu = imp.load_source("html_docu" + driver_name, main_path + os.sep + "html_docu.py")


class Device(Labjack_T_Series_BaseClass.LabjackBaseClass):
    """ the Class that will be used by the switch module to control the instrument.
        Only semantic functions are called by SweepMe!"""

    description = html_docu.html_driver_descript

    def __init__(self):
        super().__init__()

        self.shortname = "Labjack Tx Counter"  # short name will be shown in the sequencer
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        self.parameters = {}
        self.output_highs = []
        self.output_lows = []

    def set_GUIparameter(self):

        GUIparameter = {
            "Counter read pins": "CIO1, CIO2",
            "Count time s": 1.0,
            "": None,
            "Bus time correction in s": 30e-6,
            "Override clock": True
        }
        # "Prevent overwrite of Output by read/analogue"
        return GUIparameter

    def get_GUIparameter(self, parameter):
        """ parse and store GUI options"""

        port_string: str = parameter["Port"]  # "TX:SN"
        try:
            serial_number = int(port_string.split(":SN")[-1])
        except ValueError:
            serial_number = None
        self.parameters["serial number"] = serial_number

        counter_pins: str = parameter["Counter read pins"]
        self.counter_pins = counter_pins.replace(" ", "").split(",")
        if self.counter_pins == [""]:
            self.counter_pins = []
        if not self.counter_pins:
            raise ValueError("Please specify counter pins or disable logger")

        self.variables = self.counter_pins
        self.units = [""] * len(self.variables)

        self.count_time = float(parameter["Count time s"])
        self.bus_correction = float(parameter["Bus time correction in s"])
        self.override_clock = bool(parameter['Override clock'])

    def configure(self):
        # CIOxxx not accepted by counter & EF pin set commands. Translate
        translation = Labjack_T_Series_BaseClass.ljm_constants.EF_DIO_NAMES[self.dev_type]  # CIO-->DIO
        self.counter_pins = [
            pin if pin not in translation else translation[pin] for pin in self.counter_pins
        ]
        self.set_pins_to_hs_counter(self.counter_pins, override_clock=self.override_clock)

    def call(self):
        """
        """
        return list(self.results)

    def measure(self):

        self.results = self.read_counter_pins(count_time=self.count_time,
                                              bus_correction=self.bus_correction)
