# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class IoPortType(Enum):
    """
    Kind of I/O pin to use.
    """

    NONE = 0
    """No port type specified."""

    ANALOG_INPUT = 1
    """An analog input channel that reads a voltage."""

    ANALOG_OUTPUT = 2
    """An analog output channel that outputs a voltage."""

    DIGITAL_INPUT = 3
    """A digital input channel that reads a boolean state."""

    DIGITAL_OUTPUT = 4
    """A digital output channel that controls a boolean state."""
