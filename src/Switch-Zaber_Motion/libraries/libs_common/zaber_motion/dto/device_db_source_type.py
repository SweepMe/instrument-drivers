# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class DeviceDbSourceType(Enum):
    """
    Type of source of Device DB data.
    """

    WEB_SERVICE = 0
    """Fetch device information from a web service."""

    FILE = 1
    """Load device information from a local database file."""
