# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class ProcessControllerMode(Enum):
    """
    Mode of the process controller.
    """

    MANUAL = 0
    """Allows direct control of the output voltage."""

    PID = 1
    """Closed-loop PID control to maintain a setpoint."""

    PID_HEATER = 2
    """PID control optimized for heater loads."""

    ON_OFF = 3
    """Binary on/off switching based on a threshold."""
