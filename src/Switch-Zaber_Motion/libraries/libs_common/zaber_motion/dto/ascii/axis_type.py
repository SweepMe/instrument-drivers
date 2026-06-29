# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class AxisType(Enum):
    """
    Denotes type of an axis and units it accepts.
    """

    UNKNOWN = 0
    """Axis type could not be determined."""

    LINEAR = 1
    """A linear axis that accepts length units for position."""

    ROTARY = 2
    """A rotary axis that accepts angle units for position."""

    PROCESS = 3
    """A process on a process controller."""

    LAMP = 4
    """A lamp on a light source controller."""
