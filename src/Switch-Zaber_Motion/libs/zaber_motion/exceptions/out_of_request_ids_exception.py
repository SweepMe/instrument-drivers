# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class OutOfRequestIdsException(MotionLibException):
    """
    Thrown when the library is overwhelmed with too many simultaneous requests.
    """
