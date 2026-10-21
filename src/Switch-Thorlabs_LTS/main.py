# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2025-2026 SweepMe! GmbH (sweep-me.net)
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

import sys
import threading
import time
from typing import Any

import clr
from pysweepme.EmptyDeviceClass import EmptyDevice
from System import Action, Decimal, UInt64

# Import Kinesis dll
if sys.maxsize > 2**32:
    kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis"
else:
    kinesis_path = "C:\\Program Files (x86)\\Thorlabs\\Kinesis"

kinesis_import_error: Exception | None = None  # reason why the Kinesis .NET dlls could not be imported

try:
    if kinesis_path not in sys.path:
        sys.path.insert(0, kinesis_path)

    clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
    clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
    clr.AddReference("Thorlabs.MotionControl.IntegratedStepperMotorsCLI")

    from Thorlabs.MotionControl import DeviceManagerCLI
    from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage

except Exception as e:
    kinesis_import_error = e

MAX_HOME_VELOCITY = 20.0  # in mm/s
MAX_TRAVEL_RANGE = 300.0  # in mm, longest LTS stage, used for the homing timeout if Kinesis reports no travel range
POSITION_TOLERANCE = 1e-4  # in mm, targets this close outside the travel range are clipped to the travel range
SIMULATION_MODE = False  # if True, the driver will list simulated devices from Kinesis Simulator


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
        self.simulations_initialized: bool = False  # whether this driver initialized the Kinesis simulations

        # Device Parameters
        self.stage: LongTravelStage = None
        self.sweep_mode: str = "Absolute position in mm"
        self.velocity: float | str = 10.0  # in mm/s, as set in the GUI
        self.home_at_start: bool = True
        self.home_velocity: float | str = 10.0  # in mm/s, as set in the GUI

        # Travel range of the stage, read from Kinesis in initialize(). Both are 0 if Kinesis reports no travel range.
        self.position_min: float = 0.0  # in mm
        self.position_max: float = 0.0  # in mm

        self.move_velocity: float = 10.0  # in mm/s, checked velocity, set in configure()
        self.timeout: float = 60  # in s, updated in apply() based on the distance to travel and the velocity
        self.move_completed: threading.Event = threading.Event()  # set by Kinesis once the latest movement is completed
        self.relative_movement_done: bool = False  # whether the relative movement was already performed in apply()

    def find_ports(self) -> list[str]:
        """Returns the serial numbers of all devices connected via Kinesis, in simulation mode the simulated ones."""
        if SIMULATION_MODE:
            # Outside of try, so that a missing Kinesis raises its ImportError instead of failing in the cleanup
            self.initialize_simulations()
            try:
                device_list = self.list_devices()
            finally:
                self.uninitialize_simulations()
        else:
            device_list = self.list_devices()

        if not device_list:
            device_list = ["No devices found!"]

        return device_list

    @staticmethod
    def check_kinesis_imported() -> None:
        """Raise an ImportError with the reason if the Kinesis .NET dlls could not be imported."""
        if kinesis_import_error is not None:
            msg = (
                f"Kinesis .NET dlls could not be loaded from {kinesis_path}: {kinesis_import_error}. Please install "
                "Kinesis with the same bitness as SweepMe!, and ensure it is closed when running this driver."
            )
            raise ImportError(msg) from kinesis_import_error

    @staticmethod
    def list_devices() -> list[str]:
        """Lists all connected devices.

        Simulated devices are listed while the Kinesis simulations are initialized, and Kinesis keeps listing them
        after the simulations are uninitialized again.
        """
        Device.check_kinesis_imported()

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
        self.velocity = parameters.get("Velocity in mm/s", 10.0)

        self.home_at_start = parameters.get("Home at start", True)
        if self.home_at_start:
            self.home_velocity = parameters.get("Home velocity in mm/s", 10.0)

    def connect(self) -> None:
        """Connect to the device. This function is called only once at the start of the measurement."""
        if SIMULATION_MODE:
            self.initialize_simulations()
        available_devices = self.list_devices()
        if self.serial_number in ["No devices found!", ""]:
            msg = "No device connected! Please connect a Thorlabs LTS device."
            raise ValueError(msg)

        if self.serial_number not in available_devices:
            msg = (
                f"Device with serial number {self.serial_number} not found in the list of available devices: "
                f"{available_devices}"
            )
            raise ValueError(msg)

        self.stage = LongTravelStage.CreateLongTravelStage(self.serial_number)
        self.device_manager_connect()

    def device_manager_connect(self, timeout_s: int = 10) -> None:
        """Connect to the device manager with a timeout."""
        starting_time = time.time()
        while not self.stage.IsConnected and not self.is_run_stopped():
            try:
                self.stage.Connect(self.serial_number)
            except DeviceManagerCLI.DeviceNotReadyException:
                # The device is not ready yet, retry
                time.sleep(0.5)

            if time.time() - starting_time > timeout_s:
                msg = f"Failed to connect to the device {self.serial_number} within the timeout period."
                raise TimeoutError(msg)

    def disconnect(self) -> None:
        """Disconnect from the device. This function is called only once at the end of the measurement."""
        # The stage does not exist or is not connected if connect() failed
        if self.stage is not None and self.stage.IsConnected:
            self.stage.StopPolling()
            self.stage.Disconnect(True)

        # Only uninitialize the simulations if connect() initialized them, it may have failed before
        if self.simulations_initialized:
            self.uninitialize_simulations()

    def initialize(self) -> None:
        """Initialize the device. This function is called only once at the start of the measurement."""
        if not self.stage.IsSettingsInitialized():
            try:
                self.stage.WaitForSettingsInitialized(5000)
            except Exception as e:
                msg = f"The settings of the device {self.serial_number} could not be initialized within 5 s."
                raise TimeoutError(msg) from e

        self.stage.StartPolling(250)
        time.sleep(0.5)  # waiting time given by Kinesis .NET documentation example
        self.stage.EnableDevice()
        time.sleep(0.5)  # waiting time given by Kinesis .NET documentation example

        # Load motor configuration before reading the limits of the stage or moving it
        self.stage.LoadMotorConfiguration(self.serial_number)

        limits = self.stage.AdvancedMotorLimits
        self.position_min = Decimal.ToDouble(limits.LengthMinimum)
        self.position_max = Decimal.ToDouble(limits.LengthMaximum)
        if not self.has_travel_range():
            # e.g. a simulated stage, for which Kinesis loads the motor configuration "Default" with no travel range
            msg = f"Kinesis reports no travel range for stage {self.serial_number}, target positions are not checked."
            self.message_log(msg)

    def poweroff(self) -> None:
        """Stop stage movement."""
        if self.stage is not None and self.stage.IsConnected:
            self.stage.StopImmediate()

    def configure(self) -> None:
        """Configure the device. This function is called when the device is first activated in a branch."""
        self.move_velocity = self.check_velocity(self.velocity, "Velocity")
        self.set_velocity(self.move_velocity)

        if self.home_at_start:
            home_velocity = self.check_velocity(self.home_velocity, "Home velocity", MAX_HOME_VELOCITY)
            self.set_home_velocity(home_velocity)

            # Homing can start from any position within the travel range
            travel_range = self.position_max - self.position_min if self.has_travel_range() else MAX_TRAVEL_RANGE
            timeout = self.calculate_timeout(travel_range, home_velocity)
            self.wait_for_completion(self.start_homing(), timeout, "home the stage")

    def start(self) -> None:
        """Preparation before applying a new value."""
        # Reset the flag for performing the relative movement in adapt()
        self.relative_movement_done = False

    def apply(self) -> None:
        """Start the movement to the new position given by 'self.value'. reach() waits until it is completed."""
        value = self.get_sweep_value()
        current_position = self.get_position_mm()

        if self.sweep_mode.startswith("Relative"):
            new_position = current_position + value
            self.relative_movement_done = True
        else:
            new_position = value

        new_position = self.limit_to_travel_range(new_position)
        self.timeout = self.calculate_timeout(abs(new_position - current_position), self.move_velocity)
        self.move_completed = self.move_to(new_position)

    def reach(self) -> None:
        """Wait until the device has reached the target position."""
        self.wait_for_completion(self.move_completed, self.timeout, "reach the target position")

    def adapt(self) -> None:
        """Perform relative movements, as they are skipped in the apply() function.

        SweepMe! does not call apply() if the SweepValue stays the same as at the previous measurement point, which is
        the case for example when running multiple cycles of the same sequence. In this case, we perform the relative
        movement here in adapt(), which is called at every measurement point, even if the SweepValue does not change.
        """
        # Only move if apply() did not already perform the relative movement, i.e. the SweepValue did not change
        if self.sweep_mode.startswith("Relative") and not self.relative_movement_done:
            self.apply()
            self.reach()

    def call(self) -> list[float]:
        """Return the measurement results. Must return as many values as defined in self.variables."""
        return [self.get_position_mm()]

    def get_sweep_value(self) -> float:
        """Return the sweep value as float."""
        try:
            return float(self.value)
        except (TypeError, ValueError):
            msg = f"Invalid position value: {self.value}. Must be a number."
            raise ValueError(msg) from None

    @staticmethod
    def check_velocity(velocity: float | str, name: str, maximum: float | None = None) -> float:
        """Convert a velocity in mm/s to float and check that it is larger than 0 and, if given, at most maximum.

        The maximum velocity reported by Kinesis (AdvancedMotorLimits.VelocityMaximum) is not used, because it is
        lower than velocities that Kinesis accepts and the stage runs at.
        """
        try:
            velocity_float = float(velocity)
        except ValueError:
            msg = f"Invalid {name.lower()}: {velocity}. Must be a number."
            raise ValueError(msg) from None

        if velocity_float <= 0:
            msg = f"Invalid {name.lower()}: {velocity_float} mm/s. Must be larger than 0 mm/s."
            raise ValueError(msg)

        if maximum is not None and velocity_float > maximum:
            msg = f"Invalid {name.lower()}: {velocity_float} mm/s. Must be at most {maximum} mm/s."
            raise ValueError(msg)

        return velocity_float

    @staticmethod
    def calculate_timeout(distance: float, velocity: float) -> float:
        """Calculate the timeout in s for a movement over the distance in mm with the velocity in mm/s.

        The timeout is set to twice the expected travel time, with a minimum of 60 s.
        """
        return max(60.0, 2 * distance / velocity)

    def has_travel_range(self) -> bool:
        """Return whether Kinesis reported a travel range for the stage."""
        return self.position_max > self.position_min

    def limit_to_travel_range(self, position: float) -> float:
        """Check that the position in mm is within the travel range of the stage, if Kinesis reported one.

        Positions outside the travel range by less than POSITION_TOLERANCE are clipped to the travel range, as they
        occur when moving relatively to the end of the travel range due to the resolution of the position readback.
        """
        if not self.has_travel_range():
            return position

        if not self.position_min - POSITION_TOLERANCE <= position <= self.position_max + POSITION_TOLERANCE:
            msg = (
                f"Invalid target position: {position} mm. Must be within the travel range of the stage from "
                f"{self.position_min} mm to {self.position_max} mm."
            )
            raise ValueError(msg)

        return min(max(position, self.position_min), self.position_max)

    def wait_for_completion(self, completed: threading.Event, timeout_s: float, task: str) -> None:
        """Wait until Kinesis reports the task as completed, the run is stopped, or the timeout expires."""
        time_start = time.time()
        while not completed.wait(0.1):
            if self.is_run_stopped():
                return

            if time.time() - time_start > timeout_s:
                msg = f"Failed to {task} within the timeout period of {timeout_s:.0f} s."
                raise TimeoutError(msg)

    """ here, convenience functions start """

    def initialize_simulations(self) -> None:
        """Initialize the Kinesis simulations, so that the simulated devices of the Kinesis Simulator can be used."""
        self.check_kinesis_imported()
        DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()
        self.simulations_initialized = True

    def uninitialize_simulations(self) -> None:
        """Uninitialize the Kinesis simulations."""
        DeviceManagerCLI.SimulationManager.Instance.UninitializeSimulations()
        self.simulations_initialized = False

    def get_position_mm(self) -> float:
        """Get the current position in mm."""
        # Convert with Decimal.ToDouble, as str() of a .NET Decimal uses the decimal separator of the Windows locale
        return float(Decimal.ToDouble(self.stage.Position))

    def set_velocity(self, velocity: float) -> None:
        """Set the velocity of the device in mm/s."""
        velocity_parameters = self.stage.GetVelocityParams()
        velocity_parameters.MaxVelocity = Decimal(velocity)
        self.stage.SetVelocityParams(velocity_parameters)

    def set_home_velocity(self, home_velocity: float) -> None:
        """Set the home velocity of the device in mm/s."""
        self.stage.SetHomingVelocity(Decimal(home_velocity))

    def start_homing(self) -> threading.Event:
        """Start homing the device without waiting and return an event that is set once homing is completed."""
        home_completed = threading.Event()
        self.stage.Home(self.create_callback(home_completed))
        return home_completed

    def move_to(self, position: float) -> threading.Event:
        """Start a movement to the absolute position in mm and return an event that is set once it is completed."""
        move_completed = threading.Event()
        self.stage.MoveTo(Decimal(position), self.create_callback(move_completed))
        return move_completed

    @staticmethod
    def create_callback(completed: threading.Event) -> Action[UInt64]:
        """Create the .NET callback that makes a Kinesis command non-blocking and sets the event once it is completed.

        Kinesis calls the callback with the id of the completed task as argument.
        """

        def on_completed(_task_id: int) -> None:
            completed.set()

        return Action[UInt64](on_completed)
