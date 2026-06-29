# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass, field
from typing import Any, Dict, List
import decimal
from collections.abc import Iterable
import zaber_bson
from ..ascii.servo_tuning_paramset import ServoTuningParamset
from ..ascii.servo_tuning_param import ServoTuningParam


@dataclass
class SetServoTuningRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    paramset: ServoTuningParamset = next(first for first in ServoTuningParamset)

    tuning_params: List[ServoTuningParam] = field(default_factory=list)

    set_unspecified_to_default: bool = False

    @staticmethod
    def zero_values() -> 'SetServoTuningRequest':
        return SetServoTuningRequest(
            interface_id=0,
            device=0,
            axis=0,
            paramset=next(first for first in ServoTuningParamset),
            tuning_params=[],
            set_unspecified_to_default=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetServoTuningRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetServoTuningRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interfaceId': int(self.interface_id),
            'device': int(self.device),
            'axis': int(self.axis),
            'paramset': self.paramset.value,
            'tuningParams': [item.to_dict() for item in self.tuning_params] if self.tuning_params is not None else [],
            'setUnspecifiedToDefault': bool(self.set_unspecified_to_default),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetServoTuningRequest':
        return SetServoTuningRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            paramset=ServoTuningParamset(data.get('paramset')),  # type: ignore
            tuning_params=[ServoTuningParam.from_dict(item) for item in data.get('tuningParams')],  # type: ignore
            set_unspecified_to_default=data.get('setUnspecifiedToDefault'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "SetServoTuningRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "SetServoTuningRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "SetServoTuningRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "SetServoTuningRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "SetServoTuningRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "SetServoTuningRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "SetServoTuningRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "SetServoTuningRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "SetServoTuningRequest" is not integer value.')

        if self.paramset is None:
            raise ValueError(f'Property "Paramset" of "SetServoTuningRequest" is None.')

        if not isinstance(self.paramset, ServoTuningParamset):
            raise ValueError(f'Property "Paramset" of "SetServoTuningRequest" is not an instance of "ServoTuningParamset".')

        if self.tuning_params is not None:
            if not isinstance(self.tuning_params, Iterable):
                raise ValueError('Property "TuningParams" of "SetServoTuningRequest" is not iterable.')

            for i, tuning_params_item in enumerate(self.tuning_params):
                if tuning_params_item is None:
                    raise ValueError(f'Item {i} in property "TuningParams" of "SetServoTuningRequest" is None.')

                if not isinstance(tuning_params_item, ServoTuningParam):
                    raise ValueError(f'Item {i} in property "TuningParams" of "SetServoTuningRequest" is not an instance of "ServoTuningParam".')

                tuning_params_item.validate()
