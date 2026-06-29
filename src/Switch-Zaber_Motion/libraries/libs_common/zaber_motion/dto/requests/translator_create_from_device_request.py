# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import decimal
from collections.abc import Iterable
import zaber_bson
from ..gcode.translator_config import TranslatorConfig


@dataclass
class TranslatorCreateFromDeviceRequest:

    interface_id: int = 0

    device: int = 0

    axes: List[int] = field(default_factory=list)

    config: Optional[TranslatorConfig] = None

    @staticmethod
    def zero_values() -> 'TranslatorCreateFromDeviceRequest':
        return TranslatorCreateFromDeviceRequest(
            interface_id=0,
            device=0,
            axes=[],
            config=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'TranslatorCreateFromDeviceRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return TranslatorCreateFromDeviceRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axes': [int(item) for item in self.axes] if self.axes is not None else [],
            'config': self.config.to_dict() if self.config is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TranslatorCreateFromDeviceRequest':
        return TranslatorCreateFromDeviceRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axes=data.get('axes'),  # type: ignore
            config=TranslatorConfig.from_dict(data.get('config')) if data.get('config') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "TranslatorCreateFromDeviceRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "TranslatorCreateFromDeviceRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "TranslatorCreateFromDeviceRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "TranslatorCreateFromDeviceRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "TranslatorCreateFromDeviceRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "TranslatorCreateFromDeviceRequest" is not integer value.')

        if self.axes is not None:
            if not isinstance(self.axes, Iterable):
                raise ValueError('Property "Axes" of "TranslatorCreateFromDeviceRequest" is not iterable.')

            for i, axes_item in enumerate(self.axes):
                if axes_item is None:
                    raise ValueError(f'Item {i} in property "Axes" of "TranslatorCreateFromDeviceRequest" is None.')

                if not isinstance(axes_item, (int, float, decimal.Decimal)):
                    raise ValueError(f'Item {i} in property "Axes" of "TranslatorCreateFromDeviceRequest" is not a number.')

                if int(axes_item) != axes_item:
                    raise ValueError(f'Item {i} in property "Axes" of "TranslatorCreateFromDeviceRequest" is not integer value.')

        if self.config is not None:
            if not isinstance(self.config, TranslatorConfig):
                raise ValueError(f'Property "Config" of "TranslatorCreateFromDeviceRequest" is not an instance of "TranslatorConfig".')

            self.config.validate()
