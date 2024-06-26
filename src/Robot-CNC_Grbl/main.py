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

# Author: Shayan Miri A. S.
# Contribution: We like to thank TU Dresden/Shayan Miri A. S. for contributing the initial version of this driver.

# SweepMe! driver
# * Module: Robot
# * Instrument: CNC Grbl


import time
import serial

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
        <p>This SweepMe! driver can be used to control x, y, z and feed rate of a CNC machine which is using 
        the open-source platform Grbl as G-code parser and motion controller. Grbl is a common G-code parser
         for affordable CNC machines and can be flashed to various microcontroller boards like Arduino and 
         Raspberry Pi Pico. The driver is tested on FoxAlien Master Pro CNC machine, but might even work 
         with CNC machines that do not use Grbl.</p>
        <p><strong>Usage:</strong></p>
        <ul>
        <li>Insert numbers into the Axes fields x, y, z and feed. For more complex procedures, use the 
        parameter syntax {...} to handover values from other modules like ReadValues.</li>
        </ul>
        <p><strong>Coordinates:</strong></p>
        <ul>
        <li>Home position: x = 0.0 mm, y = 0.0 mm, z = 0.0 mm;</li>
        </ul>
        <p><strong>Parameters:</strong></p>
        <ul>
        <li>'Go home at start' is always checked as the machine has to be homed in the beginning of the 
        run.</li>
        <li>'Go home at end' move the robot at the end of a run to the fixed home position.</li>
        <li>The driver has a normal and jump operation modes. When jump mode is activated, the z sweep value
         is irrelevant and the robot will always go the (x, y) position in the safe height plate and then go
          down to the touch height. However, when jump mode is deactivated, (x, y, z) values can be passed 
          to the driver.</li>
        </ul>
        <p><strong>Warning:</strong></p>
        <ul>
        <li>The user must make sure that the coordinates are reachable for the machine. In some cases, the limit 
        switches just stop the movement, and passing the next coordinates can crash the machine.</li>
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
        "feed rate": {
            "Value": 2000
        },
    }

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Grbl"
        self.port_types = ["COM"]

        self.reach_position_timeout = 60.0
    
    def set_GUIparameter(self):

        gui_parameter = {
                        "Unit": ["mm"],
                        "Reach position": True,
                        
                        "Jump": None,
                        "Jump mode": False,
                        "Movement height": -10.0,
                        "Offsets": None,
                        "x offset": 0.0,
                        "y offset": 0.0,
                        "z offset": 0.0,

                        "GoHomeEnd": True,
                        }
        
        return gui_parameter

    def get_GUIparameter(self, parameter):
    
        self.port_string = parameter["Port"]

        self.length_unit = parameter["Unit"]
        self.reach_position = parameter["Reach position"]
        
        self.go_home_end = parameter["GoHomeEnd"]
        
        self.jump_mode = parameter["Jump mode"]
        self.movement_height = parameter["Movement height"]

        self.x_offset = parameter["x offset"]
        self.y_offset = parameter["y offset"]
        self.z_offset = parameter["z offset"]
        
        self.variables = ["x", "y", "z"] 
        self.units = [self.length_unit] * 3
        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """
       
    def connect(self):   
        self.pyserial_port = serial.Serial(self.port_string, 115200, timeout=30)

    def disconnect(self):    
        self.pyserial_port.close()
        
    def initialize(self):
        # print(self.get_robot_paramters())
        # self.reset_robot()
        self.clear_alarms()
        self.homing()
        
    def deinitialize(self):
        if self.go_home_end:
            if self.jump_mode:
                self.move_xyz(2000, self._last_xyzf[0], self._last_xyzf[1], self.movement_height)
                self.reach_position()
            self.move_xyz(2000, 0, 0, 0)

    def configure(self):
        self._last_xyzf = [0, 0, 0, 0]

    def unconfigure(self):
        pass

    def apply(self):
    
        # print(self.sweepvalues)
        # feed_rate = int(self.sweepvalues["feed rate"])

        if "x" in self.sweepvalues and self.sweepvalues["x"] != "nan":
            x = float(self.sweepvalues["x"]) + self.x_offset
        else: 
            x = self._last_xyzf[0]
            
        if "y" in self.sweepvalues and self.sweepvalues["y"] != "nan":
            y = float(self.sweepvalues["y"]) + self.y_offset
        else: 
            y = self._last_xyzf[1]

        if "z" in self.sweepvalues and self.sweepvalues["z"] != "nan":
            z = float(self.sweepvalues["z"]) + self.z_offset
        else: 
            z = self._last_xyzf[2]

        if "feed" in self.sweepvalues and self.sweepvalues["feed rate"] != "nan":
            feed_rate = int(self.sweepvalues["feed rate"])
        else: 
            feed_rate = self._last_xyzf[3]
            
        # Jump mode
        if self._last_xyzf[0:2] != (x, y, z, feed_rate):
            if self.jump_mode:
                self.move_xyz(self._last_xyzf[3], self._last_xyzf[0], self._last_xyzf[1], self.movement_height)
                self.wait_reach_position()
                self.move_xyz(feed_rate, x, y, self.movement_height)
                self.wait_reach_position()
                self.move_xyz(feed_rate, x, y, z)
                self.wait_reach_position()
            else: 
                self.move_xyz(feed_rate, x, y, z)
                if self.reach_position:
                    self.reach_position()
            self._last_xyzf = (x, y, z)
            
    def call(self):
        x, y, z = self.get_position()
        return x, y, z

    """ here, convenience functions start """

    def write(self, msg):
        # print("\nmsg:", (msg+"\r\n").encode())
        self.pyserial_port.write((msg+"\r\n").encode())
        time.sleep(.1)

    def read(self):
        answer = self.pyserial_port.read_until(b"ok\r\nok").strip().decode()
        # another way to read the answer, sometimes fails
        # answer = ""
        # while self.pyserial_port.inWaiting():
        #     answer += self.pyserial_port.readline().decode().strip() + "\n"
        #     time.sleep(.1)
        # print(answer)
        
        return answer

    def get_robot_paramters(self):
        self.write("$$")
        answer = self.read()
        return answer

    def clear_alarms(self):
        self.write("$X")
        answer = self.read()
        return answer

    def load_data_eeprom(self):
        self.write("$RST=*")
        answer = self.read()
        return answer

    def reset_robot(self):
        self.write("$RST=$")
        answer = self.read()
        return answer
        
    def move_xyz(self, f, x, y, z):
        self.write("G1 G90 F%d X%f Y%f Z%f" % (float(f), float(x), float(y), float(z)))
        answer = self.read()
        return answer

    def homing(self):
        self.write("$H")
        self.read()
        # sets the position to zero, pretty confusing command
        # self.write("G10 P0 L20 X0 Y0 Z0")
        # answer = self.read()
        
    def wait_reach_position(self):
        time.sleep(0.2)
        while self.get_state() == "Run":
            time.sleep(0.2)
                
    def get_position(self):
        self.write("$?")
        answer = self.read().split("|")
        return tuple(map(float, answer[1][5:].split(",")))

    def get_state(self):
        self.write("$?")
        answer = self.read().split("|")
        return answer[0][1:]
