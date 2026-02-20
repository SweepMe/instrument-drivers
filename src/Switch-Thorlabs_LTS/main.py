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
from System import Decimal, Action, UInt64
from pysweepme.EmptyDeviceClass import EmptyDevice

# Import Kinesis dll
kinesis_imported = False

bitness = 64 if sys.maxsize > 2 ** 32 else 32
kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis" if bitness == 64 else "C:\\Program Files (x86)\\Thorlabs\\Kinesis"

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

except Exception:
    pass
else:
    kinesis_imported = True


def callback_function(value):
    """Dummy callback function for the MoveTo command, which is called when the movement is completed.

    The function must take the return value of the MoveTo command as an argument.
    """
    pass


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

        # Device Parameters
        self.stage: LongTravelStage = None  # type: ignore
        self.sweep_mode: str = "Absolute position in mm"
        self.velocity: float = 5.0  # in mm/s
        self.timeout: int = 60  # in s, default value, will be updated in apply() based on the distance to travel and the velocity
        self.relative_movement_done: bool = False  # flag to keep track of whether the relative movement has already been performed in apply() or not

        self.home_at_start: bool = True
        self.home_velocity: float = 10.0  # in mm/s

    def find_ports(self) -> list[str]:
        """Returns the serial numbers of all devices connected via Kinesis."""
        device_list = self.list_devices()

        if not device_list:
            device_list = ["No devices found!"]

        return device_list

    @staticmethod
    def list_devices() -> list[str]:
        """Lists all connected devices."""
        if not kinesis_imported:
            msg = ("Kinesis .NET dlls not found! Please install Kinesis to C:\\Program Files\\Thorlabs\\Kinesis, and "
                   "ensure it is closed when running this driver.")
            raise ImportError(msg)

        DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()

        device_list = DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
        return [str(serial_num) for serial_num in device_list]

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Determine the new GUI parameters of the driver depending on the current parameters."""
        new_parameters = {
            "SweepMode": ["Absolute position in mm", "Relative position in mm"],
            "Velocity in mm/s": 10.0,
            "Home at start": True,
        }
        if parameters.get("Home at start", True):
            new_parameters["Home velocity in mm/s"] = 10.0

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Receive the values of the GUI parameters that were set by the user in the SweepMe! GUI."""
        self.serial_number = parameters.get("Port", "")
        self.sweep_mode = parameters.get("SweepMode", "Absolute position in mm")
        self.velocity = parameters.get("Velocity in mm/s", 5.0)

        self.home_at_start = parameters.get("Home at start", True)
        self.home_velocity = parameters.get("Home velocity in mm/s", 10.0)

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        available_devices = self.list_devices()
        if self.serial_number in ["No devices found!", ""]:
            msg = "No device connected! Please connect a Thorlabs LTS device."
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

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        if not self.stage.IsSettingsInitialized():
            try:
                self.stage.WaitForSettingsInitialized(5000)
            except Exception as e:
                print(f"Settings failed to initialize: {e}")

        self.stage.StartPolling(250)
        time.sleep(0.5)  # waiting time given by Kinesis .NET documentation example
        self.stage.EnableDevice()
        time.sleep(0.5)  # waiting time given by Kinesis .NET documentation example

        # Load motor configuration
        self.stage.LoadMotorConfiguration(self.serial_number)

    def poweroff(self) -> None:
        """Stop stage movement."""
        self.stage.StopImmediate()

    def configure(self) -> None:
        """Configure the device. This function is called every time the device is used in the sequencer."""
        self.set_velocity(float(self.velocity))

        if self.home_at_start:
            # Set homing velocity
            motor_device_settings = self.stage.MotorDeviceSettings
            motor_device_settings.Home.set_HomeVel(Decimal(float(self.velocity)))
            self.stage.SetSettings(motor_device_settings, False)

            self.stage.Home(60000)  # Home with a timeout of 60s

    def start(self) -> None:
        """Preparation before applying a new value."""
        # Reset the flag for performing the relative movement in adapt()
        self.relative_movement_done = False

    def apply(self) -> None:
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        self.convert_sweep_value()

        if self.sweep_mode.startswith("Relative"):
            current_position = self.get_position_mm()
            new_position = current_position + self.value
            if new_position < 0:
                msg = f"Invalid relative movement: current position is {current_position} mm, cannot move by {self.value} mm to a negative position."
                raise ValueError(msg)
            self.relative_movement_done = True
        else:
            new_position = self.value

        self.timeout = self.calculate_timeout(new_position)

        # The MoveTo method can be used in a non-blocking way by providing a callback function that is called when the movement is completed.
        # Create a .NET Action[UInt64] delegate
        action_u_int64 = Action[UInt64]
        callback_delegate = action_u_int64(callback_function)
        self.stage.MoveTo(Decimal(new_position), callback_delegate)

        # Wait either 1s or until the status shows that the movement has started
        for _ in range(10):
            if self.stage.Status.IsInMotion or self.stage.Status.IsMoving:
                break

            time.sleep(0.1)

    def reach(self) -> None:
        """Wait until the device has reached the target position."""
        time_start = time.time()
        while not self.is_run_stopped():
            if time.time() - time_start > self.timeout:
                msg = f"Failed to reach the target position within the timeout period of {self.timeout} seconds."
                raise TimeoutError(msg)

            status = self.stage.Status
            if status.IsInMotion or status.IsMoving:
                time.sleep(0.1)
            else:
                break

    def adapt(self) -> None:
        """Perform relative movements, as they are skipped in the apply() function.

        SweepMe! ignores relative movements if the SweepValue stays the same as in the previous run, which is the case
        for example when running multiple cycles of the same sequence. In this case, we perform the relative movement
        here in adapt(), which is called every time a sequence is run, even if the SweepValue does not change.
        """
        # Only perform the relative movement if it was not already performed in apply() (which is the case when the SweepValue did change since the last sweep).
        if self.sweep_mode.startswith("Relative") and not self.relative_movement_done:
            self.apply()
            self.reach()

    def call(self) -> float:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return self.get_position_mm()

    def convert_sweep_value(self) -> None:
        """Convert the sweep value to float."""
        try:
            self.value = float(self.value)
        except ValueError:
            msg = f"Invalid position value: {self.value}. Must be a number."
            raise ValueError(msg)

    def calculate_timeout(self, new_position: float) -> int:
        """Calculate the timeout in ms for the MoveTo command based on the distance to travel and the velocity.

        The timeout is set to twice the expected travel time, with a minimum of 60s.
        """
        current_position = self.get_position_mm()
        distance = abs(new_position - current_position)

        expected_travel_time = distance / float(self.velocity)
        return max(60, int(expected_travel_time * 2)) * 1000

    def get_position_mm(self) -> float:
        """Get the current position in mm."""
        status = self.stage.Status
        # TODO: there might be a more straightforward way to get the position in mm
        conv = self.stage.AdvancedMotorLimits.UnitConverter
        position_str = str(conv.DeviceUnitToReal(Decimal(status.Position), conv.UnitType.Length))
        position_float = float(position_str.replace(",", "."))
        return position_float

    def set_velocity(self, velocity: float) -> None:
        """Set the velocity of the device in mm/s."""
        velocity_parameters = self.stage.GetVelocityParams()
        velocity_parameters.MaxVelocity = Decimal(velocity)
        self.stage.SetVelocityParams(velocity_parameters)
