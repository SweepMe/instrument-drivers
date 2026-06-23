# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class PvtMode(Enum):
    """
    Mode of a PVT sequence.
    """

    DISABLED = 0
    """The PVT sequence is not set up."""

    STORE = 1
    """PVT points are queued into a buffer for later playback."""

    LIVE = 2
    """PVT points are queued and executed on the device immediately."""
