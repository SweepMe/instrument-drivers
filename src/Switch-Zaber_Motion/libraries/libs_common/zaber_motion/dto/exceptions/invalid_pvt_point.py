# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict
import decimal
import zaber_bson


@dataclass
class InvalidPvtPoint:
    """
    Contains invalid PVT points for PvtExecutionException.
    """

    index: int
    """
    Index of the point numbered from the last submitted point.
    """

    point: str
    """
    The textual representation of the point.
    """

    @staticmethod
    def zero_values() -> 'InvalidPvtPoint':
        return InvalidPvtPoint(
            index=0,
            point="",
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'InvalidPvtPoint':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return InvalidPvtPoint.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'index': int(self.index),
            'point': str(self.point or ''),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'InvalidPvtPoint':
        return InvalidPvtPoint(
            index=data.get('index'),  # type: ignore
            point=data.get('point'),  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.index is None:
            raise ValueError(f'Property "Index" of "InvalidPvtPoint" is None.')

        if not isinstance(self.index, (int, float, decimal.Decimal)):
            raise ValueError(f'Property "Index" of "InvalidPvtPoint" is not a number.')

        if int(self.index) != self.index:
            raise ValueError(f'Property "Index" of "InvalidPvtPoint" is not integer value.')

        if self.point is not None:
            if not isinstance(self.point, str):
                raise ValueError(f'Property "Point" of "InvalidPvtPoint" is not a string.')
