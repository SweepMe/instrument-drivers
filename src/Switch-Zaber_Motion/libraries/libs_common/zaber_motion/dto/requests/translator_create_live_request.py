# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..gcode.translator_config import TranslatorConfig


@dataclass
class TranslatorCreateLiveRequest:

    interface_id: int = 0

    device: int = 0

    stream_id: int = 0

    config: Optional[TranslatorConfig] = None

    @staticmethod
    def zero_values() -> 'TranslatorCreateLiveRequest':
        return TranslatorCreateLiveRequest(
            interface_id=0,
            device=0,
            stream_id=0,
            config=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorCreateLiveRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorCreateLiveRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'streamId': int(self.stream_id),
            'config': self.config.to_dict() if self.config is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorCreateLiveRequest':
        return TranslatorCreateLiveRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            stream_id=data.get('streamId'),  # type: ignore
            config=TranslatorConfig.from_dict(data.get('config')) if data.get('config') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TranslatorCreateLiveRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TranslatorCreateLiveRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TranslatorCreateLiveRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TranslatorCreateLiveRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TranslatorCreateLiveRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TranslatorCreateLiveRequest" is not integer value.')

        if self.stream_id is None:
            raise ValueError(f'Property "StreamId" of "TranslatorCreateLiveRequest" is None.')

        if not isinstance(self.stream_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "StreamId" of "TranslatorCreateLiveRequest" is not a number.')

        if int(self.stream_id) != self.stream_id:
            raise ValueError(f'Property "StreamId" of "TranslatorCreateLiveRequest" is not integer value.')

        if self.config is not None:
            if not isinstance(self.config, TranslatorConfig):
                raise ValueError(f'Property "Config" of "TranslatorCreateLiveRequest" is not an instance of "TranslatorConfig".')

            self.config.validate()
