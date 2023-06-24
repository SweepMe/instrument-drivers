# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .stream_execution_exception_data import StreamExecutionExceptionData
from ..protobufs import main_pb2
from .motion_lib_exception import MotionLibException


class StreamExecutionException(MotionLibException):
    """
    Thrown when a streamed motion fails.
    """

    @property
    def details(self) -> StreamExecutionExceptionData:
        """
        Additional data for StreamExecutionException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, StreamExecutionExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, StreamExecutionExceptionData):
            self._details = custom_data
        else:
            protobuf_obj = main_pb2.StreamExecutionExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = StreamExecutionExceptionData.from_protobuf(protobuf_obj)
