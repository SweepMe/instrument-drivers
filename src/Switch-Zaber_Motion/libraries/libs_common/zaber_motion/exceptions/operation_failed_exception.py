# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.operation_failed_exception_data import OperationFailedExceptionData
from .motion_lib_exception import MotionLibException


class OperationFailedException(MotionLibException):
    """
    Thrown when a non-motion device fails to perform a requested operation.
    """

    @property
    def details(self) -> OperationFailedExceptionData:
        """
        Additional data for OperationFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, OperationFailedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, OperationFailedExceptionData):
            self._details = custom_data
        else:
            self._details = OperationFailedExceptionData.from_binary(custom_data)
