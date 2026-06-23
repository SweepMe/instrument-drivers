# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class ConversionFailedException(MotionLibException):
    """
    Thrown when a value cannot be converted using the provided units.
    """
