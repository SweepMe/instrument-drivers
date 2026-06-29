# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..firmware_version import FirmwareVersion


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
    """

    name: str
    """
    Name of the product.
    """

    axis_count: int
    """
    Number of axes this device has.
    """

    firmware_version: FirmwareVersion
    """
    Version of the firmware.
    """

    is_modified: bool
    """
    The device has hardware modifications.
    """

    is_integrated: bool
    """
    The device is an integrated product.
    """

    @staticmethod
    def zero_values() -> 'DeviceIdentity':
        return DeviceIdentity(
            device_id=0,
            serial_number=0,
            name="",
            axis_count=0,
            firmware_version=FirmwareVersion.zero_values(),
            is_modified=False,
            is_integrated=False,
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
            'axisCount': int(self.axis_count),
            'firmwareVersion': self.firmware_version.to_dict(),
            'isModified': bool(self.is_modified),
            'isIntegrated': bool(self.is_integrated),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceIdentity':
        return DeviceIdentity(
            device_id=data.get('deviceId'),  # type: ignore
            serial_number=data.get('serialNumber'),  # type: ignore
            name=data.get('name'),  # type: ignore
            axis_count=data.get('axisCount'),  # type: ignore
            firmware_version=FirmwareVersion.from_dict(data.get('firmwareVersion')),  # type: ignore
            is_modified=data.get('isModified'),  # type: ignore
            is_integrated=data.get('isIntegrated'),  # type: ignore
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

        if self.axis_count is None:
            raise ValueError(f'Property "AxisCount" of "DeviceIdentity" is None.')

        if not isinstance(self.axis_count, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisCount" of "DeviceIdentity" is not a number.')

        if int(self.axis_count) != self.axis_count:
            raise ValueError(f'Property "AxisCount" of "DeviceIdentity" is not integer value.')

        if self.firmware_version is None:
            raise ValueError(f'Property "FirmwareVersion" of "DeviceIdentity" is None.')

        if not isinstance(self.firmware_version, FirmwareVersion):
            raise ValueError(f'Property "FirmwareVersion" of "DeviceIdentity" is not an instance of "FirmwareVersion".')

        self.firmware_version.validate()
