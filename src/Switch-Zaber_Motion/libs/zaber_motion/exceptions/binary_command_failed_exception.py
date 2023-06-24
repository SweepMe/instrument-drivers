# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from .binary_command_failed_exception_data import BinaryCommandFailedExceptionData
from ..protobufs import main_pb2
from .motion_lib_exception import MotionLibException


class BinaryCommandFailedException(MotionLibException):
    """
    Thrown when a device rejects a binary command with an error.
    """

    @property
    def details(self) -> BinaryCommandFailedExceptionData:
        """
        Additional data for BinaryCommandFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, BinaryCommandFailedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, BinaryCommandFailedExceptionData):
            self._details = custom_data
        else:
            protobuf_obj = main_pb2.BinaryCommandFailedExceptionData()
            protobuf_obj.ParseFromString(custom_data)
            self._details = BinaryCommandFailedExceptionData.from_protobuf(protobuf_obj)
