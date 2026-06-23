# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class PvtBufferAxisUnits:
    """
    Specifies the units to use for a buffer axis when reading back a PVT buffer.
    The axis number is used to determine a physical axis on the device for units conversion.
    """

    axis_number: int
    """
    Number of the physical axis on the device used for units conversion.
    """

    position_units: UnitsAndLiterals
    """
    Units to convert position values to.
    """

    velocity_units: UnitsAndLiterals
    """
    Units to convert velocity values to.
    """

    @staticmethod
    def zero_values() -> 'PvtBufferAxisUnits':
        return PvtBufferAxisUnits(
            axis_number=0,
            position_units=Units.NATIVE,
            velocity_units=Units.NATIVE,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'PvtBufferAxisUnits':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return PvtBufferAxisUnits.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axisNumber': int(self.axis_number),
            'positionUnits': units_from_literals(self.position_units).value,
            'velocityUnits': units_from_literals(self.velocity_units).value,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PvtBufferAxisUnits':
        return PvtBufferAxisUnits(
            axis_number=data.get('axisNumber'),  # type: ignore
            position_units=Units(data.get('positionUnits')),  # type: ignore
            velocity_units=Units(data.get('velocityUnits')),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axis_number is None:
            raise ValueError(f'Property "AxisNumber" of "PvtBufferAxisUnits" is None.')

        if not isinstance(self.axis_number, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "AxisNumber" of "PvtBufferAxisUnits" is not a number.')

        if int(self.axis_number) != self.axis_number:
            raise ValueError(f'Property "AxisNumber" of "PvtBufferAxisUnits" is not integer value.')

        if self.position_units is None:
            raise ValueError(f'Property "PositionUnits" of "PvtBufferAxisUnits" is None.')

        if not isinstance(self.position_units, (Units, str)):
            raise ValueError(f'Property "PositionUnits" of "PvtBufferAxisUnits" is not Units.')

        if self.velocity_units is None:
            raise ValueError(f'Property "VelocityUnits" of "PvtBufferAxisUnits" is None.')

        if not isinstance(self.velocity_units, (Units, str)):
            raise ValueError(f'Property "VelocityUnits" of "PvtBufferAxisUnits" is not Units.')
