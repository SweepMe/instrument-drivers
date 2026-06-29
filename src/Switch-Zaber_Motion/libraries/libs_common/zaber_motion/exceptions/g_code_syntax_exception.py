# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.g_code_syntax_exception_data import GCodeSyntaxExceptionData
from .motion_lib_exception import MotionLibException


class GCodeSyntaxException(MotionLibException):
    """
    Thrown when a block of G-Code cannot be parsed.
    """

    @property
    def details(self) -> GCodeSyntaxExceptionData:
        """
        Additional data for GCodeSyntaxException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, GCodeSyntaxExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, GCodeSyntaxExceptionData):
            self._details = custom_data
        else:
            self._details = GCodeSyntaxExceptionData.from_binary(custom_data)
