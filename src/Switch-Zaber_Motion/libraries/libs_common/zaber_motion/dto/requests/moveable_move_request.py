# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..measurement_or_value import MeasurementOrValue, MeasurementOrValueWireFormat
from ..cyclic_direction import CyclicDirection


@dataclass
class MoveableMoveRequest:

    moveable_id: int = 0

    wait_until_idle: bool = False

    position: Optional[MeasurementOrValue] = None

    velocity: Optional[MeasurementOrValue] = None

    acceleration: Optional[MeasurementOrValue] = None

    cyclic_direction: Optional[CyclicDirection] = None

    extra_cycles: Optional[int] = None

    @staticmethod
    def zero_values() -> 'MoveableMoveRequest':
        return MoveableMoveRequest(
            moveable_id=0,
            position=None,
            velocity=None,
            acceleration=None,
            wait_until_idle=False,
            cyclic_direction=None,
            extra_cycles=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MoveableMoveRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MoveableMoveRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'moveableId': int(self.moveable_id),
            'position': MeasurementOrValueWireFormat(self.position).to_dict() if self.position is not None else None,
            'velocity': MeasurementOrValueWireFormat(self.velocity).to_dict() if self.velocity is not None else None,
            'acceleration': MeasurementOrValueWireFormat(self.acceleration).to_dict() if self.acceleration is not None else None,
            'waitUntilIdle': bool(self.wait_until_idle),
            'cyclicDirection': self.cyclic_direction.value if self.cyclic_direction is not None else None,
            'extraCycles': int(self.extra_cycles) if self.extra_cycles is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MoveableMoveRequest':
        return MoveableMoveRequest(
            moveable_id=data.get('moveableId'),  # type: ignore
            position=MeasurementOrValueWireFormat.from_dict(data.get('position')).convert_back() if data.get('position') is not None else None,  # type: ignore
            velocity=MeasurementOrValueWireFormat.from_dict(data.get('velocity')).convert_back() if data.get('velocity') is not None else None,  # type: ignore
            acceleration=MeasurementOrValueWireFormat.from_dict(data.get('acceleration')).convert_back() if data.get('acceleration') is not None else None,  # type: ignore
            wait_until_idle=data.get('waitUntilIdle'),  # type: ignore
            cyclic_direction=CyclicDirection(data.get('cyclicDirection')) if data.get('cyclicDirection') is not None else None,  # type: ignore
            extra_cycles=data.get('extraCycles'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.moveable_id is None:
            raise ValueError(f'Property "MoveableId" of "MoveableMoveRequest" is None.')

        if not isinstance(self.moveable_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "MoveableId" of "MoveableMoveRequest" is not a number.')

        if int(self.moveable_id) != self.moveable_id:
            raise ValueError(f'Property "MoveableId" of "MoveableMoveRequest" is not integer value.')

        if self.position is not None:
            MeasurementOrValueWireFormat(self.position).validate()

        if self.velocity is not None:
            MeasurementOrValueWireFormat(self.velocity).validate()

        if self.acceleration is not None:
            MeasurementOrValueWireFormat(self.acceleration).validate()

        if self.cyclic_direction is not None:
            if not isinstance(self.cyclic_direction, CyclicDirection):
                raise ValueError(f'Property "CyclicDirection" of "MoveableMoveRequest" is not an instance of "CyclicDirection".')

        if self.extra_cycles is not None:
            if not isinstance(self.extra_cycles, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "ExtraCycles" of "MoveableMoveRequest" is not a number.')

            if int(self.extra_cycles) != self.extra_cycles:
                raise ValueError(f'Property "ExtraCycles" of "MoveableMoveRequest" is not integer value.')
