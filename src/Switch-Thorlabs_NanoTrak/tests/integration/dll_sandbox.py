from __future__ import annotations

import time

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
clr.AddReference("Thorlabs.MotionControl.GenericNanoTrakCLI")
clr.AddReference("Thorlabs.MotionControl.Benchtop.NanoTrakCLI")
clr.AddReference("Thorlabs.MotionControl.TCube.NanoTrakCLI")
clr.AddReference("Thorlabs.MotionControl.KCube.NanoTrakCLI")

import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
import Thorlabs.MotionControl.GenericNanoTrakCLI as GenericNanoTrakCLI




DeviceManagerCLI.SimulationManager.Instance.InitializeSimulations()
DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()

import Thorlabs.MotionControl.Benchtop.NanoTrakCLI as BenchtopNanoTrakCLI
benchtop_prefix = BenchtopNanoTrakCLI.BenchtopNanoTrak.DevicePrefix
# print(f"Benchtop NanoTrak Device Prefix: {benchtop_prefix}, {type(benchtop_prefix)}")

import Thorlabs.MotionControl.TCube.NanoTrakCLI as TCubeNanoTrakCLI
tcube_prefix = TCubeNanoTrakCLI.TCubeNanoTrak.DevicePrefix
# print(f"TCube NanoTrak Device Prefix: {tcube_prefix}, {type(tcube_prefix)}")

import Thorlabs.MotionControl.KCube.NanoTrakCLI as asf
ckcube_prefix = asf.KCubeNanoTrak.DevicePrefix
# print(f"CKCube NanoTrak Device Prefix: {ckcube_prefix}, {type(ckcube_prefix)}")


device_list = DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
print(f"Found devices: {[str(serial_num) for serial_num in device_list]}")
port_string = device_list[0]
print(f"Found device: {port_string}")

device = BenchtopNanoTrakCLI.BenchtopNanoTrak.CreateBenchtopNanoTrak(port_string)
time.sleep(1)
device.Connect(port_string)

time.sleep(5)

device.StartPolling(250)
time.sleep(0.5)
device.EnableDevice()
time.sleep(0.5)

print(device.GetDeviceInfo())

device.SetMode(GenericNanoTrakCLI.NanoTrakStatus.OperatingModes.Tracking)


x = 5
y = 2

position = GenericNanoTrakCLI.HVPosition(x, y)
device.SetCircleHomePosition(position)
device.HomeCircle()

# TIAReading = device.GetReading()
Position = device.GetCirclePosition()
print(f"Position: {Position.HPosition}, {Position.VPosition}")

# kinesis_device = GenericNanoTrakCLI.NanoTrak.CreateDevice(port_string)

# Which command to use to instantiate the device?
# example from other driver:
# import Thorlabs.MotionControl.IntegratedStepperMotorsCLI as IntegratedStepperMotorsCLI
# kinesis_device = IntegratedStepperMotorsCLI.CageRotator.CreateDevice(serial_num)

