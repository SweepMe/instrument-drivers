import clr
import sys
import time
from System import Decimal, Int32

kinesis_path = r"C:\Program Files\Thorlabs\Kinesis"
if kinesis_path not in sys.path:
    sys.path.insert(0, kinesis_path)

clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.ModularRackCLI")
clr.AddReference("Thorlabs.MotionControl.GenericMotorCLI")

from Thorlabs.MotionControl import DeviceManagerCLI, ModularRackCLI, GenericMotorCLI

DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()
device_list = DeviceManagerCLI.DeviceManagerCLI.GetDeviceList()
print(f"Found devices: {[str(serial_num) for serial_num in device_list]}")

# Replace with your actual NanoTrak module serial number
serial_number = device_list[0]  # 50842231
device_info = DeviceManagerCLI.DeviceFactory.GetDeviceInfo(serial_number)
rack = ModularRackCLI.Rack.ModularRack.CreateModularRack(device_info.GetTypeID(), serial_number)
stepper = rack[1]

rack.Connect(serial_number)
stepper.WaitForSettingsInitialized(5000)
# The polling loop requests regular status requests to the motor to ensure the program keeps track of the device.
stepper.StartPolling(250)
time.sleep(0.5)

# Enable the channel otherwise any move is ignored
stepper.EnableDevice()
time.sleep(0.5)

# continue with stepper_motor object - unclear why it works better than using stepper directly
stepper_motor = rack.GetStepperChannel(1)
motorConfiguration = stepper_motor.LoadMotorConfiguration(stepper.DeviceID)

new_position = 5
print(f"Moving to position {new_position}")
stepper_motor.MoveTo(Decimal(new_position), Int32(60000))

print(f"Current position: {stepper_motor.Position}")

stepper.StopPolling()
rack.Disconnect(True)

# Try to reconnect to verify that the rack can be reconnected after disconnect
time.sleep(5)
rack.Connect(serial_number)  # --> this raises an exception
