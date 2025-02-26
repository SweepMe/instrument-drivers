import time

import pytest

import pysweepme

DRIVER_PATH = r"C:\Code\SweepMe!\Devices_development"
DRIVER_NAME = "Temperature-FormFactor_Velox"


def test_load_velox() -> None:
    driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH)
    driver.connect()
    driver.disconnect()


@pytest.fixture()
def driver() -> pysweepme.EmptyDevice:
    """Load Velox driver, connect to the Velox software, and close connection in the end."""
    velox_driver = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH)
    velox_driver.get_GUIparameter(
        {
            "SweepMode": "Temperature",
            "TemperatureUnit": "C",
            "MeasureT": True,
            "Sensor": "Main",
            "Hold mode": True,
            "Soak mode": "Fixed Wafer",
            "Soak time": 60,
        },
    )
    velox_driver.connect()
    yield velox_driver
    velox_driver.disconnect()


def test_get_and_set_temperature(driver: pysweepme.EmptyDevice) -> None:
    """Test getter and setter for temperature."""
    driver.set_heater_soak(0)

    temperature = driver.get_temperature()
    assert isinstance(temperature, float)

    target_temperature = 100.0
    driver.set_target_temperature_and_start(target_temperature)

    new_target_temperature = driver.get_target_temperature()
    assert new_target_temperature == target_temperature


def test_read_status(driver: pysweepme.EmptyDevice) -> None:
    """Test reading of temperature chuck status."""
    current_temperature = driver.get_temperature()

    # Heating
    heating_temperature = current_temperature + 20
    driver.set_target_temperature_and_start(heating_temperature)
    time.sleep(1)
    status = driver.get_temperature_status()
    assert status.value == 1  # Heating

    # Cooling
    cooling_temperature = current_temperature - 20
    driver.set_target_temperature_and_start(cooling_temperature)
    time.sleep(1)
    status = driver.get_temperature_status()
    assert status.value == 2  # Heating


def test_measuring_while_heating(driver: pysweepme.EmptyDevice) -> None:
    """Test measuring the temperature while heating."""
    current_temperature = driver.get_temperature()

    # Heating
    heating_temperature = current_temperature + 20
    driver.set_target_temperature_and_start(heating_temperature)
    time.sleep(1)

    while current_temperature < heating_temperature:
        current_temperature = driver.get_temperature()
        time.sleep(1)
        print(current_temperature)

    # status = driver.get_temperature_status()
    # assert status.value == 1  # Heating
