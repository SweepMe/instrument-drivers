# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class DeviceBusyException(MotionLibException):
    """
    Thrown when a requested operation fails because the device is currently busy.
    """
