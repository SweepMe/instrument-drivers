import clr


def load_autolab_sdk(sdk_path: str) -> None:
    """Load the Autolab SDK from the specified path."""
    clr.AddReference(sdk_path)

    global AutolabSDK
    import EcoChemie.Autolab.Sdk as AutolabSDK

    print(dir(AutolabSDK))
    sdk = AutolabSDK
    print(sdk.GetInstruments())

    global Instrument
    from EcoChemie.Autolab.Sdk import Instrument


def get_hardware_setup_file(device: str) -> str:
    """Generate the path to the hardware setup file for the specified device."""
    folder = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files"

    setup_files = {
        "AutolabIMP": "HardwareSetup.xml",
        "M101": "HardwareSetup.xml",
        "PGSTAT10": "HardwareSetup.FRA2.xml",
        "PGSTAT12": "HardwareSetup.xml",  # has both versions
        "PGSTAT20": "HardwareSetup.xml",  # has both versions
        "PGSTAT30": "HardwareSetup.xml",  # has both versions
        "PGSTAT100": "HardwareSetup.xml",  # has multiple versions
        "PGSTAT100N": "HardwareSetup.xml",
        "PGSTAT101": "HardwareSetup.xml",
        "PGSTAT128N": "HardwareSetup.xml",  # has multiple versions
        "PGSTAT204": "HardwareSetup.xml",  # has multiple versions
        "PGSTAT302": "HardwareSetup.xml",  # has multiple versions
        "PGSTAT302F": "HardwareSetup.xml",  # has multiple versions
        "PGSTAT302N": "HardwareSetup.xml",  # has multiple versions
        "uAutolabII": "HardwareSetup.xml",
        "uAutolabIII": "HardwareSetup.xml",
    }

    if device not in setup_files:
        msg = f"Device '{device}' is not supported."
        raise ValueError(msg)

    return f"{folder}\\{setup_files[device]}\\HardwareSetup.FRA2.xml"


# print("AutolabSDK Module Attributes and Methods:")
# print(dir(AutolabSDK.Instrument.Fra))
#
# # Get help documentation for the AutolabSDK module
# print("\nAutolabSDK Module Documentation:")
# help(AutolabSDK)


if __name__ == "__main__":
    autolab_sdk_path = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\EcoChemie.Autolab.Sdk.dll"
    load_autolab_sdk(autolab_sdk_path)

    autolab = Instrument()

    adx = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\Adk.x"
    hardware_params = (
        r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA2.xml"
    )

    autolab.AutolabConnection.EmbeddedExeFileToStart = adx
    autolab.set_HardwareSetupFile(hardware_params)

    # print(help(autolab))
    # print(autolab.Ei)

    # autolab.Connect()
