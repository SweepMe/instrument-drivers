# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import zaber_bson
from ..ascii.servo_tuning_paramset import ServoTuningParamset


@dataclass
class ServoTuningParamsetResponse:

    paramset: ServoTuningParamset = next(first for first in ServoTuningParamset)

    @staticmethod
    def zero_values() -> 'ServoTuningParamsetResponse':
        return ServoTuningParamsetResponse(
            paramset=next(first for first in ServoTuningParamset),
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'ServoTuningParamsetResponse':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return ServoTuningParamsetResponse.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'paramset': self.paramset.value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ServoTuningParamsetResponse':
        return ServoTuningParamsetResponse(
            paramset=ServoTuningParamset(data.get('paramset')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.paramset is None:
            raise ValueError(f'Property "Paramset" of "ServoTuningParamsetResponse" is None.')

        if not isinstance(self.paramset, ServoTuningParamset):
            raise ValueError(f'Property "Paramset" of "ServoTuningParamsetResponse" is not an instance of "ServoTuningParamset".')
