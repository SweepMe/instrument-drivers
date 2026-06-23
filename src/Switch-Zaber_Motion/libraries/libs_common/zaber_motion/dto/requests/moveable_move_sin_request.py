# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ..measurement_or_value import MeasurementOrValue, MeasurementOrValueWireFormat


@dataclass
class MoveableMoveSinRequest:

    moveable_id: int = 0

    amplitude: MeasurementOrValue = 0

    period: MeasurementOrValue = 0

    count: float = 0

    wait_until_idle: bool = False

    @staticmethod
    def zero_values() -> 'MoveableMoveSinRequest':
        return MoveableMoveSinRequest(
            moveable_id=0,
            amplitude=0,
            period=0,
            count=0,
            wait_until_idle=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MoveableMoveSinRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MoveableMoveSinRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'moveableId': int(self.moveable_id),
            'amplitude': MeasurementOrValueWireFormat(self.amplitude).to_dict(),
            'period': MeasurementOrValueWireFormat(self.period).to_dict(),
            'count': float(self.count),
            'waitUntilIdle': bool(self.wait_until_idle),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MoveableMoveSinRequest':
        return MoveableMoveSinRequest(
            moveable_id=data.get('moveableId'),  # type: ignore
            amplitude=MeasurementOrValueWireFormat.from_dict(data.get('amplitude')).convert_back(),  # type: ignore
            period=MeasurementOrValueWireFormat.from_dict(data.get('period')).convert_back(),  # type: ignore
            count=data.get('count'),  # type: ignore
            wait_until_idle=data.get('waitUntilIdle'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.moveable_id is None:
            raise ValueError(f'Property "MoveableId" of "MoveableMoveSinRequest" is None.')

        if not isinstance(self.moveable_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "MoveableId" of "MoveableMoveSinRequest" is not a number.')

        if int(self.moveable_id) != self.moveable_id:
            raise ValueError(f'Property "MoveableId" of "MoveableMoveSinRequest" is not integer value.')

        if self.amplitude is None:
            raise ValueError(f'Property "Amplitude" of "MoveableMoveSinRequest" is None.')

        MeasurementOrValueWireFormat(self.amplitude).validate()

        if self.period is None:
            raise ValueError(f'Property "Period" of "MoveableMoveSinRequest" is None.')

        MeasurementOrValueWireFormat(self.period).validate()

        if self.count is None:
            raise ValueError(f'Property "Count" of "MoveableMoveSinRequest" is None.')

        if not isinstance(self.count, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Count" of "MoveableMoveSinRequest" is not a number.')
