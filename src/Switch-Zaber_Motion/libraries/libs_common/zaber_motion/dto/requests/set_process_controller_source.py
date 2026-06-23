# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict
import decimal
import zaber_bson
from ..product.process_controller_source import ProcessControllerSource


@dataclass
class SetProcessControllerSource:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    source: ProcessControllerSource = field(default_factory=ProcessControllerSource.zero_values)

    @staticmethod
    def zero_values() -> 'SetProcessControllerSource':
        return SetProcessControllerSource(
            interface_id=0,
            device=0,
            axis=0,
            source=ProcessControllerSource.zero_values(),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetProcessControllerSource':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetProcessControllerSource.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'source': self.source.to_dict(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetProcessControllerSource':
        return SetProcessControllerSource(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            source=ProcessControllerSource.from_dict(data.get('source')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "SetProcessControllerSource" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "SetProcessControllerSource" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "SetProcessControllerSource" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "SetProcessControllerSource" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "SetProcessControllerSource" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "SetProcessControllerSource" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "SetProcessControllerSource" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "SetProcessControllerSource" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "SetProcessControllerSource" is not integer value.')

        if self.source is None:
            raise ValueError(f'Property "Source" of "SetProcessControllerSource" is None.')

        if not isinstance(self.source, ProcessControllerSource):
            raise ValueError(f'Property "Source" of "SetProcessControllerSource" is not an instance of "ProcessControllerSource".')

        self.source.validate()
