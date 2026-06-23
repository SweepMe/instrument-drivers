# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.set_peripheral_state_exception_data import SetPeripheralStateExceptionData
from .motion_lib_exception import MotionLibException


class SetPeripheralStateFailedException(MotionLibException):
    """
    Thrown when an axis cannot be set to the supplied state.
    """

    @property
    def details(self) -> SetPeripheralStateExceptionData:
        """
        Additional data for SetPeripheralStateFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, SetPeripheralStateExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, SetPeripheralStateExceptionData):
            self._details = custom_data
        else:
            self._details = SetPeripheralStateExceptionData.from_binary(custom_data)
