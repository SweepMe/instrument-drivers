# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.invalid_response_exception_data import InvalidResponseExceptionData
from .motion_lib_exception import MotionLibException


class InvalidResponseException(MotionLibException):
    """
    Thrown when a device sends a response with unexpected type or data.
    """

    @property
    def details(self) -> InvalidResponseExceptionData:
        """
        Additional data for InvalidResponseException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, InvalidResponseExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, InvalidResponseExceptionData):
            self._details = custom_data
        else:
            self._details = InvalidResponseExceptionData.from_binary(custom_data)
