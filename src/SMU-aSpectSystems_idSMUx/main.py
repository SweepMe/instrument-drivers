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
        self.identifier: str = "idSMUx_"  # TODO: Maybe add the serial number here
        self.srunner: IdSmuServiceRunner = None
        # self.smu: aspectdeviceengine.enginecore.IdSmu2Module = None
        # self.channel: aspectdeviceengine.enginecore.AD5522ChannelModel = None

        # Measurement Parameters
        self.channels: list = [1, 2, 3, 4]
        self.channel_number: int = 1
        self.source: str = "Voltage in V"
        self.protection: float = 0.1
        self.average: int = 1

        self.current_ranges = {
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

        # Measured values
        self.v: float = 0
        self.i: float = 0

    @staticmethod
    def find_ports() -> list:
        """Return a list of connected devices."""
        srunner = IdSmuServiceRunner()
        service = srunner.get_idsmu_service()

        # Get first board to automatically detect connected devices
        board_model = service.get_first_board()
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
            "Average": 1,
            "CheckPulse": False,
            # "RangeVoltage": [1],

            # List Mode Parameters
            "ListSweepCheck": False,
            "ListSweepType": ["Sweep", "Custom"],
            "ListSweepStart": 0.0,
            "ListSweepEnd": 1.0,
            "ListSweepStepPointsType": ["Step width:", "Points (lin.):", "Points (log.):"],
            "ListSweepStepPointsValue": 0.1,
            "ListSweepDual": False,
            "ListSweepDelaytime": 0.0,
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Handle the GUI parameters."""
        self.source = parameter["SweepMode"]
        self.protection = parameter["Compliance"]

        # channel_ids = ["M1.S1.C1", "M1.S1.C2", "M1.S1.C3", "M1.S1.C4"]
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
            # self.list_master = True
            # self.list_receiver = False
            self.handle_list_sweep_parameter(parameter)

    def handle_list_sweep_parameter(self, parameter: dict) -> None:
        """Read out the list sweep parameters and create self.list_sweep_values."""
        list_sweep_type = parameter["ListSweepType"]

        if list_sweep_type == "Sweep":
            # Create the list sweep values
            start = float(parameter["ListSweepStart"])
            end = float(parameter["ListSweepEnd"])

            step_points_type = parameter["ListSweepStepPointsType"]
            step_points_value = float(parameter["ListSweepStepPointsValue"])

            if step_points_type.startswith("Step width"):
                list_sweep_values = np.arange(start, end, step_points_value)
                # include end value
                list_sweep_values = np.append(list_sweep_values, end)

            elif step_points_type.startswith("Points (lin.)"):
                list_sweep_values = np.linspace(start, end, int(step_points_value))

            elif step_points_type.startswith("Points (log.)"):
                list_sweep_values = np.logspace(np.log10(start), np.log10(end), int(step_points_value))

            else:
                msg = f"Unknown step points type: {step_points_type}"
                raise ValueError(msg)

        elif list_sweep_type == "Custom":
            custom_values = parameter["ListSweepCustomValues"]
            list_sweep_values = np.array([float(value) for value in custom_values.split(",")])

        else:
            msg = f"Unknown list sweep type: {list_sweep_type}"
            raise ValueError(msg)

        # Add the returning values in reverse order to the list
        if parameter["ListSweepDual"]:
            list_sweep_values = np.append(list_sweep_values, list_sweep_values[::-1])

        self.list_delay_time = float(parameter["ListSweepDelaytime"])
        self.list_sweep_values = list_sweep_values.tolist()

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

    def initialize(self) -> None:
        """Initialize the boards or receive initialized boards from other driver."""
        if self.identifier in self.device_communication:
            board_model = self.device_communication[self.identifier]
        else:
            service = self.srunner.get_idsmu_service()
            board_model = service.get_first_board()
            self.device_communication[self.identifier] = board_model

        self.smu = board_model.idSmu2Modules["M1.S1"]
        self.channel = self.smu.smu.channels[self.channel_number]

    def configure(self) -> None:
        """Enable the channel and set the current range on the SMU."""
        if not self.channel.enabled:
            self.channel.enabled = True

        self.channel.current_range = self.current_range

        # Get output ranges
        self.v_min, self.v_max, self.i_min, self.i_max = self.channel.output_ranges

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
        self.i = self.channel.current
        self.v = self.channel.voltage

        if self.average > 1:
            for _ in range(self.average - 1):
                self.i += self.channel.current
                self.v += self.channel.voltage

            self.i = self.i / self.average
            self.v = self.v / self.average

    def call(self) -> list:
        """Return the voltage and current."""
        return [self.v, self.i]
