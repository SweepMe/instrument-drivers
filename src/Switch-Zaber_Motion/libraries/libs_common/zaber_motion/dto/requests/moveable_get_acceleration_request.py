# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..ascii.accel_type import AccelType
from ...units import Units, UnitsAndLiterals, units_from_literals


@dataclass
class MoveableGetAccelerationRequest:

    moveable_id: int = 0

    accel_type: Optional[AccelType] = None

    unit: Optional[UnitsAndLiterals] = None

    @staticmethod
    def zero_values() -> 'MoveableGetAccelerationRequest':
        return MoveableGetAccelerationRequest(
            moveable_id=0,
            accel_type=None,
            unit=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'MoveableGetAccelerationRequest':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return MoveableGetAccelerationRequest.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'moveableId': int(self.moveable_id),
            'accelType': self.accel_type.value if self.accel_type is not None else None,
            'unit': units_from_literals(self.unit).value if self.unit is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'MoveableGetAccelerationRequest':
        return MoveableGetAccelerationRequest(
            moveable_id=data.get('moveableId'),  # type: ignore
            accel_type=AccelType(data.get('accelType')) if data.get('accelType') is not None else None,  # type: ignore
            unit=Units(data.get('unit')) if data.get('unit') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.moveable_id is None:
            raise ValueError(f'Property "MoveableId" of "MoveableGetAccelerationRequest" is None.')

        if not isinstance(self.moveable_id, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "MoveableId" of "MoveableGetAccelerationRequest" is not a number.')

        if int(self.moveable_id) != self.moveable_id:
            raise ValueError(f'Property "MoveableId" of "MoveableGetAccelerationRequest" is not integer value.')

        if self.accel_type is not None:
            if not isinstance(self.accel_type, AccelType):
                raise ValueError(f'Property "AccelType" of "MoveableGetAccelerationRequest" is not an instance of "AccelType".')

        if self.unit is not None:
            if not isinstance(self.unit, (Units, str)):
                raise ValueError(f'Property "Unit" of "MoveableGetAccelerationRequest" is not Units.')
