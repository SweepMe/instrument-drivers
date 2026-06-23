# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class StreamModeException(MotionLibException):
    """
    Thrown when an operation is not supported by a mode the stream is currently set up in.
    """
