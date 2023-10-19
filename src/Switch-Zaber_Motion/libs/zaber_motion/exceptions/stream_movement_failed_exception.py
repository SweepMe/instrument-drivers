# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .stream_movement_failed_exception_data import StreamMovementFailedExceptionData
from ..protobufs import main_pb2
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
            protobuf_obj = main_pb2.StreamMovementFailedExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = StreamMovementFailedExceptionData.from_protobuf(protobuf_obj)
