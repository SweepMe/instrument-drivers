# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class InvalidDataException(MotionLibException):
    """
    Thrown when incoming device data cannot be parsed as expected.
    """
