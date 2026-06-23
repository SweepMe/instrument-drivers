# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class OscilloscopeDataSource(Enum):
    """
    Kind of channel to record in the Oscilloscope.
    """

    SETTING = 0
    """Records the value of a device or axis setting over time."""

    IO = 1
    """Records the value of an I/O pin over time."""
