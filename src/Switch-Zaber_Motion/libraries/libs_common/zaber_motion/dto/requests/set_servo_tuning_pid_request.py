# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..ascii.servo_tuning_paramset import ServoTuningParamset


@dataclass
class SetServoTuningPIDRequest:

    interface_id: int = 0

    device: int = 0

    axis: int = 0

    paramset: ServoTuningParamset = next(first for first in ServoTuningParamset)

    p: float = 0

    i: float = 0

    d: float = 0

    fc: float = 0

    @staticmethod
    def zero_values() -> 'SetServoTuningPIDRequest':
        return SetServoTuningPIDRequest(
            interface_id=0,
            device=0,
            axis=0,
            paramset=next(first for first in ServoTuningParamset),
            p=0,
            i=0,
            d=0,
            fc=0,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'SetServoTuningPIDRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return SetServoTuningPIDRequest.from_dict(data)

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
            'p': float(self.p),
            'i': float(self.i),
            'd': float(self.d),
            'fc': float(self.fc),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SetServoTuningPIDRequest':
        return SetServoTuningPIDRequest(
            interface_id=data.get('interfaceId'),  # type: ignore
            device=data.get('device'),  # type: ignore
            axis=data.get('axis'),  # type: ignore
            paramset=ServoTuningParamset(data.get('paramset')),  # type: ignore
            p=data.get('p'),  # type: ignore
            i=data.get('i'),  # type: ignore
            d=data.get('d'),  # type: ignore
            fc=data.get('fc'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.interface_id is None:
            raise ValueError(f'Property "InterfaceId" of "SetServoTuningPIDRequest" is None.')

        if not isinstance(self.interface_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "InterfaceId" of "SetServoTuningPIDRequest" is not a number.')

        if int(self.interface_id) != self.interface_id:
            raise ValueError(f'Property "InterfaceId" of "SetServoTuningPIDRequest" is not integer value.')

        if self.device is None:
            raise ValueError(f'Property "Device" of "SetServoTuningPIDRequest" is None.')

        if not isinstance(self.device, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Device" of "SetServoTuningPIDRequest" is not a number.')

        if int(self.device) != self.device:
            raise ValueError(f'Property "Device" of "SetServoTuningPIDRequest" is not integer value.')

        if self.axis is None:
            raise ValueError(f'Property "Axis" of "SetServoTuningPIDRequest" is None.')

        if not isinstance(self.axis, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Axis" of "SetServoTuningPIDRequest" is not a number.')

        if int(self.axis) != self.axis:
            raise ValueError(f'Property "Axis" of "SetServoTuningPIDRequest" is not integer value.')

        if self.paramset is None:
            raise ValueError(f'Property "Paramset" of "SetServoTuningPIDRequest" is None.')

        if not isinstance(self.paramset, ServoTuningParamset):
            raise ValueError(f'Property "Paramset" of "SetServoTuningPIDRequest" is not an instance of "ServoTuningParamset".')

        if self.p is None:
            raise ValueError(f'Property "P" of "SetServoTuningPIDRequest" is None.')

        if not isinstance(self.p, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "P" of "SetServoTuningPIDRequest" is not a number.')

        if self.i is None:
            raise ValueError(f'Property "I" of "SetServoTuningPIDRequest" is None.')

        if not isinstance(self.i, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "I" of "SetServoTuningPIDRequest" is not a number.')

        if self.d is None:
            raise ValueError(f'Property "D" of "SetServoTuningPIDRequest" is None.')

        if not isinstance(self.d, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "D" of "SetServoTuningPIDRequest" is not a number.')

        if self.fc is None:
            raise ValueError(f'Property "Fc" of "SetServoTuningPIDRequest" is None.')

        if not isinstance(self.fc, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Fc" of "SetServoTuningPIDRequest" is not a number.')
