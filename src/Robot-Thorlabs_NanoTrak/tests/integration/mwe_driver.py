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


class Device(EmptyDevice):
    """Device class to implement functionalities of Thorlabs NanoTrak via Kinesis."""

    def __init__(self) -> None:
        """Initialize the device class and the instrument parameters."""
        super().__init__()

        self.shortname = "Nanotrak MWE"  # short name will be shown in the sequencer

        # Define the variables that can be measured by the device and that are returned by the 'call' function
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []

    def find_ports(self) -> list[str]:
        """Returns the serial numbers of all devices connected via Kinesis."""

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        new_parameters = {
            "SweepMode": ["None"],
            "Serial Number": "52870913",
        }

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Apply the parameters received from the SweepMe GUI or the pysweepme instance to the driver instance."""
        self.serial_number = parameters.get("Serial Number", "")

    def connect(self) -> None:
        """Connect to a fresh instance of the device every time."""
        kinesis_path = r"C:\Program Files\Thorlabs\Kinesis"
        if kinesis_path not in sys.path:
            sys.path.insert(0, kinesis_path)

        clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
        clr.AddReference("Thorlabs.MotionControl.ModularRackCLI")
        import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
        import Thorlabs.MotionControl.ModularRackCLI as ModularRackCLI
        import Thorlabs.MotionControl.GenericNanoTrakCLI as GenericNanoTrakCLI
        self.DeviceManagerCLI = DeviceManagerCLI
        self.ModularRackCLI = ModularRackCLI
        self.GenericNanoTrakCLI = GenericNanoTrakCLI

        # Build device list
        DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()

        # Get device info and create the rack object
        DeviceFactory = DeviceManagerCLI.DeviceFactory
        deviceInfo = DeviceFactory.GetDeviceInfo(self.serial_number)
        typeID = deviceInfo.GetTypeID()
        ModularRack = ModularRackCLI.Rack.ModularRack
        self.rack = ModularRack.CreateModularRack(typeID, self.serial_number)

        # Get the device channel (NanoTrak has 1 channel)
        self.device = self.rack[1]

        # Connect to the device
        self.rack.Connect(self.serial_number)
        print(f"Connected to device {self.serial_number}")

    def disconnect(self) -> None:
        """Cleanly disconnect NanoTrak and reset DLL/device state."""
        self.device.StopPolling()
        self.device.DisableDevice()
        self.rack.Disconnect(True)
        print("Device stopped and rack disconnected.")

    def initialize(self) -> None:
        """Initialize the device only after full connection."""
        # Wait for device settings to initialize (timeout 5000 ms)
        if not self.device.IsSettingsInitialized():
            try:
                self.device.WaitForSettingsInitialized(5000)
                print("Settings initialized.")
            except Exception as e:
                print("Settings failed to initialize:", e)

        # Start polling
        self.device.StartPolling(250)
        time.sleep(0.5)  # Wait for polling to start

        # Enable the device
        self.device.EnableDevice()
        time.sleep(0.5)  # Wait for device to be enabled

        print("Device is initialized, polling, and enabled.")


    def configure(self) -> None:
        """Configure the device. This function is called only once at the start of the measurement."""
        bay = 1
        device_type = self.rack.BayDeviceType(bay)
        print(device_type)
        ChannelDefinitions = self.ModularRackCLI.Rack.ChannelDefinitions

        if device_type == ChannelDefinitions.ModularRackDevices.ModularRackNanoTrak:
            nanoTrak = self.rack.GetNanoTrakChannel(bay)
            if nanoTrak is not None:
                DeviceSettingsUseOptionType = self.DeviceManagerCLI.DeviceConfiguration.DeviceSettingsUseOptionType
                nanoTrakConfiguration = nanoTrak.GetNanoTrakConfiguration(self.serialNo, DeviceSettingsUseOptionType.UseConfiguredSettings)
                currentDeviceSettings = nanoTrak.NanoTrakDeviceSettings
                nanoTrak.SetSettings(currentDeviceSettings, False)
                print(nanoTrak.GetCircleDiameter())
                print(nanoTrak.GetFeedbackSource())
                nanoTrak.GetSettings(currentDeviceSettings)
                NanoTrakStatusBase = self.GenericNanoTrakCLI.NanoTrakStatusBase
                NanoTrakFeedbackSource = self.GenericNanoTrakCLI.Settings.IOSettingsSettings.FeedbackSources
                nanoTrak.SetFeedbackSource(NanoTrakFeedbackSource.BNC_10V)
                nanoTrak.SetMode(NanoTrakStatusBase.OperatingModes.Tracking)
                print("Device set to Tracking mode.")
                HVPosition = self.GenericNanoTrakCLI.HVPosition
                # Loop to set circle diameter from 1 to 3 in increments of 0.5
                for diameter in [round(x * 0.5, 2) for x in range(2, 7)]:  # 1.0, 1.5, 2.0, 2.5, 3.0
                    nanoTrak.SetCircleDiameter(diameter)
                    print(f"Set circle diameter to {diameter}")
                    time.sleep(0.5)  # Optional: wait for device to update
                nanoTrak.SetCircleHomePosition(HVPosition(5, 5))
                nanoTrak.HomeCircle()
                nanoTrak.SetMode(NanoTrakStatusBase.OperatingModes.Latch)
                TIAOddOrEven = self.GenericNanoTrakCLI.TIAOddOrEven
                TIARangeModes = self.GenericNanoTrakCLI.TIARangeModes
                nanoTrak.SetTIARangeMode(TIARangeModes.AutoRangeAtSelected, TIAOddOrEven.All)
                time.sleep(0.5)
                reading = nanoTrak.GetReading()
                nanoTrak.SetMode(NanoTrakStatusBase.OperatingModes.Latch)
                print("NanoTrak voltage set to", reading)
                print("Absolute Reading:", reading.AbsoluteReading)
                print("Relative Reading:", reading.RelativeReading)
                print("Selected TIA Range:", reading.SelectedRange)
                print("UnderOrOverRead:", reading.UnderOrOverRead)

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""