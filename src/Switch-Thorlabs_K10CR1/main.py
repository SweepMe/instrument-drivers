# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023 SweepMe! GmbH  (sweep-me.net)
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

# SweepMe! device class
# Module: Switch
# Device: Thorlabs Kinesis K10CR1

import sys
import time

import clr
from pysweepme.EmptyDeviceClass import EmptyDevice

clr.AddReference("System")
from System import Decimal, Int32, UInt64

bitness = 64 if sys.maxsize > 2**32 else 32
if bitness == 64:
    kinesis_path = 'C:\\Program Files\\Thorlabs\\Kinesis'
elif bitness == 32:
    kinesis_path = 'C:\\Program Files (x86)\\Thorlabs\\Kinesis'
if kinesis_path not in sys.path:
    sys.path.insert(0, kinesis_path)

DEBUG = False


def add_dotnet_references():
    """Importing Kinesis .NET dll"""

    clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
    clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
    clr.AddReference("Thorlabs.MotionControl.IntegratedStepperMotorsCLI")

    import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
    import Thorlabs.MotionControl.GenericMotorCLI as GenericMotorCLI
    import Thorlabs.MotionControl.IntegratedStepperMotorsCLI as IntegratedStepperMotorsCLI

    return DeviceManagerCLI, IntegratedStepperMotorsCLI, GenericMotorCLI


class Device(EmptyDevice):
    description = """<p>Driver to control the Thorlabs Kinesis K10CR1 rotation stage</p>
        <p><strong>Requirements</strong>:</p>
        <ul>
        <li>Please install the Thorlabs kinesis 32-bit library (Default SweepMe! bitness)
          <a href="https://www.thorlabs.com/newgrouppage9.cfm?objectgroup_id=10285">download page</a>
           before running</li>
        </ul>
        <p><strong>Features</strong></p>
        <ul>
        <li>supports, homing, absolute moves and position sweeps</li>
        <li>supports move interruption if a SweepMe! run is stopped</li>
        <li>config options below</li>
        </ul>
        <p><strong>Usage:</strong></p>
        <p>The K10CR1 operates in &deg; units. Homing takes the device to 0, after which the device
          positions will be correct.</p>
        <ul>
        <li>Go home at start: perform a homing operation <em>once</em> at the start of the SweepMe!
          run.</li>
        <li>Go home at end: perform a homing operation <em>after each measurement branch</em>
          the stage is involved in</li>
        <li>Timeout: max move time. After</li>
        <li>Acceleration: move speed increase during a move in &deg;/s/s</li>
        <li>Max velocity: max speed during a move in &deg;/s</li>
        <li>Backlash correction: in &deg; for negative moves</li>
        <li>Kinesis simulator: enable use of devices simulated by the 'Kinesis Simulator'
          software (testing). A run is needed before find_ports finds simulated devices.</li>
        <li>Note the SweepMe! UI may become unresponsive if the Apply button is used with large
         moves</li>
        </ul>
        <p>&nbsp;</p>
    """
    dotnet_added = False

    def __init__(self):
        EmptyDevice.__init__(self)

        self.DeviceManagerCLI = None
        self.GenericMotorCLI = None
        self.IntegratedStepperMotorsCLI = None

        self.kinesis_device = None
        self.shortname = "K10CR1"
        self.is_simulation = False

    def find_ports(self):
        """
        This function returns the serial number of all connected devices in a list, 
        if no device is connected, None will be returned.
        Returns:
            list[serial numbers]
        """
        if not self.dotnet_added:
            self.DeviceManagerCLI, self.IntegratedStepperMotorsCLI, self.GenericMotorCLI = add_dotnet_references(
            )

        device_list = self.list_devices()

        # Searching for simulated devices if there are no real devices found
        if len(device_list) == 0:
            self.DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()
            device_list = self.list_devices()
            self.DeviceManagerCLI.SimulationManager.Instance.UninitializeSimulations()

        if len(device_list) == 0:
            device_list = ["No devices found!"]

        return device_list

    def set_GUIparameter(self):

        gui_parameter = {
            "SweepMode": ["Position"],
            "Go home at start": True,
            "Go home at end": False,
            " ": None,
            "Timeout in s": 30.0,
            "Acceleration": 20.0,
            "Max velocity": 10.0,
            "Backlash correction": 0.1,
            "": None,
            "Kinesis simulator": False,
        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        # self.sweepmode = parameter["SweepMode"]

        self.serial_num = parameter["Port"]
        self.is_simulation = parameter["Kinesis simulator"]
        self.home_on_start = parameter["Go home at start"]
        self.home_on_end = parameter["Go home at end"]
        self.timeout_ms = float(parameter["Timeout in s"]) * 1000

        self.acceleration = float(parameter["Acceleration"])
        self.max_velocity = float(parameter["Max velocity"])
        self.backlash_correction = float(parameter["Backlash correction"])

        self.variables = ["Position"]
        self.units = [""]  # make sure that you have as many units as you have variables
        self.plottype = [True]  # True to plot data, corresponding to self.variables
        self.savetype = [True]  # True to save data, corresponding to self.variables
        self.position = None

    # semantic standard functions called during a measurement start here #

    def connect(self):

        if self.serial_num == "No devices found!":
            msg = "No device was found. Please use 'Find ports' and select a serial number."
            raise ValueError(msg)
    
        if DEBUG:
            print("connecting to K10CR1")
        if not self.dotnet_added:
            self.DeviceManagerCLI, self.IntegratedStepperMotorsCLI, self.GenericMotorCLI = add_dotnet_references(
            )

        if self.is_simulation:
            self.DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()

        device_list = self.list_devices()

        if self.serial_num not in device_list:
            msg = f"Device {self.serial_num} not found in SN l {device_list}"
            raise ValueError(msg)

        # we need to check the pythonnet/clr version because there was a breaking change with 3.0.0 that leads
        # to a different interface handling. A fix for now is to add __implementation__ to the CreateDevice method
        # Because of the clr version dependent handling, the driver still works with SweepMe! 1.5.5 or python
        # environments where clr<3.0.0 is used.
        clr_version = tuple(map(int, clr.__version__.split(".")))
        if clr_version < (3, 0, 0):
            self.kinesis_device = self.IntegratedStepperMotorsCLI.CageRotator.CreateDevice(self.serial_num)
        else:
            self.kinesis_device = (self.IntegratedStepperMotorsCLI.CageRotator.CreateDevice(self.serial_num).
                                   __implementation__)

        self.kinesis_device.ClearDeviceExceptions()

        start_time = time.time()
        while not self.kinesis_device.IsConnected:
            try:
                self.kinesis_device.Connect(self.serial_num)
                time.sleep(0.2)
            except self.DeviceManagerCLI.DeviceNotReadyException:
                pass
            if time.time() - start_time > 5:
                raise TimeoutError(f"Could not connect to {self.serial_num}")

        self.kinesis_device_info = self.kinesis_device.GetDeviceInfo()
        
        if DEBUG:
            msg = f"Connected to K10CR Device {self.kinesis_device_info.Name} "
            msg += f"with SN:{self.kinesis_device_info.SerialNumber}"
            print(msg)
            
    def disconnect(self):
        if not self.kinesis_device:
            return

        self.kinesis_device.StopImmediate()
        self.wait(timeout_ms=500, allow_user_stop=False)

        self.kinesis_device.StopPolling()
        # disconnect and disable are buggy but shutdown works
        self.kinesis_device.ShutDown()
        if self.is_simulation:
            self.DeviceManagerCLI.SimulationManager.Instance.UninitializeSimulations()

    def initialize(self):

        if not self.kinesis_device.IsSettingsInitialized():
            self.kinesis_device.WaitForSettingsInitialized(10000)  # ms

        polling_rate = 100
        self.kinesis_device.StartPolling(polling_rate)

        self.enable_device(timeout=20)
        self.kinesis_device.LoadMotorConfiguration(self.serial_num)
        self.enable_device(timeout=2)

        needs_homing = self.kinesis_device.NeedsHoming

        if needs_homing or self.home_on_start:
            self.kinesis_device.Home(Int32(0))
            self.wait(timeout_ms=30e3, command="home")
            
            if DEBUG:
                print("K10CR1 homed")

            # self.move(1)
            # self.move(359)
            # self.move(0)

    def configure(self):
        # the xml config file from Thorlabs motion is wrong and will not reject bad values
        # this leads to erratic movements/skipping movements
        if self.max_velocity > 10:
            raise ValueError("max velocity cannot not exceed 10d/s")
        if self.acceleration > 20:
            raise ValueError("max acceleration cannot not exceed 20d/s/s")

        max_v = Decimal(self.max_velocity)
        accel = Decimal(self.acceleration)
        self.kinesis_device.SetVelocityParams(max_v, accel)
        self.kinesis_device.SetBacklash(Decimal(self.backlash_correction))

    def unconfigure(self):
        if self.home_on_end:
            self.kinesis_device.Home(Int32(0))
            self.wait(timeout_ms=30e3, command="home")

    # the following functions are called for each measurement point #

    def apply(self):
        """ applies the new sweep value """

        target_position = float(self.value)
        self.move(target_position)

    def call(self):
        return self.get_position()
        
    # convenience functions start here #
    
    def enable_device(self, timeout):
        start_time = time.time()
        while not self.kinesis_device.IsEnabled:
            try:
                self.kinesis_device.Enable()
                time.sleep(0.2)
                print(self.kinesis_device.IsEnabled)
            except self.DeviceManagerCLI.DeviceNotReadyException:
                pass
            if time.time() - start_time > timeout:
                raise TimeoutError("Could not enabled device")
    
    def get_position(self):
        """get the current rotator position"""
        # polling means request not needed
        decimal_pos = self.kinesis_device.DevicePosition
        return float(Decimal.ToDouble(decimal_pos))
        
    def move(self, position):
        """absolute move"""

        decimal_pos = Decimal(position)

        # use of modulo 360 if needed as the stage only accepts values between 0° and 360°
        # decimal_pos = Decimal(position % 360.0)

        self.kinesis_device.MoveTo(decimal_pos, Int32(0))
        self.wait(timeout_ms=self.timeout_ms, command="move")

        # self.kinesis_device.MoveTo(decimal_pos, move_call_back)
        # self.kinesis_device.Wait(Int32(timeout_ms))

        if DEBUG:
            position = self.get_position()
            print(f"Move complete. New position is {position}")

    def wait(self, timeout_ms, command="unknown command", allow_user_stop=True):
        """ wait loop till device not busy"""
        start_time = time.time()
        time.sleep(0.1)  # wait for IsDeviceBusy to update
        while self.kinesis_device.IsDeviceBusy:
            time.sleep(0.1)
            if hasattr(self, "is_run_stopped") and self.is_run_stopped() and allow_user_stop:
                self.kinesis_device.StopImmediate()
            if time.time() - start_time > timeout_ms / 1000:
                self.kinesis_device.StopImmediate()
                raise TimeoutError(f"{command} timed out after {timeout_ms/1000}s")

        return None

    def list_devices(self):
        """
        Lists all devices

        Bug: Once Simulation mode is switched on GetDeviceList will also find simulated devices even though simulation
        mode is uninitialized.

        Returns: list[str]
        """


        self.DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()
        device_list = self.DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
        device_list = [str(ser_n) for ser_n in device_list]
        return device_list