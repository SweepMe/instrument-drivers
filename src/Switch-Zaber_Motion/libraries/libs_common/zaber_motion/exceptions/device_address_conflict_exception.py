# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #

from typing import Union
from ..dto.exceptions.device_address_conflict_exception_data import DeviceAddressConflictExceptionData
from .motion_lib_exception import MotionLibException


class DeviceAddressConflictException(MotionLibException):
    """
    Thrown when there is a conflict in device numbers preventing unique addressing.
    """

    @property
    def details(self) -> DeviceAddressConflictExceptionData:
        """
        Additional data for DeviceAddressConflictException
        """
        return self._details

    def __init__(self, message: str, custom_data: Union[bytes, DeviceAddressConflictExceptionData]):
        MotionLibException.__init__(self, message)

        if isinstance(custom_data, DeviceAddressConflictExceptionData):
            self._details = custom_data
        else:
            self._details = DeviceAddressConflictExceptionData.from_binary(custom_data)
