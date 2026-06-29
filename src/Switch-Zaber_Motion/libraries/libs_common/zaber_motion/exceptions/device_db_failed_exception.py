# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.device_db_failed_exception_data import DeviceDbFailedExceptionData
from .motion_lib_exception import MotionLibException


class DeviceDbFailedException(MotionLibException):
    """
    Thrown when device information cannot be retrieved from the device database.
    """

    @property
    def details(self) -> DeviceDbFailedExceptionData:
        """
        Additional data for DeviceDbFailedException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, DeviceDbFailedExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, DeviceDbFailedExceptionData):
            self._details = custom_data
        else:
            self._details = DeviceDbFailedExceptionData.from_binary(custom_data)
