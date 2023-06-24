# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class StreamMode(Enum):
    """
    Mode of a stream.
    """

    DISABLED = 0
    STORE = 1
    STORE_ARBITRARY_AXES = 2
    LIVE = 3
