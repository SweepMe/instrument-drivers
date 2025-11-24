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
# * Instrument: Thorlabs LTS

from __future__ import annotations

import time
from typing import Any

import clr
import sys
from System import Decimal
from pysweepme.EmptyDeviceClass import EmptyDevice


# Import Kinesis dll
kinesis_imported = False

bitness = 64 if sys.maxsize > 2**32 else 32
kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis" # if bitness == 64 else "C:\\Program Files (x86)\\Thorlabs\\Kinesis"
try:
    if kinesis_path not in sys.path:
        sys.path.insert(0, kinesis_path)

    clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
    clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
    clr.AddReference("Thorlabs.MotionControl.IntegratedStepperMotorsCLI")

    import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
    # from Thorlabs.MotionControl.GenericMotorCLI import IGenericAdvancedMotor
    # from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import VelocityParameters
    from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage  # , ThorlabsIntegratedStepperMotorSettings

except:
    pass
else:
    kinesis_imported = True


class Device(EmptyDevice):
    """Driver for the Thorlabs LTS."""

    def __init__(self) -> None:
        """Initialize the driver class and the instrument parameters."""
        super().__init__()

        self.shortname = "LTS"  # short name will be shown in the sequencer

        # SweepMe! parameters
        self.variables = ["Position"]
        self.units = ["mm"]
        self.plottype = [True]
        self.savetype = [True]

        # Communication Parameters
        self.serial_number: str = ""
        self.use_simulation = False

        # Device Parameters
        self.stage: LongTravelStage = None  # type: ignore
        self.velocity: float = 5.0  # in mm/s

    def find_ports(self) -> list[str]:
        """Returns the serial numbers of all devices connected via Kinesis."""
        device_list = self.list_devices()

        if self.use_simulation:
            self.set_simulation_mode(True)
            device_list = self.list_devices()
            self.set_simulation_mode(False)

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

    @staticmethod
    def set_simulation_mode(state: bool) -> None:
        """Set the simulation mode for the device."""
        if state:
            DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()
        else:
            DeviceManagerCLI.SimulationManager.Instance.UninitializeSimulations()

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        del parameters
        return {
            "SweepMode": ["Position in mm"],
            "Velocity in mm/s": 10.0,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.serial_number = parameters.get("Port", "")
        self.velocity = parameters.get("Velocity in mm/s", 5.0)

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        available_devices = self.list_devices()
        if self.serial_number in ["No devices found!", ""]:
            msg = "No device connected! Please connect a Thorlabs NanoTrak device."
            raise ValueError(msg)

        if self.serial_number not in available_devices:
            msg = f"Device with serial number {self.serial_number} not found in the list of available devices: {available_devices}"
            raise ValueError(msg)

        self.stage = LongTravelStage.CreateLongTravelStage(self.serial_number)
        self.device_manager_connect()

    def device_manager_connect(self, timeout_s=10):
        """Connect to the device manager with a timeout.
        """
        starting_time = time.time()
        while not self.stage.IsConnected and not self.is_run_stopped():
            try:
                self.stage.Connect(str(self.serial_number))
            except DeviceManagerCLI.DeviceNotReadyException:
                print("DeviceNotReadyException: Device is not ready yet, retrying...")
                time.sleep(0.5)

            if time.time() - starting_time > timeout_s:
                msg = f"Failed to connect to the device {self.serial_number} within the timeout period."
                raise TimeoutError(msg)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        self.stage.StopPolling()
        self.stage.Disconnect(True)
        if self.use_simulation:
            self.set_simulation_mode(False)

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        if not self.stage.IsSettingsInitialized():
            try:
                self.stage.WaitForSettingsInitialized(5000)
            except Exception as e:
                print(f"Settings failed to initialize: {e}")

        self.stage.StartPolling(250)
        time.sleep(0.5)
        self.stage.EnableDevice()
        time.sleep(0.5)

    def deinitialize(self) -> None:
        """Deinitialize the device. This function is called only once at the end of the measurement."""

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        # Load motor configuration
        motor_config = self.stage.LoadMotorConfiguration(self.serial_number)
        current_settings: ThorlabsIntegratedStepperMotorSettings = self.stage.MotorDeviceSettings

        self.set_velocity(float(self.velocity))

    def unconfigure(self) -> None:
        """Unconfigure the device. This function is called when the procedure leaves a branch of the sequencer."""

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        try:
            new_position = Decimal(float(self.value))
        except ValueError:
            msg = f"Invalid position value: {self.value}. Must be a number."
            raise ValueError(msg)

        # todo reach. Currently, the command is blocking until the position is reached.
        self.stage.MoveTo(new_position, 60000)

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.get_position_mm()

    def get_position_mm(self) -> float:
        """Get the current position in mm."""
        status = self.stage.Status
        # TODO: there might be a more straightforward way to get the position in mm
        conv = self.stage.AdvancedMotorLimits.UnitConverter
        pos = float(str(conv.DeviceUnitToReal(Decimal(status.Position), conv.UnitType.Length)))
        return pos

    def set_velocity(self, velocity: float) -> None:
        """Set the velocity of the device in mm/s."""
        velocity_parameters = self.stage.GetVelocityParams()
        velocity_parameters.MaxVelocity = Decimal(velocity)
        self.stage.SetVelocityParams(velocity_parameters)
