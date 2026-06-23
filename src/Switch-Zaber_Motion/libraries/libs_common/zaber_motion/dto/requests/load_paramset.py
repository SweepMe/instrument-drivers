# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..ascii.servo_tuning_paramset import ServoTuningParamset


@dataclass
class LoadParamset:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    to_paramset: ServoTuningParamset = next(first for first in ServoTuningParamset)

    from_paramset: ServoTuningParamset = next(first for first in ServoTuningParamset)

    @staticmethod
    def zero_values() -> 'LoadParamset':
        return LoadParamset(
            interface_id=0,
            device=0,
            axis=0,
            to_paramset=next(first for first in ServoTuningParamset),
            from_paramset=next(first for first in ServoTuningParamset),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'LoadParamset':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return LoadParamset.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'toParamset': self.to_paramset.value,
            'fromParamset': self.from_paramset.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LoadParamset':
        return LoadParamset(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            to_paramset=ServoTuningParamset(data.get('toParamset')),  # type: ignore
            from_paramset=ServoTuningParamset(data.get('fromParamset')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "LoadParamset" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "LoadParamset" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "LoadParamset" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "LoadParamset" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "LoadParamset" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "LoadParamset" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "LoadParamset" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "LoadParamset" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "LoadParamset" is not integer value.')

        if self.to_paramset is None:
            raise ValueError(f'Property "ToParamset" of "LoadParamset" is None.')

        if not isinstance(self.to_paramset, ServoTuningParamset):
            raise ValueError(f'Property "ToParamset" of "LoadParamset" is not an instance of "ServoTuningParamset".')

        if self.from_paramset is None:
            raise ValueError(f'Property "FromParamset" of "LoadParamset" is None.')

        if not isinstance(self.from_paramset, ServoTuningParamset):
            raise ValueError(f'Property "FromParamset" of "LoadParamset" is not an instance of "ServoTuningParamset".')
