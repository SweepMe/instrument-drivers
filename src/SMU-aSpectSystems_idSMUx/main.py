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

import time
import numpy as np
from pysweepme import FolderManager as FoMa
from pysweepme.EmptyDeviceClass import EmptyDevice

FoMa.addFolderToPATH()

from aspectdeviceengine.enginecore import (
    IdSmuServiceRunner,
    ListSweep,
    ListSweepChannelConfiguration,
    MeasurementMode,
    SmuCurrentRange,
    CurrentRange,
)


class SourceMode(enum.Enum):
    """Enum class to define the type of action."""

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
        self.board_model: aspectdeviceengine.enginecore.IdSmuBoardModel = None
        self.smu: aspectdeviceengine.enginecore.IdSmu2DeviceModel = None
        self.channel: aspectdeviceengine.enginecore.AD5522ChannelModel = None

        # Measurement Parameters
        self.channels: list = [1, 2, 3, 4]
        self.channel_number: int = 1
        self.source_identifier: str = "Voltage in V"
        self.source: SourceMode = SourceMode.VOLTAGE
        self.protection: float = 0.1
        self.average: int = 1
        self.list_mode: bool = False

        self.sweep: ListSweep = None

        self.current_ranges = {
            "Auto": "Auto",
            "5 µA - idSMU2": CurrentRange.Range_5uA,
            "20 µA - idSMU2": CurrentRange.Range_20uA_SMU,
            "200 µA - idSMU2": CurrentRange.Range_200uA_SMU,
            "2 mA - id SMU2": CurrentRange.Range_2mA_SMU,
            "70 mA - idSMU2": CurrentRange.Range_70mA_SMU,
            "5 µA - DPS": CurrentRange.Range_5uA,
            "25 µA - DPS":  CurrentRange.Range_25uA_DPS,
            "250 µA - DPS": CurrentRange.Range_250uA_DPS,
            "2,5 mA - DPS": CurrentRange.Range_2500uA_DPS,
            "25 mA - DPS": CurrentRange.Range_25mA_DPS,
            "500 mA - DPS": CurrentRange.Range_500mA_DPS,
            "1200 mA - DPS": CurrentRange.Range_1200mA_DPS,
        }

        self.current_range: CurrentRange = CurrentRange.Range_70mA_SMU

        # Only 2**n values are allowed
        self.speed_options = {
            "Very fast": 2**0,  # 1
            "Fast": 2**2,  # 4
            "Medium": 2**4,  # 16
            "Slow": 2**6,  # 64
            "Very slow": 2**8,  # 256
        }

        # Output ranges
        self.v_min: float = -11
        self.v_max: float = 11
        self.i_min: float = -0.075
        self.i_max: float = 0.075

        # List Mode Parameters
        self.list_sweep_values: list[float] = []
        self.list_delay_time: int = 100  # in ms

        self.list_role: str = "None"
        """The role of the channel in the list sweep. Possible values:
            'List master' : The first channel that registers as list mode. It sets up the list sweep and runs the
            measurement.
            'List creator': If another channel also runs a list sweep, this channel creates its own list sweep
            configuration which is run in parallel.
            'List receiver': If the channel applies only single values but another channel runs list mode, this channel
            is read out in parallel by the list master.
            'None': No channel is using list mode.
        """

        # Measured values
        self.v: float = 0
        self.i: float = 0
        self.t: float = 0

    @staticmethod
    def find_ports() -> list:
        """Return a list of connected devices."""
        srunner = IdSmuServiceRunner()
        service = srunner.get_idsmu_service()

        service.detect_devices()

        board_addresses = service.get_board_addresses()

        ports = []
        for board_address in board_addresses:
            board = service.get_board(board_address)
            all_ids = board.get_all_hardware_ids()
            ports += [x for x in all_ids if "C" in x]

        # Always shut down the service runner
        srunner.shutdown()

        # returns list with strings like ["M1.S1.C1", M1.S1.C2", ... ]
        return ports

    def set_GUIparameter(self) -> dict:  # noqa: N802
        """Set the standard GUI parameters."""
        return {
            "SweepMode": ["Voltage in V", "Current in A"],
            # "Channel": self.channels,
            "RouteOut": ["Front"],
            "Compliance": 0.07,
            "Range": list(self.current_ranges),
            "Speed": list(self.speed_options),
            "CheckPulse": False,
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
        self.source_identifier = parameter["SweepMode"]

        self.protection = float(parameter["Compliance"])
        self.channel_name = parameter["Port"]
        self.board_id = self.channel_name[:-3]
        self.identifier: str = "idSMUx_" + self.board_id

        self.channel_number = int(self.channel_name[-1])

        self.current_range = self.current_ranges[parameter["Range"]]
        self.speed = parameter["Speed"]

        # List Mode Parameters
        try:
            sweep_value = parameter["SweepValue"]
        except KeyError:
            # this might be the case when driver is used with pysweepme
            # then, "SweepValue" is not defined during set_GUIparameter
            sweep_value = None

        if sweep_value == "List sweep":
            self.list_role = "List master"
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
                self.list_sweep_values = np.append(list_sweep_values, end)

            elif step_points_type.startswith("Points (lin.)"):
                self.list_sweep_values = np.linspace(start, end, int(step_points_value))

            elif step_points_type.startswith("Points (log.)"):
                self.list_sweep_values = np.logspace(np.log10(start), np.log10(end), int(step_points_value))

            else:
                msg = f"Unknown step points type: {step_points_type}"
                raise ValueError(msg)

        elif list_sweep_type == "Custom":
            custom_values = parameter["ListSweepCustomValues"]
            self.list_sweep_values = np.array([float(value) for value in custom_values.split(",")])

        else:
            msg = f"Unknown list sweep type: {list_sweep_type}"
            raise ValueError(msg)

        # Add the returning values in reverse order to the list
        if parameter["ListSweepDual"]:
            self.list_sweep_values = np.append(self.list_sweep_values, self.list_sweep_values[::-1])

        if len(self.list_sweep_values) > 52:
            msg = f"Number of points {len(self.list_sweep_values)} is too high. Maximum is 52."
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
            - "List creators": dict[str, ListSweepChannelConfiguration], Dictionary with channel name as key and
            ListSweepChannelConfiguration as value.
            - "List length": int, Number of points in the list sweep.
            - "List results": dict[str, list[float], Dictionary with channel name as key and list of measured values as
            value.
        """
        self.source = SourceMode.VOLTAGE if self.source_identifier.startswith("Voltage") else SourceMode.CURRENT

        if self.identifier in self.device_communication:
            self.board_model = self.device_communication[self.identifier]["Board"]
        else:
            service = self.srunner.get_idsmu_service()
            self.board_model = service.get_first_board()
            self.device_communication[self.identifier] = {}
            self.device_communication[self.identifier]["Board"] = self.board_model

        self.smu = self.board_model.idSmu2Modules[self.board_id]

        firmware_version = self.smu.get_firmware_version()
        hardware_id = self.smu.get_hardware_id()

        self.channel = self.smu.smu.channels[self.channel_number]
        self.channel.name = self.channel_name

        # If this channel should run the list sweep, register it as 'List master'
        # Checking if the list receiver should be used will be done in 'configure' after all channels are initialized
        if self.list_role == "List master":
            if "List master" in self.device_communication[self.identifier]:
                # If another channel already runs a list sweep, this channel creates it own list config and passes it
                # Update the role to 'List creator'
                self.list_role = "List creator"

            else:
                self.device_communication[self.identifier].update(
                    {
                        "List master": self.channel_name,
                        "List receivers": [],
                        "List creators": {},
                        "List length": len(self.list_sweep_values),
                        "List results": {},
                    },
                )

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
            self.board_model.set_current_ranges(self.current_range, [self.channel.name])
            # self.channel.current_range = self.current_range

        # Speed/integration
        self.channel.sample_count = self.speed_options[self.speed]

        # Get output ranges
        self.v_min, self.v_max, self.i_min, self.i_max = self.channel.output_ranges

        # If another channel runs a list sweep, this channel must be a list receiver
        if "List master" in self.device_communication[self.identifier]:
            # Set the measurement mode - also for the list master itself
            # Maybe this can be done simpler, but it works
            measurement_mode = MeasurementMode.isense if self.source == SourceMode.VOLTAGE else MeasurementMode.vsense
            self.board_model.set_measurement_modes(measurement_mode, [self.channel_name])

            if self.list_role == "List creator":
                # Check if the number of list points matches the list master
                list_length = self.device_communication[self.identifier]["List length"]
                if list_length != len(self.list_sweep_values):
                    msg = (
                        f"Number of list sweep points {list_length} does not match the number of points of the list "
                        f"master: {len(self.list_sweep_values)}. Use the same number of points when combining list "
                        f"mode for multiple channels!"
                    )
                    raise ValueError(msg)

                # If another channel runs a list sweep, this channel must provide a list sweep configuration
                config = ListSweepChannelConfiguration()
                config.set_force_values(self.list_sweep_values)
                self.device_communication[self.identifier]["List creators"][self.channel_name] = config

            elif self.list_role not in ("List master", "List creator"):
                self.list_role = "List receiver"
                self.device_communication[self.identifier]["List receivers"].append(self.channel_name)

        # handling to read multiple channels in spotwise measurements
        self.identifier_channel_names = "Active channel names"
        if self.identifier_channel_names not in self.device_communication[self.identifier]:
            self.device_communication[self.identifier][self.identifier_channel_names] = []

        if len(self.device_communication[self.identifier][self.identifier_channel_names]) == 0:
            self._is_retrieving_data = True
        else:
            self._is_retrieving_data = False

        # adding channel name as the SMU gets active
        self.device_communication[self.identifier][self.identifier_channel_names].append(self.channel.name)

    def unconfigure(self):

        # removing channel name if the SMU is no longer active
        self.device_communication[self.identifier][self.identifier_channel_names].remove(self.channel.name)

    def apply(self) -> None:
        """Set the voltage or current on the SMU."""
        if self.source == SourceMode.VOLTAGE:
            if self.value > self.v_max or self.value < self.v_min:
                msg = f"Voltage {self.value} V out of range {self.v_min} V to {self.v_max} V"
                raise ValueError(msg)
            self.channel.voltage = float(self.value)

        else:
            if self.value > self.i_max or self.value < self.i_min:
                msg = f"Current {self.value} A out of range {self.i_min} A to {self.i_max} A"
                raise ValueError(msg)
            self.channel.current = float(self.value)

    def measure(self) -> None:
        """Read the voltage and current from the SMU."""
        if self.list_role == "List master":
            self.run_list_sweep()
            return

        if self.list_role in ("List receiver", "List creator"):
            # as list receiver or creator, the measurement is started by the list master
            return

        if self._is_retrieving_data:
            active_channel_names = self.device_communication[self.identifier][self.identifier_channel_names]

            channel_numbers = [int(x[-1]) for x in active_channel_names]


            self.board_model.set_measurement_modes(MeasurementMode.vsense, active_channel_names)
            self.future_v = self.smu.measure_channels_async(sample_count=self.speed_options[self.speed],
                                            repetitions=1,
                                            channel_numbers=channel_numbers,
                                            wait_for_trigger=False,
                                            )

            self.board_model.set_measurement_modes(MeasurementMode.isense, active_channel_names)
            self.future_i = self.smu.measure_channels_async(sample_count=self.speed_options[self.speed],
                                            repetitions=1,
                                            channel_numbers=channel_numbers,
                                            wait_for_trigger=False,
                                            )
    def read_result(self):

        if self.list_role in ("List master", "List receiver", "List creator"):
            return

        if self._is_retrieving_data:
            result_v = self.future_v.get()
            result_i = self.future_i.get()
            self.v = result_v.get_float_values(self.channel_name)[0]
            self.i = result_i.get_float_values(self.channel_name)[0]
            self.device_communication[self.identifier]["data"] = [result_v, result_i]
        else:
            self.v = self.device_communication[self.identifier]["data"][0].get_float_values(self.channel_name)[0]
            self.i = self.device_communication[self.identifier]["data"][1].get_float_values(self.channel_name)[0]

    def run_list_sweep(self) -> None:
        """Run the list sweep."""
        # Get all channels that should be measured
        list_receivers = self.device_communication[self.identifier]["List receivers"]
        list_creators = self.device_communication[self.identifier]["List creators"]

        # Create list config for master channel
        config = ListSweepChannelConfiguration()
        config.set_force_values(self.list_sweep_values)
        self.sweep = ListSweep(self.smu.name, self.board_model)
        self.sweep.add_channel_configuration(self.channel.name, config)

        # Create only-read list config for all receiver channels
        for receiver in list_receivers:
            receiver_config = ListSweepChannelConfiguration()
            receiver_config.set_constant_force_mode(len(self.list_sweep_values))
            self.sweep.add_channel_configuration(receiver, receiver_config)

        # List creators provide their own config
        for creator, creator_config in list_creators.items():
            self.sweep.add_channel_configuration(creator, creator_config)

        self.sweep.set_measurement_delay(self.list_delay_time)
        self.sweep.run()

        try:
            measurement_result = self.sweep.get_measurement_result(self.channel.name)
        except IndexError as e:
            if str(e) == "invalid map<K, T> key":
                msg = "Error in list readout. Try reducing the number of points if you are using multiple channels."
                raise ValueError(msg) from e
            raise e

        if self.source == SourceMode.VOLTAGE:
            self.v = config.force_values
            self.i = measurement_result
        else:
            self.v = measurement_result
            self.i = config.force_values

        # Store the results of the other channels in device_communication
        for channel in [*list_receivers, *list_creators.keys()]:
            measurement_results = self.sweep.get_measurement_result(channel)
            self.device_communication[self.identifier]["List results"][channel] = measurement_results

        self.device_communication[self.identifier]["Time stamp"] = self.sweep.timecode
        self.t = self.sweep.timecode * 1e-6

    def call(self) -> list:
        """Return the voltage and current."""
        if self.list_role == "List master":
            return [self.v, self.i, self.t]

        if self.list_role != "None":
            # As list receiver/creator, the measurement data is read out by the List master
            results = self.device_communication[self.identifier]["List results"][self.channel_name]
            time_stamp = self.device_communication[self.identifier]["Time stamp"]

            # Currently, the list mode reads only one parameter, so the source value is used for the other parameter
            if self.list_role == "List creator":
                set_values = self.list_sweep_values
            else:
                set_values = [float(self.value)] * len(results)

            if self.source == SourceMode.VOLTAGE:
                self.i = results
                self.v = set_values
            else:
                self.v = results
                self.i = set_values

            # Channels that use do not use list mode learn too late that they are list receivers and could return a time
            # stamp.  Hence, the sweep time stamp from list master is returned only for list creators.
            if self.list_role == "List creator":
                return [self.v, self.i, time_stamp]

        return [self.v, self.i]

    """further convenience functions """

    def set_compliance(self, value: float) -> None:
        """Set the compliance on the SMU.

        The device automatically switches to voltage compliance when current is forced and vice versa.
        """
        value = abs(value)
        self.channel.clamp_high_value = value
        self.channel.clamp_low_value = -value
        self.channel.clamp_enabled = True