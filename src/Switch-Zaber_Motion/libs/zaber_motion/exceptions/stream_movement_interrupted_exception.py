# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .stream_movement_interrupted_exception_data import StreamMovementInterruptedExceptionData
from ..protobufs import main_pb2
from .motion_lib_exception import MotionLibException


class StreamMovementInterruptedException(MotionLibException):
    """
    Thrown when ongoing stream movement is interrupted by another command or user input.
    """

    @property
    def details(self) -> StreamMovementInterruptedExceptionData:
        """
        Additional data for StreamMovementInterruptedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, StreamMovementInterruptedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, StreamMovementInterruptedExceptionData):
            self._details = custom_data
        else:
            protobuf_obj = main_pb2.StreamMovementInterruptedExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = StreamMovementInterruptedExceptionData.from_protobuf(protobuf_obj)
