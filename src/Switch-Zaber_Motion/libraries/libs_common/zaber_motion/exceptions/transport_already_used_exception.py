# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class TransportAlreadyUsedException(MotionLibException):
    """
    Thrown when a transport has already been used to open another connection.
    """
