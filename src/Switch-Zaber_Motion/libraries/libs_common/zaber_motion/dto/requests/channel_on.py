# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..measurement import Measurement


@dataclass
class ChannelOn:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    on: bool = False

    duration: Optional[Measurement] = None

    @staticmethod
    def zero_values() -> 'ChannelOn':
        return ChannelOn(
            interface_id=0,
            device=0,
            axis=0,
            on=False,
            duration=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ChannelOn':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ChannelOn.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'on': bool(self.on),
            'duration': self.duration.to_dict() if self.duration is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ChannelOn':
        return ChannelOn(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            on=data.get('on'),  # type: ignore
            duration=Measurement.from_dict(data.get('duration')) if data.get('duration') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "ChannelOn" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "ChannelOn" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "ChannelOn" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "ChannelOn" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "ChannelOn" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "ChannelOn" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "ChannelOn" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "ChannelOn" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "ChannelOn" is not integer value.')

        if self.duration is not None:
            if not isinstance(self.duration, Measurement):
                raise ValueError(f'Property "Duration" of "ChannelOn" is not an instance of "Measurement".')

            self.duration.validate()
