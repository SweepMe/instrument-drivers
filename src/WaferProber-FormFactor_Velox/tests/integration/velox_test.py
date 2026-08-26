
import pytest

import pysweepme

DRIVER_PATH = r"C:\Code\instrument-drivers\src"
DRIVER_NAME = "WaferProber-FormFactor_Velox"
PORT = "localhost"  # Velox running on this computer

PROBEPLAN_PATH = r"C:\Users\Public\Documents\Velox\MyProject.map"

# Velox reports the die index in micrometres; a pitch in mm must land well below this.
MAX_PLAUSIBLE_PITCH_MM = 1000.0


def test_load_velox() -> None:
    driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, PORT)
    driver.connect()
    driver.disconnect()

@pytest.fixture()
def driver() -> pysweepme.EmptyDevice:
    """Load Velox driver, connect to the Velox software, and close connection in the end."""
    velox_driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, PORT)
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


def test_get_wafer_geometry(driver: pysweepme.EmptyDevice) -> None:
    """Geometry of the loaded map is reported instead of having to be typed in by hand.

    Values are those of the wafer currently loaded in Velox, so only the shape and the units are
    asserted here — not the numbers of one particular project.
    """
    geometry = driver.get_wafer_geometry()

    assert set(geometry) == {
        "diameter_mm", "pitch_x_mm", "pitch_y_mm", "columns", "rows",
        "map_type", "notch", "flat_length_mm", "origin",
    }
    assert geometry["map_type"] in ("wafer", "rectangle")

    assert 0.0 < geometry["pitch_x_mm"] < MAX_PLAUSIBLE_PITCH_MM
    assert 0.0 < geometry["pitch_y_mm"] < MAX_PLAUSIBLE_PITCH_MM
    assert geometry["columns"] > 0
    assert geometry["rows"] > 0

    if geometry["map_type"] == "wafer":
        assert geometry["diameter_mm"] > 0.0
        assert geometry["notch"] in ("down", "up", "left", "right")

    assert geometry["origin"] in ("upper_left", "upper_right", "lower_left", "lower_right")


def test_get_wafer_geometry_leaves_connection_as_found() -> None:
    """The geometry query must not close a session that somebody else opened."""
    velox_driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, PORT)

    # Nothing open: the call connects and hands the connection back.
    velox_driver.get_wafer_geometry()
    assert velox_driver.msg_server is None

    # Already open: the call must leave that session untouched.
    velox_driver.connect_to_velox()
    session = velox_driver.msg_server
    velox_driver.get_wafer_geometry()
    assert velox_driver.msg_server is session
    velox_driver.disconnect_from_velox()


def test_port_string_without_selection_is_reported_clearly() -> None:
    """An empty Port must name the field to fix, not surface a raw socket error."""
    velox_driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH)
    velox_driver.handle_port_string("")

    with pytest.raises(Exception, match="No port selected"):
        velox_driver.connect_to_velox()
