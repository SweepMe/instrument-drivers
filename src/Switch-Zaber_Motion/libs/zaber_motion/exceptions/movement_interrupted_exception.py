# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .movement_interrupted_exception_data import MovementInterruptedExceptionData
from ..protobufs import main_pb2
from .motion_lib_exception import MotionLibException


class MovementInterruptedException(MotionLibException):
    """
    Thrown when ongoing movement is interrupted by another command or user input.
    """

    @property
    def details(self) -> MovementInterruptedExceptionData:
        """
        Additional data for MovementInterruptedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, MovementInterruptedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, MovementInterruptedExceptionData):
            self._details = custom_data
        else:
            protobuf_obj = main_pb2.MovementInterruptedExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = MovementInterruptedExceptionData.from_protobuf(protobuf_obj)
