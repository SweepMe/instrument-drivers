# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class InvalidRequestDataException(MotionLibException):
    """
    Used for internal error handling.
    Indicates passing values of incorrect type from scripting languages or mixed library binary files.
    """
