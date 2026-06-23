# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class Ge1xGripperState(Enum):
    """
    State of a GE1x series gripper.
    """

    NO_REFERENCE_POSITION = 0
    """The gripper has not been homed and does not have a reference position."""

    HOMING = 1
    """The gripper is currently performing a homing operation."""

    IDLE = 2
    """The gripper is idle at its target position."""

    MOVING = 3
    """The gripper is moving to its target position."""

    OBJECT_DETECTED = 4
    """The gripper has detected an object."""

    OBJECT_DROPPED = 5
    """The gripper has detected that an object it was holding has been dropped."""
