# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class TriggerOperation(Enum):
    """
    Operation for trigger action.
    """

    SET_TO = 0
    """Assign the value to the setting (=)."""

    INCREMENT_BY = 1
    """Add the value to the current setting value (+=)."""

    DECREMENT_BY = 2
    """Subtract the value from the current setting value (-=)."""
