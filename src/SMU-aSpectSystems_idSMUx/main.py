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
# * Module: SMU
# * Instrument: aSpectSystems idSMU modules

import enum
from pysweepme import FolderManager as FoMa
from pysweepme.EmptyDeviceClass import EmptyDevice

FoMa.addFolderToPATH()

from aspectdeviceengine.enginecore import (
    IdSmuServiceRunner,
    MeasurementMode,
    ListSweep,
    ListSweepChannelConfiguration,
    SmuCurrentRange,
)


class SourceMode(enum.Enum):
    """Enum class to define the different source modes of the SMU."""
    VOLTAGE = enum.auto()
    CURRENT = enum.auto()


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
        self.channel_name: str = f"{self.board_id}_CH1"
        """The channel can be given a custom name, which is used to set the mode and readout data in list mode."""

        self.srunner: IdSmuServiceRunner = None
        self.smu: aspectdeviceengine.enginecore.IdSmu2DeviceModel = None
        self.channel: aspectdeviceengine.enginecore.AD5522ChannelModel = None

        # Measurement Parameters
        self.channels: list = [1, 2, 3, 4]
        self.channel_number: int = 1
        self.source: SourceMode = SourceMode.VOLTAGE
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

        self.list_master: bool = False
        """Only one channel can run the list sweep and is the master."""

        self.list_receiver: bool = False
        """If another channel runs a list sweep, the measurement must be done as list receiver."""

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
        if parameter["SweepMode"].startswith("Voltage"):
            self.source = SourceMode.VOLTAGE
        elif parameter["SweepMode"].startswith("Current"):
            self.source = SourceMode.CURRENT
        else:
            msg = f"Unknown source mode {parameter['SweepMode']}. Use 'Voltage in V' or 'Current in A'."
            raise ValueError(msg)

        self.protection = float(parameter["Compliance"])
        self.board_id = parameter["Port"]
        self.identifier: str = "idSMUx_" + self.board_id

        self.channel_number = int(parameter["Channel"])
        self.channel_name = f"{self.board_id}_CH{self.channel_number}"
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
            self.list_master = True
            self.list_receiver = False
            self.handle_list_sweep_parameter(parameter)

    def handle_list_sweep_parameter(self, parameter: dict) -> None:
        """Read out the list sweep parameters and create self.list_sweep_values."""
        self.list_start = float(parameter["ListSweepStart"])
        self.list_end = float(parameter["ListSweepEnd"])

        step_points_type = parameter["ListSweepStepPointsType"]
        if step_points_type.startswith("Step width"):
            self.number_of_points = int(
                (self.list_end - self.list_start) / float(parameter["ListSweepStepPointsValue"]),
            )
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
        """Initialize the boards or receive initialized boards from other driver.

        The device_communication dictionary contains the following elements:
            - "Board": aspectdeviceengine.enginecore.IdSmuBoardModel, The board object from service.get_first_board().
            - "List master": str, The name of channel that runs the list sweep.
            - "List receivers": list[str], List of names of all other channels should be measured in parallel.
            - "List length": int, Number of points in the list sweep.
            - "List results": dict[str, list[float], Dictionary with channel name as key and list of measured values as value.
        """
        if self.identifier in self.device_communication:
            board_model = self.device_communication[self.identifier]["Board"]
        else:
            service = self.srunner.get_idsmu_service()
            board_model = service.get_first_board()
            self.device_communication[self.identifier] = {}
            self.device_communication[self.identifier]["Board"] = board_model

        self.smu = board_model.idSmu2Modules[self.board_id]
        self.channel = self.smu.smu.channels[self.channel_number]
        self.channel.name = self.channel_name

        # If this channel should run the list sweep, register it as 'List master'
        # Checking if the list receiver should be used will be done in 'configure' after all channels are initialized
        if self.list_master:
            if "List master" in self.device_communication[self.identifier]:
                msg = "Detected multiple channels with list modes. Please use only one channel for list mode."
                raise Exception(msg)

            self.device_communication[self.identifier].update({
                "List master": self.channel_name,
                "List receivers": [],
                "List results": {},
            })

            # TODO: Needed?
            # self.device_communication[self.identifier]["List length"] = len(self.list_sweep_values)

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

        # If another channel runs a list sweep, this channel must be a list receiver
        # TODO: Measurement data will also be stored in device_communication
        if "List master" in self.device_communication[self.identifier] and not self.list_master:
            self.list_receiver = True
            self.device_communication[self.identifier]["List receivers"].append(self.channel_name)

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
        if self.source == SourceMode.VOLTAGE:
            if self.value > self.v_max or self.value < self.v_min:
                msg = f"Voltage {self.value} V out of range {self.v_min} V to {self.v_max} V"
                raise ValueError(msg)
            self.channel.voltage = float(self.value)

        elif self.source == SourceMode.CURRENT:
            if self.value > self.i_max or self.value < self.i_min:
                msg = f"Current {self.value} A out of range {self.i_min} A to {self.i_max} A"
                raise ValueError(msg)
            self.channel.current = float(self.value)

        # if self.list_receiver:
        #     # If another channel runs a list sweep, this channel must provide a list sweep configuration
        #     config = ListSweepChannelConfiguration()
        #     number_of_points = self.device_communication[self.identifier]["List length"]
        #     config.set_constant_force_mode(number_of_points)

    def measure(self) -> None:
        """Read the voltage and current from the SMU."""
        if self.list_master:
            self.run_list_sweep()
            return

        if self.list_receiver:
            # as list receiver, the measurement is started by the list master
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
        mbx1 = self.srunner.get_idsmu_service().get_first_board()

        # Get all channels that should be measured
        list_receivers = self.device_communication[self.identifier]["List receivers"]
        channel_list = [self.channel_name, *list_receivers]

        measurement_mode = MeasurementMode.isense if self.source == SourceMode.VOLTAGE else MeasurementMode.vsense
        mbx1.set_measurement_modes(measurement_mode, channel_list)

        # ListMode must be set by ListMaster channel
        config = ListSweepChannelConfiguration()
        config.set_linear_sweep(self.list_start, self.list_end, self.number_of_points)
        self.sweep = ListSweep(self.smu.name, mbx1)
        self.sweep.add_channel_configuration(self.channel.name, config)

        for receiver in list_receivers:
            receiver_config = ListSweepChannelConfiguration()
            receiver_config.set_constant_force_mode(self.number_of_points + 1)  # +1 as first and last value are counted
            self.sweep.add_channel_configuration(receiver, receiver_config)

        self.sweep.set_measurement_delay(self.list_delay_time)
        self.sweep.run()

        try:
            measurement_result = self.sweep.get_measurement_result(self.channel.name)
        except IndexError as e:
            if str(e) == "invalid map<K, T> key":
                msg = "Error in list readout. Try reducing the number of points if you are using multiple channels."
                raise ValueError(msg) from e
            else:
                raise e

        if self.source == SourceMode.VOLTAGE:
            self.v = self.config.force_values
            self.i = measurement_result
        else:
            self.v = measurement_result
            self.i = self.config.force_values

        # Store the results of the other channels in device_communication
        for receiver in list_receivers:
            measurement_results = self.sweep.get_measurement_result(receiver)
            self.device_communication[self.identifier]["List results"][receiver] = measurement_results

        self.t = self.sweep.timecode

    def call(self) -> list:
        """Return the voltage and current."""
        if self.list_master:
            return [self.v, self.i, self.t]

        if self.list_receiver:
            if self.source == SourceMode.VOLTAGE:
                self.i = self.device_communication[self.identifier]["List results"][self.channel_name]
                self.v = [float(self.value)] * len(self.i)
            else:
                self.v = self.device_communication[self.identifier]["List results"][self.channel_name]
                self.i = [float(self.value)] * len(self.i)

        return [self.v, self.i]
