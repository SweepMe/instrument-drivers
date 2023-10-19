# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class ConnectionClosedException(MotionLibException):
    """
    Thrown when attempting to communicate on a closed connection.
    """
