# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson


@dataclass
class BinaryDeviceDetectResponse:

    devices: List[int] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'BinaryDeviceDetectResponse':
        return BinaryDeviceDetectResponse(
            devices=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'BinaryDeviceDetectResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return BinaryDeviceDetectResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'devices': [int(item) for item in self.devices] if self.devices is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BinaryDeviceDetectResponse':
        return BinaryDeviceDetectResponse(
            devices=data.get('devices'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.devices is not None:
            if not isinstance(self.devices, Iterable):
                raise ValueError('Property "Devices" of "BinaryDeviceDetectResponse" is not iterable.')

            for i, devices_item in enumerate(self.devices):
                if devices_item is None:
                    raise ValueError(f'Item {i} in property "Devices" of "BinaryDeviceDetectResponse" is None.')

                if not isinstance(devices_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Devices" of "BinaryDeviceDetectResponse" is not a number.')

                if int(devices_item) != devices_item:
                    raise ValueError(f'Item {i} in property "Devices" of "BinaryDeviceDetectResponse" is not integer value.')
