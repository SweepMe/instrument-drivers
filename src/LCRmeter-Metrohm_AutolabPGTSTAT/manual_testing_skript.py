import clr
import time


def example_script(autolab):
    ei = autolab.Ei
    fra = autolab.Fra

    fra.Frequency = 100000
    fra.Amplitude = 0.01
    fra.WaveType = fra.WaveType.Sine
    fra.MinimumIntegrationCycles = 1
    fra.MinimumIntegrationTime = 0.125

    ei.CurrentRange = ei.EICurrentRange.CR10_1mA
    ei.Bandwidth = ei.EIBandwidth.High_Speed
    ei.Setpoint = 0
    ei.EnableDsgInput = True
    ei.CellOnOff = ei.EICellOnOff.On

    fra.Start()
    # time.sleep(1)

    # fra.Start()

    ztotal = fra.Modulus[0]
    phase = fra.Phase[0]
    zreal = fra.Real[0]
    zimag = fra.Imaginary[0]

    print(fra.Phase)

    # print(f"Ztotal: {ztotal}, Phase: {phase}, Zreal: {zreal}, Zimag: {zimag}")

    ei.CellOnOff = ei.EICellOnOff.Off
    ei.EnableDsgInput = False
    # autolab.SwitchFraOff()
    fra.Finalize()

    autolab.Disconnect()


if __name__ == "__main__":
    # load the Autolab SDK
    autolab_sdk_path = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\EcoChemie.Autolab.Sdk.dll"
    clr.AddReference(autolab_sdk_path)

    from EcoChemie.Autolab.Sdk import Instrument

    autolab = Instrument()

    # Import adx and hardware setup file
    adx = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\Adk.x"

    hardware_params = (
        # r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA2.xml"
        r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\PGSTAT302N\HardwareSetup.AUT83940.xml"
    )

    autolab.AutolabConnection.EmbeddedExeFileToStart = adx
    autolab.set_HardwareSetupFile(hardware_params)

    # Connect
    print("Connecting to Autolab...")
    autolab.Connect()
    print("Connected to Autolab.")

    Fra = autolab.Fra
    Ei = autolab.Ei

    # print(dir(Instrument))

    # Fra.Frequency = 100000
    # time.sleep(1)
    # print(f"Frequency: {Fra.Frequency}")

    # print(Ei.CurrentRange.GetNames(Ei.EICurrentRange))

    example_script(autolab)
    # fra = autolab.Fra
    # print(help(fra.Start))

