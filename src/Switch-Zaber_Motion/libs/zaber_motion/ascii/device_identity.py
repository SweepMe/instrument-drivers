# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=W0201

from ..protobufs import main_pb2
from ..firmware_version import FirmwareVersion


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
    def axis_count(self) -> int:
        """
        Number of axes this device has.
        """

        return self._axis_count

    @axis_count.setter
    def axis_count(self, value: int) -> None:
        self._axis_count = value

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
    def is_modified(self) -> bool:
        """
        The device has hardware modifications.
        """

        return self._is_modified

    @is_modified.setter
    def is_modified(self, value: bool) -> None:
        self._is_modified = value

    def __repr__(self) -> str:
        return str(self.__dict__)

    @staticmethod
    def from_protobuf(
        pb_data: main_pb2.DeviceIdentity
    ) -> 'DeviceIdentity':
        instance = DeviceIdentity.__new__(
            DeviceIdentity
        )  # type: DeviceIdentity
        instance.device_id = pb_data.device_id
        instance.serial_number = pb_data.serial_number
        instance.name = pb_data.name
        instance.axis_count = pb_data.axis_count
        instance.firmware_version = FirmwareVersion.from_protobuf(pb_data.firmware_version)
        instance.is_modified = pb_data.is_modified
        return instance
