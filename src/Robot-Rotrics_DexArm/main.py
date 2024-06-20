# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 - 2022 SweepMe! GmbH (sweep-me.net)
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
# Type: Robot
# Device: Rotrics DexArm

from FolderManager import addFolderToPATH

addFolderToPATH()

import pydexarm
import importlib 
importlib.reload(pydexarm)
import re

import time

from ErrorMessage import error, debug
from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!

class Device(EmptyDevice):
    description = """
                    <p>Driver for a Rotrics DexArm robot to handover x,y,z coordinates.</p>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>At the beginning, we recommend to update the firmware v2.3.5 of the robot which is needed to retrieve real positions.&nbsp;Otherwise, only setpoint values are returned for x, y, and z</li>
                    <li>Use the jump mode, to move to a new position by doing a jump via the movement height, i.e. the robot arm is lifted up and laterally moved to go to the new position.&nbsp;</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Coordinates:</strong></p>
                    <ul>
                    <li>Home position: x=0, y=300, z=0</li>
                    <li>y: horizonal direction of the robot arm in the home position</li>
                    <li>x: horizontal direction perpendicular to y</li>
                    <li>z: vertical direction perpendicular to x and y&nbsp;</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Parameters:</strong></p>
                    <ul>
                    <li>'Pump state' expects a bool or an integer being 0 and 1.</li>
                    <li>'Laser state' expects an integer in the range 0 to 255.</li>
                    <li>'Rotation angle in &deg;' expects an integer in the range 0 to 360.&nbsp;</li>
                    <li>'Reach position' must be checked if the driver should block until a new position or state is reached</li>
                    <li>'Use jump mode' activates the use of the jump mode where the robot arm is doing lateral movements at a movement height.</li>
                    <li>'Movement height' is the height at which lateral movement are done in jump mode.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Caution:</strong></p>
                    <p>If you use this instrument driver with the laser module, please use a cover box and laser safety goggles to prevent damage to your body and your eyes. In case of an error, it might happen that the laser is not switched off after the program run.</p>
                    """

    axes = {
        "x": {
            "Value": 0.0
        },
        "y": {
            "Value": 300.0
        },
        "z": {
            "Value": 0.0
        },
        "Pump state": {
            "Value": 0.0
        },
        "Laser state": {
            "Value": 0
        },
        "Rotation angle in °": {
            "Value": 0.0
        },
    }

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "DexArm"  # short name will be shown in the sequencer

        self.port_manager = True

        self.port_types = ["COM"]

        self.port_properties = {
            "baudrate": 115200,
            "timeout": 5,
        }

        self.module_type_dict = {
            "Pen": 0,
            "Laser": 1,
            "Pump": 2,
            "Printing": 3,
            "Rotation": 6,

        }

    def set_GUIparameter(self):

        gui_parameter = {
            "Unit": ["mm", "inch"],
            "Speed in unit/s": "1000",
            "Acceleration": "120",
            "Module type": list(self.module_type_dict.keys()),
            "Reach position": True,
            "GoHomeStart": True,
            "GoHomeEnd": True,

            "": None,
            "Jump": None,
            "Use jump mode": False,
            "Movement height": "0.0",
        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.speed = parameter["Speed in unit/s"]
        self.length_unit = parameter["Unit"]
        self.acceleration = parameter["Acceleration"]
        self.module_type = parameter["Module type"]
        self.use_jump_mode = parameter["Use jump mode"]
        self.movement_height = parameter["Movement height"]
        
        self.reach_position = parameter["Reach position"]
        self.go_home_start = parameter["GoHomeStart"]
        self.go_home_end = parameter["GoHomeEnd"]

        self.variables = ["x", "y", "z"]
        self.units = [self.length_unit] * 3
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

    def connect(self):
        ### called only once at the start of the measurement
        ### this function 'connect' is typically not needed if the port manager is activated

        def _send_cmd(data, wait=True):
            """ Functions is used to overwrite the function of pydexarm lib to use SweepMe!'s port manager"""

            self.port.port.reset_input_buffer()
            self.port.write(data)

            if wait:
                while True:
                    serial_str = self.port.read()
                    if len(serial_str) > 0:
                        if "ok" in serial_str:
                            # print("read ok")
                            break
                        elif "HOME" in serial_str:  # "Send M1112 or click HOME to initialize DexArm first before any motion."
                            raise Exception("Please use 'Go home at start' or 'Go home' button at first use")
                        else:
                            pass
                            # print("read：", serial_str)
                        
        def get_current_position():

            self.port.port.reset_input_buffer()
            self.port.write('M114\r')

            x, y, z, e, a, b, c = [float('nan')] * 7

            # even though we use reset_input_buffer() at the beginning
            # it can happen that 'ok' is retrieved before the answer to M114
            # we have to make sure to wait until a position is read
            # Otherwise no position values will be returned
            is_position_read = False

            while True:
                serial_str = self.port.read()
                # print("serial string", serial_str)

                if "X:" in serial_str:

                    temp = re.findall(r"[-+]?\d*\.\d+|\d+", serial_str)
                    x = float(temp[0])
                    y = float(temp[1])
                    z = float(temp[2])

                    # newer firmware versions send the real position, but without the feed rate
                    if "Real position" not in serial_str:
                        e = float(temp[3])

                    is_position_read = True

                elif "DEXARM Theta" in serial_str:
                    temp = re.findall(r"[-+]?\d*\.\d+|\d+", serial_str)
                    a = float(temp[0])
                    b = float(temp[1])
                    c = float(temp[2])
                    return x, y, z, e, a, b, c

                elif "ok" in serial_str and is_position_read:
                    return x, y, z, e, a, b, c

        def get_module_type():
            """
            Get the type of end effector.

            Returns:
                string that indicates the type of the module
            """

            self.port.port.reset_input_buffer()
            self.port.write('M888\r')
            module_type = "NA"  # not available
            while True:
                serial_str = self.port.read()
                if len(serial_str) > 0:
                    if serial_str.find("PEN") > -1:
                        module_type = 'PEN'
                    elif serial_str.find("LASER") > -1:
                        module_type = 'LASER'
                    elif serial_str.find("PUMP") > -1:
                        module_type = 'PUMP'
                    elif serial_str.find("3D") > -1:
                        module_type = '3D'
                    elif serial_str.find("ROTARY") > -1:
                        module_type = 'ROTARY'
                if len(serial_str) > 0:
                    if serial_str.find("ok") > -1:
                        return module_type

        self.dexarm = pydexarm.Dexarm(None)  # no port is handed over as we take care about port handling
        self.dexarm._send_cmd = _send_cmd  # here we overwrite _send_cmd of the Dexarm class
        self.dexarm.get_current_position = get_current_position  # here we overwrite _send_cmd of the Dexarm class
        self.dexarm.get_module_type = get_module_type  # here we overwrite _send_cmd of the Dexarm class

    def initialize(self):

        self.dexarm.set_module_type(self.module_type_dict[self.module_type])
        # print(self.dexarm.get_module_type())

        if self.go_home_start:
            self.go_home()

    def deinitialize(self):

        if self.go_home_end:
            self.go_home()

        self.dexarm._send_cmd("M410")  # pause the movement, only works with latest firmware

    def configure(self):

        if self.length_unit == "mm":
            self.dexarm._send_cmd("G21")
        elif self.length_unit == "inch":
            self.dexarm._send_cmd("G20")

        self.dexarm.set_acceleration(acceleration=100, travel_acceleration=self.acceleration, retract_acceleration=60)

        self._last_pump_state = False
        self._last_laser_state = False
        self._last_rotation_angle = None
        self._last_xyze = (None, None, None, False)

        if self.use_jump_mode:
            self.movement_height = float(self.movement_height)
            self.dexarm.move_to(
                # x=x,  # not needed as we just move up
                # y=y,  # not needed as we just move up
                z=self.movement_height,
                e=False,
                feedrate=self.speed,
                mode="G0",  # G0 = Fast, G1 = Normal
                wait=self.reach_position,
            )

    def unconfigure(self):

        if self.module_type == "Laser":
            self.dexarm.laser_on(0)
            self.dexarm.laser_off()

        if self.use_jump_mode:
            self.movement_height = float(self.movement_height)
            self.dexarm.move_to(
                # x=x,  # not needed as we just move up
                # y=y,  # not needed as we just move up
                z=self.movement_height,
                e=False,
                feedrate=self.speed,
                mode="G0",  # G0 = Fast, G1 = Normal
                wait=self.reach_position,
            )

        self.dexarm._send_cmd("M400")  # complete movement

    def apply(self):
        """ 'apply' is used to set the new setvalue that is always available as 'self.value' """

        # print(self.sweepvalues)

        x, y, z, e = None, None, None, None

        if "x" in self.sweepvalues:
            if self.sweepvalues["x"] != "nan":
                x = float(self.sweepvalues["x"])

        if "y" in self.sweepvalues:
            if self.sweepvalues["y"] != "nan":
                y = float(self.sweepvalues["y"])

        if "z" in self.sweepvalues:
            if self.sweepvalues["z"] != "nan":
                z = float(self.sweepvalues["z"])

        if self.module_type == "Printing":
            if "tool" in self.sweepvalues:
                feed = int(float(self.sweepvalues["tool"]))
                if feed > 0:
                    e = True
                else:
                    e = False

        if self._last_xyze != (x, y, z, e):
            self._last_xyze = (x, y, z, e)

            if self.use_jump_mode:

                self.movement_height = float(self.movement_height)

                self.dexarm.move_to(
                                    # x=x,  # not needed as we just move up
                                    # y=y,  # not needed as we just move up
                                    z=self.movement_height,
                                    e=False,
                                    feedrate=self.speed,
                                    mode="G0",  # G0 = Fast, G1 = Normal
                                    wait=self.reach_position,
                                    )

                self.dexarm.move_to(
                                    x=x,
                                    y=y,
                                    # z=self.movement_height,  # not needed as we just move lateral
                                    e=False,
                                    feedrate=self.speed,
                                    mode="G0",  # G0 = Fast, G1 = Normal
                                    wait=self.reach_position,
                                    )

            # this step can always be done, independent from jump mode
            self.dexarm.move_to(
                x=x,
                y=y,
                z=z,
                e=e,
                feedrate=self.speed,
                mode="G0",  # G0 = Fast, G1 = Normal
                wait=self.reach_position,
            )

        if self.module_type == "Pen":
            pass

        elif self.module_type == "Rotation":
            if "Rotation angle in °" in self.sweepvalues:

                angle = float(self.sweepvalues["Rotation angle in °"])
                if self._last_rotation_angle != angle:
                    self._last_rotation_angle = angle
                    self.rotate_to(angle)

        elif self.module_type == "Pump":

            if "Pump state" in self.sweepvalues:

                if self.sweepvalues["Pump state"] == "1" or self.sweepvalues["Pump state"] == 1 or self.sweepvalues[
                    "Pump state"] == "True" or self.sweepvalues["Pump state"] == True:
                    pump_state = True
                else:
                    pump_state = False

                if self._last_pump_state != pump_state:

                    self._last_pump_state = pump_state

                    if pump_state:
                        self.dexarm.soft_gripper_place()
                    else:
                        self.dexarm.soft_gripper_nature()
                        # self.dexarm.soft_gripper_place()
                        # self.dexarm.soft_gripper_pick()

        elif self.module_type == "Laser":
            if "Laser state" in self.sweepvalues:

                value = int(float(self.sweepvalues["Laser state"]))
                value = min(value, 255)
                value = max(value, 0)

                if self._last_laser_state != value:

                    self._last_laser_state = value

                    if value > 0:
                        self.dexarm.laser_on(value)
                    else:
                        self.dexarm.laser_on(0)
                        self.dexarm.laser_off()

        if self.reach_position:
            self.dexarm._send_cmd("M400")  # wait for all movements to be completed before further continuation

    def call(self):

        # requesting the angle takes some time and is not used for now
        # angle = self.get_angle()
        # print("Angle:", angle)

        x, y, z, e, a, b, c = self.dexarm.get_current_position()  # only returns the recent set position, but not the actual position
        # print("xyz coordinates",x,y,z)
        return [x, y, z]

    def go_home(self):
        self.dexarm.go_home()

    def rotate_to(self, angle):

        # print("Rotation angle to set:", angle)
        self.dexarm._send_cmd("M2101 P %i" % int(float(angle)))

    def get_angle(self):

        self.port.port.reset_input_buffer()
        self.dexarm._send_cmd("M2101")

        angle = float('nan')

        while True:
            serial_str = self.port.read()
            # print("serial string", serial_str)

            # checking for 'current posit' because at the moment it answers with 'current positon'
            # should the typo be fixed, the solution below still works
            if "current posit" in serial_str:
                angle = float(serial_str.split(" = ")[1])
                return angle

            if "wait" in serial_str:
                return angle
