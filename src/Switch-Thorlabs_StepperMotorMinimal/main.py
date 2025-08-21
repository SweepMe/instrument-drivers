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

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ["Position"],
            "Bay": "1",  # maybe just use line edit
            "Serial Number": "52870913",
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.serial_number = parameters.get("Serial Number", "")
        self.sweep_mode = parameters.get("SweepMode", "Position")
        self.channel = parameters.get("Bay", "1")

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        # build device list
        DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()

        # Get device info and create rack object
        device_info = DeviceManagerCLI.DeviceFactory.GetDeviceInfo(self.serial_number)
        self.rack = ModularRackCLI.Rack.ModularRack.CreateModularRack(device_info.GetTypeID(), self.serial_number)

        # get the device channel
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

        print(f"Connected to device {self.serial_number}. Connection status: {self.rack.IsConnected}")

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        self.stepper.StopPolling()
        # self.stepper.DisableDevice()
        self.rack.Disconnect(True)
        print("Device stopped and rack disconnected.")

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        try:
            status = self.rack.IsSettingsInitialized()
            #print(f"Rack settings initialized: {status}")
        except Exception as e:
            print("Could not check if rack is initialized:", e)

        if not self.stepper.IsSettingsInitialized():
            try:
                self.stepper.WaitForSettingsInitialized(5000)
                #print("Settings initialized.")
            except Exception as e:
                print("Settings failed to initialize:", e)

        # Start polling
        self.stepper.StartPolling(250)
        time.sleep(0.5)  # Wait for polling to start

        # Enable the channel otherwise any move is ignored
        self.stepper.EnableDevice()
        time.sleep(0.5)  # Wait for device to be enabled

        print("Device is initialized, polling, and enabled.")
        self.stepper_motor = self.rack.GetStepperChannel(int(self.channel))
        # Why?
        motorConfiguration = self.stepper_motor.LoadMotorConfiguration(self.stepper.DeviceID)
        currentDeviceSettings = self.stepper_motor.MotorDeviceSettings

        #print("Homing device")
        #self.stepper_motor.Home(60000)
        #print("Device Homed")

        #print(self.stepper, type(self.stepper), self.stepper_motor, type(self.stepper_motor))

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        print(self.stepper_motor.MoveTo.Overloads)
        if self.sweep_mode == "Position":
            try:
                position = Decimal(self.value)
            except ValueError as e:
                msg = f"Invalid position format. Expected a integer, got '{self.value}'."
                raise ValueError(msg) from e

            #print(f"Moving Device to {position}")
            # Move the stepper motor to the specified position
            self.stepper_motor.MoveTo(position, Int32(self.timeout_ms))
            #print(f"Device Moved to {self.stepper_motor.Position}")

    def call(self) -> str:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        #return 1
        return float(str(self.stepper_motor.Position))

