# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class LogOutputMode(Enum):
    """
    Mode of logging output of the library.
    """

    OFF = 0
    """Discard all log output."""

    STDOUT = 1
    """Write logs to standard output."""

    STDERR = 2
    """Write logs to standard error."""

    FILE = 3
    """Write logs to a specified file."""
