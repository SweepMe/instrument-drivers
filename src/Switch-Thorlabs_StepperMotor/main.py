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
#
# SweepMe! driver
# * Module: Switch
# * Instrument: Thorlabs Stepper Motor

from __future__ import annotations

import contextlib

import sys
import time
from typing import Any

import clr
from pysweepme.EmptyDeviceClass import EmptyDevice
from System import Decimal, Int32

# Import Kinesis dll
kinesis_imported = False

bitness = 64 if sys.maxsize > 2**32 else 32
kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis" # if bitness == 64 else "C:\\Program Files (x86)\\Thorlabs\\Kinesis"
try:
    if kinesis_path not in sys.path:
        sys.path.insert(0, kinesis_path)

    clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
    clr.AddReference("Thorlabs.MotionControl.ModularRackCLI")

    from Thorlabs.MotionControl import DeviceManagerCLI, ModularRackCLI
except:
    pass
else:
    kinesis_imported = True


class Device(EmptyDevice):
    """Driver for the Thorlabs Stepper Motor."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "Stepper Motor"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Position"]
        self.units = ["mm"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.serial_number: str = ""
        self.rack = None
        self.stepper = None

        # Measurement parameters
        self.channel: int = 1
        self.sweep_mode: str = "Position"
        self.timeout_ms: int = 60000  # Default timeout for operations in milliseconds

    def find_ports(self) -> list[str]:
        """Returns the serial numbers of all devices connected via Kinesis."""
        device_list = self.list_devices()

        if not device_list:
            device_list = ["No devices found!"]

        return device_list

    @staticmethod
    def list_devices() -> list[str]:
        """Lists all devices.

        Bug: Once Simulation mode is switched on, GetDeviceList will also find simulated devices even when simulation
        mode is uninitialized.
        The device list can be filtered by the device prefix, e.g. BenchtopNanoTrakCLI.BenchtopNanoTrak.DevicePrefix
        """
        if not kinesis_imported:
            msg = ("Kinesis .NET dlls not found! Please install Kinesis to C:\\Program Files\\Thorlabs\\Kinesis, and "
                   "ensure it is closed when running this driver.")
            raise ImportError(msg)

        DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()
        device_list = DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()

        return [str(serial_num) for serial_num in device_list]

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ["Position"],
            "Bay": "1",  # maybe just use line edit
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.serial_number = parameters.get("Port", "")
        self.sweep_mode = parameters.get("SweepMode", "Position")
        self.channel = parameters.get("Bay", "1")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if not kinesis_imported:
            msg = ("Kinesis .NET dlls not found! Please install Kinesis to C:\\Program Files\\Thorlabs\\Kinesis, and "
                   "ensure it is closed when running this driver.")
            raise ImportError(msg)

        available_devices = self.list_devices()
        if self.serial_number in ["No devices found!", ""]:
            msg = "No device connected! Please connect a Thorlabs NanoTrak device."
            raise ValueError(msg)

        if self.serial_number not in available_devices:
            msg = f"Device with serial number {self.serial_number} not found in the list of available devices: {available_devices}"
            raise ValueError(msg)

        device_info = DeviceManagerCLI.DeviceFactory.GetDeviceInfo(self.serial_number)
        self.rack = ModularRackCLI.Rack.ModularRack.CreateModularRack(device_info.GetTypeID(), self.serial_number)

        self.stepper = self.rack[int(self.channel)]

        # Connect to the device
        timeout_s = 10
        while not self.rack.IsConnected:
            try:
                self.rack.Connect(self.serial_number)
            except DeviceManagerCLI.DeviceNotReadyException:
                #print("DeviceNotReadyException: Device is not ready yet, retrying...")
                time.sleep(0.2)
                timeout_s -= 0.2

            if timeout_s <= 0:
                #print("Timeout: Device connection failed after 10 seconds.")
                msg = "Failed to connect to the device within the timeout period."
                raise TimeoutError(msg)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        if not self.stepper:
            return

        self.stepper.StopPolling()
        self.rack.Disconnect(True)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        # pass if the device is already initialized
        if not self.stepper.IsSettingsInitialized():
            with contextlib.suppress(Exception):
                self.stepper.WaitForSettingsInitialized(5000)

        # The polling loop requests regular status requests to the motor to ensure the program keeps track of the device.
        self.stepper.StartPolling(250)
        time.sleep(0.5)

        # Enable the channel otherwise any move is ignored
        self.stepper.EnableDevice()
        time.sleep(0.5)

        # continue with stepper_motor object - unclear why
        self.stepper_motor = self.rack.GetStepperChannel(int(self.channel))
        # Why?
        motorConfiguration = self.stepper_motor.LoadMotorConfiguration(self.stepper.DeviceID)
        currentDeviceSettings = self.stepper_motor.MotorDeviceSettings

        self.stepper.Home(self.timeout_ms)

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        if self.sweep_mode == "Position":
            try:
                position = Decimal(self.value)
            except ValueError as e:
                msg = f"Invalid position format. Expected a integer, got '{self.value}'."
                raise ValueError(msg) from e

            self.stepper_motor.MoveTo(position, Int32(self.timeout_ms))

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return float(str(self.stepper_motor.Position))

