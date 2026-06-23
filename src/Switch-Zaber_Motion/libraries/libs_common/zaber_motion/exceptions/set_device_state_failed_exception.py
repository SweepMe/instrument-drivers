# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.set_device_state_exception_data import SetDeviceStateExceptionData
from .motion_lib_exception import MotionLibException


class SetDeviceStateFailedException(MotionLibException):
    """
    Thrown when a device cannot be set to the supplied state.
    """

    @property
    def details(self) -> SetDeviceStateExceptionData:
        """
        Additional data for SetDeviceStateFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, SetDeviceStateExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, SetDeviceStateExceptionData):
            self._details = custom_data
        else:
            self._details = SetDeviceStateExceptionData.from_binary(custom_data)
