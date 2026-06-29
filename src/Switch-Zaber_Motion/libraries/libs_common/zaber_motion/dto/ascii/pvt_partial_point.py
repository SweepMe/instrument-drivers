# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from collections.abc import Iterable
import zaber_bson
from ..measurement import Measurement


@dataclass
class PvtPartialPoint:
    """
    Data representing a single point in a PVT sequence or buffer with optional members.
    This is used to represent sequences with missing columns such as velocity or time.
    The data must be completed using the PvtSequence.Generate... methods before it can be sent to a device.
    """

    positions: List[Optional[Measurement]]
    """
    Position of this point for all series (axes).
    """

    velocities: List[Optional[Measurement]]
    """
    Velocity at this point for all series (axes).
    """

    time: Optional[Measurement] = None
    """
    Time to take to reach this point from the previous point or starting position.
    """

    relative: Optional[bool] = None
    """
    Flag indicating if this point's position is relative to the previous point or starting position.
    Defaults to false, meaning absolute positioning.
    """

    @staticmethod
    def zero_values() -> 'PvtPartialPoint':
        return PvtPartialPoint(
            positions=[],
            velocities=[],
            time=None,
            relative=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtPartialPoint':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtPartialPoint.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'positions': [item.to_dict() if item is not None else None for item in self.positions] if self.positions is not None else [],
            'velocities': [item.to_dict() if item is not None else None for item in self.velocities] if self.velocities is not None else [],
            'time': self.time.to_dict() if self.time is not None else None,
            'relative': bool(self.relative) if self.relative is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtPartialPoint':
        return PvtPartialPoint(
            positions=[Measurement.from_dict(item) if item is not None else None for item in data.get('positions')],  # type: ignore
            velocities=[Measurement.from_dict(item) if item is not None else None for item in data.get('velocities')],  # type: ignore
            time=Measurement.from_dict(data.get('time')) if data.get('time') is not None else None,  # type: ignore
            relative=data.get('relative'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.positions is not None:
            if not isinstance(self.positions, Iterable):
                raise ValueError('Property "Positions" of "PvtPartialPoint" is not iterable.')

            for i, positions_item in enumerate(self.positions):
                if positions_item is not None:
                    if not isinstance(positions_item, Measurement):
                        raise ValueError(f'Item {i} in property "Positions" of "PvtPartialPoint" is not an instance of "Measurement".')

                    positions_item.validate()

        if self.velocities is not None:
            if not isinstance(self.velocities, Iterable):
                raise ValueError('Property "Velocities" of "PvtPartialPoint" is not iterable.')

            for i, velocities_item in enumerate(self.velocities):
                if velocities_item is not None:
                    if not isinstance(velocities_item, Measurement):
                        raise ValueError(f'Item {i} in property "Velocities" of "PvtPartialPoint" is not an instance of "Measurement".')

                    velocities_item.validate()

        if self.time is not None:
            if not isinstance(self.time, Measurement):
                raise ValueError(f'Property "Time" of "PvtPartialPoint" is not an instance of "Measurement".')

            self.time.validate()
