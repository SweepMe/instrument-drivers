# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.stream_movement_failed_exception_data import StreamMovementFailedExceptionData
from .motion_lib_exception import MotionLibException


class StreamMovementFailedException(MotionLibException):
    """
    Thrown when a device registers a fault during streamed movement.
    """

    @property
    def details(self) -> StreamMovementFailedExceptionData:
        """
        Additional data for StreamMovementFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, StreamMovementFailedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, StreamMovementFailedExceptionData):
            self._details = custom_data
        else:
            self._details = StreamMovementFailedExceptionData.from_binary(custom_data)
