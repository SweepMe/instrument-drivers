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

import socket
import time

class MPISentioProber:
    """
    This library does not handle asynchronous commands.
    """

    def __init__(self, comm):

        self.comm = comm
        # Error and status codes according to the Remote Commands Manual version UG_REV2.1 AST-TW-062, 06-2020
        self.error_codes = {
            0: "NoError",
            1: "InternalError",
            2: "ExecutionError",
            3: "CommandHandlerNotFound",
            4: "InvalidCommand",
            5: "InvalidCommandFormat",
            6: "InvalidParameter",
            7: "InvalidNumberOfParameters",
            8: "ArgumentOutOfBounds",
            9: "FileNotFound",
            10: "InvalidFileFormat",
            11: "EndOfRoute",
            12: "InvalidOperation",
            13: "NotSupported",
            14: "SubsiteNotRoutable",
            15:
            "TransferSlotOccupied",  # Not found in documentation, but in SentioProberControl github library.
            16:
            "TransferSlotEmpty",  # Not found in documentation, but in SentioProberControl github library.
            17: "PrealignmentFailed",
            18: "IsBusy",  # Not found in documentation, but in SentioProberControl github library.
            19: "Timeout",
            20: "PatternNotTrained",
            21: "PatternNotFound",
            22: "TooManyPatternsFound",
            30: "CommandPending",
            31: "AsyncCommandAborted",
            32: "UnknownCommandId",
            35: "CameraNotCalibrated",
            36: "CameraDoesNotExist",
            60: "FrontDoorOpen",
            61: "LoaderDoorOpen",
            62: "FrontDoorLockFail",
            63: "LoaderDoorLockFail",
            64: "SlotOrStationOccupied",
            65: "SlotOrStationEmpty",
            80: "NoCassetteExistint",
            81: "SlotNumberError",
            83: "PraAlignerAlignAngleError",
            85: "NoWaferOnPrealigner",
            86: "NoWaferOnChuck",
            87: "NoWaferOnSlotOrTray",
            88: "NoWaferOnRobot",
            89: "PreAlignerIdReaderAngleError",
            90: "NoIdReader",
            100: "PositionerNotInitial",
            101: "PositionerServoOnOffFail",
            120: "OverTravelOverLimit",
            121: "MissingTopographyTable",
        }

        # status code defined here, but not used
        self.status_codes = {
            # Status Bits(only for stepping):
            1024: "LastDie",  # (Bit 11)
            2048: "LastSubsite",  # (Bit 12)
        }

    def __del__(self):
        if isinstance(self.comm, socket.socket):
            self.comm.close()

    # Communication methods
    def write(self, cmd):
        """
        This function sends a message over the comm object, which is created in connect() method.
        Args:
            cmd: string or integer
            EOL: character

        Returns:
            None
        """
        if isinstance(self.comm, socket.socket):
            cmd = cmd + "\n"
            self.comm.send(cmd.encode('latin-1'))
        else:
            self.comm.write(cmd)

    def read(self, timeout=20):
        """
        This function reads a message from the comm object. The user can pass a socket object,
        or a pysweepme port object. Pysweepme's port object is useful when NI VISA runtime is installed.
        Returns:
            string: response
        """

        if isinstance(self.comm, socket.socket):
            start_time = time.time()
            while True:
                if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                    raise IOError("Measurement was stopped during read port.")
                if time.time() - start_time > timeout:
                    raise IOError("Timeout: No answer received for movement commands.")

                try:
                    answer = self.comm.recv(1024).decode('latin-1').strip()
                    break
                except socket.timeout:
                    pass  # Handle the timeout manually.
        else:
            answer = self.comm.read()  # using pysweepme.Ports.Port object

        value, id_, response = answer.split(",", maxsplit=2)
        value = int(value)
        errc = value & 1023  # splitting the lower 10 bits, being the error code

        # status information, not used so far
        last_die = (value & 1024) != 0
        last_subsite = (value & 2048) != 0

        if errc == 0:
            return response
        elif errc in self.error_codes:
            raise Exception("MPI Sentio error %d (%s): %s" %
                            (errc, self.error_codes[errc], response))
        else:
            raise Exception("Received answer with undefined error code: %s" % answer)

    # Command methods start from here.

    # Low level commands
    def get_rcs(self):
        """
        Retrieves the currently active remote command set.
        Returns:
            str: answer
        """
        self.write("*RCS?")
        answer = self.read()
        return answer

    # Status commands
    def status_get_prop(self, property_name, args_string):
        """
        A generic function to retrieve the value of a specific data item from the dashboard module.
        Returns:
            str: answer
        """
        self.write("status:get_prop %s %s" % (property_name, args_string))
        answer = self.read()
        return answer

    def status_set_prop(self, property_name, args_string):
        """
        A generic function to set the value of a specific property.
        Args:
            property_name: str
            args_string: str

        Returns:
            str: answer
        """
        self.write("status:set_prop %s, %s" % (property_name, args_string))
        answer = self.read()
        return answer

    def status_get_machine_id(self):
        """
        Retrieves the machine ID.
        Returns:
            str: answer
        """
        self.write("status:get_machine_id")
        answer = self.read()
        return answer

    def status_get_version(self):
        """
        Retrieves the system version.
        Returns:
            str: answer
        """
        self.write("status:get_version")
        answer = self.read()
        return answer

    def status_get_machine_status(self):
        """
        Retrieves the machine status flags:
            NotReady: System is not initialized.
            Ready: System is initialized.
            Running: System is busy (i.e. Stage is moving).
            IsMeasuring: System is running a measurement with an instrument (Qalibria).
            LoaderBusy The Cassette Loader / Slot loader is busy (TS3500/TS2500 only).
        Returns:
            str: answer
        """
        self.write("status:get_machine_status")
        answer = self.read()
        return answer

    def status_show_message(self,
                            message,
                            caption="popup window",
                            level="Hint",
                            buttons="OKCancel"):
        """
        Shows a message dialog for user interaction. Button options are "OK" [default], "OKCancel", "YesNo", and
        "YesNoCancel". Level options are: "Hint" [default], "Warning", and "Error".
        Args:
            message: str
            caption: str
            level: str
            buttons: str

        Returns:
            str: answer
        """
        self.write("status:show %s,%s,%s,%s" % (message, buttons, caption, level))
        answer = self.read(timeout=60)
        return answer

    # Chuck commands
    def get_chuck_site_heights(self, index=""):
        """

        Args:
            index:

        Returns:
            tuple: [ContactHeight, SeparationHeight, OvertravelGap, HoverHeight]
        """
        self.write("get_chuck_site_heights %s" % str(index))
        answer = tuple(map(float, self.read().split(",")))
        return answer

    def get_chuck_site_status(self):
        """
        Retrieves status information of a chuck site:
            -1: not available
            0: false
            1: true

        Returns:
            tuple: (Home, Contact, Overtravel, Vacuum)
        """
        self.write("get_chuck_site_status")
        answer = tuple(map(int, self.read().split(",")))
        return answer

    def get_chuck_xy(self):
        """
        Reads the current xy position of a chuck site in µm with respect to the zero position, which is
        the default reference of response of other commands.
        Returns:
            tuple: (x, y)
        """
        self.write("get_chuck_xy")
        answer = tuple(map(float, self.read().split(",")))
        return answer

    def get_chuck_z(self):
        """
        Reads the chuck height with respect to the zero height.
        Returns:
            float: z
        """
        self.write("get_chuck_z")
        z = float(self.read())
        return z

    def get_chuck_theta(self):
        """
        Reads the current theta angle of a chuck site with respect to site home angle.
        Returns:
            float: theta
        """
        self.write("get_chuck_theta")
        theta = float(self.read())
        return theta

    def get_chuck_speed(self):
        """
        Retrieves the chuck speed settings, can be Fast, Normal, Slow, Jog, or Index.
        Returns:
            str: answer
        """
        self.write("get_chuck_speed")
        answer = self.read()
        return answer

    def set_chuck_speed(self, speed_string):
        """
        Sets the chuck speed settings, can be Fast, Normal, Slow, Jog, or Index.
        Args:
            speed_string: str
        Returns:
            str: answer
        """
        self.write("set_chuck_speed %s" % speed_string)
        answer = self.read()
        return answer

    def set_soft_contact(self, state):
        """
        Sets the soft contact to enable or disable.
        Args:
            state: int or bool

        Returns:
            str: answer
        """
        self.write("set_soft_contact %s" % int(state))
        answer = self.read()
        return answer

    def set_vacuum(self, state):
        """
        Switches the vacuum of a chuck site on or off.
        Args:
            state: int or bool

        Returns:
            str: answer
        """
        self.write("set_vacuum %s" % int(state))
        answer = self.read()
        return answer

    def move_chuck_center(self):
        """
        Moves chuck xy to center position of the currently active site.
        Returns:
            float: new_x
            float: new_y
        """
        self.write("move_chuck_center")
        new_x, new_y = map(float, self.read().split(","))
        return new_x, new_y

    def move_chuck_contact(self):
        """
        Moves chuck to contact height. If overtravel is enabled chuck moves to overtravel height.
        If contact height is not set the command is not carried out.
        Returns:
            str: new_z
        """
        self.write("move_chuck_contact")
        new_z = float(self.read())
        return new_z

    def move_chuck_home(self):
        """
        Moves chuck xy to home position of the currently active site.
        Returns:
            float: new_x
            float: new_y
        """
        self.write("move_chuck_home")
        new_x, new_y = map(float, self.read().split(","))
        return new_x, new_y

    def move_chuck_separation(self):
        """
        Moves chuck to separation height. If contact height is not set the command is not carried out.
        Returns:
            str: new_z
        """
        self.write("move_chuck_separation")
        new_z = float(self.read())
        return new_z

    def move_chuck_load(self, load_position="front"):
        """
        This command will move chuck to load position.
        Args:
            load_position: str

        Returns:
            str: answer
        """
        self.write("move_chuck_load %s" % load_position)
        answer = self.read()
        return answer

    def set_chuck_separation_gap(self, gap):
        """
        Sets separation gap for all chuck sites in um.
        Returns:
            str: answer
        """
        self.write("set_chuck_separation_gap %f" % gap)
        answer = self.read()
        return answer

    def stop_chuck_theta(self):
        """
        Stops chuck rotation.
        Returns:
            str: answer
        """
        self.write("stop_chuck_theta")
        answer = self.read()
        return answer

    def stop_chuck_xyz(self):
        """
        Stops chuck movement in xyz directions.
        Returns:
            str: answer
        """
        self.write("stop_chuck_xyz")
        answer = self.read()
        return answer

    # Door commands
    def get_door_status_prober(self):
        """
        Retrieves the “Closed” and “Locked” state of the prober's door.
        Returns:
            str: closed_state
            str: locked_state
        """
        self.write("get_door_status prober")
        closed_state, locked_state = map(float, self.read().split(","))
        return closed_state, locked_state

    def get_door_status_loader(self):
        """
        Retrieves the “Closed” and “Locked” state of the loader's door.
        Returns:
            str: closed_state
            str: locked_state
        """
        self.write("get_door_status loader")
        answer = tuple(map(float, self.read().split(",")))
        return answer

    # Scope commands
    def has_scope_xyz(self):
        """
        Check the system has motoric scope XYZ.
        Returns:
            str: answer
        """
        self.write("has_scope_xyz")
        answer = self.read()
        return answer

    def has_scope_z(self):
        """
        Check the system has motoric scope Z.
        Returns:
            str: answer
        """
        self.write("has_scope_z")
        answer = self.read()
        return answer

    # Thermochuck commands
    def status_get_chuck_temp(self):
        """
        Retrieves the current chuck temperature.
        Returns:
            float: temperature
        """
        self.write("status:get_chuck_temp")
        temperature = float(self.read())
        return temperature

    # Project handling commands
    def get_project(self):
        """
        Retrieves the project information.
        Returns:
            str: answer
        """
        self.write("get_project")
        answer = self.read()
        return answer

    # Map commands
    def map_get_prop(self, property_name, args_string):
        """
        A generic function to retrieve the value of a specific data item from the map module.
        Returns:
            str: answer
        """
        self.write("map:get_prop %s,%s" % (property_name, args_string))
        answer = self.read()
        return answer

    def map_step_die(self, column_index, row_index, subsite_index=""):
        """
        Steps to a die at a defined position.
        Args:
            column_index: int
            row_index: int

        Returns:
            int: new_column_index
            int: new_row_index
            int: new_subsite_index
        """
        self.write("map:step_die %s,%s,%s" % (column_index, row_index, subsite_index))
        new_column_index, new_row_index, new_subsite_index = map(int, self.read().split(","))
        return new_column_index, new_row_index, new_subsite_index

    def map_step_die_seq(self, die_index, subsite_index=""):
        """
        Steps to a subsite of a die within the routing sequence.
        Args:
            die_index: int
            subsite_index: int
        Returns:
            int: new_column_index
            int: new_row_index
            int: new_subsite_index
        """
        
        cmd = "map:step_die_seq %s" % die_index
        if subsite_index != "":
            cmd += ",%s" % subsite_index
        self.write(cmd)

        new_column_index, new_row_index, new_subsite_index = map(int, self.read().split(","))
        return new_column_index, new_row_index, new_subsite_index

    def map_step_next_die(self, subsite_index=""):
        """
        Steps to the submitted subsite of the next die in the stepping route. If target subsite
        is not routable, an error occurs. If SubsiteIndex is omitted, target subsite is the
        currently active subsite and target die is the next one within the stepping route
        where target subsite is routable. Only executable if routing is active and currently
        active die is part of the route.
        Args:
            subsite_index: int
        Returns:
            int: new_column_index
            int: new_row_index
            int: new_subsite_index

        """
        self.write("map:step_next_die %s" % subsite_index)
        new_column_index, new_row_index, new_subsite_index = map(int, self.read().split(","))
        return new_column_index, new_row_index, new_subsite_index

    def map_step_previous_die(self):
        """
        Step to the currently active subsite of the previous die in the stepping route whose
        currently active subsite is routable. Only executable if routing is active and currently
        active die is part of the route.
        Returns:

        """
        self.write("map:step_previous_die")
        new_column_index, new_row_index = map(int, self.read().split(","))
        return new_column_index, new_row_index

    def map_subsite_get_num(self, group="GP"):
        """
        Gets the number of a specified subsite group (GP for global subsite definitions).
        Returns:
            int: count
        """
        self.write("map:subsite:get_num %s" % group)
        count = int(self.read())
        return count

    def map_subsite_step(self, subsite_index):
        self.write("map:subsite:step %s" % subsite_index)
        column_index, row_index, subsite_index = map(int, self.read().split(","))
        return column_index, row_index, subsite_index

    def map_get_num_dies(self, group="selected"):
        """
        Retrieves the number of dies in the defined group ("selected" for dies selected for test.)
        Args:
            group: str

        Returns:
            int: count
        """
        self.write("map:get_num_dies %s" % group)
        count = int(self.read())
        return count

    def map_die_get_current_index(self):
        """
        Retrieves Information about current die. If no die is active massage “No die active” is returned.
        If active die does not belong to the stepping route ListIndex -1 is returned. The indexes are relative
        to the grid origin.

        Returns:
            int: routing_list_index
            int: column_index
            int: row_index
        """
        self.write("map:die:get_current_index")
        routing_list_index, column_index, row_index = map(int, self.read().split(","))
        return routing_list_index, column_index, row_index

    def map_die_get_current_subsite(self):
        """
        Retrieves Information about the currently active subsite. If no subsite is active massage
        “No subsite active” is returned.

        Returns:
            int: subsite_index
        """
        self.write("map:die:get_current_subsite")
        subsite_index = int(self.read())
        return subsite_index

    def map_get_die_seq(self):
        """
        Retrieves the current die sequence number of wafer map (only for round wafer map).
        Returns:
            int: count
        """
        self.write("map:get_die_seq")
        count = int(self.read())
        return count

    def map_get_num_rows(self):
        """
        Retrieves the number of rows in the grid.
        Returns:
            int: row_number
        """
        self.write("map:get_num_rows")
        row_number = int(self.read())
        return row_number

    def map_get_num_cols(self):
        """
        Retrieves the number of columns in the grid
        Returns:
            int: column_number
        """
        self.write("map:get_num_cols")
        column_number = int(self.read())
        return column_number

    def map_get_grid_origin(self):
        """
        Retrieves the origin of the grid within the base grid.
        Returns:
            int: column
            int: row
        """
        self.write("map:get_grid_origin")
        column, row = map(int, self.read().split(","))
        return column, row

    def map_path_get_die(self, die_sequence_number):
        """
        Query the die row/column by die sequence number.
        Args:
            die_sequence_number: int
        Returns:

        """
        self.write("map:path:get_die %d" % die_sequence_number)
        column, row = map(int, self.read().split(","))
        return column, row

    # Module commands

    # Auxiliary sites substrate commands

    # Vision commands

    # Setup commands
    def light_off_at_contact(self, state):
        """
        In remote mode, defines whether light has to be switched off when chuck has been
        moved to contact height
        Args:
            state: int or bool or str

        Returns:
            str: answer
        """
        self.write("setup:remote:light_off_at_contact %s" % int(state))
        answer = self.read()
        return answer

    def light_on_at_separation(self, state):
        """
        In remote mode, defines whether light has to be switched on when chuck has been
        moved to separation height
        Args:
            state: int or bool or str

        Returns:
            str: answer
        """
        self.write("setup:remote:light_on_at_separation %s" % int(state))
        answer = self.read()
        return answer

    # QAlibria host commands

    # Automation handling commands
    def loader_scan_station(self, station):
        """
        Scans the wafer presence status of a specific station. The answer is a number with length of the number of
        available slots.
        Remark: Supported only on fully automatic machines (TS2000-IFE, TS2500, TS3500).
        Args:
            station: str
        Returns:
            str: slots_state
        """
        self.write("loader:scan_station %s" % station)
        slots_state = int(self.read())
        return slots_state

    # Motorized positioner commands
    def move_positioner_xy(self, positioner_id, reference="zero", x_coord=None, y_coord=None):
        """
        Move a positioner in XY plane.
        Remark: The x and y values are relative to zero.
        Args:
            reference: str
            x_coord: int
            y_coord: int
            positioner_id: int or str
        Returns:
            str: answer
        """

        self.write("move_positioner_xy %s,%s,%s,%s" % (positioner_id, reference, x_coord, y_coord))
        answer = self.read().split(",")
        result = list(map(float, answer))
        return result

    def get_positioner_xy(self, positioner_id, reference="zero"):
        """
        Get a positioner's position in XY plane.
        Remark: By default, the x and y values are relative to zero position.
        Args:
            positioner_id: int or str
            reference: str
        Returns:
            str: answer
        """

        self.write("get_positioner_xy %s,%s" % (positioner_id, reference))
        answer = self.read().split(",")
        result = list(map(float, answer))
        return result

    # Other commands

    # Auxiliary commands (asynchronous)

    # SiPH application commands
    def siph_move_hover(self, positioner_id):
        """
        Move SiPH positioner to hover height position.
        Args:
            positioner_id: int or str
        Returns:
            str: answer
        """
        self.write("siph:move_hover %s" % positioner_id)
        answer = self.read()
        return answer

    def siph_move_separation(self, positioner_id):
        """
        Move SiPH positioner to separation height position.
        Args:
            positioner_id: int or str
        Returns:
            str: answer
        """
        self.write("siph:move_separation %s" % positioner_id)
        answer = self.read()
        return answer

    def siph_fast_alignment(self, positioner_id=None):
        """
        Start SiPH positioner execute fast alignment.
        Args:
            positioner_id: int or str, optional
        Returns:
            str: answer
        """
        if positioner_id:
            self.write("siph:fast_alignment %s" % positioner_id)
        else:
            self.write("siph:fast_alignment")
        answer = self.read()
        return answer

    def siph_gradient_search(self, positioner_id):
        """
        Start SiPH positioner execute gradient search.
        Args:
            positioner_id: int or str
        Returns:
            str: answer
        """
        self.write("siph:gradient_search %s" % positioner_id)
        answer = self.read()
        return answer

    def siph_get_intensity(self):
        """
        Get the intensity value.

        Returns:
            str: intensity
        """
        self.write("siph:get_intensity")
        intensity = float(self.read())
        return intensity

    def siph_power_calibration(self, positioner_id):
        """
        Move the chuck to probe position of power Calibration site and return the power value.
        Returns:
            str: intensity
        """
        self.write("siph:power_calibration")
        power = float(self.read())
        return power

    def siph_move_origin(self, positioner_id):
        """
        Move the positioner to origin position.
        Args:
            positioner_id: int or str
        Returns:
            str: answer
        """
        self.write("siph:move_origin %s" % positioner_id)
        answer = self.read()
        return answer

    def siph_set_alignment(self, fiber_type, coarse_seach, fine_search, gradient_search, rotary_focal_search, positioner_id):
        """
        Set the fast alignment function enable including Coarse, Fine, Gradient, and Rotary/Focal searching.
        Args:
            fiber_type: str
            coarse_seach: str
            fine_search: str
            gradient_search: str
            rotary_focal_search: str
            positioner_id: str or int
        Returns:
            str: answer
        """
        self.write("siph:set_alignment %s,%s,%s,%s,%s,%s" % (positioner_id, fiber_type, coarse_seach, fine_search, gradient_search, rotary_focal_search))
        answer = self.read()
        return answer

    def siph_get_alignment(self, positioner_id, fiber_type=""):
        """
        Get the fast alignment function enable including Coarse, Fine, Gradient, and Rotary/Focal searching.
        Args:
            positioner_id: str or int
            fiber_type: str (optional)
        Returns:
            list: status
        """
        self.write("siph:get_alignment %s,%s" % (positioner_id, fiber_type))
        answer = self.read().split(",")
        status = list(map(bool, answer))
        return status

if __name__ == "__main__":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(20)
    client.connect(("127.0.0.1", 35555))
    prober = MPISentioProber(client)
    print(prober.siph_get_intensity())