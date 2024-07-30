import pysweepme
import pytest

driver_name = "LCRmeter-Metrohm_AutolabPGSTAT"
driver_path = r"/src/LCRmeter-Metrohm_AutolabPGSTAT"
port_string = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA2V10.xml"
adk_path = r"C:\Program Files\Metrohm Autolab\Autolab SDK 2.1\Hardware Setup Files\Adk.x"


def test_init_device() -> None:
    """Test the initialization of the device."""
    device = pysweepme.get_driver(driver_name, driver_path, port_string)
    assert device is not None


@pytest.fixture()
def setup_device() -> pysweepme.Device:
    """Set up the device for testing."""
    device = pysweepme.get_driver(driver_name, driver_path, port_string)
    device.adk_path = adk_path
    device.hardware_setup_file = port_string

    yield device

    del device


def test_connect(device: pysweepme.Device) -> None:
    """Test the connection to the device."""
    device.connect()
