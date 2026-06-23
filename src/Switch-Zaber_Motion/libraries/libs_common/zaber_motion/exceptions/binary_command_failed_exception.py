# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.binary_command_failed_exception_data import BinaryCommandFailedExceptionData
from .motion_lib_exception import MotionLibException


class BinaryCommandFailedException(MotionLibException):
    """
    Thrown when a device rejects a binary command with an error.
    """

    @property
    def details(self) -> BinaryCommandFailedExceptionData:
        """
        Additional data for BinaryCommandFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, BinaryCommandFailedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, BinaryCommandFailedExceptionData):
            self._details = custom_data
        else:
            self._details = BinaryCommandFailedExceptionData.from_binary(custom_data)
