# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class DefaultMotionUnits:
    """
    Default units of measurement for movement operations.
    """

    position: Optional[UnitsAndLiterals] = None
    """
    Default unit for position.
    """

    speed: Optional[UnitsAndLiterals] = None
    """
    Default unit for velocity.
    """

    acceleration: Optional[UnitsAndLiterals] = None
    """
    Default unit for acceleration.
    """

    time: Optional[UnitsAndLiterals] = None
    """
    Default unit for time.
    """

    @staticmethod
    def zero_values() -> 'DefaultMotionUnits':
        return DefaultMotionUnits(
            position=None,
            speed=None,
            acceleration=None,
            time=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'DefaultMotionUnits':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return DefaultMotionUnits.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'position': units_from_literals(self.position).value if self.position is not None else None,
            'speed': units_from_literals(self.speed).value if self.speed is not None else None,
            'acceleration': units_from_literals(self.acceleration).value if self.acceleration is not None else None,
            'time': units_from_literals(self.time).value if self.time is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DefaultMotionUnits':
        return DefaultMotionUnits(
            position=Units(data.get('position')) if data.get('position') is not None else None,  # type: ignore
            speed=Units(data.get('speed')) if data.get('speed') is not None else None,  # type: ignore
            acceleration=Units(data.get('acceleration')) if data.get('acceleration') is not None else None,  # type: ignore
            time=Units(data.get('time')) if data.get('time') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.position is not None:
            if not isinstance(self.position, (Units, str)):
                raise ValueError(f'Property "Position" of "DefaultMotionUnits" is not Units.')

        if self.speed is not None:
            if not isinstance(self.speed, (Units, str)):
                raise ValueError(f'Property "Speed" of "DefaultMotionUnits" is not Units.')

        if self.acceleration is not None:
            if not isinstance(self.acceleration, (Units, str)):
                raise ValueError(f'Property "Acceleration" of "DefaultMotionUnits" is not Units.')

        if self.time is not None:
            if not isinstance(self.time, (Units, str)):
                raise ValueError(f'Property "Time" of "DefaultMotionUnits" is not Units.')
