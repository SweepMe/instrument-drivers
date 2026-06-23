# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class PvtAxisType(Enum):
    """
    Denotes type of the PVT sequence axis.
    """

    PHYSICAL = 0
    """A regular physical axis of the device."""

    LOCKSTEP = 1
    """A lockstep group combining multiple physical axes."""
