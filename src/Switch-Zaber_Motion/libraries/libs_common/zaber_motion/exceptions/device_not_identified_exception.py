# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class DeviceNotIdentifiedException(MotionLibException):
    """
    Thrown when attempting an operation that requires an identified device.
    """
