# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List
from collections.abc import Iterable
import zaber_bson
from ..measurement import Measurement


@dataclass
class PvtPoint:
    """
    Data representing a single point in a PVT sequence or buffer.
    """

    positions: List[Measurement]
    """
    Position of this point for all series (axes).
    """

    velocities: List[Measurement]
    """
    Velocity at this point for all series (axes).
    """

    time: Measurement
    """
    Time to take to reach this point from the previous point or starting position.
    """

    relative: bool
    """
    Flag indicating if this point's position is relative to the previous point or starting position.
    Defaults to false, meaning absolute positioning.
    """

    @staticmethod
    def zero_values() -> 'PvtPoint':
        return PvtPoint(
            positions=[],
            velocities=[],
            time=Measurement.zero_values(),
            relative=False,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtPoint':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtPoint.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'positions': [item.to_dict() for item in self.positions] if self.positions is not None else [],
            'velocities': [item.to_dict() for item in self.velocities] if self.velocities is not None else [],
            'time': self.time.to_dict(),
            'relative': bool(self.relative),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtPoint':
        return PvtPoint(
            positions=[Measurement.from_dict(item) for item in data.get('positions')],  # type: ignore
            velocities=[Measurement.from_dict(item) for item in data.get('velocities')],  # type: ignore
            time=Measurement.from_dict(data.get('time')),  # type: ignore
            relative=data.get('relative'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.positions is not None:
            if not isinstance(self.positions, Iterable):
                raise ValueError('Property "Positions" of "PvtPoint" is not iterable.')

            for i, positions_item in enumerate(self.positions):
                if positions_item is None:
                    raise ValueError(f'Item {i} in property "Positions" of "PvtPoint" is None.')

                if not isinstance(positions_item, Measurement):
                    raise ValueError(f'Item {i} in property "Positions" of "PvtPoint" is not an instance of "Measurement".')

                positions_item.validate()

        if self.velocities is not None:
            if not isinstance(self.velocities, Iterable):
                raise ValueError('Property "Velocities" of "PvtPoint" is not iterable.')

            for i, velocities_item in enumerate(self.velocities):
                if velocities_item is None:
                    raise ValueError(f'Item {i} in property "Velocities" of "PvtPoint" is None.')

                if not isinstance(velocities_item, Measurement):
                    raise ValueError(f'Item {i} in property "Velocities" of "PvtPoint" is not an instance of "Measurement".')

                velocities_item.validate()

        if self.time is None:
            raise ValueError(f'Property "Time" of "PvtPoint" is None.')

        if not isinstance(self.time, Measurement):
            raise ValueError(f'Property "Time" of "PvtPoint" is not an instance of "Measurement".')

        self.time.validate()
