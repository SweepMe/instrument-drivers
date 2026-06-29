# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.movement_failed_exception_data import MovementFailedExceptionData
from .motion_lib_exception import MotionLibException


class MovementFailedException(MotionLibException):
    """
    Thrown when a device registers a fault during movement.
    """

    @property
    def details(self) -> MovementFailedExceptionData:
        """
        Additional data for MovementFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, MovementFailedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, MovementFailedExceptionData):
            self._details = custom_data
        else:
            self._details = MovementFailedExceptionData.from_binary(custom_data)
