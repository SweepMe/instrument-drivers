# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..device_discovery_result import DeviceDiscoveryResult


@dataclass
class DiscoverTCPDevicesResponse:

    result: List[DeviceDiscoveryResult] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'DiscoverTCPDevicesResponse':
        return DiscoverTCPDevicesResponse(
            result=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DiscoverTCPDevicesResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DiscoverTCPDevicesResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'result': [item.to_dict() for item in self.result] if self.result is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DiscoverTCPDevicesResponse':
        return DiscoverTCPDevicesResponse(
            result=[DeviceDiscoveryResult.from_dict(item) for item in data.get('result')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.result is not None:
            if not isinstance(self.result, Iterable):
                raise ValueError('Property "Result" of "DiscoverTCPDevicesResponse" is not iterable.')

            for i, result_item in enumerate(self.result):
                if result_item is None:
                    raise ValueError(f'Item {i} in property "Result" of "DiscoverTCPDevicesResponse" is None.')

                if not isinstance(result_item, DeviceDiscoveryResult):
                    raise ValueError(f'Item {i} in property "Result" of "DiscoverTCPDevicesResponse" is not an instance of "DeviceDiscoveryResult".')

                result_item.validate()
