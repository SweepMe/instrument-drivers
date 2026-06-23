# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class StreamMode(Enum):
    """
    Mode of a stream.
    """

    DISABLED = 0
    """The stream is not set up."""

    STORE = 1
    """Actions are queued into a stream buffer for later playback."""

    STORE_ARBITRARY_AXES = 2
    """Actions are queued into a stream buffer for later playback (axes not specified)."""

    LIVE = 3
    """Actions are queued and executed on the device immediately."""
