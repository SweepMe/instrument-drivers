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

import clr
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import error

# Import Kinesis dll
bitness = 64 if sys.maxsize > 2**32 else 32
kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis" # if bitness == 64 else "C:\\Program Files (x86)\\Thorlabs\\Kinesis"

if kinesis_path not in sys.path:
    sys.path.insert(0, kinesis_path)


def add_dotnet_references() -> tuple:
    """Importing Kinesis .NET dll."""
    clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
    clr.AddReference("Thorlabs.MotionControl.GenericNanoTrakCLI")
    clr.AddReference("Thorlabs.MotionControl.Benchtop.NanoTrakCLI")

    from Thorlabs.MotionControl import DeviceManagerCLI, GenericNanoTrakCLI
    from Thorlabs.MotionControl.Benchtop import NanoTrakCLI

    return DeviceManagerCLI, GenericNanoTrakCLI, NanoTrakCLI


class Device(EmptyDevice):
    """Device class to implement functionalities of Thorlabs NanoTrak via Kinesis."""
    description = """
                    <h3>Driver Template</h3>
                    When using center position, the value must be a string with two values separated by a comma, e.g. "5,2" for horizontal and vertical position.
                    <p>Setup:</p>
                    <ul>
                    <li>Install Kinesis</li>
                    </ul>
                    """

    dotnet_added = False

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
        self.DeviceManagerCLI = None
        self.GenericNanoTrakCLI = None
        self.BenchtopNanoTrakCLI = None

        # Communication parameters
        self.serial_number: str = ""  # Serial number of the device
        self.device = None
        self.is_simulation = False

        # Measurement parameters
        self.reading_mode: str = "Absolute"  # Can be "Absolute", "Relative", or "None"

    def find_ports(self) -> list[str]:
        """Returns the serial numbers of all devices connected via Kinesis."""
        if not self.dotnet_added:
            self.import_kinesis()

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

    def set_simulation_mode(self, state: bool) -> None:
        """Set the simulation mode for the device."""
        if state:
            self.DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()

        else:
            self.DeviceManagerCLI.SimulationManager.Instance.UninitializeSimulations()

    def import_kinesis(self) -> None:
        """Import Kinesis .NET dll."""
        if not self.dotnet_added:
            self.DeviceManagerCLI, self.GenericNanoTrakCLI, self.BenchtopNanoTrakCLI = add_dotnet_references()
            self.dotnet_added = True

    def list_devices(self) -> list[str]:
        """Lists all devices.

        Bug: Once Simulation mode is switched on, GetDeviceList will also find simulated devices even when simulation
        mode is uninitialized.
        """
        self.DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()
        device_list = self.DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
        return [str(serial_num) for serial_num in device_list]

    def set_GUIparameter(self) -> dict:
        """Returns a dictionary with keys and values to generate GUI elements in the SweepMe! GUI."""
        return {
            "SweepMode": ["Center Position"],
            "Simulation": False,
            "Reading": ["Absolute", "Relative", "None"],
        }

    def get_GUIparameter(self, parameter: dict) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.serial_number = parameter.get("Port", "")
        self.is_simulation = parameter.get("Simulation", False)
        self.reading_mode = parameter.get("Reading", "Absolute")

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

        if not self.dotnet_added:
            self.import_kinesis()

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if self.serial_number in ["No devices found!", ""]:
            error("No device connected! Please connect a Thorlabs NanoTrak device.")
            return

        # If no devices are found, initialize simulations
        if self.is_simulation:
            self.set_simulation_mode(True)

        # TODO: Test if the timeouts are sufficient or can be reduced
        self.device = self.BenchtopNanoTrakCLI.BenchtopNanoTrak.CreateBenchtopNanoTrak(self.serial_number)
        print(f"Device: {self.device}, Serial Number: {self.serial_number}")
        time.sleep(2.5)
        self.device.Connect(str(self.serial_number))

        # print(self.device.IsSettingsInitialized())
        # self.kinesis_device.WaitForSettingsInitialized(5000)

        self.device.StartPolling(250)
        time.sleep(0.5)
        self.device.EnableDevice()
        time.sleep(0.5)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        if not self.device:
            return

        self.device.StopPolling()
        self.device.Disconnect(True)

        if self.is_simulation:
            self.set_simulation_mode(False)

    def configure(self) -> None:
        """Configure the device. This function is called only once at the start of the measurement."""
        config = self.device.GetNanoTrakConfiguration(self.serial_number)
        self.device.SetMode(self.GenericNanoTrakCLI.NanoTrakStatus.OperatingModes.Tracking)
        # self.device.SetTIARangeMode(TIARangeModes.AutoRangeAtSelected, TIAOddOrEven.All);

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        # TODO: Check which mode should be used and which values are needed
        if self.sweepmode == "Center Position":
            horizontal, vertical = self.value.split(",")
            position = self.GenericNanoTrakCLI.HVPosition(float(horizontal), vertical(vertical))

            self.device.SetCircleHomePosition(position)
            self.device.HomeCircle()

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        # time.sleep(0.5)
        horizontal, vertical = self.get_current_position()

        if self.reading_mode in ["Absolute", "Relative"]:
            reading = self.device.GetReading()
            reading_value = reading.AbsoluteReading if self.reading_mode == "Absolute" else reading.RelativeReading
            return [horizontal, vertical, reading_value]

        return [horizontal, vertical]

    def finish(self) -> None:
        """Do some final steps after the acquisition of a measurement point."""

    """Wrapper Functions"""

    def get_identification(self) -> str:
        """Returns the identification of the device."""
        if not self.device:
            error("Device not connected!")
            return ""

        return self.device.GetDeviceInfo().SerialNumber

    def get_current_position(self) -> tuple[float, float]:
        """Get the current circular position and signal strength at the current position."""
        if not self.device:
            error("Device not connected!")
            return 0.0, 0.0

        position = self.device.GetCirclePosition()
        return position.HPosition, position.VPosition

    def set_mode(self, mode_string: str = "Tracking") -> None:
        """Set the mode of the device to either Tracking or Latch."""
        if not self.device:
            error("Device not connected!")
            return

        mode_string = mode_string.strip().lower()

        if mode_string == "tracking":
            new_mode = self.GenericNanoTrakCLI.NanoTrakStatus.OperatingModes.Tracking
        elif mode_string == "latch":
            new_mode = self.GenericNanoTrakCLI.NanoTrakStatus.OperatingModes.Latch
        else:
            error(f"Unknown mode: {mode_string}")
            return

        self.device.SetMode(new_mode)
