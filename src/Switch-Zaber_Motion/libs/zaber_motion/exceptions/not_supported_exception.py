# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class NotSupportedException(MotionLibException):
    """
    Thrown when a device does not support a requested command or setting.
    """
