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
# Type: Logger
# Device: Landgraf HLL LA-1xx

import time
from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):

    description =   """
                    <p>Driver for syringe pumps from Landgraf HLL</p>
                    <p>&nbsp;</p>
                    <p><strong>Models:</strong> LA-100, LA-102 LA-110, LA-120, LA-160, LA-180, LA-190</p>
                    <p>&nbsp;</p>
                    <p><strong>Communication:</strong></p>
                    <ul>
                    <li>COM port / RS-232:
                    <ul>
                    <li>baudrate -&gt; 19200</li>
                    </ul>
                    </li>
                    <li>Protocol: Basic mode (no checksum), Safe mode is not yet supported but can be implemented on demand.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>At each step of the run, the driver runs a single phase program with the desired rate and volume.</li>
                    <li>If you do not like to use the pump, set rate or volume to 0.</li>
                    <li>Enter a positive rate to withdraw and negative rate to infuse.</li>
                    <li>The volume will always be interpreted as absolute value.</li>
                    <li>Controlling multiple pumps by daisy chaining has not been tested but should basically work.</li>
                    <li>In order to make rate or volume variable, you can use the parameter syntax {...}</li>
                    </ul>
                    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "LA-100"

        self.port_manager = True
        self.port_types = ["COM"]

        self.port_properties = {
                                  "timeout": 1,
                                  "baudrate": 19200,  # possible values 19200, 9600, 2400, 1200, or 300
                                  "EOL": '',
                                  "bytesize": 8,
                                  "stopbits": 1,
                                  "parity": 'N',
                                }

        self.STX = 0x02
        self.ETX = 0x03

        self._is_safemode = False

        self.status_codes = {
            "I": "Infusing",
            "W": "Withdrawing",
            "S": "Pumping program stopped",
            "P": "Pumping program paused",
            "T": "Timed paused phase",
            "U": "Operational trigger wait (user wait)",
            "X": "Purging",
        }

        self.alarm_code = {
            "R": "Pump was reset (power was interrupted)",
            "S": "Pump motor stalled",
            "T": "Safe mode communications time out",
            "E": "Pumping Program error",
            "O": "Pumping Program Phase is out of range",
        }

        self.rate_units = {
            "μl / hr": "UH",
            "μl / min": "UM",
            "ml / hr": "MH",
            "ml / min": "MM",
        }

        self.volume_units = {
            "ml": "ML",
            "µl": "UL",
        }

    def set_GUIparameter(self):

        gui_parameter = {
                        "Address": list(range(0, 99, 1)),
                        "SweepMode": ["None"],
                        "Diameter in mm": 20.0,
                        "RS-232 protocol": ["Basic mode", ],  # "Safe mode"
                        "": None,
                        "Rate unit": list(self.rate_units.keys()),
                        "Rate": "0.0",
                        " ": None,
                        "Volume unit": list(self.volume_units.keys()),
                        "Volume": "0.0",
                        # "  ": None,
                        # "Wait for program": True,
                        }
        
        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.address = parameter["Address"]
        self.diameter = parameter["Diameter in mm"]

        # self.is_wait_for_program = parameter["Wait for program"]

        # if float(self.diameter) <= 14.0:
        #     volume_unit = "μl"
        # else:
        #     volume_unit = "ml"

        self.rate_unit = parameter["Rate unit"]
        self.rate = parameter["Rate"]

        self.volume_unit = parameter["Volume unit"]
        self.volume = parameter["Volume"]

        self.variables = ["Rate", "Volume", "Volume, infused", "Volume, withdrawn", "is finished"]

        self.units = [self.rate_unit, self.volume_unit, self.volume_unit, self.volume_unit, ""]

    def initialize(self):

        self.set_phase(2)
        self.set_phase_function("STP")
        self.set_phase(1)
        self.set_phase_function("RAT")

        self.set_diameter(self.diameter)
        self.set_volume_unit(self.volume_units[self.volume_unit])

        self.set_rate(0.0, "UH")
        self.set_volume(0.0)

    def configure(self):

        if float(self.rate) < 0.0:
            self.set_pumping_direction("WDR")
        else:
            self.set_pumping_direction("INF")

        self.set_rate(self.rate, self.rate_units[self.rate_unit])
        self.set_volume(self.volume)
        # self.clear_dispensed_volume()

    def reconfigure(self, parameters, keys):

        if "Rate" in keys:
            rate = parameters["Rate"]
            if float(rate) < 0.0:
                self.set_pumping_direction("WDR")
            else:
                self.set_pumping_direction("INF")
            self.set_rate(rate, self.rate_units[self.rate_unit])

        if "Volume" in keys:
            volume = parameters["Volume"]
            self.set_volume(volume)

    def unconfigure(self):

        self.stop_program()  # this might just pause a running program
        self.stop_program()  # this finally stops the program

    def start(self):
        self.stop_program()  # this might just pause a running program
        self.stop_program()  # this finally stops the program
        self.clear_dispensed_volume()
        self.run_program()

    def measure(self):

        # if self.is_wait_for_program:
        self.wait_for_program()

        self.rate_set = self.get_rate()
        self.volume_set = self.get_volume()
        self.vol_infused, self.vol_withdrawn = self.get_dispensed_volumes()
        self.is_finished = self.is_program_done()

    def call(self):

        return self.rate_set, self.volume_set, self.vol_infused, self.vol_withdrawn, self.is_finished

    def send_message(self, cmd):

        # print()
        msg = cmd

        if self._is_safemode:
            msg = "???"  # TODO: must be defined
            raise Exception("Safe mode communication not supported yet.")
        else:
            if not cmd.startswith("*"):
                msg = "%02d" % int(self.address) + msg
            msg += "\r"

        # print("Message to send:", repr(msg))
        self.port.write(msg)

    def read_message(self):

        msg = ""

        starttime = time.perf_counter()
        while True:
            msg += self.port.read(1)
            if msg[-1] == chr(self.ETX):
                break
            if time.perf_counter() - starttime > 3.0:
                raise Exception("Timeout during reading message.")

        # print("Received message:", msg)

        if msg[0] != chr(self.STX):
            raise Exception("Message does not start with STX character.")
        if msg[-1] != chr(self.ETX):
            raise Exception("Message does not end with ETX character.")

        if self._is_safemode:
            length = int(msg[0])
            if length != msg[1:]:
                raise Exception("Returned message has incorrect length")
            response = msg[2:-3]   # stripping off STX, length byte, CRC1, CRC2, ETX
            CRC1 = msg[-3]
            CRC2 = msg[-2]

            # TODO: check if CRC is correct

        else:
            response = msg[1:-1]  # stripping off STX and ETX

        address = response[:2]
        status = response[2]
        answer = response[3:]

        self.check_status(status)

        # TODO: do something with response
        # 1. check for alarm or status
        # 2. if response return response message

        return status, answer

    def check_status(self, status):

        if status in self.status_codes:
            pass
            # print("Status:", self.status_codes[status])
        else:
            raise Exception("Unknown status code received:", status)

    def calculate_checksum(self, cmd):
        pass

    """ taken from https://stackoverflow.com/questions/35205702/calculating-crc16-in-python """
    @staticmethod
    def crc16(data: bytearray, offset, length):
        if data is None or offset < 0 or offset > len(data) - 1 and offset + length > len(data):
            return 0
        crc = 0xFFFF
        for i in range(0, length):
            crc ^= data[offset + i] << 8
            for j in range(0, 8):
                if (crc & 0x8000) > 0:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc = crc << 1
        return crc & 0xFFFF

    def get_status(self):

        self.send_message("DIS")
        status, _ = self.read_message()

        return status

    def wait_for_program(self):

        while True:

            if self.is_program_done():
                break

    def reset(self):
        """
        Clears program memory and resets communication parameters to Basic mode and address 0.

        This is a special system command that will be accepted by the pump regardless of its
        current address.
        """
        self.send_message("*RESET")
        self.read_message()

    def get_address(self):
        self.send_message("*ADR")
        status, answer = self.read_message()
        return answer

    def get_version(self):
        self.send_message("VER")
        status, answer = self.read_message()
        return answer

    def set_basic_mode(self):

        self.port.write((chr(0x02)+chr(0x08)+"SAF0"+chr(0x55)+chr(0x43)+chr(0x3)).encode("ascii"))
        self.set_safe_mode(0)
        self._is_safemode = False

    def set_safe_mode(self, timeout):
        """
        0 to 255 seconds

        Args:
            timeout: Timeout value in seconds before Alarm is triggered if no further communication is received.
            A value of 0 enables the basic mode.
        """

        timeout = int(float(timeout))

        if timeout > 255:
            raise Exception("Timeout in s cannot be higher than 255.")
        elif timeout < 0:
            raise Exception("Timeout in s cannot be lower than 0.")

        self.send_message("SAF %i" % timeout)

        if timeout == 0:
            self._is_safemode = False
        else:
            self._is_safemode = True

    def run_program(self, phase=""):
        self.send_message("RUN%s" % str(phase))
        self.read_message()

    def stop_program(self):
        self.send_message("STP")
        self.read_message()

    def is_program_done(self):

        status = self.get_status()

        if status in ["I", "W"]:
            return False
        else:
            return True

    def set_phase(self, number):
        self.send_message("PHN%i" % int(number))
        self.read_message()

    def get_phase(self):
        self.send_message("PHN")
        status, answer = self.read_message()
        return int(answer)

    def set_phase_function(self, function):
        """
        Rate Data Functions
        -----------------------
        RAT Pumping rate. ‘RATE’
        INC Increment rate. ‘INCR’
        DEC Decrement rate. ‘DECR’

        Non-Rate Data Functions
        -----------------------
        STP Stop pump. ‘STOP’
        JMP <phase data> Jump to Program Phase. ‘JP:nn’
        LOP <count data> Loop to previous loop start ‘nn’ times. ‘LP:nn’
        PRI Program Selection Input. 'Pr:In'
        PRL <count data> Program Selection Label definition. 'Pr:nn'
        LPS Loop starting Phase. ‘LP:ST’
        LPE Loop end Phase. ‘LP:EN’
        PAS <number data> Pauses pumping for ‘nn’ seconds. ‘PS:nn’
        PAS <n.n> Pauses pumping for 'n.n' seconds. 'PS:n.n'
        IF <phase data> If Program input TTL pin low, jump to Phase.
        ‘IF:nn’
        EVN <phase data> Set event trigger trap. ‘EV:nn’
        EVS <phase data> Set event square wave trigger trap. 'ES:nn'
        EVR Event trigger reset. ‘EV:RS’
        BEP Sound short beep. ‘BEEP’
        OUT <TTL level> Set programmable output pin. ‘OUT.n’

        Args:
            function:

        Returns:

        """
        self.send_message("FUN %s" + str(function))
        self.read_message()

    def get_phase_function(self):

        self.send_message("FUN")
        status, answer = self.read_message()
        return answer

    def set_diameter(self, diameter):
        """
        From 0.1 to 14.0 mm Syringes smaller than 10 ml: Volume units are ‘μl’
        From 14.01 to 50.0 mm Syringes greater than or equal to 10 ml: Volume units are 'ml’
        """
        diameter = float(diameter)

        if diameter < 0.1:
            raise Exception("Syringe diameter must 0.1 mm or larger.")
        elif diameter > 50.0:
            raise Exception("Syringe diameter must be 50 mm or smaller.")

        self.send_message("DIA%1.2f" % diameter)
        self.read_message()

    def get_diameter(self):
        self.send_message("DIA")
        status, answer = self.read_message()
        return answer

    def set_rate(self, rate, unit):
        """
        UM = μl/min
        MM = ml/min
        UH = μl/hr
        MH = ml/hr

        Args:
            rate:
            unit:
        """

        self.send_message("RAT%1.4g%s" % (abs(float(rate)), str(unit)))
        self.read_message()

    def get_rate(self):
        """
        set the rate to be used

        Returns:

        """

        self.send_message("RAT")
        status, answer = self.read_message()
        return float(answer[:-2])

    def set_volume(self, volume):
        """
        set the volume to be dispensed

        Args:
            volume:

        Returns:
        """

        self.send_message("VOL%1.4g" % abs(float(volume)))
        self.read_message()

    def get_volume(self):

        self.send_message("VOL")
        status, answer = self.read_message()
        return float(answer[:-2])

    def set_volume_unit(self, unit):

        if unit not in ["ML", "UL"]:
            raise Exception("Volumen unit '%s' not supported. Allowed are 'ML' for microliters and 'UL' for"
                            "for microliters." % unit)

        self.send_message("VOL%s" % str(unit))
        self.read_message()

    def get_dispensed_volumes(self):

        self.send_message("DIS")
        status, answer = self.read_message()
        infused_volume = float(answer.replace("I", "").split("W")[0])
        withdrawn_volume = float(answer.replace("I", "").split("W")[1][:-2])
        return infused_volume, withdrawn_volume

    def clear_dispensed_volume(self):

        self.send_message("VOLINF")
        self.read_message()
        self.send_message("VOLWDR")
        self.read_message()

    def set_pumping_direction(self, direction):

        """
        Args:
            direction: pumping direction
                INF: Infuse
                WDR: Withdrawing 
                REV: Revert direction

        Returns:

        """

        self.send_message("DIR%s" % str(direction))
        self.read_message()

    def get_pumping_direction(self):

        self.send_message("DIR")
        status, answer = self.read_message()
        return answer
