from __future__ import annotations

import time
import sys
import clr

from System import Decimal


# Import Kinesis dll
bitness = 64 if sys.maxsize > 2**32 else 32
kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis" # if bitness == 64 else "C:\\Program Files (x86)\\Thorlabs\\Kinesis"

if kinesis_path not in sys.path:
    sys.path.insert(0, kinesis_path)

clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
clr.AddReference("Thorlabs.MotionControl.IntegratedStepperMotorsCLI")

import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
# from Thorlabs.MotionControl.GenericMotorCLI import IGenericAdvancedMotor
# from Thorlabs.MotionControl.GenericMotorCLI.ControlParameters import VelocityParameters
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import LongTravelStage#, ThorlabsIntegratedStepperMotorSettings

# DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()
DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()

device_list = DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
print(f"Found devices: {[str(serial_num) for serial_num in device_list]}")
port_string = device_list[0]
print(f"Found device: {port_string}")

device = LongTravelStage.CreateLongTravelStage(port_string)
time.sleep(1)
device.Connect(port_string)

time.sleep(2)

# Initialize settings
if not device.IsSettingsInitialized():
    try:
        device.WaitForSettingsInitialized(5000)
    except Exception as e:
        print(f"Settings failed to initialize: {e}")


device.StartPolling(250)
time.sleep(0.5)
device.EnableDevice()
time.sleep(0.5)

# Load motor configuration
motor_config = device.LoadMotorConfiguration(port_string)
current_settings = device.MotorDeviceSettings

position = Decimal(60)
device.MoveTo(position, 60000)

status = device.Status
# print(status.Position, type(status.Position))

conv = device.AdvancedMotorLimits.UnitConverter
pos = float(str(conv.DeviceUnitToReal(Decimal(status.Position), conv.UnitType.Length)))
print(f"Position: {pos} mm")

