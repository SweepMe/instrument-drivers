import pytest

import pysweepme

DRIVER_PATH = r"C:\Code\instrument-drivers\src"
DRIVER_NAME = "Robot-Thorlabs_NanoTrak"


def test_get_connected_devices() -> None:
    """Test the find ports function."""
    driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH)
    assert isinstance(driver, pysweepme.EmptyDevice), "Driver should be an instance of EmptyDevice"

    connected_devices = driver.find_ports()
    print(connected_devices)
