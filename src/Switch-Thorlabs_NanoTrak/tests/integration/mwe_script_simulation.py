import clr
import sys
import time

kinesis_path = r"C:\Program Files\Thorlabs\Kinesis"
if kinesis_path not in sys.path:
    sys.path.insert(0, kinesis_path)

clr.AddReference("Thorlabs.MotionControl.DeviceManagerCLI")
clr.AddReference("Thorlabs.MotionControl.ModularRackCLI")
import Thorlabs.MotionControl.DeviceManagerCLI as DeviceManagerCLI
import Thorlabs.MotionControl.ModularRackCLI as ModularRackCLI
import Thorlabs.MotionControl.GenericNanoTrakCLI as GenericNanoTrakCLI

clr.AddReference("Thorlabs.MotionControl.Benchtop.NanoTrakCLI")
import Thorlabs.MotionControl.Benchtop.NanoTrakCLI as BenchtopNanoTrakCLI
kinesis_client = BenchtopNanoTrakCLI

# Build device list
DeviceManagerCLI.DeviceManagerCLI.BuildDeviceList()

# Replace with your actual NanoTrak module serial number
serial_number = "22000001"

# # Get device info and create the rack object
# DeviceFactory = DeviceManagerCLI.DeviceFactory
# deviceInfo = DeviceFactory.GetDeviceInfo(serialNo)
# typeID = deviceInfo.GetTypeID()
# ModularRack = ModularRackCLI.Rack.ModularRack
# rack = ModularRack.CreateModularRack(typeID, serialNo)
#
# # Get the device channel (NanoTrak has 1 channel)
# device = rack[1]

device = kinesis_client.BenchtopNanoTrak.CreateBenchtopNanoTrak(serial_number)

# Connect to the device
# device.Connect(serial_number)
print(f"Connected to device {serial_number}")

# Wait for device settings to initialize (timeout 5000 ms)
if not device.IsSettingsInitialized():
    try:
        device.WaitForSettingsInitialized(5000)
        print("Settings initialized.")
    except Exception as e:
        print("Settings failed to initialize:", e)

# Start polling
device.StartPolling(250)
time.sleep(0.5)  # Wait for polling to start

# Enable the device
device.EnableDevice()
time.sleep(0.5)  # Wait for device to be enabled

print("Device is initialized, polling, and enabled.")

# Add references for Benchtop device settings
clr.AddReference("Thorlabs.MotionControl.Benchtop.PiezoCLI")
clr.AddReference("Thorlabs.MotionControl.Benchtop.StepperMotorCLI")
clr.AddReference("Thorlabs.MotionControl.Benchtop.NanoTrakCLI")
import Thorlabs.MotionControl.Benchtop.PiezoCLI as BenchtopPiezoCLI
import Thorlabs.MotionControl.Benchtop.StepperMotorCLI as BenchtopStepperCLI
import Thorlabs.MotionControl.Benchtop.NanoTrakCLI as BenchtopNanoTrakCLI

# Check the device type in bay 1
bay = 1
device_type = rack.BayDeviceType(bay)
print(device_type)
ChannelDefinitions = ModularRackCLI.Rack.ChannelDefinitions

if device_type == ChannelDefinitions.ModularRackDevices.ModularRackStepperMotor:
    stepperMotor = rack.GetStepperChannel(bay)
    if stepperMotor is not None:
        motorConfiguration = stepperMotor.LoadMotorConfiguration(stepperMotor.DeviceID)
        currentDeviceSettings = stepperMotor.MotorDeviceSettings
        print("Homing device")
        stepperMotor.Home(60000)
        print("Device Homed")
        position = 5.0
        print(f"Moving Device to {position}")
        stepperMotor.MoveTo(position, 60000)
        print(f"Device Moved to {stepperMotor.Position}")

elif device_type == ChannelDefinitions.ModularRackDevices.ModularRackNanoTrak:
    nanoTrak = rack.GetNanoTrakChannel(bay)
    if nanoTrak is not None:
        DeviceSettingsUseOptionType = DeviceManagerCLI.DeviceConfiguration.DeviceSettingsUseOptionType
        nanoTrakConfiguration = nanoTrak.GetNanoTrakConfiguration(serialNo, DeviceSettingsUseOptionType.UseConfiguredSettings)
        currentDeviceSettings = nanoTrak.NanoTrakDeviceSettings
        nanoTrak.SetSettings(currentDeviceSettings, False)
        print(nanoTrak.GetCircleDiameter())
        print(nanoTrak.GetFeedbackSource())
        nanoTrak.GetSettings(currentDeviceSettings)
        NanoTrakStatusBase = GenericNanoTrakCLI.NanoTrakStatusBase
        NanoTrakFeedbackSource = GenericNanoTrakCLI.Settings.IOSettingsSettings.FeedbackSources
        nanoTrak.SetFeedbackSource(NanoTrakFeedbackSource.BNC_10V)
        nanoTrak.SetMode(NanoTrakStatusBase.OperatingModes.Tracking)
        print("Device set to Tracking mode.")
        HVPosition = GenericNanoTrakCLI.HVPosition
        # Loop to set circle diameter from 1 to 3 in increments of 0.5
        for diameter in [round(x * 0.5, 2) for x in range(2, 7)]:  # 1.0, 1.5, 2.0, 2.5, 3.0
            nanoTrak.SetCircleDiameter(diameter)
            print(f"Set circle diameter to {diameter}")
            time.sleep(0.5)  # Optional: wait for device to update
        nanoTrak.SetCircleHomePosition(HVPosition(5, 5))
        nanoTrak.HomeCircle()
        nanoTrak.SetMode(NanoTrakStatusBase.OperatingModes.Latch)
        TIAOddOrEven = GenericNanoTrakCLI.TIAOddOrEven
        TIARangeModes = GenericNanoTrakCLI.TIARangeModes
        nanoTrak.SetTIARangeMode(TIARangeModes.AutoRangeAtSelected, TIAOddOrEven.All)
        time.sleep(0.5)
        reading = nanoTrak.GetReading()
        nanoTrak.SetMode(NanoTrakStatusBase.OperatingModes.Latch)
        print("NanoTrak voltage set to", reading)
        print("Absolute Reading:", reading.AbsoluteReading)
        print("Relative Reading:", reading.RelativeReading)
        print("Selected TIA Range:", reading.SelectedRange)
        print("UnderOrOverRead:", reading.UnderOrOverRead)


# Stop polling and disconnect
device.StopPolling()
device.DisableDevice()
rack.Disconnect(True)
print("Device stopped and rack disconnected.")
