# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class CyclicDirection(Enum):
    """
    Direction a cyclic device should move when doing an absolute move.
    """

    POSITIVE = 0
    """Move to the target in a positive direction."""

    NEGATIVE = 1
    """Move to the target in a negative direction."""

    SHORTEST = 2
    """Take the shortest path to the target position."""
