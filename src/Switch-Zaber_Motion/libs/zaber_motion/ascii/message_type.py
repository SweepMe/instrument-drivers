# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class MessageType(Enum):
    """
    Denotes type of the response message.
    For more information refer to:
    [ASCII Protocol Manual](https://www.zaber.com/protocol-manual#topic_message_format).
    """

    REPLY = 0
    INFO = 1
    ALERT = 2
