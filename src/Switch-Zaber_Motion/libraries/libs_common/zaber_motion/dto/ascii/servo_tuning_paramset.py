# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class ServoTuningParamset(Enum):
    """
    Servo Tuning Parameter Set to target.
    """

    LIVE = 0
    """The currently active servo tuning parameters."""

    P_1 = 1
    """Stored parameter set 1."""

    P_2 = 2
    """Stored parameter set 2."""

    P_3 = 3
    """Stored parameter set 3."""

    P_4 = 4
    """Stored parameter set 4."""

    P_5 = 5
    """Stored parameter set 5."""

    P_6 = 6
    """Stored parameter set 6."""

    P_7 = 7
    """Stored parameter set 7."""

    P_8 = 8
    """Stored parameter set 8."""

    P_9 = 9
    """Stored parameter set 9."""

    STAGING = 10
    """A temporary working area for preparing tuning changes."""

    DEFAULT = 11
    """The factory default parameter set."""
