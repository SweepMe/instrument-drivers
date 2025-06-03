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


# SweepMe! driver
# * Module: WaferProber
# * Instrument: SemiProbe PILOT / SP Map


import socket
import time

import numpy as np

from pysweepme import error, debug

from pysweepme import EmptyDevice


class Device(EmptyDevice):

    description = """
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>By setting the "Find feature retries", the user can specify how many times the PILOT software
                    find feature should be called. Set it to 0 to deactivate find feature.</li>
                    <li>According to the manual, find feature score is a value between 20 and 100.</li>
                    </ul>
                    <p>&nbsp;</p>
                 """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "PILOT"  # short name will be shown in the sequencer
        self.variables = ["Die index", "Die x", "Die y"]  # defines as many variables you want
        self.units = ["", "", ""]  # make sure that units and variables have the same amount
        self.plottype = [True, True, True]   # True to plot data, corresponding to self.variables
        self.savetype = [True, True, True]   # True to save data, corresponding to self.variables
        self.port_manager = False
        self.timeout = 1
        
        self.verbose = False

    def set_GUIparameter(self):
        gui_parameter = {
            "Contact wafer": False,
            "": None,
            "Find feature": None,
            "Retries": 0,
            }
        return gui_parameter
     
    def get_GUIparameter(self, parameter):

        self.find_feature_retries = int(parameter["Retries"])
        if self.find_feature_retries > 0:
            self.feature_found = False
            self.variables.append("Feature found")
            self.units.append("")
            self.plottype.append(True)
            self.savetype.append(True)
        self.port_string = parameter["Port"]
        self.is_contact_wafer = parameter["Contact wafer"]

    def find_ports(self):
        return ["xxx.xxx.xxx.xxx", "localhost"]

    def get_probeplan(self, path):
        navigation_array = self.load_smt_file(path)
        dies = []
        for i in range(0, navigation_array.shape[0]):
            dies.append("%s,%s#%s" % (int(navigation_array[i, 1]),
                                      int(navigation_array[i, 2]),
                                      int(navigation_array[i, 0])))
        subsites = []
        wafers = []
        return wafers, dies, subsites

    # here semantic functions start

    # Todo: add find_ports method to automatically take care of the ip address and port.
    def connect(self):

        # Socket communication could be moved to SweepMe! Port Manager in future
        if not self.port_manager:
            if self.port_string == "xxx.xxx.xxx.xxx":
                raise Exception("Please input the ip address of the SemiProbe PILOT computer.")
            elif self.port_string == "localhost":
                ip, port = "127.0.0.1", 5050
            else:
                ip, port = self.port_string, 4000
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(self.timeout)
            try:
                self.client.connect((ip, port))
            try:
                self.client.connect((ip, port))
            except socket.timeout:
                debug("Connection timed out. Please check the IP/port and network connectivity.")
                raise
            except ConnectionRefusedError:
                debug("Connection refused. Please ensure the PILOT 'Communications Controller' is running and accessible.")
                raise
            except socket.error as e:
                debug(f"Socket error during connection: {e}. Please check network configuration.")
                raise
            except Exception as e: # Catch other unexpected exceptions
                debug(f"An unexpected error occurred during connection: {e}")
                raise
        
    def disconnect(self):
    def disconnect(self):
        try:
            self.reset_connection()
        finally:
            if hasattr(self, 'client') and self.client:
                self.client.close()

    def configure(self):
        self.switch_motor(1)
        self.move_z_separation()
   
    def unconfigure(self):
        self.move_z_separation()  

    def apply(self):
    
        if self.verbose:
            print("PILOT new setvalue:", self.value)
        die_str = self.sweepvalues["Die"]
        xy, self.index = die_str.split("#")
        self.die_x, self.die_y = xy.split(",")
        if not isinstance(self.value, str):
            self.stop_Measurement("Sweep value must be a string of the 'Die[<x>,<y>]_Sub[<subsite index>#<Label>]'")
            return False
        
        self.move_z_separation()  

        # move to new die xy and subsite
        self.move_die(self.die_x, self.die_y)
        for i in range(self.find_feature_retries):  # if self.find_feature_retries is 0, the loop does not run.

            answer = self.find_feature()
            print("Find feature:", answer)
            self.feature_found = "Executed!" in answer
            
        if self.is_contact_wafer:
        
            if self.find_feature_retries > 0 and not self.feature_found:
                pass
            else:
                self.move_z_contact()
       
    def call(self):
        # most import function:
        # return exactly the number of values that have been defined by self.variables and self.units
        if self.find_feature_retries > 0:
            return [self.index, int(self.die_x), int(self.die_y), self.feature_found]
        else:
            return [self.index, int(self.die_x), int(self.die_y)]
        
    # here further convenience functions are defined

    def write_message(self, cmd, EOL="\n"):
        """This function sends a message over the socket client, which is created in connect() method. The EOL can be
        selected in the PILOT Communication Controller.
        Args:
            cmd: string or integer
            EOL: character

        Returns:
            None
        """
        if self.verbose:
            print("PILOT command:", cmd)
        
        cmd = cmd + EOL
        self.client.send(cmd.encode('latin-1')) # Match the decoding scheme or use the protocol-specified encoding

    def read_message(self, timeout=10):
        """This function reads a message from the socket client.
        Returns:
            string: answer
        """
        start_time = time.time()

        while True:
            try:
                answer = self.client.recv(1024).decode('latin-1')
                if self.verbose:
                    print("PILOT response:", answer)
                return answer[:-3]
            except socket.timeout:
                pass
            
            if time.time() - start_time > timeout:
                raise Exception("Timeout: No answer received for movement commands.")
            
            if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                break

    def load_smt_file(self, path):
        """This function loads wafer navigation map from an .smt file. Right now only the dies coordinates are supported.

        Args:
            path

        Returns:
            navigation_array
        """
        navigation_array = np.genfromtxt(path, delimiter=",", skip_header=16, skip_footer=1)
        # smt_map_info = open(path, "r").readlines()[:16]
        # print(smt_map_info)
        return navigation_array

    # Here wrapped functions start.
    # The method's docstring is collected from the SemiProbe PILOT user manual (Rev 072616).

    def initialize_system(self):
        """PIInitialize - Initialize the probing/inspection system
        
        Returns:
            string: answer
        """
        self.write_message("21")
        answer = self.read_message()
        return answer

    def reset_connection(self):
        # Todo: Check if this command is really needed at the end.
        self.write_message("1")

    def get_xy_position(self):
        """PIGetXYPosition - Get the current X and Y position index of the stage

        Returns:
            x: float
            y: float
        """
        self.write_message("24")
        answer_splitted = self.read_message().split(" ")
        return answer_splitted[-1], answer_splitted[-2]
    
    def get_zt_position(self):
        """PIGetZTPosition - Get the current Z and T position of the stage

        Returns:
            z: float
            T: float
        """
        self.write_message("25")
        answer_splitted = self.read_message().split(" ")
        return answer_splitted[-1], answer_splitted[-2]

    def stop(self):
        """PIEMO - Stop all movement of the prober

        Returns:
            string: answer
        """
        self.write_message("35")
        answer = self.read_message()
        return answer

    def move_load_position(self):
        """PIMoveToLoad - Move the chuck to the load position

        Returns:
            answer: string
        """
        self.write_message("19")
        answer = self.read_message(300)
        return answer

    def move_z_contact(self):
        """PIMoveZContact - Move the chuck to the contact position

        Returns:
            string: answer
        """
        self.write_message("15")
        answer = self.read_message(300)
        return answer

    def move_z_separation(self):
        """PIMoveZSeparation - Move the chuck to the separation position

        Returns:
            string: answer
        """
        self.write_message("16")
        answer = self.read_message(300)
        return answer

    def move_xy_absolute(self, x, y, speed):
        """PIMoveXYAbsolute - Move X and Y to the location specified

        Args:
            x: float
            y: float
            speed: integer
        Returns:
            string: answer
        """
        self.write_message("13 %s %s %s" % (x, y, speed))
        answer = self.read_message(300)
        return answer

    def move_z_absolute(self, z, speed):
        """PIMoveZAbsolute - Move Z to the location specified

        Args:
            z: float
            speed: integer
        Returns:
            string: answer
        """
        self.write_message("14 %s %s" % (z, speed))
        answer = self.read_message(300)
        return answer

    def move_theta_absolute(self, theta, speed):
        """PIMoveThetaAbsolute - Move Theta to the specified location

        Args:
            theta: float
            speed: integer

        Returns:
            string: answer
        """
        self.write_message("17 %s %s" % (theta, speed))
        answer = self.read_message(300)
        return answer
    
    def move_die(self, x, y):
        """SPMMove - Move the map to a specific die location (index)

        Args:
            x: integer
            y: integer

        Returns:
            string: answer
        """
        self.write_message("4000 MoveState= L, X= %s, Y= %s" % (int(x), int(y)))
        answer = self.read_message(300)
        return answer
     
    def move_die_next(self):
        """SPMMove - Move the map to the next die location (index)

        Returns:
            string: answer
        """
        self.write_message("4000 MoveState= N")
        answer = self.read_message(300)
        return answer
    
    def move_die_previous(self):
        """SPMMove - Move the map to the previous die location (index)

        Returns:
            string: answer
        """
        self.write_message("4000 MoveState= P")
        answer = self.read_message(300)
        return answer
        
    def set_die_home(self):
        """SPMSetHome - Set the home die position to the current prober position

        Returns:
            answer: string
        """
        self.write_message("4002")
        answer = self.read_message()
        return answer

    def die_state(self):
        """SPMDieState - Inquire probable status of specified die location

        Returns:
            answer: string
        """
        self.write_message("4007 X= -1, Y= -1")  # do we need it?
        answer = self.read_message()
        return answer
        
    def switch_motor(self, state):
        """PIMotorsOnOff - Will turn the motors to the XYZ and theta axis on or off

        Args:
            state: boolean (also as string and integer)

        Returns:
            string or none: answer
        """
        if state in ["0", "1", 0, 1, True, False]:
            self.write_message("70 MotorState= %s" % int(state))
            answer = self.read_message()
            return answer  
        else:
            raise Exception("The state should be '0' for off or '1' for on")

    def find_feature(self):
        """VFindFeature - Find feature in current die and move to its location

        Returns:
            string: answer
        """
        self.write_message("331")
        answer = self.read_message()
        return answer

    def align_wafer(self):
        """VAlignWafer - Align the Wafer

        Returns:
            string: answer
        """
        self.write_message("329")
        answer = self.read_message()
        return answer

    def go_home(self):
        """VFindHome - Got to the home position

        Returns:
            string: answer
        """
        self.write_message("330")
        answer = self.read_message(300)
        return answer

    def get_score(self):
        """VSetGetScore - Retrieve the previous score result from the last attempt to find a model

        Returns:
            integer: score
        """
        self.write_message("343 Type= G")
        score = self.read_message().split(" ")[-1]
        return int(score)

    def set_score(self, score):
        """VSetGetScore - Set the score to use when looking for a model

        Args:
            score: integer
        Returns:
            string: answer
        """
        score = int(score)
        if 20 < score < 100:
            self.write_message("343 Type= S: Score= %i:" % score)
            answer = self.read_message()
            return answer
        else:
            raise Exception("The score value should be an integer between 20 and 100.")

    def switch_light(self, state):
        """PILightSource - Turns the Microscope Illuminator On or Off.

        Args:
            state: boolean (also as string and integer)

        Returns:
            string or none: answer
        """
        if state in ["0", "1", 0, 1, True, False]:
            self.write_message("53 %s" % int(state))
            answer = self.read_message()
            return answer
        else:
            raise Exception("The state should be '0' for off or '1' for on")
