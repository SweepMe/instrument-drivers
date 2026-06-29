# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class DeviceSetStorageNumberRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    key: str = ""

    value: float = 0

    @staticmethod
    def zero_values() -> 'DeviceSetStorageNumberRequest':
        return DeviceSetStorageNumberRequest(
            interface_id=0,
            device=0,
            axis=0,
            key="",
            value=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DeviceSetStorageNumberRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DeviceSetStorageNumberRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'key': str(self.key or ''),
            'value': float(self.value),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DeviceSetStorageNumberRequest':
        return DeviceSetStorageNumberRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            key=data.get('key'),  # type: ignore
            value=data.get('value'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetStorageNumberRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "DeviceSetStorageNumberRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "DeviceSetStorageNumberRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "DeviceSetStorageNumberRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "DeviceSetStorageNumberRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "DeviceSetStorageNumberRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "DeviceSetStorageNumberRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "DeviceSetStorageNumberRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "DeviceSetStorageNumberRequest" is not integer value.')

        if self.key is not None:
            if not isinstance(self.key, str):
                raise ValueError(f'Property "Key" of "DeviceSetStorageNumberRequest" is not a string.')

        if self.value is None:
            raise ValueError(f'Property "Value" of "DeviceSetStorageNumberRequest" is None.')

        if not isinstance(self.value, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Value" of "DeviceSetStorageNumberRequest" is not a number.')
