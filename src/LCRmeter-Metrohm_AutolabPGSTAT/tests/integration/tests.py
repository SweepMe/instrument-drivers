import pytest
import pysweepme


driver_name = "LCRmeter-Metrohm_AutolabPGTSTAT"
driver_path = r"/src/LCRmeter-Metrohm_AutolabPGSTAT"
port_string = "COM5"


def test_init_device() -> None:
    """Test the initialization of the device."""
    device = pysweepme.get_driver(driver_name, driver_path, port_string)
    assert device is not None


@pytest.fixture()
def setup_device() -> pysweepme.Device:
    """Set up the device for testing."""
    device = pysweepme.get_driver(driver_name, driver_path, port_string)
    yield device
    del device


def test_connect(device: pysweepme.Device) -> None:
    """Test the connection to the device."""
    device.connect()


def test_load_sdk():
    autolab_sdk_path = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\EcoChemie.Autolab.Sdk.dll"
    clr.AddReference(autolab_sdk_path)

    import EcoChemie.Autolab.Sdk as AutolabSDK

    global Instrument
    from EcoChemie.Autolab.Sdk import Instrument

