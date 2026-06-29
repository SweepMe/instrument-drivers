# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..device_db_source import DeviceDbSource


@dataclass
class SetDeviceDbLayeredSourcesRequest:

    sources: List[DeviceDbSource] = field(default_factory=list)

    @staticmethod
    def zero_values() -> 'SetDeviceDbLayeredSourcesRequest':
        return SetDeviceDbLayeredSourcesRequest(
            sources=[],
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetDeviceDbLayeredSourcesRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetDeviceDbLayeredSourcesRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'sources': [item.to_dict() for item in self.sources] if self.sources is not None else [],
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetDeviceDbLayeredSourcesRequest':
        return SetDeviceDbLayeredSourcesRequest(
            sources=[DeviceDbSource.from_dict(item) for item in data.get('sources')],  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.sources is not None:
            if not isinstance(self.sources, Iterable):
                raise ValueError('Property "Sources" of "SetDeviceDbLayeredSourcesRequest" is not iterable.')

            for i, sources_item in enumerate(self.sources):
                if sources_item is None:
                    raise ValueError(f'Item {i} in property "Sources" of "SetDeviceDbLayeredSourcesRequest" is None.')

                if not isinstance(sources_item, DeviceDbSource):
                    raise ValueError(f'Item {i} in property "Sources" of "SetDeviceDbLayeredSourcesRequest" is not an instance of "DeviceDbSource".')

                sources_item.validate()
