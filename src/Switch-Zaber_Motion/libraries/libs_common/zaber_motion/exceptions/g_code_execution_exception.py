# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.g_code_execution_exception_data import GCodeExecutionExceptionData
from .motion_lib_exception import MotionLibException


class GCodeExecutionException(MotionLibException):
    """
    Thrown when a block of G-Code cannot be executed.
    """

    @property
    def details(self) -> GCodeExecutionExceptionData:
        """
        Additional data for GCodeExecutionException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, GCodeExecutionExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, GCodeExecutionExceptionData):
            self._details = custom_data
        else:
            self._details = GCodeExecutionExceptionData.from_binary(custom_data)
