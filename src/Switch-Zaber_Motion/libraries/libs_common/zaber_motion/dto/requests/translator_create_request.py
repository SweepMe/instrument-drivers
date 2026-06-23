# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import zaber_bson
from ..gcode.device_definition import DeviceDefinition
from ..gcode.translator_config import TranslatorConfig


@dataclass
class TranslatorCreateRequest:

    definition: DeviceDefinition = field(default_factory=DeviceDefinition.zero_values)

    config: Optional[TranslatorConfig] = None

    @staticmethod
    def zero_values() -> 'TranslatorCreateRequest':
        return TranslatorCreateRequest(
            definition=DeviceDefinition.zero_values(),
            config=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorCreateRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorCreateRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'definition': self.definition.to_dict(),
            'config': self.config.to_dict() if self.config is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorCreateRequest':
        return TranslatorCreateRequest(
            definition=DeviceDefinition.from_dict(data.get('definition')),  # type: ignore
            config=TranslatorConfig.from_dict(data.get('config')) if data.get('config') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.definition is None:
            raise ValueError(f'Property "Definition" of "TranslatorCreateRequest" is None.')

        if not isinstance(self.definition, DeviceDefinition):
            raise ValueError(f'Property "Definition" of "TranslatorCreateRequest" is not an instance of "DeviceDefinition".')

        self.definition.validate()

        if self.config is not None:
            if not isinstance(self.config, TranslatorConfig):
                raise ValueError(f'Property "Config" of "TranslatorCreateRequest" is not an instance of "TranslatorConfig".')

            self.config.validate()
