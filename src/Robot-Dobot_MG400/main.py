# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022-2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Robot
# * Instrument: Dobot MG400

from __future__ import annotations

import importlib
import json
import select
import socket
import time
from typing import Any

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

import dobot_alarms
import dobot_api

# SweepMe! reloads this file automatically when it changes, but modules from the libs folder stay cached in
# sys.modules. Reload them here so that a driver update does not run with stale library code.
importlib.reload(dobot_alarms)
importlib.reload(dobot_api)

from pysweepme.EmptyDeviceClass import EmptyDevice


DEBUG_MODE: bool = False


class DobotConnectionError(Exception):
    """Raised when the TCP connection to the robot cannot be established or is lost."""


class DobotTimeoutError(Exception):
    """Raised when the robot does not reply to a command within the timeout."""


class DobotResponseError(Exception):
    """Raised when the robot replies to a command with a non-zero error code."""


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

        # Set when a movement fails (collision, timeout, alarm). Used to skip the 'go home at end' movement,
        # so that the robot pauses where it stopped instead of moving through a possibly blocked path.
        self._motion_error: bool = False

        # Target of the last movement command. sync() verifies that this position is actually reached,
        # because the Sync() reply of the robot can arrive while the robot is still moving.
        self._last_target: tuple[float, float, float, float] | None = None

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

        # If anything fails during connect, close the sockets that were already opened. Otherwise, a stale
        # connection stays open in the SweepMe! process and the robot rejects the next run as second client.
        try:
            self.api_dashboard = DobotDashboard(self.port_string, port_api_dashboard)
            self.api_move = DobotMove(self.port_string, port_api_move)

            # A robot that is not in remote control mode accepts the TCP connection but does not answer
            # commands. Check the communication here to give a clear message instead of a timeout at the
            # first real command.
            try:
                mode = self.get_robot_mode()
            except DobotTimeoutError as exc:
                msg = (
                    f"The robot at {self.port_string} accepted the TCP connection but does not answer "
                    "commands. Connect to the robot with DobotStudioPro and set 'Configuration -> Remote "
                    "Control -> Current Mode' to 'TCP/IP Secondary Development'. If the mode is already set, "
                    "another program might be blocking the robot or the controller needs a restart."
                )
                raise DobotConnectionError(msg) from exc
        except Exception:
            self.disconnect()
            raise

        if DEBUG_MODE:
            mode_name = dobot_alarms.ROBOT_MODES.get(mode, "unknown")
            print(f"MG400: connected, robot mode is {mode} ({mode_name})")

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        if hasattr(self, "api_dashboard"):
            self.api_dashboard.close()
        if hasattr(self, "api_move"):
            self.api_move.close()
        
    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        self._motion_error = False
        self.clear_error()
        self.reset_robot()

        # first without any parameters. Otherwise, the robot tends to throw error 105 "Servo on failed"
        self.enable_robot()
        self.enable_robot(self.payload_weight, self.payload_x_offset, self.payload_y_offset, 0.0)

        self.set_collision_level(self.collision_level)
        self.set_collision_response_pause()

        # The line below should be used to set payload properties. However, the command did not work correctly
        # and now payload properties are handed over during self.enable_robot()
        # self.set_payload(self.payload_weight, self.payload_inertia)

        if self.go_home_start:
            self.go_home()
        
    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""
        if not hasattr(self, "api_dashboard"):
            return  # connect() failed - there is nothing to move or to disable

        try:
            if self.go_home_end:
                try:
                    has_alarm, alarm_message = self.read_alarms()
                except Exception:
                    has_alarm = True  # robot state unknown - do not risk a movement
                    alarm_message = "The robot alarms could not be read."
                if self._motion_error or has_alarm:
                    # Safety: after a collision or failed movement the robot must pause where it stopped
                    # instead of moving to the home position through a possibly blocked path.
                    print(
                        "MG400: skipping 'go home at end' because a movement failed or the robot has alarms. "
                        "The robot stays at its current position.\n" + alarm_message
                    )
                else:
                    self.go_home()
        finally:
            # disabling must not raise a secondary error during shutdown, e.g. when the connection was lost
            try:
                self.disable_robot()
            except Exception as exc:
                print(f"MG400: could not disable the robot during shutdown: {exc}")

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.set_acceleration_linear(self.acceleration_factor)  # Linear acceleration factor 1-100
        self.set_speed_global(self.global_speed_factor)  # Global speed factor 1-100
        self.set_speed_linear(self.speed_factor)  # Linear speed factor 1-100
        self._last_xyzr = self.get_position()

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""
        if not hasattr(self, "api_move"):
            return  # connect() failed - there is nothing to move
        if self.use_jump_mode and not self._motion_error:
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
                    
    def call(self) -> tuple[float, float, float, float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        x, y, z, r = self.get_position()
        return x, y, z, r

    def enable_robot(self, *args) -> None:
        response = self.api_dashboard.EnableRobot(args)
        try:
            status = int(response.split(",")[0])
        except ValueError:
            msg = f"EnableRobot() returned an unreadable response: {response}"
            raise Exception(msg) from None
        if status != 0:
            msg = (
                f"EnableRobot() failed with error code {status}: {dobot_alarms.describe_response_error(status)} "
                "Check if 'Remote Control - Mode' was set to 'TCP/IP Secondary Development' in DobotStudioPro "
                "and that no emergency stop is active."
            )
            try:
                has_alarm, alarm_message = self.read_alarms()
            except Exception:
                has_alarm = False
                alarm_message = ""
            if has_alarm:
                msg += f"\nActive robot alarms:\n{alarm_message}"
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

    def set_collision_response_pause(self) -> None:
        """Set the robot to pause at its current position after detecting a collision.

        Older firmware versions may not support the SetPostCollisionMode command. In that case a note is
        printed and the response configured in DobotStudioPro applies - set it to 'pause' there.
        """
        try:
            self.api_dashboard.SetPostCollisionMode(1)  # 1: pause status after a collision
        except DobotResponseError as exc:
            if "-10000" in str(exc):  # command does not exist on this firmware
                print(
                    "MG400: this firmware does not support setting the collision response via TCP. The "
                    "response configured in DobotStudioPro applies - set it to 'pause' there, or update "
                    "the robot firmware."
                )
            else:
                raise
        
    def set_speed_global(self, factor) -> None:
        self.api_dashboard.SpeedFactor(int(float(factor)))  # Global speed factor 1-100
        
    def set_speed_linear(self, speed) -> None:
        self.api_dashboard.SpeedL(int(float(speed)))

    def set_acceleration_linear(self, acc) -> None:
        self.api_dashboard.AccL(int(float(acc)))

    def get_robot_mode(self) -> int:
        """Read the current robot mode. See dobot_alarms.ROBOT_MODES for the meaning of the values."""
        response = self.api_dashboard.RobotMode()
        return int(self.get_response_data(response)[0])

    def move_linear(self, x, y, z, r) -> None:
        """Linear move to the given cartesian coordinates.

        If the position is out of the robot's working range, the robot will beep and go into error state.
        When the robot is controlled remotely, this is only noticed when the next move command is sent and results in a
        timeout. To prevent the timeout, the error state is checked after each movement.
        """
        self.api_move.MovL(x, y, z, r)
        self._last_target = (float(x), float(y), float(z), float(r))
        has_alarm, alarm_message = self.read_alarms()
        if has_alarm:
            self._motion_error = True
            msg = (
                f"MovL({x}, {y}, {z}, {r}) failed. Check if the position is within the robot's working range.\n"
                f"Robot alarms:\n{alarm_message}"
            )
            raise Exception(msg)

    def read_alarms(self) -> tuple[bool, str]:
        """Read the robot alarms via GetErrorID() and return them as human-readable text.

        Returns:
            Tuple of a bool indicating whether at least one alarm is active and a string describing all active
            alarms, one per line.
        """
        response = self.api_dashboard.GetErrorID()
        # The response has the format "ErrorID,{[[id,...], [id], ...]},GetErrorID();". The first inner list holds
        # the controller/algorithm alarms, the following lists hold the servo alarms of the individual joints.
        try:
            alarm_lists = json.loads(response[response.find("{") + 1 : response.rfind("}")])
        except (ValueError, json.JSONDecodeError):
            # Fallback for unknown response formats: a response longer than the empty alarm structure indicates
            # an alarm, but the ids cannot be extracted.
            return len(response) > 51, f"The robot alarm response could not be parsed: {response}"
        has_alarm = any(alarm_id != 0 for alarms in alarm_lists for alarm_id in alarms)
        return has_alarm, dobot_alarms.describe_alarms(alarm_lists)

    def has_error(self) -> bool:
        """Readout the robot alarms and return True if at least one alarm is active."""
        has_alarm, _ = self.read_alarms()
        return has_alarm
        
    def go_home(self) -> None:
        """Move the robot to the fixed home position.

        Besides being called during initialize/deinitialize, this method is triggered by the 'Go home' button
        of the Robot module, which connects to the robot but skips the initialization, and by driver actions,
        which do not even connect. The robot state is therefore checked first to give a readable message
        instead of running into a Sync timeout on a robot that cannot move.
        """
        if not hasattr(self, "api_dashboard"):
            msg = (
                "Cannot go home: the driver is not connected to the robot. "
                "This can happen when 'go_home' is triggered as a driver action outside of a run."
            )
            raise Exception(msg)

        mode = self.get_robot_mode()
        if mode == dobot_alarms.ROBOT_MODE_ERROR:
            msg = "Cannot go home: the robot is in an error state. Clear the error first, e.g. by starting a run."
            has_alarm, alarm_message = self.read_alarms()
            if has_alarm:
                msg += f"\nRobot alarms:\n{alarm_message}"
            raise Exception(msg)

        # A collision stop can leave the robot enabled (mode 5) with the alarm still pending, so the alarms
        # must be checked in addition to the mode before moving through a possibly blocked path.
        has_alarm, alarm_message = self.read_alarms()
        if has_alarm:
            msg = (
                "Cannot go home: the robot has active alarms and might move through a blocked path. "
                f"Clear the error first, e.g. by starting a run.\nRobot alarms:\n{alarm_message}"
            )
            raise Exception(msg)

        was_disabled = mode == dobot_alarms.ROBOT_MODE_DISABLED
        if was_disabled:
            # convenience for the 'Go home' button: enable a disabled robot temporarily for the homing move
            self.enable_robot()  # first without parameters to avoid error 105 "Servo on failed"
            self.enable_robot(self.payload_weight, self.payload_x_offset, self.payload_y_offset, 0.0)
        elif mode not in (dobot_alarms.ROBOT_MODE_ENABLED, dobot_alarms.ROBOT_MODE_RUNNING):
            mode_name = dobot_alarms.ROBOT_MODES.get(mode, "unknown")
            msg = (
                f"Cannot go home: the robot is '{mode_name}' (mode {mode}) and will not execute movements. "
                "Enable the robot first, e.g. with the 'Apply' button, by starting a run, or in DobotStudioPro."
            )
            raise Exception(msg)

        try:
            self.move_linear(350.0, 0.0, 0.0, 0.0)  # linear move to home position
            self.sync(self.reach_position_timeout)
            self._last_xyzr = self.get_position()
        finally:
            if was_disabled:
                self.disable_robot()  # restore the state the robot was found in
                
    def sync(self, timeout=10.0) -> None:
        """Wait until the robot has reached the target of the last movement command.

        The Sync() reply of the robot is not reliable: it can arrive while the robot is still moving
        (observed with the go-home movement). Therefore, the position is polled until the target of the
        last movement command is reached. While waiting, alarms, the robot mode, and a standstill of the
        robot are checked, so that an interrupted movement (e.g. a collision pause, which old firmware does
        not report at all) is detected within about two seconds.
        """
        target = self._last_target
        self.api_move.send_data("Sync()")
        sync_replied = False
        end_time = time.time() + timeout
        standstill_polls = 0  # consecutive polls in which the robot position did not change
        last_pose: tuple[float, float, float, float] | None = None

        while True:
            sync_replied = self._wait_poll_interval(sync_replied)

            # user pressed stop: end the wait, stop the robot, and let SweepMe! shut down regularly
            if self.is_run_stopped():
                self.reset_robot()
                return

            self._abort_if_alarms(
                "The movement was interrupted - the robot reported alarms and pauses at its current position:"
            )
            self._abort_if_pause_or_error_mode()

            pose = self.get_position()
            if self._is_target_reached(pose, target):
                break
            if target is None and sync_replied:
                break  # no movement command sent before: the Sync reply is the only signal available

            standstill_polls = standstill_polls + 1 if self._is_standstill(pose, last_pose) else 0
            last_pose = pose
            if standstill_polls >= 3:
                self._motion_error = True
                msg = (
                    "The movement was interrupted - the robot has not moved for about 2 seconds without "
                    f"reaching the target position {target}, it stands at {pose}. Most likely a collision "
                    "paused the movement. The robot stays at its current position. Remove the obstacle and "
                    "start a new run to clear the state."
                )
                raise Exception(msg)

            if time.time() > end_time:
                self._motion_error = True
                msg = (
                    f"The robot did not reach the target position within {timeout} s. Possible reasons: the "
                    "movement is slow (low speed factor) and needs a larger timeout, or the motion queue is "
                    "blocked. To recover a blocked queue, start a new run or restart the robot."
                )
                raise Exception(msg)

        # an alarm can also appear right at the end of the movement, e.g. when stopping at the target
        self._abort_if_alarms(
            "The robot reported alarms during the movement and may have stopped short of the target position:"
        )

    def _wait_poll_interval(self, sync_replied: bool) -> bool:
        """Wait one polling interval of 0.5 s and consume the Sync reply when it arrives.

        The reply only signals that the motion queue was processed - it can arrive while the robot is still
        moving, so it is no proof that the movement is finished.
        """
        if sync_replied:
            time.sleep(0.5)
            return True
        if self.api_move.is_package_ready(timeout=0.5):
            self.api_move.wait_reply(timeout=1.0)
            return True
        return False

    def _abort_if_alarms(self, description: str) -> None:
        """Read the robot alarms and raise an exception with the given description if one is active."""
        has_alarm, alarm_message = self.read_alarms()
        if has_alarm:
            self._motion_error = True
            raise Exception(f"{description}\n{alarm_message}")

    def _abort_if_pause_or_error_mode(self) -> None:
        """Raise an exception if the robot changed to the pause or error mode, e.g. after a collision.

        A collision with response 'pause' interrupts the movement without reporting an alarm - newer
        firmware at least changes to the pause mode.
        """
        mode = self.get_robot_mode()
        if mode in (dobot_alarms.ROBOT_MODE_PAUSE, dobot_alarms.ROBOT_MODE_ERROR):
            self._motion_error = True
            mode_name = dobot_alarms.ROBOT_MODES.get(mode, "unknown")
            msg = (
                f"The movement was interrupted - the robot is '{mode_name}' (mode {mode}), most likely "
                "because a collision was detected. The robot stays at its current position. Remove the "
                "obstacle and start a new run to clear the state."
            )
            raise Exception(msg)

    @staticmethod
    def _is_target_reached(
        pose: tuple[float, float, float, float],
        target: tuple[float, float, float, float] | None,
        tolerance: float = 0.1,
    ) -> bool:
        """Check whether the position matches the movement target within the tolerance (in mm and deg)."""
        return target is not None and all(abs(a - b) <= tolerance for a, b in zip(pose, target))

    @staticmethod
    def _is_standstill(
        pose: tuple[float, float, float, float],
        last_pose: tuple[float, float, float, float] | None,
        tolerance: float = 0.01,
    ) -> bool:
        """Check whether the position did not change since the last poll (within the tolerance in mm/deg).

        A robot that stands still away from the target has been stopped, most likely by a collision - old
        firmware reports neither an alarm nor the pause mode in this case, but DobotStudioPro shows the
        warning.
        """
        return last_pose is not None and all(abs(a - b) <= tolerance for a, b in zip(pose, last_pose))
        
    def get_pose(self) -> tuple[float, float, float, float]:
        answer = self.api_dashboard.GetPose()  # added function
        x,y,z,r = tuple(map(float, self.get_response_data(answer)[0:4]))
        return x,y,z,r
      
    def get_position(self) -> tuple[float, float, float, float]:
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


class DobotSocket:
    """Mixin that replaces the connection and reply handling of dobot_api with detailed error messages."""

    connect_timeout: float = 5.0

    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port
        self.socket_dobot = 0
        self.text_log = None
        self.last_command = ""
        try:
            self.socket_dobot = socket.create_connection((ip, port), timeout=self.connect_timeout)
        except socket.timeout as exc:
            msg = (
                f"Connecting to the robot at {ip}:{port} timed out after {self.connect_timeout} s. "
                "Check that the robot is powered on and has finished booting (takes about 1 minute), that the "
                "Ethernet cable is connected, and that this PC uses a static IP address in the subnet of the "
                "robot, e.g. 192.168.1.5 with subnet mask 255.255.255.0 when using the first Ethernet port of "
                "the robot (192.168.1.6)."
            )
            raise DobotConnectionError(msg) from exc
        except ConnectionRefusedError as exc:
            msg = (
                f"The robot at {ip}:{port} refused the connection. Possible reasons: another program is "
                "blocking the port, a previous connection was not closed yet, or the controller firmware is "
                "older than 1.6.0.0, which has a known issue with TCP connections (update the robot firmware "
                "in this case). Restarting the robot can also help."
            )
            raise DobotConnectionError(msg) from exc
        except OSError as exc:
            msg = (
                f"Could not connect to the robot at {ip}:{port} ({exc}). Check the network configuration: this "
                "PC needs a static IP address in the subnet of the robot, e.g. 192.168.1.5 with subnet mask "
                "255.255.255.0 when using the first Ethernet port of the robot (192.168.1.6)."
            )
            raise DobotConnectionError(msg) from exc

    def is_package_ready(self, timeout: float = 0.0) -> bool:
        ready, _, _ = select.select([self.socket_dobot], [], [], timeout)
        return bool(ready)

    def raise_connection_closed(self) -> None:
        """Raise an error explaining that the robot closed the connection.

        A closed socket stays readable in select() and recv() returns empty bytes, which must not be mistaken
        for a reply. The MG400 only serves the first client that connects to each port: further connections are
        accepted on TCP level but closed again without ever answering a command.
        """
        msg = (
            f"The robot at {self.ip}:{self.port} closed the connection. The MG400 only serves the first "
            "client on each TCP port, so most likely another program or PC is already connected to the robot "
            "(e.g. another SweepMe! instance, a Python script, or a stale connection of a crashed run or "
            "another PC). DobotStudioPro uses a separate channel and does not block these ports. "
            "Close the other connection or restart the robot to free the port."
        )
        raise DobotConnectionError(msg)

    def send_data(self, string: str) -> None:
        # Discard stale replies of earlier commands that ran into a timeout, so that the next reply that is
        # read belongs to the command sent here.
        while self.is_package_ready():
            stale = self.socket_dobot.recv(1024)
            if not stale:
                self.raise_connection_closed()
            if DEBUG_MODE:
                self.log(f"Discard stale reply: {str(stale, encoding='utf-8')}")

        self.last_command = string
        if DEBUG_MODE:
            self.log(f"Send to {self.ip}:{self.port}: {string}")
        try:
            self.socket_dobot.send(str.encode(string, "utf-8"))
        except OSError as exc:
            msg = (
                f"Sending '{string}' to the robot at {self.ip}:{self.port} failed ({exc}). "
                "The connection to the robot was probably lost."
            )
            raise DobotConnectionError(msg) from exc

    def wait_reply(self, timeout: float = 3.0, check: bool = True) -> str:
        """Read the reply of the last sent command and check its error code."""
        if not self.is_package_ready(timeout=timeout):
            msg = (
                f"The robot did not reply to '{self.last_command}' within {timeout} s. Possible reasons: "
                "the remote control mode is not set to 'TCP/IP Secondary Development' in DobotStudioPro, "
                "the robot is in an alarm state, or the motion queue is blocked."
            )
            raise DobotTimeoutError(msg)
        data = self.socket_dobot.recv(1024)
        if not data:
            self.raise_connection_closed()
        data_str = str(data, encoding="utf-8")
        if DEBUG_MODE:
            self.log(f"Receive from {self.ip}:{self.port}: {data_str}")
        if check:
            self.check_response(data_str)
        return data_str

    def check_response(self, response: str) -> None:
        """Raise a readable exception if the leading ErrorID of a command response is non-zero."""
        try:
            error_id = int(response.split(",", 1)[0])
        except ValueError:
            return  # the response does not follow the "ErrorID,{...},Command();" format
        if error_id != 0:
            msg = (
                f"The robot answered '{self.last_command}' with error code {error_id}: "
                f"{dobot_alarms.describe_response_error(error_id)}"
            )
            raise DobotResponseError(msg)


class DobotDashboard(DobotSocket, dobot_api.DobotApiDashboard):

    def ClearError(self):
        """Clear controller alarms. Not checked because it is used to recover from alarm states."""
        self.send_data("ClearError()")
        return self.wait_reply(check=False)

    def ResetRobot(self):
        """Stop the robot. Not checked because it is used to recover from alarm states."""
        self.send_data("ResetRobot()")
        return self.wait_reply(check=False)

    def DisableRobot(self):
        """Disable the robot. Not checked because it is called during shutdown."""
        self.send_data("DisableRobot()")
        return self.wait_reply(check=False)

    def EnableRobot(self, *args):
        """
        Enable the robot
        """
        if len(*args) == 0:
            string = "EnableRobot()"
        elif len(*args) == 1:
            string = "EnableRobot({:f})".format(float(*args[0]))
        elif len(*args) == 4:
            string = "EnableRobot({:f},{:f},{:f},{:f})".format(*tuple(map(float, *args)))
        else:
            raise Exception("EnableRobot() requires 0, 1, or 4 parameters")

        self.send_data(string)
        return self.wait_reply(check=False)  # the error code is evaluated in Device.enable_robot

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

    def SetPostCollisionMode(self, mode):
        """
        Set the status the robot enters after detecting a collision
            0: stop status
            1: pause status
        """
        string = "SetPostCollisionMode({:d})".format(int(mode))
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


class DobotMove(DobotSocket, dobot_api.DobotApiMove):

    def Sync(self, timeout = 10.0):
        """
        The blocking program executes the queue instruction and returns after all the queue instructions are executed
        """
        string = "Sync()"
        self.send_data(string)
        return self.wait_reply(timeout)
