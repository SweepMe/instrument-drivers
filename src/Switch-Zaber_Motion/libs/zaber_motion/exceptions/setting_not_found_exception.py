# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class SettingNotFoundException(MotionLibException):
    """
    Thrown when a get or a set command cannot be found for a setting.
    """
