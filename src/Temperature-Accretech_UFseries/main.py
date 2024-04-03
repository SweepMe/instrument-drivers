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

# SweepMe! device class
# Type: Temperature
# Device: Accretech UF series


from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

# standard import
# import accretech_uf
# importlib.reload(accretech_uf)

# direct import by path
import imp
import os

accretech_uf = imp.load_source(
    "accretech_uf", os.path.dirname(os.path.abspath(__file__)) + os.sep + r"libs\accretech_uf.py",
)

# this is needed as a fallback solutions as pysweepme.UserInterface is not available for all 1.5.5 update versions
try:
    from pysweepme.UserInterface import message_box
except ModuleNotFoundError:
    message_box = print
    print(
        "Accretech driver: Please use the latest version of SweepMe! to use this "
        "driver to display a message box. "
        "Fallback to 'print' method.",
    )


class Device(EmptyDevice):
    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Accretech"
        self.variables = ["Wafer ID", "Wafer", "Die x", "Die y", "X", "Y"]
        self.units = ["", "", "", "", "", ""]  # unit of X and Y is either µm or inch, depending on system settings
        self.plottype = [False, True, True, True, True, True]
        self.savetype = [True, True, True, True, True, True]

        self.port_manager = True
        self.port_types = ["GPIB"]
        self.port_properties = {
            "timeout": 5,  # only for write&read messages, SRQ&STB commands have own timeout
            "GPIB_EOLwrite": "\r\n",
            "GPIB_EOLread": "\r\n",
        }

        # self.actual_wafer_text = ""
        # self.actual_die_text = ""
        # self.actual_subsite_text = "Not available"
        # self.actual_xpos = "Not available"
        # self.actual_ypos = "Not available"

        self.verbosemode = True

    def set_GUIparameter(self):
        gui_parameter = {
            "SweepValueWafer": "Wafer table",
            "SweepValueDie": "Die table",
            "SweepValueSubsite": "Subsite table",
        }
        return gui_parameter

    def get_GUIparameter(self, parameter):
        self.sweep_value_wafer = parameter["SweepValueWafer"]
        self.sweep_value_die = parameter["SweepValueDie"]
        self.sweep_value_subsite = parameter["SweepValueSubsite"]

    def connect(self):
        # creating an AccretechProber instance that handles all communication
        self.prober = accretech_uf.AccretechProber(self.port)
        self.prober.set_verbose(self.verbosemode)

    def disconnect(self):
        del self.prober  # this makes sure the event mechanism is disabled

    def initialize(self):
        self.print_info()

        self.print_status()

        self.prober.reset_alarm()

    def deinitialize(self):
        pass

    def configure(self):
        pass

    def unconfigure(self):
        pass

    def apply(self):
        pass

    def call(self):
        return [
            self.last_wafer_id,
            self.last_wafer_str,
            self.die_x,
            self.die_y,
            self.last_position[0],
            self.last_position[1],
        ]
