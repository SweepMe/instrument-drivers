# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from ..firmware_version import FirmwareVersion
from .mock_peripheral import MockPeripheral


@dataclass
class MockDevice:
    """
    Definition of a mock device.
    """

    device_id: int
    """
    A valid Zaber device ID.
    """

    firmware_version: Optional[FirmwareVersion] = None
    """
    Version of the firmware. Defaults to device database latest. To omit minor or build version, set them to -1.
    """

    is_modified: Optional[bool] = None
    """
    The device has hardware modifications. Defaults to false.
    """

    resolution: Optional[int] = None
    """
    The number of microsteps per full step for integrated devices. Defaults to device database default.
    """

    peripherals: Optional[List[MockPeripheral]] = None
    """
    List of mock peripherals connected to the device.
    """

    @staticmethod
    def zero_values() -> 'MockDevice':
        return MockDevice(
            device_id=0,
            firmware_version=None,
            is_modified=None,
            resolution=None,
            peripherals=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MockDevice':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MockDevice.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'deviceId': int(self.device_id),
            'firmwareVersion': self.firmware_version.to_dict() if self.firmware_version is not None else None,
            'isModified': bool(self.is_modified) if self.is_modified is not None else None,
            'resolution': int(self.resolution) if self.resolution is not None else None,
            'peripherals': [item.to_dict() for item in self.peripherals] if self.peripherals is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MockDevice':
        return MockDevice(
            device_id=data.get('deviceId'),  # type: ignore
            firmware_version=FirmwareVersion.from_dict(data.get('firmwareVersion')) if data.get('firmwareVersion') is not None else None,  # type: ignore
            is_modified=data.get('isModified'),  # type: ignore
            resolution=data.get('resolution'),  # type: ignore
            peripherals=[MockPeripheral.from_dict(item) for item in data.get('peripherals')] if data.get('peripherals') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.device_id is None:
            raise ValueError(f'Property "DeviceId" of "MockDevice" is None.')

        if not isinstance(self.device_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "DeviceId" of "MockDevice" is not a number.')

        if int(self.device_id) != self.device_id:
            raise ValueError(f'Property "DeviceId" of "MockDevice" is not integer value.')

        if self.firmware_version is not None:
            if not isinstance(self.firmware_version, FirmwareVersion):
                raise ValueError(f'Property "FirmwareVersion" of "MockDevice" is not an instance of "FirmwareVersion".')

            self.firmware_version.validate()

        if self.resolution is not None:
            if not isinstance(self.resolution, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "Resolution" of "MockDevice" is not a number.')

            if int(self.resolution) != self.resolution:
                raise ValueError(f'Property "Resolution" of "MockDevice" is not integer value.')

        if self.peripherals is not None:
            if not isinstance(self.peripherals, Iterable):
                raise ValueError('Property "Peripherals" of "MockDevice" is not iterable.')

            for i, peripherals_item in enumerate(self.peripherals):
                if peripherals_item is None:
                    raise ValueError(f'Item {i} in property "Peripherals" of "MockDevice" is None.')

                if not isinstance(peripherals_item, MockPeripheral):
                    raise ValueError(f'Item {i} in property "Peripherals" of "MockDevice" is not an instance of "MockPeripheral".')

                peripherals_item.validate()
