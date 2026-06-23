# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from .motion_lib_exception import MotionLibException


class IncompatibleSharedLibraryException(MotionLibException):
    """
    Thrown when the loaded shared library is incompatible with the running code.
    Typically caused by mixed library binary files. Reinstall the library.
    """
