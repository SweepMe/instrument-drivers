# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.command_failed_exception_data import CommandFailedExceptionData
from .motion_lib_exception import MotionLibException


class CommandFailedException(MotionLibException):
    """
    Thrown when a device rejects a command.
    """

    @property
    def details(self) -> CommandFailedExceptionData:
        """
        Additional data for CommandFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, CommandFailedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, CommandFailedExceptionData):
            self._details = custom_data
        else:
            self._details = CommandFailedExceptionData.from_binary(custom_data)
