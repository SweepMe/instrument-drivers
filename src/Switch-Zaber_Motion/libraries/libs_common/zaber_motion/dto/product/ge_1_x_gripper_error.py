# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from enum import Enum


class Ge1xGripperError(Enum):
    """
    Error for a GE1x series gripper.
    """

    NONE = 0
    """No error."""

    UNDERVOLTAGE = 1
    """The gripper supply voltage is too low."""

    OVERVOLTAGE = 2
    """The gripper supply voltage is too high."""

    OVERCURRENT = 3
    """The gripper is drawing too much current."""

    OVERTEMPERATURE = 4
    """The gripper temperature is too high."""

    MOTOR_PHASE_LOSS = 10
    """There is a 3-phase imbalance in the motor."""

    OVERSPEED = 11
    """The gripper has exceeded its rated speed."""

    ENCODER_ERROR = 32
    """There is an error with the gripper encoder."""

    ENCODER_COMMUNICATION_ERROR = 33
    """There is a communication error with the gripper encoder."""

    SAMPLING_CIRCUIT_ERROR = 34
    """The gripper current sampling offset is abnormal."""

    DRIVER_CIRCUIT_ERROR = 35
    """There is an error with the gripper driver circuit."""

    FLASH_CHIP_ERROR = 36
    """There is an error with the gripper flash memory."""

    FILE_SYSTEM_ERROR = 37
    """There is an error with the gripper file system."""
