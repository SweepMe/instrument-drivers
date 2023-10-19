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
# Device: Labnack T-series

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

        self.shortname = "Labjack TTL"  # short name will be shown in the sequencer
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

        self.parameters = {}
        self.output_pins = []
        self.initial_state = None
        self.final_state = None

    def set_GUIparameter(self):

        GUIparameter = {
            "Output pins": "EIO0, CIO1",
            "State (start)": ["High", "Low"],
            "State (end)": ["High", "Low"],
            "SweepMode": ["None", "Output"]
        }
        # "Prevent overwrite of Output by read/analogue"
        return GUIparameter

    def get_GUIparameter(self, parameter):
        """ parse and store GUI options"""

        port_string = parameter["Port"]  # "TX:SN"
        try:
            serial_number = int(port_string.split(":SN")[-1])
        except ValueError:
            serial_number = None
        self.parameters["serial number"] = serial_number

        pins = parameter["Output pins"].replace(" ", "")
        self.output_pins = pins.split(",") if pins else []

        self.initial_state = 1 if parameter["State (start)"] == "High" else 0
        self.final_state = 1 if parameter["State (end)"] == "High" else 0

        self.sweepmode = parameter["SweepMode"]
        self.variables = self.output_pins
        self.units = [""] * len(self.variables)

    def configure(self):

        if self.initial_state:
            pins_high = self.output_pins
            pins_low = []
        else:
            pins_low = self.output_pins
            pins_high = []
        self.set_digital_IO(pin_names_high=pins_high, pin_names_low=pins_low, pins_names_inputs=[])

    def call(self):
        """
        """
        pin_states = self.read_DIO_states()
        pin_names = self.output_pins
        return [pin_states[pin_name] for pin_name in pin_names]

    def apply(self):

        allowed = [1, 0, "High", "Low", "1", "0"]

        if self.sweepmode == "Output":
            output_state = self.value
            if output_state in [1, "High", "1"]:
                self.set_digital_IO(pin_names_high=self.output_pins,
                                    pin_names_low=[],
                                    pins_names_inputs=[])
            elif output_state in [0, "Low", "0"]:
                self.set_digital_IO(pin_names_high=[],
                                    pin_names_low=self.output_pins,
                                    pins_names_inputs=[])
            else:
                raise ValueError(f"Invalid output state {output_state} not in allowed {allowed}")

    def unconfigure(self):

        if self.final_state:
            pins_high = self.output_pins
            pins_low = []
        else:
            pins_low = self.output_pins
            pins_high = []
        self.set_digital_IO(pin_names_high=pins_high, pin_names_low=pins_low, pins_names_inputs=[])
