# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
# pylint: disable=line-too-long, unused-argument, f-string-without-interpolation, too-many-branches, too-many-statements, unnecessary-pass, unused-variable
from dataclasses import dataclass
from typing import Any, Dict, Optional
import decimal
import zaber_bson
from ..measurement import Measurement


@dataclass
class AxisTransformation:
    """
    Represents a transformation of a translator axis.
    """

    axis_letter: str
    """
    Letter of the translator axis (X,Y,Z,A,B,C,E).
    """

    scaling: Optional[float] = None
    """
    Scaling factor.
    """

    translation: Optional[Measurement] = None
    """
    Translation distance.
    """

    @staticmethod
    def zero_values() -> 'AxisTransformation':
        return AxisTransformation(
            axis_letter="",
            scaling=None,
            translation=None,
        )

    @staticmethod
    def from_binary(data_bytes: bytes) -> 'AxisTransformation':
        """" Deserialize a binary representation of this class. """
        data = zaber_bson.loads(data_bytes)  # type: Dict[str, Any]
        return AxisTransformation.from_dict(data)

    def to_binary(self) -> bytes:
        """" Serialize this class to a binary representation. """
        self.validate()
        return zaber_bson.dumps(self.to_dict())  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        return {
            'axisLetter': str(self.axis_letter or ''),
            'scaling': float(self.scaling) if self.scaling is not None else None,
            'translation': self.translation.to_dict() if self.translation is not None else None,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AxisTransformation':
        return AxisTransformation(
            axis_letter=data.get('axisLetter'),  # type: ignore
            scaling=data.get('scaling'),  # type: ignore
            translation=Measurement.from_dict(data.get('translation')) if data.get('translation') is not None else None,  # type: ignore
        )

    def validate(self) -> None:
        """" Validates the properties of the instance. """
        if self.axis_letter is not None:
            if not isinstance(self.axis_letter, str):
                raise ValueError(f'Property "AxisLetter" of "AxisTransformation" is not a string.')

        if self.scaling is not None:
            if not isinstance(self.scaling, (int, float, decimal.Decimal)):
                raise ValueError(f'Property "Scaling" of "AxisTransformation" is not a number.')

        if self.translation is not None:
            if not isinstance(self.translation, Measurement):
                raise ValueError(f'Property "Translation" of "AxisTransformation" is not an instance of "Measurement".')

            self.translation.validate()
