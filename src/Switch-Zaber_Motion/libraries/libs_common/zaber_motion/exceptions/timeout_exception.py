# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class TimeoutException(MotionLibException):
    """
    Thrown for various timeouts across the library excluding request to a device (see RequestTimeoutException).
    """
