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


# SweepMe! device class
# Type: WaferProber
# Device: Accretech UF series

import inspect
from datetime import datetime
from typing import List, Tuple

from pysweepme.ErrorMessage import debug
from pyvisa import constants

try:
    from pysweepme.UserInterface import get_input
except ModuleNotFoundError:
    # using the default input function that does not work with SweepMe! (only standalone scripts)
    get_input = input
    print(
        "accretech_uf: Please use the latest version of SweepMe! to use this driver."
        " Falling back to 'input' method that only works with pysweepme standalone scripts."
    )


class AccretechProber:
    def __init__(self, port):

        self.port = port

        self._verbose = False

        self.event_type = constants.EventType.service_request
        self.event_mech = constants.EventMechanism.queue

        if not self.port.port:
            raise Exception(
                "No connection established with Accretech UF prober. "
                "Please check port address / instrument is connected"
            )

        self.register_srq_event()

        # not used at the moment as the default is set in acquire_status_byte()
        # self.service_request_timeout = 5  # in seconds

        # Status Bytes codes
        self.stb_codes = {
            64: "End of GPIB initial setting",
            65: "End of X/Y-axis movement",
            66: "End of movement to coordinator value",
            67: "Z UP (test start)",
            68: "Z DOWN",
            69: "End of marking",
            70: "First chip (End of wafer loading)",
            71: "End of wafer unloading",
            74: "Out of probing area",
            76: "Format error - Execution condition error - Error",
            77: "End of index size setting",
            78: "End of pass count up",
            79: "End of fail count up",
            80: "Wafer count",
            81: "Wafer end - End of sub die",
            82: "Cassette end",
            84: "Alignment rejected",
            85: "Probing stop by command (without alarm)",
            86: "End of cleaning wafer - End of print data reception",
            87: "Warning",
            88: "Test start (Count not needed)",
            89: "End of needle cleaning",
            90: "Probing stop",
            91: "Probing start",
            92: "End of Z UP/Z DOWN",
            93: "End of hot chuck control command reception",
            94: "End of lot process",
            95: "STOP command reception - Removing the cassette",
            97: "Setting and removing the cassette",
            98: "Normal end of commands - Completion of next block transfer",
            99: "Abnormal end of commands",
            100: "Test complete reception",
            101: "Normal end of em command",
            103: "Normal end of map data downloading",
            104: "Abnormal end of map data downloading",
            105: "Ready to execute needle height setting process",
            107: "Start of binary data uploading",
            108: "End of binary data uploading",
            109: "End of last passed die movement",
            110: "Normal end of inspection",
            111: "Abnormal end of inspection",
            112: "End of wafer sensing",
            113: "End of re-execution of wafer alignment process",
            114: "Normal end of auto needle alignment process",
            115: "Abnormal end of auto needle alignment process",
            116: "End of contact height settling",
            117: "Continuous fail error",
            118: "End of wafer loading",
            119: "Centering - Completion of alarm reset",
            120: "Normal end of start command - Request downloading probing result map data",
            121: "Abnormal end of start command",
            122: "End of 1 pas PMI",
            123: "End if fail mark inspection",
            124: "End of preload",
            125: "Probing stop via GEM host",
            127: "End of all sub dies",
        }

        # Ignored status bytes that from 0 to 63 that randomly happen
        ignored_stb_codes = {}
        for i in range(64):
            ignored_stb_codes[i] = "Unknown - Ignored status byte"
        self.stb_codes.update(ignored_stb_codes)

        self.prober_status_codes = {
            "I": "Waiting for lot process to start",
            "C": "Probe card is being changed",
            "R": "Performing lot process",
            "E": "Error is occurring",
        }

        self.cassette_status_codes = {
            "0": "Not Ready (No cassette)",
            "1": "Ready (Before lot process start)",
            "2": "Performing lot process",
            "3": "End of lot process",
            "4": "Cassette for rejects",
        }

        self.wafer_status_codes = {
            "0": "No wafer",
            "1": "Before probing start",
            "2": "End of probing",
            "3": "During probing",
        }

        self.error_status_codes = {
            "S": "System error",
            "E": "Error",
            "O": "Operator call",
            "W": "Warning error",
            "I": "Information",
        }

        self.error_codes = {
            # GP-IB I/F TRANSMIT ERROR!!
            "O0651": "When the equipment sends STB code or response data to the tester, an error "
            "occurs in the driver software for the GPIB interface control on the prober side.",
            # GP-IB RECEIVE COMMAND FORMAT INVALID!!
            "O0660": "The format of the received command (used characters or number of bytes) is incorrect.",
            # GP-IB COMMAND EXECUTION ERROR!!
            "O0661": "The prober cannot execute the received command due to its status or timing.",
            # GP-IB COMMUNICATION TIMEOUT ERROR!!
            "O0667": "The period of time before sending a GPIB command from the tester side "
            "exceeds the timeout set in the equipment.",
            # GP-IB I/F RECEIVE ERRRO!
            "S0650": "When the equipment receives the command from the tester, "
            "an error occurs in the driver software for the GPIB interface control on the prober side",
        }

    def __del__(self):
        self.unregister_srq_event()

    def register_srq_event(self):
        self.port.port.enable_event(self.event_type, self.event_mech)

    def unregister_srq_event(self):
        self.port.port.disable_event(self.event_type, self.event_mech)

    def set_verbose(self, state=True):

        self._verbose = state

    def get_prober_status_message(self, prober_status):
        """

        Args:
            prober_status:
                str: 'I', 'C', 'R', or 'E'

        Returns:
            str -> prober status message
        """

        if prober_status in self.prober_status_codes:
            return self.prober_status_codes[prober_status]
        else:
            raise ValueError("Prober status '%s' unknown." % str(prober_status))

    @staticmethod
    def get_waferlist_from_status(wafer_status: str) -> List[Tuple[int, int]]:

        wafer_list = []

        # iterates through cassettes
        for cassette_id, cassette_info in enumerate(wafer_status.split(".")):
            status = cassette_info[0]
            wafers = cassette_info[1:]
            if status != "0":
                # iterates trough wafers of each cassette
                for wafer_id, val in enumerate(wafers):
                    if val != "0":
                        # adding a tuple of cassette and wafer number
                        wafer_list.append((cassette_id + 1, wafer_id + 1))

        return wafer_list

    def wait_until_status_byte(self, stb_success, timeout=5.0):
        """
        Args:
            stb_success: integer or tuple of integer. The function waits until one of the given
              status bytes has been acquired.
            timeout: float, timeout in seconds to acquire a status byte until a Timeout Error is raised.

        Returns:
            int: status byte

        """

        # this is the name of the function calling acquire_status_byte
        function_calling_name = inspect.stack()[1].function
        now = datetime.now()  # current date and time
        if self._verbose:
            print()
            print("-->", now.strftime("%H:%M:%S"), "Function:", function_calling_name)

        if isinstance(stb_success, int):
            stb_success = (stb_success,)  # make it a tuple

        stb = None
        while stb not in stb_success:
            stb = self.acquire_status_byte(timeout)

        return stb

    def acquire_status_byte(self, timeout=10.0):
        """

        Args:
            timeout:  Timeout value to wait for SRQ event in seconds

        Returns:
            int: status byte

        """

        # this is the name of the function calling acquire_status_byte
        function_calling_name = inspect.stack()[1].function
        if (
            function_calling_name != "wait_until_status_byte"
            and function_calling_name != "acquire_status_byte"
        ):
            now = datetime.now()  # current date and time
            if self._verbose:
                print()
                print(
                    "-->", now.strftime("%H:%M:%S"), "Function:", function_calling_name
                )

        # Wait for the SRQ event to occur
        response = self.port.port.wait_on_event(
            self.event_type, int(timeout * 1000)
        )  # conversion from s to ms

        # The event mechanism was changed after pyvisa 1.9.0 and the WaitResponse structure is different
        if hasattr(response, "event"):
            # pyvisa default way, for version such as 1.12.0
            assert response.event.event_type == self.event_type, (
                "Wrong event type, " "expected service request (SRQ) event!"
            )
        else:
            # pyvisa 1.9.0
            assert response.event_type == self.event_type, (
                "Wrong event type, " "expected service request (SRQ) event!"
            )
        assert (
            response.timed_out is False
        ), "Timeout expired during waiting for service request SRQ!"

        stb = self.port.port.read_stb()
        now = datetime.now()  # current date and time
        if self._verbose:
            print(
                "<--",
                now.strftime("%H:%M:%S"),
                "Returned STB:",
                stb,
                self.stb_codes[stb],
            )

        if stb == 76:  # Error
            error_code = self.request_error_code()
            # the status letter at the beginning of the code
            error_status = error_code[0]
            # error_number = int(error_code[1:])
            error_type = self.error_status_codes[error_status]
            error_message = self.request_error_message()
            print()
            print(
                error_type, "(%s):" % error_code, error_message, "after status byte 76"
            )

            # If an error occurs that cannot be handled, we stop the program by throwing an exception
            if error_code in list(self.error_codes.keys()):
                raise Exception(
                    error_type,
                    "(%s):" % error_code,
                    error_message,
                    "after status byte 76",
                )

            while True:
                msg = "Accretech: " + error_type + " (%s): " % error_code + error_message + " after status byte 76"
                answer = get_input(msg + "\n\nDo you like to continue y/n?")

                if answer.lower() == "y":
                    # we call this function again to make sure a new status byte is retrieved
                    # if a further error happens, this functions will be called again
                    stb = self.acquire_status_byte(timeout)
                    break
                elif answer.lower() == "n":
                    raise Exception(
                        error_type,
                        "(%s):" % error_code,
                        error_message,
                        "after status byte 76",
                    )

        return stb

    def query(self, cmd):

        self.port.write(cmd)
        answer = self.port.read()
        return answer[len(cmd) :]

    def raise_error(self, stb: int):
        function_calling_name = inspect.stack()[1].function
        stb_message = self.stb_codes[stb]
        raise Exception(
            f"Accretech UF series function '{function_calling_name}' did not succeed: "
            f"STB {stb} ('{stb_message}')"
        )

    def request_prober_id(self):

        return self.query("B")

    def request_wafer_id(self):

        return self.query("b")

    def request_prober_type(self):

        answer = self.query("PV")
        prober_type = answer[:6]
        return prober_type

    def request_system_version(self):

        answer = self.query("PV")
        system_version = answer[6:]
        return system_version

    def request_error_code(self):

        return self.query("E")

    def request_error_message(self):

        return self.query("e")

    def request_wafer_status(self):
        """
        queries the wafer status

        Returns: str with 53 characters
            Position:
            1  -> Cassette 1 status
            2-26  - > Wafer statuses of cassette 1
            27 ->  . (A point separating infos of cassette 1 and cassette 2
            28 -> Cassette 2 status
            29-53 -> Wafer statuses of cassette 2

        """

        return self.query("w")

    def request_cassette_status(self):
        """
        Position
        1 + 2: slot number in the cassette that stores the wafer on the chuck
        3 + 4: Number of wafers in the cassette for which the probing has not been performed
        5:     Information that shows the status of the cassette in load port 1 or elevator 1
        6:     Information that shows the status of the cassette in load port 2 or elevator 2
        Returns:
            int, Status byte code
        """

        return self.query("x")

    def request_prober_status(self):

        return self.query("ms")

    def request_parameter(self, value):
        """

        Args:
            value:  00 Device name
                    01 Wafer size
                    20 Card Type
                    22 Wafer thickness
                    24 Contact height

        Returns:
        """

        return self.query("i%02d" % int(value))

    def request_device_name(self):
        return self.request_parameter(0)

    def request_wafer_size(self):
        return self.request_parameter(1)

    def request_card_type(self):
        return self.request_parameter(20)

    def request_wafer_thickness(self):
        return self.request_parameter(22)

    def request_contact_height(self):
        return self.request_parameter(24)

    def request_onwafer_info(self):
        """
        Retrieves on-wafer information by returning status integer (0 or 1) for sites 1-8
        Returns:
            tuple of integers: status 1 or 0 for site 1-8
        """
        answer = self.query("O")
        bit_list = tuple(map(int, '{:016b}'.format(ord(answer))))
        return (bit_list[7],  # site 1
                bit_list[6],  # site 2
                bit_list[5],  # site 3
                bit_list[4],  # site 4
                bit_list[15],  # site 5
                bit_list[14],  # site 6
                bit_list[13],  # site 7
                bit_list[12])  # site 8

    def request_onwafer_info_with_marking(self):
        return self.query("o")

    def request_operator_name(self):
        return self.query("OP")

    def request_die_coordinate(self):
        """

        Returns:
            int: x coordinate of the current die
            int: y coordinate of the current die
        """

        answer = self.query("Q")
        yindex = answer.find("Y")
        xindex = answer.find("X")

        y = int(answer[yindex + 1 : xindex])
        x = int(answer[xindex + 1 :])

        return x, y

    def request_first_die_coordinate(self):
        """

        Returns:
            int: x coordinate of the current die
            int: y coordinate of the current die
        """

        answer = self.query("q")
        yindex = answer.find("Y")
        xindex = answer.find("X")

        y = int(answer[yindex + 1 : xindex])
        x = int(answer[xindex + 1 :])

        return x, y

    def request_subdie_coordinate(self):
        """
        Returns:
            int: x coordinate of the current subdie
            int: y coordinate of the current subdie
            int: s index of the current subdie
        """

        answer = self.query("QS")

        yindex = answer.find("Y")
        xindex = answer.find("X")
        sindex = answer.find("S")

        y = int(answer[yindex + 1 : xindex])
        x = int(answer[xindex + 1 : sindex])
        s = int(answer[sindex + 1 :])

        return x, y, s

    def request_cassette_slot(self):
        """

        Returns:
            int: cassette index
            int: slot index
        """

        answer = self.query("X")
        cassette_index = int(answer[2])
        slot_index = int(answer[:2])
        return cassette_index, slot_index

    def request_current_status(self):
        """
        requests z-axis status, wafer status, and alarm status

        Returns:
            int: z-axis status -> 0 = Other than contact status, 1 = Contact status
            int: wafer status  -> 0 = No wafer on the chuck, 1 =  Wafer on the chuck
            int: alarm status  -> 0 = No alarm occurs, 1 = Alarm is occuring

        """

        answer = self.query("S1")

        zaxis_status = int(answer[1])
        wafer_status = int(answer[3])
        alarm_status = int(answer[5])

        return zaxis_status, wafer_status, alarm_status

    def request_position(self):
        """
        get the current absolute position

        Caution: Unit depends on system settings. Using 'Metric' unit is 1e-1 µm. Using 'English' unit is 1e-5 inch.

        Attention:
        The command 'R' was designed for 200 mm wafer and might not work with 300 mm wafer
        In future, one could use the command ur11401 und ur11402 to read x and y position. The 'ur' command is used
        to read parameter values. However, the coordinate system of ur11401 und ur11402 is different with respect to
        the 'R' command

        Returns:
            int: x coordinate in µm
            int: y coordinate in µm
        """

        self.port.write("R")
        answer = self.port.read()
        x = int(answer[-7:])*0.1
        y = int(answer[2:9])*0.1

        return x, y

    def is_chuck_contacted(self):
        return bool(self.request_current_status()[0])

    def is_wafer_on_chuck(self):
        return bool(self.request_current_status()[1])

    def is_last_wafer_on_chuck(self):
        self.query("LIW")
        answer = self.port.read()
        return answer == "1"

    def is_alarm(self):
        return bool(self.request_current_status()[2])

    def get_device_parameters(self):
        """
        makes the device parameters available

        Returns:

        """

        return self.query("ku")

    def check_status_byte(self, status_byte):
        """

        Args:
            status_byte: integer between 64 and 127 that is used to check the status byte communication

        Returns:
            int: returned status byte that was sent to the prober

        """

        status_byte = int(status_byte)
        self.port.write("STB%03d" % status_byte)
        stb = self.wait_until_status_byte(status_byte, timeout=10.0)
        return stb

    def start(self):
        """

        Returns:
            int: status byte
                # 120
                # 121 Abnormal end
        """

        self.port.write("st")
        stb = self.wait_until_status_byte((120, 121), timeout=300.0)
        if stb == 121:
            self.raise_error(stb)
        return stb

    def stop(self):
        """
        This command stops the probing and return status byte 90.
        If the operator resets the alarm a status byte 85 is sent, that is not handled by this function

        Returns:
            int: status byte
                # 90 Probing stop
        """

        self.port.write("K")
        stb = self.wait_until_status_byte(
            90, timeout=600.0
        )
        return stb

    def terminate_lot_process_forcibly(self):
        """
        forces to terminate the the lot process

        Returns:
            int: status byte
                # 98
                # 99
        """

        self.port.write("le")
        stb = self.wait_until_status_byte((98, 99), timeout=180.0)
        if stb == 99:
            self.raise_error(stb)
        return stb

    def terminate_lot_process_immediately(self):
        """

        Returns:
            int: status byte
                # 94
                # 99
        """

        self.port.write("jv")
        stb = self.wait_until_status_byte((94, 99), timeout=180.0)
        if stb == 99:
            self.raise_error(stb)
        return stb

    def unload(self):
        """

        Returns:
            int: status  byte
                # 71
        """

        self.port.write("U")
        stb = self.wait_until_status_byte(71, timeout=180.0)
        return stb

    def unload_all_wafers(self):
        """

        Returns:
            int: status byte
                # 94
        """

        self.port.write("U0")
        stb = self.wait_until_status_byte(94, timeout=30.0)
        return stb

    def unload_to_inspection_tray(self):
        """

        Returns:
            int: status  byte
                # 71
        """

        self.port.write("U9")
        stb = self.wait_until_status_byte(71, timeout=120.0)
        return stb

    def load_specified_wafer(self, cassette, slot):
        """
        This command can be use to load a wafer from a cassette. It indirectly starts
         a lot process and is not used with 'start'.
        You can terminate the lot process by using cassette = 9 and slot = 99

        Args:
            cassette: id of the cassette, being
                        1 -> cassette 1
                        2 -> cassette 2
                        5 -> inspection tray
                        6 -> fixed tray
                        9 -> can be used to terminate lot process if slot is 99
            slot: if of the slot
                        1 - 25 -> in case cassette is 1 or 2
                        0 -> in case of cassette = 5 (inspection tray)
                        0, 1, 2 -> in case of cassette = 6 (fixed tray)
                        99 -> in case of cassette = 9 (terminate lot process)

        Returns:
            int: status byte
                # 94 -> end of lot process
                # 70 -> First chip (End of wafer loading)
        """

        if int(cassette) == 9 and int(slot) != 99:
            raise Exception(
                "Accretech UF series: slot id must be 99 if cassette id is 9."
            )
        elif int(slot) == 99 and int(cassette) != 9:
            raise Exception(
                "Accretech UF series: cassette id must be 9 if slot id is 99."
            )

        self.port.write("j2%i%02d" % (int(cassette), int(slot)))
        stb = self.wait_until_status_byte((70, 94), timeout=600.0)

        return stb

    def preload_specified_wafer(self, cassette, slot):
        """
        This command ("j3") can be use to preload a wafer from a cassette to the subchuck.
        If there is a wafer on the chuck, it is unloaded to the cassette.
        If there is already a wafer on the subchuck, it gets loaded to the chuck.
        You can terminate a lot process by using cassette = 9 and slot = 99
        A wafer can be loaded back from the chuck to the subchuck using cassette = 0 and slot = 0.
        This command is typically used in conjunction with 'load_preload_wafer' ("j4") in order to load the chuck and
        preload the subchuck at the first step of the lot process.


        Args:
            cassette: id of the cassette, being
                        0 -> unloads the wafer on the chuck and loads it onto the subchuck if slot = 0
                        1 -> cassette 1
                        2 -> cassette 2
                        5 -> inspection tray
                        6 -> fixed tray
                        9 -> can be used to terminate lot process if slot is 99
            slot: if of the slot
                        0 -> unloads the wafer on the chuck and loads it onto the subchuck if cassette = 0
                        1 - 25 -> in case cassette is 1 or 2
                        0 -> in case of cassette = 5 (inspection tray)
                        0, 1, 2 -> in case of cassette = 6 (fixed tray)
                        99 -> in case of cassette = 9 (terminate lot process)

        Returns:
            int: stb
                # 94 -> end of lot process
                # 70 -> First chip (End of wafer loading)
        """

        if int(cassette) == 9 and int(slot) != 99:
            raise Exception(
                "Accretech UF series: slot id must be 99 if cassette id is 9."
            )
        elif int(slot) == 99 and int(cassette) != 9:
            raise Exception(
                "Accretech UF series: cassette id must be 9 if slot id is 99."
            )

        if int(cassette) == 0 and int(slot) != 0:
            raise Exception(
                "Accretech UF series: slot id must be 0 if cassette id is 0."
            )

        self.port.write("j3%i%02d" % (int(cassette), int(slot)))
        stb = self.wait_until_status_byte((94, 70), timeout=300.0)
        return stb

    def load_and_preload_specified_wafers(
        self, cassette, slot, preload_cassette, preload_slot
    ):
        """
        This command ("j4") is used at the beginning of a lot process to load a wafer on the chuck and
        preload another wafer on the subchuck.
        Afterwards one can continue with the command 'preload_specified_wafer' ("j3").

        Args:
            cassette: cassette id 1 or 2, 5 for inspection tray, and 6 for fixed tray
            slot: slot id 1-25 for cassettes, 0 for inspection tray, and 1-2 for fixed tray
            preload_cassette: cassette id 1 or 2
            preload_slot: slot id 1 or 2

        Returns:
            int: status byte
                # 70: First chip (End of wafer loading)
        """

        self.port.write(
            "j4%i%02d%i%02d"
            % (int(cassette), int(slot), int(preload_cassette), int(preload_slot))
        )
        stb = self.wait_until_status_byte(70, timeout=300.0)

        return stb

    def load_wafer_aligned(self):
        """

        Returns:
            int: status byte
                # 70: First chip (End of wafer loading)
                # 94: End of lot process
        """

        self.port.write("L")
        stb = self.wait_until_status_byte((70, 94), timeout=180.0)

        return stb

    def load_wafer_unaligned(self):
        """

        Returns:
            int: status byte
                # 118: End of wafer loading
        """

        self.port.write("L1")
        stb = self.wait_until_status_byte(118, timeout=60.0)

        return stb

    def preload_wafer(self):
        """

        Returns:
            int: status byte
            # 118: End of wafer loading

        """

        self.port.write("L8")
        stb = self.wait_until_status_byte(118, timeout=60.0)

        return stb

    def load_inspection_wafer_aligned(self):
        """

        Returns:
            int: status byte
                # 70: First chip (End of wafer loading)
                # 94: End of lot process
        """

        self.port.write("LI")
        stb = self.wait_until_status_byte((70, 94), timeout=300.0)

        return stb

    def load_inspection_wafer_unaligned(self):

        self.port.write("L9")
        stb = self.wait_until_status_byte(118, timeout=120.0)
        # 118: End of wafer loading
        return stb

    def move_position(self, x, y):
        """
        relative move at the current position.

        Caution: Unit depends on system settings. Using 'Metric' unit is µm. Using 'English' unit is 0.1 mil.

        Args:
            x: distance in x direction
            y: distance in y direction

        Returns:
            int: status byte
                # 65: End of X/Y-axis movement
                # 67: Z UP (test start)
                # 74: Out of probing area
        """

        self.port.write("AY{:+07}X{:+07}".format(int(y), int(x)))

        stb = self.wait_until_status_byte((65, 67), timeout=30.0)


        return stb

    def move_next_die(self):
        """
        moves to the next die, the chuck remains in the position as it was beforehand.

        # 66: End of movement to coordinator value
        # 67: Z UP (test start)
        # 81: Wafer end -> just signals that there will be no further die on that wafer (not forwarded here)
        """

        self.port.write("J")
        stb = self.wait_until_status_byte((67, 66), timeout=30.0)

        return stb

    def move_specified_die(self, x, y):
        """
        Move to specified die coordinate value

        Args:
            x: index coordinate of the x axis
            y: index coordinate of the y axis

        Returns:
            int: status byte
                # 66: End of movement to coordinator value
                # 67: Z UP (test start)
                # 74: Out of probing area
        """

        self.port.write("JY%04dX%04d" % (int(y), int(x)))

        stb = self.wait_until_status_byte((66, 67, 74), timeout=30.0)
        if stb == 74:
            self.raise_error(stb)

        return stb

    def move_next_subdie_block(self):
        """
        moves to next subdie block

            # 66: End of movement to coordinator value
            # 67: Z UP (test start)
            # 81: Wafer end
            # 127: End of all sub dies -> just signals that there will be no further sub die (not forwarded here)
        """

        self.port.write("JJ")
        stb = self.wait_until_status_byte((66, 67), timeout=30.0)

        return stb

    def move_next_subdie(self):
        """
        chuck is automatically put to Z DOWN before movement to next die

        # 66: End of movement to coordinator value
        # 67: Z UP (test start)
        # 81: End of sub die -> just signals that there will be no further sub die on that die (not forwarded here)
        """

        self.port.write("JS")
        stb = self.wait_until_status_byte((66, 67), timeout=30.0)

        return stb

    def move_specified_subdie(self, x, y, s):
        """

        Args:
            x: sub die block coordinate in x-direction
            y: sub die block coordinate in y-direction
            s: sub die address

        Returns:
            int: status byte
                # 66: End of movement to coordinator value
                # 67: Z UP (test start)

        """

        self.port.write("JSY%03dX%03dS%03d" % (int(y), int(x), int(s)))
        stb = self.wait_until_status_byte((66, 67), timeout=10.0)

        return stb

    def move_contact_position(self, position):
        """

        Args:
            position:

        Returns:
            int: status byte
                # 65: End of X/Y-axis movement
                # 67: Z UP (test start)
                # 74: Out of probing area

        """

        self.port.write("CM%02dX" % (int(position)))
        stb = self.wait_until_status_byte((65, 67, 74), timeout=10.0)

        return stb

    def sense_wafers(self, cassette="") -> int:
        """
        sense all wafer in all cassettes or a specific cassette

        Args:
            cassette: 1 or 2

        Returns:
            int: status byte
                # 98
        """

        self.port.write("jw" + str(cassette))
        stb = self.wait_until_status_byte(98, timeout=30.0)
        return stb

    def align_wafer(self):
        """
        This commands re-executes the wafer alignment process if a wafer is on the chuck.
         If there is no wafer on the chuck it loads the next the wafer
         first, before doing the alignment process.

        Returns:
            int: status byte
                # 70: First chip (End of wafer loading)
        """

        self.port.write("N")
        stb = self.wait_until_status_byte(70, timeout=60.0)

        return stb

    def align_wafer_only(self):
        """
        This commands re-executes the wafer alignment process if a wafer is on the chuck. It does not succeed if there
        is no wafer on the chuck.

        Returns:
            int: status byte
                # 113: End of re-execution of wafer alignment process
        """

        self.port.write("N1")
        stb = self.wait_until_status_byte(113, timeout=60.0)

        return stb

    def align_needle(self):
        """
        This commands re-executes the needle alignment process for a wafer that has already been aligned.

        Returns:
            int: status byte
                # 114: Normal end of auto needle alignment process
                # 115: Abnormal end of auto needle alignment process
        """

        self.port.write("N2")
        stb = self.wait_until_status_byte((114, 115), timeout=60.0)

        return stb

    def align_wafer_from_inspection_tray(self):
        """
        This commands performs a wafer and needle alignment and should be used in conjunction with
        load_inspection_wafer_unaligned ("L9")

        Returns:
            int: status byte
                # 119: Centering
        """

        self.port.write("N9")
        stb = self.wait_until_status_byte(119, timeout=300.0)

        return stb

    def z_up(self) -> int:
        """
        moves the chuck up in order to contact the wafer

        Returns:
             int: status byte
                # 67
        """

        self.port.write("Z")
        stb = self.wait_until_status_byte(67)
        return stb

    def z_down(self) -> int:
        """
        moves the chuck down in order to not contact the wafer

        Returns:
             int: status byte code
                # 68
        """

        self.port.write("D")
        stb = self.wait_until_status_byte(68)
        return stb

    def set_alarm(self, message):

        if len(message) > 20:
            message = message[:20]  # restrict to 20 characters
            debug(
                "Accretech UF series function 'set_alarm': No more than 20 characters are allowed!"
            )

        self.port.write("em" + str(message))
        stb = self.wait_until_status_byte(101)
        return stb

    def reset_alarm(self):

        self.port.write("es")
        stb = self.wait_until_status_byte(119)
        return stb
