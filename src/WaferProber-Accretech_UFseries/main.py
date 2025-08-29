# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022-2024 SweepMe! GmbH (sweep-me.net)
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

# SweepMe! driver
# * Module: WaferProber
# * Instrument: Accretech UF series

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

        self.port_str = "undefined_port"

        # self.actual_wafer_text = ""
        # self.actual_die_text = ""
        # self.actual_subsite_text = "Not available"
        # self.actual_xpos = "Not available"
        # self.actual_ypos = "Not available"

        self.verbosemode = True

        # Variable that is set != "" in case an exception happens in the apply phase.
        # In this case, the wafer is not unloaded and the exception steps tells the user whether the exception happened
        # when the wafer, the die, or the subsite was changed.
        self.exception_step_during_apply = ""

    def set_GUIparameter(self):
        gui_parameter = {
            "SweepValueWafer": "Wafer table",
            "SweepValueDie": "Die table",
            "SweepValueSubsite": "Subsite table",
        }
        return gui_parameter

    def get_GUIparameter(self, parameter):
        self.port_str = parameter["Port"]
        self.sweep_value_wafer = parameter["SweepValueWafer"]
        self.sweep_value_die = parameter["SweepValueDie"]
        self.sweep_value_subsite = parameter["SweepValueSubsite"]

    def get_probeplan(self, probeplan_path):
        # important function to retrieve the probe plan before the measurement starts,

        # Wafers
        wafer_status = self.prober.request_wafer_status()
        # a list of tuples containing cassette and wafer id
        wafer_list = self.prober.get_waferlist_from_status(wafer_status)

        self.check_and_sense_wafers()

        wafer_status = self.prober.request_wafer_status()
        # a list of tuples containing cassette and wafer id
        wafer_list = self.prober.get_waferlist_from_status(wafer_status)

        if len(wafer_list) == 0:
            if self.prober.is_wafer_on_chuck():
                wafers = ["inspection tray"]
            else:
                debug(
                    "Empty wafer list, please make sure the cassette is filled and "
                    "you have sensed the wafer before you try again.",
                )
                wafers = []
        else:
            wafers = [f"C{i}W{j}" for i, j, k in wafer_list]

        # Dies
        die_list = self.read_controlmap(probeplan_path)
        dies = die_list

        # Subsites
        subsites = []  # Subsites cannot be defined via file or loaded from the wafer

        # Name
        probeplan_name = "..." + probeplan_path[-15:]

        return wafers, dies, subsites, probeplan_name

    def get_current_wafer(self):
        """Function is used by the WaferProber module to get the current wafer
        before the run starts in case the sweep values "Current Wafer" is used.
        """
        if self.prober.is_wafer_on_chuck:
            cassette, slot = self.prober.request_cassette_slot()
            current_wafer = f"C{cassette}W{slot}"
        else:
            current_wafer = ""

        return current_wafer

    def get_current_die(self):
        """Function is used by the WaferProber module to get the current die before the
        run starts in case the sweep value "Current Die" is used.
        """
        if self.prober.is_wafer_on_chuck:
            die_x, die_y = self.prober.request_die_coordinate()
            current_die = f"{die_x},{die_y}"
        else:
            current_die = ""

        return current_die

    def get_current_subsite(self):
        """Function is used by the WaferProber module to get the current subsite before the run
        starts in case the sweep value "Current Subsite" is used.
        """
        current_subsite = ""

        return current_subsite

    def load_wafer(self, wafer_str):
        self.print_info()

        self.print_status()

        self.prober.reset_alarm()

        self.check_and_sense_wafers()

        wafer_status = self.prober.request_wafer_status()
        # a list of tuples containing cassette and wafer id
        wafer_list = self.prober.get_waferlist_from_status(wafer_status)

        wafer = wafer_str.replace("C", "").split("W")  # creates a list, e.g. [1,3]
        wafer = tuple(map(int, wafer))

        # wafer is a tuple with cassette number and wafer number.
        # adding (3,) extends this tuple with the status where 3 means wafer on chuck
        if wafer + (3,) not in wafer_list:
            # independent whether there is a wafer on the chuck we can use
            # load_specified_wafer after check for sensed wafers
            # If there is a wafer on the chuck, it will automatically be unloaded
            self.prober.load_specified_wafer(*wafer)
        else:
            message_box(f"Wafer {wafer_str} is already on the chuck!", blocking=False)

    def unload_wafer(self):
        self.print_info()

        self.print_status()

        self.prober.reset_alarm()

        if self.prober.is_wafer_on_chuck():
            self.prober.preload_specified_wafer(9, 99)
        else:
            message_box("There is no wafer on the chuck, that can be unloaded!", blocking=False)

    def connect(self):
        # creating an AccretechProber instance that handles all communication
        self.prober = accretech_uf.AccretechProber(self.port)
        self.prober.set_verbose(self.verbosemode)

        # This identifier must be equal with the identifier used by the Temperature_Accretech_UFseries driver
        self.unique_identifier = "Driver_Accretech_UFseries_" + self.port_str
        if self.unique_identifier not in self.device_communication:
            self.device_communication[self.unique_identifier] = None

    def disconnect(self):
        if self.unique_identifier in self.device_communication:
            self.prober.unregister_srq_event()  # this makes sure the event mechanism is disabled
            del self.device_communication[self.unique_identifier]
        del self.prober

    def initialize(self):
        self.print_info()

        self.print_status()

        self.prober.reset_alarm()

        if self.sweep_value_wafer == "Current wafer":
            if not self.prober.is_wafer_on_chuck():
                msg = "There is no wafer on the chuck, although 'Current wafer' is selected as Sweep value."
                raise Exception(msg)
        else:
            if self.sweep_value_die == "Current die":
                msg = (
                    "Performing a wafer variation for the current die is not possible as the current die is not "
                    "defined for a wafer variation."
                )
                raise Exception(msg)

            if self.prober.is_wafer_on_chuck():
                self.prober.unload_all_wafers()

            self.check_and_sense_wafers()

        if self.sweep_value_subsite == "Current subsite":
            msg = "Option 'Current subsite' is not supported yet."
            raise Exception(msg)

    def configure(self):
        self.last_wafer = None
        self.last_wafer_str = ""
        self.last_wafer_id = ""

        self.last_die = None
        self.last_die_str = ""

        self.last_sub = (0, 0)
        self.last_sub_str = ""

        # absolute position of the current die starting position
        self.current_die_position = (None, None)

        # last absolute position
        self.last_position = (None, None)

    def unconfigure(self):
        # Chuck down
        self.prober.z_down()

        if self.sweep_value_wafer != "Current wafer":
            if self.exception_step_during_apply != "":
                message_box(
                    "Accretech wafer prober failed to change to the next %s. Wafer remains on the chuck."
                    % self.exception_step_during_apply.lower(),
                    blocking=False,
                )
            else:
                # Terminating the lot process bringing all wafers back to cassette
                if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                    message_box(
                        "Lot process will be finished which takes 1-2 minutes.\n\n"
                        "Do not terminate the run and please wait until the program finishes."
                        "You can close this message when the run has completed normally.",
                        blocking=False,
                    )

                self.prober.preload_specified_wafer(9, 99)

    def apply(self):
        """Applies the new wafer, die or subsite.

        The function takes the self.sweepvalues dictionary and checks whether wafer, die, or subsite have changed by
        comparing with the last wafer, last, or last subsite.

        It starts with processing the wafer, then the die and at the end the subsite.

        In case a wafer is changed, the last die is reset.
        In case a die is changed, the last subsite is reset.

        The driver support the handling preloading the next wafer. Because of preloading, different commands need to be
        used for loading the first wafer loading the last wafer, or loading a wafer inbetween. This is why there are
        several if-else to handle these situations.
        """
        wafer_str = self.sweepvalues["Wafer"]
        die_str = self.sweepvalues["Die"]
        subsite_str = self.sweepvalues["Subsite"]
        die = die_str.split(",")  # create a list of x and y coordinates, e.g "1,3" -> [1,3]
        preload_wafer_str = self.sweepvalues["NextWafer"]

        if wafer_str is None:
            msg = "You need to specify at least one wafer or use 'Current wafer' as sweep value!"
            raise Exception(msg)

        if die_str is None:
            msg = "You need to specify at least one die or use 'Current die' as sweep value!"
            raise Exception(msg)

        # We do not check whether subsites are None because in that case no subsite was defined and the prober
        # stays at the start position of the die

        # Wafer
        try:
            # self.skip_wafer handed over from WaferProber module when user clicks "Go to next wafer"
            if self.skip_wafer:
                return

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
                            # command to transfer last wafer from subchuck to chuck
                            self.prober.preload_specified_wafer(0, 0)

                    # this is the case if there is a next wafer
                    else:
                        # creates a list, e.g. [1,3]
                        preload_wafer = preload_wafer_str.replace("C", "").split("W")

                        # if there is a iteration of a higher module in the sequencer
                        # it can happen that the wafer on the chuck needs to be preloaded
                        # in this case, we need to bring back the wafer on the chuck first.
                        if preload_wafer == self.last_wafer:
                            self.prober.unload_all_wafers()
                            # we set last wafer to None because in this case the preload and chuck wafer
                            # are loaded in the code below
                            self.last_wafer = None
                            self.last_wafer_str = ""
                            self.last_wafer_id = ""

                        # must be the first wafer of several, so need to load and preload ("j4" command)
                        if self.last_wafer is None:
                            self.prober.load_and_preload_specified_wafers(*wafer, *preload_wafer)
                        else:
                            # we only need to preload the next wafer, the current wafer on the subchuck is automatically
                            # forwarded to the main chuck according to command "j3"
                            self.prober.preload_specified_wafer(*preload_wafer)

                    self.last_position = (None, None)

                    self.last_wafer = wafer
                    self.last_wafer_str = wafer_str

                    # we need to set back the last die information in case to trigger a new move to
                    # the first requested die of this new wafer even if the die is the same like
                    # the last one of the previous wafer
                    self.last_die = None
                    self.last_die_str = ""

            self.last_wafer_id = self.prober.request_wafer_id()

            self.print_status()

        except Exception:
            self.exception_step_during_apply = "Wafer"
            raise

        # Die
        # self.skip_die is handed over from the WaferProber module when the user clicks "Go to next die"
        if self.skip_die:
            return
        if self.sweep_value_die != "Current die" and die != self.last_die:
            try:
                self.step_to_die(die_str)
            except Exception as e:
                self.exception_step_during_apply = "Die"
                raise e

        # Subsite
        if subsite_str is not None:
            try:
                self.step_to_subsite(subsite_str)
            except Exception as e:
                self.exception_step_during_apply = "Subsite"
                raise e

        # Retrieving position and check whether position has indeed changed
        position = self.prober.request_position()
        if position != self.last_position:
            debug("Subsite position did not change for unknown reason")
        self.last_position = position

        self.die_x, self.die_y = self.prober.request_die_coordinate()

        # We always get in contact if not done already
        if not self.prober.is_chuck_contacted():
            self.prober.z_up()

        # Check whether dies are correct
        self.print_die_info()

    def step_to_die(self, die_string: str) -> None:
        """Move to a specified die position given as comma separated string '1,3'."""
        die = die_string.split(",")  # create a list of x and y coordinates, e.g "1,3" -> [1,3]

        # We always separate if not already the case
        if self.prober.is_chuck_contacted():
            self.prober.z_down()

        # In any case, the die must have changed, and we need to move to it
        self.prober.move_specified_die(*die)  # die at index x,y

        # once we approach a die, we save the current absolute position at the start position of the die
        # This position is then used to navigate to the correct position
        self.current_die_position = self.prober.request_position()

        self.last_die = die
        self.last_die_str = die_string

        # we reset the last subsite position as the position always starts at (0,0) after
        # going to the die
        self.last_sub = (0, 0)
        self.last_position = (None, None)

    def step_to_subsite(self, subsite_str: str) -> None:
        """Move to a specified subsite position given as comma separated string starting with A: 'A1,3'."""
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

            position = self.prober.request_position()

            # we subtract the position from the origin to invert the sign of the rel_sub
            # this way the difference can directly be compared with new_sub
            # Please note that A command (new_sub) has opposite coordinate system than
            # R command (rel_sub)
            # A command is a relative move towards while R command returns a global
            rel_sub = tuple(np.array(self.current_die_position) - np.array(position))

            # Check whether new position is not more than 5um away in each coordinate direction
            # from the requested move

            if abs(new_sub[0] - rel_sub[0]) > 5 or abs(new_sub[1] - rel_sub[1]) > 5:
                msg = (
                    f"Relative subsite position after move {rel_sub} is not in "
                    f"agreement with requested subsite position {new_sub}."
                )
                raise Exception(msg)

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
        print("Prober status:", prober_status, self.prober.get_prober_status_message(prober_status))

        lock_status = self.prober.request_cassette_lock_status()
        print("Cassette lock status:", lock_status)

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

    def check_and_sense_wafers(self):
        if not self.prober.is_wafer_on_chuck():
            # in case of an inspection wafer on the chuck or a lot process was already started,
            # there is no need to sense the wafers

            cassette_status = self.prober.request_cassette_status()

            # if none of the two cassettes has a status yet
            if cassette_status[-2:] == "00":
                self.prober.sense_wafers()  # Wafer sensing "jw" command

    def get_wafer_on_chuck(self):
        """Returns the current wafer on the chuck

        Returns:
            tuple of cassette id and wafer id, (None, None) in case there is no wafer on the chuck

        """
        wafer = (None, None)
        if self.prober.is_wafer_on_chuck():
            # Get cassettes and wafers
            wafer_status = self.prober.request_wafer_status()
            # a list of tuples containing cassette and wafer id
            wafer_list = self.prober.get_waferlist_from_status(wafer_status)

            wafer_during_test_status = 3
            for wafer_ in wafer_list:
                if wafer_[2] == wafer_during_test_status:  # wafer during testing -> wafer on chuck
                    wafer = (wafer_[0], wafer_[1])
                    break

        return wafer

    def read_controlmap(self, controlmap) -> List[str]:
        """Reads a given controlmap file

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
        """Return die xy positions as [(x,y),...] ints"""
        xy_die_positions = self.read_controlmap(self, controlmap)
        return [tuple(int(val) for val in pos.split(",")) for pos in xy_die_positions]
