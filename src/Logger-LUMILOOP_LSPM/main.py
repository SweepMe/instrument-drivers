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
# * Module: Logger
# * Instrument: LUMILOOP LPSM


import numpy as np

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug, error


class Device(EmptyDevice):
    description = """
        <h3>LUMILOOP LPSM power meter</h3>
        <p>The driver communicates with the LUMILOOP TCP server</p>
    """

    def __init__(self):
        super().__init__()

        self.shortname = "LPSM"

        self.port_manager = True
        self.port_types = ["TCPIP"]  # could be extended to SOCKET to circumvent use of VISA runtime

        self.port_properties = {
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
            "timeout": 2,
        }

    def set_GUIparameter(self):

        gui_parameter = {
            "Serial number": "",  # could be also changed to serial number for correct identification
            "Channel 1": True,
            "Channel 2": False,
            "Channel 3": False,
            "Mode": ["0", "1", "2", "3"],
            "Compensation frequency in Hz": "1e9",
            "Crossover frequency in Hz": "0",
            "Automatic video bandwidth": True,
            "Video bandwidth in Hz": "3e6",
        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.sn = int(parameter["Serial number"])
        self.channels = {}
        for i in range(1,4):
            self.channels[i] = parameter[f"Channel {i}"]
        self.all_channel_indices = [i-1 for i in self.channels if self.channels[i]]

        self.variables = [f"Power {i}" for i in self.channels if self.channels[i]]
        self.units = ["dBm" for i in self.channels if self.channels[i]]
        self.plottype = [True for i in self.channels if self.channels[i]]
        self.savetype = [True for i in self.channels if self.channels[i]]

        self.mode = int(parameter["Mode"])
        self.frequency = float(parameter["Compensation frequency in Hz"])
        self.lhfrequency = float(parameter["Crossover frequency in Hz"])
        self.automatic_video_bandwidth = parameter["Automatic video bandwidth"]
        self.video_bandwidth = float(parameter["Video bandwidth in Hz"])

    def connect(self):
        pass

        # Problems
        # *RST -> How to wait for the reset before continuing with further commands, *OPC? seems to respond immediately
        # :SYST:COU? -> no response Error -113 Undefined header
        # :MEASure[:PMeter]:RDY? [<MPMeter>] -> no response Error -113 Undefined header
        #

    def initialize(self):

        identifier = self.get_identification()
        print("Identifier:", identifier)

        self.clear()

        # self.reset()  # does not work yet as the reset is still ongoing when further commands are sent

        stb = self.get_status_byte()
        print("STB:", stb)

        opc = self.is_operation_complete()
        print("OPC:", opc)

        # count_meters = self.get_meter_count()  # does not work
        # print("Number of power meters:", count_meters)

        self.port.write(f":MPM:SER {self.sn}, {self.sn}")
        self.pm_index = self.sn

        print()
        print(f"Power meter {self.pm_index} properties")
        print("Channels:", self.get_meter_channels(self.pm_index))
        print("Version:", self.get_meter_version(self.pm_index))
        print("Model:", self.get_meter_model(self.pm_index))
        print("Firmware:", self.get_meter_firmware(self.pm_index))
        print("SN:", self.get_meter_serial_number(self.pm_index))
        print("Maker:", self.get_meter_maker(self.pm_index))
        # print("Ready:", self.get_meter_ready(self.pm_index))

        ready = self.is_system_ready(self.pm_index)
        print("Ready:", ready)

        if not ready:
            msg = "System not ready. Please wait until temperature has reached."
            raise Exception(msg)

    def deinitialize(self):
        self.print_all_errors()

    def configure(self):

        # Mode
        self.set_system_mode(self.pm_index, self.mode)
        mode = self.get_system_mode(self.pm_index)
        print("Mode:", mode)

        self.max_frequency = self.get_maximum_frequency(self.pm_index)
        self.min_frequency = self.get_minimum_frequency(self.pm_index)

        if self.frequency < self.min_frequency:
            msg = "Selected compensation frequency below calibration range."
            raise Exception(msg)

        if self.frequency > self.max_frequency:
            msg = "Selected compensation frequency above calibration range."
            raise Exception(msg)

        # Compensation Frequency
        self.set_frequency(self.pm_index, self.frequency)
        frequency = self.get_frequency(self.pm_index)
        print("Frequency in Hz:", frequency)

        # Low-high frequency
        self.set_frequency(self.pm_index, self.lhfrequency)
        frequency = self.get_frequency(self.pm_index)
        print("LH Frequency in Hz:", frequency)

        # Video bandwidth
        if self.automatic_video_bandwidth:
            self.set_automatic_video_bandwidth(self.pm_index, self.automatic_video_bandwidth)
        else:
            self.set_automatic_video_bandwidth(self.pm_index, not self.automatic_video_bandwidth)
            self.set_video_bandwidth(self.pm_index, self.video_bandwidth)

        # Triggering

        # Sweep times

    def measure(self):
        self.results = self.get_meter_power(self.pm_index)  # retrieves all power values from 1st device

    def call(self):

        return list(np.array(self.results)[self.all_channel_indices])

    def print_all_errors(self):

        while True:
            msg = self.get_error()
            print("Error:", msg)
            if "No error" in msg:
                break

    def get_identification(self):
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer

    def reset(self):
        self.port.write("*RST")

    def clear(self):
        self.port.write("*CLS")

    def get_status_byte(self):
        self.port.write("*STB?")
        answer = self.port.read()
        return int(answer)

    def is_operation_complete(self):
        self.port.write("*OPC?")
        answer = self.port.read()
        return int(answer)

    def is_system_ready(self, index: int):
        self.port.write(f":SYST:RDY? {index}")
        answer = self.port.read()
        return int(answer)

    def get_error(self):
        self.port.write(":SYST:ERR?")
        answer = self.port.read()
        return answer

    def get_error_count(self):
        self.port.write(":SYST:ERR:COUN?")
        answer = self.port.read()
        return int(answer)

    def get_meter_count(self):
        self.port.write(":SYST:COU?")
        answer = self.port.read()
        return int(answer)

    def get_meter_serial_number(self, index: int):
        self.port.write(f":SYST:SER? {index}")
        answer = self.port.read()
        return int(answer)

    def get_meter_maker(self, index: int):
        self.port.write(f":SYST:MAK? {index}")
        answer = self.port.read()
        return answer

    def get_meter_model(self, index: int):
        self.port.write(f":SYST:DEV? {index}")
        answer = self.port.read()
        return answer

    def get_meter_version(self, index: int):
        self.port.write(f":SYST:VERS? {index}")
        answer = self.port.read()
        return answer

    def get_meter_firmware(self, index: int):
        self.port.write(f":SYST:FVERS? {index}")
        answer = self.port.read()
        return answer

    def get_meter_mode(self, index: int):
        self.port.write(f":MEAS:MOD? {index}")
        answer = self.port.read()
        return int(answer)

    def get_meter_ready(self, index: int):
        self.port.write(f":MEAS:READY? {index}")
        answer = self.port.read()
        return bool(int(answer))

    def get_meter_power(self, index: int):
        self.port.write(f":MEAS:ALL? {index}")
        answer = self.port.read()
        return list(map(float, answer.split(",")))

    def get_meter_channels(self, index: int):
        self.port.write(f"SYST:CHAN? {index}")
        answer = self.port.read()
        return int(answer)

    def set_system_mode(self, index: int, mode: int):
        self.port.write(f":SYST:MOD {mode}, {index}")

    def get_system_mode(self, index: int):
        self.port.write(f":SYST:MOD? {index}")
        answer = self.port.read()
        return int(answer)

    def set_frequency(self, index: int, frequency: float):
        self.port.write(f":SYST:FREQ {frequency}, {index}")

    def get_frequency(self, index: int):
        self.port.write(f":SYST:FREQ? {index}")
        answer = self.port.read()
        return float(answer)

    def get_minimum_frequency(self, index: int):
        self.port.write(f":SYST:FREQ:MIN? {index}")
        answer = self.port.read()
        return float(answer)

    def get_maximum_frequency(self, index: int):
        self.port.write(f":SYST:FREQ:MAX? {index}")
        answer = self.port.read()
        return float(answer)

    def set_LHfrequency(self, index: int, frequency: float):
        self.port.write(f":SYST:LHF {frequency}, {index}")

    def get_LHfrequency(self, index: int):
        self.port.write(f":SYST:LHF? {index}")
        answer = self.port.read()
        return float(answer)

    def set_automatic_video_bandwidth(self, index: int, state: bool):
        self.port.write(f":MEAS:AUTOVBW {int(state)}, {index}")

    def is_automatic_video_bandwidth(self, index: int):
        self.port.write(f":MEAS:AUTOVBW? {index}")
        answer = self.port.read()
        return int(answer)

    def set_video_bandwidth(self, index: int, frequency: float):
        self.port.write(f":MEAS:VBW {frequency}, {index}")

    def get_video_bandwidth(self, index: int):
        self.port.write(f":MEAS:VBW? {index}")
        answer = self.port.read()
        return float(answer)