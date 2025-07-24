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
        self.variables = ["Horizontal Position", "Vertical Position", "Signal Strength"]
        self.units = ["m", "m", ""]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        # Imported Kinesis .NET dlls
        self.kinesis_client = None
        """The device specific NanoTrak CLI module, e.g. BenchtopNanoTrakCLI, TCubeNanoTrakCLI, or KCubeNanoTrakCLI."""

        # Communication parameters
        self.serial_number: str = ""  # Serial number of the device
        self.nanotrak = None
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
            "SweepMode": ["Center Position", "Circle Diameter", "None"],
            "Mode": ["Tracking", "Latch"],
            "Reading": ["Absolute", "Relative", "None"],
            "Simulation": False,
            "Modular Rack": False,
        }

        if parameters.get("Modular Rack", False):
            new_parameters["Bay"] = 1

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Apply the parameters received from the SweepMe GUI or the pysweepme instance to the driver instance."""
        self.serial_number = parameters.get("Port", "")
        self.tracking_mode = parameters.get("Mode", "Tracking")
        self.is_simulation = parameters.get("Simulation", False)
        self.reading_mode = parameters.get("Reading", "Absolute")

        self.is_modular_rack = parameters.get("Modular Rack", False)
        if self.is_modular_rack:
            self.bay = parameters.get("Bay", 1)

        self.variables = ["Horizontal Position", "Vertical Position"]
        self.units = ["m", "m"]
        if self.reading_mode == "Absolute":
            self.variables.append("Absolute Reading")
            self.units.append("")
        elif self.reading_mode == "Relative":
            self.variables.append("Relative Reading")
            self.units.append("%")

        self.plottype = [True] * len(self.variables)
        self.savetype = [True] * len(self.variables)

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

        # Wait for device connection
        print("Waiting for device to set IsConnected to True...")
        timeout_s = 10
        while not self.nanotrak.IsConnected:
            try:
                self.nanotrak.Connect(str(self.serial_number))
            except self.DeviceManagerCLI.DeviceNotReadyException:
                print("DeviceNotReadyException: Device is not ready yet, retrying...")
                time.sleep(0.2)
                timeout_s -= 0.2

            if timeout_s <= 0:
                msg = f"Failed to connect to the device {self.serial_number} within the timeout period."
                raise TimeoutError(msg)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        if not self.nanotrak:
            return

        self.nanotrak.StopPolling()
        self.nanotrak.Disconnect(True)

        if self.is_simulation:
            self.set_simulation_mode(False)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        if not self.nanotrak.IsSettingsInitialized():
            print("Waiting for settings to be initialized...")
            self.nanotrak.WaitForSettingsInitialized(10000)  # ms

        print("Start polling the device...")
        polling_rate = 250
        self.nanotrak.StartPolling(polling_rate)
        time.sleep(0.5)

        # Enable the device
        self.nanotrak.EnableDevice()
        time.sleep(0.5)

    def configure(self) -> None:
        """Configure the device. This function is called only once at the start of the measurement."""
        # ToDo: Could add
        # DeviceSettingsUseOptionType = DeviceManagerCLI.DeviceConfiguration.DeviceSettingsUseOptionType
        # nanoTrakConfiguration = nanoTrak.GetNanoTrakConfiguration(serialNo, DeviceSettingsUseOptionType.UseConfiguredSettings)
        # currentDeviceSettings = nanoTrak.NanoTrakDeviceSettings
        # nanoTrak.SetSettings(currentDeviceSettings, False)

        # config = self.device.GetNanoTrakConfiguration(self.serial_number)
        self.set_mode(self.tracking_mode)
        # self.device.SetTIARangeMode(TIARangeModes.AutoRangeAtSelected, TIAOddOrEven.All);

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweepmode == "Center Position":
            if "," in self.value:
                horizontal, vertical = map(float, self.value.split(","))
            elif ";" in self.value:
                horizontal, vertical = map(float, self.value.split(";"))
            else:
                msg = f"Invalid format for Center Position: {self.value}. Expected 'x,y' or 'x;y'."
                raise ValueError(msg)

            position = GenericNanoTrakCLI.HVPosition(horizontal, vertical)

            self.nanotrak.SetCircleHomePosition(position)
            self.nanotrak.HomeCircle()

        elif self.sweepmode == "Circle Diameter":
            diameter = abs(float(self.value))
            self.nanotrak.SetCircleDiameter(diameter)
            time.sleep(0.5)  # Optional: wait for device to update

            self.nanotrak.HomeCircle()

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        horizontal, vertical = self.get_current_position()

        if self.reading_mode in ["Absolute", "Relative"]:
            reading = self.nanotrak.GetReading()
            reading_value = reading.AbsoluteReading if self.reading_mode == "Absolute" else reading.RelativeReading
            return [horizontal, vertical, reading_value]

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
            rack = modular_rack.CreateModularRack(type_id, serial_number)

            # Could also be rack[1] or rack[bay]
            self.nanotrak = rack.GetNanoTrakChannel(self.bay)

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
        if not self.nanotrak:
            error("NanoTrak not connected!")
            return 0.0, 0.0

        position = self.nanotrak.GetCirclePosition()
        return position.HPosition, position.VPosition

    def set_mode(self, mode_string: str = "Tracking") -> None:
        """Set the mode of the device to either Tracking or Latch."""
        if not self.nanotrak:
            error("NanoTrak not connected!")
            return

        mode_string = mode_string.strip().lower()

        if mode_string == "tracking":
            new_mode = GenericNanoTrakCLI.NanoTrakStatus.OperatingModes.Tracking
        elif mode_string == "latch":
            new_mode = GenericNanoTrakCLI.NanoTrakStatus.OperatingModes.Latch
        else:
            error(f"Unknown mode: {mode_string}")
            return

        self.nanotrak.SetMode(new_mode)
