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

from __future__ import annotations

from typing import Any

# SweepMe! driver
# * Module: Robot
# * Instrument: Dobot MG400

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

import dobot_api
# import importlib 
# importlib.reload(dobot_api)

import select

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver to control a Dobot MG400 robotic arm."""

    # needs to be defined for Robot drivers to define the variables and default values for the axes section
    axes = {
            "x": {
                "Value": 350.0
                },
            "y": {
                "Value": 0.0
                },
            "z": {
                "Value": 0.0
                },   
            "r": {
                "Value": 0.0
                },
            }

    actions = ["go_home"]

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "MG400"  # short name will be shown in the sequencer
            
        self.reach_position_timeout = 30.0

        self._last_xyzr = (None, None, None, None)

        # Measurement Parameters
        self.variables: list[str] = []
        self.units: list[str] = []
        self.plottype: list[bool] = []
        self.savetype: list[bool] = []

        # Communication Parameters
        self.port_string: str = ""
        self.api_dashboard: DobotDashboard
        self.api_move: DobotMove

        self.length_unit: str = "mm"
        self.go_home_start: bool = False
        self.go_home_end: bool = False

        self.payload_weight: float = 0.0
        self.payload_x_offset: float = 0.0
        self.payload_y_offset: float = 0.0
        self.collision_level: str = "5"

        self.acceleration_factor: int = 10
        self.global_speed_factor: int = 100
        self.speed_factor: str = "10"

        self.use_jump_mode: bool = False
        self.movement_height: float = 0.0
            
    def set_GUIparameter(self) -> dict[str, Any]:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "Port": "192.168.1.6",  # Standard IP of first Ethernet port
            "Unit": ["mm"],
            # "Reach position": True,
            "Collision level": ["5", "4", "3", "2", "1", "0"],  # TODO: turn
            "Acceleration factor": 10,
            "Global speed factor": 100,
            "Speed factor": "10",
            "": None,  # Empty line
            "Payload": None,  # Section label
            "Payload weight in kg": 0.0,
            # "Payload inertia in kgm²": 0.0,
            "Payload x offset": 0.0,
            "Payload y offset": 0.0,
            # "Payload z offset": 0.0,
            " ": None,  # Another empty line with a different empty key
            "Jump": None,  # Section label
            "Use jump mode": False,
            "Movement height": 0.0,
            "  ": None,   # Another empty line with a different empty key

            "GoHomeStart": True,
            "GoHomeEnd": True,
        }

    def get_GUIparameter(self, parameter: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.port_string = parameter["Port"]

        self.length_unit = parameter["Unit"]
        # self.reach_position = parameter["Reach position"]
        self.go_home_start = parameter["GoHomeStart"]
        self.go_home_end = parameter["GoHomeEnd"]
        
        self.payload_weight = parameter["Payload weight in kg"]
        # self.payload_inertia = parameter["Payload inertia in kgm²"]
        self.payload_x_offset = parameter["Payload x offset"]
        self.payload_y_offset = parameter["Payload y offset"]
        # self.payload_z_offset = parameter["Payload z offset"]
        self.collision_level = parameter["Collision level"]

        self.acceleration_factor = parameter["Acceleration factor"]
        self.global_speed_factor = parameter["Global speed factor"]
        self.speed_factor = parameter["Speed factor"]

        self.use_jump_mode = parameter["Use jump mode"]  # Activates jump mode
        self.movement_height = float(parameter["Movement height"])  # Lateral movement height in jump mode
        
        self.variables = ["x", "y", "z", "r"] 
        self.units = [self.length_unit] * 3 + ["°"]
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)
        
    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        port_api_dashboard = 29999
        port_api_move = 30003
        
        self.api_dashboard = DobotDashboard(self.port_string, port_api_dashboard)
        self.api_move = DobotMove(self.port_string, port_api_move)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        if hasattr(self, "api_dashboard"):
            self.api_dashboard.close()
        if hasattr(self, "api_move"):
            self.api_move.close()
        
    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self.clear_error()
        self.reset_robot()

        self.set_collision_level(self.collision_level)

        # first without any parameters. Otherwise, the robot tends to throw error 105 "Servo on failed"
        self.enable_robot()
        self.enable_robot(self.payload_weight, self.payload_x_offset, self.payload_y_offset, 0.0)

        # The line below should be used to set payload properties. However, the command did not work correctly
        # and now payload properties are handed over during self.enable_robot()
        # self.set_payload(self.payload_weight, self.payload_inertia)

        if self.go_home_start:
            self.go_home()
        
    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        if self.go_home_end:
            self.go_home()
            
        self.disable_robot()

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.set_acceleration_linear(self.acceleration_factor)  # Linear acceleration factor 1-100
        self.set_speed_global(self.global_speed_factor)  # Global speed factor 1-100
        self.set_speed_linear(self.speed_factor)  # Linear speed factor 1-100
        self._last_xyzr = self.get_position()

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        if self.use_jump_mode:
            self.move_linear(self._last_xyzr[0], self._last_xyzr[1], self.movement_height, self._last_xyzr[3])
            self.sync(self.reach_position_timeout)

    def reconfigure(self, parameters, keys) -> None:
        """'reconfigure' is called whenever parameters of the GUI change by using the {...}-parameter system."""
        if "Speed factor" in keys:
            self.speed_factor = parameters["Speed factor"]
            self.set_speed_linear(self.speed_factor)  # Linear speed factor 1-100

    def apply(self) -> None:
        """This function is called if the set value has changed. Applies the new value available as self.value."""
        # Position
        if "x" in self.sweepvalues and self.sweepvalues["x"] != "nan":
            x = float(self.sweepvalues["x"])
        else: 
            x = self._last_xyzr[0]
            
        if "y" in self.sweepvalues and self.sweepvalues["y"] != "nan":
            y = float(self.sweepvalues["y"])
        else: 
            y = self._last_xyzr[1]

        if "z" in self.sweepvalues and self.sweepvalues["z"] != "nan":
            z = float(self.sweepvalues["z"])
        else: 
            z = self._last_xyzr[2]
                    
        if "r" in self.sweepvalues and self.sweepvalues["r"] != "nan":
            r = float(self.sweepvalues["r"])   
        else: 
            r = self._last_xyzr[3]     

        if self._last_xyzr != (x, y, z, r):

            if self.use_jump_mode:

                # we only move to movement height if x, y, or r change
                # in case of a z scan, we do not need to go back to movement height                
                if self._last_xyzr[0:2] != (x, y) or self._last_xyzr[3] != r:

                    # vertical move to movement height
                    self.move_linear(self._last_xyzr[0], self._last_xyzr[1], self.movement_height, self._last_xyzr[3])
                    self.sync(self.reach_position_timeout)

                    # lateral move at movement height
                    self.move_linear(x, y, self.movement_height, r)
                    self.sync(self.reach_position_timeout)

            self.move_linear(x, y, z, r)
            self._last_xyzr = (x, y, z, r)

    def reach(self) -> None:
        """'reach' can be added to make sure the latest setvalue applied during 'apply' is reached."""
        self.sync(self.reach_position_timeout)  # wait to finish all commands in queue
                    
    def call(self) -> tuple[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        x, y, z, r = self.get_position()
        return x, y, z, r

    def enable_robot(self, *args) -> None:
        response = self.api_dashboard.EnableRobot(args)
        status = response.split(",")[0]
        if status == "-1":
            msg = (f"EnableRobot() failed. Check if 'Remote Control - Mode' was set to 'TCP/IP "
                   f"Secondary Development' in DobotStudioPro.")
            raise Exception(msg)

    def disable_robot(self) -> None:
        self.api_dashboard.DisableRobot()
        
    def clear_error(self) -> None:
        self.api_dashboard.ClearError()
        
    def reset_robot(self) -> None:
        self.api_dashboard.ResetRobot()
        
    def set_payload(self, weight, inertia) -> None:
        self.api_dashboard.PayLoad(float(weight), float(inertia))
        
    def set_collision_level(self, level) -> None:
        self.api_dashboard.SetCollisionLevel(level)
        
    def set_speed_global(self, factor) -> None:
        self.api_dashboard.SpeedFactor(int(float(factor)))  # Global speed factor 1-100
        
    def set_speed_linear(self, speed) -> None:
        self.api_dashboard.SpeedL(int(float(speed)))

    def set_acceleration_linear(self, acc) -> None:
        self.api_dashboard.AccL(int(float(acc)))

    def get_robot_mode(self):
        mode = self.api_dashboard.RobotMode()
        return mode
        
    def move_linear(self, x, y, z, r) -> None:
        print(f"Moving to x={x} y={y} z={z} r={r}")
        self.api_move.MovL(x, y, z, r)  # linear move to home position
        
    def go_home(self) -> None:
        self.move_linear(350.0, 0.0, 0.0, 0.0)  # linear move to home position
        self.sync()
        self._last_xyzr = self.get_position()
                
    def sync(self, timeout=10.0) -> None:
        self.api_move.Sync(timeout) 
        
    def get_pose(self):
        answer = self.api_dashboard.GetPose()  # added function
        x,y,z,r = tuple(map(float, self.get_response_data(answer)[0:4]))
        print(f"Current position: x={x} y={y} z={z} r={r}")
        return x,y,z,r
      
    def get_position(self):
        return self.get_pose()
        
    def get_angles(self):
        answer = self.api_dashboard.GetAngle()
        a,b,c,r = answer
        return a,b,c,r

    @staticmethod
    def get_response_data(msg):
        lindex = msg.find("{")+1
        rindex = msg.find("}")
        data_string = msg[lindex:rindex]
        return data_string.split(",")


class DobotDashboard(dobot_api.DobotApiDashboard):

    # def log(self, text):
    #     pass
    #     print(text)

    def is_package_ready(self, timeout = 0.0):
        ready, _, _ = select.select([self.socket_dobot], [], [], timeout)
        return not not ready  # first "not" makes a bool, second "not" negates the bool to what is needed

    def send_data(self, string):
        self.log(f"Send: {string}")
        self.socket_dobot.send(str.encode(string, 'utf-8'))

    def wait_reply(self, timeout=3.0):
        """
        Read the return value
        """
        if self.is_package_ready(timeout=timeout):
            data = self.socket_dobot.recv(1024)
            data_str = str(data, encoding="utf-8")
            self.log(f'Receive: {data_str}')
            return data_str
        else:
            raise Exception("No package returned within timeout.")

    def EnableRobot(self, *args):
        """
        Enable the robot
        """
        # string = "EnableRobot({:f},{:f},{:f},{:f})".format(float(mass), float(x), float(y), float(z))
        # string = "EnableRobot({:f})".format(float(mass))
                
        if len(*args) == 0:
            string = "EnableRobot()"
        elif len(*args) == 1:
            string = "EnableRobot({:f})".format(float(*args[0]))
        elif len(*args) == 4:
            string = "EnableRobot({:f},{:f},{:f},{:f})".format(*tuple(map(float, *args)))
        else:
            raise Exception("EnableRobot() requires 0, 1, or 4 parameters")
            
        self.send_data(string)
        return self.wait_reply()

    def GetPose(self):
        """
        Retrieve position in cartesian coordinates
        """
        string = "GetPose()"
        self.send_data(string)
        return self.wait_reply()

    def GetAngle(self):
        """
        Retrieve angles of all joints
        """
        string = "GetAngle()"
        self.send_data(string)
        return self.wait_reply()

    def SetCollisionLevel(self, level):
        """
        Set the collision level
        collision level:
            0: switch off collision detection
            1~5: more sensitive with higher level
        """
        string = "SetCollisionLevel({:d})".format(int(level))
        self.send_data(string)
        return self.wait_reply()

    def ToolDO(self, index, status):
        """
        Set digital signal output at the robotic arm (Queue instruction). If you want to set the digital outputs at the
        back panel of the robot, use DO(index, status).
        index : Digital output index (Value range:1~2)
        status : Status of digital signal output port(0:Low level，1:High level
        """
        string = "ToolDO({:d},{:d})".format(index, status)
        self.send_data(string)
        return self.wait_reply()


class DobotMove(dobot_api.DobotApiMove):

    # def log(self, text):
    #     pass
    #     print(text)

    def is_package_ready(self, timeout = 0.0):
        ready, _, _ = select.select([self.socket_dobot], [], [], timeout)
        return not not ready  # first "not" makes a bool, second "not" negates the bool to what is needed

    def send_data(self, string):
        self.log(f"Send move: {string}")
        self.socket_dobot.send(str.encode(string, 'utf-8'))

    def wait_reply(self, timeout=3.0):
        """
        Read the return value
        """
        if self.is_package_ready(timeout=timeout):
            data = self.socket_dobot.recv(1024)
            data_str = str(data, encoding="utf-8")
            self.log(f'Receive move: {data_str}')
            return data_str
        else:
            raise Exception("No package returned within timeout.")
            
    def Sync(self, timeout = 10.0):
        """
        The blocking program executes the queue instruction and returns after all the queue instructions are executed
        """
        string = "Sync()"
        self.send_data(string)
        return self.wait_reply(timeout)
