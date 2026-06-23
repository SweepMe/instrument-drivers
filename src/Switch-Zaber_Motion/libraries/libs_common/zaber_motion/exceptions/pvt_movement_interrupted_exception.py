# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.pvt_movement_interrupted_exception_data import PvtMovementInterruptedExceptionData
from .motion_lib_exception import MotionLibException


class PvtMovementInterruptedException(MotionLibException):
    """
    Thrown when ongoing PVT movement is interrupted by another command or user input.
    """

    @property
    def details(self) -> PvtMovementInterruptedExceptionData:
        """
        Additional data for PvtMovementInterruptedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, PvtMovementInterruptedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, PvtMovementInterruptedExceptionData):
            self._details = custom_data
        else:
            self._details = PvtMovementInterruptedExceptionData.from_binary(custom_data)
