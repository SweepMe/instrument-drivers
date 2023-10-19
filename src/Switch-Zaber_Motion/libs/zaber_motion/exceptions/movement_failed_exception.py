# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .movement_failed_exception_data import MovementFailedExceptionData
from ..protobufs import main_pb2
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
            protobuf_obj = main_pb2.MovementFailedExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = MovementFailedExceptionData.from_protobuf(protobuf_obj)
