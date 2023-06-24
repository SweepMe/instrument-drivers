# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022-2023 SweepMe! GmbH (sweep-me.net)
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
# Device: Accretech UF series

import importlib
from typing import List, Tuple
import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

# standard import
# import accretech_uf
# importlib.reload(accretech_uf)

# direct import by path
import imp
import os
accretech_uf = imp.load_source("accretech_uf", os.path.dirname(os.path.abspath(__file__)) +
                               os.sep + r"libs\accretech_uf.py")


# this is needed as a fallback solutions as pysweepme.UserInterface is not available for all 1.5.5 update versions
try:
    from pysweepme.UserInterface import message_box
except ModuleNotFoundError:
    message_box = print
    print("Accretech driver: Please use the latest version of SweepMe! to use this "
          "driver to display a message box. "
          "Fallback to 'print' method.")


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

    def get_probeplan(self, probeplan_path):
        # important function to retrieve the probe plan before the measurement starts,

        # Wafers
        wafer_status = self.prober.request_wafer_status()
        # a list of tuples containing cassette and wafer id
        wafer_list = self.prober.get_waferlist_from_status(wafer_status)

        if len(wafer_list) == 0:
            self.prober.sense_wafers()  # Wafer sensing "jw" command

            wafer_status = self.prober.request_wafer_status()
            # a list of tuples containing cassette and wafer id
            wafer_list = self.prober.get_waferlist_from_status(wafer_status)

            if len(wafer_list) == 0:
                debug("Empty wafer list, please make sure the cassette is filled and "
                      "you have sensed the wafer before you try again.")

        wafers = [f"C{i}W{j}" for i, j in wafer_list]

        # Dies
        die_list = self.read_controlmap(probeplan_path)
        dies = die_list

        # Subsites
        subsites = []  # Subsites cannot be defined via file or loaded from the wafer

        # Name
        probeplan_name = "..." + probeplan_path[-15:]

        return wafers, dies, subsites, probeplan_name

    def get_current_wafer(self):
        """
        function is used by the WaferProber module to get the current wafer
         before the run starts in case the sweep values "Current Wafer" is used.
        """

        if self.prober.is_wafer_on_chuck:
            cassette, slot = self.prober.request_cassette_slot()
            current_wafer = f"C{cassette}W{slot}"
        else:
            current_wafer = ""

        return current_wafer

    def get_current_die(self):
        """
        function is used by the WaferProber module to get the current die before the
        run starts in case the sweep value "Current Die" is used.
        """

        if self.prober.is_wafer_on_chuck:
            die_x, die_y = self.prober.request_die_coordinate()
            current_die = f"{die_x},{die_y}"
        else:
            current_die = ""

        return current_die

    def get_current_subsite(self):
        """
        function is used by the WaferProber module to get the current subsite before the run
         starts in case the sweep value "Current Subsite" is used.
        """

        current_subsite = ""

        return current_subsite

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

        if self.sweep_value_wafer == "Current wafer":
            if not self.prober.is_wafer_on_chuck():
                raise Exception(
                    "There is no wafer on the chuck, although 'Current wafer' is selected as Sweep value."
                )
        else:
            if self.prober.is_wafer_on_chuck():
                raise Exception(
                    "There is already a wafer on the chuck. Please terminate the ongoing lot process or "
                    "remove the wafer.")

            if self.sweep_value_die == "Current die":
                raise Exception(
                    "Performing a wafer variation for the current die is not possible as the current die is"
                    "not defined when no wafer is on the chuck.")

            if self.sweep_value_die == "Current die":
                raise Exception(
                    "Performing a wafer variation for the current die is not possible as the current die is"
                    "not defined when no wafer is on the chuck.")

            cassette_status = self.prober.request_cassette_status()
            if cassette_status == "000000":
                self.prober.sense_wafers()  # Wafer sensing "jw" command

            # Get cassettes and wafers
            wafer_status = self.prober.request_wafer_status()
            # a list of tuples containing cassette and wafer id
            wafer_list = self.prober.get_waferlist_from_status(wafer_status)

            if len(wafer_list) == 0:
                self.prober.sense_wafers()  # Wafer sensing "jw" command

                wafer_status = self.prober.request_wafer_status()
                # a list of tuples containing cassette and wafer id
                wafer_list = self.prober.get_waferlist_from_status(wafer_status)

                if len(wafer_list) == 0:
                    raise Exception("Empty wafer list, please make sure the cassette is filled and "
                                    "you have sensed the wafer before you try again.")

        if self.sweep_value_subsite == "Current subsite":
            raise Exception("Option 'Current subsite' is not supported yet.")

    def deinitialize(self):
        pass

    def configure(self):

        self.last_wafer = None
        self.last_wafer_str = ""
        self.last_wafer_id = None

        self.last_die = None
        self.last_die_str = ""

        self.last_sub_str = None
        self.last_sub = (0, 0)

        # absolute position of the current die starting position
        self.current_die_position = (None, None)

        # last absolute position
        self.last_position = (None, None)

    def unconfigure(self):

        # Chuck down
        self.prober.z_down()

        if self.sweep_value_wafer != "Current wafer":
            # Terminating the lot process bringing all wafers back to cassette
            if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                message_box("Lot process will be finished which takes 1-2 minutes.\n\n"
                            "Do not terminate the run and please wait until the program finishes."
                            "You can close this message when the run has completed normally.")

            self.prober.terminate_lot_process_immediately()

    def apply(self):

        # print()
        # print("New setvalue to apply:", self.value)
        # print(self.sweepvalues)

        # self.skip_wafer handed over from WaferProber module when user clicks "Go to next wafer"
        if self.skip_wafer:
            return

        wafer_str = self.sweepvalues["Wafer"]
        die_str = self.sweepvalues["Die"]
        subsite_str = self.sweepvalues["Subsite"]
        die = die_str.split(",")  # create a list of x and y coordinates, e.g "1,3" -> [1,3]
        preload_wafer_str = self.sweepvalues["NextWafer"]

        if wafer_str is None:
            raise Exception(
                "You need to specify at least one wafer or use 'Current wafer' as sweep value!")

        if die_str is None:
            raise Exception(
                "You need to specify at least one die or use 'Current die' as sweep value!")

        # We do not check whether subsites are None because in that case no subsite was defined and the prober
        # stays at the start position of the die

        # only if we vary the wafer, we need to load it. Otherwise, we just need to go the die
        if self.sweep_value_wafer != "Current wafer":

            wafer = wafer_str.replace("C", "").split("W")  # creates a list, e.g. [1,3]

            if wafer != self.last_wafer:

                # We always separate if not already the case
                if self.prober.is_chuck_contacted():
                    self.prober.z_down()

                # this can be the case if only one wafer has to be tested or we reached the last one
                if preload_wafer_str is None:

                    # it must be the first wafer and the only one
                    if self.last_wafer is None:
                        self.prober.load_specified_wafer(*wafer)

                    # it must be the last wafer of multiple wafers
                    else:
                        self.prober.preload_specified_wafer(
                            0, 0)  # command to transfer last wafer from subchuck to chuck

                # this is the case if there is a next wafer
                else:
                    preload_wafer = preload_wafer_str.replace("C", "").split(
                        "W")  # creates a list, e.g. [1,3]

                    # must be the first wafer of several, so need to load and preload ("j4" command)
                    if self.last_wafer is None:
                        self.prober.load_and_preload_specified_wafers(*wafer, *preload_wafer)
                    # it is a wafer in the middle of at least three wafers
                    else:
                        # we only need to preload the next wafer, the current wafer on the subchuck is automatically
                        # forwarded to the main chuck according to command "j3"
                        self.prober.preload_specified_wafer(*preload_wafer)

            self.last_wafer = wafer
            self.last_wafer_str = wafer_str

        self.last_wafer_id = self.prober.request_wafer_id()

        self.print_status()

        # self.skip_die is handed over from the WaferProber module when the user clicks "Go to next die"
        if self.skip_die:
            return

        if self.sweep_value_die != "Current die":

            if die != self.last_die:

                # We always separate if not already the case
                if self.prober.is_chuck_contacted():
                    self.prober.z_down()

                # In any case, the die must have changed, and we need to move to it
                self.prober.move_specified_die(*die)  # die at index x,y

                # once we approach a die, we save the current absolute position at the start position of the die
                # This position is then used to navigate to the correct position
                self.current_die_position = self.prober.request_position()

                self.last_die = die
                self.last_die_str = die_str
                self.last_sub = (0, 0)

        if subsite_str is not None:

            # We always separate if not already the case
            if self.prober.is_chuck_contacted():
                self.prober.z_down()

            if subsite_str.startswith("A"):
                # xy_subsite_pos is defined with respect to the initial start position of the die
                # xy_move is the relative move from the current position to the next subsite position
                # current_die_position is the absolute reference to start position of a die
                # position_die_ref is the last position with respect to start position of the die

                # Extracting the coordinates relative to the die start position
                new_sub = tuple(map(int, subsite_str.replace("A", "").split(",")))

                """
                # Alternative Code to calculate relative move based on measured absolute position based on R command
                # Calculating the last position with respect to the current die position
                position_die_ref = np.array(self.last_position) - np.array(self.current_die_position)

                # Calculating the relative from the current position to the new position
                xy_move = np.array(new_sub) - position_die_ref
                """

                xy_move = np.array(new_sub) - np.array(self.last_sub)

                self.prober.move_position(*xy_move)

                self.last_sub_str = subsite_str
                self.last_sub = new_sub

        self.last_position = self.prober.request_position()

        self.die_x, self.die_y = self.prober.request_die_coordinate()

        # We always get in contact if not done already
        # if not self.prober.is_chuck_contacted():
        #     self.prober.z_up()

        # Check whether dies are correct
        self.print_die_info()

    def call(self):
        return [
            self.last_wafer_id,
            self.last_wafer_str,
            self.die_x,
            self.die_y,
            self.last_position[0],
            self.last_position[1],
        ]

    # further convenience functions

    def print_info(self):

        print()  # empty line for better readability
        print("**** Info ****")

        prober_id = self.prober.request_prober_id()
        print("Prober ID:", prober_id)

        prober_type = self.prober.request_prober_type()
        print("Prober type:", prober_type)

        system_version = self.prober.request_system_version()
        print("System version:", system_version)

    def print_status(self):

        print()  # empty line for better readability
        print("**** Status ****")

        wafer_id = self.prober.request_wafer_id()
        print("Wafer ID:", wafer_id)

        wafer_status = self.prober.request_wafer_status()
        print("Wafer status:", wafer_status)

        cassette_status = self.prober.request_cassette_status()
        print("Cassette status:", cassette_status)

        prober_status = self.prober.request_prober_status()
        print(
            "Prober status:",
            prober_status,
            self.prober.get_prober_status_message(prober_status),
        )

        chuck_status = self.prober.is_chuck_contacted()
        print("Chuck in contact:", chuck_status)

        wafer_on_chuck = self.prober.is_wafer_on_chuck()
        print("Wafer on chuck", wafer_on_chuck)

        alarm = self.prober.is_alarm()
        print("Alarm", alarm)

        error_code = self.prober.request_error_code()
        print("Error code:", error_code)

        error_message = self.prober.request_error_message()
        print("Error message:", error_message)

    def print_die_info(self):

        print()  # empty line for better readability
        print("**** Die info ****")

        cassette, wafer = self.prober.request_cassette_slot()
        print("Cassette - Wafer:", cassette, wafer)

        x_real, y_real = self.prober.request_die_coordinate()
        print("Current die x y:", x_real, y_real)

        on_wafer_info = self.prober.request_onwafer_info()
        print("On wafer info:", on_wafer_info)

        chuck_status = self.prober.is_chuck_contacted()
        print("Chuck in contact:", chuck_status)

        position = self.prober.request_position()
        print("Absolute position:", position)

    def read_controlmap(self, controlmap) -> List[str]:
        """
        Args:
            controlmap: path to the Control Map .MDF file. 
            Control map files can be exported using Device Commander software

        Returns:
            List of strings with each entry describing the x and y index of the die "<x>,<y>"
        """

        with open(controlmap, "r") as mdf_file:

            die_assignment = {
                "MARK": [],
                "PROB": [],
                "SKIP": [],
                "INSP": [],
            }

            last_section = None
            for line in mdf_file.readlines():

                line = line.strip()

                # Comments
                if line.startswith("#"):
                    continue

                splitted = line.split("=")

                # Sections
                if len(splitted) == 1:
                    last_section = line
                    continue

                # Dies
                if last_section == "[DIEINFO]":
                    if splitted[0] in die_assignment:
                        die_assignment[splitted[0]].append(splitted[1])

            # print("Marked dies:", die_assignment["MARK"])
            # print("Skipped dies:", die_assignment["SKIP"])
            # print("Inspection dies:", die_assignment["INSP"])
            # print("Dies to probe:", die_assignment["PROB"])

            return die_assignment["PROB"]

    def read_controlmap_as_tuples(self, controlmap) -> List[Tuple[int, int]]:
        """return die xy positions as [(x,y),...] ints"""
        xy_die_positions = self.read_controlmap(self, controlmap)
        return [tuple(int(val) for val in pos.split(",")) for pos in xy_die_positions]
