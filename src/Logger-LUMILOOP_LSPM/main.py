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
        self.variables = ["Power1", "Power2", "Power3"]
        self.units = ["dBm", "dBm", "dBm"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        self.port_manager = True
        self.port_types = ["TCPIP", "SOCKET"]

        self.port_properties = {
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
        }

    def set_GUIparameter(self):

        gui_parameter = {
            "Serial number": "",  # could be also changed to serial number for correct identification
        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.sn = int(parameter["Serial number"])

    def connect(self):
        pass
        # TODO: Find power meter index for given serial number

    def initialize(self):

        identifier = self.get_identification()
        print("Identifier:", identifier)

        count_meters = self.get_meter_count()
        print("Number of power meters:", count_meters)

        for i in range(1, count_meters+1):
            print()
            print(f"Power meter {i} properties")
            print("Mode:", self.get_meter_mode(i))
            print("Maker:", self.get_meter_maker(i))
            print("Model:", self.get_meter_model(i))
            print("Version:", self.get_meter_version(i))
            print("Firmware:", self.get_meter_firmware(i))
            print("SN:", self.get_meter_serial_number(i))
            print("Ready:", self.get_meter_ready(i))

    def configure(self):

        # Video bandwidth

        # Low pass frequency

        # Triggering

        # Sweep times

        # Frequencies

        self.print_all_errors()

    def measure(self):
        self.p1, self.p2, self.p3 = self.get_meter_power(1)  # retrieve power values from 1st device

    def call(self):
        return self.p1, self.p2, self.p3

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

    def get_error(self):
        self.port.write(":SYST:ERR?")
        answer = self.port.read()
        return answer

    def get_error_count(self):
        self.port.write(":SYST:ERR:COUN?")
        answer = self.port.read()
        return int(answer)

    def get_meter_count(self):
        self.port.write(":SYST:COUN?")
        answer = self.port.read()
        return int(answer)

    def get_meter_serial_number(self, index: int):
        self.port.write(f":SYST:SER? {index}")
        answer = self.port.read()
        return answer

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
        self.port.write(f":MEAS:RDY? {index}")
        answer = self.port.read()
        return bool(int(answer))

    def get_meter_power(self, index: int):
        self.port.write(f":MEAS:ALL? {index}")
        answer = self.port.read()
        return list(map(float, answer))
