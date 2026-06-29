# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict
import decimal
import zaber_bson
from ..microscopy.microscope_config import MicroscopeConfig


@dataclass
class MicroscopeEmptyRequest:

    interface_id: int = 0

    config: MicroscopeConfig = field(default_factory=MicroscopeConfig.zero_values)

    @staticmethod
    def zero_values() -> 'MicroscopeEmptyRequest':
        return MicroscopeEmptyRequest(
            interface_id=0,
            config=MicroscopeConfig.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MicroscopeEmptyRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MicroscopeEmptyRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'config': self.config.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MicroscopeEmptyRequest':
        return MicroscopeEmptyRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            config=MicroscopeConfig.from_dict(data.get('config')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "MicroscopeEmptyRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "MicroscopeEmptyRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "MicroscopeEmptyRequest" is not integer value.')

        if self.config is None:
            raise ValueError(f'Property "Config" of "MicroscopeEmptyRequest" is None.')

        if not isinstance(self.config, MicroscopeConfig):
            raise ValueError(f'Property "Config" of "MicroscopeEmptyRequest" is not an instance of "MicroscopeConfig".')

        self.config.validate()
