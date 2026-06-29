# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict
import zaber_bson
from ..microscopy.microscope_config import MicroscopeConfig


@dataclass
class MicroscopeConfigResponse:

    config: MicroscopeConfig = field(default_factory=MicroscopeConfig.zero_values)

    @staticmethod
    def zero_values() -> 'MicroscopeConfigResponse':
        return MicroscopeConfigResponse(
            config=MicroscopeConfig.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MicroscopeConfigResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MicroscopeConfigResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'config': self.config.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MicroscopeConfigResponse':
        return MicroscopeConfigResponse(
            config=MicroscopeConfig.from_dict(data.get('config')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.config is None:
            raise ValueError(f'Property "Config" of "MicroscopeConfigResponse" is None.')

        if not isinstance(self.config, MicroscopeConfig):
            raise ValueError(f'Property "Config" of "MicroscopeConfigResponse" is not an instance of "MicroscopeConfig".')

        self.config.validate()
