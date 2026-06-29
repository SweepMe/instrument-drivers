# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class AccelType(Enum):
    """
    Type of acceleration to get or set.
    """

    ACCEL_DECEL = 0
    """Both acceleration and deceleration."""

    ACCEL_ONLY = 1
    """Acceleration only."""

    DECEL_ONLY = 2
    """Deceleration only."""
