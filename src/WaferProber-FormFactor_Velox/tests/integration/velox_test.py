
import pytest

import pysweepme

DRIVER_PATH = r"C:\Code\SweepMe!\Devices_development"
DRIVER_NAME = "WaferProber-FormFactor_VeloxSDK"

PROBEPLAN_PATH = r"C:\Users\Public\Documents\Velox\MyProject.map"


def test_load_velox() -> None:
    driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH)
    driver.connect()
    driver.disconnect()

@pytest.fixture()
def driver() -> pysweepme.EmptyDevice:
    """Load Velox driver, connect to the Velox software, and close connection in the end."""
    velox_driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH)
    velox_driver.connect()
    yield velox_driver
    velox_driver.disconnect()


def test_get_probeplan(driver: pysweepme.EmptyDevice) -> None:
    """Test get_probeplan function."""
    wafers, dies, subsites = driver.get_probeplan(PROBEPLAN_PATH)
    assert isinstance(wafers, list)
    assert isinstance(dies, list)
    assert dies[-1] == "0,8"

    assert isinstance(subsites, list)
    assert subsites == ["0", "1", "2"]


def test_positioning(driver: pysweepme.EmptyDevice) -> None:
    """Test query of current position and moving."""
    driver.get_probeplan(PROBEPLAN_PATH)

    current_wafer = driver.get_current_wafer()
    assert isinstance(current_wafer, str)

    driver.step_to_home()

    die_x, die_y, subsite = driver.get_current_position()

    assert die_x == 2
    assert die_y == 4
    assert subsite == -1

    assert driver.get_current_die() == "2,4"
    assert driver.get_current_subsite() == "-1"

    driver.step_to_die("3,5", "1")
    assert driver.get_current_die() == "3,5"
    assert driver.get_current_subsite() == "1"
