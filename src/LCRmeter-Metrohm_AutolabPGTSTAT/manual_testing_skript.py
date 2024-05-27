import clr

if __name__ == "__main__":
    # load the Autolab SDK
    autolab_sdk_path = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\EcoChemie.Autolab.Sdk.dll"
    clr.AddReference(autolab_sdk_path)

    from EcoChemie.Autolab.Sdk import Instrument

    autolab = Instrument()

    # Import adx and hardware setup file
    adx = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\Adk.x"

    # TODO: Choose correct device
    hardware_params = (
        r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA2.xml"
    )

    autolab.AutolabConnection.EmbeddedExeFileToStart = adx
    autolab.set_HardwareSetupFile(hardware_params)

    # Connect
    print("Connecting to Autolab...")
    autolab.Connect()
    print("Connected to Autolab.")

    # Check functions of Ei, Fra, Dac
    ei = autolab.Ei
    print(ei, type(ei))
    print(dir(ei))

    fra = autolab.Fra
    print(fra, type(fra))
    print(dir(fra))

    dac = autolab.Dac
    print(dac, type(dac))
    print(dir(dac))
