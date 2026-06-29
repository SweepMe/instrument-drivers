# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class DigitalOutputAction(Enum):
    """
    Action type for digital output.
    """

    OFF = 0
    """Set the digital output low."""

    ON = 1
    """Set the digital output high."""

    TOGGLE = 2
    """Toggle the current state of the digital output."""

    KEEP = 3
    """Leave the digital output in its current state."""
