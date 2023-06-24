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
# Type: Switch
# Device: Ocean Controls KTx-290
# Authors: Shayan Miri (sweep-me.net), Axel Fischer (sweep-me.net)

import time

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
    <p><strong>Usage:</strong></p>
    <ul>
    <li>The KTx stepper motor driver will work in quasi-relative mode if the user selects 'Use start position as zero'. 
    In this case, the position is read once at the beginning and used as reference for all further absolute 
    positions.</li>
    <li>The frequency is the driver's driving pulse rate. This will ramp from the start freq to the end freq at the 
    specified ramp rate for each move./li&gt;</li>
    <li>The conversion factor relates motor steps to the selected position unit (e.g. 180 steps per mm.)</li>
    <li>The offset is added to the set value in the selected position unit.</li>
    <li>End position: moves to this position after measurement. The parameter is optional.</li>
    <li>The KTx-290 stepper motor driver can drive up to 16 motors by connecting multiple KTx-290 units in series.</li>
    </ul>
    <p>&nbsp;</p>
    <p><strong>Info:</strong></p>
    <ul>
    <li>The driver saves the current position to the non-volatile memory after every run to make sure that each move is 
    tracked.</li>
    </ul>
    <p>&nbsp;</p>
    <p><strong>Requirements:</strong></p>
    <ul>
    <li>This motor driver communicates through a virtual COM port using a common USB to serial converter IC from FTDI. 
    Most computers have a suitable FTDI driver for this chip and the KTx-290 motor driver card appears as a virtual 
    COM port when plugged to the PC through USB. If not, the FTDI drivers can be downloaded from: 
    <br />http://www.ftdichip.com/Drivers/VCP.htm</li>
    </ul>
    """

    axis: int
    position_unit: str
    conversion_factor: float
    offset: float
    use_start_position_as_zero: bool
    end_position: float
    initial_freq: int
    frequency_ramp: int
    final_freq: int
    initial_position: int
    value: float

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "KTx-290"

        self.variables = ["Position"]
        self.units = [""]
        self.plottype = [True]
        self.savetype = [True]

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 2,
            "baudrate": 57600,  # Default value: 57600   # 230400
            "EOL": "\r\n",
            "Exception": False,  # can be used to not throw an error in case of a timeout
        }

        self.move_timeout = 60.0

    def set_GUIparameter(self):

        # If the checksum mode is activated, the last byte of message has to be the checksum. It's not implemented and
        # the default settings is deactivated. It might be useful when more controllers are connected in series.
        gui_parameter = {
            "SweepMode": ["Position"],
            "Motor axis": [i for i in range(1, 17)],
            # "Checksum mode": ["Off"],
            "Position unit": ["Steps", "mm", "inch", "°"],
            "Conversion factor": "1.0",  # User input to motor steps
            "Offset": "0.0",  # must be in the position unit
            "Use start position as zero": True,
            "End position": "",
            "": None,
            "Initial frequency in Hz": 10,
            "Frequency ramp in Hz/steps": 1,
            "Final frequency in Hz": 1000,
        }

        return gui_parameter

    def get_GUIparameter(self, parameter={}):

        # self.sweepmode = parameter["SweepMode"]
        self.device_name = parameter["Device"]
        self.port_string = parameter["Port"]
        self.axis = int(parameter["Motor axis"])
        self.position_unit = parameter["Position unit"]
        self.conversion_factor = float(parameter["Conversion factor"])
        self.offset = float(parameter["Offset"])
        self.use_start_position_as_zero = parameter["Use start position as zero"]
        self.end_position = parameter["End position"]
        self.initial_freq = int(parameter["Initial frequency in Hz"])
        self.frequency_ramp = int(parameter["Frequency ramp in Hz/steps"])
        self.final_freq = int(parameter["Final frequency in Hz"])

        if self.position_unit == "mm":
            self.units[0] = "mm"
        elif self.position_unit == "°":
            self.units[0] = "°"
        elif self.position_unit == "inch":
            self.units[0] = "inch"
        else:
            self.units[0] = ""

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        # must be defined here, to be available in disconnect if initialize is omitted
        self.device_identifier = self.device_name + "_" + self.port_string

    def initialize(self):

        if self.device_identifier not in self.device_communication:
            # Sending reset only once to the controller in case of multiple axes
            answer = self.reset()
            # print("KTx-290 reset answer:", answer)

            if all([x == "" for x in answer]):
                raise Exception("Did not receive any response from the KTx-290 during initial reset. "
                                "Please check baudrate (default = 57600).")

            # Registering the key to inform other driver instances, value does not matter
            self.device_communication[self.device_identifier] = None

        # can be used to zero the internal position
        # if self.use_start_position_as_zero:
        #     self.set_position(self.axis, 0)

        self.initial_position = self.get_position(self.axis)

    def deinitialize(self):

        if self.end_position != "":
            value_converted = int(self.conversion_factor * (float(self.end_position) + self.offset))
            if self.use_start_position_as_zero:
                value_converted += self.initial_position

            self.absolute_move(self.axis, value_converted)

        self.stop()

    def disconnect(self):

        if self.device_identifier in self.device_communication:
            # we only save all parameters once even if multiple axes are used

            # save the current position to the non-volatile memory to make sure the position
            # is not reset during the reset() command in 'initialize'
            self.save()

            # removing the key from self.device_communication so that other driver instances do not run
            # the code above again
            del self.device_communication[self.device_identifier]

    def configure(self):

        # these settings apply to every move
        self.set_initial_frequency(self.axis, self.initial_freq)
        self.set_frequency_ramp(self.axis, self.frequency_ramp)
        self.set_final_frequency(self.axis, self.final_freq)

    def unconfigure(self):
        pass

    def apply(self):
        """ set new value"""

        self.value = float(self.value)

        value_converted = int(self.conversion_factor * (self.value + self.offset))

        if self.use_start_position_as_zero:
            value_converted += self.initial_position

        # not needed anymore as we are splitting the write and read command
        # into 'apply' and 'reach'
        # self.absolute_move(self.axis, value_converted)

        if self.axis in range(1, 17):
            self.port.write("@%d AMOV %d" % (self.axis, value_converted))
        else:
            raise Exception("Axis must be in range 1-16.", self.axis)

        self.port.read()  # First reading is the axis address

        # reading the final message of the absolute move command in 'apply'
        starttime = time.time()
        while True:
            answer = self.port.read()
            if "!" in answer:
                # print("Absolute move of axis %d finished." % self.axis)
                break
            if time.time() - starttime > self.move_timeout:
                raise Exception("Timeout during absolute move of KTx-290")
            if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                raise Exception("Measurement stopped while waiting to reach absolute position")

    def call(self):
        return [self.value]

    """ here, convenience functions start """

    def stop(self):
        """
        This function stops all axes immediately. The address of an axis (here @01) is not important.
        Returns:
            None
        """
        self.port.write("@01 STOP")
        self.port.read()

    def save(self):
        """
        The SAVE command records the controller’s configuration settings to non-volatile memory
        so they aren’t lost when power is removed.
        Returns:
            None
        """
        self.port.write("@01 SAVE")
        self.port.read()

    def reset(self):
        """
        This function resets the instrument to the default values saved to EEPROM. The reply is the power-up message,
        which includes the firmware version and the current card address.
        Returns:
             str: firmware version and the current card address
        """
        self.port.write("@01 RSET")
        # This instrument sends 5 lines of reply. All of them have to be read.
        answer = ""
        for _ in range(0, 6):
            answer = answer + "\n" + self.port.read()
        return answer

    def set_initial_frequency(self, axis, freq):
        """
        This function sets the initial frequency of an axis in Hz. The default value for initial frequency is 10.
        Args:
            axis: int
            freq: int

        Returns:
            None
        """
        if axis in range(1, 17) and freq in range(10, 10000):
            self.port.write("@%d ACCS %d" % (axis, freq))
            self.port.read()
        else:
            raise Exception("Arguments of function set_initial_frequency() are not correct: ", axis,
                            freq)

    def set_frequency_ramp(self, axis, ramp):
        """
        This function sets the frequency ramp of an axis. The default value for to ramp up or down the frequency is 1.
        The ramp unit is Hz/steps.
        Args:
            axis: int
            ramp: int

        Returns:
            None
        """
        if axis in range(1, 17) and ramp in range(1, 10000):
            self.port.write("@%d ACCI %d" % (axis, ramp))
            self.port.read()
        else:
            raise Exception("Arguments of function set_frequency_ramp() are not correct: ", axis,
                            ramp)

    def set_final_frequency(self, axis, freq):
        """
        This function sets the final frequency of an axis in Hz. The default value for the final frequency is 1000.
        Args:
            axis: int
            freq: int

        Returns:
            None
        """
        if axis in range(1, 17) and freq in range(10, 50001):
            self.port.write("@%d ACCF %d" % (axis, freq))
            self.port.read()
        else:
            raise Exception("Arguments of function set_final_frequency() are not correct: ", axis,
                            freq)

    def absolute_move(self, axis, pos):
        """
        This function moves the motor on the selected axis to given absolute position. The KTx driver keeps the latest
        position of an axis in a non-volatile memory.
        Args:
            axis: int
            pos: int

        Returns:
            None
        """
        if axis in range(1, 17):
            self.port.write("@%d AMOV %d" % (axis, pos))
        else:
            raise Exception("Axis must be in range 1-16.", axis, pos)

        self.port.read()  # First reading is the axis address

        starttime = time.time()
        while True:

            answer = self.port.read()
            if "!" in answer:
                print("Absolute move of axis %d finished." % axis)
                break
            if time.time() - starttime > self.move_timeout:
                raise Exception("Timeout during absolute move of KTx-290")
            if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                raise Exception("Measurement stopped while waiting to reach absolute position")

    def relative_move(self, axis, pos):
        """
        This function moves the motor on the selected axis to given relative position.
        Args:
            axis: int
            pos: int

        Returns:
            None
        """
        if axis in range(1, 17):
            self.port.write("@%d RMOV %d" % (axis, pos))
        else:
            raise Exception("Axis must be in range 1-16.", axis, pos)

        self.port.read()  # First reading is the axis address

        starttime = time.time()
        while True:

            answer = self.port.read()
            if "!" in answer:
                print("Relative move of axis %d finished." % axis)
                break

            if time.time() - starttime > self.move_timeout:
                raise Exception("Timeout during relative move of KTx-290")

            if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                raise Exception("Measurement stopped while waiting to reach relative position")

    def set_positions(self, axis, positions):
        """
        This function sets the positions of all four axes of a controller.
        Args:
            axis: int
            positions: list

        Returns:
            None
        """
        if axis in range(1, 17):
            self.port.write("@%d POSN %d %d %d %d" % (axis, *positions))
        else:
            raise Exception("Axis must be in the range of 1-16.", axis)
        self.port.read()

    def set_position(self, axis, pos):
        """
        This function sets internal value of the current position of an axis of a controller.
        NB: this is not go to position
        Args:
            axis: int
            pos: int

        Returns:
            None
        """
        positions = self.get_positions(axis)
        positions[(axis - 1) % 4] = pos
        self.set_positions(axis, positions)

    def get_positions(self, axis):
        if axis in range(1, 17):
            self.port.write("@%d PSTT" % axis)
        else:
            raise Exception("Axis must be in the range of 1-16.", axis)
        answer = self.port.read().split(" ")[1:]
        return list(map(int, answer))

    def get_position(self, axis):
        """
        This function gets the position of an axis in steps
        Returns:
            int: position
        """
        if axis in range(1, 17):
            self.port.write("@%d POSN" % axis)
        else:
            raise ValueError("Axis must be in the range of 1-16.", axis)
        answer = int(self.port.read().split(" ")[1])
        return answer

    def get_frequencies(self, axis):
        """
        This function gets the frequencies of a given axis.

        Returns:
            list: frequencies
        """
        if axis in range(1, 17):
            self.port.write("@%d RACC" % axis)
        else:
            raise ValueError("Axis must be in the range of 1-16.", axis)

        answer = self.port.read().split(" ")[1:]
        return list(map(int, answer))

    def get_status(self, axis):
        """ retrieves status flags for movings, directions and limit switches """

        if axis in range(1, 17):
            self.port.write("@%d STAT" % axis)
        else:
            raise ValueError("Axis must be in the range of 1-16.", axis)

        answer = self.port.read()
        # print("Status KTx-290:", answer)
        flags = int(answer.split(" ")[1])
        flags_dict = {}

        # TODO: change dictionary keys to correct axis numbers
        flags_dict["Axis1 moving"] = flags & 0 != 0
        flags_dict["Axis2 moving"] = flags & 1 != 0
        flags_dict["Axis3 moving"] = flags & 2 != 0
        flags_dict["Axis4 moving"] = flags & 4 != 0

        flags_dict["Axis1 forward"] = flags & 8 != 0
        flags_dict["Axis2 forward"] = flags & 16 != 0
        flags_dict["Axis3 forward"] = flags & 32 != 0
        flags_dict["Axis4 forward"] = flags & 64 != 0

        flags_dict["Limit switch 1"] = flags & 128 != 0
        flags_dict["Limit switch 2"] = flags & 256 != 0
        flags_dict["Limit switch 3"] = flags & 512 != 0
        flags_dict["Limit switch 4"] = flags & 1024 != 0

        return flags_dict


if __name__ == "__main__":
    # SweepMe drivers can also be run directly or used in pure python codes through pysweepme. For this purpose a driver
    # contains two sets of functions, standard functions, which are called by SweepMe! iteratively and
    # convenience functions. Here is a simple example of directly running the driver.
    ktx = Device()
    print(dir(ktx))
    print(ktx)
    print(ktx.reset())
    print(ktx.get_frequencies(1))

    ktx.relative_move(1, 1000)
    ktx.relative_move(1, -1000)
