# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class DeviceType(Enum):
    """
    Denotes type of an device and units it accepts.
    """

    UNKNOWN = 0
    """Device type could not be determined."""

    LINEAR = 1
    """A linear device that accepts length units for position."""

    ROTARY = 2
    """A rotary device that accepts angle units for position."""
