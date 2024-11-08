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
import time

# SweepMe! driver
# * Module: SMU
# * Instrument: aSpectSystems idSMU modules

from pysweepme import FolderManager as FoMa
from pysweepme.EmptyDeviceClass import EmptyDevice

FoMa.addFolderToPATH()

from aspectdeviceengine.enginecore import IdSmuService, IdSmuServiceRunner, IdSmuBoardModel, SmuCurrentRange


class Device(EmptyDevice):
    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "idSMUx"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.srunner: IdSmuServiceRunner = None
        self.service: IdSmuService = None
        # self.smu: aspectdeviceengine.enginecore.IdSmu2Module = None
        # self.channel: aspectdeviceengine.enginecore.AD5522ChannelModel = None

        # Measurement Parameters
        self.channels: list = [1, 2, 3, 4]
        self.channel_number: int = 1
        self.source: str = "Voltage in V"
        self.protection: float = 0.1

        self.current_ranges = {
            "5uA": SmuCurrentRange._5uA,
            "20uA": SmuCurrentRange._20uA,
            "200uA": SmuCurrentRange._200uA,
            "2mA": SmuCurrentRange._2mA,
            "70mA": SmuCurrentRange._70mA,
        }
        self.current_range: SmuCurrentRange = SmuCurrentRange._70mA



    @staticmethod
    def find_ports() -> list:
        """Return a list of connected devices."""
        srunner = IdSmuServiceRunner()
        service = srunner.get_idsmu_service()

        # Get first board to automatically detect connected devices
        first_board = service.get_first_board()
        print(first_board.get_current_range("M1.S1.C1"))
        ports = service.get_board_addresses()

        # TODO: Need list of devices such as M1.S1, M1.S2, ... in case multiple boards are connected

        # Always shut down the service runner
        srunner.shutdown()

        return ports

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard GUI parameters."""
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": self.channels,
            "RouteOut": ["Front"],
            "Compliance": 0.1,
            "Range": list(self.current_ranges),
            # "RangeVoltage": [1],
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle the GUI parameters."""
        self.source = parameter["SweepMode"]
        self.protection = parameter["Compliance"]

        # channel_ids = ["M1.S1.C1", "M1.S1.C2", "M1.S1.C3", "M1.S1.C4"]
        self.channel_number = int(parameter["Channel"])
        self.current_range = self.current_ranges[parameter["Range"]]

    def connect(self) -> None:
        """Connect to the SMU."""
        self.srunner = IdSmuServiceRunner()
        self.service = self.srunner.get_idsmu_service()

        first_board = self.service.get_first_board()

        self.smu = first_board.idSmu2Modules["M1.S1"]
        self.channel = self.smu.smu.channels[self.channel_number]

    def disconnect(self) -> None:
        """Terminate the connection to the SMU."""
        self.srunner.shutdown()

    def initialize(self) -> None:
        """Enable the SMU channel."""
        if not self.channel.enabled:
            self.channel.enabled = True

    def configure(self):
        self.channel.current_range = self.current_range

    def apply(self) -> None:
        """Set the voltage or current on the SMU."""
        if self.source == "Voltage in V":
            self.channel.voltage = float(self.value)
        elif self.source == "Current in A":
            self.channel.current = float(self.value)

    def measure(self) -> None:
        """Read the voltage and current from the SMU."""
        self.i = self.channel.current
        self.v = self.channel.voltage

    def call(self) -> list:
        """Return the voltage and current."""
        return [self.v, self.i]
