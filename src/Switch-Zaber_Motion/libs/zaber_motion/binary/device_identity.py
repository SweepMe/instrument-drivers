# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2
from ..firmware_version import FirmwareVersion
from .device_type import DeviceType


class DeviceIdentity:
    """
    Representation of data gathered during device identification.
    """

    @property
    def device_id(self) -> int:
        """
        Unique ID of the device hardware.
        """

        return self._device_id

    @device_id.setter
    def device_id(self, value: int) -> None:
        self._device_id = value

    @property
    def serial_number(self) -> int:
        """
        Serial number of the device.
        """

        return self._serial_number

    @serial_number.setter
    def serial_number(self, value: int) -> None:
        self._serial_number = value

    @property
    def name(self) -> str:
        """
        Name of the product.
        """

        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def firmware_version(self) -> FirmwareVersion:
        """
        Version of the firmware.
        """

        return self._firmware_version

    @firmware_version.setter
    def firmware_version(self, value: FirmwareVersion) -> None:
        self._firmware_version = value

    @property
    def is_peripheral(self) -> bool:
        """
        Indicates whether the device is a peripheral or part of an integrated device.
        """

        return self._is_peripheral

    @is_peripheral.setter
    def is_peripheral(self, value: bool) -> None:
        self._is_peripheral = value

    @property
    def peripheral_id(self) -> int:
        """
        Unique ID of the peripheral hardware.
        """

        return self._peripheral_id

    @peripheral_id.setter
    def peripheral_id(self, value: int) -> None:
        self._peripheral_id = value

    @property
    def peripheral_name(self) -> str:
        """
        Name of the peripheral hardware.
        """

        return self._peripheral_name

    @peripheral_name.setter
    def peripheral_name(self, value: str) -> None:
        self._peripheral_name = value

    @property
    def device_type(self) -> DeviceType:
        """
        Determines the type of an device and units it accepts.
        """

        return self._device_type

    @device_type.setter
    def device_type(self, value: DeviceType) -> None:
        self._device_type = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.BinaryDeviceIdentity
    ) -> 'DeviceIdentity':
        instance = DeviceIdentity.__new__(
            DeviceIdentity
        )  # type: DeviceIdentity
        instance.device_id = pb_data.device_id
        instance.serial_number = pb_data.serial_number
        instance.name = pb_data.name
        instance.firmware_version = FirmwareVersion.from_protobuf(pb_data.firmware_version)
        instance.is_peripheral = pb_data.is_peripheral
        instance.peripheral_id = pb_data.peripheral_id
        instance.peripheral_name = pb_data.peripheral_name
        instance.device_type = DeviceType(pb_data.device_type)
        return instance
