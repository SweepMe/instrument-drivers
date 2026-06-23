# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class MessageType(Enum):
    """
    Denotes type of the response message.
    For more information refer to:
    ASCII Protocol Manual (https://www.zaber.com/protocol-manual#topic_message_format).
    """

    REPLY = 0
    """A direct response to a command sent to the device."""

    INFO = 1
    """An additional data message supplementing a reply."""

    ALERT = 2
    """An unsolicited message from the device reporting a status change."""
