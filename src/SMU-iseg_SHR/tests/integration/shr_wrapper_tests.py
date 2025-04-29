import os
import pytest

import pysweepme

# use the system variable SWEEPME_DRIVERS_REPO as path
DRIVER_REPO = os.getenv("SWEEPME_DRIVERS_REPO")
DRIVER_NAME = "SMU-iseg_SHR"

# Update depending on the connected device
PORT = "COM5"


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


def _test_command(driver: pysweepme.EmptyDevice, command: str, parameter: any = None) -> None:
    """Test the command with the given parameters."""
    assert hasattr(driver, command), f"Driver does not have command: {command}"
    func = getattr(driver, command)
    assert callable(func), f"{command} is not callable"

    # Test the commands
    try:
        if parameter is not None:
            func(parameter)
        else:
            func()
    except Exception as e:
        pytest.fail(f"Command {command} failed with parameter {parameter}: {e}")


def test_channel_voltage_commands(driver: pysweepme.EmptyDevice) -> None:
    """Test the channel dependent voltage commands on page 33."""
    command_parameters = {
        "set_voltage": 2,
        "voltage_on": None,
        "voltage_off": None,
        "voltage_emergency_off": None,
        "voltage_emergency_clear": None,
        "set_voltage_bounds": 10,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)

def test_channel_current_commands(driver: pysweepme.EmptyDevice) -> None:
    """Test the channel dependent current commands on page 33."""
    command_parameters = {
        "set_current": 2,
        "set_current_bounds": 10,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)


def test_channel_event_commands(driver: pysweepme.EmptyDevice) -> None:
    """Test the channel dependent event commands on page 33."""
    command_parameters = {
        "clear_event": None,
        "clear_event_mask": 32,
        "set_event_mask": 65535,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)


def test_channel_configuration(driver: pysweepme.EmptyDevice) -> None:
    """Test the channel dependent configuration commands on page 34."""
    command_parameters = {
        "set_trip_timeout": 250,
        "get_trip_timeout": None,
        "set_trip_action": 0,
        "get_trip_action": None,
        "set_inhibit_action": 0,
        "get_inhibit_action": None,
        "set_output_mode": 1,  # Might fail depending on if device supports this mode
        "get_output_mode": None,
        "get_supported_output_modes": None,
        "set_output_polarity": "n",
        "get_output_polarity": None,
        "get_supported_output_polarities": None,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)


def test_channel_read(driver: pysweepme.EmptyDevice) -> None:
    """Test the channel dependent read commands on page 34-35."""
    command_parameters = {
        "get_voltage_set": None,
        "get_voltage_limit": None,
        "get_voltage_nominal": None,
        "get_voltage_mode": None,
        "get_supported_voltage_modes": None,
        "get_voltage_bounds": None,
        "get_voltage_on": None,
        "get_voltage_emergency": None,

        "get_current_set": None,
        "get_current_limit": None,
        "get_current_nominal": None,
        "get_current_mode": None,
        "get_supported_current_modes": None,
        "get_current_bounds": None,

        "get_voltage_ramp_speed": None,
        "get_voltage_ramp_speed_minimum": None,
        "get_voltage_ramp_speed_maximum": None,
        "get_current_ramp_speed": None,
        "get_current_ramp_speed_minimum": None,
        "get_current_ramp_speed_maximum": None,

        "get_channel_control_register": None,
        "get_channel_status_register": None,
        "get_channel_event_status_register": None,
        "get_channel_event_mask_register": None,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)


def test_channel_measure(driver: pysweepme.EmptyDevice) -> None:
    """Test the channel dependent measure commands on page 35."""
    command_parameters = {
        "get_voltage": None,
        "get_current": None,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)


def test_configure_ramp_all_channels(driver: pysweepme.EmptyDevice) -> None:
    """Test the configure ramp commands for all channels on page 36."""
    command_parameters = {
        "set_module_voltage_ramp_speed": 20,
        "get_module_voltage_ramp_speed": None,
        "set_module_voltage_ramp_speed_emergency": 200,
        # "get_module_voltage_ramp_speed_emergency": None,
        # "get_module_voltage_ramp_speed_emergency_minimum": None,
        # "get_module_voltage_ramp_speed_emergency_maximum": None,
        "set_module_current_ramp_speed": 20,
        "get_module_current_ramp_speed": None,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)


def test_directional_ramp_speed(driver: pysweepme.EmptyDevice) -> None:
    """Test the directional ramp speed commands on page 36-37."""
    command_parameters = {
        "set_voltage_ramp_up_speed": 20,
        "get_voltage_ramp_up_speed": None,
        "set_voltage_ramp_down_speed": 20,
        "get_voltage_ramp_down_speed": None,
        "set_voltage_ramp_up_down_speed": 20,

        "set_current_ramp_up_speed": 2E-3,
        "get_current_ramp_up_speed": None,
        "set_current_ramp_down_speed": 2E-3,
        "get_current_ramp_down_speed": None,
        "set_current_ramp_up_down_speed": 2E-3,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)


def test_configure_module(driver: pysweepme.EmptyDevice) -> None:
    """Test the configure module commands on page 38-39."""
    command_parameters = {
        "set_averaging": 16,
        "get_averaging": None,
        "set_kill_enable_function": 0,
        "get_kill_enable_function": None,
        "set_fine_adjustment": 1,
        "get_fine_adjustment": None,

        "reset_module_event_status_register": None,
        "clear_module_event_status_register": 8192,
        "set_module_event_mask_register": 0,
        "get_module_event_mask_register": None,
        "set_module_event_channel_mask_register": 255,
        "get_module_event_channel_mask_register": None,

        "set_module_can_bus_address": 23,
        # "get_module_can_bus_address": None,
        "set_can_bus_bit_rate": 250000,
        # "get_can_bus_bit_rate": None,

        # "get_serial_baud_rate": None,
        "set_serial_baud_rate": None,
        "get_echo_enabled": None,
        "set_echo_enabled": 1,
    }

    for command, parameter in command_parameters.items():
        _test_command(driver, command, parameter)

