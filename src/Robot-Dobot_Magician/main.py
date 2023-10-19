# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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
# Device: Dobot Magician

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

# this imports dobot-python that is just called "lib" on github
from lib.interface import Interface
from lib.message import Message

import time

from pysweepme.ErrorMessage import error, debug

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
        <p>This driver can be used to control x, y, z of a Dobot Magician tabletop robot.</p>
        <p>&nbsp;</p>
        <p><strong>Requirements</strong>:</p>
        <ul>
        <li>Before using this driver, you need to install the USB to UART driver at the link below:<br>
        https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers</li>
        </ul>
        <p><strong>Usage:</strong></p>
        <ul>
        <li>Insert numbers into the Axes fields x, y, z, r. For more complex procedures, use the parameter 
        syntax {...} to handover values from other modules.</li>
        <li>If the object attached to robot is heavy, one should set the payload mass and eventually the 
        eccentric distance of the object.</li>
        <li>The Robot module works best in combination with add-on modules such as "ReadValues" or 
        "TableValues" where you create a list of x, y, z, r values that you handover to the Robot module 
        using the parameter syntax {...}</li>
        <li>Home position is fixed at x = 320 mm, y = 0 mm, z = 0 mm, r = 0&deg;<br />&nbsp;</li>
        </ul>
        <p><strong>Coordinates:</strong></p>
        <ul>
        <li>Home position: x = 320.0 mm, y = 0.0 mm, z = 0.0 mm, r = 0&deg;</li>
        <li>x: horizontal direction of the robot arm in the home position</li>
        <li>y: horizontal direction perpendicular to y</li>
        <li>z: vertical direction perpendicular to x and y&nbsp;</li>
        <li>r: Rotation angle in &deg; (-90 to +90)</li>
        </ul>
        <p>&nbsp;</p>
        <p><strong>Parameters:</strong></p>
        <ul>
        <li>'Go home at start' moves the robot at the beginning of a run to the fixed home position.</li>
        <li>'Go home at end' moves the robot at the end of a run to the fixed home position.</li>
        <li>Global speed factor affects all moves: 1-100</li>
        <li>Global acceleration factor: 1-100<br />&nbsp;</li>
        </ul>
        <p><strong>Caution:</strong></p>
        <ul>
        <li>The home position is fixed and independent from an individual position set in Dobot Studio Pro, 
        so please check whether Go home before or after the run works for you.</li>
        <li>Furthermore, initiating the homing does not work as expected which is why 'Go home at start' and 
        'Go home at end' is set to False for now. Please try yourself. Otherwise ues the Dobot Studio to do a 
        homing before a run.</li>
        </ul>
    """
                    
    axes = {
            "x": {
                "Value": 0.0
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

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Magician"  # short name will be shown in the sequencer
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
                                "baudrate": 115200,
                                "timeout": 1,
                                "EOL": "\r\n",
                                }

        self.reach_position_timeout = 30  # seconds
        self.home_position = 320.0, 0.0, 0.0, 0.0
            
    def set_GUIparameter(self):

        gui_parameter = {
                        "Unit": ["mm"],
                        "Reach position": True,
                        "Global acceleration factor": 10,
                        "Global speed factor": 10,
                        # "Auto leveling": False,
                        
                        "": None,

                        "Jump": None,
                        "Use jump mode": False,
                        "Movement height": 0,
                        
                        "GoHomeStart": False,  # Attention: Homing does not work as expected yet
                        "GoHomeEnd": False,  # Attention: Homing does not work as expected yet
                        }
        
        return gui_parameter

    def get_GUIparameter(self, parameter):
    
        # self.port_string = parameter["Port"]

        self.length_unit = parameter["Unit"]
        self.reach_position = parameter["Reach position"]

        self.is_jump_mode = parameter["Use jump mode"]
        self.movement_height = parameter["Movement height"]
        
        self.go_home_start = parameter["GoHomeStart"]
        self.go_home_end = parameter["GoHomeEnd"]
        # self.auto_leveling = parameter["AutoLeveling"]

        self.global_acceleration_factor = parameter["Global acceleration factor"]
        self.global_speed_factor = parameter["Global speed factor"]
        
        self.variables = ["x", "y", "z", "r"] 
        self.units = [self.length_unit] * 3 + ["°"]
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):

        self.dobot = Interface(port=None)  # no port will be opened or created
        #self.dobot = MagicianInterface(port=None)  # no port will be opened or created

        # We overwrite the pyserial COM port object with the one from the port manager
        self.dobot.serial = self.port.port

        # print()  # empty line
        # print("Dobot", self.dobot)
        # print("Dobot serial", self.dobot.serial)
        # print('Dobot name is ', self.dobot.get_device_name())
        # print('Dobot version is ', self.dobot.get_device_version())
        # print('Dobot SN is ', self.dobot.get_device_serial_number())

    def disconnect(self):
        pass
        
    def initialize(self):

        self.dobot.clear_alarms_state()

        self.dobot.set_homing_parameters(*self.home_position)
        
        self.dobot.stop_queue(True)
        self.dobot.clear_queue()
        self.dobot.start_queue()
        
        if self.go_home_start:
            self.dobot.set_homing_command(0)
            self.wait()

        # Auto leveling function requires the leveling tool to be mounted on the robot.
        # Todo: No reference value for this accuracy was found in the user manual. According to the datasheet, 
        # the general accuracy of the robot is 0.2 mm.
        # if self.auto_leveling:
        #     self.dobot.set_auto_leveling(enable=True, accuracy=0.2)
        
    def deinitialize(self):

        if self.go_home_end:
            self.dobot.set_homing_command(0)
            self.wait()

        self.dobot.stop_queue(True)

    def configure(self):
        
        # Coordinate velocity was rather unclear. You need to anyway either set them here or in the apply method.
        # self.dobot.set_point_to_point_coordinate_params(50, 50, 50, 50)

        # TODO: check whether this must be float or int
        self.dobot.set_point_to_point_common_params(
            float(self.global_speed_factor),
            float(self.global_acceleration_factor),
        )
        self._last_xyzr = self.dobot.get_pose()
        if self.is_jump_mode:
            # We set the z limit equal to movement height.
            self.dobot.set_point_to_point_jump_params(
                float(self.movement_height),
                float(self.movement_height),
            )
            self.dobot.set_point_to_point_command(
                2,
                self._last_xyzr[0],
                self._last_xyzr[1],
                float(self.movement_height),
                self._last_xyzr[3],
            )
            self.wait()

    def unconfigure(self):

        if self.is_jump_mode:
            # we just move up to the movement height
            self.dobot.set_point_to_point_command(
                2,  # movement mode
                self._last_xyzr[0],
                self._last_xyzr[1],
                float(self.movement_height),
                self._last_xyzr[3],
            )
            self.wait()

    # Carefully check the mode first. There was some conflicts and ambiguity. Requires trial and error.
    def apply(self):
        
        print("Applying:", self.sweepvalues)

        # this command takes both velocity and accelaration for each axes.
        # todo: do trial and errors to figure out how it works.
        # self.dobot.set_point_to_point_coordinate_params(50, 50, 50, 50)

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

        # print(x,y,z,r)
        if self._last_xyzr != (x, y, z, r):

            # The command number 4 is the shortest path.
            if self.is_jump_mode:
                #self.dobot.set_point_to_point_command(0, x, y, z, r)

                self.dobot.set_point_to_point_command(
                    2,  # movement mode
                    self._last_xyzr[0],
                    self._last_xyzr[1],
                    float(self.movement_height),
                    self._last_xyzr[3],
                )
                self.wait()

                self.dobot.set_point_to_point_command(
                    2,  # movement mode
                    x,
                    y,
                    float(self.movement_height),
                    r,
                )
                self.wait()

                self.dobot.set_point_to_point_command(
                    2,
                    x,
                    y,
                    z,
                    r,
                )

            else:
                self.dobot.set_point_to_point_command(
                    2,  # movement mode
                    x,
                    y,
                    z,
                    r,
                )

            self._last_xyzr = (x, y, z, r)
            # print("Last xyzr: ", self._last_xyzr)

    def reach(self):

        if self.reach_position:
            if hasattr(self.dobot, "get_last_id"):
                id = self.dobot.get_last_id()
                self.wait(id)
            else:
                self.wait()

    def call(self):

        # get_pose returns the cartesion coordinates, the rotation and the four joint angles
        x, y, z, r, j1, j2, j3, j4 = self.dobot.get_pose()
        return x, y, z, r

    """ here, convenience functions start """

    def wait(self, queue_id=None):
        # The get_current_queue_index method always returns the last command's queue id, if the queue has finished.
        # The perfect solution for this method would be to take the command queue id from the response of the dobot and
        # compare it with the current queue id (look at the pydobot lib).

        if queue_id is None:
            # This does not work if multiple commands are in the queue.
            queue_id = self.dobot.get_current_queue_index()
            print("Current queue id at start is:", queue_id)
        else:
            print("Queue id to wait for:", queue_id)

        # we add a meaning less step to just let the queue id proceed if the last
        # step was finished. Otherwise the queue id stays at the last step
        self.dobot.wait(0)
        starttime = time.time()

        while True:
            current_queue_id = self.dobot.get_current_queue_index()
            if current_queue_id > queue_id:
                break
            if time.time() - starttime > self.reach_position_timeout:
                print("Queue id after timeout is:", current_queue_id)
                raise Exception("Timeout error: Cannot reach next queue id.")

            time.sleep(0.05)


class MagicianInterface(Interface):

    _last_id = None

    def send(self, message):
        self.lock.acquire()
        self.serial.write(message.package())
        self.serial.flush()
        response = Message.read(self.serial)
        self.lock.release()
        self._last_id = response.id
        return response.params

    def get_last_id(self):
        return self._last_id
