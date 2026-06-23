# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class ProcessControllerSourceSensor(Enum):
    """
    The type of input sensor that provides feedback to the process controller.
    """

    THERMISTOR = 10
    """Use a thermistor sensor port on the device to measure temperature."""

    ANALOG_INPUT = 20
    """Use an analog input I/O channel on the device to measure voltage."""
