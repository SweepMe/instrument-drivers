# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class DevicePortType(Enum):
    """
    Type of TCP port used to connect to a device on the network.
    """

    DEVICE = 0
    """TCP port that communicates only with the connected device."""

    DEVICE_CHAIN = 1
    """TCP port that communicates with the connected device and all chained devices."""
