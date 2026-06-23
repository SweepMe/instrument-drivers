# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class CommandPreemptedException(MotionLibException):
    """
    Thrown when a movement command gets preempted by another command.
    """
