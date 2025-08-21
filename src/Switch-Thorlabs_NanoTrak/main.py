# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025 SweepMe! GmbH (sweep-me.net)
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
# * Module: Switch
# * Instrument: Thorlabs NanoTrak

from __future__ import annotations

import contextlib

import sys
import time
from typing import Any

import clr
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import error

# Import Kinesis dll
kinesis_imported = False

bitness = 64 if sys.maxsize > 2**32 else 32
kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis" # if bitness == 64 else "C:\\Program Files (x86)\\Thorlabs\\Kinesis"
try:
    if kinesis_path not in sys.path:
        sys.path.insert(0, kinesis_path)

    clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
    clr.AddReference("Thorlabs.MotionControl.GenericNanoTrakCLI")

    from Thorlabs.MotionControl import DeviceManagerCLI, GenericNanoTrakCLI
except:
    pass
else:
    kinesis_imported = True


class Device(EmptyDevice):
    """Device class to implement functionalities of Thorlabs NanoTrak via Kinesis."""
    description = """
                    <h3>Thorlabs NanoTrak</h3>
                    This drivers implements the functionalities of the Thorlabs NanoTrak devices via Kinesis. NanoTrak
                    comes in three different versions: Benchtop, TCube, and KCube. The driver detects the device type
                    automatically based on the serial number prefix.
                    The driver detects the optimum position during 'configure', and does not require a set value.

                    <p>Setup:</p>
                    <ul>
                    <li>Install Kinesis</li>
                    <li>Kinesis must be closed when running this driver.</li>
                    </ul>

                    <p>Parameters:</p>
                    <ul>
                    <li>Reading: Return the reading as absolute, relative, or not.</li>
                    <li>When using center position, the value must be a string with two values separated by a semicolon,
                     e.g. "5;2" for horizontal and vertical position.</li>
                    <li>When using circle diameter, the value must be a float representing the diameter in NT Units.</li>
                    </ul>
                    """

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Nanotrak"  # short name will be shown in the sequencer

        # Define the variables that can be measured by the device and that are returned by the 'call' function
        self.variables = ["Horizontal Position", "Vertical Position"]
        self.units = ["m", "m"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        # Imported Kinesis .NET dlls
        self.kinesis_client = None
        """The device specific NanoTrak CLI module, e.g. BenchtopNanoTrakCLI, TCubeNanoTrakCLI, or KCubeNanoTrakCLI."""

        # Communication parameters
        self.serial_number: str = ""  # Serial number of the device
        self.nanotrak = None
        self.rack = None  # When using a rack, the rack element contains the self.nanotrak element
        self.is_simulation = False

        self.device_prefixes = {
            "benchtop": 22,  # BenchtopNanoTrakCLI.BenchtopNanoTrak.DevicePrefix
            "tcube": 82,  # TCubeNanoTrakCLI.TCubeNanoTrak.DevicePrefix
            "kcube": 57,  # KCubeNanoTrakCLI.KCubeNanoTrak.DevicePrefix
            "modular_rack": 52,  # Not been tested, but could be NanoTrack in a Modular Rack
        }
        """These prefixes can be loaded from the corresponding CLI modules, e.g.:
            clr.AddReference("Thorlabs.MotionControl.Benchtop.NanoTrakCLI")
            import Thorlabs.MotionControl.Benchtop.NanoTrakCLI as BenchtopNanoTrakCLI
            benchtop_prefix = BenchtopNanoTrakCLI.BenchtopNanoTrak.DevicePrefix
        For ease of use they are hardcoded in this function.
        """
        self.nanotrak_type: str = "Unknown"  # Will be set in the connect() function
        self.is_modular_rack: bool = False  # True if the device is a modular rack device
        self.bay: int = 1  # Bay number for modular rack devices, default is 1

        # Feedback sources
        nano_trak_feedback_source = GenericNanoTrakCLI.Settings.IOSettingsSettings.FeedbackSources
        self.feedback_sources = {
            "BNC 10V ": nano_trak_feedback_source.BNC_10V,
            "BNC 5V": nano_trak_feedback_source.BNC_5V,
            "BNC 2V": nano_trak_feedback_source.BNC_2V,
            "BNC 1V": nano_trak_feedback_source.BNC_1V,
            "TIA": nano_trak_feedback_source.TIA,
        }

        # Measurement parameters
        self.sweepmode: str = "Center Position"
        self.tracking_mode: str = "Tracking"  # Can be "Tracking" or "Latch"
        self.reading_mode: str = "Absolute"  # Can be "Absolute", "Relative", or "None"

    def find_ports(self) -> list[str]:
        """Returns the serial numbers of all devices connected via Kinesis."""
        device_list = self.list_devices()
        self.is_simulation = False

        # Searching for simulated devices if there are no real devices found
        if not device_list:
            print("-> No devices found, initializing simulations...")
            self.set_simulation_mode(True)
            device_list = self.list_devices()
            self.is_simulation = True
            self.set_simulation_mode(False)

        if not device_list:
            device_list = ["No devices found!"]

        return device_list

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        new_parameters = {
            "Home position": "1.0,1.0",
            "Circle diameter in NT": "1",
            "Tracking time in s": "10",
            "Feedback Source": list(self.feedback_sources.keys()),
            "Simulation": False,
            "Debug while Tracking": False,
            "Modular Rack": False,
        }

        if parameters.get("Modular Rack", False):
            new_parameters["Bay"] = 1

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Apply the parameters received from the SweepMe GUI or the pysweepme instance to the driver instance."""
        self.serial_number = parameters.get("Port", "")
        self.home_position_string = parameters.get("Home position", "1.0,1.0")
        self.circle_diameter_string = parameters.get("Circle diameter in NT", "1")
        self.feedback_source = parameters.get("Feedback Source", "BNC 10V")
        self.tracking_time_string = parameters.get("Tracking time in s", 10)
        self.debug_while_tracking = parameters.get("Debug while Tracking", False)

        self.is_simulation = parameters.get("Simulation", False)

        self.is_modular_rack = parameters.get("Modular Rack", False)
        if self.is_modular_rack:
            self.bay = parameters.get("Bay", 1)

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if not kinesis_imported:
            msg = ("Kinesis .NET dlls not found! Please install Kinesis to C:\\Program Files\\Thorlabs\\Kinesis, and "
                   "ensure it is closed when running this driver.")
            raise ImportError(msg)

        if self.is_simulation:
            self.set_simulation_mode(True)

        available_devices = self.list_devices()
        if self.serial_number in ["No devices found!", ""]:
            msg = "No device connected! Please connect a Thorlabs NanoTrak device."
            raise ValueError(msg)

        if self.serial_number not in available_devices:
            msg = f"Device with serial number {self.serial_number} not found in the list of available devices: {available_devices}"
            raise ValueError(msg)

        # Determine device type based on the serial number prefix
        self.nanotrak_type = self.determine_nanotrak_type(self.serial_number)
        self.import_device_dlls(self.nanotrak_type)
        self.nanotrak = self.create_nanotrak(self.serial_number, self.nanotrak_type)

        # Connect to device / rack
        connecting_element = self.nanotrak if not self.is_modular_rack else self.rack
        print("Waiting for device to set IsConnected to True...")
        timeout_s = 10
        while not connecting_element.IsConnected:
            try:
                connecting_element.Connect(str(self.serial_number))
            except DeviceManagerCLI.DeviceNotReadyException:
                print("DeviceNotReadyException: Device is not ready yet, retrying...")
                time.sleep(0.2)
                timeout_s -= 0.2

            if timeout_s <= 0:
                msg = f"Failed to connect to the device {self.serial_number} within the timeout period."
                raise TimeoutError(msg)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        if not self.nanotrak:
            print(f"self.nanotrak {self.nanotrak} is not")
            return

        self.nanotrak.StopPolling()
        # self.nanotrak.DisableDevice()
        if self.is_modular_rack:
            self.rack.Disconnect(True)

        if self.is_simulation:
            self.set_simulation_mode(False)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        if not self.nanotrak.IsSettingsInitialized():
            # If the device is already initialized, this would raise an exception.
            with contextlib.suppress(Exception):
                self.nanotrak.WaitForSettingsInitialized(5000)  # ms

        # Start polling
        polling_rate = 250
        self.nanotrak.StartPolling(polling_rate)
        time.sleep(0.5)

        # Enable the device
        self.nanotrak.EnableDevice()
        time.sleep(0.5)

    def configure(self) -> None:
        """Configure the device. This function is called only once at the start of the measurement."""
        # Unsure why, but when using a modular rack, there is a difference between rack.GetNanoTrakChannel and rack[bay].
        if self.is_modular_rack:
            self.nanotrak_channel = self.rack.GetNanoTrakChannel(int(self.bay))
        else:
            self.nanotrak_channel = self.nanotrak

        try:
            tracking_time = float(self.tracking_time_string)
        except ValueError as e:
            msg = f"Invalid tracking time: {self.tracking_time_string}. Expected a float value."
            raise ValueError(msg) from e

        # Configure NanoTrak
        DeviceSettingsUseOptionType = DeviceManagerCLI.DeviceConfiguration.DeviceSettingsUseOptionType
        nanoTrakConfiguration = self.nanotrak_channel.GetNanoTrakConfiguration(self.serial_number, DeviceSettingsUseOptionType.UseConfiguredSettings)
        currentDeviceSettings = self.nanotrak_channel.NanoTrakDeviceSettings
        self.nanotrak_channel.SetSettings(currentDeviceSettings, False)

        self.nanotrak_channel.GetSettings(currentDeviceSettings)
        NanoTrakStatusBase = GenericNanoTrakCLI.NanoTrakStatusBase

        # Set feedback source depending on the GUI parameter
        self.nanotrak_channel.SetFeedbackSource(self.feedback_sources[self.feedback_source])

        # Home Position
        home_pos1, home_pos2 = map(float, self.home_position_string.split(","))
        HVPosition = GenericNanoTrakCLI.HVPosition
        self.nanotrak_channel.SetCircleHomePosition(HVPosition(home_pos1, home_pos2))
        self.nanotrak_channel.HomeCircle()

        # Allow comma separated values for multiple trackings
        diameter_list = self.circle_diameter_string.split(",")
        for diameter in diameter_list:
            # we latch before changing the diameter
            self.nanotrak_channel.SetMode(NanoTrakStatusBase.OperatingModes.Latch)
            self.set_circle_diameter(float(diameter))
            self.track()

            # tracking time
            remaining_tracking_time = tracking_time
            while remaining_tracking_time > 0:
                if self.is_run_stopped():
                    break

                # Check position
                horizontal_position, vertical_position = self.get_current_position()
                self.debug(f"{horizontal_position}, {vertical_position}")

                wait_time = min(remaining_tracking_time, 0.5)
                time.sleep(wait_time)
                remaining_tracking_time -= wait_time

            # Latch after tracking is finished
            self.latch()

            # TODO: Check if position is too close to the edges

        print("NanoTrak finished configuration.")

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        horizontal, vertical = self.get_current_position()
        return [horizontal, vertical]

    # Utility functions

    def list_devices(self, nanotrak_type: str = "") -> list[str]:
        """Lists all devices.

        filter: either empty, 'benchtop', 'kcube' or 'tcube'.

        Bug: Once Simulation mode is switched on, GetDeviceList will also find simulated devices even when simulation
        mode is uninitialized.
        The device list can be filtered by the device prefix, e.g. BenchtopNanoTrakCLI.BenchtopNanoTrak.DevicePrefix
        """
        if not kinesis_imported:
            msg = ("Kinesis .NET dlls not found! Please install Kinesis to C:\\Program Files\\Thorlabs\\Kinesis, and "
                   "ensure it is closed when running this driver.")
            raise ImportError(msg)

        DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()

        if not nanotrak_type:
            device_list = DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
        elif nanotrak_type.lower() in self.device_prefixes:
            prefix = self.device_prefixes[nanotrak_type.lower()]
            device_list = DeviceManagerCLI.DeviceManagerCLI.GetDeviceList(prefix)
        else:
            msg = f"Unknown filter '{nanotrak_type}'. Valid filters are: {', '.join(self.device_prefixes.keys())} or an empty string."
            raise ValueError(msg)

        return [str(serial_num) for serial_num in device_list]

    def determine_nanotrak_type(self, serial_number: str) -> str:
        """Determine the device type based on the serial number prefix."""
        if self.is_modular_rack:
            # TODO: Add prefix
            return "modular_rack"

        for supported_type, prefix in self.device_prefixes.items():
            if serial_number.startswith(str(prefix)):
                return supported_type

        return "Unknown"

    def import_device_dlls(self, nanotrak_type: str) -> None:
        """Import the device specific Kinesis .NET dll based on the device type."""
        if nanotrak_type == "benchtop":
            clr.AddReference("Thorlabs.MotionControl.Benchtop.NanoTrakCLI")
            import Thorlabs.MotionControl.Benchtop.NanoTrakCLI as BenchtopNanoTrakCLI
            self.kinesis_client = BenchtopNanoTrakCLI

        elif nanotrak_type == "tcube":
            clr.AddReference("Thorlabs.MotionControl.TCube.NanoTrakCLI")
            import Thorlabs.MotionControl.TCube.NanoTrakCLI as TCubeNanoTrakCLI
            self.kinesis_client = TCubeNanoTrakCLI

        elif nanotrak_type == "kcube":
            clr.AddReference("Thorlabs.MotionControl.KCube.NanoTrakCLI")
            import Thorlabs.MotionControl.KCube.NanoTrakCLI as KCubeNanoTrakCLI
            self.kinesis_client = KCubeNanoTrakCLI

        elif nanotrak_type == "modular_rack":
            # Modular Rack does not require a specific CLI module, it uses the ModularRackCLI
            clr.AddReference("Thorlabs.MotionControl.ModularRackCLI")
            import Thorlabs.MotionControl.ModularRackCLI as ModularRackCLI
            self.kinesis_client = ModularRackCLI

        else:
            msg = f"Unknown device type: {nanotrak_type}. Supported prefixes (first two numbers) are: {', '.join(self.device_prefixes.values())}."
            raise ValueError(msg)

    def create_nanotrak(self, serial_number: str, nanotrak_type: str) -> GenericNanoTrakCLI.GenericNanoTrak:
        """Create a nanotrak instance based on the serial number and device type."""
        if nanotrak_type == "benchtop":
            self.nanotrak = self.kinesis_client.BenchtopNanoTrak.CreateBenchtopNanoTrak(serial_number)
        elif nanotrak_type == "tcube":
            self.nanotrak = self.kinesis_client.TCubeNanoTrak.CreateTCubeNanoTrak(serial_number)
        elif nanotrak_type == "kcube":
            self.nanotrak = self.kinesis_client.KCubeNanoTrak.CreateKCubeNanoTrak(serial_number)

        elif nanotrak_type == "modular_rack":
            # Create a modular rack instance
            device_factory = DeviceManagerCLI.DeviceFactory
            device_info = device_factory.GetDeviceInfo(serial_number)
            type_id = device_info.GetTypeID()
            modular_rack = self.kinesis_client.Rack.ModularRack
            self.rack = modular_rack.CreateModularRack(type_id, serial_number)

            # Could also be rack[1] or rack[bay]
            self.nanotrak = self.rack[int(self.bay)]
            # self.nanotrak = self.rack.GetNanoTrakChannel(int(self.bay))

        else:
            msg = f"Unknown nanotrak type for serial number {self.serial_number}. Supported prefixes (first two numbers) are: {', '.join(self.device_prefixes.values())}."
            raise ValueError(msg)

        return self.nanotrak

    # Wrapper Functions

    @staticmethod
    def set_simulation_mode(state: bool) -> None:
        """Set the simulation mode for the device."""
        if state:
            DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()

        else:
            DeviceManagerCLI.SimulationManager.Instance.UninitializeSimulations()

    def get_identification(self) -> str:
        """Returns the identification of the device."""
        if not self.nanotrak:
            error("NanoTrak not connected!")
            return ""

        return self.nanotrak.GetDeviceInfo().SerialNumber

    def get_current_position(self) -> tuple[float, float]:
        """Get the current circular position and signal strength at the current position."""
        if not self.nanotrak_channel:
            error("NanoTrak not connected!")
            return 0.0, 0.0

        position = self.nanotrak_channel.GetCirclePosition()
        return position.HPosition, position.VPosition

    def latch(self) -> None:
        """Set the mode to latch."""
        self.nanotrak_channel.SetMode(GenericNanoTrakCLI.NanoTrakStatusBase.OperatingModes.Latch)
        TIAOddOrEven = GenericNanoTrakCLI.TIAOddOrEven
        TIARangeModes = GenericNanoTrakCLI.TIARangeModes
        self.nanotrak_channel.SetTIARangeMode(TIARangeModes.AutoRangeAtSelected, TIAOddOrEven.All)
        time.sleep(0.5)
        self.debug("NanoTrak latched")

    def track(self) -> None:
        """Set the mode to tracking."""
        self.nanotrak_channel.SetMode(GenericNanoTrakCLI.NanoTrakStatusBase.OperatingModes.Tracking)
        self.debug("NanoTrak set to Tracking mode.")

    def set_circle_diameter(self, diameter: float) -> None:
        """Set the circle diameter and wait."""
        self.nanotrak_channel.SetCircleDiameter(diameter)
        self.debug(f"Set circle diameter to {diameter}")
        time.sleep(0.5)  # Optional: wait for device to update

    def debug(self, message: str) -> None:
        """Print the message if 'debug while tracking' is activated."""
        if self.debug_while_tracking:
            print(message)