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
import numpy as np

# SweepMe! driver
# * Module: SMU
# * Instrument: aSpectSystems idSMU modules
from pysweepme import FolderManager as FoMa
from pysweepme.EmptyDeviceClass import EmptyDevice

FoMa.addFolderToPATH()

from aspectdeviceengine.enginecore import IdSmuServiceRunner, SmuCurrentRange, MeasurementMode, ListSweepChannelConfiguration, ListSweep


class Device(EmptyDevice):
    """Device Class for the aSpectSystems idSMU modules."""
    def __init__(self) -> None:
        """Initialize the Device Class."""
        EmptyDevice.__init__(self)

        self.shortname = "idSMUx"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Communication Parameters
        self.identifier: str = "idSMUx_"  # TODO: Maybe add the serial number here
        self.board_id: str = "M1.S1"
        self.srunner: IdSmuServiceRunner = None

        # Measurement Parameters
        self.channels: list = [1, 2, 3, 4]
        self.channel_number: int = 1
        self.source: str = "Voltage in V"
        self.protection: float = 0.1
        self.average: int = 1
        self.list_mode: bool = False

        self.sweep: ListSweep = None

        self.current_ranges = {
            "Auto": "Auto",
            "5uA": SmuCurrentRange._5uA,
            "20uA": SmuCurrentRange._20uA,
            "200uA": SmuCurrentRange._200uA,
            "2mA": SmuCurrentRange._2mA,
            "70mA": SmuCurrentRange._70mA,
        }
        self.current_range: SmuCurrentRange = SmuCurrentRange._70mA

        # Output ranges
        self.v_min: float = -11
        self.v_max: float = 11
        self.i_min: float = -0.075
        self.i_max: float = 0.075

        # List Mode Parameters
        self.list_start: float = 0.0
        self.list_end: float = 1.0
        self.number_of_points: int = 10
        self.list_delay_time: int = 100  # in ms

        # Measured values
        self.v: float = 0
        self.i: float = 0
        self.t: float = 0

    @staticmethod
    def find_ports() -> list:
        """Return a list of connected devices."""
        srunner = IdSmuServiceRunner()
        service = srunner.get_idsmu_service()

        # Get first board to automatically detect connected devices
        board = service.get_first_board()
        ports = board.get_all_hardware_ids()

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
            "Average": 1,
            "CheckPulse": False,
            # List Mode Parameters
            "ListSweepCheck": False,
            "ListSweepType": ["Sweep"],
            "ListSweepStart": 0.0,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": ["Step width:", "Points (lin.):"],
            "ListSweepStepPointsValue": 0.1,
            "ListSweepDelaytime": 0.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle the GUI parameters."""
        self.source = parameter["SweepMode"]
        self.protection = float(parameter["Compliance"])
        self.board_id = parameter["Port"]
        self.identifier: str = "idSMUx_" + self.board_id

        self.channel_number = int(parameter["Channel"])
        self.current_range = self.current_ranges[parameter["Range"]]

        self.average = int(parameter["Average"])

        # List Mode Parameters
        try:
            sweep_value = parameter["SweepValue"]
        except KeyError:
            # this might be the case when driver is used with pysweepme
            # then, "SweepValue" is not defined during set_GUIparameter
            sweep_value = None

        if sweep_value == "List sweep":
            self.list_mode = True
            self.handle_list_sweep_parameter(parameter)

    def handle_list_sweep_parameter(self, parameter: dict) -> None:
        """Read out the list sweep parameters and create self.list_sweep_values."""
        self.list_start = float(parameter["ListSweepStart"])
        self.list_end = float(parameter["ListSweepEnd"])

        step_points_type = parameter["ListSweepStepPointsType"]
        if step_points_type.startswith("Step width"):
            self.number_of_points = int((self.list_end - self.list_start) / float(parameter["ListSweepStepPointsValue"]))
        else:
            self.number_of_points = int(parameter["ListSweepStepPointsValue"])

        if self.number_of_points > 52:
            msg = f"Number of points {self.number_of_points} is too high. Maximum is 52."
            raise ValueError(msg)

        self.list_delay_time = int(float(parameter["ListSweepDelaytime"]) * 1000)

        # Add time staps to return values
        self.variables.append("Time stamp")
        self.units.append("s")
        self.plottype.append(True)
        self.savetype.append(True)

    def connect(self) -> None:
        """Connect to the SMU."""
        self.srunner = IdSmuServiceRunner()

    def disconnect(self) -> None:
        """Terminate the connection to the SMU."""
        self.srunner.shutdown()
        if self.identifier in self.device_communication:
            del self.device_communication[self.identifier]

    def initialize(self) -> None:
        """Initialize the boards or receive initialized boards from other driver."""
        if self.identifier in self.device_communication:
            board_model = self.device_communication[self.identifier]
        else:
            service = self.srunner.get_idsmu_service()
            board_model = service.get_first_board()
            self.device_communication[self.identifier] = board_model

        self.smu = board_model.idSmu2Modules[self.board_id]
        self.channel = self.smu.smu.channels[self.channel_number]

    def configure(self) -> None:
        """Enable the channel and set the current range on the SMU."""
        if not self.channel.enabled:
            self.channel.enabled = True

        self.set_compliance(self.protection)

        # Current Range
        if self.current_range == "Auto":
            self.channel.autorange = True
        else:
            self.channel.autorange = False
            self.channel.current_range = self.current_range

        # Get output ranges
        self.v_min, self.v_max, self.i_min, self.i_max = self.channel.output_ranges

    def set_compliance(self, value: float) -> None:
        """Set the compliance on the SMU.

        The device automatically switches to voltage compliance when current is forced and vice versa.
        """
        value = abs(value)
        self.channel.clamp_high_value = value
        self.channel.clamp_low_value = -value
        self.channel.clamp_enabled = True

    def apply(self) -> None:
        """Set the voltage or current on the SMU."""
        if self.source == "Voltage in V":
            if self.value > self.v_max or self.value < self.v_min:
                msg = f"Voltage {self.value} V out of range {self.v_min} V to {self.v_max} V"
                raise ValueError(msg)
            self.channel.voltage = float(self.value)

        elif self.source == "Current in A":
            if self.value > self.i_max or self.value < self.i_min:
                msg = f"Current {self.value} A out of range {self.i_min} A to {self.i_max} A"
                raise ValueError(msg)
            self.channel.current = float(self.value)

    def measure(self) -> None:
        """Read the voltage and current from the SMU."""
        if self.list_mode:
            self.run_list_sweep()
            return

        self.i = self.channel.current
        self.v = self.channel.voltage

        if self.average > 1:
            for _ in range(self.average - 1):
                # TODO: Check if the value gets updated
                self.i += self.channel.current
                self.v += self.channel.voltage

            self.i = self.i / self.average
            self.v = self.v / self.average

    def run_list_sweep(self) -> None:
        """Run the list sweep."""
        # TODO: What about current list mode?
        mbx1 = self.srunner.get_idsmu_service().get_first_board()
        # mbx1.set_measurement_mode(MeasurementMode.isense, [channel])
        # self.channel.set
        print(self.list_start, self.list_end, self.number_of_points)
        self.config = ListSweepChannelConfiguration()
        self.config.set_linear_sweep(self.list_start, self.list_end, self.number_of_points)
        self.sweep = ListSweep(self.smu.name, mbx1)

        # TODO: Can i add multiple channels for readout?
        self.sweep.add_channel_configuration(self.channel.name, self.config)
        self.sweep.set_measurement_delay(self.list_delay_time)
        self.sweep.run()

        self.v = self.sweep.get_measurement_result(self.channel.name)
        self.i = self.config.force_values
        self.t = self.sweep.timecode

    def call(self) -> list:
        """Return the voltage and current."""
        if self.list_mode:
            return [self.v, self.i, self.t]

        return [self.v, self.i]
