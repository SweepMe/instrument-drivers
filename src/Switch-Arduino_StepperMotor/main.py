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


# SweepMe! device class
# Type: Switch
# Device: Arduino StepperMotor


from pysweepme import EmptyDevice
import time

class Device(EmptyDevice):

    actions = ["go_home"]

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Arduino StepperMotor"
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "EOL": "\n",
            "timeout": 15,
            "baudrate": 57600,
        }
        
        self.previous_value = 0
        self.direction = "CW"

        self.motor_types_enum = {
            "Driver": 1,
            "Full 2 wire": 2,
            "Full 3 wire": 3,
            "Full 4 wire": 4,
            "Half 3 wire": 5,
            "Half 4 wire": 6,
        }

    def set_GUIparameter(self):
        
        gui_parameter = {
            "Motor type": list(self.motor_types_enum.keys()),
            "SweepMode": ["Position"],
            "Position unit": ["Steps", "mm", "inch", "°"],
            "Conversion factor": 1.0,
            "Offset": 0.0,
            "Timeout in s": 30.0,
            "Speed": 1000,  # Todo: write unit?
            "Acceleration": 500,
            # "": None,
            "Homing": ["Home at the lower switch", "Home at the current position", "None"],
            "Upper limit switch": True,
            "Lower limit switch": True,
            # " ": None,
            "Reach position": True,
            "Go home at end": True,
            }
                        
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):
        self.sweepmode = parameter["SweepMode"]
        self.variables = [parameter["SweepMode"]]
        self.units = [parameter["Position unit"]]

        self.motor_type_string = parameter["Motor type"]
        self.conversion_factor = float(parameter["Conversion factor"])
        self.offset = float(parameter["Offset"])
        self.timeout = float(parameter["Timeout in s"])
        self.speed = int(float(parameter["Speed"]))
        self.acceleration = int(float(parameter["Acceleration"]))
        self.homing = parameter["Homing"]
        self.activate_upper_limit_switch = parameter["Upper limit switch"]
        self.activate_lower_limit_switch = parameter["Lower limit switch"]
        self.reach_position = parameter["Reach position"]
        self.go_home_at_end = parameter["Go home at end"]

        self.plottype = [True]
        self.savetype = [True]

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        answer = self.port.read() # waits for message sent by Arduino upon initialization
        # print(answer)

    def initialize(self):
        self.set_motor_type(self.motor_types_enum[self.motor_type_string])
        if not self.activate_lower_limit_switch and not self.activate_upper_limit_switch:
            self.set_limit_switches_config(0)
        elif self.activate_lower_limit_switch and not self.activate_upper_limit_switch:
            self.set_limit_switches_config(1)
        elif not self.activate_lower_limit_switch and self.activate_upper_limit_switch:
            self.set_limit_switches_config(2)
        elif self.activate_lower_limit_switch and self.activate_upper_limit_switch:
            self.set_limit_switches_config(3)

    def deinitialize(self):
        if self.go_home_at_end:
            self.set_target_position(0)
            start_time = time.time()
            while True:
                time.sleep(0.05)
                if not self.is_running():
                    break
                if time.time() - start_time > self.timeout:
                    raise Exception("Timeout: No answer received for movement commands.")

        self.stop_movement()

    def configure(self):
        self.set_speed(self.speed)
        self.set_acceleration(self.acceleration)
        # Todo: here hardcode homing speed and acc.?
        if self.homing == "Home at the lower switch":
            if self.activate_lower_limit_switch:
                answer = self.go_home()
                if "Homing failed" in answer:
                    raise Exception("Homing failed. Max homing steps reached out. "
                                    "Please increase it in the arduino ino code and upload the code again.")
            else:
                raise Exception("You must activate the lower limit switch to be able home at it.")

    def apply(self):
        converted_value = int(self.conversion_factor * (float(self.value) + self.offset))
        # it seems calling the moveTo methods of the arduino AccelStepper lib two times in a row,
        # causes the motor to make some noises.

        current_position = self.get_current_position()
        target_position = self.get_target_position()
        # print(current_position, target_position)
        if converted_value < current_position < target_position:
            # self.soft_stop()
            self.stop_movement()
        if target_position < current_position < converted_value:
            # self.soft_stop()
            self.stop_movement()
        
        self.set_target_position(converted_value)

    def reach(self):
        if self.reach_position:
            self.wait_until_reached()

    def measure(self):
        self.pos_current = self.get_current_position()

    def call(self):
        return self.pos_current

    """ here, convenience functions start """

    def wait_until_reached(self):
        start_time = time.time()
        while True:
            time.sleep(0.05)
            if not self.is_running():
                return True
            if time.time() - start_time > self.timeout:
                raise Exception("Timeout: No answer received for movement commands.")
            if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                return False

    def get_identification(self):
        self.port.write("IDN?")
        iden_string = self.port.read()
        compnay, driver_name, version_no = iden_string.split(",")
        return compnay, driver_name, version_no

    def set_motor_type(self, motor_type):
        if type(motor_type) is not int:
            raise TypeError("Input argument %s has to be int." % motor_type)
        self.port.write("MT=%d" % motor_type)
        answer = int(float(self.port.read()))
        return answer
    
    def get_motor_type(self):
        self.port.write("MT?")
        motor_type = int(float(self.port.read()))
        return motor_type
    
    def set_target_position(self, target_position):
        if type(target_position) is not int:
            raise TypeError("Input argument %s has to be int." % target_position)
        self.port.write("TP=%d" % target_position)
        updated_target_position = int(float(self.port.read()))
        return updated_target_position
    
    def get_target_position(self):
        self.port.write("TP?")
        target_position = int(float(self.port.read()))
        return target_position
    
    def set_relative_position(self, relative_position):
        if type(relative_position) is not int:
            raise TypeError("Input argument %s has to be int." % relative_position)
        self.port.write("RP=%d" % relative_position)
        updated_target_position = int(float(self.port.read()))
        return updated_target_position
        
    def set_current_position(self, current_position):
        if type(current_position) is not int:
            raise TypeError("Input argument %s has to be int." % current_position)
        self.port.write("P=%d" % current_position)
        updated_position = int(float(self.port.read()))
        return updated_position
    
    def get_current_position(self):
        self.port.write("P?")
        position = int(float(self.port.read()))
        return position
    
    def set_speed(self, speed):
        if type(speed) is not int:
            raise TypeError("Input argument %s has to be int." % speed)
        self.port.write("S=%d" % speed)
        updated_speed = int(float(self.port.read()))
        return updated_speed
    
    def get_speed(self):
        self.port.write("S?")
        speed = int(float(self.port.read()))
        return speed

    def set_acceleration(self, acceleration):
        if type(acceleration) is not int:
            raise TypeError("Input argument %s has to be int." % acceleration)
        self.port.write("A=%d" % acceleration)
        updated_acceleration = int(float(self.port.read()))
        return updated_acceleration
    
    def get_acceleration(self):
        self.port.write("A?")
        acceleration = int(float(self.port.read()))
        return acceleration
    
    def is_running(self):
        self.port.write("R?")
        running_state = bool(float(self.port.read()))
        return running_state
    
    def stop_movement(self):
        self.port.write("STOP")
        answer = self.port.read()
        return answer

    def soft_stop(self):
        self.port.write("SOFTSTOP")
        answer = self.port.read()
        return answer
       
    def go_home(self):
        self.port.write("HOME")
        answer = self.port.read()
        return answer

    def set_homing_speed(self, homing_speed):
        if type(homing_speed) is not int:
            raise TypeError("Input argument %s has to be int." % homing_speed)
        self.port.write("HS=%d" % homing_speed)
        updated_homing_speed = int(float(self.port.read()))
        return updated_homing_speed
    
    def get_homing_speed(self):
        self.port.write("HS?")
        homing_speed = int(float(self.port.read()))
        return homing_speed
    
    def get_upper_limit_switch_state(self):
        self.port.write("LU?")
        upper_limit_switch_state = bool(float(self.port.read()))
        return upper_limit_switch_state

    def get_lower_limit_switch_state(self):
        self.port.write("LL?")
        lower_limit_switch_state = bool(float(self.port.read()))
        return lower_limit_switch_state
    
    def save_position(self):
        self.port.write("SAVE")
        saved_position = int(float(self.port.read()))
        return saved_position

    def load_position(self):
        self.port.write("LOAD")
        loaded_position = int(float(self.port.read()))
        return loaded_position
    
    def set_limit_switches_config(self, config):
        if type(config) is not int or not 0 <= config <= 3:
            raise TypeError("Input argument %s is not valid." % config)
        self.port.write("SC=%d" % config)
        updated_config = self.port.read()
        return updated_config
    
    def get_limit_switches_config(self):
        self.port.write("SC?")
        config = self.port.read()
        return config