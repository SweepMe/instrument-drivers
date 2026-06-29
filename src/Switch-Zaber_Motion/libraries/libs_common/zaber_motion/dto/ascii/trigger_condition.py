# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class TriggerCondition(Enum):
    """
    Comparison operator for trigger condition.
    """

    EQ = 0
    """Equal To (==)"""

    NE = 1
    """Not Equal To (!=)"""

    GT = 2
    """Greater Than (>)"""

    GE = 3
    """Greater Than or Equal To (>=)"""

    LT = 4
    """Less Than (<)"""

    LE = 5
    """Less Than or Equal To (<=)"""
