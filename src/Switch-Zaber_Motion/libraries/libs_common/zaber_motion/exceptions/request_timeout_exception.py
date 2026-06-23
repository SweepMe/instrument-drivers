# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class RequestTimeoutException(MotionLibException):
    """
    Thrown when a device does not respond to a request in time.
    """
