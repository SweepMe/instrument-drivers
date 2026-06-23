# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..firmware_version import FirmwareVersion
from .device_type import DeviceType


@dataclass
class DeviceIdentity:
    """
    Representation of data gathered during device identification.
    """

    device_id: int
    """
    Unique ID of the device hardware.
    """

    serial_number: int
    """
    Serial number of the device.
    Requires at least Firmware 6.15 for devices or 6.24 for peripherals.
    """

    name: str
    """
    Name of the product.
    """

    firmware_version: FirmwareVersion
    """
    Version of the firmware.
    """

    is_peripheral: bool
    """
    Indicates whether the device is a peripheral or part of an integrated device.
    """

    peripheral_id: int
    """
    Unique ID of the peripheral hardware.
    """

    peripheral_name: str
    """
    Name of the peripheral hardware.
    """

    device_type: DeviceType
    """
    Determines the type of an device and units it accepts.
    """

    @staticmethod
    def zero_values() -> 'DeviceIdentity':
        return DeviceIdentity(
            device_id=0,
            serial_number=0,
            name="",
            firmware_version=FirmwareVersion.zero_values(),
            is_peripheral=False,
            peripheral_id=0,
            peripheral_name="",
            device_type=next(first for first in DeviceType),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceIdentity':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceIdentity.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'deviceId': int(self.device_id),
            'serialNumber': int(self.serial_number),
            'name': str(self.name or ''),
            'firmwareVersion': self.firmware_version.to_dict(),
            'isPeripheral': bool(self.is_peripheral),
            'peripheralId': int(self.peripheral_id),
            'peripheralName': str(self.peripheral_name or ''),
            'deviceType': self.device_type.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceIdentity':
        return DeviceIdentity(
            device_id=data.get('deviceId'),  # type: ignore
            serial_number=data.get('serialNumber'),  # type: ignore
            name=data.get('name'),  # type: ignore
            firmware_version=FirmwareVersion.from_dict(data.get('firmwareVersion')),  # type: ignore
            is_peripheral=data.get('isPeripheral'),  # type: ignore
            peripheral_id=data.get('peripheralId'),  # type: ignore
            peripheral_name=data.get('peripheralName'),  # type: ignore
            device_type=DeviceType(data.get('deviceType')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.device_id is None:
            raise ValueError(f'Property "DeviceId" of "DeviceIdentity" is None.')

        if not isinstance(self.device_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceId" of "DeviceIdentity" is not a number.')

        if int(self.device_id) != self.device_id:
            raise ValueError(f'Property "DeviceId" of "DeviceIdentity" is not integer value.')

        if self.serial_number is None:
            raise ValueError(f'Property "SerialNumber" of "DeviceIdentity" is None.')

        if not isinstance(self.serial_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "SerialNumber" of "DeviceIdentity" is not a number.')

        if int(self.serial_number) != self.serial_number:
            raise ValueError(f'Property "SerialNumber" of "DeviceIdentity" is not integer value.')

        if self.name is not None:
            if not isinstance(self.name, str):
                raise ValueError(f'Property "Name" of "DeviceIdentity" is not a string.')

        if self.firmware_version is None:
            raise ValueError(f'Property "FirmwareVersion" of "DeviceIdentity" is None.')

        if not isinstance(self.firmware_version, FirmwareVersion):
            raise ValueError(f'Property "FirmwareVersion" of "DeviceIdentity" is not an instance of "FirmwareVersion".')

        self.firmware_version.validate()

        if self.peripheral_id is None:
            raise ValueError(f'Property "PeripheralId" of "DeviceIdentity" is None.')

        if not isinstance(self.peripheral_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "PeripheralId" of "DeviceIdentity" is not a number.')

        if int(self.peripheral_id) != self.peripheral_id:
            raise ValueError(f'Property "PeripheralId" of "DeviceIdentity" is not integer value.')

        if self.peripheral_name is not None:
            if not isinstance(self.peripheral_name, str):
                raise ValueError(f'Property "PeripheralName" of "DeviceIdentity" is not a string.')

        if self.device_type is None:
            raise ValueError(f'Property "DeviceType" of "DeviceIdentity" is None.')

        if not isinstance(self.device_type, DeviceType):
            raise ValueError(f'Property "DeviceType" of "DeviceIdentity" is not an instance of "DeviceType".')
