# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..firmware_version import FirmwareVersion


@dataclass
class DeviceIdentifyRequest:

    interface_id: int = 0

    device: int = 0

    assume_version: Optional[FirmwareVersion] = None

    @staticmethod
    def zero_values() -> 'DeviceIdentifyRequest':
        return DeviceIdentifyRequest(
            interface_id=0,
            device=0,
            assume_version=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceIdentifyRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceIdentifyRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'assumeVersion': self.assume_version.to_dict() if self.assume_version is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceIdentifyRequest':
        return DeviceIdentifyRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            assume_version=FirmwareVersion.from_dict(data.get('assumeVersion')) if data.get('assumeVersion') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceIdentifyRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceIdentifyRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceIdentifyRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceIdentifyRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceIdentifyRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceIdentifyRequest" is not integer value.')

        if self.assume_version is not None:
            if not isinstance(self.assume_version, FirmwareVersion):
                raise ValueError(f'Property "AssumeVersion" of "DeviceIdentifyRequest" is not an instance of "FirmwareVersion".')

            self.assume_version.validate()
