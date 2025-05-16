import os
import pytest

import pysweepme

# use the system variable SWEEPME_DRIVERS_REPO as path
DRIVER_REPO = os.getenv("SWEEPME_DRIVERS_REPO")
DRIVER_NAME = "SMU-iseg_SHR"

# Update depending on the connected device
PORT = "TCPIP0::192.168.178.30::10001::SOCKET"


@pytest.fixture()
def driver() -> pysweepme.EmptyDevice:
    """Load iseg SHR driver, connect to the device, and close connection in the end."""
    shr_driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_REPO, port_string=PORT)
    shr_driver.get_GUIparameter(
        {
            "SweepMode": "Voltage in V",
            "Channel": "0",
            "Average": 1,
            "Speed": 100,
            "Range": "2kV/4mA",
            "RangeVoltage": "Auto",
            "Port": PORT,
        },
    )
    shr_driver.connect()
    yield shr_driver
    shr_driver.disconnect()


def test_tcpip_communication(driver: pysweepme.EmptyDevice) -> None:
    """Test communication via TCP/IP."""
    ret = driver.get_identification()
    assert ret.startswith("iseg Spezialelektronik GmbH,SR")

    driver.reset()
    # driver.set_polarity("p")
    driver.voltage_on()
    driver.set_voltage(10)

