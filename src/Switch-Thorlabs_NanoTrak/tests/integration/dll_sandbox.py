from __future__ import annotations

import sys

import clr

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug, error


# Import Kinesis dll
bitness = 64 if sys.maxsize > 2**32 else 32
kinesis_path = "C:\\Program Files\\Thorlabs\\Kinesis" # if bitness == 64 else "C:\\Program Files (x86)\\Thorlabs\\Kinesis"

if kinesis_path not in sys.path:
    sys.path.insert(0, kinesis_path)


clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")
clr.AddReference("Thorlabs.MotionControl.GenericNanoTrakCLI")

# clr.AddReference("Thorlabs.MotionControl.IntegratedStepperMotorsCLI")

import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
import Thorlabs.MotionControl.GenericMotorCLI as GenericMotorCLI
import Thorlabs.MotionControl.GenericNanoTrakCLI as GenericNanoTrakCLI

DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()
DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()
device_list = DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
port_string = device_list[0]
print(f"Found device: {port_string}")

kinesis_device = GenericNanoTrakCLI.NanoTrak.CreateDevice(port_string)

