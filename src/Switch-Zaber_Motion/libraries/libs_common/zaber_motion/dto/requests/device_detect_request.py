# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from .device_type import DeviceType


@dataclass
class DeviceDetectRequest:

    interface_id: int = 0

    identify_devices: bool = False

    type: DeviceType = next(first for first in DeviceType)

    @staticmethod
    def zero_values() -> 'DeviceDetectRequest':
        return DeviceDetectRequest(
            interface_id=0,
            identify_devices=False,
            type=next(first for first in DeviceType),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceDetectRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceDetectRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'identifyDevices': bool(self.identify_devices),
            'type': self.type.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceDetectRequest':
        return DeviceDetectRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            identify_devices=data.get('identifyDevices'),  # type: ignore
            type=DeviceType(data.get('type')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceDetectRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceDetectRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceDetectRequest" is not integer value.')

        if self.type is None:
            raise ValueError(f'Property "Type" of "DeviceDetectRequest" is None.')

        if not isinstance(self.type, DeviceType):
            raise ValueError(f'Property "Type" of "DeviceDetectRequest" is not an instance of "DeviceType".')
