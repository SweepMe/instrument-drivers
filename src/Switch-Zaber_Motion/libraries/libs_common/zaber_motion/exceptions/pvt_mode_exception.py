# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class PvtModeException(MotionLibException):
    """
    Thrown when an operation is not supported by a mode the PVT sequence is currently set up in.
    """
