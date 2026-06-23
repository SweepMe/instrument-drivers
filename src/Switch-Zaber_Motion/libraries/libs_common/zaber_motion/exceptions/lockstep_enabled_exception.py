# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class LockstepEnabledException(MotionLibException):
    """
    Thrown when an operation cannot be performed because lockstep motion is enabled.
    """
