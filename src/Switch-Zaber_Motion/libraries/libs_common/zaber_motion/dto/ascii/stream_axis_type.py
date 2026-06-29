# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class StreamAxisType(Enum):
    """
    Denotes type of the stream axis.
    """

    PHYSICAL = 0
    """A regular physical axis of the device."""

    LOCKSTEP = 1
    """A lockstep group combining multiple physical axes."""
