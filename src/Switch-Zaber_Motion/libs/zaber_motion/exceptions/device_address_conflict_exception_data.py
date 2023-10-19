# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from typing import List
from ..protobufs import main_pb2


class DeviceAddressConflictExceptionData:
    """
    Contains additional data for DeviceAddressConflictException.
    """

    @property
    def device_addresses(self) -> List[int]:
        """
        The full list of detected device addresses.
        """

        return self._device_addresses

    @device_addresses.setter
    def device_addresses(self, value: List[int]) -> None:
        self._device_addresses = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.DeviceAddressConflictExceptionData
    ) -> 'DeviceAddressConflictExceptionData':
        instance = DeviceAddressConflictExceptionData.__new__(
            DeviceAddressConflictExceptionData
        )  # type: DeviceAddressConflictExceptionData
        instance.device_addresses = list(pb_data.device_addresses)
        return instance
